"""
DEBUG VERSION - Replicate agent input with full debugging enabled.
Shows which sizing method is used and calculation details.
"""

import asyncio
import sys
import os
import base64

# ENABLE DEBUG MODE
os.environ['FONT_SIZE_DEBUG'] = 'true'

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_agent_input_debug():
    """Replicate agent's exact find_and_replace input WITH DEBUG"""

    print("=" * 70)
    print("AGENT INPUT REPLICATION - DEBUG MODE ENABLED")
    print("=" * 70)
    print("\nThis will show detailed calculations for EVERY text box")
    print("Look for:")
    print("  - [PILLOW] = Using Pillow measurement (accurate)")
    print("  - [HEURISTIC] = Using heuristic fallback (less accurate)")
    print("  - WARNING messages = Text doesn't fit even at minimum size")
    print("=" * 70)

    auth = {}

    # Load HK Template.pptx
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "HK Template.pptx"
    )

    if not os.path.exists(template_path):
        print(f"\n[ERROR] Template not found at: {template_path}")
        return

    print(f"\n1. Loading template: {template_path}")
    with open(template_path, 'rb') as f:
        template_content = base64.b64encode(f.read()).decode('utf-8')

    files = [{
        "name": "HK Template.pptx",
        "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "content": template_content
    }]

    async with ExecutionContext(auth=auth) as context:
        # Create presentation with template
        print("\n2. Creating presentation with template...")
        result = await slide_maker.execute_action(
            "create_presentation",
            {"files": files},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]
        print(f"   [OK] Presentation created: {presentation_id}")

        # Execute the exact find_and_replace operation from agent
        print("\n3. Executing find_and_replace with DEBUG enabled...")
        print("=" * 70)
        replacements = [
            {"find": "[Project Title]", "replace": "**Digital Transformation Strategy and Roadmap Development**"},
            {"find": "[Provide a brief overview of the project]", "replace": "**Project Name:** Digital Transformation Strategy and Roadmap Development\n\n**Objective:** Develop a comprehensive digital transformation roadmap for TechVenture Solutions, including stakeholder interviews, current state assessment, and strategic recommendations to modernize technology infrastructure and improve customer experience platforms.\n\n**Project Duration:** October 14, 2025 - November 15, 2025\n\n**Lead Consultant:** Emma Patterson\n\n**Client:** TechVenture Solutions Limited\n**Primary Contact:** David Walsh, CEO"},
            {"find": "[Detail the complete scope of work]", "replace": "The engagement consists of **three comprehensive phases**:\n\n**PHASE 1: DISCOVERY AND INTERVIEWS**\n- Preparation and development of interview guides\n- Coordination and scheduling of stakeholder interviews  \n- Conduct 8 one-hour interviews with executive team and department heads\n- Preliminary analysis of interview findings\n\n**PHASE 2: STRATEGY WORKSHOP FACILITATION**\n- Workshop design and preparation\n- Two-day intensive strategy workshop with leadership team\n- Facilitation of collaborative strategy development sessions\n- Synthesis of interview findings\n- Co-creation of transformation roadmap\n\n**PHASE 3: DOCUMENTATION AND BOARD PRESENTATION**\n- Development of comprehensive strategy document\n- Creation of visual transformation roadmap\n- Preparation of board presentation materials\n- Delivery of 90-minute board presentation"},
            {"find": "PHASE 1: [PHASE-p1 NAME]\n[Start Date-p1] - [End Date-p1]", "replace": "PHASE 1: **DISCOVERY AND INTERVIEWS**\n**October 14-21, 2025**"},
            {"find": "[List key activities for phase 1]", "replace": "• **Preparation and development of interview guides**\n• **Coordination and scheduling of stakeholder interviews**\n• **Conduct 8 one-hour interviews** with executive team and department heads:\n  - David Walsh (CEO)\n  - Lisa Martinez (Head of Product)\n  - James Chen (CTO)\n  - Sarah Thompson (CFO)\n  - Marcus Brown (Head of Sales)\n  - Rachel Kim (Head of Customer Service)\n  - Tom Rodriguez (Head of IT Operations)\n  - Jessica Wu (Head of Marketing)\n• **Preliminary analysis of interview findings**\n\n**Interview Schedule:** October 14-18, 2025 (9am - 5pm each day)"},
            {"find": "PHASE 2: [PHASE NAME-p2]\n[Start Date-p2] - [End Date-p2]", "replace": "PHASE 2: **STRATEGY WORKSHOP FACILITATION**\n**October 28-29, 2025**"},
            {"find": "[Phase 2 Details here]", "replace": "**Activities:**\n• Workshop design and preparation\n• Two-day intensive strategy workshop with leadership team\n• Facilitation of collaborative strategy development sessions\n• Synthesis of interview findings\n• Co-creation of transformation roadmap\n\n**Workshop Details:**\n• **Date:** October 28-29, 2025 (2 full days)\n• **Participants:** 12 leadership team members\n• **Location:** TechVenture Solutions offices, Wellington"},
            {"find": "PHASE 3: [PHASE NAME-p3]\n[Start Date-p3] - [End Date-p3]", "replace": "PHASE 3: **DOCUMENTATION AND BOARD PRESENTATION**\n**October 30 - November 15, 2025**"},
            {"find": "[Deliverable 1]\n[Deliverable 2]\n[Deliverable 3]\n[Deliverable 4]", "replace": "• **Comprehensive digital transformation strategy document**\n• **Visual transformation roadmap**\n• **Board presentation materials**\n• **90-minute board presentation** on November 15, 2025"},
            {"find": "[Requirement 1]\n[Requirement 2]\n[Requirement 3]\n[Requirement 4]", "replace": "• **Boardroom with presentation facilities** including screen and projector or large monitor\n• **Video conferencing capability** (for remote board members)\n• **Availability of board members** on November 15, 2025\n• **Timely feedback and approvals** throughout the documentation phase"},
            {"find": "[KMDate1] - [KMilestone1 description]\n[KMDate2] - [KMilestone2 description]\n[KMDate3] - [KMilestone3 description]", "replace": "**October 7, 2025** - Client confirms interviewee availability\n**October 14-18, 2025** - Stakeholder interviews conducted\n**October 21, 2025** - Phase 1 complete / Invoice 1 issued"},
            {"find": "[DateAM1] - [AMilestone1 description]\n[DateAM2] - [AMilestone2 description]\n[DateAM3] - [AMilestone3 description]\n[DateAM4] - [AMilestone4 description]", "replace": "**October 28-29, 2025** - Two-day strategy workshop\n**November 1, 2025** - Phase 2 complete / Invoice 2 issued\n**November 15, 2025** - Board presentation delivered\n**November 18, 2025** - Phase 3 complete / Invoice 3 issued"},
            {"find": "[Phase 1 Description] - $[Amount-P1]\n[Phase 2 Description] - $[Amount-P2]\n[Phase 3 Description] - $[Amount-P3]", "replace": "**Discovery and Interviews** - **$18,500**\n(Includes preparation, 8 stakeholder interviews, coordination, and initial analysis)\n\n**Strategy Workshop Facilitation** - **$22,000**\n(Includes workshop design, two-day facilitation, materials provided by Consultant)\n\n**Documentation and Board Presentation** - **$16,500**\n(Includes strategy document, visual roadmap, presentation materials and delivery)"},
            {"find": "[Describe anticipated travel/expense costs for the project]", "replace": "**Anticipated travel costs for Consultant travel between Auckland and Wellington:**\n\n**Trip 1** - Interview Week (Oct 14-18): $2,150\n**Trip 2** - Workshop (Oct 28-29): $1,290\n**Trip 3** - Board Presentation (Nov 15): $750\n\n*Travel costs are estimates based on current pricing. Actual costs will be invoiced based on receipts, kept at reasonable rates.*"},
            {"find": "Professional Fees: $[PCAmount1]\nTravel & Expenses: $[PCAmount2]", "replace": "**Professional Fees:** $57,000 (excluding GST)\n**Travel & Expenses:** $4,190 (excluding GST)\n**TOTAL PROJECT COST:** **$61,190 (excluding GST)**\n**Plus GST (15%):** $9,178.50\n**TOTAL INCLUDING GST:** **$70,368.50**"},
            {"find": "Invoice 1: ~[DateI1] ([PTMilestoneP1])\nInvoice 2: ~[DateI2] ([PTMilestoneP2])\nInvoice 3: ~[DateI3] ([PTMilestoneP3])", "replace": "**Invoice 1:** ~October 21, 2025 (following completion of Phase 1)\n**Invoice 2:** ~November 1, 2025 (following completion of Phase 2)\n**Invoice 3:** ~November 18, 2025 (following completion of Phase 3)\n\n**Payment Terms:** 14 days from invoice date\n**Invoice Recipient:** accounts@techventuresolutions.co.nz"},
            {"find": "[Contact Name]\n[Title/Position]\n[Email Address]", "replace": "**Emma Patterson**\nSenior Consultant\nemma.patterson@humankind.co.nz\n\n**Humankind Limited**"}
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
        print(f"\n[OK] Replacements made: {result['total_replacements']}")

        files = [result["file"]]

        # Save output
        import time
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_agent_DEBUG_{int(time.time())}.pptx"
        )

        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"\n[OK] Saved to: {output_path}")
        print("\n" + "=" * 70)
        print("DEBUG ANALYSIS COMPLETE")
        print("=" * 70)
        print("\nReview the debug output above to see:")
        print("  1. Which method was used (PILLOW vs HEURISTIC)")
        print("  2. Box dimensions and usable space")
        print("  3. Lines needed vs available")
        print("  4. Final font size chosen")
        print("  5. Any WARNING messages about overflow")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_agent_input_debug())
