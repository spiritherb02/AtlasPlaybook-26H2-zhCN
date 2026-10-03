# -*- coding: utf-8 -*-
"""
ZipCrypto 加密 ZIP 读写工具（AME .apbx 兼容）

AME Wizard 的 .apbx 是 ZipCrypto 加密的 ZIP，通用密码 'malte'。
Python zipfile 可读不可写，这里补上写入能力。

用法：
    python apbx_tool.py list   <in.apbx>
    python apbx_tool.py read   <in.apbx> <internal/path>
    python apbx_tool.py grep   <in.apbx> <regex>
    python apbx_tool.py addbuild <in.apbx> <out.apbx> <build> [build...]
    python apbx_tool.py setreg <in.apbx> <out.apbx> <file> <regex> <replacement>
"""
import os
import re
import sys
import zlib
import struct
import random
import zipfile

PASSWORD = b"malte"


def _make_crc_table():
    t = []
    for n in range(256):
        c = n
        for _ in range(8):
            c = (0xEDB88320 ^ (c >> 1)) if (c & 1) else (c >> 1)
        t.append(c)
    return t


_CRC = _make_crc_table()


class ZipCrypto:
    def __init__(self, password):
        self.k0, self.k1, self.k2 = 0x12345678, 0x23456789, 0x34567890
        for b in password:
            self._update(b)

    def _update(self, c):
        self.k0 = ((self.k0 >> 8) ^ _CRC[(self.k0 ^ c) & 0xFF]) & 0xFFFFFFFF
        self.k1 = (self.k1 + (self.k0 & 0xFF)) & 0xFFFFFFFF
        self.k1 = (self.k1 * 134775813 + 1) & 0xFFFFFFFF
        self.k2 = ((self.k2 >> 8) ^ _CRC[(self.k2 ^ ((self.k1 >> 24) & 0xFF)) & 0xFF]) & 0xFFFFFFFF

    def encrypt(self, data):
        k0, k1, k2 = self.k0, self.k1, self.k2
        t = _CRC
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


def write_encrypted_zip(entries, out_path):
    out, central = bytearray(), bytearray()
    for e in entries:
        name = e["name"].encode("utf-8")
        dt = e["date_time"] if e["date_time"][0] >= 1980 else [1980, 1, 1, 0, 0, 0]
        dos_time = (dt[3] << 11) | (dt[4] << 5) | (dt[5] // 2)
        dos_date = ((dt[0] - 1980) << 9) | (dt[1] << 5) | dt[2]
        offset = len(out)
        flags = 0x0800  # UTF-8 名字

        if e["is_dir"]:
            crc = csize = usize = 0
            method = 0
            blob = b""
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
                               e.get("external_attr", 0), offset) + name

    cd_off = len(out)
    out += central + struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(entries), len(entries),
                                 len(central), cd_off, 0)
    with open(out_path, "wb") as f:
        f.write(out)


def verify(old, new, expect_diff_names=("playbook.conf",), quiet=False):
    """逐条比对：名称顺序一致、内容仅指定文件不同。返回 (ok, 报告字符串)"""
    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    no = [i.filename for i in zo.infolist()]
    nn = [i.filename for i in zn.infolist()]
    lines = ["条目数 原=%d 新=%d 名称与顺序一致=%s" % (len(no), len(nn), no == nn)]
    ok = (no == nn)
    bad, diff = [], []
    for a, b in zip(zo.infolist(), zn.infolist()):
        if a.filename.endswith("/"):
            continue
        try:
            da = zo.read(a.filename, pwd=PASSWORD)
        except Exception as ex:
            bad.append((a.filename, "原包读取失败: %s" % ex)); continue
        try:
            db = zn.read(b.filename, pwd=PASSWORD)
        except Exception as ex:
            bad.append((b.filename, "新包读取失败: %s" % ex)); continue
        if da != db:
            diff.append(b.filename)
    lines.append("解密+CRC 校验失败 = %d" % len(bad))
    lines.append("内容不同的条目 = %s" % (diff or "无"))
    ok = ok and not bad and set(diff) <= set(expect_diff_names)
    for f, e in bad[:10]:
        lines.append("  !! %s -> %s" % (f, e))
    rpt = "\n".join(lines)
    if not quiet:
        print(rpt)
    return ok, rpt


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    cmd, src = sys.argv[1], sys.argv[2]

    if cmd == "list":
        for i in zipfile.ZipFile(src).infolist():
            print("%10d  %s" % (i.file_size, i.filename))
    elif cmd == "read":
        print(zipfile.ZipFile(src).read(sys.argv[3], pwd=PASSWORD).decode("utf-8-sig", "ignore"))
    elif cmd == "grep":
        pat = re.compile(sys.argv[3])
        z = zipfile.ZipFile(src)
        for i in z.infolist():
            if i.file_size == 0 or i.file_size > 400000:
                continue
            if not re.search(r"\.(cmd|bat|ps1|psm1|yml|yaml|conf|xml|reg|json|md|txt|inf)$",
                             i.filename, re.I):
                continue
            try:
                t = z.read(i.filename, pwd=PASSWORD).decode("utf-8", "ignore")
            except Exception:
                continue
            for k, ln in enumerate(t.splitlines(), 1):
                if pat.search(ln):
                    print("[%s:%d] %s" % (i.filename, k, ln.strip()[:180]))
    elif cmd == "addbuild":
        src2, dst = sys.argv[2], sys.argv[3]
        builds = sys.argv[4:] or ["26300"]
        es = read_entries(src2)
        tgt = next(e for e in es if e["name"] == "playbook.conf")
        conf = tgt["data"].decode("utf-8-sig")
        m = re.search(r"<SupportedBuilds>.*?</SupportedBuilds>", conf, re.S)
        existing = re.findall(r"<string>(\d+)</string>", m.group(0))
        lines = ["\t<SupportedBuilds>"]
        lines += ["\t\t<string>%s</string>" % b for b in existing]
        added = [b for b in builds if b not in existing]
        lines += ["\t\t<string>%s</string>" % b for b in added]
        lines.append("\t</SupportedBuilds>")
        conf = conf[:m.start()] + "\n".join(lines) + conf[m.end():]
        tgt["data"] = conf.encode("utf-8")
        write_encrypted_zip(es, dst)
        print("已写出 %s（新增 %s）" % (dst, ", ".join(added) or "无"))
        verify(src2, dst)
    elif cmd == "setreg":
        _, src2, dst, fname, pat, repl = sys.argv
        es = read_entries(src2)
        tgt = next(e for e in es if e["name"] == fname)
        t = tgt["data"].decode("utf-8-sig")
        new, n = re.subn(pat, repl, t, flags=re.S)
        if n == 0:
            print("!! 正则未匹配"); sys.exit(2)
        tgt["data"] = new.encode("utf-8")
        write_encrypted_zip(es, dst)
        print("已写出 %s（替换 %d 处）" % (dst, n))
        verify(src2, dst, expect_diff_names=(fname,))
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
