#!/usr/bin/env python3
"""多組通行碼加密（母指令 §15／§21／§30）。

一份內容用隨機 DEK 加密一次；每組通行碼各包一份 DEK（key slot），任一組都能解。
- 通行碼順序固定：〔客戶, 教練一, 教練二, 顧問夥伴（Wader）〕，開啟紀錄依序記成「客戶／教練一／教練二／顧問夥伴」。
- --ck：§30 雲華陀連結的客戶專屬金鑰檔（32 bytes）；只包進第 1 組（客戶）slot，教練 slot 不含。
- 外殼：tools/gate_shell_multi.html（含 §21 開啟紀錄、§15 教練聲明紅框、記住 30 天存 DEK）。

用法：
  python3 tools/multi_enc.py 明文報告.html 輸出.html --key xiaoan --log "保障現況分析｜xiaoan" 客戶碼 coach2026 coach2026b [--ck cloud_ck.bin]

明文報告.html 需為 v4.12 以後格式：<body> 後是 <div id="gate">…</div>，之後是 <div id="app" hidden>…（加密內容）。
"""
import argparse, base64, json, os, re, sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HERE = Path(__file__).resolve().parent
ITER = 200_000
b64 = lambda x: base64.b64encode(x).decode()


def find_div_end(s, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("找不到通行碼頁結尾")


def split(s):
    body = re.search(r"<body[^>]*>", s)
    g = s.find('<div id="gate"', body.end())
    ge = find_div_end(s, g)
    rest = s[ge:]
    m = re.match(r"\s*<script[^>]*>([\s\S]*?)</script>", rest)
    if m and "__gTry" in m.group(1):
        rest = rest[m.end():]
    close = rest.rfind("</body>")
    payload = rest[:close] if close >= 0 else rest
    assert 'id="app"' in payload, '加密內容裡找不到 id="app"'
    return s[:body.end()], s[g:ge], payload


def pack(payload, pws, ck=None):
    dek, iv = os.urandom(32), os.urandom(12)
    E = {"n": ITER, "i": b64(iv), "c": b64(AESGCM(dek).encrypt(iv, payload.encode(), None)), "k": []}
    for j, pw in enumerate(pws):
        s, i = os.urandom(16), os.urandom(12)
        k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=s, iterations=ITER).derive(pw.encode())
        wrapped = dek + ck if (ck and j == 0) else dek
        E["k"].append({"s": b64(s), "i": b64(i), "c": b64(AESGCM(k).encrypt(i, wrapped, None))})
    return E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("pws", nargs="+")
    ap.add_argument("--key", required=True, help="記住登入代號（客戶代號）")
    ap.add_argument("--log", required=True, help="開啟紀錄的報告名稱，例：保障現況分析｜xiaoan")
    ap.add_argument("--ck", help="§30 客戶專屬金鑰檔")
    a = ap.parse_args()
    pws = [re.sub(r"\s+", "", p) for p in a.pws]
    if any(len(p) < 6 for p in pws):
        sys.exit("❌ 通行碼至少 6 碼")
    head, gate, payload = split(Path(a.src).read_text(encoding="utf-8"))
    ck = Path(a.ck).read_bytes() if a.ck else None
    E = pack(payload, pws, ck)
    shell = (HERE / "gate_shell_multi.html").read_text(encoding="utf-8")
    shell = shell.replace("__PAYLOAD__", json.dumps(E)).replace("__KEY__", a.key + "-enc2").replace("__LOGNAME__", a.log)
    out = head + "\n" + gate + "\n" + shell
    probe = [w for w in re.sub(r"<[^>]+>", " ", payload).split() if len(w) >= 8][:300]
    leak = [w for w in probe if w in shell]
    if leak:
        sys.exit(f"⚠️ 外殼含明文片段：{leak[:3]}")
    Path(a.dst).write_text(out, encoding="utf-8")
    print(f"✅ {a.dst}（{len(out)//1024} KB，{len(pws)} 組通行碼{'，含雲華陀客戶金鑰' if ck else ''}）")


if __name__ == "__main__":
    main()
