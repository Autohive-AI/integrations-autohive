"""
Test context for Shopify Admin API integration.
Sets up import paths for testing.
"""

import sys
import os

# Add parent directory to path for importing the integration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add dependencies directory for SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dependencies")))

from shopify_admin import shopify_admin
