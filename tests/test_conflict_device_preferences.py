import unittest
from unittest.mock import patch

from src.controllers.tweak_conflicts import find_conflicts
from src.tweaks.candidate_preferences import InstalledAppSuggestionsBlacklist
from src.tweaks.tweak_names import TweakID


class DevicePreferenceConflictTests(unittest.TestCase):
    def test_preview_with_live_bound_listener_does_not_copy_subscriptions(self):
        from src.tweaks.store import ChangeBus
        from src.tweaks.tweak_classes import BasicPlistTweak
        from src.tweaks.basic_plist_locations import FileLocation
        class Listener:
            calls = 0
            def changed(self):
                self.calls += 1
        listener = Listener()
        bus = ChangeBus()
        unsubscribe = bus.subscribe(listener.changed)
        tweak = BasicPlistTweak(FileLocation.springboard, 'example', value=True)
        tweak._change_bus = bus
        tweak.enabled = True
        before = listener.calls
        self.assertEqual(find_conflicts({TweakID.RTL: tweak}), [])
        self.assertIs(tweak._change_bus, bus)
        self.assertEqual(listener.calls, before)
        bus.notify()
        self.assertEqual(listener.calls, before+1)
        unsubscribe()

    def test_review_does_not_build_unprepared_device_preference(self):
        tweak = InstalledAppSuggestionsBlacklist()
        tweak.enabled = True
        with patch.object(tweak, 'apply_tweak', side_effect=AssertionError('device writer called')):
            self.assertEqual(find_conflicts({TweakID.RTL: tweak}), [])
        self.assertIsNone(tweak._bundle_ids)

    def test_review_does_not_consume_prepared_app_list(self):
        tweak = InstalledAppSuggestionsBlacklist()
        tweak.enabled = True
        tweak._bundle_ids = ['com.example.app']
        self.assertEqual(find_conflicts({TweakID.RTL: tweak}), [])
        self.assertEqual(tweak._bundle_ids, ['com.example.app'])

    def test_apply_still_requires_preparation(self):
        tweak = InstalledAppSuggestionsBlacklist()
        tweak.enabled = True
        with self.assertRaisesRegex(ValueError, 'installed apps'):
            tweak.apply_tweak({})
