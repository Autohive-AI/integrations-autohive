"""Pytest configuration - sets up import path to match deployment environment."""
import sys
import os

# Add this directory to path so absolute imports work like in deployment
_integration_dir = os.path.dirname(os.path.abspath(__file__))
if _integration_dir not in sys.path:
    sys.path.insert(0, _integration_dir)
