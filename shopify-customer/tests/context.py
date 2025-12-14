"""
Test context setup for Shopify Customer Account API integration.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shopify_customer import shopify_customer

__all__ = ['shopify_customer']
