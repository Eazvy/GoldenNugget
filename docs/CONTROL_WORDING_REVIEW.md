# Plain-language control review

Reviewed the full registry of 287 tweaks, 214 daemon catalog records (including records not offered as controls), and all 62 legacy daemon-group descriptions. Groups and catalog records overlap; these counts are not a count of distinct visible switches.

## What changed

- Short, everyday titles and descriptions say what a setting tries to change and what can stop working. Descriptions were shortened again after feedback: at most 91 characters for tweaks and 86 for catalog services. Cards describe intended effects; compatibility cautions are available through the matching question-mark help controls.
- Removed repeated technical explanations from cards. Confirmation warnings still explain important consequences, using plain language.
- Removed promises unsupported by the evidence: Dynamic Island suppression does not guarantee removal of its black background; thermal indicators can be limited to Apple test devices; hidden glass controls are not verified system-wide glass removal.
- Unknown effects remain explicitly unknown. Repeated tries/tests/may phrases were removed from the descriptions; the tweaks page and help explain that these are intended effects, not proof of device results. A friendly title is not proof that a setting works or is safe. No speed, battery-life, restriction-removal, or feature-unlock benefit was invented.
- Help explains how each supported control type is undone, instead of incorrectly saying every switch behaves the same way. Numeric input limits are labeled as allowed app input, not proven system-supported limits.
- The daemon master description explains that switching it off does not undo previously applied changes.

## Research and evidence limits

Each entry was reviewed against its stored key/value or daemon labels. Existing local disassembly and preference-binding reports for iOS 27.0.1 (24A446) were checked for the SpringBoard and glass families. Relevant records include `ADDITIONAL_PREFERENCE_READERS.md` and the retained research reports in `/Users/oma/Downloads/GoldenNugget-display-research`.

A fresh index of 684 service labels was built from the locally extracted 24B5110a firmware plist files. Of 214 catalog records, 174 had a matching label in that index. The other 40 must not be presented as confirmed active services. A missing index match does not prove absence from every firmware or from the connected device. Legacy group members were checked against the same index individually.

A launch file verifies an identity, executable and exposed service names. These can support a cautious role description, but they do not establish every consequence of disabling the service. Preference registration likewise does not prove that retail-device consumers honor a write. The per-entry ledger in [CONTROL_WORDING_AUDIT.csv](CONTROL_WORDING_AUDIT.csv) records evidence and limits rather than treating all entries as verified.

Primary public sources used to check feature terminology and avoid overclaiming:

- [Apple: MetricKit performance reporting](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [Apple: Ad attribution](https://developer.apple.com/app-store/ad-attribution/)
- [Apple: DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [Apple: StoreKit purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [Apple: Content and privacy restrictions](https://support.apple.com/en-ca/guide/iphone/iph3ff83f3b1/ios)
- [SwiftUI Solarium reconstruction](https://github.com/pookjw/MySwiftUI/blob/main/Sources/MySwiftUICore/Solarium.swift): reconstructed implementation, not an Apple guarantee or a device result.
- [DynamicNotLand implementation](https://github.com/verygenericname/DynamicNotLand/blob/main/Tweak.xm): runtime view changes are not writable plist controls.

Apple feature documentation supports feature descriptions, not an assertion that every private service has been traced through all callers. Private entries without sufficient evidence remain marked as unknown, a test, or a possible effect. No new physical-device disable tests were performed. It is not possible to guarantee the precise effect of every undocumented toggle from these sources alone.

## Scope and checks

Setting IDs, plist keys, values, factories, default states, compatibility restrictions, daemon labels and membership were retained. User presets and device data were not changed. The saved catalog snapshots were compared for ID/key/value/path and daemon-membership changes; only wording differed. Source compilation passed. No automated test suite, device restore, commit, push or PR update was performed.

## Later catalog removals

Twenty controls were subsequently removed at the user's request: power-event logging, the Wallet button-trigger test, presentation alert suppression, wake sounds, internal widgets/apps, keyboard glass refresh, glass drawing logs/live adjustment, Lock Screen legal text/tips/swipe counter, Home Screen layout code, left-of-Home app, and all six Lock Screen quick-action overrides. Their stable enum names remain for compatibility, but they have no registered tweak and old preset entries are ignored. This does not undo values already applied to a device. The active registry now contains 267 entries.

Floating Views, Focus Highlights, Layered Icons, and Icon Depth & Motion now render after all other groups on the page, in that order. Their existing section ownership and compatibility rules are retained.
