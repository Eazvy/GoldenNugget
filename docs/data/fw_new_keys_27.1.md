# iOS 27.1 SpringBoardFoundation 新键逆向报告

> 工具链（全部可复现）：
> - `tools/fw_accessor_pairs.py` —— accessor/key 精确配对 + 双缓存差分
> - `tools/dyld_cache_lookup.py --pool` —— 命中点周围 C 字符串池 dump
> - `tools/build_27_1_batter.py` —— 模板生成
> - `tools/verify_community_batters.py` —— 三重验证（builder round-trip +
>   GoldenNugget 真加载器 + 全开 `collect()` 合并）
>
> 原始数据：`docs/data/pairs_27.1_sbf.txt`，本报告每个键名都可在该文件中
> 逐条核对（417 键全表 + NEW 段）。
>
> 固件：iOS 27.1 模拟器 runtime `24A94401` 的
> `dyld_sim_shared_cache_arm64`，对比 iOS 27.0（`24A5380i`）。

## 0. 结论速览

SpringBoardFoundation 的 defaults 键表 **388 → 417**，净增 **29 键、0 删除**。
29 键的构成：

| 类别 | 数量 | 判定 |
|---|---|---|
| strict（accessor 严格配对） | 14 | 活 defaults 键；9 个开关 + 1 个滑杆已交付，4 个是数组/字典不交付 |
| loose 但是活键（ambient 区） | 2 | 已交付；配对算法因发射顺序漏掉，人工池 dump 补证 |
| loose 且不是 defaults 键 | 13 | 不交付：ObjC 类名 6、调试工具参数/常量 3、FF domain 名 2、未定 2 |
| 27.0 已存在但从未交付的 defaults 表键 | 4 | 已交付（本次扫描新发现，非 27.1 新增） |

最终交付 **`community-batters/SpringBoard-27.1.batter`：16 tweaks / 16 键**，
全部写 `/var/Managed Preferences/mobile/com.apple.springboard.plist`
（Managed Preferences 稀疏覆盖，低风险），与既有 5 个模板**零键冲突**，
263/263 tweaks 通过 GoldenNugget 真加载器验证。

**证据等级声明**：所有键都是固件级证据——键名 + accessor 存在于
SpringBoardFoundation 自己的 bind 表（`__cstring`）。无一个经过真机 A/B 测试。
按 `SPRINGBOARD_TWEAK_CANDIDATES.md` 的分级，strict 键属于"Tier C 中最强的
一种"（有 accessor 佐证），未达到 Tier A/B。

## 1. 方法

SpringBoardFoundation 把 defaults 绑定表摊平成一串 NUL 分隔的 C 字符串，
accessor 选择器紧挨它驱动的键：

```
... shouldDisableDockSpecular \0 SBDisableDockSpecular \0 ...
```

`fw_accessor_pairs.py` 用令牌流（单令牌进位）切出每个字符串，若某键的前一个
令牌是 lowerCamelCase 形态就记为一对（STRICT），否则记 loose。拿到两个缓存
的键集合后做差集。对高价值键再用 `dyld_cache_lookup.py --pool` dump 命中点
±几百字节的字符串池——`__cstring` 的相关字面量是相邻的，一次 dump 经常能
拿出整张键表。

## 2. 差分总览

```
=== SpringBoardFoundation: 388 keys @ 27.0 -> 417 @ 27.1 ===
  added: 29   removed: 0
```

（`docs/data/pairs_27.1_sbf.txt` 头部：`STRICT 296 / loose 121 (total 417)`，
`new vs baseline+repo: 14 strict, 15 loose`。）

27.1 没有删除任何键——所有变化是纯增量，这与"新硬件形态（折叠）+ 新调试
设施"的方向一致。

## 3. 14 个 strict 新键（活 defaults 键）

| # | 键 | accessor | 推断类型 | 所属表 | 交付 |
|---|---|---|---|---|---|
| 1 | `SBHomeScreenShowsSearchButton` | `showsHomeScreenSearchAffordance` | BOOL | SBHomeScreenDefaults | ✅ 开关（见 §6） |
| 2 | `SBDebugHUD` | `debugHUD` | BOOL | **SBDebugHUDDefaults（27.1 新类）** | ✅ 开关 |
| 3 | `SBShowHingeAngleHUD` | `showHingeAngleHUD` | BOOL | SBDebugHUDDefaults | ✅ 开关（折叠设备） |
| 4 | `SBVisualizeTouchSuppression` | `visualizeTouchSuppression` | BOOL | always-on/misc 表 | ✅ 开关 |
| 5 | `SBRequireFreshTouch` | `freshTouchRequired` | BOOL | SBCoverSheet* 块 | ✅ 开关 |
| 6 | `SBForceAllAppsToSupportLimitedResizing` | `forceAllAppsToSupportLimitedResizing` | BOOL | resizing 表 | ✅ 开关 |
| 7 | `SBEnableDisplayDimTouchSuppressionForAllSurfaces` | `enableDisplayDimTouchSuppressionForAllSurfaces` | BOOL | idle timer 块 | ✅ 开关 |
| 8 | `SBUseFallbackDisplayRegionBlankingRenderer` | `useFallbackDisplayRegionBlankingRenderer` | BOOL | SBSystemApertureDefaults | ✅ 开关 |
| 9 | `SBAlwaysSendHingeUpdates` | `alwaysSendHingeUpdates` | BOOL | SBMiscellaneousDefaults | ✅ 开关（折叠设备） |
| 10 | `SBAmbientExtendedIdleTimer` | `ambientExtendedIdleTimer` | number（秒） | SBAmbientDefaults | ✅ 滑杆 |
| 11 | `SBBundleIdentifiersToForceSupportLimitedResizing` | `bundleIdentifiersToForceSupportLimitedResizing` | array | resizing 表 | ❌ 数组 |
| 12 | `SBFDevicePoseLastKnownCMAngle` | `lastKnownCMAngleDictionary` | dict | DevicePose | ❌ 状态字典 |
| 13 | `SBFDevicePoseLastKnownCMMagicPose` | `lastKnownCMMagicPoseDictionary` | dict | DevicePose | ❌ 状态字典 |
| 14 | `SBResizingCapabilityOverrideForApps` | `resizingCapabilityOverrideForApps` | dict | resizing 表 | ❌ 每 app 字典 |

池证据要点（`dyld_cache_lookup.py --pool`，偏移见 `pairs_27.1_sbf.txt`）：

- **`SBDebugHUD` / `SBShowHingeAngleHUD`**：27.1 新增了整个 defaults 类。
  ObjC 类表里 `SBDebugHUDDefaults` 出现在 `SBAccessibilityDefaults` /
  `SBAmbientDefaults` / `SBHomeScreenDefaults` 旁边（类型编码串
  `T@"SBDebugHUDDefaults",R,&,N` 可证）。键表里 `debugHUD \0 SBDebugHUD \0
  showHingeAngleHUD \0 SBShowHingeAngleHUD` 四连，随后是完整的
  **Continuous Fold** 子系统字符串（`continuousFoldTransitionEnabled`、
  `partiallyOpenToOpenFlatBoundary`、`transitionAutoCompleteDuration`、
  "Hinge Regions (Degrees) / Durations (Seconds)" 等）——折叠屏工程 UI。
- **`SBAlwaysSendHingeUpdates`**：键后面 5 个令牌就是字面量
  `-[SBMiscellaneousDefaults _bindAndRegisterDefaults]`，归属铁证。
- **`SBForceAllAppsToSupportLimitedResizing`** 与
  `SBBundleIdentifiersToForceSupportLimitedResizing` 在表中相邻
  （一个全局开关、一个按 bundle id 列表），accessor 分别为
  `forceAllAppsToSupportLimitedResizing` /
  `bundleIdentifiersToForceSupportLimitedResizing`。
- **`SBUseFallbackDisplayRegionBlankingRenderer`**：位于
  `SBNeverRenderSystemApertureFillOnGPU` 与
  `SBEnableSystemApertureStateCollection` 之间，属 SystemAperture 家族。
- **`SBAmbientExtendedIdleTimer`**：位于 `SBNotificationVisibleIdleTimer`
  （已交付滑杆，量程 0.1–3600、实测默认 8）与
  `SBEnableDisplayDimTouchSuppressionForAllSurfaces` 之间，同族同单位。
  滑杆量程照搬该兄弟键，描述中注明"单位未知、无实测默认值"。

## 4. ambient 区的发射顺序——配对算法的盲区

`SBAmbientDefaults` 的字符串不是"accessor \0 key"交替，而是**先键块、
后 accessor 块**。池 dump（±420 B）显示：

```
SBAmbientQiChargingIdleTimerDuration           <- 键块（27.0 已有）
SBAmbientTransientOverlayInteractiveDismissal  <- 键块（27.1 新）
SBAmbientPresentationControllerMockIsCharging  <- 键块（27.1 新）
qiChargingIdleTimerDuration                    <- accessor 块
presentationControllerMockIsCharging           <- accessor 块
transientOverlayInteractiveDismissal           <- accessor 块
```

三个 accessor 各自是键名的字面子串，配对无歧义。所以这两个 27.1 新键是活
defaults 键，只是被令牌流的前驱规则判成 loose。**教训：loose 不等于死键，
也可能是别的 defaults 类的发射顺序不同**——这也是本次没有把 loose 一键
否决、而是逐个 dump 池的原因。

## 5. 13 个 loose 键为什么不是 tweak

| 键 | 池证据 | 归类 |
|---|---|---|
| `SBFDevicePoseProvider` | `SBFDevicePoseProvider.m`、`T@"SBFDevicePoseProvider",R,N,V_poseProvider` | ObjC 类名 |
| `SBFHingeSamples` | `SBFHingeSamples.m`、`/var/mobile/Library/SpringBoard/hinge-samples.csv` | ObjC 类名 |
| `SBFIEDynamicMarkPersistence` | 邻接 `com.apple.SpringBoard.SBFInstrumentationEmitter` | ObjC 类名 |
| `SBContinuousFoldController` | 邻接 "Display content mode will change" 等日志串 | ObjC 类名 |
| `SBFDisplayContentModeTransitionContinuationLock` | "Can't acquire a continuation lock after invalidation." | ObjC 类名 |
| `SBFDisplayContentModeTransitionLockProvider` | 块类型编码 `v24@?0@"...Context"8@"...LockProvider"16` | ObjC 类名 |
| `SBFDisplayToolSystemSpace` | `-systemSpace=` 调试参数、`controlcenter`/`overlay` | 调试工具参数值 |
| `SBFDisplayToolSwapSettings` | `targetMode`/`targetHingePosition`/`-position=`/`-fade` | 调试工具参数 |
| `SBFHingeReplaySettings` | `mode`/`offset` | 调试工具参数 |
| `SBF_HINGE_SAMPLES` | 与 `hinge-samples.csv`、`SBFHingeSamples` 同池 | 宏/常量 |
| `SBForceButterfly` | 与无前缀 FF domain 名同表（见下） | FF domain 名 |
| `SBPhoneRingLight` | 同上 | FF domain 名 |
| `SBPerDisplayPowerStates` | 同上，但名字像状态字典 | 未定（不交付） |

FF domain 名的判定依据：这些 SB 前缀串与一批**无 SB 前缀**的名字出现在同一
区域——`ChamoisWindowingUI`、`ChamoisWindowingLivingOn`、`FlexibleWindowing`、
`ForceButterfly`、`WindowFlattening`、`FullScreenLetterboxing`、`Oneness`、
`ContinuousFold`、`SensitiveUI`、`DevicePose`、`DisplayContentMode` 等。
`...LivingOn` 是 Apple feature flag rollout domain 的典型形态。把这类名字当
defaults 键写进 `com.apple.springboard.plist` 不会有效果；而写
FeatureFlags plist 在 iOS 27 上本就不可用（`build_community_batters.py`
模块 docstring 已记录：restore 无法写 FeatureFlags plist，且
`/var/preferences` 是高风险系统目录）。

## 6. 搜索胶囊：27.1 的键更名

这是本次最有用户价值的发现，且与仓库已有资产直接相关：

- **已交付**：`SBHideSearchAffordance`（`SpringBoard.batter`），写遗留键
  `SBHomeScreenShowsSearchAffordance=False` 隐藏搜索胶囊。来源
  `src/tweaks/registry.py:994`（`TweakID.SBHideSearchAffordance`），
  **Tier A 真机验证**（`SPRINGBOARD_TWEAK_CANDIDATES.md` §4：设为 NO 移除
  主屏搜索胶囊，恢复后像素级一致）。
- **27.1 变化**：accessor `showsHomeScreenSearchAffordance` 现在绑定到
  **新键** `SBHomeScreenShowsSearchButton`。池 dump 中三连：
  `showsHomeScreenSearchAffordance \0 SBHomeScreenShowsSearchButton \0
  SBHomeScreenShowsSearchAffordance`——旧名仍留在表内但已无 accessor 绑定
  （推测作为迁移回退读取）。
- **交付决策**：新 tweak **只写新键**。旧键已被 `SBHideSearchAffordance`
  占用且语义相反（它 ON = 写 False），两个 tweak 写同一个键会互相覆盖。
  新 tweak ON = 写 True（显示胶囊），与 Tier A 实测的极性一致。
- 附带结论：27.1 上旧 tweak 写旧键可能不再生效（读取方已换键名），
  新 tweak 是 27.1 的正确拼写。

## 7. 交付物与验证

`community-batters/SpringBoard-27.1.batter`（16 tweaks）：

| tweak | 键 | min_version | 证据组 |
|---|---|---|---|
| Show Home Screen Search Button | `SBHomeScreenShowsSearchButton` | 27.1 | strict |
| Debug HUD | `SBDebugHUD` | 27.1 | strict |
| Visualize Touch Suppression | `SBVisualizeTouchSuppression` | 27.1 | strict |
| Require Fresh Touch (Cover Sheet) | `SBRequireFreshTouch` | 27.1 | strict |
| Force All Apps to Support Limited Resizing | `SBForceAllAppsToSupportLimitedResizing` | 27.1 | strict |
| Display Dim Touch Suppression (All Surfaces) | `SBEnableDisplayDimTouchSuppressionForAllSurfaces` | 27.1 | strict |
| Fallback Display Region Blanking Renderer | `SBUseFallbackDisplayRegionBlankingRenderer` | 27.1 | strict |
| Show Hinge Angle HUD | `SBShowHingeAngleHUD` | 27.1 | strict（折叠设备） |
| Always Send Hinge Updates | `SBAlwaysSendHingeUpdates` | 27.1 | strict（折叠设备） |
| Ambient Extended Idle Timer（滑杆） | `SBAmbientExtendedIdleTimer` | 27.1 | strict |
| Mock Charging State (StandBy) | `SBAmbientPresentationControllerMockIsCharging` | 27.1 | ambient 活键 |
| Ambient Overlay Interactive Dismissal | `SBAmbientTransientOverlayInteractiveDismissal` | 27.1 | ambient 活键 |
| Disable Auto Dim | `SBDisableAutoDim` | 27.0 | 27.0 已存在 |
| Home Screen Wallpaper Dimming | `SBEnableHomeScreenWallpaperDimming` | 27.0 | 27.0 已存在 |
| External Display Mirroring | `SBExternalDisplayMirroringEnabled` | 27.0 | 27.0 已存在 |
| Sensitive UI | `SBSensitiveUIEnabled` | 27.0 | 27.0 已存在 |

验证结果（`tools/verify_community_batters.py`）：

```
[OK ] LiquidGlass.batter: 57 tweaks, 0 builder errors | 57 tweaks accepted
[OK ] LiquidGlass-Advanced.batter: 54 tweaks, 0 builder errors | 54 tweaks accepted
[OK ] SpringBoard.batter: 24 tweaks, 0 builder errors | 24 tweaks accepted
[OK ] SpringBoard-Experimental.batter: 58 tweaks, 0 builder errors | 58 tweaks accepted
[OK ] SpringBoard-Experimental-2.batter: 54 tweaks, 0 builder errors | 54 tweaks accepted
[OK ] SpringBoard-27.1.batter: 16 tweaks, 0 builder errors | 16 tweaks accepted
collect() with every tweak on, iOS 26.1 / 27.0: 无冲突
ALL OK
```

另外单独做了键级重叠检查：新模板 16 个键与既有 5 个模板写入的键**零交集**
（第一版曾把遗留键 `SBHomeScreenShowsSearchAffordance` 一起写，与
`SBHideSearchAffordance` 冲突，已按 §6 去掉）。

## 8. 未交付清单及理由

1. **4 个 strict 数组/字典键**（§3 表 #11–14）：`.batter` 的 plist 写入是
   整值替换，数组/字典没有有意义的开关语义；其中两个 `...LastKnown...` 是
   系统自己写的状态，用户写进去只会被覆盖。
2. **13 个 loose 非 defaults 键**（§5）：类名 / FF domain / 调试参数。
3. **同区域发现但不属于 SpringBoardFoundation 的键**：
   - `SBShowVictoria` —— 池中紧邻 `com.apple.springboard.usage` domain 串，
     属于**另一个 domain**，不能写进 `com.apple.springboard.plist`。
   - `SBHomeIcon*`（`SBHomeIconTintColor`、`SBHomeIconUserInterfaceStyle*`
     等）—— 27.0 起就存在的遗留键，且 `SPRINGBOARD_TWEAK_CANDIDATES.md`
     §13 已证死：存储已迁往 PosterBoard poster 配置
     （`SBMigratedHomeScreenDefaultsTintToPosterBoard` 迁移标记同在表内）。
   - `SBShowBatteryPercentage` —— 27.0 已存在的状态栏区键，无 accessor，
     疑似 `SBShowBatteryLevel`（已交付）的 legacy 别名；未验证前不交付。
   - `SBOrientationActuation` / `SBShowInternalWidgets` —— 位于 UIKit
     preference domain 区，归属不确定。
   - `SBRecentDisplays` / `SBRecentDisplayItems` / `SBRecentDisplayItemRoles`
     / `SBMostRecentFloatingApplicationState` / `SBStackshotUIFeedback` ——
     无 accessor 的松散簇，像状态跟踪键而非开关。

## 9. 过程中发现并修复的工具缺陷

1. **`fw_accessor_pairs.py` 的 `known_keys()` 静默失败**（已修复）：
   该函数用 `try/except Exception: pass` 包住两个 import——`src.tweaks.registry`
   需要 PySide6（系统 python 没有），`batter_builder` 不在 sys.path（工具只
   插入了 repo 路径）。两个都失败时 `known` 退化成"3 个文档的全部 6+ 字符
   token"，靠文档恰好提到 registry 键才蒙对。修复：加入 BUILDER 路径、
   每个源报告加载量、失败时向 stderr 打印醒目警告。用带 PySide6 的
   `~/.workbuddy/binaries/python/envs/default/bin/python` 重跑后
   `known_keys sources: registry:253 template_builder:135 + 3 docs -> 923 keys`，
   与 `known_keys_data.SOURCE` 声称的 923 一致；重跑差分结果不变（仍 29 键），
   证明旧结果正确但属于运气。
2. **bash grep 多交替模式的偶发空结果**：本轮早前两次用
   `grep "A\|B\|C\|..."` 查 registry 得到空输出（实际有匹配），导致一度误判
   "14 个 strict 键都不在 registry"。已用 Python 对 17 个候选键逐一计数复核
   （只有 `SBHomeScreenShowsSearchAffordance` 在册）。教训延续仓库既有纪律：
   **否定结论必须用可枚举方式复核，不能依赖单条 grep 的空输出**。
