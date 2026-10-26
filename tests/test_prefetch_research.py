import plistlib
import unittest

from src.tweaks.registry import SPECS_BY_ID
from src.tweaks.tweak_names import TweakID
from src.tweaks.tweak_classes import BasicPlistTweak, ResearchOnlyTweak


class PrefetchResearchTests(unittest.TestCase):
    def test_swiftui_scroll_prefetch_control_targets_native_preferences(self):
        spec = SPECS_BY_ID[TweakID.DisableSwiftUIScrollPrefetch]
        self.assertEqual(spec.location.value,
                         '/var/mobile/Library/Preferences/com.apple.SwiftUI.plist')
        self.assertEqual(spec.key, 'EnableScrollPrefetch')
        self.assertIs(spec.value, False)
        self.assertEqual(spec.min_version, '27.2')
        self.assertTrue(spec.experimental)

        tweak = spec.factory()
        payloads = tweak.apply_tweak({})
        self.assertEqual(payloads, {})
        tweak.set_enabled(True)
        payloads = tweak.apply_tweak({})
        self.assertIs(payloads[spec.location][spec.key], False)
        tweak.set_enabled(False)
        payloads = tweak.apply_tweak({})
        self.assertIs(payloads[spec.location][spec.key], True)

    def test_collection_override_is_integer_at_native_path(self):
        spec = SPECS_BY_ID[TweakID.DisableCollectionViewPrefetching]
        self.assertEqual(spec.location.value,
                         '/var/mobile/Library/Preferences/com.apple.UIKit.plist')
        tweak = BasicPlistTweak(spec.location, spec.key, value=spec.value)
        self.assertEqual(tweak.apply_tweak({}), {})
        tweak.enabled = True
        value = plistlib.loads(plistlib.dumps(tweak.apply_tweak({})[spec.location]))
        self.assertIs(type(value[spec.key]), int)
        self.assertEqual(value[spec.key], -2)

    def test_unverified_leads_have_no_writer_or_invented_values(self):
        for name in ('SpotlightMetricsWritingResearch',
                     'ICloudBackgroundTaskSchedulingResearch', 'DASFairSchedulingQueueResearch',
                     'AccountDarkWakeEnabled'):
            with self.subTest(name=name):
                spec = SPECS_BY_ID[TweakID[name]]
                self.assertIsNone(spec.location)
                self.assertIsNone(spec.value)
                self.assertTrue(spec.show_when_unavailable)
                tweak = spec.factory()
                self.assertIsInstance(tweak, ResearchOnlyTweak)
                with self.assertRaises(ValueError):
                    tweak.set_enabled(True)

    def test_runtime_loader_merges_both_integer_overrides(self):
        from src.tweaks.tweak_loader import load_plist_tweaks
        from src.tweaks.tweaks import tweaks
        from copy import copy
        load_plist_tweaks()
        payloads = {}
        for tid in (TweakID.DisableCollectionViewPrefetching, TweakID.TableViewCellPrefetchingModeResearch):
            spec = SPECS_BY_ID[tid]
            self.assertIsNone(spec.unavailable_reason)
            tweak = copy(tweaks[tid])
            tweak.enabled = True
            payloads = tweak.apply_tweak(payloads)
        self.assertEqual(len(payloads), 1)
        payload = plistlib.loads(plistlib.dumps(next(iter(payloads.values()))))
        self.assertEqual(payload, {'CollectionViewCellPrefetchingMode': -2,
                                  'TableViewCellPrefetchingMode': -1})
        self.assertTrue(all(type(value) is int for value in payload.values()))
