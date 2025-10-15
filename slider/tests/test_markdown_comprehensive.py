# Comprehensive test for markdown functionality across all actions
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os

async def test_markdown_complete_workflow():
    """
    Comprehensive test demonstrating markdown support across all actions.
    Creates a complete presentation showcasing all markdown features.
    Outputs: test_markdown_complete.pptx
    """
    print("=" * 80)
    print("COMPREHENSIVE MARKDOWN TEST - Slide Maker Integration")
    print("=" * 80)
    print("\nThis test demonstrates markdown support across ALL text-accepting actions:")
    print("  1. create_presentation (title/subtitle)")
    print("  2. add_text (text content)")
    print("  3. add_bullet_list (bullet items)")
    print("  4. add_table (table cells)")
    print("  5. build_slide_from_markdown (entire slide)")
    print("  6. modify_element (text boxes and table cells)")
    print("  7. build_presentation_from_markdown (multi-slide)")
    print("\n" + "=" * 80 + "\n")

    auth = {}

    # ========================================================================
    # SLIDE 1: Create Presentation with Markdown Title/Subtitle
    # ========================================================================
    print("SLIDE 1: Creating presentation with markdown title/subtitle...")
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "**Markdown Integration** - *Comprehensive Test*",
            "subtitle": "__Powered by__ Slide Maker with `HTML/Markdown` parsing",
            "custom_filename": "test_markdown_complete"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]

        print(f"  [OK] Created presentation: {presentation_id}")
        print(f"       Title: {inputs['title']}")
        print(f"       Subtitle: {inputs['subtitle']}")
        print(f"       Expected: Bold 'Markdown Integration', italic 'Comprehensive Test'")
        print(f"                 Underlined 'Powered by', code style 'HTML/Markdown'")

    # ========================================================================
    # SLIDE 2: Add Text with Markdown
    # ========================================================================
    print("\nSLIDE 2: Testing add_text with markdown...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        add_slide_inputs = {"presentation_id": presentation_id, "files": [file_data]}
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        file_data = result["file"]

        # Add title
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "# add_text() with Markdown",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_text", inputs, context)
        file_data = result["file"]

        # Add examples of all supported markdown features
        markdown_examples = [
            ("**Bold text** example", {"left": 1, "top": 2, "width": 8, "height": 0.5}),
            ("*Italic text* example", {"left": 1, "top": 2.6, "width": 8, "height": 0.5}),
            ("__Underlined text__ example", {"left": 1, "top": 3.2, "width": 8, "height": 0.5}),
            ("`Code style` text example", {"left": 1, "top": 3.8, "width": 8, "height": 0.5}),
            ("**Bold** and *italic* and __underlined__ combined!", {"left": 1, "top": 4.4, "width": 8, "height": 0.5}),
            ("Plain text without markers passes through naturally", {"left": 1, "top": 5, "width": 8, "height": 0.5})
        ]

        for text, position in markdown_examples:
            inputs = {
                "presentation_id": presentation_id,
                "slide_index": 1,
                "text": text,
                "position": position,
                "files": [file_data]
            }
            result = await slide_maker.execute_action("add_text", inputs, context)
            file_data = result["file"]
            print(f"  [OK] Added: {text}")

    # ========================================================================
    # SLIDE 3: Add Bullet List with Markdown Items
    # ========================================================================
    print("\nSLIDE 3: Testing add_bullet_list with markdown items...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        add_slide_inputs = {"presentation_id": presentation_id, "files": [file_data]}
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        file_data = result["file"]

        # Add title
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "text": "# add_bullet_list() with Markdown",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_text", inputs, context)
        file_data = result["file"]

        # Add bullet list with markdown formatting in items
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "bullet_items": [
                {"text": "**Bold bullet** item", "level": 0},
                {"text": "*Italic bullet* item", "level": 0},
                {"text": "Nested with __underline__", "level": 1},
                {"text": "Nested with `code style`", "level": 1},
                {"text": "Mixed: **bold** and *italic* and `code`", "level": 0},
                {"text": "Revenue: **$5M** *(+25% growth)*", "level": 1}
            ],
            "position": {"left": 1, "top": 2, "width": 8, "height": 3},
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_bullet_list", inputs, context)
        file_data = result["file"]
        print(f"  [OK] Added bullet list with {result['items_count']} markdown-formatted items")

    # ========================================================================
    # SLIDE 4: Add Table with Markdown Cells
    # ========================================================================
    print("\nSLIDE 4: Testing add_table with markdown cells...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        add_slide_inputs = {"presentation_id": presentation_id, "files": [file_data]}
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        file_data = result["file"]

        # Add title
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 3,
            "text": "# add_table() with Markdown Cells",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_text", inputs, context)
        file_data = result["file"]

        # Add table with markdown in cells
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 3,
            "rows": 4,
            "cols": 3,
            "position": {"left": 1, "top": 2, "width": 8, "height": 3},
            "data": [
                ["**Metric**", "**Target**", "**Actual**"],
                ["Revenue", "$4M", "**$5M** *(+25%)*"],
                ["Customers", "120", "**150** *new*"],
                ["Growth", "20%", "__30%__ `exceeded`"]
            ],
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_table", inputs, context)
        file_data = result["file"]
        print(f"  [OK] Added table with markdown-formatted cells")
        print(f"       Headers: Bold")
        print(f"       Data: Mixed formatting (bold numbers, italic notes, etc.)")

    # ========================================================================
    # SLIDE 5: Build Slide from Markdown (Full Structure)
    # ========================================================================
    print("\nSLIDE 5: Testing build_slide_from_markdown...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        add_slide_inputs = {"presentation_id": presentation_id, "files": [file_data]}
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        file_data = result["file"]

        # Build entire slide from markdown
        markdown_content = """
# Q4 Financial Results

## Revenue Performance
- Q4 Revenue: **$5.2M** *(+28% YoY)*
- Recurring: **$3.8M** *(73% of total)*
- New business: __$1.4M__

## Key Metrics

| Department | Budget | Actual | Variance |
|------------|--------|--------|----------|
| Sales | $2M | **$2.5M** | *+25%* |
| Marketing | $800K | **$750K** | *-6%* |
| Engineering | $1.5M | **$1.6M** | *+7%* |

> **Note**: All departments met or exceeded targets

## Technology Stack
- Frontend: `React` + `TypeScript`
- Backend: `Python` + `FastAPI`
- Database: **PostgreSQL** (migrated from MySQL)
"""

        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "markdown": markdown_content,
            "files": [file_data]
        }
        result = await slide_maker.execute_action("build_slide_from_markdown", inputs, context)
        file_data = result["file"]

        print(f"  [OK] Built slide from markdown")
        print(f"       Elements created: {result['elements_created']}")
        print(f"       Includes: title, headings, bullets, table, blockquote, code")

    # ========================================================================
    # SLIDE 6: Template Modification with modify_element
    # ========================================================================
    print("\nSLIDE 6: Testing modify_element with markdown...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        add_slide_inputs = {"presentation_id": presentation_id, "files": [file_data]}
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        file_data = result["file"]

        # First create a "template" with placeholder text
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "text": "{{TITLE}}",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_text", inputs, context)
        file_data = result["file"]

        # Add a table template
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "rows": 3,
            "cols": 2,
            "position": {"left": 1, "top": 2, "width": 8, "height": 2},
            "data": [
                ["Metric", "Value"],
                ["{{METRIC_1}}", "{{VALUE_1}}"],
                ["{{METRIC_2}}", "{{VALUE_2}}"]
            ],
            "files": [file_data]
        }
        result = await slide_maker.execute_action("add_table", inputs, context)
        file_data = result["file"]

        print(f"  [OK] Created template slide with placeholders")

        # Now fill the template using modify_element with markdown
        print(f"  [*] Filling template with markdown...")

        # Fill title
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "element_index": 0,
            "text_content": "**Template Filled** with *Markdown*",
            "files": [file_data]
        }
        result = await slide_maker.execute_action("modify_element", inputs, context)
        file_data = result["file"]
        print(f"       [OK] Updated title with markdown")

        # Fill table cells with markdown
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "element_index": 1,
            "table_cell_updates": [
                {"row": 1, "col": 0, "text": "**Total Revenue**"},
                {"row": 1, "col": 1, "text": "$5M *(+25%)*"},
                {"row": 2, "col": 0, "text": "*Customer Count*"},
                {"row": 2, "col": 1, "text": "**150** __new customers__"}
            ],
            "files": [file_data]
        }
        result = await slide_maker.execute_action("modify_element", inputs, context)
        file_data = result["file"]
        print(f"       [OK] Updated {len(inputs['table_cell_updates'])} table cells with markdown")

    # ========================================================================
    # SLIDES 7-9: Build Presentation from Markdown (Multi-Slide)
    # ========================================================================
    print("\nSLIDES 7-9: Testing build_presentation_from_markdown...")
    async with ExecutionContext(auth=auth) as context:

        # Build multiple slides from markdown outline
        markdown_outline = """
# Product Roadmap 2024

## Q1 Deliverables
- **Feature A**: User authentication
- **Feature B**: Dashboard analytics
- *Status*: __On track__

---

# Technical Architecture

## Stack Overview
| Layer | Technology | Status |
|-------|------------|--------|
| Frontend | **React** + `TypeScript` | *Deployed* |
| Backend | **Python** + `FastAPI` | *In Progress* |
| Database | **PostgreSQL** | __Migrated__ |

## Infrastructure
- Cloud: **AWS** *(primary)*
- CDN: `CloudFlare`
- Monitoring: __DataDog__

---

# Team & Resources

## Current Team
- Engineering: **12 developers**
- Product: *3 managers*
- Design: __2 designers__

> **Hiring**: Looking for 5 more engineers in Q2

## Budget Status
Overall budget: **$500K** allocated
- Spent: $320K *(64%)*
- Remaining: __$180K__
"""

        inputs = {
            "presentation_id": presentation_id,
            "outline": markdown_outline,
            "files": [file_data]
        }
        result = await slide_maker.execute_action("build_presentation_from_markdown", inputs, context)
        file_data = result["file"]

        print(f"  [OK] Built presentation from markdown outline")
        print(f"       Slides created: {result['slides_created']}")
        print(f"       Each H1 header created a new slide")
        print(f"       All markdown formatting preserved")

    # ========================================================================
    # Save Final Presentation
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING FINAL PRESENTATION...")
    print("=" * 80)

    # Save the file to disk for verification
    output_path = os.path.join(os.path.dirname(__file__), "..", "test_markdown_complete.pptx")

    # Decode and save the file
    import base64
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Presentation saved to:")
    print(f"          {output_path}")
    print(f"\nPRESENTATION SUMMARY:")
    print(f"  Total slides: ~9 slides")
    print(f"  Slide 1: Title slide (create_presentation)")
    print(f"  Slide 2: add_text examples (all markdown features)")
    print(f"  Slide 3: add_bullet_list (markdown in bullets)")
    print(f"  Slide 4: add_table (markdown in cells)")
    print(f"  Slide 5: build_slide_from_markdown (full structure)")
    print(f"  Slide 6: modify_element (template filling)")
    print(f"  Slides 7-9: build_presentation_from_markdown (multi-slide)")
    print(f"\nVERIFICATION:")
    print(f"  Open the file in PowerPoint to verify:")
    print(f"  - Bold, italic, underline, strikethrough formatting")
    print(f"  - Code style (monospace) text")
    print(f"  - Mixed formatting in single text elements")
    print(f"  - Formatted bullet items")
    print(f"  - Formatted table cells")
    print(f"  - Complete slide structures from markdown")
    print(f"\n" + "=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_markdown_complete_workflow()
        print(f"\n[TEST COMPLETE]")
        print(f"\nNext steps:")
        print(f"  1. Open: {output_path}")
        print(f"  2. Verify all markdown formatting is correctly applied")
        print(f"  3. Check that plain text (no markers) renders normally")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
