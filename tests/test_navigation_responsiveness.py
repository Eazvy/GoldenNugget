import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel
from src.gui.liquid.cards import ControlGrid
from src.gui.liquid.dock import LiquidDock
from src.gui.ios.daemons import IOSDaemonsPage
from src.gui.liquid.reveal import PageReveal

APP=QApplication.instance() or QApplication([])


class NavigationResponsivenessTests(unittest.TestCase):
    def test_grid_reuses_measurement_and_invalidates_for_content_changes(self):
        parent=QWidget()
        grid=ControlGrid()
        parent.setLayout(grid)
        card=QWidget()
        body=QVBoxLayout(card)
        label=QLabel('A wrapping description')
        label.setWordWrap(True)
        body.addWidget(label)
        grid.addWidget(card)
        with patch.object(grid,'arrange',wraps=grid.arrange) as arrange:
            first=grid.heightForWidth(600)
            self.assertEqual(grid.heightForWidth(600),first)
            self.assertEqual(arrange.call_count,1)
            grid.invalidate()
            grid.heightForWidth(600)
            self.assertEqual(arrange.call_count,2)

    def test_clicking_current_page_does_not_restart_transition(self):
        liquid=SimpleNamespace(settings=Mock(),page_transition=Mock())
        window=SimpleNamespace(liquid=liquid,ios_pages=Mock(),show_ios_page=Mock())
        window.ios_pages.currentIndex.return_value=1
        dock=SimpleNamespace(window=window,popup=Mock(),sync=Mock())
        LiquidDock.navigate(dock,1)
        liquid.page_transition.assert_not_called()
        window.show_ios_page.assert_not_called()
        LiquidDock.navigate(dock,3)
        window.show_ios_page.assert_called_once_with(3)

    def test_daemon_show_does_not_drain_builder(self):
        window=QWidget()
        page=IOSDaemonsPage(window)
        with patch.object(page,'prepare_content') as prepare,patch.object(page,'refresh_from_tweaks'):
            page.showEvent(QShowEvent())
        prepare.assert_called_once_with(finish=False)

    def test_transition_animation_duration_and_curve_are_preserved(self):
        widget=QWidget()
        reveal=PageReveal(widget)
        self.assertEqual(reveal.motion.duration(),560)
        from PySide6.QtCore import QEasingCurve
        self.assertEqual(reveal.motion.easingCurve().type(),QEasingCurve.InOutCubic)
