import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from src.gui.dialogs.update_dialog import UpdateDialog
from src.gui.credits import CREDITS, CREDIT_AVATARS

APP=QApplication.instance() or QApplication([])


class UpstreamRefreshTests(unittest.TestCase):
    def test_download_uses_latest_url_and_closes_on_success(self):
        with patch('src.controllers.web_request_handler.update_download_url',
                   side_effect=['https://example.com/old','https://example.com/new']):
            dialog=UpdateDialog()
            try:
                dialog.show()
                with patch('src.gui.dialogs.update_dialog.QDesktopServices.openUrl',return_value=True) as opener:
                    dialog.accept()
                self.assertEqual(opener.call_args.args[0].toString(),'https://example.com/new')
                self.assertFalse(dialog.isVisible())
            finally:
                dialog.deleteLater()

    def test_failed_download_keeps_dialog_open(self):
        with patch('src.controllers.web_request_handler.update_download_url',return_value='https://example.com/update'):
            dialog=UpdateDialog()
            try:
                dialog.show()
                with patch('src.gui.dialogs.update_dialog.QDesktopServices.openUrl',return_value=False):
                    dialog.accept()
                self.assertTrue(dialog.isVisible())
            finally:
                dialog.hide()
                dialog.deleteLater()

    def test_upstream_attribution_preserves_local_credits(self):
        names={name for _,name,_ in CREDITS}
        for name in ('@omaw','disfordottie','JJTech','f1shy-dev','Eazvy',
                     'Lucide contributors','MiniVoidyy','mattisklein (Project Linwood)'):
            self.assertIn(name,names)
        self.assertIn('https://github.com/qt',CREDIT_AVATARS)


if __name__=='__main__':
    unittest.main()
