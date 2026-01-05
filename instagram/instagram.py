"""
Instagram Business/Creator Integration for Autohive

This module provides comprehensive Instagram management including:
- Account information retrieval
- Media publishing (images, videos, reels, carousels, stories)
- Media retrieval and deletion
- Comment management (read, reply, hide, delete)
- Account and media insights/analytics
- Mentions and hashtag discovery
- Direct messaging

All actions use the Instagram Graph API v24.0.
"""

from autohive_integrations_sdk import Integration
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
instagram = Integration.load(config_path)

# Import actions to register handlers
import actions  # noqa: F401 - import triggers action registration via decorators
