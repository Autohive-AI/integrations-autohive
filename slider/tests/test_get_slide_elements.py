# Test get_slide_elements action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_elements():
    """Helper to create a presentation with various elements for testing"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        create_inputs = {
            "title": "Element Inspection Test",
            "subtitle": "Testing boundary and overlap detection",
            "custom_filename": "test_inspection_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add text box that fits well
        text_inputs1 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Normal text box",
            "position": {"left": 1.0, "top": 3.0, "width": 3.0, "height": 1.0},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs1, context)
        
        # Add text box that might overlap
        text_inputs2 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Overlapping text box",
            "position": {"left": 3.5, "top": 3.2, "width": 3.0, "height": 1.0},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs2, context)
        
        # Add text box that extends beyond boundary
        text_inputs3 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Boundary violating text",
            "position": {"left": 8.0, "top": 4.5, "width": 4.0, "height": 1.5},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs3, context)
        
        return presentation_id, result["file"]

async def test_basic_inspection():
    """Test basic slide element inspection"""
    print("Testing basic slide inspection...")
    
    presentation_id, file_data = await create_test_presentation_with_elements()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "include_content": False,  # Minimal output
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("get_slide_elements", inputs, context)
        
        print(f"✅ Inspection results:")
        print(f"   Total elements: {result['total_elements']}")
        print(f"   Layout status: {result['layout_status']}")
        print(f"   Slide dimensions: {result['slide_dimensions']['width']}\" x {result['slide_dimensions']['height']}\"")
        
        if result['layout_status'] == 'issues_detected':
            if 'elements_outside_boundary' in result:
                print(f"   Elements outside boundary: {result['elements_outside_boundary']}")
            if 'total_overlapping_pairs' in result:
                print(f"   Overlapping pairs: {result['total_overlapping_pairs']}")
        
        print(f"   Elements found:")
        for element in result['elements']:
            pos = element['position']
            print(f"     - Element {element['index']} ({element['type']}): {pos['left']}\", {pos['top']}\" | {pos['width']}\" x {pos['height']}\"")
            if 'boundary_status' in element:
                print(f"       Boundary status: {element['boundary_status']}")
            if 'content' in element:
                print(f"       Content: \"{element['content'][:30]}...\"")
        
        return result

async def test_inspection_with_content():
    """Test inspection with content included"""
    print("\nTesting inspection with content included...")
    
    presentation_id, file_data = await create_test_presentation_with_elements()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "include_content": True,  # Show all content
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("get_slide_elements", inputs, context)
        
        print(f"✅ Inspection with content:")
        print(f"   Layout status: {result['layout_status']}")
        
        for element in result['elements']:
            if 'content' in element and element['content']:
                print(f"   Element {element['index']}: \"{element['content']}\"")
        
        return result

async def test_empty_slide_inspection():
    """Test inspecting an empty slide"""
    print("\nTesting empty slide inspection...")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create blank presentation
        create_inputs = {"custom_filename": "test_empty_slide"}
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        
        # Inspect the empty slide
        inspect_inputs = {
            "presentation_id": result["presentation_id"],
            "slide_index": 0,
            "files": [result["file"]]
        }
        
        inspect_result = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)
        
        print(f"✅ Empty slide inspection:")
        print(f"   Total elements: {inspect_result['total_elements']}")
        print(f"   Layout status: {inspect_result['layout_status']}")
        print(f"   Should show 'no_issues' for empty slide")
        
        return inspect_result

async def main():
    print("Testing Get Slide Elements Action")
    print("=================================")
    
    try:
        await test_basic_inspection()
        await test_inspection_with_content()
        await test_empty_slide_inspection()
        print("\n✅ All get_slide_elements tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())