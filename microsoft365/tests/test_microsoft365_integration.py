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
        self.assertEqual(result["metadata"]["id"], "file123")
        self.assertEqual(result["file"]["name"], "document.docx")
        self.assertEqual(result["metadata"]["size"], 2048)
        self.assertEqual(result["file"]["contentType"], "application/pdf")
        self.assertIsNotNone(result["file"]["content"])  # Should have base64 encoded PDF
        
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
        self.assertEqual(result["file"]["name"], "notes.txt")
        self.assertEqual(result["file"]["contentType"], "text/plain")
        self.assertIsNotNone(result["file"]["content"])  # Should have base64 encoded content
        
        # Check content call (no PDF conversion for text file)
        content_call = self.mock_context.fetch.call_args_list[1]
        self.assertIn("/drive/items/file456/content", content_call[0][0])
        self.assertNotIn("format=pdf", content_call[0][0])

    @patch('microsoft365.microsoft365.fetch_binary_content')
    async def test_read_onedrive_file_content_native_pdf(self, mock_fetch_binary):
        """Test file content reading for native PDF files."""
        # Mock metadata response for PDF file
        mock_metadata = {
            "id": "file789",
            "name": "AICPA_SOC2_Compliance_Guide_on_AWS.pdf",
            "size": 755287,
            "mimeType": "application/pdf",
            "webUrl": "https://onedrive.com/file789"
        }

        # Mock PDF binary content
        mock_content = b"%PDF-1.4\n%\xc4\xe5\xf2\xe5\xeb\xa7\xf3\xa0\xd0\xc4\xc6 Native PDF content with binary data"

        # Mock context.fetch for metadata and fetch_binary_content for content
        self.mock_context.fetch.return_value = mock_metadata
        mock_fetch_binary.return_value = mock_content

        handler = microsoft365.ReadOneDriveFileContentAction()
        inputs = {"file_id": "file789"}

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["file"]["name"], "AICPA_SOC2_Compliance_Guide_on_AWS.pdf")
        self.assertEqual(result["file"]["contentType"], "application/pdf")
        self.assertIsNotNone(result["file"]["content"])  # Should have base64 encoded content

        # Verify binary fetch was called with correct URL
        mock_fetch_binary.assert_called_once()
        call_args = mock_fetch_binary.call_args[0]
        self.assertIn("/drive/items/file789/content", call_args[0])
        self.assertNotIn("format=pdf", call_args[0])

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
        
        self.assertFalse(result["result"])  # Operation fails when content retrieval fails
        self.assertEqual(result["file"]["name"], "restricted.pdf")
        self.assertEqual(result["file"]["content"], "")  # Empty content on failure
        self.assertIn("Access denied", result["error"])


class TestCreateDraftEmailAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for draft email tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    async def test_create_draft_email_success(self):
        """Test successful draft email creation."""
        # Mock API response
        mock_response = {
            "id": "draft123",
            "subject": "Test Draft",
            "createdDateTime": "2024-08-20T10:00:00Z",
            "isDraft": True
        }
        self.mock_context.fetch.return_value = mock_response

        handler = microsoft365.CreateDraftEmailAction()
        inputs = {
            "subject": "Test Draft",
            "body": "This is a test draft",
            "body_type": "Text",
            "to_recipients": ["test@example.com"]
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["draft_id"], "draft123")
        self.assertEqual(result["subject"], "Test Draft")
        self.assertTrue(result["is_draft"])

        # Verify API call
        self.mock_context.fetch.assert_called_once()
        call_args = self.mock_context.fetch.call_args
        self.assertIn("/me/messages", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")

    async def test_create_draft_email_with_all_recipients(self):
        """Test draft creation with CC and BCC recipients."""
        mock_response = {
            "id": "draft456",
            "subject": "Complete Draft",
            "createdDateTime": "2024-08-20T10:00:00Z",
            "isDraft": True
        }
        self.mock_context.fetch.return_value = mock_response

        handler = microsoft365.CreateDraftEmailAction()
        inputs = {
            "subject": "Complete Draft",
            "body": "Draft with all recipient types",
            "to_recipients": [{"address": "to@example.com", "name": "To User"}],
            "cc_recipients": ["cc@example.com"],
            "bcc_recipients": [{"address": "bcc@example.com"}],
            "importance": "High"
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["draft_id"], "draft456")

        # Check the message structure in the API call
        call_args = self.mock_context.fetch.call_args
        message_body = call_args[1]["json"]
        self.assertIn("ccRecipients", message_body)
        self.assertIn("bccRecipients", message_body)
        self.assertEqual(message_body["importance"], "High")


class TestSendDraftEmailAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for send draft tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    async def test_send_draft_email_success(self):
        """Test successful draft sending."""
        # Mock API response (202 Accepted with no body)
        self.mock_context.fetch.return_value = None

        handler = microsoft365.SendDraftEmailAction()
        inputs = {"draft_id": "draft123"}

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["draft_id"], "draft123")
        self.assertEqual(result["status"], "sent")

        # Verify API call
        call_args = self.mock_context.fetch.call_args
        self.assertIn("/me/messages/draft123/send", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")
        self.assertEqual(call_args[1]["headers"]["Content-Length"], "0")


class TestReplyToEmailAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for reply tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    async def test_reply_to_email_success(self):
        """Test successful email reply."""
        # Mock API response (202 Accepted with no body)
        self.mock_context.fetch.return_value = None

        handler = microsoft365.ReplyToEmailAction()
        inputs = {
            "message_id": "msg123",
            "comment": "Thanks for the email!"
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["message_id"], "msg123")
        self.assertEqual(result["operation"], "reply")
        self.assertEqual(result["status"], "sent")

        # Verify API call
        call_args = self.mock_context.fetch.call_args
        self.assertIn("/me/messages/msg123/reply", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")
        self.assertEqual(call_args[1]["json"]["comment"], "Thanks for the email!")

    async def test_reply_to_email_without_comment(self):
        """Test email reply without comment."""
        self.mock_context.fetch.return_value = None

        handler = microsoft365.ReplyToEmailAction()
        inputs = {"message_id": "msg456"}

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["message_id"], "msg456")

        # Verify API call with empty JSON body
        call_args = self.mock_context.fetch.call_args
        self.assertEqual(call_args[1]["json"], {})


class TestForwardEmailAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for forward tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    async def test_forward_email_success(self):
        """Test successful email forwarding."""
        # Mock API response (202 Accepted with no body)
        self.mock_context.fetch.return_value = None

        handler = microsoft365.ForwardEmailAction()
        inputs = {
            "message_id": "msg789",
            "to_recipients": ["forward@example.com", {"address": "user@test.com", "name": "Test User"}],
            "comment": "FYI"
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["message_id"], "msg789")
        self.assertEqual(result["operation"], "forward")
        self.assertEqual(result["status"], "sent")

        # Verify API call
        call_args = self.mock_context.fetch.call_args
        self.assertIn("/me/messages/msg789/forward", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")

        # Check recipients structure
        forward_data = call_args[1]["json"]
        self.assertEqual(len(forward_data["toRecipients"]), 2)
        self.assertEqual(forward_data["comment"], "FYI")


class TestDownloadEmailAttachmentAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for attachment download tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    @patch('microsoft365.microsoft365.fetch_binary_content')
    async def test_download_attachment_success(self, mock_fetch_binary):
        """Test successful attachment download."""
        # Mock attachment metadata
        mock_metadata = {
            "id": "att123",
            "name": "document.pdf",
            "contentType": "application/pdf",
            "size": 1024,
            "isInline": False
        }

        # Mock binary content
        mock_binary_content = b"PDF binary data here"

        self.mock_context.fetch.return_value = mock_metadata
        mock_fetch_binary.return_value = mock_binary_content

        handler = microsoft365.DownloadEmailAttachmentAction()
        inputs = {
            "message_id": "msg123",
            "attachment_id": "att123",
            "include_content": True
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["attachment"]["id"], "att123")
        self.assertEqual(result["attachment"]["name"], "document.pdf")
        self.assertEqual(result["attachment"]["content_type"], "application/pdf")
        self.assertIsNotNone(result["attachment"]["content"])  # Base64 encoded

        # Verify API calls
        self.mock_context.fetch.assert_called_once()
        mock_fetch_binary.assert_called_once()

    async def test_download_attachment_metadata_only(self):
        """Test attachment metadata retrieval without content."""
        mock_metadata = {
            "id": "att456",
            "name": "image.jpg",
            "contentType": "image/jpeg",
            "size": 2048,
            "isInline": True
        }

        self.mock_context.fetch.return_value = mock_metadata

        handler = microsoft365.DownloadEmailAttachmentAction()
        inputs = {
            "message_id": "msg456",
            "attachment_id": "att456",
            "include_content": False
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["attachment"]["content"], "")  # No content
        self.assertTrue(result["attachment"]["is_inline"])


class TestSearchEmailsAction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for search tests."""
        self.mock_context = Mock()
        self.mock_context.fetch = AsyncMock()

    async def test_search_emails_success(self):
        """Test successful email search."""
        # Mock search API response
        mock_response = {
            "value": [{
                "hitsContainers": [{
                    "total": 2,
                    "hits": [
                        {
                            "resource": {
                                "id": "msg1",
                                "subject": "Project Update",
                                "from": {
                                    "emailAddress": {
                                        "address": "sender@example.com",
                                        "name": "Sender Name"
                                    }
                                },
                                "receivedDateTime": "2024-08-20T10:00:00Z",
                                "bodyPreview": "Here is the project update...",
                                "hasAttachments": True
                            }
                        },
                        {
                            "resource": {
                                "id": "msg2",
                                "subject": "Meeting Notes",
                                "from": {
                                    "emailAddress": {
                                        "address": "colleague@example.com",
                                        "name": "Colleague"
                                    }
                                },
                                "receivedDateTime": "2024-08-19T15:30:00Z",
                                "bodyPreview": "Notes from today's meeting...",
                                "hasAttachments": False
                            }
                        }
                    ]
                }]
            }]
        }

        self.mock_context.fetch.return_value = mock_response

        handler = microsoft365.SearchEmailsAction()
        inputs = {
            "query": "project meeting",
            "limit": 25,
            "enable_top_results": True
        }

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["query"], "project meeting")
        self.assertEqual(result["total_results"], 2)
        self.assertEqual(len(result["messages"]), 2)

        # Check first message structure
        first_msg = result["messages"][0]
        self.assertEqual(first_msg["message_id"], "msg1")
        self.assertEqual(first_msg["subject"], "Project Update")
        self.assertTrue(first_msg["has_attachments"])

        # Verify API call
        call_args = self.mock_context.fetch.call_args
        self.assertIn("search/query", call_args[0][0])
        self.assertEqual(call_args[1]["method"], "POST")

        # Check search request structure
        search_request = call_args[1]["json"]["requests"][0]
        self.assertEqual(search_request["entityTypes"], ["message"])
        self.assertEqual(search_request["query"]["queryString"], "project meeting")
        self.assertTrue(search_request["enableTopResults"])

    async def test_search_emails_no_results(self):
        """Test search with no results."""
        mock_response = {
            "value": [{
                "hitsContainers": [{
                    "total": 0,
                    "hits": []
                }]
            }]
        }

        self.mock_context.fetch.return_value = mock_response

        handler = microsoft365.SearchEmailsAction()
        inputs = {"query": "nonexistent"}

        result = await handler.execute(inputs, self.mock_context)

        self.assertTrue(result["result"])
        self.assertEqual(result["total_results"], 0)
        self.assertEqual(len(result["messages"]), 0)


if __name__ == '__main__':
    unittest.main()