#!/usr/bin/env python3
"""解密線上加密報告（§12 全盤檢視、§20 交叉核對、§27 防覆蓋用）。支援多組通行碼外殼與舊版單組外殼。

用法：python3 tools/dec_multi.py 加密檔.html 輸出內容.html 通行碼 [通行碼2 …]
輸出：解密後的內容（<div id="app">…），並印出符合的是第幾組 slot（0＝客戶、1＝教練一…）。
"""
import base64, json, re, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

src, out, pws = sys.argv[1], sys.argv[2], sys.argv[3:]
h = open(src, encoding="utf-8").read()
b = base64.b64decode
m = re.search(r"var E=(\{.*?\}),K=", h, re.S) or re.search(r"var E\s*=\s*(\{.*?\});", h, re.S)
if not m:
    sys.exit("找不到加密資料")
E = json.loads(m.group(1))
kd = lambda pw, s, n: PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b(s), iterations=n).derive(pw.encode())
for pw in pws:
    if "k" in E:  # 多組
        for j, sl in enumerate(E["k"]):
            try:
                dek = AESGCM(kd(pw, sl["s"], E["n"])).decrypt(b(sl["i"]), b(sl["c"]), None)
            except Exception:
                continue
            pt = AESGCM(dek[:32]).decrypt(b(E["i"]), b(E["c"]), None).decode()
            open(out, "w", encoding="utf-8").write(pt)
            print(f"OK slot {j}（{'客戶' if j == 0 else '教練' + str(j)}）{'含雲華陀金鑰' if len(dek) > 32 else ''} {len(pt)} 字")
            sys.exit(0)
    else:  # 單組（tools/encrypt.py）
        try:
            pt = AESGCM(kd(pw, E["s"], E["n"])).decrypt(b(E["i"]), b(E["c"]), None).decode()
            open(out, "w", encoding="utf-8").write(pt)
            print(f"OK 單組 {len(pt)} 字")
            sys.exit(0)
        except Exception:
            pass
sys.exit("❌ 通行碼都不符")
