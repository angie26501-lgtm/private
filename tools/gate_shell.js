(function(){var E=__PAYLOAD__,K="__KEY__";
function b64(s){var r=atob(s),u=new Uint8Array(r.length);for(var i=0;i<r.length;i++)u[i]=r.charCodeAt(i);return u}
function bs(u){var s='';for(var i=0;i<u.length;i++)s+=String.fromCharCode(u[i]);return btoa(s)}
function err(t){var e=document.getElementById('gerr');if(e)e.textContent=t}
async function dec(raw){var k=await crypto.subtle.importKey('raw',raw,{name:'AES-GCM'},false,['decrypt']);
var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(E.i)},k,b64(E.c));return new TextDecoder().decode(pt)}
function show(html){var t=document.createElement('div');t.innerHTML=html;var sc=[].slice.call(t.querySelectorAll('script'));sc.forEach(function(s){s.remove()});
var gate=document.getElementById('gate');while(t.firstChild)document.body.appendChild(t.firstChild);
sc.forEach(function(s){var n=document.createElement('script');n.textContent=s.textContent;document.body.appendChild(n)});
gate.style.display='none';var app=document.getElementById('app');app.hidden=false;app.style.display='';
try{if(window.__onUnlock)window.__onUnlock('')}catch(e){console.error(e)}}
async function tryRaw(raw){var h=await dec(raw);show(h)}
function ready(fn){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fn);else setTimeout(fn,0)}
if(!(window.crypto&&crypto.subtle)){ready(function(){err('此瀏覽器不支援安全解密，請改用 Safari／Chrome 最新版開啟。')})}
ready(function(){try{var s=JSON.parse(localStorage.getItem(K)||'null');if(s&&s.k&&s.exp>Date.now()){tryRaw(b64(s.k)).catch(function(){try{localStorage.removeItem(K)}catch(e){}})}}catch(e){}});
var busy=false;
window.__gTry=async function(){if(busy)return;var cs=document.getElementById('gcons');if(cs&&!cs.checked){err('請先閱讀並勾選同意「個人資料保護告知」。');return}
var pw=document.getElementById('gpw').value.replace(/\s+/g,'');if(!pw){err('請輸入通行碼。');return}
busy=true;err('驗證中…');try{var bk=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveBits']);
var bits=await crypto.subtle.deriveBits({name:'PBKDF2',salt:b64(E.s),iterations:E.n,hash:'SHA-256'},bk,256);var raw=new Uint8Array(bits);
var h=await dec(raw);err('');try{if(document.getElementById('grem').checked)localStorage.setItem(K,JSON.stringify({k:bs(raw),exp:Date.now()+30*864e5}))}catch(e){}
show(h)}catch(e){err('通行碼不正確，請再試一次。')}busy=false};
window.__logout=function(){try{localStorage.removeItem(K)}catch(e){}location.reload()};
})();