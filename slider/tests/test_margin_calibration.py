"""
Calibration test to determine if PowerPoint has additional internal padding
beyond the explicit margins we set.

Creates test boxes with known text and measures if they overflow.
"""

import asyncio
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_margin_calibration():
    """Test if PowerPoint has additional internal padding"""

    print("=" * 70)
    print("MARGIN CALIBRATION TEST")
    print("=" * 70)

    auth = {}

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action(
            "create_presentation",
            {"title": "Margin Calibration"},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]

        print("\nCreating test boxes to check for overflow...")
        print("All boxes request 18pt font - we'll see which ones fit\n")

        # Test case 1: Should fit perfectly at 18pt (based on our calculation)
        test_cases = [
            {
                "label": "TEST 1: Calculated to fit at 18pt",
                "text": "Short text",
                "box": {"left": 1, "top": 1, "width": 3, "height": 0.5},
                "note": "If this overflows, margins are wrong"
            },
            {
                "label": "TEST 2: Medium text, should fit at 18pt",
                "text": "This is medium length text that should wrap nicely",
                "box": {"left": 5, "top": 1, "width": 4, "height": 1},
                "note": "If this overflows, line height calc is wrong"
            },
            {
                "label": "TEST 3: Fill to 80% capacity",
                "text": "This text is calibrated to fill approximately 80% of the vertical space in the box at 18pt font size based on our calculations",
                "box": {"left": 1, "top": 2, "width": 4, "height": 1.5},
                "note": "If this overflows, we need more safety margin"
            },
            {
                "label": "TEST 4: Extreme - tiny box",
                "text": "Too much text for this tiny box to handle at any reasonable font size",
                "box": {"left": 6, "top": 2, "width": 3, "height": 0.3},
                "note": "Will scale to minimum, likely still overflows"
            },
        ]

        for i, test in enumerate(test_cases):
            print(f"\n{test['label']}")
            print(f"  Text: \"{test['text'][:40]}...\"")
            print(f"  Box: {test['box']['width']}w x {test['box']['height']}h")
            print(f"  Note: {test['note']}")

            # Add label
            result = await slide_maker.execute_action(
                "add_elements",
                {
                    "presentation_id": presentation_id,
                    "slide_index": 0,
                    "elements": [{
                        "content": test['label'],
                        "position": {
                            "left": test['box']['left'],
                            "top": test['box']['top'] - 0.25,
                            "width": test['box']['width'],
                            "height": 0.2
                        }
                    }],
                    "files": files
                },
                context
            )
            if "file" in result:
                files = [result["file"]]

            # Add test box
            result = await slide_maker.execute_action(
                "add_elements",
                {
                    "presentation_id": presentation_id,
                    "slide_index": 0,
                    "elements": [{
                        "content": test['text'],
                        "position": test['box']
                    }],
                    "files": files
                },
                context
            )
            if "file" in result:
                files = [result["file"]]

            print(f"  [OK] Added")

        # Save
        import time
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_margin_calibration_{int(time.time())}.pptx"
        )

        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"\n[OK] Saved to: {output_path}")
        print("\n" + "=" * 70)
        print("VISUAL INSPECTION:")
        print("=" * 70)
        print("\n1. Open the PowerPoint file")
        print("2. For EACH test box, check if text overflows (cut off/ellipsis)")
        print("\n3. If TEST 1-2 overflow:")
        print("   -> Our margins are TOO SMALL, need to increase them")
        print("\n4. If TEST 3 overflows:")
        print("   -> Need additional safety margin in calculation")
        print("\n5. If ALL tests fit perfectly:")
        print("   -> Margins are correct, template boxes are just too small")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_margin_calibration())
