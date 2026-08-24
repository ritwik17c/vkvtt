from pathlib import Path
import re, base64

# ---------- shared premium shell ----------
css = r'''
/* VKVTT v66.2 unified premium shell */
html.v66-ui body > header:not(.topbar){background:linear-gradient(112deg,#0b2b42,#164e70)!important;border-bottom:3px solid #c88a18!important;box-shadow:0 6px 24px rgba(11,43,66,.13)!important}
html.v66-ui body > header:not(.topbar)::before{opacity:.64!important}
html.v66-ui .card,html.v66-ui .view,html.v66-ui .panel{border:1px solid #d6e1e7!important;border-radius:16px!important;box-shadow:0 1px 2px rgba(11,43,66,.05),0 5px 18px rgba(11,43,66,.04)!important}
html.v66-ui .tile,.premiumTile{position:relative;overflow:hidden;border:1px solid #d2dfe6;border-left:4px solid #1f668c;border-radius:14px;background:#fff;box-shadow:0 4px 14px rgba(11,43,66,.055)}
html.v66-ui .tile:nth-child(3n+2){border-left-color:#247548}html.v66-ui .tile:nth-child(3n){border-left-color:#c88a18}
html.v66-ui .tile::after,.premiumTile::after{content:"";position:absolute;right:-8px;bottom:-20px;width:80px;height:80px;opacity:.66;background-image:linear-gradient(#dbe7ed 1px,transparent 1px),linear-gradient(90deg,#dbe7ed 1px,transparent 1px);background-size:14px 14px;transform:rotate(10deg);pointer-events:none}
html.v66-ui .btn,html.v66-ui button{transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}
html.v66-ui .btn:active,html.v66-ui button:active{transform:translateY(0) scale(.99)}
/* home header */
body:not(.adminDashboardPage) header .homeTitleBlock::before{content:"SCHOOL OPERATIONS";display:block;color:#f5c86b;font-size:.72rem;font-weight:850;letter-spacing:.13em;margin-bottom:4px}
body:not(.adminDashboardPage) header .logo{width:82px!important;height:96px!important;flex:0 0 82px!important;object-fit:contain!important;clip-path:none!important;border-radius:44% 44% 46% 46%/40% 40% 52% 52%!important;padding:7px!important;background:#fff!important;box-shadow:0 1px 0 rgba(255,255,255,.25)!important}
body:not(.adminDashboardPage) header .homeTitleBlock h1{font-size:2rem!important}
/* home premium compact tiles */
.myGrid>button,.nav>button,.opsGrid>button{min-height:76px!important;padding:14px 18px!important;background:#fff!important;color:#103a56!important;border:1px solid #cfdde5!important;border-left:4px solid #1f668c!important;border-radius:14px!important;text-align:left!important;box-shadow:0 4px 14px rgba(11,43,66,.055)!important;position:relative!important;overflow:hidden!important}
.myGrid>button:nth-child(2n),.opsGrid>button:nth-child(2n){border-left-color:#247548!important}.myGrid>button:nth-child(3n),.nav>button:nth-child(3n),.opsGrid>button:nth-child(3n){border-left-color:#c88a18!important}
.myGrid>button::after,.nav>button::after,.opsGrid>button::after{content:""!important;position:absolute!important;right:-7px!important;bottom:-17px!important;width:78px!important;height:78px!important;opacity:.62!important;background-image:linear-gradient(#dbe7ed 1px,transparent 1px),linear-gradient(90deg,#dbe7ed 1px,transparent 1px)!important;background-size:14px 14px!important;transform:rotate(10deg)!important;pointer-events:none!important}
.myGrid>button.active,.nav>button.active,.opsGrid>button.active,.myGrid>button[aria-pressed="true"],.nav>button[aria-pressed="true"],.opsGrid>button[aria-pressed="true"]{border:2px solid #c88a18!important;border-left:4px solid #c88a18!important;background:#fffaf0!important;color:#103a56!important;box-shadow:0 0 0 2px rgba(200,138,24,.11),0 7px 18px rgba(11,43,66,.07)!important}
#periodReminderControl{display:grid!important;grid-template-columns:auto 1fr auto;gap:8px 14px;align-items:center;margin:12px 0 18px!important;padding:10px 14px!important;border:1px solid #dcc57f!important;border-left:4px solid #c88a18!important;border-radius:12px!important;background:#fffaf0!important;box-shadow:0 3px 10px rgba(11,43,66,.04)!important}
#periodReminderControl .prText{font-size:.8rem;color:#617685}#periodReminderControl .prOptions{display:flex;gap:10px;flex-wrap:wrap;align-items:center}#periodReminderControl #prStatus{grid-column:1/-1;margin-top:0!important}
/* admin dashboard width + hero */
@media(min-width:1100px){body.adminDashboardPage header .wrap,body.adminDashboardPage main.wrap{width:min(1360px,calc(100% - 150px))!important;max-width:1360px!important;margin-inline:auto!important;padding-left:0!important;padding-right:0!important}}
@media(max-width:1099px){body.adminDashboardPage header .wrap,body.adminDashboardPage main.wrap{width:calc(100% - 32px)!important;margin-inline:auto!important}}
body.adminDashboardPage #dashboardHome{border-top:4px solid #1f668c!important}
.adminWorkspaceHero{position:relative;display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,420px);align-items:center;min-height:142px;margin:14px 0 16px;border:1px solid #cbdde6;border-radius:18px;background:linear-gradient(108deg,rgba(255,255,255,.98),rgba(239,247,249,.96));overflow:hidden;box-shadow:0 1px 2px rgba(11,43,66,.05),0 5px 18px rgba(11,43,66,.04)}
.adminWorkspaceHero::before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(#c88a18,#e0ad45 52%,#1f668c 52%)}
.adminWorkspaceCopy{padding:22px 16px 22px 30px}.adminWorkspaceCopy .eyebrow{color:#a86f0c;font-size:.68rem;font-weight:850;letter-spacing:.13em;text-transform:uppercase}.adminWorkspaceCopy strong{display:block;margin-top:4px;color:#0b2b42;font-size:1.55rem}.adminWorkspaceCopy p{margin:6px 0 0;color:#607383;font-size:.88rem}
.adminWorkspaceArt{height:142px;background:right center/contain no-repeat url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 420 142'%3E%3Cg fill='none' stroke='%231f668c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 118h388M55 118V60h116v58M44 60l69-43 69 43M84 118V91h58v27M75 73h17v17H75zM137 73h17v17h-17z'/%3E%3Cpath d='M212 44h105v72H212zM229 61h71M229 78h71M229 95h71M247 44v72M282 44v72'/%3E%3Ccircle cx='357' cy='70' r='35'/%3E%3Cpath d='M357 51v20l14 9' stroke='%23c88a18'/%3E%3Cpath d='M357 107c16-10 33-10 50 0v22c-17-10-34-10-50 0-17-10-34-10-50 0v-22c17-10 34-10 50 0Z'/%3E%3Cpath d='M357 107v22'/%3E%3C/g%3E%3C/svg%3E")}
/* leave history/edit helpers */
.teacherHistoryLine{grid-template-columns:minmax(130px,.65fr) minmax(190px,1fr) 1.25fr auto!important;align-items:center}.historyEditBtn{padding:6px 9px!important;font-size:.76rem!important;white-space:nowrap}
.recoveryCard{border:1px solid #d7e3e9;border-left:5px solid #c88a18;border-radius:14px;padding:13px;margin:9px 0;background:#fffdf8}.recoveryCard.ok{border-left-color:#247548;background:#f8fcf9}.recoveryCard.warn{border-left-color:#c88a18;background:#fffaf0}
@media(max-width:800px){.adminWorkspaceHero{grid-template-columns:1fr}.adminWorkspaceArt{height:110px}.teacherHistoryLine{grid-template-columns:1fr!important}#periodReminderControl{grid-template-columns:1fr!important}}
'''
Path('v66-premium-unified.css').write_text(css,encoding='utf-8')

# inject unified stylesheet into active pages (old snapshots excluded)
exclude={'admin-leave-editor-v63.html','admin-leave-editor-v64-clean.html'}
for p in Path('.').glob('*.html'):
    if p.name in exclude: continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    if 'v66-premium-unified.css' not in s and '</head>' in s:
        s=s.replace('</head>','<link rel="stylesheet" href="v66-premium-unified.css?v=66.2-premium-1">\n</head>',1)
    p.write_text(s,encoding='utf-8')

# ---------- exact portrait source -> real binary JPEG ----------
svg=Path('swamiji-gold.svg').read_text(encoding='utf-8',errors='ignore')
m=re.search(r'data:image/jpeg;base64,([^\"\']+)',svg)
if not m: raise SystemExit('No embedded approved Swamiji JPEG found')
b=base64.b64decode(re.sub(r'\s+','',m.group(1)),validate=False)
if not (b.startswith(b'\xff\xd8\xff') and b.endswith(b'\xff\xd9')): raise SystemExit('Embedded Swamiji JPEG failed magic check')
Path('swamiji-portrait.jpg').write_bytes(b)

# homepage: use real binary portrait
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=re.sub(r'src="swamiji-(?:clean\.svg|gold\.svg|portrait\.jpg)[^"]*"','src="swamiji-portrait.jpg?v=66.2-premium-1"',s)
p.write_text(s,encoding='utf-8')

# period reminder: place after My Area grid, compact markup
p=Path('period-notifications.js');s=p.read_text(encoding='utf-8')
s=s.replace("const anchor=document.getElementById('myTimetableBtn')||document.querySelector('.myGrid');", "const anchor=document.querySelector('.myGrid')||document.getElementById('myTimetableBtn');")
s=s.replace("box.style.cssText='margin-top:10px;padding:12px;border:1px solid #d7c27a;border-radius:13px;background:#fffaf0';", "box.style.cssText='';")
s=s.replace("box.innerHTML=`<b>🔔 Period Reminder</b><div style=\"font-size:.82rem;margin:4px 0 9px\">Uses the <b>Activated Schedule</b>. Announces exactly 1 minute before your period while VKVTT is active.</div><label style=\"display:inline-flex;gap:6px;align-items:center;margin-right:12px\"><input id=\"prEnabled\" type=\"checkbox\" ${p.enabled?'checked':''}> Enabled</label><label style=\"display:inline-flex;gap:6px;align-items:center;margin-right:12px\"><input id=\"prVoice\" type=\"checkbox\" ${p.voice?'checked':''}> Voice</label><label style=\"display:inline-flex;gap:6px;align-items:center\"><input id=\"prNotify\" type=\"checkbox\" ${p.notification?'checked':''}> Notification</label><button id=\"prTest\" type=\"button\" style=\"margin-left:10px\">Test Voice</button><div id=\"prStatus\" style=\"font-size:.78rem;margin-top:7px\"></div>`;", "box.innerHTML=`<b>🔔 Period Reminder</b><div class=\"prText\">1-minute alert from the Activated Schedule.</div><div class=\"prOptions\"><label><input id=\"prEnabled\" type=\"checkbox\" ${p.enabled?'checked':''}> Enabled</label><label><input id=\"prVoice\" type=\"checkbox\" ${p.voice?'checked':''}> Voice</label><label><input id=\"prNotify\" type=\"checkbox\" ${p.notification?'checked':''}> Notification</label><button id=\"prTest\" type=\"button\">Test Voice</button></div><div id=\"prStatus\"></div>`;")
p.write_text(s,encoding='utf-8')

# admin dashboard: restore workspace hero
p=Path('admin-dashboard.html');s=p.read_text(encoding='utf-8')
marker='<div class="help">Choose an administrative area. No section opens automatically.</div>'
hero='''<div class="adminWorkspaceHero"><div class="adminWorkspaceCopy"><div class="eyebrow">Vivekananda Kendra Vidyalaya, Nalbari</div><strong>School Administration Workspace</strong><p>Timetable, classes, staff, attendance and academic records in one organised workspace.</p></div><div class="adminWorkspaceArt" aria-hidden="true"></div></div>'''
if 'adminWorkspaceHero' not in s and marker in s: s=s.replace(marker,marker+'\n    '+hero,1)
p.write_text(s,encoding='utf-8')

# auth persistence helper for active authenticated subpages
for name in ['admin-leave-editor.html','admin-leave.html','admin-leave-rules.html','admin-schedules.html','admin-export.html','admin-import.html','admin-leave-import.html','admin-timetable-studio.html']:
    p=Path(name)
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    if 'getAuth' not in s: continue
    if 'browserLocalPersistence' not in s:
        s=re.sub(r'import\s*\{([^}]*)\}\s*from\s*["\']https://www\.gstatic\.com/firebasejs/12\.17\.1/firebase-auth\.js["\'];',lambda m:'import{'+m.group(1).strip()+',setPersistence,browserLocalPersistence}from"https://www.gstatic.com/firebasejs/12.17.1/firebase-auth.js";',s,count=1)
        # after first auth=getAuth(...) statement
        s=re.sub(r'(\bauth\s*=\s*getAuth\([^;]+;)',r"\1\nawait setPersistence(auth,browserLocalPersistence).catch(()=>{});\nif(typeof auth.authStateReady==='function')await auth.authStateReady().catch(()=>{});",s,count=1)
    p.write_text(s,encoding='utf-8')

# ---------- Leave Editor: compact ranges, direct history edit, recovery ----------
p=Path('admin-leave-editor.html');s=p.read_text(encoding='utf-8')
# compact continuous plans as one range line
s=re.sub(r"function recordText\(p\)\{\n const ds=planDates\(p\);return ds.length<=5\?ds.map\(displayDate\).join\(' · '\):`\$\{ds.slice\(0,5\).map\(displayDate\).join\(' · '\)\} · \+\$\{ds.length-5\} more`\n\}","function recordText(p){\n const ds=planDates(p);if(p.mode!=='multiple'&&p.startDate){const a=p.startDate||p.date,b=p.endDate||a;return a===b?displayDate(a):`${displayDate(a)} → ${displayDate(b)} · ${ds.length} day${ds.length===1?'':'s'}`;}return ds.length<=5?ds.map(displayDate).join(' · '):`${ds.slice(0,5).map(displayDate).join(' · ')} · +${ds.length-5} more`;\n}",s,count=1)
# history row edit buttons
old="const lines=ordered.map(g=>{const x=g.item,state=g.dates.includes(today)?'Current':(g.dates.some(d=>d>today)?'Upcoming':'Past'),category=historyCategoryText(g),units=(x.type==='full'||x.type==='half')?`${g.units} unit${g.units===1?'':'s'}`:'—';return `<div class=\"teacherHistoryLine\"><div class=\"teacherHistoryDate\">${safe(historyDateText(g))}</div><div>${safe(category)} · ${safe(units)} <span class=\"pill\">${safe(state)}</span></div><div>${safe((g.remarks||[]).join(' · ')||'No remarks')}</div></div>`}).join('');"
new="const lines=ordered.map(g=>{const x=g.item,state=g.dates.includes(today)?'Current':(g.dates.some(d=>d>today)?'Upcoming':'Past'),category=historyCategoryText(g),units=(x.type==='full'||x.type==='half')?`${g.units} unit${g.units===1?'':'s'}`:'—',editKind=x._kind==='manual'?'manual':'plan',editKey=x._kind==='manual'?manualKey(x):x.id;return `<div class=\"teacherHistoryLine\"><div class=\"teacherHistoryDate\">${safe(historyDateText(g))}</div><div>${safe(category)} · ${safe(units)} <span class=\"pill\">${safe(state)}</span></div><div>${safe((g.remarks||[]).join(' · ')||'No remarks')}</div><div><button type=\"button\" class=\"historyEditBtn\" data-history-edit-kind=\"${editKind}\" data-history-edit-key=\"${safe(editKey)}\">✏ Edit</button></div></div>`}).join('');"
if old in s: s=s.replace(old,new,1)
wire="""\n  out.querySelectorAll('[data-history-edit-key]').forEach(b=>b.onclick=()=>b.dataset.historyEditKind==='manual'?startEditManual(b.dataset.historyEditKey):startEditPlan(b.dataset.historyEditKey));"""
s=s.replace("  scheduleLeaveRulePreview();\n }catch(e){if(token===teacherHistoryToken)",wire+"\n  scheduleLeaveRulePreview();\n }catch(e){if(token===teacherHistoryToken)",1)

# recovery section before VL bulk
recovery_section='''\n<section class="card quick-hide" id="legacyDatedRecoverySection">\n  <div class="sectionTitle"><div><h2>♻ Recover Verified Dated Leave Records</h2><div class="help">Shows older leave/accounting cards that already contain verified dates or a verified date range but are not yet visible as operational leave. No dates are invented.</div></div><button id="scanRecoverableBtn">↻ Scan</button></div>\n  <div id="recoverableSummary" class="status info">Scanning saved legacy cards…</div>\n  <div class="actions"><button id="recoverVerifiedBtn" class="primary">♻ Recover / Sync Safe Verified Records</button></div>\n  <div id="recoverableList"></div>\n</section>\n'''
if 'legacyDatedRecoverySection' not in s: s=s.replace('<section class="card quick-hide" id="vlBulkSection">',recovery_section+'\n<section class="card quick-hide" id="vlBulkSection">',1)

recovery_js=r'''
function explicitLegacyDateInfo(x){
 const marker=x&&((x.vlHasVerifiedRange===true)||(x.hasVerifiedDates===true)||(x.datesVerified===true)||(x.verified===true)||(String(x.resolutionStatus||'')==='resolved-dated'));
 if(!marker)return{dates:[],reason:'No explicit date-verification marker'};
 let dates=[];
 if(Array.isArray(x.verifiedDates))dates=x.verifiedDates.filter(Boolean);
 else if(Array.isArray(x.resolvedDates))dates=x.resolvedDates.filter(Boolean);
 else if(Array.isArray(x.dates)&&x.hasVerifiedDates===true)dates=x.dates.filter(Boolean);
 else{
   const a=x.vlFromDate||x.verifiedFromDate||x.fromDate||'',b=x.vlToDate||x.verifiedToDate||x.toDate||a;
   if(a&&b)dates=rangeDates(a,b);
 }
 dates=[...new Set(dates.filter(d=>/^\d{4}-\d{2}-\d{2}$/.test(String(d))))].sort();
 if(!dates.length)return{dates:[],reason:'Verified marker exists but no valid saved dates were found'};
 const units=Number(x.units||0),cat=String(x.category||'').trim().toUpperCase();
 if(!cat)return{dates,reason:'Leave category is missing'};
 if(!(units>0))return{dates,reason:'Leave units are missing'};
 if(Math.abs(units-dates.length)>0.001)return{dates,reason:`Saved units (${units}) do not match ${dates.length} verified full-day date${dates.length===1?'':'s'}`};
 return{dates,category:cat,units,reason:''};
}
function legacyRecoveryState(x){
 const info=explicitLegacyDateInfo(x);if(!info.dates.length||info.reason)return{...info,state:'review'};
 const existing=activePlans().filter(p=>String(p.code)===String(x.teacherCode)&&String(p.leaveCategory||'').toUpperCase()===info.category),covered=new Set();
 for(const p of existing)for(const d of planDates(p))covered.add(d);
 const hits=info.dates.filter(d=>covered.has(d));
 return{...info,state:hits.length===info.dates.length?'already':hits.length?'partial':'safe',hits};
}
function renderRecoverableLegacy(){
 const box=$('recoverableList'),sum=$('recoverableSummary');if(!box||!sum)return;
 const rows=legacy.filter(x=>x&&x.active!==false).map(x=>({x,st:legacyRecoveryState(x)})).filter(z=>z.st.dates.length||z.x.vlHasVerifiedRange===true||z.x.hasVerifiedDates===true||z.x.datesVerified===true);
 const safeRows=rows.filter(z=>z.st.state==='safe'),partial=rows.filter(z=>z.st.state==='partial'),already=rows.filter(z=>z.st.state==='already'),review=rows.filter(z=>z.st.state==='review');
 sum.className='status '+(partial.length||review.length?'warn':'ok');sum.innerHTML=`<b>${rows.length}</b> dated/verified legacy card${rows.length===1?'':'s'} found · ${safeRows.length} safe to recover · ${already.length} already represented · ${partial.length+review.length} need review.`;
 box.innerHTML=rows.length?rows.map(({x,st})=>`<div class="recoveryCard ${st.state==='already'?'ok':st.state==='safe'?'ok':'warn'}"><div class="cardTop"><div><div class="cardTitle">${safe(x.teacherName||teacherByCode(x.teacherCode)?.name||x.teacherCode)} <span class="pill">${safe(x.teacherCode||'')}</span></div><div class="meta">${safe(catLabel(x.category))} · ${safe(x.units||'—')} unit${Number(x.units)===1?'':'s'} · ${st.dates.length?(safe(displayDate(st.dates[0]))+(st.dates.length>1?' → '+safe(displayDate(st.dates[st.dates.length-1]))+` · ${st.dates.length} days`:'')):'No saved dates'}<br>${safe(x.reason||x.resolutionNote||'Older saved leave/accounting card')}</div></div><span class="pill ${st.state==='safe'||st.state==='already'?'ok':'warn'}">${st.state==='safe'?'Safe to recover':st.state==='already'?'Already visible':st.state==='partial'?'Partial overlap':'Review needed'}</span></div>${st.reason?`<div class="small">${safe(st.reason)}</div>`:''}<label class="small"><input class="bulkSelect" type="checkbox" data-bulk-del="legacy|${safe(x.id)}" ${bulkDeleteSelection.has('legacy|'+x.id)?'checked':''}> Select for bulk erroneous/duplicate cleanup</label></div>`).join(''):'<div class="empty">No saved legacy cards with explicit verified dates were found.</div>';
 wireBulkDeleteSelection();updateBulkDeleteCount();
}
async function recoverVerifiedLegacy(){
 await requireAdminSession();await loadSecondaryData();
 const candidates=legacy.filter(x=>x&&x.active!==false).map(x=>({x,st:legacyRecoveryState(x)})).filter(z=>z.st.state==='safe');
 if(!candidates.length){alert('No safe verified legacy records are waiting for recovery.');renderRecoverableLegacy();return}
 if(!confirm(`Recover ${candidates.length} verified dated legacy record${candidates.length===1?'':'s'} into the operational leave register?\n\nOnly cards with explicit saved dates and matching full-day unit totals will be recovered. No dates will be invented.`))return;
 const actor=await requireAdminSession(),newMap={...plans};let recovered=0;
 for(const {x,st} of candidates){
   const stamp=Date.now()+recovered,created=[];
   st.dates.forEach((date,i)=>{const row={date,type:'full',category:st.category,units:1,part:'full',from:0,to:0,note:`Recovered from verified legacy record ${x.id}${x.month?' · '+x.month:''}`},p=makePlan(row,String(x.teacherCode),stamp,i,actor);p.source='legacy-verified-recovery-v66.2';p.legacySourceId=x.id;newMap[p.id]=p;created.push(p)});
   for(const p of created){await setDoc(doc(db,'approvedStatusPlans',String(p.id)),{...p,approved:true,updatedAt:serverTimestamp(),updatedBy:actor.uid,updatedByEmail:actor.email||''},{merge:true});try{await addPersonalProjection(p)}catch(e){}}
   await setDoc(doc(db,'legacyLeaveAccounting',x.id),{resolutionStatus:'resolved-dated',active:false,resolvedPlanIds:created.map(p=>p.id),resolutionNote:'Recovered from previously verified dated legacy leave card.',resolvedAt:serverTimestamp(),resolvedBy:actor.uid,resolvedByEmail:actor.email||''},{merge:true});
   x.resolutionStatus='resolved-dated';x.active=false;x.resolvedPlanIds=created.map(p=>p.id);recovered++;
 }
 await setDoc(doc(db,'dailyRecords','__leavePlans'),{date:'__leavePlans',dayName:'Scheduled Leave / Status Plans',plans:newMap,updatedAt:serverTimestamp(),updatedBy:actor.uid,updatedByEmail:actor.email||''},{merge:false});plans=newMap;
 await syncLeaveControl();renderAll();renderLeaveIntegrity();alert(`Recovered ${recovered} verified dated legacy leave record${recovered===1?'':'s'}.`);
}
'''
if 'function explicitLegacyDateInfo' not in s:
    s=s.replace('function eligibleVlItems(){',recovery_js+'\nfunction eligibleVlItems(){',1)
s=s.replace(' renderControl();renderPending();renderRecords();renderFinalAccounting();',' renderControl();renderPending();renderRecords();renderFinalAccounting();renderRecoverableLegacy();',1)
# wire buttons near existing bottom bindings
if "$('recoverVerifiedBtn').onclick" not in s:
    s=s.replace("$('removeSafeDuplicatesBtn').onclick=removeSafeExactDuplicates;", "$('removeSafeDuplicatesBtn').onclick=removeSafeExactDuplicates;\nif($('scanRecoverableBtn'))$('scanRecoverableBtn').onclick=renderRecoverableLegacy;\nif($('recoverVerifiedBtn'))$('recoverVerifiedBtn').onclick=recoverVerifiedLegacy;",1)
p.write_text(s,encoding='utf-8')

# Approved leave register: action column -> edit source record in master editor
p=Path('admin-leave.html');s=p.read_text(encoding='utf-8')
s=s.replace('<th>Remarks</th></tr></thead>', '<th>Remarks</th><th>Action</th></tr></thead>',1)
s=s.replace("<td>${safe((x._remarks||[]).join(' · ')||'—')}</td></tr>", "<td>${safe((x._remarks||[]).join(' · ')||'—')}</td><td><a class=\"btn\" href=\"admin-leave-editor.html?v=66.0\">✏ Edit in Leave Master</a></td></tr>",1)
p.write_text(s,encoding='utf-8')

print('Applied v66.2 final correction pass')
