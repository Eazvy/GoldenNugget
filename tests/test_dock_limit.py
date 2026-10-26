import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from PySide6.QtCore import QPoint, QRect
from src.gui.liquid.dock import LiquidDock, ENTRIES, MAX_DOCK_ITEMS
from src.qt import resources_rc
from src.gui.ios.feature_icons import FEATURE_ICONS
from src.gui.theme import theme_icon, ColorThemeManager
from PySide6.QtWidgets import QApplication

APP=QApplication.instance() or QApplication([])


class DockLimitTests(unittest.TestCase):
    def test_dock_uses_same_artwork_as_home_cards(self):
        colors=ColorThemeManager.instance().colors
        for key,(name,_,_) in ENTRIES.items():
            icon=LiquidDock.entry_icon(None,key)
            self.assertFalse(icon.isNull())
            if name in FEATURE_ICONS:
                expected=theme_icon(FEATURE_ICONS[name],colors.text_primary)
                self.assertEqual(icon.cacheKey(),expected.cacheKey())
                self.assertFalse(icon.pixmap(52,52).isNull())
        self.assertEqual(LiquidDock.entry_icon(None,'presets').cacheKey(),
                         theme_icon(':/icon/folder.svg',colors.text_primary).cacheKey())
    def dock(self, count):
        return SimpleNamespace(order=list(ENTRIES)[:count], save_order=Mock(),
            popup=Mock(), position=Mock(), _preview_order=None, edge='bottom')

    def test_pin_cannot_exceed_five(self):
        dock = self.dock(MAX_DOCK_ITEMS)
        source = list(ENTRIES)[MAX_DOCK_ITEMS]
        LiquidDock._move_item(dock, source, True)
        self.assertEqual(len(dock.order), MAX_DOCK_ITEMS)
        dock.save_order.assert_not_called()

    def test_fifth_item_can_be_pinned(self):
        dock = self.dock(4)
        LiquidDock._move_item(dock, list(ENTRIES)[4], True)
        self.assertEqual(len(dock.order), 5)
        dock.save_order.assert_called_once()

    def test_drag_rejects_sixth_item_but_allows_reordering(self):
        dock = self.dock(5)
        dock._drag_source = list(ENTRIES)[5]
        dock._drag_slots = {key: QRect(index*40, 0, 40, 40)
                            for index, key in enumerate(dock.order)}
        LiquidDock._drag_at(dock, QPoint(45, 10))
        self.assertIsNone(dock._preview_order)
        dock._drag_source = dock.order[0]
        LiquidDock._drag_at(dock, QPoint(45, 10))
        self.assertEqual(dock._preview_order[1], dock.order[0])
        self.assertEqual(len(dock._preview_order), 5)
