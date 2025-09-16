# Test modify_element action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_text():
    """Helper to create a presentation with text elements for modification"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        create_inputs = {
            "title": "Modification Test",
            "custom_filename": "test_modify_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add a text box to modify
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Original text content",
            "position": {"left": 2.0, "top": 3.0, "width": 4.0, "height": 1.5},
            "formatting": {"font_size": 18, "bold": False, "color": "#000000"},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        return presentation_id, result["file"]

async def test_modify_position():
    """Test modifying element position and size"""
    print("Testing element position modification...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # First inspect to see current position
        inspect_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "include_content": True,
            "files": [file_data]
        }
        inspect_result = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)
        
        print(f"Original position of element 1:")
        element = inspect_result['elements'][1]  # Second element (first is title)
        pos = element['position']
        print(f"   Position: {pos['left']}\", {pos['top']}\" | Size: {pos['width']}\" x {pos['height']}\"")
        
        # Modify position
        modify_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": 1,
            "position": {
                "left": 5.0,
                "top": 1.0,
                "width": 3.0,
                "height": 2.0
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_element", modify_inputs, context)
        
        print(f"✅ Modified element position:")
        print(f"   Modified: {result['modified']}")
        print(f"   Changes made: {result['changes_made']}")
        new_pos = result['new_position']
        print(f"   New position: {new_pos['left']}\", {new_pos['top']}\" | Size: {new_pos['width']}\" x {new_pos['height']}\"")
        
        return result

async def test_modify_text_content():
    """Test modifying text content"""
    print("\nTesting text content modification...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": 1,  # Text element we created
            "text_content": "🚀 Updated text content with emoji!",
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_element", inputs, context)
        
        print(f"✅ Modified text content:")
        print(f"   Modified: {result['modified']}")
        print(f"   Changes made: {result['changes_made']}")
        
        return result

async def test_modify_formatting():
    """Test modifying text formatting"""
    print("\nTesting text formatting modification...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": 1,  # Text element we created
            "formatting": {
                "font_size": 28,
                "bold": True,
                "italic": True,
                "color": "#FF0000"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_element", inputs, context)
        
        print(f"✅ Modified text formatting:")
        print(f"   Modified: {result['modified']}")
        print(f"   Changes made: {result['changes_made']}")
        print(f"   Applied to both paragraph and run levels")
        
        return result

async def test_combined_modifications():
    """Test modifying position, content, and formatting together"""
    print("\nTesting combined modifications...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": 1,
            "position": {
                "left": 1.5,
                "top": 4.0,
                "width": 7.0,
                "height": 1.0
            },
            "text_content": "✨ Completely updated element ✨",
            "formatting": {
                "font_size": 20,
                "bold": True,
                "color": "#9B59B6"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_element", inputs, context)
        
        print(f"✅ Combined modifications:")
        print(f"   Modified: {result['modified']}")
        print(f"   Changes made ({len(result['changes_made'])} total):")
        for change in result['changes_made']:
            print(f"     - {change}")
        
        return result

async def main():
    print("Testing Modify Element Action")
    print("=============================")
    
    try:
        await test_modify_position()
        await test_modify_text_content()
        await test_modify_formatting()
        await test_combined_modifications()
        print("\n✅ All modify_element tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())