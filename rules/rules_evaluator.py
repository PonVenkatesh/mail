from actions.actions_controller import ActionsController


class RulesEvaluator:
    def __init__(self, email_data, rules):
        self.email_data = email_data
        self.rules = rules

    def evaluate(self):
        result_email_ids = []
        for rule in self.rules:
            matching_mail_ids_per_condition_list = []
            for condition in rule.get("conditions", []):
                print(condition.get("field"))
                if condition.get("field") in list(EVALUATOR_OBJ_MAP.keys()):
                    if EVALUATOR_OBJ_MAP[condition.get("field")]().is_valid_operator(condition):
                        print(" IN In In")
                        matching_mail_ids = EVALUATOR_OBJ_MAP[condition.get("field")]().evaluate(condition, self.email_data)
                        print(matching_mail_ids)
                        matching_mail_ids_per_condition_list.append(matching_mail_ids)

            if rule.get("conditions_relation", "AND") == "OR":
                result_email_ids = flatten_list(matching_mail_ids_per_condition_list)
            elif rule.get("conditions_relation", "AND") == "AND":
                result_email_ids = intersection_list(matching_mail_ids_per_condition_list)
            else:
                print(" Invalid conditions_relation : {}".format(rule.get("conditions_relation")))
                continue
            print(" mail_ids matching with the conditions : {}".format(result_email_ids))
            if result_email_ids:
                ActionsController(self, result_email_ids).validate_action()

def intersection_list(list_of_lists):
    common_set = set(list_of_lists[0])
    for sublist in list_of_lists[1:]:
        common_set.intersection_update(sublist)

    common_values = list(common_set)
    return common_values



def flatten_list(nested_list):
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten_list(item))
        else:
            flattened_list.append(item)
    return flattened_list


def string_fields_validation(field_value, operator, matching_value):
    if operator == "equals":
        return field_value == matching_value
    elif operator == "not-equals":
        return field_value != matching_value
    elif operator == "contains":
        return matching_value.lower() in field_value.lower()
    elif operator == "not-contains":
        return matching_value.lower() not in field_value.lower()

class SenderIdEvaluator:
    def __init__(self):
        self.field_name = "sender_id"
        self.applicable_operations = ["equals", "not-equals", "contains", "not-contains"]

    def is_valid_operator(self, condition):
        if condition.get("operator") not in self.applicable_operations:
            return False
        return True

    def evaluate(self, condition, dataset):
        matching_email_ids = []
        for each in dataset:
            if string_fields_validation(each.get(self.field_name), condition.get("operator"), condition.get("value")):
                matching_email_ids.append(each["email_id"])
        return matching_email_ids

EVALUATOR_OBJ_MAP = {
    "sender_id": SenderIdEvaluator
}