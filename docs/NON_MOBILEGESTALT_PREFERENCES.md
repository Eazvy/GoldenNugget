# Non-MobileGestalt preference additions

## Current controls

The Mute Control experiment was removed at the user’s request.

- **Disable OTA Updates** is the existing `Daemon.OTA` control in Daemons. Selecting it also writes Boolean false for `MobileAssetSUAllowOSVersionChange` in `/var/Managed Preferences/mobile/com.apple.MobileAsset.plist`. This added preference is not a verified update blocker on iOS 27.
- The seven separate OTA preference controls were removed. Server URL overrides, audience editing and same-version replacement restrictions are not staged.
- The companion preference is included only when daemon modifications are enabled and the OTA service group has an explicit selection. Turning OTA off and applying removes the version-change override. Untouched OTA selections write nothing; the disabled daemon master switch prevents all these writes.
- The existing iOS 27 managed-preference mirror is included in backup exclusions and daemon Restore Defaults handling, so it cannot reinstate the override after a reset.

## Feature flags not exposed as functioning controls

Original Nugget uses a nested domain/flag dictionary in `/var/preferences/FeatureFlags/Global.plist`. Most flags use `{"Enabled": bool}`; its Photos `Lemonade` entry instead uses a Boolean directly. It does not establish a reader for the proposed `/var/Managed Preferences/mobile/FeatureFlags/Domain/*.plist` files. Copying the flags to that location would not demonstrate that Apple reads them. The current GoldenNugget restore code also explicitly excludes the old feature-flag route on iOS 27.

These requested candidates are non-MobileGestalt but have no verified supported write route here, so no duplicate or nonfunctional toggles were added:

| Domain | Flags |
| --- | --- |
| SpringBoard | SwiftUITimeAnimation, AutobahnQuickSwitchTransition, SlipSwitch, PosterEditorKashida, SolariumElasticHUD, Domino, SuperDomino |
| IconServices | EnhancedGlass, SolariumCornerRadius |
| DocumentCamera | CaptureLiquidGlass |
| Photos | SolariumGridMagicPocket, Lemonade |
| Sharing | ShareSheetSolarium |
| Mail | SolariumSearch |
| PreferencesFramework | ForcedRetailKioskMode |
| Siri | sae_override, assistant_engine_override |
| SiriUI | sae |

Feature-flag names do not establish their functional effects on iOS 27 or imply that Siri/AI hardware eligibility can be changed.

## Primary sources

- https://github.com/leminlimez/Nugget/blob/main/src/tweaks/basic_plist_locations.py
- https://github.com/leminlimez/Nugget/blob/main/src/tweaks/tweak_classes.py
- https://github.com/leminlimez/Nugget/blob/main/src/tweaks/tweak_loader.py
