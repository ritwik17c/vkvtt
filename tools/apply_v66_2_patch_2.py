from pathlib import Path


def replace_once(path, old, new, marker):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if marker in text:
        print(f'{path}: already patched: {marker}'); return
    if old not in text:
        raise SystemExit(f'{path}: anchor not found: {marker}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')
    print(f'{path}: patched: {marker}')

# -----------------------------------------------------------------------------
# index.html: teacher-change snapshot/warning panel + dynamic category host.
# -----------------------------------------------------------------------------
replace_once(
 'index.html',
 '<div class="controls"><div><label>Teacher</label><select id="leaveTeacher"><option value="">Select...</option></select></div></div>',
 '<div class="controls"><div><label>Teacher</label><select id="leaveTeacher" onchange="onHomepageLeaveTeacherChange()"><option value="">Select...</option></select></div></div>\n<div id="homepageLeaveSnapshot" class="proxycard" style="display:none" aria-live="polite"></div>',
 'id="homepageLeaveSnapshot"'
)
replace_once(
 'index.html',
 '<div class="leaveBtns categoryQuickBtns" style="margin-top:10px">',
 '<div id="leaveCategoryQuickBtns" class="leaveBtns categoryQuickBtns" style="margin-top:10px">',
 'id="leaveCategoryQuickBtns"'
)
replace_once(
 'index.html',
 '<div><label>Leave Category</label><select id="leaveCategory" onchange="refreshLeaveCategoryUi(false)"><option value="">Select…</option><option value="VL">VL</option><option value="EL">EL</option><option value="CL">CL</option><option value="SEL">SEL</option><option value="EOL">EOL</option><option value="MATERNITY">Maternity Leave</option></select></div>\n<div><label>Leave Days</label><input id="leaveUnits" type="number" min="0" step="0.5" placeholder="Auto calculated"><div class="small">Auto-calculated from the selected dates; you may correct it when school leave-counting rules require a different figure.</div></div>',
 '<div><label>Leave Category</label><select id="leaveCategory" onchange="refreshLeaveCategoryUi(false)"><option value="">Select…</option></select></div>\n<div><label>Leave Days</label><input id="leaveUnits" type="number" min="0" step="0.5" placeholder="Auto calculated" oninput="renderHomepageLeaveRuleWarning()"><div class="small">Auto-calculated from the selected dates; you may correct it when school leave-counting rules require a different figure.</div></div>',
 'oninput="renderHomepageLeaveRuleWarning()"'
)
replace_once(
 'index.html',
 '<div class="actions" style="margin-top:8px"><button type="button" onclick="autoFillLeaveUnits()">↻ Auto Calculate Leave Days</button><span id="leaveAccountHint" class="small"></span></div>\n</div>',
 '<div class="actions" style="margin-top:8px"><button type="button" onclick="autoFillLeaveUnits()">↻ Auto Calculate Leave Days</button><span id="leaveAccountHint" class="small"></span></div>\n<div id="homepageLeaveRuleWarning" class="small" style="margin-top:9px" aria-live="polite"></div>\n</div>',
 'id="homepageLeaveRuleWarning"'
)
replace_once(
 'index.html',
 'Loading today’s Leave / OD / Assignment summary…',
 'Loading today’s Leave / Duty Leave / Operational Status summary…',
 'Duty Leave / Operational Status summary'
)

# -----------------------------------------------------------------------------
# Firestore: status editors may READ leave rules; only Admin can write them.
# -----------------------------------------------------------------------------
replace_once(
 'FIRESTORE_RULES_V66_REPLACE_ALL.txt',
 """    match /leaveRules/{documentId} {
      allow read, create, update: if isAdmin();
      allow delete: if false;
    }
""",
 """    match /leaveRules/{documentId} {
      allow read: if isStatusEditor();
      allow create, update: if isAdmin();
      allow delete: if false;
    }
""",
 'allow read: if isStatusEditor();'
)

# -----------------------------------------------------------------------------
# Leave Master wording correction requested by user.
# -----------------------------------------------------------------------------
replace_once(
 'admin-leave-editor.html',
 'Live calculation for all Full/Half Date Rows and Date-Range Rows in this transaction.',
 'Leave calculation for all Full/Half Date Rows and Date-Range Rows in this transaction.',
 'Leave calculation for all Full/Half Date Rows'
)

# -----------------------------------------------------------------------------
# v66-home-cloud.js: one cached source for homepage teacher leave snapshot.
# Reads the same dailyRecords + leaveRules used by operational entry; Admin also
# receives legacy accounting for exact legacy-aware balances. No invented dates.
# -----------------------------------------------------------------------------
replace_once(
 'v66-home-cloud.js',
 "let currentUser=null,currentProfile=null,todayPollTimer=null,publishedPollTimer=null,leavePlanPollTimer=null,schedulePollTimer=null,accessCheckTimer=null,cloudHydrating=false,cloudWriting=false,syncTimer=null,coreWrapped=false;",
 "let currentUser=null,currentProfile=null,todayPollTimer=null,publishedPollTimer=null,leavePlanPollTimer=null,schedulePollTimer=null,accessCheckTimer=null,cloudHydrating=false,cloudWriting=false,syncTimer=null,coreWrapped=false,homepageLeaveContextCache=null;",
 'homepageLeaveContextCache=null'
)

anchor="""const LEAVE_PLAN_DOC='__leavePlans';
const PERSONAL_STATUS_TYPES=new Set(['full','half','od','special']);
"""
insert="""const LEAVE_PLAN_DOC='__leavePlans';
const PERSONAL_STATUS_TYPES=new Set(['full','half','od','special']);

window.loadHomepageLeaveContext=async function(code,force=false){
 if(!currentUser||!canEditStatus())throw new Error('Admin or Manager access is required to view staff leave balances.');
 const now=Date.now();
 if(!force&&homepageLeaveContextCache&&now-homepageLeaveContextCache.at<30000)return homepageLeaveContextCache.data;
 const [ruleSnap,dailySnap]=await Promise.all([getDoc(doc(db,'leaveRules','current')),getDocs(collection(db,'dailyRecords'))]);
 const rd=ruleSnap.exists()?(ruleSnap.data()||{}):{},scheduled=[],manual=[];
 dailySnap.forEach(d=>{
   const data=d.data()||{};
   if(d.id===LEAVE_PLAN_DOC){Object.values(data.plans||{}).forEach(p=>{if(p&&p.active!==false)scheduled.push({...p})});return}
   const date=data.date||d.id;
   (data.statuses||[]).forEach(x=>{if(x)manual.push({...x,_date:date})});
 });
 let legacy=[],legacyAvailable=false;
 if(isAdmin()){
   try{const ls=await getDocs(collection(db,'legacyLeaveAccounting'));ls.forEach(d=>legacy.push({id:d.id,...(d.data()||{})}));legacyAvailable=true}catch(e){console.warn('Homepage legacy leave context:',e)}
 }
 const data={categories:Array.isArray(rd.categories)?rd.categories:[],entitlementPeriod:rd.entitlementPeriod||null,staffCategoryOverrides:rd.staffCategoryOverrides||{},scheduled,manual,legacy,legacyAvailable,loadedAt:now};
 homepageLeaveContextCache={at:now,data};
 return data;
};
window.invalidateHomepageLeaveContext=()=>{homepageLeaveContextCache=null};
"""
replace_once('v66-home-cloud.js',anchor,insert,'window.loadHomepageLeaveContext=async function')

# Invalidate the cached balance after scheduled-plan and daily-status writes.
p=Path('v66-home-cloud.js'); text=p.read_text(encoding='utf-8')
if 'homepageLeaveContextCache=null;\n   cloudSync.textContent=\'Synced\';' not in text:
    old="""   cloudSync.textContent='Synced';
 }finally{
"""
    new="""   homepageLeaveContextCache=null;
   cloudSync.textContent='Synced';
 }finally{
"""
    if old not in text: raise SystemExit('v66-home-cloud.js: pushToday cache anchor not found')
    text=text.replace(old,new,1)
# saveScheduledStatusPlan block: invalidate immediately after write/sync before cache/render.
needle=""" await setDoc(ref,{date:LEAVE_PLAN_DOC,dayName:'Scheduled Leave / Status Plans',plans,updatedAt:serverTimestamp(),updatedBy:currentUser.uid,updatedByEmail:currentUser.email||''},{merge:false});
"""
if needle in text and 'homepageLeaveContextCache=null;\n cacheLeavePlans(plans);' not in text:
    text=text.replace(needle,needle+' homepageLeaveContextCache=null;\n',1)
p.write_text(text,encoding='utf-8')

# -----------------------------------------------------------------------------
# v66-home.js: dynamic configured leave categories + teacher snapshot + live
# balance/exhaustion/applicability warning + save-time validation.
# -----------------------------------------------------------------------------
insert_after="""function leaveCategoryLabel(v){return LEAVE_CATEGORY_LABELS[String(v||\"\").toUpperCase()]||String(v||\"\")}
"""
addition="""function leaveCategoryLabel(v){const code=String(v||'').toUpperCase(),ctx=window.__homepageLeaveContext,r=ctx&&Array.isArray(ctx.categories)?ctx.categories.find(x=>String(x.code||'').toUpperCase()===code):null;return r?(r.name||r.code):(LEAVE_CATEGORY_LABELS[code]||String(v||''))}
let homepageLeaveContextCode='',homepageLeaveContextLoading=false;
function homePeriodValid(ctx){const p=ctx&&ctx.entitlementPeriod;return !!(p&&/^\\d{4}-\\d{2}-\\d{2}$/.test(String(p.startDate||''))&&/^\\d{4}-\\d{2}-\\d{2}$/.test(String(p.endDate||''))&&p.startDate<=p.endDate)}
function homePeriodKey(ctx){const p=ctx&&ctx.entitlementPeriod;return homePeriodValid(ctx)?String(p.key||`${p.startDate}__${p.endDate}`):''}
function homeRule(code,ctx=window.__homepageLeaveContext){code=String(code||'').toUpperCase();return ctx&&Array.isArray(ctx.categories)?ctx.categories.find(r=>String(r.code||'').toUpperCase()===code)||null:null}
function homeActiveRules(ctx=window.__homepageLeaveContext){return ctx&&Array.isArray(ctx.categories)?ctx.categories.filter(r=>r&&r.active!==false&&String(r.code||'').trim()&&(r.unlimited===true||(Number.isFinite(Number(r.max))&&Number(r.max)>0))).sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.code).localeCompare(String(b.code))):[]}
function homeStaffCategory(code,ctx=window.__homepageLeaveContext){
 const t=teacherByEffectiveCode(code)||permanentTeacherByCode(code)||nonTeachingStaffByCode(code);if(!t)return'unknown';
 const explicit=String(t.leaveStaffCategory||'');if(['teaching','administrative','non-teaching'].includes(explicit))return explicit;
 const ov=String(ctx&&ctx.staffCategoryOverrides&&ctx.staffCategoryOverrides[code]||'');if(['teaching','administrative','non-teaching'].includes(ov))return ov;
 if(t.nonTeaching||nonTeachingStaffByCode(code))return'non-teaching';if(permanentTeacherByCode(code))return'teaching';return'unknown';
}
function homeRuleApplies(rule,staffCat){if(staffCat==='teaching')return rule.teaching===true;if(staffCat==='administrative')return rule.admin===true;if(staffCat==='non-teaching')return rule.nonTeaching===true;return false}
function homePlanDates(p){if(!p)return[];if(p.mode==='multiple')return [...new Set((p.dates||[]).filter(Boolean))].sort();const a=String(p.startDate||p.date||''),b=String(p.endDate||a);if(!a)return[];const out=[];for(let d=dateFromKey(a),last=dateFromKey(b);d<=last;d.setDate(d.getDate()+1))out.push(dateKeyFromDate(d));return out}
function homeLegacyState(x,ctx){const key=homePeriodKey(ctx);if(!key)return'unknown';const assigned=String(x.entitlementPeriodKey||'');if(assigned)return assigned===key?'current':'other';const p=ctx.entitlementPeriod;if(x.vlHasVerifiedRange===true&&x.vlFromDate&&x.vlToDate){if(x.vlFromDate>=p.startDate&&x.vlToDate<=p.endDate)return'current';if(x.vlToDate<p.startDate||x.vlFromDate>p.endDate)return'other'}return'unknown'}
function homeLeaveUsage(code,category,ctx=window.__homepageLeaveContext){
 const cat=String(category||'').toUpperCase(),p=ctx&&ctx.entitlementPeriod;let dated=0,legacyAssigned=0,legacyUnassigned=0;
 if(homePeriodValid(ctx)){
   for(const x of (ctx.scheduled||[])){if(String(x.code)!==String(code)||!['full','half'].includes(x.type)||String(x.leaveCategory||'').toUpperCase()!==cat)continue;const per=x.type==='half'?0.5:1;for(const d of homePlanDates(x))if(d>=p.startDate&&d<=p.endDate)dated+=per}
   for(const x of (ctx.manual||[])){if(String(x.code)!==String(code)||!['full','half'].includes(x.type)||String(x.leaveCategory||'').toUpperCase()!==cat)continue;const d=String(x._date||'');if(d>=p.startDate&&d<=p.endDate)dated+=x.type==='half'?0.5:1}
 }
 if(ctx&&ctx.legacyAvailable){for(const x of (ctx.legacy||[])){if(x&&x.active!==false&&String(x.teacherCode)===String(code)&&String(x.category||'').toUpperCase()===cat&&x.resolutionStatus!=='resolved-dated'){const state=homeLegacyState(x,ctx),u=Number(x.units||0);if(state==='current')legacyAssigned+=u;else if(state==='unknown')legacyUnassigned+=u}}
 }
 return{dated:Math.round(dated*2)/2,legacyAssigned:Math.round(legacyAssigned*2)/2,legacyUnassigned:Math.round(legacyUnassigned*2)/2,used:Math.round((dated+legacyAssigned)*2)/2};
}
function populateHomepageLeaveCategories(ctx,existing=''){
 const select=E('leaveCategory'),quick=E('leaveCategoryQuickBtns');if(!select||!quick)return;
 const current=String(existing||select.value||'').toUpperCase(),rules=homeActiveRules(ctx),codes=rules.map(r=>String(r.code||'').toUpperCase());
 if(current&&!codes.includes(current)){const r=homeRule(current,ctx);if(r)codes.push(current)}
 select.innerHTML='<option value="">Select…</option>'+codes.map(c=>`<option value="${esc(c)}">${esc(leaveCategoryLabel(c))}${homeRule(c,ctx)?.active===false?' · Historical':''}</option>`).join('');
 quick.innerHTML=rules.map(r=>{const c=String(r.code||'').toUpperCase();return `<button data-leave-category="${esc(c)}" onclick="chooseLeaveCategory('${esc(c)}',this)">${esc(r.name||c)}</button>`}).join('');
 if(codes.includes(current))select.value=current;
}
function homeHistoryItems(code,ctx=window.__homepageLeaveContext){
 const out=[];for(const x of (ctx?.scheduled||[]))if(String(x.code)===String(code)&&['full','half'].includes(x.type))out.push({...x,_dates:homePlanDates(x)});for(const x of (ctx?.manual||[]))if(String(x.code)===String(code)&&['full','half'].includes(x.type))out.push({...x,_dates:[x._date]});return out.sort((a,b)=>String((b._dates||[]).slice(-1)[0]||'').localeCompare(String((a._dates||[]).slice(-1)[0]||'')))}
function renderHomepageLeaveSnapshot(){
 const box=E('homepageLeaveSnapshot'),code=E('leaveTeacher')?.value,ctx=window.__homepageLeaveContext;if(!box)return;if(!code){box.style.display='none';box.innerHTML='';return}box.style.display='block';
 if(homepageLeaveContextLoading){box.innerHTML='<div class="proxyhead">Leave Snapshot</div><div class="small">Loading leave history and balances…</div>';return}
 if(!ctx||homepageLeaveContextCode!==code){box.innerHTML='<div class="proxyhead">Leave Snapshot</div><div class="small">Leave information is not loaded yet.</div>';return}
 const t=teacherByEffectiveCode(code)||{name:code},rules=homeActiveRules(ctx),metrics=rules.map(r=>{const cat=String(r.code||'').toUpperCase(),u=homeLeaveUsage(code,cat,ctx);let value='—',detail='';if(r.unlimited===true){value='Unlimited';detail=`Used in saved dated records: ${u.used}`}else if(!homePeriodValid(ctx)){value='Period not set';detail='Limited balance unavailable'}else{const max=Number(r.max),rem=Math.round((max-u.used)*2)/2;value=`${Math.max(0,rem)} left`;detail=`Used ${u.used} of ${max}${u.legacyUnassigned?` · ${u.legacyUnassigned} legacy unit(s) unassigned`:''}`};return `<div class="teacherHistoryMetric"><b>${esc(cat)} · ${esc(value)}</b><span>${esc(detail)}</span></div>`}).join('');
 const history=homeHistoryItems(code,ctx).slice(0,6).map(x=>{const ds=x._dates||[],dateText=ds.length===1?displayDate(ds[0]):(ds.length?`${displayDate(ds[0])} → ${displayDate(ds[ds.length-1])}`:'—');return `<div class="teacherHistoryLine"><div class="teacherHistoryDate">${esc(dateText)}</div><div>${esc(leaveCategoryLabel(x.leaveCategory))} · ${esc(x.type==='half'?'Half Leave':'Full Leave')}</div><div>${esc(x.note||'No remarks')}</div></div>`}).join('');
 box.innerHTML=`<div class="teacherHistoryHead"><div><div class="proxyhead">${esc(t.name)} · Leave Snapshot</div><div class="small">Regular Leave only. OD / Special Assignment are Duty Leave and are not deducted here.</div></div></div><div class="teacherHistoryMetrics">${metrics||'<div class="small">No active Leave Rules configured.</div>'}</div><div class="teacherHistoryList">${history||'<div class="small">No saved regular leave history.</div>'}</div>`;
}
function evaluateHomepageLeaveRule(code,category,requested=0,ctx=window.__homepageLeaveContext){
 const rule=homeRule(category,ctx),staffCat=homeStaffCategory(code,ctx);if(!ctx)return{kind:'config',message:'Leave Rules are not loaded.'};if(!rule||rule.active===false)return{kind:'config',message:'This leave category is not available for new entries.'};if(staffCat==='unknown')return{kind:'config',message:'Staff leave classification is not configured.'};if(!homeRuleApplies(rule,staffCat))return{kind:'blocked',message:`${leaveCategoryLabel(category)} is not applicable to this staff category.`};const u=homeLeaveUsage(code,category,ctx);if(rule.unlimited===true)return{kind:'ok',message:`${leaveCategoryLabel(category)}: Unlimited. Saved dated usage: ${u.used}.`,usage:u,rule};if(!homePeriodValid(ctx))return{kind:'config',message:'Entitlement period is not configured for limited leave.'};const max=Number(rule.max),remaining=Math.round((max-u.used)*2)/2;if(remaining<=0)return{kind:'blocked',message:`${leaveCategoryLabel(category)} exhausted — no leave remaining. Used ${u.used} of ${max}.`,usage:u,rule,remaining};if(Number(requested)>remaining)return{kind:'blocked',message:`${leaveCategoryLabel(category)} available: ${remaining} remaining, but this entry requests ${requested}.`,usage:u,rule,remaining};return{kind:'ok',message:`${leaveCategoryLabel(category)} available: ${remaining} remaining${requested?` · ${requested} requested`:''}.`,usage:u,rule,remaining};
}
function renderHomepageLeaveRuleWarning(){
 const out=E('homepageLeaveRuleWarning');if(!out)return;const code=E('leaveTeacher')?.value,cat=E('leaveCategory')?.value;if(!(selectedStatus==='full'||selectedStatus==='half')){out.textContent='';return}if(!code){out.innerHTML='<span style="color:#7a5b18">Select a teacher to check the leave balance.</span>';return}if(!cat){out.innerHTML='<span style="color:#617685">Choose a leave category to check the remaining balance.</span>';return}const requested=Number(E('leaveUnits')?.value||autoCalculatedLeaveUnits()||0),r=evaluateHomepageLeaveRule(code,cat,requested);const colour=r.kind==='ok'?'#245c34':r.kind==='blocked'?'#8b2d2d':'#7a5b18';out.innerHTML=`<b style="color:${colour}">${esc(r.message)}</b>${r.usage&&r.usage.legacyUnassigned?`<br><span style="color:#7a5b18">⚠ ${esc(r.usage.legacyUnassigned)} legacy unit(s) are period-unassigned and are not included in this balance.</span>`:''}`;
}
async function onHomepageLeaveTeacherChange(force=false){
 const code=E('leaveTeacher')?.value;homepageLeaveContextCode=code||'';if(!code){renderHomepageLeaveSnapshot();renderHomepageLeaveRuleWarning();return}homepageLeaveContextLoading=true;renderHomepageLeaveSnapshot();try{const ctx=await window.loadHomepageLeaveContext(code,force);window.__homepageLeaveContext=ctx;populateHomepageLeaveCategories(ctx,E('leaveCategory')?.value||'');homepageLeaveContextLoading=false;renderHomepageLeaveSnapshot();renderHomepageLeaveRuleWarning()}catch(e){homepageLeaveContextLoading=false;const box=E('homepageLeaveSnapshot');if(box){box.style.display='block';box.innerHTML='<div class="proxyhead">Leave Snapshot</div><div class="warn">Could not load leave history: '+esc(e&&e.message?e.message:e)+'</div>'}renderHomepageLeaveRuleWarning()}
}
async function validateHomepageLeaveBeforeSave(code,category,requested){
 try{const ctx=await window.loadHomepageLeaveContext(code,true);window.__homepageLeaveContext=ctx;homepageLeaveContextCode=code;populateHomepageLeaveCategories(ctx,category);renderHomepageLeaveSnapshot();const r=evaluateHomepageLeaveRule(code,category,requested,ctx);renderHomepageLeaveRuleWarning();if(r.kind==='ok')return'';return r.message+(r.kind==='blocked'?' Use Quick Add Leave / Leave Master Editor if a Principal policy override is genuinely required.':'')}catch(e){return e&&e.message?e.message:String(e)}
}
window.onHomepageLeaveTeacherChange=onHomepageLeaveTeacherChange;window.renderHomepageLeaveRuleWarning=renderHomepageLeaveRuleWarning;
"""
p=Path('v66-home.js'); text=p.read_text(encoding='utf-8')
if 'let homepageLeaveContextCode=' not in text:
    if insert_after not in text: raise SystemExit('v66-home.js: leaveCategoryLabel anchor not found')
    text=text.replace(insert_after,addition,1)
# Ensure refreshLeaveCategoryUi triggers current warning.
old='if(hint){const c=cat&&cat.value?leaveCategoryLabel(cat.value):"Select the leave category";const n=units&&units.value?Number(units.value):0;hint.textContent=c+(n?" · "+n+" leave day"+(n===1?"":"s"):"")}}'
new='if(hint){const c=cat&&cat.value?leaveCategoryLabel(cat.value):"Select the leave category";const n=units&&units.value?Number(units.value):0;hint.textContent=c+(n?" · "+n+" leave day"+(n===1?"":"s"):"")}renderHomepageLeaveRuleWarning()}'
if old in text:text=text.replace(old,new,1)
# Save-time configurable rule validation replaces hard-coded category list.
old2='const cat=String(E("leaveCategory").value||"").trim().toUpperCase();if(!cat||!LEAVE_CATEGORY_LABELS[cat]){E("statusMsg").textContent="Select the leave category (VL / EL / CL / SEL / EOL / Maternity Leave).";return}\n   let units=Number(E("leaveUnits").value);if(!isFinite(units)||units<=0)units=autoCalculatedLeaveUnits();if(!units||units<=0){E("statusMsg").textContent="Enter the number of leave days.";return}\n   rec.leaveCategory=cat;rec.leaveUnits=Math.round(units*2)/2;'
new2='const cat=String(E("leaveCategory").value||"").trim().toUpperCase();if(!cat){E("statusMsg").textContent="Select the leave category.";return}\n   let units=Number(E("leaveUnits").value);if(!isFinite(units)||units<=0)units=autoCalculatedLeaveUnits();if(!units||units<=0){E("statusMsg").textContent="Enter the number of leave days.";return}\n   const ruleError=await validateHomepageLeaveBeforeSave(c,cat,Math.round(units*2)/2);if(ruleError){E("statusMsg").textContent=ruleError;return}\n   rec.leaveCategory=cat;rec.leaveUnits=Math.round(units*2)/2;'
if old2 not in text and 'const ruleError=await validateHomepageLeaveBeforeSave' not in text: raise SystemExit('v66-home.js: save category anchor not found')
text=text.replace(old2,new2,1)
# After editing a plan and selecting teacher, refresh its snapshot.
old3='refreshLeaveCategoryUi(false);\n E("statusMsg").textContent="Editing saved entry: "+leavePlanDateText(p)'
new3='refreshLeaveCategoryUi(false);onHomepageLeaveTeacherChange();\n E("statusMsg").textContent="Editing saved entry: "+leavePlanDateText(p)'
if old3 in text:text=text.replace(old3,new3,1)
# Vacant must be visible in proxy summary and terminology updated.
old4=".filter(o=>o&&['full','half','od','special'].includes(o.type));if(!rows.length){out.innerHTML='<b>Today’s Leave / OD / Assignment Summary</b><div class=\"small\" style=\"margin-top:5px\">No approved Leave, On Duty or Special Assignment record is available for today.</div>';return}out.innerHTML='<b>Today’s Leave / OD / Assignment Summary</b>"
new4=".filter(o=>o&&['full','half','od','special','vacant'].includes(o.type));if(!rows.length){out.innerHTML='<b>Today’s Leave / Duty Leave / Operational Status Summary</b><div class=\"small\" style=\"margin-top:5px\">No approved Leave, Duty Leave or Vacant Position record is available for today.</div>';return}out.innerHTML='<b>Today’s Leave / Duty Leave / Operational Status Summary</b>"
if old4 not in text and "['full','half','od','special','vacant']" not in text: raise SystemExit('v66-home.js: proxy summary filter anchor not found')
text=text.replace(old4,new4,1)
p.write_text(text,encoding='utf-8')
print('v66-home.js homepage leave and vacant summary patch complete')

print('VKVTT v66.2 homepage leave/proxy patch completed.')
