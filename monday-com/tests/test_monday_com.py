# Testbed for Monday.com integration
import asyncio
from context import monday_com
from autohive_integrations_sdk import ExecutionContext

# Configuration - Replace these placeholder values with actual values for testing
BOARD_ID = "your_board_id_here"  # Replace with actual Monday.com board ID
ITEM_ID = "your_item_id_here"    # Replace with actual item ID for update tests

# Sample auth configuration
# Note: You'll need a valid Monday.com API token
auth = {
    "auth_type": "custom",
    "credentials": {
        "api_token": "your_api_token_here"  # Replace with actual API token
    }
}

async def test_get_boards():
    """Test retrieving boards from Monday.com."""
    print("=== TESTING GET BOARDS ===")

    try:
        inputs = {
            "limit": 10,
            "page": 1
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("get_boards", inputs, context)

            if result.get('result'):
                print(f"   ✓ Boards retrieved successfully")
                print(f"   Boards returned: {result.get('board_count')}")
                if result.get('boards'):
                    board = result.get('boards')[0]
                    print(f"   Sample board: {board.get('name')} (ID: {board.get('id')})")
            else:
                print(f"   ✗ Failed to get boards: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== GET BOARDS TEST COMPLETED ===\n")

async def test_get_items():
    """Test retrieving items from a Monday.com board."""
    print("=== TESTING GET ITEMS ===")

    try:
        inputs = {
            "board_id": BOARD_ID,
            "limit": 10,
            "page": 1
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("get_items", inputs, context)

            if result.get('result'):
                print(f"   ✓ Items retrieved successfully")
                print(f"   Items returned: {result.get('item_count')}")
                if result.get('items'):
                    item = result.get('items')[0]
                    print(f"   Sample item: {item.get('name')} (ID: {item.get('id')})")
            else:
                print(f"   ✗ Failed to get items: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== GET ITEMS TEST COMPLETED ===\n")

async def test_create_item():
    """Test creating a new item on a Monday.com board."""
    print("=== TESTING CREATE ITEM ===")

    try:
        inputs = {
            "board_id": BOARD_ID,
            "item_name": "Test Item from Integration",
            "column_values": '{"status": "Working on it"}'
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("create_item", inputs, context)

            if result.get('result'):
                print(f"   ✓ Item created successfully")
                item = result.get('item')
                if item:
                    print(f"   Created item: {item.get('name')} (ID: {item.get('id')})")
            else:
                print(f"   ✗ Failed to create item: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== CREATE ITEM TEST COMPLETED ===\n")

async def test_update_item():
    """Test updating an existing item on a Monday.com board."""
    print("=== TESTING UPDATE ITEM ===")

    try:
        inputs = {
            "board_id": BOARD_ID,
            "item_id": ITEM_ID,
            "column_values": '{"status": "Done"}'
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("update_item", inputs, context)

            if result.get('result'):
                print(f"   ✓ Item updated successfully")
                item = result.get('item')
                if item:
                    print(f"   Updated item: {item.get('name')} (ID: {item.get('id')})")
            else:
                print(f"   ✗ Failed to update item: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== UPDATE ITEM TEST COMPLETED ===\n")

async def test_create_update():
    """Test creating an update (comment) on a Monday.com item."""
    print("=== TESTING CREATE UPDATE ===")

    try:
        inputs = {
            "item_id": ITEM_ID,
            "body": "This is a test update from the integration!"
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("create_update", inputs, context)

            if result.get('result'):
                print(f"   ✓ Update created successfully")
                update = result.get('update')
                if update:
                    print(f"   Update ID: {update.get('id')}")
                    print(f"   Created by: {update.get('creator', {}).get('name')}")
            else:
                print(f"   ✗ Failed to create update: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== CREATE UPDATE TEST COMPLETED ===\n")

async def test_get_users():
    """Test retrieving users from Monday.com workspace."""
    print("=== TESTING GET USERS ===")

    try:
        inputs = {
            "limit": 10,
            "page": 1
        }

        async with ExecutionContext(auth=auth) as context:
            result = await monday_com.execute_action("get_users", inputs, context)

            if result.get('result'):
                print(f"   ✓ Users retrieved successfully")
                print(f"   Users returned: {result.get('user_count')}")
                if result.get('users'):
                    user = result.get('users')[0]
                    print(f"   Sample user: {user.get('name')} ({user.get('email')})")
            else:
                print(f"   ✗ Failed to get users: {result.get('error')}")

    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

    print("=== GET USERS TEST COMPLETED ===\n")

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MONDAY.COM INTEGRATION TEST SUITE")
    print("="*60 + "\n")

    print("NOTE: Update BOARD_ID, ITEM_ID, and api_token before running tests\n")

    await test_get_boards()
    await test_get_items()
    await test_create_item()
    await test_update_item()
    await test_create_update()
    await test_get_users()

    print("="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
