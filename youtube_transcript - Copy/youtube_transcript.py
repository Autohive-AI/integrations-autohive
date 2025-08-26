from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any
from supadata import Supadata, SupadataError

# Create the integration using the config.json
youtube_transcript = Integration.load()

# ---- Action Handlers ----

@youtube_transcript.action("get_transcript")
class GetTranscriptAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        video_url = inputs["video_url"]
        api_key = context.auth.get("credentials", {}).get("api_key", {})        
        try:
            # Initialize the Supadata client
            supadata = Supadata(api_key=api_key)
            
            # Get transcript using the Supadata SDK
            transcript_response = supadata.transcript(
                url=video_url,
                text=True,  # Return plain text instead of timestamped chunks
                mode="auto"  # Try native first, fallback to generate if unavailable
            )
            
            return {
                "transcript": transcript_response.content,
                "language": getattr(transcript_response, 'lang', ''),
                "available_languages": getattr(transcript_response, 'available_langs', [])
            }
            
        except SupadataError as e:
            raise ValueError(f"Supadata API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error getting transcript: {str(e)}")
    
