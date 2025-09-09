import unittest
from unittest.mock import AsyncMock, Mock, patch
import json
from context import zoho

class TestZohoIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()
        self.mock_context.auth = {
            'credentials': {
                'access_token': 'test_access_token'
            }
        }
    
    async def test_create_contact_success(self):
        """Test successful contact creation."""
        # Mock successful API response
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {
                    "id": "123456789"
                },
                "message": "record added"
            }]
        }
        self.mock_context.fetch.return_value = mock_response
        
        # Create action handler
        handler = zoho.CreateContactAction()
        
        # Test inputs
        inputs = {
            "Last_Name": "Smith",
            "First_Name": "John",
            "Email": "john.smith@example.com",
            "Phone": "+1-555-0123",
            "Account_Name": "Acme Corporation"
        }
        
        # Execute action
        result = await handler.execute(inputs, self.mock_context)
        
        # Verify result
        self.assertEqual(result["id"], "123456789")
        self.assertEqual(result["status"], "SUCCESS")
        
        # Verify API call
        self.mock_context.fetch.assert_called_once()
        call_args = self.mock_context.fetch.call_args
        self.assertIn("Contacts", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")
    
    async def test_get_contact_success(self):
        """Test successful contact retrieval."""
        # Mock API response
        mock_response = {
            "data": [{
                "id": "123456789",
                "Last_Name": "Smith",
                "First_Name": "John",
                "Email": "john.smith@example.com",
                "Phone": "+1-555-0123"
            }]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.GetContactAction()
        inputs = {"contact_id": "123456789"}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(result["id"], "123456789")
        self.assertEqual(result["Last_Name"], "Smith")
        self.assertEqual(result["Email"], "john.smith@example.com")
    
    async def test_create_deal_success(self):
        """Test successful deal creation."""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {
                    "id": "987654321"
                },
                "message": "record added"
            }]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.CreateDealAction()
        inputs = {
            "Deal_Name": "Q4 Enterprise Software Deal",
            "Amount": 50000,
            "Stage": "Proposal/Price Quote",
            "Account_Name": "Acme Corporation"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(result["id"], "987654321")
        self.assertEqual(result["status"], "SUCCESS")
        
        # Verify API call structure
        call_args = self.mock_context.fetch.call_args
        self.assertIn("Deals", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")
    
    async def test_convert_lead_success(self):
        """Test successful lead conversion."""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {
                    "Contacts": "111111111",
                    "Accounts": "222222222", 
                    "Deals": "333333333"
                }
            }]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.ConvertLeadAction()
        inputs = {
            "lead_id": "456789123",
            "convert_to_contact": True,
            "convert_to_account": True,
            "convert_to_deal": True
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(result["contact_id"], "111111111")
        self.assertEqual(result["account_id"], "222222222")
        self.assertEqual(result["deal_id"], "333333333")
    
    async def test_list_contacts_success(self):
        """Test successful contact listing with pagination."""
        mock_response = {
            "data": [
                {
                    "id": "123456789",
                    "Last_Name": "Smith",
                    "First_Name": "John",
                    "Email": "john.smith@example.com"
                },
                {
                    "id": "987654321",
                    "Last_Name": "Johnson",
                    "First_Name": "Jane",
                    "Email": "jane.johnson@example.com"
                }
            ],
            "info": {
                "count": 2,
                "page": 1,
                "per_page": 200,
                "more_records": False
            }
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.ListContactsAction()
        inputs = {"page": 1, "per_page": 200}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(len(result["contacts"]), 2)
        self.assertEqual(result["info"]["count"], 2)
        self.assertFalse(result["info"]["more_records"])
    
    async def test_execute_coql_query_success(self):
        """Test successful COQL query execution."""
        mock_response = {
            "data": [
                {
                    "First_Name": "John",
                    "Last_Name": "Smith", 
                    "Email": "john.smith@example.com",
                    "Account_Name": "Acme Corporation"
                }
            ],
            "info": {
                "count": 1,
                "more_records": False
            }
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.ExecuteCoqlQueryAction()
        inputs = {
            "query": "SELECT First_Name, Last_Name, Email, Account_Name FROM Contacts WHERE Lead_Source = 'Website'"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["Email"], "john.smith@example.com")
        self.assertEqual(result["info"]["count"], 1)
    
    async def test_create_task_success(self):
        """Test successful task creation."""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {
                    "id": "555666777"
                },
                "message": "record added"
            }]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.CreateTaskAction()
        inputs = {
            "Subject": "Follow up with lead",
            "Status": "Not Started",
            "Priority": "High",
            "Due_Date": "2024-12-31"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(result["id"], "555666777")
        self.assertEqual(result["status"], "SUCCESS")
    
    async def test_get_related_records_success(self):
        """Test successful related records retrieval."""
        mock_response = {
            "data": [
                {
                    "id": "111111111",
                    "Last_Name": "Smith",
                    "First_Name": "John",
                    "Email": "john.smith@example.com"
                }
            ],
            "info": {
                "count": 1,
                "more_records": False
            }
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = zoho.GetRelatedRecordsAction()
        inputs = {
            "module_api_name": "Accounts",
            "record_id": "123456789",
            "related_list_api_name": "Contacts"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(len(result["related_records"]), 1)
        self.assertEqual(result["related_records"][0]["Email"], "john.smith@example.com")
    
    async def test_authentication_headers(self):
        """Test that proper authentication headers are built."""
        from zoho import build_zoho_headers
        
        headers = build_zoho_headers(self.mock_context)
        
        self.assertEqual(headers["Authorization"], "Zoho-oauthtoken test_access_token")
        self.assertEqual(headers["Content-Type"], "application/json")
    
    async def test_error_handling(self):
        """Test error handling in actions."""
        # Mock API error
        self.mock_context.fetch.side_effect = Exception("API Rate Limit Exceeded")
        
        handler = zoho.CreateContactAction()
        inputs = {
            "Last_Name": "Smith"
        }
        
        # Should raise the exception for proper error handling
        with self.assertRaises(Exception) as context:
            await handler.execute(inputs, self.mock_context)
        
        self.assertEqual(str(context.exception), "API Rate Limit Exceeded")
    
    async def test_field_validation(self):
        """Test input field validation and data building."""
        from zoho import build_contact_data
        
        inputs = {
            "Last_Name": "Smith",
            "First_Name": "John",
            "Email": "john.smith@example.com",
            "Phone": "+1-555-0123",
            "": "",  # Empty field should be filtered out
            "Account_Name": None  # None field should be filtered out
        }
        
        contact_data = build_contact_data(inputs)
        
        self.assertEqual(contact_data["Last_Name"], "Smith")
        self.assertEqual(contact_data["Email"], "john.smith@example.com")
        self.assertNotIn("", contact_data)  # Empty key should not be included
        self.assertNotIn("Account_Name", contact_data)  # None value should not be included
    
    def test_api_url_building(self):
        """Test API URL building helper function."""
        from zoho import get_zoho_api_url
        
        base_url = get_zoho_api_url()
        self.assertEqual(base_url, "https://www.zohoapis.com.au/crm/v8")
        
        contacts_url = get_zoho_api_url("/Contacts")
        self.assertEqual(contacts_url, "https://www.zohoapis.com.au/crm/v8/Contacts")

if __name__ == '__main__':
    unittest.main()
