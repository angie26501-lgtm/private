# -*- coding: utf-8 -*-
"""§14 顧問內部筆記＋§16 列印需管理者密碼＋§19 工作記錄＋§23 管理者專區
enc_notes(data, 管理者密碼) → 以 PBKDF2-SHA256 20 萬次＋AES-GCM 加密的 JSON（不含密碼或雜湊）
apply(pay, notes, admin_html, 管理者密碼) → 回傳已插入 📝 圖示、工具列按鈕、CSS、JS 的 payload
"""
import os, json, base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 200_000


def enc_notes(data, pw):
    b = lambda x: base64.b64encode(x).decode()
    s, i = os.urandom(16), os.urandom(12)
    k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=s, iterations=ITER).derive(pw.encode())
    c = AESGCM(k).encrypt(i, json.dumps(data, ensure_ascii=False).encode(), None)
    return {"s": b(s), "i": b(i), "n": ITER, "c": b(c)}


CSS = """<style>
/* ---- §14 顧問筆記／§16 列印／§23 管理者 ---- */
.advdot{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;border:1.5px dashed #c9b48a;background:#fffdf6;color:#8B6F4E;font-size:14px;cursor:pointer;opacity:.75;margin:6px 0;padding:0}
.advdot:hover{opacity:1}
.advnote{border:2px dashed #E9A92A;background:#FFFBEF;border-radius:12px;padding:10px 14px;margin:8px 0 12px;font-size:14px}
.advnote .an-h{font-weight:700;color:#8a5a00;margin-bottom:6px}
.advnote table.t{font-size:13px}
.advnote ul,.advnote ol{margin:4px 0;padding-left:20px}
.toolbar .advbtn{border-color:#b3261e;color:#b3261e}
#adv-menu{display:none;max-width:220px;font:inherit;font-size:13.5px;border:1.5px solid #b3261e;border-radius:20px;padding:5px 10px;background:#fff;color:#5E4A33}
body.advmode #adv-menu{display:inline-block}
body.advmode .vband.client{background:#b3261e}
#adv-modal{position:fixed;inset:0;background:rgba(30,24,16,.55);z-index:2147483100;display:none;align-items:center;justify-content:center;padding:16px}
#adv-modal.on{display:flex}
#adv-modal .am{background:#fff;border-top:8px solid #b3261e;border-radius:14px;padding:20px;width:min(360px,100%)}
#adv-modal h4{margin:0 0 4px;color:#5E4A33;font-size:17px}
#adv-modal .am-s{font-size:13px;color:#6f6a62;margin-bottom:8px}
#adv-modal input{width:100%;font-size:16px;padding:9px 10px;border:1.5px solid #d8cdb9;border-radius:8px}
#adv-modal .am-b{display:flex;gap:8px;margin-top:10px}
#adv-modal .am-b button{flex:1;border:0;border-radius:8px;padding:9px;font-size:15px;font-weight:700;cursor:pointer}
#adv-modal .am-ok{background:#b3261e;color:#fff}#adv-modal .am-no{background:#eee;color:#5E4A33}
#adv-modal .am-e{color:#b3261e;font-size:13.5px;min-height:18px;margin-top:6px}
.admzone{margin-top:16px;border-top:1px dashed #d8ccb6;padding-top:10px;text-align:center}
.admbtn{font:inherit;font-size:13px;border:1.5px solid #b3261e;color:#b3261e;background:#fff;border-radius:16px;padding:3px 12px;cursor:pointer}
#adm-box{display:none;text-align:left;margin-top:10px;border:2px solid #b3261e;border-radius:12px;padding:12px 14px;background:#FFF5F4}
#adm-box.on{display:block}
#adm-box h4{margin:0 0 8px;color:#b3261e}
@media (max-width:760px){#adv-menu{max-width:150px}.toolbar{flex-wrap:wrap;justify-content:flex-end}}
@media print{.advdot,.admzone{display:none!important}
 html.adm-print body>#app{display:block!important}
 html.adm-print body>#app .vband,html.adm-print body>#app .toolbar,html.adm-print body>#app .mtip{display:none!important}
 html.adm-print body:after{content:none!important;display:none!important}}
</style>"""

MODAL = """<div id="adv-modal" role="dialog" aria-modal="true"><div class="am"><h4 id="am-t">🔒 管理者密碼</h4><div class="am-s" id="am-s">顧問版與列印需管理者密碼。</div>
<input id="am-pw" type="password" autocomplete="off" placeholder="請輸入管理者密碼" onkeydown="if(event.key==='Enter'){event.preventDefault();__amOk()}if(event.key==='Escape')__amNo()">
<div class="am-b"><button class="am-no" type="button" onclick="__amNo()">取消</button><button class="am-ok" type="button" onclick="__amOk()">確定</button></div><div class="am-e" id="am-e"></div></div></div>"""

JS = r"""<script>
(function(){var ADV=__ADV__,DATA=null,cb=null,busy=false;
function b(s){var r=atob(s),u=new Uint8Array(r.length);for(var i=0;i<r.length;i++)u[i]=r.charCodeAt(i);return u}
async function dec(pw){var bk=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveBits']);
var bits=await crypto.subtle.deriveBits({name:'PBKDF2',salt:b(ADV.s),iterations:ADV.n,hash:'SHA-256'},bk,256);
var k=await crypto.subtle.importKey('raw',new Uint8Array(bits),{name:'AES-GCM'},false,['decrypt']);
var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b(ADV.i)},k,b(ADV.c));return JSON.parse(new TextDecoder().decode(pt))}
function $(i){return document.getElementById(i)}
function ask(t,s,f){if(DATA){f();return}cb=f;$('am-t').textContent=t;$('am-s').textContent=s;$('am-e').textContent='';$('am-pw').value='';$('adv-modal').classList.add('on');setTimeout(function(){$('am-pw').focus()},50)}
window.__amNo=function(){$('adv-modal').classList.remove('on');cb=null};
window.__amOk=async function(){if(busy)return;var pw=$('am-pw').value.replace(/\s+/g,'');if(!pw){$('am-e').textContent='請輸入管理者密碼。';return}
busy=true;$('am-e').textContent='驗證中…';try{DATA=await dec(pw);$('adv-modal').classList.remove('on');var f=cb;cb=null;f&&f()}catch(e){$('am-e').textContent='管理者密碼不正確。'}busy=false};
function on(){document.body.classList.add('advmode');
document.querySelectorAll('.advdot').forEach(function(d){var n=DATA.notes[d.dataset.n];if(!n)return;var x=document.createElement('div');x.className='advnote';x.id='an-'+d.dataset.n;
x.innerHTML='<div class="an-h">📝 顧問內部筆記・'+n.page+'｜'+n.title+'（客戶版不顯示）</div>'+n.html;d.style.display='none';d.parentNode.insertBefore(x,d.nextSibling)});
var m=$('adv-menu');m.innerHTML='<option value="">📝 顧問筆記選單</option>'+Object.keys(DATA.notes).map(function(k){var n=DATA.notes[k];return '<option value="an-'+k+'">'+n.page+'｜'+n.title+'</option>'}).join('');
$('adv-tg').textContent='👤 切回客戶版';var a=$('adm-box');if(a){a.innerHTML=DATA.admin;a.classList.add('on')}}
function off(){document.body.classList.remove('advmode');document.querySelectorAll('.advnote').forEach(function(x){x.remove()});document.querySelectorAll('.advdot').forEach(function(d){d.style.display=''});
$('adv-tg').textContent='📝 顧問版';var a=$('adm-box');if(a){a.innerHTML='';a.classList.remove('on')}}
window.__advToggle=function(){if(document.body.classList.contains('advmode')){off();return}ask('📝 顧問版','輸入管理者密碼後顯示顧問內部筆記（只在這次瀏覽有效）。',on)};
window.__advDot=function(){if(!document.body.classList.contains('advmode'))ask('📝 顧問筆記','此處為顧問內部筆記，需管理者密碼。',on)};
window.__advGo=function(v){if(!v)return;var el=$(v);if(el)el.scrollIntoView({behavior:'smooth',block:'center'});$('adv-menu').value=''};
window.__admOpen=function(){if(document.body.classList.contains('advmode')){var a=$('adm-box');a&&a.scrollIntoView({behavior:'smooth'});return}ask('🔒 管理者專區','限管理者使用，請輸入管理者密碼。',on)};
window.__advPrint=function(){ask('🔒 列印','列印／存 PDF 需管理者密碼。',function(){document.documentElement.classList.add('adm-print');document.body.classList.remove('compact');
document.querySelectorAll('details').forEach(function(d){d.open=true});setTimeout(function(){window.print()},200)})};
window.addEventListener('afterprint',function(){document.documentElement.classList.remove('adm-print')});
})();
</script>"""


def apply(pay, notes, anchors, admin_html, pw):
    """anchors: [(note_id, 插入位置字串, 'before'|'after')]"""
    for nid, key, where in anchors:
        assert pay.count(key) == 1, (nid, key)
        dot = f'<button type="button" class="advdot no-print" data-n="{nid}" title="顧問筆記（限顧問）" aria-label="顧問筆記（限顧問）" onclick="__advDot()">📝</button>'
        pay = pay.replace(key, dot + key if where == 'before' else key + dot)
    tb_old = '<div class="toolbar no-print"><button onclick="__logout()">登出</button></div>'
    assert tb_old in pay
    tb_new = ('<div class="toolbar no-print"><select id="adv-menu" onchange="__advGo(this.value)" aria-label="顧問筆記選單"></select>'
              '<button class="advbtn" id="adv-tg" onclick="__advToggle()">📝 顧問版</button>'
              '<button onclick="__advPrint()">🔒 列印</button><button onclick="__logout()">登出</button></div>')
    pay = pay.replace(tb_old, tb_new)
    # 管理者專區按鈕：放最後一頁最下方
    end = '</section></main></div>'
    assert pay.count(end) == 1
    pay = pay.replace(end, '<div class="admzone no-print"><button class="admbtn" type="button" onclick="__admOpen()">🔒 管理者</button><div id="adm-box"></div></div>' + end)
    enc = enc_notes({"notes": notes, "admin": admin_html}, pw)
    pay = CSS + pay + MODAL + JS.replace('__ADV__', json.dumps(enc))
    return pay


def strip(pay):
    """§35 底稿用：把已套過 apply() 的線上報告內容還原成無筆記層的 payload（之後再用新案的筆記與管理者密碼重新 apply）。"""
    import re
    if pay.startswith(CSS):
        pay = pay[len(CSS):]
    i = pay.rfind(MODAL)
    if i > 0:
        pay = pay[:i]
    pay = re.sub(r'<button type="button" class="advdot no-print"[^>]*>📝</button>', '', pay)
    pay = pay.replace('<div class="admzone no-print"><button class="admbtn" type="button" onclick="__admOpen()">🔒 管理者</button><div id="adm-box"></div></div>', '')
    tb_new = ('<div class="toolbar no-print"><select id="adv-menu" onchange="__advGo(this.value)" aria-label="顧問筆記選單"></select>'
              '<button class="advbtn" id="adv-tg" onclick="__advToggle()">📝 顧問版</button>'
              '<button onclick="__advPrint()">🔒 列印</button><button onclick="__logout()">登出</button></div>')
    pay = pay.replace(tb_new, '<div class="toolbar no-print"><button onclick="__logout()">登出</button></div>')
    for k in ['advdot', 'adm-box', '__ADV__', 'adv-modal']:
        assert k not in pay, ('筆記層未清乾淨', k)
    return pay
