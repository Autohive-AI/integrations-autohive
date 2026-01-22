from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler
from typing import Dict, Any, List, Optional

microsoft_excel = Integration.load()

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
EXCEL_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_headers(context: ExecutionContext) -> Dict[str, str]:
    access_token = context.auth["credentials"]["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@microsoft_excel.action("excel_list_workbooks")
class ListWorkbooks(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            name_contains = inputs.get("name_contains")
            folder_path = inputs.get("folder_path")
            page_size = inputs.get("page_size", 25)
            page_token = inputs.get("page_token")

            filter_parts = [
                f"file/mimeType eq '{EXCEL_MIMETYPE}'"
            ]

            if folder_path:
                url = f"{GRAPH_BASE_URL}/me/drive/root:/{folder_path}:/children"
            else:
                url = f"{GRAPH_BASE_URL}/me/drive/root/children"

            params = {
                "$filter": " and ".join(filter_parts),
                "$top": min(page_size, 100),
                "$select": "id,name,webUrl,lastModifiedDateTime,file,size",
                "$orderby": "lastModifiedDateTime desc",
            }

            if page_token:
                url = page_token

            response = await context.fetch(url, method="GET", headers=headers, params=params if not page_token else None)

            if response.status_code != 200:
                return {
                    "workbooks": [],
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            items = data.get("value", [])

            workbooks = []
            for item in items:
                if item.get("file", {}).get("mimeType") == EXCEL_MIMETYPE:
                    if name_contains and name_contains.lower() not in item.get("name", "").lower():
                        continue
                    workbooks.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "webUrl": item.get("webUrl"),
                        "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                        "size": item.get("size"),
                    })

            result = {"workbooks": workbooks, "result": True}
            next_link = data.get("@odata.nextLink")
            if next_link:
                result["next_page_token"] = next_link

            return result

        except Exception as e:
            return {"workbooks": [], "result": False, "error": str(e)}


@microsoft_excel.action("excel_get_workbook")
class GetWorkbook(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]

            file_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}"
            file_response = await context.fetch(file_url, method="GET", headers=headers)

            if file_response.status_code != 200:
                return {
                    "result": False,
                    "error": f"Failed to get file info: {file_response.status_code}",
                }

            file_data = file_response.json()

            worksheets_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets"
            ws_response = await context.fetch(worksheets_url, method="GET", headers=headers)

            worksheets = []
            if ws_response.status_code == 200:
                ws_data = ws_response.json()
                for ws in ws_data.get("value", []):
                    worksheets.append({
                        "id": ws.get("id"),
                        "name": ws.get("name"),
                        "position": ws.get("position"),
                        "visibility": ws.get("visibility"),
                    })

            tables_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables"
            tables_response = await context.fetch(tables_url, method="GET", headers=headers)

            tables = []
            if tables_response.status_code == 200:
                tables_data = tables_response.json()
                for table in tables_data.get("value", []):
                    tables.append({
                        "id": table.get("id"),
                        "name": table.get("name"),
                        "showHeaders": table.get("showHeaders"),
                        "showTotals": table.get("showTotals"),
                        "style": table.get("style"),
                    })

            names_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/names"
            names_response = await context.fetch(names_url, method="GET", headers=headers)

            named_ranges = []
            if names_response.status_code == 200:
                names_data = names_response.json()
                for name in names_data.get("value", []):
                    named_ranges.append({
                        "name": name.get("name"),
                        "value": name.get("value"),
                        "type": name.get("type"),
                    })

            return {
                "workbook": {
                    "id": file_data.get("id"),
                    "name": file_data.get("name"),
                    "webUrl": file_data.get("webUrl"),
                    "lastModifiedDateTime": file_data.get("lastModifiedDateTime"),
                },
                "worksheets": worksheets,
                "tables": tables,
                "named_ranges": named_ranges,
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_list_worksheets")
class ListWorksheets(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets"
            response = await context.fetch(url, method="GET", headers=headers)

            if response.status_code != 200:
                return {
                    "worksheets": [],
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            worksheets = []
            for ws in data.get("value", []):
                worksheets.append({
                    "id": ws.get("id"),
                    "name": ws.get("name"),
                    "position": ws.get("position"),
                    "visibility": ws.get("visibility"),
                })

            return {"worksheets": worksheets, "result": True}

        except Exception as e:
            return {"worksheets": [], "result": False, "error": str(e)}


@microsoft_excel.action("excel_read_range")
class ReadRange(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            range_address = inputs["range"]
            value_render_option = inputs.get("value_render_option", "FORMATTED_VALUE")

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')"
            response = await context.fetch(url, method="GET", headers=headers)

            if response.status_code != 200:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            values = data.get("values", [])
            formulas = data.get("formulas", []) if value_render_option == "FORMULA" else []
            number_format = data.get("numberFormat", [])

            row_count = len(values)
            column_count = len(values[0]) if values else 0

            return {
                "range": data.get("address", range_address),
                "values": values,
                "formulas": formulas,
                "number_format": number_format,
                "row_count": row_count,
                "column_count": column_count,
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_write_range")
class WriteRange(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            range_address = inputs["range"]
            values = inputs["values"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')"

            body = {"values": values}
            response = await context.fetch(url, method="PATCH", headers=headers, json=body)

            if response.status_code not in [200, 201]:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            row_count = len(values)
            column_count = len(values[0]) if values else 0

            return {
                "updated_range": data.get("address", range_address),
                "updated_rows": row_count,
                "updated_columns": column_count,
                "updated_cells": row_count * column_count,
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_list_tables")
class ListTables(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs.get("worksheet_name")

            if worksheet_name:
                url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/tables"
            else:
                url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables"

            response = await context.fetch(url, method="GET", headers=headers)

            if response.status_code != 200:
                return {
                    "tables": [],
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            tables = []
            for table in data.get("value", []):
                tables.append({
                    "id": table.get("id"),
                    "name": table.get("name"),
                    "showHeaders": table.get("showHeaders"),
                    "showTotals": table.get("showTotals"),
                    "style": table.get("style"),
                })

            return {"tables": tables, "result": True}

        except Exception as e:
            return {"tables": [], "result": False, "error": str(e)}


@microsoft_excel.action("excel_get_table_data")
class GetTableData(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]
            select_columns = inputs.get("select_columns")
            top = inputs.get("top")
            skip = inputs.get("skip")

            header_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/headerRowRange"
            header_response = await context.fetch(header_url, method="GET", headers=headers)

            if header_response.status_code != 200:
                return {
                    "result": False,
                    "error": f"Failed to get table headers: {header_response.status_code}",
                }

            header_data = header_response.json()
            all_headers = header_data.get("values", [[]])[0]

            rows_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/dataBodyRange"
            rows_response = await context.fetch(rows_url, method="GET", headers=headers)

            if rows_response.status_code != 200:
                return {
                    "result": False,
                    "error": f"Failed to get table data: {rows_response.status_code}",
                }

            rows_data = rows_response.json()
            all_rows = rows_data.get("values", [])

            if select_columns:
                col_indices = [all_headers.index(c) for c in select_columns if c in all_headers]
                headers_out = [all_headers[i] for i in col_indices]
                rows_out = [[row[i] for i in col_indices] for row in all_rows]
            else:
                headers_out = all_headers
                rows_out = all_rows

            if skip:
                rows_out = rows_out[skip:]
            if top:
                rows_out = rows_out[:top]

            row_objects = []
            for row in rows_out:
                row_obj = {}
                for i, header in enumerate(headers_out):
                    row_obj[header] = row[i] if i < len(row) else None
                row_objects.append(row_obj)

            return {
                "headers": headers_out,
                "rows": row_objects,
                "total_rows": len(all_rows),
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_add_table_row")
class AddTableRow(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]
            rows = inputs["rows"]
            index = inputs.get("index")

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/rows/add"

            body: Dict[str, Any] = {"values": rows}
            if index is not None:
                body["index"] = index

            response = await context.fetch(url, method="POST", headers=headers, json=body)

            if response.status_code not in [200, 201]:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            range_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/range"
            range_response = await context.fetch(range_url, method="GET", headers=headers)
            table_range = ""
            if range_response.status_code == 200:
                table_range = range_response.json().get("address", "")

            return {
                "added_rows": len(rows),
                "table_range": table_range,
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_get_used_range")
class GetUsedRange(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            values_only = inputs.get("values_only", False)

            if values_only:
                url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/usedRange(valuesOnly=true)"
            else:
                url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/usedRange"

            response = await context.fetch(url, method="GET", headers=headers)

            if response.status_code != 200:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()
            values = data.get("values", [])

            return {
                "range": data.get("address", ""),
                "row_count": data.get("rowCount", len(values)),
                "column_count": data.get("columnCount", len(values[0]) if values else 0),
                "values": values,
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_create_worksheet")
class CreateWorksheet(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            name = inputs["name"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/add"

            body = {"name": name}
            response = await context.fetch(url, method="POST", headers=headers, json=body)

            if response.status_code not in [200, 201]:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code} - {response.text}",
                }

            data = response.json()

            return {
                "worksheet": {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "position": data.get("position"),
                    "visibility": data.get("visibility"),
                },
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_delete_worksheet")
class DeleteWorksheet(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}"
            response = await context.fetch(url, method="DELETE", headers=headers)

            if response.status_code not in [200, 204]:
                return {
                    "deleted": False,
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            return {"deleted": True, "result": True}

        except Exception as e:
            return {"deleted": False, "result": False, "error": str(e)}


@microsoft_excel.action("excel_create_table")
class CreateTable(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            range_address = inputs["range"]
            has_headers = inputs.get("has_headers", True)

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/tables/add"

            body = {"address": range_address, "hasHeaders": has_headers}
            response = await context.fetch(url, method="POST", headers=headers, json=body)

            if response.status_code not in [200, 201]:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            data = response.json()
            return {
                "table": {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "showHeaders": data.get("showHeaders"),
                },
                "result": True,
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_update_table_row")
class UpdateTableRow(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]
            row_index = inputs["row_index"]
            values = inputs["values"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/rows/itemAt(index={row_index})"

            body = {"values": [values]}
            response = await context.fetch(url, method="PATCH", headers=headers, json=body)

            if response.status_code not in [200, 201]:
                return {
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            data = response.json()
            return {"updated_row": data, "result": True}

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_excel.action("excel_delete_table_row")
class DeleteTableRow(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]
            row_index = inputs["row_index"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/rows/itemAt(index={row_index})"
            response = await context.fetch(url, method="DELETE", headers=headers)

            if response.status_code not in [200, 204]:
                return {
                    "deleted": False,
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            return {"deleted": True, "result": True}

        except Exception as e:
            return {"deleted": False, "result": False, "error": str(e)}


@microsoft_excel.action("excel_sort_range")
class SortRange(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            range_address = inputs["range"]
            sort_fields = inputs["sort_fields"]
            has_headers = inputs.get("has_headers", True)

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')/sort/apply"

            fields = []
            for sf in sort_fields:
                fields.append({
                    "key": sf.get("column_index", 0),
                    "ascending": sf.get("ascending", True),
                })

            body = {"fields": fields, "hasHeaders": has_headers, "matchCase": False}
            response = await context.fetch(url, method="POST", headers=headers, json=body)

            if response.status_code not in [200, 204]:
                return {
                    "sorted": False,
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            return {"sorted": True, "result": True}

        except Exception as e:
            return {"sorted": False, "result": False, "error": str(e)}


@microsoft_excel.action("excel_apply_filter")
class ApplyFilter(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]
            column_index = inputs["column_index"]
            filter_criteria = inputs["filter_criteria"]

            columns_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/columns"
            columns_response = await context.fetch(columns_url, method="GET", headers=headers)

            if columns_response.status_code != 200:
                return {
                    "filtered": False,
                    "result": False,
                    "error": f"Failed to get columns: {columns_response.status_code}",
                }

            columns = columns_response.json().get("value", [])
            if column_index >= len(columns):
                return {
                    "filtered": False,
                    "result": False,
                    "error": "Column index out of range",
                }

            column_id = columns[column_index].get("id")
            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/columns/{column_id}/filter/apply"

            body = {"criteria": filter_criteria}
            response = await context.fetch(url, method="POST", headers=headers, json=body)

            if response.status_code not in [200, 204]:
                return {
                    "filtered": False,
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            return {"filtered": True, "result": True}

        except Exception as e:
            return {"filtered": False, "result": False, "error": str(e)}


@microsoft_excel.action("excel_clear_filter")
class ClearFilter(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            table_name = inputs["table_name"]

            url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/tables/{table_name}/clearFilters"
            response = await context.fetch(url, method="POST", headers=headers)

            if response.status_code not in [200, 204]:
                return {
                    "cleared": False,
                    "result": False,
                    "error": f"Microsoft Graph API error: {response.status_code}",
                }

            return {"cleared": True, "result": True}

        except Exception as e:
            return {"cleared": False, "result": False, "error": str(e)}


@microsoft_excel.action("excel_format_range")
class FormatRange(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            workbook_id = inputs["workbook_id"]
            worksheet_name = inputs["worksheet_name"]
            range_address = inputs["range"]
            format_spec = inputs["format"]

            base_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')/format"

            if "font" in format_spec:
                font_url = f"{base_url}/font"
                await context.fetch(font_url, method="PATCH", headers=headers, json=format_spec["font"])

            if "fill" in format_spec:
                fill_url = f"{base_url}/fill"
                await context.fetch(fill_url, method="PATCH", headers=headers, json=format_spec["fill"])

            alignment_body = {}
            if "horizontalAlignment" in format_spec:
                alignment_body["horizontalAlignment"] = format_spec["horizontalAlignment"]
            if "verticalAlignment" in format_spec:
                alignment_body["verticalAlignment"] = format_spec["verticalAlignment"]

            if alignment_body:
                await context.fetch(base_url, method="PATCH", headers=headers, json=alignment_body)

            if "numberFormat" in format_spec:
                range_url = f"{GRAPH_BASE_URL}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')"
                await context.fetch(range_url, method="PATCH", headers=headers, json={"numberFormat": format_spec["numberFormat"]})

            return {"formatted": True, "result": True}

        except Exception as e:
            return {"formatted": False, "result": False, "error": str(e)}
