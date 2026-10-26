import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import gc
import unittest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from src.gui.ios.components import NumberInputDialog, TextInputDialog

APP = QApplication.instance() or QApplication([])


class NumberEntryTests(unittest.TestCase):
    def test_unverified_glass_arrays_cannot_open_free_form_editor(self):
        from types import SimpleNamespace
        from src.gui.ios.tweaks import IOSSectionContent
        from src.tweaks.registry import SPECS_BY_ID
        from src.tweaks.tweaks import TweakID
        for tid in (TweakID.AdaptiveGlassHysteresisDarkRange,
                    TweakID.AdaptiveGlassHysteresisLightRange):
            self.assertTrue(SPECS_BY_ID[tid].unavailable_reason)
            content = SimpleNamespace()
            IOSSectionContent._show_text_input_dialog(content, tid, 'Thresholds', '', None)
            self.assertFalse(hasattr(content, '_value_editor_panel'))

    def test_integer_rejects_letters_decimal_and_paste(self):
        dialog = NumberInputDialog('Count', 12, 0, 100)
        gc.collect()
        dialog.input.selectAll()
        QTest.keyClicks(dialog.input, 'abc')
        self.assertEqual(dialog.input.text(), '12')
        APP.clipboard().setText('junk')
        dialog.input.paste()
        self.assertEqual(dialog.input.text(), '12')
        QTest.keyClicks(dialog.input, '42')
        self.assertEqual(dialog.get_value(), 42)
        QTest.keyClicks(dialog.input, '.')
        self.assertEqual(dialog.input.text(), '42')
        dialog.deleteLater()

    def test_decimal_accepts_fraction_but_not_exponents_or_letters(self):
        dialog = NumberInputDialog('Opacity', 0.5, 0, 1, step=0.01)
        dialog.input.selectAll()
        QTest.keyClicks(dialog.input, '0.25')
        self.assertEqual(dialog.get_value(), 0.25)
        QTest.keyClicks(dialog.input, 'exyz')
        self.assertEqual(dialog.input.text(), '0.25')
        dialog.input.setText('5')
        self.assertFalse(dialog._ok_button.isEnabled())
        with self.assertRaises(ValueError):
            dialog.get_value()
        dialog.deleteLater()

    def test_signed_and_empty_values_and_text_fields(self):
        dialog = NumberInputDialog('Offset', 0, -100, 100)
        dialog.input.selectAll()
        QTest.keyClicks(dialog.input, '-25')
        self.assertEqual(dialog.get_value(), -25)
        dialog.input.clear()
        self.assertFalse(dialog._ok_button.isEnabled())
        text = TextInputDialog('Carrier', '')
        QTest.keyClicks(text.input, 'Carrier 123')
        self.assertEqual(text.get_value(), 'Carrier 123')
        dialog.deleteLater()
        text.deleteLater()
