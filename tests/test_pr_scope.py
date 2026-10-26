import hashlib
from pathlib import Path
import unittest


UPSTREAM_DAEMON_FILES = {
    "src/tweaks/daemons_tweak.py": "2b9dadae6f5a05fe1bc4039103c291bdb223ca267a843b7b6ec68b39e69de9f3",
    "src/tweaks/daemon_descriptions.py": "7f416576f2e16a085dc14eec3bb32837b1ec119c8701a726029923ce64b7d592",
    "src/gui/ios/daemon_categories.py": "02e341dfd67ec7651b84c924795cacbfa70491456782fe6e63c7b9ac70dd9f38"
}


class PullRequestScopeTests(unittest.TestCase):
    def test_daemon_catalog_and_allowlist_are_unchanged_from_upstream(self):
        root=Path(__file__).resolve().parents[1]
        for relative,expected in UPSTREAM_DAEMON_FILES.items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((root/relative).read_bytes()).hexdigest(),expected)
        self.assertFalse((root/'src/tweaks/daemon_catalog.json').exists())

    def test_daemon_ui_references_only_upstream_members(self):
        import ast
        from src.tweaks.daemons_tweak import Daemon
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'src/gui/ios/daemons.py').read_text())
        members={node.attr for node in ast.walk(tree) if isinstance(node,ast.Attribute)
                 and isinstance(node.value,ast.Name) and node.value.id=='Daemon'}
        self.assertTrue(members<=set(Daemon.__members__))


if __name__=='__main__':
    unittest.main()
