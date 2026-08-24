from pathlib import Path
import base64,re,io
from PIL import Image

root=Path('.')
idx=root/'index.html'
css=root/'v66-premium-unified.css'
ui=root/'v66-ui.js'
shell=root/'v66-home-shell-v662.js'
admin=root/'admin-dashboard.html'
sw=root/'sw.js'

# 1) Convert the approved portrait to a browser-safe PNG and embed it directly.
raw=(root/'swamiji-portrait.jpg').read_bytes()
im=Image.open(io.BytesIO(raw)).convert('RGBA')
out=io.BytesIO(); im.save(out,format='PNG',optimize=True)
png=out.getvalue(); b64=base64.b64encode(png).decode('ascii')
(root/'swamiji-portrait.png').write_bytes(png)
html=idx.read_text(encoding='utf-8')
html=re.sub(r'(<img class="swamijiHomePortrait"\s+src=")[^"]+("\s+alt="Swami Vivekananda line portrait")',r'\1data:image/png;base64,'+b64+r'\2',html,count=1)
html=re.sub(r'(<div class="vkvLoaderPortrait"><img src=")[^"]+("[^>]*>)',r'\1data:image/png;base64,'+b64+r'\2',html,count=1)
# cache-bust the visual assets touched in this pass
html=html.replace('v66-ui.js?v=66.2-sync-1','v66-ui.js?v=66.2-interface-1')
html=html.replace('v66-premium-unified.css?v=66.2-premium-1','v66-premium-unified.css?v=66.2-interface-1')
html=html.replace('v66-home-shell-v662.js?v=66.2-sync-1','v66-home-shell-v662.js?v=66.2-interface-1')
idx.write_text(html,encoding='utf-8')

# 2) Remove injected school ribbons. The static hero/card is the sole visual authority.
u=ui.read_text(encoding='utf-8')
u=u.replace("    addSchoolRibbon(file);","    // Phase-1: no injected school ribbon; static page layout is authoritative.")
ui.write_text(u,encoding='utf-8')

s=shell.read_text(encoding='utf-8')
s=s.replace("  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addRibbon);else addRibbon();","  // Phase-1: keep tile feedback only; do not inject an extra school ribbon.")
shell.write_text(s,encoding='utf-8')

# 3) Admin dashboard: remove the older competing polish layer and keep one static hero.
a=admin.read_text(encoding='utf-8')
a=a.replace('<link rel="stylesheet" href="v66-admin-reference-polish.css?v=66.2-adminref-1">\n','')
a=a.replace('v66-ui.js?v=66.0-school-identity-1','v66-ui.js?v=66.2-interface-1')
a=a.replace('v66-premium-unified.css?v=66.2-premium-1','v66-premium-unified.css?v=66.2-interface-1')
admin.write_text(a,encoding='utf-8')

# 4) Lock the v60 premium proportions and prevent any legacy duplicate motif from displaying.
c=css.read_text(encoding='utf-8')
marker='/* PHASE1 INTERFACE AUTHORITY 2026-08-24 */'
if marker in c:
    c=c.split(marker)[0].rstrip()+"\n"
c += '''\n/* PHASE1 INTERFACE AUTHORITY 2026-08-24 */
/* Homepage: plain premium navy header, tight crest badge, subtle portrait. */
body:not(.adminDashboardPage)>header::before{display:none!important}
body:not(.adminDashboardPage) header .logo{
  width:70px!important;height:82px!important;flex:0 0 70px!important;
  object-fit:contain!important;clip-path:none!important;
  padding:2px!important;background:#fff!important;
  border-radius:35px!important;box-shadow:0 1px 4px rgba(0,0,0,.09)!important;
}
header .swamijiHomePortrait{display:block!important;object-fit:contain!important;opacity:.92!important;margin-left:auto!important}
@media(min-width:701px){header .swamijiHomePortrait{width:108px!important;height:108px!important}}
@media(max-width:700px){
  body:not(.adminDashboardPage) header .logo{width:54px!important;height:64px!important;flex-basis:54px!important;padding:2px!important;border-radius:27px!important}
  header .swamijiHomePortrait{width:68px!important;height:68px!important}
}
/* Never show legacy injected school ribbons on home/admin. */
body[data-page="index"] .v66-school-ribbon,body[data-page="index"] .v662-school-ribbon,
body.adminDashboardPage .v66-school-ribbon,body.adminDashboardPage .v662-school-ribbon,body.adminDashboardPage .v66-admin-reference-ribbon{display:none!important}
/* Admin: exactly one compact static workspace hero with one restrained motif. */
body.adminDashboardPage .adminWorkspaceHero{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(220px,330px)!important;min-height:126px!important;margin:14px 0 18px!important}
body.adminDashboardPage .adminWorkspaceArt{display:block!important;width:100%!important;max-width:330px!important;height:118px!important;justify-self:end!important;opacity:.62!important;background-size:contain!important;background-position:right center!important}
body.adminDashboardPage #dashboardHome>.adminWorkspaceHero~.adminWorkspaceHero{display:none!important}
@media(max-width:800px){body.adminDashboardPage .adminWorkspaceHero{grid-template-columns:1fr!important}body.adminDashboardPage .adminWorkspaceArt{height:84px!important;max-width:260px!important;opacity:.48!important}}
'''
css.write_text(c,encoding='utf-8')

# 5) Make the service worker scope-relative so preview and production both update cleanly.
sw.write_text("""const CACHE_NAME='vkvtt-shell-v66-2-interface-1';\nconst APP_SHELL=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./v66-home.css','./v66-design-system.css','./v66-home.js','./v66-home-cloud.js','./v66-ui.js','./period-notifications.js','./v66-home-shell-v662.css','./v66-home-shell-v662.js','./v66-premium-unified.css'];\nself.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)));self.skipWaiting();});\nself.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))));self.clients.claim();});\nself.addEventListener('fetch',event=>{if(event.request.method!=='GET')return;event.respondWith(fetch(event.request).then(response=>{const copy=response.clone();caches.open(CACHE_NAME).then(cache=>cache.put(event.request,copy));return response;}).catch(()=>caches.match(event.request).then(hit=>hit||(event.request.mode==='navigate'?caches.match('./index.html'):undefined))));});\nself.addEventListener('message',event=>{const d=event.data||{};if(d.type!=='VKVTT_SHOW_NOTIFICATION'||!d.title)return;const icon=new URL('icon-192.png',self.registration.scope).href;event.waitUntil(self.registration.showNotification(d.title,{body:d.body||'',icon,badge:icon,tag:d.tag||'vkvtt-period-reminder',renotify:false,data:{url:d.url||self.registration.scope}}));});\nself.addEventListener('notificationclick',event=>{event.notification.close();const url=event.notification.data?.url||self.registration.scope;event.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(list=>{for(const c of list){if('focus'in c){c.navigate(url);return c.focus();}}return clients.openWindow?clients.openWindow(url):undefined;}));});\n""",encoding='utf-8')

# Verification
html=idx.read_text(encoding='utf-8')
assert 'class="swamijiHomePortrait" src="data:image/png;base64,' in html
m=re.search(r'class="swamijiHomePortrait" src="data:image/png;base64,([A-Za-z0-9+/=]+)"',html); assert m
p=base64.b64decode(m.group(1)); assert p[:8]==b'\x89PNG\r\n\x1a\n'; Image.open(io.BytesIO(p)).verify()
assert 'v66-admin-reference-polish.css' not in admin.read_text(encoding='utf-8')
assert 'addSchoolRibbon(file);' not in ui.read_text(encoding='utf-8')
assert "addEventListener('DOMContentLoaded',addRibbon)" not in shell.read_text(encoding='utf-8')
assert 'PHASE1 INTERFACE AUTHORITY 2026-08-24' in css.read_text(encoding='utf-8')
assert "'./period-notifications.js','./v66-home-shell-v662.css'" in sw.read_text(encoding='utf-8')
print('PASS portrait converted and embedded as valid PNG',len(p))
print('PASS compact v60 crest badge lock')
print('PASS legacy home/admin ribbons disabled')
print('PASS old admin reference polish unlinked')
print('PASS one restrained static admin hero remains')
print('PASS service worker is scope-relative and syntactically corrected')
