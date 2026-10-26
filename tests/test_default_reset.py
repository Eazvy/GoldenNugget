import asyncio
from contextlib import closing
import hashlib
import plistlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.controllers.default_reset import preference_reset_plan, remaining_reset_entries
from src.restore.inject import _build_mbfile_blob, _merge_preference_payload, inject_files_into_backup
from src.restore.restore import merge_duplicates, restore_files
from src.tweaks.basic_plist_locations import FileLocation
from src.utils.file_to_restore import FileToRestore
from src.utils.pages import Page
from src.utils.preference_reset import PreferenceKeyReset


class DefaultResetTests(unittest.TestCase):
    def test_injection_materializes_reset_as_valid_plist(self):
        with tempfile.TemporaryDirectory() as folder:
            device = Path(folder) / 'device'
            device.mkdir()
            domain, path = 'DatabaseDomain', 'com.apple.xpc.launchd/disabled.plist'
            file_id = hashlib.sha1(f'{domain}-{path}'.encode()).hexdigest()
            payload = device / file_id[:2] / file_id
            payload.parent.mkdir()
            original = plistlib.dumps({'selected': True, 'unrelated': True})
            payload.write_bytes(original)
            with closing(sqlite3.connect(device / 'Manifest.db')) as conn:
                conn.execute('CREATE TABLE Files(fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)')
                conn.execute('INSERT INTO Files VALUES (?,?,?,?,?)',
                             (file_id, domain, path, 1,
                              _build_mbfile_blob(path, original, owner=0, group=0)))
                conn.commit()
            self.assertEqual(inject_files_into_backup(folder, 'device', [
                (domain, path, PreferenceKeyReset([('selected',)]), 0o100644, 0, 0)]), (1, 0, 0))
            self.assertEqual(plistlib.loads(payload.read_bytes()), {'unrelated': True})

    def test_removes_recorded_daemons_preserving_unrelated_services(self):
        entries = {'Daemons/com.apple.analyticsd': {'value': True},
                   'Daemons/com.apple.locationd': {'value': False}}
        plan = preference_reset_plan(entries, [Page.Daemons])
        old = plistlib.dumps({'com.apple.analyticsd': True, 'com.apple.locationd': False,
                             'unrelated.service': True})
        result = plistlib.loads(_merge_preference_payload(old, plan[FileLocation.disabledDaemons]))
        self.assertEqual(result, {'unrelated.service': True})
        self.assertEqual(remaining_reset_entries(entries, [Page.Daemons]), {})

    def test_reset_is_idempotent_and_can_produce_an_empty_map(self):
        request = PreferenceKeyReset([('example',)])
        result = _merge_preference_payload(plistlib.dumps({'example': True}), request)
        self.assertEqual(plistlib.loads(result), {})
        self.assertEqual(plistlib.loads(_merge_preference_payload(result, request)), {})

    def test_nested_flags_preserve_other_fields_and_siblings(self):
        old = {'UIKit': {'Example': {'Enabled': True, 'Other': 7},
                         'Unrelated': {'Enabled': False}}}
        result = _merge_preference_payload(plistlib.dumps(old),
                                          PreferenceKeyReset([('UIKit', 'Example', 'Enabled')]))
        self.assertEqual(plistlib.loads(result), {
            'UIKit': {'Example': {'Other': 7}, 'Unrelated': {'Enabled': False}}})

    def test_duplicate_resets_merge_but_cannot_mix_with_normal_writes(self):
        def file(data):
            return FileToRestore(data, 'Library/Preferences/example.plist', domain='HomeDomain')
        merged = merge_duplicates([file(PreferenceKeyReset([('a',)])),
                                   file(PreferenceKeyReset([('b',)]))])
        self.assertEqual(merged[0].contents.paths, (('a',), ('b',)))
        with self.assertRaises(ValueError):
            merge_duplicates([file(PreferenceKeyReset([('a',)])), file(plistlib.dumps({'b': 2}))])

    def test_reset_cannot_be_delivered_as_an_empty_sparse_file(self):
        file = FileToRestore(PreferenceKeyReset([('example',)]),
                             'com.apple.xpc.launchd/disabled.plist', domain='DatabaseDomain')
        with self.assertRaisesRegex(Exception, 'unencrypted protective backup'):
            asyncio.run(restore_files([file], lockdown_client=Mock()))

    def test_only_selected_sections_are_reset(self):
        entries = {'DisableSecondsHand': {'value': True},
                   'Daemons/com.apple.analyticsd': {'value': True}}
        plan = preference_reset_plan(entries, [Page.InternalOptions])
        self.assertNotIn(FileLocation.disabledDaemons, plan)
        self.assertTrue(plan)
        self.assertEqual(set(remaining_reset_entries(entries, [Page.InternalOptions])),
                         {'Daemons/com.apple.analyticsd'})

    def test_missing_history_is_not_a_factory_default_guess(self):
        with self.assertRaises(ValueError):
            preference_reset_plan(None, [Page.Daemons])
