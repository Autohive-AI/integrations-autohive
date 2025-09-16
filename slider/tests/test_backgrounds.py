# Test background-related actions
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Background Test",
            "custom_filename": "test_background_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_solid_color_background():
    """Test setting solid color background"""
    print("Testing solid color background...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Test hex color
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "color": "#3498DB",  # Blue
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_slide_background_color", inputs, context)
        
        print(f"✅ Set hex color background:")
        print(f"   Success: {result['success']}")
        print(f"   Color set: {result['color_set']}")
        
        # Test RGB color
        rgb_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "color": {"rgb": [231, 76, 60]},  # Red
            "files": [result["file"]]
        }
        
        rgb_result = await slide_maker.execute_action("set_slide_background_color", rgb_inputs, context)
        
        print(f"✅ Set RGB color background:")
        print(f"   Success: {rgb_result['success']}")
        print(f"   Color set: {rgb_result['color_set']}")
        
        return rgb_result

async def test_gradient_background():
    """Test setting gradient background"""
    print("\nTesting gradient background...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "angle": 45,  # Diagonal gradient
            "gradient_stops": [
                {
                    "position": 0.0,
                    "color": {"rgb": [52, 152, 219]}  # Blue
                },
                {
                    "position": 1.0,
                    "color": {"rgb": [155, 89, 182]}  # Purple
                }
            ],
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_slide_background_gradient", inputs, context)
        
        print(f"✅ Set gradient background:")
        print(f"   Success: {result['success']}")
        print(f"   Gradient angle: {result['gradient_angle']}°")
        print(f"   Gradient stops applied: {result['gradient_stops_applied']}")
        
        return result

async def test_reset_background():
    """Test resetting background to master"""
    print("\nTesting background reset...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # First set a color
        color_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "color": "#E74C3C",
            "files": [file_data]
        }
        color_result = await slide_maker.execute_action("set_slide_background_color", color_inputs, context)
        
        # Then reset it
        reset_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "files": [color_result["file"]]
        }
        
        result = await slide_maker.execute_action("reset_slide_background", reset_inputs, context)
        
        print(f"✅ Reset background:")
        print(f"   Success: {result['success']}")
        print(f"   Follow master background: {result['follow_master_background']}")
        print(f"   Note: {result['note']}")
        
        return result

async def test_theme_color_background():
    """Test setting theme color background"""
    print("\nTesting theme color background...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "color": {"theme_color": "ACCENT_1"},
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("set_slide_background_color", inputs, context)
        
        print(f"✅ Set theme color background:")
        print(f"   Success: {result['success']}")
        print(f"   Color set: {result['color_set']}")
        
        return result

async def main():
    print("Testing Background Actions")
    print("==========================")
    
    try:
        await test_solid_color_background()
        await test_gradient_background()
        await test_reset_background()
        await test_theme_color_background()
        print("\n✅ All background tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())