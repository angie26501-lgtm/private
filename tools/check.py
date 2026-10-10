#!/usr/bin/env python3
"""上傳前檢查：客戶子目錄只能有加密的客戶版，不能有內部版、通行碼、PDF。

用法：python3 tools/check.py [代號 ...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"_template", "tools", ".git", ".github"}
ALLOWED_EXT = {".html", ".txt", ".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico"}
BAD_NAME = re.compile(r"(內部|核對|本機|adv|printable|build|\.pdf$|\.py$|\.xlsx?$|\.zip$|\.docx?$)", re.I)
TEMPLATE_LEFTOVER = ["小安", "小晴", "xiaoan", "全虛構", "示範案例"]
ID_NO = re.compile(r"\b[A-Z][12]\d{8}\b")          # 身分證字號
PHONE = re.compile(r"09\d{2}-?\d{3}-?\d{3}")
ADVISOR_PHONE = {"0918800852"}
# 公開網站（不含任何客戶資料，經負責人同意免通行碼）：只略過「必須加密」與「明文長度」兩項，其餘檢查照跑
PUBLIC_OK = {"story101"}  # 101夜傳承秘境：2026/10/10 起公開


def visible_text(html: str) -> str:
    t = re.sub(r"<script[\s\S]*?</script>", " ", html)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t)
    return re.sub(r"<[^>]+>", " ", t)


def check_dir(d: Path) -> list[str]:
    errs = []
    code = d.name
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", code):
        errs.append(f"子目錄名稱「{code}」請只用小寫英文代號")
    files = [p for p in d.rglob("*") if p.is_file()]
    for p in files:
        rel = p.relative_to(ROOT)
        if BAD_NAME.search(p.name):
            errs.append(f"{rel}：看起來是內部檔或原始檔，不可上傳")
        elif p.suffix.lower() not in ALLOWED_EXT:
            errs.append(f"{rel}：副檔名 {p.suffix} 不在允許清單")
    for p in files:
        if p.suffix.lower() != ".html":
            continue
        rel = p.relative_to(ROOT)
        s = p.read_text(encoding="utf-8", errors="ignore")
        if "noindex" not in s:
            errs.append(f"{rel}：缺少 noindex meta")
        if re.search(r"通行碼備註", s):
            errs.append(f"{rel}：含通行碼備註（本機版總目錄或內部版？）")
        if re.search(r"\b[a-z]{2,8}(adv|adm)\d{4}\b|\bcoach20\d\d[a-z]?\b", visible_text(s)):
            errs.append(f"{rel}：畫面出現疑似通行碼／管理者密碼")
        for w in TEMPLATE_LEFTOVER:
            if w in s:
                errs.append(f"{rel}：有範本殘留「{w}」")
        if ID_NO.search(s):
            errs.append(f"{rel}：疑似身分證字號")
        for m in PHONE.findall(s):
            if m.replace("-", "") not in ADVISOR_PHONE:
                errs.append(f"{rel}：疑似客戶電話 {m}")
        encrypted = "AES-GCM" in s
        is_report = p.name.endswith("-review.html") or encrypted
        if p.name.endswith("-review.html") and not encrypted:
            errs.append(f"{rel}：報告書內容未加密（找不到 AES-GCM），不可上傳")
        # 任何頁面的明文都不該多到像一份報告（加密頁的通行碼頁、目錄頁、方案頁都很短）
        limit = 400 if is_report else 1500
        if code not in PUBLIC_OK and len(visible_text(s).split()) > limit:
            errs.append(f"{rel}：明文內容偏多，請確認報告內容已加密")
    if code not in PUBLIC_OK and not any("AES-GCM" in p.read_text(encoding="utf-8", errors="ignore")
               for p in files if p.suffix.lower() == ".html"):
        errs.append(f"{code}/：找不到加密的報告書")
    return errs


def main() -> int:
    if not (ROOT / "robots.txt").exists():
        print("❌ 根目錄缺少 robots.txt")
        return 1
    targets = sys.argv[1:] or sorted(
        p.name for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith(".")
    )
    bad = 0
    for code in targets:
        d = ROOT / code
        if not d.is_dir():
            print(f"❌ {code}：子目錄不存在")
            bad += 1
            continue
        errs = check_dir(d)
        if errs:
            bad += 1
            print(f"❌ {code}")
            for e in errs:
                print(f"   - {e}")
        else:
            print(f"✅ {code}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
