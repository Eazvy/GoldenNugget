"""Update download dialog opened from the version notice."""
from PySide6.QtCore import QUrl, QCoreApplication
from PySide6.QtGui import QDesktopServices
from src.gui.dialogs.confirmation import ConfirmationDialog


class UpdateDialog(ConfirmationDialog):
    def __init__(self, parent=None):
        tr = lambda text: QCoreApplication.translate("UpdateDialog", text)
        from src.version import App_Version
        from src.controllers.web_request_handler import last_fetched_version, update_download_url
        self._download_url = update_download_url()
        message = tr('You have GoldenNugget {0}.').format(App_Version)
        if last_fetched_version:
            message += '\n' + tr('Version {0} is available.').format(last_fetched_version)
        instructions = (tr('Download and extract the source archive, then follow its installation instructions.')
                        if '/archive/' in self._download_url else
                        tr('Download the update, then open the downloaded package to install it.'))
        message += '\n\n' + instructions
        super().__init__(parent, tr('Update GoldenNugget'), message, tr('Download update'),
                         icon=':/icon/arrow-clockwise.svg')
        self.cancel_btn.setText(tr('Later'))
        self.resize(560, self.height())

    def accept(self):
        if QDesktopServices.openUrl(QUrl(self._download_url)):
            super().accept()
