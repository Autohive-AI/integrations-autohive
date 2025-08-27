from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import json
import re
import os

# Create the integration using the config.json
# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

whatsapp = Integration.load(config_path)

# ---- Action Handlers ----

@whatsapp.action("send_message")
class SendMessageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        to = inputs["to"]
        message = inputs["message"]
        
        # Validate phone number format
        if not self._validate_phone_number(to):
            return {
                "message_id": "",
                "success": False,
                "error": "Invalid phone number format. Use format: +1234567890"
            }
        
        try:
            # WhatsApp Business API endpoint for sending messages
            response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{context.auth.get('phone_number_id')}/messages",
                method="POST",
                headers={
                    "Authorization": f"Bearer {context.auth.get('access_token')}",
                    "Content-Type": "application/json"
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": to.lstrip('+'),
                    "type": "text",
                    "text": {"body": message}
                }
            )
            
            if "messages" in response and response["messages"]:
                message_id = response["messages"][0]["id"]
                return {
                    "message_id": message_id,
                    "success": True
                }
            else:
                return {
                    "message_id": "",
                    "success": False,
                    "error": response.get("error", {}).get("message", "Unknown error")
                }
                
        except Exception as e:
            return {
                "message_id": "",
                "success": False,
                "error": f"Failed to send message: {str(e)}"
            }
    
    def _validate_phone_number(self, phone: str) -> bool:
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))


@whatsapp.action("send_template_message")
class SendTemplateMessageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        to = inputs["to"]
        template_name = inputs["template_name"]
        language_code = inputs.get("language_code", "en")
        parameters = inputs.get("parameters", [])
        
        # Validate phone number format
        if not self._validate_phone_number(to):
            return {
                "message_id": "",
                "success": False,
                "error": "Invalid phone number format. Use format: +1234567890"
            }
        
        try:
            # Build template message payload
            template_payload = {
                "messaging_product": "whatsapp",
                "to": to.lstrip('+'),
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }
            
            # Add parameters if provided
            if parameters:
                template_payload["template"]["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                }]
            
            response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{context.auth.get('phone_number_id')}/messages",
                method="POST",
                headers={
                    "Authorization": f"Bearer {context.auth.get('access_token')}",
                    "Content-Type": "application/json"
                },
                json=template_payload
            )
            
            if "messages" in response and response["messages"]:
                message_id = response["messages"][0]["id"]
                return {
                    "message_id": message_id,
                    "success": True
                }
            else:
                return {
                    "message_id": "",
                    "success": False,
                    "error": response.get("error", {}).get("message", "Unknown error")
                }
                
        except Exception as e:
            return {
                "message_id": "",
                "success": False,
                "error": f"Failed to send template message: {str(e)}"
            }
    
    def _validate_phone_number(self, phone: str) -> bool:
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))


@whatsapp.action("send_media_message")
class SendMediaMessageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        to = inputs["to"]
        media_type = inputs["media_type"]
        media_url = inputs["media_url"]
        caption = inputs.get("caption", "")
        filename = inputs.get("filename", "")
        
        # Validate phone number format
        if not self._validate_phone_number(to):
            return {
                "message_id": "",
                "success": False,
                "error": "Invalid phone number format. Use format: +1234567890"
            }
        
        try:
            # Build media message payload
            media_payload = {
                "messaging_product": "whatsapp",
                "to": to.lstrip('+'),
                "type": media_type
            }
            
            # Configure media object based on type
            media_object = {"link": media_url}
            
            if media_type == "document" and filename:
                media_object["filename"] = filename
            
            if caption and media_type in ["image", "video", "document"]:
                media_object["caption"] = caption
                
            media_payload[media_type] = media_object
            
            response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{context.auth.get('phone_number_id')}/messages",
                method="POST",
                headers={
                    "Authorization": f"Bearer {context.auth.get('access_token')}",
                    "Content-Type": "application/json"
                },
                json=media_payload
            )
            
            if "messages" in response and response["messages"]:
                message_id = response["messages"][0]["id"]
                return {
                    "message_id": message_id,
                    "success": True
                }
            else:
                return {
                    "message_id": "",
                    "success": False,
                    "error": response.get("error", {}).get("message", "Unknown error")
                }
                
        except Exception as e:
            return {
                "message_id": "",
                "success": False,
                "error": f"Failed to send media message: {str(e)}"
            }
    
    def _validate_phone_number(self, phone: str) -> bool:
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))


@whatsapp.action("get_contact_info")
class GetContactInfoAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        phone_number = inputs["phone_number"]
        
        # Validate phone number format
        if not self._validate_phone_number(phone_number):
            return {
                "phone_number": phone_number,
                "display_name": "",
                "profile_picture_url": "",
                "is_whatsapp_user": False,
                "success": False,
                "error": "Invalid phone number format. Use format: +1234567890"
            }
        
        try:
            # Check if the contact is a WhatsApp user
            response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{context.auth.get('phone_number_id')}/contacts",
                method="POST",
                headers={
                    "Authorization": f"Bearer {context.auth.get('access_token')}",
                    "Content-Type": "application/json"
                },
                json={
                    "blocking": "wait",
                    "contacts": [phone_number.lstrip('+')]
                }
            )
            
            if "contacts" in response and response["contacts"]:
                contact = response["contacts"][0]
                return {
                    "phone_number": phone_number,
                    "display_name": contact.get("profile", {}).get("name", ""),
                    "profile_picture_url": "",
                    "is_whatsapp_user": contact.get("status") == "valid",
                    "success": True
                }
            else:
                return {
                    "phone_number": phone_number,
                    "display_name": "",
                    "profile_picture_url": "",
                    "is_whatsapp_user": False,
                    "success": True
                }
                
        except Exception as e:
            return {
                "phone_number": phone_number,
                "display_name": "",
                "profile_picture_url": "",
                "is_whatsapp_user": False,
                "success": False,
                "error": f"Failed to get contact info: {str(e)}"
            }
    
    def _validate_phone_number(self, phone: str) -> bool:
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
