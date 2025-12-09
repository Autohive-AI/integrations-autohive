# Monday.com Integration

Monday.com integration for managing boards, items, updates, and team collaboration workflows.

## Features

### Board Management
- Retrieve boards with columns and groups
- Filter boards by type (public, private, shared)
- Support for pagination

### Item Operations
- Get items from boards with all column values
- Create new items with custom column values
- Update existing items
- Track item metadata (creator, creation date, updates)

### Collaboration
- Create updates (comments) on items
- Get workspace users
- Access team information

### Flexible Querying
- GraphQL-based API for efficient data retrieval
- Pagination support across all list actions
- Detailed column value access

## Authentication

This integration uses Monday.com API token authentication. You'll need:

- **API Token**: A valid Monday.com API token from your account

To get your API token:
1. Log in to Monday.com
2. Click on your avatar in the bottom left
3. Select "Admin" > "API"
4. Generate or copy your API token

## Actions

### get_boards
Retrieve boards from your Monday.com workspace.

**Inputs:**
- `limit` (integer, optional): Maximum number of boards to return (default: 25)
- `page` (integer, optional): Page number for pagination (default: 1)
- `board_kind` (string, optional): Filter by board type: "public", "private", or "share"

**Output:**
- `boards` (array): Array of board objects with columns and groups
- `board_count` (integer): Number of boards returned
- `result` (boolean): Success status

### get_items
Retrieve items from a specific board.

**Inputs:**
- `board_id` (string, required): The board ID to retrieve items from
- `limit` (integer, optional): Maximum number of items to return (default: 25)
- `page` (integer, optional): Page number for pagination (default: 1)

**Output:**
- `items` (array): Array of item objects with all column values
- `item_count` (integer): Number of items returned
- `result` (boolean): Success status

### create_item
Create a new item on a board.

**Inputs:**
- `board_id` (string, required): The board ID to create the item on
- `group_id` (string, optional): The group ID within the board
- `item_name` (string, required): The name of the new item
- `column_values` (string, optional): JSON string of column values (e.g., '{"status": "Done", "text": "Hello"}')

**Output:**
- `item` (object): The created item object
- `result` (boolean): Success status

### update_item
Update an existing item on a board.

**Inputs:**
- `board_id` (string, required): The board ID containing the item
- `item_id` (string, required): The item ID to update
- `column_values` (string, required): JSON string of column values to update

**Output:**
- `item` (object): The updated item object
- `result` (boolean): Success status

### create_update
Create an update (comment) on an item.

**Inputs:**
- `item_id` (string, required): The item ID to create the update on
- `body` (string, required): The text content of the update/comment

**Output:**
- `update` (object): The created update object with creator info and timestamp
- `result` (boolean): Success status

### get_users
Retrieve users from your Monday.com workspace.

**Inputs:**
- `limit` (integer, optional): Maximum number of users to return (default: 25)
- `page` (integer, optional): Page number for pagination (default: 1)

**Output:**
- `users` (array): Array of user objects with email, title, and team info
- `user_count` (integer): Number of users returned
- `result` (boolean): Success status

## Common Board Columns

Monday.com supports various column types:
- `status` - Status labels (e.g., "Working on it", "Done", "Stuck")
- `text` - Plain text fields
- `numbers` - Numeric values
- `date` - Date fields
- `people` - User assignments
- `timeline` - Timeline/date range
- `dropdown` - Single-select dropdown
- `email` - Email addresses
- `phone` - Phone numbers
- `link` - URLs
- `file` - File attachments
- `checkbox` - Boolean checkboxes

## Column Value Format

When setting column values in `create_item` or `update_item`, use JSON format:

```json
{
  "status": "Working on it",
  "text": "Project description",
  "numbers": "42",
  "date": "2025-12-15",
  "people": {"personsAndTeams": [{"id": 12345678, "kind": "person"}]},
  "dropdown": "Option 1"
}
```

## Technical Details

### API Endpoint

- Monday.com GraphQL API v2: `https://api.monday.com/v2`
- API Version: `2024-10`

### Rate Limits

Monday.com API has the following rate limits:
- Complexity-based rate limiting (each query has a complexity score)
- Standard accounts: ~1M requests per minute
- Check your account's specific limits in the API documentation

### Best Practices

1. Use pagination for large datasets to avoid timeouts
2. Request only the fields you need in GraphQL queries
3. Cache board metadata (columns, groups) as they change infrequently
4. Use batch operations when possible to reduce API calls
5. Handle errors gracefully and check the `result` field in responses

## Testing

To test the integration:

1. Obtain a Monday.com API token from your account settings
2. Find your board IDs from the Monday.com interface (visible in the URL)
3. Update the credentials in `tests/test_monday_com.py`
4. Replace `BOARD_ID` and `api_token` with your values
5. Run the tests: `python tests/test_monday_com.py`

## Example Usage

### Get All Boards
```python
inputs = {
    "limit": 10,
    "board_kind": "public"
}
```

### Get Items from a Board
```python
inputs = {
    "board_id": "1234567890",
    "limit": 50,
    "page": 1
}
```

### Create an Item
```python
inputs = {
    "board_id": "1234567890",
    "item_name": "New Task",
    "column_values": '{"status": "Working on it", "text": "Task description"}'
}
```

### Update an Item
```python
inputs = {
    "board_id": "1234567890",
    "item_id": "9876543210",
    "column_values": '{"status": "Done"}'
}
```

### Add a Comment
```python
inputs = {
    "item_id": "9876543210",
    "body": "Great progress on this task!"
}
```

## Resources

- [Monday.com API Documentation](https://developer.monday.com/api-reference/docs)
- [GraphQL Explorer](https://monday.com/developers/v2/try-it-yourself)
- [Column Types Reference](https://developer.monday.com/api-reference/docs/column-types)
- [API Rate Limits](https://developer.monday.com/api-reference/docs/rate-limits)

## Version

1.0.0
