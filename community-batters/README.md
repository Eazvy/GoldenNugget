# Liquid Glass & SpringBoard 社区 Tweaks（.batter）

用 GoldenNugget-TemplateBuilder 的 model / rules / archive 模块生成，并用
**GoldenNugget 自己的加载器**（`src/tweaks/posterboard/community_tweaks.py`
的 `parse_tweaks`）逐个验证通过。重新生成：

```bash
python3 tools/build_community_batters.py   # 构建 + rules.validate（0 error）
python3 tools/build_27_1_batter.py         # 27.1 固件发现模板
python3 tools/build_internal_batter.py     # Internal Options 模板
python3 tools/build_china_ai_batter.py     # 国行 AI eligibility 覆盖
python3 tools/verify_community_batters.py  # 真加载器 + 全开 collect() 合并模拟
```

## 文件

| 文件 | Tweaks | 内容 |
|---|---|---|
| `LiquidGlass.batter` | 57 | Liquid Glass 核心：玻璃外观/反射/阴影/图标样式（registry 全量）+ SwiftUI 总开关 `com.apple.SwiftUI.DisableSolarium` + `UIViewGlassTintAmount` 滑杆 + iOS 26 Feature Flags 关闭法 |
| `LiquidGlass-Advanced.batter` | 54 | `UISolarium*` 数值调试族（浮动面板/焦点高光/堆叠图标运动）+ 两个被刷新误删的调试键 + 6 个 App 的每-App `DisableSolarium` |
| `SpringBoard.batter` | 24 | registry 非实验 SpringBoard 全量 + watchOS 配对放宽 + 2 个真机备份已验证 key + iOS 26 锁屏 Feature Flags |
| `SpringBoard-Experimental.batter` | 58 | 实验性 registry 第 1 批（警告已写入描述） |
| `SpringBoard-Experimental-2.batter` | 54 | 实验性 registry 第 2 批 |
| `SpringBoard-27.1.batter` | 16 | iOS 27.1 固件逆向新键：9 个 strict 开关 + 1 个 ambient 滑杆 + 2 个 ambient 活键 + 4 个 27.0 已存在但从未交付的键。全部 Managed Preferences 低风险写入。证据：`docs/data/fw_new_keys_27.1.md` |
| `InternalOptions.batter` | 18 | registry Internal Options 全量（状态栏构建号、强制布局方向、隐藏图标、各 App 测试设置、触摸可视化、粘贴声音等）。全部 Managed Preferences 低风险写入。SiriAI / ResetSiriAIOverrides 刻意排除——它们是 NSKeyedArchiver 归档操作，不是 plist 开关（见构建脚本 docstring） |
| `ChinaAI.batter` | 2 | 国行 Apple Intelligence 的 eligibility 覆盖：把 Project Linwood 的 override 归档（`enable.data` / `reset.data`，与 App 内置 Siri AI 开关同一份载荷）写进 eligibilityd 容器，强制 GREYMATTER/AMERICIUM/SIRI_MODE 在策略计算前即为合格，从而在 eligibility 层绕过国行 CH 区域封锁。二进制整文件写入，root:root，HIGH 风险。**实测在 iPad 上失败，见下方"实测失败"** |

### 实测失败（2026-10-22，iPad16,2 / iOS 27.0 24A5390f / RegionInfo CH/A）

开关选中（`AppleIntelligence.CN` enabled）、apply 无报错、载荷成功注入，但设置里
没有 AI 面板。从该设备自己的备份（33608 行 manifest）查到的原因：

| 域 | 目录行 | 文件行 |
|---|---|---|
| `SysContainerDomain-com.apple.eligibilityd` | 5 | **0** |
| `SysContainerDomain-com.apple.springboard` | 5 | **0** |
| `SysContainerDomain-com.apple.lsd` | 5 | 4 |
| `SystemPreferencesDomain` | 2 | 9 |
| `SysContainerDomain-com.apple.linkd` | 42 | 33 |

- iOS **不给这些系统守护进程的 `SysContainerDomain-*` 放任何文件行**。
  `eligibilityd` 只有 `""` / `Documents` / `Library` / `Library/Preferences` /
  `tmp` 五个目录行，`Library/Caches` 根本没被枚举，所以
  `Library/Caches/NeverRestore/` 在备份里从不出现。springboard、backboardd、
  apsd、akd、geod、metrickitd、coretelephony 及所有
  `SysSharedContainerDomain-systemgroup.*` 缓存容器同样为零；`lsd` 有 4 个文件行、
  `SystemPreferencesDomain` 有 9 个，说明容器格式本身支持文件——这是 iOS 逐守护
  进程的主动决定。
- 答案缓存 `os_eligibility`（`/var/db/os_eligibility/`）在全量备份里 **0 行**，
  eligibilityd 真实算出的答案在任何备份/恢复通道上都不可观测。
- `com.apple.MobileGestalt` 在该设备上通过 lockdown 返回 0 个键；
  `SysSharedContainerDomain-systemgroup.com.apple.mobilegestaltcache` 备份里
  只有根目录行。

结论：override store 既读不回来、也无法证明送达，而 iOS 27 的恢复代理从未被证明
会接受一个"设备自己的备份代理都拒绝枚举"的路径上的注入行。开关保留（batter 唯一
能碰的杠杆就是它），但**"没有 AI 面板"是预期结果，不是配置错误**。完整数据见
`files/siri_ai/README.md`。

合计 283 个开关。所有布尔开关都带 `writes_off`（把键写回原值）；数值滑杆的
`writes_off` 使用 registry 规定的移除值（如 `-1`）。`ChinaAI.batter` 的两个开关
**故意不写 `writes_off`**：关掉开关不清除已生效的覆盖，只能用 Reset 开关写空
map（同 App 内置行为）。

## 来源（全部可追溯）

| 来源 | 内容 |
|---|---|
| `src/tweaks/registry.py` SPECS | 权威键表：Liquid Glass 100 条 + SpringBoard 136 条 + Internal Options 20 条的路径、键、值、版本门控、警告，逐条镜像 |
| 上游 leminlimez/Nugget `tweak_loader.py` | 原版 "Disable Liquid Glass"：`com.apple.SwiftUI.DisableSolarium` → `.GlobalPreferences` |
| git 历史（`3b2bc17~1`） | Feature Flags 页面原始结构（SwiftUI/IconServices/DocumentCamera/Photos/AppleMediaServices/Sharing/Mail + SpringBoard 锁屏旗标）。该功能是被"整体移除"的 QOL 清理，非故障修复；iOS 27 无法经恢复写入且 `/var/preferences` 属高风险，故限 26.0–26.99 |
| `docs/data/effective_key_value_pairs.md` | `UIViewGlassTintAmount` 是唯一有完整 8 点响应曲线的 Liquid Glass 键；`cf9d2d9` 的无理由回退已逐条排除故障假设，原作者即本仓库所有者 |
| `docs/SPRINGBOARD_TWEAK_CANDIDATES.md` §5 | Tier B：`SBMedusaMultitaskingEnabled`、`SBFlexibleWindowingAutomaticStageCreationEnabledExternal`（SpringBoard 自己写进真机备份，键真实、效果未验证） |
| 社区报告（TidBITS / ArsTechnica 等） | 每-App `com.apple.SwiftUI.DisableSolarium`（Clock/Music/App Store/Weather/Notes/Home） |
| git 历史（`8e91241`） | `GlassContainerLogging`、`SolariumLiveTuning`：刷新时被摘掉，无故障记录，按原键补入 Advanced |
| iOS 27.1 固件逆向（`24A94401` vs `24A5380i` dyld shared cache） | `SpringBoard-27.1.batter` 全部 16 键：27.1 新增 29 键中 12 个活 defaults 键（14 strict + 2 个 ambient 键块发射顺序活键，扣掉 4 个数组/字典和更名关系的 1 个），外加 4 个 27.0 已存在、accessor 配对从未解析的 defaults 表键。工具：`tools/fw_accessor_pairs.py`（配对+差分）、`tools/dyld_cache_lookup.py --pool`（池证据）。完整分类与排除理由见 `docs/data/fw_new_keys_27.1.md` |
| Project Linwood（MIT，commit `b9438ce`）+ `files/siri_ai/*.data` | `ChinaAI.batter` 的两个 NSKeyedArchiver 载荷，构建时按 `src/tweaks/siri_ai.py` 的 SHA-256 校验，字节与 App 内置 Siri AI 开关完全一致；交付域 `SysContainerDomain-com.apple.eligibilityd` + `Library/Caches/NeverRestore/eligibility_overrides.data`（root:root） |
| 上游 Nugget `8a5966f`（"ai enabler"，2024-09） | 国行路线**刻意未采用**的旧实现：伪造 `/var/db/eligibilityd/eligibility.plist`（GREYMATTER 强制 4）+ 区域码替换版 OSEligibility asset `Config.plist` + MobileGestalt 键 `A62OafQ85EJAiiqKn4agtg`（generative-model-systems）/ `h9jDsbgj7xIVeIQ8S3/X3Q`（机型）。理由见下方"刻意排除" |

## 刻意排除（及理由）

- **国行旧路线：伪造 `/var/db/eligibilityd/eligibility.plist`（上游 `8a5966f`）**：
  该路线在 iOS 18.1–26.1 有过实测，26.2+ 被 Apple 修补；而且整文件替换会把设备
  自己的答案缓存换成 iOS 17 时代的快照（那份 37 域快照里**根本没有 GREYMATTER**）。
  27.x 的正确入口是 NeverRestore 里的 override store。
- **OSEligibility asset `Config.plist`（`/var/MobileAsset/AssetsV2/...`）**：
  `src/restore/path_mapping.py` 没有 `/var/MobileAsset/` 的域映射，app 与加载器
  都会直接拒绝这个路径；上游那两个 asset 哈希也是 18.x 的。
- **上游 AI enabler 里的 `OS_ELIGIBILITY_DOMAIN_CALCIUM` 条目**：那是给港/澳/台
  名称加"(China)"后缀的域，属于命名改动而不是 AI 开关，不在本模板范围内。
- **任何 MobileGestalt 写入**（区域码、generative-model-systems、机型）：本仓没有
  MobileGestalt 支持，而模板只能整文件替换 `/var/preferences/.../MobileGestalt.plist`，
  会连设备自己的键一起抹掉。
- **`SiriAI` / `ResetSiriAIOverrides`**（registry Internal Options 的 20 条里
  唯二不入模板的两条）：factory 是 `SiriAITweak`
  （`src/tweaks/siri_ai.py`），载荷是 SHA-256 校验的 NSKeyedArchiver
  （`EligibilityOverrideData`），且强制走未加密 protective backup
  （`require_protective_delivery`）。batter 的 plist 写入会把
  `{"SiriAI": true}` 合并进 `eligibility_overrides.data`——损坏归档、绕过
  哈希校验和保护性交付门，并落在 HIGH 风险的
  `/var/containers/Data/SystemGroup/` 容器里。这两个开关留在 App 内置的
  Internal Options 页面，守卫逻辑都在那里。
- **`SBHideDockBackground` / `SBDockAlpha`**：只存在于 `documentation.md`
  format-3 的示例里，上游与 registry 均无依据。
- **264 个 Tier-C SpringBoard 候选**：活体命中率 3.1%，未经证明的开关不如不上。
- **`SBHomeIcon*` 家族**：已证伪，存储已迁到 PosterBoard poster 配置
  （候选报告 §13）。
- **候选报告 §7 的危险键**（设备擦除、锁状态、安全渲染校验等）。
- **registry 标记 unavailable 的 3 条**（`SBStatusBarishLogOptions`、
  `SBExternalDisplayContentsScaleAndDontFileRadars`、
  `SBMainDisplayDarkeningPercentage`）：无有效取值域，滑杆无法表达。
- **只有 enum、从未接线的条目**（`dockCornerRadius` 等）：无任何生效证据。

## 风险提示

- 绝大多数写入落在 `/var/Managed Preferences/`（低风险，稀疏覆盖）。
- 3 处非 Managed 写入，GoldenNugget 的检查器会标风险，描述里也已注明：
  - `LockScreenFootnote` → SharedDeviceConfiguration.plist（高风险目录）
  - `WatchOSCompatibility` → com.apple.NanoRegistry.plist（整文件替换）
  - Feature Flags ×2 → /var/preferences/FeatureFlags/Global.plist（高风险，仅 iOS 26）
- `ChinaAI.batter` 的两个开关额外落在
  `/var/containers/Data/SystemGroup/com.apple.eligibilityd/`（HIGH），且如上所述
  在 iOS 27 上**无法确认送达**。想回退就用同模板的 Reset 开关（写空 map）。
- 两个 Feature Flags 开关按**顶层 category 分流**到不同文件（Solarium 类在
  LiquidGlass.batter，SpringBoard 类在 SpringBoard.batter），同时开启也不会
  互相覆盖——已用全开 `collect()` 模拟验证。
