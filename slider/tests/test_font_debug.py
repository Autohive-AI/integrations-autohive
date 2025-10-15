# Debug font extraction in table cells
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def debug_table_font_extraction():
    """Debug what's happening with font extraction in table cells"""
    print("🔬 Debugging Table Font Extraction")
    print("=" * 50)

    auth = {}
    async with ExecutionContext(auth=auth) as context:

        # Create a simple test presentation
        create_inputs = {
            "title": "Font Debug Test",
            "custom_filename": "font_debug_test"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]

        # Add a simple 2x2 table
        table_data = [
            ["Header 1", "Header 2"],
            ["Data 1", "Data 2"]
        ]

        table_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "rows": 2,
            "cols": 2,
            "position": {"left": 1.0, "top": 2.0, "width": 5.0, "height": 2.0},
            "data": table_data,
            "files": [result["file"]]
        }

        result = await slide_maker.execute_action("add_table", table_inputs, context)
        print("✅ Created 2×2 test table")

        # Find the table element
        inspect_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "files": [result["file"]]
        }

        slide_elements = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)
        table_element_index = None

        for i, element in enumerate(slide_elements['elements']):
            if element['type'] == 'table':
                table_element_index = i
                break

        if table_element_index is None:
            raise Exception("No table found!")

        print(f"🎯 Found table at index {table_element_index}")

        # Apply some Lato font styling
        print("\n🎨 Applying Lato font styling...")

        # This modify_element doesn't actually set font name - let's see what happens
        style_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,
            "table_cell_updates": [
                {
                    "row": 0, "col": 0, "text": "Lato Header 1",
                    "formatting": {"font_size": 16, "bold": True, "color": "#FF0000"}
                },
                {
                    "row": 0, "col": 1, "text": "Lato Header 2",
                    "formatting": {"font_size": 16, "bold": True, "color": "#00FF00"}
                },
                {
                    "row": 1, "col": 0, "text": "Lato Data 1",
                    "formatting": {"font_size": 12, "color": "#008000"}
                },
                {
                    "row": 1, "col": 1, "text": "Lato Data 2",
                    "formatting": {"font_size": 12, "color": "#0000FF"}
                }
            ],
            "files": [result["file"]]
        }

        result = await slide_maker.execute_action("modify_element", style_inputs, context)
        print(f"Applied styling - Changes: {len(result.get('changes_made', []))}")

        # Now debug extract styling
        print("\n🔍 Extracting and debugging styling...")

        styling_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,
            "files": [result["file"]]
        }

        styling_result = await slide_maker.execute_action("get_element_styling", styling_inputs, context)

        print("📋 Raw styling description:")
        print("-" * 40)
        print(styling_result['styling_description'])
        print("-" * 40)

        # Let's create a custom debug version to see what's in the cells
        print("\n🔬 Deep diving into font properties...")

        # We need to access the table directly to debug
        # This would require modifying the action or creating a debug method
        print("Note: Need to create debug method to access table cell font properties directly")

        return styling_result

async def main():
    try:
        await debug_table_font_extraction()
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())