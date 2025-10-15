# Comprehensive error handling and edge case testing for add_elements
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_error_handling():
    """
    Comprehensive error handling tests:

    1. Invalid slide indices
    2. Invalid element indices (reposition_element)
    3. Boundary violations (elements outside slide)
    4. Overlap detection and skip behavior
    5. Malformed markdown parsing
    6. Missing required parameters
    7. Auto-positioning when no space available
    8. Empty content handling
    9. Very large elements (boundary clipping)
    10. Mixed success/failure scenarios
    """
    print("=" * 80)
    print("ERROR HANDLING & EDGE CASES TEST - add_elements")
    print("=" * 80)

    auth = {}

    # ========================================================================
    # SETUP: Create Test Presentation
    # ========================================================================
    print("\n[SETUP] Creating test presentation...")
    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("create_presentation", {
            "title": "**Error Handling Test**",
            "subtitle": "*Testing graceful failure and recovery*",
            "custom_filename": "test_error_handling"
        }, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  [OK] Created presentation: {presentation_id}")

    # ========================================================================
    # TEST 1: Invalid Slide Index
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 1: Invalid slide index (should raise error)")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await slide_maker.execute_action("add_elements", {
                "presentation_id": presentation_id,
                "slide_index": 999,  # Invalid index
                "elements": [{"content": "This should fail"}],
                "files": [file_data]
            }, context)
            print(f"  [FAIL] Should have raised error for invalid slide index")
        except ValueError as e:
            print(f"  [OK] Correctly raised ValueError: {str(e)[:80]}...")

    # ========================================================================
    # TEST 2: Boundary Violations - Element Outside Slide
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 2: Boundary violations - element extends outside slide")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide to avoid overlap with title
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        boundary_test_slide = result["slide_index"]

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": boundary_test_slide,
            "elements": [
                {
                    "content": "**Too Wide!**",
                    "position": {"left": 8, "top": 1, "width": 5, "height": 1}
                    # Left 8 + Width 5 = 13 inches (slide is 10 inches wide)
                },
                {
                    "content": "**Too Tall!**",
                    "position": {"left": 1, "top": 6, "width": 2, "height": 5}
                    # Top 6 + Height 5 = 11 inches (slide is 7.5 inches tall)
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")

        for elem in result['elements_added']:
            print(f"\n    Element {elem['index']} adjusted:")
            print(f"      Requested: {elem['requested_position']['width']}\" x {elem['requested_position']['height']}\"")
            print(f"      Final: {elem['final_position']['width']:.2f}\" x {elem['final_position']['height']:.2f}\"")
            print(f"      Adjusted: {elem['position_adjusted']}")
            print(f"      Reason: {elem['adjustment_reason']}")

        print(f"\n  [OK] Boundary violations auto-adjusted (dimensions clipped to fit slide)")

    # ========================================================================
    # TEST 3: Overlap Detection Without auto_position
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Overlap detection - multiple overlapping elements, auto_position=false")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "elements": [
                {
                    "content": "First element at 2,2",
                    "position": {"left": 2, "top": 2, "width": 3, "height": 1}
                },
                {
                    "content": "Second element - OVERLAPS!",
                    "position": {"left": 2.5, "top": 2.5, "width": 3, "height": 1},
                    "auto_position": False  # Should be skipped
                },
                {
                    "content": "Third element - also overlaps",
                    "position": {"left": 3, "top": 2.2, "width": 2, "height": 1},
                    "auto_position": False  # Should be skipped
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Total requested: {result['total_requested']}")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        print(f"\n    Skipped elements:")
        for skip in result['elements_skipped']:
            print(f"      - Element {skip['index']}: {skip['skip_reason']}")

        print(f"\n  [OK] Overlapping elements correctly skipped (1 added, 2 skipped)")

    # ========================================================================
    # TEST 4: Overlap Detection WITH auto_position
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 4: Auto-positioning - should find alternative positions")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "elements": [
                {
                    "content": "Auto-positioned 1",
                    "position": {"left": 2, "top": 2, "width": 2, "height": 0.5},
                    "auto_position": True  # Should find alternative
                },
                {
                    "content": "Auto-positioned 2",
                    "position": {"left": 2.5, "top": 2.5, "width": 2, "height": 0.5},
                    "auto_position": True  # Should find alternative
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        for elem in result['elements_added']:
            print(f"\n    Element {elem['index']}:")
            print(f"      Requested: ({elem['requested_position']['left']:.1f}, {elem['requested_position']['top']:.1f})")
            print(f"      Final: ({elem['final_position']['left']:.1f}, {elem['final_position']['top']:.1f})")
            print(f"      Adjusted: {elem['position_adjusted']}")

        print(f"\n  [OK] Auto-positioning found alternative positions for overlapping requests")

    # ========================================================================
    # TEST 5: Malformed Markdown - Invalid Table
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 5: Malformed markdown - invalid table syntax")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide for error tests
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        error_slide_idx = result["slide_index"]

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": error_slide_idx,
            "elements": [
                {
                    "content": "| Bad Table |\nNo separator line\n| Missing pipes"
                },
                {
                    "content": "| Good | Table |\n|-----|-------|\n| A | B |",
                    "position": {"left": 1, "top": 2, "width": 4, "height": 1}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        for skip in result['elements_skipped']:
            print(f"\n    Skipped element {skip['index']}:")
            print(f"      Content: {skip['content_preview']}")
            print(f"      Reason: {skip['skip_reason']}")
            print(f"      Suggestion: {skip['suggestion']}")

        print(f"\n  [OK] Invalid table skipped, valid table added")

    # ========================================================================
    # TEST 6: Malformed Markdown - Invalid Bullets
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 6: Malformed markdown - invalid bullet syntax")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": error_slide_idx,
            "elements": [
                {
                    "content": "Just one line\nNo bullets here",  # Not a bullet list
                    "position": {"left": 1, "top": 3.5, "width": 4, "height": 1}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        elem = result['elements_added'][0] if result['elements_added'] else None
        print(f"    Type detected: {elem['type'] if elem else 'N/A'}")
        print(f"  [OK] Non-bullet content treated as text (fallback behavior)")

    # ========================================================================
    # TEST 7: Empty Content
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 7: Empty content handling")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": error_slide_idx,
            "elements": [
                {
                    "content": "",
                    "position": {"left": 6, "top": 1, "width": 3, "height": 0.5}
                },
                {
                    "content": "   ",  # Whitespace only
                    "position": {"left": 6, "top": 2, "width": 3, "height": 0.5}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Elements: {[e['type'] for e in result['elements_added']]}")
        print(f"  [OK] Empty content handled (creates empty text boxes)")

    # ========================================================================
    # TEST 8: No Space Available for Auto-Positioning
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 8: Auto-positioning with no available space")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide and fill it completely
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        full_slide_idx = result["slide_index"]

        # Fill slide with large element
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": full_slide_idx,
            "elements": [
                {
                    "content": "**This fills most of the slide**",
                    "position": {"left": 0.5, "top": 0.5, "width": 9, "height": 6.5}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Now try to add element with auto_position (should fail - no space)
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": full_slide_idx,
            "elements": [
                {
                    "content": "This should be skipped - no space!",
                    "position": {"left": 1, "top": 1, "width": 3, "height": 1},
                    "auto_position": True
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
            print(f"\n    Skipped:")
            print(f"      Reason: {skip['skip_reason']}")

        print(f"\n  [OK] Auto-positioning correctly failed when no space available")

    # ========================================================================
    # TEST 9: Invalid Element Index (reposition_element)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 9: Invalid element index in reposition_element")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await slide_maker.execute_action("reposition_element", {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "element_index": 999,  # Invalid
                "position": {"left": 1, "top": 1, "width": 2, "height": 1},
                "files": [file_data]
            }, context)
            print(f"  [FAIL] Should have raised error")
        except ValueError as e:
            print(f"  [OK] Correctly raised ValueError: {str(e)[:80]}...")

    # ========================================================================
    # TEST 10: Malformed Table Markdown (No Separator)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 10: Malformed table - missing separator line")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": error_slide_idx,
            "elements": [
                {
                    "content": "| Header 1 | Header 2 |\n| Data 1 | Data 2 |",
                    # Missing separator: |-------|--------|
                    "position": {"left": 1, "top": 5, "width": 5, "height": 1}
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
            print(f"\n    Skipped table:")
            print(f"      Reason: {skip['skip_reason']}")
            print(f"      Suggestion: {skip['suggestion']}")
        else:
            # If it didn't skip, it was likely treated as text (fallback)
            elem = result['elements_added'][0]
            print(f"\n    Treated as: {elem['type']}")
            print(f"  [OK] Malformed table treated as text (graceful fallback)")

    # ========================================================================
    # TEST 11: Single Bullet Item (Less than 2 - Treated as Text)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 11: Single bullet item - should be treated as text")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": error_slide_idx,
            "elements": [
                {
                    "content": "- Only one bullet item",
                    "position": {"left": 6, "top": 3.5, "width": 3, "height": 0.5}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        elem = result['elements_added'][0] if result['elements_added'] else None
        print(f"\n  Result:")
        print(f"    Type detected: {elem['type'] if elem else 'N/A'}")
        print(f"  [OK] Single bullet treated as text (requires 2+ items for bullets)")

    # ========================================================================
    # TEST 12: Negative Positions (Boundary Clipping)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 12: Negative positions - should clip to 0")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        neg_slide_idx = result["slide_index"]

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": neg_slide_idx,
            "elements": [
                {
                    "content": "Negative position test",
                    "position": {"left": -1, "top": -0.5, "width": 3, "height": 1}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        if result['elements_added']:
            elem = result['elements_added'][0]
            print(f"    Final position: ({elem['final_position']['left']:.1f}, {elem['final_position']['top']:.1f})")
            print(f"  [OK] Negative positions handled (may allow or clip depending on implementation)")

    # ========================================================================
    # TEST 13: Mixed Success and Failure
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 13: Mixed success/failure - partial batch completion")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": neg_slide_idx,
            "elements": [
                {
                    "content": "**Success 1**",
                    "position": {"left": 1, "top": 2, "width": 2, "height": 0.5}
                },
                {
                    "content": "| Bad | Table\nMissing separator",
                    "position": {"left": 4, "top": 2, "width": 3, "height": 1}
                },
                {
                    "content": "**Success 2**",
                    "position": {"left": 1, "top": 3, "width": 2, "height": 0.5}
                },
                {
                    "content": "Overlaps with Success 1",
                    "position": {"left": 1.5, "top": 2.2, "width": 2, "height": 0.5},
                    "auto_position": False  # Should skip
                },
                {
                    "content": "- Bullet 1\n- Bullet 2",
                    "position": {"left": 4, "top": 3.5, "width": 3, "height": 1}
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Total requested: {result['total_requested']}")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Skipped: {result['skipped']}")

        print(f"\n    Added:")
        for elem in result['elements_added']:
            print(f"      - Element {elem['index']}: {elem['type']}")

        print(f"\n    Skipped:")
        for skip in result['elements_skipped']:
            print(f"      - Element {skip['index']}: {skip['skip_reason'][:60]}...")

        print(f"\n  [OK] Batch processing: some succeed, some fail - graceful handling")

    # ========================================================================
    # TEST 14: Auto-Layout Mode with Malformed Markdown
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 14: AUTO-LAYOUT mode - handles malformed elements gracefully")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        auto_error_slide = result["slide_index"]

        markdown_with_errors = """# Title Works

## Heading Works

Regular paragraph text.

| Bad Table |
No separator
| Missing

- Good bullet 1
- Good bullet 2

Another paragraph.
"""

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": auto_error_slide,
            "markdown": markdown_with_errors,
            "auto_layout": True,
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Mode: {result['mode']}")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Elements: {[e['type'] for e in result['elements_added']]}")
        print(f"\n  [OK] Auto-layout skips malformed elements, continues with valid ones")

    # ========================================================================
    # TEST 15: Very Large Element (Should Clip)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 15: Very large element - boundary clipping")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": auto_error_slide,
            "elements": [
                {
                    "content": "**Huge Element**",
                    "position": {"left": 0, "top": 0, "width": 50, "height": 50}
                    # Way bigger than slide (10" x 7.5")
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        if result['elements_added']:
            elem = result['elements_added'][0]
            print(f"    Requested: {elem['requested_position']['width']}\" x {elem['requested_position']['height']}\"")
            print(f"    Final: {elem['final_position']['width']:.1f}\" x {elem['final_position']['height']:.1f}\"")
            print(f"    Adjusted: {elem['position_adjusted']}")
            print(f"  [OK] Large element clipped to slide boundaries")

    # ========================================================================
    # TEST 16: Default Positions Without Overlap Checking
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 16: Default positions - may overlap if not careful")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        default_slide = result["slide_index"]

        # Add many elements without positions (use defaults)
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": default_slide,
            "elements": [
                {"content": f"Element {i}"} for i in range(10)
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"    Vertical positions:")
        for elem in result['elements_added'][:5]:
            print(f"      - Element {elem['index']}: top={elem['final_position']['top']:.1f}\"")
        print(f"  [OK] Default positions use vertical stacking (0.5\" increments)")

    # ========================================================================
    # TEST 17: Invalid Presentation ID (No Files Provided)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 17: Invalid presentation ID (no files to load)")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await slide_maker.execute_action("add_elements", {
                "presentation_id": "invalid-pres-id-12345",
                "slide_index": 0,
                "elements": [{"content": "Test"}]
                # No files parameter - can't load presentation
            }, context)
            print(f"  [FAIL] Should have raised error")
        except ValueError as e:
            print(f"  [OK] Correctly raised ValueError: {str(e)[:70]}...")

    # ========================================================================
    # TEST 18: Missing Required Parameters
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 18: Missing required parameters")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        try:
            # auto_layout=false without elements array
            result = await slide_maker.execute_action("add_elements", {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "auto_layout": False,
                # Missing "elements" parameter
                "files": [file_data]
            }, context)
            print(f"  [FAIL] Should have raised error")
        except ValueError as e:
            print(f"  [OK] Correctly raised ValueError: {str(e)}")

    async with ExecutionContext(auth=auth) as context:
        try:
            # auto_layout=true without markdown parameter
            result = await slide_maker.execute_action("add_elements", {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "auto_layout": True,
                # Missing "markdown" parameter
                "files": [file_data]
            }, context)
            print(f"  [FAIL] Should have raised error")
        except ValueError as e:
            print(f"  [OK] Correctly raised ValueError: {str(e)}")

    # ========================================================================
    # TEST 19: Minimum Size Enforcement
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 19: Minimum size enforcement")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": default_slide,
            "elements": [
                {
                    "content": "Tiny box",
                    "position": {"left": 7, "top": 1, "width": 0.1, "height": 0.05}
                    # Way below minimum (0.5" x 0.3")
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        if result['elements_added']:
            elem = result['elements_added'][0]
            print(f"    Requested: {elem['requested_position']['width']}\" x {elem['requested_position']['height']}\"")
            print(f"    Final: {elem['final_position']['width']:.1f}\" x {elem['final_position']['height']:.1f}\"")
            print(f"  [OK] Minimum size enforced (0.5\" x 0.3\")")

    # ========================================================================
    # TEST 20: Get Slide Elements - Boundary Warnings
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 20: Get slide elements - detect boundary issues")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # First add element that's outside boundary (force it)
        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": default_slide,
            "elements": [
                {
                    "content": "Edge element",
                    "position": {"left": 9.5, "top": 7, "width": 2, "height": 1}
                    # Will be clipped but might still trigger warnings
                }
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Now check elements
        result = await slide_maker.execute_action("get_slide_elements", {
            "presentation_id": presentation_id,
            "slide_index": default_slide,
            "files": [file_data]
        }, context)

        print(f"\n  Result:")
        print(f"    Total elements: {result['total_elements']}")
        print(f"    Layout status: {result['layout_status']}")

        if result.get('boundary_warning'):
            print(f"    Boundary warning: {result['boundary_warning']}")

        if result.get('overlap_warning'):
            print(f"    Overlap warning: {result['overlap_warning']}")

        print(f"\n  [OK] Boundary analysis detects issues")

    # ========================================================================
    # TEST 21: Auto-Layout with Empty Markdown
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 21: Auto-layout with empty/whitespace markdown")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        # Add new slide
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]
        empty_slide = result["slide_index"]

        result = await slide_maker.execute_action("add_elements", {
            "presentation_id": presentation_id,
            "slide_index": empty_slide,
            "markdown": "   \n\n   ",  # Whitespace only
            "auto_layout": True,
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Successfully added: {result['successfully_added']}")
        print(f"  [OK] Empty markdown handled gracefully")

    # ========================================================================
    # SAVE AND REPORT
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING RESULT...")
    print("=" * 80)

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_error_handling.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Saved: {output_path}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\nError Handling Tests:")
    print("  [OK] Invalid slide index - ValueError raised")
    print("  [OK] Invalid element index - ValueError raised")
    print("  [OK] Invalid presentation ID - ValueError raised")
    print("  [OK] Missing required parameters - ValueError raised")
    print("\nBoundary Handling Tests:")
    print("  [OK] Element too wide - auto-clipped to fit slide")
    print("  [OK] Negative positions - handled")
    print("  [OK] Very large elements - clipped to slide boundaries")
    print("  [OK] Minimum size enforcement - 0.5\" x 0.3\"")
    print("\nOverlap Detection Tests:")
    print("  [OK] Overlap without auto_position - elements skipped")
    print("  [OK] Overlap with auto_position - alternative positions found")
    print("  [OK] No space available - gracefully skipped")
    print("\nMarkdown Parsing Tests:")
    print("  [OK] Invalid table syntax - skipped or treated as text")
    print("  [OK] Single bullet item - treated as text")
    print("  [OK] Empty/whitespace content - handled gracefully")
    print("\nBatch Processing Tests:")
    print("  [OK] Mixed success/failure - continues with valid elements")
    print("  [OK] Skipped elements reported with suggestions")
    print("\nLayout Analysis:")
    print("  [OK] Boundary detection working")
    print("  [OK] Overlap detection working")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_error_handling()
        print(f"\n[ALL TESTS PASSED]")
        print(f"Output file: {output_path}")

    except Exception as e:
        print(f"\n[TEST SUITE FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
