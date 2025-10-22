from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import mistune

# Create the integration using the config.json
circle = Integration.load()

# Circle Admin API Base URL - v2
CIRCLE_API_BASE = "https://app.circle.so/api/admin/v2"

# ---- TipTap Converter ----

class TipTapRenderer(mistune.BaseRenderer):
    """Single-pass renderer that emits TipTap/ProseMirror JSON directly."""
    
    NAME = 'tiptap'
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.options = {
            "allow_images": False,
            "allow_tables": False,
            "allow_underline": False,
            "unsupported_policy": "degrade",  # degrade|codeblock|drop
        }
        if options:
            self.options.update(options)
    
    # Helper methods
    def _marks(self, state) -> List[Dict[str, Any]]:
        """Get the current marks stack from state."""
        return state.env.setdefault("marks", [])
    
    def _with_mark(self, state, mark: Dict[str, Any]):
        """Context manager for applying marks."""
        class MarkContext:
            def __init__(self, marks, mark):
                self.marks = marks
                self.mark = mark
            
            def __enter__(self):
                self.marks.append(self.mark)
                return self
            
            def __exit__(self, *args):
                self.marks.pop()
        
        return MarkContext(self._marks(state), mark)
    
    def _text_node(self, text: str, state) -> Optional[Dict[str, Any]]:
        """Create a text node with current marks."""
        if not text:
            return None
        node = {"type": "text", "text": text}
        if self._marks(state):
            node["marks"] = list(self._marks(state))
        return node
    
    def _normalize_inline(self, nodes: List[Any]) -> List[Dict[str, Any]]:
        """Merge adjacent text nodes with identical marks."""
        out = []
        for n in nodes or []:
            if not n:
                continue
            if out and out[-1].get("type") == "text" and n.get("type") == "text":
                if out[-1].get("marks", []) == n.get("marks", []):
                    out[-1]["text"] += n["text"]
                    continue
            out.append(n)
        return out
    
    def _wrap_inline_in_paragraph(self, children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Wrap inline content in paragraph for block contexts like listItem."""
        if not children:
            return [{"type": "paragraph", "content": []}]
        
        block_types = {"paragraph", "heading", "bulletList", "orderedList", "blockquote", "codeBlock", "horizontalRule"}
        has_block = any(c.get("type") in block_types for c in children)
        
        if has_block:
            return children
        
        return [{"type": "paragraph", "content": self._normalize_inline(children)}]
    
    def _render_children(self, token, state) -> List[Any]:
        """Render child tokens."""
        children = token.get("children")
        if not children:
            return []
        result = []
        for child in children:
            rendered = self.render_token(child, state)
            if rendered is not None:
                if isinstance(rendered, list):
                    result.extend(rendered)
                else:
                    result.append(rendered)
        return result
    
    # Block-level elements
    def paragraph(self, token, state):
        children = self._normalize_inline(self._render_children(token, state))
        return {"type": "paragraph", "content": children}
    
    def heading(self, token, state):
        level = token["attrs"]["level"]
        children = self._normalize_inline(self._render_children(token, state))
        return {"type": "heading", "attrs": {"level": level}, "content": children}
    
    def list(self, token, state):
        ordered = token["attrs"].get("ordered", False)
        children = self._render_children(token, state)
        list_type = "orderedList" if ordered else "bulletList"
        return {"type": list_type, "content": [c for c in children if c]}
    
    def list_item(self, token, state):
        children = self._render_children(token, state)
        children = [c for c in children if c]
        return {"type": "listItem", "content": self._wrap_inline_in_paragraph(children)}
    
    def block_quote(self, token, state):
        children = self._render_children(token, state)
        return {"type": "blockquote", "content": [c for c in children if c]}
    
    def block_code(self, token, state):
        info = (token.get("attrs", {}) or {}).get("info") or ""
        lang = (info.strip().split() or [None])[0] or None
        content = [{"type": "text", "text": token["raw"]}] if token.get("raw") else []
        
        node = {"type": "codeBlock"}
        if lang:
            node["attrs"] = {"language": lang}
        node["content"] = content
        return node
    
    def thematic_break(self, token, state):
        return {"type": "horizontalRule"}
    
    # Inline elements and marks
    def strong(self, token, state):
        with self._with_mark(state, {"type": "bold"}):
            return self._render_children(token, state)
    
    def emphasis(self, token, state):
        with self._with_mark(state, {"type": "italic"}):
            return self._render_children(token, state)
    
    def strikethrough(self, token, state):
        with self._with_mark(state, {"type": "strike"}):
            return self._render_children(token, state)
    
    def codespan(self, token, state):
        with self._with_mark(state, {"type": "code"}):
            return [self._text_node(token["raw"], state)]
    
    def link(self, token, state):
        attrs = {"href": token["attrs"]["url"]}
        title = token["attrs"].get("title")
        if title:
            attrs["title"] = title
        
        with self._with_mark(state, {"type": "link", "attrs": attrs}):
            return self._render_children(token, state)
    
    def image(self, token, state):
        attrs = token.get("attrs", {})
        if self.options["allow_images"]:
            node = {
                "type": "image",
                "attrs": {
                    "src": attrs.get("url", ""),
                    "alt": attrs.get("alt", "")
                }
            }
            if attrs.get("title"):
                node["attrs"]["title"] = attrs["title"]
            return node
        
        # Degrade to alt text
        alt = attrs.get("alt", "")
        return self._text_node(alt, state) if alt else None
    
    def linebreak(self, token, state):
        return {"type": "hardBreak"}
    
    def softbreak(self, token, state):
        return {"type": "hardBreak"}
    
    def text(self, token, state):
        return self._text_node(token["raw"], state)
    
    def blank_line(self, token, state):
        return None
    
    # Tables
    def table(self, token, state):
        if self.options["allow_tables"]:
            pass
        
        # Degrade to pipe-separated paragraphs
        rows = []
        
        def extract_text(node):
            """Extract plain text from nested structure."""
            if isinstance(node, dict):
                if node.get("type") == "text":
                    return node.get("text", node.get("raw", ""))
                children = node.get("children", [])
                return "".join(extract_text(ch) for ch in children)
            return ""
        
        # Walk table structure
        for section in token.get("children", []):
            for row in section.get("children", []):
                if row.get("type") == "table_row":
                    cells = []
                    for cell in row.get("children", []):
                        cell_text = extract_text(cell)
                        cells.append(cell_text.strip())
                    rows.append(" | ".join(cells))
        
        # Build paragraph with hard breaks
        content = []
        for i, line in enumerate(rows):
            if i:
                content.append({"type": "hardBreak"})
            content.append({"type": "text", "text": line})
        
        return {"type": "paragraph", "content": content} if content else None
    
    def table_head(self, token, state):
        return token
    
    def table_body(self, token, state):
        return token
    
    def table_row(self, token, state):
        return token
    
    def table_cell(self, token, state):
        return token
    
    # HTML handling
    def block_html(self, token, state):
        policy = self.options["unsupported_policy"]
        raw = token.get("raw", "")
        
        if policy == "codeblock":
            return {"type": "codeBlock", "content": [{"type": "text", "text": raw}]}
        elif policy == "degrade":
            import re
            text = re.sub(r'<[^>]+>', '', raw).strip()
            return {"type": "paragraph", "content": [{"type": "text", "text": text}]} if text else None
        
        return None
    
    def inline_html(self, token, state):
        return self.block_html(token, state)
    
    def block_text(self, token, state):
        return self._render_children(token, state)
    
    def block_error(self, token, state):
        children = self._render_children(token, state)
        return children
    
    # Override token rendering to collect results instead of joining strings
    def render_tokens(self, tokens, state):
        """Render tokens and collect results, returning a doc structure."""
        content = []
        for tok in tokens:
            rendered = self.render_token(tok, state)
            if rendered is not None:
                if isinstance(rendered, list):
                    content.extend([r for r in rendered if r and isinstance(r, dict)])
                elif isinstance(rendered, dict):
                    content.append(rendered)
        
        return {"type": "doc", "content": content}


def text_to_tiptap_body(text: str) -> Dict[str, Any]:
    """Convert markdown to TipTap format for Circle API."""
    md = mistune.create_markdown(
        renderer=TipTapRenderer({
            "allow_images": False,
            "allow_tables": False,
            "allow_underline": False,
            "unsupported_policy": "degrade",
        }),
        plugins=["strikethrough", "table", "url"]
    )
    doc = md(text)
    return doc

# ---- Utility Functions ----

def build_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """Build authorization headers for Circle API"""
    api_token = context.auth.get("credentials", {}).get("api_token")
    if not api_token:
        raise Exception("Circle API token is required in auth (field 'api_token').")
    
    # Circle API expects "Token AUTH_TOKEN" format
    return {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json"
    }


def build_search_params(inputs: Dict[str, Any], allowed_params: List[str]) -> Dict[str, Any]:
    """Build query parameters from inputs, filtering only allowed params"""
    params = {}
    for key in allowed_params:
        if key in inputs and inputs[key] is not None:
            params[key] = inputs[key]
    return params


def handle_api_response(response: Dict[str, Any], default_return: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Check API response for errors and handle HTML responses.
    Returns error dict if there's an error, None if response is valid.
    """
    if "error" in response:
        error_msg = response.get('error', 'Unknown error')
        # Truncate HTML error pages
        if isinstance(error_msg, str) and len(error_msg) > 500:
            error_msg = "API request failed. Received HTML error page instead of JSON. Check endpoint URL and authentication."
        
        return {
            **default_return,
            "result": False,
            "error": f"API request failed: {error_msg}"
        }
    return None


# ---- Post Actions ----

@circle.action("search_posts")
class SearchPostsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            # Build query parameters
            params = build_search_params(inputs, ["query", "space_id", "tag", "status", "per_page", "page"])
            
            # Default per_page if not provided
            if "per_page" not in params:
                params["per_page"] = 10

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts",
                headers=headers,
                params=params
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"posts": [], "count": 0})
            if error_response:
                return error_response

            # Parse response - Circle API returns paginated data
            posts = response.get("records", [])
            count = response.get("count", 0)

            return {
                "posts": posts,
                "count": count,
                "result": True
            }

        except Exception as e:
            return {
                "posts": [],
                "count": 0,
                "result": False,
                "error": f"Error searching posts: {str(e)}"
            }


@circle.action("get_post")
class GetPostAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            post_id = inputs["post_id"]

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts/{post_id}",
                headers=headers
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"post": {}})
            if error_response:
                return error_response

            return {
                "post": response,
                "result": True
            }

        except Exception as e:
            return {
                "post": {},
                "result": False,
                "error": f"Error getting post: {str(e)}"
            }


@circle.action("create_post")
class CreatePostAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)

            # Convert body text to TipTap format
            tiptap_doc = text_to_tiptap_body(inputs["body"])

            # Build post payload
            post_data = {
                "space_id": inputs["space_id"],
                "name": inputs["name"],
                "tiptap_body": {
                    "body": tiptap_doc
                },
                "status": inputs.get("status", "published"),
                "is_pinned": inputs.get("is_pinned", False),
                "is_comments_enabled": inputs.get("is_comments_enabled", True)
            }

            # Add optional user_email if provided
            if "user_email" in inputs:
                post_data["user_email"] = inputs["user_email"]

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts",
                headers=headers,
                method="POST",
                json=post_data
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"post": {}})
            if error_response:
                return error_response

            return {
                "post": response,
                "result": True
            }

        except Exception as e:
            return {
                "post": {},
                "result": False,
                "error": f"Error creating post: {str(e)}"
            }


@circle.action("update_post")
class UpdatePostAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            post_id = inputs["post_id"]

            # Build update payload - only include provided fields
            update_data = {}
            if "name" in inputs:
                update_data["name"] = inputs["name"]
            if "body" in inputs:
                update_data["body"] = inputs["body"]
            if "status" in inputs:
                update_data["status"] = inputs["status"]
            if "is_pinned" in inputs:
                update_data["is_pinned"] = inputs["is_pinned"]

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts/{post_id}",
                headers=headers,
                method="PUT",
                json=update_data
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"post": {}})
            if error_response:
                return error_response

            return {
                "post": response,
                "result": True
            }

        except Exception as e:
            return {
                "post": {},
                "result": False,
                "error": f"Error updating post: {str(e)}"
            }


# ---- Member Actions ----

@circle.action("search_member_by_email")
class SearchMemberByEmailAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)

            # Build query parameters - email is required
            params = {"email": inputs["email"]}

            # Make API call - use /community_members/search for v2
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/community_members/search",
                headers=headers,
                params=params
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"member": {}})
            if error_response:
                return error_response

            return {
                "member": response,
                "result": True
            }

        except Exception as e:
            return {
                "member": {},
                "result": False,
                "error": f"Error searching member by email: {str(e)}"
            }


@circle.action("list_members")
class ListMembersAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)

            # Build query parameters
            params = build_search_params(inputs, ["status", "per_page", "page"])
            
            # Default per_page if not provided
            if "per_page" not in params:
                params["per_page"] = 10

            # Make API call - GET /community_members lists all members
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/community_members",
                headers=headers,
                params=params
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"members": [], "count": 0})
            if error_response:
                return error_response

            # Parse response
            members = response.get("records", [])
            count = response.get("count", 0)

            return {
                "members": members,
                "count": count,
                "result": True
            }

        except Exception as e:
            return {
                "members": [],
                "count": 0,
                "result": False,
                "error": f"Error listing members: {str(e)}"
            }


@circle.action("get_member")
class GetMemberAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            member_id = inputs["member_id"]

            # Make API call - use /community_members/{id} for v2
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/community_members/{member_id}",
                headers=headers
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"member": {}})
            if error_response:
                return error_response

            return {
                "member": response,
                "result": True
            }

        except Exception as e:
            return {
                "member": {},
                "result": False,
                "error": f"Error getting member: {str(e)}"
            }


# ---- Space Actions ----

@circle.action("search_spaces")
class SearchSpacesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            # Build query parameters
            params = build_search_params(inputs, ["query", "space_type", "per_page", "page"])
            
            # Default per_page if not provided
            if "per_page" not in params:
                params["per_page"] = 10

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/spaces",
                headers=headers,
                params=params
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"spaces": [], "count": 0})
            if error_response:
                return error_response

            # Parse response
            spaces = response.get("records", [])
            count = response.get("count", 0)

            return {
                "spaces": spaces,
                "count": count,
                "result": True
            }

        except Exception as e:
            return {
                "spaces": [],
                "count": 0,
                "result": False,
                "error": f"Error searching spaces: {str(e)}"
            }


@circle.action("get_space")
class GetSpaceAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            space_id = inputs["space_id"]

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/spaces/{space_id}",
                headers=headers
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"space": {}})
            if error_response:
                return error_response

            return {
                "space": response,
                "result": True
            }

        except Exception as e:
            return {
                "space": {},
                "result": False,
                "error": f"Error getting space: {str(e)}"
            }


# ---- Event Actions ----

@circle.action("search_events")
class SearchEventsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            # Build query parameters
            params = build_search_params(inputs, ["query", "time_filter", "space_id", "per_page", "page"])
            
            # Default per_page if not provided
            if "per_page" not in params:
                params["per_page"] = 10

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/events",
                headers=headers,
                params=params
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"events": [], "count": 0})
            if error_response:
                return error_response

            # Parse response
            events = response.get("records", [])
            count = response.get("count", 0)

            return {
                "events": events,
                "count": count,
                "result": True
            }

        except Exception as e:
            return {
                "events": [],
                "count": 0,
                "result": False,
                "error": f"Error searching events: {str(e)}"
            }


@circle.action("get_event")
class GetEventAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            event_id = inputs["event_id"]

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/events/{event_id}",
                headers=headers
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"event": {}})
            if error_response:
                return error_response

            return {
                "event": response,
                "result": True
            }

        except Exception as e:
            return {
                "event": {},
                "result": False,
                "error": f"Error getting event: {str(e)}"
            }


# ---- Comment Actions ----

@circle.action("create_comment")
class CreateCommentAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            post_id = inputs["post_id"]
            
            # Build comment payload
            comment_data = {
                "body": inputs["body"]
            }

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts/{post_id}/comments",
                headers=headers,
                method="POST",
                json=comment_data
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"comment": {}})
            if error_response:
                return error_response

            return {
                "comment": response,
                "result": True
            }

        except Exception as e:
            return {
                "comment": {},
                "result": False,
                "error": f"Error creating comment: {str(e)}"
            }


@circle.action("get_post_comments")
class GetPostCommentsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            post_id = inputs["post_id"]
            per_page = inputs.get("per_page", 20)

            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/posts/{post_id}/comments",
                headers=headers,
                params={"per_page": per_page}
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"comments": [], "count": 0})
            if error_response:
                return error_response

            # Parse response
            comments = response.get("records", [])
            count = response.get("count", 0)

            return {
                "comments": comments,
                "count": count,
                "result": True
            }

        except Exception as e:
            return {
                "comments": [],
                "count": 0,
                "result": False,
                "error": f"Error getting post comments: {str(e)}"
            }


# ---- Community Actions ----

@circle.action("get_community_info")
class GetCommunityInfoAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = build_auth_headers(context)
            
            # Make API call
            response = await context.fetch(
                f"{CIRCLE_API_BASE}/community",
                headers=headers
            )

            # Check for API errors or HTML responses
            error_response = handle_api_response(response, {"community": {}})
            if error_response:
                return error_response

            return {
                "community": response,
                "result": True
            }

        except Exception as e:
            return {
                "community": {},
                "result": False,
                "error": f"Error getting community info: {str(e)}"
            }
