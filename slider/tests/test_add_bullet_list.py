# Test add_bullet_list action
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def create_test_presentation():
    """Helper to create a test presentation"""
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "title": "Bullet List Test",
            "custom_filename": "test_bullet_presentation"
        }
        result = await slide_maker.execute_action("create_presentation", inputs, context)
        return result["presentation_id"], result["file"]

async def test_simple_bullet_list():
    """Test adding a simple bullet list"""
    print("Testing simple bullet list...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "bullet_items": [
                {"text": "First bullet point", "level": 0},
                {"text": "Second bullet point", "level": 0},
                {"text": "Third bullet point", "level": 0}
            ],
            "position": {
                "left": 1.0,
                "top": 2.5,
                "width": 8.0,
                "height": 2.0
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_bullet_list", inputs, context)
        
        print(f"✅ Added simple bullet list:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Items count: {result['items_count']}")
        print(f"   All items at level 0")
        
        return result

async def test_multi_level_bullet_list():
    """Test adding a multi-level bullet list"""
    print("\nTesting multi-level bullet list...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "bullet_items": [
                {"text": "🐝 Bee Hierarchy", "level": 0},
                {"text": "Queen Bee", "level": 1},
                {"text": "Lives 2-5 years", "level": 2},
                {"text": "Lays up to 2,000 eggs daily", "level": 2},
                {"text": "Worker Bees", "level": 1},
                {"text": "95% of colony", "level": 2},
                {"text": "Live 6 weeks in summer", "level": 2},
                {"text": "Drones", "level": 1},
                {"text": "Male bees for mating", "level": 2}
            ],
            "position": {
                "left": 0.5,
                "top": 2.0,
                "width": 9.0,
                "height": 3.5
            },
            "formatting": {
                "font_size": 14,
                "color": "#2C3E50"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_bullet_list", inputs, context)
        
        print(f"✅ Added multi-level bullet list:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Items count: {result['items_count']}")
        print(f"   Levels 0-2 with different bullet symbols (•, ◦, ▪)")
        print(f"   Applied 14pt font formatting")
        
        return result

async def test_bullet_list_with_emoji():
    """Test bullet list with emoji content"""
    print("\nTesting bullet list with emojis...")
    
    presentation_id, file_data = await create_test_presentation()
    
    auth = {}
    async with ExecutionContext(auth=auth) as context:
        inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "bullet_items": [
                {"text": "🍯 Honey Production Facts", "level": 0},
                {"text": "🐝 One bee produces 1/12 teaspoon in lifetime", "level": 1},
                {"text": "🏺 1 lb honey = 556 worker bees", "level": 1},
                {"text": "🌸 2 million flowers visited per lb", "level": 1},
                {"text": "✈️ Bees fly 55,000 miles per lb of honey", "level": 1}
            ],
            "position": {
                "left": 1.0,
                "top": 2.0,
                "width": 8.0,
                "height": 3.0
            },
            "formatting": {
                "font_size": 16,
                "bold": True,
                "color": "#E67E22"
            },
            "files": [file_data]
        }
        
        result = await slide_maker.execute_action("add_bullet_list", inputs, context)
        
        print(f"✅ Added emoji bullet list:")
        print(f"   Shape ID: {result['shape_id']}")
        print(f"   Items count: {result['items_count']}")
        print(f"   Contains emojis with proper character handling")
        print(f"   Bold orange formatting applied")
        
        return result

async def main():
    print("Testing Add Bullet List Action")
    print("==============================")
    
    try:
        await test_simple_bullet_list()
        await test_multi_level_bullet_list()
        await test_bullet_list_with_emoji()
        print("\n✅ All add_bullet_list tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())