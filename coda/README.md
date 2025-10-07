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

### update_doc

Updates metadata for a Coda doc (title and icon). Requires Doc Maker permissions for updating the title.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc to update (e.g., "AbCDeFGH")
- `title` (optional): String - New title for the doc
- `icon_name` (optional): String - New icon name (e.g., "rocket", "star", "heart")

**Output:**
- `data`: Object with updated doc details
- `result`: Boolean - Whether the operation was successful
- `error`: String - Error message if operation failed

**Example Usage:**

Update doc title:
```
Update Coda doc "abc123" with new title "Q4 Project Tracker"
```

Update doc icon:
```
Update Coda doc "abc123" with rocket icon
```

Update both:
```
Update Coda doc "abc123" with title "Launch Plan" and rocket icon
```

### delete_doc

Deletes a Coda doc. Returns HTTP 202 (Accepted) as deletion is queued for processing. This action is permanent and cannot be undone.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc to delete (e.g., "AbCDeFGH")

**Output:**
- `data`: Object with deletion confirmation
- `result`: Boolean - Whether the operation was successful
- `error`: String - Error message if operation failed

**Warning:** This action permanently deletes the doc and cannot be reversed.

**Example Usage:**

Delete a doc:
```
Delete Coda doc "abc123"
```

### list_pages

Returns a list of pages in a Coda doc. Use this to discover the doc structure and navigate between pages.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc (e.g., "AbCDeFGH")
- `limit` (optional): Integer - Maximum number of results per page (1-500, default: 100)
- `page_token` (optional): String - Token for fetching next page of results

**Output:**
- `pages`: Array of page objects with metadata (id, name, subtitle, icon, parent, children)
- `next_page_token`: String - Token for next page if more results available
- `result`: Boolean - Whether operation was successful
- `error`: String - Error message if failed

**Example Usage:**

List all pages in a doc:
```
List all pages in Coda doc "abc123"
```

List with pagination:
```
List first 10 pages in doc "abc123"
```

### get_page

Returns detailed metadata for a specific page including title, subtitle, icon, image, parent/child relationships, and authors.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc (e.g., "AbCDeFGH")
- `page_id_or_name` (required): String - Page ID or name (e.g., "canvas-abc123")

**Output:**
- `data`: Object with comprehensive page metadata:
  - `id`: Page ID
  - `name`: Page name
  - `subtitle`: Page subtitle
  - `icon`: Icon details
  - `image`: Cover image details
  - `parent`: Parent page reference
  - `children`: Array of child pages
  - `authors`: Array of author details
  - `createdAt`: Creation timestamp
- `result`: Boolean - Whether operation was successful
- `error`: String - Error message if failed

**Example Usage:**

Get page by ID:
```
Get Coda page "canvas-xyz789" from doc "abc123"
```

Get page details:
```
Show me details for page "Project Overview" in doc "abc123"
```

### create_page

Creates a new page in a Coda doc with optional content, subtitle, icon, and parent page. Returns HTTP 202 (Accepted) as creation is processed asynchronously. Requires Doc Maker permissions.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc
- `name` (required): String - Page name/title
- `subtitle` (optional): String - Page subtitle text
- `icon_name` (optional): String - Icon name (e.g., "rocket", "star", "heart", "bell", "calendar")
- `image_url` (optional): String - URL for cover image
- `parent_page_id` (optional): String - Parent page ID to create as subpage
- `content_format` (optional): String - Format of page content: "html" or "markdown" (default: "html")
- `content` (optional): String - Page content in HTML or Markdown format

**Output:**
- `data`: Object with created page details including id and requestId
- `result`: Boolean - Whether operation was successful
- `error`: String - Error message if failed

**Example Usage:**

Create a blank page:
```
Create a page called "Meeting Notes" in doc "abc123"
```

Create page with content:
```
Create a page called "Status Update" with HTML content "<h1>Project Status</h1><p>On track</p>" in doc "abc123"
```

Create a subpage:
```
Create a page called "Q1 Goals" as a subpage of "canvas-parent123" in doc "abc123"
```

Create with icon:
```
Create a page called "Launch Plan" with rocket icon in doc "abc123"
```

### update_page

Updates a page's metadata (name, subtitle, icon, image). Cannot update page content after creation. Returns HTTP 202 (Accepted). Requires Doc Maker permissions for updating title/icon.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc
- `page_id_or_name` (required): String - Page ID or name to update
- `name` (optional): String - New page name/title
- `subtitle` (optional): String - New page subtitle
- `icon_name` (optional): String - New icon name (e.g., "rocket", "star", "heart")
- `image_url` (optional): String - New cover image URL

**Output:**
- `data`: Object with updated page details including id and requestId
- `result`: Boolean - Whether operation was successful
- `error`: String - Error message if failed

**Example Usage:**

Update page title:
```
Update page "canvas-xyz789" in doc "abc123" with new name "Updated Project Plan"
```

Update page icon:
```
Update page "canvas-xyz789" in doc "abc123" with star icon
```

Update multiple fields:
```
Update page "canvas-xyz789" in doc "abc123" with name "Final Report" and subtitle "Q4 2024"
```

### delete_page

Deletes the specified page from a Coda doc. Returns HTTP 202 (Accepted) as deletion is queued for processing. Use page IDs rather than names when possible.

**Input Parameters:**
- `doc_id` (required): String - ID of the doc
- `page_id_or_name` (required): String - Page ID or name to delete

**Output:**
- `data`: Object with deletion confirmation including id and requestId
- `result`: Boolean - Whether operation was successful
- `error`: String - Error message if failed

**Note:** Using names is discouraged as they can be changed by users. If multiple pages have the same name, an arbitrary one will be selected.

**Example Usage:**

Delete page by ID:
```
Delete page "canvas-xyz789" from doc "abc123"
```

Delete page by name:
```
Delete page "Old Notes" from doc "abc123"
```

## Rate Limits

- **Reading data (GET)**: 100 requests per 6 seconds
- **Writing data (POST/PUT/PATCH)**: 10 requests per 6 seconds
- **Writing doc/page content (POST/PUT/PATCH)**: 5 requests per 10 seconds
- **Listing docs**: 4 requests per 6 seconds

**Note:** Write operations (like create_doc, create_page, update_page, delete_page) return HTTP 202, indicating the edit has been accepted and queued for asynchronous processing. Changes are typically processed within a few seconds.

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
- **Page management and organization**
- **Automated page creation with content**
- **Doc structure discovery and navigation**
- **Dynamic content generation in pages**
- **Page metadata management (icons, subtitles)**
- **Subpage creation for hierarchical docs**

## Technical Details

- **API Endpoint**: `https://coda.io/apis/v1`
- **Authentication**: Bearer token (Custom API token)
- **Response Format**: JSON
- **Async Processing**: Create operations return 202 and process asynchronously
- **API Version**: v1 (Standard Coda API)

## Permissions

**For list_docs, get_doc, list_pages, and get_page:**
- Requires read access to docs (granted by API token scope)

**For create_doc:**
- Token owner must be **Doc Maker** (or Admin) in the workspace
- OR workspace must have "Any member can create docs" enabled (Editor auto-promoted to Doc Maker)

**For create_page, update_page, and delete_page:**
- Token owner must be **Doc Maker** (or Admin) in the workspace
- Updating page title or icon specifically requires Doc Maker permissions

## Additional Resources

- [Coda API Official Documentation](https://coda.io/developers)
- [Coda API Getting Started Guide](https://coda.io/@oleg/getting-started-guide-coda-api)
- [Coda Account Settings (API Token)](https://coda.io/account)
