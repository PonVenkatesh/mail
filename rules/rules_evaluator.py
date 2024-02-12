import time

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
                if condition.get("field") in list(EVALUATOR_OBJ_MAP.keys()):
                    if EVALUATOR_OBJ_MAP[condition.get("field")]().is_valid_operator(condition):
                        matching_mail_ids = EVALUATOR_OBJ_MAP[condition.get("field")]().evaluate(condition, self.email_data)
                        matching_mail_ids_per_condition_list.append(matching_mail_ids)
            print(matching_mail_ids_per_condition_list)
            if rule.get("conditions_relation", "AND") == "OR":
                result_email_ids = flatten_list(matching_mail_ids_per_condition_list)
            elif rule.get("conditions_relation", "AND") == "AND":
                result_email_ids = intersection_list(matching_mail_ids_per_condition_list)
            else:
                print(" Invalid conditions_relation : {}".format(rule.get("conditions_relation")))
                continue
            #taking unique mail_ids
            result_email_ids = list(set(result_email_ids))
            print(" mail_ids matching with the conditions : {}".format(result_email_ids))
            try:
                if result_email_ids:
                    ActionsController(self, result_email_ids, rule.get("actions", [])).validate_action().perform()
            except Exception as e:
                print(e.args[0])
                continue

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


def calculate_time_difference(epoch_timestamp):
    given_epoch = int(epoch_timestamp)
    current_epoch = int(time.time()) * 1000
    print(given_epoch)
    print(current_epoch)
    time_difference_seconds = int((current_epoch - given_epoch) / 1000)

    return time_difference_seconds

def date_fields_validation(field_value, operator, matching_value, metric):
    time_difference_seconds = calculate_time_difference(field_value)
    print(time_difference_seconds)
    print((matching_value * 3600))
    if operator == "less_than":
        if metric == "days":
            return time_difference_seconds < (matching_value * 24 * 3600)
        elif metric == "hours":
            return time_difference_seconds < (matching_value * 3600)
        elif metric == "mins":
            return time_difference_seconds < (matching_value * 60)
    elif operator == "greater_than":
        if metric == "days":
            return time_difference_seconds > (matching_value * 24 * 3600)
        elif metric == "hours":
            return time_difference_seconds > (matching_value * 3600)
        elif metric == "mins":
            return time_difference_seconds < (matching_value * 60)
    return False

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

class SubjectEvaluator:
    def __init__(self):
        self.field_name = "subject"
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

class AttachmentEvaluator:
    def __init__(self):
        self.field_name = "attachment_id"
        self.applicable_operations = ["exist"]

    def is_valid_operator(self, condition):
        if condition.get("operator") not in self.applicable_operations:
            return False
        return True

    def evaluate(self, condition, dataset):
        matching_email_ids = []
        for each in dataset:
            if each.get(self.field_name):
                matching_email_ids.append(each["email_id"])
        return matching_email_ids

class ReceivedAtEvaluator:
    def __init__(self):
        self.field_name = "received_at"
        self.applicable_operations = ["less_than", "greater_than"]

    def is_valid_operator(self, condition):
        if condition.get("operator") not in self.applicable_operations:
            return False
        return True

    def evaluate(self, condition, dataset):
        matching_email_ids = []
        for each in dataset:
            print(each.get(self.field_name))
            if each.get(self.field_name):
                print(" hereeee")
                if date_fields_validation(each.get(self.field_name), condition.get("operator"), condition.get("value"), condition.get("metric")):
                    matching_email_ids.append(each["email_id"])
        return matching_email_ids

EVALUATOR_OBJ_MAP = {
    "sender_id": SenderIdEvaluator,
    "subject": SubjectEvaluator,
    "attachment": AttachmentEvaluator,
    "received_at": ReceivedAtEvaluator
}