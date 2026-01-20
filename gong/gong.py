from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import json



gong = Integration.load()

class GongAPIClient:
    """Client for interacting with the Gong API"""
    
    def __init__(self, context: ExecutionContext):
        self.context = context
        self.base_url = context.metadata.get("api_base_url")
        if not self.base_url:
            raise ValueError("api_base_url is required in auth context. This should be provided by Gong's OAuth flow as 'api_base_url_for_customer'.")
    
    async def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None):
        """Make an authenticated request to the Gong API"""
        url = f"{self.base_url}/v2/{endpoint}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use the context's fetch method for authenticated requests (OAuth handled by SDK)
        if method == "GET": 
            return await self.context.fetch(url, params=params, headers=headers)
        elif method == "POST":
            return await self.context.fetch(url, method="POST", json=data, headers=headers)
        elif method == "PUT":
            return await self.context.fetch(url, method="PUT", json=data, headers=headers)
        elif method == "DELETE":
            return await self.context.fetch(url, method="DELETE", headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

# ---- Action Handlers ----

@gong.action("list_calls")
class ListCallsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        
        # Build query parameters with proper date format
        params = {}
        
        if inputs.get("from_date"):
            # Convert YYYY-MM-DD to datetime format required by Gong
            from datetime import datetime
            from_dt = datetime.strptime(inputs["from_date"], "%Y-%m-%d")
            params["fromDateTime"] = from_dt.strftime("%Y-%m-%dT00:00:00.000Z")
        if inputs.get("to_date"):
            from datetime import datetime
            to_dt = datetime.strptime(inputs["to_date"], "%Y-%m-%d")
            params["toDateTime"] = to_dt.strftime("%Y-%m-%dT23:59:59.999Z")
        if inputs.get("user_ids"):
            params["userIds"] = inputs["user_ids"]
        if inputs.get("limit"):
            params["limit"] = inputs["limit"]
        if inputs.get("cursor"):
            params["cursor"] = inputs["cursor"]
        
        # Add default date range if none provided (last 30 days)
        if not inputs.get("from_date") and not inputs.get("to_date"):
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            params["fromDateTime"] = start_date.strftime("%Y-%m-%dT00:00:00.000Z")
            params["toDateTime"] = end_date.strftime("%Y-%m-%dT23:59:59.999Z")
        
        try:
            response = await client._make_request("calls", params=params)
            
            calls = []
            for call in response.get("calls", []):
                # Filter out private calls
                if bool(call.get("isPrivate", False)):
                    continue
                calls.append({
                    "id": call.get("id"),
                    "title": call.get("title", ""),
                    "started": call.get("started"),
                    "duration": call.get("duration", 0),
                    "participants": call.get("participants", []),
                    "outcome": call.get("outcome", "")
                })
            
            # Sort calls by start time, newest first
            calls.sort(key=lambda x: x.get("started", ""), reverse=True)
            
            return {
                "calls": calls,
                "has_more": response.get("hasMore", False),
                "next_cursor": response.get("nextCursor")
            }
        except Exception as e:
            return {
                "calls": [],
                "has_more": False,
                "next_cursor": None,
                "error": str(e)
            }

@gong.action("get_call_transcript")
class GetCallTranscriptAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        call_id = inputs["call_id"]
        
        try:
            # First get call details with parties/participants
            call_data = {
                "filter": {
                    "callIds": [call_id]
                },
                "contentSelector": {
                    "exposedFields": {
                        "parties": True
                    }
                }
            }
            call_response = await client._make_request("calls/extensive", method="POST", data=call_data)
            
            # Block access to private calls
            calls = call_response.get("calls", [])
            if calls and bool(calls[0].get("isPrivate", False)):
                return {
                    "call_id": call_id,
                    "transcript": [],
                    "error": "private_call_filtered"
                }

            # Build speaker mapping from call data
            speaker_map = {}
            if calls:
                call_data = calls[0]
                # Check multiple possible locations for participant data
                participants = (call_data.get("parties") or 
                              call_data.get("participants") or 
                              call_data.get("users") or [])
                
                for participant in participants:
                    # Extract speaker ID and name using multiple possible field names
                    speaker_id = str(participant.get("speakerId") or 
                                   participant.get("userId") or 
                                   participant.get("id") or "")
                    
                    # Try different name field combinations
                    name = (participant.get("name") or 
                           participant.get("title") or
                           f"{participant.get('firstName', '')} {participant.get('lastName', '')}".strip() or
                           participant.get("emailAddress") or
                           participant.get("email") or "")
                    
                    if speaker_id and name:
                        speaker_map[speaker_id] = name
            
            # Get transcript data
            transcript_data = {
                "filter": {
                    "callIds": [call_id]
                }
            }
            response = await client._make_request("calls/transcript", method="POST", data=transcript_data)
            
            transcript = []
            # Response structure: {"callTranscripts": [{"callId": "...", "transcript": [...]}]}
            call_transcripts = response.get("callTranscripts", [])
            if call_transcripts:
                for segment in call_transcripts[0].get("transcript", []):
                    # Normalize speaker_id to string for schema and mapping consistency
                    raw_speaker_id = segment.get("speakerId", "")
                    speaker_id = str(raw_speaker_id) if raw_speaker_id is not None else ""
                    topic = segment.get("topic", "")
                    
                    # Use speaker mapping or fallback to ID
                    speaker_name = speaker_map.get(speaker_id, f"Speaker {speaker_id}" if speaker_id else "Unknown Speaker")
                    
                    # Process sentences within each segment
                    for sentence in segment.get("sentences", []):
                        transcript.append({
                            "speaker_id": speaker_id,  # Original Gong speaker ID
                            "speaker_name": speaker_name,  # Temporary speaker name
                            "start_time": sentence.get("start", 0) / 1000,  # Convert ms to seconds
                            "end_time": sentence.get("end", 0) / 1000,  # Convert ms to seconds
                            "text": sentence.get("text", "")
                        })
            
            return {
                "call_id": call_id,
                "transcript": transcript
            }
        except Exception as e:
            return {
                "call_id": call_id,
                "transcript": [],
                "error": str(e)
            }

@gong.action("get_call_details")
class GetCallDetailsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        call_id = inputs["call_id"]
        
        try:
            # Use calls/extensive endpoint with specific call ID filter
            data = {
                "filter": {
                    "callIds": [call_id]
                },
                "contentSelector": {
                    "context": "Extended",
                    "exposedFields": {
                        "parties": True,
                        "content": {
                            "callOutcome": True
                        }
                    }
                }
            }
            response = await client._make_request("calls/extensive", method="POST", data=data)
            
            # Extract first call from response
            calls = response.get("calls", [])
            if calls:
                call = calls[0]
                # Block access to private calls
                if bool(call.get("isPrivate", False)):
                    return {
                        "id": call_id,
                        "title": "",
                        "started": "",
                        "duration": 0,
                        "participants": [],
                        "outcome": "",
                        "crm_data": {},
                        "error": "private_call_filtered"
                    }
                return {
                    "id": call.get("id", call_id),
                    "title": call.get("title", "Unknown Call"),
                    "started": call.get("started", ""),
                    "duration": call.get("duration", 0),
                    "participants": call.get("participants", []),
                    "outcome": call.get("outcome", ""),
                    "crm_data": call.get("crmData", {})
                }
            else:
                # Call not found, return empty but valid structure
                return {
                    "id": call_id,
                    "title": "Call Not Found",
                    "started": "",
                    "duration": 0,
                    "participants": [],
                    "outcome": "",
                    "crm_data": {}
                }
        except Exception as e:
            return {
                "id": call_id,
                "title": "",
                "started": "",
                "duration": 0,
                "participants": [],
                "outcome": "",
                "crm_data": {},
                "error": str(e)
            }

@gong.action("search_calls")
class SearchCallsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        
        # Use calls/extensive endpoint with proper JSON structure
        data = {
            "filter": {
                "fromDateTime": None,
                "toDateTime": None
            },
            "contentSelector": [
                "highlights", 
                "topics", 
                "keyPoints"
            ]
        }
        
        if inputs.get("from_date"):
            from datetime import datetime
            from_dt = datetime.strptime(inputs["from_date"], "%Y-%m-%d")
            data["filter"]["fromDateTime"] = from_dt.strftime("%Y-%m-%dT00:00:00.000Z")
        else:
            # Default to last 30 days if no date provided
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=30)
            data["filter"]["fromDateTime"] = start_date.strftime("%Y-%m-%dT00:00:00.000Z")
            
        if inputs.get("to_date"):
            from datetime import datetime
            to_dt = datetime.strptime(inputs["to_date"], "%Y-%m-%d")
            data["filter"]["toDateTime"] = to_dt.strftime("%Y-%m-%dT23:59:59.999Z")
        else:
            # Default to now if no end date provided
            from datetime import datetime
            data["filter"]["toDateTime"] = datetime.now().strftime("%Y-%m-%dT23:59:59.999Z")
        
        try:
            response = await client._make_request("calls/extensive", method="POST", data=data)
            
            # Filter calls based on search query in content
            query = inputs["query"].lower()
            results = []
            
            for call in response.get("calls", []):
                # Skip private calls
                if bool(call.get("isPrivate", False)):
                    continue
                # Check if query appears in call content/highlights/topics
                content_match = False
                matched_segments = []
                
                # Check various content fields for the search query
                content_fields = call.get("content", {})
                highlights = content_fields.get("highlights", [])
                topics = content_fields.get("topics", [])
                
                # Search in highlights
                for highlight in highlights:
                    if query in highlight.get("text", "").lower():
                        content_match = True
                        matched_segments.append({
                            "text": highlight.get("text", ""),
                            "start_time": highlight.get("startTime", 0)
                        })
                
                # Search in topics
                for topic in topics:
                    if query in topic.get("value", "").lower():
                        content_match = True
                
                if content_match:
                    results.append({
                        "call_id": call.get("id"),
                        "title": call.get("title", ""),
                        "started": call.get("started"),
                        "relevance_score": len(matched_segments),  # Use number of matches as relevance
                        "matched_segments": matched_segments
                    })
            
            return {
                "results": results,
                "total_count": len(results)
            }
        except Exception as e:
            return {
                "results": [],
                "total_count": 0,
                "error": str(e)
            }

@gong.action("list_users")
class ListUsersAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        
        params = {
            "limit": inputs.get("limit", 100)
        }
        
        if inputs.get("cursor"):
            params["cursor"] = inputs["cursor"]
        
        try:
            response = await client._make_request("users", params=params)
            
            users = []
            for user in response.get("users", []):
                users.append({
                    "id": user.get("id"),
                    "name": user.get("name", ""),
                    "email": user.get("email", ""),
                    "role": user.get("role", ""),
                    "active": user.get("active", True)
                })
            
            return {
                "users": users,
                "has_more": response.get("hasMore", False),
                "next_cursor": response.get("nextCursor")
            }
        except Exception as e:
            return {
                "users": [],
                "has_more": False,
                "next_cursor": None,
                "error": str(e)
            }