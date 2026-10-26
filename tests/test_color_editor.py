import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

import unittest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QDialog
from src.gui.liquid.color_editor import ColorPickerDialog
from src.gui.theme import ColorThemeManager

APP=QApplication.instance() or QApplication([])


class ColorEditorTests(unittest.TestCase):
    def test_reset_returns_no_override_even_with_invalid_hex(self):
        dialog=ColorPickerDialog(QColor('#abcdef'))
        dialog.input.setText('#ab')
        dialog.reset_button.click()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted)
        self.assertIsNone(dialog.get_value())
        dialog.deleteLater()

    def test_picker_preserves_alpha_and_does_not_change_app_accent(self):
        accent=ColorThemeManager.instance().colors.accent
        dialog=ColorPickerDialog(QColor.fromRgbF(.2,.4,.8,.5))
        dialog.select(QColor('#ff0000'))
        dialog.alpha.setValue(25)
        self.assertEqual(dialog.get_value().name(),'#ff0000')
        self.assertAlmostEqual(dialog.get_value().alphaF(),.25,places=3)
        self.assertEqual(ColorThemeManager.instance().colors.accent,accent)
        dialog.deleteLater()

    def test_invalid_hex_cannot_be_saved(self):
        dialog=ColorPickerDialog(QColor('#abcdef'))
        dialog.input.setText('#abc')
        self.assertFalse(dialog._ok.isEnabled())
        dialog.accept()
        self.assertEqual(dialog.result(),0)
        with self.assertRaises(ValueError):
            dialog.get_value()
        dialog.input.setText('#123456')
        self.assertEqual(dialog.get_value().name(),'#123456')
        dialog.deleteLater()
