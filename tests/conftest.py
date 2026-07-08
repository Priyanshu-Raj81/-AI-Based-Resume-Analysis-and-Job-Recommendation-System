"""
Ensures the project root is on sys.path so `from utils.xxx import yyy`
resolves correctly no matter where `pytest` is invoked from.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)