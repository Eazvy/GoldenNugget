import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QWidget
from src.gui.liquid.controls import LiquidButton
from src.qt import resources_rc
from src.gui.liquid.restore_changes_panel import RestoreChangesPanel
from src.utils.pages import Page

APP = QApplication.instance() or QApplication([])


class RestoreChangesPanelTests(unittest.TestCase):
    def setUp(self):
        self.window = QWidget()
        self.window.resize(900, 700)
        self.window.apply_in_progress = False
        self.window.device_manager = SimpleNamespace(get_current_device_udid=Mock(return_value='phone-a'))
        self.window.show_ios_page = Mock()
        self.window.apply_changes = Mock(side_effect=lambda pages: setattr(self.window, 'apply_in_progress', True))
        self.window._start_cache_restore = Mock(side_effect=AssertionError('Full backup recovery must not run'))
        self.panel = RestoreChangesPanel(self.window)
        self.panel.anchor = LiquidButton('Restore Changes', self.window)
        self.panel._device_uid = 'phone-a'
        with patch('src.gui.liquid.restore_changes_panel.get_resettable_pages',
                   return_value=[Page.StatusBar, Page.Daemons, Page.Springboard]):
            self.panel._populate()
        self.window.show()
        self.panel.setGeometry(20,20,520,410)
        self.panel.show()
        APP.processEvents()
        self.addCleanup(self.window.deleteLater)
        self.addCleanup(self.window.hide)

    def test_selection_gates_confirmation_and_restores_label(self):
        self.assertEqual(self.panel.anchor.text(), 'Confirm Restore')
        self.assertFalse(self.panel.anchor.isEnabled())
        self.panel.page_switches[Page.Daemons].setChecked(True)
        self.assertTrue(self.panel.anchor.isEnabled())
        if os.environ.get('LIQUID_RESTORE_QA_PATH'):
            self.panel.grab().save(os.environ['LIQUID_RESTORE_QA_PATH'])
        self.panel._confirm()
        self.window.apply_changes.assert_called_once_with([Page.Daemons])
        self.window._start_cache_restore.assert_not_called()
        self.window.show_ios_page.assert_called_once_with(6)
        self.assertEqual(self.panel.anchor.text(), 'Restore Changes')

    def test_select_all_and_deselect_one(self):
        self.assertEqual(next(iter(self.panel.page_switches)), Page.Daemons)
        self.panel.all_switch.setChecked(True)
        self.assertEqual(self.panel.selected_pages, set(self.panel.page_switches))
        self.panel.page_switches[Page.StatusBar].setChecked(False)
        self.assertFalse(self.panel.all_switch.isChecked())
        self.assertEqual(self.panel.selected_pages, {Page.Daemons, Page.Springboard})

    def test_device_change_requires_new_selection(self):
        self.panel.page_switches[Page.Daemons].setChecked(True)
        self.window.device_manager.get_current_device_udid.return_value = 'phone-b'
        with patch('src.gui.liquid.restore_changes_panel.get_resettable_pages', return_value=[Page.Daemons]):
            self.panel._confirm()
        self.window.apply_changes.assert_not_called()
        self.assertEqual(self.panel.selected_pages, set())
