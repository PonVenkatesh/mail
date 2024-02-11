
class ActionsController:
    def __init__(self, rules_evaluator, result_mail_ids, actions):
        self.actions = actions
        self.rules_evaluator = rules_evaluator
        self.result_mad_ids = result_mail_ids
        self.email_id_data_dict = {each["email_id"]: each for each in rules_evaluator.email_data}

    def validate_action(self):
        for action in self.actions:
            if action.get("action") in list(ACTIONS_OBJ_MAP.keys()):
                ACTIONS_OBJ_MAP[action.get("action")]().perform()
            else:
                print(" Invalid Action : {}".format(action.get("action")))
        pass

class MoveTo:
    def __init__(self):
        pass

    def perform(self):
        pass

ACTIONS_OBJ_MAP = {
    "moveTo": MoveTo
}