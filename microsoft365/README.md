# Microsoft 365 Integration

This integration provides access to Microsoft 365 services including Outlook, OneDrive, and Calendar through the Microsoft Graph API.

## Features

### Actions
- **Send Email**: Send emails via Outlook with support for CC, BCC, and HTML content
- **List Emails**: List emails for specific dates or date ranges with full content
- **List Emails from Contact**: Get latest emails from a specific contact
- **Read Email**: Read email content and list attachment metadata
- **Mark Email as Read/Unread**: Change the read status of emails
- **Move Email to Folder**: Move emails between folders (Archive, Junk, etc.)
- **Create Calendar Event**: Create calendar events with attendees and location
- **Update Calendar Event**: Update existing calendar events by ID
- **List Calendar Events**: List calendar events for specific dates or date ranges
- **Upload File**: Upload files to OneDrive with folder support
- **List Files**: List files and folders in OneDrive
- **Read Contacts**: Read and search contacts from Outlook with detailed information


## Authentication

This integration uses Microsoft Graph OAuth2 authentication. Users need to connect their Microsoft 365 account through the Autohive platform.

Required Microsoft Graph API permissions:
- `Mail.ReadWrite` - Read and send emails
- `Mail.Send` - Send emails on behalf of user
- `Files.ReadWrite` - Access OneDrive files
- `Calendars.ReadWrite` - Manage calendar events
- `Contacts.Read` - Read user contacts

## Configuration

The integration is configured through the `config.json` file and uses the Autohive integrations SDK for execution.

## Usage Examples

### Send Email
```json
{
  "to": "recipient@example.com",
  "subject": "Hello from Autohive",
  "body": "This is a test email sent via Microsoft 365 integration",
  "body_type": "Text",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"]
}
```

### Create Calendar Event
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

### Upload File
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

### List Emails
```json
{
  "start_datetime": "2024-08-01T07:00:00Z",
  "end_datetime": "2024-08-02T06:59:59Z",
  "folder": "Inbox",
  "limit": 20
}
```

**Timezone Handling**: For timezone-aware queries, use `start_datetime` and `end_datetime` parameters with UTC timestamps. Legacy `start_date` and `end_date` parameters default to UTC timezone.

### List Emails from Contact
```json
{
  "contact_email": "john.doe@example.com",
  "limit": 5,
  "folder": "Inbox"
}
```

### Read Email with Attachments
```json
{
  "email_id": "AAMkAGVmMDEzMTM4LWZmNjktNDVkNC1iZGRiLTJkNTBmNjNlNTM0ZAAA",
  "include_attachments": true
}
```

### Mark Email as Read/Unread
```json
{
  "email_id": "AAMkAGVmMDEzMTM4LWZmNjktNDVkNC1iZGRiLTJkNTBmNjNlNTM0ZAAA",
  "is_read": true
}
```

### Move Email to Folder
```json
{
  "email_id": "AAMkAGVmMDEzMTM4LWZmNjktNDVkNC1iZGRiLTJkNTBmNjNlNTM0ZAAA",
  "destination_folder": "Archive"
}
```

### Update Calendar Event
```json
{
  "event_id": "AAMkAGI2TG93AAA=",
  "subject": "Updated Team Meeting",
  "start_time": "2024-08-01T15:00:00Z",
  "end_time": "2024-08-01T16:00:00Z",
  "location": "Conference Room B",
  "attendees": ["newteam@example.com"]
}
```

### List Calendar Events
```json
{
  "start_datetime": "2024-08-01T07:00:00Z",
  "end_datetime": "2024-08-02T06:59:59Z",
  "limit": 20
}
```

**Timezone Handling**: For timezone-aware queries, use `start_datetime` and `end_datetime` parameters with UTC timestamps. Legacy `start_date` and `end_date` parameters default to UTC timezone.

### Read Contacts
```json
{
  "limit": 50,
  "search": "John"
}
```

## Error Handling

All actions return a standardized response format with:
- `result`: Boolean indicating success/failure
- `error`: Error message if operation failed
- Additional action-specific fields on success

## Development

Built using the Autohive Integrations SDK following the established patterns from other integrations in this repository.