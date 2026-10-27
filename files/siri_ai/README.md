# Siri AI eligibility archives

Source: https://github.com/mattisklein/project-linwood
Pinned commit: b9438cec65b384974a9c6be6169ec9fa1e64c83a
Author: mattisklein. MIT license reproduced in LICENSE.

`enable.data` is the original 631-byte `override_enable_gm.data`.
`reset.data` is the original 320-byte `override_reset.data`.
Both were generated using Apple's NSKeyedArchiver; never reserialize these as
ordinary preference plists. The runtime verifies their SHA-256 hashes.

Enable overrides SIRI_MODE (155), AMERICIUM (96), GREYMATTER (122) to answer 4;
AMERICIUM includes OS_ELIGIBILITY_CONTEXT_LINWOOD_AVAILABILITY = 2.
Reset is a valid archive with an empty overrideMap, not an empty file.

## Use

Internal Options contains **Siri AI (Ineligible Regions)** and **Reset Siri AI
Overrides**, mutually exclusive experimental switches. Select one, apply, and
reboot. Disabling a switch only deselects the operation. To roll back an applied
override, select Reset Siri AI Overrides and apply. This clears *all* overrides;
it does not restore a previous map. The ordinary Internal Options preference
reset does not clear these archives; use the dedicated switch.

Enable is available on iPhone 15 Pro / Pro Max and later iPhone generations
running any iOS 27.x release. Reset remains available on all iPhones on iOS 27.x
for recovery. iOS 26 and 28 are excluded.
Only iPhone 16 Pro (`iPhone17,1`), build 24A437 was reported verified upstream;
other builds and hardware are not verified by us.
Siri language must be English (US); complete Siri AI consent in Settings after
reboot. This does not add German voice support or guarantee server availability.

Delivery requires a prepared unencrypted protective backup. Encrypted backups,
skipping protection, and forced sparse delivery are refused for this payload.
File: `SysContainerDomain-com.apple.eligibilityd` /
`Library/Caches/NeverRestore/eligibility_overrides.data`, root:root, 0644,
protection class 4; generated directories root:root, 0755, class 0.

No real-device activation has been performed as part of this integration.

## Failed on iPad16,2 / iOS 27.0 (24A5390f), RegionInfo CH/A — 2026-10-22

The switch was selected (`AppleIntelligence.CN` enabled), the apply reported no
error, and the payload was injected — but Settings showed no AI panel.

Root cause, measured from that device's own backup (33,608 manifest rows):
**iOS does not put any file rows in `SysContainerDomain-*` for these system
daemons.** `SysContainerDomain-com.apple.eligibilityd` contributes 5 directory
rows (`""`, `Documents`, `Library`, `Library/Preferences`, `tmp`) and **0 file
rows** — `Library/Caches` is not even enumerated, so
`Library/Caches/NeverRestore/` never appears. The same holds for springboard,
backboardd, apsd, akd, geod, metrickitd, coretelephony and every
`SysSharedContainerDomain-systemgroup.*` cache container.

| Domain | dir rows | file rows |
|---|---|---|
| `SysContainerDomain-com.apple.eligibilityd` | 5 | **0** |
| `SysContainerDomain-com.apple.springboard` | 5 | **0** |
| `SysContainerDomain-com.apple.lsd` | 5 | 4 |
| `SystemPreferencesDomain` | 2 | 9 |
| `SysContainerDomain-com.apple.linkd` | 42 | 33 |

`lsd` shows the container is *capable* of carrying files, so this is a per-daemon
decision, not a format limitation. MobileGestalt is likewise unavailable:
`com.apple.MobileGestalt` returns 0 keys over lockdown on an unpaired-to-us
non-jailbroken device, and only the root directory of
`SysSharedContainerDomain-systemgroup.com.apple.mobilegestaltcache` is backed up.

Consequence: the override store cannot be *read back* to confirm delivery, and
iOS 27's restore agent has never been shown to accept an injected row for a path
the device's own backup agent refuses to enumerate. `os_eligibility` (the answer
cache under `/var/db/os_eligibility/`) has **0 rows** in a full backup, so the
answer that eligibilityd actually computed is not observable through any
backup/restore channel on this release.

Keep these switches, but treat "no AI panel" on iPad as the expected outcome
rather than a misconfiguration.
