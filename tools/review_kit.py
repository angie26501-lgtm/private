# -*- coding: utf-8 -*-
"""保障現況分析（保戶版）產生器共用元件（母指令 v3.6）。

用法（build.py 內）：
    import sys; sys.path.insert(0, '/home/claude/private/tools')
    from review_kit import *
以「最新上架案」解密後的內容為底稿（§0 底稿選擇），只替換客戶資料區塊：
- donut()/card()：P3 與家人頁四大支柱卡（計算式、80 歲後說明收合）
- rows()/tbody_replace()：P4／家人明細主表＋附約展開（不列給付重點）；季繳／月繳保單在 dict 加 pm='季繳'
- tour_resize()：§31 導覽視窗調整大小
- cloud_link()：§30 雲華陀連結，回傳 (payload, ck)；ck 交給 multi_enc.py --ck
"""
import json, os, re, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def tg(x):
    t = {'A': '保單文件載明', 'B': '依A級加總或到期年齡推算', 'C': '規劃參考值', 'D': '待補充'}[x]
    return f'<span class="tg t{x}" title="{t}">{x}</span>'


def fmt(v):
    return f'{v:,}'


def donut(color, pct, sub, track='#eee', text=None):
    dash = 289.0 * min(pct, 100) / 100
    arc = '' if pct <= 0 else f'<circle cx="60" cy="60" r="46" fill="none" stroke="{color}" stroke-width="13" stroke-dasharray="{dash:.1f} 289.0" transform="rotate(-90 60 60)" stroke-linecap="butt"/>'
    return (f'<svg viewBox="0 0 120 120" class="donut"><circle cx="60" cy="60" r="46" fill="none" stroke="{track}" stroke-width="13"/>{arc}'
            f'<text x="60" y="60" text-anchor="middle" font-size="22" font-weight="700" fill="{color}">{text or str(pct) + "%"}</text>'
            f'<text x="60" y="80" text-anchor="middle" font-size="10.5" fill="#6f6a62">{sub}</text></svg>')


def card(cid, color, title, dn, fm, items, ftag, fname, fpct, fsum, flist):
    lis = ''.join(f'<li><span>{a}</span><b>{b}</b></li>' for a, b in items)
    fl = ''.join(f'<li>{x}</li>' for x in flist)
    pct = f'<b class="pf-pct">{fpct}</b>' if fpct else ''
    return (f'<div class="pc" id="{cid}" style="--pc:{color}"><div class="pctop">{dn}<div><h4>{title}</h4>'
            f'<details class="dd fmdd"><summary>計算式</summary><div class="fm">{fm}</div></details></div></div>'
            f'<ul class="pl">{lis}</ul><div class="pf"><div class="pf-h"><span class="pf-tag">{ftag}</span><span class="pf-n">{fname}</span>{pct}</div>'
            f'<details class="dd"><summary>{fsum}</summary><ul class="pf-l">{fl}</ul></details></div></div>')


def rows(pols):
    out = ''
    for p in pols:
        k = f"pr{p['n']}"
        st = ''.join(f'<div class="stl"><span class="stk">{a}</span>{b}</div>' for a, b in p['st'])
        sub = ''.join(f'<tr><td>{a}</td><td class="pname">{b}</td><td>{c}</td><td>{d}</td><td>{e}</td><td class="r">{fmt(f)}</td></tr>'
                      for a, b, c, d, e, f in p['riders'])
        out += (f'<tr><td class="c"><button class="pm" data-t="{k}" aria-label="展開附約">＋</button></td><td class="c">{p["n"]}</td>'
                f'<td>{p["co"]}</td><td class="mh">{p["no"]}</td><td class="mh">{p["ph"]}</td><td class="mh">{p["d"]}</td>'
                f'<td class="mh c">{p["age"]}</td><td class="mh">{p.get("pm", "年繳")}</td><td class="mh">{p["day"]}</td><td class="r"><b>{fmt(p["fee"])}</b></td>'
                f'<td><span class="stp">正常</span><details class="dd stdd"><summary>說明</summary>{st}</details></td></tr>'
                f'<tr class="xrow" data-x="{k}"><td colspan="11" class="sub"><table class="t2"><thead><tr><th>類型</th><th>商品名稱</th>'
                f'<th>繳費年期</th><th>保障年期</th><th>保額</th><th>保費</th></tr></thead><tbody>{sub}</tbody></table></td></tr>')
    return out


def tbody_replace(src, table_id, new_rows):
    a = src.find(f'id="{table_id}"')
    a = src.find('<tbody>', a) + len('<tbody>')
    # 找主表 tbody 結尾（主表內有子表 tbody，用深度計算）
    depth, i = 1, a
    while depth:
        m = re.compile(r'<tbody>|</tbody>').search(src, i)
        depth += 1 if m.group(0) == '<tbody>' else -1
        i = m.end()
    return src[:a] + new_rows + src[i - len('</tbody>'):]





A, B, C, D = tg('A'), tg('B'), tg('C'), tg('D')
WARN = '<div class="warn">⚠️ 本頁保障內容僅供保單健診參考，實際保障以各保險公司保單條款為主，如有疑問請洽財顧芸。</div>'


def tour_resize(pay):
    """§31 導覽視窗：四邊四角拖曳調整大小（右下 ◢）、記住大小、↺ 重設；展開收合時金框即時重算。回傳新 payload。"""
    TK_OLD_BUILD = "document.body.appendChild(E.pop);\nE.pop.querySelector('.tk-x').onclick=close;E.pop.querySelector('.tk-re').onclick=function(){userPos=null;place()};"
    TK_NEW_BUILD = ("document.body.appendChild(E.pop);rzPop();\n"
        "E.pop.querySelector('.tk-x').onclick=close;E.pop.querySelector('.tk-re').onclick=function(){userPos=null;E.pop.style.width='';E.pop.style.height='';ls(C.key+'-size','');place(st?(st.list[st.i].s?document.querySelector(st.list[st.i].s):null):null)};")
    assert pay.count(TK_OLD_BUILD) == 1
    pay = pay.replace(TK_OLD_BUILD, TK_NEW_BUILD)
    RZ = r"""function rzPop(){var P=E.pop,M=innerWidth<=760?240:300,MH=150;
    ['n','s','e','w','ne','nw','se','sw'].forEach(function(d){var g=document.createElement('div');g.className='tk-rz tk-rz-'+d;g.title='拖曳調整視窗大小';P.appendChild(g);
    var sx,sy,r0,on=false;
    g.addEventListener('pointerdown',function(e){if(P.classList.contains('min'))return;on=true;g.setPointerCapture(e.pointerId);sx=e.clientX;sy=e.clientY;r0=P.getBoundingClientRect();e.preventDefault();e.stopPropagation()});
    g.addEventListener('pointermove',function(e){if(!on)return;var dx=e.clientX-sx,dy=e.clientY-sy,L=r0.left,T=r0.top,W=r0.width,H=r0.height;
    if(d.indexOf('e')>=0)W=Math.min(Math.max(M,r0.width+dx),innerWidth-r0.left-4);
    if(d.indexOf('s')>=0)H=Math.min(Math.max(MH,r0.height+dy),innerHeight-r0.top-4);
    if(d.indexOf('w')>=0){W=Math.max(M,r0.width-dx);L=r0.right-W;if(L<4){L=4;W=r0.right-4}}
    if(d.indexOf('n')>=0){H=Math.max(MH,r0.height-dy);T=r0.bottom-H;if(T<4){T=4;H=r0.bottom-4}}
    P.style.width=W+'px';P.style.height=H+'px';P.style.maxWidth='none';P.style.left=L+'px';P.style.top=T+'px';userPos=[L,T]});
    g.addEventListener('pointerup',function(){if(!on)return;on=false;var r=P.getBoundingClientRect();ls(C.key+'-size',JSON.stringify([r.width,r.height]))})});
    try{var z=JSON.parse(ls(C.key+'-size')||'null');if(z&&z[0]){P.style.width=Math.min(z[0],innerWidth-8)+'px';P.style.height=Math.min(z[1],innerHeight-8)+'px';P.style.maxWidth='none'}}catch(e){}}
    function hlNow(){if(!st)return;var s=st.list[st.i],n=s&&s.s?document.querySelector(s.s):null;if(!n)return;var r=n.getBoundingClientRect();
    E.hl.style.left=(r.left+scrollX-6)+'px';E.hl.style.top=(r.top+scrollY-6)+'px';E.hl.style.width=(r.width+12)+'px';E.hl.style.height=(r.height+12)+'px'}
    document.addEventListener('toggle',function(){setTimeout(hlNow,30)},true);
    document.addEventListener('click',function(){if(st)setTimeout(hlNow,60)},true);
    """
    anchor = "function dragPop(){"
    assert pay.count(anchor) == 1
    pay = pay.replace(anchor, RZ + anchor)
    # 拖曳標題列時保留目前大小
    pay = pay.replace("function clampP(x,y){var r=E.pop.getBoundingClientRect();return [Math.max(4,Math.min(x,innerWidth-r.width-4)),Math.max(4,Math.min(y,innerHeight-40))]}",
                      "function clampP(x,y){var r=E.pop.getBoundingClientRect();return [Math.max(4,Math.min(x,innerWidth-r.width-4)),Math.max(4,Math.min(y,innerHeight-40))]}")
    TK_CSS = """<style>/* ---- v1.2 導覽視窗調整大小 ---- */
    #tk-pop{resize:none!important}
    #tk-pop .tk-rz{position:absolute;z-index:3;touch-action:none}
    #tk-pop .tk-rz-n,#tk-pop .tk-rz-s{left:12px;right:12px;height:8px;cursor:ns-resize}
    #tk-pop .tk-rz-n{top:0}#tk-pop .tk-rz-s{bottom:0}
    #tk-pop .tk-rz-e,#tk-pop .tk-rz-w{top:12px;bottom:12px;width:8px;cursor:ew-resize}
    #tk-pop .tk-rz-e{right:0}#tk-pop .tk-rz-w{left:0}
    #tk-pop .tk-rz-ne,#tk-pop .tk-rz-nw,#tk-pop .tk-rz-se,#tk-pop .tk-rz-sw{width:16px;height:16px}
    #tk-pop .tk-rz-ne{top:0;right:0;cursor:nesw-resize}#tk-pop .tk-rz-nw{top:0;left:0;cursor:nwse-resize}
    #tk-pop .tk-rz-sw{bottom:0;left:0;cursor:nesw-resize}
    #tk-pop .tk-rz-se{bottom:0;right:0;width:20px;height:20px;cursor:nwse-resize;background:linear-gradient(135deg,transparent 0 45%,#c9a65a 45% 52%,transparent 52% 64%,#c9a65a 64% 71%,transparent 71% 83%,#c9a65a 83% 90%,transparent 90%)}
    #tk-pop.min .tk-rz{display:none}
    #tk-pop .tk-head{cursor:move}
    #tk-pop .tk-foot{padding-right:24px}
    </style>"""
    pay = TK_CSS + pay
    for k in ['rzPop', 'hlNow', 'tk-rz-se']:
        assert k in pay, k


    return pay


def cloud_link(pay, url, date):
    """§30：把雲華陀網址用客戶專屬金鑰 CK 加密後放進 P4 框（#cloud-p4）；教練 slot 不含 CK 就看不到。
    底稿需已有 <div class="note cream" id="cloud-p4" hidden> 與 initCloud()。回傳 (pay, ck)。"""
    ck, iv = os.urandom(32), os.urandom(12)
    L = {"i": base64.b64encode(iv).decode(), "c": base64.b64encode(AESGCM(ck).encrypt(iv, url.encode(), None)).decode()}
    pay = re.sub(r'（雲華陀，[^）]*）', f'（雲華陀，{date}）', pay, count=1)
    i0 = pay.find('function initCloud(){'); assert i0 > 0, '底稿沒有 initCloud'
    i1 = pay.find('var L=', i0) + len('var L='); i2 = pay.find('};', i1) + 1
    return pay[:i1] + json.dumps(L) + pay[i2:], ck


def remove_cloud(pay):
    """本案沒有雲華陀連結時：移除 P4 框並讓 initCloud 變空函式。"""
    c0 = pay.find('<div class="note cream" id="cloud-p4"')
    if c0 >= 0:
        c1 = pay.find('</div></div>', c0) + len('</div></div>')
        pay = pay[:c0] + pay[c1:]
    i0 = pay.find('function initCloud(){'); i1 = pay.find('window.__onUnlock', i0)
    return pay[:i0] + 'function initCloud(){}\n' + pay[i1:]
