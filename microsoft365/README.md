# Microsoft 365 Integration for Autohive

Connects Autohive to Microsoft 365 services including Outlook, OneDrive, and Calendar through the Microsoft Graph API.

## Description

This integration provides comprehensive access to Microsoft 365 services, enabling users to manage emails, calendar events, contacts, and files through a unified interface. It interacts with the Microsoft Graph API to deliver seamless integration with Outlook email, OneDrive file storage, and Calendar management.

Key capabilities include sending and managing emails, creating and updating calendar events, uploading and accessing files, and reading contact information. The integration supports advanced features like HTML email content, file attachments, timezone-aware operations, and folder management.

## Setup & Authentication

This integration uses Microsoft Graph OAuth2 authentication through the Autohive platform. Users need to connect their Microsoft 365 account to authorize the integration.

**Authentication Method:** Platform OAuth2 (Microsoft 365)

Required Microsoft Graph API permissions:
- `Mail.ReadWrite` - Read and send emails
- `Mail.Send` - Send emails on behalf of user  
- `Files.ReadWrite` - Access OneDrive files
- `Calendars.ReadWrite` - Manage calendar events
- `Contacts.Read` - Read user contacts

**Authentication Fields:**

The integration uses platform-level OAuth2 authentication, so no manual configuration of authentication fields is required. Users simply need to authorize their Microsoft 365 account through the Autohive platform.

## Actions

### Action: `send_email`

*   **Description:** Send an email via Outlook with support for CC, BCC, and HTML content
*   **Inputs:**
    *   `to`: Recipient email address
    *   `subject`: Email subject
    *   `body`: Email body content
    *   `body_type`: Body content type (Text or HTML)
    *   `cc`: CC email addresses (optional)
    *   `bcc`: BCC email addresses (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `error`: Error message if operation failed

### Action: `list_emails`

*   **Description:** List emails for specific dates or date ranges with full content
*   **Inputs:**
    *   `start_datetime`: Start datetime for filtering (UTC)
    *   `end_datetime`: End datetime for filtering (UTC)
    *   `folder`: Email folder to search (default: Inbox)
    *   `limit`: Maximum number of emails to return
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `emails`: List of email objects with full details
    *   `error`: Error message if operation failed

### Action: `list_emails_from_contact`

*   **Description:** Get latest emails from a specific contact
*   **Inputs:**
    *   `contact_email`: Email address of the contact
    *   `limit`: Maximum number of emails to return
    *   `folder`: Email folder to search (default: Inbox)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `emails`: List of email objects from the specified contact
    *   `error`: Error message if operation failed

### Action: `read_email`

*   **Description:** Read email content and list attachment metadata
*   **Inputs:**
    *   `email_id`: Unique identifier of the email
    *   `include_attachments`: Include attachment metadata (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `email`: Complete email object with content
    *   `attachments`: List of attachment metadata (if requested)
    *   `error`: Error message if operation failed

### Action: `mark_email_read`

*   **Description:** Change the read status of emails
*   **Inputs:**
    *   `email_id`: Unique identifier of the email
    *   `is_read`: Boolean to set read status
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `error`: Error message if operation failed

### Action: `move_email_to_folder`

*   **Description:** Move emails between folders (Archive, Junk, etc.)
*   **Inputs:**
    *   `email_id`: Unique identifier of the email
    *   `destination_folder`: Target folder name
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `error`: Error message if operation failed

### Action: `create_draft_email`

*   **Description:** Create a draft email message that can be sent later
*   **Inputs:**
    *   `subject`: Email subject line
    *   `body`: Email body content
    *   `body_type`: Content type (Text or HTML, default: Text)
    *   `to_recipients`: List of recipient email addresses
    *   `cc_recipients`: List of CC recipient email addresses (optional)
    *   `bcc_recipients`: List of BCC recipient email addresses (optional)
    *   `importance`: Email importance level (Low, Normal, High)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `draft_id`: ID of the created draft
    *   `subject`: Subject of the draft
    *   `created_datetime`: When the draft was created
    *   `is_draft`: Whether this is a draft message
    *   `error`: Error message if operation failed

### Action: `send_draft_email`

*   **Description:** Send a previously created draft email
*   **Inputs:**
    *   `draft_id`: ID of the draft to send
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `draft_id`: ID of the sent draft
    *   `status`: Status of the operation
    *   `error`: Error message if operation failed

### Action: `reply_to_email`

*   **Description:** Reply to an existing email message
*   **Inputs:**
    *   `message_id`: ID of the message to reply to
    *   `comment`: Reply message text (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `message_id`: ID of the original message
    *   `operation`: Type of operation performed
    *   `status`: Status of the operation
    *   `error`: Error message if operation failed

### Action: `forward_email`

*   **Description:** Forward an existing email message to other recipients
*   **Inputs:**
    *   `message_id`: ID of the message to forward
    *   `to_recipients`: List of recipients to forward to
    *   `comment`: Additional message text to include (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `message_id`: ID of the original message
    *   `operation`: Type of operation performed
    *   `status`: Status of the operation
    *   `error`: Error message if operation failed

### Action: `download_email_attachment`

*   **Description:** Download the content of an email attachment
*   **Inputs:**
    *   `message_id`: ID of the message containing the attachment
    *   `attachment_id`: ID of the attachment to download
    *   `include_content`: Whether to include attachment content (default: true)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `attachment`: Object with attachment details including base64 encoded content
        *   `id`: Attachment ID
        *   `name`: Attachment filename
        *   `content_type`: MIME type of the attachment
        *   `size`: File size in bytes
        *   `content`: Base64 encoded attachment content
        *   `is_inline`: Whether attachment is inline
    *   `error`: Error message if operation failed

### Action: `search_emails`

*   **Description:** Search for emails using natural language queries
*   **Inputs:**
    *   `query`: Search query to find emails (searches body, sender, subject, and attachments)
    *   `limit`: Maximum number of results to return (default: 25, max: 1000)
    *   `enable_top_results`: Enable relevance-based ranking for top results (default: false)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `query`: The search query that was executed
    *   `total_results`: Total number of matching emails found
    *   `messages`: List of matching email messages with details
    *   `error`: Error message if operation failed

### Action: `create_calendar_event`

*   **Description:** Create calendar events with attendees and location
*   **Inputs:**
    *   `subject`: Event subject/title
    *   `start_time`: Event start time (UTC)
    *   `end_time`: Event end time (UTC)
    *   `location`: Event location (optional)
    *   `body`: Event description (optional)
    *   `attendees`: List of attendee email addresses (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `id`: Unique identifier of the created event
    *   `webLink`: Web link to the event
    *   `error`: Error message if operation failed

### Action: `update_calendar_event`

*   **Description:** Update existing calendar events by ID
*   **Inputs:**
    *   `event_id`: Unique identifier of the event to update
    *   `subject`: Updated event subject/title (optional)
    *   `start_time`: Updated start time (optional)
    *   `end_time`: Updated end time (optional)
    *   `location`: Updated location (optional)
    *   `attendees`: Updated list of attendee email addresses (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `id`: Unique identifier of the updated event
    *   `webLink`: Web link to the event
    *   `error`: Error message if operation failed

### Action: `list_calendar_events`

*   **Description:** List calendar events for specific dates or date ranges
*   **Inputs:**
    *   `start_datetime`: Start datetime for filtering (UTC)
    *   `end_datetime`: End datetime for filtering (UTC)
    *   `limit`: Maximum number of events to return
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `events`: List of calendar event objects
    *   `error`: Error message if operation failed

### Action: `upload_file`

*   **Description:** Upload files to OneDrive with folder support
*   **Inputs:**
    *   `filename`: Name of the file to upload
    *   `content`: Base64 encoded file content
    *   `content_type`: MIME type of the file
    *   `folder_path`: Target folder path in OneDrive (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `id`: Unique identifier of the uploaded file
    *   `webUrl`: Web URL to access the file
    *   `size`: File size in bytes
    *   `error`: Error message if operation failed

### Action: `list_files`

*   **Description:** List files and folders in OneDrive
*   **Inputs:**
    *   `folder_path`: Folder path to list (optional, defaults to root)
    *   `limit`: Maximum number of items to return
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `files`: List of file and folder objects
    *   `error`: Error message if operation failed

### Action: `read_contacts`

*   **Description:** Read and search contacts from Outlook with detailed information
*   **Inputs:**
    *   `limit`: Maximum number of contacts to return
    *   `search`: Search term to filter contacts (case-insensitive, partial matching)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `contacts`: List of contact objects with detailed information
    *   `message`: Descriptive message about the search results
    *   `search_term`: The search term used (only present when searching)
    *   `total_searched`: Total number of contacts searched through (only present when searching)
    *   `error`: Error message if operation failed

### Action: `search_onedrive_files`

*   **Description:** Search for files in OneDrive using natural language queries
*   **Inputs:**
    *   `query`: Search query to find files (e.g., 'quarterly report', 'budget 2024')
    *   `limit`: Maximum number of files to return (default: 10)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `files`: List of matching file objects with metadata
    *   `query`: The search query that was executed
    *   `error`: Error message if operation failed

### Action: `read_onedrive_file_content`

*   **Description:** Read the content of a OneDrive file by ID, with automatic PDF conversion for Office documents
*   **Inputs:**
    *   `file_id`: The ID of the file to read (obtained from search or list operations)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `file`: Object with file content and metadata
        *   `content`: Base64 encoded file content (PDF for Office documents, original content for text files)
        *   `name`: The name of the file
        *   `contentType`: Content type of the returned file (application/pdf for converted Office docs)
    *   `metadata`: File metadata including ID, size, and web URL
    *   `error`: Error message if operation failed

## Requirements

*   `autohive_integrations_sdk`
*   `aiohttp`

## Usage Examples

**Example 1: Send a simple email**

```json
{
  "to": "recipient@example.com",
  "subject": "Hello from Autohive",
  "body": "This is a test email sent via Microsoft 365 integration",
  "body_type": "Text"
}
```

**Example 2: Create a calendar event with attendees**

```json
{
  "subject": "Team Meeting",
  "start_time": "2024-08-01T14:00:00Z",
  "end_time": "2024-08-01T15:00:00Z",
  "location": "Conference Room A",
  "body": "Weekly team sync meeting",
  "attendees": ["team@example.com", "manager@example.com"]
}
```

**Example 3: Upload a file to OneDrive**

```json
{
  "filename": "document.pdf",
  "content": "base64-encoded-file-content",
  "content_type": "application/pdf",
  "folder_path": "/Documents"
}
```

**Example 4: List recent emails with timezone handling**

```json
{
  "start_datetime": "2024-08-01T07:00:00Z",
  "end_datetime": "2024-08-02T06:59:59Z",
  "folder": "Inbox",
  "limit": 20
}
```

**Example 5: Create and send a draft email**

```json
{
  "subject": "Meeting Follow-up",
  "body": "Thank you for attending today's meeting. Please find the action items below.",
  "body_type": "HTML",
  "to_recipients": [
    {"address": "team@example.com", "name": "Team"}
  ],
  "cc_recipients": ["manager@example.com"],
  "importance": "High"
}
```

**Example 6: Reply to an email**

```json
{
  "message_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYNKvwAAA=",
  "comment": "Thanks for the information. I'll review it and get back to you."
}
```

**Example 7: Search emails for specific content**

```json
{
  "query": "budget meeting quarterly",
  "limit": 10,
  "enable_top_results": true
}
```

**Example 8: Download an email attachment**

```json
{
  "message_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYNKvwAAA=",
  "attachment_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYNKvwAAABEgAQAMUhSlfLjElNlFm_4bZVWoc=",
  "include_content": true
}
```

**Example 9: Search OneDrive files**

```json
{
  "query": "quarterly report Q4",
  "limit": 5
}
```

**Example 10: Read OneDrive file content**

```json
{
  "file_id": "01BYE5RZ6QN3ZWBTUANRHZI4XJBEYH2C3X"
}
```

## Testing

To run the tests:

1.  Navigate to the integration's directory: `cd microsoft365`
2.  Install dependencies: `pip install -r requirements.txt -t dependencies`
3.  Run the tests: `python tests/test_microsoft365_integration.py`

Note: Testing requires proper Microsoft 365 authentication credentials and may require mock data for certain test scenarios.