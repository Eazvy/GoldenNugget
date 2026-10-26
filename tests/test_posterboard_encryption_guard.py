import asyncio
import plistlib
import tempfile
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from src.restore.posterboard_backup import _require_readable_backup
from src.restore.protective import extract_posterboard_db
from src.exceptions.device_errors import is_connection_error
from src.exceptions.nugget_exception import PosterBoardBackupEncryptionError
from src.utils.async_retry import async_retry


class PosterBoardEncryptionTests(unittest.IsolatedAsyncioTestCase):
    async def test_encrypted_backup_fails_once_without_retry(self):
        client=AsyncMock()
        client.get_will_encrypt.return_value=True
        attempt=AsyncMock(side_effect=lambda: None)
        async def run():
            await attempt()
            await _require_readable_backup(client)
        with patch('src.utils.async_retry.asyncio.sleep',new_callable=AsyncMock) as sleep:
            with self.assertRaises(PosterBoardBackupEncryptionError):
                await async_retry(run,3,retry_if=is_connection_error)
            sleep.assert_not_awaited()
        attempt.assert_awaited_once()

    async def test_plain_backup_remains_allowed(self):
        client=AsyncMock()
        client.get_will_encrypt.return_value=False
        await _require_readable_backup(client)

    async def test_encrypted_manifest_not_reported_as_corrupt_sqlite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'device'
            root.mkdir()
            (root/'Manifest.plist').write_bytes(plistlib.dumps({'IsEncrypted':True}))
            (root/'Manifest.db').write_bytes(b'encrypted bytes not SQLite')
            with self.assertRaises(PosterBoardBackupEncryptionError):
                extract_posterboard_db(folder,'device',str(Path(folder)/'poster.sqlite3'))
            self.assertEqual((root/'Manifest.db').read_bytes(),b'encrypted bytes not SQLite')
