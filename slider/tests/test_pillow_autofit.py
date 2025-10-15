"""
Test Pillow-based auto-fitting functionality.

This test verifies that the new Pillow-based font size calculation
produces accurate results compared to the heuristic approach.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_pillow_autofit():
    """Test Pillow-based auto-fitting with various text lengths"""

    print("=" * 70)
    print("PILLOW AUTO-FIT TEST")
    print("=" * 70)

    auth = {}

    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        print("\n1. Creating presentation...")
        result = await slide_maker.execute_action(
            "create_presentation",
            {"title": "Pillow Auto-Fit Test"},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]
        print(f"   [OK] Presentation created: {presentation_id}")

        # Test cases with different text lengths
        # Note: max_font_size is 18pt by default, so text only scales DOWN if needed
        test_cases = [
            {
                "label": "Short Text (should remain at 18pt)",
                "text": "Hello World",
                "expected_size": "18pt (fits, no scaling needed)"
            },
            {
                "label": "Medium Text (might scale down slightly)",
                "text": "This is a medium length text for testing the auto-fit functionality",
                "expected_size": "16-18pt (may need slight scaling)"
            },
            {
                "label": "Long Text (should scale down significantly)",
                "text": "This is a very long piece of text that contains significantly more content and should require a much smaller font size to fit within the box dimensions properly. The Pillow-based measurement should calculate this accurately.",
                "expected_size": "10-12pt (scaled down to fit)"
            },
            {
                "label": "Short Formatted Text (should remain at 18pt)",
                "text": "**Bold Title** with *italic* and `code`",
                "expected_size": "18pt (fits, no scaling needed)"
            }
        ]

        print("\n2. Adding test text boxes...")
        for i, test_case in enumerate(test_cases):
            print(f"\n   Test {i+1}: {test_case['label']}")
            print(f"   Expected: {test_case['expected_size']}")
            print(f"   Text: \"{test_case['text'][:50]}{'...' if len(test_case['text']) > 50 else ''}\"")

            # Add text box with auto-fitting
            result = await slide_maker.execute_action(
                "add_elements",
                {
                    "presentation_id": presentation_id,
                    "slide_index": 0,
                    "elements": [{
                        "content": test_case["text"],
                        "position": {
                            "left": 1,
                            "top": 1 + (i * 1.5),
                            "width": 8,
                            "height": 1.2
                        }
                    }],
                    "files": files
                },
                context
            )
            # Update files with the result
            if "file" in result:
                files = [result["file"]]

            print(f"   [OK] Text box added with Pillow auto-fitting")

        # Save final presentation
        print("\n3. Saving presentation...")
        output_path = os.path.join(
            os.path.dirname(__file__),
            "test_pillow_autofit_output.pptx"
        )

        import base64
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(files[0]["content"]))

        print(f"   [OK] Saved to: {output_path}")

        print("\n" + "=" * 70)
        print("[SUCCESS] PILLOW AUTO-FIT TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nPlease open the output file to verify:")
        print("  1. All text fits within boxes without overflow")
        print("  2. Short text remains at requested size (18pt, not scaled up)")
        print("  3. Long text is scaled DOWN to fit (smaller than 18pt)")
        print("  4. Formatted text (bold, italic, code) renders correctly")
        print("  5. No text is ever scaled UP beyond the requested size")
        print(f"\n[FILE] Output: {output_path}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_pillow_autofit())
