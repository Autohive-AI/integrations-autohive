# Test the specific template replacement issue
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext
import os
import base64

async def test_template_replacement():
    """
    Test the actual template file with the problematic replacement.
    This will help us see exactly what's in the template and why the replacement fails.
    """
    print("=" * 80)
    print("TEMPLATE REPLACEMENT DEBUG TEST")
    print("=" * 80)

    auth = {}

    # ========================================================================
    # STEP 1: Load the template file
    # ========================================================================
    print("\n[STEP 1] Loading template file...")

    template_path = r"C:\Users\Onil\Downloads\HK Template.pptx"

    if not os.path.exists(template_path):
        print(f"  [ERROR] Template file not found: {template_path}")
        return

    # Read template file and encode as base64
    with open(template_path, "rb") as f:
        template_bytes = f.read()
        template_b64 = base64.b64encode(template_bytes).decode('utf-8')

    file_data = {
        "name": "HK Template.pptx",
        "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "content": template_b64
    }

    print(f"  [OK] Loaded template: {len(template_bytes)} bytes")

    # ========================================================================
    # STEP 2: Create presentation from template
    # ========================================================================
    print("\n[STEP 2] Creating presentation from template...")

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("create_presentation", {
            "files": [file_data],
            "custom_filename": "test_template_debug"
        }, context)
        presentation_id = result["presentation_id"]
        file_data = result["file"]
        print(f"  [OK] Presentation ID: {presentation_id}")
        print(f"  [OK] Slide count: {result['slide_count']}")

    # ========================================================================
    # STEP 3: Get slide elements to see exact content
    # ========================================================================
    print("\n[STEP 3] Getting slide elements with content...")

    async with ExecutionContext(auth=auth) as context:
        # Check each slide for the problematic text
        for slide_idx in range(result['slide_count']):
            result_elem = await slide_maker.execute_action("get_slide_elements", {
                "presentation_id": presentation_id,
                "slide_index": slide_idx,
                "include_content": True,
                "files": [file_data]
            }, context)

            for element in result_elem['elements']:
                if element.get('content') and ('[Detail' in element['content'] or 'scope of work' in element['content']):
                    print(f"\n  Slide {slide_idx}, Element {element['index']}:")
                    print(f"  Type: {element['type']}")
                    print(f"  " + "=" * 76)
                    print(f"\n  EXACT CONTENT (repr):")
                    print(f"  {repr(element['content'])}")
                    print(f"\n  DISPLAY CONTENT:")
                    print(f"  {element['content']}")
                    print()

    # ========================================================================
    # STEP 4: Try the problematic replacement
    # ========================================================================
    print("\n[STEP 4] Testing the problematic replacement...")

    find_text = """[Detail the complete scope of work, including:
• Specific activities and tasks to be performed
• Methodologies and approaches to be used
• Work phases and stages
• Boundaries and exclusions
• Quality standards and success criteria]"""

    replace_text = """The engagement consists of **three comprehensive phases:**

• **Phase 1:** Discovery and stakeholder interviews
• **Phase 2:** Strategy workshop facilitation
• **Phase 3:** Documentation and board presentation

**Methodology:** Collaborative approach combining stakeholder interviews, workshop facilitation, and strategic documentation to deliver actionable transformation roadmap."""

    print(f"  Find string (repr): {repr(find_text[:100])}...")
    print(f"  Find string length: {len(find_text)}")

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": find_text, "replace": replace_text}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Total replacements: {result['total_replacements']}")
        print(f"    Warnings: {result['warnings']}")

        if result['blocked']:
            print(f"\n  Blocked:")
            for block in result['blocked']:
                print(f"    {block.get('BLOCKED', 'Unknown')}")

    # ========================================================================
    # STEP 5: Try simpler replacement (just the start)
    # ========================================================================
    print("\n[STEP 5] Testing simpler replacement (just match start)...")

    find_simple = "[Detail the complete scope of work"

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action("find_and_replace", {
            "presentation_id": presentation_id,
            "replacements": [
                {"find": find_simple, "replace": replace_text}
            ],
            "files": [file_data]
        }, context)
        file_data = result["file"]

        print(f"\n  Result:")
        print(f"    Success: {result['success']}")
        print(f"    Total replacements: {result['total_replacements']}")
        print(f"    Warnings: {result['warnings']}")

    # ========================================================================
    # STEP 6: Save result for inspection
    # ========================================================================
    print("\n[STEP 6] Saving result...")

    output_path = os.path.join(os.path.dirname(__file__), "..", "test_template_debug.pptx")
    file_content = base64.b64decode(file_data["content"])
    with open(output_path, "wb") as f:
        f.write(file_content)

    print(f"  [OK] Saved: {output_path}")

    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    print("\nThe output above shows:")
    print("  1. EXACT text as stored in PowerPoint (with repr())")
    print("  2. Whether the find string matches")
    print("  3. Character encoding differences (\\n vs real newlines, \\u2022 vs •)")
    print("\nIf replacement failed, check:")
    print("  [ ] Are the bullet characters exactly the same?")
    print("  [ ] Are the line breaks \\n or actual newlines?")
    print("  [ ] Is there extra whitespace?")
    print("  [ ] Are there invisible characters?")
    print("=" * 80)

    return output_path

async def main():
    try:
        output_path = await test_template_replacement()
        print(f"\n[TEST COMPLETE]")
        print(f"Output: {output_path}")

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
