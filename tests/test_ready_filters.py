import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QWidget
from src.gui.ios.incremental_builder import IncrementalBuilder
from src.gui.ios.tweaks import IOSSectionContent, IOSTweaksPage
from src.gui.ios.daemons import IOSDaemonsContent
from src.tweaks.tweaks import TweakID

APP = QApplication.instance() or QApplication([])


class ReadyFilterTests(unittest.TestCase):
    def test_idle_preparation_does_not_drain_builder(self):
        content = SimpleNamespace(_inner=None, _building=False, _builder=Mock())
        content.rebuild = Mock(side_effect=lambda: setattr(content, '_inner', object()))
        IOSTweaksPage.prepare_content(SimpleNamespace(content=content), finish=False)
        content.rebuild.assert_called_once()
        content._builder.finish.assert_not_called()

    def test_device_detection_prepares_tweaks_before_navigation(self):
        from src.gui.main_window_mixins import DeviceBarMixin
        from src.gui.pages.pages_list import Page
        device = SimpleNamespace(udid='test', model='iPhone16,2', version='27.2', build='test')
        page = Mock()
        window = SimpleNamespace(pages={Page.Home: Mock()},
            device_manager=SimpleNamespace(data_singleton=SimpleNamespace(current_device=device)),
            ios_tweaks=page, ios_pages=SimpleNamespace(currentWidget=lambda: None))
        DeviceBarMixin.updateInterfaceForNewDevice(window)
        self.assertFalse(page._device_rebuild_pending)
        page.rebuild.assert_called_once()
        DeviceBarMixin.updateInterfaceForNewDevice(window)
        page.rebuild.assert_called_once()

    def test_unchanged_daemons_do_not_reapply_every_switch_on_open(self):
        content = SimpleNamespace(_building=False,
            daemons_tweak=SimpleNamespace(enabled=True, value={'test': True}),
            _refresh_signature=(True, (('test', True),), False), master_switch=Mock())
        content.master_switch.isChecked.return_value=True
        IOSDaemonsContent.refresh_from_tweaks(content)
        content.master_switch.setChecked.assert_not_called()

    def test_finish_prepares_all_steps_without_waiting_for_event_loop(self):
        owner = QWidget()
        builder = IncrementalBuilder(owner)
        results = []
        def steps():
            for number in range(25):
                results.append(number)
                yield
        builder.start(steps())
        builder.finish()
        builder.finish()
        self.assertEqual(results, list(range(25)))
        self.assertFalse(builder._timer.isActive())
        owner.deleteLater()

    def test_tweaks_prepare_only_builds_once(self):
        content = SimpleNamespace(_inner=None, _building=False, _builder=Mock())
        def rebuild():
            content._inner = object()
        content.rebuild = Mock(side_effect=rebuild)
        page = SimpleNamespace(content=content)
        IOSTweaksPage.prepare_content(page)
        IOSTweaksPage.prepare_content(page)
        content.rebuild.assert_called_once()
        self.assertEqual(content._builder.finish.call_count, 2)

    def test_disabled_filters_exclude_enabled_controls(self):
        cards = [QWidget(), QWidget()]
        search = SimpleNamespace(text=lambda: '', matches=lambda *args: True)
        common = dict(search=search, filter_control=SimpleNamespace(currentData=lambda: 'disabled'),
                      _favorites=SimpleNamespace(names=lambda: set()),
                      search_empty=Mock(), _visibility_batch=Mock())
        ids = list(TweakID)[:2]
        content = SimpleNamespace(**common, _search_rows=[
            (card, tid, '', '', True) for card, tid in zip(cards, ids)],
            _search_sections=[], _inner=object(), _solarium_visible=None)
        with patch('src.gui.ios.tweaks.tweaks', {
                ids[0]: SimpleNamespace(enabled=True), ids[1]: SimpleNamespace(enabled=False)}):
            IOSSectionContent._filter_rows(content)
        self.assertEqual(content._visibility_batch.apply.call_args.args[1][:2],
                         [(cards[0], False), (cards[1], True)])
        content = SimpleNamespace(**common, daemon_cards=cards,
            _screen_time_card=None, _category_groups=[], _rows=object(),
            daemons_tweak=SimpleNamespace(enabled=True, never_enable=set()))
        daemon = SimpleNamespace(value=['com.example.service'])
        content.daemon_switches = [(daemon, SimpleNamespace(isChecked=lambda: True)),
                                  (daemon, SimpleNamespace(isChecked=lambda: False))]
        IOSDaemonsContent._filter_rows(content)
        self.assertEqual(content._visibility_batch.apply.call_args.args[1][:2],
                         [(cards[0], False), (cards[1], True)])
        for card in cards:
            card.deleteLater()
