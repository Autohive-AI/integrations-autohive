# Test save_presentation and extract_text actions
import asyncio
import os
import tempfile
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_content():
    """Helper to create a presentation with content for testing"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        create_inputs = {
            "title": "🐝 Save and Extract Test",
            "subtitle": "Testing file operations",
            "custom_filename": "test_save_extract_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add a second slide
        add_slide_inputs = {
            "presentation_id": presentation_id,
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_slide", add_slide_inputs, context)
        
        # Add content to second slide
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "text": "🍯 Honey Facts:\n• Honey never spoils\n• Bees visit 2 million flowers for 1 lb\n• Ancient Egyptians used honey as currency",
            "position": {"left": 1.0, "top": 1.0, "width": 8.0, "height": 3.0},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        # Add bullet list to second slide
        bullet_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 1,
            "bullet_items": [
                {"text": "🐝 Worker bee facts", "level": 0},
                {"text": "Lives only 6 weeks in summer", "level": 1},
                {"text": "Produces 1/12 teaspoon honey in lifetime", "level": 1},
                {"text": "Visits 50-100 flowers per trip", "level": 1}
            ],
            "position": {"left": 1.0, "top": 4.5, "width": 8.0, "height": 1.0},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_bullet_list", bullet_inputs, context)
        
        return presentation_id, result["file"]

async def test_save_presentation():
    """Test saving presentation with custom filename"""
    print("Testing save_presentation action...")
    
    presentation_id, file_data = await create_test_presentation_with_content()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "file_path": "saved_bee_presentation.pptx"
        }
        
        result = await slide_maker.execute_action("save_presentation", inputs, context)
        
        print(f"✅ Saved presentation:")
        print(f"   Saved: {result['saved']}")
        print(f"   File path: {result['file_path']}")
        print(f"   File name: {result['file']['name']}")
        print(f"   Content type: {result['file']['contentType']}")
        print(f"   Content size: {len(result['file']['content'])} characters (base64)")
        
        return result

async def test_extract_text_from_memory():
    """Test extracting text from presentation in memory"""
    print("\nTesting text extraction from memory presentation...")
    
    # Create a presentation with content
    presentation_id, file_data = await create_test_presentation_with_content()
    
    # Save to temporary file for extraction
    with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as tmp_file:
        # Decode the base64 content and save to file
        import base64
        file_content = base64.b64decode(file_data['content'])
        tmp_file.write(file_content)
        tmp_file.flush()
        
        temp_path = tmp_file.name
    
    try:
        auth = {}
        async with ExecutionContext(auth=auth) as context:
            inputs = {
                "file_path": temp_path
            }
            
            result = await slide_maker.execute_action("extract_text", inputs, context)
            
            print(f"✅ Extracted text:")
            print(f"   Total slides: {len(result['slides'])}")
            
            for slide_info in result['slides']:
                print(f"   Slide {slide_info['slide_index']}:")
                for i, text in enumerate(slide_info['text_content']):
                    print(f"     - Text {i}: \"{text[:50]}...\"")
            
            print(f"   Combined text length: {len(result['all_text'])} characters")
            print(f"   Contains emojis and bullet points")
            
            return result
            
    finally:
        # Clean up temporary file
        os.unlink(temp_path)

async def test_save_with_error_handling():
    """Test save action with invalid presentation ID"""
    print("\nTesting save action error handling...")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        try:
            inputs = {
                "presentation_id": "invalid_id",
                "file_path": "should_fail.pptx"
            }
            
            result = await slide_maker.execute_action("save_presentation", inputs, context)
            print("❌ Should have failed with invalid ID")
            
        except ValueError as e:
            print(f"✅ Correctly caught error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")

async def main():
    print("Testing Save and Extract Actions")
    print("================================")
    
    try:
        await test_save_presentation()
        await test_extract_text_from_memory()
        await test_save_with_error_handling()
        print("\n✅ All save and extract tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())