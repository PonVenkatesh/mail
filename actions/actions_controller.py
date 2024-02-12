import json
import os

import requests

from global_constants import UPDATE_ENDPOINT


class ActionsController:
    def __init__(self, rules_evaluator, result_mail_ids, actions):
        self.actions = actions
        self.rules_evaluator = rules_evaluator
        self.result_mail_ids = result_mail_ids
        # self.email_id_data_dict = {each["email_id"]: each for each in rules_evaluator.email_data}
        self.add_label_ids = []
        self.remove_label_ids = []

    def validate_action(self):
        for action in self.actions:
            if action.get("action") == "move_to" and action.get("value"):
                self.add_label_ids.append(action.get("value"))
            elif action.get("action") == "mark_as" and action.get("value"):
                if action.get("value") == "read":
                    self.remove_label_ids.append("UNREAD")
                elif action.get("value") == "unread":
                    self.add_label_ids.append("UNREAD")
            else:
                print(" Invalid Action : {}".format(action.get("action")))
                raise "Invalid Action"
        return self

    def perform(self):
        # Build the modify request payload
        modify_request = {}
        if self.result_mail_ids:
            modify_request = {
                "ids": self.result_mail_ids
            }
            if self.remove_label_ids:
                modify_request["removeLabelIds"] = self.remove_label_ids
            if self.add_label_ids:
                modify_request["addLabelIds"] = self.add_label_ids
        self.batch_update(modify_request)

    def batch_update(self, request_payload):
        def get_access_token():
            if os.path.exists(os.getcwd() + "/token.json"):
                with open(os.getcwd() + "/token.json", 'r') as json_file:
                    try:
                        token_json = json.load(json_file)
                        return token_json.get("token")
                    except:
                        print(" access token extraction failed, Re-authenticate")
                        return None
            return None

        if not request_payload:
            print(" Request Payload is empty")
            return
        access_token = get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Make a POST request to the Gmail API endpoint
        print(request_payload)
        response = requests.post(UPDATE_ENDPOINT, json=request_payload, headers=headers)
        print(response.text)
        # Check the response status
        if response.status_code in range(200, 300):
            print("Batch update Successful")
        else:
            print(f"Batch Update failed. {response.status_code}")
