# Atlas 精简后环境验证报告

> 生成时间：2026-10-03 11:20 (GMT+8)
> 机器：麦本本 XiaoMai 系列笔记本 / Pentium 4415U (Kaby Lake 7 代, 2C4T) / 16 GB / Intel HD 610 + NVIDIA 940MX
> 系统：Windows 11 专业版 26H2，build 26300.9457

## 总体结论

精简**成功落地**，无致命损坏。系统启动时间 10:59:35，Atlas 生效。核心服务、网络、音频、显示、驱动全部正常。
发现 **1 个需要你处理的问题**（芯片组/读卡器驱动缺失）与 **1 个行为变化需知悉**（不能休眠）。

---

## 一、Atlas 生效证据

| 检查项 | 结果 | 判定 |
|---|---|---|
| `HKLM\SOFTWARE\AtlasOS\Services` | 存在，含配置子键 | 已写入 |
| 桌面 `Atlas.lnk` | 存在，指向 `C:\Windows\Atlas` | 已安装 |
| 电源方案 | `Atlas Power Scheme`（GUID 1111…）已激活 | 已应用 |
| DiagTrack（遥测） | Stopped / **Disabled** | 已禁 |
| TrkWks（活动记录） | Stopped / **Disabled** | 已禁 |
| MapsBroker | Stopped / **Disabled** | 已禁 |
| PcaSvc（程序兼容性助手） | Stopped / **Disabled** | 已禁 |
| ssh-agent | Stopped / **Disabled** | 已禁 |
| WerSvc（错误报告） | 服务已不存在 | 已移除 |
| Fax / TabletInputService / diagnosticshub | 服务已不存在 | 已移除 |
| AllowTelemetry | 0 | 已禁 |
| AdvertisingID | 0 | 已禁 |
| Copilot 策略 | TurnOffWindowsCopilot = 1 | 已禁 |
| 搜索框建议 | DisableSearchBoxSuggestions = 1 | 已禁 |
| GameDVR | GameDVR_Enabled = 1（=禁用） | 已禁 |
| 菜单延迟 MenuShowDelay | 0 | 已应用 |
| 启动延迟 StartupDelayInMSec | 0 | 已应用 |
| MMCSS SystemResponsiveness | 10（默认 20） | 已调 |
| NetworkThrottlingIndex | 10（默认 10） | 已调 |
| Games 任务优先级 | 2 高 | 已调 |
| 内存占用 | 15.9 GB 中用 6.4 GB（40.3%），147 进程 | 正常偏低 |

## 二、前面建议项的实际结果 — 全部按预期生效

| 项目 | 建议 | 实测 | 结论 |
|---|---|---|---|
| 缓解措施 | Disable | `FeatureSettingsOverride=3`、`Mask=3`、SEHOP 关、`ProtectionMode=0` | ✅ 已关 |
| Defender | Enable | WinDefend **Running/Automatic**，SecurityHealthService、wscsvc 均 Running | ✅ 保留完好 |
| 自动更新 | Disable（改通知） | `AUOptions=2`；wuauserv/BITS/UsoSvc 均 Running，Catroot2 完整 | ✅ 只是不自动装 |
| 休眠 | 勾选 | `hiberfil.sys` 已删，`HibernateEnabled=0`，`powercfg /a` 显示"尚未启用休眠" | ✅ 已关 |
| 快速启动 | — | `HiberbootEnabled=0`，`powercfg /a` 显示"休眠不可用" | ✅ 附带关掉 |
| 电源性能 | 勾选 | `PowerThrottlingOff=1`、NVMe `IdlePowerMode=0`、`StorageD3InModernStandby=0` | ✅ 已应用 |
| 截图工具 | 卸掉 | `ScreenSketch` 无残留；`PrintScreenKeyForSnippingEnabled=0` | ✅ 已让出 PrtSc |
| Core Isolation | 勾选（空操作） | `EnableVirtualizationBasedSecurity=0` | ✅ 符合预期 |
| Edge | 不勾 | Edge 保留，WebView2 运行时 `154.0.4258.53` 在，默认浏览器仍是 Edge | ✅ 未误伤 |

## 三、必须处理的问题

### ~~问题 1：微软商店被禁用~~ → 已排除（误判）

初次检测用 `Get-AppxPackage` 没查到商店三件套，一度判断"商店被移除"。**经复核，这是误判**：

- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore\Applications` 中
  `Microsoft.WindowsStore`、`Microsoft.StorePurchaseApp`、`Microsoft.DesktopAppInstaller`
  **均有记录**；
- HKCU 用户级注册表显示实际版本：
  - `Microsoft.WindowsStore_22608.1401.5.0_x64__8wekyb3d8bbwe`
  - `Microsoft.DesktopAppInstaller_1.26.509.0_x64__8wekyb3d8bbwe`
- `%LOCALAPPDATA%\Microsoft\WindowsApps\` 下 `winget.exe`、`store.exe`、`microsoftstore.exe`
  别名全部存在（`WindowsPackageManagerServer.exe` 也在）。

**结论：商店与 winget 完好可用，无需修复。** 先前 `Get-AppxPackage` 无输出，是沙箱环境下
Cmdlet 枚举返回不完整所致，不是系统问题。

### 问题 1（中）：7 个设备的驱动报 Error

| 设备 | 说明 |
|---|---|
| SM 总线控制器 | 芯片组 SMBus，装机后未装驱动 |
| PCI 数据捕获和信号处理控制器 | 芯片组，未装驱动 |
| PCI 内存控制器 | 芯片组，未装驱动 |
| 基本系统设备 | 芯片组，未装驱动 |
| USB2.0-CRW | 读卡器，未装驱动 |
| Microsoft Kernel Debug Network Adapter | 内核调试适配器，无害可忽略 |

- 这 5 个芯片组/读卡器设备是**笔记本电源管理与读卡器**相关，缺驱动会导致待机/续航异常。
- 修复：装 Intel 芯片组 INF 驱动包（Apache Pass/芯片组），或用 Atlas 桌面
  `2. Drivers\Run Update Drivers.cmd`（需先跑 `.reg` 允许 Windows Update 装驱动）。

### 问题 2（需知悉）：只有 S3 睡眠可用，休眠/快速启动已被移除

`powercfg /a` 显示只有 S3 待机可用；休眠、混合睡眠、快速启动全部不可用（因为 hibernate 关掉了）。
这是预期的，但意味着**合盖只能睡眠、不能休眠**，长时间不用会掉电。
想恢复休眠：`Atlas\3. General Configuration\Hibernation\Enable Hibernation.cmd`（会重新启用快速启动）。

## 四、其他观察

- **Windows.old 仍存在**：装完 Atlas 未清理，占空间且可能干扰。官方建议清理掉（Disk Cleanup 或 `Dism /Online /Cleanup-Image /StartComponentCleanup`）。C 盘还有 192.5 GB 可用，不急。
- **启动项**：OneDrive、QQNT、WorkBuddy、MicrosoftEdgeAutoLaunch 四项，正常。
- **缺少浏览器**：除 Edge 外没有其他浏览器（你选了不装第三方浏览器），符合预期。
- **个人数据完好**：`Documents`(7 项)、`Downloads`(6 项)、`Desktop`(4 项)、`atlas`(4 项)、`.workbuddy`(57 项) 全在。
- **关键目录完好**：`System32`、`SysWOW64`、`Fonts`、`WinSxS`、`DriverStore`、`Windows.old` 均存在。
- **硬件正常**：Intel 无线 AC 3168、Realtek 有线网卡、Intel HD 610、NVIDIA 940MX、HD Audio、蓝牙均 Status=OK。
- **防火墙**：Domain/Private/Public 三档全部启用。
- **事件日志**：System 日志正常记录（1023 条）。

## 五、建议的后续动作（按优先级）

1. **装芯片组驱动**，解决 5 个 Error 设备 —— 对笔记本电源管理有实际影响。
   首选 Intel 芯片组 INF 包；或跑 Atlas 桌面 `2. Drivers\Run Update Drivers.cmd`
   （需先用同目录的 `.reg` 放开 Windows Update 装驱动）。
2. 装完驱动后清理 `Windows.old`（当前仍存在）：
   磁盘清理 → 清理系统文件 → 勾"以前的 Windows 安装"；或
   `Dism /Online /Cleanup-Image /StartComponentCleanup`。
3. 把 Windows Update 改成延迟模式（若还没做）：
   `Atlas\3. General Configuration\Windows Updates\Set Windows Update Deferral.cmd`
   → 功能更新 365 天，质量更新 7–30 天。
4. 验证 WSL：`wsl --status`（本次因沙箱拦截 `wsl.exe` 未能实测，
   但 playbook 确认未动 Hyper-V/WSL 组件，应可用）。装 Arch 需
   `wsl --install -d archlinux`，或在启用 `Microsoft-Windows-Subsystem-Linux` +
   `VirtualMachinePlatform` 后导入第三方 Arch 发行包。
5. 重启一次后复查 `powercfg /a` 与驱动状态，确认无异常。
