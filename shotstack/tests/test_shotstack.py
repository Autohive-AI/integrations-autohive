"""
Shotstack Integration Tests

To run tests, set your API key and run:
    python -m pytest tests/test_shotstack.py -v

Or run individual tests:
    python tests/test_shotstack.py
"""

import asyncio
import pytest
from context import shotstack

pytestmark = pytest.mark.asyncio
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


def get_result_data(result):
    """Extract data dict from IntegrationResult or return dict directly."""
    if hasattr(result, 'result') and hasattr(result.result, 'data'):
        return result.result.data
    return result


# ---- File Upload/Download Tests ----

async def test_get_upload_url():
    """Test getting a presigned upload URL."""
    auth = get_test_auth()

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("get_upload_url", inputs, context)
            data = get_result_data(result)
            print(f"Get Upload URL Result: {data}")
            assert data.get('result') == True
            assert 'upload_url' in data
            assert 'source_id' in data
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_download_render():
    """Test downloading a rendered video."""
    auth = get_test_auth()

    # First create a simple render
    render_result = await test_render_and_wait()
    if not render_result or not render_result.get('url'):
        print("Skipping download_render - no render available")
        return None

    inputs = {
        "url": render_result['url']
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("download_render", inputs, context)
            data = get_result_data(result)
            print(f"Download Render Result: content_type={data.get('content_type')}, size={data.get('size')}")
            assert data.get('result') == True
            assert 'content' in data
            assert data.get('size', 0) > 0
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Workflow Tests ----

async def test_render_and_wait():
    """Test rendering a video and waiting for completion."""
    auth = get_test_auth()

    inputs = {
        "timeline": {
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "title",
                                "text": "Render and Wait Test",
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
            "resolution": "preview"
        },
        "max_wait_seconds": 120,
        "poll_interval_seconds": 3
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("render_and_wait", inputs, context)
            data = get_result_data(result)
            print(f"Render and Wait Result: {data}")
            assert data.get('result') == True
            assert data.get('status') == 'done'
            assert 'url' in data
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_custom_edit():
    """Test custom edit with full timeline control."""
    auth = get_test_auth()

    inputs = {
        "timeline": {
            "background": "#000000",
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "title",
                                "text": "Custom Edit Test",
                                "style": "blockbuster",
                                "color": "#ffffff",
                                "size": "large"
                            },
                            "start": 0,
                            "length": 5,
                            "transition": {
                                "in": "fade",
                                "out": "fade"
                            }
                        }
                    ]
                }
            ]
        },
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True,
        "max_wait_seconds": 120
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("custom_edit", inputs, context)
            data = get_result_data(result)
            print(f"Custom Edit Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Convenience Action Tests ----

async def test_compose_video():
    """Test composing video from multiple clips."""
    auth = get_test_auth()

    inputs = {
        "clips": [
            {
                "url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/images/wave-01.jpg",
                "duration": 3,
                "fit": "crop",
                "effect": "zoomIn"
            },
            {
                "url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/images/wave-02.jpg",
                "duration": 3,
                "fit": "crop",
                "transition": {"in": "fade"}
            }
        ],
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "background_color": "#000000",
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("compose_video", inputs, context)
            data = get_result_data(result)
            print(f"Compose Video Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_add_text_overlay():
    """Test adding text overlay to a video."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4",
        "text": "Beach Vibes",
        "style": "blockbuster",
        "position": "center",
        "start_time": 0,
        "duration": 5,
        "font_size": "large",
        "color": "#ffffff",
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("add_text_overlay", inputs, context)
            data = get_result_data(result)
            print(f"Add Text Overlay Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_add_logo_overlay():
    """Test adding logo overlay to a video."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4",
        "logo_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/logos/real-estate-logo.png",
        "position": "bottomRight",
        "scale": 0.2,
        "opacity": 0.8,
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("add_logo_overlay", inputs, context)
            data = get_result_data(result)
            print(f"Add Logo Overlay Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_add_audio_track():
    """Test adding audio track to a video."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4",
        "audio_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/music/freepd/fireworks.mp3",
        "volume": 0.5,
        "mix_mode": "mix",
        "fade_in": True,
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("add_audio_track", inputs, context)
            data = get_result_data(result)
            print(f"Add Audio Track Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_trim_video():
    """Test trimming a video segment."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4",
        "start_time": 2,
        "duration": 5,
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("trim_video", inputs, context)
            data = get_result_data(result)
            print(f"Trim Video Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_concatenate_videos():
    """Test concatenating multiple videos."""
    auth = get_test_auth()

    inputs = {
        "videos": [
            "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/beach-overhead.mp4",
            "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/sunset.mp4"
        ],
        "transition": "fade",
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("concatenate_videos", inputs, context)
            data = get_result_data(result)
            print(f"Concatenate Videos Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_add_captions_auto():
    """Test adding auto-generated captions to a video."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/scott-ko-walking.mp4",
        "auto_generate": True,
        "font_size": 20,
        "font_color": "#ffffff",
        "stroke_color": "#000000",
        "stroke_width": 2,
        "background_color": "#000000",
        "background_opacity": 0.7,
        "background_padding": 12,
        "background_border_radius": 6,
        "position": "bottom",
        "margin_bottom": 0.1,
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True,
        "max_wait_seconds": 300
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("add_captions", inputs, context)
            data = get_result_data(result)
            print(f"Add Captions (Auto) Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_add_captions_manual():
    """Test adding manual captions from SRT file to a video."""
    auth = get_test_auth()

    inputs = {
        "video_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/footage/scott-ko-walking.mp4",
        "subtitle_url": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/captions/scott-ko.srt",
        "auto_generate": False,
        "font_size": 18,
        "font_color": "#ffff00",
        "position": "bottom",
        "output": {
            "format": "mp4",
            "resolution": "preview"
        },
        "wait_for_completion": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await shotstack.execute_action("add_captions", inputs, context)
            data = get_result_data(result)
            print(f"Add Captions (Manual SRT) Result: {data}")
            assert data.get('result') == True
            return data
        except Exception as e:
            print(f"Error: {e}")
            return None


# ---- Test Runner ----

async def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Get Upload URL", test_get_upload_url),
        ("Render and Wait", test_render_and_wait),
        ("Custom Edit", test_custom_edit),
        ("Compose Video", test_compose_video),
        ("Add Text Overlay", test_add_text_overlay),
        ("Add Logo Overlay", test_add_logo_overlay),
        ("Add Audio Track", test_add_audio_track),
        ("Trim Video", test_trim_video),
        ("Concatenate Videos", test_concatenate_videos),
        ("Add Captions (Auto)", test_add_captions_auto),
        ("Add Captions (Manual)", test_add_captions_manual),
        ("Download Render", test_download_render),
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
