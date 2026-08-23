from pathlib import Path


def replace_once(path, old, new, marker):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if marker in text:
        print(f'{path}: already patched: {marker}')
        return
    if old not in text:
        raise SystemExit(f'{path}: exact patch anchor not found for {marker}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'{path}: patched: {marker}')


# -----------------------------------------------------------------------------
# 1. Admin Dashboard: load only lightweight Active Schedule + top metrics
#    immediately after master preload; preserve lazy heavy-table rendering.
# -----------------------------------------------------------------------------
replace_once(
    'admin-dashboard.html',
    """   showDashboard();
   // Preload master only when the browser is idle. Do not render heavy tables yet.
   const preload=()=>ensureMasterLoaded(false).catch(()=>{});
   if('requestIdleCallback' in window)requestIdleCallback(preload,{timeout:2500});else setTimeout(preload,1200);
""",
    """   showDashboard();
   // Preload master only when the browser is idle. Keep heavy tables lazy,
   // but update the lightweight dashboard schedule/metrics as soon as data arrives.
   const preload=()=>ensureMasterLoaded(false).then(renderDashboardSummary).catch(e=>renderDashboardLoadError(e));
   if('requestIdleCallback' in window)requestIdleCallback(preload,{timeout:2500});else setTimeout(preload,1200);
""",
    'renderDashboardLoadError(e)'
)

replace_once(
    'admin-dashboard.html',
    """function activeSchedule(){const id=master.activeScheduleProfileId||'normal',profiles=master.scheduleProfiles||{};return profiles[id]||profiles.normal||{name:'Normal Schedule'}}
function activeReplacements(date=todayKey()){return master.temporaryReplacements.filter(r=>r&&r.active!==false&&r.startDate&&r.endDate&&date>=r.startDate&&date<=r.endDate)}
function renderAll(){
 const ap=activeSchedule();$('activeScheduleStatus').innerHTML='<b>Active Schedule:</b> '+safe(ap.name||'Normal Schedule');
 $('mTeachers').textContent=master.teachers.length;$('mClasses').textContent=master.classes.length;$('mEntries').textContent=master.records.length;$('mTemp').textContent=activeReplacements().length;
""",
    """function activeSchedule(){const id=master.activeScheduleProfileId||'normal',profiles=master.scheduleProfiles||{};return profiles[id]||profiles.normal||{name:'Normal Schedule'}}
function activeReplacements(date=todayKey()){return master.temporaryReplacements.filter(r=>r&&r.active!==false&&r.startDate&&r.endDate&&date>=r.startDate&&date<=r.endDate)}
function renderDashboardSummary(){
 if(!master||!Array.isArray(master.records))return;
 const ap=activeSchedule(),status=$('activeScheduleStatus');
 if(status){status.className='status ok';status.innerHTML='<b>Active Schedule:</b> '+safe(ap.name||'Normal Schedule')}
 if($('mTeachers'))$('mTeachers').textContent=master.teachers.length;
 if($('mClasses'))$('mClasses').textContent=master.classes.length;
 if($('mEntries'))$('mEntries').textContent=master.records.length;
 if($('mTemp'))$('mTemp').textContent=activeReplacements().length;
}
function renderDashboardLoadError(e){
 const status=$('activeScheduleStatus');if(!status)return;
 status.className='status error';
 status.innerHTML='<b>Active schedule unavailable.</b> '+safe((e&&e.message)||e||'Please retry.');
}
function renderAll(){
 renderDashboardSummary();
""",
    'function renderDashboardSummary()'
)


# -----------------------------------------------------------------------------
# 2. Leave Rules: session-safe writes + local Staff Classification feedback.
# -----------------------------------------------------------------------------
replace_once(
    'admin-leave-rules.html',
    """    <div id=\"staffTable\" class=\"tablewrap\"></div>
    <div class=\"actions\"><button id=\"saveStaffCategories\" class=\"primary\">Save Staff Classifications</button></div>
""",
    """    <div id=\"staffTable\" class=\"tablewrap\"></div>
    <div class=\"actions\"><button id=\"saveStaffCategories\" class=\"primary\">Save Staff Classifications</button></div>
    <div id=\"staffCategorySaveStatus\" class=\"status info hide\" aria-live=\"polite\"></div>
""",
    'id="staffCategorySaveStatus"'
)

replace_once(
    'admin-leave-rules.html',
    """function resolutionState(x){if(x.resolutionStatus)return x.resolutionStatus;const r=String(x.reason||'');return(/admin-reviewed/i.test(r)&&/retained/i.test(r))?'pending':'final-accounting'}

async function saveRulesDoc(extra={}){
 await setDoc(doc(db,'leaveRules','current'),{categories:rules,entitlementPeriod,staffCategoryOverrides,updatedAt:serverTimestamp(),updatedByUid:user.uid,updatedByEmail:user.email||'',...extra},{merge:true});
}
""",
    """function resolutionState(x){if(x.resolutionStatus)return x.resolutionStatus;const r=String(x.reason||'');return(/admin-reviewed/i.test(r)&&/retained/i.test(r))?'pending':'final-accounting'}

async function requireAdminSession(){
 const current=auth.currentUser;
 if(!current)throw new Error('Your Admin session needs to be refreshed. Please sign in again. No changes have been saved.');
 const p=await getDoc(doc(db,'authorizedUsers',current.uid));
 if(!p.exists()||p.data().active!==true||String(p.data().role||'')!=='admin')throw new Error('Admin access is no longer available for this account. No changes have been saved.');
 user=current;
 return current;
}
async function saveRulesDoc(extra={}){
 const actor=await requireAdminSession();
 await setDoc(doc(db,'leaveRules','current'),{categories:rules,entitlementPeriod,staffCategoryOverrides,updatedAt:serverTimestamp(),updatedByUid:actor.uid,updatedByEmail:actor.email||'',...extra},{merge:true});
}
""",
    'async function requireAdminSession()'
)

replace_once(
    'admin-leave-rules.html',
    """$('saveStaffCategories').onclick=async()=>{
 const map={};document.querySelectorAll('[data-staff-code]').forEach(sel=>{map[sel.dataset.staffCode]=sel.value});staffCategoryOverrides=map;
 try{await saveRulesDoc();msg('Staff leave classifications saved.','ok');renderStaff()}catch(e){msg('Could not save staff classifications: '+(e.message||e),'error')}
};
""",
    """$('saveStaffCategories').onclick=async()=>{
 const btn=$('saveStaffCategories'),local=$('staffCategorySaveStatus');
 const map={};document.querySelectorAll('[data-staff-code]').forEach(sel=>{map[sel.dataset.staffCode]=sel.value});staffCategoryOverrides=map;
 btn.disabled=true;btn.textContent='Saving…';
 if(local){local.className='status info';local.textContent='Saving staff classifications…';local.classList.remove('hide')}
 try{
   await saveRulesDoc();
   if(local){local.className='status ok';local.textContent='✓ Staff classifications saved successfully.'}
   msg('Staff leave classifications saved.','ok');renderStaff();
 }catch(e){
   if(local){local.className='status error';local.textContent='Could not save staff classifications: '+(e.message||e)}
   msg('Could not save staff classifications: '+(e.message||e),'error');
 }finally{btn.disabled=false;btn.textContent='Save Staff Classifications'}
};
""",
    "const btn=$('saveStaffCategories'),local=$('staffCategorySaveStatus');"
)


# -----------------------------------------------------------------------------
# 3. Leave Master Editor: prevent null user.uid save crashes.
#    Revalidate current Firebase Admin immediately before the save transaction.
# -----------------------------------------------------------------------------
replace_once(
    'admin-leave-editor.html',
    """async function verify(u){
 const [p,m]=await Promise.all([
   getDoc(doc(db,'authorizedUsers',u.uid)),
   getDoc(doc(db,'master','current'))
 ]);
 if(!p.exists()||p.data().active!==true||String(p.data().role||'')!=='admin')throw new Error('Only the Principal/Admin account can open the Leave Master Editor.');
 if(!m.exists())throw new Error('Master timetable is not available.');
 master=m.data().data||m.data();
 teachers=[...(master.teachers||[]),...(master.nonTeachingStaff||[]).filter(x=>x&&x.active!==false).map(x=>({...x,name:x.name+' — Non-Teaching · '+(x.designation||'Staff')}))].sort((a,b)=>String(a.name).localeCompare(String(b.name)));
}
""",
    """async function verify(u){
 const [p,m]=await Promise.all([
   getDoc(doc(db,'authorizedUsers',u.uid)),
   getDoc(doc(db,'master','current'))
 ]);
 if(!p.exists()||p.data().active!==true||String(p.data().role||'')!=='admin')throw new Error('Only the Principal/Admin account can open the Leave Master Editor.');
 if(!m.exists())throw new Error('Master timetable is not available.');
 master=m.data().data||m.data();
 teachers=[...(master.teachers||[]),...(master.nonTeachingStaff||[]).filter(x=>x&&x.active!==false).map(x=>({...x,name:x.name+' — Non-Teaching · '+(x.designation||'Staff')}))].sort((a,b)=>String(a.name).localeCompare(String(b.name)));
}
async function requireAdminSession(){
 const current=auth.currentUser;
 if(!current)throw new Error('Your Admin session needs to be refreshed. Please sign in again. No leave record has been saved.');
 const p=await getDoc(doc(db,'authorizedUsers',current.uid));
 if(!p.exists()||p.data().active!==true||String(p.data().role||'')!=='admin')throw new Error('Admin access is no longer available for this account. No leave record has been saved.');
 user=current;
 return current;
}
""",
    "No leave record has been saved.');\n const p=await getDoc(doc(db,'authorizedUsers',current.uid));"
)

replace_once(
    'admin-leave-editor.html',
    """function makePlan(row,code,stamp,i){
 const id=`le_${code}_${row.date.replaceAll('-','')}_${stamp}_${i}`,p={id,code,type:row.type,mode:'single',startDate:row.date,endDate:row.date,active:true,source:'admin-leave-editor-v64',createdAtMs:Date.now(),updatedAtMs:Date.now(),updatedBy:user.uid,updatedByEmail:user.email||''};
""",
    """function makePlan(row,code,stamp,i,actor){
 const id=`le_${code}_${row.date.replaceAll('-','')}_${stamp}_${i}`,p={id,code,type:row.type,mode:'single',startDate:row.date,endDate:row.date,active:true,source:'admin-leave-editor-v64',createdAtMs:Date.now(),updatedAtMs:Date.now(),updatedBy:actor.uid,updatedByEmail:actor.email||''};
""",
    'function makePlan(row,code,stamp,i,actor)'
)

replace_once(
    'admin-leave-editor.html',
    """async function savePlans(rows,reason){
 const code=$('editTeacher').value;if(!code)throw new Error('Select the teacher.');
""",
    """async function savePlans(rows,reason){
 const actor=await requireAdminSession();
 const code=$('editTeacher').value;if(!code)throw new Error('Select the teacher.');
""",
    'const actor=await requireAdminSession();'
)

# Inside savePlans only, route audit/write identity through the verified actor.
p=Path('admin-leave-editor.html')
text=p.read_text(encoding='utf-8')
start=text.index('async function savePlans(rows,reason){')
end=text.index('\nfunction showSave',start)
block=text[start:end]
new_block=block.replace('makePlan(r,code,stamp,i)', 'makePlan(r,code,stamp,i,actor)').replace('user.uid','actor.uid').replace('user.email','actor.email')
if new_block != block:
    text=text[:start]+new_block+text[end:]
    p.write_text(text,encoding='utf-8')
    print('admin-leave-editor.html: patched verified actor through savePlans')
else:
    print('admin-leave-editor.html: savePlans actor routing already applied')

print('VKVTT v66.2 critical patch completed.')
