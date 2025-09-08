from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

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
                "result": True
            }
            
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
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
                "id": response["id"],
                "webLink": response["webLink"],
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
            filename = inputs["filename"]
            content = inputs["content"]
            content_type = inputs.get("content_type", "text/plain")
            folder_path = inputs.get("folder_path", "/").strip("/")
            
            # Convert text to bytes
            file_content = content.encode('utf-8')
            
            # Build upload URL
            if folder_path:
                upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}/{filename}:/content"
            else:
                upload_url = f"{GRAPH_API_BASE}/me/drive/root:/{filename}:/content"
            
            # Upload file
            response = await context.fetch(
                upload_url,
                method="PUT",
                data=file_content,
                headers={"Content-Type": content_type}
            )
            
            return {
                "id": response["id"],
                "webUrl": response["webUrl"],
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
                "id": response["id"],
                "webLink": response["webLink"],
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
            # Accept either datetime or date parameters, with intelligent defaults
            if "start_datetime" in inputs:
                start_datetime = inputs["start_datetime"]
                end_datetime = inputs.get("end_datetime", start_datetime)
            elif "start_date" in inputs:
                # Legacy date-only support (defaults to UTC)
                start_date = inputs["start_date"]
                end_date = inputs.get("end_date", start_date)
                start_datetime = f"{start_date}T00:00:00Z"
                end_datetime = f"{end_date}T23:59:59Z"
            else:
                # Intelligent default: next 30 days of calendar events (more useful for calendars)
                # Use UTC time for intelligent defaults (agent can provide timezone-aware datetime if needed)
                now = datetime.utcnow()
                end_time = now + timedelta(days=30)
                start_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                end_datetime = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            limit = inputs.get("limit", 100)
            
            # Build query parameters  
            params = {
                "$top": limit,
                "$orderby": "start/dateTime",
                "$select": "id,subject,start,end,location,bodyPreview,organizer,attendees,webLink,isAllDay"
            }
            
            # Skip date filtering for calendar events due to API issues
            # TODO: Fix datetime filter compatibility
            
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
            # Accept either datetime or date parameters, with intelligent defaults
            if "start_datetime" in inputs:
                start_datetime = inputs["start_datetime"]
                end_datetime = inputs.get("end_datetime", start_datetime)
            elif "start_date" in inputs:
                # Legacy date-only support (defaults to UTC)
                start_date = inputs["start_date"]
                end_date = inputs.get("end_date", start_date)
                start_datetime = f"{start_date}T00:00:00Z"
                end_datetime = f"{end_date}T23:59:59Z"
            else:
                # Intelligent default: last 1 day of emails
                # Use UTC time for intelligent defaults (agent can provide timezone-aware datetime if needed)
                now = datetime.utcnow()
                start_time = now - timedelta(days=1)
                start_datetime = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                end_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            folder = inputs.get("folder", "Inbox")
            limit = inputs.get("limit", 50)
            
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
            
            # Build query parameters - skip complex filters due to API limitations
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc", 
                "$select": "id,subject,sender,receivedDateTime,bodyPreview,body,hasAttachments,isRead,importance"
            }
            
            # TODO: Implement contact filtering in post-processing
            
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
                "id": response["id"],
                "isRead": response["isRead"],
                "lastModifiedDateTime": response["lastModifiedDateTime"],
                "result": True
            }
            
        except Exception as e:
            return {
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
            
            return {
                "id": response["id"],
                "parentFolderId": response["parentFolderId"],
                "result": True
            }
            
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }

@microsoft365.action("read_email")
class ReadEmailAction(ActionHandler):
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            email_id = inputs["email_id"]
            include_attachments = inputs.get("include_attachments", True)
            
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
                    
                    # Return attachment metadata only (no content download)
                    attachment_data = {
                        "id": attachment_id,
                        "name": attachment_name,
                        "size": attachment_size,
                        "content_type": content_type,
                        "message": "Attachment metadata only. Content extraction not supported for this file type."
                    }
                    
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