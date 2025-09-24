from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import uuid
import os
import base64
from io import BytesIO
from PIL import Image
import markdown
from bs4 import BeautifulSoup
import re

doc_maker = Integration.load()

documents = {}
uploaded_images = {}

def process_files(files: List[Dict[str, Any]]) -> Dict[str, BytesIO]:
    """Process files from the files parameter and return streams by filename"""
    processed_files = {}
    if files:
        for file_item in files:
            content_as_string = file_item['content']

            padded_content_string = content_as_string + '=' * (-len(content_as_string) % 4)

            file_binary_data = base64.urlsafe_b64decode(padded_content_string.encode('ascii'))
            file_stream = BytesIO(file_binary_data)

            processed_files[file_item['name']] = file_stream

    return processed_files

def load_document_from_files(document_id: str, files: List[Dict[str, Any]]) -> None:
    """Load document from files parameter if not in memory"""
    if document_id not in documents and files:
        processed_files = process_files(files)

        for filename, file_stream in processed_files.items():
            if filename.lower().endswith('.docx') or filename.lower().endswith('.bin'):
                try:
                    doc = Document(file_stream)
                    documents[document_id] = doc
                    return
                except Exception as e:
                    continue

        # If no valid Word file found, provide better error message
        available_files = list(processed_files.keys())
        raise ValueError(f"No valid Word file found in files. Tried to load: {available_files}. Files may be corrupted or not Word format.")
    elif document_id not in documents:
        raise ValueError(f"Document {document_id} not found and no files provided for loading")

async def save_and_return_document(original_result: Dict[str, Any], document_id: str, context: ExecutionContext, custom_filename: str = None) -> Dict[str, Any]:
    """Helper to save document and return combined result"""
    save_action = SaveDocumentAction()

    if custom_filename:
        if not custom_filename.lower().endswith('.docx'):
            custom_filename += '.docx'
        file_path = custom_filename
    else:
        file_path = f"{document_id}.docx"

    save_inputs = {
        "document_id": document_id,
        "file_path": file_path
    }
    save_result = await save_action.execute(save_inputs, context)

    combined_result = original_result.copy()
    combined_result.update({
        "saved": save_result["saved"],
        "file_path": save_result["file_path"],
        "file": save_result["file"],
        "error": save_result.get("error", "")
    })
    return combined_result

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def iter_block_items(parent):
    """
    Iterate through paragraphs and tables in document order.
    Generates a reference to each paragraph and table child within parent.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Parent must be Document or _Cell")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def detect_placeholder_patterns(text: str) -> bool:
    """Detect if text looks like a placeholder that needs filling"""
    if not text or len(text.strip()) == 0:
        return True  # Empty text is fillable

    text = text.strip().lower()

    # Common placeholder patterns
    placeholder_patterns = [
        r'\{\{.*?\}\}',  # {{field}}
        r'\[.*?\]',      # [field]
        r'__.*?__',      # __field__
        r'\{.*?\}',      # {field}
        r'insert.*here', # "insert name here"
        r'add.*here',    # "add content here"
        r'data here',    # "data here"
        r'your.*here',   # "your name here"
        r'enter.*',      # "enter details"
        r'type.*here',   # "type content here"
        r'^(xxx+|yyy+|zzz+)$',  # "XXX", "YYY", etc.
        r'^(_+|\.+|-+)$',       # "___", "...", "---"
        r'(to be|tbd|tbc)',     # "to be determined"
        r'(sample|example|placeholder|dummy)', # sample text
    ]

    # Check if text matches any placeholder pattern
    for pattern in placeholder_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # Short generic text (likely placeholder)
    if len(text) < 20 and any(word in text for word in ['name', 'date', 'title', 'content', 'text', 'data', 'info']):
        return True

    return False

def analyze_document_structure(doc: Document) -> dict:
    """Analyze document structure and identify fillable elements"""
    elements = []
    element_index = 0

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            is_fillable = detect_placeholder_patterns(text)

            elements.append({
                "type": "paragraph",
                "index": element_index,
                "content": text,
                "is_fillable": is_fillable,
                "length": len(text),
                "style": block.style.name if block.style else "Normal"
            })

        elif isinstance(block, Table):
            table_info = {
                "type": "table",
                "index": element_index,
                "rows": len(block.rows),
                "cols": len(block.columns) if block.rows else 0,
                "cells": []
            }

            for row_idx, row in enumerate(block.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    is_fillable = detect_placeholder_patterns(cell_text)

                    table_info["cells"].append({
                        "row": row_idx,
                        "col": col_idx,
                        "content": cell_text,
                        "is_fillable": is_fillable,
                        "length": len(cell_text)
                    })

            elements.append(table_info)

        element_index += 1

    # Summary statistics
    fillable_paragraphs = len([e for e in elements if e["type"] == "paragraph" and e["is_fillable"]])
    fillable_cells = sum(len([c for c in e.get("cells", []) if c["is_fillable"]]) for e in elements if e["type"] == "table")

    return {
        "total_elements": len(elements),
        "paragraphs": len([e for e in elements if e["type"] == "paragraph"]),
        "tables": len([e for e in elements if e["type"] == "table"]),
        "fillable_paragraphs": fillable_paragraphs,
        "fillable_cells": fillable_cells,
        "elements": elements
    }

def parse_markdown_to_docx(doc: Document, markdown_text: str) -> None:
    """Parse markdown text and add elements to Word document"""
    # Convert markdown to HTML
    html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')

    # Process each HTML element in order
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote', 'table', 'pre']):
        if element.name.startswith('h'):
            # Handle headings
            level = int(element.name[1])  # Extract number from h1, h2, etc.
            text = element.get_text().strip()
            if text:
                doc.add_heading(text, level=level)

        elif element.name == 'p':
            # Handle paragraphs with inline formatting
            paragraph = doc.add_paragraph()
            _add_formatted_text_to_paragraph(paragraph, element)

        elif element.name in ['ul', 'ol']:
            # Handle lists
            is_numbered = element.name == 'ol'
            for li in element.find_all('li', recursive=False):
                text = li.get_text().strip()
                if text:
                    if is_numbered:
                        paragraph = doc.add_paragraph(text, style='List Number')
                    else:
                        paragraph = doc.add_paragraph(text, style='List Bullet')

        elif element.name == 'blockquote':
            # Handle blockquotes
            text = element.get_text().strip()
            if text:
                paragraph = doc.add_paragraph(text, style='Quote')

        elif element.name == 'table':
            # Handle tables
            _add_table_from_html(doc, element)

        elif element.name == 'pre':
            # Handle code blocks
            code_text = element.get_text()
            if code_text:
                paragraph = doc.add_paragraph(code_text)
                # Apply monospace font to code
                for run in paragraph.runs:
                    run.font.name = 'Courier New'

def _add_formatted_text_to_paragraph(paragraph, html_element):
    """Add formatted text from HTML element to Word paragraph"""
    # Handle direct text and formatting
    for content in html_element.contents:
        if hasattr(content, 'name') and content.name:
            # This is an HTML tag
            if content.name == 'strong' or content.name == 'b':
                run = paragraph.add_run(content.get_text())
                run.bold = True
            elif content.name == 'em' or content.name == 'i':
                run = paragraph.add_run(content.get_text())
                run.italic = True
            elif content.name == 'code':
                run = paragraph.add_run(content.get_text())
                run.font.name = 'Courier New'
            elif content.name == 'u':
                run = paragraph.add_run(content.get_text())
                run.underline = True
            else:
                # Nested elements - recursively process only if it has contents
                if hasattr(content, 'contents'):
                    _add_formatted_text_to_paragraph(paragraph, content)
                else:
                    # Just add the text content
                    text = content.get_text()
                    if text:
                        paragraph.add_run(text)
        else:
            # This is plain text (NavigableString) - preserve ALL whitespace
            text = str(content)
            if text:  # Don't strip() here to preserve spaces
                paragraph.add_run(text)

def _add_table_from_html(doc: Document, table_element):
    """Add a table from HTML table element to Word document"""
    rows = table_element.find_all('tr')
    if not rows:
        return

    # Determine table dimensions
    max_cols = 0
    for row in rows:
        cols = len(row.find_all(['td', 'th']))
        max_cols = max(max_cols, cols)

    if max_cols == 0:
        return

    # Create Word table
    table = doc.add_table(rows=len(rows), cols=max_cols)
    table.style = 'Table Grid'

    # Fill table data
    for row_idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        for col_idx, cell in enumerate(cells):
            if col_idx < max_cols:
                word_cell = table.cell(row_idx, col_idx)
                text = cell.get_text().strip()
                word_cell.text = text

                # Make header cells bold
                if cell.name == 'th':
                    for paragraph in word_cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True

# ---- Action Handlers ----

@doc_maker.action("get_document_elements")
class GetDocumentElementsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        include_content = inputs.get("include_content", True)
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]

        # Analyze document structure
        analysis = analyze_document_structure(doc)

        # Filter content if requested
        if not include_content:
            for element in analysis["elements"]:
                if element["type"] == "paragraph":
                    element["content"] = f"[{element['length']} chars]" if element["length"] > 0 else "[empty]"
                elif element["type"] == "table":
                    for cell in element["cells"]:
                        cell["content"] = f"[{cell['length']} chars]" if cell["length"] > 0 else "[empty]"

        return analysis

@doc_maker.action("create_document")
class CreateDocumentAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        title = inputs.get("title")
        markdown_content = inputs.get("markdown_content")
        files = inputs.get("files", [])
        custom_filename = inputs.get("custom_filename")

        processed_files = process_files(files)

        template_file = None
        for filename, file_stream in processed_files.items():
            if filename.lower().endswith('.docx'):
                template_file = file_stream
                break

        if template_file:
            doc = Document(template_file)
        else:
            doc = Document()

        # Add title if provided (but not if we have markdown content with its own title)
        if title and not markdown_content:
            title_paragraph = doc.add_heading(title, level=1)

        # Process markdown content if provided
        if markdown_content:
            parse_markdown_to_docx(doc, markdown_content)

        # Generate unique ID and store document
        document_id = str(uuid.uuid4())
        documents[document_id] = doc

        result = {
            "document_id": document_id,
            "paragraph_count": len(doc.paragraphs),
            "markdown_processed": bool(markdown_content)
        }

        return await save_and_return_document(result, document_id, context, custom_filename)



@doc_maker.action("add_table")
class AddTableAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        rows = inputs["rows"]
        cols = inputs["cols"]
        data = inputs.get("data", [])
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]
        table = doc.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'

        # Fill table with data if provided
        for row_idx, row_data in enumerate(data[:rows]):
            for col_idx, cell_value in enumerate(row_data[:cols]):
                table.cell(row_idx, col_idx).text = str(cell_value)

        original_result = {"table_rows": rows, "table_cols": cols}
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("add_image")
class AddImageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        width = inputs.get("width")  # in inches
        height = inputs.get("height")  # in inches
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        processed_files = process_files(files)
        image_file = None

        for file_item in files:
            filename = file_item['name']
            content_type = file_item.get('contentType', '')

            # Check if it's an image by extension or content type
            is_image_by_extension = any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'])
            is_image_by_content_type = content_type.startswith('image/')

            if is_image_by_extension or is_image_by_content_type:
                image_file = processed_files[filename]
                break

        if not image_file:
            raise ValueError("No image file found in files parameter")

        doc = documents[document_id]
        paragraph = doc.add_paragraph()

        if width and height:
            paragraph.add_run().add_picture(image_file, width=Inches(width), height=Inches(height))
        elif width:
            paragraph.add_run().add_picture(image_file, width=Inches(width))
        elif height:
            paragraph.add_run().add_picture(image_file, height=Inches(height))
        else:
            paragraph.add_run().add_picture(image_file)

        original_result = {"image_added": True}
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("add_markdown_content")
class AddMarkdownContentAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        markdown_text = inputs["markdown_content"]
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]

        # Parse and add markdown content to document
        parse_markdown_to_docx(doc, markdown_text)

        # Count elements added (approximate by counting paragraphs and headings added)
        elements_added = len([p for p in doc.paragraphs if p.text.strip()])

        original_result = {
            "markdown_processed": True,
            "elements_added": elements_added
        }
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("update_by_position")
class UpdateByPositionAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        updates = inputs["updates"]
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]
        changes_made = []

        # Process updates
        for update in updates:
            update_type = update.get("type")

            if update_type == "paragraph":
                paragraph_index = update["index"]
                new_content = update["content"]

                # Get paragraph by index using iter_block_items
                paragraphs = [block for block in iter_block_items(doc) if isinstance(block, Paragraph)]

                if paragraph_index < len(paragraphs):
                    paragraph = paragraphs[paragraph_index]

                    # Preserve formatting by clearing and adding new text
                    paragraph.clear()
                    paragraph.text = new_content
                    changes_made.append(f"Updated paragraph {paragraph_index}")
                else:
                    changes_made.append(f"Paragraph {paragraph_index} not found")

            elif update_type == "table_cell":
                table_index = update["table_index"]
                row = update["row"]
                col = update["col"]
                new_content = update["content"]

                # Get table by index
                tables = [block for block in iter_block_items(doc) if isinstance(block, Table)]

                if table_index < len(tables):
                    table = tables[table_index]
                    if row < len(table.rows) and col < len(table.columns):
                        cell = table.cell(row, col)
                        cell.text = new_content
                        changes_made.append(f"Updated table {table_index} cell ({row},{col})")
                    else:
                        changes_made.append(f"Cell ({row},{col}) out of range in table {table_index}")
                else:
                    changes_made.append(f"Table {table_index} not found")

        original_result = {
            "updates_applied": len(changes_made),
            "changes_made": changes_made
        }
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("find_and_replace")
class FindAndReplaceAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        replacements = inputs["replacements"]
        case_sensitive = inputs.get("case_sensitive", False)
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]
        total_replacements = 0
        warnings = []
        skipped_replacements = []

        for replacement in replacements:
            find_text = replacement["find"]
            replace_text = replacement.get("replace", "")  # Default to empty string if not provided
            replace_all = replacement.get("replace_all", False)

            # Validation
            if not find_text or len(find_text.strip()) == 0:
                warnings.append(f"Skipped replacement: 'find' text cannot be empty")
                continue

            # Handle space-as-delete (convert single space to empty for deletion)
            if replace_text == " ":
                replace_text = ""

            # First, scan for all matches to check for multiple occurrences
            matches_found = []

            # Scan paragraphs for matches
            for para_idx, paragraph in enumerate(doc.paragraphs):
                if case_sensitive:
                    if find_text in paragraph.text:
                        matches_found.append({
                            "type": "paragraph",
                            "index": para_idx,
                            "content": paragraph.text[:100] + "..." if len(paragraph.text) > 100 else paragraph.text,
                            "context": f"Paragraph {para_idx}"
                        })
                else:
                    if find_text.lower() in paragraph.text.lower():
                        matches_found.append({
                            "type": "paragraph",
                            "index": para_idx,
                            "content": paragraph.text[:100] + "..." if len(paragraph.text) > 100 else paragraph.text,
                            "context": f"Paragraph {para_idx}"
                        })

            # Scan tables for matches
            for table_idx, table in enumerate(doc.tables):
                for row_idx, row in enumerate(table.rows):
                    for col_idx, cell in enumerate(row.cells):
                        if case_sensitive:
                            if find_text in cell.text:
                                matches_found.append({
                                    "type": "table_cell",
                                    "table_index": table_idx,
                                    "row": row_idx,
                                    "col": col_idx,
                                    "content": cell.text,
                                    "context": f"Table {table_idx}, Row {row_idx}, Col {col_idx}"
                                })
                        else:
                            if find_text.lower() in cell.text.lower():
                                matches_found.append({
                                    "type": "table_cell",
                                    "table_index": table_idx,
                                    "row": row_idx,
                                    "col": col_idx,
                                    "content": cell.text,
                                    "context": f"Table {table_idx}, Row {row_idx}, Col {col_idx}"
                                })

            # Safety check for multiple matches
            if len(matches_found) > 1 and not replace_all:
                skipped_replacement = {
                    "find_text": find_text,
                    "matches_count": len(matches_found),
                    "matches_found": matches_found,
                    "safety_message": f"MULTIPLE MATCHES DETECTED: '{find_text}' found in {len(matches_found)} locations. Use more specific context or set replace_all=true to replace all instances."
                }
                skipped_replacements.append(skipped_replacement)
                warnings.append(f"Skipped '{find_text}': {len(matches_found)} matches found - be more specific or use replace_all=true")
                continue  # Skip this replacement

            elif len(matches_found) == 0:
                warnings.append(f"No matches found for '{find_text}'")
                continue

            # Proceed with replacement
            replacements_count = 0

            # Perform replacements in paragraphs
            for paragraph in doc.paragraphs:
                if case_sensitive:
                    if find_text in paragraph.text:
                        paragraph.text = paragraph.text.replace(find_text, replace_text)
                        replacements_count += 1
                else:
                    original_text = paragraph.text
                    new_text = re.sub(re.escape(find_text), replace_text, original_text, flags=re.IGNORECASE)
                    if new_text != original_text:
                        paragraph.text = new_text
                        replacements_count += 1

            # Perform replacements in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if case_sensitive:
                            if find_text in cell.text:
                                cell.text = cell.text.replace(find_text, replace_text)
                                replacements_count += 1
                        else:
                            original_text = cell.text
                            new_text = re.sub(re.escape(find_text), replace_text, original_text, flags=re.IGNORECASE)
                            if new_text != original_text:
                                cell.text = new_text
                                replacements_count += 1

            total_replacements += replacements_count

        original_result = {
            "total_replacements": total_replacements,
            "replacements_processed": len(replacements),
            "skipped_replacements": skipped_replacements,
            "warnings": warnings,
            "safety_checks_performed": True
        }
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("fill_template_fields")
class FillTemplateFieldsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        template_data = inputs["template_data"]
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]
        changes_made = []

        # Process different types of template data

        # 1. Placeholder data ({{field}} format)
        if "placeholder_data" in template_data:
            for placeholder, value in template_data["placeholder_data"].items():
                replacement_count = 0

                # Replace in paragraphs
                for paragraph in doc.paragraphs:
                    if placeholder in paragraph.text:
                        paragraph.text = paragraph.text.replace(placeholder, str(value))
                        replacement_count += 1

                # Replace in tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if placeholder in cell.text:
                                cell.text = cell.text.replace(placeholder, str(value))
                                replacement_count += 1

                if replacement_count > 0:
                    changes_made.append(f"Replaced '{placeholder}' {replacement_count} times")

        # 2. Position-based updates
        if "position_data" in template_data:
            paragraphs = [block for block in iter_block_items(doc) if isinstance(block, Paragraph)]
            tables = [block for block in iter_block_items(doc) if isinstance(block, Table)]

            for position_key, new_content in template_data["position_data"].items():
                if position_key.startswith("paragraph_"):
                    idx = int(position_key.split("_")[1])
                    if idx < len(paragraphs):
                        paragraphs[idx].text = str(new_content)
                        changes_made.append(f"Updated paragraph {idx}")

                elif position_key.startswith("table_"):
                    # Format: table_0_row_1_col_2
                    parts = position_key.split("_")
                    table_idx = int(parts[1])
                    row_idx = int(parts[3])
                    col_idx = int(parts[5])

                    if table_idx < len(tables):
                        table = tables[table_idx]
                        if row_idx < len(table.rows) and col_idx < len(table.columns):
                            table.cell(row_idx, col_idx).text = str(new_content)
                            changes_made.append(f"Updated table {table_idx} cell ({row_idx},{col_idx})")

        # 3. Search and replace patterns
        if "search_replace" in template_data:
            for item in template_data["search_replace"]:
                find_text = item["find"]
                replace_text = item["replace"]
                replacement_count = 0

                # Replace in paragraphs
                for paragraph in doc.paragraphs:
                    if find_text.lower() in paragraph.text.lower():
                        original_text = paragraph.text
                        paragraph.text = re.sub(re.escape(find_text), replace_text, original_text, flags=re.IGNORECASE)
                        if paragraph.text != original_text:
                            replacement_count += 1

                # Replace in tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if find_text.lower() in cell.text.lower():
                                original_text = cell.text
                                cell.text = re.sub(re.escape(find_text), replace_text, original_text, flags=re.IGNORECASE)
                                if cell.text != original_text:
                                    replacement_count += 1

                if replacement_count > 0:
                    changes_made.append(f"Found and replaced '{find_text}' {replacement_count} times")

        original_result = {
            "fields_filled": len(changes_made),
            "changes_made": changes_made,
            "template_processed": True
        }
        return await save_and_return_document(original_result, document_id, context)

@doc_maker.action("save_document")
class SaveDocumentAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        file_path = inputs["file_path"]

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]

        # Save document to memory buffer instead of disk
        try:
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            file_content = buffer.getvalue()

            # Encode as base64
            content_base64 = base64.b64encode(file_content).decode('utf-8')

            # Get file name from path
            file_name = os.path.basename(file_path)

            return {
                "saved": True,
                "file_path": file_path,
                "file": {
                    "content": content_base64,
                    "name": file_name,
                    "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
            }
        except Exception as e:
            return {
                "saved": False,
                "file_path": file_path,
                "file": {
                    "content": "",
                    "name": os.path.basename(file_path),
                    "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                },
                "error": f"Could not generate document for streaming: {str(e)}"
            }

@doc_maker.action("add_page_break")
class AddPageBreakAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        document_id = inputs["document_id"]
        files = inputs.get("files", [])

        load_document_from_files(document_id, files)

        if document_id not in documents:
            raise ValueError(f"Document {document_id} not found")

        doc = documents[document_id]
        paragraph = doc.add_paragraph()
        paragraph.add_run().add_break(WD_BREAK.PAGE)

        original_result = {"page_break_added": True}
        return await save_and_return_document(original_result, document_id, context)

