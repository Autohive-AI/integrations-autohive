import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import sys

# Add the parent directory (adwords_tool) to the Python path
# to allow importing adwords_module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patch Integration.load at the module level before importing adwords_module
# This prevents it from trying to load a real config.json during test collection/setup
with patch('adwords_module.Integration.load', return_value=MagicMock()) as mock_integration_load:
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
    @patch('adwords_module.proto.Message')
    def test_execute_success(self, MockProtoMessage, MockGoogleAdsClient):
        # Mock the GoogleAdsClient.load_from_dict to return our mock client instance
        mock_ads_client_instance = MockGoogleAdsClient.load_from_dict.return_value
        mock_ga_service = mock_ads_client_instance.get_service.return_value

        mock_row_dict = {
            'campaign': {'id': '123', 'name': 'Test Campaign', 'status': 'ENABLED', 'bidding_strategy_system_status': 'ACTIVE', 'advertising_channel_type': 'SEARCH', 'optimization_score': 0.8, 'bidding_strategy_type': 'MANUAL_CPC'},
            'metrics': {'cost_micros': 1000000, 'impressions': 100, 'clicks': 10, 'conversions_value': 50.0, 'all_conversions': 5, 'average_cpc': 100000, 'cost_per_conversion': 200000, 'average_cpv': 0, 'interactions':10, 'interaction_rate': 0.1, 'average_cost': 1000000},
            'customer': {'currency_code': 'USD', 'descriptive_name': 'Test Account'},
            'campaign_budget': {'amount_micros': 50000000}
        }
        MockProtoMessage.to_dict.return_value = mock_row_dict
        mock_ga_service.search.return_value = [MagicMock()] # Simulate a list of one row object

        action = AdwordsCampaignAction()
        
        context = MagicMock()
        # Mock context.auth.get calls
        context.auth.get.side_effect = lambda key: {
            "refresh_token": "fake_refresh_token",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret"
        }.get(key)
        
        # Mock context.config.get calls
        context.config.get.side_effect = lambda key: {
            "developer_token": "fake_dev_token",
            "login_customer_id": "fake_login_cid" # Optional
        }.get(key)

        action_inputs = {
            'customer_id': 'test_customer_id',
            'date_ranges': ['2023-01-01_2023-01-15']
        }
            
        result = action.execute(context, action_inputs)

        MockGoogleAdsClient.load_from_dict.assert_called_once_with({
            "developer_token": "fake_dev_token",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
            "use_proto_plus": True,
            "login_customer_id": "fake_login_cid"
        })
        self.assertIsNotNone(result)
        self.assertNotIn('error', result[0])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['date_range'], '2023-01-01 to 2023-01-15')
        self.assertEqual(len(result[0]['data']), 1)
        self.assertEqual(result[0]['data'][0]['Campaign ID'], '123')
        mock_ga_service.search.assert_called_once()

    @patch('adwords_module.GoogleAdsClient')
    def test_execute_missing_customer_id(self, MockGoogleAdsClient):
        # Mock client initialization as it happens before customer_id check
        MockGoogleAdsClient.load_from_dict.return_value = MagicMock()

        action = AdwordsCampaignAction()
        context = MagicMock()
        # Mock context.auth.get calls
        context.auth.get.side_effect = lambda key: {
            "refresh_token": "fake_refresh_token",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret"
        }.get(key)
        # Mock context.config.get calls
        context.config.get.side_effect = lambda key: {
            "developer_token": "fake_dev_token"
        }.get(key)
        
        action_inputs = {'date_ranges': ['last_7_days']} # Missing customer_id
        result = action.execute(context, action_inputs)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Customer ID is required')
        MockGoogleAdsClient.load_from_dict.assert_called_once() # Ensure client init was attempted

    @patch('adwords_module.GoogleAdsClient')
    def test_execute_google_api_error(self, MockGoogleAdsClient):
        mock_ads_client_instance = MockGoogleAdsClient.load_from_dict.return_value
        mock_ga_service = mock_ads_client_instance.get_service.return_value
        mock_ga_service.search.side_effect = Exception("API Error")

        action = AdwordsCampaignAction()
        context = MagicMock()
        # Mock context.auth.get calls
        context.auth.get.side_effect = lambda key: {
            "refresh_token": "fake_refresh_token",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret"
        }.get(key)
        # Mock context.config.get calls
        context.config.get.side_effect = lambda key: {
            "developer_token": "fake_dev_token"
        }.get(key)

        action_inputs = {
            'customer_id': 'test_customer_id',
            'date_ranges': ['2023-01-01_2023-01-15']
        }
        result = action.execute(context, action_inputs)
        
        MockGoogleAdsClient.load_from_dict.assert_called_once()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertIn('error', result[0])
        self.assertTrue("Failed to retrieve data: API Error" in result[0]['error'])

if __name__ == '__main__':
    unittest.main() 