import plistlib
import unittest

from src.restore.inject import _merge_preference_payload
from src.restore.preference_scope import is_preference_file
from src.tweaks.basic_plist_locations import FileLocation
from src.tweaks.registry import SPECS_BY_ID
from src.tweaks.tweak_names import TweakID


class FeatureFlagCandidateTests(unittest.TestCase):
    def test_avconference_thermal_flag_is_an_experimental_tri_state_feature_flag(self):
        self._assert_flag(
            TweakID.AVConferenceThermalLightMitigationsResearch,
            'AVConference',
            'EnableThermalLightMitigations',
        )

    def test_ipcs_memory_transaction_is_an_experimental_tri_state_feature_flag(self):
        self._assert_flag(
            TweakID.IPCSMemoryTransactionResearch,
            'IntelligencePlatform',
            'IPCSMemoryTransaction',
        )

    def test_ipcs_memory_reduction_is_an_experimental_tri_state_feature_flag(self):
        self._assert_flag(
            TweakID.IPCSMemoryReductionResearch,
            'IntelligencePlatform',
            'IPCSMemoryReduction',
        )

    def test_swiftui_stack_layout_optimizations_is_experimental_tri_state(self):
        self._assert_flag(
            TweakID.SwiftUIStackLayoutOptimizationsResearch,
            'SwiftUI',
            'StackLayoutOptimizations',
            min_version='27.0',
        )

    def test_swiftui_standard_defaults_use_global_defaults_restore_path(self):
        self.assertEqual(
            FileLocation.globalPreferencesHomeDomain.value,
            '/var/mobile/Library/Preferences/.GlobalPreferences.plist',
        )
        self.assertTrue(is_preference_file(
            'HomeDomain', 'Library/Preferences/.GlobalPreferences.plist'))
        candidates = (
            (TweakID.SwiftUIPersistentLazyStackCache,
             'com.apple.SwiftUI.PersistentLazyStackCache'),
            (TweakID.SwiftUIHitTestingCache, 'com.apple.SwiftUI.HitTestingCache'),
            (TweakID.SwiftUIDisableAsyncRendering,
             'com.apple.SwiftUI.DisableAsyncRendering'),
            (TweakID.SwiftUIGestureContainers, 'com.apple.SwiftUI.GestureContainers'),
            (TweakID.SwiftUIUniversalGestureRelationships,
             'com.apple.SwiftUI.UniversalGestureRelationships'),
            (TweakID.SwiftUIDisableRemoteEffects,
             'com.apple.SwiftUI.DisableRemoteEffects'),
        )
        patch = {}
        for tweak_id, key in candidates:
            with self.subTest(key=key):
                spec = SPECS_BY_ID[tweak_id]
                self.assertIs(spec.location, FileLocation.globalPreferencesHomeDomain)
                self.assertEqual(spec.key, key)
                self.assertEqual(spec.min_version, '27.2')
                self.assertTrue(spec.experimental)
                self.assertIn('app-specific values can override', spec.warning)

                tweak = spec.factory()
                self.assertEqual(tweak.apply_tweak({}), {})
                for state in (False, True):
                    tweak.set_state(state)
                    patch = tweak.apply_tweak(patch)
                    self.assertIs(
                        patch[FileLocation.globalPreferencesHomeDomain][key],
                        state,
                    )

        self.assertIn(FileLocation.globalPreferencesHomeDomain, patch)
        stored = plistlib.dumps({'ExistingGlobalSetting': True})
        merged = _merge_preference_payload(
            stored,
            plistlib.dumps(patch[FileLocation.globalPreferencesHomeDomain]),
        )
        result = plistlib.loads(merged)
        self.assertIs(result['ExistingGlobalSetting'], True)
        for _, key in candidates:
            self.assertIs(result[key], True)

    def test_swiftui_scroll_edge_effect_uses_suite_preference_file(self):
        location = FileLocation.swiftuiPreferencesHomeDomain
        key = 'NewScrollEdgeEffectTag'
        self.assertEqual(
            location.value,
            '/var/mobile/Library/Preferences/com.apple.SwiftUI.plist',
        )
        self.assertTrue(is_preference_file(
            'HomeDomain', 'Library/Preferences/com.apple.SwiftUI.plist'))

        spec = SPECS_BY_ID[TweakID.SwiftUINewScrollEdgeEffectTag]
        self.assertIs(spec.location, location)
        self.assertEqual(spec.key, key)
        self.assertEqual(spec.min_version, '27.2')
        self.assertTrue(spec.experimental)
        self.assertIn('suite resolution', spec.warning)

        tweak = spec.factory()
        self.assertEqual(tweak.apply_tweak({}), {})
        for state in (False, True):
            with self.subTest(state=state):
                tweak.set_state(state)
                self.assertEqual(
                    tweak.apply_tweak({}),
                    {location: {key: state}},
                )
        tweak.set_state(None)
        self.assertEqual(tweak.apply_tweak({}), {})

    def _assert_flag(self, tweak_id, domain, key, min_version='26.2'):
        spec = SPECS_BY_ID[tweak_id]
        self.assertIs(spec.location, FileLocation.featureflags)
        self.assertEqual(spec.key, key)
        self.assertEqual(spec.min_version, min_version)
        self.assertTrue(spec.experimental)
        self.assertIsNotNone(spec.warning)

        tweak = spec.factory()
        self.assertEqual(tweak.apply_tweak({}), {})

        for state in (True, False):
            with self.subTest(state=state):
                tweak.set_state(state)
                self.assertEqual(
                    tweak.apply_tweak({}),
                    {FileLocation.featureflags: {
                        domain: {key: {'Enabled': state}},
                    }},
                )

        tweak.set_state(None)
        self.assertEqual(tweak.apply_tweak({}), {})


if __name__ == '__main__':
    unittest.main()
