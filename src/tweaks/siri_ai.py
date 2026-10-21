"""Experimental eligibility payloads from MIT-licensed Project Linwood.

These are opaque NSKeyedArchives, never ordinary preference dictionaries.
"""
import hashlib
from pathlib import Path

from src.controllers.files_handler import get_bundle_files
from src.exceptions.nugget_exception import NuggetException
from src.utils.file_to_restore import FileToRestore
from .tweak_classes import Tweak

DOMAIN = "SysContainerDomain-com.apple.eligibilityd"
RELATIVE_PATH = "Library/Caches/NeverRestore/eligibility_overrides.data"
HASHES = {
    "enable": "4290e93faf86fd4f0d38364d2bb67398d9acb77f637555790c3339ad44f64d17",
    "reset": "f9b394804d478874f40eedcade937ab1d4a73773b4c8ed018ce51fb407a00818",
}


def payload_file(action):
    data = Path(get_bundle_files(f"files/siri_ai/{action}.data")).read_bytes()
    if hashlib.sha256(data).hexdigest() != HASHES[action]:
        raise NuggetException("The bundled Siri AI archive is damaged. Reinstall GoldenNugget.")
    return FileToRestore(contents=data, restore_path=RELATIVE_PATH,
                         domain=DOMAIN, owner=0, group=0)


def require_protective_delivery(files, inject_all):
    if any(f.domain == DOMAIN for f in files) and not inject_all:
        raise NuggetException(
            "Siri AI overrides require a prepared, unencrypted protective backup. "
            "Enable protective backup, disable local backup encryption in Finder/iTunes, "
            "and remove protective/sparse restore environment overrides before retrying.")


class SiriAITweak(Tweak):
    def __init__(self, action="enable"):
        super().__init__(key="SiriAI", owner=0, group=0)
        self.action = action

    def apply_tweak(self, files_to_restore, version, model):
        if not self.enabled:
            return
        # The archive schema is only verified on the research device/build.
        # Do not let presets or the iOS 26 "untested tweaks" option bypass this.
        if version != "27.0" or model != "iPhone17,1":
            raise NuggetException(
                "Siri AI overrides are currently limited to iPhone 16 Pro on iOS 27.0. "
                "Project Linwood verified build 24A437; other builds are untested.")
        files_to_restore.append(payload_file(self.action))
