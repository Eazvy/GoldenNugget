import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from src.tweaks.registry import SPECS, Section, LOCAL_ONLY_IDS
from src.tweaks.tweak_names import TweakID


class CatalogIntegrationTests(unittest.TestCase):
    def test_managed_preferences_skip_locationless_specs(self):
        from src.tweaks.registry import managed_pref_app_plists
        from src.tweaks.basic_plist_locations import FileLocation
        specs = [SimpleNamespace(location=None),
                 SimpleNamespace(location=FileLocation.springboard)]
        with patch('src.tweaks.registry.SPECS', specs):
            mirrors = managed_pref_app_plists()
        self.assertIn('Library/Preferences/com.apple.springboard.plist', mirrors)
        self.assertNotIn(None, mirrors)

    def test_local_catalog_is_additive_and_unique(self):
        self.assertEqual(len(SPECS), len({spec.id for spec in SPECS}))
        from src.tweaks.local_catalog import SPECS as LOCAL_SPECS
        self.assertTrue(LOCAL_ONLY_IDS)
        self.assertTrue(LOCAL_ONLY_IDS <= {spec.id for spec in LOCAL_SPECS})
        self.assertTrue({spec.id for spec in LOCAL_SPECS} <= {spec.id for spec in SPECS})

    def test_wallpaper_controls_only_belong_to_posterboard(self):
        for spec in SPECS:
            if any(word in spec.id.name.lower() for word in ('wallpaper', 'poster')):
                self.assertEqual(spec.section, Section.POSTERBOARD, spec.id.name)

    def test_posterkit_values_roundtrip_through_preset_codec(self):
        from src.controllers.preset_manager import PresetManager
        from src.tweaks.posterboard.device_overrides import PosterKitOverrides
        manager = PresetManager.__new__(PresetManager)
        source = PosterKitOverrides()
        source.enabled = True
        source.value = {'Clock:clockOpacity': 0.25}
        saved = manager._serialize_tweak(source)
        target = PosterKitOverrides()
        manager._apply_tweak(target, saved)
        self.assertEqual(target.value, source.value)
        self.assertTrue(target.enabled)
        target.value.clear()
        self.assertEqual(source.value, {'Clock:clockOpacity': 0.25})

    def test_empty_compilation_emits_no_preference_files(self):
        from src.controllers.tweak_compiler import CompilationContext, compile_tweaks
        store = {TweakID.Daemons: SimpleNamespace(enabled=False, never_enable=set())}
        hotload = SimpleNamespace(hidden_tweak_names=Mock(return_value=set()),
                                 rule_for=Mock(return_value=None),
                                 disabled_daemon_keys=Mock(return_value=set()))
        concat = Mock()
        context = CompilationContext(store, '27.2', 'iPhone16,2', [], False,
                                     AsyncMock(), concat, Mock(), Mock())
        result = asyncio.run(compile_tweaks(context, hotload))
        self.assertEqual(result.files, [])
        concat.assert_not_called()
