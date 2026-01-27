"""
Shotstack Integration Tests

To run tests, set your API key and run:
    python -m pytest tests/test_shotstack.py -v

Or run individual tests:
    python tests/test_shotstack.py
"""

import asyncio
from context import shotstack
from autohive_integrations_sdk import ExecutionContext


# Test credentials - replace with your actual API key for testing
TEST_API_KEY = "your_api_key_here"
TEST_ENVIRONMENT = "stage"  # Use 'stage' for testing (watermarked but free)


def get_test_auth():
    """Get test authentication configuration."""
    return {
        "auth_type": "Custom",
        "credentials": {
            "api_key": TEST_API_KEY,
            "environment": TEST_ENVIRONMENT
        }
    }


# ---- Edit API Tests ----

async def test_render_video():
    """Test submitting a render job."""
    auth = get_test_auth()

    inputs = {
        "timeline": {
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "title",
                                "text": "Hello World",
                                "style": "minimal"
                            },
                            "start": 0,
                            "length": 3
                        }
                    ]
                }
            ]
        },
        "output": {
            "format": "mp4",
            "resolution": "sd"
        }
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("render_video", inputs, context)
            print(f"Render Video Result: {result}")
            assert result.get('result') == True
            assert 'render_id' in result
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_get_render_status():
    """Test checking render status."""
    auth = get_test_auth()

    # First create a render to get an ID
    render_result = await test_render_video()
    if not render_result or not render_result.get('render_id'):
        print("Skipping get_render_status - no render_id available")
        return None

    inputs = {
        "render_id": render_result['render_id']
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("get_render_status", inputs, context)
            print(f"Get Render Status Result: {result}")
            assert result.get('result') == True
            assert 'status' in result
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_probe_media():
    """Test probing a media file."""
    auth = get_test_auth()

    inputs = {
        "url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("probe_media", inputs, context)
            print(f"Probe Media Result: {result}")
            assert result.get('result') == True
            assert 'metadata' in result
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Template Tests ----

async def test_create_template():
    """Test creating a template."""
    auth = get_test_auth()

    inputs = {
        "name": "Test Template",
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {
                                    "type": "title",
                                    "text": "{{TITLE}}",
                                    "style": "minimal"
                                },
                                "start": 0,
                                "length": 3
                            }
                        ]
                    }
                ]
            },
            "output": {
                "format": "mp4",
                "resolution": "sd"
            }
        }
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("create_template", inputs, context)
            print(f"Create Template Result: {result}")
            assert result.get('result') == True
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_list_templates():
    """Test listing templates."""
    auth = get_test_auth()

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("list_templates", inputs, context)
            print(f"List Templates Result: {result}")
            assert result.get('result') == True
            assert 'templates' in result
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_render_template():
    """Test rendering a template with merge fields."""
    auth = get_test_auth()

    # First create a template
    template_result = await test_create_template()
    if not template_result or not template_result.get('template_id'):
        print("Skipping render_template - no template_id available")
        return None

    inputs = {
        "template_id": template_result['template_id'],
        "merge": [
            {"find": "TITLE", "replace": "Hello from Template!"}
        ]
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("render_template", inputs, context)
            print(f"Render Template Result: {result}")
            assert result.get('result') == True
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Ingest API Tests ----

async def test_ingest_source():
    """Test ingesting a source file."""
    auth = get_test_auth()

    inputs = {
        "url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("ingest_source", inputs, context)
            print(f"Ingest Source Result: {result}")
            assert result.get('result') == True
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_list_sources():
    """Test listing ingested sources."""
    auth = get_test_auth()

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("list_sources", inputs, context)
            print(f"List Sources Result: {result}")
            assert result.get('result') == True
            assert 'sources' in result
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Create API Tests ----

async def test_create_generated_asset():
    """Test generating an AI asset."""
    auth = get_test_auth()

    # Using Shotstack's built-in text-to-speech
    inputs = {
        "provider": "shotstack",
        "options": {
            "type": "text-to-speech",
            "text": "Hello, this is a test of the Shotstack integration.",
            "voice": "Matthew"
        }
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("create_generated_asset", inputs, context)
            print(f"Create Generated Asset Result: {result}")
            assert result.get('result') == True
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Test Runner ----

async def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Probe Media", test_probe_media),
        ("List Templates", test_list_templates),
        ("List Sources", test_list_sources),
        ("Render Video", test_render_video),
        ("Create Template", test_create_template),
    ]

    results = []
    print("\n" + "=" * 60)
    print("SHOTSTACK INTEGRATION TESTS")
    print("=" * 60 + "\n")

    for name, test_func in tests:
        print(f"\n--- Running: {name} ---")
        try:
            result = await test_func()
            success = result is not None and result.get('result', False)
            results.append((name, success))
            print(f"Status: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            results.append((name, False))
            print(f"Status: FAILED - {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed

    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("Note: Replace TEST_API_KEY with your actual Shotstack API key before running tests.")
    print("Get your API key from: https://dashboard.shotstack.io/apikeys\n")
    asyncio.run(run_all_tests())
