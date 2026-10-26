import asyncio
from contextlib import closing
from pathlib import Path
import plistlib
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from src.devicemanagement.device_manager import DeviceManager
from src.restore.inject import _prepare_preference_merges, preference_delivery_warnings
from src.utils.preference_reset import PreferenceKeyReset


class ManagedPreferenceMirrorTests(unittest.TestCase):
    def prepare(self, managed, native, *, has_native=True, missing_payload=False,
                managed_path='mobile/com.apple.springboard.plist'):
        with tempfile.TemporaryDirectory() as folder, closing(sqlite3.connect(':memory:')) as conn:
            conn.execute('CREATE TABLE Files(fileID TEXT, domain TEXT, relativePath TEXT, flags INTEGER)')
            path = 'Library/Preferences/' + managed_path[len('mobile/'):]
            if has_native:
                conn.execute('INSERT INTO Files VALUES (?,?,?,1)', ('abcdef', 'HomeDomain', path))
                if not missing_payload:
                    (Path(folder) / 'abcdef').write_bytes(plistlib.dumps({
                        'ExistingSetting': 123, 'SBShowBatteryPercentage': True}))
            files = [('ManagedPreferencesDomain', managed_path, managed, 0o100644, 501, 501),
                     ('HomeDomain', path, native, 0o100644, 501, 501)]
            return _prepare_preference_merges(conn, Path(folder), files)

    def test_identical_native_write_is_merged_without_creating_managed_file(self):
        patch = plistlib.dumps({'TweakKey': True})
        warnings = []
        token = preference_delivery_warnings.set(warnings)
        try:
            prepared = self.prepare(patch, patch)
        finally:
            preference_delivery_warnings.reset(token)
        self.assertEqual(len(prepared), 1)
        self.assertEqual(prepared[0][0], 'HomeDomain')
        self.assertEqual(plistlib.loads(prepared[0][2]), {
            'ExistingSetting': 123, 'SBShowBatteryPercentage': True, 'TweakKey': True})
        self.assertEqual(warnings, ['mobile/com.apple.springboard.plist'])

    def test_different_native_edit_is_not_a_substitute(self):
        with self.assertRaises(ValueError):
            self.prepare(plistlib.dumps({'One': True}), plistlib.dumps({'Two': True}))

    def test_merged_native_superset_covers_managed_edit(self):
        from src.restore.restore import merge_duplicates
        from src.utils.file_to_restore import FileToRestore
        managed = plistlib.dumps({'ManagedKey': True})
        files = merge_duplicates([
            FileToRestore(managed, 'Library/Preferences/com.apple.springboard.plist', domain='HomeDomain'),
            FileToRestore(plistlib.dumps({'NativeOnlyKey': 7}),
                          'Library/Preferences/com.apple.springboard.plist', domain='HomeDomain')])
        prepared = self.prepare(managed, files[0].contents)
        values = plistlib.loads(prepared[0][2])
        self.assertTrue(values['ManagedKey'])
        self.assertEqual(values['NativeOnlyKey'], 7)
        self.assertTrue(values['SBShowBatteryPercentage'])

    def test_encoding_differences_do_not_prevent_identical_edits(self):
        prepared = self.prepare(plistlib.dumps({'Key': True}, fmt=plistlib.FMT_BINARY),
                                plistlib.dumps({'Extra': 2, 'Key': True}, sort_keys=False))
        self.assertEqual(len(prepared), 1)

    def test_conflicting_or_differently_typed_values_still_abort(self):
        for value in (False, 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.prepare(plistlib.dumps({'Key': True}),
                             plistlib.dumps({'Key': value, 'Extra': 2}))

    def test_missing_or_unreadable_native_baseline_still_aborts(self):
        patch = plistlib.dumps({'TweakKey': True})
        for options in ({'has_native': False}, {'missing_payload': True}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.prepare(patch, patch, **options)

    def test_resets_require_identical_key_paths_not_just_empty_bytes(self):
        prepared = self.prepare(PreferenceKeyReset([('ExistingSetting',)]),
                                PreferenceKeyReset([('ExistingSetting',)]))
        self.assertNotIn('ExistingSetting', plistlib.loads(prepared[0][2]))
        with self.assertRaises(ValueError):
            self.prepare(PreferenceKeyReset([('One',)]), PreferenceKeyReset([('Two',)]))

    def test_other_managed_files_do_not_receive_a_generic_fallback(self):
        patch = plistlib.dumps({'TweakKey': True})
        with self.assertRaises(ValueError):
            self.prepare(patch, patch, managed_path='mobile/com.apple.other.plist')

    def test_ios27_does_not_stage_legacy_purplebuddy_scaffolding(self):
        manager = SimpleNamespace(get_current_device_version=lambda: '27.2',
                                  pref_manager=SimpleNamespace(skip_setup=True))
        files = []
        asyncio.run(DeviceManager.add_skip_setup(manager, files, True))
        self.assertEqual(files, [])
