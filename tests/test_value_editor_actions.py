import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QVBoxLayout, QWidget
from src.qt import resources_rc
from src.gui.ios.components import TextInputDialog
from src.gui.liquid.value_editor import ValueEditor
from src.gui.liquid.value_entry import GlassValueEntry

APP = QApplication.instance() or QApplication([])


class ValueEditorActionsTests(unittest.TestCase):
    def setUp(self):
        APP.setProperty('liquid_reduce_motion', True)
        self.window = QWidget()
        self.window.resize(500, 320)
        self.card = QWidget(self.window)
        self.card.setGeometry(20, 20, 340, 180)
        self.entry = GlassValueEntry('Carrier')
        QVBoxLayout(self.card).addWidget(self.entry)
        self.window.show()
        self.saved = []
        self.dialog = TextInputDialog('Carrier', 'Example', self.window, pattern='[A-Z]+')
        self.editor = ValueEditor(self.window, self.entry, self.dialog, 'Carrier',
                                  lambda: self.saved.append(self.dialog.get_value()))
        APP.processEvents()
        self.box = self.dialog.findChild(QDialogButtonBox)
        self.addCleanup(self.window.close)
        self.addCleanup(self.window.deleteLater)
        self.addCleanup(APP.setProperty, 'liquid_reduce_motion', False)

    def test_balanced_actions_keep_validation_and_accept_behavior(self):
        ok = self.box.button(QDialogButtonBox.Ok)
        cancel = self.box.button(QDialogButtonBox.Cancel)
        self.assertTrue(self.box.centerButtons())
        self.assertEqual(ok.objectName(), 'valueEditorOk')
        self.assertEqual(cancel.objectName(), 'valueEditorCancel')
        self.assertFalse(ok.isEnabled())
        self.dialog.input.setText('VALID')
        self.assertTrue(ok.isEnabled())
        self.assertLess(cancel.geometry().center().x(), ok.geometry().center().x())
        QTest.mouseClick(ok, Qt.LeftButton)
        self.assertEqual(self.saved, ['VALID'])

    def test_cancel_discards_edits_and_renders(self):
        self.dialog.input.setText('CHANGED')
        folder = os.environ.get('LIQUID_ACTION_QA_DIR')
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.window.grab().save(str(Path(folder) / 'editor-actions.png'))
        QTest.mouseClick(self.box.button(QDialogButtonBox.Cancel), Qt.LeftButton)
        self.assertEqual(self.saved, [])
