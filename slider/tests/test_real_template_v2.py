"""
Test HK Template Real.pptx with second agent input.
Tests form-filling with actual agent replacements.
"""

import asyncio
import sys
import os
import base64

# ENABLE DEBUG MODE
os.environ['FONT_SIZE_DEBUG'] = 'true'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_real_template_v2():
    """Test with HK Template Real.pptx - Agent Input V2"""

    print("=" * 70)
    print("REAL TEMPLATE TEST V2 - DEBUG MODE")
    print("=" * 70)

    auth = {}

    # Load HK Template Real.pptx
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "HK Template Real.pptx"
    )

    if not os.path.exists(template_path):
        print(f"\n[ERROR] Template not found at: {template_path}")
        return

    print(f"\n1. Loading template: {template_path}")
    with open(template_path, 'rb') as f:
        template_content = base64.b64encode(f.read()).decode('utf-8')

    files = [{
        "name": "HK Template Real.pptx",
        "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "content": template_content
    }]

    async with ExecutionContext(auth=auth) as context:
        print("\n2. Creating presentation with template...")
        result = await slide_maker.execute_action(
            "create_presentation",
            {"files": files},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]
        print(f"   [OK] Presentation created: {presentation_id}")

        # Execute find_and_replace with exact agent input
        print("\n3. Executing find_and_replace (14 replacements)...")
        print("=" * 70)

        replacements = [
            {"find": "[Date / 13 October 2025]", "replace": "30 September 2025", "replace_all": False},
            {"find": "[Goal of the work]", "replace": "Digital Transformation Strategy and Roadmap Development", "replace_all": False},
            {"find": "[COMPANY]", "replace": "TechVenture Solutions Limited", "replace_all": True},
            {"find": "[PARTNERSHIP]", "replace": "digital transformation", "replace_all": False},
            {"find": "[GOALS]", "replace": "you're looking to develop a comprehensive digital transformation roadmap, including stakeholder interviews, current state assessment, and strategic recommendations to modernize technology infrastructure and improve customer experience platforms.", "replace_all": False},
            {"find": "[Partnership name]", "replace": "Digital Transformation Strategy", "replace_all": False},
            {"find": "[Other option name]", "replace": "Extended Implementation Support", "replace_all": False},
            {"find": "[description of option]", "replace": "Additional hands-on support for implementing the transformation roadmap recommendations, including change management and technology rollout assistance.", "replace_all": False},
            {"find": "[Clients Challenge]", "replace": "TechVenture Solutions' Digital Transformation Challenge", "replace_all": False},
            {"find": "[$x,xxx]", "replace": "$61,190 (excluding GST) / $70,368.50 (including GST)", "replace_all": False},
            {"find": "[Name | Title]", "replace": "Emma Patterson | Senior Consultant", "replace_all": False},
            {"find": "[email@humankind.nz]", "replace": "emma.patterson@humankind.co.nz", "replace_all": False},
            {"find": "[Phone Contact]", "replace": "Contact via email for phone consultation", "replace_all": False},
            {"find": "CLIENT", "replace": "TechVenture Solutions Limited", "replace_all": True}
        ]

        result = await slide_maker.execute_action(
            "find_and_replace",
            {
                "presentation_id": presentation_id,
                "replacements": replacements,
                "files": files
            },
            context
        )

        print("=" * 70)
        print(f"\n[OK] Total replacements made: {result['total_replacements']}")
        print(f"[OK] Processed: {result['processed']}")
        if result['blocked']:
            print(f"[WARN] Blocked: {len(result['blocked'])}")
            for blocked in result['blocked']:
                print(f"  - {blocked.get('find_phrase')}: {blocked.get('BLOCKED')}")
        if result['warnings']:
            print(f"[INFO] Warnings: {len(result['warnings'])}")
            for warning in result['warnings']:
                print(f"  - {warning}")

        files = [result["file"]]

        # Save output
        import time
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_real_v2_output_{int(time.time())}.pptx"
        )

        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"\n4. Saved to: {output_path}")

        print("\n" + "=" * 70)
        print("[SUCCESS] REAL TEMPLATE V2 TEST COMPLETE!")
        print("=" * 70)
        print("\nVERIFY IN OUTPUT FILE:")
        print("  1. Bullets are preserved and visible")
        print("  2. Text fills space appropriately")
        print("  3. No overflow or cut-off text")
        print("  4. Font sizes respect placeholder sizes")
        print("  5. Template structure maintained")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_real_template_v2())
