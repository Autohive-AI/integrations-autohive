# Dropbox Integration for Autohive

Connects Autohive to the Dropbox API to enable file browsing, metadata retrieval, search, and account management (read-only operations).

## Description

This integration provides read-only access to Dropbox's file storage platform. It allows users to browse folders, search files, retrieve metadata, get temporary download links, and access account information directly from Autohive.

The integration uses Dropbox API v2 with OAuth 2.0 authentication and implements 10 comprehensive read-only actions covering files, folders, search, and account information.

## Setup & Authentication

This integration uses **OAuth 2.0** authentication for secure access to your Dropbox account.

### Authentication Method

The integration uses OAuth 2.0 with the following scopes:
- `account_info.read` - Read account information
- `files.metadata.read` - Read file and folder metadata
- `files.content.read` - Read file content and download files

### Setup Steps in Autohive

1. Add Dropbox integration in Autohive
2. Click "Connect to Dropbox" to authorize the integration
3. Sign in to your Dropbox account when prompted
4. Review and authorize the requested permissions
5. You'll be redirected back to Autohive once authorization is complete

The OAuth integration automatically handles token management and refresh, so you don't need to manually manage access tokens.

## Action Results

All actions return a standardized response structure:
- `result` (boolean): Indicates whether the action succeeded (true) or failed (false)
- `error` (string, optional): Contains error message if the action failed
- Additional action-specific data fields (e.g., `entries`, `metadata`, `account`)

Example successful response:
```json
{
  "result": true,
  "metadata": {
    ".tag": "file",
    "name": "document.pdf",
    "path_display": "/Documents/document.pdf",
    "id": "id:a4ayc_80_OEAAAAAAAAAXw"
  }
}
```

Example error response:
```json
{
  "result": false,
  "error": "path/not_found/...",
  "metadata": {}
}
```

## Actions

### File and Folder Listing (2 actions)

#### `list_folder`
Lists contents of a folder.

**Inputs:**
- `path` (optional): Path to the folder (default: "" for root folder, or "/folder_name" for subfolders)
- `recursive` (optional): If true, list folder recursively (default: false)
- `include_deleted` (optional): If true, include deleted files (default: false)
- `include_has_explicit_shared_members` (optional): If true, include sharing info (default: false)
- `include_mounted_folders` (optional): If true, include mounted folders (default: true)
- `limit` (optional): Maximum number of results to return (1-2000)

**Outputs:**
- `entries`: Array of file and folder entries
- `cursor`: Cursor for pagination (use with list_folder_continue)
- `has_more`: Whether there are more entries to fetch
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

**Entry Structure:**
Each entry includes:
- `.tag`: "file" or "folder"
- `name`: File or folder name
- `path_display`: Display path
- `id`: Unique identifier
- For files: `size`, `client_modified`, `server_modified`, etc.

---

#### `list_folder_continue`
Continues listing folder contents using a cursor from list_folder.

**Inputs:**
- `cursor` (required): Cursor from previous list_folder call

**Outputs:**
- `entries`: Array of file and folder entries
- `cursor`: Cursor for pagination
- `has_more`: Whether there are more entries to fetch
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

### Metadata (1 action)

#### `get_metadata`
Returns metadata for a file or folder at a given path.

**Inputs:**
- `path` (required): Path to the file or folder (e.g., "/folder/file.txt")
- `include_deleted` (optional): If true, will return deleted metadata (default: false)
- `include_has_explicit_shared_members` (optional): If true, include sharing info (default: false)

**Outputs:**
- `metadata`: File or folder metadata object
  - `.tag`: "file" or "folder"
  - `name`: File or folder name
  - `path_display`: Display path
  - `id`: Unique identifier
  - For files: `size`, `client_modified`, `server_modified`, `content_hash`, etc.
  - For folders: `shared_folder_id`, etc.
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

### Download and Preview (3 actions)

#### `get_temporary_link`
Gets a temporary link to stream content of a file. Valid for 4 hours.

**Inputs:**
- `path` (required): Path to the file (e.g., "/folder/file.txt")

**Outputs:**
- `link`: Temporary download link (valid for 4 hours)
- `metadata`: Metadata for the file
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

**Note:** The temporary link allows direct download of the file content without authentication for 4 hours.

---

#### `get_preview`
Gets a preview for a file. Supports documents, images, and more.

**Inputs:**
- `path` (required): Path to the file to preview

**Outputs:**
- `preview`: Preview content or data
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

**Supported File Types:**
- Documents (PDF, Word, Excel, PowerPoint, etc.)
- Images (JPEG, PNG, GIF, etc.)
- Text files
- And more

---

#### `get_thumbnail`
Gets a thumbnail for an image file.

**Inputs:**
- `path` (required): Path to the image file
- `format` (optional): Image format - "jpeg" or "png" (default: "jpeg")
- `size` (optional): Thumbnail size (default: "w64h64")
  - Options: "w32h32", "w64h64", "w128h128", "w256h256", "w480h320", "w640h480", "w960h640", "w1024h768", "w2048h1536"
- `mode` (optional): How to resize the image (default: "strict")
  - "strict": Scale down the image to fit within size
  - "bestfit": Scale down the image to fit within size, preserving aspect ratio
  - "fitone_bestfit": Scale down the image to cover size, preserving aspect ratio

**Outputs:**
- `thumbnail`: Thumbnail data
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

### Search (2 actions)

#### `search`
Searches for files and folders by name and content.

**Inputs:**
- `query` (required): Search query string
- `path` (optional): Scope search to a specific folder path
- `max_results` (optional): Maximum number of results (1-1000, default: 100)
- `file_status` (optional): Filter by file status - "active" or "deleted"
- `filename_only` (optional): If true, search only file names, not content (default: false)

**Outputs:**
- `matches`: Array of search matches (each contains match_type and metadata)
- `has_more`: Whether there are more results
- `cursor`: Cursor for pagination (use with search_continue)
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

**Match Structure:**
Each match includes:
- `match_type`: Type of match (e.g., "filename", "content")
- `metadata`: File or folder metadata

---

#### `search_continue`
Continues search results using a cursor from search.

**Inputs:**
- `cursor` (required): Cursor from previous search call

**Outputs:**
- `matches`: Array of search matches
- `has_more`: Whether there are more results
- `cursor`: Cursor for pagination
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

### Account Information (2 actions)

#### `get_current_account`
Gets information about the current user's Dropbox account.

**Inputs:** None

**Outputs:**
- `account`: Account information object
  - `account_id`: Unique account identifier
  - `name`: User's name (display_name, given_name, surname, etc.)
  - `email`: User's email address
  - `email_verified`: Whether email is verified
  - `profile_photo_url`: URL to profile photo (if available)
  - `disabled`: Whether account is disabled
  - `country`: User's country code
  - `locale`: User's locale
  - `account_type`: Account type (.tag: "basic", "pro", "business")
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

#### `get_space_usage`
Gets the space usage information for the current user's account.

**Inputs:** None

**Outputs:**
- `used`: Total space used in bytes
- `allocation`: Space allocation details
  - `.tag`: Allocation type ("individual" or "team")
  - `allocated`: Total allocated space in bytes
  - Additional fields based on allocation type
- `result`: Success status (boolean)
- `error`: Error message if action failed (optional)

---

## Requirements

- `autohive-integrations-sdk` - The Autohive integrations SDK

## API Information

- **API Version**: v2
- **Base URLs**:
  - API: `https://api.dropboxapi.com/2`
  - Content: `https://content.dropboxapi.com/2`
- **Authentication**: OAuth 2.0
- **Documentation**: https://www.dropbox.com/developers/documentation/http/documentation
- **Rate Limits**: Dropbox uses a points-based rate limiting system. Each endpoint costs different points.

## Important Notes

- OAuth tokens are automatically managed by the platform
- Tokens are automatically refreshed when needed
- You can revoke access at any time from your Dropbox account settings
- All paths are relative to the app's root folder
- Empty string ("") represents the root folder
- All other paths must start with a slash (e.g., "/Documents/file.txt")
- Files and folders have both `path_display` (display format) and `path_lower` (normalized lowercase)
- Each file and folder has a unique `id` (e.g., "id:abc123xyz")
- Temporary links from `get_temporary_link` expire after 4 hours
- This integration provides **read-only** access - no upload, delete, or modify operations

## Testing

To test the integration:

1. Navigate to the integration directory: `cd dropbox`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure OAuth credentials through the Autohive platform
4. Run tests to verify functionality

## Common Use Cases

**File Browsing:**
1. List all files in root folder
2. Navigate through folder hierarchy
3. Get detailed metadata for specific files
4. Check file sizes and modification dates

**File Access:**
1. Get temporary download links for files
2. Generate previews for documents and images
3. Create thumbnails for image files
4. Access file content without full download

**Search and Discovery:**
1. Search for files by name
2. Search file contents for specific text
3. Filter search results by folder
4. Find recently modified files

**Account Management:**
1. View account information
2. Check space usage and quota
3. Monitor storage allocation
4. View account type and status

**Workflow Automation:**
1. Monitor folders for new files
2. Extract metadata for reporting
3. Generate download links for sharing
4. Search and index file contents
5. Track file modifications

## Path Examples

- Root folder: `""`
- Subfolder: `"/Documents"`
- File in root: `"/file.txt"`
- File in subfolder: `"/Documents/report.pdf"`
- Nested path: `"/Projects/2024/Q1/report.xlsx"`

## OAuth Scopes Explained

- **account_info.read**: Allows reading basic account information like name, email, and account type
- **files.metadata.read**: Allows listing folders, reading file/folder metadata, and searching
- **files.content.read**: Allows downloading file content, getting temporary links, and previews

## Version History

- **1.0.0** - Initial release with 10 read-only actions
  - Listing: list_folder, list_folder_continue (2 actions)
  - Metadata: get_metadata (1 action)
  - Download/Preview: get_temporary_link, get_preview, get_thumbnail (3 actions)
  - Search: search, search_continue (2 actions)
  - Account: get_current_account, get_space_usage (2 actions)

## Sources

- [Dropbox API v2 Documentation](https://www.dropbox.com/developers/documentation/http/documentation)
- [Dropbox OAuth Guide](https://developers.dropbox.com/oauth-guide)
- [Customizing OAuth Scopes](https://dropbox.tech/developers/customizing-scopes-in-oauth-flow)
