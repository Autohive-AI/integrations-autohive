from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler
from typing import Dict, Any, List, Optional

google_docs = Integration.load()

# Google Docs API base URL
DOCS_API_BASE = "https://docs.googleapis.com/v1"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"


def handle_api_error(error: Exception, message: str = "Google API error") -> Dict[str, Any]:
    """Handle API error responses."""
    return {'result': False, 'error': f'{message}: {str(error)}'}


# ---- Action Handlers ----

@google_docs.action("docs_create")
class CreateDocument(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Create a new Google Doc."""
        try:
            title = inputs.get('title', 'Untitled Document')
            url = f"{DOCS_API_BASE}/documents"
            payload = {'title': title}

            document = await context.fetch(url, method="POST", json=payload)

            return {
                'documentId': document.get('documentId'),
                'title': document.get('title'),
                'result': True
            }
        except Exception as e:
            return handle_api_error(e, "Failed to create document")


@google_docs.action("docs_get")
class GetDocument(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve full document content."""
        try:
            document_id = inputs['document_id']
            include_tabs = inputs.get('include_tabs_content', True)

            # Build the URL with query parameters
            url = f"{DOCS_API_BASE}/documents/{document_id}"
            params = {}

            if include_tabs:
                params['includeTabsContent'] = 'true'

            document = await context.fetch(url, method="GET", params=params)

            return {
                'document': document,
                'result': True
            }
        except Exception as e:
            error_result = handle_api_error(e, "Failed to get document")
            error_result['document'] = {}
            return error_result


@google_docs.action("docs_insert_paragraphs")
class InsertParagraphs(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Insert multiple plain text paragraphs into the document.

        This action is for inserting bulk plain paragraphs without markdown formatting.
        Each paragraph will be separated by double newlines.

        For structured content with headings, use docs_smart_insert_with_tabs instead.

        Inputs:
        - document_id: The document ID
        - paragraphs: Array of paragraph text strings
        - append: If true, append to end; if false, insert at beginning (default: true)
        - tab_id: Optional tab ID if working with a specific tab
        """
        try:
            document_id = inputs['document_id']
            paragraphs = inputs['paragraphs']
            tab_id = inputs.get('tab_id')
            append = inputs.get('append', True)

            # Validate paragraphs is an array
            if not isinstance(paragraphs, list):
                return {'result': False, 'error': 'paragraphs must be an array of strings'}

            if not paragraphs:
                return {'result': False, 'error': 'paragraphs array is empty'}

            # Get insertion index
            if append:
                # Get the end index for appending
                url = f"{DOCS_API_BASE}/documents/{document_id}"
                params = {}

                if tab_id:
                    params['includeTabsContent'] = 'true'
                    params['fields'] = 'tabs(tabId,documentTab/body/content(endIndex))'
                else:
                    params['fields'] = 'body/content(endIndex)'

                document = await context.fetch(url, method="GET", params=params)

                if tab_id:
                    index = None
                    for tab in document.get('tabs', []):
                        if tab.get('tabId') == tab_id:
                            doc_tab = tab.get('documentTab', {})
                            body = doc_tab.get('body', {})
                            content = body.get('content', [])
                            index = content[-1].get('endIndex', 1) - 1 if content else 1
                            break
                    if index is None:
                        return {'result': False, 'error': f'Tab with ID {tab_id} not found'}
                else:
                    body = document.get('body', {})
                    content = body.get('content', [])
                    index = content[-1].get('endIndex', 1) - 1 if content else 1
            else:
                # Insert at beginning
                index = 1

            # Build batch requests for all paragraphs
            batch_requests = []
            current_index = index

            for paragraph in paragraphs:
                para_text = str(paragraph) + '\n\n'
                insert_request = {
                    'insertText': {
                        'text': para_text,
                        'location': {'index': current_index}
                    }
                }

                if tab_id:
                    insert_request['insertText']['location']['tabId'] = tab_id

                batch_requests.append(insert_request)
                current_index += len(para_text)

            # Execute batch insert
            url = f"{DOCS_API_BASE}/documents/{document_id}:batchUpdate"
            payload = {'requests': batch_requests}

            await context.fetch(url, method="POST", json=payload)

            return {
                'result': True,
                'paragraphs_inserted': len(paragraphs),
                'inserted_at_index': index
            }
        except Exception as e:
            return handle_api_error(e, "Failed to insert paragraphs")


@google_docs.action("docs_batch_update")
class BatchUpdate(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Execute multiple document updates in a single batch request.

        This is a flexible action that can handle any Google Docs API request type.

        Common use cases:

        1. Insert text:
           {"insertText": {"text": "Hello", "location": {"index": 1}}}

        2. Apply bold formatting:
           {"updateTextStyle": {
               "range": {"startIndex": 1, "endIndex": 10},
               "textStyle": {"bold": true},
               "fields": "bold"
           }}

        3. Apply italic formatting:
           {"updateTextStyle": {
               "range": {"startIndex": 1, "endIndex": 10},
               "textStyle": {"italic": true},
               "fields": "italic"
           }}

        4. Apply multiple text styles (bold + italic + font size):
           {"updateTextStyle": {
               "range": {"startIndex": 1, "endIndex": 10},
               "textStyle": {
                   "bold": true,
                   "italic": true,
                   "fontSize": {"magnitude": 14, "unit": "PT"}
               },
               "fields": "bold,italic,fontSize"
           }}

        5. Apply paragraph style (heading):
           {"updateParagraphStyle": {
               "range": {"startIndex": 1, "endIndex": 20},
               "paragraphStyle": {"namedStyleType": "HEADING_1"},
               "fields": "namedStyleType"
           }}

        6. Change text color:
           {"updateTextStyle": {
               "range": {"startIndex": 1, "endIndex": 10},
               "textStyle": {
                   "foregroundColor": {
                       "color": {"rgbColor": {"red": 1.0, "green": 0.0, "blue": 0.0}}
                   }
               },
               "fields": "foregroundColor"
           }}

        Inputs:
        - document_id: The document ID
        - requests: Array of Google Docs API request objects
        """
        try:
            document_id = inputs['document_id']
            batch_requests = inputs['requests']

            # Validate requests is a list of dicts
            if not isinstance(batch_requests, list) or not all(isinstance(r, dict) for r in batch_requests):
                return {'result': False, 'error': 'requests must be an array of objects'}

            url = f"{DOCS_API_BASE}/documents/{document_id}:batchUpdate"
            payload = {'requests': batch_requests}

            result = await context.fetch(url, method="POST", json=payload)

            return {
                'replies': result.get('replies', []),
                'result': True
            }
        except Exception as e:
            error_result = handle_api_error(e, "Failed to execute batch update")
            error_result['replies'] = []
            return error_result


@google_docs.action("docs_parse_structure")
class ParseStructure(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Parse document structure to identify headings, paragraphs, and their positions."""
        try:
            document_id = inputs['document_id']
            tab_id = inputs.get('tab_id')

            # Fetch document with full content
            url = f"{DOCS_API_BASE}/documents/{document_id}"
            params = {}

            if tab_id:
                params['includeTabsContent'] = 'true'

            document = await context.fetch(url, method="GET", params=params)

            # Get the body content
            if tab_id:
                # Find the specific tab
                body = None
                for tab in document.get('tabs', []):
                    if tab.get('tabId') == tab_id:
                        doc_tab = tab.get('documentTab', {})
                        body = doc_tab.get('body', {})
                        break
                if body is None:
                    return {'result': False, 'error': f'Tab with ID {tab_id} not found'}
            else:
                body = document.get('body', {})

            content = body.get('content', [])

            # Parse the structure
            structure = []
            for element in content:
                # Skip elements without proper indices
                start_index = element.get('startIndex')
                end_index = element.get('endIndex')

                if start_index is None or end_index is None:
                    continue

                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    para_style = paragraph.get('paragraphStyle', {})
                    named_style = para_style.get('namedStyleType', 'NORMAL_TEXT')

                    # Extract text content
                    text_content = ''
                    for text_element in paragraph.get('elements', []):
                        if 'textRun' in text_element:
                            text_content += text_element['textRun'].get('content', '')

                    # Determine if it's a heading or body paragraph
                    element_type = 'heading' if named_style.startswith('HEADING') or named_style in ['TITLE', 'SUBTITLE'] else 'paragraph'

                    structure_element = {
                        'type': element_type,
                        'style': named_style,
                        'text': text_content.strip(),
                        'startIndex': start_index,
                        'endIndex': end_index
                    }

                    # Add alignment if present
                    if 'alignment' in para_style:
                        structure_element['alignment'] = para_style['alignment']

                    structure.append(structure_element)
                elif 'table' in element:
                    structure.append({
                        'type': 'table',
                        'startIndex': start_index,
                        'endIndex': end_index
                    })
                elif 'sectionBreak' in element:
                    structure.append({
                        'type': 'section_break',
                        'startIndex': start_index,
                        'endIndex': end_index
                    })

            return {
                'structure': structure,
                'result': True
            }
        except Exception as e:
            error_result = handle_api_error(e, "Failed to parse document structure")
            error_result['structure'] = []
            return error_result


@google_docs.action("docs_insert_markdown_content")
class InsertMarkdownContent(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Insert markdown-formatted content with automatic heading detection and styling.

        IMPORTANT: This action requires markdown format with headings (# for H1, ## for H2).
        For plain paragraphs without headings, use docs_insert_paragraphs instead.

        Features:
        - Parses markdown headings (# H1, ## H2, ### H3, etc.)
        - Automatically applies Google Docs heading styles (HEADING_1, HEADING_2, etc.)
        - Inserts and styles in a single batch operation
        - No duplicate content

        Inputs:
        - document_id: The document ID
        - content: Markdown text with headings (# Heading, ## Subheading, etc.)
        - heading_level: Which heading level to parse (default: 1 for #)
        - tab_id: Optional tab ID if working with a specific tab
        - append: If true, append to end of document (default: True)
        """
        try:
            document_id = inputs['document_id']
            content = inputs['content']
            heading_level = inputs.get('heading_level', 1)
            tab_id = inputs.get('tab_id')
            append = inputs.get('append', True)

            # Step 1: Parse content into sections
            sections = self._parse_sections(content, heading_level)

            if not sections:
                return {'result': False, 'error': 'No sections found in content'}

            # Step 2: Get the insertion index
            insertion_index = await self._get_insertion_index(
                context, document_id, tab_id, append
            )

            # Step 3: Insert all content with styles in a single batch operation
            result = await self._insert_and_style_sections(
                context, document_id, tab_id, sections, insertion_index, heading_level
            )

            return result

        except Exception as e:
            return handle_api_error(e, "Failed to insert markdown content")

    def _parse_sections(self, content: str, heading_level: int) -> List[Dict[str, Any]]:
        """Parse content into sections based on heading level."""
        sections = []
        heading_marker = '#' * heading_level + ' '

        lines = content.split('\n')
        current_heading = None
        current_paragraphs = []
        current_buffer = []

        for line in lines:
            stripped = line.strip()

            # Check if it's a heading at the target level
            if stripped.startswith(heading_marker):
                # Save previous section
                if current_heading is not None:
                    if current_buffer:
                        # Join lines with space to preserve word boundaries
                        current_paragraphs.append(' '.join(current_buffer).strip())
                    sections.append({
                        'heading': current_heading,
                        'paragraphs': [p for p in current_paragraphs if p]
                    })

                # Start new section
                current_heading = stripped[len(heading_marker):].strip()
                current_paragraphs = []
                current_buffer = []

            # Check for paragraph breaks (empty lines separate paragraphs)
            elif not stripped:
                if current_buffer:
                    # Join lines with space to preserve word boundaries
                    current_paragraphs.append(' '.join(current_buffer).strip())
                    current_buffer = []
            else:
                current_buffer.append(line)

        # Save last section
        if current_heading is not None:
            if current_buffer:
                # Join lines with space to preserve word boundaries
                current_paragraphs.append(' '.join(current_buffer).strip())
            sections.append({
                'heading': current_heading,
                'paragraphs': [p for p in current_paragraphs if p]
            })

        return sections

    async def _get_insertion_index(self, context: ExecutionContext,
                                   document_id: str, tab_id: Optional[str],
                                   append: bool) -> int:
        """Get the index where content should be inserted."""
        if not append:
            return 1  # Insert at beginning

        # Get end index for appending
        url = f"{DOCS_API_BASE}/documents/{document_id}"
        params = {}

        if tab_id:
            params['includeTabsContent'] = 'true'
            params['fields'] = 'tabs(tabId,documentTab/body/content(endIndex))'
        else:
            params['fields'] = 'body/content(endIndex)'

        try:
            document = await context.fetch(url, method="GET", params=params)
        except Exception:
            return 1  # Default to beginning on error

        if tab_id:
            for tab in document.get('tabs', []):
                if tab.get('tabId') == tab_id:
                    doc_tab = tab.get('documentTab', {})
                    body = doc_tab.get('body', {})
                    content = body.get('content', [])
                    return content[-1].get('endIndex', 1) - 1 if content else 1
            return 1
        else:
            body = document.get('body', {})
            content = body.get('content', [])
            return content[-1].get('endIndex', 1) - 1 if content else 1

    async def _insert_and_style_sections(self, context: ExecutionContext,
                                         document_id: str, tab_id: Optional[str],
                                         sections: List[Dict[str, Any]],
                                         start_index: int,
                                         heading_level: int) -> Dict[str, Any]:
        """
        Insert all sections with content and apply styles in a single batch operation.
        This prevents duplicate content by doing everything in one go.
        """
        try:
            batch_requests = []
            current_index = start_index

            # Map heading level to Google Docs heading style
            heading_style_map = {
                1: 'HEADING_1',
                2: 'HEADING_2',
                3: 'HEADING_3',
                4: 'HEADING_4',
                5: 'HEADING_5',
                6: 'HEADING_6'
            }
            heading_style = heading_style_map.get(heading_level, 'HEADING_1')

            # Build all insertion and styling requests
            for section in sections:
                heading = section['heading']
                paragraphs = section['paragraphs']

                # Insert heading text
                heading_text = heading + '\n'
                heading_insert = {
                    'insertText': {
                        'text': heading_text,
                        'location': {'index': current_index}
                    }
                }
                if tab_id:
                    heading_insert['insertText']['location']['tabId'] = tab_id
                batch_requests.append(heading_insert)

                # Apply heading style
                heading_style_request = {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(heading_text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': heading_style
                        },
                        'fields': 'namedStyleType'
                    }
                }
                if tab_id:
                    heading_style_request['updateParagraphStyle']['range']['tabId'] = tab_id
                batch_requests.append(heading_style_request)

                current_index += len(heading_text)

                # Insert paragraphs
                for paragraph in paragraphs:
                    para_text = paragraph + '\n\n'
                    para_insert = {
                        'insertText': {
                            'text': para_text,
                            'location': {'index': current_index}
                        }
                    }
                    if tab_id:
                        para_insert['insertText']['location']['tabId'] = tab_id
                    batch_requests.append(para_insert)

                    current_index += len(para_text)

            # Execute all insertions and styling in a single batch
            url = f"{DOCS_API_BASE}/documents/{document_id}:batchUpdate"
            payload = {'requests': batch_requests}

            await context.fetch(url, method="POST", json=payload)

            return {
                'result': True,
                'sections_inserted': len(sections),
                'total_paragraphs': sum(len(s['paragraphs']) for s in sections)
            }

        except Exception as e:
            return handle_api_error(e, "Failed to insert and style sections")

