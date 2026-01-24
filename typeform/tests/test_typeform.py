# Test suite for Typeform integration
import asyncio
from context import typeform
from autohive_integrations_sdk import ExecutionContext


# ---- User Tests ----

async def test_get_current_user():
    """Test getting current user info."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_current_user", {}, context)
            print(f"Get Current User Result: {result}")
            assert result.data.get('result') == True
            assert 'user' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_current_user: {e}")
            return None


# ---- Form Tests ----

async def test_list_forms():
    """Test listing forms."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"page_size": 10}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_forms", inputs, context)
            print(f"List Forms Result: {result}")
            assert result.data.get('result') == True
            assert 'forms' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_forms: {e}")
            return None


async def test_get_form():
    """Test getting form details."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_form", inputs, context)
            print(f"Get Form Result: {result}")
            assert result.data.get('result') == True
            assert 'form' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_form: {e}")
            return None


async def test_create_form():
    """Test creating a form."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {
        "title": "Test Form",
        "fields": [
            {
                "type": "short_text",
                "title": "What is your name?"
            }
        ]
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("create_form", inputs, context)
            print(f"Create Form Result: {result}")
            assert result.data.get('result') == True
            assert 'form' in result.data
            return result
        except Exception as e:
            print(f"Error testing create_form: {e}")
            return None


async def test_update_form():
    """Test updating a form."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {
        "form_id": "your_form_id_here",
        "title": "Updated Test Form"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("update_form", inputs, context)
            print(f"Update Form Result: {result}")
            assert result.data.get('result') == True
            assert 'form' in result.data
            return result
        except Exception as e:
            print(f"Error testing update_form: {e}")
            return None


async def test_delete_form():
    """Test deleting a form."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_to_delete"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_form", inputs, context)
            print(f"Delete Form Result: {result}")
            assert result.data.get('result') == True
            assert result.data.get('deleted') == True
            return result
        except Exception as e:
            print(f"Error testing delete_form: {e}")
            return None


# ---- Response Tests ----

async def test_list_responses():
    """Test listing form responses."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_here", "page_size": 25}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_responses", inputs, context)
            print(f"List Responses Result: {result}")
            assert result.data.get('result') == True
            assert 'responses' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_responses: {e}")
            return None


async def test_delete_responses():
    """Test deleting form responses."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {
        "form_id": "your_form_id_here",
        "included_response_ids": "response_id_1,response_id_2"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_responses", inputs, context)
            print(f"Delete Responses Result: {result}")
            assert result.data.get('result') == True
            return result
        except Exception as e:
            print(f"Error testing delete_responses: {e}")
            return None


# ---- Workspace Tests ----

async def test_list_workspaces():
    """Test listing workspaces."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_workspaces", inputs, context)
            print(f"List Workspaces Result: {result}")
            assert result.data.get('result') == True
            assert 'workspaces' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_workspaces: {e}")
            return None


async def test_get_workspace():
    """Test getting workspace details."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"workspace_id": "your_workspace_id_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_workspace", inputs, context)
            print(f"Get Workspace Result: {result}")
            assert result.data.get('result') == True
            assert 'workspace' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_workspace: {e}")
            return None


async def test_create_workspace():
    """Test creating a workspace."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"name": "Test Workspace"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("create_workspace", inputs, context)
            print(f"Create Workspace Result: {result}")
            assert result.data.get('result') == True
            assert 'workspace' in result.data
            return result
        except Exception as e:
            print(f"Error testing create_workspace: {e}")
            return None


async def test_update_workspace():
    """Test updating a workspace."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"workspace_id": "your_workspace_id_here", "name": "Updated Workspace Name"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("update_workspace", inputs, context)
            print(f"Update Workspace Result: {result}")
            assert result.data.get('result') == True
            assert 'workspace' in result.data
            return result
        except Exception as e:
            print(f"Error testing update_workspace: {e}")
            return None


async def test_delete_workspace():
    """Test deleting a workspace."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"workspace_id": "your_workspace_id_to_delete"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_workspace", inputs, context)
            print(f"Delete Workspace Result: {result}")
            assert result.data.get('result') == True
            return result
        except Exception as e:
            print(f"Error testing delete_workspace: {e}")
            return None


# ---- Theme Tests ----

async def test_list_themes():
    """Test listing themes."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_themes", inputs, context)
            print(f"List Themes Result: {result}")
            assert result.data.get('result') == True
            assert 'themes' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_themes: {e}")
            return None


async def test_get_theme():
    """Test getting theme details."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"theme_id": "your_theme_id_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_theme", inputs, context)
            print(f"Get Theme Result: {result}")
            assert result.data.get('result') == True
            assert 'theme' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_theme: {e}")
            return None


async def test_create_theme():
    """Test creating a theme."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {
        "name": "Test Theme",
        "colors": {
            "question": "#3D3D3D",
            "answer": "#4FB0AE",
            "button": "#4FB0AE",
            "background": "#FFFFFF"
        }
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("create_theme", inputs, context)
            print(f"Create Theme Result: {result}")
            assert result.data.get('result') == True
            assert 'theme' in result.data
            return result
        except Exception as e:
            print(f"Error testing create_theme: {e}")
            return None


async def test_delete_theme():
    """Test deleting a theme."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"theme_id": "your_theme_id_to_delete"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_theme", inputs, context)
            print(f"Delete Theme Result: {result}")
            assert result.data.get('result') == True
            return result
        except Exception as e:
            print(f"Error testing delete_theme: {e}")
            return None


# ---- Image Tests ----

async def test_list_images():
    """Test listing images."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_images", inputs, context)
            print(f"List Images Result: {result}")
            assert result.data.get('result') == True
            assert 'images' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_images: {e}")
            return None


async def test_get_image():
    """Test getting image details."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"image_id": "your_image_id_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_image", inputs, context)
            print(f"Get Image Result: {result}")
            assert result.data.get('result') == True
            assert 'image' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_image: {e}")
            return None


async def test_delete_image():
    """Test deleting an image."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"image_id": "your_image_id_to_delete"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_image", inputs, context)
            print(f"Delete Image Result: {result}")
            assert result.data.get('result') == True
            return result
        except Exception as e:
            print(f"Error testing delete_image: {e}")
            return None


# ---- Webhook Tests ----

async def test_list_webhooks():
    """Test listing webhooks."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("list_webhooks", inputs, context)
            print(f"List Webhooks Result: {result}")
            assert result.data.get('result') == True
            assert 'webhooks' in result.data
            return result
        except Exception as e:
            print(f"Error testing list_webhooks: {e}")
            return None


async def test_get_webhook():
    """Test getting webhook details."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_here", "tag": "your_webhook_tag"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("get_webhook", inputs, context)
            print(f"Get Webhook Result: {result}")
            assert result.data.get('result') == True
            assert 'webhook' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_webhook: {e}")
            return None


async def test_create_webhook():
    """Test creating a webhook."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {
        "form_id": "your_form_id_here",
        "tag": "test_webhook",
        "url": "https://example.com/webhook",
        "enabled": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("create_webhook", inputs, context)
            print(f"Create Webhook Result: {result}")
            assert result.data.get('result') == True
            assert 'webhook' in result.data
            return result
        except Exception as e:
            print(f"Error testing create_webhook: {e}")
            return None


async def test_delete_webhook():
    """Test deleting a webhook."""
    auth = {
        "auth_type": "PlatformOauth2",
        "credentials": {"access_token": "your_access_token_here"}
    }
    inputs = {"form_id": "your_form_id_here", "tag": "webhook_tag_to_delete"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await typeform.execute_action("delete_webhook", inputs, context)
            print(f"Delete Webhook Result: {result}")
            assert result.data.get('result') == True
            return result
        except Exception as e:
            print(f"Error testing delete_webhook: {e}")
            return None


# Main test runner
async def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Typeform Integration Test Suite")
    print("=" * 60)

    test_functions = [
        # User
        ("Get Current User", test_get_current_user),
        # Forms
        ("List Forms", test_list_forms),
        ("Get Form", test_get_form),
        ("Create Form", test_create_form),
        ("Update Form", test_update_form),
        ("Delete Form", test_delete_form),
        # Responses
        ("List Responses", test_list_responses),
        ("Delete Responses", test_delete_responses),
        # Workspaces
        ("List Workspaces", test_list_workspaces),
        ("Get Workspace", test_get_workspace),
        ("Create Workspace", test_create_workspace),
        ("Update Workspace", test_update_workspace),
        ("Delete Workspace", test_delete_workspace),
        # Themes
        ("List Themes", test_list_themes),
        ("Get Theme", test_get_theme),
        ("Create Theme", test_create_theme),
        ("Delete Theme", test_delete_theme),
        # Images
        ("List Images", test_list_images),
        ("Get Image", test_get_image),
        ("Delete Image", test_delete_image),
        # Webhooks
        ("List Webhooks", test_list_webhooks),
        ("Get Webhook", test_get_webhook),
        ("Create Webhook", test_create_webhook),
        ("Delete Webhook", test_delete_webhook),
    ]

    results = []
    for test_name, test_func in test_functions:
        print(f"\n{'-' * 60}")
        print(f"Running: {test_name}")
        print(f"{'-' * 60}")
        result = await test_func()
        results.append((test_name, result is not None))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
