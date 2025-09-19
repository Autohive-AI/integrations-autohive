from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import json

# Create the integration using the config.json
front = Integration.load()

# Front API Base URL
FRONT_API_BASE = "https://api2.frontapp.com"

# ---- Utility Classes ----

class FrontDataParser:
    @staticmethod
    def parse_conversation(raw_conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw Front conversation into standardized format."""
        conversation = {
            "id": raw_conversation.get('id', ''),
            "subject": raw_conversation.get('subject', ''),
            "status": raw_conversation.get('status', ''),
        }

        # Add optional fields if they exist
        if 'assignee' in raw_conversation:
            conversation['assignee'] = raw_conversation['assignee']
        if 'recipient' in raw_conversation:
            conversation['recipient'] = raw_conversation['recipient']
        if 'tags' in raw_conversation:
            conversation['tags'] = raw_conversation['tags']
        if 'last_message' in raw_conversation:
            conversation['last_message'] = raw_conversation['last_message']
        if 'created_at' in raw_conversation:
            conversation['created_at'] = raw_conversation['created_at']
        if 'is_private' in raw_conversation:
            conversation['is_private'] = raw_conversation['is_private']

        return conversation

    @staticmethod
    def parse_message(raw_message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw Front message into standardized format."""
        message = {
            "id": raw_message.get('id', ''),
            "type": raw_message.get('type', ''),
            "is_inbound": raw_message.get('is_inbound', False),
            "author": raw_message.get('author', {}),
        }

        # Add optional fields if they exist
        if 'recipients' in raw_message:
            message['recipients'] = raw_message['recipients']
        if 'subject' in raw_message:
            message['subject'] = raw_message['subject']
        if 'body' in raw_message:
            message['body'] = raw_message['body']
        if 'created_at' in raw_message:
            message['created_at'] = raw_message['created_at']

        return message

# ---- Action Handlers ----

@front.action("get_inbox")
class GetInboxAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            inbox_id = inputs["inbox_id"]

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/inboxes/{inbox_id}"
            )

            # Check for API errors
            if "error" in response:
                return {
                    "inbox": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse inbox
            inbox = {
                "id": response.get("id", ""),
                "name": response.get("name", ""),
                "address": response.get("address", ""),
            }

            # Add optional fields
            if 'type' in response:
                inbox['type'] = response['type']
            if 'send_as' in response:
                inbox['send_as'] = response['send_as']
            if 'is_private' in response:
                inbox['is_private'] = response['is_private']

            return {
                "inbox": inbox,
                "result": True
            }

        except Exception as e:
            return {
                "inbox": {},
                "result": False,
                "error": f"Error getting inbox: {str(e)}"
            }

@front.action("list_inbox_conversations")
class ListInboxConversationsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            inbox_id = inputs["inbox_id"]

            # Build query parameters
            params = {}
            if inputs.get("status"):
                params["status"] = inputs["status"]
            if inputs.get("tag_id"):
                params["tag_id"] = inputs["tag_id"]

            limit = inputs.get("limit", 50)
            params["limit"] = min(limit, 100)

            # Make API call to inbox-specific conversations endpoint
            response = await context.fetch(
                f"{FRONT_API_BASE}/inboxes/{inbox_id}/conversations",
                params=params
            )

            # Check for API errors
            if "error" in response:
                return {
                    "conversations": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse conversations
            conversations = []
            raw_conversations = response.get("_results", [])

            for raw_conv in raw_conversations:
                conversations.append(FrontDataParser.parse_conversation(raw_conv))

            return {
                "conversations": conversations,
                "result": True
            }

        except Exception as e:
            return {
                "conversations": [],
                "result": False,
                "error": f"Error listing inbox conversations: {str(e)}"
            }

@front.action("get_conversation")
class GetConversationAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            conversation_id = inputs["conversation_id"]

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/conversations/{conversation_id}"
            )

            # Check for API errors
            if "error" in response:
                return {
                    "conversation": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse conversation - Front returns conversation data directly
            conversation = FrontDataParser.parse_conversation(response)

            return {
                "conversation": conversation,
                "result": True
            }

        except Exception as e:
            return {
                "conversation": {},
                "result": False,
                "error": f"Error getting conversation: {str(e)}"
            }

@front.action("list_conversation_messages")
class ListConversationMessagesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            conversation_id = inputs["conversation_id"]
            limit = inputs.get("limit", 50)

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/conversations/{conversation_id}/messages",
                params={"limit": min(limit, 100)}
            )

            # Check for API errors
            if "error" in response:
                return {
                    "messages": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse messages
            messages = []
            raw_messages = response.get("_results", [])

            for raw_msg in raw_messages:
                messages.append(FrontDataParser.parse_message(raw_msg))

            return {
                "messages": messages,
                "result": True
            }

        except Exception as e:
            return {
                "messages": [],
                "result": False,
                "error": f"Error listing conversation messages: {str(e)}"
            }

@front.action("create_message_reply")
class CreateMessageReplyAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build message payload for reply
            message_data = {
                "type": "reply",
                "conversation_id": inputs["conversation_id"],
                "author_id": inputs["author_id"],
                "body": inputs["body"]
            }

            # Add optional fields
            if inputs.get("to"):
                message_data["to"] = inputs["to"]
            if inputs.get("cc"):
                message_data["cc"] = inputs["cc"]
            if inputs.get("bcc"):
                message_data["bcc"] = inputs["bcc"]
            if inputs.get("subject"):
                message_data["subject"] = inputs["subject"]

            # Create message reply using Front API
            response = await context.fetch(
                f"{FRONT_API_BASE}/messages",
                method="POST",
                json=message_data
            )

            # Check for API errors
            if "error" in response:
                return {
                    "message_uid": "",
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Front returns message_uid for async processing
            return {
                "message_uid": response.get("message_uid", ""),
                "result": True
            }

        except Exception as e:
            return {
                "message_uid": "",
                "result": False,
                "error": f"Error creating message reply: {str(e)}"
            }

@front.action("get_message")
class GetMessageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            message_id = inputs["message_id"]

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/messages/{message_id}"
            )

            # Check for API errors
            if "error" in response:
                return {
                    "message": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse message
            message = FrontDataParser.parse_message(response)

            return {
                "message": message,
                "result": True
            }

        except Exception as e:
            return {
                "message": {},
                "result": False,
                "error": f"Error getting message: {str(e)}"
            }

@front.action("create_message")
class CreateMessageAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            channel_id = inputs["channel_id"]

            # Build message payload for new message
            message_data = {
                "author_id": inputs["author_id"],
                "body": inputs["body"],
                "to": inputs["to"]
            }

            # Add optional fields
            if inputs.get("cc"):
                message_data["cc"] = inputs["cc"]
            if inputs.get("bcc"):
                message_data["bcc"] = inputs["bcc"]
            if inputs.get("subject"):
                message_data["subject"] = inputs["subject"]

            # Create new message using correct Front API endpoint
            response = await context.fetch(
                f"{FRONT_API_BASE}/channels/{channel_id}/messages",
                method="POST",
                json=message_data
            )

            # Check for API errors
            if "error" in response:
                return {
                    "message_uid": "",
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Front returns message_uid for async processing
            return {
                "message_uid": response.get("message_uid", ""),
                "result": True
            }

        except Exception as e:
            return {
                "message_uid": "",
                "result": False,
                "error": f"Error creating message: {str(e)}"
            }

@front.action("list_channels")
class ListChannelsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            limit = inputs.get("limit", 50)

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/channels",
                params={"limit": min(limit, 100)}
            )

            # Check for API errors
            if "error" in response:
                return {
                    "channels": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse channels
            channels = []
            raw_channels = response.get("_results", [])

            for raw_channel in raw_channels:
                channel = {
                    "id": raw_channel.get("id", ""),
                    "name": raw_channel.get("name", ""),
                    "type": raw_channel.get("type", ""),
                }
                # Add optional fields
                if 'address' in raw_channel:
                    channel['address'] = raw_channel['address']
                if 'send_as' in raw_channel:
                    channel['send_as'] = raw_channel['send_as']
                if 'settings' in raw_channel:
                    channel['settings'] = raw_channel['settings']

                channels.append(channel)

            return {
                "channels": channels,
                "result": True
            }

        except Exception as e:
            return {
                "channels": [],
                "result": False,
                "error": f"Error listing channels: {str(e)}"
            }

@front.action("list_inbox_channels")
class ListInboxChannelsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            inbox_id = inputs["inbox_id"]
            limit = inputs.get("limit", 50)

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/inboxes/{inbox_id}/channels",
                params={"limit": min(limit, 100)}
            )

            # Check for API errors
            if "error" in response:
                return {
                    "channels": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse channels
            channels = []
            raw_channels = response.get("_results", [])

            for raw_channel in raw_channels:
                channel = {
                    "id": raw_channel.get("id", ""),
                    "name": raw_channel.get("name", ""),
                    "type": raw_channel.get("type", ""),
                }
                # Add optional fields
                if 'address' in raw_channel:
                    channel['address'] = raw_channel['address']
                if 'send_as' in raw_channel:
                    channel['send_as'] = raw_channel['send_as']
                if 'settings' in raw_channel:
                    channel['settings'] = raw_channel['settings']

                channels.append(channel)

            return {
                "channels": channels,
                "result": True
            }

        except Exception as e:
            return {
                "channels": [],
                "result": False,
                "error": f"Error listing inbox channels: {str(e)}"
            }

@front.action("get_channel")
class GetChannelAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            channel_id = inputs["channel_id"]

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/channels/{channel_id}"
            )

            # Check for API errors
            if "error" in response:
                return {
                    "channel": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse channel
            channel = {
                "id": response.get("id", ""),
                "name": response.get("name", ""),
                "type": response.get("type", ""),
            }

            # Add optional fields
            if 'address' in response:
                channel['address'] = response['address']
            if 'send_as' in response:
                channel['send_as'] = response['send_as']
            if 'settings' in response:
                channel['settings'] = response['settings']
            if 'is_private' in response:
                channel['is_private'] = response['is_private']

            return {
                "channel": channel,
                "result": True
            }

        except Exception as e:
            return {
                "channel": {},
                "result": False,
                "error": f"Error getting channel: {str(e)}"
            }

@front.action("list_message_templates")
class ListMessageTemplatesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            limit = inputs.get("limit", 50)

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/message_templates",
                params={"limit": min(limit, 100)}
            )

            # Check for API errors
            if "error" in response:
                return {
                    "templates": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse templates
            templates = []
            raw_templates = response.get("_results", [])

            for raw_template in raw_templates:
                template = {
                    "id": raw_template.get("id", ""),
                    "name": raw_template.get("name", ""),
                    "subject": raw_template.get("subject"),
                    "body": raw_template.get("body", ""),
                    "attachments": raw_template.get("attachments", []),
                    "metadata": raw_template.get("metadata", {})
                }

                templates.append(template)

            return {
                "templates": templates,
                "result": True
            }

        except Exception as e:
            return {
                "templates": [],
                "result": False,
                "error": f"Error listing message templates: {str(e)}"
            }

@front.action("get_message_template")
class GetMessageTemplateAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            template_id = inputs["message_template_id"]

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/message_templates/{template_id}"
            )

            # Check for API errors
            if "error" in response:
                return {
                    "template": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse template
            template = {
                "id": response.get("id", ""),
                "name": response.get("name", ""),
                "subject": response.get("subject"),
                "body": response.get("body", ""),
                "attachments": response.get("attachments", []),
                "metadata": response.get("metadata", {})
            }

            return {
                "template": template,
                "result": True
            }

        except Exception as e:
            return {
                "template": {},
                "result": False,
                "error": f"Error getting message template: {str(e)}"
            }

@front.action("update_conversation")
class UpdateConversationAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            conversation_id = inputs["conversation_id"]

            # Build update payload
            update_data = {}

            if inputs.get("assignee_id"):
                update_data["assignee_id"] = inputs["assignee_id"]
            if inputs.get("status"):
                update_data["status"] = inputs["status"]
            if inputs.get("tags"):
                update_data["tag_ids"] = inputs["tags"]

            if not update_data:
                return {
                    "conversation": {},
                    "result": False,
                    "error": "No valid update fields provided"
                }

            # Update conversation
            response = await context.fetch(
                f"{FRONT_API_BASE}/conversations/{conversation_id}",
                method="PATCH",
                json=update_data
            )

            # Check for API errors
            if "error" in response:
                return {
                    "conversation": {},
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse response conversation
            conversation = FrontDataParser.parse_conversation(response)

            return {
                "conversation": conversation,
                "result": True
            }

        except Exception as e:
            return {
                "conversation": {},
                "result": False,
                "error": f"Error updating conversation: {str(e)}"
            }

@front.action("list_inboxes")
class ListInboxesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            limit = inputs.get("limit", 50)

            # Make API call
            response = await context.fetch(
                f"{FRONT_API_BASE}/inboxes",
                params={"limit": min(limit, 100)}
            )

            # Check for API errors
            if "error" in response:
                return {
                    "inboxes": [],
                    "result": False,
                    "error": f"API request failed: {response.get('error', 'Unknown error')}"
                }

            # Parse inboxes
            inboxes = []
            raw_inboxes = response.get("_results", [])

            for raw_inbox in raw_inboxes:
                inbox = {
                    "id": raw_inbox.get("id", ""),
                    "name": raw_inbox.get("name", ""),
                    "address": raw_inbox.get("address", ""),
                }
                # Add optional fields
                if 'type' in raw_inbox:
                    inbox['type'] = raw_inbox['type']
                if 'send_as' in raw_inbox:
                    inbox['send_as'] = raw_inbox['send_as']

                inboxes.append(inbox)

            return {
                "inboxes": inboxes,
                "result": True
            }

        except Exception as e:
            return {
                "inboxes": [],
                "result": False,
                "error": f"Error listing inboxes: {str(e)}"
            }



