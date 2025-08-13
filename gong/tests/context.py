# -*- coding: utf-8 -*-

import sys
import os

CURRENT_DIR = os.path.dirname(__file__)
INTEGRATION_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
DEPS_DIR = os.path.join(INTEGRATION_DIR, 'dependencies')

sys.path.insert(0, INTEGRATION_DIR)
if os.path.isdir(DEPS_DIR):
    sys.path.insert(0, DEPS_DIR)

import importlib.util

_module_path = os.path.join(INTEGRATION_DIR, "gong.py")
spec = importlib.util.spec_from_file_location("gong_module", _module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[attr-defined]

gong = module.gong  # integration instance defined in gong.py

