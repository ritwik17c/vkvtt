from pathlib import Path


def replace_once(path, old, new, marker):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if marker in s:
        print(f'{path}: already patched {marker}'); return
    if old not in s: raise SystemExit(f'{path}: anchor not found {marker}')
    p.write_text(s.replace(old,new,1),encoding='utf-8'); print(f'{path}: patched {marker}')

# -----------------------------------------------------------------------------
# Homepage terminology: Leave / Duty Leave / Operational Status.
# -----------------------------------------------------------------------------
for old,new,marker in [
 ('📝 Leave / OD / Special / Vacant','📝 Leave / Duty Leave / Vacant','Leave / Duty Leave / Vacant'),
 ('<h2>Leave / On Duty / Special Assignment / Vacant Position</h2>','<h2>Leave / Duty Leave / Operational Status</h2>','Leave / Duty Leave / Operational Status</h2>'),
 ("<button data-leave-type=\"od\" onclick=\"chooseStatus('od',this)\">On Duty</button>","<button data-leave-type=\"od\" onclick=\"chooseStatus('od',this)\">Duty Leave · On Duty</button>",'Duty Leave · On Duty'),
 ("<button data-leave-type=\"special\" onclick=\"chooseStatus('special',this)\">Special Assignment</button>","<button data-leave-type=\"special\" onclick=\"chooseStatus('special',this)\">Duty Leave · Special Assignment</button>",'Duty Leave · Special Assignment'),
 ("<button data-leave-type=\"vacant\" onclick=\"chooseStatus('vacant',this)\">Vacant Position</button>","<button data-leave-type=\"vacant\" onclick=\"chooseStatus('vacant',this)\">Operational Status · Vacant Position</button>",'Operational Status · Vacant Position'),
 ('<div class="proxyhead">4. Duration for On Duty / Special Assignment</div>','<div class="proxyhead">4. Duty Leave Duration · On Duty / Special Assignment</div>','Duty Leave Duration · On Duty / Special Assignment'),
 ('<button id="myStatusBtn" onclick="openMyStatus(this)">🗂 My Leave Record</button>','<button id="myStatusBtn" onclick="openMyStatus(this)">🗂 My Leave &amp; Duty Leave</button>','My Leave &amp; Duty Leave'),
 ('<h2>My Leave / OD / Special Assignment</h2>','<h2>My Leave &amp; Duty Leave</h2>','<h2>My Leave &amp; Duty Leave</h2>')
]: replace_once('index.html',old,new,marker)

# -----------------------------------------------------------------------------
# Leave Master: teacher Leave History must contain only Full/Half Leave.
# OD/Special remain in approved records and retain Full Edit/Archive.
# -----------------------------------------------------------------------------
p=Path('admin-leave-editor.html'); s=p.read_text(encoding='utf-8')
old="const records=teacherHistoryRecords(code),compact=compactTeacherHistory(records),today=todayIso(),ordered=[...compact].sort((a,b)=>{const af=a.dates.some(d=>d>=today),bf=b.dates.some(d=>d>=today);return Number(bf)-Number(af)||String(b.last).localeCompare(String(a.last))}).slice(0,10);"
new="const records=teacherHistoryRecords(code),leaveRecords=records.filter(x=>['full','half'].includes(String(x.type||''))),compact=compactTeacherHistory(leaveRecords),today=todayIso(),ordered=[...compact].sort((a,b)=>{const af=a.dates.some(d=>d>=today),bf=b.dates.some(d=>d>=today);return Number(bf)-Number(af)||String(b.last).localeCompare(String(a.last))}).slice(0,10);"
if 'leaveRecords=records.filter' not in s:
    if old not in s: raise SystemExit('admin-leave-editor.html: selected history records anchor not found')
    s=s.replace(old,new,1)
    s=s.replace("...records.map(x=>String(x.leaveCategory||'').toUpperCase()).filter(Boolean)","...leaveRecords.map(x=>String(x.leaveCategory||'').toUpperCase()).filter(Boolean)",1)
    s=s.replace("<span class=\"pill\">${records.length} saved dated record${records.length===1?'':'s'}</span>","<span class=\"pill\">${leaveRecords.length} saved dated leave record${leaveRecords.length===1?'':'s'}</span>",1)
    s=s.replace("No approved dated leave history for this teacher.","No approved Regular / Conditional Leave history for this teacher. Duty Leave is listed separately in Approved Records.",1)
# Add system classification pill on Approved Records cards without restructuring edit actions.
needle="${safe(statusText(p))} · ${safe(dateText)}"
if 'recordSystemLabel(p)' not in s:
    helper="""function recordSystemLabel(p){const t=String(p&&p.type||'');return(t==='od'||t==='special')?'Duty Leave':(t==='full'||t==='half')?'Leave':'Operational Status'}
"""
    pos=s.find('function filteredRecords(){')
    if pos<0: raise SystemExit('admin-leave-editor.html: filteredRecords anchor not found')
    s=s[:pos]+helper+s[pos:]
    if needle in s:s=s.replace(needle,"<span class=\"pill\">${safe(recordSystemLabel(p))}</span> · ${safe(statusText(p))} · ${safe(dateText)}",1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# Approved Register: explicit Leave vs Duty Leave sections for teacher history.
# -----------------------------------------------------------------------------
replace_once('admin-leave.html','VKV Nalbari · Approved Leave Register','VKV Nalbari · Approved Leave & Duty Leave Register','Approved Leave & Duty Leave Register')
replace_once('admin-leave.html','Leave / OD / Special Assignment · Cloud v66.0','Leave · Duty Leave · Cloud v66.2','Leave · Duty Leave · Cloud v66.2')
replace_once('admin-leave.html','This page contains only school-approved Leave, OD and Special Assignment records. It does not expose draft proxy allotments.','This page contains school-approved Leave and Duty Leave records. Leave balances and Duty Leave remain separate; draft proxy allotments are not exposed.','Leave balances and Duty Leave remain separate')
replace_once('admin-leave.html','<option value="">Leave + OD + Special</option><option value="leave">Leave only</option><option value="od">OD only</option><option value="special">Special Assignment only</option>','<option value="">Leave + Duty Leave</option><option value="leave">Leave only</option><option value="duty">Duty Leave only</option><option value="od">On Duty only</option><option value="special">Special Assignment only</option>','<option value="duty">Duty Leave only</option>')

p=Path('admin-leave.html'); s=p.read_text(encoding='utf-8')
start=s.find('function renderTeacher(){')
end=s.find("$('viewTeacher').onclick=renderTeacher",start)
if start<0 or end<0: raise SystemExit('admin-leave.html: renderTeacher boundaries not found')
if 'function teacherRecordTable(' not in s:
    replacement="""function teacherRecordTable(title,rows){
 if(!rows.length)return `<h3>${title}</h3><div class="empty">No ${title.toLowerCase()} records.</div>`;
 const merged=mergeConsecutiveRecords(rows),stateName=x=>{const st=recordState(x);return st==='current'?'Current':st==='upcoming'?'Upcoming':'Past'};
 return `<h3>${title}</h3><div class="tablewrap"><table><thead><tr><th>State</th><th>Status</th><th>Category</th><th>Leave Days</th><th>Date(s)</th><th>Duration</th><th>Remarks</th></tr></thead><tbody>${merged.map(x=>{const st=recordState(x);return `<tr><td><span class="pill ${st}">${stateName(x)}</span></td><td>${safe(statusLabel(x))}</td><td>${safe(mergedCategoryText(x))}</td><td>${safe(['full','half'].includes(String(x.type))?(x._displayUnits||'—'):'—')}</td><td>${safe(mergedDateText(x))}${x._items.length>1?`<br><span class="help">${x._dates.length} consecutive dates · one approval</span>`:''}</td><td>${safe(durationText(x))}</td><td>${safe((x._remarks||[]).join(' · ')||'—')}</td></tr>`}).join('')}</tbody></table></div>`;
}
function renderTeacher(){
 const code=$('teacherPick').value,kind=$('teacherType').value;if(!code){$('teacherResult').innerHTML='<div class="empty">Select a teacher.</div>';return}
 let rows=allTeacherRecords(code);if(kind==='leave')rows=rows.filter(x=>['full','half'].includes(String(x.type)));else if(kind==='duty')rows=rows.filter(x=>['od','special'].includes(String(x.type)));else if(kind)rows=rows.filter(x=>String(x.type)===kind);
 const t=teacherByCode(code)||{name:code,code},leaveRows=rows.filter(x=>['full','half'].includes(String(x.type))),dutyRows=rows.filter(x=>['od','special'].includes(String(x.type))),cats={VL:0,EL:0,CL:0,SEL:0,EOL:0,MATERNITY:0};
 for(const x of leaveRows)if(cats.hasOwnProperty(String(x.leaveCategory||'').toUpperCase()))cats[String(x.leaveCategory).toUpperCase()]+=Number(x.leaveUnits||0);
 const metrics='<div class="metrics">'+Object.entries(cats).map(([k,v])=>`<div class="metric"><b>${safe(v||0)}</b><span>${safe(catLabel(k))} used</span></div>`).join('')+'</div>';
 const legacyRows=legacyAccounting.filter(x=>String(x.teacherCode)===String(code)),legacyHtml=legacyRows.length?`<h3>Legacy Leave Accounting · Non-Dated</h3><div class="tablewrap"><table><thead><tr><th>Month</th><th>Category</th><th>Units</th><th>Reason</th></tr></thead><tbody>${legacyRows.map(x=>`<tr><td>${safe(x.month||'—')}</td><td>${safe(catLabel(x.category))}</td><td>${safe(x.units||'—')}</td><td>${safe(x.reason||'Legacy accounting')}</td></tr>`).join('')}</tbody></table></div>`:'';
 $('teacherResult').innerHTML=`<div class="status ok"><b>${safe(t.name)} (${safe(code)})</b> · ${leaveRows.length} Leave record${leaveRows.length===1?'':'s'} · ${dutyRows.length} Duty Leave record${dutyRows.length===1?'':'s'}.</div>${metrics}${teacherRecordTable('Leave History',leaveRows)}${teacherRecordTable('Duty Leave History',dutyRows)}${legacyHtml}`;
}
"""
    s=s[:start]+replacement+s[end:]
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# My Area: separate Leave History and Duty Leave History.
# -----------------------------------------------------------------------------
p=Path('v66-home-cloud.js'); s=p.read_text(encoding='utf-8')
start=s.find("   const groups={current:[],upcoming:[],past:[]};items.forEach(x=>groups[stateOf(x)].push(x));",s.find('window.loadMyStatusCloud'))
end=s.find("   if(msg)msg.textContent='Updated';",start)
if start<0 or end<0: raise SystemExit('v66-home-cloud.js: My Status grouping boundaries not found')
if "categorySection('Leave History'" not in s:
    new="""   const leaveItems=items.filter(x=>['full','half'].includes(String(x.type||''))),dutyItems=items.filter(x=>['od','special'].includes(String(x.type||'')));
   const stateLabel=x=>{const s=stateOf(x);return s==='current'?'Current':s==='upcoming'?'Upcoming':'Past'};
   const categorySection=(title,arr,empty)=>'<h3 style="margin:16px 0 7px">'+title+'</h3>'+(arr.length?'<div class="table"><table><tr><th>State</th><th>Status</th><th>Category</th><th>Leave Days</th><th>Date(s)</th><th>Remarks</th></tr>'+arr.sort((a,b)=>dateSortKey(b).localeCompare(dateSortKey(a))).map(x=>'<tr><td>'+safe(stateLabel(x))+'</td><td>'+safe(labelOf(x))+'</td><td>'+safe(x.leaveCategory?leaveCategoryLabel(x.leaveCategory):'—')+'</td><td>'+safe((x.type==='full'||x.type==='half')?(x.leaveUnits||'—'):'—')+'</td><td>'+safe(dateText(x))+'</td><td>'+safe(x.note||'—')+'</td></tr>').join('')+'</table></div>':'<div class="small">'+empty+'</div>');
   if(!items.length){
     out.innerHTML='<div class="slotComplete">No approved Leave or Duty Leave record is available for you yet.</div><div class="small">If an older approved record is missing, the Admin can run “Sync My Area Records” once from User Access & Roles.</div>';
   }else{
     out.innerHTML='<div class="slotComplete"><b>'+items.length+' approved record'+(items.length===1?'':'s')+' available.</b> Leave and Duty Leave are shown separately.</div>'+categorySection('Leave History',leaveItems,'No approved Leave history.')+categorySection('Duty Leave History',dutyItems,'No approved Duty Leave history.');
   }
"""
    s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# Core status labels: identify Duty Leave / Operational Status without changing
# stored status codes or proxy logic.
# -----------------------------------------------------------------------------
p=Path('v66-home.js'); s=p.read_text(encoding='utf-8')
old="function statusLabel(o){if(!o)return\"\";if(o.type===\"full\")return \"Full Leave\"+(o.leaveCategory?\" · \"+leaveCategoryLabel(o.leaveCategory):\"\");if(o.type===\"half\")return \"Half Leave · P5–P8\"+(o.leaveCategory?\" · \"+leaveCategoryLabel(o.leaveCategory):\"\");if(o.type===\"od\")return \"On Duty\"+(o.duration?\" · \"+dutyDurationLabel(o):\"\");if(o.type===\"special\")return \"Special Assignment\"+(o.duration?\" · \"+dutyDurationLabel(o):\"\");if(o.type===\"vacant\")return \"Vacant Position\";return o.type||\"\"}"
new="function statusLabel(o){if(!o)return\"\";if(o.type===\"full\")return \"Full Leave\"+(o.leaveCategory?\" · \"+leaveCategoryLabel(o.leaveCategory):\"\");if(o.type===\"half\")return \"Half Leave · P5–P8\"+(o.leaveCategory?\" · \"+leaveCategoryLabel(o.leaveCategory):\"\");if(o.type===\"od\")return \"Duty Leave · On Duty\"+(o.duration?\" · \"+dutyDurationLabel(o):\"\");if(o.type===\"special\")return \"Duty Leave · Special Assignment\"+(o.duration?\" · \"+dutyDurationLabel(o):\"\");if(o.type===\"vacant\")return \"Operational Status · Vacant Position\";return o.type||\"\"}"
if old in s:s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

print('VKVTT v66.2 Duty Leave separation patch completed.')
