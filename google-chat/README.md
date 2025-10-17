# Google Chat Integration for Autohive

Connects Autohive to Google Chat to enable sending messages, managing spaces, and interacting with conversations as an authenticated user.

## Description

This integration provides user-authenticated access to Google Chat (formerly Hangouts Chat), allowing users to automate their Google Chat interactions. Users can send messages, create and manage spaces, react to messages, and manage space memberships directly from Autohive workflows.

The integration uses Google Chat API and implements 13 core actions covering spaces, messages, members, and reactions.

## Setup & Authentication

This integration uses **Platform Authentication** with Google OAuth2.

### Authentication Method

Google Chat uses OAuth 2.0 for user authentication. The integration handles the OAuth flow automatically and requests the necessary scopes to interact with Google Chat on behalf of the authenticated user.

### Required Scopes

- `https://www.googleapis.com/auth/chat.messages` - Read and send messages
- `https://www.googleapis.com/auth/chat.spaces` - View and manage Chat spaces
- `https://www.googleapis.com/auth/chat.messages.reactions` - Add and remove message reactions

### Setup Steps

1. **Configure in Autohive:**
   - Add the Google Chat integration in Autohive
   - Click "Authenticate" to start the OAuth flow
   - Sign in with your Google account
   - Grant the requested permissions
   - The integration will automatically receive and store the access tokens

2. **Important Notes:**
   - This integration uses **user authentication**, not bot/service account authentication
   - The authenticated user must be a member of any space they want to interact with
   - All actions are performed as the authenticated user

## Actions

### Spaces (3 actions)

#### `list_spaces`
Lists all Google Chat spaces the user is a member of, including direct messages, group chats, and named spaces.

**Inputs:**
- `page_size` (optional): Maximum number of spaces to return (default: 100, max: 1000)
- `page_token` (optional): Page token for pagination from previous response
- `filter` (optional): Filter spaces by type (e.g., `spaceType = "SPACE"` for named spaces only)

**Outputs:**
- `spaces`: Array of space objects with name, display_name, space_type, and other properties
- `next_page_token`: Token for retrieving the next page of results
- `result`: Success status

---

#### `get_space`
Get details about a specific Google Chat space including its properties and settings.

**Inputs:**
- `space_name` (required): Resource name of the space (e.g., `spaces/AAAAMpdlehY`)

**Outputs:**
- `space`: Complete space object with all properties
- `result`: Success status

---

#### `create_space`
Create a new Google Chat space with specified settings and initial members.

**Inputs:**
- `display_name` (required): Display name for the new space
- `space_type` (optional): Type of space to create (default: `SPACE`)
- `space_details` (optional): Object containing:
  - `description`: Description of the space
  - `guidelines`: Guidelines for the space

**Outputs:**
- `space`: Created space object with name, display_name, and space_type
- `result`: Success status

---

### Messages (5 actions)

#### `send_message`
Send a text message to a Google Chat space. With user authentication, only text messages with basic formatting are supported.

**Inputs:**
- `space_name` (required): Resource name of the space to send message to
- `text` (required): Text content of the message (supports @mentions, hyperlinks, and basic formatting)
- `thread_key` (optional): Thread key to reply to a specific thread
- `message_id` (optional): Client-assigned message ID (must start with `client-`)
- `message_reply_option` (optional): How to handle replies in threaded spaces

**Outputs:**
- `message`: Sent message object with name, text, create_time, sender, and thread info
- `result`: Success status

---

#### `list_messages`
List messages from a Google Chat space with filtering and pagination options.

**Inputs:**
- `space_name` (required): Resource name of the space
- `page_size` (optional): Maximum number of messages to return (default: 25, max: 1000)
- `page_token` (optional): Page token for pagination
- `filter` (optional): Filter messages by timestamp (e.g., `createTime > "2023-04-21T11:30:00-04:00"`)
- `order_by` (optional): Sort order for messages (e.g., `createTime desc`)
- `show_deleted` (optional): Whether to include deleted messages (default: false)

**Outputs:**
- `messages`: Array of message objects
- `next_page_token`: Token for next page of results
- `result`: Success status

---

#### `get_message`
Get details about a specific message in Google Chat.

**Inputs:**
- `message_name` (required): Resource name of the message (e.g., `spaces/AAAAMpdlehY/messages/xyz`)

**Outputs:**
- `message`: Complete message object with all properties
- `result`: Success status

---

#### `update_message`
Update a message that was previously sent. Only text content can be updated with user authentication.

**Inputs:**
- `message_name` (required): Resource name of the message to update
- `text` (required): New text content for the message
- `update_mask` (optional): Field mask specifying which fields to update (default: `text`)

**Outputs:**
- `message`: Updated message object
- `result`: Success status

**Note:** You can only update messages that you sent.

---

#### `delete_message`
Delete a message from Google Chat. Only messages sent by the authenticated user can be deleted.

**Inputs:**
- `message_name` (required): Resource name of the message to delete
- `force` (optional): When true, deletes message for all users. When false, only removes for the calling user (default: false)

**Outputs:**
- `result`: Success status

---

### Members (1 action)

#### `list_members`
List all members in a Google Chat space, including users and Chat apps.

**Inputs:**
- `space_name` (required): Resource name of the space
- `page_size` (optional): Maximum number of members to return (default: 100, max: 1000)
- `page_token` (optional): Page token for pagination
- `filter` (optional): Filter members by role (e.g., `role="ROLE_MANAGER"`)

**Outputs:**
- `members`: Array of membership objects with name, member details, state, role, and timestamps
- `next_page_token`: Token for next page of results
- `result`: Success status

---

### Reactions (3 actions)

#### `add_reaction`
Add an emoji reaction to a message in Google Chat.

**Inputs:**
- `message_name` (required): Resource name of the message to react to
- `emoji` (required): Emoji object containing either:
  - `unicode`: Unicode emoji (e.g., `👍`)
  - `custom_emoji`: Custom emoji object with `uid`

**Outputs:**
- `reaction`: Created reaction object
- `result`: Success status

---

#### `list_reactions`
List all reactions on a specific message in Google Chat.

**Inputs:**
- `message_name` (required): Resource name of the message
- `page_size` (optional): Maximum number of reactions to return (default: 25, max: 1000)
- `page_token` (optional): Page token for pagination
- `filter` (optional): Filter reactions by emoji

**Outputs:**
- `reactions`: Array of reaction objects
- `next_page_token`: Token for next page of results
- `result`: Success status

---

#### `remove_reaction`
Remove an emoji reaction from a message in Google Chat.

**Inputs:**
- `reaction_name` (required): Resource name of the reaction to remove

**Outputs:**
- `result`: Success status

---

### Utilities (1 action)

#### `find_direct_message`
Find an existing direct message conversation with another user, or returns details to create one.

**Inputs:**
- `user_name` (required): Resource name of the user to find DM with (e.g., `users/example@gmail.com`)

**Outputs:**
- `space`: Direct message space object
- `result`: Success status

---

## Requirements

- `autohive_integrations_sdk` - The Autohive integrations SDK

## API Information

- **API Version**: v1
- **Base URL**: `https://chat.googleapis.com/v1`
- **Authentication**: OAuth 2.0 (User authentication)
- **Documentation**: https://developers.google.com/chat/api
- **Rate Limits**: Subject to Google Chat API quotas

## Important Notes

- This integration uses **user authentication** (OAuth), not bot/service account authentication
- All actions are performed as the authenticated user
- The user must be a member of any space they want to interact with
- With user authentication, only text messages with basic formatting are supported (no cards or interactive elements)
- Messages can only be updated or deleted by the user who sent them
- Resource names (space names, message names, etc.) are in the format returned by the API (e.g., `spaces/AAAAMpdlehY`)

## Testing

To test the integration:

1. Navigate to the integration directory: `cd google_chat`
2. Install dependencies: `pip install -r requirements.txt`
3. Update test credentials in `tests/test_google_chat.py` with valid OAuth tokens
4. Run tests: `python tests/test_google_chat.py`

## Common Use Cases

**Team Communication Automation:**
1. Send notifications to team spaces when events occur
2. Create new spaces for projects or initiatives
3. React to important messages automatically
4. List and search messages from spaces

**Direct Messaging:**
1. Find or create DM conversations with specific users
2. Send automated reminders or notifications via DM
3. Update previously sent messages with new information

**Space Management:**
1. List all spaces the user is a member of
2. Create new spaces with descriptions and guidelines
3. List members in a space to understand team composition

## Version History

- **1.0.0** - Initial release with 13 core actions
  - Spaces: list, get, create
  - Messages: send, list, get, update, delete
  - Members: list
  - Reactions: add, list, remove
  - Utilities: find_direct_message
