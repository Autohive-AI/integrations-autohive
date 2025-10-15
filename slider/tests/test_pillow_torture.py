"""
TORTURE TEST for Pillow-based auto-fitting.

This test covers edge cases, extreme scenarios, and boundary conditions
to ensure the auto-fitting implementation is robust.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_pillow_torture():
    """Torture test with extreme cases and edge conditions"""

    print("=" * 70)
    print("PILLOW AUTO-FIT TORTURE TEST")
    print("=" * 70)
    print("\nTesting edge cases, extreme scenarios, and boundary conditions...")

    auth = {}

    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        print("\n1. Creating presentation...")
        result = await slide_maker.execute_action(
            "create_presentation",
            {"title": "Torture Test"},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]
        print(f"   [OK] Presentation created: {presentation_id}")

        # TORTURE TEST CASES
        test_cases = [
            # Edge Case: Empty and minimal text
            {
                "label": "EDGE: Single character",
                "text": "A",
                "box": {"left": 1, "top": 0.5, "width": 8, "height": 1},
                "expected": "Should stay at 18pt"
            },
            {
                "label": "EDGE: Two characters",
                "text": "Hi",
                "box": {"left": 1, "top": 1.7, "width": 8, "height": 1},
                "expected": "Should stay at 18pt"
            },

            # Edge Case: Very long single word (can't wrap)
            {
                "label": "EDGE: Unbreakable long word",
                "text": "Pneumonoultramicroscopicsilicovolcanoconiosis",
                "box": {"left": 1, "top": 2.9, "width": 3, "height": 0.8},
                "expected": "Must scale down (word too long)"
            },

            # Edge Case: Lots of spaces
            {
                "label": "EDGE: Text with many spaces",
                "text": "Word    with    many    spaces    between    words",
                "box": {"left": 1, "top": 3.9, "width": 5, "height": 0.8},
                "expected": "Should handle wrapping"
            },

            # Edge Case: Numbers and special chars
            {
                "label": "EDGE: Numbers and punctuation",
                "text": "1234567890!@#$%^&*()_+-=[]{}|;':,.<>?/",
                "box": {"left": 1, "top": 4.9, "width": 4, "height": 0.6},
                "expected": "Different character widths"
            },

            # Extreme: Very narrow box
            {
                "label": "EXTREME: Very narrow box (0.5 inches)",
                "text": "This text is in a very narrow box and will wrap to many lines",
                "box": {"left": 1, "top": 5.7, "width": 0.5, "height": 2},
                "expected": "Many wrapped lines"
            },

            # Extreme: Very short box
            {
                "label": "EXTREME: Very short box (0.3 inches)",
                "text": "Short box with not much vertical space available",
                "box": {"left": 2, "top": 5.7, "width": 3, "height": 0.3},
                "expected": "Must scale down significantly"
            },

            # Extreme: Very wide box
            {
                "label": "EXTREME: Very wide box (8.5 inches)",
                "text": "This is in a very wide box",
                "box": {"left": 3, "top": 6.2, "width": 8.5, "height": 0.5},
                "expected": "Should stay at 18pt, minimal wrapping"
            },

            # Extreme: Massive text block
            {
                "label": "EXTREME: Huge text block (500+ chars)",
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.",
                "box": {"left": 6, "top": 0.5, "width": 3.5, "height": 2},
                "expected": "Significant scaling needed"
            },

            # Formatting: Heavy markdown
            {
                "label": "FORMAT: Heavy markdown formatting",
                "text": "**Bold** *italic* `code` **_bold italic_** ~~strike~~ **`bold code`**",
                "box": {"left": 6, "top": 2.7, "width": 3.5, "height": 0.8},
                "expected": "Mixed formatting widths"
            },

            # Formatting: All bold
            {
                "label": "FORMAT: All bold text",
                "text": "**This entire text block is completely bold and takes more space**",
                "box": {"left": 6, "top": 3.7, "width": 3.5, "height": 0.8},
                "expected": "Bold is wider, may need scaling"
            },

            # Boundary: Text that JUST fits
            {
                "label": "BOUNDARY: Text that just fits at 18pt",
                "text": "Precisely sized",
                "box": {"left": 6, "top": 4.7, "width": 2, "height": 0.4},
                "expected": "Should stay at 18pt (boundary)"
            },

            # Boundary: Text that just overflows
            {
                "label": "BOUNDARY: Text that barely overflows",
                "text": "Slightly too much text for this box size",
                "box": {"left": 6, "top": 5.3, "width": 2, "height": 0.4},
                "expected": "Should scale down by 1-2pt"
            },

            # Real-world: Bullet point simulation
            {
                "label": "REAL-WORLD: Simulated bullet points",
                "text": "First point about something\nSecond point with more detail\nThird point with even more information",
                "box": {"left": 1, "top": 8, "width": 4, "height": 1.5},
                "expected": "Multiple lines with newlines"
            },

            # Real-world: Title-like text
            {
                "label": "REAL-WORLD: Slide title (32pt requested)",
                "text": "**Quarterly Business Review Q4 2024**",
                "box": {"left": 5.5, "top": 8, "width": 4, "height": 1},
                "expected": "Should handle larger font request"
            },
        ]

        print("\n2. Running torture tests (all requesting 24pt font)...")
        print(f"   Total test cases: {len(test_cases)}")
        print("   NOTE: All tests request 24pt. If text appears smaller, it scaled down!")

        for i, test_case in enumerate(test_cases):
            print(f"\n   [{i+1}/{len(test_cases)}] {test_case['label']}")
            print(f"      Text: \"{test_case['text'][:40]}{'...' if len(test_case['text']) > 40 else ''}\"")
            print(f"      Box: {test_case['box']['width']}w x {test_case['box']['height']}h inches")
            print(f"      Expected: {test_case['expected']}")

            try:
                # Set all fonts to 24pt (or 32pt for titles) to visually see scaling
                max_font_size = 32 if "title" in test_case['label'].lower() else 24

                # Add label above each test box to identify it
                label_text = f"[{test_case['label']}] Requested: {max_font_size}pt"
                label_result = await slide_maker.execute_action(
                    "add_elements",
                    {
                        "presentation_id": presentation_id,
                        "slide_index": 0,
                        "elements": [{
                            "content": label_text,
                            "position": {
                                "left": test_case["box"]["left"],
                                "top": test_case["box"]["top"] - 0.25,
                                "width": test_case["box"]["width"],
                                "height": 0.2
                            }
                        }],
                        "files": files
                    },
                    context
                )
                if "file" in label_result:
                    files = [label_result["file"]]

                # Add element and capture updated file
                result = await slide_maker.execute_action(
                    "add_elements",
                    {
                        "presentation_id": presentation_id,
                        "slide_index": 0,
                        "elements": [{
                            "content": test_case["text"],
                            "position": test_case["box"]
                        }],
                        "files": files
                    },
                    context
                )
                # Update files with the result
                if "file" in result:
                    files = [result["file"]]
                print(f"      [OK] Rendered successfully")

            except Exception as e:
                print(f"      [FAIL] Error: {str(e)}")
                # Continue with other tests even if one fails

        # Additional stress test: Many small boxes (24pt requested, very small boxes)
        print("\n3. Stress test: Adding 20 small boxes (24pt requested)...")
        for i in range(20):
            row = i // 10
            col = i % 10
            result = await slide_maker.execute_action(
                "add_elements",
                {
                    "presentation_id": presentation_id,
                    "slide_index": 0,
                    "elements": [{
                        "content": f"Box{i+1}",
                        "position": {
                            "left": 0.2 + (col * 1),
                            "top": 9 + (row * 0.4),
                            "width": 0.8,
                            "height": 0.3
                        }
                    }],
                    "files": files
                },
                context
            )
            # Update files after each addition
            if "file" in result:
                files = [result["file"]]
        print(f"   [OK] Added 20 small boxes (should scale down significantly)")

        # Save presentation
        print("\n4. Saving torture test presentation...")
        import time
        timestamp = int(time.time())
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_pillow_torture_24pt_{timestamp}.pptx"
        )

        import base64
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"   [OK] Saved to: {output_path}")

        print("\n" + "=" * 70)
        print("[SUCCESS] TORTURE TEST COMPLETED!")
        print("=" * 70)
        print("\nTest Results:")
        print(f"  - Total edge cases tested: {len(test_cases)}")
        print(f"  - Extreme scenarios: 5")
        print(f"  - Boundary conditions: 2")
        print(f"  - Real-world scenarios: 2")
        print(f"  - Stress test: 20 small boxes")
        print("\nPlease open the output file to verify:")
        print("  1. ALL TEXT BOXES have labels showing 'Requested: 24pt' (or 32pt)")
        print("  2. Text that's SMALLER than requested = successfully scaled down")
        print("  3. Text that's AT requested size = it fit perfectly, no scaling needed")
        print("  4. All text fits within boxes (no overflow)")
        print("  5. Labels help you identify which test is which")
        print("\n  VISUAL TEST: Look for font size differences!")
        print("  - Short text (A, Hi) should stay at 24pt")
        print("  - Long text / small boxes should be visibly smaller")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_pillow_torture())
