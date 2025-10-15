# Test that auto-sizing works in ALL text actions
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_all_actions_autosizing():
    """
    Test auto-sizing across ALL actions that handle text.
    Creates: test_universal_autosizing.pptx
    """
    print("=" * 80)
    print("UNIVERSAL AUTO-SIZING TEST - All Text Actions")
    print("=" * 80)
    print("\nTesting auto-sizing in:")
    print("  1. create_presentation (title/subtitle)")
    print("  2. add_text")
    print("  3. add_bullet_list")
    print("  4. add_table")
    print("  5. modify_element (text content)")
    print("  6. modify_element (table cells)")
    print("  7. modify_slide (text replacement)")
    print("  8. build_slide_from_markdown")
    print("\n" + "=" * 80 + "\n")

    auth = {}

    # Long text to force auto-sizing
    LONG_TEXT = "This is intentionally very long text with **bold formatting** and *italic styling* to test if auto-sizing works properly. " * 3

    # ========================================================================
    # TEST 1: create_presentation with long title/subtitle
    # ========================================================================
    print("TEST 1: create_presentation with EXTREMELY long title/subtitle...")
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "**Super Long Title with Bold Formatting** - " + "Testing Auto-Sizing Behavior with Extremely Long Content " * 10,
            "subtitle": "*Long subtitle with formatting* - " + "More text here " * 15,
            "custom_filename": "test_universal_autosizing"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  [OK] Created with long formatted title/subtitle")
        print(f"       Title: {len(inputs['title'])} chars (should shrink to fit)")
        print(f"       Subtitle: {len(inputs['subtitle'])} chars (should shrink to fit)")

    # ========================================================================
    # TEST 2: add_text with varying amounts of content
    # ========================================================================
    print("\nTEST 2: add_text with long content in small boxes...")
    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Test 1: Short box, long plain text
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "Plain text: " + ("Word " * 30),
            "position": {"left": 1, "top": 1, "width": 2, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Plain text (150+ chars) in 2x1 box")

        # Test 2: Short box, long formatted text
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "**Bold text:** " + ("Important " * 20) + " *and italic too*",
            "position": {"left": 4, "top": 1, "width": 2, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Formatted text (bold/italic, 150+ chars) in 2x1 box")

        # Test 3: Tiny box, moderate text
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "__Underlined text__ with more content than fits",
            "position": {"left": 7, "top": 1, "width": 1.5, "height": 0.6},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Underlined text in tiny 1.5x0.6 box")

    # ========================================================================
    # TEST 3: add_bullet_list with long bullets in small box
    # ========================================================================
    print("\nTEST 3: add_bullet_list with long formatted bullets...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Long bullets with formatting in constrained space
        result = await slide_maker.execute_action("add_bullet_list", {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "bullet_items": [
                {"text": "**First bullet**: This is a very long bullet point with bold formatting and lots of content that needs to shrink", "level": 0},
                {"text": "*Second bullet*: Another lengthy item with italic text and more words to fill space", "level": 0},
                {"text": "__Third bullet__: Underlined text with even more content to test sizing", "level": 0},
                {"text": "Nested bullet with `code` and additional text", "level": 1},
                {"text": "Another nested item with content", "level": 1},
            ],
            "position": {"left": 1, "top": 1, "width": 3, "height": 2},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] 5 long formatted bullets in 3x2 box (should shrink)")

    # ========================================================================
    # TEST 4: add_table with long cell content
    # ========================================================================
    print("\nTEST 4: add_table with long formatted cell content...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Table with varying content lengths
        result = await slide_maker.execute_action("add_table", {
            "presentation_id": presentation_id,
            "slide_index": 3,
            "rows": 3,
            "cols": 2,
            "position": {"left": 1, "top": 1, "width": 6, "height": 2},
            "data": [
                ["**Header 1**", "**Header 2 with Long Text**"],
                ["Short", "This is a very long cell with **bold** and *italic* formatting that should shrink to fit the cell width and height"],
                ["Item 2", "__Underlined__ text with `code samples` and more content to test cell auto-sizing behavior"]
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Table with long formatted cells (should shrink per cell)")

    # ========================================================================
    # TEST 5: modify_element - Update text content
    # ========================================================================
    print("\nTEST 5: modify_element - Update text with long content...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # First create a text box
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "text": "Placeholder",
            "position": {"left": 1, "top": 1, "width": 3, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Now modify it with long content
        result = await slide_maker.execute_action("modify_element", {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "element_index": 0,
            "text_content": "**Modified Text**: " + ("This is replacement text with formatting " * 5),
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Modified text box with long formatted content (should shrink)")

    # ========================================================================
    # TEST 6: modify_element - Update table cells
    # ========================================================================
    print("\nTEST 6: modify_element - Update table cells with long content...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Create table with placeholders
        result = await slide_maker.execute_action("add_table", {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "rows": 3,
            "cols": 2,
            "position": {"left": 1, "top": 1, "width": 6, "height": 1.5},
            "data": [
                ["A", "B"],
                ["C", "D"],
                ["E", "F"]
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Now fill cells with long formatted content
        result = await slide_maker.execute_action("modify_element", {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "element_index": 0,
            "table_cell_updates": [
                {"row": 0, "col": 0, "text": "**Very Long Header** with lots of text"},
                {"row": 1, "col": 0, "text": "Normal cell"},
                {"row": 1, "col": 1, "text": "*Italic cell* with " + ("more text " * 10)},
                {"row": 2, "col": 1, "text": "__Underlined__ and **bold** with " + ("content " * 8)}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Updated 4 table cells with long formatted content (should shrink per cell)")

    # ========================================================================
    # TEST 7: modify_slide - Text replacement
    # ========================================================================
    print("\nTEST 7: modify_slide - Replace with long formatted text...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Create text with placeholder
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 6,
            "text": "Replace: PLACEHOLDER",
            "position": {"left": 1, "top": 1, "width": 2.5, "height": 0.8},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Replace with long content
        result = await slide_maker.execute_action("modify_slide", {
            "presentation_id": presentation_id,
            "slide_index": 6,
            "updates": {
                "replace_text": [
                    {"old_text": "PLACEHOLDER", "new_text": "**Long replacement** with *formatting* and " + ("more words " * 10)}
                ]
            },
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Replaced text with long formatted content (should shrink)")

    # ========================================================================
    # TEST 8: build_slide_from_markdown - Full slide
    # ========================================================================
    print("\nTEST 8: build_slide_from_markdown with lots of content...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Build slide with lots of content (should auto-size all elements)
        markdown = """
# Very Long Title with Lots of Words to Test Auto-Sizing Behavior Across Multiple Lines

## Long Heading Section with Additional Text to Ensure Proper Sizing

This is a paragraph with **bold text** and *italic text* and __underlined text__ that contains a significant amount of content to test whether the auto-sizing calculation properly handles formatted paragraphs with mixed styling and ensures everything fits.

## Bullet Section
- **First bullet**: This is a very long bullet point with bold text and lots of content that needs to shrink to fit properly within the allocated space
- *Second bullet*: Another lengthy bullet with italic formatting and additional words to fill the space
- __Third bullet__: Underlined text with even more content to verify sizing works
- Nested item with `code` and more text
- Another bullet with content

## Table Section
| **Column 1** | **Column 2 with Long Header Text** |
|--------------|-------------------------------------|
| Short | **Bold cell** with lots of text content that should shrink to fit the cell dimensions |
| Item | *Italic cell* with even more text to test auto-sizing in table cells |
"""

        result = await slide_maker.execute_action("build_slide_from_markdown", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "markdown": markdown,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Built slide with {result['elements_created']} elements (all should auto-size)")

    # ========================================================================
    # SAVE AND VERIFY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING TEST PRESENTATION...")
    print("=" * 80)

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_universal_autosizing.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Saved: {output_path}")
    print("\n" + "=" * 80)
    print("VERIFICATION CHECKLIST:")
    print("=" * 80)
    print("\nOpen the file and verify ALL text fits properly:")
    print("")
    print("  Slide 1 - create_presentation:")
    print("    [ ] Long title fits in title box")
    print("    [ ] Long subtitle fits in subtitle box")
    print("    [ ] Bold/italic formatting preserved")
    print("")
    print("  Slide 2 - add_text (3 boxes):")
    print("    [ ] Left box: Plain text fits in 2x1")
    print("    [ ] Middle box: Bold/italic text fits in 2x1")
    print("    [ ] Right box: Underlined text fits in 1.5x0.6")
    print("    [ ] All formatting preserved")
    print("")
    print("  Slide 3 - add_bullet_list:")
    print("    [ ] 5 long formatted bullets fit in 3x2 box")
    print("    [ ] Nested bullets visible")
    print("    [ ] Bold/italic/underline formatting intact")
    print("")
    print("  Slide 4 - add_table:")
    print("    [ ] Long header text fits in cells")
    print("    [ ] Long formatted cell content fits")
    print("    [ ] Each cell sized independently")
    print("    [ ] Formatting preserved in all cells")
    print("")
    print("  Slide 5 - modify_element (text):")
    print("    [ ] Modified long formatted text fits in 3x1 box")
    print("    [ ] Bold formatting preserved")
    print("")
    print("  Slide 6 - modify_element (table cells):")
    print("    [ ] All 4 updated cells fit their content")
    print("    [ ] Each cell sized independently")
    print("    [ ] Formatting preserved")
    print("")
    print("  Slide 7 - modify_slide (replacement):")
    print("    [ ] Replacement text fits in 2.5x0.8 box")
    print("    [ ] Bold/italic formatting preserved")
    print("")
    print("  Slide 8 - build_slide_from_markdown:")
    print("    [ ] Long title fits at top")
    print("    [ ] Long heading fits")
    print("    [ ] Paragraph with mixed formatting fits")
    print("    [ ] All 5 bullets fit")
    print("    [ ] Table cells with long content fit")
    print("    [ ] All elements have proper font sizes")
    print("")
    print("=" * 80)
    print("\nKEY TEST:")
    print("  If ANY text overflows vertically, report which slide/element!")
    print("  Auto-sizing should work in ALL actions now.")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_all_actions_autosizing()
        print(f"\n[TEST COMPLETE]")
        print(f"File: {output_path}")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
