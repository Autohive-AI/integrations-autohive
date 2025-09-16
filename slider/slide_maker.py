from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR, MSO_FILL_TYPE
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
import uuid
import os
import base64
from io import BytesIO
from PIL import Image

slide_maker = Integration.load()

presentations = {}
uploaded_images = {}

# Only blank slides are supported (layout index 6)
BLANK_LAYOUT_INDEX = 6

CHART_TYPE_MAP = {
    "column_clustered": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": XL_CHART_TYPE.LINE,
    "pie": XL_CHART_TYPE.PIE,
    "bar_clustered": XL_CHART_TYPE.BAR_CLUSTERED,
    "area": XL_CHART_TYPE.AREA,
    "xy_scatter": XL_CHART_TYPE.XY_SCATTER
}

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

def load_presentation_from_files(presentation_id: str, files: List[Dict[str, Any]]) -> None:
    """Load presentation from files parameter if not in memory"""
    if presentation_id not in presentations and files:
        processed_files = process_files(files)
        
        for filename, file_stream in processed_files.items():
            if filename.lower().endswith('.pptx') or filename.lower().endswith('.bin'):
                try:
                    prs = Presentation(file_stream)
                    presentations[presentation_id] = prs
                    return
                except Exception as e:
                    continue
        
        # If no valid PowerPoint file found, provide better error message
        available_files = list(processed_files.keys())
        raise ValueError(f"No valid PowerPoint file found in files. Tried to load: {available_files}. Files may be corrupted or not PowerPoint format.")
    elif presentation_id not in presentations:
        raise ValueError(f"Presentation {presentation_id} not found and no files provided for loading")

async def save_and_return_presentation(original_result: Dict[str, Any], presentation_id: str, context: ExecutionContext, custom_filename: str = None) -> Dict[str, Any]:
    """Helper to save presentation and return combined result"""
    save_action = SavePresentationAction()
    
    if custom_filename:
        if not custom_filename.lower().endswith('.pptx'):
            custom_filename += '.pptx'
        file_path = custom_filename
    else:
        file_path = f"{presentation_id}.pptx"
    
    save_inputs = {
        "presentation_id": presentation_id,
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

def calculate_overlap(element1_pos, element2_pos):
    """Calculate overlap between two rectangular elements"""
    left1, top1, right1, bottom1 = element1_pos["left"], element1_pos["top"], element1_pos["right"], element1_pos["bottom"]
    left2, top2, right2, bottom2 = element2_pos["left"], element2_pos["top"], element2_pos["right"], element2_pos["bottom"]
    
    overlap_left = max(left1, left2)
    overlap_top = max(top1, top2)
    overlap_right = min(right1, right2)
    overlap_bottom = min(bottom1, bottom2)
    
    # Check if there's an overlap
    if overlap_left < overlap_right and overlap_top < overlap_bottom:
        overlap_width = overlap_right - overlap_left
        overlap_height = overlap_bottom - overlap_top
        overlap_area = overlap_width * overlap_height
        
        # Calculate percentages of overlap relative to each element
        area1 = element1_pos["width"] * element1_pos["height"]
        area2 = element2_pos["width"] * element2_pos["height"]
        
        overlap_percent1 = (overlap_area / area1 * 100) if area1 > 0 else 0
        overlap_percent2 = (overlap_area / area2 * 100) if area2 > 0 else 0
        
        return {
            "overlaps": True,
            "overlap_area": round(overlap_area, 3),
            "overlap_width": round(overlap_width, 3),
            "overlap_height": round(overlap_height, 3),
            "overlap_position": {
                "left": round(overlap_left, 3),
                "top": round(overlap_top, 3),
                "right": round(overlap_right, 3),
                "bottom": round(overlap_bottom, 3)
            },
            "overlap_percent_element1": round(overlap_percent1, 1),
            "overlap_percent_element2": round(overlap_percent2, 1)
        }
    else:
        return {"overlaps": False}

def analyze_all_element_overlaps(elements):
    """Analyze overlaps between ALL elements on the slide"""
    overlaps = []
    total_overlaps = 0
    
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            element1 = elements[i]
            element2 = elements[j]
            
            overlap_info = calculate_overlap(element1["position"], element2["position"])
            
            if overlap_info["overlaps"]:
                total_overlaps += 1
                overlap_details = {
                    "element1_index": element1["index"],
                    "element1_type": element1["type"],
                    "element1_name": element1.get("name", ""),
                    "element2_index": element2["index"],
                    "element2_type": element2["type"], 
                    "element2_name": element2.get("name", ""),
                    "overlap_area": overlap_info["overlap_area"],
                    "overlap_dimensions": {
                        "width": overlap_info["overlap_width"],
                        "height": overlap_info["overlap_height"]
                    },
                    "overlap_position": overlap_info["overlap_position"],
                    "overlap_percentages": {
                        "element1_coverage": overlap_info["overlap_percent_element1"],
                        "element2_coverage": overlap_info["overlap_percent_element2"]
                    },
                    "severity": "high" if max(overlap_info["overlap_percent_element1"], overlap_info["overlap_percent_element2"]) > 50 else 
                              "medium" if max(overlap_info["overlap_percent_element1"], overlap_info["overlap_percent_element2"]) > 20 else "low",
                    "description": f"{element1['type']} (#{element1['index']}) overlaps {element2['type']} (#{element2['index']}) by {overlap_info['overlap_area']:.2f} sq inches ({max(overlap_info['overlap_percent_element1'], overlap_info['overlap_percent_element2']):.1f}% coverage)"
                }
                overlaps.append(overlap_details)
    
    return overlaps, total_overlaps

def get_element_info(shape, index: int, slide_width_inches: float, slide_height_inches: float) -> dict:
    """Extract detailed information about a shape/element including boundary checking"""
    from pptx.util import Inches
    
    # Convert EMU to inches for positions and sizes
    left_inches = shape.left / 914400 if shape.left is not None else 0
    top_inches = shape.top / 914400 if shape.top is not None else 0
    width_inches = shape.width / 914400 if shape.width is not None else 0
    height_inches = shape.height / 914400 if shape.height is not None else 0
    
    right_inches = left_inches + width_inches
    bottom_inches = top_inches + height_inches
    
    warnings = []
    boundary_status = "inside"
    
    if left_inches < 0:
        warnings.append(f"Element extends {abs(left_inches):.3f} inches to the left of slide")
        boundary_status = "outside"
    
    if top_inches < 0:
        warnings.append(f"Element extends {abs(top_inches):.3f} inches above slide")
        boundary_status = "outside"
    
    if right_inches > slide_width_inches:
        overhang = right_inches - slide_width_inches
        warnings.append(f"Element extends {overhang:.3f} inches to the right of slide")
        boundary_status = "outside"
    
    if bottom_inches > slide_height_inches:
        overhang = bottom_inches - slide_height_inches
        warnings.append(f"Element extends {overhang:.3f} inches below slide")
        boundary_status = "outside"
    
    # Determine element type
    element_type = "unknown"
    if hasattr(shape, 'shape_type'):
        shape_type = shape.shape_type
        if shape_type == 1:  # MSO_SHAPE_TYPE.AUTO_SHAPE
            element_type = "shape"
        elif shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
            element_type = "image"
        elif shape_type == 19:  # MSO_SHAPE_TYPE.TABLE
            element_type = "table"
        elif shape_type == 3:  # MSO_SHAPE_TYPE.CHART
            element_type = "chart"
        elif shape_type == 17:  # MSO_SHAPE_TYPE.TEXT_BOX
            element_type = "text_box"
        elif hasattr(shape, 'has_text_frame') and shape.has_text_frame:
            element_type = "text_element"
    
    # Extract text content
    content = ""
    has_text = False
    text_overflow_detected = False
    
    if hasattr(shape, 'has_text_frame') and shape.has_text_frame:
        has_text = True
        try:
            text_frame = shape.text_frame
            
            text_parts = []
            for paragraph in text_frame.paragraphs:
                paragraph_text = ''.join(run.text for run in paragraph.runs)
                if paragraph_text.strip():
                    text_parts.append(paragraph_text.strip())
                    
            content = '\n'.join(text_parts)
                        
        except:
            content = ""
    
    # Get shape name if available
    name = ""
    if hasattr(shape, 'name'):
        name = shape.name or ""


    result = {
        "index": index,
        "type": element_type,
        "shape_id": str(shape.shape_id) if hasattr(shape, 'shape_id') else str(index),
        "position": {
            "left": round(left_inches, 3),
            "top": round(top_inches, 3),
            "width": round(width_inches, 3),
            "height": round(height_inches, 3),
            "right": round(right_inches, 3),
            "bottom": round(bottom_inches, 3)
        },
        "content": content,
        "has_text": has_text,
        "name": name,
        "boundary_status": boundary_status,
        "boundary_warnings": warnings
    }
    
    return result


# ---- Action Handlers ----

@slide_maker.action("create_presentation")
class CreatePresentationAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        title = inputs.get("title")
        subtitle = inputs.get("subtitle")
        files = inputs.get("files", [])
        custom_filename = inputs.get("custom_filename")
        
        processed_files = process_files(files)
        
        template_file = None
        for filename, file_stream in processed_files.items():
            if filename.lower().endswith('.pptx'):
                template_file = file_stream
                break
        
        if template_file:
            prs = Presentation(template_file)
        else:
            prs = Presentation()
        
        # Always ensure at least one slide exists
        if len(prs.slides) == 0:
            blank_slide_layout = prs.slide_layouts[BLANK_LAYOUT_INDEX]
            slide = prs.slides.add_slide(blank_slide_layout)
        else:
            slide = prs.slides[0]
        
        # Add title and subtitle as text boxes if provided
        if title:
            
            # Add title as a text box on the blank slide
            title_left = 0.5 
            title_top = 0.5   
            title_width = prs.slide_width / 914400 - 1.0 
            title_height = 1.0 
            
            title_box = slide.shapes.add_textbox(
                Inches(title_left), Inches(title_top), 
                Inches(title_width), Inches(title_height)
            )
            title_frame = title_box.text_frame
            title_frame.text = title
            title_frame.paragraphs[0].font.size = Pt(32)
            title_frame.paragraphs[0].font.bold = True
            
            # Add subtitle if provided
            if subtitle:
                subtitle_top = title_top + title_height + 0.2  
                subtitle_height = 0.8
                
                subtitle_box = slide.shapes.add_textbox(
                    Inches(title_left), Inches(subtitle_top),
                    Inches(title_width), Inches(subtitle_height)
                )
                subtitle_frame = subtitle_box.text_frame
                subtitle_frame.text = subtitle
                subtitle_frame.paragraphs[0].font.size = Pt(18)
        
        # Generate unique ID and store presentation
        presentation_id = str(uuid.uuid4())
        presentations[presentation_id] = prs
        
        result = {
            "presentation_id": presentation_id,
            "slide_count": len(prs.slides)
        }
        
        return await save_and_return_presentation(result, presentation_id, context, custom_filename)

@slide_maker.action("add_slide")
class AddSlideAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        slide_layout = prs.slide_layouts[BLANK_LAYOUT_INDEX]
        slide = prs.slides.add_slide(slide_layout)
        
        original_result = {
            "slide_index": len(prs.slides) - 1,
            "slide_count": len(prs.slides)
        }
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("add_text")
class AddTextAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        text = inputs["text"]
        position = inputs["position"]
        formatting = inputs.get("formatting", {})
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        left = Inches(position["left"])
        top = Inches(position["top"])
        width = Inches(position["width"])
        height = Inches(position["height"])
        
        # Validate text box doesn't exceed slide boundaries
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        # Adjust if text box exceeds slide boundaries
        if left + width > slide_width:
            width = slide_width - left - Inches(0.1)  
        if top + height > slide_height:
            height = slide_height - top - Inches(0.1)
            
        # Ensure minimum text box size
        if width < Inches(0.5):
            width = Inches(0.5)
        if height < Inches(0.3):
            height = Inches(0.3)
        
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.text = text
        
        # Apply text containment features to prevent overflow
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        tf.word_wrap = True
        
        tf.margin_left = Inches(0.1)
        tf.margin_right = Inches(0.1)
        tf.margin_top = Inches(0.05)
        tf.margin_bottom = Inches(0.05)
        
        # Apply formatting
        p = tf.paragraphs[0]
        if formatting.get("bold"):
            p.font.bold = True
        if formatting.get("italic"):
            p.font.italic = True
        if formatting.get("color"):
            rgb = hex_to_rgb(formatting["color"])
            p.font.color.rgb = RGBColor(*rgb)
        
        # Handle font size carefully with auto-sizing
        if formatting.get("font_size"):
            font_size = formatting["font_size"]
            # If a specific font size is requested, disable auto-sizing first
            tf.auto_size = MSO_AUTO_SIZE.NONE
            p.font.size = Pt(font_size)
        else:
            # Force recalculation by slightly adjusting text box size
            original_width = txBox.width
            original_height = txBox.height
            
            # Slightly adjust size (by 1 EMU - the smallest unit in PowerPoint)
            txBox.width = original_width + 1
            txBox.height = original_height + 1
            
            # Restore original dimensions
            txBox.width = original_width
            txBox.height = original_height
        
        original_result = {"shape_id": str(txBox.shape_id)}
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("add_image")
class AddImageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        position = inputs["position"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
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
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        left = Inches(position["left"])
        top = Inches(position["top"])
        
        # Get slide dimensions for boundary checking
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        if "width" in position and "height" in position:
            width = Inches(position["width"])
            height = Inches(position["height"])
            
            # Validate image doesn't exceed slide boundaries
            if left + width > slide_width:
                width = slide_width - left - Inches(0.1)
            if top + height > slide_height:
                height = slide_height - top - Inches(0.1)
                
            if width < Inches(0.5):
                width = Inches(0.5)
            if height < Inches(0.5):
                height = Inches(0.5)
                
            pic = slide.shapes.add_picture(image_file, left, top, width, height)
        else:
            # If no explicit size, add at original size but validate position
            if left > slide_width - Inches(1):
                left = slide_width - Inches(1)
            if top > slide_height - Inches(1):
                top = slide_height - Inches(1)
                
            pic = slide.shapes.add_picture(image_file, left, top)
        
        original_result = {"shape_id": str(pic.shape_id)}
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("add_table")
class AddTableAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        rows = inputs["rows"]
        cols = inputs["cols"]
        position = inputs["position"]
        data = inputs.get("data", [])
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        left = Inches(position["left"])
        top = Inches(position["top"])
        width = Inches(position["width"])
        height = Inches(position["height"])
        
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        # Adjust if table exceeds slide boundaries
        if left + width > slide_width:
            width = slide_width - left - Inches(0.1)  # Leave small margin
        if top + height > slide_height:
            height = slide_height - top - Inches(0.1)  # Leave small margin
            
        if width < Inches(1):
            width = Inches(1)
        if height < Inches(0.5):
            height = Inches(0.5)
        
        table = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        # Fill table with data if provided
        for row_idx, row_data in enumerate(data[:rows]):
            for col_idx, cell_value in enumerate(row_data[:cols]):
                table.cell(row_idx, col_idx).text = str(cell_value)
        
        original_result = {"table_id": f"table_{slide_index}_{len(slide.shapes)}"}
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("add_chart")
class AddChartAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        chart_type = inputs["chart_type"]
        position = inputs["position"]
        data = inputs["data"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        chart_data = CategoryChartData()
        chart_data.categories = data["categories"]
        
        for series in data["series"]:
            chart_data.add_series(series["name"], series["values"])
        
        left = Inches(position["left"])
        top = Inches(position["top"])
        width = Inches(position["width"])
        height = Inches(position["height"])
        
        # Validate chart doesn't exceed slide boundaries
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        # Adjust if chart exceeds slide boundaries
        if left + width > slide_width:
            width = slide_width - left - Inches(0.1)  
        if top + height > slide_height:
            height = slide_height - top - Inches(0.1)  
            
        if width < Inches(1):
            width = Inches(1)
        if height < Inches(1):
            height = Inches(1)
        
        chart_type_enum = CHART_TYPE_MAP.get(chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)
        chart_shape = slide.shapes.add_chart(chart_type_enum, left, top, width, height, chart_data)
        
        original_result = {"chart_id": str(chart_shape.shape_id)}
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("extract_text")
class ExtractTextAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        file_path = inputs["file_path"]
        
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} not found")
        
        prs = Presentation(file_path)
        slides_text = []
        all_text_parts = []
        
        for slide_idx, slide in enumerate(prs.slides):
            slide_text = []
            
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                    
                for paragraph in shape.text_frame.paragraphs:
                    text_run = ''.join(run.text for run in paragraph.runs)
                    if text_run.strip():
                        slide_text.append(text_run.strip())
                        all_text_parts.append(text_run.strip())
            
            slides_text.append({
                "slide_index": slide_idx,
                "text_content": slide_text
            })
        
        return {
            "slides": slides_text,
            "all_text": "\n".join(all_text_parts)
        }

@slide_maker.action("modify_slide")
class ModifySlideAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        updates = inputs["updates"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        modified = False
        
        # Update title if provided
        if "title" in updates and slide.shapes.title:
            slide.shapes.title.text = updates["title"]
            modified = True
        
        # Perform text replacements
        if "replace_text" in updates:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                    
                for paragraph in shape.text_frame.paragraphs:
                    for replacement in updates["replace_text"]:
                        old_text = replacement["old_text"]
                        new_text = replacement["new_text"]
                        
                        paragraph_text = ''.join(run.text for run in paragraph.runs)
                        if old_text in paragraph_text:
                            # Replace text in the paragraph
                            new_paragraph_text = paragraph_text.replace(old_text, new_text)
                            
                            # Clear existing runs and add new text
                            paragraph.clear()
                            paragraph.text = new_paragraph_text
                            modified = True
        
        original_result = {"modified": modified}
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("save_presentation")
class SavePresentationAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        file_path = inputs["file_path"]
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        
        # Save presentation to memory buffer instead of disk
        try:
            from io import BytesIO
            buffer = BytesIO()
            prs.save(buffer)
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
                    "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                }
            }
        except Exception as e:
            return {
                "saved": False,
                "file_path": file_path,
                "file": {
                    "content": "",
                    "name": os.path.basename(file_path),
                    "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                },
                "error": f"Could not generate presentation for streaming: {str(e)}"
            }

@slide_maker.action("set_text_autosize")
class SetTextAutosizeAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        shape_index = inputs["shape_index"]
        autosize_type = inputs["autosize_type"]
        word_wrap = inputs.get("word_wrap", None)
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if shape_index >= len(slide.shapes):
            raise ValueError(f"Shape index {shape_index} out of range")
        
        shape = slide.shapes[shape_index]
        if not shape.has_text_frame:
            raise ValueError("Shape does not have a text frame")
        
        text_frame = shape.text_frame
        
        # Map string values to MSO_AUTO_SIZE constants
        autosize_map = {
            "NONE": MSO_AUTO_SIZE.NONE,
            "SHAPE_TO_FIT_TEXT": MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT,
            "TEXT_TO_FIT_SHAPE": MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        }
        
        if autosize_type not in autosize_map:
            raise ValueError(f"Invalid autosize_type. Must be one of: {list(autosize_map.keys())}")
        
        text_frame.auto_size = autosize_map[autosize_type]
        
        if word_wrap is not None:
            text_frame.word_wrap = word_wrap
            
        # Force recalculation by slightly adjusting text box size
        if autosize_type != "NONE":
            original_width = shape.width
            original_height = shape.height
            
            shape.width = original_width + 1
            shape.height = original_height + 1
            
            shape.width = original_width
            shape.height = original_height
            
        original_result = {
            "success": True,
            "autosize_type": autosize_type,
            "word_wrap": text_frame.word_wrap
        }
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("fit_text_to_shape")
class FitTextToShapeAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        shape_index = inputs["shape_index"]
        max_size = inputs.get("max_size", 48)
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if shape_index >= len(slide.shapes):
            raise ValueError(f"Shape index {shape_index} out of range")
        
        shape = slide.shapes[shape_index]
        if not shape.has_text_frame:
            raise ValueError("Shape does not have a text frame")
        
        text_frame = shape.text_frame
        
        # Use the fit_text method to automatically size text to fit shape
        text_frame.fit_text(max_size=max_size)
        
        # Force recalculation by slightly adjusting text box size
        original_width = shape.width
        original_height = shape.height
        
        shape.width = original_width + 1
        shape.height = original_height + 1
        
        shape.width = original_width
        shape.height = original_height
        
        original_result = {
            "success": True,
            "max_size": max_size,
            "auto_size": "TEXT_TO_FIT_SHAPE"
        }
        return await save_and_return_presentation(original_result, presentation_id, context)

@slide_maker.action("set_text_margins")
class SetTextMarginsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        shape_index = inputs["shape_index"]
        margins = inputs["margins"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if shape_index >= len(slide.shapes):
            raise ValueError(f"Shape index {shape_index} out of range")
        
        shape = slide.shapes[shape_index]
        if not shape.has_text_frame:
            raise ValueError("Shape does not have a text frame")
        
        text_frame = shape.text_frame
        
        # Set margins (values in inches)
        if "left" in margins:
            text_frame.margin_left = Inches(margins["left"])
        if "right" in margins:
            text_frame.margin_right = Inches(margins["right"])
        if "top" in margins:
            text_frame.margin_top = Inches(margins["top"])
        if "bottom" in margins:
            text_frame.margin_bottom = Inches(margins["bottom"])
            
        result = {
            "success": True,
            "margins_set": margins
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("set_text_alignment")
class SetTextAlignmentAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        shape_index = inputs["shape_index"]
        vertical_anchor = inputs.get("vertical_anchor", None)
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if shape_index >= len(slide.shapes):
            raise ValueError(f"Shape index {shape_index} out of range")
        
        shape = slide.shapes[shape_index]
        if not shape.has_text_frame:
            raise ValueError("Shape does not have a text frame")
        
        text_frame = shape.text_frame
        
        # Map string values to MSO_ANCHOR constants
        anchor_map = {
            "TOP": MSO_ANCHOR.TOP,
            "MIDDLE": MSO_ANCHOR.MIDDLE,
            "BOTTOM": MSO_ANCHOR.BOTTOM
        }
        
        if vertical_anchor and vertical_anchor in anchor_map:
            text_frame.vertical_anchor = anchor_map[vertical_anchor]
            
        result = {
            "success": True,
            "vertical_anchor": vertical_anchor
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("set_slide_background_color")
class SetSlideBackgroundColorAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        color = inputs["color"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        background = slide.background
        
        # Set solid color background (this will automatically override master inheritance)
        fill = background.fill
        fill.solid()
        
        # Handle different color input formats
        if isinstance(color, dict):
            if "rgb" in color:
                # RGB format: {"rgb": [255, 0, 0]}
                r, g, b = color["rgb"]
                fill.fore_color.rgb = RGBColor(r, g, b)
            elif "theme_color" in color:
                # Theme color format: {"theme_color": "ACCENT_1"}
                theme_map = {
                    "ACCENT_1": MSO_THEME_COLOR.ACCENT_1,
                    "ACCENT_2": MSO_THEME_COLOR.ACCENT_2,
                    "ACCENT_3": MSO_THEME_COLOR.ACCENT_3,
                    "ACCENT_4": MSO_THEME_COLOR.ACCENT_4,
                    "ACCENT_5": MSO_THEME_COLOR.ACCENT_5,
                    "ACCENT_6": MSO_THEME_COLOR.ACCENT_6,
                    "BACKGROUND_1": MSO_THEME_COLOR.BACKGROUND_1,
                    "BACKGROUND_2": MSO_THEME_COLOR.BACKGROUND_2,
                    "DARK_1": MSO_THEME_COLOR.DARK_1,
                    "DARK_2": MSO_THEME_COLOR.DARK_2,
                    "LIGHT_1": MSO_THEME_COLOR.LIGHT_1,
                    "LIGHT_2": MSO_THEME_COLOR.LIGHT_2
                }
                theme_color = color["theme_color"]
                if theme_color in theme_map:
                    fill.fore_color.theme_color = theme_map[theme_color]
                else:
                    raise ValueError(f"Invalid theme color: {theme_color}")
        elif isinstance(color, str):
            # Hex format: "#FF0000"
            if color.startswith("#"):
                hex_color = color[1:]
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                fill.fore_color.rgb = RGBColor(r, g, b)
            else:
                raise ValueError("String color must be in hex format (e.g., '#FF0000')")
        else:
            raise ValueError("Color must be dict with 'rgb'/'theme_color' or hex string")
            
        result = {
            "success": True,
            "color_set": color
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("set_slide_background_gradient")
class SetSlideBackgroundGradientAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        angle = inputs.get("angle", 90)  # Default 90 degrees (bottom to top)
        gradient_stops = inputs.get("gradient_stops", [])
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        background = slide.background
        
        # Set gradient background (this will automatically override master inheritance)
        fill = background.fill
        fill.gradient()
        
        fill.gradient_angle = angle
        
        # Set gradient stops if provided
        if gradient_stops:
            stops = fill.gradient_stops
            # Clear existing stops except first two (minimum required)
            while len(stops) > 2:
                stops[-1].remove()
            
            for i, stop_info in enumerate(gradient_stops[:len(stops)]):
                stop = stops[i]
                if "position" in stop_info:
                    stop.position = stop_info["position"]
                if "color" in stop_info:
                    color_info = stop_info["color"]
                    if isinstance(color_info, dict) and "rgb" in color_info:
                        r, g, b = color_info["rgb"]
                        stop.color.rgb = RGBColor(r, g, b)
                    elif isinstance(color_info, dict) and "theme_color" in color_info:
                        theme_map = {
                            "ACCENT_1": MSO_THEME_COLOR.ACCENT_1,
                            "ACCENT_2": MSO_THEME_COLOR.ACCENT_2,
                            "ACCENT_3": MSO_THEME_COLOR.ACCENT_3,
                            "ACCENT_4": MSO_THEME_COLOR.ACCENT_4,
                            "ACCENT_5": MSO_THEME_COLOR.ACCENT_5,
                            "ACCENT_6": MSO_THEME_COLOR.ACCENT_6
                        }
                        theme_color = color_info["theme_color"]
                        if theme_color in theme_map:
                            stop.color.theme_color = theme_map[theme_color]
            
        result = {
            "success": True,
            "gradient_angle": angle,
            "gradient_stops_applied": len(gradient_stops) if gradient_stops else 2
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("add_background_image_workaround")
class AddBackgroundImageWorkaroundAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        processed_files = process_files(files)
        image_file = None
        
        # Check both filename extensions and content types
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
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        # Add picture that covers entire slide (position at 0,0)
        picture = slide.shapes.add_picture(image_file, 0, 0, slide_width, slide_height)
        
        # Send picture to back so other elements appear on top
        # Note: python-pptx doesn't have a direct "send to back" method
        # The picture will be behind elements added after it
        
        result = {
            "success": True,
            "method": "workaround_full_slide_picture",
            "picture_width": slide_width,
            "picture_height": slide_height,
            "note": "Image added as full-slide picture. Add other elements after this for proper layering."
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("reset_slide_background")
class ResetSlideBackgroundAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        # Reset background by removing custom background fill
        # This will cause the slide to inherit from master/layout
        background = slide.background
        fill = background.fill
        
        # Clear the background fill to revert to master
        try:
            # Remove any custom background by setting it to no fill
            if hasattr(fill, '_fill') and fill._fill is not None:
                fill._fill.clear()
        except:
            # Alternative approach: set background to inherit from master
            try:
                slide._element.cSld.attrib.pop('showMasterSp', None)
                if hasattr(slide._element.cSld, 'bg'):
                    bg_element = slide._element.cSld.bg
                    if bg_element is not None:
                        slide._element.cSld.remove(bg_element)
            except:
                pass  # If reset fails, continue
        
        result = {
            "success": True,
            "follow_master_background": True,
            "note": "Slide background reset to inherit from master/layout"
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("add_bullet_list")
class AddBulletListAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        bullet_items = inputs["bullet_items"]
        position = inputs["position"]
        formatting = inputs.get("formatting", {})
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        left = Inches(position["left"])
        top = Inches(position["top"])
        width = Inches(position["width"])
        height = Inches(position["height"])
        
        # Validate bullet list doesn't exceed slide boundaries
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        # Adjust if bullet list exceeds slide boundaries
        if left + width > slide_width:
            width = slide_width - left - Inches(0.1)
        if top + height > slide_height:
            height = slide_height - top - Inches(0.1)
            
        if width < Inches(1):
            width = Inches(1)
        if height < Inches(0.5):
            height = Inches(0.5)
        
        # Always create a text box for consistent behavior and avoid double bullets
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.clear()
        bullet_placeholder = False
        
        # Apply text containment features
        text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        text_frame.word_wrap = True
        text_frame.margin_left = Inches(0.1)
        text_frame.margin_right = Inches(0.1)
        text_frame.margin_top = Inches(0.05)
        text_frame.margin_bottom = Inches(0.05)
        
        # Add bullet items
        for i, item in enumerate(bullet_items):
            text = item.get("text", "")
            level = item.get("level", 0)
            
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            if bullet_placeholder:
                # Use built-in bullet formatting from placeholder
                p.text = text
                p.level = min(max(level, 0), 8)
            else:
                # Create manual bullets with Unicode symbols only when no placeholder
                bullet_symbols = ["•", "◦", "▪", "▫", "‣"]  # Different levels
                bullet_symbol = bullet_symbols[min(level, len(bullet_symbols)-1)]
                indent = "    " * level  # Manual indentation
                p.text = f"{indent}{bullet_symbol} {text}"
            
            p.alignment = PP_ALIGN.LEFT
        
        # Apply formatting to all paragraphs
        if formatting:
            for paragraph in text_frame.paragraphs:
                if formatting.get("font_size"):
                    paragraph.font.size = Pt(formatting["font_size"])
                if formatting.get("bold"):
                    paragraph.font.bold = formatting["bold"]
                if formatting.get("italic"):
                    paragraph.font.italic = formatting["italic"]
                if formatting.get("color"):
                    rgb = hex_to_rgb(formatting["color"])
                    paragraph.font.color.rgb = RGBColor(*rgb)
        
        shape_id = str(textbox.shape_id)
        
        result = {
            "shape_id": shape_id,
            "items_count": len(bullet_items)
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("delete_element")
class DeleteElementAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        shape_index = inputs["shape_index"]
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if shape_index >= len(slide.shapes):
            raise ValueError(f"Shape index {shape_index} out of range. Slide has {len(slide.shapes)} shapes.")
        
        # Get shape information before deletion for reporting
        shape = slide.shapes[shape_index]
        element_type = "unknown"
        
        # Try to identify the element type
        if hasattr(shape, 'shape_type'):
            shape_type = shape.shape_type
            if shape_type == 1:  # MSO_SHAPE_TYPE.AUTO_SHAPE
                element_type = "shape"
            elif shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                element_type = "image"
            elif shape_type == 19:  # MSO_SHAPE_TYPE.TABLE
                element_type = "table"
            elif shape_type == 3:  # MSO_SHAPE_TYPE.CHART
                element_type = "chart"
            elif shape_type == 17:  # MSO_SHAPE_TYPE.TEXT_BOX
                element_type = "text_box"
            elif hasattr(shape, 'has_text_frame') and shape.has_text_frame:
                element_type = "text_element"
        
        # Delete the shape
        # In python-pptx, we need to delete by getting the shape's element and removing it from its parent
        shape_element = shape.element
        shape_element.getparent().remove(shape_element)
        
        # Get remaining shape count after deletion
        remaining_shapes = len(slide.shapes)
        
        result = {
            "deleted": True,
            "element_type": element_type,
            "remaining_shapes": remaining_shapes
        }
        
        return await save_and_return_presentation(result, presentation_id, context)

@slide_maker.action("get_slide_elements")
class GetSlideElementsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        include_content = inputs.get("include_content", False)
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        
        # Get slide dimensions in inches
        slide_width_inches = prs.slide_width / 914400
        slide_height_inches = prs.slide_height / 914400
        
        # Get information about all elements on the slide
        elements = []
        elements_outside_boundary = 0
        all_warnings = []
        
        for i, shape in enumerate(slide.shapes):
            element_info = get_element_info(shape, i, slide_width_inches, slide_height_inches)
            elements.append(element_info)
            
            # Track boundary violations
            if element_info["boundary_status"] == "outside":
                elements_outside_boundary += 1
                for warning in element_info["boundary_warnings"]:
                    all_warnings.append(f"Element {i} ({element_info['type']}): {warning}")
        
        # Analyze element overlaps
        overlaps, total_overlaps = analyze_all_element_overlaps(elements)
        
        # Create summary warning messages
        boundary_warning = ""
        if elements_outside_boundary > 0:
            boundary_warning = f"{elements_outside_boundary} element(s) extend beyond slide boundaries (slide size: {slide_width_inches:.1f}\" x {slide_height_inches:.1f}\")"
        
        overlap_warning = ""
        if total_overlaps > 0:
            high_severity = len([o for o in overlaps if o["severity"] == "high"])
            if high_severity > 0:
                overlap_warning = f"{total_overlaps} element overlap(s) detected ({high_severity} high severity)"
            else:
                overlap_warning = f"{total_overlaps} element overlap(s) detected"
        
        combined_warnings = []
        if boundary_warning:
            combined_warnings.append(boundary_warning)
        if overlap_warning:
            combined_warnings.append(overlap_warning)
        
        overall_warning = "; ".join(combined_warnings) if combined_warnings else ""
        
        # Create optimized result with minimal tokens
        has_issues = elements_outside_boundary > 0 or total_overlaps > 0
        
        result = {
            "slide_index": slide_index,
            "total_elements": len(elements),
            "layout_status": "issues_detected" if has_issues else "no_issues",
            "slide_dimensions": {
                "width": round(slide_width_inches, 3),
                "height": round(slide_height_inches, 3)
            }
        }
        
        # Only include issue details if there are actual issues
        if has_issues:
            result["elements_outside_boundary"] = elements_outside_boundary
            result["total_overlapping_pairs"] = total_overlaps
            
            if overlaps:
                result["element_overlaps"] = overlaps
        
        # Optimize element data based on include_content parameter
        optimized_elements = []
        for element in elements:
            optimized_element = {
                "index": element["index"],
                "type": element["type"],
                "shape_id": element["shape_id"],
                "position": {
                    "left": element["position"]["left"],
                    "top": element["position"]["top"], 
                    "width": element["position"]["width"],
                    "height": element["position"]["height"]
                }
            }
            
            # Include content if requested OR if there are issues with this element
            has_element_issues = (element["boundary_status"] != "inside" or 
                                element["boundary_warnings"])
            
            if include_content or has_element_issues:
                if element["has_text"] and element["content"]:
                    optimized_element["content"] = element["content"]
            
            # Only include problem indicators if there are actual problems
            if element["boundary_status"] != "inside":
                optimized_element["boundary_status"] = element["boundary_status"]
            
            if element["boundary_warnings"]:
                optimized_element["boundary_warnings"] = element["boundary_warnings"]
            
            optimized_elements.append(optimized_element)
        
        result["elements"] = optimized_elements
        
        return result

@slide_maker.action("modify_element")
class ModifyElementAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        presentation_id = inputs["presentation_id"]
        slide_index = inputs["slide_index"]
        element_index = inputs["element_index"]
        new_position = inputs.get("position")
        new_text_content = inputs.get("text_content")
        formatting = inputs.get("formatting", {})
        files = inputs.get("files", [])
        
        load_presentation_from_files(presentation_id, files)
        
        if presentation_id not in presentations:
            raise ValueError(f"Presentation {presentation_id} not found")
        
        prs = presentations[presentation_id]
        if slide_index >= len(prs.slides):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = prs.slides[slide_index]
        if element_index >= len(slide.shapes):
            raise ValueError(f"Element index {element_index} out of range. Slide has {len(slide.shapes)} elements.")
        
        shape = slide.shapes[element_index]
        changes_made = []
        
        # Get element type for reporting
        element_type = "unknown"
        if hasattr(shape, 'shape_type'):
            shape_type = shape.shape_type
            if shape_type == 1:
                element_type = "shape"
            elif shape_type == 13:
                element_type = "image"
            elif shape_type == 19:
                element_type = "table"
            elif shape_type == 3:
                element_type = "chart"
            elif shape_type == 17:
                element_type = "text_box"
            elif hasattr(shape, 'has_text_frame') and shape.has_text_frame:
                element_type = "text_element"
        
        # Modify position and size if provided
        if new_position:
            if "left" in new_position:
                shape.left = Inches(new_position["left"])
                changes_made.append(f"Updated left position to {new_position['left']} inches")
            if "top" in new_position:
                shape.top = Inches(new_position["top"])
                changes_made.append(f"Updated top position to {new_position['top']} inches")
            if "width" in new_position:
                shape.width = Inches(new_position["width"])
                changes_made.append(f"Updated width to {new_position['width']} inches")
            if "height" in new_position:
                shape.height = Inches(new_position["height"])
                changes_made.append(f"Updated height to {new_position['height']} inches")
        
        # Modify text content if provided and element supports text
        if new_text_content is not None and hasattr(shape, 'has_text_frame') and shape.has_text_frame:
            shape.text_frame.clear()
            shape.text_frame.text = new_text_content
            changes_made.append(f"Updated text content")
        
        # Apply text formatting if provided and element supports text
        if formatting and hasattr(shape, 'has_text_frame') and shape.has_text_frame:
            text_frame = shape.text_frame
            
            # Apply formatting to ALL levels: paragraphs AND runs
            for paragraph in text_frame.paragraphs:
                # Apply to paragraph level first
                if formatting.get("font_size"):
                    paragraph.font.size = Pt(formatting["font_size"])
                if formatting.get("bold") is not None:
                    paragraph.font.bold = formatting["bold"]
                if formatting.get("italic") is not None:
                    paragraph.font.italic = formatting["italic"]
                if formatting.get("color"):
                    rgb = hex_to_rgb(formatting["color"])
                    paragraph.font.color.rgb = RGBColor(*rgb)
                
                # Apply to all runs to override any existing run-level formatting
                for run in paragraph.runs:
                    if formatting.get("font_size"):
                        run.font.size = Pt(formatting["font_size"])
                    if formatting.get("bold") is not None:
                        run.font.bold = formatting["bold"]
                    if formatting.get("italic") is not None:
                        run.font.italic = formatting["italic"]
                    if formatting.get("color"):
                        rgb = hex_to_rgb(formatting["color"])
                        run.font.color.rgb = RGBColor(*rgb)
            
            # Add change notifications
            if formatting.get("font_size"):
                changes_made.append(f"Updated font size to {formatting['font_size']}pt")
            if formatting.get("bold") is not None:
                changes_made.append(f"Set bold to {formatting['bold']}")
            if formatting.get("italic") is not None:
                changes_made.append(f"Set italic to {formatting['italic']}")
            if formatting.get("color"):
                changes_made.append(f"Updated text color to {formatting['color']}")
        
        # Get updated position information
        new_left = shape.left / 914400 if shape.left is not None else 0
        new_top = shape.top / 914400 if shape.top is not None else 0
        new_width = shape.width / 914400 if shape.width is not None else 0
        new_height = shape.height / 914400 if shape.height is not None else 0
        
        result = {
            "modified": len(changes_made) > 0,
            "element_index": element_index,
            "element_type": element_type,
            "changes_made": changes_made,
            "new_position": {
                "left": round(new_left, 3),
                "top": round(new_top, 3),
                "width": round(new_width, 3),
                "height": round(new_height, 3),
                "right": round(new_left + new_width, 3),
                "bottom": round(new_top + new_height, 3)
            }
        }
        
        return await save_and_return_presentation(result, presentation_id, context)



