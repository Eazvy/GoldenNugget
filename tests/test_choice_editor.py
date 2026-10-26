import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import unittest

from PySide6.QtCore import QPoint, QPointF, QEvent, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from src.qt import resources_rc
from src.gui.liquid.choice_editor import GlassComboBox
from src.gui.liquid.sounds import UiSounds

APP = QApplication.instance() or QApplication([])


class ChoiceEditorTests(unittest.TestCase):
    def test_wheel_scrolls_options_without_closing_or_selecting(self):
        for index in range(30):
            self.combo.addItem(f'Language {index}', index)
        editor = self.open()
        viewport = editor.dialog.options.viewport()
        local = viewport.rect().center()
        event = QWheelEvent(QPointF(local), QPointF(viewport.mapToGlobal(local)),
                            QPoint(), QPoint(0, -120), Qt.NoButton, Qt.NoModifier,
                            Qt.NoScrollPhase, False)
        APP.sendEvent(viewport, event)
        self.assertTrue(editor.isVisible())
        self.assertGreater(editor.dialog.options.verticalScrollBar().value(), 0)
        self.assertEqual(self.combo.currentIndex(), 0)

    def test_wheel_propagated_to_parent_keeps_picker_open(self):
        editor = self.open()
        position = editor.mapToGlobal(editor.rect().center())
        event = QWheelEvent(QPointF(self.window.mapFromGlobal(position)), QPointF(position),
                            QPoint(), QPoint(0, -120), Qt.NoButton, Qt.NoModifier,
                            Qt.NoScrollPhase, False)
        self.assertTrue(editor.eventFilter(self.window, event))
        self.assertTrue(editor.isVisible())

    def test_wheel_outside_picker_still_dismisses_it(self):
        editor = self.open()
        position = self.window.mapToGlobal(QPoint(1, 1))
        event = QWheelEvent(QPointF(1, 1), QPointF(position), QPoint(), QPoint(0, -120),
                            Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
        editor.eventFilter(self.window, event)
        self.assertFalse(editor.isVisible())

    def setUp(self):
        APP.setProperty('liquid_reduce_motion', True)
        UiSounds.instance().enabled = False
        self.window = QWidget()
        self.window.resize(620, 560)
        layout = QVBoxLayout(self.window)
        layout.addWidget(QLabel('Language'))
        self.combo = GlassComboBox()
        self.combo.addItem('English', 'en')
        self.combo.addItem('French', 'fr')
        self.combo.addItem('German', 'de')
        layout.addWidget(self.combo)
        layout.addStretch()
        self.window.show()
        APP.processEvents()
        self.addCleanup(self.window.close)
        self.addCleanup(self.window.deleteLater)
        self.addCleanup(APP.setProperty, 'liquid_reduce_motion', False)

    def open(self):
        QTest.mouseClick(self.combo, Qt.LeftButton,
                         pos=QPoint(self.combo.width() - 10, self.combo.height() // 2))
        APP.processEvents()
        editor = self.combo._choice_editor
        self.assertTrue(editor.isVisible())
        return editor

    def test_mouse_open_search_and_select_preserve_combo_callbacks(self):
        changed, activated, text_activated = [], [], []
        self.combo.currentIndexChanged.connect(changed.append)
        self.combo.activated.connect(activated.append)
        self.combo.textActivated.connect(text_activated.append)
        editor = self.open()
        editor.dialog.input.setText('fren')
        editor.dialog.accept()
        self.assertEqual(self.combo.currentData(), 'fr')
        self.assertEqual(changed, [1])
        self.assertEqual(activated, [1])
        self.assertEqual(text_activated, ['French'])

    def test_cancel_does_not_change_selection(self):
        editor = self.open()
        editor.dialog.options.setCurrentRow(2)
        editor.dialog.reject()
        self.assertEqual(self.combo.currentIndex(), 0)

    def test_disabling_control_closes_picker_without_saving(self):
        editor = self.open()
        editor.dialog.options.setCurrentRow(2)
        self.combo.setEnabled(False)
        self.assertFalse(editor.isVisible())
        self.assertEqual(self.combo.currentIndex(), 0)

    def test_disabled_options_and_no_matches_cannot_commit(self):
        self.combo.model().item(1).setEnabled(False)
        editor = self.open()
        editor.dialog.options.setCurrentRow(1)
        editor.dialog.accept()
        self.assertEqual(self.combo.currentIndex(), 0)
        editor.dialog.input.setText('no such choice')
        editor.dialog.accept()
        self.assertEqual(self.combo.currentIndex(), 0)

    def test_model_changes_do_not_select_a_removed_row(self):
        editor = self.open()
        editor.dialog.options.setCurrentRow(1)
        self.combo.removeItem(1)
        editor.dialog.accept()
        self.assertEqual(self.combo.currentData(), 'en')

    def test_keyboard_can_open_and_choose(self):
        self.combo.setFocus()
        QTest.keyClick(self.combo, Qt.Key_Down, Qt.AltModifier)
        APP.processEvents()
        editor = self.combo._choice_editor
        self.assertTrue(editor.isVisible())
        editor.dialog.input.setText('germ')
        QTest.keyClick(editor.dialog.input, Qt.Key_Return)
        self.assertEqual(self.combo.currentData(), 'de')

    def test_render_expanding_picker(self):
        folder = os.environ.get('LIQUID_CHOICE_QA_DIR')
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.open()
            APP.processEvents()
            self.window.grab().save(str(Path(folder) / 'choice-editor.png'))

    def test_expansion_animation_finishes_without_changing_selection(self):
        APP.setProperty('liquid_reduce_motion', False)
        editor = self.open()
        self.assertTrue(editor._liquid_animations)
        QTest.qWait(280)
        self.assertFalse(editor._liquid_animations)
        self.assertTrue(editor.mask().isEmpty())
        self.assertEqual(self.combo.currentIndex(), 0)
