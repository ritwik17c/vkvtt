from pathlib import Path

# Replace malformed literal \\n tail with real JavaScript newlines.
p=Path('v66-home.js'); s=p.read_text(encoding='utf-8')
marker='/* v66.2 authoritative Daily History override */'
base=s.split(marker)[0].rstrip('\\n\\r\\ \\')
block='''

/* v66.2 authoritative Daily History override */
renderHistory=function(){
  const inp=E("historyDate");
  if(!inp.value)inp.value=displayDate(todayKey());
  const date=inputDate(inp.value),out=E("historyResult");
  if(!date){out.innerHTML='<div class="warn">Enter the date as dd/mm/yyyy.</div>';return}
  inp.value=displayDate(date);
  const h=historyData()[date]||{};
  const day=h.dayName||dayNameForDate(date);
  const sts=(leaveData(date)||[]).filter(o=>o&&['full','half','od','special','vacant'].includes(String(o.type||'')));
  const allots=Object.values((h.allotments||allotData(date)||{})).filter(x=>x&&(!x.day||x.day===day)).sort((a,b)=>Number(a.period||0)-Number(b.period||0));
  const groups={leave:[],duty:[],operational:[]};
  sts.forEach(o=>{if(['full','half'].includes(o.type))groups.leave.push(o);else if(['od','special'].includes(o.type))groups.duty.push(o);else if(o.type==='vacant')groups.operational.push(o)});
  const block=(title,rows)=>'<h3>'+title+'</h3>'+(rows.length?rows.map(o=>{const t=teacherByEffectiveCode(o.code,date);return '<div>'+esc(t?t.name:o.code)+' ('+esc(o.code)+') — '+esc(statusLabel(o))+'</div>'}).join(''):'None');
  out.innerHTML='<b>'+displayDate(date)+' · '+esc(day)+'</b>'+block('Regular Leave',groups.leave)+block('Duty Leave · OD / Special Assignment',groups.duty)+block('Operational Status · Vacant Position',groups.operational)+'<h3>Normal Proxy Allotments</h3>'+(allots.length?allots.map(x=>'<div>'+PL(x.period)+' — '+esc(x.name)+' ('+esc(x.code)+') — Regular '+esc(x.regular)+' + Proxy '+esc(x.proxyNumber)+' = '+esc(x.total)+'</div>').join(''):'None');
};
'''
p.write_text(base+block,encoding='utf-8')

p=Path('v66-home-cloud.js'); s=p.read_text(encoding='utf-8')
marker='/* v66.2 authoritative personal leave history override */'
base=s.split(marker)[0].rstrip('\\n\\r\\ \\')
block='''

/* v66.2 authoritative personal leave history override */
window.loadMyStatusCloud=async function(){
 const out=document.getElementById('myStatusResult'),msg=document.getElementById('myStatusMsg');
 const code=String(window.__vkvMyTeacherCode||'').trim();
 if(!code){if(out)out.innerHTML=window.myLinkMissingHtml?window.myLinkMissingHtml():'Staff link unavailable.';if(msg)msg.textContent='';return}
 if(msg)msg.textContent='Loading complete approved history…';
 const TYPES=new Set(['full','half','od','special']);
 const today=(()=>{const d=new Date(),p=n=>String(n).padStart(2,'0');return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}`})();
 const fmt=k=>{const m=String(k||'').match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);return m?`${m[3]}/${m[2]}/${m[1]}`:String(k||'')};
 const dateObj=k=>{const a=String(k||'').split('-').map(Number);return new Date(a[0]||1970,(a[1]||1)-1,a[2]||1)};
 const dateKey=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
 const planDates=p=>{if(!p)return[];if(p.mode==='multiple')return[...new Set((p.dates||[]).filter(Boolean))].sort();const a=String(p.startDate||p.date||''),b=String(p.endDate||a);if(!a)return[];const z=[];for(let d=dateObj(a),e=dateObj(b);d<=e;d.setDate(d.getDate()+1))z.push(dateKey(d));return z};
 const state=d=>d>today?'Upcoming':d===today?'Current':'Past';
 const label=x=>x.type==='full'?'Full Leave':x.type==='half'?'Half Leave':x.type==='od'?'On Duty (OD)':x.type==='special'?'Special Assignment':String(x.type||'');
 const cat=x=>String(x.leaveCategory||x.category||'—');
 const units=x=>x.leaveUnits!=null?x.leaveUnits:(x.type==='half'?0.5:(x.type==='full'?1:'—'));
 const remarks=x=>String(x.note||x.remarks||x.reason||'—');
 try{
   const source=await getDocs(collection(db,'dailyRecords')),rows=[],seen=new Set();
   const add=(x,date,sourceName)=>{if(!x||!TYPES.has(String(x.type||''))||String(x.code||'')!==code||!date)return;const key=[date,x.type,cat(x),remarks(x),String(x.id||''),sourceName].join('|');if(seen.has(key))return;seen.add(key);rows.push({...x,date,_source:sourceName})};
   source.forEach(d=>{const x=d.data()||{};if(d.id==='__leavePlans'){Object.values(x.plans||{}).forEach(p=>{if(!p||p.active===false||!TYPES.has(String(p.type||''))||String(p.code||'')!==code)return;planDates(p).forEach(date=>add(p,date,'Scheduled / Imported'))});return}const date=x.date||d.id;(x.statuses||[]).forEach(r=>add(r,date,'Daily'))});
   rows.sort((a,b)=>String(b.date).localeCompare(String(a.date))||String(a.type).localeCompare(String(b.type)));
   const leave=rows.filter(x=>['full','half'].includes(String(x.type))),duty=rows.filter(x=>['od','special'].includes(String(x.type)));
   const table=(title,arr)=>{if(!arr.length)return '<h3>'+title+'</h3><div class="small">No approved '+(title.startsWith('Duty')?'Duty Leave':'Leave')+' history.</div>';return '<h3>'+title+'</h3><div class="table"><table><thead><tr><th>State</th><th>Status</th><th>Category</th><th>Leave Days</th><th>Date(s)</th><th>Remarks</th></tr></thead><tbody>'+arr.map(x=>'<tr><td>'+safe(state(x.date))+'</td><td>'+safe(label(x))+'</td><td>'+safe(['full','half'].includes(String(x.type))?cat(x):'—')+'</td><td>'+safe(['full','half'].includes(String(x.type))?units(x):'—')+'</td><td>'+safe(fmt(x.date))+'</td><td>'+safe(remarks(x))+'</td></tr>').join('')+'</tbody></table></div>'};
   if(out)out.innerHTML='<div class="status ok"><b>'+rows.length+' approved dated record'+(rows.length===1?'':'s')+' available.</b> Leave and Duty Leave are shown separately.</div>'+table('Leave History',leave)+table('Duty Leave History',duty);
   if(msg)msg.textContent='Updated';
 }catch(e){if(out)out.innerHTML='<div class="warn"><b>Could not load complete approved history.</b><br>'+safe(e&&e.message?e.message:String(e))+'</div>';if(msg)msg.textContent=''}
};
'''
p.write_text(base+block,encoding='utf-8')
print('Tail syntax repaired')
