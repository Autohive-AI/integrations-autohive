# Test add_slide action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Test Presentation for Add Slide",
            "custom_filename": "test_add_slide_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_add_slide():
    """Test adding a blank slide to existing presentation"""
    print("Testing add_slide action...")
    
    # Create a test presentation first
    presentation_id, file_data = await create_test_presentation()
    print(f"Created test presentation: {presentation_id}")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_slide", inputs, context)
        
        print(f"✅ Added blank slide:")
        print(f"   New slide index: {result['slide_index']}")
        print(f"   Total slides: {result['slide_count']}")
        print(f"   Saved: {result['saved']}")
        
        return result

async def test_add_multiple_slides():
    """Test adding multiple slides"""
    print("\nTesting multiple slide addition...")
    
    # Create a test presentation first
    presentation_id, file_data = await create_test_presentation()
    print(f"Created test presentation: {presentation_id}")
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Add first slide
        inputs1 = {
            "presentation_id": presentation_id,
            "files": [file_data]
        }
        result1 = await slide_maker.execute_action("add_slide", inputs1, context)
        
        # Add second slide using updated file
        inputs2 = {
            "presentation_id": presentation_id,
            "files": [result1["file"]]
        }
        result2 = await slide_maker.execute_action("add_slide", inputs2, context)
        
        print(f"✅ Added multiple slides:")
        print(f"   First slide index: {result1['slide_index']}")
        print(f"   Second slide index: {result2['slide_index']}")
        print(f"   Total slides: {result2['slide_count']}")
        
        return result2

async def main():
    print("Testing Add Slide Action")
    print("========================")
    
    try:
        await test_add_slide()
        await test_add_multiple_slides()
        print("\n✅ All add_slide tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())