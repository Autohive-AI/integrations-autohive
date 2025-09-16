# Test delete_element action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_multiple_elements():
    """Helper to create a presentation with multiple elements for deletion testing"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        create_inputs = {
            "title": "Element Deletion Test",
            "custom_filename": "test_deletion_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add text box
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Text box to be deleted",
            "position": {"left": 1.0, "top": 3.0, "width": 3.0, "height": 1.0},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        # Add bullet list
        bullet_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "bullet_items": [
                {"text": "Bullet item 1", "level": 0},
                {"text": "Bullet item 2", "level": 0}
            ],
            "position": {"left": 5.0, "top": 3.0, "width": 4.0, "height": 1.5},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_bullet_list", bullet_inputs, context)
        
        return presentation_id, result["file"]

async def test_inspect_before_deletion():
    """Test inspecting elements before deletion"""
    print("Testing element inspection before deletion...")
    
    presentation_id, file_data = await create_test_presentation_with_multiple_elements()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "include_content": True,
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("get_slide_elements", inputs, context)
        
        print(f"✅ Elements before deletion:")
        print(f"   Total elements: {result['total_elements']}")
        for element in result['elements']:
            print(f"   Element {element['index']} ({element['type']}): \"{element.get('content', 'No content')[:30]}...\"")
        
        return result, file_data

async def test_delete_specific_element():
    """Test deleting a specific element"""
    print("\nTesting element deletion...")
    
    inspect_result, file_data = await test_inspect_before_deletion()
    presentation_id = "test_deletion_presentation"  # We know this from the creation
    
    # Delete element at index 2 (the bullet list)
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        delete_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 2,  # Delete the bullet list
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("delete_element", delete_inputs, context)
        
        print(f"✅ Deleted element:")
        print(f"   Deleted: {result['deleted']}")
        print(f"   Element type: {result['element_type']}")
        print(f"   Remaining shapes: {result['remaining_shapes']}")
        
        # Inspect after deletion
        inspect_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "include_content": True,
            "files": [result["file"]]
        }
        
        inspect_after = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)
        
        print(f"   Elements after deletion:")
        print(f"   Total elements: {inspect_after['total_elements']}")
        for element in inspect_after['elements']:
            print(f"   Element {element['index']} ({element['type']}): \"{element.get('content', 'No content')[:30]}...\"")
        
        return result

async def test_delete_invalid_element():
    """Test attempting to delete invalid element index"""
    print("\nTesting invalid element deletion...")
    
    presentation_id, file_data = await create_test_presentation_with_multiple_elements()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        try:
            inputs = {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "shape_index": 99,  # Invalid index
                "files": [file_data]
            }
            
            result = await slide_maker.execute_action("delete_element", inputs, context)
            print("❌ Should have failed with invalid index")
            
        except ValueError as e:
            print(f"✅ Correctly caught invalid index error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")

async def main():
    print("Testing Delete Element Action")
    print("=============================")
    
    try:
        await test_inspect_before_deletion()
        await test_delete_specific_element()
        await test_delete_invalid_element()
        print("\n✅ All delete_element tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())