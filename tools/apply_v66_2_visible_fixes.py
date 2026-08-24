from pathlib import Path
import re

# 1) Homepage identity scale + reliable approved Swamiji asset rendering
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='<!-- v66.2 visible-fixes -->'
if marker not in s:
    css='''\n<style id="v66-2-visible-fixes">\n@media (min-width:701px){\n header .head{min-height:132px!important;gap:18px!important}\n header .logo{width:92px!important;height:92px!important;padding:4px!important;flex:0 0 92px!important}\n header .homeTitleBlock h1{font-size:2rem!important;line-height:1.12!important}\n header .homeTitleBlock small{font-size:1.04rem!important}\n header .swamijiHomePortrait{width:132px!important;height:132px!important;object-fit:contain!important;margin-left:auto!important}\n}\n@media (max-width:700px){\n header .head{min-height:94px!important;gap:11px!important}\n header .logo{width:66px!important;height:66px!important;flex:0 0 66px!important}\n header .homeTitleBlock h1{font-size:1.4rem!important}\n header .homeTitleBlock small{font-size:.9rem!important}\n header .swamijiHomePortrait{width:82px!important;height:82px!important;object-fit:contain!important;margin-left:auto!important}\n}\n</style>\n'''
    s=s.replace('</head>',marker+css+'</head>')
p.write_text(s,encoding='utf-8')

# Rebuild SVG using the exact embedded approved portrait image, but without the failing SVG filter chain.
p=Path('swamiji-gold.svg'); svg=p.read_text(encoding='utf-8')
m=re.search(r'href="(data:image/jpeg;base64,[^"]+)"',svg)
if not m: raise SystemExit('Embedded Swamiji portrait image not found')
data=m.group(1)
newsvg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" role="img" aria-label="Swami Vivekananda line portrait">\n  <image href="{data}" x="0" y="0" width="320" height="320" preserveAspectRatio="xMidYMid meet" style="filter:sepia(1) saturate(1.65) hue-rotate(348deg) brightness(.94) contrast(1.08);opacity:.94"/>\n</svg>\n'''
p.write_text(newsvg,encoding='utf-8')

# 2) Admin Dashboard: widen desktop main area so content heading aligns with header heading.
p=Path('admin-dashboard.html'); s=p.read_text(encoding='utf-8')
marker='<!-- v66.2 dashboard-width-fix -->'
if marker not in s:
    css='''\n<style id="v66-2-dashboard-width-fix">\n@media (min-width:1100px){\n main.wrap{max-width:none!important;width:auto!important;margin:0!important;padding-left:12px!important;padding-right:12px!important}\n main.wrap>.card{margin-left:0!important;margin-right:0!important}\n}\n</style>\n'''
    s=s.replace('</head>',marker+css+'</head>')
p.write_text(s,encoding='utf-8')

# 3) Leave Integrity card: physically move directly after Leave Reconciliation Control.
p=Path('admin-leave-editor.html'); s=p.read_text(encoding='utf-8')
integ=re.search(r'<section class="card quick-hide" id="leaveIntegritySection">.*?</section>',s,re.S)
if not integ: raise SystemExit('Integrity section not found')
integ_html=integ.group(0)
s=s[:integ.start()]+s[integ.end():]
rec=re.search(r'<section class="card quick-hide">\s*<div class="sectionTitle"><div><h2>🧭 Leave Reconciliation Control</h2>.*?</section>',s,re.S)
if not rec: raise SystemExit('Reconciliation section not found')
s=s[:rec.end()]+'\n\n'+integ_html+s[rec.end():]
p.write_text(s,encoding='utf-8')

# 4) Daily History: authoritative dated operational summary from leaveData(date), not stale snapshot statuses.
p=Path('v66-home.js'); s=p.read_text(encoding='utf-8')
marker='/* v66.2 authoritative Daily History override */'
if marker not in s:
    s += r'''\n\n/* v66.2 authoritative Daily History override */\nrenderHistory=function(){\n  const inp=E("historyDate");\n  if(!inp.value)inp.value=displayDate(todayKey());\n  const date=inputDate(inp.value),out=E("historyResult");\n  if(!date){out.innerHTML='<div class="warn">Enter the date as dd/mm/yyyy.</div>';return}\n  inp.value=displayDate(date);\n  const h=historyData()[date]||{};\n  const day=h.dayName||dayNameForDate(date);\n  const sts=(leaveData(date)||[]).filter(o=>o&&['full','half','od','special','vacant'].includes(String(o.type||'')));\n  const allots=Object.values((h.allotments||allotData(date)||{})).filter(x=>x&&(!x.day||x.day===day)).sort((a,b)=>Number(a.period||0)-Number(b.period||0));\n  const groups={leave:[],duty:[],operational:[]};\n  sts.forEach(o=>{if(['full','half'].includes(o.type))groups.leave.push(o);else if(['od','special'].includes(o.type))groups.duty.push(o);else if(o.type==='vacant')groups.operational.push(o)});\n  const block=(title,rows)=>'<h3>'+title+'</h3>'+(rows.length?rows.map(o=>{const t=teacherByEffectiveCode(o.code,date);return '<div>'+esc(t?t.name:o.code)+' ('+esc(o.code)+') — '+esc(statusLabel(o))+'</div>'}).join(''):'None');\n  out.innerHTML='<b>'+displayDate(date)+' · '+esc(day)+'</b>'+block('Regular Leave',groups.leave)+block('Duty Leave · OD / Special Assignment',groups.duty)+block('Operational Status · Vacant Position',groups.operational)+'<h3>Normal Proxy Allotments</h3>'+(allots.length?allots.map(x=>'<div>'+PL(x.period)+' — '+esc(x.name)+' ('+esc(x.code)+') — Regular '+esc(x.regular)+' + Proxy '+esc(x.proxyNumber)+' = '+esc(x.total)+'</div>').join(''):'None');\n};\n'''
p.write_text(s,encoding='utf-8')

# 5) My Leave & Duty Leave: use the exact authoritative source used by Approved Leave Register.
p=Path('v66-home-cloud.js'); s=p.read_text(encoding='utf-8')
marker='/* v66.2 authoritative personal leave history override */'
if marker not in s:
    s += r'''\n\n/* v66.2 authoritative personal leave history override */\nwindow.loadMyStatusCloud=async function(){\n const out=document.getElementById('myStatusResult'),msg=document.getElementById('myStatusMsg');\n const code=String(window.__vkvMyTeacherCode||'').trim();\n if(!code){if(out)out.innerHTML=window.myLinkMissingHtml?window.myLinkMissingHtml():'Staff link unavailable.';if(msg)msg.textContent='';return}\n if(msg)msg.textContent='Loading complete approved history…';\n const TYPES=new Set(['full','half','od','special']);\n const today=(()=>{const d=new Date(),p=n=>String(n).padStart(2,'0');return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}`})();\n const fmt=k=>{const m=String(k||'').match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);return m?`${m[3]}/${m[2]}/${m[1]}`:String(k||'')};\n const dateObj=k=>{const a=String(k||'').split('-').map(Number);return new Date(a[0]||1970,(a[1]||1)-1,a[2]||1)};\n const dateKey=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');\n const planDates=p=>{if(!p)return[];if(p.mode==='multiple')return[...new Set((p.dates||[]).filter(Boolean))].sort();const a=String(p.startDate||p.date||''),b=String(p.endDate||a);if(!a)return[];const z=[];for(let d=dateObj(a),e=dateObj(b);d<=e;d.setDate(d.getDate()+1))z.push(dateKey(d));return z};\n const state=d=>d>today?'Upcoming':d===today?'Current':'Past';\n const label=x=>x.type==='full'?'Full Leave':x.type==='half'?'Half Leave':x.type==='od'?'On Duty (OD)':x.type==='special'?'Special Assignment':String(x.type||'');\n const cat=x=>String(x.leaveCategory||x.category||'—');\n const units=x=>x.leaveUnits!=null?x.leaveUnits:(x.type==='half'?0.5:(x.type==='full'?1:'—'));\n const remarks=x=>String(x.note||x.remarks||x.reason||'—');\n try{\n   const source=await getDocs(collection(db,'dailyRecords')),rows=[],seen=new Set();\n   const add=(x,date,sourceName)=>{if(!x||!TYPES.has(String(x.type||''))||String(x.code||'')!==code||!date)return;const key=[date,x.type,cat(x),remarks(x),String(x.id||''),sourceName].join('|');if(seen.has(key))return;seen.add(key);rows.push({...x,date,_source:sourceName})};\n   source.forEach(d=>{const x=d.data()||{};if(d.id==='__leavePlans'){Object.values(x.plans||{}).forEach(p=>{if(!p||p.active===false||!TYPES.has(String(p.type||''))||String(p.code||'')!==code)return;planDates(p).forEach(date=>add(p,date,'Scheduled / Imported'))});return}const date=x.date||d.id;(x.statuses||[]).forEach(r=>add(r,date,'Daily'))});\n   rows.sort((a,b)=>String(b.date).localeCompare(String(a.date))||String(a.type).localeCompare(String(b.type)));\n   const leave=rows.filter(x=>['full','half'].includes(String(x.type))),duty=rows.filter(x=>['od','special'].includes(String(x.type)));\n   const table=(title,arr)=>{if(!arr.length)return '<h3>'+title+'</h3><div class="small">No approved '+(title.startsWith('Duty')?'Duty Leave':'Leave')+' history.</div>';return '<h3>'+title+'</h3><div class="table"><table><thead><tr><th>State</th><th>Status</th><th>Category</th><th>Leave Days</th><th>Date(s)</th><th>Remarks</th></tr></thead><tbody>'+arr.map(x=>'<tr><td>'+safe(state(x.date))+'</td><td>'+safe(label(x))+'</td><td>'+safe(['full','half'].includes(String(x.type))?cat(x):'—')+'</td><td>'+safe(['full','half'].includes(String(x.type))?units(x):'—')+'</td><td>'+safe(fmt(x.date))+'</td><td>'+safe(remarks(x))+'</td></tr>').join('')+'</tbody></table></div>'};\n   if(out)out.innerHTML='<div class="status ok"><b>'+rows.length+' approved dated record'+(rows.length===1?'':'s')+' available.</b> Leave and Duty Leave are shown separately.</div>'+table('Leave History',leave)+table('Duty Leave History',duty);\n   if(msg)msg.textContent='Updated';\n }catch(e){if(out)out.innerHTML='<div class="warn"><b>Could not load complete approved history.</b><br>'+safe(e&&e.message?e.message:String(e))+'</div>';if(msg)msg.textContent=''}\n};\n'''
p.write_text(s,encoding='utf-8')

print('Applied visible fixes')
