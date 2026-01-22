# Microsoft Excel Integration - Product Requirements Document

## Overview

The Microsoft Excel integration enables Autohive agents to read, write, and manipulate Excel workbooks stored in OneDrive for Business, SharePoint, or Group drives via the Microsoft Graph API.

### Target Users
- Business analysts automating data extraction and reporting
- Sales teams managing lead/customer data in Excel
- Finance teams automating spreadsheet operations
- Operations teams integrating Excel-based workflows

### Key Value Proposition
- Automate repetitive Excel tasks through AI agents
- Extract and analyze data from Excel without manual intervention
- Update spreadsheets programmatically based on workflow triggers
- Generate reports and aggregate data across multiple workbooks

---

## Technical Foundation

### API: Microsoft Graph API v1.0
- **Base URL**: `https://graph.microsoft.com/v1.0`
- **Workbook Access**: `/me/drive/items/{id}/workbook/` or `/me/drive/root:/{item-path}:/workbook/`
- **Supported Formats**: Office Open XML (.xlsx) only - .xls NOT supported
- **Platform**: OneDrive for Business, SharePoint, Group drives (OneDrive Consumer NOT supported)

### Authentication
- **Type**: OAuth 2.0 (Platform authentication)
- **Provider**: Microsoft 365
- **Required Scopes**:
  - `Files.Read` - Read access to workbooks
  - `Files.ReadWrite` - Read and write access to workbooks
  - `offline_access` - Refresh token support

### Session Management
The Excel API supports three modes:
1. **Persistent Session** - Changes are saved (most efficient)
2. **Non-Persistent Session** - Temporary changes, not saved
3. **Sessionless** - One-off requests (least efficient)

Sessions expire after 5-7 minutes of inactivity.

---

## Actions (Phase 1 - Basic Features)

### 1. List Excel Workbooks
**Action Name**: `excel_list_workbooks`
**Display Name**: List Excel Workbooks
**Description**: Find accessible Excel workbooks in OneDrive/SharePoint. Supports filtering by name.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name_contains` | string | No | Filter workbooks whose name contains this string |
| `folder_path` | string | No | Folder path to search in (default: root) |
| `page_size` | integer | No | Maximum results to return (default: 25, max: 100) |
| `page_token` | string | No | Token for pagination |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `workbooks` | array | List of workbook objects with id, name, webUrl, lastModifiedDateTime |
| `next_page_token` | string | Token for next page if more results exist |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 2. Get Workbook Metadata
**Action Name**: `excel_get_workbook`
**Display Name**: Get Workbook Metadata
**Description**: Retrieve workbook properties including list of worksheets, named ranges, and tables.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `workbook` | object | Workbook properties |
| `worksheets` | array | List of worksheet objects with id, name, position, visibility |
| `tables` | array | List of table objects with id, name, showHeaders |
| `named_ranges` | array | List of named ranges with name, value |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 3. List Worksheets
**Action Name**: `excel_list_worksheets`
**Display Name**: List Worksheets
**Description**: List all worksheet tabs in a workbook with their properties.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `worksheets` | array | List of worksheet objects |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

**Worksheet Object**:
```json
{
  "id": "{worksheet-id}",
  "name": "Sheet1",
  "position": 0,
  "visibility": "Visible"
}
```

---

### 4. Read Range
**Action Name**: `excel_read_range`
**Display Name**: Read Range
**Description**: Read cell values from a specified range using A1 notation.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Name of the worksheet |
| `range` | string | Yes | A1 notation range (e.g., "A1:D10", "Sheet1!A1:B5") |
| `value_render_option` | string | No | How values should be rendered: `FORMATTED_VALUE`, `UNFORMATTED_VALUE`, `FORMULA` |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `range` | string | The actual range read |
| `values` | array[array] | 2D array of cell values |
| `formulas` | array[array] | 2D array of formulas (if requested) |
| `number_format` | array[array] | 2D array of number formats |
| `row_count` | integer | Number of rows in result |
| `column_count` | integer | Number of columns in result |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 5. Write Range
**Action Name**: `excel_write_range`
**Display Name**: Write Range
**Description**: Write values to a specified cell range.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Name of the worksheet |
| `range` | string | Yes | A1 notation range for the starting cell/range |
| `values` | array[array] | Yes | 2D array of values to write |
| `input_option` | string | No | `RAW` or `USER_ENTERED` (default: USER_ENTERED) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `updated_range` | string | The range that was updated |
| `updated_rows` | integer | Number of rows updated |
| `updated_columns` | integer | Number of columns updated |
| `updated_cells` | integer | Total cells updated |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 6. List Tables
**Action Name**: `excel_list_tables`
**Display Name**: List Tables
**Description**: List all tables in a workbook or specific worksheet.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | No | Filter tables to specific worksheet |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `tables` | array | List of table objects |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

**Table Object**:
```json
{
  "id": "1",
  "name": "Table1",
  "showHeaders": true,
  "showTotals": false,
  "style": "TableStyleMedium2"
}
```

---

### 7. Get Table Data
**Action Name**: `excel_get_table_data`
**Display Name**: Get Table Data
**Description**: Read all rows from a table including headers.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name or ID of the table |
| `select_columns` | array | No | Specific column names to return |
| `top` | integer | No | Maximum rows to return |
| `skip` | integer | No | Rows to skip (for pagination) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `headers` | array | Column header names |
| `rows` | array[object] | Array of row objects (key-value pairs) |
| `total_rows` | integer | Total row count in table |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 8. Add Table Row
**Action Name**: `excel_add_table_row`
**Display Name**: Add Table Row
**Description**: Append one or more rows to an existing table.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name or ID of the table |
| `rows` | array[array] | Yes | Array of row values to add |
| `index` | integer | No | Position to insert (null = end) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `added_rows` | integer | Number of rows added |
| `table_range` | string | Updated table range |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 9. Create Worksheet
**Action Name**: `excel_create_worksheet`
**Display Name**: Create Worksheet
**Description**: Add a new worksheet tab to a workbook.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `name` | string | Yes | Name for the new worksheet |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `worksheet` | object | Created worksheet details |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 10. Delete Worksheet
**Action Name**: `excel_delete_worksheet`
**Display Name**: Delete Worksheet
**Description**: Remove a worksheet from the workbook.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Name of the worksheet to delete |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `deleted` | boolean | Whether worksheet was deleted |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

## Actions (Phase 2 - Advanced Features)

### 11. Create Table
**Action Name**: `excel_create_table`
**Display Name**: Create Table
**Description**: Convert a range to an Excel table with headers.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Worksheet containing the range |
| `range` | string | Yes | A1 range to convert to table |
| `has_headers` | boolean | No | First row contains headers (default: true) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `table` | object | Created table details |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 12. Update Table Row
**Action Name**: `excel_update_table_row`
**Display Name**: Update Table Row
**Description**: Update values in an existing table row.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name or ID of the table |
| `row_index` | integer | Yes | Zero-based row index to update |
| `values` | array | Yes | New values for the row |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `updated_row` | object | Updated row data |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 13. Delete Table Row
**Action Name**: `excel_delete_table_row`
**Display Name**: Delete Table Row
**Description**: Remove a row from a table.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name or ID of the table |
| `row_index` | integer | Yes | Zero-based row index to delete |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `deleted` | boolean | Whether row was deleted |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 14. Sort Range
**Action Name**: `excel_sort_range`
**Display Name**: Sort Range
**Description**: Sort a range or table by specified columns.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Worksheet name |
| `range` | string | Yes | Range to sort |
| `sort_fields` | array | Yes | Array of sort criteria |
| `has_headers` | boolean | No | First row is headers (default: true) |

**Sort Field Object**:
```json
{
  "column_index": 0,
  "ascending": true
}
```

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `sorted` | boolean | Whether sort was applied |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 15. Apply Filter
**Action Name**: `excel_apply_filter`
**Display Name**: Apply Filter
**Description**: Apply filter to a table column.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name of the table |
| `column_index` | integer | Yes | Zero-based column index |
| `filter_criteria` | object | Yes | Filter criteria object |

**Filter Criteria Examples**:
```json
// Values filter
{ "filterOn": "Values", "values": ["Active", "Pending"] }

// Custom filter
{ "filterOn": "Custom", "criterion1": ">100" }
```

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `filtered` | boolean | Whether filter was applied |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 16. Clear Filter
**Action Name**: `excel_clear_filter`
**Display Name**: Clear Filter
**Description**: Clear filters from a table.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `table_name` | string | Yes | Name of the table |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `cleared` | boolean | Whether filters were cleared |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 17. Get Used Range
**Action Name**: `excel_get_used_range`
**Display Name**: Get Used Range
**Description**: Get the range that contains data in a worksheet.

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Worksheet name |
| `values_only` | boolean | No | Only include cells with values (default: false) |

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `range` | string | A1 notation of used range |
| `row_count` | integer | Number of rows |
| `column_count` | integer | Number of columns |
| `values` | array[array] | Cell values if requested |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

### 18. Format Range
**Action Name**: `excel_format_range`
**Display Name**: Format Range
**Description**: Apply formatting to a cell range (font, fill, borders, number format).

**Inputs**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workbook_id` | string | Yes | The drive item ID of the workbook |
| `worksheet_name` | string | Yes | Worksheet name |
| `range` | string | Yes | A1 range to format |
| `format` | object | Yes | Format specification |

**Format Object**:
```json
{
  "font": {
    "bold": true,
    "color": "#FF0000",
    "size": 12,
    "name": "Arial"
  },
  "fill": {
    "color": "#FFFF00"
  },
  "horizontalAlignment": "Center",
  "verticalAlignment": "Center",
  "numberFormat": "#,##0.00"
}
```

**Outputs**:
| Field | Type | Description |
|-------|------|-------------|
| `formatted` | boolean | Whether formatting was applied |
| `result` | boolean | Success/failure indicator |
| `error` | string | Error message if failed |

---

## Error Handling

### Common Error Codes
| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 400 | BadRequest | Invalid request format or parameters |
| 401 | Unauthorized | Invalid or expired access token |
| 403 | Forbidden | Insufficient permissions |
| 404 | NotFound | Workbook, worksheet, or range not found |
| 409 | Conflict | Resource conflict (e.g., duplicate name) |
| 429 | TooManyRequests | Rate limit exceeded |
| 500 | InternalServerError | Microsoft Graph service error |

### Session Errors
- Session expired (404) - Create new session and retry
- Session not found - Re-authenticate

---

## Rate Limits & Constraints

### API Limits
- **Large Range**: Avoid ranges exceeding 5M cells
- **Batch Operations**: Recommended for multiple operations
- **Session Timeout**: 5-7 minutes of inactivity

### Best Practices
1. Use sessions for multiple operations on same workbook
2. Break large range operations into smaller chunks
3. Use table operations when working with structured data
4. Implement exponential backoff for rate limiting

---

## Implementation Notes

### File Path Resolution
Files can be accessed via:
- Drive Item ID: `/me/drive/items/{id}/workbook/`
- File Path: `/me/drive/root:/{item-path}:/workbook/`

### Session Header
```
workbook-session-id: {session-id}
```

### Content Type
All requests use `application/json`

---

## Success Metrics

- **Integration Adoption**: Number of agents using Excel actions
- **Action Success Rate**: >99% success rate for valid requests
- **Response Time**: <2s average for read operations, <5s for write operations
- **User Satisfaction**: Reduction in manual Excel data entry tasks

---

## Timeline

| Phase | Scope | Duration |
|-------|-------|----------|
| Phase 1 | Basic Actions (1-10) | 2 weeks |
| Phase 2 | Advanced Actions (11-18) | 2 weeks |
| Phase 3 | Charts & Pivot Tables | Future |

---

## Dependencies

- Microsoft 365 OAuth provider configured in Autohive
- `autohive-integrations-sdk` package
- Microsoft Graph API access

---

## Open Questions

1. Should we support creating new workbooks, or only work with existing files?
2. Chart image export - is this needed for Phase 1?
3. Pivot table support - complexity vs. demand assessment needed
4. Batch update API for multiple operations in single request?

---

## References

- [Microsoft Graph Excel API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/excel)
- [Excel API Overview](https://learn.microsoft.com/en-us/graph/excel-concept-overview)
- [Working with Excel Sessions](https://learn.microsoft.com/en-us/graph/excel-manage-sessions)
- [Write to Excel Workbook](https://learn.microsoft.com/en-us/graph/excel-write-to-workbook)
