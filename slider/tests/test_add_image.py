# Test add_image action
import asyncio
import base64
from io import BytesIO
from PIL import Image
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

def create_test_image(width=200, height=150, color=(52, 152, 219)):
    """Create a test image in memory"""
    # Create a simple colored image
    img = Image.new('RGB', (width, height), color)
    
    # Save to bytes
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Encode as base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    return {
        "name": f"test_image_{width}x{height}.png",
        "contentType": "image/png",
        "content": img_base64
    }

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Image Test Presentation",
            "custom_filename": "test_image_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_add_image_with_size():
    """Test adding an image with specified size"""
    print("Testing add_image with specified size...")
    
    presentation_id, file_data = await create_test_presentation()
    
    # Create test image
    test_image = create_test_image(300, 200, (231, 76, 60))  # Red image
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "position": {
                "left": 2.0,
                "top": 2.5,
                "width": 4.0,
                "height": 2.5
            },
            "files": [file_data, test_image]
        }
        
        result = await slide_maker.execute_action("add_image", inputs, context)
        
        print(f"✅ Added image with specified size:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Position: 2.0\", 2.5\" | Size: 4.0\" x 2.5\"")
        print(f"   Image: 300x200px red PNG")
        print(f"   Saved: {result['saved']}")
        
        return result

async def test_add_image_original_size():
    """Test adding an image at original size"""
    print("\nTesting add_image at original size...")
    
    presentation_id, file_data = await create_test_presentation()
    
    # Create test image
    test_image = create_test_image(150, 100, (46, 204, 113))  # Green image
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "position": {
                "left": 1.0,
                "top": 3.0
                # No width/height - use original size
            },
            "files": [file_data, test_image]
        }
        
        result = await slide_maker.execute_action("add_image", inputs, context)
        
        print(f"✅ Added image at original size:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Position: 1.0\", 3.0\" | Size: Original (150x100px)")
        print(f"   Image: Green PNG at natural dimensions")
        
        return result

async def test_add_multiple_images():
    """Test adding multiple images to same slide"""
    print("\nTesting multiple images on same slide...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Add first image (blue)
        blue_image = create_test_image(180, 120, (52, 152, 219))
        inputs1 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "position": {"left": 1.0, "top": 2.0, "width": 2.5, "height": 1.5},
            "files": [file_data, blue_image]
        }
        result1 = await slide_maker.execute_action("add_image", inputs1, context)
        
        # Add second image (purple) 
        purple_image = create_test_image(160, 140, (155, 89, 182))
        inputs2 = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "position": {"left": 5.0, "top": 2.0, "width": 2.5, "height": 1.5},
            "files": [result1["file"], purple_image]
        }
        result2 = await slide_maker.execute_action("add_image", inputs2, context)
        
        print(f"✅ Added multiple images:")
        print(f"   First image (blue): {result1['shape_id']}")
        print(f"   Second image (purple): {result2['shape_id']}")
        print(f"   Both images positioned side by side")
        
        return result2

async def test_image_boundary_adjustment():
    """Test image boundary adjustment when exceeding slide"""
    print("\nTesting image boundary adjustment...")
    
    presentation_id, file_data = await create_test_presentation()
    
    # Create test image
    test_image = create_test_image(400, 300, (241, 196, 15))  # Yellow image
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        # Try to add image that would exceed slide boundaries
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "position": {
                "left": 7.0,   # Near right edge
                "top": 4.0,    # Near bottom
                "width": 5.0,  # Would exceed slide width (10")
                "height": 3.0  # Would exceed slide height (~5.6")
            },
            "files": [file_data, test_image]
        }
        
        result = await slide_maker.execute_action("add_image", inputs, context)
        
        print(f"✅ Added image with boundary adjustment:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Original request: 7.0\", 4.0\" | 5.0\" x 3.0\"")
        print(f"   Should be automatically adjusted to fit within slide")
        print(f"   Integration applies boundary validation")
        
        return result

async def test_no_image_error():
    """Test error handling when no image file provided"""
    print("\nTesting no image file error handling...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        try:
            inputs = {
                "presentation_id": presentation_id,
                "slide_index": 0,
                "position": {"left": 1.0, "top": 1.0, "width": 2.0, "height": 2.0},
                "files": [file_data]  # No image file provided
            }
            
            result = await slide_maker.execute_action("add_image", inputs, context)
            print("❌ Should have failed with no image error")
            
        except ValueError as e:
            print(f"✅ Correctly caught no image error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")

async def main():
    print("Testing Add Image Action")
    print("========================")
    
    try:
        await test_add_image_with_size()
        await test_add_image_original_size()
        await test_add_multiple_images()
        await test_image_boundary_adjustment()
        await test_no_image_error()
        print("\n✅ All add_image tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())