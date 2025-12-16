# -*- coding: utf-8 -*-

import sys
import os

# Set working directory to parent so config.json can be found
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(parent_dir)

sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../dependencies")))

from google_ads import google_ads