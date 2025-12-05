"""
Facebook Pages Integration for Autohive

This module provides comprehensive Facebook Pages management including:
- Page discovery and listing
- Post creation (text, photo, video, links) with scheduling
- Post retrieval and deletion
- Comment management (read, reply, hide, delete)
- Page and post insights/analytics

All actions use the Facebook Graph API v21.0.

Action implementations are organized in the `actions/` subpackage:
- actions/pages.py: Page discovery
- actions/posts.py: Post CRUD operations
- actions/comments.py: Comment management
- actions/insights.py: Analytics
"""

from autohive_integrations_sdk import Integration
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
facebook = Integration.load(config_path)

from . import actions
