#!/usr/bin/env python3
"""§30-2 多份報告時的「健診分析規劃書（PDF）」附件頁（參考 WISH 附件七）。

只用「客戶通行碼」一組加密（教練碼打不開，符合 §30 教練看不到雲華陀網址）；網址只存在加密內容裡。
用法：python3 tools/cloud_pdf_page.py 輸出.html --code xiaoan --name 小安 --date 115/10/07 --url "<雲華陀網址>" --pw 客戶碼 [--label 附件七]
"""
import argparse, subprocess, sys, tempfile, html
from pathlib import Path
HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("dst"); ap.add_argument("--code", required=True); ap.add_argument("--name", required=True)
ap.add_argument("--date", required=True); ap.add_argument("--url", required=True); ap.add_argument("--pw", required=True)
ap.add_argument("--label", default="附件")
a = ap.parse_args()
title = f"{a.label}：健診分析規劃書（PDF）"
gate = (HERE / "gate_page.html").read_text(encoding="utf-8").replace("__TITLE__", html.escape(title)).replace("__NAME__", html.escape(a.name))
card = f"""<div id="app" hidden><style>.pc{{max-width:640px;margin:28px auto;background:#fff;border-top:8px solid #FFC850;border-radius:14px;padding:24px 20px;box-shadow:0 6px 24px rgba(0,0,0,.12);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;line-height:1.7}}
.pc h1{{color:#A3182A;font-size:21px;margin:0 0 4px}}.pc .sub{{color:#8B6F4E;font-size:14px;margin-bottom:14px}}
.pc a.dl{{display:block;text-align:center;background:#1E6FB8;color:#fff;text-decoration:none;font-weight:800;font-size:17px;border-radius:10px;padding:14px;margin:14px 0}}
.pc ul{{padding-left:20px;font-size:14px;margin:8px 0}}.pc li{{margin:4px 0}}.pc .back{{font-size:13.5px;color:#1E6FB8}}
.pc .sig{{border-top:1px solid #eee;margin-top:16px;padding-top:10px;font-size:12.5px;color:#6f6a62;line-height:1.7}}
@media (max-width:680px){{.pc{{margin:14px 12px}}}}</style>
<div class="pc"><h1>📄 {html.escape(title)}</h1><div class="sub">{html.escape(a.name)} 專屬・保單健診系統產出的原始報告（製表 {html.escape(a.date)}）</div>
<a class="dl" href="{html.escape(a.url)}" target="_blank" rel="noopener noreferrer">打開／下載 健診分析規劃書 PDF ↗</a>
<ul><li>這份是保單健診系統直接產出的原始報告，「保障現況分析」就是依這份整理。</li>
<li>點上方按鈕會在新分頁開啟，可直接下載或列印。內容含個人資料，請勿轉傳。</li>
<li>建議用電腦或平板開啟；若在 LINE 裡打不開，請改用 Safari／Chrome。</li>
<li>連結如果無法開啟，請告訴芸琪，會重新提供。</li></ul>
<a class="back" href="index.html">← 回報告總目錄</a>
<div class="sig">顧問　陳芸琪 Angie Chen<br>財顧芸｜家族傳承生活顧問・人生財務設計顧問｜AI 賦能應用<br>RFC 國際認證財務顧問師｜RFP 美國註冊財務策劃師｜RFA 退休理財規劃顧問</div></div></div>"""
head = f"""<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">
<title>財顧芸｜{html.escape(title)}</title><style>body{{margin:0;background:#efe9df}}</style></head><body>"""
with tempfile.TemporaryDirectory() as d:
    src = Path(d) / "plain.html"
    src.write_text(head + gate + card + "</body></html>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "multi_enc.py"), str(src), a.dst, a.pw, "--key", a.code + "-pdf", "--log", f"健診PDF｜{a.code}"])
    sys.exit(r.returncode)
