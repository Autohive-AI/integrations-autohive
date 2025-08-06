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

@microsoft365.action("update_calendar_event")
class UpdateCalendarEventAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            event_id = inputs["event_id"]
            
            # Build event update data (only include fields that are provided)
            event_data = {}
            
            if inputs.get("subject"):
                event_data["subject"] = inputs["subject"]
            
            if inputs.get("start_time"):
                event_data["start"] = {
                    "dateTime": inputs["start_time"],
                    "timeZone": "UTC"
                }
            
            if inputs.get("end_time"):
                event_data["end"] = {
                    "dateTime": inputs["end_time"],
                    "timeZone": "UTC"
                }
            
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
            
            # Update event
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/events/{event_id}",
                method="PATCH",
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

@microsoft365.action("list_calendar_events")
class ListCalendarEventsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            start_date = inputs["start_date"]
            end_date = inputs.get("end_date", start_date)
            limit = inputs.get("limit", 100)
            
            # Convert dates to datetime strings for filtering
            # Assume dates are in YYYY-MM-DD format, convert to ISO 8601
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date}T23:59:59Z"
            
            # Build query parameters
            params = {
                "$top": limit,
                "$orderby": "start/dateTime",
                "$select": "id,subject,start,end,location,bodyPreview,organizer,attendees,webLink,isAllDay",
                "$filter": f"start/dateTime ge {start_datetime} and start/dateTime le {end_datetime}"
            }
            
            response = await context.fetch(f"{GRAPH_API_BASE}/me/events", params=params)
            
            # Format events
            events = []
            for event in response.get("value", []):
                # Process attendees
                attendees = []
                for attendee in event.get("attendees", []):
                    attendees.append({
                        "email": attendee["emailAddress"]["address"],
                        "name": attendee["emailAddress"]["name"],
                        "response_status": attendee["status"]["response"]
                    })
                
                # Get organizer email
                organizer_email = ""
                if event.get("organizer") and event["organizer"].get("emailAddress"):
                    organizer_email = event["organizer"]["emailAddress"]["address"]
                
                events.append({
                    "id": event["id"],
                    "subject": event.get("subject", ""),
                    "start_time": event["start"]["dateTime"],
                    "end_time": event["end"]["dateTime"],
                    "location": event.get("location", {}).get("displayName", ""),
                    "body_preview": event.get("bodyPreview", ""),
                    "organizer": organizer_email,
                    "attendees": attendees,
                    "web_link": event["webLink"],
                    "is_all_day": event.get("isAllDay", False)
                })
            
            return {
                "events": events,
                "result": True
            }
            
        except Exception as e:
            return {
                "events": [],
                "result": False,
                "error": str(e)
            }

@microsoft365.action("list_emails")
class ListEmailsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            start_date = inputs["start_date"]
            end_date = inputs.get("end_date", start_date)
            folder = inputs.get("folder", "Inbox")
            limit = inputs.get("limit", 50)
            
            # Convert dates to datetime strings for filtering
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date}T23:59:59Z"
            
            # Build query parameters
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,sender,receivedDateTime,bodyPreview,body,hasAttachments,isRead,importance",
                "$filter": f"receivedDateTime ge {start_datetime} and receivedDateTime le {end_datetime}"
            }
            
            api_url = f"{GRAPH_API_BASE}/me/mailFolders/{folder}/messages"
            response = await context.fetch(api_url, params=params)
            
            # Format emails
            emails = []
            for email in response.get("value", []):
                emails.append({
                    "id": email["id"],
                    "subject": email.get("subject", ""),
                    "sender": email["sender"]["emailAddress"]["address"],
                    "sender_name": email["sender"]["emailAddress"]["name"],
                    "received_time": email["receivedDateTime"],
                    "body_preview": email.get("bodyPreview", ""),
                    "body_content": email.get("body", {}).get("content", ""),
                    "has_attachments": email.get("hasAttachments", False),
                    "is_read": email.get("isRead", False),
                    "importance": email.get("importance", "normal")
                })
            
            return {
                "emails": emails,
                "result": True
            }
            
        except Exception as e:
            return {
                "emails": [],
                "result": False,
                "error": str(e)
            }

@microsoft365.action("list_emails_from_contact")
class ListEmailsFromContactAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            contact_email = inputs["contact_email"]
            limit = inputs.get("limit", 5)
            folder = inputs.get("folder", "Inbox")
            
            # Build query parameters to filter by sender email
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,sender,receivedDateTime,bodyPreview,body,hasAttachments,isRead,importance",
                "$filter": f"sender/emailAddress/address eq '{contact_email}'"
            }
            
            api_url = f"{GRAPH_API_BASE}/me/mailFolders/{folder}/messages"
            response = await context.fetch(api_url, params=params)
            
            # Format emails
            emails = []
            for email in response.get("value", []):
                emails.append({
                    "id": email["id"],
                    "subject": email.get("subject", ""),
                    "sender": email["sender"]["emailAddress"]["address"],
                    "sender_name": email["sender"]["emailAddress"]["name"],
                    "received_time": email["receivedDateTime"],
                    "body_preview": email.get("bodyPreview", ""),
                    "body_content": email.get("body", {}).get("content", ""),
                    "has_attachments": email.get("hasAttachments", False),
                    "is_read": email.get("isRead", False),
                    "importance": email.get("importance", "normal")
                })
            
            return {
                "emails": emails,
                "contact_email": contact_email,
                "result": True
            }
            
        except Exception as e:
            return {
                "emails": [],
                "contact_email": contact_email,
                "result": False,
                "error": str(e)
            }

@microsoft365.action("mark_email_read")
class MarkEmailReadAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            email_id = inputs["email_id"]
            is_read = inputs["is_read"]
            
            # Update email read status
            update_data = {
                "isRead": is_read
            }
            
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/messages/{email_id}",
                method="PATCH",
                json=update_data
            )
            
            return {
                "email_id": email_id,
                "is_read": is_read,
                "result": True
            }
            
        except Exception as e:
            return {
                "email_id": inputs.get("email_id", ""),
                "is_read": inputs.get("is_read", False),
                "result": False,
                "error": str(e)
            }

@microsoft365.action("move_email")
class MoveEmailAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            email_id = inputs["email_id"]
            destination_folder = inputs["destination_folder"]
            
            # Move email to destination folder
            move_data = {
                "destinationId": destination_folder
            }
            
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/messages/{email_id}/move",
                method="POST",
                json=move_data
            )
            
            # The response contains the moved email with potentially new ID
            new_email_id = response.get("id", email_id)
            
            return {
                "email_id": email_id,
                "destination_folder": destination_folder,
                "new_email_id": new_email_id,
                "result": True
            }
            
        except Exception as e:
            return {
                "email_id": inputs.get("email_id", ""),
                "destination_folder": inputs.get("destination_folder", ""),
                "result": False,
                "error": str(e)
            }

@microsoft365.action("read_email")
class ReadEmailAction(ActionHandler):
    # Reuse file type categories from ReadFileAction
    READABLE_FILE_TYPES = {
        'text/plain', 'text/csv', 'application/json', 'text/xml', 
        'text/markdown', 'application/x-yaml', 'text/yaml',
        'application/x-yaml', 'text/x-log'
    }
    
    IMAGE_FILE_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 
        'image/tiff', 'image/webp', 'image/svg+xml'
    }
    
    OFFICE_FILE_TYPES = {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/msword',
        'application/vnd.ms-excel',
        'application/vnd.ms-powerpoint'
    }
    
    PDF_FILE_TYPE = 'application/pdf'
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            email_id = inputs["email_id"]
            include_attachments = inputs.get("include_attachments", True)
            max_attachment_size_mb = inputs.get("max_attachment_size_mb", 50)
            max_size_bytes = max_attachment_size_mb * 1024 * 1024
            
            # Get email details
            email_response = await context.fetch(
                f"{GRAPH_API_BASE}/me/messages/{email_id}",
                params={
                    "$select": "id,subject,sender,receivedDateTime,body,hasAttachments"
                }
            )
            
            # Format email details
            email_details = {
                "id": email_response["id"],
                "subject": email_response.get("subject", ""),
                "sender": email_response["sender"]["emailAddress"]["address"],
                "sender_name": email_response["sender"]["emailAddress"]["name"],
                "received_time": email_response["receivedDateTime"],
                "body_content": email_response.get("body", {}).get("content", ""),
                "has_attachments": email_response.get("hasAttachments", False)
            }
            
            attachments = []
            
            if include_attachments and email_details["has_attachments"]:
                # Get attachments
                attachments_response = await context.fetch(
                    f"{GRAPH_API_BASE}/me/messages/{email_id}/attachments"
                )
                
                for attachment in attachments_response.get("value", []):
                    attachment_id = attachment["id"]
                    attachment_name = attachment["name"]
                    attachment_size = attachment.get("size", 0)
                    content_type = attachment.get("contentType", "application/octet-stream")
                    
                    # Determine file category
                    if content_type in self.OFFICE_FILE_TYPES:
                        # Office documents must be handled as binary files first
                        file_category = "office_document"
                        is_readable = False
                    elif content_type in self.READABLE_FILE_TYPES:
                        file_category = "text"
                        is_readable = True
                    elif content_type in self.IMAGE_FILE_TYPES:
                        file_category = "image" 
                        is_readable = False
                    elif content_type == self.PDF_FILE_TYPE:
                        file_category = "pdf"
                        is_readable = False
                    else:
                        file_category = "other"
                        is_readable = False
                    
                    attachment_data = {
                        "id": attachment_id,
                        "name": attachment_name,
                        "size": attachment_size,
                        "content_type": content_type,
                        "file_category": file_category,
                        "is_readable": is_readable
                    }
                    
                    if attachment_size > max_size_bytes:
                        attachment_data.update({
                            "content_encoding": "too_large",
                            "message": f"Attachment size ({attachment_size} bytes) exceeds limit ({max_attachment_size_mb}MB). Cannot download content."
                        })
                    else:
                        try:
                            # Download attachment content
                            attachment_content = await context.fetch(
                                f"{GRAPH_API_BASE}/me/messages/{email_id}/attachments/{attachment_id}/$value"
                            )
                            
                            if file_category == "text":
                                # Try to decode as text
                                try:
                                    text_content = attachment_content.decode('utf-8')
                                    attachment_data.update({
                                        "content": text_content,
                                        "content_encoding": "text"
                                    })
                                except UnicodeDecodeError:
                                    attachment_data.update({
                                        "content": base64.b64encode(attachment_content).decode('utf-8'),
                                        "content_encoding": "base64",
                                        "message": "File appeared to be text but contained non-UTF8 characters. Returned as base64."
                                    })
                            else:
                                # Return as base64 for binary files
                                attachment_data.update({
                                    "content": base64.b64encode(attachment_content).decode('utf-8'),
                                    "content_encoding": "base64"
                                })
                                
                                if file_category == "image":
                                    attachment_data["message"] = "Image attachment returned as base64."
                                elif file_category == "pdf":
                                    attachment_data["message"] = "PDF attachment returned as base64. Use specialized PDF tools for text extraction."
                                elif file_category == "office_document":
                                    attachment_data["message"] = "Office document returned as base64."
                                else:
                                    attachment_data["message"] = f"Binary attachment ({content_type}) returned as base64."
                                    
                        except Exception as e:
                            attachment_data.update({
                                "content_encoding": "error",
                                "message": f"Failed to download attachment: {str(e)}"
                            })
                    
                    attachments.append(attachment_data)
            
            return {
                "email": email_details,
                "attachments": attachments,
                "result": True
            }
            
        except Exception as e:
            return {
                "email": {},
                "attachments": [],
                "result": False,
                "error": str(e)
            }

@microsoft365.action("read_file")
class ReadFileAction(ActionHandler):
    # File type categories based on MIME types
    READABLE_FILE_TYPES = {
        'text/plain', 'text/csv', 'application/json', 'text/xml', 
        'text/markdown', 'application/x-yaml', 'text/yaml',
        'application/x-yaml', 'text/x-log'
    }
    
    IMAGE_FILE_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 
        'image/tiff', 'image/webp', 'image/svg+xml'
    }
    
    OFFICE_FILE_TYPES = {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
        'application/msword',  # .doc
        'application/vnd.ms-excel',  # .xls  
        'application/vnd.ms-powerpoint'  # .ppt
    }
    
    PDF_FILE_TYPE = 'application/pdf'
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            file_id = inputs["file_id"]
            include_content = inputs.get("include_content", True)
            max_size_mb = inputs.get("max_size_mb", 50)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            # Get file metadata including download URL
            # Use select to get specific properties including @microsoft.graph.downloadUrl
            params = {
                "$select": "id,name,size,webUrl,file,@microsoft.graph.downloadUrl"
            }
            
            file_info = await context.fetch(
                f"{GRAPH_API_BASE}/me/drive/items/{file_id}",
                params=params
            )
            
            file_name = file_info['name']
            file_size = file_info.get('size', 0)
            web_url = file_info['webUrl']
            download_url = file_info.get('@microsoft.graph.downloadUrl', '')
            
            # Get MIME type from file facet
            mime_type = file_info.get('file', {}).get('mimeType', 'application/octet-stream')
            
            # Determine file category
            if mime_type in self.OFFICE_FILE_TYPES:
                # Office documents must be handled as binary files first
                file_category = "office_document"
                is_readable = False
            elif mime_type in self.READABLE_FILE_TYPES:
                file_category = "text"
                is_readable = True
            elif mime_type in self.IMAGE_FILE_TYPES:
                file_category = "image"
                is_readable = False
            elif mime_type == self.PDF_FILE_TYPE:
                file_category = "pdf"
                is_readable = False
            else:
                file_category = "other"
                is_readable = False
            
            # Base response with metadata
            response = {
                "file_name": file_name,
                "file_size": file_size,
                "mime_type": mime_type,
                "file_category": file_category,
                "download_url": download_url,
                "web_url": web_url,
                "is_readable": is_readable,
                "result": True
            }
            
            # Handle content inclusion
            if include_content:
                if file_size > max_size_bytes:
                    # File too large - return URL only
                    response.update({
                        "content_type": "url_only",
                        "message": f"File size ({file_size} bytes) exceeds limit ({max_size_mb}MB). Use download_url to access file."
                    })
                else:
                    # Download file content - use download_url if available, otherwise use /content endpoint
                    try:
                        if download_url:
                            file_content = await context.fetch(download_url)
                        else:
                            # Fallback to /content endpoint when @microsoft.graph.downloadUrl is missing
                            file_content = await context.fetch(f"{GRAPH_API_BASE}/me/drive/items/{file_id}/content")
                        
                        if file_category == "text":
                            # Return as text content
                            try:
                                text_content = file_content.decode('utf-8')
                                response.update({
                                    "content": text_content,
                                    "content_type": "text"
                                })
                            except UnicodeDecodeError:
                                # Fallback to base64 if text decoding fails
                                response.update({
                                    "content": base64.b64encode(file_content).decode('utf-8'),
                                    "content_type": "base64",
                                    "message": "File appeared to be text but contained non-UTF8 characters. Returned as base64."
                                })
                        else:
                            # Return as base64 for binary files
                            response.update({
                                "content": base64.b64encode(file_content).decode('utf-8'),
                                "content_type": "base64"
                            })
                            
                            # Add specific messages for different file types
                            if file_category == "image":
                                response["message"] = "Image file returned as base64. Can be displayed or processed by image tools."
                            elif file_category == "pdf":
                                response["message"] = "PDF file returned as base64. Use specialized PDF tools for text extraction."
                            elif file_category == "office_document":
                                response["message"] = "Office document returned as base64. Use appropriate tools for content extraction."
                            else:
                                response["message"] = f"Binary file ({mime_type}) returned as base64."
                                
                    except Exception as download_error:
                        # Failed to download content
                        response.update({
                            "content_type": "download_error",
                            "message": f"Failed to download file content: {str(download_error)}"
                        })
            else:
                response.update({
                    "content_type": "metadata_only",
                    "message": "File metadata only. Set include_content=true to retrieve file content."
                })
            
            return response
            
        except Exception as e:
            return {
                "file_name": "",
                "file_size": 0,
                "mime_type": "application/octet-stream",
                "file_category": "unknown",
                "download_url": "",
                "web_url": "",
                "is_readable": False,
                "content_type": "error",
                "result": False,
                "error": str(e)
            }

@microsoft365.action("read_contacts")
class ReadContactsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            limit = inputs.get("limit", 100)
            search = inputs.get("search")
            
            # Build API URL
            api_url = f"{GRAPH_API_BASE}/me/contacts"
            
            # Build query parameters
            params = {
                "$top": limit,
                "$select": "id,displayName,givenName,surname,emailAddresses,businessPhones,homePhones,mobilePhone,companyName,jobTitle"
            }
            
            # Add search filter if provided
            if search:
                params["$filter"] = f"startswith(displayName,'{search}') or startswith(givenName,'{search}') or startswith(surname,'{search}')"
            
            response = await context.fetch(api_url, params=params)
            
            # Format contacts
            contacts = []
            for contact in response.get("value", []):
                # Process email addresses
                email_addresses = []
                for email in contact.get("emailAddresses", []):
                    email_addresses.append({
                        "address": email.get("address", ""),
                        "name": email.get("name", "")
                    })
                
                # Process phone numbers
                phone_numbers = []
                
                # Business phones
                for phone in contact.get("businessPhones", []):
                    phone_numbers.append({
                        "number": phone,
                        "type": "business"
                    })
                
                # Home phones  
                for phone in contact.get("homePhones", []):
                    phone_numbers.append({
                        "number": phone,
                        "type": "home"
                    })
                
                # Mobile phone
                mobile = contact.get("mobilePhone")
                if mobile:
                    phone_numbers.append({
                        "number": mobile,
                        "type": "mobile"
                    })
                
                contacts.append({
                    "id": contact.get("id", ""),
                    "display_name": contact.get("displayName", ""),
                    "given_name": contact.get("givenName", ""),
                    "surname": contact.get("surname", ""),
                    "email_addresses": email_addresses,
                    "phone_numbers": phone_numbers,
                    "company_name": contact.get("companyName", ""),
                    "job_title": contact.get("jobTitle", "")
                })
            
            return {
                "contacts": contacts,
                "result": True
            }
            
        except Exception as e:
            return {
                "contacts": [],
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