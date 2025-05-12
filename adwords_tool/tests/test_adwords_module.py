import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory (adwords_tool) to the Python path
# to allow importing adwords_module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adwords_module import AdwordsCampaignAction, parse_date_range

class TestAdwordsModule(unittest.TestCase):

    def test_parse_date_range_predefined(self):
        # Test predefined ranges (actual dates will vary based on current date)
        # We're mostly testing that it doesn't raise an error for valid inputs
        self.assertIsNotNone(parse_date_range("last_7_days"))
        self.assertIsNotNone(parse_date_range("prev_7_days"))

    def test_parse_date_range_custom(self):
        expected = {"start_date": "2023-01-01", "end_date": "2023-01-31"}
        self.assertEqual(parse_date_range("2023-01-01_2023-01-31"), expected)

    def test_parse_date_range_invalid(self):
        with self.assertRaises(ValueError):
            parse_date_range("invalid_range_format")
        with self.assertRaises(ValueError):
            parse_date_range("2023-13-01_2023-01-31") # Invalid month

    @patch('adwords_module.GoogleAdsClient')
    def test_adwords_campaign_action_initialization_success(self, MockGoogleAdsClient):
        # Test successful initialization if google-ads.yaml is supposedly loadable
        mock_client_instance = MockGoogleAdsClient.load_from_storage.return_value
        action = AdwordsCampaignAction()
        self.assertIsNotNone(action.client)
        MockGoogleAdsClient.load_from_storage.assert_called_once_with("google-ads.yaml")

    @patch('adwords_module.GoogleAdsClient')
    def test_adwords_campaign_action_initialization_failure(self, MockGoogleAdsClient):
        # Test initialization failure if google-ads.yaml loading fails
        MockGoogleAdsClient.load_from_storage.side_effect = Exception("File not found")
        action = AdwordsCampaignAction()
        self.assertIsNone(action.client) # Or check for specific error handling if implemented
        # Optionally, check logger call if action.client remains None due to error

    @patch('adwords_module.GoogleAdsClient')
    def test_execute_success(self, MockGoogleAdsClient):
        # Mock the GoogleAdsClient and its chained calls (get_service, search)
        mock_ads_client = MockGoogleAdsClient.load_from_storage.return_value
        mock_ga_service = mock_ads_client.get_service.return_value
        
        # Mock the response from ga_service.search
        # Create a mock row that proto.Message.to_dict can process
        mock_proto_message = MagicMock()
        # Simulate the structure that to_dict would expect for a simple case
        # This needs to be more detailed if specific fields are accessed directly in to_dict's output
        # For now, assume to_dict returns a dict directly
        mock_row_dict = {
            'campaign': {'id': '123', 'name': 'Test Campaign', 'status': 'ENABLED', 'bidding_strategy_system_status': 'ACTIVE', 'advertising_channel_type': 'SEARCH', 'optimization_score': 0.8, 'bidding_strategy_type': 'MANUAL_CPC'},
            'metrics': {'cost_micros': 1000000, 'impressions': 100, 'clicks': 10, 'conversions_value': 50.0, 'all_conversions': 5, 'average_cpc': 100000, 'cost_per_conversion': 200000, 'average_cpv': 0, 'interactions':10, 'interaction_rate': 0.1, 'average_cost': 1000000},
            'customer': {'currency_code': 'USD', 'descriptive_name': 'Test Account'},
            'campaign_budget': {'amount_micros': 50000000}
        }
        # For simplicity, making proto.Message.to_dict return our mock_row_dict
        # In a real scenario, you'd mock the iterator of rows, and each row would be a proto message.
        with patch('adwords_module.proto.Message') as MockProtoMessage:
            MockProtoMessage.to_dict.return_value = mock_row_dict
            mock_ga_service.search.return_value = [mock_proto_message] # Simulate a list of one row

            action = AdwordsCampaignAction()
            action.client = mock_ads_client # Ensure the action uses our mocked client

            context = MagicMock() # Mock ExecutionContext if its methods are used
            action_inputs = {
                'customer_id': 'test_customer_id',
                'date_ranges': ['2023-01-01_2023-01-15']
            }
            
            result = action.execute(context, action_inputs)

            self.assertIsNotNone(result)
            self.assertNotIn('error', result[0]) # Assuming result is a list of date range results
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['date_range'], '2023-01-01 to 2023-01-15')
            self.assertEqual(len(result[0]['data']), 1)
            self.assertEqual(result[0]['data'][0]['Campaign ID'], '123')
            mock_ga_service.search.assert_called_once()

    @patch('adwords_module.GoogleAdsClient')
    def test_execute_missing_customer_id(self, MockGoogleAdsClient):
        action = AdwordsCampaignAction()
        action.client = MockGoogleAdsClient.load_from_storage.return_value 
        context = MagicMock()
        action_inputs = {'date_ranges': ['last_7_days']}
        result = action.execute(context, action_inputs)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Customer ID is required')

    @patch('adwords_module.GoogleAdsClient')
    def test_execute_google_api_error(self, MockGoogleAdsClient):
        mock_ads_client = MockGoogleAdsClient.load_from_storage.return_value
        mock_ga_service = mock_ads_client.get_service.return_value
        mock_ga_service.search.side_effect = Exception("API Error")

        action = AdwordsCampaignAction()
        action.client = mock_ads_client
        context = MagicMock()
        action_inputs = {
            'customer_id': 'test_customer_id',
            'date_ranges': ['2023-01-01_2023-01-15']
        }
        result = action.execute(context, action_inputs)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertIn('error', result[0])
        self.assertTrue("Failed to retrieve data: API Error" in result[0]['error'])

if __name__ == '__main__':
    unittest.main() 