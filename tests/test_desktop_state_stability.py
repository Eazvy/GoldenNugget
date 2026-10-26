import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QLabel
from src.controllers.autosave_store import write_autosave
from src.gui.main_window_mixins import DeviceBarMixin
from src.gui.ios.viewport_rows import _ViewportRow

APP = QApplication.instance() or QApplication([])


class DesktopStateStabilityTests(unittest.TestCase):
    def test_stale_instance_does_not_undo_other_instance_toggle(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'AutoSave.json'
            original = {'tweaks': {'A': {'enabled': False}, 'B': {'enabled': False}}}
            baseline_a = write_autosave(path, original)
            baseline_b = json.loads(json.dumps(baseline_a))
            changed_b = {'tweaks': {'A': {'enabled': True}, 'B': {'enabled': False}}}
            write_autosave(path, changed_b, baseline_b)
            baseline_a = write_autosave(path, original, baseline_a)
            self.assertTrue(json.loads(path.read_text())['tweaks']['A']['enabled'])
            original['tweaks']['B']['enabled'] = True
            write_autosave(path, original, baseline_a)
            values = json.loads(path.read_text())['tweaks']
            self.assertTrue(values['A']['enabled'])
            self.assertTrue(values['B']['enabled'])

    def test_failed_write_preserves_original_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'AutoSave.json'
            baseline = write_autosave(path, {'tweaks': {'A': {'enabled': False}}})
            original = path.read_bytes()
            with patch('src.controllers.autosave_store.os.replace', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    write_autosave(path, {'tweaks': {'A': {'enabled': True}}}, baseline)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual([p.name for p in path.parent.iterdir()], ['AutoSave.json'])

    def test_different_daemon_toggles_from_two_instances_are_merged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'AutoSave.json'
            original = {'tweaks': {'Daemons': {'enabled': True, 'value': {'A': False, 'B': False}}}}
            baseline = write_autosave(path, original)
            write_autosave(path, {'tweaks': {'Daemons': {
                'enabled': True, 'value': {'A': True, 'B': False}}}}, baseline)
            write_autosave(path, {'tweaks': {'Daemons': {
                'enabled': True, 'value': {'A': False, 'B': True}}}}, baseline)
            self.assertEqual(json.loads(path.read_text())['tweaks']['Daemons']['value'],
                             {'A': True, 'B': True})

    def test_invalid_autosave_is_not_replaced_with_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'AutoSave.json'
            path.write_text('{incomplete')
            with self.assertRaises(ValueError):
                write_autosave(path, {'tweaks': {}})
            self.assertEqual(path.read_text(), '{incomplete')

    def test_false_values_and_unknown_controls_survive(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'AutoSave.json'
            write_autosave(path, {'tweaks': {'OtherEdition': {'enabled': True}}})
            write_autosave(path, {'tweaks': {'A': {'enabled': False, 'state': False, 'value': 0}}})
            values = json.loads(path.read_text())['tweaks']
            self.assertTrue(values['OtherEdition']['enabled'])
            self.assertIs(values['A']['state'], False)
            self.assertEqual(values['A']['value'], 0)

    def test_reconnect_returns_to_previous_category_not_home(self):
        stack = QStackedWidget()
        shell = QWidget()
        placeholder = QWidget()
        stack.addWidget(shell)
        stack.addWidget(placeholder)
        pages = QStackedWidget()
        for _ in range(4):
            pages.addWidget(QWidget())
        pages.setCurrentIndex(2)
        navigation = []
        window = SimpleNamespace(
            connect_placeholder=placeholder, content_stack=stack, ios_pages=pages,
            device_manager=SimpleNamespace(devices=[]), apply_in_progress=False,
            device_scan_completed=True,
            set_ios_page=lambda index, **kwargs: navigation.append(index),
            _update_shared_nav=lambda index: None)
        DeviceBarMixin._update_device_gate(window)
        self.assertIs(stack.currentWidget(), placeholder)
        window.device_manager.devices = [object()]
        DeviceBarMixin._update_device_gate(window)
        self.assertEqual(navigation, [2])
        stack.close()
        pages.close()

    def test_virtualization_does_not_change_row_height(self):
        card = QWidget()
        layout = QVBoxLayout(card)
        label = QLabel('A detailed description. ' * 20)
        label.setWordWrap(True)
        layout.addWidget(label)
        row = _ViewportRow(card, SimpleNamespace(request=lambda *args: None, invalidate=lambda *args: None))
        row.resize(350, row.heightForWidth(350))
        expected = row.heightForWidth(350)
        row.show()
        for shown in (True, False, True, False):
            row.display(shown)
            APP.processEvents()
            self.assertEqual(row.heightForWidth(350), expected)
            self.assertEqual(row.height(), expected)
        row.close()
