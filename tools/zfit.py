#!/usr/bin/env python3
"""§13 列印縮放量測：解鎖加密報告 → 列印模式展開全部收合 → 逐頁找出 A4 一頁放得下的最大 --z（0.01 一階，下限 0.65）。

用法：python3 tools/zfit.py 加密報告.html 客戶通行碼 [--pdf 輸出.pdf]
輸出：{"p1": 0.89, ...}（JSON），把每頁再減 0.01 寫進 build.py 的 ZF 表後重建；--pdf 另輸出 A4 PDF 供檢查頁數＝頁面數。
"""
import asyncio, json, sys, argparse
from pathlib import Path
from playwright.async_api import async_playwright


async def main(a):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context(viewport={'width': 1280, 'height': 900})).new_page()
        await pg.route('**/formResponse', lambda r: r.fulfill(status=200, body=''))
        await pg.goto(Path(a.src).resolve().as_uri()); await pg.fill('#gpw', a.pw)
        for c in await pg.query_selector_all('#gate input[type=checkbox]'):
            if not await c.is_checked(): await c.check()
        await pg.evaluate("__gTry()"); await pg.wait_for_timeout(2500)
        await pg.evaluate("try{TourKit.close()}catch(e){}")
        await pg.evaluate("document.documentElement.classList.add('adm-print');document.body.classList.remove('compact');document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.emulate_media(media='print')
        res, low = {}, []
        for sid in await pg.evaluate("[...document.querySelectorAll('section.page')].map(s=>s.id)"):
            z = 1.0
            while True:
                await pg.evaluate(f"document.getElementById('{sid}').style.setProperty('--z','{z}')")
                over = await pg.evaluate(f"(()=>{{var s=document.getElementById('{sid}');return s.scrollHeight-s.clientHeight}})()")
                if over <= 1 or z <= 0.65: break
                z = round(z - 0.01, 2)
            res[sid] = z
            if z <= 0.65 and over > 1: low.append(sid)
        print(json.dumps(res))
        if low: print('⚠️ 縮到 0.65 仍放不下，請拆頁：', low)
        if a.pdf:
            await pg.pdf(path=a.pdf, format='A4', print_background=True, margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
        await b.close()

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('pw'); ap.add_argument('--pdf')
asyncio.run(main(ap.parse_args()))
