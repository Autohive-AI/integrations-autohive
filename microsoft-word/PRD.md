# Microsoft Word Integration - Product Requirements Document

## Overview

The Microsoft Word integration enables Autohive agents to read, create, and manipulate Word documents stored in OneDrive for Business, SharePoint, or Group drives via the Microsoft Graph API.

### Target Users
- Content creators automating document generation and updates
- Legal teams managing contracts and legal documents
- HR teams automating offer letters and policy documents
- Marketing teams generating reports and proposals
- Operations teams integrating document-based workflows

### Key Value Proposition
- Automate repetitive document creation and editing tasks through AI agents
- Extract text and structured content from Word documents without manual intervention
- Update documents programmatically based on workflow triggers
- Generate standardized documents from templates with dynamic content
- Search and replace text across documents at scale

---

## Technical Foundation

### API: Microsoft Graph API v1.0
- **Base URL**: `https://graph.microsoft.com/v1.0`
- **Document Access**: `/me/drive/items/{id}/` or `/me/drive/root:/{item-path}:/`
- **Content Access**: `/me/drive/items/{id}/content` for download/upload
- **Supported Formats**: Office Open XML (.docx) only - .doc NOT supported
- **Platform**: OneDrive for Business, SharePoint, Group drives (OneDrive Consumer NOT supported)

### Authentication
- **Type**: OAuth 2.0 (Platform authentication)
- **Provider**: Microsoft 365
- **Required Scopes**:
  - `Files.Read` - Read access to documents
  - `Files.ReadWrite` - Read and write access to documents
  - `offline_access` - Refresh token support

### Content Manipulation
The Word API provides access to document content through:
1. **Direct Content Download** - Get raw .docx file for parsing
2. **Content Conversion** - Convert to PDF, HTML, or other formats
3. **OOXML Manipulation** - Modify document XML structure directly

---

## Actions (Phase 1 - Core Features)

### 1. List Word Documents
**Action Name**: `word_list_documents`
**Display Name**: List Word Documents
**Description**: Find accessible Word documents (.docx) in OneDrive/SharePoint. Supports filtering by name.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name_contains` | string | No | Filter documents whose name contains this string |
| `folder_path` | string | No | Folder path to search in (default: root) |
| `page_size` | integer | No | Maximum results to return (default: 25, max: 100) |
| `page_token` | string | No | Token for pagination |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | List of document objects with id, name, webUrl, lastModifiedDateTime, size |
| `next_page_token` | string | Token for next page if more results exist |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

**Document Object**:
```json
{
  "id": "{drive-item-id}",
  "name": "Report.docx",
  "webUrl": "https://...",
  "lastModifiedDateTime": "2024-01-15T10:30:00Z",
  "size": 45678,
  "createdBy": {
    "user": {
      "displayName": "John Doe"
    }
  }
}
```

---

### 2. Get Document Metadata
**Action Name**: `word_get_document`
**Display Name**: Get Document Metadata
**Description**: Retrieve document properties including metadata, permissions, and file details.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `document` | object | Document properties |
| `id` | string | Drive item ID |
| `name` | string | File name |
| `size` | integer | File size in bytes |
| `webUrl` | string | URL to view in browser |
| `createdDateTime` | string | Creation timestamp |
| `lastModifiedDateTime` | string | Last modified timestamp |
| `createdBy` | object | User who created the document |
| `lastModifiedBy` | object | User who last modified the document |
| `parentReference` | object | Parent folder information |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 3. Get Document Content
**Action Name**: `word_get_content`
**Display Name**: Get Document Content
**Description**: Read the text content from a Word document. Returns plain text or structured paragraphs.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `format` | string | No | Output format: `text` (default), `html`, `markdown` |
| `include_metadata` | boolean | No | Include document properties (default: false) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Document text content in requested format |
| `word_count` | integer | Total word count |
| `character_count` | integer | Total character count |
| `paragraph_count` | integer | Number of paragraphs |
| `metadata` | object | Document properties if requested |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 4. Create Document
**Action Name**: `word_create_document`
**Display Name**: Create Document
**Description**: Create a new Word document with optional initial content.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Document name (with or without .docx extension) |
| `folder_path` | string | No | Folder path to create in (default: root) |
| `content` | string | No | Initial text content for the document |
| `template_id` | string | No | ID of template document to copy from |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `document_id` | string | The drive item ID of the created document |
| `name` | string | Final document name |
| `webUrl` | string | URL to view in browser |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 5. Update Document Content
**Action Name**: `word_update_content`
**Display Name**: Update Document Content
**Description**: Replace the entire content of a Word document with new content.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `content` | string | Yes | New text content for the document |
| `preserve_formatting` | boolean | No | Try to preserve existing formatting (default: false) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `updated` | boolean | Whether content was updated |
| `document_id` | string | The document ID |
| `word_count` | integer | New word count |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 6. Insert Text
**Action Name**: `word_insert_text`
**Display Name**: Insert Text
**Description**: Insert text at a specific location in the document.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `text` | string | Yes | Text to insert |
| `location` | string | Yes | Where to insert: `start`, `end`, `after_paragraph`, `before_paragraph` |
| `paragraph_index` | integer | No | Paragraph index (required for after_paragraph/before_paragraph) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `inserted` | boolean | Whether text was inserted |
| `document_id` | string | The document ID |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 7. Get Paragraphs
**Action Name**: `word_get_paragraphs`
**Display Name**: Get Paragraphs
**Description**: Get all paragraphs from a document with their content and formatting.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `start_index` | integer | No | Start paragraph index (default: 0) |
| `count` | integer | No | Maximum paragraphs to return (default: all) |
| `include_formatting` | boolean | No | Include paragraph formatting info (default: false) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `paragraphs` | array | List of paragraph objects |
| `total_count` | integer | Total number of paragraphs |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

**Paragraph Object**:
```json
{
  "index": 0,
  "text": "This is the paragraph content.",
  "style": "Normal",
  "formatting": {
    "alignment": "left",
    "lineSpacing": 1.15,
    "bold": false,
    "italic": false
  }
}
```

---

### 8. Search and Replace
**Action Name**: `word_search_replace`
**Display Name**: Search and Replace
**Description**: Find and replace text throughout the document.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `search_text` | string | Yes | Text to find |
| `replace_text` | string | Yes | Text to replace with |
| `match_case` | boolean | No | Case-sensitive search (default: false) |
| `match_whole_word` | boolean | No | Match whole words only (default: false) |
| `replace_all` | boolean | No | Replace all occurrences (default: true) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `replaced` | boolean | Whether any replacements were made |
| `replacement_count` | integer | Number of replacements made |
| `document_id` | string | The document ID |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 9. Export to PDF
**Action Name**: `word_export_pdf`
**Display Name**: Export to PDF
**Description**: Export the Word document to PDF format.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `output_name` | string | No | Name for the PDF file (default: same as document) |
| `save_to_drive` | boolean | No | Save PDF to OneDrive (default: false, returns download URL) |
| `folder_path` | string | No | Folder path if saving to drive |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `pdf_url` | string | URL to download/access the PDF |
| `pdf_id` | string | Drive item ID if saved to drive |
| `size` | integer | PDF file size in bytes |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 10. Get Tables
**Action Name**: `word_get_tables`
**Display Name**: Get Tables
**Description**: Extract tables from a Word document.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string | Yes | The drive item ID of the document |
| `table_index` | integer | No | Specific table index to retrieve (default: all tables) |
| `include_formatting` | boolean | No | Include cell formatting (default: false) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `tables` | array | List of table objects |
| `table_count` | integer | Total number of tables in document |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

**Table Object**:
```json
{
  "index": 0,
  "rows": 5,
  "columns": 3,
  "data": [
    ["Header 1", "Header 2", "Header 3"],
    ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
    ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
  ],
  "hasHeaderRow": true
}
```

---

## Error Handling

### Common Error Codes
| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 400 | BadRequest | Invalid request format or parameters |
| 401 | Unauthorized | Invalid or expired access token |
| 403 | Forbidden | Insufficient permissions |
| 404 | NotFound | Document or folder not found |
| 409 | Conflict | Resource conflict (e.g., duplicate name) |
| 413 | PayloadTooLarge | Content exceeds size limits |
| 423 | Locked | Document is locked for editing |
| 429 | TooManyRequests | Rate limit exceeded |
| 500 | InternalServerError | Microsoft Graph service error |
| 503 | ServiceUnavailable | Service temporarily unavailable |

### Document-Specific Errors
| Error | Description | Resolution |
|-------|-------------|------------|
| DocumentCorrupted | Document file is corrupted | Cannot process, user must fix source |
| UnsupportedFormat | File is .doc not .docx | Convert to .docx format |
| DocumentLocked | Document open by another user | Wait or request unlock |
| ContentTooLarge | Document exceeds processing limits | Process in sections |

---

## Rate Limits & Constraints

### API Limits
- **File Size**: Maximum 250 MB for document operations
- **Content Length**: Large documents may require chunked processing
- **Request Rate**: Standard Microsoft Graph limits apply (~10,000 requests per 10 minutes)

### Best Practices
1. Check document size before processing large files
2. Use pagination for listing operations
3. Implement exponential backoff for rate limiting
4. Cache document metadata to reduce API calls
5. Use batch operations when making multiple changes

---

## Implementation Notes

### File Path Resolution
Files can be accessed via:
- Drive Item ID: `/me/drive/items/{id}`
- File Path: `/me/drive/root:/{item-path}:`

### Content Download
```
GET /me/drive/items/{id}/content
Returns: Binary .docx file
```

### Content Upload
```
PUT /me/drive/items/{id}/content
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Body: Binary .docx file
```

### Format Conversion
```
GET /me/drive/items/{id}/content?format=pdf
Returns: PDF version of document
```

### Content-Type Headers
- Download: `application/octet-stream`
- Upload: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- PDF Export: `application/pdf`

### Document Parsing
The integration uses python-docx or similar library to:
- Parse .docx file structure (OOXML)
- Extract text content and paragraphs
- Read and modify tables
- Preserve formatting during updates

---

## Success Metrics

- **Integration Adoption**: Number of agents using Word actions
- **Action Success Rate**: >99% success rate for valid requests
- **Response Time**: <2s average for read operations, <5s for write operations
- **Document Processing**: <10s for documents under 10MB
- **User Satisfaction**: Reduction in manual document creation tasks

---

## Timeline

| Phase | Scope | Duration |
|-------|-------|----------|
| Phase 1 | Core Actions (1-10) | 2 weeks |
| Phase 2 | Advanced Actions (Headers, Footers, Sections) | 2 weeks |
| Phase 3 | Template Processing & Mail Merge | Future |
| Phase 4 | Comments & Track Changes | Future |

---

## Dependencies

- Microsoft 365 OAuth provider configured in Autohive
- `autohive-integrations-sdk` package
- Microsoft Graph API access
- `python-docx` library for document manipulation

---

## Future Enhancements (Phase 2+)

### Headers & Footers
- `word_get_headers` - Get header content
- `word_set_headers` - Set header content
- `word_get_footers` - Get footer content
- `word_set_footers` - Set footer content

### Sections
- `word_list_sections` - List document sections
- `word_add_section_break` - Add section break
- `word_format_section` - Set section formatting (margins, orientation)

### Styles
- `word_list_styles` - List available styles
- `word_apply_style` - Apply style to paragraph/text

### Comments & Revisions
- `word_get_comments` - Get document comments
- `word_add_comment` - Add comment to text
- `word_get_revisions` - Get tracked changes
- `word_accept_revision` - Accept/reject changes

### Images
- `word_insert_image` - Insert image into document
- `word_list_images` - List images in document

---

## Open Questions

1. Should we support real-time collaboration detection before edits?
2. Template variable syntax - use {{variable}} or ${variable}?
3. How to handle password-protected documents?
4. Should PDF export include option for specific page ranges?
5. Support for headers/footers in Phase 1 or defer?

---

## References

- [Microsoft Graph DriveItem API](https://learn.microsoft.com/en-us/graph/api/resources/driveitem)
- [Download File Content](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content)
- [Upload File Content](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content)
- [Convert File Format](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format)
- [python-docx Library](https://python-docx.readthedocs.io/)
- [Office Open XML (OOXML)](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-docx/)
