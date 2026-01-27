"""
Shotstack Video Editing Integration for Autohive

This module provides comprehensive video editing capabilities including:
- File upload and management
- Video rendering with timeline control
- High-level editing actions (compose, overlay, trim, concatenate)
- Text and logo overlays
- Audio track management

All actions use the Shotstack Edit and Ingest APIs.
"""

from autohive_integrations_sdk import Integration
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
shotstack = Integration.load(config_path)

# Import actions to register handlers
try:
    from . import actions
except ImportError:
    import actions
