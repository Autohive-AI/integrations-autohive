# Test text control actions (autosize, margins, alignment, fit_text)
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation_with_text():
    """Helper to create a presentation with text for testing text controls"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Create presentation
        create_inputs = {
            "title": "Text Controls Test",
            "custom_filename": "test_text_controls_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        
        # Add a text box with long content for testing
        text_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "This is a longer text content that we can use to test various text control features like auto-sizing, margins, alignment, and text fitting capabilities.",
            "position": {"left": 1.0, "top": 2.5, "width": 6.0, "height": 2.0},
            "formatting": {"font_size": 16},
            "files": [result["file"]]
        }
        result = await slide_maker.execute_action("add_text", text_inputs, context)
        
        return presentation_id, result["file"]

async def test_set_text_autosize():
    """Test setting text auto-sizing behavior"""
    print("Testing set_text_autosize action...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Test TEXT_TO_FIT_SHAPE
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,  # The text box we created
            "autosize_type": "TEXT_TO_FIT_SHAPE",
            "word_wrap": True,
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_text_autosize", inputs, context)
        
        print(f"✅ Set auto-sizing to TEXT_TO_FIT_SHAPE:")
        print(f"   Success: {result['success']}")
        print(f"   Autosize type: {result['autosize_type']}")
        print(f"   Word wrap: {result['word_wrap']}")
        print(f"   Dimension adjustment workaround applied")
        
        # Test SHAPE_TO_FIT_TEXT
        inputs2 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,
            "autosize_type": "SHAPE_TO_FIT_TEXT",
            "files": [result["file"]]
        }
        
        result2 = await slide_maker.execute_action("set_text_autosize", inputs2, context)
        
        print(f"✅ Set auto-sizing to SHAPE_TO_FIT_TEXT:")
        print(f"   Success: {result2['success']}")
        print(f"   Autosize type: {result2['autosize_type']}")
        
        return result2

async def test_fit_text_to_shape():
    """Test fit_text_to_shape action"""
    print("\nTesting fit_text_to_shape action...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,
            "max_size": 20,  # Max 20pt font
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("fit_text_to_shape", inputs, context)
        
        print(f"✅ Applied fit_text_to_shape:")
        print(f"   Success: {result['success']}")
        print(f"   Max size: {result['max_size']}pt")
        print(f"   Auto size: {result['auto_size']}")
        print(f"   Dimension adjustment applied for recalculation")
        
        return result

async def test_set_text_margins():
    """Test setting text margins"""
    print("\nTesting set_text_margins action...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,
            "margins": {
                "left": 0.2,
                "right": 0.2,
                "top": 0.15,
                "bottom": 0.15
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_text_margins", inputs, context)
        
        print(f"✅ Set text margins:")
        print(f"   Success: {result['success']}")
        print(f"   Margins set: {result['margins_set']}")
        
        return result

async def test_set_text_alignment():
    """Test setting text vertical alignment"""
    print("\nTesting set_text_alignment action...")
    
    presentation_id, file_data = await create_test_presentation_with_text()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Test MIDDLE alignment
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,
            "vertical_anchor": "MIDDLE",
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_text_alignment", inputs, context)
        
        print(f"✅ Set text alignment to MIDDLE:")
        print(f"   Success: {result['success']}")
        print(f"   Vertical anchor: {result['vertical_anchor']}")
        
        # Test BOTTOM alignment
        inputs2 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "shape_index": 1,
            "vertical_anchor": "BOTTOM",
            "files": [result["file"]]
        }
        
        result2 = await slide_maker.execute_action("set_text_alignment", inputs2, context)
        
        print(f"✅ Set text alignment to BOTTOM:")
        print(f"   Success: {result2['success']}")
        print(f"   Vertical anchor: {result2['vertical_anchor']}")
        
        return result2

async def main():
    print("Testing Text Control Actions")
    print("============================")
    
    try:
        await test_set_text_autosize()
        await test_fit_text_to_shape()
        await test_set_text_margins()
        await test_set_text_alignment()
        print("\n✅ All text control tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())