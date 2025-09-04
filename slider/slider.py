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

# Create the integration using the config.json
slider = Integration.load()

# Global dictionary to store presentations in memory
presentations = {}

# Slide layout mapping
LAYOUT_MAP = {
    "title": 0,
    "title_content": 1,
    "section_header": 2,
    "two_content": 3,
    "comparison": 4,
    "title_only": 5,
    "blank": 6,
    "content_with_caption": 7,
    "picture_with_caption": 8
}

def get_rgb_from_hex(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# ---- Action Handlers ----

@slider.action("create_complete_presentation")
class CreatePresentationAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        import time
        start_time = time.time()
        
        # Extract main inputs
        presentation_metadata = inputs.get("presentation_metadata", {})
        slides_data = inputs.get("slides", [])
        global_settings = inputs.get("global_settings", {})
        processing_options = inputs.get("processing_options", {})
        
        # Create presentation
        template_path = presentation_metadata.get("template_path")
        if template_path and os.path.exists(template_path):
            prs = Presentation(template_path)
        else:
            prs = Presentation()
        
        # Generate unique presentation ID
        presentation_id = str(uuid.uuid4())
        presentations[presentation_id] = prs
        
        slides_created = 0
        elements_created = 0
        warnings = []
        
        # Create slides
        for slide_data in slides_data:
            try:
                # Always use blank layout (layout index 6)
                slide_layout = prs.slide_layouts[6]  # Force blank layout
                slide = prs.slides.add_slide(slide_layout)
                slides_created += 1
                
                # Apply background if specified
                background = slide_data.get("background")
                if background:
                    try:
                        self._apply_background(slide, background, prs)
                    except Exception as e:
                        warnings.append(f"Failed to apply background to slide {slides_created}: {str(e)}")
                
                # Add elements
                elements = slide_data.get("elements", [])
                for element in elements:
                    try:
                        element_type = element.get("element_type")
                        
                        if element_type == "text":
                            self._add_text_element(slide, element)
                        elif element_type == "chart":
                            self._add_chart_element(slide, element)
                        elif element_type == "table":
                            self._add_table_element(slide, element)
                        elif element_type == "image":
                            self._add_image_element(slide, element)
                        elif element_type == "bullet_list":
                            self._add_bullet_list_element(slide, element)
                        
                        elements_created += 1
                    except Exception as e:
                        warnings.append(f"Failed to add element {element_type} to slide {slides_created}: {str(e)}")
                        
            except Exception as e:
                warnings.append(f"Failed to create slide {len(slides_data)}: {str(e)}")
        
        # Save presentation to memory and encode as base64
        from io import BytesIO
        buffer = BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        file_content = buffer.getvalue()
        content_base64 = base64.b64encode(file_content).decode('utf-8')
        
        processing_time = time.time() - start_time
        
        # Determine filename
        title = presentation_metadata.get("title", "presentation")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}.pptx" if safe_title else "presentation.pptx"
        
        return {
            "success": True,
            "presentation_id": presentation_id,
            "file": {
                "content": content_base64,
                "name": filename,
                "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            },
            "slides_created": slides_created,
            "elements_created": elements_created,
            "processing_time": processing_time,
            "warnings": warnings
        }
    
    def _apply_background(self, slide, background, prs):
        """Apply background to slide"""
        bg_type = background.get("type")
        slide_bg = slide.background
        
        if bg_type == "solid":
            fill = slide_bg.fill
            fill.solid()
            color = background.get("color")
            
            if isinstance(color, str) and color.startswith("#"):
                # Hex color
                r, g, b = hex_to_rgb(color[1:])
                fill.fore_color.rgb = RGBColor(r, g, b)
            elif isinstance(color, dict):
                if "rgb" in color:
                    r, g, b = color["rgb"]
                    fill.fore_color.rgb = RGBColor(r, g, b)
                elif "theme_color" in color:
                    theme_map = {
                        "ACCENT_1": MSO_THEME_COLOR.ACCENT_1,
                        "ACCENT_2": MSO_THEME_COLOR.ACCENT_2,
                        "ACCENT_3": MSO_THEME_COLOR.ACCENT_3,
                        "ACCENT_4": MSO_THEME_COLOR.ACCENT_4,
                        "ACCENT_5": MSO_THEME_COLOR.ACCENT_5,
                        "ACCENT_6": MSO_THEME_COLOR.ACCENT_6,
                    }
                    theme_color = color.get("theme_color")
                    if theme_color in theme_map:
                        fill.fore_color.theme_color = theme_map[theme_color]
                        
        elif bg_type == "gradient":
            fill = slide_bg.fill
            fill.gradient()
            
            angle = background.get("angle", 90)
            fill.gradient_angle = angle
            
        elif bg_type == "image":
            # Add background image as full-slide picture
            image_data = background.get("image_data")
            if image_data:
                from io import BytesIO
                image_bytes = base64.b64decode(image_data)
                image_stream = BytesIO(image_bytes)
                slide.shapes.add_picture(image_stream, 0, 0, prs.slide_width, prs.slide_height)
    
    def _add_text_element(self, slide, element):
        """Add text element to slide"""
        text = element.get("text", "")
        position = element.get("position", {})
        formatting = element.get("formatting", {})
        
        left = Inches(position.get("left", 1))
        top = Inches(position.get("top", 1))
        width = Inches(position.get("width", 4))
        height = Inches(position.get("height", 1))
        
        # Add text box
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.text = text
        
        # Apply formatting
        if formatting:
            paragraph = text_frame.paragraphs[0]
            
            if "font_size" in formatting:
                paragraph.font.size = Pt(formatting["font_size"])
            if "bold" in formatting:
                paragraph.font.bold = formatting["bold"]
            if "italic" in formatting:
                paragraph.font.italic = formatting["italic"]
            if "color" in formatting and formatting["color"].startswith("#"):
                r, g, b = hex_to_rgb(formatting["color"][1:])
                paragraph.font.color.rgb = RGBColor(r, g, b)
            
            # Text containment features
            if "autosize_type" in formatting:
                autosize_map = {
                    "NONE": MSO_AUTO_SIZE.NONE,
                    "SHAPE_TO_FIT_TEXT": MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT,
                    "TEXT_TO_FIT_SHAPE": MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                }
                autosize_type = formatting["autosize_type"]
                if autosize_type in autosize_map:
                    text_frame.auto_size = autosize_map[autosize_type]
            
            if "word_wrap" in formatting:
                text_frame.word_wrap = formatting["word_wrap"]
            
            if "vertical_anchor" in formatting:
                anchor_map = {
                    "TOP": MSO_ANCHOR.TOP,
                    "MIDDLE": MSO_ANCHOR.MIDDLE,
                    "BOTTOM": MSO_ANCHOR.BOTTOM
                }
                anchor = formatting["vertical_anchor"]
                if anchor in anchor_map:
                    text_frame.vertical_anchor = anchor_map[anchor]
            
            # Text margins to prevent edge overflow
            margins = formatting.get("margins", {})
            if margins:
                if "left" in margins:
                    text_frame.margin_left = Inches(margins["left"])
                if "right" in margins:
                    text_frame.margin_right = Inches(margins["right"])
                if "top" in margins:
                    text_frame.margin_top = Inches(margins["top"])
                if "bottom" in margins:
                    text_frame.margin_bottom = Inches(margins["bottom"])
            else:
                # Set default margins to prevent text touching edges
                text_frame.margin_left = Inches(0.1)
                text_frame.margin_right = Inches(0.1)
                text_frame.margin_top = Inches(0.05)
                text_frame.margin_bottom = Inches(0.05)
            
            # Auto-fit text to shape if specified
            fit_text = formatting.get("fit_text", {})
            if fit_text and "max_size" in fit_text:
                max_size = fit_text["max_size"]
                text_frame.fit_text(max_size=max_size)
            
        else:
            # Even without formatting, set default margins and word wrap
            text_frame.word_wrap = True
            text_frame.margin_left = Inches(0.1)
            text_frame.margin_right = Inches(0.1)
            text_frame.margin_top = Inches(0.05)
            text_frame.margin_bottom = Inches(0.05)
    
    def _add_chart_element(self, slide, element):
        """Add chart element to slide"""
        chart_type_map = {
            "column_clustered": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "line": XL_CHART_TYPE.LINE,
            "pie": XL_CHART_TYPE.PIE,
            "bar_clustered": XL_CHART_TYPE.BAR_CLUSTERED
        }
        
        chart_type = element.get("chart_type", "column_clustered")
        position = element.get("position", {})
        data = element.get("data", {})
        
        left = Inches(position.get("left", 1))
        top = Inches(position.get("top", 1))
        width = Inches(position.get("width", 6))
        height = Inches(position.get("height", 4))
        
        # Prepare chart data
        chart_data = CategoryChartData()
        categories = data.get("categories", [])
        series_list = data.get("series", [])
        
        chart_data.categories = categories
        for series in series_list:
            chart_data.add_series(series["name"], series["values"])
        
        # Add chart
        slide.shapes.add_chart(
            chart_type_map.get(chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED),
            left, top, width, height, chart_data
        )
    
    def _add_table_element(self, slide, element):
        """Add table element to slide"""
        rows = element.get("rows", 2)
        cols = element.get("cols", 2)
        position = element.get("position", {})
        data = element.get("data", [])
        
        left = Inches(position.get("left", 1))
        top = Inches(position.get("top", 1))
        width = Inches(position.get("width", 6))
        height = Inches(position.get("height", 3))
        
        # Add table
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
        table = table_shape.table
        
        # Populate data
        for row_idx, row_data in enumerate(data[:rows]):
            for col_idx, cell_data in enumerate(row_data[:cols]):
                if row_idx < len(table.rows) and col_idx < len(table.columns):
                    table.cell(row_idx, col_idx).text = str(cell_data)
    
    def _add_image_element(self, slide, element):
        """Add image element to slide"""
        image_source = element.get("image_source", {})
        position = element.get("position", {})
        
        left = Inches(position.get("left", 1))
        top = Inches(position.get("top", 1))
        width = Inches(position.get("width", 4)) if "width" in position else None
        height = Inches(position.get("height", 3)) if "height" in position else None
        
        if image_source.get("type") == "base64":
            image_data = image_source.get("image_data")
            if image_data:
                from io import BytesIO
                image_bytes = base64.b64decode(image_data)
                image_stream = BytesIO(image_bytes)
                
                if width and height:
                    slide.shapes.add_picture(image_stream, left, top, width, height)
                else:
                    slide.shapes.add_picture(image_stream, left, top)
    
    def _add_bullet_list_element(self, slide, element):
        """Add bullet list element to slide"""
        bullet_items = element.get("bullet_items", [])
        position = element.get("position", {})
        
        left = Inches(position.get("left", 1))
        top = Inches(position.get("top", 1))
        width = Inches(position.get("width", 6))
        height = Inches(position.get("height", 4))
        
        # Add text box for bullet list
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.clear()
        
        # Add bullet items
        for i, item in enumerate(bullet_items):
            text = item.get("text", "")
            level = item.get("level", 0)
            
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            p.text = text
            p.level = min(max(level, 0), 8)
            p.alignment = PP_ALIGN.LEFT