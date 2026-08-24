from pathlib import Path
import re,base64

# 1) Homepage auth persistence: wait for local session restoration before auth gate logic.
p=Path('v66-home-cloud.js'); s=p.read_text(encoding='utf-8')
needle='const firebaseApp=initializeApp(firebaseConfig),auth=getAuth(firebaseApp),db=getFirestore(firebaseApp),provider=new GoogleAuthProvider();'
insert=needle+'\nawait setPersistence(auth,browserLocalPersistence).catch(e=>console.warn(\'Auth persistence setup:\',e));\nif(typeof auth.authStateReady===\'function\')await auth.authStateReady().catch(e=>console.warn(\'Auth restore:\',e));'
if 'Auth persistence setup:' not in s:
    s=s.replace(needle,insert,1)
p.write_text(s,encoding='utf-8')

# 2) Self-contained approved Swamiji portrait on homepage + delayed loader using same face.
p=Path('index.html'); s=p.read_text(encoding='utf-8')
b64=base64.b64encode(Path('swamiji-portrait.jpg').read_bytes()).decode('ascii')
data='data:image/jpeg;base64,'+b64
s=re.sub(r'<img class="swamijiHomePortrait"[^>]*>',f'<img class="swamijiHomePortrait" src="{data}" alt="Swami Vivekananda line portrait">',s,count=1)
if 'id="vkvSlowLoader"' not in s:
    loader=f'''<div id="vkvSlowLoader" aria-hidden="true"><div class="vkvLoaderPortrait"><img src="{data}" alt=""><span class="vkvBlink"></span></div><div>Loading VKVTT…</div></div>'''
    s=s.replace('<body>', '<body>'+loader,1)
    s=s.replace('</head>', '''<style id="vkv-swamiji-inline-loader">
#vkvSlowLoader{position:fixed;inset:0;z-index:99999;display:none;place-items:center;align-content:center;gap:8px;background:rgba(247,250,248,.94);color:#17364f;font-weight:750}.vkvLoaderPortrait{position:relative;width:112px;height:112px}.vkvLoaderPortrait img{width:100%;height:100%;object-fit:contain;border-radius:18px;opacity:.92}.vkvBlink{position:absolute;left:27%;right:27%;top:43%;height:12%;background:rgba(200,138,24,.12);transform:scaleY(0);transform-origin:center;pointer-events:none}@keyframes vkvBlink{0%,92%,100%{transform:scaleY(0)}94%,96%{transform:scaleY(1)}}#vkvSlowLoader.show{display:grid}.vkvLoaderPortrait .vkvBlink{animation:vkvBlink 5.8s infinite}
</style></head>''',1)
    s=s.replace('</body>', '''<script>(function(){let done=false;const el=document.getElementById('vkvSlowLoader'),t=setTimeout(()=>{if(!done&&el)el.classList.add('show')},1800);window.addEventListener('load',()=>{done=true;clearTimeout(t);if(el)el.classList.remove('show')},{once:true});setTimeout(()=>{if(el)el.classList.remove('show')},12000)})();</script></body>''',1)
p.write_text(s,encoding='utf-8')

# 3) Leave snapshot/categories: only ordinary applicable rules appear as general options/balances.
p=Path('v66-home.js'); s=p.read_text(encoding='utf-8')
old="function homeActiveRules(ctx=window.__homepageLeaveContext){return ctx&&Array.isArray(ctx.categories)?ctx.categories.filter(r=>r&&r.active!==false&&String(r.code||'').trim()&&(r.unlimited===true||(Number.isFinite(Number(r.max))&&Number(r.max)>0))).sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.code).localeCompare(String(b.code))):[]}"
new="function homeActiveRules(ctx=window.__homepageLeaveContext,code=''){const staff=code?homeStaffCategory(code,ctx):'';return ctx&&Array.isArray(ctx.categories)?ctx.categories.filter(r=>{if(!(r&&r.active!==false&&String(r.code||'').trim()&&(r.unlimited===true||(Number.isFinite(Number(r.max))&&Number(r.max)>0))))return false;if(String(r.ruleType||'regular')==='conditional')return !!code&&homeConditionalEligible(code,r,ctx);if(staff&&staff!=='unknown'&&!homeRuleApplies(r,staff))return false;return true}).sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.code).localeCompare(String(b.code))):[]}"
if old in s:s=s.replace(old,new,1)
s=s.replace("const current=String(existing||select.value||'').toUpperCase(),rules=homeActiveRules(ctx),codes=rules.map", "const current=String(existing||select.value||'').toUpperCase(),staffCode=E('leaveTeacher')?.value||'',rules=homeActiveRules(ctx,staffCode),codes=rules.map",1)
s=s.replace("const t=teacherByEffectiveCode(code)||{name:code},rules=homeActiveRules(ctx),metrics=rules.map", "const t=teacherByEffectiveCode(code)||{name:code},rules=homeActiveRules(ctx,code),metrics=rules.map",1)
s=s.replace("if(r.unlimited===true){value='Unlimited';detail=`Used in saved dated records: ${u.used}`}", "if(r.unlimited===true){value='Subject to approval';detail=`No fixed maximum · saved dated usage ${u.used}`}",1)
p.write_text(s,encoding='utf-8')

# 4) Admin dashboard: suppress duplicate/oversized motif and keep proportionate hero art.
p=Path('v66-premium-unified.css'); s=p.read_text(encoding='utf-8')
s += '\n/* Phase-1 admin motif restraint */\nbody.adminDashboardPage .adminWorkspaceHero{min-height:126px!important}body.adminDashboardPage .adminWorkspaceArt{height:126px!important;max-width:360px!important;justify-self:end;opacity:.72!important;background-size:contain!important}body.adminDashboardPage #dashboardHome>.adminWorkspaceHero~.adminWorkspaceHero{display:none!important}\n@media(max-width:800px){body.adminDashboardPage .adminWorkspaceArt{height:92px!important;opacity:.55!important}}\n'
p.write_text(s,encoding='utf-8')

# 5) Logo white backing: tighter, softer earlier-style badge.
s=Path('v66-premium-unified.css').read_text(encoding='utf-8')
s += '\n/* Phase-1 crest badge refinement */\nbody:not(.adminDashboardPage) header .logo{width:78px!important;height:88px!important;flex-basis:78px!important;padding:5px!important;border-radius:46% 46% 49% 49%/42% 42% 50% 50%!important;background:#fff!important;box-shadow:0 2px 8px rgba(0,0,0,.10)!important}\n'
Path('v66-premium-unified.css').write_text(s,encoding='utf-8')

print('phase1 patch applied')