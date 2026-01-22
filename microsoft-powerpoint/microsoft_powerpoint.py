from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, Optional
import io
import tempfile
import os

microsoft_powerpoint = Integration.load()

GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"

THUMBNAIL_SIZES = {
    "small": {"width": 176, "height": 144},
    "medium": {"width": 800, "height": 600},
    "large": {"width": 1600, "height": 1200}
}


async def download_file_content(context: ExecutionContext, item_id: str) -> bytes:
    response = await context.fetch(
        f"{GRAPH_API_BASE_URL}/me/drive/items/{item_id}/content",
        method="GET",
        raw_response=True
    )
    return response


async def upload_file_content(context: ExecutionContext, folder_path: str, file_name: str, content: bytes) -> Dict[str, Any]:
    if folder_path and folder_path != "/":
        upload_url = f"{GRAPH_API_BASE_URL}/me/drive/root:/{folder_path.strip('/')}/{file_name}:/content"
    else:
        upload_url = f"{GRAPH_API_BASE_URL}/me/drive/root:/{file_name}:/content"
    
    response = await context.fetch(
        upload_url,
        method="PUT",
        headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        },
        data=content
    )
    return response


def create_blank_pptx() -> bytes:
    try:
        from pptx import Presentation
        prs = Presentation()
        buffer = io.BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        return buffer.read()
    except ImportError:
        raise ImportError("python-pptx library is required for creating presentations. Install with: pip install python-pptx")


@microsoft_powerpoint.action("powerpoint_list_presentations")
class ListPresentationsAction(ActionHandler):
    """Find accessible PowerPoint presentations (.pptx) in OneDrive/SharePoint."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            folder_path = inputs.get('folder_path', '')
            name_contains = inputs.get('name_contains', '')
            page_size = min(inputs.get('page_size', 25), 100)
            page_token = inputs.get('page_token')

            if folder_path and folder_path != "/":
                base_url = f"{GRAPH_API_BASE_URL}/me/drive/root:/{folder_path.strip('/')}:/children"
            else:
                base_url = f"{GRAPH_API_BASE_URL}/me/drive/root/children"

            filter_parts = ["endswith(name, '.pptx')"]
            if name_contains:
                filter_parts.append(f"contains(name, '{name_contains}')")

            params = {
                "$filter": " and ".join(filter_parts),
                "$top": page_size,
                "$select": "id,name,webUrl,lastModifiedDateTime,size,createdDateTime"
            }

            if page_token:
                response = await context.fetch(page_token, method="GET")
            else:
                response = await context.fetch(base_url, method="GET", params=params)

            items = response.get('value', [])
            presentations = [
                {
                    "id": item.get('id'),
                    "name": item.get('name'),
                    "webUrl": item.get('webUrl'),
                    "lastModifiedDateTime": item.get('lastModifiedDateTime'),
                    "size": item.get('size')
                }
                for item in items
            ]

            next_page_token = response.get('@odata.nextLink')

            return {
                "presentations": presentations,
                "next_page_token": next_page_token,
                "result": True
            }

        except Exception as e:
            return {"presentations": [], "result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_get_presentation")
class GetPresentationAction(ActionHandler):
    """Retrieve presentation properties including file info, author, and last modified details."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            presentation_id = inputs['presentation_id']

            response = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}",
                method="GET",
                params={
                    "$select": "id,name,size,webUrl,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,parentReference"
                }
            )

            return {
                "id": response.get('id'),
                "name": response.get('name'),
                "size": response.get('size'),
                "webUrl": response.get('webUrl'),
                "createdDateTime": response.get('createdDateTime'),
                "lastModifiedDateTime": response.get('lastModifiedDateTime'),
                "createdBy": response.get('createdBy'),
                "lastModifiedBy": response.get('lastModifiedBy'),
                "parentReference": response.get('parentReference'),
                "result": True
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_get_slides")
class GetSlidesAction(ActionHandler):
    """List all slides in a presentation with their thumbnails and basic metadata."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            presentation_id = inputs['presentation_id']
            include_thumbnails = inputs.get('include_thumbnails', True)
            thumbnail_size = inputs.get('thumbnail_size', 'medium')

            thumbnails_response = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}/thumbnails",
                method="GET"
            )

            thumbnail_sets = thumbnails_response.get('value', [])
            slides = []

            for i, thumb_set in enumerate(thumbnail_sets):
                slide = {
                    "index": i + 1,
                    "id": thumb_set.get('id', str(i))
                }

                if include_thumbnails:
                    size_data = thumb_set.get(thumbnail_size, thumb_set.get('medium', {}))
                    slide["thumbnailUrl"] = size_data.get('url')
                    slide["thumbnailWidth"] = size_data.get('width')
                    slide["thumbnailHeight"] = size_data.get('height')

                slides.append(slide)

            return {
                "slides": slides,
                "slide_count": len(slides),
                "result": True
            }

        except Exception as e:
            return {"slides": [], "slide_count": 0, "result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_get_slide")
class GetSlideAction(ActionHandler):
    """Get details for a specific slide by its index (1-based)."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            presentation_id = inputs['presentation_id']
            slide_index = inputs['slide_index']
            include_thumbnail = inputs.get('include_thumbnail', True)
            thumbnail_size = inputs.get('thumbnail_size', 'large')

            if slide_index < 1:
                return {"result": False, "error": "Slide index must be 1 or greater"}

            thumbnails_response = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}/thumbnails",
                method="GET"
            )

            thumbnail_sets = thumbnails_response.get('value', [])
            
            if slide_index > len(thumbnail_sets):
                return {"result": False, "error": f"Slide index {slide_index} is out of range. Presentation has {len(thumbnail_sets)} slides."}

            thumb_set = thumbnail_sets[slide_index - 1]
            
            result = {
                "index": slide_index,
                "id": thumb_set.get('id', str(slide_index - 1)),
                "result": True
            }

            if include_thumbnail:
                size_data = thumb_set.get(thumbnail_size, thumb_set.get('large', {}))
                result["thumbnailUrl"] = size_data.get('url')
                result["thumbnailWidth"] = size_data.get('width')
                result["thumbnailHeight"] = size_data.get('height')

            return result

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_create_presentation")
class CreatePresentationAction(ActionHandler):
    """Create a new PowerPoint presentation in the specified folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            name = inputs['name']
            folder_path = inputs.get('folder_path', '')
            template_id = inputs.get('template_id')

            if not name.endswith('.pptx'):
                file_name = f"{name}.pptx"
            else:
                file_name = name

            if template_id:
                if folder_path and folder_path != "/":
                    dest_path = f"/{folder_path.strip('/')}"
                else:
                    dest_path = "/"

                copy_body = {
                    "name": file_name,
                    "parentReference": {
                        "path": f"/drive/root:{dest_path}" if dest_path != "/" else "/drive/root:"
                    }
                }

                response = await context.fetch(
                    f"{GRAPH_API_BASE_URL}/me/drive/items/{template_id}/copy",
                    method="POST",
                    json=copy_body
                )

                if response.get('id'):
                    return {
                        "id": response.get('id'),
                        "name": response.get('name'),
                        "webUrl": response.get('webUrl'),
                        "createdDateTime": response.get('createdDateTime'),
                        "result": True
                    }
                else:
                    return {
                        "result": True,
                        "message": "Copy operation initiated. The file will be available shortly.",
                        "name": file_name
                    }
            else:
                pptx_content = create_blank_pptx()
                response = await upload_file_content(context, folder_path, file_name, pptx_content)

                return {
                    "id": response.get('id'),
                    "name": response.get('name'),
                    "webUrl": response.get('webUrl'),
                    "createdDateTime": response.get('createdDateTime'),
                    "result": True
                }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_add_slide")
class AddSlideAction(ActionHandler):
    """Add a new slide to an existing presentation."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt

            presentation_id = inputs['presentation_id']
            position = inputs.get('position')
            layout = inputs.get('layout', 'blank')
            title = inputs.get('title')
            content = inputs.get('content')

            content_bytes = await download_file_content(context, presentation_id)
            
            prs = Presentation(io.BytesIO(content_bytes))

            layout_mapping = {
                'blank': 6,
                'title': 0,
                'titleContent': 1,
                'twoContent': 3,
                'comparison': 4,
                'titleOnly': 5,
                'contentCaption': 7,
                'pictureCaption': 8
            }
            
            layout_index = layout_mapping.get(layout, 6)
            if layout_index >= len(prs.slide_layouts):
                layout_index = 6 if 6 < len(prs.slide_layouts) else 0

            slide_layout = prs.slide_layouts[layout_index]
            
            if position and position <= len(prs.slides):
                new_slide = prs.slides.add_slide(slide_layout)
                slide_id = new_slide.slide_id
                
                xml_slides = prs.slides._sldIdLst
                slides_list = list(xml_slides)
                last_slide = slides_list[-1]
                xml_slides.remove(last_slide)
                xml_slides.insert(position - 1, last_slide)
                slide_index = position
            else:
                new_slide = prs.slides.add_slide(slide_layout)
                slide_index = len(prs.slides)

            if title:
                for shape in new_slide.shapes:
                    if shape.has_text_frame and shape.is_placeholder:
                        if shape.placeholder_format.type == 1:
                            shape.text = title
                            break

            if content:
                for shape in new_slide.shapes:
                    if shape.has_text_frame and shape.is_placeholder:
                        if shape.placeholder_format.type == 2:
                            shape.text = content
                            break

            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)

            file_info = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}",
                method="GET",
                params={"$select": "name,parentReference"}
            )

            file_name = file_info.get('name')
            parent_path = file_info.get('parentReference', {}).get('path', '/drive/root:').replace('/drive/root:', '')

            await upload_file_content(context, parent_path, file_name, buffer.read())

            return {
                "slide_index": slide_index,
                "slide_count": len(prs.slides),
                "result": True
            }

        except ImportError:
            return {"result": False, "error": "python-pptx library is required. Install with: pip install python-pptx"}
        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_update_slide")
class UpdateSlideAction(ActionHandler):
    """Update the content of an existing slide."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            from pptx import Presentation

            presentation_id = inputs['presentation_id']
            slide_index = inputs['slide_index']
            title = inputs.get('title')
            content = inputs.get('content')
            notes = inputs.get('notes')

            if slide_index < 1:
                return {"result": False, "error": "Slide index must be 1 or greater"}

            content_bytes = await download_file_content(context, presentation_id)
            prs = Presentation(io.BytesIO(content_bytes))

            if slide_index > len(prs.slides):
                return {"result": False, "error": f"Slide index {slide_index} is out of range. Presentation has {len(prs.slides)} slides."}

            slide = prs.slides[slide_index - 1]
            updated = False

            if title is not None:
                for shape in slide.shapes:
                    if shape.has_text_frame and shape.is_placeholder:
                        if hasattr(shape, 'placeholder_format') and shape.placeholder_format.type == 1:
                            shape.text = title
                            updated = True
                            break

            if content is not None:
                for shape in slide.shapes:
                    if shape.has_text_frame and shape.is_placeholder:
                        if hasattr(shape, 'placeholder_format') and shape.placeholder_format.type == 2:
                            shape.text = content
                            updated = True
                            break

            if notes is not None:
                notes_slide = slide.notes_slide
                notes_slide.notes_text_frame.text = notes
                updated = True

            if updated:
                buffer = io.BytesIO()
                prs.save(buffer)
                buffer.seek(0)

                file_info = await context.fetch(
                    f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}",
                    method="GET",
                    params={"$select": "name,parentReference"}
                )

                file_name = file_info.get('name')
                parent_path = file_info.get('parentReference', {}).get('path', '/drive/root:').replace('/drive/root:', '')

                await upload_file_content(context, parent_path, file_name, buffer.read())

            return {
                "updated": updated,
                "slide_index": slide_index,
                "result": True
            }

        except ImportError:
            return {"result": False, "error": "python-pptx library is required. Install with: pip install python-pptx"}
        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_delete_slide")
class DeleteSlideAction(ActionHandler):
    """Delete a slide from the presentation."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            from pptx import Presentation

            presentation_id = inputs['presentation_id']
            slide_index = inputs['slide_index']

            if slide_index < 1:
                return {"result": False, "error": "Slide index must be 1 or greater"}

            content_bytes = await download_file_content(context, presentation_id)
            prs = Presentation(io.BytesIO(content_bytes))

            if slide_index > len(prs.slides):
                return {"result": False, "error": f"Slide index {slide_index} is out of range. Presentation has {len(prs.slides)} slides."}

            slide_id = prs.slides._sldIdLst[slide_index - 1].rId
            prs.part.drop_rel(slide_id)
            del prs.slides._sldIdLst[slide_index - 1]

            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)

            file_info = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}",
                method="GET",
                params={"$select": "name,parentReference"}
            )

            file_name = file_info.get('name')
            parent_path = file_info.get('parentReference', {}).get('path', '/drive/root:').replace('/drive/root:', '')

            await upload_file_content(context, parent_path, file_name, buffer.read())

            return {
                "deleted": True,
                "slide_count": len(prs.slides),
                "result": True
            }

        except ImportError:
            return {"result": False, "error": "python-pptx library is required. Install with: pip install python-pptx"}
        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_export_pdf")
class ExportPdfAction(ActionHandler):
    """Export the presentation to PDF format."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            presentation_id = inputs['presentation_id']
            output_folder = inputs.get('output_folder')
            output_name = inputs.get('output_name')

            file_info = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}",
                method="GET",
                params={"$select": "name,parentReference"}
            )

            original_name = file_info.get('name', 'presentation.pptx')
            parent_path = file_info.get('parentReference', {}).get('path', '/drive/root:').replace('/drive/root:', '')

            if output_name:
                pdf_name = output_name if output_name.endswith('.pdf') else f"{output_name}.pdf"
            else:
                pdf_name = original_name.replace('.pptx', '.pdf')

            dest_folder = output_folder if output_folder else parent_path

            pdf_content = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}/content?format=pdf",
                method="GET",
                raw_response=True
            )

            if dest_folder and dest_folder != "/":
                upload_url = f"{GRAPH_API_BASE_URL}/me/drive/root:/{dest_folder.strip('/')}/{pdf_name}:/content"
            else:
                upload_url = f"{GRAPH_API_BASE_URL}/me/drive/root:/{pdf_name}:/content"

            response = await context.fetch(
                upload_url,
                method="PUT",
                headers={"Content-Type": "application/pdf"},
                data=pdf_content
            )

            download_response = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{response.get('id')}",
                method="GET",
                params={"$select": "@microsoft.graph.downloadUrl"}
            )

            return {
                "pdf_id": response.get('id'),
                "pdf_name": response.get('name'),
                "pdf_webUrl": response.get('webUrl'),
                "pdf_size": response.get('size'),
                "download_url": download_response.get('@microsoft.graph.downloadUrl'),
                "result": True
            }

        except Exception as e:
            return {"result": False, "error": str(e)}


@microsoft_powerpoint.action("powerpoint_get_slide_image")
class GetSlideImageAction(ActionHandler):
    """Get a slide as an image (PNG/JPEG thumbnail)."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            presentation_id = inputs['presentation_id']
            slide_index = inputs['slide_index']
            size = inputs.get('size', 'large')
            image_format = inputs.get('format', 'png')

            if slide_index < 1:
                return {"result": False, "error": "Slide index must be 1 or greater"}

            size_info = THUMBNAIL_SIZES.get(size, THUMBNAIL_SIZES['large'])
            custom_size = f"c{size_info['width']}x{size_info['height']}"

            thumbnails_response = await context.fetch(
                f"{GRAPH_API_BASE_URL}/me/drive/items/{presentation_id}/thumbnails",
                method="GET"
            )

            thumbnail_sets = thumbnails_response.get('value', [])
            
            if slide_index > len(thumbnail_sets):
                return {"result": False, "error": f"Slide index {slide_index} is out of range. Presentation has {len(thumbnail_sets)} slides."}

            thumb_set = thumbnail_sets[slide_index - 1]
            
            size_data = thumb_set.get(size, thumb_set.get('large', {}))

            return {
                "image_url": size_data.get('url'),
                "width": size_data.get('width', size_info['width']),
                "height": size_data.get('height', size_info['height']),
                "format": image_format,
                "result": True
            }

        except Exception as e:
            return {"result": False, "error": str(e)}
