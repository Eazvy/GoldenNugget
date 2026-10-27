#!/usr/bin/env python3
"""Read the device's own eligibility state - read-only, no writes.

Why this exists
---------------
"Enable Apple Intelligence on a China-SKU device" is a chain with three
links, and only the first one is a file we can deliver:

  1. eligibilityd's answer for GREYMATTER / AMERICIUM / SIRI_MODE. We can
     force it: the durable override store in the eligibilityd container
     (delivered by ChinaAI.batter or the built-in Siri AI switch) is applied
     *before* the policy is computed, so the China-SKU block never runs.
  2. the device's own MobileGestalt keys (generative-model-systems and the
     region code). On a CH/A device these say "no AI", and they live in
     /var/preferences, which the iOS 27 backup agent will not install and
     which the sparse route loses to Security Recovery (see
     docs/iOS27_StatusBar_Research.md, 13 runs on 24A5408d).
  3. Apple's servers: whether the models and the Siri orchestration are
     served for a mainland China account at all.

This tool answers "which link failed" for a real device, so the next step
is evidence-based instead of guesswork. It reads:

  * the eligibilityd container   - did the override archive actually land,
    and is it byte-identical to the one we ship?
  * the answer cache             - what does eligibilityd currently report
    for GREYMATTER / AMERICIUM / SIRI_MODE, and which input is red?
  * MobileGestalt                - is the file even in the backup, and what
    does it say about generative models and the region?

Nothing is written to the device. The backup is filtered down to a handful
of files, exactly like src/restore/statusbar_fetch.py does for the status
bar archive.

Usage:
    python3 tools/probe_eligibility_state.py [udid]
"""
import asyncio
import hashlib
import os
import plistlib
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.usbmux import list_devices

from src.restore.protective import ProtectiveBackupService
from src.tweaks.siri_ai import HASHES

ELIGIBILITY_DOMAIN = "SysContainerDomain-com.apple.eligibilityd"
OVERRIDE_REL = "Library/Caches/NeverRestore/eligibility_overrides.data"

# Domains the answer cache shows up in.
ANSWER_DOMAINS = ("OS_ELIGIBILITY_DOMAIN_GREYMATTER", "OS_ELIGIBILITY_DOMAIN_AMERICIUM",
                  "OS_ELIGIBILITY_DOMAIN_SIRI_MODE", "OS_ELIGIBILITY_DOMAIN_SIRI_MODE_NEEDS_CONSENT")

# 2 = check failed, 3 = check passed (os_eligibility_input_t).
INPUT_NAMES = {
    "OS_ELIGIBILITY_INPUT_DEVICE_LANGUAGE": "device language",
    "OS_ELIGIBILITY_INPUT_SIRI_LANGUAGE": "Siri language",
    "OS_ELIGIBILITY_INPUT_DEVICE_REGION_CODE": "device region code",
    "OS_ELIGIBILITY_INPUT_COUNTRY_BILLING": "account billing country",
    "OS_ELIGIBILITY_INPUT_COUNTRY_LOCATION": "located country",
    "OS_ELIGIBILITY_INPUT_CHINA_CELLULAR": "China cellular",
    "OS_ELIGIBILITY_INPUT_GENERATIVE_MODEL_SYSTEM": "generative model system (MobileGestalt)",
    "OS_ELIGIBILITY_INPUT_EXTERNAL_BOOT_DRIVE": "external boot drive",
    "OS_ELIGIBILITY_INPUT_SHARED_IPAD": "shared iPad",
    "OS_ELIGIBILITY_INPUT_DEVICE_CLASS": "device class",
}


def keep(backup_file) -> bool:
    """Mid-stream filter: keep only the three things this probe reads."""
    name = getattr(backup_file, "device_name", "") or ""
    domain = getattr(backup_file, "domain", "") or ""
    rel = getattr(backup_file, "relative_path", "") or ""
    if domain.startswith(ELIGIBILITY_DOMAIN):
        return True
    if "os_eligibility" in rel or "os_eligibility" in name:
        return True
    if "MobileGestalt" in rel or "MobileGestalt" in name:
        return True
    return False


def device_dir_of(backup_root: str, udid: str) -> Path:
    root = Path(backup_root)
    candidate = root / udid
    if candidate.is_dir():
        return candidate
    if (root / "Manifest.db").is_file():
        return root
    for entry in root.iterdir():
        if entry.is_dir() and (entry / "Manifest.db").is_file():
            return entry
    return root


def read_payload(device_dir: Path, file_id: str) -> bytes:
    payload = device_dir / file_id[:2] / file_id
    if not payload.is_file():
        payload = device_dir / file_id
    return payload.read_bytes() if payload.is_file() else b""


def report_override(rows, device_dir: Path) -> bool:
    print("\n=== 1. eligibilityd override store ===")
    targets = [r for r in rows if r[1].startswith(ELIGIBILITY_DOMAIN)]
    if not targets:
        print("  NOT in the backup - the container was never uploaded,")
        print("  so nothing of ours could have landed either.")
        return False
    found = False
    for file_id, domain, rel, flags in targets:
        print(f"  {domain}/{rel} (flags={flags})")
        if not rel.endswith("eligibility_overrides.data"):
            continue
        found = True
        data = read_payload(device_dir, file_id)
        digest = hashlib.sha256(data).hexdigest()
        print(f"    {len(data)} bytes  sha256={digest}")
        known = {v: k for k, v in HASHES.items()}
        if digest in known:
            print(f"    -> our '{known[digest]}' payload, byte-identical")
        else:
            print("    -> NOT one of our payloads (different content)")
        try:
            archive = plistlib.loads(data)
            objects = archive["$objects"]
            mapping = objects[objects[archive["$top"]["root"].data]["overrideMap"].data]
            keys = [objects[k.data] for k in mapping["NS.keys"]]
            answers = {objects[k.data]: objects[objects[v.data]["answer"].data]
                       for k, v in zip(mapping["NS.keys"], mapping["NS.objects"])}
            print(f"    overrideMap domains: {keys}")
            print(f"    answers: {answers}")
        except Exception as error:
            print(f"    not a readable NSKeyedArchiver: {error}")
    if not found:
        print("  the container is in the backup but the override file is not")
    return found


def report_cache(rows, device_dir: Path) -> None:
    print("\n=== 2. eligibility answer cache ===")
    targets = [r for r in rows if "os_eligibility" in r[2].lower()]
    if not targets:
        print("  /var/db/os_eligibility/ is NOT part of the backup - the answer")
        print("  cache cannot be read through this channel.")
        return
    for file_id, domain, rel, flags in targets:
        print(f"  {domain}/{rel} (flags={flags})")
        data = read_payload(device_dir, file_id)
        try:
            cache = plistlib.loads(data)
        except Exception as error:
            print(f"    not a plist: {error}")
            continue
        print(f"    {len(cache)} domains cached")
        for name in ANSWER_DOMAINS:
            entry = cache.get(name)
            if entry is None:
                print(f"    {name}: not cached")
                continue
            answer = entry.get("os_eligibility_answer_t")
            source = entry.get("os_eligibility_answer_source_t")
            print(f"    {name}: answer={answer} source={source} "
                  f"({'eligible' if answer == 4 else 'not eligible' if answer == 2 else answer})")
            for key, value in (entry.get("status") or {}).items():
                if value != 3:
                    print(f"        red input: {INPUT_NAMES.get(key, key)} ({key}) = {value}")
            context = entry.get("context") or {}
            for key, value in context.items():
                print(f"        context: {key} = {value}")


def report_gestalt(rows, device_dir: Path) -> None:
    print("\n=== 3. MobileGestalt ===")
    targets = [r for r in rows if "MobileGestalt" in r[2]]
    if not targets:
        print("  com.apple.MobileGestalt.plist is NOT in the backup.")
        print("  It lives in /var/preferences, and the iOS 27 backup agent")
        print("  installs only 10 SystemPreferencesDomain paths, so it is")
        print("  neither readable nor writable through a restore.")
        return
    for file_id, domain, rel, flags in targets:
        print(f"  {domain}/{rel} (flags={flags})")
        data = read_payload(device_dir, file_id)
        try:
            gestalt = plistlib.loads(data)
        except Exception as error:
            print(f"    not a plist: {error}")
            continue
        print(f"    {len(gestalt)} keys")
        for key, value in sorted(gestalt.items()):
            low = key.lower()
            if any(token in low for token in ("generative", "region", "siri", "intelligence",
                                              "ai", "producttype", "deviceclass")):
                print(f"    {key} = {value!r}")


async def run(udid: str) -> int:
    ld = await create_using_usbmux(serial=udid, autopair=True)
    print(f"device: {ld.all_values.get('ProductType')} "
          f"({ld.all_values.get('DeviceClass')}) "
          f"iOS {ld.all_values.get('ProductVersion')} ({ld.all_values.get('BuildVersion')}) "
          f"region {ld.all_values.get('RegionInfo')}")
    with tempfile.TemporaryDirectory(prefix="nugget_elig_probe_") as backup_root:
        print("\n[1] filtered backup (eligibilityd container, answer cache, MobileGestalt)...",
              flush=True)
        # ProtectiveBackupService, not the raw service: its factory info lists
        # no app containers, so the device never uploads them. Over the network
        # the raw service would ship every app's data before the filter drops
        # it.
        async with ProtectiveBackupService(ld) as backup_client:
            await backup_client.backup(full=True, backup_directory=backup_root,
                                       progress_callback=lambda percent: None,
                                       filter_callback=keep)
        device_dir = device_dir_of(backup_root, udid)
        manifest = device_dir / "Manifest.db"
        if not manifest.is_file():
            print("no Manifest.db in the backup - nothing to read")
            return 1
        conn = sqlite3.connect(str(manifest))
        rows = conn.execute(
            "SELECT fileID, domain, relativePath, flags FROM Files "
            "WHERE domain LIKE ? OR relativePath LIKE ? OR relativePath LIKE ?",
            (ELIGIBILITY_DOMAIN + "%", "%os_eligibility%", "%MobileGestalt%")).fetchall()
        print(f"[2] {len(rows)} interesting manifest rows")
        report_override(rows, device_dir)
        report_cache(rows, device_dir)
        report_gestalt(rows, device_dir)
        conn.close()
    await ld.close()
    return 0


async def main() -> int:
    udid = sys.argv[1] if len(sys.argv) > 1 else None
    if not udid:
        devices = await list_devices()
        if not devices:
            print("no device connected")
            return 1
        udid = devices[0].serial
        print(f"using device {udid}")
    return await run(udid)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
