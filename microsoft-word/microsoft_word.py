from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler
from typing import Dict, Any, List, Optional
import io
import base64
import re

microsoft_word = Integration.load()

GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"


def handle_api_error(error: Exception, message: str = "Microsoft Graph API error") -> Dict[str, Any]:
    """Handle API error responses."""
    return {'result': False, 'error': f'{message}: {str(error)}'}


def ensure_docx_extension(name: str) -> str:
    """Ensure filename has .docx extension."""
    if not name.lower().endswith('.docx'):
        return f"{name}.docx"
    return name


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0


def count_characters(text: str) -> int:
    """Count characters in text."""
    return len(text) if text else 0


# ---- Document Parsing Utilities ----

def parse_docx_content(docx_bytes: bytes) -> Dict[str, Any]:
    """
    Parse a .docx file and extract text content, paragraphs, and tables.
    
    Uses the python-docx library pattern via zipfile and XML parsing.
    """
    import zipfile
    from xml.etree import ElementTree as ET
    
    WORD_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as docx_zip:
            document_xml = docx_zip.read('word/document.xml')
        
        tree = ET.fromstring(document_xml)
        body = tree.find(f'{WORD_NS}body')
        
        if body is None:
            return {
                'paragraphs': [],
                'tables': [],
                'full_text': '',
                'word_count': 0,
                'character_count': 0,
                'paragraph_count': 0
            }
        
        paragraphs = []
        tables = []
        full_text_parts = []
        
        for element in body:
            if element.tag == f'{WORD_NS}p':
                para_info = _parse_paragraph(element, WORD_NS, len(paragraphs))
                paragraphs.append(para_info)
                if para_info['text']:
                    full_text_parts.append(para_info['text'])
            
            elif element.tag == f'{WORD_NS}tbl':
                table_info = _parse_table(element, WORD_NS, len(tables))
                tables.append(table_info)
        
        full_text = '\n'.join(full_text_parts)
        
        return {
            'paragraphs': paragraphs,
            'tables': tables,
            'full_text': full_text,
            'word_count': count_words(full_text),
            'character_count': count_characters(full_text),
            'paragraph_count': len(paragraphs)
        }
        
    except Exception as e:
        raise ValueError(f"Failed to parse document: {str(e)}")


def _parse_paragraph(para_element, ns: str, index: int) -> Dict[str, Any]:
    """Parse a paragraph element."""
    text_parts = []
    style = 'Normal'
    formatting = {
        'alignment': 'left',
        'bold': False,
        'italic': False
    }
    
    pPr = para_element.find(f'{ns}pPr')
    if pPr is not None:
        pStyle = pPr.find(f'{ns}pStyle')
        if pStyle is not None:
            style = pStyle.get(f'{ns}val', 'Normal')
        
        jc = pPr.find(f'{ns}jc')
        if jc is not None:
            alignment = jc.get(f'{ns}val', 'left')
            formatting['alignment'] = alignment
    
    for run in para_element.findall(f'{ns}r'):
        rPr = run.find(f'{ns}rPr')
        if rPr is not None:
            if rPr.find(f'{ns}b') is not None:
                formatting['bold'] = True
            if rPr.find(f'{ns}i') is not None:
                formatting['italic'] = True
        
        for text_elem in run.findall(f'{ns}t'):
            if text_elem.text:
                text_parts.append(text_elem.text)
    
    return {
        'index': index,
        'text': ''.join(text_parts),
        'style': style,
        'formatting': formatting
    }


def _parse_table(table_element, ns: str, index: int) -> Dict[str, Any]:
    """Parse a table element."""
    rows_data = []
    
    for tr in table_element.findall(f'{ns}tr'):
        row = []
        for tc in tr.findall(f'{ns}tc'):
            cell_text_parts = []
            for p in tc.findall(f'{ns}p'):
                for r in p.findall(f'{ns}r'):
                    for t in r.findall(f'{ns}t'):
                        if t.text:
                            cell_text_parts.append(t.text)
            row.append(''.join(cell_text_parts))
        rows_data.append(row)
    
    num_rows = len(rows_data)
    num_cols = max(len(row) for row in rows_data) if rows_data else 0
    
    return {
        'index': index,
        'rows': num_rows,
        'columns': num_cols,
        'data': rows_data,
        'hasHeaderRow': num_rows > 0
    }


def create_docx_from_text(text: str) -> bytes:
    """
    Create a minimal .docx file from plain text.
    """
    import zipfile
    from xml.etree import ElementTree as ET
    
    WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
    CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
    
    paragraphs = text.split('\n') if text else ['']
    
    body_content = ''
    for para in paragraphs:
        escaped_text = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body_content += f'''
        <w:p xmlns:w="{WORD_NS}">
            <w:r>
                <w:t>{escaped_text}</w:t>
            </w:r>
        </w:p>'''
    
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{WORD_NS}">
    <w:body>
        {body_content}
        <w:sectPr/>
    </w:body>
</w:document>'''
    
    content_types_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT_NS}">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
    
    rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL_NS}">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        docx_zip.writestr('[Content_Types].xml', content_types_xml)
        docx_zip.writestr('_rels/.rels', rels_xml)
        docx_zip.writestr('word/document.xml', document_xml)
    
    return output.getvalue()


def modify_docx_content(docx_bytes: bytes, modifications: Dict[str, Any]) -> bytes:
    """
    Modify a .docx file with the given modifications.
    
    Supports:
    - replace_all: Replace entire content with new text
    - search_replace: Find and replace text
    - insert_text: Insert text at location
    """
    import zipfile
    from xml.etree import ElementTree as ET
    
    WORD_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    
    with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as docx_zip:
        file_list = docx_zip.namelist()
        files = {name: docx_zip.read(name) for name in file_list}
    
    document_xml = files['word/document.xml'].decode('utf-8')
    
    if 'replace_all' in modifications:
        new_text = modifications['replace_all']
        new_docx = create_docx_from_text(new_text)
        return new_docx
    
    if 'search_replace' in modifications:
        sr = modifications['search_replace']
        search_text = sr['search_text']
        replace_text = sr['replace_text']
        match_case = sr.get('match_case', False)
        replace_all = sr.get('replace_all', True)
        
        if match_case:
            if replace_all:
                document_xml = document_xml.replace(search_text, replace_text)
            else:
                document_xml = document_xml.replace(search_text, replace_text, 1)
        else:
            pattern = re.escape(search_text)
            flags = re.IGNORECASE if not match_case else 0
            if replace_all:
                document_xml = re.sub(pattern, replace_text, document_xml, flags=flags)
            else:
                document_xml = re.sub(pattern, replace_text, document_xml, count=1, flags=flags)
    
    files['word/document.xml'] = document_xml.encode('utf-8')
    
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        for name, content in files.items():
            docx_zip.writestr(name, content)
    
    return output.getvalue()


def text_to_html(text: str) -> str:
    """Convert plain text to HTML."""
    paragraphs = text.split('\n')
    html_parts = ['<html><body>']
    for para in paragraphs:
        if para.strip():
            escaped = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_parts.append(f'<p>{escaped}</p>')
    html_parts.append('</body></html>')
    return '\n'.join(html_parts)


def text_to_markdown(text: str) -> str:
    """Convert plain text to markdown (minimal formatting)."""
    return text


# ---- Action Handlers ----

@microsoft_word.action("word_list_documents")
class ListDocuments(ActionHandler):
    """Find accessible Word documents (.docx) in OneDrive/SharePoint."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            name_contains = inputs.get('name_contains', '')
            folder_path = inputs.get('folder_path', '')
            page_size = min(inputs.get('page_size', 25), 100)
            page_token = inputs.get('page_token', '')
            
            if page_token:
                url = page_token
                params = {}
            else:
                if folder_path:
                    folder_path = folder_path.strip('/')
                    url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}:/children"
                else:
                    url = f"{GRAPH_API_BASE}/me/drive/root/children"
                
                filter_parts = ["file/mimeType eq 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'"]
                
                if name_contains:
                    filter_parts.append(f"contains(name, '{name_contains}')")
                
                params = {
                    '$filter': ' and '.join(filter_parts),
                    '$top': str(page_size),
                    '$select': 'id,name,webUrl,lastModifiedDateTime,size,createdBy,lastModifiedBy'
                }
            
            response = await context.fetch(url, method="GET", params=params)
            
            documents = []
            for item in response.get('value', []):
                if item.get('name', '').lower().endswith('.docx'):
                    documents.append({
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'webUrl': item.get('webUrl'),
                        'lastModifiedDateTime': item.get('lastModifiedDateTime'),
                        'size': item.get('size'),
                        'createdBy': item.get('createdBy', {})
                    })
            
            next_link = response.get('@odata.nextLink')
            
            return {
                'documents': documents,
                'next_page_token': next_link if next_link else None,
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to list documents")


@microsoft_word.action("word_get_document")
class GetDocument(ActionHandler):
    """Retrieve document properties including metadata."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            
            url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}"
            params = {
                '$select': 'id,name,size,webUrl,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,parentReference,file'
            }
            
            document = await context.fetch(url, method="GET", params=params)
            
            return {
                'document': document,
                'result': True
            }
            
        except Exception as e:
            error_result = handle_api_error(e, "Failed to get document")
            error_result['document'] = {}
            return error_result


@microsoft_word.action("word_get_content")
class GetContent(ActionHandler):
    """Read the text content from a Word document."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            output_format = inputs.get('format', 'text')
            include_metadata = inputs.get('include_metadata', False)
            
            content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            
            response = await context.fetch(content_url, method="GET")
            
            if isinstance(response, bytes):
                docx_bytes = response
            elif isinstance(response, str):
                docx_bytes = response.encode('latin-1')
            else:
                return {'result': False, 'error': 'Unexpected response format from API'}
            
            parsed = parse_docx_content(docx_bytes)
            
            if output_format == 'html':
                content = text_to_html(parsed['full_text'])
            elif output_format == 'markdown':
                content = text_to_markdown(parsed['full_text'])
            else:
                content = parsed['full_text']
            
            result = {
                'content': content,
                'word_count': parsed['word_count'],
                'character_count': parsed['character_count'],
                'paragraph_count': parsed['paragraph_count'],
                'result': True
            }
            
            if include_metadata:
                meta_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}"
                metadata = await context.fetch(meta_url, method="GET")
                result['metadata'] = metadata
            
            return result
            
        except Exception as e:
            return handle_api_error(e, "Failed to get document content")


@microsoft_word.action("word_create_document")
class CreateDocument(ActionHandler):
    """Create a new Word document with optional initial content."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            name = ensure_docx_extension(inputs['name'])
            folder_path = inputs.get('folder_path', '')
            content = inputs.get('content', '')
            template_id = inputs.get('template_id')
            
            if template_id:
                copy_url = f"{GRAPH_API_BASE}/me/drive/items/{template_id}/copy"
                
                copy_body = {'name': name}
                if folder_path:
                    folder_path = folder_path.strip('/')
                    folder_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}"
                    folder_info = await context.fetch(folder_url, method="GET")
                    copy_body['parentReference'] = {
                        'driveId': folder_info.get('parentReference', {}).get('driveId'),
                        'id': folder_info.get('id')
                    }
                
                await context.fetch(copy_url, method="POST", json=copy_body)
                
                await _wait_for_copy(context, name, folder_path)
            
            else:
                docx_bytes = create_docx_from_text(content)
                
                if folder_path:
                    folder_path = folder_path.strip('/')
                    upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{name}:/content"
                else:
                    upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{name}:/content"
                
                headers = {
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                
                response = await context.fetch(
                    upload_url,
                    method="PUT",
                    headers=headers,
                    data=docx_bytes
                )
                
                return {
                    'document_id': response.get('id'),
                    'name': response.get('name'),
                    'webUrl': response.get('webUrl'),
                    'result': True
                }
            
            if folder_path:
                search_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{name}"
            else:
                search_url = f"{GRAPH_API_BASE}/me/drive/root:/{name}"
            
            new_doc = await context.fetch(search_url, method="GET")
            
            return {
                'document_id': new_doc.get('id'),
                'name': new_doc.get('name'),
                'webUrl': new_doc.get('webUrl'),
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to create document")


async def _wait_for_copy(context: ExecutionContext, name: str, folder_path: str, max_attempts: int = 10):
    """Wait for copy operation to complete (poll for file existence)."""
    import asyncio
    
    for _ in range(max_attempts):
        try:
            if folder_path:
                check_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{name}"
            else:
                check_url = f"{GRAPH_API_BASE}/me/drive/root:/{name}"
            
            await context.fetch(check_url, method="GET")
            return
        except Exception:
            await asyncio.sleep(1)


@microsoft_word.action("word_update_content")
class UpdateContent(ActionHandler):
    """Replace the entire content of a Word document with new content."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            content = inputs['content']
            preserve_formatting = inputs.get('preserve_formatting', False)
            
            if preserve_formatting:
                content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
                existing_bytes = await context.fetch(content_url, method="GET")
                
                if isinstance(existing_bytes, str):
                    existing_bytes = existing_bytes.encode('latin-1')
                
                docx_bytes = modify_docx_content(existing_bytes, {'replace_all': content})
            else:
                docx_bytes = create_docx_from_text(content)
            
            upload_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            headers = {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            
            await context.fetch(upload_url, method="PUT", headers=headers, data=docx_bytes)
            
            return {
                'updated': True,
                'document_id': document_id,
                'word_count': count_words(content),
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to update document content")


@microsoft_word.action("word_insert_text")
class InsertText(ActionHandler):
    """Insert text at a specific location in the document."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            text = inputs['text']
            location = inputs['location']
            paragraph_index = inputs.get('paragraph_index', 0)
            
            content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            existing_bytes = await context.fetch(content_url, method="GET")
            
            if isinstance(existing_bytes, str):
                existing_bytes = existing_bytes.encode('latin-1')
            
            parsed = parse_docx_content(existing_bytes)
            paragraphs = parsed['paragraphs']
            
            texts = [p['text'] for p in paragraphs]
            
            if location == 'start':
                texts.insert(0, text)
            elif location == 'end':
                texts.append(text)
            elif location == 'after_paragraph':
                if paragraph_index >= len(texts):
                    texts.append(text)
                else:
                    texts.insert(paragraph_index + 1, text)
            elif location == 'before_paragraph':
                if paragraph_index >= len(texts):
                    texts.insert(len(texts), text)
                else:
                    texts.insert(paragraph_index, text)
            else:
                return {'result': False, 'error': f"Invalid location: {location}"}
            
            new_content = '\n'.join(texts)
            docx_bytes = create_docx_from_text(new_content)
            
            upload_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            headers = {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            
            await context.fetch(upload_url, method="PUT", headers=headers, data=docx_bytes)
            
            return {
                'inserted': True,
                'document_id': document_id,
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to insert text")


@microsoft_word.action("word_get_paragraphs")
class GetParagraphs(ActionHandler):
    """Get all paragraphs from a document with their content and formatting."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            start_index = inputs.get('start_index', 0)
            count = inputs.get('count')
            include_formatting = inputs.get('include_formatting', False)
            
            content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            docx_bytes = await context.fetch(content_url, method="GET")
            
            if isinstance(docx_bytes, str):
                docx_bytes = docx_bytes.encode('latin-1')
            
            parsed = parse_docx_content(docx_bytes)
            paragraphs = parsed['paragraphs']
            
            if start_index > 0:
                paragraphs = paragraphs[start_index:]
            
            if count is not None:
                paragraphs = paragraphs[:count]
            
            if not include_formatting:
                paragraphs = [
                    {'index': p['index'], 'text': p['text'], 'style': p['style']}
                    for p in paragraphs
                ]
            
            return {
                'paragraphs': paragraphs,
                'total_count': parsed['paragraph_count'],
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to get paragraphs")


@microsoft_word.action("word_search_replace")
class SearchReplace(ActionHandler):
    """Find and replace text throughout the document."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            search_text = inputs['search_text']
            replace_text = inputs['replace_text']
            match_case = inputs.get('match_case', False)
            match_whole_word = inputs.get('match_whole_word', False)
            replace_all = inputs.get('replace_all', True)
            
            content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            docx_bytes = await context.fetch(content_url, method="GET")
            
            if isinstance(docx_bytes, str):
                docx_bytes = docx_bytes.encode('latin-1')
            
            parsed_before = parse_docx_content(docx_bytes)
            text_before = parsed_before['full_text']
            
            if match_case:
                count_before = text_before.count(search_text)
            else:
                count_before = text_before.lower().count(search_text.lower())
            
            if count_before == 0:
                return {
                    'replaced': False,
                    'replacement_count': 0,
                    'document_id': document_id,
                    'result': True
                }
            
            modifications = {
                'search_replace': {
                    'search_text': search_text,
                    'replace_text': replace_text,
                    'match_case': match_case,
                    'replace_all': replace_all
                }
            }
            
            if match_whole_word:
                modifications['search_replace']['search_text'] = f'\\b{re.escape(search_text)}\\b'
            
            modified_bytes = modify_docx_content(docx_bytes, modifications)
            
            upload_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            headers = {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            
            await context.fetch(upload_url, method="PUT", headers=headers, data=modified_bytes)
            
            replacement_count = 1 if not replace_all else count_before
            
            return {
                'replaced': True,
                'replacement_count': replacement_count,
                'document_id': document_id,
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to search and replace")


@microsoft_word.action("word_export_pdf")
class ExportPdf(ActionHandler):
    """Export the Word document to PDF format."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            output_name = inputs.get('output_name')
            save_to_drive = inputs.get('save_to_drive', False)
            folder_path = inputs.get('folder_path', '')
            
            pdf_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content?format=pdf"
            
            pdf_response = await context.fetch(pdf_url, method="GET")
            
            if isinstance(pdf_response, dict) and '@microsoft.graph.downloadUrl' in pdf_response:
                download_url = pdf_response['@microsoft.graph.downloadUrl']
                
                if not save_to_drive:
                    return {
                        'pdf_url': download_url,
                        'result': True
                    }
            
            if save_to_drive:
                if isinstance(pdf_response, str):
                    pdf_bytes = pdf_response.encode('latin-1')
                elif isinstance(pdf_response, bytes):
                    pdf_bytes = pdf_response
                else:
                    return {'result': False, 'error': 'Could not retrieve PDF content'}
                
                if not output_name:
                    doc_info = await context.fetch(
                        f"{GRAPH_API_BASE}/me/drive/items/{document_id}",
                        method="GET"
                    )
                    original_name = doc_info.get('name', 'document.docx')
                    output_name = original_name.rsplit('.', 1)[0] + '.pdf'
                
                if not output_name.lower().endswith('.pdf'):
                    output_name += '.pdf'
                
                if folder_path:
                    folder_path = folder_path.strip('/')
                    upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{output_name}:/content"
                else:
                    upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{output_name}:/content"
                
                headers = {'Content-Type': 'application/pdf'}
                
                uploaded = await context.fetch(
                    upload_url,
                    method="PUT",
                    headers=headers,
                    data=pdf_bytes
                )
                
                return {
                    'pdf_url': uploaded.get('webUrl'),
                    'pdf_id': uploaded.get('id'),
                    'size': uploaded.get('size'),
                    'result': True
                }
            
            return {
                'pdf_url': pdf_url,
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to export to PDF")


@microsoft_word.action("word_get_tables")
class GetTables(ActionHandler):
    """Extract tables from a Word document."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            document_id = inputs['document_id']
            table_index = inputs.get('table_index')
            include_formatting = inputs.get('include_formatting', False)
            
            content_url = f"{GRAPH_API_BASE}/me/drive/items/{document_id}/content"
            docx_bytes = await context.fetch(content_url, method="GET")
            
            if isinstance(docx_bytes, str):
                docx_bytes = docx_bytes.encode('latin-1')
            
            parsed = parse_docx_content(docx_bytes)
            tables = parsed['tables']
            
            if table_index is not None:
                if table_index < 0 or table_index >= len(tables):
                    return {
                        'tables': [],
                        'table_count': len(tables),
                        'result': True,
                        'error': f'Table index {table_index} out of range'
                    }
                tables = [tables[table_index]]
            
            return {
                'tables': tables,
                'table_count': len(parsed['tables']),
                'result': True
            }
            
        except Exception as e:
            return handle_api_error(e, "Failed to get tables")
