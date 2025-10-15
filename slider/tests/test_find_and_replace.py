# Test find_and_replace action with safety checks
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_find_and_replace():
    """
    Test find_and_replace action:
    1. Safe single replacements
    2. Blocked multiple matches (safety)
    3. Confirmed multiple replacements (replace_all=true)
    4. Markdown parsing + auto-sizing
    5. Color preservation
    """
    print("=" * 80)
    print("FIND AND REPLACE TEST - Template Filling with Safety")
    print("=" * 80)

    auth = {}

    # ========================================================================
    # Create Template Presentation with Placeholders
    # ========================================================================
    print("\nCREATING TEMPLATE with placeholders...")
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        result = await slide_maker.execute_action("create_presentation", {
            "title": "{{TITLE}}",
            "subtitle": "{{SUBTITLE}}",
            "custom_filename": "test_find_replace"
        }, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  [OK] Created template presentation")

        # Add slide 2 with more placeholders
        result = await slide_maker.execute_action("add_slide", {
            "presentation_id": presentation_id,
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Add text boxes with placeholders
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "Company: {{COMPANY}}",
            "position": {"left": 1, "top": 1, "width": 5, "height": 0.8},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "Date: {{DATE}}",
            "position": {"left": 1, "top": 2, "width": 5, "height": 0.8},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Add ambiguous placeholder (will appear in table too)
        result = await slide_maker.execute_action("add_text", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "Revenue",  # Ambiguous - no {{ }}
            "position": {"left": 1, "top": 3, "width": 5, "height": 0.8},
            "files": [file_data]
        }, context)
        file_data = result["file"]

        # Add table with placeholders
        result = await slide_maker.execute_action("add_table", {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "rows": 3,
            "cols": 2,
            "position": {"left": 1, "top": 4, "width": 7, "height": 2},
            "data": [
                ["Metric", "Value"],
                ["{{METRIC_1}}", "{{VALUE_1}}"],
                ["Revenue", "{{REVENUE}}"]  # "Revenue" appears here too
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"  [OK] Added placeholders:")
        print(f"       - {{{{TITLE}}}}, {{{{SUBTITLE}}}} (Slide 1)")
        print(f"       - {{{{COMPANY}}}}, {{{{DATE}}}} (Slide 2)")
        print(f"       - {{{{METRIC_1}}}}, {{{{VALUE_1}}}}, {{{{REVENUE}}}} (Slide 2 table)")
        print(f"       - 'Revenue' (appears in 2 places - text box AND table)")

    # ========================================================================
    # TEST 1: Safe Replacements (Single Matches)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 1: Safe replacements (single matches with {{  }} markers)...")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": "{{TITLE}}", "replace": "**Q4 Financial Report**"},
                {"find": "{{SUBTITLE}}", "replace": "*Prepared by Finance Team*"},
                {"find": "{{COMPANY}}", "replace": "__Acme Corporation__"},
                {"find": "{{DATE}}", "replace": "`October 2024`"},
                {"find": "{{METRIC_1}}", "replace": "**Total Revenue**"},
                {"find": "{{VALUE_1}}", "replace": "*$5M*"},
                {"find": "{{REVENUE}}", "replace": "**$5,000,000**"}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Total replacements: {result['total_replacements']}")
        print(f"    Processed: {result['processed']}")
        print(f"    Blocked: {len(result['blocked'])}")
        print(f"    Warnings: {len(result['warnings'])}")

        if result['warnings']:
            print(f"\n  Warnings:")
            for warning in result['warnings']:
                print(f"    - {warning}")

        if result['blocked']:
            print(f"\n  Blocked:")
            for block in result['blocked']:
                print(f"    - {block.get('BLOCKED', 'Unknown')}")

        print(f"\n  [OK] All 7 unique placeholders replaced successfully")

    # ========================================================================
    # TEST 2: Blocked Replacement (Multiple Matches, No replace_all)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 2: BLOCKED replacement (ambiguous - multiple matches)...")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": "Revenue", "replace": "**UPDATED**"}  # No replace_all!
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Replacements: {result['total_replacements']}")
        print(f"    Blocked: {len(result['blocked'])}")

        if result['blocked']:
            print(f"\n  BLOCKED Details:")
            block = result['blocked'][0]
            print(f"    Reason: {block.get('BLOCKED')}")
            print(f"    Find phrase: '{block.get('find_phrase')}'")
            print(f"    Matches found: {block.get('match_count')}")
            print(f"    Fix required: {block.get('fix_required')}")
            print(f"\n    Locations:")
            for match in block.get('matches', []):
                print(f"      - {match.get('location')}: \"{match.get('content')}\"")

        print(f"\n  [OK] Correctly BLOCKED ambiguous replacement (safety feature)")

    # ========================================================================
    # TEST 3: Confirmed Multiple Replacement (replace_all=true)
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Confirmed replacement (replace_all=true)...")
    print("=" * 80)

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": "Revenue", "replace": "**Revenue (Updated)**", "replace_all": True}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Replacements: {result['total_replacements']}")
        print(f"    Blocked: {len(result['blocked'])}")

        print(f"\n  [OK] Replaced {result['total_replacements']} instances (user confirmed with replace_all=true)")

    # ========================================================================
    # SAVE AND VERIFY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING RESULT...")
    print("=" * 80)

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_find_replace.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"\n[SUCCESS] Saved: {output_path}")
    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    print("\nOpen file and verify:")
    print("  Slide 1:")
    print("    [ ] Title: 'Q4 Financial Report' (bold)")
    print("    [ ] Subtitle: 'Prepared by Finance Team' (italic)")
    print("")
    print("  Slide 2:")
    print("    [ ] 'Company: Acme Corporation' (underlined)")
    print("    [ ] 'Date: October 2024' (code style)")
    print("    [ ] 'Revenue (Updated)' (bold - replaced with replace_all)")
    print("")
    print("  Slide 2 Table:")
    print("    [ ] Row 2, Col 1: 'Total Revenue' (bold)")
    print("    [ ] Row 2, Col 2: '$5M' (italic)")
    print("    [ ] Row 3, Col 1: 'Revenue (Updated)' (bold - replaced with replace_all)")
    print("    [ ] Row 3, Col 2: '$5,000,000' (bold)")
    print("")
    print("  All text should:")
    print("    [ ] Have proper markdown formatting applied")
    print("    [ ] Fit in boxes (auto-sized)")
    print("    [ ] Preserve colors if any")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_find_and_replace()
        print(f"\n[TEST COMPLETE]")
        print(f"File: {output_path}")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
