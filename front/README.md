# Front Integration

Connects to the Front API to allow users to manage customer conversations, messages, and team collaboration directly from their workflows.

## Description

This integration provides comprehensive Front customer service functionality, enabling users to manage conversations, send messages, organize inboxes, and collaborate with team members. It supports conversation filtering, message threading, assignee management, and conversation tagging. The integration uses Front's platform authentication to securely access workspace resources.

Key features:
- List and manage inboxes and their channels
- List and filter conversations from specific inboxes
- View and send messages within conversations
- Create new messages and reply to existing conversations
- Access message templates for consistent responses
- Manage conversation assignments and status updates
- Support for CC/BCC messaging and conversation updates
- Optional author assignment using teammate IDs for message authorship control

## Setup & Authentication

The integration uses Front's OAuth2 platform authentication. Users need to authenticate through Front's OAuth flow within Autohive to grant workspace access permissions.

**Authentication Type:** Platform (Front)

**Required Scopes:**
- `Shared resources` - Access to workspace-wide conversations and data

No additional configuration fields are required as authentication is handled through Front's OAuth2 flow.

## Actions

### Inbox Management

#### Action: `list_inboxes`
- **Description:** List all accessible inboxes in the workspace
- **Inputs:**
  - `limit`: Maximum number of inboxes to return (optional, default: 50)
- **Outputs:**
  - `inboxes`: Array of inbox objects with ID, name, address, type, and send_as information
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `get_inbox`
- **Description:** Get details of a specific inbox
- **Inputs:**
  - `inbox_id`: The inbox ID to retrieve
- **Outputs:**
  - `inbox`: Inbox object with detailed information
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `list_inbox_conversations`
- **Description:** List conversations from a specific inbox with filtering options
- **Inputs:**
  - `inbox_id`: The inbox ID to get conversations from
  - `status`: Filter by conversation status - archived, deleted, open, assigned, unassigned (optional)
  - `tag_id`: Filter conversations by tag ID (optional)
  - `limit`: Maximum number of conversations to return (optional, default: 50)
- **Outputs:**
  - `conversations`: Array of conversation objects with ID, subject, status, assignee, recipient, tags, and last message
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

### Conversation Management

#### Action: `get_conversation`
- **Description:** Retrieve detailed information about a specific conversation including metadata
- **Inputs:**
  - `conversation_id`: The conversation ID to retrieve
- **Outputs:**
  - `conversation`: Complete conversation object with all metadata
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `update_conversation`
- **Description:** Update conversation properties including assignee, status, and tags
- **Inputs:**
  - `conversation_id`: The conversation ID to update
  - `assignee_id`: ID of teammate to assign conversation to (optional)
  - `status`: New conversation status - archived, deleted, open (optional)
  - `tags`: Array of tag IDs to apply to conversation (optional)
- **Outputs:**
  - `conversation`: Updated conversation object with changes reflected
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

### Message Management

#### Action: `list_conversation_messages`
- **Description:** List all messages within a specific conversation with pagination support
- **Inputs:**
  - `conversation_id`: The conversation ID to get messages from
  - `limit`: Maximum number of messages to return (optional, default: 50)
- **Outputs:**
  - `messages`: Array of message objects with ID, type, author, recipients, subject, body, and timestamps
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `get_message`
- **Description:** Get details of a specific message
- **Inputs:**
  - `message_id`: The message ID to retrieve
- **Outputs:**
  - `message`: Message object with detailed information
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `create_message`
- **Description:** Create a new message (starts new conversation) via a channel
- **Inputs:**
  - `channel_id`: Channel ID to send from
  - `body`: Message body content
  - `to`: Array of recipient email addresses
  - `cc`: Array of CC email addresses (optional)
  - `bcc`: Array of BCC email addresses (optional)
  - `sender_name`: Name used for the sender info of the message (optional)
  - `subject`: Message subject for email messages (optional)
  - `author_id`: ID of the teammate on behalf of whom the message is sent (optional)
  - `text`: Text version of the body for email messages (optional)
  - `signature_id`: ID of the signature to attach to this message (optional)
  - `should_add_default_signature`: Whether to add the default signature (optional)
- **Outputs:**
  - `message_uid`: Temporary message UID for async processing
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `create_message_reply`
- **Description:** Reply to an existing conversation
- **Inputs:**
  - `conversation_id`: The conversation ID to reply to
  - `body`: Message body content
  - `to`: Array of recipient email addresses (optional)
  - `cc`: Array of CC email addresses (optional)
  - `bcc`: Array of BCC email addresses (optional)
  - `sender_name`: Name used for the sender info of the message (optional)
  - `subject`: Message subject for email messages (optional)
  - `author_id`: ID of the teammate on behalf of whom the message is sent (optional)
  - `channel_id`: Channel ID the message is sent from (optional)
  - `text`: Text version of the body for email messages (optional)
  - `quote_body`: Body for the quote that the message is referencing (email channels only) (optional)
  - `signature_id`: ID of the signature to attach to this message (optional)
  - `should_add_default_signature`: Whether to add the default signature (optional)
- **Outputs:**
  - `message_uid`: Temporary message UID for async processing
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

### Channel Management

#### Action: `list_channels`
- **Description:** List all channels in the account
- **Inputs:**
  - `limit`: Maximum number of channels to return (optional, default: 50)
- **Outputs:**
  - `channels`: Array of channel objects with ID, name, type, and settings
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `list_inbox_channels`
- **Description:** List channels for a specific inbox
- **Inputs:**
  - `inbox_id`: The inbox ID to get channels from
  - `limit`: Maximum number of channels to return (optional, default: 50)
- **Outputs:**
  - `channels`: Array of channel objects with ID, name, type, and settings
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `get_channel`
- **Description:** Get details of a specific channel
- **Inputs:**
  - `channel_id`: The channel ID to retrieve
- **Outputs:**
  - `channel`: Channel object with detailed information
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

### Message Templates

#### Action: `list_message_templates`
- **Description:** List all message templates available
- **Inputs:**
  - `limit`: Maximum number of templates to return (optional, default: 50)
- **Outputs:**
  - `templates`: Array of template objects with ID, name, subject, body, attachments, and metadata
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

#### Action: `get_message_template`
- **Description:** Get details of a specific message template
- **Inputs:**
  - `message_template_id`: The message template ID to retrieve
- **Outputs:**
  - `template`: Template object with complete details including subject, body, attachments, and metadata
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

### Team Management

#### Action: `list_teammates`
- **Description:** List all teammates in the workspace
- **Inputs:**
  - `limit`: Maximum number of teammates to return (optional, default: 50)
- **Outputs:**
  - `teammates`: Array of teammate objects with ID, username, first_name, last_name, email, and metadata
  - `result`: Success status boolean
  - `error`: Error message (if operation failed)

## Requirements

- Python dependencies are handled by the Autohive platform
- Front API access
- Valid Front workspace with appropriate permissions

## Usage Examples

**Example 1: Find billing inbox and list its conversations**

Step 1 - List inboxes:
```json
{
  "limit": 25
}
```

Step 2 - List conversations from billing inbox:
```json
{
  "inbox_id": "inb_billing123",
  "status": "open",
  "limit": 10
}
```

**Example 2: Reply to a customer conversation with specific author**

Step 1 - List teammates to get author ID:
```json
{
  "limit": 25
}
```

Step 2 - Reply with specific teammate as author:
```json
{
  "conversation_id": "cnv_456",
  "body": "Thank you for reaching out! I'll help you resolve this issue right away.",
  "author_id": "tea_789"
}
```

**Example 3: Create new message using a channel with specific author**

Step 1 - List teammates to get author ID:
```json
{
  "limit": 25
}
```

Step 2 - Get inbox channels:
```json
{
  "inbox_id": "inb_billing123",
  "limit": 10
}
```

Step 3 - Create message via channel with specific author:
```json
{
  "channel_id": "cha_email123",
  "body": "Hello! We received your inquiry and will get back to you shortly.",
  "to": ["customer@example.com"],
  "subject": "Re: Your Support Request",
  "author_id": "tea_789"
}
```

**Example 4: Use message template for consistent responses**

Step 1 - List available templates:
```json
{
  "limit": 20
}
```

Step 2 - Get specific template:
```json
{
  "message_template_id": "tpl_456"
}
```

Step 3 - Use template content in reply:
```json
{
  "conversation_id": "cnv_456",
  "author_id": "tea_789",
  "body": "[Template body content with customizations]"
}
```

**Example 5: Assign conversation and add tags**

```json
{
  "conversation_id": "cnv_456",
  "assignee_id": "tea_789",
  "tags": ["tag_urgent", "tag_billing"]
}
```

## Testing

To run the tests:

1. Navigate to the integration's directory: `cd front`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the tests: `python tests/test_front.py`

Note: The tests use mock authentication and are designed for development validation. For production testing, ensure you have valid Front OAuth credentials configured.
