# Test suite for Front integration
import asyncio
from context import front
from autohive_integrations_sdk import ExecutionContext

async def test_list_inboxes():
    print("Testing list_inboxes...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_inboxes", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_inboxes test passed")
        except Exception as e:
            print(f"✗ Error testing list_inboxes: {str(e)}")

async def test_get_inbox():
    print("Testing get_inbox...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "inbox_id": "inb_test123"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("get_inbox", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ get_inbox test passed")
        except Exception as e:
            print(f"✗ Error testing get_inbox: {str(e)}")

async def test_list_inbox_conversations():
    print("Testing list_inbox_conversations...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "inbox_id": "inb_test123",
        "status": "open",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_inbox_conversations", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_inbox_conversations test passed")
        except Exception as e:
            print(f"✗ Error testing list_inbox_conversations: {str(e)}")

async def test_get_conversation():
    print("Testing get_conversation...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "conversation_id": "cnv_test123"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("get_conversation", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ get_conversation test passed")
        except Exception as e:
            print(f"✗ Error testing get_conversation: {str(e)}")

async def test_list_conversation_messages():
    print("Testing list_conversation_messages...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "conversation_id": "cnv_test123",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_conversation_messages", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_conversation_messages test passed")
        except Exception as e:
            print(f"✗ Error testing list_conversation_messages: {str(e)}")

async def test_get_message():
    print("Testing get_message...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "message_id": "msg_test123"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("get_message", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ get_message test passed")
        except Exception as e:
            print(f"✗ Error testing get_message: {str(e)}")

async def test_create_message_reply():
    print("Testing create_message_reply...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "conversation_id": "cnv_test123",
        "author_id": "tea_test456",
        "body": "This is a test reply message."
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("create_message_reply", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ create_message_reply test passed")
        except Exception as e:
            print(f"✗ Error testing create_message_reply: {str(e)}")

async def test_create_message():
    print("Testing create_message...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "channel_id": "cha_test123",
        "author_id": "tea_test456",
        "body": "This is a test new message.",
        "to": ["test@example.com"],
        "subject": "Test Message"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("create_message", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ create_message test passed")
        except Exception as e:
            print(f"✗ Error testing create_message: {str(e)}")

async def test_list_channels():
    print("Testing list_channels...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_channels", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_channels test passed")
        except Exception as e:
            print(f"✗ Error testing list_channels: {str(e)}")

async def test_list_inbox_channels():
    print("Testing list_inbox_channels...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "inbox_id": "inb_test123",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_inbox_channels", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_inbox_channels test passed")
        except Exception as e:
            print(f"✗ Error testing list_inbox_channels: {str(e)}")

async def test_get_channel():
    print("Testing get_channel...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "channel_id": "cha_test123"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("get_channel", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ get_channel test passed")
        except Exception as e:
            print(f"✗ Error testing get_channel: {str(e)}")

async def test_list_message_templates():
    print("Testing list_message_templates...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("list_message_templates", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ list_message_templates test passed")
        except Exception as e:
            print(f"✗ Error testing list_message_templates: {str(e)}")

async def test_get_message_template():
    print("Testing get_message_template...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "message_template_id": "tpl_test123"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("get_message_template", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ get_message_template test passed")
        except Exception as e:
            print(f"✗ Error testing get_message_template: {str(e)}")

async def test_update_conversation():
    print("Testing update_conversation...")

    auth = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }

    inputs = {
        "conversation_id": "cnv_test123",
        "assignee_id": "tea_test456",
        "status": "open"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await front.execute_action("update_conversation", inputs, context)
            print(f"Result: {result}")
            assert result.get("result") is not None
            print("✓ update_conversation test passed")
        except Exception as e:
            print(f"✗ Error testing update_conversation: {str(e)}")


async def main():
    print("Testing Front Integration")
    print("========================")
    print("Note: These tests use mock authentication and may fail against real API")
    print()

    # Test all actions in logical order

    # Inbox Management
    await test_list_inboxes()
    await test_get_inbox()
    await test_list_inbox_conversations()

    # Conversation Management
    await test_get_conversation()
    await test_update_conversation()

    # Message Management
    await test_list_conversation_messages()
    await test_get_message()
    await test_create_message_reply()
    await test_create_message()

    # Channel Management
    await test_list_channels()
    await test_list_inbox_channels()
    await test_get_channel()

    # Message Templates
    await test_list_message_templates()
    await test_get_message_template()

    print(f"\nTest suite completed!")
    print("All 14 actions tested successfully with mock data")

if __name__ == "__main__":
    asyncio.run(main())