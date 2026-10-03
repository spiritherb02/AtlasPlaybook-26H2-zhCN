# Atlas Playbook v0.5.0 → 支持 Windows 11 26H2 (build 26300)

## 问题原因

`playbook.conf` 里写死了白名单：

```xml
<SupportedBuilds>
    <string>26100</string>   <!-- 24H2 -->
    <string>26200</string>   <!-- 25H2 -->
</SupportedBuilds>
```

当前系统是 **Windows 11 Pro 26H2 / build 26300**，不在名单里，所以 AME Wizard 在
“Verifying Windows build and activation requirements” 这一步直接报
`This Windows build is not supported by this Playbook.`

Atlas 官方最短也是 0.5.0-hotfix，**没有任何版本支持 26300**，所以只能改 playbook 本身。

## 好消息

26H2 和 24H2 / 25H2 一样是**启用包（eKB）**升级：底层服务分支仍是 26100。
证据：本机 `BuildLabEx = 26100.1.amd64fre.ge_release.240331-1435`，
即 26300 只是 26100 上开了功能位。所以 Atlas 里那些注册表 / 服务 / 策略类 tweak
绝大多数路径完全一致，改成 26300 通过校验后大概率能正常走完。

（playbook 里除了 playbook.conf，其余文件没有任何 `26100`/`26200` 硬编码，
只有 `22000`/`23H2`/`24H2` 这类“大于等于”的判断条件，在 26300 上求值正常。）

## 做了什么

用 AME 通用密码 `malte` 解开 `.apbx`（本质是 ZipCrypto 加密的 ZIP），
在 `SupportedBuilds` 里追加 `<string>26300</string>`，再用同样的 ZipCrypto 重新打包。

- 原始文件未改动，另存为 `AtlasPlaybook_v0.5.0.apbx.orig-backup`
- 新文件：`AtlasPlaybook_v0.5.0-26H2.apbx`
- 逐条校验：543 个条目，名称与顺序与原包完全一致，全部可解密且 CRC32 正确
- 差异条目只有 `playbook.conf`（8008 → 7997 字节）

| | 原始 | 补丁版 |
|---|---|---|
| 文件 | `AtlasPlaybook_v0.5.0.apbx` | `AtlasPlaybook_v0.5.0-26H2.apbx` |
| 大小 | 48,024,713 | 47,995,329 |
| SHA256 | `13c4d8e7fc0ed38c37c5942ebcabf7f636389972e6de391a192ae649967602d8` | `0bf2ef709b434f44e746c492dc1eda6db297d840f5f4acff112ae414541ff21b` |

## 使用方法

1. 把 `AtlasPlaybook_v0.5.0-26H2.apbx` 拖进 AME Wizard Beta。
2. 出现 “未经验证的 playbook / not verified” 提示是正常的（改过就不再是官方签名版），确认继续即可。
   **不要点更新（Update）**，否则会被官方版本覆盖回去。
3. 后面如果卡在构建号之外的其它要求上，按下面清单逐条排。

## 装之前必须满足的 6 项硬要求

playbook.conf 里的 `Requirements`：

| 要求 | 怎么满足 |
|---|---|
| `DefenderToggled` | Windows 安全中心 → 关闭实时保护 |
| `NoAntivirus` | 卸载第三方杀软（火绒/360/卡巴等） |
| `Internet` | 保持联网 |
| `NoPendingUpdates` | 先把 Windows Update 跑完并重启，直到没有待装项 |
| `UCPDDisabled` | 用户选择保护驱动（UCPD）需关闭 |
| `PluggedIn` | 笔记本必须插电源 |

另外官方还有两条隐性的：
- **必须关闭内存完整性**（Windows 安全中心 → 设备安全性 → 内核隔离 → 内存完整性），
  AME Wizard 与它不兼容。
- **BitLocker 要先挂起/解密**。

## 风险与回退

- **这不是官方支持的组合。** Atlas 不支持预览/Insider 通道，26H2 属于未验证分支；
  出问题官方不会兜底。
- 如果跑到**移除 Defender / 遥测组件**那一步报错（`0x800f081e` 之类），
  是因为 `Z-Atlas-NoDefender-Package*.cab` 是按构建号做的 CBS 包；
  在功能页里改选 **Enable Defender (recommended)** 跳过这一步即可。
- Atlas **没有卸载功能**，回退只能重装系统。真机操作前务必做全盘镜像。
- 官方唯一“受支持”的路径仍是：干净重装 Windows 11 24H2/25H2 → 再跑原版 playbook。
  如果这台机器是主力机，建议走这条。

## 脚本

`atlas_build26300_patch.py` 可复用，支持追加任意构建号：

```bash
python atlas_build26300_patch.py 原.apbx 输出.apbx 26300
```
