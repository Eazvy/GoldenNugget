"""Run the custom interface regressions through the isolated offline runner."""
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

from PySide6.QtCore import QSettings,QStandardPaths

QStandardPaths.setTestModeEnabled(True)
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat,QSettings.UserScope,os.environ.get('XDG_CONFIG_HOME',str(ROOT/'test-results/config')))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(not result.wasSuccessful())
