# -*- coding: utf-8 -*-
import sys
import os

# Add parent directory and dependencies to path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../dependencies")))

# Import the circle integration
from circle import circle