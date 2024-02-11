import json
import os

from postgres.postgres import fetch_data_from_postgres
from rules.rules_evaluator import RulesEvaluator


def main():
    gmail_data = fetch_data_from_postgres()
    rules = []
    print(len(gmail_data))
    if gmail_data:
        json_filename = "rules_test.json"

        # Create the full path to the JSON file
        json_filepath = os.path.join("rules", json_filename)

        rules = []
        # Check if the file exists before reading
        if os.path.exists(json_filepath):
            print("in")
            with open(json_filepath, 'r') as json_file:
                try:
                    rules = json.load(json_file).get("rules", [])

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

        else:
            print(f"File not found: {json_filepath}")
        if rules:
            print("here")
            RulesEvaluator(gmail_data, rules).evaluate()

    else:
        print(" Unable to fetch gmail data / Postgres is empty")




if __name__ == "__main__":
    main()

