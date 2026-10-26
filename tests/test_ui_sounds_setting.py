import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from PySide6.QtCore import QObject, QPoint, QSettings
from PySide6.QtWidgets import QApplication
from src.gui.liquid.sounds import UiSounds

APP = QApplication.instance() or QApplication([])


class UiSoundsSettingTests(unittest.TestCase):
    def sounds(self):
        sounds = UiSounds.__new__(UiSounds)
        QObject.__init__(sounds)
        sounds.effects = {name: Mock() for name in ('toggle', 'untoggle', 'favorite', 'unfavorite', 'ui_hover')}
        sounds.enabled = True
        sounds._settings = None
        sounds._hover_click_position = None
        sounds._last_ui_hover_position = None
        sounds._native = False
        return sounds

    def test_mute_stops_current_audio_and_blocks_all_playback(self):
        sounds = self.sounds()
        sounds.set_enabled(False)
        for name in sounds.effects:
            sounds.play(name)
        sounds.play_ui_hover(QPoint(20, 20))
        for effect in sounds.effects.values():
            effect.stop.assert_called_once()
            effect.play.assert_not_called()

    def test_setting_is_saved_and_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'settings.ini')
            sounds = self.sounds()
            sounds.configure(QSettings(path, QSettings.IniFormat))
            self.assertTrue(sounds.enabled)
            sounds.set_enabled(False)
            reopened = self.sounds()
            reopened.configure(QSettings(path, QSettings.IniFormat))
            self.assertFalse(reopened.enabled)
            reopened.set_enabled(True)
            reopened.play('toggle')
            reopened.effects['toggle'].play.assert_called_once()
