# Coda Integration for Autohive

Document management integration for Coda. Create, list, and retrieve Coda docs programmatically to streamline document-based workflows.

## Description

This integration provides access to Coda's API for managing documents, enabling automation workflows to interact with Coda docs. It returns structured data optimized for integration with other systems.

Key features include:
- List all accessible Coda docs with filtering options
- Retrieve detailed metadata for specific docs
- Create new Coda docs (optionally from templates)
- Filter docs by owner, query, published status, and starred status
- Support for pagination and result limits

This integration uses the Coda API v1 and provides robust error handling with structured response formats.

## Setup & Authentication

This integration uses custom API token authentication.

**How to get your API token:**
1. Go to your Coda account settings
2. Navigate to **API Settings** section
3. Click **"Generate API Token"**
4. Choose scope:
   - **Unrestricted** - Access all your docs
   - **Specific doc/table** - Limit access to specific resources
5. Copy and securely store your API token

**Authentication URL:** https://coda.io/account

The integration automatically handles:
- Bearer token authentication
- API request headers
- Error handling for authentication failures

## Actions

### list_docs

Returns a list of Coda docs accessible by the user. Docs are returned in reverse chronological order by the latest event relevant to the user (last viewed, edited, or shared).

**Input Parameters:**
- `is_owner` (optional): Boolean - Show only docs owned by the user (default: false)
- `query` (optional): String - Search term to filter docs by name
- `source_doc` (optional): String - Show only docs copied from the specified doc ID
- `is_published` (optional): Boolean - Show only published docs
- `is_starred` (optional): Boolean - Show only starred docs
- `limit` (optional): Integer - Maximum number of results to return (1-500, default: 100)

**Output:**
- `docs`: Array of document objects with:
  - `id`: Document ID
  - `type`: Resource type
  - `href`: Full API URL
  - `name`: Document name
  - `owner`: Owner email
  - `workspace`: Workspace details
  - `createdAt`: Creation timestamp
  - `updatedAt`: Last update timestamp
- `result`: Boolean - Whether the operation was successful
- `error`: String - Error message if operation failed

**Example Usage:**

List all your docs:
```
Get all my Coda docs
```

List only owned docs:
```
Show me only the Coda docs I own
```

Search for specific docs:
```
Find Coda docs with "project" in the name
```

List published docs:
```
Show all published Coda docs
```

### get_doc

Returns metadata for the specified Coda doc, including name, owner, creation date, and other details.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc (e.g., "AbCDeFGH")

**Output:**
- `data`: Object with doc metadata including:
  - `id`: Document ID
  - `type`: Resource type
  - `href`: Full API URL
  - `name`: Document name
  - `owner`: Owner email
  - `workspace`: Workspace details
  - `createdAt`: Creation timestamp
  - `updatedAt`: Last update timestamp
  - Additional metadata fields
- `result`: Boolean - Whether the operation was successful
- `error`: String - Error message if operation failed

**Example Usage:**

Get doc by ID:
```
Get Coda doc with ID "abc123xyz"
```

Retrieve doc details:
```
Show me details for Coda doc "AbCDeFGH"
```

### create_doc

Creates a new Coda doc. Optionally copies content from an existing doc. Returns HTTP 202 (Accepted) as doc creation is processed asynchronously.

**Input Parameters:**
- `title` (required): String - Title of the new doc
- `source_doc` (optional): String - Doc ID to copy content from (e.g., "AbCDeFGH")
- `timezone` (optional): String - Timezone for the doc (e.g., "America/Los_Angeles")
- `folder_id` (optional): String - Folder ID where the doc should be created

**Output:**
- `data`: Object with created doc details including:
  - `id`: New document ID
  - `name`: Document name
  - `href`: Full API URL
  - `requestId`: Async processing request ID
- `result`: Boolean - Whether the operation was successful
- `error`: String - Error message if operation failed

**Example Usage:**

Create a blank doc:
```
Create a new Coda doc called "Meeting Notes"
```

Create from template:
```
Create a Coda doc called "Q1 Report" using template doc "template123"
```

Create with timezone:
```
Create a Coda doc called "Project Plan" in America/New_York timezone
```

## Rate Limits

- **Reading data (GET)**: 100 requests per 6 seconds
- **Writing data (POST/PUT/PATCH)**: 10 requests per 6 seconds
- **Listing docs**: 4 requests per 6 seconds

**Note:** Write operations (like create_doc) return HTTP 202, indicating the edit has been accepted and queued for asynchronous processing. Docs are typically created within a few seconds.

## Error Handling

The integration provides structured error responses for:
- Invalid or expired API tokens (401 errors)
- Access forbidden - no permission to resource (403 errors)
- Resource not found (404 errors)
- Rate limit exceeded (429 errors)
- General API failures

All actions return a consistent structure:
```json
{
  "data": {} or "docs": [],
  "result": true/false,
  "error": "Error message if failed"
}
```

## Use Cases

- Automated doc creation from templates
- Document inventory and management
- Doc metadata retrieval for reporting
- Workflow automation with Coda docs
- Cross-platform doc synchronization
- Team doc organization and filtering
- Automated doc provisioning for projects
- Document lifecycle management

## Technical Details

- **API Endpoint**: `https://coda.io/apis/v1`
- **Authentication**: Bearer token (Custom API token)
- **Response Format**: JSON
- **Async Processing**: Create operations return 202 and process asynchronously
- **API Version**: v1 (Standard Coda API)

## Permissions

**For list_docs and get_doc:**
- Requires read access to docs (granted by API token scope)

**For create_doc:**
- Token owner must be **Doc Maker** (or Admin) in the workspace
- OR workspace must have "Any member can create docs" enabled (Editor auto-promoted to Doc Maker)

## Additional Resources

- [Coda API Official Documentation](https://coda.io/developers)
- [Coda API Getting Started Guide](https://coda.io/@oleg/getting-started-guide-coda-api)
- [Coda Account Settings (API Token)](https://coda.io/account)
