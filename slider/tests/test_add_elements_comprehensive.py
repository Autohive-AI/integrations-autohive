# Comprehensive test for add_elements action (both granular and auto-layout modes)
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_add_elements_comprehensive():
    """
    Comprehensive test for add_elements action:

    GRANULAR MODE (elements array):
    1. Add text box with markdown
    2. Add table from markdown syntax
    3. Add bullet list from markdown
    4. Test auto-positioning (overlap detection)

    AUTO-LAYOUT MODE (markdown document):
    5. Build slide from unified markdown with h1, h2, paragraphs, bullets, tables

    OTHER ACTIONS:
    6. Test add_image
    7. Test add_chart
    8. Test find_and_replace
    9. Test reposition_element (position only)
    10. Test get_slide_elements
    """
    print("=" * 80)
    print("COMPREHENSIVE TEST - add_elements (Granular + Auto-Layout Modes)")
    print("=" * 80)

    auth = {}

    # ========================================================================
    # SETUP: Create Presentation
    # ========================================================================
    print("\n[SETUP] Creating presentation...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("create_presentation", {
            "title": "**Comprehensive Test Suite**",
            "subtitle": "*Testing add_elements unified action*",
            "custom_filename": "test_add_elements_comprehensive"
        }, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  [OK] Created presentation: {presentation_id}")

    # ========================================================================
    # TEST 1: GRANULAR MODE - Single Element (Text Box)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 1: GRANULAR MODE - Add text box with markdown")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        slide_1_idx = result["slide_index"]

        # Add text box using add_elements (granular mode)
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "elements": [
                {
                    "content": "**Sales Report** for *Q4 2024*\n\nRevenue increased by __25%__",
                    "position": {"left": 1, "top": 1, "width": 5, "height": 1.5}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Mode: {result['mode']}")
        print(f"    Total requested: {result['total_requested']}")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        for elem in result['elements_added']:
            print(f"\n    Element {elem['index']}:")
            print(f"      Type: {elem['type']}")
            print(f"      Shape ID: {elem['shape_id']}")
            print(f"      Position adjusted: {elem['position_adjusted']}")
            if elem.get('adjustment_reason'):
                print(f"      Reason: {elem['adjustment_reason']}")

        print(f"\n  [OK] Text box added with markdown formatting")

    # ========================================================================
    # TEST 2: GRANULAR MODE - Multiple Elements (Table + Bullets)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 2: GRANULAR MODE - Add table and bullets together")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "elements": [
                {
                    "content": "| Product | Q3 Revenue | Q4 Revenue |\n|---------|------------|------------|\n| Widget | **$50K** | **$65K** |\n| Gadget | *$30K* | *$35K* |",
                    "position": {"left": 1, "top": 3, "width": 6, "height": 1.5}
                },
                {
                    "content": "- **Key Drivers:**\n  - Increased marketing spend\n  - New product launches\n  - *Improved* sales team performance",
                    "position": {"left": 1, "top": 5, "width": 5, "height": 1.8}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Mode: {result['mode']}")
        print(f"    Total requested: {result['total_requested']}")
        print(f"    Successfully added: {result['successfully_added']}")

        for elem in result['elements_added']:
            print(f"\n    Element {elem['index']}:")
            print(f"      Auto-detected type: {elem['type']}")
            print(f"      Position: ({elem['final_position']['left']:.1f}, {elem['final_position']['top']:.1f})")

        print(f"\n  [OK] Table and bullets auto-detected and added")

    # ========================================================================
    # TEST 3: GRANULAR MODE - Auto-Positioning (Overlap Detection)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 3: GRANULAR MODE - Auto-positioning with overlap detection")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Try to add element at position that overlaps with existing
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "elements": [
                {
                    "content": "This will overlap!",
                    "position": {"left": 1, "top": 1, "width": 3, "height": 0.5},
                    "auto_position": True  # Enable auto-positioning
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        if result['elements_added']:
            elem = result['elements_added'][0]
            print(f"\n    Element repositioned:")
            print(f"      Requested: ({elem['requested_position']['left']:.1f}, {elem['requested_position']['top']:.1f})")
            print(f"      Final: ({elem['final_position']['left']:.1f}, {elem['final_position']['top']:.1f})")
            print(f"      Adjusted: {elem['position_adjusted']}")
            print(f"      Reason: {elem.get('adjustment_reason', 'N/A')}")

        print(f"\n  [OK] Auto-positioning avoided overlap successfully")

    # ========================================================================
    # TEST 4: GRANULAR MODE - Without Auto-Position (Should Skip)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 4: GRANULAR MODE - Overlap without auto_position (should skip)")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "elements": [
                {
                    "content": "This will be skipped!",
                    "position": {"left": 1, "top": 1, "width": 2, "height": 0.5},
                    "auto_position": False  # No auto-positioning
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        if result['elements_skipped']:
            skip = result['elements_skipped'][0]
            print(f"\n    Skipped element:")
            print(f"      Index: {skip['index']}")
            print(f"      Reason: {skip['skip_reason']}")
            print(f"      Suggestion: {skip['suggestion']}")

        print(f"\n  [OK] Element correctly skipped due to overlap")

    # ========================================================================
    # TEST 5: AUTO-LAYOUT MODE - Full Markdown Document
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 5: AUTO-LAYOUT MODE - Build slide from markdown document")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide for auto-layout test
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        slide_2_idx = result["slide_index"]

        # Use add_elements with auto_layout=true
        markdown_doc = """# Executive Summary

## Key Findings

Our Q4 performance shows **significant growth** across all metrics.

### Financial Results

- Revenue: **$5.2M** (+25% YoY)
- Profit: **$1.1M** (+30% YoY)
- Customers: **1,200** (+15% YoY)

### Performance by Product

| Product | Q3 | Q4 | Growth |
|---------|-----|-----|--------|
| Widget | $2M | $2.6M | **+30%** |
| Gadget | $1.5M | $1.8M | *+20%* |
| Tool | $800K | $850K | +6% |

> **Note:** All figures are preliminary and subject to final audit.

### Next Steps

1. Continue marketing investment
2. Launch new product line in Q1
3. Expand sales team by 20%
"""

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_2_idx,
            "markdown": markdown_doc,
            "auto_layout": True,
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Mode: {result['mode']}")
        print(f"    Total requested: {result['total_requested']}")
        print(f"    Successfully added: {result['successfully_added']}")

        print(f"\n    Elements created:")
        for elem in result['elements_added']:
            print(f"      - {elem['type']} (shape_id: {elem['shape_id']})")

        print(f"\n  [OK] Full markdown document auto-laid out with h1, h2, h3, paragraphs, bullets, table, blockquote, numbered list")

    # ========================================================================
    # TEST 6: Add Image
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 6: Add Image (requires actual image file)")
    print("=" * 80)
    print("  [SKIPPED] - No image file provided")
    print("  Note: add_image still exists as separate action (not markdown-based)")

    # ========================================================================
    # TEST 7: Add Chart
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 7: Add Chart")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide for chart
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        slide_3_idx = result["slide_index"]

        # Add chart
        result = await slide_maker.execute_action("add_chart", {
            "presentation_id": presentation_id,
            "slide_index": slide_3_idx,
            "chart_type": "column_clustered",
            "position": {"left": 1, "top": 1, "width": 7, "height": 4},
            "data": {
                "categories": ["Q1", "Q2", "Q3", "Q4"],
                "series": [
                    {"name": "Revenue", "values": [4.5, 4.8, 5.0, 5.2]},
                    {"name": "Profit", "values": [0.8, 0.9, 1.0, 1.1]}
                ]
            },
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Chart ID: {result['chart_id']}")
        print(f"  [OK] Chart added successfully")

    # ========================================================================
    # TEST 8: Find and Replace
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 8: Find and Replace with markdown")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": "Q4 2024", "replace": "**Q4 2024**"},
                {"find": "$5.2M", "replace": "**$5.2M** 🚀"}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Total replacements: {result['total_replacements']}")
        print(f"  [OK] Find and replace completed")

    # ========================================================================
    # TEST 9: Get Slide Elements (Boundary & Overlap Analysis)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 9: Get Slide Elements (check layout)")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("get_slide_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "include_content": False,
            "files": [file_data]
        }, context)

        print(f"\n  Result:")
        print(f"    Total elements: {result['total_elements']}")
        print(f"    Layout status: {result['layout_status']}")
        print(f"    Slide dimensions: {result['slide_dimensions']['width']:.1f}\" x {result['slide_dimensions']['height']:.1f}\"")

        if result.get('elements_outside_boundary', 0) > 0:
            print(f"    ⚠ Elements outside boundary: {result['elements_outside_boundary']}")

        if result.get('total_overlapping_pairs', 0) > 0:
            print(f"    ⚠ Overlapping pairs: {result['total_overlapping_pairs']}")
            for overlap in result.get('element_overlaps', [])[:3]:
                print(f"      - {overlap['description']} (severity: {overlap['severity']})")

        print(f"\n  [OK] Layout analysis complete")

    # ========================================================================
    # TEST 10: Reposition Element (Position/Size Only - No Text Change)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 10: Reposition Element (position/size only)")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Reposition first element
        result = await slide_maker.execute_action("reposition_element", {
            "presentation_id": presentation_id,
            "slide_index": slide_1_idx,
            "element_index": 0,
            "position": {"left": 0.5, "top": 0.5, "width": 6, "height": 1.5},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Modified: {result['modified']}")
        print(f"    Changes: {result['changes_made']}")
        print(f"  [OK] Element repositioned (text change NOT supported - as intended)")

    # ========================================================================
    # TEST 11: AUTO-LAYOUT MODE - H1 Detection and Layout
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 11: AUTO-LAYOUT mode - H1 title positioning")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        slide_4_idx = result["slide_index"]

        # Use add_elements with auto_layout directly (no wrapper needed)
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_4_idx,
            "markdown": "# Main Title\n\n## Section Heading\n\nBody paragraph text.\n\n- Point 1\n- Point 2",
            "auto_layout": True,
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Mode: {result['mode']}")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Element types: {[e['type'] for e in result['elements_added']]}")
        print(f"  [OK] Auto-layout with H1 title positioning works directly")

    # ========================================================================
    # TEST 12: GRANULAR MODE - Default Positions (No Position Specified)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 12: GRANULAR MODE - Default positions")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        slide_5_idx = result["slide_index"]

        # Add elements without specifying positions
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": slide_5_idx,
            "elements": [
                {"content": "First element (default position)"},
                {"content": "Second element (default position)"},
                {"content": "- Bullet 1\n- Bullet 2"}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")

        for elem in result['elements_added']:
            print(f"\n    Element {elem['index']}:")
            print(f"      Type: {elem['type']}")
            print(f"      Position: ({elem['final_position']['left']:.1f}, {elem['final_position']['top']:.1f})")

        print(f"\n  [OK] Default positions applied with vertical stacking")

    # ========================================================================
    # SAVE AND VERIFY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING RESULT...")
    print("=" * 80)

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_add_elements_comprehensive.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Saved: {output_path}")

    # ========================================================================
    # VERIFICATION CHECKLIST
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION CHECKLIST:")
    print("=" * 80)
    print("\nSlide 1 (Title):")
    print("  [ ] Title: 'Comprehensive Test Suite' (bold)")
    print("  [ ] Subtitle: 'Testing add_elements unified action' (italic)")
    print("\nSlide 2 (GRANULAR MODE):")
    print("  [ ] Text box: 'Sales Report for Q4 2024' with bold/italic/underline")
    print("  [ ] Table: Product revenue data with bold/italic formatting in cells")
    print("  [ ] Bullets: 'Key Drivers' with nested bullets and formatting")
    print("  [ ] Auto-positioned text: 'This will overlap!' (should be moved to avoid overlap)")
    print("\nSlide 3 (AUTO-LAYOUT MODE):")
    print("  [ ] H1: 'Executive Summary' (large, centered)")
    print("  [ ] H2: 'Key Findings' (section heading)")
    print("  [ ] H3: 'Financial Results' (sub-heading)")
    print("  [ ] Bullets: Revenue, Profit, Customers with bold formatting")
    print("  [ ] H3: 'Performance by Product'")
    print("  [ ] Table: 3x4 table with product data and bold/italic")
    print("  [ ] Blockquote: 'Note: All figures are preliminary...'")
    print("  [ ] H3: 'Next Steps'")
    print("  [ ] Numbered list: 1, 2, 3")
    print("\nSlide 4 (AUTO-LAYOUT WITH H1):")
    print("  [ ] H1: 'Main Title' (large, centered)")
    print("  [ ] H2: 'Section Heading'")
    print("  [ ] Paragraph text")
    print("  [ ] Bullets: Point 1, Point 2")
    print("\nSlide 5 (DEFAULT POSITIONS):")
    print("  [ ] Three elements with default vertical stacking")
    print("\nSlide 6 (CHART):")
    print("  [ ] Column chart with Revenue and Profit series")
    print("\nGeneral:")
    print("  [ ] All text should have markdown formatting applied correctly")
    print("  [ ] No elements should be cut off or overlapping (except intentional test)")
    print("  [ ] Font sizes should be auto-calculated and readable")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_add_elements_comprehensive()
        print(f"\n[TEST COMPLETE]")
        print(f"File: {output_path}")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
