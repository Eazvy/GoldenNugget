import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtCore import Qt, QEvent, QPoint, QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

APP = QApplication.instance() or QApplication([])


class IntegratedWindowTests(unittest.TestCase):
    def test_pages_start_without_device_io_or_dock_status_overlay(self):
        from src.controllers.translator import Translator
        from src.devicemanagement.device_manager import DeviceManager
        from src.gui.main_window import MainWindow, DeviceMonitorThread
        from src.gui.ios.contributor_media import ContributorMedia
        from src.gui.liquid.dock import ENTRIES
        from src.controllers.hotload import HotLoad
        previous = QStandardPaths.isTestModeEnabled()
        QStandardPaths.setTestModeEnabled(True)
        self.addCleanup(QStandardPaths.setTestModeEnabled, previous)
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            settings = QSettings(folder+'/settings.ini', QSettings.IniFormat)
            for method in ('refresh_devices', '_load_last_preset', '_register_tweak_autosave'):
                stack.enter_context(patch.object(MainWindow, method))
            stack.enter_context(patch.object(DeviceMonitorThread, 'start'))
            stack.enter_context(patch.object(ContributorMedia, 'fetch'))
            stack.enter_context(patch.object(HotLoad, 'update', return_value=False))
            stack.enter_context(patch('src.gui.dialogs.confirmation.ask_confirmation',return_value=True))
            window = MainWindow(DeviceManager(), Translator(APP, settings))
            try:
                self.assertIsNone(window.ios_daemons.content)
                self.assertIsNone(window.ios_tweaks.content._inner)
                window.ios_tweaks.prepare_content()
                window.ios_daemons.prepare_content()
                from src.tweaks.tweaks import tweaks
                from src.tweaks.tweak_classes import TriStateBooleanPlistTweak
                for tid,control in window.ios_tweaks.content._tweak_switches.items():
                    tweak=tweaks[tid]
                    if isinstance(tweak,TriStateBooleanPlistTweak) and control.isEnabled():
                        original=(tweak.enabled,tweak.value)
                        try:
                            control.setChecked(False)
                            control.setChecked(True)
                            self.assertEqual(control._value_editor.value,'Enabled')
                            self.assertTrue(tweak.state)
                        finally:
                            control.blockSignals(True)
                            control.setChecked(original[0])
                            control.blockSignals(False)
                            tweak.enabled,tweak.value=original
                        break
                else:
                    self.fail('No enabled boolean dropdown found for regression test')
                window.resize(1180, 820)
                window.show()
                APP.processEvents()
                with patch.object(window.device_manager,'get_current_device_udid',return_value=''):
                    window.liquid.restore.refresh_device()
                    preview=window.liquid.restore.device_render.image.toImage()
                    self.assertEqual(preview.pixelColor(134,100).name(),'#000000')
                    self.assertEqual(preview.pixelColor(134,510).name(),'#000000')
                self.assertEqual(window.ios_pages.count(), 15)
                review = window.liquid.restore
                self.assertFalse(review.review_area.isAncestorOf(review.confirm_button))
                self.assertTrue(review.review_area.isAncestorOf(review.ack))
                review.resize(560,340)
                review.details.setText('Long review detail\n'*50)
                review.details.show()
                review.show()
                APP.processEvents()
                self.assertTrue(review.confirm_button.isVisible())
                self.assertIs(review.confirm_button, window.ios_home.apply_btn)
                self.assertEqual(window.ios_home.apply_btn.text(), 'Confirm Changes')
                with patch.object(review, 'readiness_valid', return_value=True):
                    review.total=1
                    review.ack.show()
                    review.ack.setChecked(False)
                    review.update_confirm()
                    self.assertFalse(window.ios_home.apply_btn.isEnabled())
                    review.ack.setChecked(True)
                    self.assertTrue(window.ios_home.apply_btn.isEnabled())
                with patch.object(review, 'confirm') as confirm:
                    review.activate()
                    confirm.assert_called_once()
                for widget in (review, window.ios_home.apply_btn):
                    point=widget.mapToGlobal(widget.rect().center())
                    event=QMouseEvent(QEvent.MouseButtonPress,
                        QPointF(window.mapFromGlobal(point)),QPointF(point),
                        Qt.LeftButton,Qt.LeftButton,Qt.NoModifier)
                    window.liquid.eventFilter(window,event)
                    self.assertTrue(review.isVisible())
                point=window.mapToGlobal(QPoint(window.width()-2,2))
                event=QMouseEvent(QEvent.MouseButtonPress,
                    QPointF(window.mapFromGlobal(point)),QPointF(point),
                    Qt.LeftButton,Qt.LeftButton,Qt.NoModifier)
                window.liquid.eventFilter(window,event)
                self.assertFalse(review.isVisible())
                self.assertEqual(window.ios_home.apply_btn.text(), 'Apply Changes')
                device = window.liquid.device
                device.refresh()
                self.assertFalse(device.empty.isHidden())
                self.assertTrue(device.connected.isHidden())
                self.assertEqual(device.check.text(), 'Check connection')
                with patch.object(device, 'frost', side_effect=AssertionError('Opening must not capture the window')):
                    device.open()
                    self.assertTrue(device.isVisible())
                    self.assertTrue(device.mask().isEmpty())
                point = device.mapToGlobal(QPoint(20,20))
                event = QMouseEvent(QEvent.MouseButtonPress,
                    QPointF(window.mapFromGlobal(point)), QPointF(point),
                    Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                window.liquid.eventFilter(window,event)
                self.assertTrue(device.isVisible())
                device.hide()
                reset = window.liquid.restore_changes_panel
                reset._populate()
                row_count=(len(reset.page_switches)+1)//2
                expected_height=48*row_count+4*(row_count-1)+4
                self.assertGreaterEqual(reset.scroll.minimumHeight(),expected_height)
                for index in range(reset.rows.count()):
                    row,column,_,_=reset.rows.getItemPosition(index)
                    self.assertEqual((row,column),(index//2,index%2))
                reset.anchor = window.liquid.restore_button
                reset._populate()
                reset.setGeometry(30,100,700,430)
                reset.show()
                APP.processEvents()
                from src.utils.pages import Page
                self.assertIn(Page.Daemons, reset.page_switches)
                self.assertEqual(next(iter(reset.page_switches)), Page.Daemons)
                from src.gui.ios.feature_icons import FEATURE_ICONS
                self.assertEqual(reset.page_switches[Page.Daemons].icon_path,FEATURE_ICONS['Daemons'])
                self.assertEqual(reset.page_switches[Page.StatusBar].icon_path,FEATURE_ICONS['Status Bar'])
                category_icons=[reset.page_switches[page].icon_path for page in
                                (Page.Springboard,Page.InternalOptions,Page.LiquidGlass)]
                self.assertEqual(len(set(category_icons)),3)
                switch = reset.page_switches[Page.Daemons]
                QTest.mouseClick(switch, Qt.LeftButton)
                self.assertTrue(reset.isVisible())
                self.assertIn(Page.Daemons, reset.selected_pages)
                point = reset.mapToGlobal(QPoint(20,20))
                event = QMouseEvent(QEvent.MouseButtonPress,
                    QPointF(window.mapFromGlobal(point)), QPointF(point),
                    Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                window.liquid.eventFilter(window,event)
                self.assertTrue(reset.isVisible())
                reset.hide()
                if os.environ.get('LIQUID_DEVICE_QA_PATH'):
                    device.reposition()
                    device.show()
                    APP.processEvents()
                    window.grab().save(os.environ['LIQUID_DEVICE_QA_PATH'])
                    device.hide()
                self.assertTrue(window.ios_apply.isAncestorOf(window.ios_apply.progress_card))
                self.assertTrue(window.ios_apply.isAncestorOf(window.ios_apply.result_card))
                for busy in (True, False):
                    with patch.object(window.device_manager, 'get_current_device_partially_supported', return_value=False):
                        window.ios_apply.set_busy(busy)
                    for control in (window.ios_apply.apply_header, window.ios_apply.apply_card,
                                    window.ios_apply.remove_header, window.ios_apply.remove_card):
                        self.assertTrue(control.isHidden())
                with patch.object(window.liquid.restore, 'open') as review:
                    window.ios_home.apply_btn.setEnabled(True)
                    window.ios_home.apply_btn.click()
                    review.assert_called_once()
                window.on_applyPageBtn_clicked()
                self.assertEqual(window.ios_pages.currentIndex(), 6)
                self.assertEqual(ENTRIES['apply'][2], 6)
                content = window.ios_daemons.content
                shown_cards = {card for _, cards in content._category_groups for card in cards}
                for card, (daemon, switch) in zip(content.daemon_cards, content.daemon_switches):
                    if any(key in content.daemons_tweak.never_enable for key in daemon.value):
                        self.assertNotIn(card, shown_cards)
                        self.assertFalse(switch.isEnabled())
                self.assertEqual(len(window.ios_home.cards_grid._cards), 6)
                self.assertEqual(window.ios_home.cards_grid.MAX_COLUMNS, 6)
                if os.environ.get('LIQUID_HOME_QA_PATH'):
                    window.grab().save(os.environ['LIQUID_HOME_QA_PATH'])
                self.assertFalse(hasattr(window.bottom_navigation, 'operation'))
                dock = window.bottom_navigation
                dock._populate_more()
                labels = [dock.popup_column.itemAt(i).widget().text()
                          for i in range(dock.popup_column.count())
                          if dock.popup_column.itemAt(i).widget() is not None
                          and hasattr(dock.popup_column.itemAt(i).widget(), 'text')]
                self.assertEqual(labels[labels.index('GitHub')+1], 'Templates')
                self.assertEqual(window.ios_posterboard.tab_stack.count(), 3)
                window.on_templatesPageBtn_clicked()
                self.assertEqual(window.ios_pages.currentIndex(), 14)
                self.assertTrue(window.ui.templatesPageBtn.isChecked())
                window.ios_pages.setCurrentIndex(2)
                window.ios_posterboard.tab_stack.setCurrentIndex(2)
                APP.processEvents()
                self.assertFalse(window.grab().isNull())
                if os.environ.get('LIQUID_CONNECT_QA_PATH'):
                    window.content_stack.setCurrentWidget(window.connect_placeholder)
                    window.connect_placeholder.set_scan_status('Waiting for a trusted USB connection.')
                    APP.processEvents()
                    window.grab().save(os.environ['LIQUID_CONNECT_QA_PATH'])
            finally:
                window.hide()
                APP.removeEventFilter(window)
                window.deleteLater()
                APP.processEvents()
