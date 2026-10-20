#!/usr/bin/env python3
"""Home artwork sizing and refresh regressions, without device access."""
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PySide6.QtGui import QBitmap, QRegion
from PySide6.QtWidgets import QApplication, QLabel, QFrame
from src.qt import resources_rc
from src.gui.ios.feature_icons import FEATURE_ICONS
from src.gui.ios.home import IOSHomePage

APP = QApplication.instance() or QApplication([])


class FeatureArtwork(unittest.TestCase):
    def test_passcode_artwork_uses_requested_size(self):
        home = SimpleNamespace(_c=SimpleNamespace(text_primary='#ffffff'),
                               devicePixelRatioF=lambda: 1)
        label = QLabel()
        label.setFixedSize(140, 128)
        IOSHomePage._paint_tile_icon(home, label, FEATURE_ICONS['Passcode Theme'])
        bounds = QRegion(QBitmap.fromImage(label.pixmap().toImage().createAlphaMask())).boundingRect()
        self.assertGreaterEqual(bounds.height(), 124)
        self.assertLessEqual(abs(bounds.center().x() - label.rect().center().x()), 1)

    def test_device_refresh_reuses_tile_renderer(self):
        icon, title, caption = QLabel(), QLabel(), QLabel()
        resource = FEATURE_ICONS['Passcode Theme']
        renderer = Mock()
        home = SimpleNamespace(
            window=SimpleNamespace(device_manager=Mock()),
            passcode_theme_card=QFrame(),
            _tiles=[(icon, resource, title, caption)],
            _c=SimpleNamespace(text_secondary='#aaaaaa', text_primary='#ffffff', text_disabled='#666666'),
            _paint_tile_icon=renderer)
        with patch('src.gui.ios.home.current_passcode_theme_reason', return_value=None):
            IOSHomePage.update_passcode_support(home)
        renderer.assert_called_once_with(icon, resource)


if __name__ == '__main__':
    unittest.main()
