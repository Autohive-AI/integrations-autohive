# Microsoft 365 Integration

This integration provides access to Microsoft 365 services including Outlook, OneDrive, and Calendar through the Microsoft Graph API.

## Features

### Actions
- **Send Email**: Send emails via Outlook with support for CC, BCC, and HTML content
- **Create Calendar Event**: Create calendar events with attendees and location
- **Upload File**: Upload files to OneDrive with folder support
- **List Files**: List files and folders in OneDrive

### Polling Triggers
- **New Emails**: Monitor for new emails in specified folders (default: Inbox)
- **New Files**: Monitor OneDrive folders for new files

## Authentication

This integration uses Microsoft Graph OAuth2 authentication. Users need to connect their Microsoft 365 account through the Autohive platform.

Required Microsoft Graph API permissions:
- `Mail.ReadWrite` - Read and send emails
- `Files.ReadWrite` - Access OneDrive files
- `Calendars.ReadWrite` - Manage calendar events

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

## Error Handling

All actions return a standardized response format with:
- `result`: Boolean indicating success/failure
- `error`: Error message if operation failed
- Additional action-specific fields on success

## Development

Built using the Autohive Integrations SDK following the established patterns from other integrations in this repository.