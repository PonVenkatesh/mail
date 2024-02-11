import base64
import os
import traceback

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from postgres.postgres import push_data_to_postgres

# This code will fetch emails from gmail user inbox, and put it into postgres tables

# Gmail API scope for read-write access
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailMessage:
    def __init__(self, email_id, sender, receiver, subject, body, received_at, label_ids, attachment_data,
                 attachment_id, filename):
        self.email_id = email_id
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.received_at = received_at
        self.label_ids = label_ids
        self.attachment_data = attachment_data
        self.attachment_id = attachment_id
        self.filename = filename

    def pre_process_data(self):
        # All preprocessing can be done here
        if isinstance(self.subject, str):
            if "'" in self.subject:
                self.subject = self.subject.replace("'", "''")

        return self


class Gmail:
    def __init__(self):
        self.service = self.authenticate_gmail_api()
        # self.user_df = {"user_id": [], "user_name": []}
        # self.mail_df = {"email_id": [], "subject": [], "body": [], "sender_id": [], "received_at": []}
        # self.attachment_df = {"attachment_id": [], "filename": [], "data": [], "email_id": []}
        # self.label_df = {"label_id": [], "email_id": []}
        self.user_data = []
        self.mail_data = []
        self.attachment_data = []
        self.label_data = []

    def authenticate_gmail_api(self):
        creds = None

        # The file token.json stores the user's access and refresh tokens
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json")

        # If credentials are not available or are invalid, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def prepare_datasets(self, message):
        # Preparing dataframes to push the data to Postgres
        if " <" in message.sender:
            user_name, user_id = message.sender.split(" <")
        else:
            user_name = message.sender
            user_id = message.sender

        self.user_data.append(
            {
                "user_id": user_id[:-1],
                "user_name": user_name
            }
        )

        self.mail_data.append(
            {
                "email_id": message.email_id,
                "subject": message.subject,
                "body": message.body,
                "sender_id": user_id[:-1],
                "received_at": message.received_at

            })

        if message.attachment_id:
            self.attachment_data.append(
                {
                    "attachment_id": message.attachment_id,
                    "data": message.attachment_data,
                    "email_id": message.email_id,
                    "filename": message.filename
                })

        if message.label_ids:
            for label_id in message.label_ids:
                self.label_data.extend([{
                    "email_id": message.email_id,
                    "label_id": label_id
                }])

    def list_emails(self, query=""):
        # List emails based on a query (default is all emails)
        results = self.service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        return messages

    def get_email_content(self, email_id):
        # Get the content of a specific email
        email = self.service.users().messages().get(userId="me", id=email_id).execute()
        print(email)
        sender = None
        receiver = None
        subject = None
        body = None
        received_at = None
        label_ids = None
        attachment_data = None
        attachment_id = None
        attachment_name = None
        try:
            # Extract sender, subject, and body
            sender = [header["value"] for header in email["payload"]["headers"] if header["name"] == "From"][0]
            receiver = [header["value"] for header in email["payload"]["headers"] if header["name"] == "To"][0]
            subject = [header["value"] for header in email["payload"]["headers"] if header["name"] == "Subject"][0]
            received_at = email.get("internalDate")
            label_ids = email.get("labelIds", [])
            if "parts" not in email["payload"]:
                body = email["payload"]["body"]["data"]
            else:
                for part in email["payload"]["parts"]:
                    if "data" in part["body"]:
                        # body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        body = part["body"]["data"]
                    if "filename" in part and part["filename"]:
                        attachment_name = part["filename"]
                        attachment_id = part['body'].get('attachmentId')
                        attachment_data = None
                        if attachment_id:
                            att = self.service.users().messages().attachments().get(
                                userId='me', id=attachment_id, messageId=email_id).execute()
                            print(att)
                            attachment_data = att['data']
                        if attachment_data:
                            save_folder = f"attachments/{email_id}"
                            os.makedirs(save_folder, exist_ok=True)
                            save_path = os.path.join(save_folder, attachment_name)
                            with open(save_path, "wb") as file:
                                file.write(base64.urlsafe_b64decode(attachment_data.encode('UTF-8')))
                            print(f"Attachment '{attachment_name}' downloaded to '{save_path}'.")
        except Exception as e:
            print(traceback.format_exc())
            print("Email body parsing failed")
        return sender, receiver, subject, body, received_at, label_ids, attachment_data, attachment_id, attachment_name


def main():
    gmail = Gmail()
    # Example: List all emails (replace 'label:TestGmail' with your desired query)
    # query = "label:TestGmail"
    failed_mail_ids = []
    all_emails = gmail.list_emails(query="")
    if all_emails:
        # Get content of each email
        for each in all_emails[:10]:
            try:
                email_id = each.get("id")
                if email_id:
                    sender, receiver, subject, body, received_at, label_ids, attachment_data, attachment_id, filename = gmail.get_email_content(
                        email_id)
                    if sender:
                        print(sender)
                        mail_message = GmailMessage(email_id, sender, receiver, subject, body, received_at, label_ids,
                                                    attachment_data, attachment_id, filename).pre_process_data()
                        gmail.prepare_datasets(mail_message)
            except Exception as e:
                failed_mail_ids.append(each["id"])

        push_data_to_postgres(gmail)
        print(" Failed Mail Ids : {}".format(failed_mail_ids))
    else:
        print("No emails found.")


if __name__ == "__main__":
    main()
