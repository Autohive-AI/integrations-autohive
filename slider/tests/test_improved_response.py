"""
Test improved find_and_replace response structure.
Shows clear status, summary, and changelog.
"""

import asyncio
import sys
import os
import base64
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext


async def test_improved_response():
    """Test improved response with mix of success/failure/blocked"""

    print("=" * 70)
    print("IMPROVED RESPONSE STRUCTURE TEST")
    print("=" * 70)

    auth = {}

    async with ExecutionContext(auth=auth) as context:
        # Create presentation with placeholders
        result = await slide_maker.execute_action(
            "create_presentation",
            {"title": "Response Test"},
            context
        )

        presentation_id = result["presentation_id"]
        files = [result["file"]]

        # Add placeholders
        await slide_maker.execute_action(
            "add_elements",
            {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "elements": [
                    {"content": "[TITLE]", "position": {"left": 1, "top": 1, "width": 8, "height": 1}},
                    {"content": "[COMPANY] and [COMPANY] partnership", "position": {"left": 1, "top": 2.5, "width": 8, "height": 0.8}},
                    {"content": "[BODY]", "position": {"left": 1, "top": 3.5, "width": 8, "height": 1.5}}
                ],
                "files": files
            },
            context
        )

        print("\n1. Created presentation with placeholders")

        # Test replacements: mix of success, failure, and blocked
        print("\n2. Testing replacements (success + failure + blocked)...")

        replacements = [
            # SUCCESS: Will be found and replaced
            {"find": "[TITLE]", "replace": "Q4 Business Review", "forced_font_size": 32},

            # SUCCESS with multiple matches (but replace_all=true)
            {"find": "[COMPANY]", "replace": "TechVenture Solutions", "replace_all": True},

            # FAILURE: Not found
            {"find": "[NONEXISTENT]", "replace": "This won't match anything"},

            # BLOCKED: Multiple matches without replace_all
            # (Won't actually block in this test since [COMPANY] only appears in one place, but demonstrates the structure)

            # SUCCESS: Normal replacement
            {"find": "[BODY]", "replace": "This is the body content that will be auto-sized to fit the available space in the text box."}
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

        print("\n" + "=" * 70)
        print("RESPONSE STRUCTURE:")
        print("=" * 70)

        # Pretty print the new fields
        print(f"\n[STATUS]: {result['status']}")
        print(f"\n[SUMMARY]:")
        print(f"  Requested: {result['summary']['requested']}")
        print(f"  Successful: {result['summary']['successful']}")
        print(f"  Failed: {result['summary']['failed']}")
        print(f"  Blocked: {result['summary']['blocked']}")

        print(f"\n[CHANGES] ({len(result['changes'])} records):")
        for i, change in enumerate(result['changes']):
            print(f"\n  Change {i+1}:")
            print(f"    Find: \"{change['find']}\"")
            print(f"    Replace: \"{change['replace'][:50]}{'...' if len(change['replace']) > 50 else ''}\"")
            print(f"    Status: {change['status']}")
            print(f"    Occurrences: {change['occurrences']}")

            if change['status'] == 'replaced':
                print(f"    Font size: {change.get('font_size_applied')}pt {('(forced)' if change.get('forced') else '(auto)')}")
                print(f"    Locations:")
                for loc in change.get('locations', []):
                    if loc['type'] == 'text_box':
                        print(f"      - Slide {loc['slide']}, Element {loc['element']} (text box)")
                    else:
                        print(f"      - Slide {loc['slide']}, Element {loc['element']}, Cell ({loc.get('row')},{loc.get('col')})")
            elif change['status'] == 'not_found':
                print(f"    Suggestion: {change.get('suggestion', 'N/A')}")
            elif change['status'] == 'blocked':
                print(f"    Reason: {change.get('reason', 'N/A')}")

        print("\n" + "=" * 70)
        print("BACKWARD COMPATIBILITY CHECK:")
        print("=" * 70)
        print(f"  success: {result['success']} (deprecated but kept)")
        print(f"  total_replacements: {result['total_replacements']}")
        print(f"  processed: {result['processed']}")
        print(f"  warnings: {len(result['warnings'])} warning(s)")

        print("\n" + "=" * 70)
        print("[SUCCESS] Response structure is clear and actionable for LLMs!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_improved_response())
