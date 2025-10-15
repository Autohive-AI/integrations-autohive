"""
Test forced_font_size parameter in find_and_replace.
Demonstrates forcing specific font sizes for titles/headers.
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


async def test_forced_font_size():
    """Test forced_font_size parameter"""

    print("=" * 70)
    print("FORCED FONT SIZE TEST")
    print("=" * 70)

    auth = {}

    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        result = await slide_maker.execute_action(
            "create_presentation",
            {"title": "Forced Font Size Test"},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]

        print("\n1. Adding test text boxes with placeholders...")

        # Add test boxes with various placeholders
        await slide_maker.execute_action(
            "add_elements",
            {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "elements": [
                    {
                        "content": "[TITLE-32]",
                        "position": {"left": 1, "top": 1, "width": 8, "height": 1.5}
                    },
                    {
                        "content": "[HEADING-24]",
                        "position": {"left": 1, "top": 2.7, "width": 8, "height": 1}
                    },
                    {
                        "content": "[BODY-AUTO]",
                        "position": {"left": 1, "top": 4, "width": 8, "height": 1.2}
                    }
                ],
                "files": files
            },
            context
        )

        print("   [OK] Added 3 placeholder text boxes")

        # Get updated files
        result = await slide_maker.execute_action(
            "get_slide_elements",
            {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "files": files
            },
            context
        )

        print("\n2. Executing find_and_replace with forced sizes...")
        print("=" * 70)

        replacements = [
            {
                "find": "[TITLE-32]",
                "replace": "This is a Main Title",
                "forced_font_size": 32  # ← FORCED to 32pt
            },
            {
                "find": "[HEADING-24]",
                "replace": "This is a Section Heading",
                "forced_font_size": 24  # ← FORCED to 24pt
            },
            {
                "find": "[BODY-AUTO]",
                "replace": "This is body text that will be auto-sized based on the content length and box dimensions. The font size will be calculated automatically to ensure it fits properly."
                # ← NO forced_font_size, will auto-calculate
            }
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
            f"test_forced_size_{int(time.time())}.pptx"
        )

        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"\n3. Saved to: {output_path}")

        print("\n" + "=" * 70)
        print("[SUCCESS] FORCED FONT SIZE TEST COMPLETE!")
        print("=" * 70)
        print("\nEXPECTED RESULTS:")
        print("  Box 1 (Title): Should be EXACTLY 32pt (forced)")
        print("  Box 2 (Heading): Should be EXACTLY 24pt (forced)")
        print("  Box 3 (Body): Should be auto-calculated (likely 14-18pt)")
        print("\nCheck debug output above to verify:")
        print("  - [FORCED SIZE] messages for boxes 1 & 2")
        print("  - [PILLOW] calculation for box 3")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_forced_font_size())
