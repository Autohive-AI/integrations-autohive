import os
import sys

# Add parent directory to path so we can import the integration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import microsoft365