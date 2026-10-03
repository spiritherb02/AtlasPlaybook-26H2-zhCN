# 归属与许可说明 / Attribution & Licensing

本仓库是**对上游开源项目的非官方简体中文本地化与兼容性补丁**，不是独立作品。
以下逐项说明上游来源、改动范围与许可证义务。

---

## 一、上游项目

| 项目 | 作者 / 维护者 | 来源 | 许可 |
|---|---|---|---|
| **AtlasOS / Atlas** | Atlas 团队 | <https://github.com/Atlas-OS/Atlas> · <https://atlasos.net> | **GPL-3.0** |
| **AME Wizard** | Ameliorated LLC | <https://ameliorated.io> · <https://docs.amelab.io> | 专有（核心部分 MIT） |

本仓库分发的 `AtlasPlaybook_v0.5.0-26H2-zhCN.apbx` 是
**AtlasOS Playbook v0.5.0-hotfix 官方发布的 `AtlasPlaybook_v0.5.0-hotfix.apbx` 的修改版**。

原始官方发布地址：<https://github.com/Atlas-OS/Atlas/releases/tag/0.5.0-hotfix>

## 二、改动内容（相对上游原版）

改动**仅限于** `playbook.conf` 一个文件，共两类：

1. **构建号适配** — 在 `<SupportedBuilds>` 中追加一行 `<string>26300</string>`。
2. **界面汉化** — 将配置向导的显示文案译为简体中文（24 处），
   涉及 `<Text>` / `<Title>` / `<Description>` / `<ShortDescription>` 等**纯展示**字段。

**未改动**的内容：所有 `<Name>` 选项标识、所有脚本（`.ps1` / `.cmd` / `.psm1`）、
所有配置（`.yml` / `.reg`）、图标、壁纸、可执行文件、软件包（`.cab`）、
以及 AME Wizard 本体。因此功能行为与上游完全一致。

逐条比对结果：543 个归档条目，名称与顺序与原版一致，逐条解密 + CRC32 校验零失败，
内容不同的文件**仅有 `playbook.conf`**。

## 三、许可证义务

AtlasOS 采用 **GPL-3.0**，本仓库作为其衍生作品，同样以 **GPL-3.0** 分发。

- GPL-3.0 许可证全文见 [`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt)。
- 本仓库**不修改**、不替换 GPL-3.0 条款，也未额外附加限制。
- 完整对应源码（Corresponding Source）：官方源码见
  <https://github.com/Atlas-OS/Atlas>；本仓库的全部改动以补丁脚本形式完整公开于
  [`scripts/`](scripts/)，任何人可据此从官方原版重现本修改版，源码形式与二进制形式一致。
- 本仓库未对分发的 apbx 添加任何技术保护措施（无 DRM、无加密信封之外的额外限制）；
  该归档使用 AME 通用密码 `malte`，密码与算法均公开。

### 关于 `scripts/` 下的补丁脚本

`scripts/` 目录中的 `atlas_zh_patch.py`、`apbx_tool.py`、`verify_atlas.py`
为本次本地化工作**从零编写的原创工具**，采用 MIT 许可（见 [`LICENSE`](LICENSE)）。
它们仅为处理 `.apbx` 归档格式的工具，不包含上游代码。

> 说明：为保证 GPL 兼容性，若将本仓库整体视为一个作品分发，
> 可整体按 GPL-3.0 对待；脚本单独使用时可按 MIT。

## 四、商标与非隶属声明

- **AtlasOS**、**Atlas** 是 Atlas 团队的标识；**AME Wizard**、**Ameliorated**
  是 Ameliorated LLC 的标识；**Windows** 是 Microsoft Corporation 的注册商标。
- 本仓库与 Atlas 团队、Ameliorated LLC、Microsoft Corporation
  **均无任何隶属、合作或背书关系**。
- 本仓库名称中的 "zhCN" 与 "26H2" 仅描述本地化语言与目标系统版本，
  不代表上游官方支持该语言或该构建号。

## 五、免责声明

- Windows 11 **26H2（build 26300）不属于 Atlas 官方支持的构建号**。
  上游仅声明支持 26100（24H2）与 26200（25H2）。使用本修改版属于**非支持配置**。
- AtlasOS **没有官方卸载方式**，回退需重新安装 Windows。
- 本仓库作者不对任何数据丢失、系统损坏或账户风险承担责任。请在评估风险后自行决定，
  并务必提前备份数据、准备可回退方案。

## 六、反馈与贡献

如发现上游项目本身的缺陷，请反馈至上游仓库；仅与汉化或构建号适配相关的问题，
可在本仓库提交 Issue。
