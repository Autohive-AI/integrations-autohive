"""
Humanitix Integration for Autohive

This module provides event management functionality including:
- Event retrieval (single or list)
- Order management for events
- Ticket information and check-in status
- Tag categorization

All actions use the Humanitix Public API v1.
Humanitix is a non-profit ticketing platform where 100% of profits go to charity.
"""

from autohive_integrations_sdk import Integration
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
humanitix = Integration.load(config_path)

# Import actions to register handlers
import actions
