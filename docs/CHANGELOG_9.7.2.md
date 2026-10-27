# GoldenNugget Desktop 9.7.2

## General

- `.batter` templates moved to a dedicated Templates page with its own sidebar entry, home tile and "+ Import Templates" action. PosterBoard keeps Tendies and Video.
- Siri AI overrides are available on all iPhones running iOS 27.0 (previously iPhone 16 Pro only). Still experimental: only iPhone 16 Pro, build 24A437 was verified upstream.
- Mandatory update prompts: HotLoad `badNews` rules open an application-modal update dialog at startup (including cached/offline rules) that cannot be skipped with Later, Escape or closing the window, and the app stays blocked until it is restarted with an unaffected build.
- Catalog presets and templates can be marked as not tested on a device: the list and details show a "Not tested on a device" warning, and the Submit dialog asks whether the preset was tested.
- Removed the Disable App Device Verification, Disable Translation Helper and Disable Decision Helper daemon toggles, plus the Apple Watch Face Sync and Apple Watch Connection Helpers toggles. Old presets carrying those keys are dropped when applied.

## PosterBoard

- Saved poster items and their IDs survive staging cleanup instead of being wiped by it.
- Working PosterBoard databases use unique operation directories on the backup volume.
- Live Photos convert straight to the output MOV instead of holding the whole video in memory.
- Tendie previews parse in the background and read assets lazily from the ZIP with a bounded cache, so previews never apply to a destroyed dialog.

## Performance

Background work is bounded and faster (micro-benchmarks; full-apply times depend on the device):

- Media library checks are ~4x faster (3,000 files: 280 ms → 66 ms). Every file is still verified; only shared parent-directory info is reused within one walk.
- Liquid Glass previews: HSL processing of a 390×844 layer 167 ms → 1.5 ms, animation override tracks (200 × 600 keys) 7.3 ms → 0.7 ms, and CAML documents are parsed once instead of five times.
- Icon themes: adding 5,000 themes takes ~1 ms instead of 794 ms (the list is an ordered map, not a full rescan).
- The app picker filters by hiding and showing existing rows and reuses decoded icons instead of rebuilding the list on every keystroke; app icons are cached per device/bundle version for 24 hours and fetched through at most two SpringBoard services.
- The icon catalog materialises only visible cards, cancels previews outside the view, and caps its network cache at 64 MiB.
- Preset lists load from a small metadata header without parsing the whole tweak payload, and external changes invalidate the cache.
- Template payloads are streamed instead of loaded whole: a 3 × 8 MiB restore plan peaks at ~0.1 MB of Python allocations instead of ~24 MB, and the AFC inventory streams entries with up to four parallel transfers when the client demultiplexes replies.
- Backup cache snapshots copy metadata via clone/reflink where the file system supports it (payloads stay hardlinked), and recovery scratch copies stay on the backup volume instead of the system temp.
- Devices are probed concurrently (up to three) with a per-device timeout, the log viewer appends lines incrementally instead of rebuilding, and autosave debounces writes (500 ms) and replaces its JSON atomically.

## UI

- The first-run interface picker previews the real home screen instead of static screenshots.
- Home screen: seventh feature tile for Templates, PosterBoard subtitle is now "Animated wallpapers & video", and tile icons scale to fit their tiles without hardcoded offsets.
- Refreshed contributor credits with links to author profiles; added MiniVoidyy and Project Linwood.
- New random launch slogans.

## Fixes

- A corrupted or unknown manifest, encryption or inode state stops the restore instead of continuing with possibly incomplete data.
- A normal restore requires the verified AFC media store before pruning and touching the device, even when the flow is triggered outside the main device manager.
- Media restoration pushes only the up-to-date entries recorded by the verified media store; historical files stay on the computer.
- Applying a preset prepares every tweak before committing, so a failing tweak no longer leaves half-applied changes.
- Reset writes an empty plist instead of a zero-byte file on every supported iOS version, preventing SpringBoard boot loops on iOS 26 resets.
- Backup-encryption detection errors no longer abort the backup, and device-lock detection also covers passcode-required lockdown errors and code 208.
- Fixed the outgoing header action button overlapping the new one during rapid page changes.

**Full Changelog**: https://github.com/GoldenNugget-Team/GoldenNugget/compare/9.7.1...9.7.2
