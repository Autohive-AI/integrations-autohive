# -*- coding: utf-8 -*-
import sys
import os

# Add paths for imports FIRST
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../dependencies")))

# Now we can import the doc-maker module
try:
    # Import from the doc_maker module
    import importlib.util
    spec = importlib.util.spec_from_file_location("doc_maker", os.path.join(os.path.dirname(__file__), '..', 'doc_maker.py'))
    doc_maker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(doc_maker_module)

    doc_maker = doc_maker_module.doc_maker
except ImportError as e:
    print(f"Import error: {e}")
    print("Available sys.path entries:")
    for path in sys.path[:5]:  # Show first 5 paths
        print(f"  {path}")
    raise