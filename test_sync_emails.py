import unittest
from unittest.mock import patch, MagicMock
from sync_emails import Gmail, GmailMessage, push_data_to_postgres

class TestGmail(unittest.TestCase):

    @patch('sync_emails.build')
    def test_authenticate_gmail_api(self, mock_build):
        # Add unit test for authenticate_gmail_api method
        # Mock the build function and check if it's called
        gmail = Gmail()
        build = gmail.authenticate_gmail_api()
        assert build

    def test_prepare_datasets(self):
        # Add unit test for prepare_datasets method in Gmail class
        # Create a GmailMessage instance and test the prepare_datasets method
        message = GmailMessage("email_id", "sender <sender>", "receiver", "subject", "body", "received_at", ["label_id"],
                               "attachment_data", "attachment_id", "filename")
        gmail = Gmail()
        gmail.prepare_datasets(message)

        # Assert the expected data in user_data, mail_data, attachment_data, and label_data
        self.assertEqual(gmail.user_data, [{'user_id': 'sender', 'user_name': 'sender'}])
        self.assertEqual(gmail.mail_data, [{'email_id': 'email_id', 'subject': 'subject', 'body': 'body',
                                            'sender_id': 'sender', 'received_at': 'received_at'}])
        self.assertEqual(gmail.attachment_data, [{'attachment_id': 'attachment_id', 'data': 'attachment_data',
                                                  'email_id': 'email_id', 'filename': 'filename'}])
        self.assertEqual(gmail.label_data, [{'email_id': 'email_id', 'label_id': 'label_id'}])

    @patch('sync_emails.build')
    def test_list_emails(self, mock_build):
        # Add unit test for list_emails method in Gmail class
        # Mock the service and execute methods to simulate fetching emails
        mock_service = MagicMock()
        mock_execute = MagicMock(return_value={'messages': [{'id': 'email_id'}]})
        mock_service.users().messages().list().execute = mock_execute
        mock_build.return_value = mock_service

        gmail = Gmail()
        emails = gmail.list_emails(query="")

        # Assert that the mock_execute method was called and returned the expected emails
        mock_execute.assert_called()
        self.assertEqual(emails, [{'id': 'email_id'}])

    @patch('sync_emails.build')
    def test_get_email_content(self, mock_build):
        # Add unit test for get_email_content method in Gmail class
        # Mock the service and execute methods to simulate fetching email content
        mock_service = MagicMock()
        mock_execute = MagicMock(return_value={'payload': {'headers': [{'name': 'From', 'value': 'sender'}, {'name': 'To', 'value': 'receiver'}],
                                                     'body': {'data': 'base64_encoded_data'}}})
        mock_service.users().messages().get().execute = mock_execute
        mock_build.return_value = mock_service

        gmail = Gmail()
        sender, receiver, subject, body, received_at, label_ids, attachment_data, attachment_id, filename = \
            gmail.get_email_content(email_id='email_id')

        # Assert that the mock_execute method was called and returned the expected content
        self.assertEqual(sender, 'sender')
        self.assertEqual(receiver, 'receiver')


if __name__ == '__main__':
    unittest.main()
