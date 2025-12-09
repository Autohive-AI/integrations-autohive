# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../dependencies")))

<<<<<<<< HEAD:facebook/tests/context.py
from facebook import facebook
========
from google_ads import google_ads
>>>>>>>> d9079d6 (Rename adwords_tool to google_ads and update to SDK v1.0.2):google_ads/tests/context.py
