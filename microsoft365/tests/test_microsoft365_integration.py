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
        self.assertIsNone(result["files"][0]["folder"])     # document.pdf (no folder facet)
        self.assertIsNotNone(result["files"][1]["folder"]) # My Folder (has folder facet)
    
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
    
    async def test_search_onedrive_files_success(self):
        """Test successful OneDrive file search."""
        # Mock API response
        mock_response = {
            "value": [
                {
                    "id": "file123",
                    "name": "quarterly-report.docx", 
                    "size": 4096,
                    "lastModifiedDateTime": "2024-08-01T10:00:00Z",
                    "webUrl": "https://onedrive.com/file123",
                    "file": {
                        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    }
                },
                {
                    "id": "folder456",
                    "name": "Documents",
                    "lastModifiedDateTime": "2024-08-01T09:00:00Z", 
                    "webUrl": "https://onedrive.com/folder456",
                    "folder": {"childCount": 10}
                }
            ]
        }
        self.mock_context.fetch.return_value = mock_response
        
        handler = microsoft365.SearchOneDriveFilesAction()
        inputs = {"query": "quarterly report", "limit": 10}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(result["query"], "quarterly report")
        
        # Check file item structure
        file_item = result["files"][0]
        self.assertEqual(file_item["id"], "file123")
        self.assertEqual(file_item["name"], "quarterly-report.docx")
        self.assertIn("file", file_item)
        
        # Check folder item structure
        folder_item = result["files"][1] 
        self.assertEqual(folder_item["id"], "folder456")
        self.assertIn("folder", folder_item)
        
        # Verify API call with URL encoding
        call_args = self.mock_context.fetch.call_args
        api_url = call_args[0][0]
        self.assertIn("search(q='quarterly%20report')", api_url)
    
    async def test_read_onedrive_file_content_success(self):
        """Test successful OneDrive file content reading."""
        # Mock metadata response
        mock_metadata = {
            "id": "file123",
            "name": "document.docx",
            "size": 2048,
            "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "webUrl": "https://onedrive.com/file123"
        }
        
        # Mock content response (PDF conversion)
        mock_content = b"%PDF-1.4\n%fake PDF content for testing"
        
        # Set up multiple return values for the two API calls
        self.mock_context.fetch.side_effect = [mock_metadata, mock_content]
        
        handler = microsoft365.ReadOneDriveFileContentAction()
        inputs = {"file_id": "file123"}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(result["file_id"], "file123")
        self.assertEqual(result["name"], "document.docx")
        self.assertEqual(result["size"], 2048)
        self.assertTrue(result["content_available"])
        self.assertIn("retrieved and available", result["content_info"])
        
        # Verify both API calls were made
        self.assertEqual(self.mock_context.fetch.call_count, 2)
        
        # Check metadata call
        metadata_call = self.mock_context.fetch.call_args_list[0]
        self.assertIn("/drive/items/file123", metadata_call[0][0])
        self.assertIn("$select", metadata_call[1]["params"])
        
        # Check content call (PDF conversion for Office doc)
        content_call = self.mock_context.fetch.call_args_list[1]
        self.assertIn("/drive/items/file123/content", content_call[0][0])
        self.assertIn("format=pdf", content_call[0][0])
    
    async def test_read_onedrive_file_content_non_office_file(self):
        """Test file content reading for non-Office files (no PDF conversion)."""
        # Mock metadata response for text file
        mock_metadata = {
            "id": "file456", 
            "name": "notes.txt",
            "size": 512,
            "mimeType": "text/plain",
            "webUrl": "https://onedrive.com/file456"
        }
        
        # Mock content response
        mock_content = b"Sample text content"
        
        self.mock_context.fetch.side_effect = [mock_metadata, mock_content]
        
        handler = microsoft365.ReadOneDriveFileContentAction()
        inputs = {"file_id": "file456"}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])
        self.assertEqual(result["name"], "notes.txt")
        self.assertTrue(result["content_available"])
        
        # Check content call (no PDF conversion for text file)
        content_call = self.mock_context.fetch.call_args_list[1]
        self.assertIn("/drive/items/file456/content", content_call[0][0])
        self.assertNotIn("format=pdf", content_call[0][0])
    
    async def test_read_onedrive_file_content_with_content_error(self):
        """Test file content reading when content retrieval fails."""
        # Mock metadata response
        mock_metadata = {
            "id": "file789",
            "name": "restricted.pdf", 
            "size": 1024,
            "mimeType": "application/pdf",
            "webUrl": "https://onedrive.com/file789"
        }
        
        # Mock content error
        self.mock_context.fetch.side_effect = [mock_metadata, Exception("Access denied")]
        
        handler = microsoft365.ReadOneDriveFileContentAction()
        inputs = {"file_id": "file789"}
        
        result = await handler.execute(inputs, self.mock_context)
        
        self.assertTrue(result["result"])  # Operation succeeds even if content fails
        self.assertEqual(result["name"], "restricted.pdf")
        self.assertFalse(result["content_available"])
        self.assertIn("Access denied", result["content_info"])

if __name__ == '__main__':
    unittest.main()