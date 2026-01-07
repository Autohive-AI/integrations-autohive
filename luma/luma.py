"""
Luma Event Platform Integration for Autohive

This module provides comprehensive Luma event management including:
- Event creation, retrieval, and updates
- Guest management (list, add, update status)
- Invitation sending
- Ticket type and coupon management
- Calendar people and contacts

All actions use the Luma Public API v1.
Authentication via API key in the x-luma-api-key header.
"""

from autohive_integrations_sdk import Integration
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
luma = Integration.load(config_path)

import actions  # noqa: F401 - registers action handlers
