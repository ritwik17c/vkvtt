from pathlib import Path

# 1) Period reminder: use the same active-schedule resolver as the homepage.
p=Path('period-notifications.js'); s=p.read_text(encoding='utf-8')
old="function activeProfile(){const D=window.DATA;if(!D)return null;const id=D.activeScheduleProfileId;if(!id)return null;const p=D.scheduleProfiles&&D.scheduleProfiles[id];return p&&p.times?p:null}\nfunction activeTime(period){const p=activeProfile();if(!p)return '';return String(p.times?.[String(Number(period))]??p.times?.[Number(period)]??'')}"
new="function activeProfile(){if(typeof window.activeScheduleProfile==='function'){try{return window.activeScheduleProfile()}catch(_){}}const D=window.DATA;if(!D)return null;const id=D.activeScheduleProfileId||'normal',profiles=D.scheduleProfiles||{};return profiles[id]||profiles.normal||null}\nfunction activeTime(period){if(typeof window.scheduleTime==='function'){try{return String(window.scheduleTime(period)||'')}catch(_){}}const p=activeProfile();if(!p)return '';return String(p.times?.[String(Number(period))]??p.times?.[Number(period)]??'')}"
assert old in s, 'period reminder resolver not found'; s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 2) Daily History: rebuild dated operational summary from authoritative current records.
p=Path('v66-home.js'); s=p.read_text(encoding='utf-8')
old='let sts=h.statuses||[],als=Object.values(h.allotments||{}).filter(x=>x&&x.day===h.dayName).sort((a,b)=>a.period-b.period);out.innerHTML=`<b>${displayDate(date)} · ${h.dayName}</b><h3>Leave / OD / Special Assignment</h3>${sts.length?sts.map(o=>{let t=teacherByEffectiveCode(o.code,date);return `<div>${esc(t?t.name:o.code)} (${o.code}) — ${statusLabel(o)}</div>`}).join(""):"None"}<h3>Proxy Allotments</h3>${als.length?als.map(x=>`<div>${PL(x.period)} — ${esc(x.name)} (${x.code}) — Regular ${x.regular} + Proxy ${x.proxyNumber} = ${x.total}</div>`).join(""):"None"}`'
new='let snapSts=Array.isArray(h.statuses)?h.statuses:[],liveSts=[];try{liveSts=leaveData(date)||[]}catch(_){liveSts=[]}let planned=[];try{planned=window.plannedStatusesForDate?window.plannedStatusesForDate(date):[]}catch(_){planned=[]}const byKey=new Map();[...snapSts,...liveSts,...planned].filter(o=>o&&["full","half","od","special","vacant"].includes(o.type)).forEach(o=>byKey.set(String(o.code||"")+"|"+String(o.type||"")+"|"+String(o.fromPeriod||"")+"|"+String(o.toPeriod||""),o));let sts=[...byKey.values()],als=Object.values(h.allotments||{}).filter(x=>x&&x.day===h.dayName).sort((a,b)=>a.period-b.period);out.innerHTML=`<b>${displayDate(date)} · ${h.dayName}</b><h3>Leave / Duty Leave / Operational Status</h3>${sts.length?sts.map(o=>{let t=teacherByEffectiveCode(o.code,date);return `<div>${esc(t?t.name:o.code)} (${o.code}) — ${statusLabel(o)}</div>`}).join(""):"None"}<h3>Proxy Allotments</h3>${als.length?als.map(x=>`<div>${PL(x.period)} — ${esc(x.name)} (${x.code}) — Regular ${x.regular} + Proxy ${x.proxyNumber} = ${x.total}</div>`).join(""):"None"}`'
assert old in s, 'history render block not found'; s=s.replace(old,new,1)
# expose shared schedule helpers to reminder engine
needle='window.applyActiveScheduleProfile=refreshScheduleUi;'
rep='window.activeScheduleProfile=activeScheduleProfile;window.scheduleTime=scheduleTime;window.applyActiveScheduleProfile=refreshScheduleUi;'
assert needle in s; s=s.replace(needle,rep,1)
p.write_text(s,encoding='utf-8')

# 3) Attendance: top Home button + deterministic action-state audit feedback.
p=Path('attendance.html'); s=p.read_text(encoding='utf-8')
old='<body><header><div style="max-width:980px;margin:auto"><h1 style="margin:0">My Attendance</h1><div>VKV Nalbari · Pilot Geo-Attendance · Version 66.0</div></div></header><main>'
new='<body><header><div style="max-width:1180px;margin:auto;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap"><div><h1 style="margin:0">My Attendance</h1><div>VKV Nalbari · Pilot Geo-Attendance · Version 66.0</div></div><div class="actions" style="margin:0"><button onclick="location.href=\'index.html?v=66.2\'">← Return to Timetable Home</button></div></div></header><main>'
assert old in s; s=s.replace(old,new,1)
s=s.replace('main{max-width:980px;margin:auto;padding:14px}', 'main{max-width:1180px;margin:auto;padding:14px}',1)
needle="document.querySelectorAll('[data-punch]').forEach(b=>b.onclick=()=>punch(b.dataset.punch));"
addon="""function updatePunchButtons(){const day=events.filter(x=>x.date===today),last=[...day].reverse().find(x=>['arrival','leave','return','final'].includes(x.type)),arrived=day.some(x=>x.type==='arrival'),finalDone=day.some(x=>x.type==='final'),inside=arrived&&!finalDone&&(!last||['arrival','return'].includes(last.type)),outside=arrived&&!finalDone&&last?.type==='leave',hasOdIn=day.some(x=>x.type==='od_check_in'),odOut=day.some(x=>x.type==='od_check_out');const set=(type,disabled,title='')=>{const b=document.querySelector(`[data-punch=\"${type}\"]`);if(b){b.disabled=!!disabled;b.title=title}};set('arrival',arrived,'Arrival can be recorded once per day.');set('leave',!inside,'Available while you are recorded inside campus.');set('return',!outside,'Available after Leave Campus.');set('final',!arrived||finalDone||outside,'Record arrival first; return from a temporary exit before Final Departure.');set('od_check_in',!od||hasOdIn&&!odOut,'Requires an approved OD assignment.');set('od_check_out',!od||!hasOdIn||odOut,'Requires OD Check-In first.')}\n"""+needle
assert needle in s; s=s.replace(needle,addon,1)
s=s.replace("await loadEvents();renderHeader();render('today')", "await loadEvents();renderHeader();updatePunchButtons();render('today')",1)
s=s.replace("await loadEvents();render('today')", "await loadEvents();updatePunchButtons();render('today')",1)
p.write_text(s,encoding='utf-8')

# 4) Biometric import: three navigation exits near top, same tab.
p=Path('admin-biometric-import.html'); s=p.read_text(encoding='utf-8')
old='<body><header><div style="max-width:1180px;margin:auto"><h1 style="margin:0">Biometric History Import</h1><div>VKV Nalbari · Attendance Administration</div></div></header><main>'
new='<body><header><div style="max-width:1280px;margin:auto"><h1 style="margin:0">Biometric History Import</h1><div>VKV Nalbari · Attendance Administration</div></div></header><main><div class="actions"><button onclick="location.href=\'admin-attendance.html?v=66.2\'">← Attendance Administration</button><button onclick="location.href=\'admin-dashboard.html?v=66.2\'">⌂ Admin Dashboard</button><button onclick="location.href=\'index.html?v=66.2\'">▦ Timetable Home</button></div>'
assert old in s; s=s.replace(old,new,1)
s=s.replace('main{max-width:1180px;margin:auto;padding:14px}', 'main{max-width:1280px;margin:auto;padding:14px}',1)
p.write_text(s,encoding='utf-8')

# 5) Shared UI: responsive wider content, consistent sub-page return nav, integrity-card relocation.
p=Path('v66-ui.js'); s=p.read_text(encoding='utf-8')
append=r'''

/* v66.2 preview correction batch: navigation, alignment and tool hierarchy */
(function(){
  function navBtn(label,href){const a=document.createElement('a');a.className='btn v66-return-btn';a.href=href;a.textContent=label;return a}
  function addReturnNav(){
    const file=(location.pathname.split('/').pop()||'index.html').toLowerCase();
    if(file==='index.html'||file==='')return;
    const main=document.querySelector('main');if(!main||document.getElementById('v66ReturnNav'))return;
    const admin=file.startsWith('admin-'),box=document.createElement('div');box.id='v66ReturnNav';box.className='v66-return-nav';
    const parentMap={
      'admin-biometric-import.html':['← Attendance Administration','admin-attendance.html?v=66.2'],
      'admin-attendance-tests.html':['← Attendance Administration','admin-attendance.html?v=66.2'],
      'admin-leave-editor.html':['← Approved Leave','admin-leave.html?v=66.2'],
      'admin-leave-import.html':['← Approved Leave','admin-leave.html?v=66.2'],
      'admin-leave-rules.html':['← Leave Administration','admin-leave.html?v=66.2'],
      'admin-schedules.html':['← Admin Dashboard','admin-dashboard.html?v=66.2'],
      'admin-timetable-studio.html':['← Admin Dashboard','admin-dashboard.html?v=66.2']
    };
    const p=parentMap[file];if(p)box.appendChild(navBtn(p[0],p[1]));
    if(admin&&!box.querySelector('[href^="admin-dashboard"]'))box.appendChild(navBtn('⌂ Admin Dashboard','admin-dashboard.html?v=66.2'));
    box.appendChild(navBtn('▦ Timetable Home','index.html?v=66.2'));
    main.prepend(box);
  }
  function moveIntegrityCard(){
    if(!/admin-leave-editor\.html$/i.test(location.pathname))return;
    const cards=[...document.querySelectorAll('#app > section.card, #app > .card')];
    const recon=cards.find(x=>/Leave Reconciliation Control/i.test(x.textContent||''));
    const integrity=cards.find(x=>/Leave Integrity Checker\s*&\s*Duplicate Remover/i.test(x.textContent||''));
    if(recon&&integrity&&recon.nextElementSibling!==integrity)recon.insertAdjacentElement('afterend',integrity);
  }
  function style(){if(document.getElementById('v66CorrectionStyle'))return;const st=document.createElement('style');st.id='v66CorrectionStyle';st.textContent=`
    .v66-return-nav{max-width:1320px;margin:0 auto 10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
    .v66-return-nav .v66-return-btn{display:inline-flex;align-items:center;text-decoration:none}
    @media(min-width:1100px){body.v66-school-context main,.v66-school-context .wrap,.v66-school-context .cloudInner{max-width:1320px!important}}
    @media(max-width:1099px){.v66-return-nav{padding-left:2px;padding-right:2px}}
  `;document.head.appendChild(st)}
  function run(){style();addReturnNav();moveIntegrityCard()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
'''
if 'v66.2 preview correction batch' not in s:s+=append
p.write_text(s,encoding='utf-8')

# 6) Homepage header alignment / portrait fallback.
p=Path('v66-home.css'); s=p.read_text(encoding='utf-8')
append='''\n/* v66.2 header alignment correction */\n@media(min-width:900px){header .head{max-width:1250px;justify-content:flex-start}.homeTitleBlock{margin-right:auto}.swamijiHomePortrait{margin-left:auto}}\n@media(max-width:899px){header .head{justify-content:flex-start}.homeTitleBlock{margin-right:auto}}\n'''
if 'v66.2 header alignment correction' not in s:s+=append
p.write_text(s,encoding='utf-8')
