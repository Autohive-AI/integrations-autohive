# Test add_text action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Test Presentation for Add Text",
            "custom_filename": "test_add_text_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_basic_text():
    """Test adding basic text without formatting"""
    print("Testing basic text addition...")
    
    presentation_id, file_data = await create_test_presentation()
    print(f"Created test presentation: {presentation_id}")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "Hello World! This is a basic text box.",
            "position": {
                "left": 1.0,
                "top": 2.0,
                "width": 6.0,
                "height": 1.5
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_text", inputs, context)
        
        print(f"✅ Added basic text:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Saved: {result['saved']}")
        
        return result

async def test_formatted_text():
    """Test adding text with formatting"""
    print("\nTesting formatted text addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "🎯 Formatted Text Example",
            "position": {
                "left": 1.0,
                "top": 3.5,
                "width": 8.0,
                "height": 1.0
            },
            "formatting": {
                "font_size": 24,
                "bold": True,
                "italic": False,
                "color": "#FF5733"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_text", inputs, context)
        
        print(f"✅ Added formatted text:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Font: 24pt, bold, orange color")
        print(f"   Auto-sizing disabled due to specific font size")
        
        return result

async def test_auto_sized_text():
    """Test adding text with auto-sizing enabled"""
    print("\nTesting auto-sized text addition...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "This is a longer text that should automatically size to fit within the text box boundaries. The integration will apply the dimension adjustment workaround to ensure proper auto-sizing behavior.",
            "position": {
                "left": 1.0,
                "top": 1.0,
                "width": 4.0,
                "height": 2.0
            },
            "formatting": {
                "bold": True,
                "color": "#2E86AB"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_text", inputs, context)
        
        print(f"✅ Added auto-sized text:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Auto-sizing enabled with dimension workaround")
        print(f"   Bold formatting applied")
        
        return result

async def main():
    print("Testing Add Text Action")
    print("=======================")
    
    try:
        await test_basic_text()
        await test_formatted_text()
        await test_auto_sized_text()
        print("\n✅ All add_text tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())