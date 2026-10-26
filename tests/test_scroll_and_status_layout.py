import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QEnterEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget
from src.qt import resources_rc
from src.gui.ios.viewport_rows import ViewportRows
from src.gui.ios.statusbar import IOSStatusBarPage, StatusValueEntry
from src.gui.liquid.controls import LiquidCard
from src.gui.liquid.sounds import UiSounds

APP = QApplication.instance() or QApplication([])


class ScrollIndexTests(unittest.TestCase):
    def setUp(self):
        self.scroll = QScrollArea()
        self.scroll.resize(650, 450)
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        layout = QVBoxLayout(self.content)
        self.controller = ViewportRows(self.content)
        for index in range(180):
            card = LiquidCard()
            QVBoxLayout(card).addWidget(QLabel(f'Control {index}'))
            layout.addWidget(self.controller.wrap(card))
        self.scroll.setWidget(self.content)
        self.scroll.show()
        QTest.qWait(180)
        self.controller._refresh()
        self.addCleanup(self.scroll.close)
        self.addCleanup(self.scroll.deleteLater)

    def test_scroll_does_not_rebuild_the_entire_index_each_update(self):
        self.controller._dirty = False
        with patch.object(self.controller, '_build_index', wraps=self.controller._build_index) as build:
            for value in range(1, 15):
                self.scroll.verticalScrollBar().setValue(value)
                self.controller._refresh()
            self.assertEqual(build.call_count, 0)
        self.assertLess(len(self.controller._active), 20)

    def test_large_jump_and_filter_refresh_nearby_rows(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum() // 2)
        self.controller._refresh()
        self.assertLess(len(self.controller._active), 25)
        self.assertGreater(len(self.controller._active), 0)
        hidden = next(iter(self.controller._active))
        hidden.hide()
        APP.processEvents()
        self.controller._refresh()
        self.assertNotIn(hidden, self.controller._bounds)

    def test_scroll_does_not_start_hover_animations(self):
        row = next(iter(self.controller._active))
        self.controller._scrolled()
        point = QPointF(10, 10)
        APP.sendEvent(row._card, QEnterEvent(point, point, point))
        self.assertEqual(row._card.hover, 0)
        self.assertTrue(row._card._scroll_hover_deferred)


class StatusLayoutTests(unittest.TestCase):
    def setUp(self):
        UiSounds.instance().enabled = False
        self.window = QWidget()
        self.window.resize(940, 740)
        self.window.device_manager = SimpleNamespace(
            get_current_device_version=lambda: '27.2',
            get_current_device_model=lambda: 'iPhone16,2')
        self.page = IOSStatusBarPage(self.window)
        QVBoxLayout(self.window).addWidget(self.page)
        self.window.show()
        APP.processEvents()
        self.addCleanup(self.window.close)
        self.addCleanup(self.window.deleteLater)

    def test_cards_use_selection_surfaces_and_shared_value_fields(self):
        cards = [card for card, _ in self.page._rows if isinstance(card, LiquidCard)]
        self.assertGreater(len(cards), 10)
        master = self.page.enabled_switch.parentWidget()
        self.assertTrue(all(hasattr(card, '_selection_surface') for card in cards if card is not master))
        self.assertFalse(hasattr(master, '_selection_surface'))
        self.assertGreater(len(self.page.findChildren(StatusValueEntry)), 5)

    def test_cellular_controls_are_grouped_by_sim(self):
        primary = self.page.carrier_row.parentWidget().parentWidget()
        secondary = self.page.secondary_carrier_row.parentWidget().parentWidget()
        self.assertIsNot(primary, secondary)
        for switch in (self.page.badge_row, self.page.gsm_row, self.page.network_type_row):
            self.assertIs(switch.parentWidget().parentWidget(), primary)
        self.assertEqual(primary.layout().count(), 4)
        self.assertEqual(secondary.layout().count(), 4)

    def test_ios27_hides_unsupported_rows_but_keeps_signal_group(self):
        self.assertTrue(self.page.wifi_row.parentWidget().isHidden())
        self.assertFalse(self.page.gsm_row.parentWidget().isHidden())
        self.assertTrue(self.page.gsm_row.parentWidget().parentWidget().isVisible())

    def test_text_editor_saves_value_and_enables_only_its_override(self):
        switch = self.page.carrier_row
        card = switch.parentWidget()
        card.setEnabled(True)
        switch.setChecked(True)
        entry = card.findChild(StatusValueEntry)
        title = next(label for label in card.findChildren(QLabel)
                     if 'font-size: 15px' in label.styleSheet())
        saved = []
        self.page._on_text_row_edit('Carrier', '', saved.append, title, entry)
        editor = self.page._value_editor_panel
        editor.dialog.input.setText('Example Carrier')
        editor.dialog.accept()
        APP.processEvents()
        self.assertEqual(saved, ['Example Carrier'])
        self.assertEqual(entry.value, 'Example Carrier')
        self.assertTrue(switch.isChecked())

    def test_render_status_page_at_two_widths(self):
        folder = os.environ.get('LIQUID_LAYOUT_QA_DIR')
        if not folder:
            return
        Path(folder).mkdir(parents=True, exist_ok=True)
        for width in (940, 620):
            self.window.resize(width, 740)
            APP.processEvents()
            self.window.grab().save(str(Path(folder) / f'status-{width}.png'))

    def test_network_type_uses_expanding_searchable_picker(self):
        switch = self.page.network_type_row
        card = switch.parentWidget()
        card.setEnabled(True)
        switch.setChecked(True)
        entry = card.findChild(StatusValueEntry)
        saved = []
        self.page._on_network_type_edit('Network label', saved.append, entry)
        editor = self.page._value_editor_panel
        self.assertTrue(editor.isVisible())
        editor.dialog.input.setText('LTE')
        editor.dialog.accept()
        self.assertEqual(saved, [8])
        self.assertEqual(entry.value, 'LTE')
        self.assertTrue(switch.isChecked())

    def test_value_picker_requires_toggle_and_closes_when_disabled(self):
        switch = self.page.network_type_row
        card = switch.parentWidget()
        card.setEnabled(True)
        switch.setChecked(False)
        entry = card.findChild(StatusValueEntry)
        self.assertFalse(entry.isEnabled())
        self.page._on_network_type_edit('Network label', lambda value: None, entry)
        self.assertIsNone(getattr(self.page, '_value_editor_panel', None))
        switch.setChecked(True)
        self.assertTrue(entry.isEnabled())
        self.page._on_network_type_edit('Network label', lambda value: None, entry)
        editor = self.page._value_editor_panel
        self.assertTrue(editor.isVisible())
        switch.setChecked(False)
        self.assertFalse(entry.isEnabled())
        self.assertFalse(editor.isVisible())
