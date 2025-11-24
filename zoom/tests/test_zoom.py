# Test suite for the Zoom integration
import asyncio
from context import zoom
from autohive_integrations_sdk import ExecutionContext


async def test_list_meetings():
    """Test listing meetings for a user."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "user_id": "me",
        "type": "scheduled",
        "page_size": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("list_meetings", inputs, context)
            print("List Meetings Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Total Records: {result.get('total_records')}")
            if result.get('meetings'):
                for meeting in result['meetings'][:3]:
                    print(f"  - {meeting.get('topic')} (ID: {meeting.get('id')})")
            return result
        except Exception as e:
            print(f"Error testing list_meetings: {e}")
            return None


async def test_get_meeting():
    """Test getting meeting details."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("get_meeting", inputs, context)
            print("Get Meeting Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Topic: {result.get('topic')}")
            print(f"  Start Time: {result.get('start_time')}")
            print(f"  Join URL: {result.get('join_url')}")
            return result
        except Exception as e:
            print(f"Error testing get_meeting: {e}")
            return None


async def test_create_meeting():
    """Test creating a new meeting."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "user_id": "me",
        "topic": "Test Meeting from Autohive",
        "type": 2,  # Scheduled meeting
        "start_time": "2025-01-20T10:00:00Z",
        "duration": 60,
        "timezone": "America/New_York",
        "agenda": "Test meeting created via Autohive integration",
        "waiting_room": True,
        "join_before_host": False,
        "mute_upon_entry": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("create_meeting", inputs, context)
            print("Create Meeting Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Meeting ID: {result.get('id')}")
            print(f"  Topic: {result.get('topic')}")
            print(f"  Join URL: {result.get('join_url')}")
            print(f"  Start URL: {result.get('start_url')}")
            return result
        except Exception as e:
            print(f"Error testing create_meeting: {e}")
            return None


async def test_update_meeting():
    """Test updating a meeting."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here",
        "topic": "Updated Meeting Topic",
        "duration": 90,
        "agenda": "Updated meeting agenda"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("update_meeting", inputs, context)
            print("Update Meeting Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Meeting ID: {result.get('meeting_id')}")
            return result
        except Exception as e:
            print(f"Error testing update_meeting: {e}")
            return None


async def test_delete_meeting():
    """Test deleting a meeting."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here",
        "schedule_for_reminder": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("delete_meeting", inputs, context)
            print("Delete Meeting Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Meeting ID: {result.get('meeting_id')}")
            return result
        except Exception as e:
            print(f"Error testing delete_meeting: {e}")
            return None


async def test_list_recordings():
    """Test listing cloud recordings."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "user_id": "me",
        "page_size": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("list_recordings", inputs, context)
            print("List Recordings Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Total Records: {result.get('total_records')}")
            if result.get('meetings'):
                for meeting in result['meetings'][:3]:
                    print(f"  - {meeting.get('topic')} ({meeting.get('recording_count')} files)")
            return result
        except Exception as e:
            print(f"Error testing list_recordings: {e}")
            return None


async def test_get_meeting_recordings():
    """Test getting recordings for a specific meeting."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("get_meeting_recordings", inputs, context)
            print("Get Meeting Recordings Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Topic: {result.get('topic')}")
            print(f"  Total Size: {result.get('total_size')} bytes")
            if result.get('recording_files'):
                for rf in result['recording_files']:
                    print(f"  - {rf.get('file_type')}: {rf.get('recording_type')}")
            return result
        except Exception as e:
            print(f"Error testing get_meeting_recordings: {e}")
            return None


async def test_get_meeting_transcript():
    """Test getting transcript for a meeting."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("get_meeting_transcript", inputs, context)
            print("Get Meeting Transcript Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Topic: {result.get('topic')}")
            print(f"  Transcript URL: {result.get('transcript_url')}")
            if result.get('transcript_segments'):
                print(f"  Segments: {len(result['transcript_segments'])}")
                for segment in result['transcript_segments'][:3]:
                    print(f"    - {segment.get('speaker')}: {segment.get('text')[:50]}...")
            return result
        except Exception as e:
            print(f"Error testing get_meeting_transcript: {e}")
            return None


async def test_list_users():
    """Test listing users in the account."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "status": "active",
        "page_size": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("list_users", inputs, context)
            print("List Users Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Total Records: {result.get('total_records')}")
            if result.get('users'):
                for user in result['users'][:3]:
                    print(f"  - {user.get('first_name')} {user.get('last_name')} ({user.get('email')})")
            return result
        except Exception as e:
            print(f"Error testing list_users: {e}")
            return None


async def test_get_user():
    """Test getting user details."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "user_id": "me"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("get_user", inputs, context)
            print("Get User Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Name: {result.get('first_name')} {result.get('last_name')}")
            print(f"  Email: {result.get('email')}")
            print(f"  Timezone: {result.get('timezone')}")
            print(f"  PMI: {result.get('pmi')}")
            return result
        except Exception as e:
            print(f"Error testing get_user: {e}")
            return None


async def test_get_meeting_participants():
    """Test getting meeting participants."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here",
        "page_size": 30
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("get_meeting_participants", inputs, context)
            print("Get Meeting Participants Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Total Records: {result.get('total_records')}")
            if result.get('participants'):
                for participant in result['participants'][:5]:
                    print(f"  - {participant.get('name')} (Duration: {participant.get('duration')}s)")
            return result
        except Exception as e:
            print(f"Error testing get_meeting_participants: {e}")
            return None


async def test_add_meeting_registrant():
    """Test adding a meeting registrant."""
    auth = {
        "credentials": {
            "access_token": "your_access_token_here"
        }
    }

    inputs = {
        "meeting_id": "your_meeting_id_here",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "auto_approve": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await zoom.execute_action("add_meeting_registrant", inputs, context)
            print("Add Meeting Registrant Result:")
            print(f"  Success: {result.get('result')}")
            print(f"  Registrant ID: {result.get('registrant_id')}")
            print(f"  Join URL: {result.get('join_url')}")
            return result
        except Exception as e:
            print(f"Error testing add_meeting_registrant: {e}")
            return None


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Zoom Integration")
    print("=" * 60)
    print()
    print("Note: Replace 'your_access_token_here' and 'your_meeting_id_here'")
    print("with actual values to run these tests against the Zoom API.")
    print()

    # Uncomment the tests you want to run:
    # await test_list_meetings()
    # await test_get_meeting()
    # await test_create_meeting()
    # await test_update_meeting()
    # await test_delete_meeting()
    # await test_list_recordings()
    # await test_get_meeting_recordings()
    # await test_get_meeting_transcript()
    # await test_list_users()
    # await test_get_user()
    # await test_get_meeting_participants()
    # await test_add_meeting_registrant()

    print()
    print("=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
