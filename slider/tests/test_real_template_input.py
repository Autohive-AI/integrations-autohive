"""
Test with HK Template Real.pptx using actual agent input.
Verifies template-aware scaling with real template file.
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


async def test_real_template():
    """Test with HK Template Real.pptx"""

    print("=" * 70)
    print("REAL TEMPLATE TEST - DEBUG MODE")
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
        print("\n3. Executing find_and_replace (16 replacements)...")
        print("=" * 70)

        replacements = [
            {"find": "[Goal of the work]", "replace": "Digital Transformation Strategy and Roadmap Development"},
            {"find": "[Date / 13 October 2025]", "replace": "September 30, 2025"},
            {"find": "[COMPANY]", "replace": "TechVenture Solutions"},
            {"find": "[PARTNERSHIP]", "replace": "Digital Transformation Consulting"},
            {"find": "[GOALS]", "replace": "you are seeking to modernize technology infrastructure and improve customer experience platforms through comprehensive digital transformation"},
            {"find": "[Partnership name]", "replace": "Digital Transformation Strategy"},
            {"find": "[Other option name]", "replace": "Implementation Support Services"},
            {"find": "[description of option]", "replace": "Ongoing support during implementation phases including stakeholder coordination, progress monitoring, and strategic guidance to ensure successful execution of the digital transformation roadmap"},
            {"find": "[Clients Challenge]", "replace": "TechVenture Solutions' Digital Transformation Challenge"},
            {"find": "Problem definition\n- Explicitly state client's core issues\n- Use client's own language\n- Quantify potential business impact\n- Link problems to strategic objectives", "replace": "**Current State Challenges**\n- Legacy technology infrastructure limiting growth potential\n- Disconnected systems impacting operational efficiency\n- Customer experience platforms requiring modernization\n- Need for strategic roadmap to guide digital transformation\n- Executive alignment required on transformation priorities"},
            {"find": "Proposed Solution\n- Concise, outcome-focused approach\n- Direct mapping to client's specific challenges\n- Clear value proposition\n- Minimal industry jargon", "replace": "**Our Three-Phase Approach**\n- **Phase 1**: Discovery & stakeholder interviews to understand current state\n- **Phase 2**: Collaborative strategy workshop to co-create transformation roadmap\n- **Phase 3**: Comprehensive documentation and board presentation\n- Clear timeline: October 14 - November 15, 2025\n- Executive-ready deliverables and strategic recommendations"},
            {"find": "[$x,xxx]", "replace": "$57,000"},
            {"find": "[Name | Title]", "replace": "Emma Patterson | Senior Consultant"},
            {"find": "[email@humankind.nz]", "replace": "emma.patterson@humankind.co.nz"},
            {"find": "[Phone Contact]", "replace": "Contact via email for project coordination"},
            {"find": "CLIENT", "replace": "TechVenture Solutions", "replace_all": True}
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
        if result['warnings']:
            print(f"[WARN] Warnings: {len(result['warnings'])}")

        files = [result["file"]]

        # Get final state
        print("\n4. Analyzing final result...")
        final_state = await slide_maker.execute_action(
            "get_slide_elements",
            {
                "presentation_id": presentation_id,
                "files": files
            },
            context
        )

        print(f"\n   Summary:")
        print(f"   - Total slides: {final_state['total_slides']}")
        print(f"   - Total elements: {final_state['total_elements']}")
        print(f"   - Slides with issues: {final_state['slides_with_issues']}")

        # Save output
        import time
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_real_template_output_{int(time.time())}.pptx"
        )

        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"\n5. Saved to: {output_path}")

        print("\n" + "=" * 70)
        print("[SUCCESS] REAL TEMPLATE TEST COMPLETE!")
        print("=" * 70)
        print("\nREVIEW CHECKLIST:")
        print("  1. Text respects placeholder font sizes (not too big)")
        print("  2. No text overflow (not cut off)")
        print("  3. Boxes don't resize themselves")
        print("  4. Fill rates shown in debug output")
        print("  5. Template design integrity maintained")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_real_template())
