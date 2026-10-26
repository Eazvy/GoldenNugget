import unittest
from src.exceptions.device_errors import (
    is_icloud_restore_in_progress, is_device_locked_error,
    is_connection_error, is_transient_restore_error,
)
from src.devicemanagement.device_manager import show_apply_error


class ICloudRestoreErrorTests(unittest.TestCase):
    def test_error25_is_not_a_lock_or_connection_retry(self):
        error = Exception("Device link error: {'ErrorCode': 25, 'ErrorDescription': "
                          "'iTunes Backup is unavailable while an iCloud Restore is in progress (MBErrorDomain/25)'}")
        self.assertTrue(is_icloud_restore_in_progress(error))
        self.assertFalse(is_device_locked_error(error))
        self.assertFalse(is_connection_error(error))
        self.assertFalse(is_transient_restore_error(error))
        alert = show_apply_error(error)
        self.assertEqual(alert.title, 'iCloud restore in progress')
        self.assertIn('Wait for it to finish', alert.txt)

    def test_wrapped_error_is_detected_without_retry(self):
        root = Exception('MBErrorDomain/25')
        wrapped = OSError('connection closed')
        wrapped.__cause__ = root
        self.assertTrue(is_icloud_restore_in_progress(wrapped))
        self.assertFalse(is_connection_error(wrapped))
        self.assertFalse(is_transient_restore_error(wrapped))

    def test_other_codes_are_not_confused_with_25(self):
        for code in (208, 250, 205):
            self.assertFalse(is_icloud_restore_in_progress(Exception(f'MBErrorDomain/{code}')))
        self.assertTrue(is_device_locked_error(Exception('MBErrorDomain/208')))
