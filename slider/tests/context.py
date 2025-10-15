import sys
import os

# Get absolute path to parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# CRITICAL: Change to parent directory BEFORE importing
# Integration.load() needs to find config.json in cwd
original_cwd = os.getcwd()
os.chdir(parent_dir)

# Add parent directory to path so we can import
sys.path.insert(0, parent_dir)

# Now import (Integration.load() will find config.json)
from slide_maker import slide_maker
