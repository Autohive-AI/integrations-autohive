# Slide Maker Integration for Autohive

Connects Autohive to PowerPoint automation using python-pptx to create, modify, and extract content from presentations programmatically.

## Description

The Slide Maker integration provides comprehensive PowerPoint automation capabilities within Autohive workflows. It enables users to:

- Create presentations from templates or blank presentations
- Add and modify slides with text, images, charts, tables, and bullet lists
- Inspect slide layouts with boundary and overlap detection
- Modify elements in-place without recreating them
- Extract text content from presentations
- Set backgrounds, margins, alignment, and auto-sizing behaviors

The integration operates in a stateless manner, suitable for Lambda environments, where presentations are passed between actions as base64-encoded files. All slides are created as blank layouts (no predefined templates or placeholders) to ensure consistent behavior across different PowerPoint versions.

## Setup & Authentication

This integration does not require external authentication as it operates directly on PowerPoint files using the python-pptx library. No API keys or OAuth setup is needed.

**File Requirements:**
- PowerPoint files must be provided in the `files` parameter - the Autohive platform automatically intercepts and converts file uploads to base64-encoded content
- Supports .pptx format (automatically handled by Autohive's file intercept system)
- Images for insertion must be provided as separate files in supported formats (PNG, JPG, JPEG, GIF, BMP, WEBP) - also automatically processed by Autohive

## Actions

### Action: `create_presentation`

- **Description:** Create a new PowerPoint presentation with optional template. Only blank slides are supported.
- **Inputs:**
  - `title` (optional): Title for the first slide (added as text box)
  - `subtitle` (optional): Subtitle for the first slide (added as text box)
  - `files` (optional): Template files (.pptx) to use as base
  - `custom_filename` (optional): Custom filename for returned file
- **Outputs:**
  - `presentation_id`: Unique identifier for the presentation
  - `slide_count`: Number of slides created
  - `file`: Base64-encoded presentation file for streaming

### Action: `add_slide`

- **Description:** Add a new blank slide to an existing presentation
- **Inputs:**
  - `presentation_id`: ID of the presentation to modify
  - `files`: Current presentation file
- **Outputs:**
  - `slide_index`: Index of the newly added slide
  - `slide_count`: Total number of slides
  - `file`: Updated presentation file

### Action: `add_text`

- **Description:** Add formatted text to a slide in a text box at specified position
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `text`: Text content to add
  - `position`: Object with left, top, width, height in inches
  - `formatting` (optional): Font size, bold, italic, color options
  - `files`: Current presentation file
- **Outputs:**
  - `shape_id`: ID of the created text shape
  - `file`: Updated presentation file

### Action: `add_image`

- **Description:** Insert an image into a slide from uploaded files
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `position`: Object with left, top (width/height optional)
  - `files`: Current presentation file and image file
- **Outputs:**
  - `shape_id`: ID of the created image shape
  - `file`: Updated presentation file

### Action: `add_table`

- **Description:** Create a table in a slide
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `rows`: Number of rows (minimum 1)
  - `cols`: Number of columns (minimum 1)
  - `position`: Object with left, top, width, height in inches
  - `data` (optional): 2D array of table data
  - `files`: Current presentation file
- **Outputs:**
  - `table_id`: ID of the created table
  - `file`: Updated presentation file

### Action: `add_chart`

- **Description:** Create a chart in a slide
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `chart_type`: Type of chart (column_clustered, line, pie, bar_clustered, area, xy_scatter)
  - `position`: Object with left, top, width, height in inches
  - `data`: Object with categories array and series array
  - `files`: Current presentation file
- **Outputs:**
  - `chart_id`: ID of the created chart
  - `file`: Updated presentation file

### Action: `add_bullet_list`

- **Description:** Add a multi-level bullet list to a slide with automatic bullet symbols
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `bullet_items`: Array of items with text and level (0-8)
  - `position`: Object with left, top, width, height in inches
  - `formatting` (optional): Font size, bold, italic, color options
  - `files`: Current presentation file
- **Outputs:**
  - `shape_id`: ID of the created bullet list shape
  - `items_count`: Number of bullet items added
  - `file`: Updated presentation file

### Action: `get_slide_elements`

- **Description:** Get detailed information about all elements on a slide with boundary and overlap analysis
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `include_content` (optional): Whether to include text content for elements with no issues (default: false)
  - `files`: Current presentation file
- **Outputs:**
  - `layout_status`: "no_issues" or "issues_detected"
  - `slide_dimensions`: Width and height in inches
  - `total_elements`: Number of elements on slide
  - `elements`: Array of element details (index, type, position)
  - `element_overlaps` (if issues): Detailed overlap information
  - `elements_outside_boundary` (if issues): Count of boundary violations

### Action: `modify_element`

- **Description:** Modify an existing element in place without recreating it
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `element_index`: Index of element to modify (use get_slide_elements to find)
  - `position` (optional): New position/size with left, top, width, height
  - `text_content` (optional): New text content for text elements
  - `formatting` (optional): Font size, bold, italic, color options
  - `files`: Current presentation file
- **Outputs:**
  - `modified`: Whether changes were made
  - `element_type`: Type of element modified
  - `changes_made`: Array of changes applied
  - `new_position`: Updated position and size
  - `file`: Updated presentation file

### Action: `delete_element`

- **Description:** Remove a shape, text box, image, chart, or other element from a slide
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `shape_index`: Index of element to delete (use get_slide_elements to find)
  - `files`: Current presentation file
- **Outputs:**
  - `deleted`: Whether element was successfully deleted
  - `element_type`: Type of element that was deleted
  - `remaining_shapes`: Number of shapes remaining
  - `file`: Updated presentation file

### Action: `extract_text`

- **Description:** Extract all text content from a presentation
- **Inputs:**
  - `file_path`: Path to the PowerPoint file
- **Outputs:**
  - `slides`: Array of slide text content
  - `all_text`: All text content combined

### Action: `modify_slide`

- **Description:** Update content in an existing slide with text replacements
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of slide to modify
  - `updates`: Object with title and/or replace_text array
  - `files`: Current presentation file
- **Outputs:**
  - `modified`: Whether slide was successfully modified
  - `file`: Updated presentation file

### Action: `save_presentation`

- **Description:** Save a presentation and return as base64-encoded file
- **Inputs:**
  - `presentation_id`: ID of presentation to save
  - `file_path`: Path where to save the presentation
- **Outputs:**
  - `saved`: Whether presentation was successfully saved
  - `file`: Base64-encoded presentation file

### Action: `set_text_autosize`

- **Description:** Set automatic text sizing behavior for a text box
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `shape_index`: Index of the shape (0-based)
  - `autosize_type`: NONE, SHAPE_TO_FIT_TEXT, or TEXT_TO_FIT_SHAPE
  - `word_wrap` (optional): Enable/disable word wrapping
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `autosize_type`: The autosize type that was set
  - `file`: Updated presentation file

### Action: `fit_text_to_shape`

- **Description:** Automatically resize text to fit within shape boundaries
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `shape_index`: Index of the shape (0-based)
  - `max_size` (optional): Maximum font size in points (default: 48)
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `max_size`: Maximum font size used
  - `file`: Updated presentation file

### Action: `set_text_margins`

- **Description:** Set margins for a text box or shape
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `shape_index`: Index of the shape (0-based)
  - `margins`: Object with left, right, top, bottom margins in inches
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `margins_set`: The margins that were applied
  - `file`: Updated presentation file

### Action: `set_text_alignment`

- **Description:** Set vertical alignment for text within a shape
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `shape_index`: Index of the shape (0-based)
  - `vertical_anchor` (optional): TOP, MIDDLE, or BOTTOM
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `vertical_anchor`: The alignment that was set
  - `file`: Updated presentation file

### Action: `set_slide_background_color`

- **Description:** Set a solid color background for a slide
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `color`: Hex color string, RGB array, or theme color object
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `color_set`: The color that was applied
  - `file`: Updated presentation file

### Action: `set_slide_background_gradient`

- **Description:** Set a gradient background for a slide
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `angle` (optional): Gradient angle in degrees (default: 90)
  - `gradient_stops` (optional): Array of color stops with position and color
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `gradient_angle`: The angle that was set
  - `gradient_stops_applied`: Number of stops applied
  - `file`: Updated presentation file

### Action: `add_background_image_workaround`

- **Description:** Add an image as slide background using full-slide picture workaround
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `files`: Current presentation file and image file
- **Outputs:**
  - `success`: Whether operation was successful
  - `method`: Method used to add background
  - `picture_width`: Width of background picture
  - `picture_height`: Height of background picture
  - `file`: Updated presentation file

### Action: `reset_slide_background`

- **Description:** Reset slide background to inherit from master/layout
- **Inputs:**
  - `presentation_id`: ID of the presentation
  - `slide_index`: Index of the slide (0-based)
  - `files`: Current presentation file
- **Outputs:**
  - `success`: Whether operation was successful
  - `follow_master_background`: Whether slide now follows master
  - `file`: Updated presentation file

## Requirements

- `autohive_integrations_sdk`
- `python-pptx`

## Usage Examples

**Example 1: Create a presentation with title slide**

```json
{
  "action": "create_presentation",
  "title": "My Presentation",
  "subtitle": "Created with Autohive"
}
```

**Example 2: Add text box to existing slide**

```json
{
  "action": "add_text",
  "presentation_id": "abc-123",
  "slide_index": 0,
  "text": "Hello World",
  "position": {
    "left": 1.0,
    "top": 2.0,
    "width": 6.0,
    "height": 1.5
  },
  "formatting": {
    "font_size": 24,
    "bold": true,
    "color": "#FF0000"
  }
}
```

**Example 3: Inspect slide for layout issues**

```json
{
  "action": "get_slide_elements",
  "presentation_id": "abc-123",
  "slide_index": 0,
  "include_content": false
}
```

**Example 4: Fix overlapping elements**

```json
{
  "action": "modify_element",
  "presentation_id": "abc-123",
  "slide_index": 0,
  "element_index": 2,
  "position": {
    "left": 5.0,
    "top": 3.0
  }
}
```

## Testing

To run the tests:

1. Navigate to the integration's directory: `cd slider`
2. Install dependencies: `pip install -r requirements.txt -t dependencies`
3. Run element inspection tests: `python tests/test_inspection.py "path/to/presentation.pptx"`

The test suite includes local presentation inspection tools that help debug element positioning, boundary violations, and overlap detection.

## Key Features

- **Blank-only slide policy**: All slides are created without predefined layouts for consistency
- **Boundary validation**: Automatic detection of elements extending beyond slide boundaries
- **Overlap analysis**: Comprehensive checking of element spatial relationships
- **Element modification**: In-place updates without recreating elements
- **Auto-sizing support**: Built-in text fitting with dimension adjustment workarounds
- **Stateless operation**: File-based state transfer suitable for Lambda environments
- **Enhanced file loading**: Supports both .pptx and .bin files from intercept systems
- **Optimized responses**: Minimal token usage with conditional content display