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
    *   `file`: File object with name, content (base64), and contentType
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
    *   `search`: Search term to filter contacts (optional)
*   **Outputs:**
    *   `result`: Boolean indicating success/failure
    *   `contacts`: List of contact objects with detailed information
    *   `error`: Error message if operation failed

## Requirements

*   `autohive_integrations_sdk`

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
  "file": {
    "name": "document.pdf",
    "content": "base64-encoded-file-content",
    "contentType": "application/pdf"
  },
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

## Testing

To run the tests:

1.  Navigate to the integration's directory: `cd microsoft365`
2.  Install dependencies: `pip install -r requirements.txt -t dependencies`
3.  Run the tests: `python tests/test_microsoft365_integration.py`

Note: Testing requires proper Microsoft 365 authentication credentials and may require mock data for certain test scenarios.