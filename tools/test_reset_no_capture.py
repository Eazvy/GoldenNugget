#!/usr/bin/env python3
"""Offline regression gate for scoped preference reset (no device access)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

suite = unittest.defaultTestLoader.discover(
    str(ROOT / 'tests'), pattern='test_default_reset.py')
suite.addTests(unittest.defaultTestLoader.discover(
    str(ROOT / 'tests'), pattern='test_managed_preference_mirrors.py'))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
