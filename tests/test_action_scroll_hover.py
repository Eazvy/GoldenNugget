import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import unittest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QCursor, QMouseEvent, QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QWidget
from src.gui.liquid.controls import LiquidActionButton, LiquidDangerButton

APP = QApplication.instance() or QApplication([])


class ActionScrollHoverTests(unittest.TestCase):
    button_type = LiquidActionButton
    def setUp(self):
        APP.setProperty('liquid_reduce_motion', False)
        self.scroll = QScrollArea()
        self.scroll.resize(360, 260)
        self.scroll.setWidgetResizable(True)
        body = QWidget()
        body.setMinimumHeight(1100)
        layout = QVBoxLayout(body)
        self.button = self.button_type('Restore Changes' if self.button_type is LiquidDangerButton else 'Apply Changes')
        self.button.setProperty('homeAction', True)
        self.button.setFixedHeight(48)
        layout.addWidget(self.button)
        layout.addStretch()
        self.scroll.setWidget(body)
        self.scroll.show()
        APP.processEvents()
        QTest.qWait(80)
        self.button._scroll_hover_suspended = False
        self.button._hover_to(1)
        self.button._hover_animation.stop()
        self.button._set_hover(1)
        self.addCleanup(self.scroll.close)
        self.addCleanup(self.scroll.deleteLater)

    def test_scrolling_cancels_the_window_level_stretch(self):
        self.assertIsNotNone(self.button._stretch_surface)
        self.assertTrue(self.button._stretch_surface.isVisible())
        size = self.button.size()
        self.scroll.verticalScrollBar().setValue(60)
        APP.processEvents()
        self.assertEqual(self.button.hover, 0)
        self.assertTrue(self.button._stretch_surface.isHidden())
        self.assertTrue(self.button._scroll_hover_suspended)
        self.assertEqual(self.button.size(), size)

    def test_stationary_pointer_cannot_restart_stretch_after_scroll(self):
        self.button._cancel_scroll_hover()
        self.button._hover_to(1)
        global_point = QPointF(QCursor.pos())
        event = QMouseEvent(QEvent.MouseMove, QPointF(20, 20), global_point,
                            Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        APP.sendEvent(self.button, event)
        self.assertTrue(self.button._scroll_hover_suspended)
        self.assertEqual(self.button.hover, 0)

    def test_new_pointer_movement_restores_hover(self):
        self.button._cancel_scroll_hover()
        event = QMouseEvent(QEvent.MouseMove, QPointF(30, 20),
                            QPointF(self.button._scroll_pointer + QPoint(8, 8)),
                            Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        APP.sendEvent(self.button, event)
        self.assertFalse(self.button._scroll_hover_suspended)
        QTest.qWait(350)
        self.assertGreater(self.button.hover, .9)

    def test_wheel_cancels_stretch_even_at_scroll_limit(self):
        event = QWheelEvent(QPointF(20, 20), QPointF(QCursor.pos()),
                            QPoint(), QPoint(0, 120), Qt.NoButton,
                            Qt.NoModifier, Qt.NoScrollPhase, False)
        APP.sendEvent(self.button, event)
        self.assertTrue(self.button._scroll_hover_suspended)
        self.assertTrue(self.button._stretch_surface.isHidden())


class RestoreScrollHoverTests(ActionScrollHoverTests):
    button_type = LiquidDangerButton

    def test_explicit_home_scroll_binding_is_idempotent(self):
        self.button.bind_scroll_area(self.scroll)
        self.button.bind_scroll_area(self.scroll)
        self.assertEqual(len(self.button._scroll_bars), 2)
        self.scroll.verticalScrollBar().setValue(60)
        self.assertTrue(self.button._scroll_hover_suspended)
        self.assertTrue(self.button._stretch_surface.isHidden())
