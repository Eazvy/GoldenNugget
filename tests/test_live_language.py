import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QCoreApplication, QLocale, QSettings, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QLabel, QLineEdit, QStackedWidget,
    QVBoxLayout, QWidget,
)
from src.qt import resources_rc
from src.controllers.translator import Translator
from src.gui.ios.settings import IOSSettingsPage

APP = QApplication.instance() or QApplication([])


class LiveLanguageTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.old_locale = QLocale()
        self.old_direction = APP.layoutDirection()
        self.settings = QSettings(str(Path(self.folder.name) / 'settings.ini'), QSettings.IniFormat)
        self.settings.setValue('locale_code', 'en')
        self.translator = Translator(APP, self.settings)
        self.translator.set_default_locale('en')
        self.translator.load_translations()
        self.window = QWidget()
        layout = QVBoxLayout(self.window)
        self.pages = QStackedWidget()
        self.pages.addWidget(QWidget())
        body = QWidget()
        inner = QVBoxLayout(body)
        self.label = QLabel('App Language')
        self.input = QLineEdit('App Language')
        self.check = QCheckBox('Existing option')
        self.check.setChecked(True)
        self.combo = QComboBox()
        self.combo.setProperty('liveTranslateItems', True)
        self.combo.addItems(['App Language', 'Other choice'])
        self.user_combo = QComboBox()
        self.user_combo.addItem('App Language', 'user-entry')
        for widget in (self.label, self.input, self.check, self.combo, self.user_combo):
            inner.addWidget(widget)
        self.pages.addWidget(body)
        self.pages.setCurrentIndex(1)
        layout.addWidget(self.pages)
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        for translator in self.translator._installed_translators:
            APP.removeTranslator(translator)
            translator.deleteLater()
        QLocale.setDefault(self.old_locale)
        APP.setLayoutDirection(self.old_direction)

    def test_language_updates_existing_widgets_without_exec_or_state_loss(self):
        changed = []
        self.combo.currentTextChanged.connect(changed.append)
        with patch('src.controllers.translator.os.execl') as restart:
            self.translator.set_new_language('fr')
            restart.assert_not_called()
        self.assertEqual(self.label.text(), "Langue de l'application")
        self.assertEqual(self.combo.currentText(), self.label.text())
        self.assertEqual(changed, [])
        self.assertEqual(self.input.text(), 'App Language')
        self.assertEqual(self.user_combo.currentText(), 'App Language')
        self.assertEqual(self.user_combo.currentData(), 'user-entry')
        self.assertTrue(self.check.isChecked())
        self.assertEqual(self.pages.currentIndex(), 1)
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.settings.value('locale_code'), 'fr')

    def test_switching_back_and_rtl_direction_are_live(self):
        self.translator.set_new_language('fr')
        self.translator.set_new_language('en')
        self.assertEqual(self.label.text(), 'App Language')
        self.translator.set_new_language('ar')
        self.assertEqual(APP.layoutDirection(), Qt.RightToLeft)
        self.translator.set_new_language('en')
        self.assertEqual(APP.layoutDirection(), Qt.LeftToRight)

    def test_language_selectors_stay_in_sync_without_restart(self):
        mirror = QComboBox(self.window)
        mirror.addItems(['System', 'French'])
        main = QComboBox(self.window)
        main.addItems(['System', 'French'])
        translator = Mock()
        window = SimpleNamespace(settings=self.settings, translator=translator,
                                 liquid=SimpleNamespace(settings=SimpleNamespace(language=mirror)))
        page = SimpleNamespace(window=window, lang_indexes=['', 'fr'], lang_drp=main)
        IOSSettingsPage._on_lang_selected(page, 1)
        translator.set_new_language.assert_called_once_with('fr')
        self.assertEqual(main.currentIndex(), 1)
        self.assertEqual(mirror.currentIndex(), 1)
