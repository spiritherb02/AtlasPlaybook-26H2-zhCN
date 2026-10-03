# -*- coding: utf-8 -*-
"""
Atlas Playbook v0.5.0 汉化 + 26H2 适配 补丁脚本

把 playbook.conf 里的界面文案翻译成简体中文，并在 SupportedBuilds 追加构建号。
选项名（<Name>）、图标名（Icon）、文件名（FileName）、注册表值一律不动。

用法：
    python atlas_zh_patch.py <源.apbx> <输出.apbx> [构建号 ...]
    python atlas_zh_patch.py 原.apbx 输出.apbx 26300
"""
import os
import re
import sys
import zlib
import struct
import random
import zipfile

PASSWORD = b"malte"

# ---------------------------------------------------------------- ZipCrypto
def _mk_crc_table():
    t = []
    for n in range(256):
        c = n
        for _ in range(8):
            c = (0xEDB88320 ^ (c >> 1)) if (c & 1) else (c >> 1)
        t.append(c)
    return t


_CRC = _mk_crc_table()


class ZipCrypto:
    def __init__(self, password):
        self.k0, self.k1, self.k2 = 0x12345678, 0x23456789, 0x34567890
        for b in password:
            self._upd(b)

    def _upd(self, c):
        self.k0 = ((self.k0 >> 8) ^ _CRC[(self.k0 ^ c) & 0xFF]) & 0xFFFFFFFF
        self.k1 = (self.k1 + (self.k0 & 0xFF)) & 0xFFFFFFFF
        self.k1 = (self.k1 * 134775813 + 1) & 0xFFFFFFFF
        self.k2 = ((self.k2 >> 8) ^ _CRC[(self.k2 ^ ((self.k1 >> 24) & 0xFF)) & 0xFF]) & 0xFFFFFFFF

    def encrypt(self, data):
        k0, k1, k2, t = self.k0, self.k1, self.k2, _CRC
        out = bytearray(len(data))
        i = 0
        for p in data:
            x = (k2 | 2) & 0xFFFF
            out[i] = p ^ (((x * (x ^ 1)) >> 8) & 0xFF)
            i += 1
            k0 = ((k0 >> 8) ^ t[(k0 ^ p) & 0xFF]) & 0xFFFFFFFF
            k1 = (k1 + (k0 & 0xFF)) & 0xFFFFFFFF
            k1 = (k1 * 134775813 + 1) & 0xFFFFFFFF
            k2 = ((k2 >> 8) ^ t[(k2 ^ ((k1 >> 24) & 0xFF)) & 0xFF]) & 0xFFFFFFFF
        self.k0, self.k1, self.k2 = k0, k1, k2
        return bytes(out)

    def header(self, check_byte):
        return self.encrypt(bytes(random.randrange(256) for _ in range(11)) + bytes([check_byte]))


def read_entries(src):
    z = zipfile.ZipFile(src)
    out = []
    for i in z.infolist():
        is_dir = i.filename.endswith("/")
        out.append({
            "name": i.filename,
            "is_dir": is_dir,
            "compress_type": i.compress_type if i.compress_type in (0, 8) else 8,
            "date_time": list(i.date_time),
            "external_attr": i.external_attr,
            "data": b"" if is_dir else z.read(i.filename, pwd=PASSWORD),
        })
    return out


def write_zip(entries, out_path):
    out, central = bytearray(), bytearray()
    for e in entries:
        name = e["name"].encode("utf-8")
        dt = e["date_time"] if e["date_time"][0] >= 1980 else [1980, 1, 1, 0, 0, 0]
        dos_time = (dt[3] << 11) | (dt[4] << 5) | (dt[5] // 2)
        dos_date = ((dt[0] - 1980) << 9) | (dt[1] << 5) | dt[2]
        off = len(out)
        flags = 0x0800
        if e["is_dir"]:
            crc = csize = usize = 0
            method, blob = 0, b""
        else:
            raw = e["data"]
            crc = zlib.crc32(raw) & 0xFFFFFFFF
            usize = len(raw)
            method = e["compress_type"] if e["compress_type"] in (0, 8) else 8
            if method == 8:
                c = zlib.compressobj(6, zlib.DEFLATED, -15)
                payload = c.compress(raw) + c.flush()
            else:
                method, payload = 0, raw
            flags |= 0x0001
            zc = ZipCrypto(PASSWORD)
            blob = zc.header((crc >> 24) & 0xFF) + zc.encrypt(payload)
            csize = len(blob)
        out += struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, flags, method, dos_time, dos_date,
                           crc, csize, usize, len(name), 0) + name + blob
        central += struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, flags, method, dos_time,
                               dos_date, crc, csize, usize, len(name), 0, 0, 0, 0,
                               e.get("external_attr", 0), off) + name
    cd = len(out)
    out += central + struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(entries), len(entries),
                                 len(central), cd, 0)
    with open(out_path, "wb") as f:
        f.write(out)


# ---------------------------------------------------------------- 汉化词表
# 只翻译显示文本；<Name>/<FileName>/Icon/颜色/链接 不动。
TEXT_MAP = {
    # OOBE 卡片
    "Performance": "性能",
    "By removing unnecessary background processes, telemetry, optionally disabling power-saving features and more.":
        "移除不必要的后台进程与遥测数据，并可选关闭省电特性等。",
    "Usability": "易用性",
    "By removing Windows' advertising, and fixing general annoyances, you will have a more enjoyable Windows experience.":
        "移除 Windows 广告、修掉各种恼人小毛病，让你用起来更顺手。",
    "Privacy": "隐私",
    "By eliminating most of Microsoft's notorious tracking, pre-installed apps, and bloatware, Atlas makes Windows private.":
        "清除微软大量恶名昭著的追踪、预装应用与冗余软件，让 Windows 回归私密。",

    # 第 1 页 Defender
    "Disabling Defender reduces security, and is an option for advanced users only.":
        "关闭 Defender 会降低安全性，仅建议高级用户选择。",
    "Defender can be toggled in the Atlas folder.":
        "可在 Atlas 文件夹中随时切换 Defender。",
    "Enable Defender (recommended)": "启用 Defender（推荐）",
    "Disable Defender": "关闭 Defender",
    "Learn more": "了解更多",

    # 第 2 页 缓解措施
    "Disabling mitigations reduces security, and could harm performance on modern CPUs.":
        "关闭缓解措施会降低安全性；在现代 CPU 上还可能损害性能。",
    "Disabling could improve performance on older CPUs.":
        "在老款 CPU 上关闭可提升性能。",
    "Default Windows Mitigations (recommended)": "Windows 默认缓解措施（推荐）",
    "Disable All Mitigations": "关闭全部缓解措施",

    # 第 3 页 自动更新
    "Updates are important for security, you'll get update notifications regardless.":
        "更新对安全性很重要；无论如何你都会收到更新通知。",
    "This can be changed in the Atlas folder later.": "稍后可在 Atlas 文件夹中修改。",
    "Disable Automatic Windows Updates": "关闭 Windows 自动更新",
    "Enable Automatic Windows Updates": "启用 Windows 自动更新",

    # 复用的页描述
    "Select the options you would like to use, they can be changed in the Atlas folder later.":
        "选择你想要启用的项目，稍后可在 Atlas 文件夹中修改。",

    # 勾选页一
    "Disable Hibernation": "关闭休眠",
    "Maximum Performance (Disable Power Saving)": "最高性能（关闭省电）",
    "Disable Core Isolation": "关闭内核隔离",

    # 勾选页二
    "Remove Snipping Tool App": "移除截图工具应用",
    "Remove Microsoft Edge": "移除 Microsoft Edge",
    "Install a Browser": "安装浏览器",

    # Toolbox
    "Would you like to install AtlasOS Toolbox (BETA)?": "是否安装 AtlasOS 工具箱（BETA）？",
    "Install Atlas Toolbox": "安装 Atlas 工具箱",

    # 浏览器页
    "Select your preferred browser to install. Browser settings are not modified.":
        "选择你想安装的浏览器。浏览器设置不会被修改。",
    "We do not recommend Chrome for privacy reasons.":
        "出于隐私考虑，我们不推荐 Chrome。",
    "Which is best for me?": "哪个更适合我？",

    # playbook 元信息
    "AtlasOS Playbook for Windows 11": "适用于 Windows 11 的 AtlasOS Playbook",
}

# 需要保留英文的浏览器品牌名，避免误翻
KEEP_EXACT = {"Brave", "LibreWolf", "Firefox", "Chrome", "Atlas"}


def translate(conf):
    """按 XML 属性精确替换显示文本，避免动到 Name/FileName/Icon。"""
    hits = []

    def repl_attr(m):
        attr, val = m.group(1), m.group(2)
        if attr in ("Text", "Title", "Description"):
            if val in KEEP_EXACT:
                return m.group(0)
            if val in TEXT_MAP:
                hits.append((val, TEXT_MAP[val]))
                return '%s="%s"' % (attr, TEXT_MAP[val])
        return m.group(0)

    # 匹配 attr="value"（属性值内无引号）
    conf2 = re.sub(r'\b(Text|Title|Description)="([^"]*)"', repl_attr, conf)

    # <ShortDescription> / <Details> 等元素文本
    def repl_elem(m):
        tag, inner = m.group(1), m.group(2)
        if inner in TEXT_MAP:
            hits.append((inner, TEXT_MAP[inner]))
            return "<%s>%s</%s>" % (tag, TEXT_MAP[inner], tag)
        return m.group(0)

    conf2 = re.sub(r'<(ShortDescription|Details|ProgressText)>(.*?)</\1>', repl_elem, conf2, flags=re.S)
    return conf2, hits


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    builds = sys.argv[3:] or ["26300"]

    entries = read_entries(src)
    print("[+] 读取条目 %d 个" % len(entries))

    tgt = next(e for e in entries if e["name"] == "playbook.conf")
    conf = tgt["data"].decode("utf-8-sig")

    # 1) 追加 SupportedBuilds
    m = re.search(r"<SupportedBuilds>.*?</SupportedBuilds>", conf, re.S)
    existing = re.findall(r"<string>(\d+)</string>", m.group(0))
    lines = ["\t<SupportedBuilds>"]
    lines += ["\t\t<string>%s</string>" % b for b in existing]
    added = [b for b in builds if b not in existing]
    lines += ["\t\t<string>%s</string>" % b for b in added]
    lines.append("\t</SupportedBuilds>")
    conf = conf[:m.start()] + "\n".join(lines) + conf[m.end():]

    # 2) 汉化
    conf, hits = translate(conf)

    print("[+] 新增构建号: %s" % (", ".join(added) or "无"))
    print("[+] 汉化条目 %d 处：" % len(hits))
    for a, b in hits:
        print("      %-72s -> %s" % (a[:70], b))

    # 3) 校验 XML 仍然合法
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(conf)
        print("[+] XML 结构校验通过")
    except ET.ParseError as ex:
        print("[!] XML 解析失败: %s" % ex)
        sys.exit(2)

    # 4) 确认 Name 未被改动
    for nm in ["defender-enable", "mitigations-default", "auto-updates-disable",
               "disable-hibernation", "disable-power-saving", "disable-core-isolation",
               "remove-snipping-tool", "uninstall-edge", "install-another-browser",
               "install-toolbox", "browser-brave", "browser-librewolf"]:
        assert "<Name>%s</Name>" % nm in conf, "选项名被破坏: %s" % nm
    print("[+] 选项名(Name) 全部完好")

    tgt["data"] = conf.encode("utf-8")
    write_zip(entries, dst)
    print("[+] 已写出 %s (%d 字节)" % (dst, os.path.getsize(dst)))

    # 5) 回读校验
    z = zipfile.ZipFile(dst)
    bad = 0
    for i in z.infolist():
        if i.filename.endswith("/"):
            continue
        try:
            z.read(i.filename, pwd=PASSWORD)
        except Exception:
            bad += 1
    diff = []
    zo = zipfile.ZipFile(src)
    for a, b in zip(zo.infolist(), z.infolist()):
        if a.filename.endswith("/"):
            continue
        if zo.read(a.filename, pwd=PASSWORD) != z.read(b.filename, pwd=PASSWORD):
            diff.append(b.filename)
    print("[+] 校验：条目=%d，解密失败=%d，内容不同=%s"
          % (len(z.infolist()), bad, diff))


if __name__ == "__main__":
    main()
