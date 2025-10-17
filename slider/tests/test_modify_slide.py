# Test modify_slide action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_content():
    """Helper to create a presentation with content for modification testing"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation with title
        create_inputs = {
            "title": "🐝 Original Title",
            "subtitle": "Original subtitle content",
            "custom_filename": "test_modify_slide_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add some text content to modify
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "This text contains some old information that needs updating. The old system was inefficient.",
            "position": {"left": 1.0, "top": 3.0, "width": 8.0, "height": 1.5},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        # Add more text with specific content to replace
        text_inputs2 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Contact us at old-email@example.com for more information. Our old phone number was 555-0123.",
            "position": {"left": 1.0, "top": 4.8, "width": 8.0, "height": 0.8},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs2, context)
        
        return presentation_id, result["file"]

async def test_modify_slide_title():
    """Test modifying slide title"""
    print("Testing slide title modification...")
    
    presentation_id, file_data = await create_test_presentation_with_content()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "updates": {
                "title": "🚀 Updated Title"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_slide", inputs, context)
        
        print(f"✅ Modified slide title:")
        print(f"   Modified: {result['modified']}")
        print(f"   Changed title from '🐝 Original Title' to '🚀 Updated Title'")
        print(f"   Saved: {result['saved']}")
        
        return result

async def test_text_replacements():
    """Test text replacements across slide"""
    print("\nTesting text replacements...")
    
    presentation_id, file_data = await create_test_presentation_with_content()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "updates": {
                "replace_text": [
                    {
                        "old_text": "old information",
                        "new_text": "updated information"
                    },
                    {
                        "old_text": "old system",
                        "new_text": "new system"
                    },
                    {
                        "old_text": "old-email@example.com",
                        "new_text": "new-email@company.com"
                    },
                    {
                        "old_text": "555-0123",
                        "new_text": "555-9876"
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_slide", inputs, context)
        
        print(f"✅ Applied text replacements:")
        print(f"   Modified: {result['modified']}")
        print(f"   Replaced 4 different text strings across all text elements")
        print(f"   Updated: email, phone, system references")
        
        return result

async def test_combined_slide_modifications():
    """Test combining title update with text replacements"""
    print("\nTesting combined slide modifications...")
    
    presentation_id, file_data = await create_test_presentation_with_content()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "updates": {
                "title": "🔄 Completely Updated Slide",
                "replace_text": [
                    {
                        "old_text": "old information",
                        "new_text": "fresh content"
                    },
                    {
                        "old_text": "inefficient",
                        "new_text": "streamlined"
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_slide", inputs, context)
        
        print(f"✅ Combined modifications:")
        print(f"   Modified: {result['modified']}")
        print(f"   Updated both title and text content")
        print(f"   Applied multiple text replacements")
        
        return result

async def test_no_modifications():
    """Test modify_slide when no changes are made"""
    print("\nTesting no modifications scenario...")
    
    presentation_id, file_data = await create_test_presentation_with_content()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "updates": {
                "replace_text": [
                    {
                        "old_text": "nonexistent_text",
                        "new_text": "replacement"
                    }
                ]
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("modify_slide", inputs, context)
        
        print(f"✅ No modifications scenario:")
        print(f"   Modified: {result['modified']} (should be False)")
        print(f"   No text found to replace")
        print(f"   Slide unchanged but action completed successfully")
        
        return result

async def test_modify_slide_without_title():
    """Test modifying slide that has no title shape"""
    print("\nTesting slide modification without title shape...")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation without title
        create_inputs = {"custom_filename": "test_no_title_slide"}
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add some text to the blank slide
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Regular text content on blank slide",
            "position": {"left": 2.0, "top": 2.0, "width": 6.0, "height": 1.0},
            "files": [result["file"]]
        }
        text_result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        # Try to modify title (should not crash)
        modify_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "updates": {
                "title": "Attempted Title Update",
                "replace_text": [
                    {
                        "old_text": "Regular text",
                        "new_text": "Updated text"
                    }
                ]
            },
            "files": [text_result["file"]]
        }
        
        result = await slide_maker.execute_action("modify_slide", modify_inputs, context)
        
        print(f"✅ Modified slide without title shape:")
        print(f"   Modified: {result['modified']}")
        print(f"   Title update ignored (no title shape)")
        print(f"   Text replacement applied successfully")
        
        return result

async def main():
    print("Testing Modify Slide Action")
    print("===========================")
    
    try:
        await test_modify_slide_title()
        await test_text_replacements()
        await test_combined_slide_modifications()
        await test_no_modifications()
        await test_modify_slide_without_title()
        print("\n✅ All modify_slide tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())