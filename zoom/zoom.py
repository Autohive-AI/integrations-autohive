from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import quote
import re

# Load integration from config.json
zoom = Integration.load()

# ---- Constants ----
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

# ---- Helper Functions ----

def get_headers() -> Dict[str, str]:
    """Build standard headers for Zoom API requests."""
    return {
        "Content-Type": "application/json"
    }


def encode_meeting_id(meeting_id: str) -> str:
    """
    Encode meeting ID for URL path.
    UUIDs starting with '/' or containing '//' need double URL encoding.
    """
    if meeting_id.startswith('/') or '//' in meeting_id:
        return quote(quote(meeting_id, safe=''), safe='')
    return meeting_id


def parse_vtt_transcript(vtt_content: str) -> List[Dict[str, Any]]:
    """
    Parse VTT (WebVTT) transcript format into structured segments.

    Args:
        vtt_content: Raw VTT file content

    Returns:
        List of transcript segments with speaker, timestamps, and text
    """
    segments = []
    lines = vtt_content.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for timestamp lines (format: 00:00:00.000 --> 00:00:05.000)
        timestamp_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
        match = re.match(timestamp_pattern, line)

        if match:
            start_time = match.group(1)
            end_time = match.group(2)

            # Collect text lines until next timestamp or empty line
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(timestamp_pattern, lines[i]):
                text_lines.append(lines[i].strip())
                i += 1

            if text_lines:
                text = ' '.join(text_lines)

                # Try to extract speaker from text (format: "Speaker Name: text")
                speaker_match = re.match(r'^([^:]+):\s*(.+)$', text)
                if speaker_match:
                    speaker = speaker_match.group(1).strip()
                    spoken_text = speaker_match.group(2).strip()
                else:
                    speaker = "Unknown"
                    spoken_text = text

                segments.append({
                    "speaker": speaker,
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": spoken_text
                })
        else:
            i += 1

    return segments


# ---- API Client Class ----

class ZoomAPIClient:
    """Client for interacting with the Zoom API."""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.base_url = ZOOM_API_BASE_URL

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Zoom API.

        Args:
            endpoint: API endpoint path (without base URL)
            method: HTTP method (GET, POST, PATCH, DELETE)
            params: Query parameters
            data: Request body for POST/PATCH requests

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        headers = get_headers()

        if method == "GET":
            return await self.context.fetch(url, params=params, headers=headers)
        elif method == "POST":
            return await self.context.fetch(url, method="POST", json=data, headers=headers)
        elif method == "PATCH":
            return await self.context.fetch(url, method="PATCH", json=data, headers=headers)
        elif method == "DELETE":
            response = await self.context.fetch(url, method="DELETE", params=params, headers=headers)
            # DELETE typically returns empty response on success
            return response if response else {"success": True}
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


# ---- Action Handlers ----

@zoom.action("list_meetings")
class ListMeetingsAction(ActionHandler):
    """List all scheduled meetings for a user."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            user_id = inputs.get("user_id", "me")

            params = {
                "type": inputs.get("type", "scheduled"),
                "page_size": min(inputs.get("page_size", 30), 300)
            }

            if inputs.get("next_page_token"):
                params["next_page_token"] = inputs["next_page_token"]

            response = await client._make_request(f"users/{user_id}/meetings", params=params)

            # Transform meetings to consistent format
            meetings = []
            for meeting in response.get("meetings", []):
                meetings.append({
                    "id": meeting.get("id"),
                    "uuid": meeting.get("uuid", ""),
                    "topic": meeting.get("topic", ""),
                    "type": meeting.get("type"),
                    "start_time": meeting.get("start_time", ""),
                    "duration": meeting.get("duration", 0),
                    "timezone": meeting.get("timezone", ""),
                    "join_url": meeting.get("join_url", ""),
                    "created_at": meeting.get("created_at", "")
                })

            return {
                "meetings": meetings,
                "next_page_token": response.get("next_page_token"),
                "page_count": response.get("page_count", 0),
                "page_size": response.get("page_size", 0),
                "total_records": response.get("total_records", len(meetings)),
                "result": True
            }
        except Exception as e:
            return {
                "meetings": [],
                "next_page_token": None,
                "page_count": 0,
                "page_size": 0,
                "total_records": 0,
                "result": False,
                "error": str(e)
            }


@zoom.action("get_meeting")
class GetMeetingAction(ActionHandler):
    """Retrieve detailed information about a specific meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            response = await client._make_request(f"meetings/{meeting_id}")

            return {
                "id": response.get("id"),
                "uuid": response.get("uuid", ""),
                "topic": response.get("topic", ""),
                "type": response.get("type"),
                "status": response.get("status", ""),
                "start_time": response.get("start_time", ""),
                "duration": response.get("duration", 0),
                "timezone": response.get("timezone", ""),
                "agenda": response.get("agenda", ""),
                "created_at": response.get("created_at", ""),
                "start_url": response.get("start_url", ""),
                "join_url": response.get("join_url", ""),
                "password": response.get("password", ""),
                "host_id": response.get("host_id", ""),
                "host_email": response.get("host_email", ""),
                "settings": response.get("settings", {}),
                "result": True
            }
        except Exception as e:
            return {
                "id": None,
                "uuid": "",
                "topic": "",
                "type": None,
                "status": "",
                "start_time": "",
                "duration": 0,
                "timezone": "",
                "agenda": "",
                "created_at": "",
                "start_url": "",
                "join_url": "",
                "password": "",
                "host_id": "",
                "host_email": "",
                "settings": {},
                "result": False,
                "error": str(e)
            }


@zoom.action("create_meeting")
class CreateMeetingAction(ActionHandler):
    """Create a new Zoom meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            user_id = inputs.get("user_id", "me")

            # Build meeting data
            meeting_data = {
                "topic": inputs["topic"],
                "type": inputs.get("type", 2),  # Default to scheduled meeting
                "duration": inputs.get("duration", 60)
            }

            # Add optional fields
            if inputs.get("start_time"):
                meeting_data["start_time"] = inputs["start_time"]

            if inputs.get("timezone"):
                meeting_data["timezone"] = inputs["timezone"]

            if inputs.get("password"):
                meeting_data["password"] = inputs["password"]

            if inputs.get("agenda"):
                meeting_data["agenda"] = inputs["agenda"]

            # Build settings
            settings = {}
            if "waiting_room" in inputs:
                settings["waiting_room"] = inputs["waiting_room"]
            if "join_before_host" in inputs:
                settings["join_before_host"] = inputs["join_before_host"]
            if "mute_upon_entry" in inputs:
                settings["mute_upon_entry"] = inputs["mute_upon_entry"]
            if inputs.get("auto_recording"):
                settings["auto_recording"] = inputs["auto_recording"]

            if settings:
                meeting_data["settings"] = settings

            response = await client._make_request(
                f"users/{user_id}/meetings",
                method="POST",
                data=meeting_data
            )

            return {
                "id": response.get("id"),
                "uuid": response.get("uuid", ""),
                "topic": response.get("topic", ""),
                "start_time": response.get("start_time", ""),
                "duration": response.get("duration", 0),
                "start_url": response.get("start_url", ""),
                "join_url": response.get("join_url", ""),
                "password": response.get("password", ""),
                "result": True
            }
        except Exception as e:
            return {
                "id": None,
                "uuid": "",
                "topic": "",
                "start_time": "",
                "duration": 0,
                "start_url": "",
                "join_url": "",
                "password": "",
                "result": False,
                "error": str(e)
            }


@zoom.action("update_meeting")
class UpdateMeetingAction(ActionHandler):
    """Update an existing meeting's details."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            # Build update data
            update_data = {}

            if inputs.get("topic"):
                update_data["topic"] = inputs["topic"]
            if inputs.get("start_time"):
                update_data["start_time"] = inputs["start_time"]
            if inputs.get("duration"):
                update_data["duration"] = inputs["duration"]
            if inputs.get("timezone"):
                update_data["timezone"] = inputs["timezone"]
            if inputs.get("password"):
                update_data["password"] = inputs["password"]
            if inputs.get("agenda"):
                update_data["agenda"] = inputs["agenda"]

            # Build settings updates
            settings = {}
            if "waiting_room" in inputs:
                settings["waiting_room"] = inputs["waiting_room"]
            if "join_before_host" in inputs:
                settings["join_before_host"] = inputs["join_before_host"]
            if "mute_upon_entry" in inputs:
                settings["mute_upon_entry"] = inputs["mute_upon_entry"]
            if inputs.get("auto_recording"):
                settings["auto_recording"] = inputs["auto_recording"]

            if settings:
                update_data["settings"] = settings

            await client._make_request(
                f"meetings/{meeting_id}",
                method="PATCH",
                data=update_data
            )

            return {
                "meeting_id": inputs["meeting_id"],
                "result": True
            }
        except Exception as e:
            return {
                "meeting_id": inputs["meeting_id"],
                "result": False,
                "error": str(e)
            }


@zoom.action("delete_meeting")
class DeleteMeetingAction(ActionHandler):
    """Delete a scheduled meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            params = {}
            if inputs.get("occurrence_id"):
                params["occurrence_id"] = inputs["occurrence_id"]
            if "schedule_for_reminder" in inputs:
                params["schedule_for_reminder"] = inputs["schedule_for_reminder"]

            await client._make_request(
                f"meetings/{meeting_id}",
                method="DELETE",
                params=params if params else None
            )

            return {
                "meeting_id": inputs["meeting_id"],
                "result": True
            }
        except Exception as e:
            return {
                "meeting_id": inputs["meeting_id"],
                "result": False,
                "error": str(e)
            }


@zoom.action("list_recordings")
class ListRecordingsAction(ActionHandler):
    """List all cloud recordings for a user within a date range."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            user_id = inputs.get("user_id", "me")

            # Calculate default date range (last 30 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)

            params = {
                "from": inputs.get("from_date", from_date.strftime("%Y-%m-%d")),
                "to": inputs.get("to_date", to_date.strftime("%Y-%m-%d")),
                "page_size": min(inputs.get("page_size", 30), 300)
            }

            if inputs.get("next_page_token"):
                params["next_page_token"] = inputs["next_page_token"]

            response = await client._make_request(f"users/{user_id}/recordings", params=params)

            # Transform meetings with recordings
            meetings = []
            for meeting in response.get("meetings", []):
                recording_files = []
                for rf in meeting.get("recording_files", []):
                    recording_files.append({
                        "id": rf.get("id", ""),
                        "meeting_id": rf.get("meeting_id", ""),
                        "recording_type": rf.get("recording_type", ""),
                        "file_type": rf.get("file_type", ""),
                        "file_size": rf.get("file_size", 0),
                        "download_url": rf.get("download_url", ""),
                        "play_url": rf.get("play_url", ""),
                        "status": rf.get("status", "")
                    })

                meetings.append({
                    "uuid": meeting.get("uuid", ""),
                    "id": meeting.get("id"),
                    "topic": meeting.get("topic", ""),
                    "start_time": meeting.get("start_time", ""),
                    "duration": meeting.get("duration", 0),
                    "total_size": meeting.get("total_size", 0),
                    "recording_count": meeting.get("recording_count", len(recording_files)),
                    "recording_files": recording_files
                })

            return {
                "meetings": meetings,
                "next_page_token": response.get("next_page_token"),
                "page_count": response.get("page_count", 0),
                "page_size": response.get("page_size", 0),
                "total_records": response.get("total_records", len(meetings)),
                "result": True
            }
        except Exception as e:
            return {
                "meetings": [],
                "next_page_token": None,
                "page_count": 0,
                "page_size": 0,
                "total_records": 0,
                "result": False,
                "error": str(e)
            }


@zoom.action("get_meeting_recordings")
class GetMeetingRecordingsAction(ActionHandler):
    """Get all recording files for a specific meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            response = await client._make_request(f"meetings/{meeting_id}/recordings")

            # Transform recording files
            recording_files = []
            for rf in response.get("recording_files", []):
                recording_files.append({
                    "id": rf.get("id", ""),
                    "recording_type": rf.get("recording_type", ""),
                    "file_type": rf.get("file_type", ""),
                    "file_size": rf.get("file_size", 0),
                    "download_url": rf.get("download_url", ""),
                    "play_url": rf.get("play_url", ""),
                    "status": rf.get("status", ""),
                    "recording_start": rf.get("recording_start", ""),
                    "recording_end": rf.get("recording_end", "")
                })

            return {
                "uuid": response.get("uuid", ""),
                "id": response.get("id"),
                "topic": response.get("topic", ""),
                "start_time": response.get("start_time", ""),
                "duration": response.get("duration", 0),
                "total_size": response.get("total_size", 0),
                "recording_files": recording_files,
                "password": response.get("password", ""),
                "share_url": response.get("share_url", ""),
                "result": True
            }
        except Exception as e:
            return {
                "uuid": "",
                "id": None,
                "topic": "",
                "start_time": "",
                "duration": 0,
                "total_size": 0,
                "recording_files": [],
                "password": "",
                "share_url": "",
                "result": False,
                "error": str(e)
            }


@zoom.action("get_meeting_transcript")
class GetMeetingTranscriptAction(ActionHandler):
    """Retrieve the transcript for a recorded meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            # First get recordings to find transcript file
            response = await client._make_request(f"meetings/{meeting_id}/recordings")

            topic = response.get("topic", "")
            transcript_url = None
            transcript_content = None
            transcript_segments = []

            # Find transcript file in recordings
            for rf in response.get("recording_files", []):
                if rf.get("file_type") == "TRANSCRIPT" or rf.get("recording_type") == "audio_transcript":
                    transcript_url = rf.get("download_url", "")
                    break

            # If we found a transcript URL, try to fetch and parse it
            if transcript_url:
                try:
                    # Fetch transcript content
                    # Note: The download URL may require authentication
                    transcript_response = await context.fetch(
                        transcript_url,
                        headers=get_headers()
                    )

                    if isinstance(transcript_response, str):
                        transcript_content = transcript_response
                        transcript_segments = parse_vtt_transcript(transcript_content)
                    elif isinstance(transcript_response, dict) and "content" in transcript_response:
                        transcript_content = transcript_response["content"]
                        transcript_segments = parse_vtt_transcript(transcript_content)
                except Exception:
                    # Transcript download may fail if URL expired or access denied
                    # Return URL so user can download manually
                    pass

            return {
                "meeting_id": inputs["meeting_id"],
                "topic": topic,
                "transcript_url": transcript_url,
                "transcript_content": transcript_content,
                "transcript_segments": transcript_segments,
                "result": True
            }
        except Exception as e:
            return {
                "meeting_id": inputs["meeting_id"],
                "topic": "",
                "transcript_url": None,
                "transcript_content": None,
                "transcript_segments": [],
                "result": False,
                "error": str(e)
            }


@zoom.action("list_users")
class ListUsersAction(ActionHandler):
    """List all users in the Zoom account."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)

            params = {
                "status": inputs.get("status", "active"),
                "page_size": min(inputs.get("page_size", 30), 300)
            }

            if inputs.get("next_page_token"):
                params["next_page_token"] = inputs["next_page_token"]

            if inputs.get("role_id"):
                params["role_id"] = inputs["role_id"]

            response = await client._make_request("users", params=params)

            # Transform users
            users = []
            for user in response.get("users", []):
                users.append({
                    "id": user.get("id", ""),
                    "first_name": user.get("first_name", ""),
                    "last_name": user.get("last_name", ""),
                    "email": user.get("email", ""),
                    "type": user.get("type"),
                    "status": user.get("status", ""),
                    "department": user.get("dept", ""),
                    "created_at": user.get("created_at", ""),
                    "last_login_time": user.get("last_login_time", "")
                })

            return {
                "users": users,
                "next_page_token": response.get("next_page_token"),
                "page_count": response.get("page_count", 0),
                "page_size": response.get("page_size", 0),
                "total_records": response.get("total_records", len(users)),
                "result": True
            }
        except Exception as e:
            return {
                "users": [],
                "next_page_token": None,
                "page_count": 0,
                "page_size": 0,
                "total_records": 0,
                "result": False,
                "error": str(e)
            }


@zoom.action("get_user")
class GetUserAction(ActionHandler):
    """Get detailed information about a specific user."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            user_id = inputs.get("user_id", "me")

            response = await client._make_request(f"users/{user_id}")

            return {
                "id": response.get("id", ""),
                "first_name": response.get("first_name", ""),
                "last_name": response.get("last_name", ""),
                "email": response.get("email", ""),
                "type": response.get("type"),
                "role_name": response.get("role_name", ""),
                "pmi": response.get("pmi"),
                "use_pmi": response.get("use_pmi", False),
                "timezone": response.get("timezone", ""),
                "dept": response.get("dept", ""),
                "created_at": response.get("created_at", ""),
                "last_login_time": response.get("last_login_time", ""),
                "pic_url": response.get("pic_url", ""),
                "result": True
            }
        except Exception as e:
            return {
                "id": "",
                "first_name": "",
                "last_name": "",
                "email": "",
                "type": None,
                "role_name": "",
                "pmi": None,
                "use_pmi": False,
                "timezone": "",
                "dept": "",
                "created_at": "",
                "last_login_time": "",
                "pic_url": "",
                "result": False,
                "error": str(e)
            }


@zoom.action("get_meeting_participants")
class GetMeetingParticipantsAction(ActionHandler):
    """Get the list of participants who attended a past meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            params = {
                "page_size": min(inputs.get("page_size", 30), 300)
            }

            if inputs.get("next_page_token"):
                params["next_page_token"] = inputs["next_page_token"]

            # Use past meetings endpoint for participants
            response = await client._make_request(
                f"past_meetings/{meeting_id}/participants",
                params=params
            )

            # Transform participants
            participants = []
            for participant in response.get("participants", []):
                participants.append({
                    "id": participant.get("id", ""),
                    "user_id": participant.get("user_id", ""),
                    "name": participant.get("name", ""),
                    "user_email": participant.get("user_email", ""),
                    "join_time": participant.get("join_time", ""),
                    "leave_time": participant.get("leave_time", ""),
                    "duration": participant.get("duration", 0),
                    "attentiveness_score": participant.get("attentiveness_score", "")
                })

            return {
                "participants": participants,
                "next_page_token": response.get("next_page_token"),
                "page_count": response.get("page_count", 0),
                "page_size": response.get("page_size", 0),
                "total_records": response.get("total_records", len(participants)),
                "result": True
            }
        except Exception as e:
            return {
                "participants": [],
                "next_page_token": None,
                "page_count": 0,
                "page_size": 0,
                "total_records": 0,
                "result": False,
                "error": str(e)
            }


@zoom.action("add_meeting_registrant")
class AddMeetingRegistrantAction(ActionHandler):
    """Register a participant for a scheduled meeting."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            client = ZoomAPIClient(context)
            meeting_id = encode_meeting_id(inputs["meeting_id"])

            registrant_data = {
                "email": inputs["email"],
                "first_name": inputs["first_name"]
            }

            if inputs.get("last_name"):
                registrant_data["last_name"] = inputs["last_name"]

            # Auto-approve parameter is handled via query param
            params = {}
            if inputs.get("auto_approve", True):
                params["status"] = "approved"

            response = await client._make_request(
                f"meetings/{meeting_id}/registrants",
                method="POST",
                data=registrant_data
            )

            return {
                "registrant_id": response.get("registrant_id", ""),
                "id": response.get("id"),
                "topic": response.get("topic", ""),
                "start_time": response.get("start_time", ""),
                "join_url": response.get("join_url", ""),
                "result": True
            }
        except Exception as e:
            return {
                "registrant_id": "",
                "id": None,
                "topic": "",
                "start_time": "",
                "join_url": "",
                "result": False,
                "error": str(e)
            }
