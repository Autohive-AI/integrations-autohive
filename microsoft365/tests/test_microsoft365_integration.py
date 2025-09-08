import unittest
from unittest.mock import AsyncMock, Mock, patch
import json
from context import microsoft365

class TestMicrosoft365Integration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()
    
    async def test_send_email_success(self):
        """Test successful email sending."""
        # Mock successful API response
        self.mock_context.fetch.return_value = None
        
        # Create action handler
        handler = microsoft365.SendEmailAction()
        
        # Test inputs
        inputs = {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test email",
            "body_type": "Text"
        }
        
        # Execute action
        result = await handler.execute(inputs, self.mock_context)
        
        # Verify result
        self.assertTrue(result["result"])
        
        # Verify API call
        self.mock_context.fetch.assert_called_once()
        call_args = self.mock_context.fetch.call_args
        self.assertIn("sendMail", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")
    
    async def test_send_email_with_cc_bcc(self):
        """Test email sending with CC and BCC."""
        self.mock_context.fetch.return_value = None
        
        handler = microsoft365.SendEmailAction()
        inputs = {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "Test body",
            "cc": ["cc@example.com"],
            "bcc": ["bcc@example.com"]
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        
        # Check that the API was called with CC and BCC recipients
        call_args = self.mock_context.fetch.call_args
        email_data = call_args[1]["json"]
        self.assertIn("ccRecipients", email_data["message"])
        self.assertIn("bccRecipients", email_data["message"])
    
    async def test_create_calendar_event_success(self):
        """Test successful calendar event creation."""
        # Mock API response
        mock_response = {
            "id": "event123",
            "webLink": "https://outlook.office365.com/calendar/event123"
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = microsoft365.CreateCalendarEventAction()
        inputs = {
            "subject": "Test Event",
            "start_time": "2024-08-01T14:00:00Z",
            "end_time": "2024-08-01T15:00:00Z",
            "location": "Conference Room",
            "attendees": ["attendee@example.com"]
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(result["id"], "event123")
        self.assertIn("webLink", result)
    
    async def test_upload_file_success(self):
        """Test successful file upload."""
        # Mock API response
        mock_response = {
            "id": "file123",
            "webUrl": "https://onedrive.com/file123",
            "size": 1024,
            "@microsoft.graph.downloadUrl": "https://download.url"
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = microsoft365.UploadFileAction()
        inputs = {
            "filename": "test.txt",
            "content": "Test content",
            "content_type": "text/plain",
            "folder_path": "/Documents"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(result["id"], "file123")
        self.assertEqual(result["size"], 1024)
    
    async def test_list_files_success(self):
        """Test successful file listing."""
        # Mock API response
        mock_response = {
            "value": [
                {
                    "id": "file1",
                    "name": "document.pdf",
                    "size": 2048,
                    "lastModifiedDateTime": "2024-08-01T10:00:00Z",
                    "webUrl": "https://onedrive.com/file1"
                },
                {
                    "id": "folder1",
                    "name": "My Folder",
                    "lastModifiedDateTime": "2024-08-01T09:00:00Z",
                    "webUrl": "https://onedrive.com/folder1",
                    "folder": {}
                }
            ]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = microsoft365.ListFilesAction()
        inputs = {"folder_path": "/", "limit": 100}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(len(result["files"]), 2)
        self.assertFalse(result["files"][0]["is_folder"])  # document.pdf
        self.assertTrue(result["files"][1]["is_folder"])   # My Folder
    
    async def test_error_handling(self):
        """Test error handling in actions."""
        # Mock API error
        self.mock_context.fetch.side_effect = Exception("API Error")
        
        handler = microsoft365.SendEmailAction()
        inputs = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test"
        }
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertFalse(result["result"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API Error")

if __name__ == '__main__':
    unittest.main()