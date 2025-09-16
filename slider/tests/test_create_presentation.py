# Test create_presentation action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def test_create_blank_presentation():
    """Test creating a blank presentation"""
    print("Testing blank presentation creation...")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "custom_filename": "test_blank_presentation"
        }
        
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        
        print(f"✅ Created presentation: {result['presentation_id']}")
        print(f"   Slide count: {result['slide_count']}")
        print(f"   Saved: {result['saved']}")
        print(f"   File path: {result['file_path']}")
        
        return result

async def test_create_presentation_with_title():
    """Test creating presentation with title and subtitle"""
    print("\nTesting presentation with title and subtitle...")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Test Presentation",
            "subtitle": "Created by Autohive Integration Tests",
            "custom_filename": "test_titled_presentation"
        }
        
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        
        print(f"✅ Created titled presentation: {result['presentation_id']}")
        print(f"   Slide count: {result['slide_count']}")
        print(f"   Title and subtitle added as text boxes on blank slide")
        
        return result

async def main():
    print("Testing Create Presentation Action")
    print("==================================")
    
    try:
        await test_create_blank_presentation()
        await test_create_presentation_with_title()
        print("\n✅ All create_presentation tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())