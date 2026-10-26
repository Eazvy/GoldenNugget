"""Offline daemon favorite feedback tests; no device or app selections touched."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QCoreApplication, QStandardPaths
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QLabel, QWidget

from src.gui.liquid.controls import FavoriteButton
from src.gui.liquid.favorite_feedback import FavoriteFeedbackLabel
from src.gui.liquid.selection_card import bind_selection_card


class FavoriteFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        QStandardPaths.setTestModeEnabled(True)
        QCoreApplication.setOrganizationName('GoldenNuggetFeedbackTests')
        QCoreApplication.setApplicationName('GoldenNuggetFeedbackTests')
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.app.setProperty('liquid_reduce_motion', False)
        self.card = QWidget()
        self.card.setStyleSheet('background:#202124;color:#eeeeee;')
        self.card.resize(480, 100)
        layout = QHBoxLayout(self.card)
        layout.addWidget(QLabel('Daemon preview'))
        self.switch = QCheckBox(self.card)
        layout.addWidget(self.switch)
        self.favorite = FavoriteButton(self.card)
        self.favorite.setCheckable(True)
        self.favorite.setFixedSize(44, 44)
        layout.addWidget(self.favorite)
        bind_selection_card(self.card, self.switch, favorite_feedback=True)
        self.surface = self.card._selection_surface
        self.label = self.surface.action_label
        self.card.show()
        self.app.processEvents()

    def tearDown(self):
        self.card.close()
        self.card.deleteLater()
        self.app.processEvents()
        self.app.setProperty('liquid_reduce_motion', False)

    def test_favorite_temporarily_replaces_text_and_returns_latest_state(self):
        self.assertIsInstance(self.label, FavoriteFeedbackLabel)
        original_width = self.label.width()
        self.assertEqual(self.label.text(), 'Disabled')
        self.favorite.setChecked(True)
        self.assertEqual(self.label.text(), 'Favorited')
        self.switch.setChecked(True)
        self.assertEqual(self.label.text(), 'Favorited')
        QTest.qWait(self.label.SWEEP_MS + self.label.HOLD_MS + 100)
        self.assertEqual(self.label.text(), 'Enabled')
        self.assertEqual(self.label.width(), original_width)

    def test_unfavorite_reverses_into_original_color_without_changing_switch(self):
        self.favorite.setChecked(True)
        self.favorite.setChecked(False)
        self.assertFalse(self.label._favorited)
        self.assertTrue(self.label._feedback_active)
        self.assertEqual(self.label.text(), 'Disabled')
        self.assertFalse(self.switch.isChecked())
        QTest.qWait(self.label.SWEEP_MS + 100)
        self.assertFalse(self.label._feedback_active)
        self.assertEqual(self.label.text(), 'Disabled')

    def test_rapid_clicks_cancel_old_completion_timers(self):
        self.favorite.setChecked(True)
        QTest.qWait(40)
        self.favorite.setChecked(False)
        QTest.qWait(40)
        self.favorite.setChecked(True)
        self.assertEqual(self.label.text(), 'Favorited')
        QTest.qWait(self.label.SWEEP_MS + self.label.HOLD_MS + 100)
        self.assertEqual(self.label.text(), 'Disabled')
        self.assertFalse(self.label._hold.isActive())

    def test_hide_cancels_animation_and_hold(self):
        self.favorite.setChecked(True)
        self.card.hide()
        self.app.processEvents()
        self.assertFalse(self.label._feedback_active)
        self.assertFalse(self.label._hold.isActive())
        self.assertEqual(self.label.text(), 'Disabled')

    def test_reduced_motion_uses_brief_static_feedback(self):
        self.app.setProperty('liquid_reduce_motion', True)
        self.favorite.setChecked(True)
        self.assertEqual(self.label.text(), 'Favorited')
        self.assertEqual(self.label._progress, 1.0)
        QTest.qWait(self.label.HOLD_MS + 80)
        self.assertEqual(self.label.text(), 'Disabled')
        self.favorite.setChecked(False)
        self.assertFalse(self.label._feedback_active)

    def test_tweak_cards_keep_existing_plain_labels(self):
        card = QWidget()
        layout = QHBoxLayout(card)
        switch = QCheckBox(card)
        layout.addWidget(switch)
        bind_selection_card(card, switch)
        self.assertNotIsInstance(card._selection_surface.action_label, FavoriteFeedbackLabel)
        card.deleteLater()

    def test_actual_daemon_cards_use_feedback_without_changing_service_selection(self):
        from src.gui.ios.daemons import IOSDaemonsContent
        page = IOSDaemonsContent(None)
        try:
            for _ in range(400):
                if not page._building:
                    break
                QTest.qWait(5)
            self.assertFalse(page._building)
            daemon, switch = page.daemon_switches[0]
            label = switch._selection_surface.action_label
            self.assertIsInstance(label, FavoriteFeedbackLabel)
            before = dict(page.daemons_tweak.value)
            button = page._favorite_buttons['daemon:' + daemon.name]
            button.setChecked(False)
            button.setChecked(True)
            self.assertEqual(label.text(), 'Favorited')
            self.assertEqual(page.daemons_tweak.value, before)
            button.setChecked(False)
            self.assertFalse(label._favorited)
            self.assertEqual(page.daemons_tweak.value, before)
        finally:
            page.close()
            page.deleteLater()

    def test_render_gloss_frames(self):
        output = Path(__file__).resolve().parents[1] / 'test-results/favorite-feedback'
        output.mkdir(parents=True, exist_ok=True)
        self.card.grab().save(str(output / 'normal.png'))
        self.favorite.setChecked(True)
        self.label._motion.setCurrentTime(self.label.SWEEP_MS // 2)
        self.app.processEvents()
        self.assertTrue(self.card.grab().save(str(output / 'favorited.png')))
        self.favorite.setChecked(False)
        self.label._motion.setCurrentTime(self.label.SWEEP_MS // 2)
        self.app.processEvents()
        self.assertTrue(self.card.grab().save(str(output / 'unfavorite.png')))


if __name__ == '__main__':
    unittest.main()
