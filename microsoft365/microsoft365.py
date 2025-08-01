from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, PollingTriggerHandler
)
from typing import Dict, Any, List, Optional
import json
import base64
from datetime import datetime, timezone

# Create the integration using the config.json
microsoft365 = Integration.load()

# Microsoft Graph API Base URL
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# ---- Action Handlers ----

@microsoft365.action("send_email")
class SendEmailAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build email message
            message = {
                "subject": inputs["subject"],
                "body": {
                    "contentType": inputs.get("body_type", "Text"),
                    "content": inputs["body"]
                },
                "toRecipients": [
                    {"emailAddress": {"address": inputs["to"]}}
                ]
            }
            
            # Add CC recipients if provided
            if inputs.get("cc"):
                message["ccRecipients"] = [
                    {"emailAddress": {"address": email}} for email in inputs["cc"]
                ]
            
            # Add BCC recipients if provided
            if inputs.get("bcc"):
                message["bccRecipients"] = [
                    {"emailAddress": {"address": email}} for email in inputs["bcc"]
                ]
            
            # Send email
            email_data = {
                "message": message,
                "saveToSentItems": True
            }
            
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/sendMail",
                method="POST",
                json=email_data
            )
            
            return {
                "message_id": "sent",  # Graph API doesn't return message ID for sendMail
                "status": "sent",
                "result": True
            }
            
        except Exception as e:
            return {
                "result": False,
                "error": str(e),
                "status": "failed"
            }

@microsoft365.action("create_calendar_event")
class CreateCalendarEventAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build event data
            event_data = {
                "subject": inputs["subject"],
                "start": {
                    "dateTime": inputs["start_time"],
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": inputs["end_time"],
                    "timeZone": "UTC"
                }
            }
            
            # Add optional fields
            if inputs.get("location"):
                event_data["location"] = {
                    "displayName": inputs["location"]
                }
            
            if inputs.get("body"):
                event_data["body"] = {
                    "contentType": "Text",
                    "content": inputs["body"]
                }
            
            if inputs.get("attendees"):
                event_data["attendees"] = [
                    {
                        "emailAddress": {"address": email, "name": email},
                        "type": "required"
                    } for email in inputs["attendees"]
                ]
            
            # Create event
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/events",
                method="POST",
                json=event_data
            )
            
            return {
                "event_id": response["id"],
                "web_link": response["webLink"],
                "result": True
            }
            
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }

@microsoft365.action("upload_file")
class UploadFileAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            file_obj = inputs["file"]
            folder_path = inputs.get("folder_path", "/").strip("/")
            
            # Extract file properties
            file_name = file_obj["name"]
            file_content = base64.b64decode(file_obj["content"])
            
            # Build upload URL
            if folder_path:
                upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{file_name}:/content"
            else:
                upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{file_name}:/content"
            
            # Upload file
            response = await context.fetch(
                upload_url,
                method="PUT",
                data=file_content,
                headers={"Content-Type": "application/octet-stream"}
            )
            
            return {
                "file_id": response["id"],
                "web_url": response["webUrl"],
                "download_url": response.get("@microsoft.graph.downloadUrl", ""),
                "size": response["size"],
                "result": True
            }
            
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }

@microsoft365.action("list_files")
class ListFilesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            folder_path = inputs.get("folder_path", "/").strip("/")
            limit = inputs.get("limit", 100)
            
            # Build API URL
            if folder_path:
                api_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}:/children"
            else:
                api_url = f"{GRAPH_API_BASE}/me/drive/root/children"
            
            # Add query parameters
            params = {
                "$top": limit,
                "$select": "id,name,size,lastModifiedDateTime,webUrl,folder"
            }
            
            response = await context.fetch(api_url, params=params)
            
            # Format files
            files = []
            for item in response.get("value", []):
                files.append({
                    "id": item["id"],
                    "name": item["name"],
                    "size": item.get("size", 0),
                    "modified_time": item["lastModifiedDateTime"],
                    "web_url": item["webUrl"],
                    "is_folder": "folder" in item
                })
            
            return {
                "files": files,
                "result": True
            }
            
        except Exception as e:
            return {
                "files": [],
                "result": False,
                "error": str(e)
            }

# ---- Polling Trigger Handlers ----

@microsoft365.polling_trigger("new_emails")
class NewEmailsPoller(PollingTriggerHandler):
    async def poll(self, inputs: Dict[str, Any], last_poll_ts: Optional[str], context: ExecutionContext) -> List[Dict[str, Any]]:
        try:
            folder = inputs.get("folder", "Inbox")
            limit = inputs.get("limit", 50)
            
            # Build query parameters
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,sender,receivedDateTime,bodyPreview,hasAttachments"
            }
            
            # Add time filter if we have a last poll timestamp
            if last_poll_ts:
                params["$filter"] = f"receivedDateTime gt {last_poll_ts}"
            
            # Get emails from specified folder
            # Use well-known folder names (inbox, drafts, sentitems, deleteditems)
            # or folder IDs for other folders
            api_url = f"{GRAPH_API_BASE}/me/mailFolders/{folder}/messages"
            
            response = await context.fetch(api_url, params=params)
            
            # Format emails for polling trigger
            new_emails = []
            for email in response.get("value", []):
                new_emails.append({
                    "id": email["id"],  # Deduplication key
                    "data": {
                        "id": email["id"],
                        "subject": email["subject"],
                        "sender": email["sender"]["emailAddress"]["address"],
                        "received_time": email["receivedDateTime"],
                        "body_preview": email["bodyPreview"],
                        "has_attachments": email["hasAttachments"]
                    }
                })
            
            return new_emails
            
        except Exception as e:
            print(f"Error polling for new emails: {e}")
            return []

@microsoft365.polling_trigger("new_files")
class NewFilesPoller(PollingTriggerHandler):
    async def poll(self, inputs: Dict[str, Any], last_poll_ts: Optional[str], context: ExecutionContext) -> List[Dict[str, Any]]:
        try:
            folder_path = inputs.get("folder_path", "/").strip("/")
            
            # Build API URL
            if folder_path:
                api_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}:/children"
            else:
                api_url = f"{GRAPH_API_BASE}/me/drive/root/children"
            
            # Query parameters
            params = {
                "$orderby": "lastModifiedDateTime desc",
                "$select": "id,name,lastModifiedDateTime,createdDateTime,size,webUrl,folder"
            }
            
            response = await context.fetch(api_url, params=params)
            
            # Filter for new files since last poll
            new_files = []
            for item in response.get("value", []):
                # Skip folders for now (only monitor files)
                if "folder" in item:
                    continue
                
                modified_time = item["lastModifiedDateTime"]
                
                # If we have a last poll timestamp, only include newer files
                if last_poll_ts and modified_time <= last_poll_ts:
                    continue
                
                file_path = f"{folder_path}/{item['name']}" if folder_path else item["name"]
                
                new_files.append({
                    "id": item["id"],  # Deduplication key
                    "data": {
                        "id": item["id"],
                        "name": item["name"],
                        "path": file_path,
                        "size": item.get("size", 0),
                        "modified_time": modified_time,
                        "created_time": item["createdDateTime"]
                    }
                })
            
            return new_files
            
        except Exception as e:
            print(f"Error polling for new files: {e}")
            return []