#!/usr/bin/env python3
"""把明文客戶版報告書加密成可上架版本（通行碼由顧問自訂）。

用法：
  python3 tools/encrypt.py 明文報告.html 輸出.html 通行碼 [--key 記住登入用代號]

做法：
- 保留 <head>（樣式）與通行碼頁（id="gate"，含個資告知與同意勾選）
- 通行碼頁之後的內容（#app 與報告的 script）整段用 AES-GCM 加密
- 金鑰：PBKDF2-SHA256（200,000 次）由通行碼推導；原始碼裡不存通行碼、也不存雜湊
- 解密介面沿用 tools/gate_shell.js（與 jane 相同，支援「記住 30 天」）
"""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HERE = Path(__file__).resolve().parent
ITER = 200_000


def find_div_end(s: str, start: int) -> int:
    """回傳從 start 開始的 <div ...> 對應 </div> 結尾位置。"""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("找不到通行碼頁的結尾 </div>")


def split_report(s: str):
    body = re.search(r"<body[^>]*>", s)
    if not body:
        raise ValueError("找不到 <body>")
    g = s.find('<div id="gate"', body.end())
    if g < 0:
        raise ValueError('找不到通行碼頁 <div id="gate">')
    g_end = find_div_end(s, g)
    rest = s[g_end:]
    # 移除原本的明文通行碼檢查 script（定義 __gTry 的那一段）
    m = re.match(r"\s*<script[^>]*>([\s\S]*?)</script>", rest)
    if m and "__gTry" in m.group(1):
        rest = rest[m.end():]
    close = rest.rfind("</body>")
    payload = rest[:close] if close >= 0 else rest
    if 'id="app"' not in payload:
        raise ValueError('加密內容裡找不到 id="app"，請確認是 v4.12 格式的報告書')
    return s[: body.end()], s[g:g_end], payload


def encrypt(payload: str, password: str) -> dict:
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
    ct = AESGCM(key).encrypt(iv, payload.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"s": b(salt), "i": b(iv), "n": ITER, "c": b(ct)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("password")
    ap.add_argument("--key", help="記住登入用的代號（預設取輸出檔名）")
    a = ap.parse_args()

    pw = re.sub(r"\s+", "", a.password)
    if len(pw) < 6:
        print("❌ 通行碼至少 6 碼")
        return 1
    s = Path(a.src).read_text(encoding="utf-8")
    head, gate, payload = split_report(s)
    E = encrypt(payload, pw)
    key = (a.key or Path(a.dst).stem) + "-enc"
    shell = (HERE / "gate_shell.js").read_text(encoding="utf-8")
    shell = shell.replace("__PAYLOAD__", json.dumps(E)).replace("__KEY__", key)
    out = f"{head}\n{gate}\n<script>{shell}</script></body></html>\n"
    Path(a.dst).write_text(out, encoding="utf-8")
    # 自我檢查：明文報告內容不得出現在輸出檔
    probe = re.sub(r"<[^>]+>", " ", payload)
    words = [w for w in probe.split() if len(w) >= 8][:50]
    leaked = [w for w in words if w in out.replace(gate, "")]
    if leaked:
        print(f"⚠️ 輸出檔仍有明文片段：{leaked[:3]}")
        return 1
    print(f"✅ 已加密：{a.dst}（{len(out)//1024} KB，記住登入代號 {key}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
