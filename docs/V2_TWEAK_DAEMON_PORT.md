# Local v2 catalog port

Source: `/Users/oma/Downloads/GoldenNugget-v2`.

Added 45 daemon controls covering 46 previously absent labels. All are experimental, off by default, and listed under Risky tweaks. Source labels are carried over without claiming they exist or work on the connected firmware. Previously removed services remain blocked. No device apply was performed.

Added `SBDisableIconOutline` in the source Global Preferences domain as an unverified, explicit-state experiment. Untouched controls write nothing; switching off after enabling writes false.

Skipped duplicate ReduceHighlightingEffectsEnabled (v2 calls it Disable Icon Shimmer). Preserved the existing SpringBoard-domain SBDisallowGlassLockScreen control instead of adding a competing Global Preferences writer. Existing daemon groups with the same underlying labels were not duplicated.

## Added daemon controls

- Battery Usage Logging: `com.apple.powerlogd`, `com.apple.powerlogHelperd`
- Aggregated Diagnostics: `com.apple.aggregated`
- AppleSeed Services: `com.apple.appleseedd`
- OTA Package Services: `com.apple.otapackd`
- Network Diagnostic Capture: `com.apple.corecaptured`
- Packet Capture: `com.apple.pcapd`
- IME Traffic Collection: `com.apple.imetrafficcollector`
- CommCenter Core Telephony: `com.apple.commcenter.coretelephony`
- Core Telephony: `com.apple.coretelephony`
- Generator Services: `com.apple.generatord`
- MLT Services: `com.apple.mlt`
- App Store Services: `com.apple.appstored`
- Commerce Services: `com.apple.Commerced`
- Sale Services: `com.apple.saled`
- Repair Services: `com.apple.repaird`
- Recalibration Services: `com.apple.recalibrationd`
- Privacy Services: `com.apple.privacyd`
- Cipher Mining Services: `com.apple.cipherminingd`
- Life Science Services: `com.apple.lifescienced`
- Unattended Siri Services: `com.apple.siriunattended`
- Siri Service: `com.apple.SiriService`
- Siri Core Services: `com.apple.siri`
- Find My Network: `com.apple.searchpartyd`
- Nearby Services: `com.apple.nearbyd`
- Nearby Interaction: `com.apple.nearbyinteractiond`
- Find My Device Services: `com.apple.findmydeviced`
- Find My Location Services: `com.apple.findmylocate`
- Gaze Services: `com.apple.gaze`
- SportsKit Services: `com.apple.sportskitd`
- ARKit Services: `com.apple.arkitd`
- Face Services: `com.apple.faced`
- Media Session Services: `com.apple.mediasessiond`
- Remote Media Controls: `com.apple.mediaremotecontrol`
- Messaging Services: `com.apple.imagent`
- Messaging Foundation Services: `com.apple.imfoundation`
- Message Attachment Conversion: `com.apple.imtranscodingagent`
- Continuity Services: `com.apple.continuityd`
- OS Analytics: `com.apple.osanalyticsd`
- Microstackshot Collection: `com.apple.microstackshots`
- Stackshot Collection: `com.apple.stackshot.server`
- Crash Reporter Support: `com.apple.CrashReporterSupportHelper`
- Apple Account Services: `com.apple.appleaccountd`
- Apple ID Services: `com.apple.appleidservice`
- CloudKit Services: `com.apple.cloudd`
- iCloud Keychain Sync: `com.apple.cloudkeychainproxy`
