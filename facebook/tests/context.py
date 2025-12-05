# -*- coding: utf-8 -*-
"""
Test context setup.

This module sets up the Python path so that the facebook package
can be imported with proper relative imports working.
"""
import sys
import os

# Add the parent of 'facebook' to sys.path so 'facebook' is importable as a package
# This allows relative imports within the facebook package to work correctly
_facebook_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _facebook_parent not in sys.path:
    sys.path.insert(0, _facebook_parent)

# Also add dependencies path if it exists
_dependencies_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dependencies"))
if os.path.exists(_dependencies_path) and _dependencies_path not in sys.path:
    sys.path.insert(0, _dependencies_path)

from facebook.facebook import facebook
