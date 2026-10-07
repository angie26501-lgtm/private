#!/usr/bin/env python3
"""網路版總目錄「觀看流程版」產生器（母指令 §7-1，參考 WISH 定稿 2026/10/07）。

一案有 2 份以上報告（現況檢視＋附件、或保障現況分析＋健診 PDF 頁）時，網路版 index.html 用這個版型：
① 📖 怎麼看這幾份報告（5 點）② 一句話重點表（報告／一句話重點／先看這裡）③ 🧭 觀看流程 SOP 軸（步驟、目的、時間、打開按鈕；選讀灰點、最後一步藍點）
④ 🔑 同一組通行碼＋裝置提醒＋AI 賦能 ⑤ 📁 全部報告（相對連結）。不寫任何通行碼、不寫數字以外的個資。

用法：python3 tools/index_flow.py 設定.json 輸出/index.html
設定.json 範例見 _template/index-flow/config-example.json
"""
import json, sys, html

CSS = 'body{margin:0;background:#efe9df;font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;color:#2d2a26;line-height:1.7}\n.band{background:#2e8b57;color:#fff;padding:8px 16px;font-size:14px}\n.demo{background:#fff3cd;color:#7a5a00;border-bottom:1px solid #f1d58a;font-size:13px;text-align:center;padding:5px 10px}\n.card{max-width:760px;margin:24px auto;background:#fff;border-top:8px solid #FFC850;border-radius:14px;padding:24px 20px;box-shadow:0 6px 24px rgba(0,0,0,.12)}\nh1{color:#A3182A;font-size:22px;margin:0 0 4px}.sub{color:#8B6F4E;font-size:14px;margin-bottom:16px}\na.it{display:block;background:#FFF7E6;border-left:5px solid #E9A92A;border-radius:8px;padding:12px 14px;color:#1E6FB8;text-decoration:none;font-weight:700;margin:10px 0}\na.it span{display:block;color:#6f6a62;font-weight:400;font-size:13.5px}.f{font-size:12.5px;color:#6f6a62;margin-top:18px}\n@media (max-width:680px){.card{margin:14px 12px}}.sop{position:relative;margin:8px 0 0;padding-left:34px}\n.sop:before{content:"";position:absolute;left:15px;top:8px;bottom:8px;width:3px;background:linear-gradient(#E9A92A,#1E6FB8);border-radius:3px}\n.sp{position:relative;margin:0 0 12px;background:#fff;border:1px solid #e5dccb;border-radius:10px;padding:10px 13px}\n.sp .no{position:absolute;left:-34px;top:9px;width:30px;height:30px;border-radius:50%;background:#E9A92A;color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:15px;box-shadow:0 0 0 3px #fff}\n.sp.last .no{background:#1E6FB8}.sp.opt .no{background:#b9ad98}\n.sp h3{margin:0;font-size:15.5px;color:#5E4A33}.sp .goal{display:inline-block;font-size:12px;font-weight:700;color:#A3182A;background:#FFF0EC;border-radius:999px;padding:1px 9px;margin:3px 6px 3px 0}\n.sp .tm{display:inline-block;font-size:12px;color:#6f6a62;background:#f3efe7;border-radius:999px;padding:1px 9px}\n.sp p{margin:4px 0 6px;font-size:13.5px;color:#4a453e;line-height:1.7}\n.sp a.go{display:inline-block;font-size:13px;font-weight:700;color:#fff;background:#1E6FB8;border-radius:8px;padding:5px 12px;text-decoration:none}\n.tips{background:#FFF7E6;border-left:5px solid #E9A92A;border-radius:8px;padding:9px 13px;font-size:13px;line-height:1.8;margin-top:6px}\n.howto{background:#fff;border:1px solid #e5dccb;border-left:5px solid #1E6FB8;border-radius:10px;padding:10px 14px;margin:6px 0 10px}\n.howto h3{margin:0 0 4px;font-size:15.5px;color:#1E6FB8}.howto ol{margin:4px 0 0;padding-left:20px}.howto li{font-size:13.5px;margin:4px 0;line-height:1.75}\n.kt{width:100%;border-collapse:collapse;font-size:13.5px;margin:4px 0 10px;background:#fff}.kt th{background:#5E4A33;color:#fff;text-align:left;padding:6px 8px;font-weight:600}\n.kt td{border-bottom:1px solid #eee;padding:6px 8px;vertical-align:top}.kt td:first-child{font-weight:700;white-space:nowrap;color:#5E4A33}\n.lg span{display:inline-block;font-size:12px;font-weight:700;color:#fff;border-radius:4px;padding:0 7px;margin:0 2px}\n@media (max-width:680px){.kt td:first-child{white-space:normal}}h2.t{font-size:17px;color:#5E4A33;margin:18px 0 4px}'

def esc(t): return html.escape(str(t), quote=False)

def build(c):
    base = c["base_url"].rstrip("/") + "/"
    rows = "".join(f"<tr><td>{esc(r['icon'])} {esc(r['short'])}</td><td>{esc(r['one_line'])}</td><td>{esc(r['look'])}</td></tr>" for r in c["reports"])
    steps = ""
    for i, st in enumerate(c["steps"], 1):
        cls = "sp" + (" opt" if st.get("optional") else "") + (" last" if i == len(c["steps"]) else "")
        tm = f'<span class="tm">⏱ {esc(st["time"])}</span>' if st.get("time") else ""
        go = ""
        if st.get("file"):
            href = st["file"] if st["file"].startswith("http") else base + st["file"]
            go = f'<a class="go" href="{href}" target="_blank" rel="noopener">{esc(st.get("button", "打開 ↗"))}</a>'
        steps += f'<div class="{cls}"><div class="no">{i}</div><h3>{esc(st["title"])}</h3><span class="goal">{esc(st["goal"])}</span>{tm}<p>{esc(st["desc"])}</p>{go}</div>'
    alls = "".join(f'<a class="it" href="{esc(r["file"])}">{esc(r["icon"])} {esc(r["title"])}<span>{esc(r["note"])}</span></a>' for r in c["reports"])
    n = len(c["reports"])
    howto = "".join(f"<li>{h}</li>" for h in c.get("howto", [
        f"<b>先看現況，再看規劃，最後看明細。</b>{esc(c['reports'][0]['title'])}是主報告；其他是延伸參考，依編號往下看即可。",
        "<b>每份先看「一句話重點」</b>（下表），有興趣再看細節；不用一次全部看完。",
        "<b>看數字旁的標籤</b>：<span class='lg'><span style='background:#2e8b57'>A 文件載明</span><span style='background:#1E6FB8'>B 加總推算</span><span style='background:#E08A1E'>C 參考值</span><span style='background:#9a9a9a'>D 待補充</span></span>，推算與參考值不是保證數值。",
        "<b>有疑問或和您認知不同的地方，先記下來</b>，看完一次傳給芸琪。",
        f"全部看完約 {esc(c.get('total_time', '30 分鐘'))}，可以分幾次看；勾選「記住 30 天」就不用每次輸入通行碼。"]))
    return f'''<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">
<title>{esc(c["name"])}｜報告總目錄</title>
<style>{CSS}h2.t{{font-size:17px;color:#5E4A33;margin:18px 0 8px}}</style></head>
<body><div class="band">客戶版｜{esc(c["name"])}｜總目錄　{esc(c["date"])}・觀看流程版</div>
<div class="card"><h1>{esc(c["name"])}　專屬</h1><div class="sub">財顧芸｜馥芸財富學苑｜幸福財務領航員</div>
<div class="howto"><h3>📖 怎麼看這幾份報告</h3><ol>{howto}</ol></div>
<table class="kt"><tr><th>報告</th><th>一句話重點</th><th>先看這裡</th></tr>{rows}</table>
<h2 class="t">🧭 報告書觀看流程（照順序看，約 {esc(c.get("total_time", "30 分鐘"))}）</h2><div class="sop">{steps}</div>
<div class="tips">🔑 {n} 份報告用<b>同一組通行碼</b>；勾選「記住 30 天」下次免再輸入。💻 建議用電腦或平板開啟；在 LINE 裡打開若無法記住登入，請改用 Safari／Chrome。🤖 本規劃透過 AI 賦能應用，資料整理與試算經顧問逐項核對。</div>
<h2 class="t">📁 全部報告</h2>
{alls}
<div class="f">本網頁以化名及遮蔽方式呈現。建議將本頁加入書籤作為入口。</div></div></body></html>
'''

if __name__ == "__main__":
    c = json.load(open(sys.argv[1], encoding="utf-8"))
    open(sys.argv[2], "w", encoding="utf-8").write(build(c))
    print("✅", sys.argv[2])
