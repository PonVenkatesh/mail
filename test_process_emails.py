import unittest
from unittest.mock import patch, Mock

from process_emails import main

class TestMainFunction(unittest.TestCase):
    @patch('process_emails.RulesEvaluator')  # Mock the RulesEvaluator class
    @patch('process_emails.fetch_data_from_postgres', return_value=[{'example': 'data'}])
    @patch('process_emails.json.load', return_value={'rules': [{'example_rule': 'value'}]})
    @patch('process_emails.os.path.exists', return_value=True)
    @patch('process_emails.open', create=True)
    def test_main_function(self, mock_open, mock_path_exists, mock_json_load, mock_fetch_data, mock_rules_evaluator):
        main()

        mock_fetch_data.assert_called_once()
        mock_path_exists.assert_called_once_with('rules/rules_test.json')
        mock_json_load.assert_called_once_with(mock_open.return_value.__enter__.return_value)
        mock_rules_evaluator.assert_called_once_with([{'example': 'data'}], [{'example_rule': 'value'}])

if __name__ == '__main__':
    unittest.main()
