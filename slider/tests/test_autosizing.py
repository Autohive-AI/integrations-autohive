# Test auto-sizing behavior with markdown content
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_autosizing_scenarios():
    """
    Test various auto-sizing scenarios with markdown content.
    Creates: test_autosizing.pptx for manual verification
    """
    print("=" * 80)
    print("AUTO-SIZING TEST - Text Containment with Markdown")
    print("=" * 80)
    print("\nTesting scenarios:")
    print("  1. Short text in large box (should not expand)")
    print("  2. Long text in small box (should shrink to fit)")
    print("  3. Very long text (test overflow prevention)")
    print("  4. Markdown formatted text (bold, italic, etc.)")
    print("  5. Multi-line text with line breaks")
    print("  6. Bullet lists with varying amounts of content")
    print("  7. Table cells with long markdown content")
    print("  8. Build from markdown (auto-layout)")
    print("\n" + "=" * 80 + "\n")

    auth = {}

    # ========================================================================
    # SETUP: Create Presentation
    # ========================================================================
    print("Creating test presentation...")
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "**Auto-Sizing Tests**",
            "subtitle": "Text Containment with Markdown",
            "custom_filename": "test_autosizing"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  Created presentation: {presentation_id}\n")

    # ========================================================================
    # SLIDE 2: Short Text in Various Sized Boxes
    # ========================================================================
    print("SLIDE 2: Short text in different box sizes...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "# Short Text Tests",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Test 1: Short text in large box
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "**Short**",
            "position": {"left": 1, "top": 2, "width": 3, "height": 2},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Short text in large box (3x2 inches)")

        # Test 2: Short text in small box
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "*Tiny*",
            "position": {"left": 5, "top": 2, "width": 1, "height": 0.5},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Short text in small box (1x0.5 inches)")

    # ========================================================================
    # SLIDE 3: Long Text in Small Boxes (Should Auto-Shrink)
    # ========================================================================
    print("\nSLIDE 3: Long text in small boxes (auto-shrink test)...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "text": "# Long Text Auto-Shrink Tests",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Test 1: Long plain text in small box
        long_text = "This is a very long piece of text that should automatically shrink to fit within the small text box boundaries using TEXT_TO_FIT_SHAPE auto-sizing."
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "text": long_text,
            "position": {"left": 1, "top": 2, "width": 3, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Long plain text ({len(long_text)} chars) in 3x1 box")

        # Test 2: Long markdown text in small box
        markdown_text = "**Important Notice**: This is *formatted text* with __multiple__ `styles` that should automatically shrink to fit the available space."
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "text": markdown_text,
            "position": {"left": 5, "top": 2, "width": 3, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Long markdown text ({len(markdown_text)} chars) in 3x1 box")

        # Test 3: Very long text
        very_long_text = "**Executive Summary**: " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 2,
            "text": very_long_text,
            "position": {"left": 1, "top": 3.5, "width": 4, "height": 1.5},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Very long text ({len(very_long_text)} chars) in 4x1.5 box")

    # ========================================================================
    # SLIDE 4: Multi-line Text with Line Breaks
    # ========================================================================
    print("\nSLIDE 4: Multi-line text with line breaks...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 3,
            "text": "# Multi-line Text Tests",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Test with explicit line breaks in markdown
        multiline_text = """**Line 1**: First line
*Line 2*: Second line
__Line 3__: Third line
`Line 4`: Fourth line"""

        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 3,
            "text": multiline_text,
            "position": {"left": 1, "top": 2, "width": 7, "height": 2},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Multi-line markdown with different formatting per line")

    # ========================================================================
    # SLIDE 5: Bullet Lists with Varying Content Length
    # ========================================================================
    print("\nSLIDE 5: Bullet lists with varying content...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "text": "# Bullet List Auto-Sizing",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Short bullets in constrained space
        result = await slide_maker.execute_action("add_bullet_list", {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "bullet_items": [
                {"text": "**Short**", "level": 0},
                {"text": "*Tiny*", "level": 0},
                {"text": "`Code`", "level": 0}
            ],
            "position": {"left": 1, "top": 2, "width": 3, "height": 1.5},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] 3 short bullets in 3x1.5 box")

        # Long bullets in constrained space
        result = await slide_maker.execute_action("add_bullet_list", {
            "presentation_id": presentation_id,
            "slide_index": 4,
            "bullet_items": [
                {"text": "**First point**: This is a longer bullet with __important__ information", "level": 0},
                {"text": "*Second point*: Another lengthy item with `code references` included", "level": 0},
                {"text": "**Third point**: Even more content that might need to shrink", "level": 0},
                {"text": "Nested detail under third", "level": 1},
                {"text": "More nested detail", "level": 1}
            ],
            "position": {"left": 5, "top": 2, "width": 4, "height": 2},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] 5 long bullets in 4x2 box (should auto-adjust)")

    # ========================================================================
    # SLIDE 6: Table Cells with Long Content
    # ========================================================================
    print("\nSLIDE 6: Table cells with long markdown content...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "text": "# Table Cell Auto-Sizing",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Table with varying cell content lengths
        result = await slide_maker.execute_action("add_table", {
            "presentation_id": presentation_id,
            "slide_index": 5,
            "rows": 4,
            "cols": 2,
            "position": {"left": 1, "top": 2, "width": 8, "height": 3},
            "data": [
                ["**Short**", "**Headers**"],
                ["Item 1", "A very long description with **bold** and *italic* formatting that might overflow"],
                ["Item 2", "Another __lengthy__ piece of `content` here"],
                ["Item 3", "More text with multiple formats: **bold** *italic* __underline__ and `code`"]
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Table with varying cell content lengths")

    # ========================================================================
    # SLIDE 7: Build from Markdown (Auto-Layout Test)
    # ========================================================================
    print("\nSLIDE 7: Build from markdown with auto-layout...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Build slide with lots of content
        markdown_content = """
# Complex Slide with Lots of Content

## Section 1: Introduction
This is a paragraph with **important** information that needs to be displayed. It contains *various* formatting and __underlined__ text with `code samples`.

## Section 2: Key Points
- **First major point**: This bullet has a lot of text to test how auto-sizing handles longer content with multiple formats
- *Second major point*: Another lengthy bullet point with __critical__ information and `technical details`
- **Third point**: Short but bold

## Section 3: Data Table
| Metric | Q1 | Q2 | Q3 |
|--------|----|----|-----|
| **Revenue** | $1M | $1.5M | **$2M** |
| *Customers* | 50 | 75 | **100** |
| __Growth__ | 10% | *15%* | **20%** |

## Section 4: Additional Notes
More paragraph content here with multiple sentences. This tests how the layout handles flowing content down the slide and whether elements properly size themselves.

> **Important**: This is a blockquote with critical information
"""

        result = await slide_maker.execute_action("build_slide_from_markdown", {
            "presentation_id": presentation_id,
            "slide_index": 6,
            "markdown": markdown_content,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Built complex slide with {result['elements_created']} elements")
        print(f"       Check for: proper spacing, no overlaps, readable text")

    # ========================================================================
    # SLIDE 8: Extreme Cases
    # ========================================================================
    print("\nSLIDE 8: Extreme auto-sizing cases...")
    async with ExecutionContext(auth=auth) as context:
        # Add slide
        result = await slide_maker.execute_action("add_slide",
            {"presentation_id": presentation_id, "files": [file_data]}, context)
        file_data = result["file"]

        # Title
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "text": "# Extreme Cases",
            "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 1},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Test 1: Minimum size box with text
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "text": "**Minimal Box Test**",
            "position": {"left": 1, "top": 2, "width": 0.5, "height": 0.3},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Text in minimum size box (0.5x0.3)")

        # Test 2: Very long single word
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "text": "**Pneumonoultramicroscopicsilicovolcanoconiosis**",
            "position": {"left": 3, "top": 2, "width": 2, "height": 0.5},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print("  [OK] Very long word in constrained box (2x0.5)")

        # Test 3: Maximum content in fixed space
        max_content = "**Test**: " + ("Word " * 100)
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "text": max_content,
            "position": {"left": 1, "top": 3, "width": 3, "height": 2},
            "files": [file_data]
        }, context)
        file_data = result["file"]
        print(f"  [OK] Maximum content ({len(max_content)} chars) in 3x2 box")

    # ========================================================================
    # SLIDE 9: Inspect and Validate
    # ========================================================================
    print("\nSLIDE 9: Using get_slide_elements to check for issues...")
    async with ExecutionContext(auth=auth) as context:
        # Check slide 7 (extreme cases) for issues
        result = await slide_maker.execute_action("get_slide_elements", {
            "presentation_id": presentation_id,
            "slide_index": 7,
            "include_content": True,
            "files": [file_data]
        }, context)
        # get_slide_elements doesn't modify the file, so keep using existing file_data

        print(f"  Layout Status: {result['layout_status']}")
        print(f"  Total Elements: {result['total_elements']}")

        if result.get('elements_outside_boundary', 0) > 0:
            print(f"  [WARNING] {result['elements_outside_boundary']} elements outside boundaries")

        if result.get('total_overlapping_pairs', 0) > 0:
            print(f"  [WARNING] {result['total_overlapping_pairs']} overlapping pairs detected")

        if result['layout_status'] == 'no_issues':
            print("  [OK] No layout issues detected")

    # ========================================================================
    # Save and Report
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING TEST PRESENTATION...")
    print("=" * 80)

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_autosizing.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Test presentation saved to:")
    print(f"          {output_path}")
    print(f"\nMANUAL VERIFICATION CHECKLIST:")
    print(f"  Open the file and check each slide:")
    print(f"")
    print(f"  Slide 2 - Short Text:")
    print(f"    [ ] Short text doesn't look tiny in large box")
    print(f"    [ ] Small box text is readable")
    print(f"")
    print(f"  Slide 3 - Long Text Auto-Shrink:")
    print(f"    [ ] Long plain text fits in box (text shrunk)")
    print(f"    [ ] Markdown formatted text fits in box")
    print(f"    [ ] Very long text (500+ chars) is readable")
    print(f"    [ ] Text is NOT cut off")
    print(f"")
    print(f"  Slide 4 - Multi-line:")
    print(f"    [ ] Line breaks are preserved")
    print(f"    [ ] Each line has correct formatting")
    print(f"")
    print(f"  Slide 5 - Bullet Lists:")
    print(f"    [ ] Short bullets don't look weird")
    print(f"    [ ] Long bullets fit in box")
    print(f"    [ ] Nested bullets are indented properly")
    print(f"")
    print(f"  Slide 6 - Table Cells:")
    print(f"    [ ] Long cell content fits (no cutoff)")
    print(f"    [ ] Markdown formatting preserved in cells")
    print(f"")
    print(f"  Slide 7 - Build from Markdown:")
    print(f"    [ ] All elements visible")
    print(f"    [ ] No overlaps between elements")
    print(f"    [ ] Elements don't extend off slide")
    print(f"")
    print(f"  Slide 8 - Extreme Cases:")
    print(f"    [ ] Minimum box has visible text")
    print(f"    [ ] Very long word handled gracefully")
    print(f"    [ ] 500+ word text fits in box")
    print(f"")
    print("=" * 80)
    print("\nREPORT BACK:")
    print("  Please open the file and report any issues you find:")
    print("  - Text cut off / not visible")
    print("  - Text too small to read")
    print("  - Overlapping elements")
    print("  - Elements extending off slide")
    print("  - Formatting not applied correctly")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_autosizing_scenarios()
        print(f"\n[READY FOR REVIEW]")
        print(f"File: {output_path}")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
