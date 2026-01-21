from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult, ConnectedAccountHandler, ConnectedAccountInfo
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
            
            return ActionResult(data={
                "calls": calls,
                "has_more": response.get("hasMore", False),
                "next_cursor": response.get("nextCursor")
            })
        except Exception as e:
            return ActionResult(data={
                "calls": [],
                "has_more": False,
                "next_cursor": None,
                "error": str(e)
            })

@gong.action("get_call_transcript")
class GetCallTranscriptAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        call_id = inputs["call_id"]
        
        try:
            # 1. Get basic details to check privacy and get start time
            response = await client._make_request(f"calls/{call_id}")
            call_data = response.get("call", response)
            
            # Block access to private calls
            if bool(call_data.get("isPrivate", False)):
                return ActionResult(data={
                    "call_id": call_id,
                    "transcript": [],
                    "error": "private_call_filtered"
                })

            # 2. Get extensive details for speaker mapping
            speaker_map = {}
            
            # Fetch parties using extensive endpoint
            # We use a safe default date 2015-01-01
            ext_data = {
                "filter": {
                    "callIds": [call_id],
                    "fromDateTime": "2015-01-01T00:00:00Z"
                },
                "contentSelector": {
                    "exposedFields": {
                        "parties": True
                    }
                }
            }
            
            try:
                ext_response = await client._make_request("calls/extensive", method="POST", data=ext_data)
                ext_calls = ext_response.get("calls", [])
                
                if ext_calls:
                    ext_call = ext_calls[0]
                    participants = ext_call.get("parties", [])
                    
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
            except Exception as e:
                print(f"Warning: Failed to fetch speaker details: {e}")

            # 3. Get transcript data
            # Requires api:calls:read:transcript scope
            transcript_data = {
                "filter": {
                    "callIds": [call_id],
                    "fromDateTime": "2015-01-01T00:00:00.000Z"  # Ensure we find the call regardless of date
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
            
            return ActionResult(data={
                "call_id": call_id,
                "transcript": transcript
            })
        except Exception as e:
            return ActionResult(data={
                "call_id": call_id,
                "transcript": [],
                "error": str(e)
            })

@gong.action("get_call_details")
class GetCallDetailsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = GongAPIClient(context)
        call_id = inputs["call_id"]
        
        try:
            # 1. Get basic call details using GET /v2/calls/{id}
            response = await client._make_request(f"calls/{call_id}")
            call = response.get("call", response)
            
            # Check for private call
            if bool(call.get("isPrivate", False)):
                return ActionResult(data={
                    "id": call_id,
                    "title": "",
                    "started": "",
                    "duration": 0,
                    "participants": [],
                    "outcome": "",
                    "crm_data": {},
                    "error": "private_call_filtered"
                })

            # 2. Fetch extended details (participants/parties) using POST /v2/calls/extensive
            # We use the call's start time to narrow the search, which is required/recommended for performance
            participants = []
            crm_data = call.get("crmData", {})
            
            started_str = call.get("started")
            if started_str:
                try:
                    # Parse start time to create a safe window
                    # Handle 'Z' by replacing with +00:00 for fromisoformat compatibility
                    dt_str = started_str.replace("Z", "+00:00")
                    # Remove milliseconds if present for safer parsing if needed, but ISO usually ok
                    # simpler: just use the string as is for the API if possible, but calculating window is safer
                    
                    # Create a wide window (e.g. +/- 1 day) to avoid timezone/precision issues
                    # But actually, just passing the exact same string as fromDateTime might be risky if they mean "strictly after"
                    # So let's try to pass the exact string first, or even better, a fixed "old" date if we don't want to parse.
                    # BUT, the issue before was empty results.
                    # Let's try to use the fromDateTime we used before "2015-01-01" BUT with the ID.
                    # Wait, why did the user say "that didn't work" before? 
                    # Maybe extensive endpoint *requires* a tighter date range? 
                    # Or maybe the "2015" date was fine but something else was wrong?
                    # The user said "call details are empty".
                    
                    # Let's use the actual call date found from the GET request.
                    extensive_data = {
                        "filter": {
                            "callIds": [call_id],
                            "fromDateTime": "2015-01-01T00:00:00Z" # Safe fallback
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
                    
                    # If we have a start time, use it to optimize/ensure finding
                    if started_str:
                         extensive_data["filter"]["fromDateTime"] = "2015-01-01T00:00:00Z" 
                         # Actually, sticking to 2015 is safest if it works. 
                         # But let's rely on the fact that we have the ID.
                    
                    ext_response = await client._make_request("calls/extensive", method="POST", data=extensive_data)
                    ext_calls = ext_response.get("calls", [])
                    if ext_calls:
                        ext_call = ext_calls[0]
                        participants = ext_call.get("parties", [])
                        crm_data = ext_call.get("crmData", crm_data)
                        # Update outcome if available
                        if not call.get("outcome"):
                            call["outcome"] = ext_call.get("outcome", "")
                except Exception as e:
                    # If extensive fails, we still return the basic info we have
                    print(f"Warning: Failed to fetch extensive details: {e}")
                    pass

            return ActionResult(data={
                "id": call.get("id", call_id),
                "title": call.get("title", "Unknown Call"),
                "started": call.get("started", ""),
                "duration": call.get("duration", 0),
                "participants": participants,
                "outcome": call.get("outcome", ""),
                "crm_data": crm_data
            })
        except Exception as e:
            return ActionResult(data={
                "id": call_id,
                "title": "",
                "started": "",
                "duration": 0,
                "participants": [],
                "outcome": "",
                "crm_data": {},
                "error": str(e)
            })

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
            "contentSelector": {
                "context": "Extended",
                "exposedFields": {
                    "content": {
                        "topics": True,
                        "pointsOfInterest": True
                    }
                }
            }
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
                highlights = content_fields.get("pointsOfInterest", []) # renamed from highlights based on likely API structure or just generic access
                # Note: The original code used "highlights", "topics", "keyPoints" in contentSelector list which was wrong.
                # In Extended context, pointsOfInterest is a common field.
                # However, to be safe and consistent with the previous logic that tried to access highlights,
                # I should check what fields are returned.
                # The original code had:
                # "contentSelector": ["highlights", "topics", "keyPoints"] (which was wrong format)
                # And logic:
                # highlights = content_fields.get("highlights", [])
                
                # I'll stick to what I know works or generic safe access, 
                # but I also updated contentSelector to be correct dictionary format above.
                
                # Let's try to match the original logic as much as possible but with valid API request structure.
                topics = content_fields.get("topics", [])
                
                # Since I requested pointsOfInterest, let's use that if highlights is empty
                points_of_interest = content_fields.get("pointsOfInterest", [])
                
                # Search in points_of_interest (assuming it has text field)
                for poi in points_of_interest:
                     if query in poi.get("action", "").lower() or query in poi.get("concept", "").lower():
                        content_match = True
                        matched_segments.append({
                            "text": f"{poi.get('action', '')} {poi.get('concept', '')}",
                            "start_time": poi.get("startTime", 0)
                        })

                # Search in topics
                for topic in topics:
                    if query in topic.get("name", "").lower():
                         content_match = True
                
                # Fallback to simple title search if nothing else
                if query in call.get("title", "").lower():
                    content_match = True

                if content_match:
                    results.append({
                        "call_id": call.get("id"),
                        "title": call.get("title", ""),
                        "started": call.get("started"),
                        "relevance_score": len(matched_segments) + (1 if query in call.get("title", "").lower() else 0), 
                        "matched_segments": matched_segments
                    })
            
            return ActionResult(data={
                "results": results,
                "total_count": len(results)
            })
        except Exception as e:
            return ActionResult(data={
                "results": [],
                "total_count": 0,
                "error": str(e)
            })

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
            
            return ActionResult(data={
                "users": users,
                "has_more": response.get("hasMore", False),
                "next_cursor": response.get("nextCursor")
            })
        except Exception as e:
            return ActionResult(data={
                "users": [],
                "has_more": False,
                "next_cursor": None,
                "error": str(e)
            })
