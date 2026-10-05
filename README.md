# AtlasPlaybook 26H2 简体中文汉化版

> **本仓库是对 [Atlas-OS/Atlas](https://github.com/Atlas-OS/Atlas) 的
> 非官方简体中文本地化与兼容性补丁，遵循上游 GPL-3.0 许可。**
> 与 Atlas 团队、Ameliorated LLC 均无隶属关系。详见 [ATTRIBUTION.md](ATTRIBUTION.md)。

AtlasOS Playbook v0.5.0-hotfix 的**简体中文汉化 + Windows 11 26H2 (build 26300) 构建号适配**版本。

上游原版：<https://github.com/Atlas-OS/Atlas/releases/tag/0.5.0-hotfix> ·
官网 <https://atlasos.net>

原版 AtlasOS Playbook 的 `SupportedBuilds` 只写了 `26100`(24H2) / `26200`(25H2)，
在 26H2 (build 26300) 上会被 AME Wizard 拒绝：

```
This Windows build is not supported by this Playbook.
```

本项目做两件事：

1. **构建号适配** — 在 `SupportedBuilds` 中追加 `26300`，让 26H2 通过校验。
2. **界面汉化** — 把配置向导里的文案翻译成简体中文（选项内部标识 `<Name>` 保持英文不动，
   因此所有功能行为与原版完全一致）。

## 本仓库改了什么（仅为 `playbook.conf`）

| 改动 | 说明 |
|---|---|
| 追加构建号 | `<SupportedBuilds>` 增加 `<string>26300</string>` |
| 界面汉化 | 40 处纯展示文案译为简体中文（属性形式 + 元素形式，见下） |

`playbook.conf` 里的界面文案有两种存法，两种都必须翻，否则会出现
「**页面的提问翻译了，下面的选项还是英文**」：

| 形式 | 例子 | 说明 |
|---|---|---|
| 属性 | `<TopLine Text="…"/>`、`<RadioPage Description="…">` | 页面标题 / 说明 / 上下提示行 |
| 元素 | `<Text>…</Text>`、`<Details>…</Details>`、`<ProgressText>…</ProgressText>`、`<Description><![CDATA[…]]></Description>` | 单选 / 勾选 / 浏览器选项文案、卡片副标题、安装进度文案 |

v1 的脚本只正则匹配了 `attr="value"`，把元素形式的 `<Text>` 全部漏掉了，
于是 13 条选项（Defender、缓解措施、自动更新、休眠、内核隔离、截图工具、
Edge、浏览器、工具箱…）留在英文。v2 已按 XML 结构同时覆盖两种形式。

**未改动**：所有 `<Name>` 选项标识、全部脚本与配置文件、图标、壁纸、软件包，
以及 AME Wizard 本体。逐条比对确认 543 个归档条目名称与顺序与原版一致，
逐条解密 + CRC32 校验零失败，唯一差异文件为 `playbook.conf`。

## 上游引用

本项目基于以下上游作品，版权归原作者所有：

- **AtlasOS** — Atlas 团队 · <https://github.com/Atlas-OS/Atlas> · GPL-3.0
- **AME Wizard** — Ameliorated LLC · <https://ameliorated.io> · 专有
  （本仓库不包含、不修改 AME Wizard）


---

## 下载

| 文件 | 说明 |
|---|---|
| [`AtlasPlaybook_v0.5.0-26H2-zhCN.apbx`](https://github.com/spiritherb02/AtlasPlaybook-26H2-zhCN/releases/latest/download/AtlasPlaybook_v0.5.0-26H2-zhCN.apbx) | 汉化 + 26H2 适配版（直接用这个，约 48 MB） |
| [`Releases`](https://github.com/spiritherb02/AtlasPlaybook-26H2-zhCN/releases) | 版本列表与校验值 |
| `scripts/` | 可复现的补丁脚本，支持任意构建号 |

> 48 MB 的 apbx 通过 Release 提供，避免 Git 仓库体积膨胀。

## 更新记录

- **v2（当前）** — 修复选项文案未汉化：`<Text>` 等元素形式的显示文本此前被漏掉，
  13 条选项（及 `<Details>` / `<ProgressText>` / 卡片 `<Description>`）现全部为简体中文。
  汉化条目 24 → 40 处。
- v1 — 首次发布：追加构建号 26300 + 属性形式文案汉化。

## 使用方法

1. 从 [AME 官方](https://ameliorated.io/) 下载 AME Wizard Beta（本仓库不提供，也不修改它）。
2. 把 `AtlasPlaybook_v0.5.0-26H2-zhCN.apbx` 拖进 AME Wizard。
3. 会提示 playbook **未经验证（not verified）** —— 这是正常的，改动过就不再是官方签名版，
   确认继续即可。**不要点 Update**，否则会被官方版本覆盖回去。
4. 按向导完成安装。

## 装机前必须满足的条件

playbook 里定义了 6 项硬性要求，缺一项都进不去：

| 要求 | 说明 |
|---|---|
| `DefenderToggled` | 关闭 Windows Defender 实时保护 |
| `NoAntivirus` | 卸载所有第三方杀毒软件 |
| `Internet` | 保持联网 |
| `NoPendingUpdates` | 先跑完 Windows Update 并重启，直到无待装项 |
| `UCPDDisabled` | 关闭用户选择保护驱动（UCPD） |
| `PluggedIn` | 笔记本必须插电源 |

另外还有两条官方隐性要求：

- **关闭内存完整性**：Windows 安全中心 → 设备安全性 → 内核隔离 → 内存完整性，必须关闭（AME Wizard 与之不兼容）。
- **挂起 BitLocker**。

## 各选项说明与建议

汉化后的向导界面（括号内为内部标识）：

| 界面文案 | 内部标识 | 说明 |
|---|---|---|
| 启用 Defender（推荐） / 关闭 Defender | `defender-enable` / `defender-disable` | 关闭会移除 Defender 组件包，降低安全性 |
| Windows 默认缓解措施（推荐） / 关闭全部缓解措施 | `mitigations-default` / `mitigations-disable` | 关闭会禁用 Spectre/Meltdown 等软件缓解，**老 CPU 上有性能收益** |
| 关闭 Windows 自动更新 / 启用 Windows 自动更新 | `auto-updates-disable` / `auto-updates-default` | 「关闭」实为改为通知模式（`AUOptions=2`），并非彻底禁用更新 |
| 关闭休眠 | `disable-hibernation` | 同时删除 `hiberfil.sys` 并关闭快速启动 |
| 最高性能（关闭省电） | `disable-power-saving` | 切换到「Atlas Power Scheme」节能方案副本，仅修改接通电源时的设置 |
| 关闭内核隔离 | `disable-core-isolation` | 关闭 VBS / HVCI |
| 移除截图工具应用 | `remove-snipping-tool` | 同时让出 PrtSc 键，适合已有第三方截图工具的用户 |
| 移除 Microsoft Edge | `uninstall-edge` | 注意可能影响依赖 WebView2 的程序 |
| 安装浏览器 | `install-another-browser` | 勾选后进入浏览器选择页 |
| 安装 Atlas 工具箱 | `install-toolbox` | 安装 AtlasOS Toolbox (BETA) |

### 关于 26H2 的已知注意事项

- 该构建号不属于 Atlas 官方支持范围。26H2 与 24H2/25H2 同属 `ge_release` 服务分支
  （26100 / 26200 / 26300），`BuildLabEx` 仍为 `26100.1.amd64fre.ge_release.…`，
  即高版本号来自启用包（eKB）。因此注册表 / 服务 / 策略类调整路径基本一致。
- **移除 Defender 的 CBS 组件包（`Z-Atlas-NoDefender-Package*.cab`）按构建号编译**，
  在非官方白名单构建上可能安装失败（如 `0x800f081e`）。建议在向导里选择
  **启用 Defender**，装完后再通过 `Atlas\7. Security\Defender\Toggle Defender.cmd` 自行调整。
- AtlasOS **没有官方卸载方式**，回退需要重装系统。真机操作前请做好全盘备份。

## 自行构建

无需依赖第三方库，仅用 Python 标准库：

```bash
# 汉化 + 追加构建号
python scripts/atlas_zh_patch.py 原版.apbx 输出.apbx 26300

# 只追加构建号，不汉化
python scripts/apbx_tool.py addbuild 原版.apbx 输出.apbx 26300

# 查看 / 提取 / 搜索 playbook 内容
python scripts/apbx_tool.py list   原版.apbx
python scripts/apbx_tool.py read   原版.apbx playbook.conf
python scripts/apbx_tool.py grep   原版.apbx "SupportedBuilds"
```

脚本会自动做校验：XML 结构合法性、选项名未被破坏、以及逐条解密 + CRC32 比对
（确认除 `playbook.conf` 外没有任何文件被改动）。

### 技术说明

`.apbx` 文件本质是 **ZipCrypto 加密的 ZIP 归档**，AME 的固定密码是 `malte`。
Python 的 `zipfile` 可以读取加密成员（`zipfile.ZipFile(f).read(name, pwd=b"malte")`），
但**不支持写入加密 ZIP**，因此 `scripts/` 中的脚本自行实现了 ZipCrypto 算法用于重新打包。
注意 `zipfile.testzip()` 不支持密码参数，校验时应改用逐个 `read()`。

## 精简后验证

`scripts/verify_atlas.py` 可在应用 playbook 并重启后检查系统状态：
Atlas 落地证据、服务禁用情况、缓解措施、Defender 存活、更新策略、休眠 / 快速启动、
电源节流、PrntSc 设置、Edge / WebView2、驱动异常、个人数据完好性等。

```bash
python scripts/verify_atlas.py
```

## 许可与声明

本仓库包含两种许可，请区分使用：

| 内容 | 许可 | 说明 |
|---|---|---|
| `dist/*.apbx`（Playbook 修改版） | **GPL-3.0** | 上游 AtlasOS 采用 GPL-3.0，衍生作品同样以 GPL-3.0 分发。全文见 [`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt) |
| `scripts/*.py`（本仓库原创工具） | **MIT** | 仅处理 `.apbx` 归档格式，不含上游代码。全文见 [`LICENSE`](LICENSE) |

- 本仓库是对 [Atlas-OS/Atlas](https://github.com/Atlas-OS/Atlas) 的**非官方本地化与兼容性补丁**，
  未修改 GPL-3.0 条款，未添加额外限制。
- 完整对应源码：官方源码见上游仓库；本仓库的全部改动以补丁脚本形式完整公开于
  [`scripts/`](scripts/)，可据此从官方原版复现本修改版。
- **AtlasOS** / **AME Wizard** / **Windows** 分别为 Atlas 团队、Ameliorated LLC、
  Microsoft Corporation 的标识或注册商标。本仓库与三者**均无隶属或背书关系**。
- 详细的归属、改动范围与许可义务说明见 [`ATTRIBUTION.md`](ATTRIBUTION.md)。

## 免责声明

- Windows 11 **26H2（build 26300）不属于 Atlas 官方支持的构建号**，属于非支持配置，请自行评估风险。
- AtlasOS **没有官方卸载方式**，回退需要重新安装 Windows。操作前请务必备份数据。
- 作者不对任何数据丢失或系统损坏承担责任。

