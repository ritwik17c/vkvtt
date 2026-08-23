from pathlib import Path


def replace_once(path, old, new, marker):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if marker in s:
        print(f'{path}: already patched {marker}'); return
    if old not in s: raise SystemExit(f'{path}: anchor not found {marker}')
    p.write_text(s.replace(old,new,1),encoding='utf-8'); print(f'{path}: patched {marker}')

# =============================================================================
# Leave Rules Admin page
# =============================================================================
replace_once('admin-leave-rules.html',
"""      <div class="checkrow"><label><input id="ruleUnlimited" type="checkbox"> Unlimited</label><label><input id="ruleActive" type="checkbox" checked> Active</label></div>
      <div id="maxWrap"><label>Maximum units for this entitlement period</label><input id="ruleMax" type="number" min="0.5" step="0.5" placeholder="Enter approved limit"></div>
      <h3>Applicable staff categories</h3>
      <div class="checkrow"><label><input id="ruleTeaching" type="checkbox"> Teaching Staff</label><label><input id="ruleAdmin" type="checkbox"> Administrative Staff</label><label><input id="ruleNonTeaching" type="checkbox"> Non-Teaching Staff</label></div>
""",
"""      <div class="grid2">
        <div><label>Leave type</label><select id="ruleType"><option value="regular">Regular Leave</option><option value="conditional">Conditional / Special Leave</option></select></div>
        <div class="checkrow" style="align-items:end"><label><input id="ruleUnlimited" type="checkbox"> Unlimited</label><label><input id="ruleActive" type="checkbox" checked> Available for New Entries</label></div>
      </div>
      <div id="conditionalWrap" class="status info hide"><label style="color:inherit"><input id="ruleIndividualEligibility" type="checkbox" style="width:auto"> Require individual staff eligibility before this leave may be allotted</label><div class="small">Recommended for leave such as Maternity Leave. Eligibility is set per staff member below and is never inferred from name or designation.</div></div>
      <div id="maxWrap"><label>Maximum units for this entitlement period</label><input id="ruleMax" type="number" min="0.5" step="0.5" placeholder="Enter approved limit"></div>
      <h3>Applicable staff categories</h3>
      <div id="ruleApplicability" class="checkrow"></div>
""",
'id="ruleType"')

# Add Staff Categories section between Leave Categories and Staff Classification.
replace_once('admin-leave-rules.html',
"""  <section class="card">
    <h2>Staff Leave Classification</h2>
""",
"""  <section class="card">
    <div class="sectionTop"><div><h2>Staff Categories</h2><div class="help">Leave-policy categories are separate from the timetable roster. Teaching Staff, Administrative Staff and Non-Teaching Staff are protected defaults; additional categories may be added when required.</div></div><button id="newStaffCategory" class="green">＋ Add Staff Category</button></div>
    <div id="staffCategoryGrid" class="ruleGrid"></div>
    <div id="staffCategoryForm" class="card hide" style="background:#f8fcfe">
      <h3 id="staffCategoryFormTitle">Add Staff Category</h3>
      <div class="grid2"><div><label>Category code</label><input id="staffCategoryCode" maxlength="30" placeholder="e.g. academic-support"></div><div><label>Display name</label><input id="staffCategoryName" maxlength="80" placeholder="e.g. Academic Support Staff"></div></div>
      <div class="checkrow"><label><input id="staffCategoryActive" type="checkbox" checked> Available for Classification</label></div>
      <div class="actions"><button id="saveStaffCategory" class="primary">Save Staff Category</button><button id="cancelStaffCategory">Cancel</button></div>
      <div class="small">Staff categories are not deleted. Deactivate an unused custom category so historical classifications remain interpretable.</div>
    </div>
  </section>

  <section class="card">
    <h2>Staff Leave Classification &amp; Conditional Eligibility</h2>
""",
'id="staffCategoryGrid"')
replace_once('admin-leave-rules.html',
'The existing teacher/non-teaching roster remains unchanged. Use an explicit override only where a staff member should be treated as Administrative, Teaching or Non-Teaching for leave applicability.',
'The existing teacher/non-teaching roster remains unchanged. Choose the leave-policy staff category here. Conditional / Special Leave eligibility is also set explicitly here; the app never guesses eligibility from a person’s name or designation.',
'Conditional / Special Leave eligibility is also set explicitly here')

# Expand page state.
replace_once('admin-leave-rules.html',
"let user=null,master=null,rules=[],entitlementPeriod=null,staffCategoryOverrides={},legacy=[],editingCode='';",
"let user=null,master=null,rules=[],entitlementPeriod=null,staffCategoryOverrides={},staffCategories=[],staffConditionalEligibility={},legacy=[],editingCode='',editingStaffCategoryCode='';",
'staffConditionalEligibility={}')

# Helpers and defaults.
replace_once('admin-leave-rules.html',
"""function ruleComplete(r){const n=Number(r?.max);return !!r&&String(r.code||'').trim()&&(r.teaching===true||r.admin===true||r.nonTeaching===true)&&(r.unlimited===true||(Number.isFinite(n)&&n>0&&Math.round(n*2)===n*2))}
function inferredStaffCategory(x,source){const explicit=String(x.leaveStaffCategory||'');if(['teaching','administrative','non-teaching'].includes(explicit))return explicit;const ov=String(staffCategoryOverrides[x.code]||'');if(['teaching','administrative','non-teaching'].includes(ov))return ov;return source==='non-teaching'?'non-teaching':'teaching'}
""",
"""const DEFAULT_STAFF_CATEGORIES=[{code:'teaching',name:'Teaching Staff',active:true,protected:true,sortOrder:10},{code:'administrative',name:'Administrative Staff',active:true,protected:true,sortOrder:20},{code:'non-teaching',name:'Non-Teaching Staff',active:true,protected:true,sortOrder:30}];
function normaliseStaffCategories(items){const map=new Map(DEFAULT_STAFF_CATEGORIES.map(x=>[x.code,{...x}]));for(const x of (Array.isArray(items)?items:[])){const code=String(x&&x.code||'').trim().toLowerCase();if(!code)continue;map.set(code,{...(map.get(code)||{}),...x,code,protected:map.has(code)?true:x.protected===true})}return [...map.values()].sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.name||a.code).localeCompare(String(b.name||b.code)))}
function activeStaffCategories(){return staffCategories.filter(x=>x&&x.active!==false)}
function ruleApplicableCodes(r){const a=Array.isArray(r&&r.applicableStaffCategories)?r.applicableStaffCategories.map(String):[];if(a.length)return a;const out=[];if(r?.teaching===true)out.push('teaching');if(r?.admin===true)out.push('administrative');if(r?.nonTeaching===true)out.push('non-teaching');return out}
function ruleComplete(r){const n=Number(r?.max);return !!r&&String(r.code||'').trim()&&ruleApplicableCodes(r).length>0&&(r.unlimited===true||(Number.isFinite(n)&&n>0&&Math.round(n*2)===n*2))}
function inferredStaffCategory(x,source){const known=new Set(staffCategories.map(c=>String(c.code)));const explicit=String(x.leaveStaffCategory||'');if(known.has(explicit))return explicit;const ov=String(staffCategoryOverrides[x.code]||'');if(known.has(ov))return ov;return source==='non-teaching'?'non-teaching':'teaching'}
function conditionalRules(){return rules.filter(r=>String(r.ruleType||'regular')==='conditional'&&r.active!==false)}
function eligibleFor(code,ruleCode){return !!(staffConditionalEligibility&&staffConditionalEligibility[code]&&staffConditionalEligibility[code][ruleCode]===true)}
""",
'DEFAULT_STAFF_CATEGORIES')

# Persist/load new state.
replace_once('admin-leave-rules.html',
"await setDoc(doc(db,'leaveRules','current'),{categories:rules,entitlementPeriod,staffCategoryOverrides,updatedAt:serverTimestamp(),updatedByUid:actor.uid,updatedByEmail:actor.email||'',...extra},{merge:true});",
"await setDoc(doc(db,'leaveRules','current'),{categories:rules,entitlementPeriod,staffCategoryOverrides,staffCategories,staffConditionalEligibility,updatedAt:serverTimestamp(),updatedByUid:actor.uid,updatedByEmail:actor.email||'',...extra},{merge:true});",
'categories:rules,entitlementPeriod,staffCategoryOverrides,staffCategories,staffConditionalEligibility')
replace_once('admin-leave-rules.html',
"if(rs.exists()){const d=rs.data()||{};rules=Array.isArray(d.categories)?d.categories:[];entitlementPeriod=d.entitlementPeriod||null;staffCategoryOverrides=d.staffCategoryOverrides||{}}else{rules=[];entitlementPeriod=null;staffCategoryOverrides={}}",
"if(rs.exists()){const d=rs.data()||{};rules=(Array.isArray(d.categories)?d.categories:[]).map(r=>({...r,ruleType:r.ruleType||(String(r.code||'').toUpperCase()==='MATERNITY'?'conditional':'regular'),requiresIndividualEligibility:r.requiresIndividualEligibility===true||(String(r.code||'').toUpperCase()==='MATERNITY'&&r.requiresIndividualEligibility!==false)}));entitlementPeriod=d.entitlementPeriod||null;staffCategoryOverrides=d.staffCategoryOverrides||{};staffCategories=normaliseStaffCategories(d.staffCategories);staffConditionalEligibility=d.staffConditionalEligibility||{}}else{rules=[];entitlementPeriod=null;staffCategoryOverrides={};staffCategories=normaliseStaffCategories([]);staffConditionalEligibility={}}",
'staffCategories=normaliseStaffCategories(d.staffCategories)')
replace_once('admin-leave-rules.html',
'function renderAll(){renderPeriod();renderRules();renderStaff();renderLegacy()}',
'function renderAll(){renderPeriod();renderRules();renderStaffCategories();renderStaff();renderLegacy()}',
'renderStaffCategories();')

# Rule rendering/editing with type/applicability.
replace_once('admin-leave-rules.html',
"box.innerHTML=rules.slice().sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.code).localeCompare(String(b.code))).map(r=>`<div class=\"ruleCard ${r.active===false?'inactive':''}\"><b>${safe(r.name||r.code)}</b> <span class=\"pill code\">${safe(r.code)}</span> ${r.active===false?'<span class=\"pill\">Inactive</span>':''}<div class=\"small\">${r.unlimited?'Unlimited':`${safe(r.max||'—')} units / period`}<br>Teaching ${r.teaching?'✓':'—'} · Administrative ${r.admin?'✓':'—'} · Non-Teaching ${r.nonTeaching?'✓':'—'}</div><div class=\"actions\"><button data-edit-rule=\"${safe(r.code)}\">Edit</button></div></div>`).join('');",
"box.innerHTML=rules.slice().sort((a,b)=>Number(a.sortOrder||999)-Number(b.sortOrder||999)||String(a.code).localeCompare(String(b.code))).map(r=>{const apps=ruleApplicableCodes(r).map(c=>staffCategories.find(x=>x.code===c)?.name||c).join(' · ');const type=String(r.ruleType||'regular')==='conditional'?'Conditional / Special Leave':'Regular Leave';return `<div class=\"ruleCard ${r.active===false?'inactive':''}\"><b>${safe(r.name||r.code)}</b> <span class=\"pill code\">${safe(r.code)}</span> <span class=\"pill\">${safe(type)}</span> ${r.active===false?'<span class=\"pill\">Not available for new entries</span>':''}<div class=\"small\">${r.unlimited?'Unlimited':`${safe(r.max||'—')} units / period`}<br>${safe(apps||'No staff category selected')}${r.requiresIndividualEligibility?'<br>Individual eligibility required':''}</div><div class=\"actions\"><button data-edit-rule=\"${safe(r.code)}\">Edit</button></div></div>`}).join('');",
'Individual eligibility required')

replace_once('admin-leave-rules.html',
"$('ruleForm').classList.remove('hide');$('ruleFormTitle').textContent=r?`Edit ${r.name||r.code}`:'Add Leave Category';$('ruleCode').disabled=!!r;$('ruleCode').value=r?.code||'';$('ruleName').value=r?.name||'';$('ruleUnlimited').checked=r?.unlimited===true;$('ruleActive').checked=r?r.active!==false:true;$('ruleMax').value=r?.unlimited?'':(r?.max||'');$('ruleTeaching').checked=r?.teaching===true;$('ruleAdmin').checked=r?.admin===true;$('ruleNonTeaching').checked=r?.nonTeaching===true;toggleMax();",
"$('ruleForm').classList.remove('hide');$('ruleFormTitle').textContent=r?`Edit ${r.name||r.code}`:'Add Leave Category';$('ruleCode').disabled=!!r;$('ruleCode').value=r?.code||'';$('ruleName').value=r?.name||'';$('ruleType').value=r?.ruleType||'regular';$('ruleUnlimited').checked=r?.unlimited===true;$('ruleActive').checked=r?r.active!==false:true;$('ruleIndividualEligibility').checked=r?.requiresIndividualEligibility===true;$('ruleMax').value=r?.unlimited?'':(r?.max||'');renderRuleApplicability(r);toggleMax();toggleConditional();",
'renderRuleApplicability(r);toggleMax();toggleConditional();')
replace_once('admin-leave-rules.html',
"function toggleMax(){$('maxWrap').classList.toggle('hide',$('ruleUnlimited').checked)}",
"function renderRuleApplicability(r){const selected=new Set(ruleApplicableCodes(r||{}));$('ruleApplicability').innerHTML=activeStaffCategories().map(c=>`<label><input type=\"checkbox\" data-rule-staff-category=\"${safe(c.code)}\" ${selected.has(c.code)?'checked':''}> ${safe(c.name||c.code)}</label>`).join('')||'<span class=\"small\">Add an active Staff Category first.</span>'}\nfunction toggleMax(){$('maxWrap').classList.toggle('hide',$('ruleUnlimited').checked)}\nfunction toggleConditional(){const conditional=$('ruleType').value==='conditional';$('conditionalWrap').classList.toggle('hide',!conditional);if(!conditional)$('ruleIndividualEligibility').checked=false}",
'function renderRuleApplicability(r)')

# Staff category render/edit functions before renderStaff.
replace_once('admin-leave-rules.html',
"function renderStaff(){\n",
"""function renderStaffCategories(){
 const box=$('staffCategoryGrid');box.innerHTML=staffCategories.map(c=>`<div class="ruleCard ${c.active===false?'inactive':''}"><b>${safe(c.name||c.code)}</b> <span class="pill code">${safe(c.code)}</span> ${c.protected?'<span class="pill">Protected default</span>':''} ${c.active===false?'<span class="pill">Inactive</span>':''}<div class="actions"><button data-edit-staff-category="${safe(c.code)}">Edit</button></div></div>`).join('');document.querySelectorAll('[data-edit-staff-category]').forEach(b=>b.onclick=()=>openStaffCategory(b.dataset.editStaffCategory));
}
function openStaffCategory(code=''){editingStaffCategoryCode=code;const c=staffCategories.find(x=>x.code===code);$('staffCategoryForm').classList.remove('hide');$('staffCategoryFormTitle').textContent=c?`Edit ${c.name||c.code}`:'Add Staff Category';$('staffCategoryCode').disabled=!!c;$('staffCategoryCode').value=c?.code||'';$('staffCategoryName').value=c?.name||'';$('staffCategoryActive').checked=c?c.active!==false:true;if(c?.protected)$('staffCategoryActive').disabled=true;else $('staffCategoryActive').disabled=false;$('staffCategoryForm').scrollIntoView({behavior:'smooth',block:'center'})
}
function renderStaff(){
""",
'function openStaffCategory(code=')

# Dynamic staff table + eligibility column.
old_staff=""" const rows=[...(master?.teachers||[]).map(x=>({...x,_source:'teaching'})),...(master?.nonTeachingStaff||[]).filter(x=>x&&x.active!==false).map(x=>({...x,_source:'non-teaching'}))].sort((a,b)=>String(a.name).localeCompare(String(b.name)));
 $('staffTable').innerHTML='<table><thead><tr><th>Staff</th><th>Roster</th><th>Leave classification</th></tr></thead><tbody>'+rows.map(x=>{const v=inferredStaffCategory(x,x._source);return `<tr><td>${safe(x.name||x.code)}<div class="small code">${safe(x.code)}</div></td><td>${x._source==='non-teaching'?'Non-Teaching roster':'Teacher roster'}</td><td><select data-staff-code="${safe(x.code)}"><option value="teaching" ${v==='teaching'?'selected':''}>Teaching</option><option value="administrative" ${v==='administrative'?'selected':''}>Administrative</option><option value="non-teaching" ${v==='non-teaching'?'selected':''}>Non-Teaching</option></select></td></tr>`}).join('')+'</tbody></table>';
"""
new_staff=""" const rows=[...(master?.teachers||[]).map(x=>({...x,_source:'teaching'})),...(master?.nonTeachingStaff||[]).filter(x=>x&&x.active!==false).map(x=>({...x,_source:'non-teaching'}))].sort((a,b)=>String(a.name).localeCompare(String(b.name))),cats=activeStaffCategories(),conditional=conditionalRules();
 $('staffTable').innerHTML='<table><thead><tr><th>Staff</th><th>Roster</th><th>Leave classification</th><th>Conditional / Special Leave eligibility</th></tr></thead><tbody>'+rows.map(x=>{const v=inferredStaffCategory(x,x._source),opts=cats.map(c=>`<option value="${safe(c.code)}" ${v===c.code?'selected':''}>${safe(c.name||c.code)}</option>`).join(''),elig=conditional.length?conditional.map(r=>`<label style="display:block;margin:3px 0"><input type="checkbox" style="width:auto" data-conditional-staff="${safe(x.code)}" data-conditional-rule="${safe(r.code)}" ${eligibleFor(x.code,r.code)?'checked':''}> ${safe(r.name||r.code)}</label>`).join(''):'<span class="small">No active conditional leave categories.</span>';return `<tr><td>${safe(x.name||x.code)}<div class="small code">${safe(x.code)}</div></td><td>${x._source==='non-teaching'?'Non-Teaching roster':'Teacher roster'}</td><td><select data-staff-code="${safe(x.code)}">${opts}</select></td><td>${elig}</td></tr>`}).join('')+'</tbody></table>';
"""
replace_once('admin-leave-rules.html',old_staff,new_staff,'data-conditional-staff=')

# Wire Staff Category form and rule type toggling before saveRule handler.
replace_once('admin-leave-rules.html',
"$('newRule').onclick=()=>openRule('');$('cancelRule').onclick=()=>{$('ruleForm').classList.add('hide');editingCode=''};$('ruleUnlimited').onchange=toggleMax;",
"$('newRule').onclick=()=>openRule('');$('cancelRule').onclick=()=>{$('ruleForm').classList.add('hide');editingCode=''};$('ruleUnlimited').onchange=toggleMax;$('ruleType').onchange=toggleConditional;\n$('newStaffCategory').onclick=()=>openStaffCategory('');$('cancelStaffCategory').onclick=()=>{$('staffCategoryForm').classList.add('hide');editingStaffCategoryCode=''};\n$('saveStaffCategory').onclick=async()=>{const code=$('staffCategoryCode').value.trim().toLowerCase(),name=$('staffCategoryName').value.trim(),active=$('staffCategoryActive').checked;if(!code||!name){msg('Staff category code and display name are required.','error');return}if(!/^[a-z0-9_-]{1,30}$/.test(code)){msg('Staff category code may contain lowercase letters, numbers, underscore and hyphen.','error');return}if(!editingStaffCategoryCode&&staffCategories.some(x=>x.code===code)){msg('That staff category already exists.','error');return}const old=staffCategories.find(x=>x.code===editingStaffCategoryCode),rec={...(old||{}),code:editingStaffCategoryCode||code,name,active:old?.protected?true:active,protected:old?.protected===true,sortOrder:old?.sortOrder||((staffCategories.length+1)*10)};if(old)staffCategories[staffCategories.indexOf(old)]=rec;else staffCategories.push(rec);staffCategories=normaliseStaffCategories(staffCategories);try{await saveRulesDoc();msg('Staff category saved.','ok');$('staffCategoryForm').classList.add('hide');editingStaffCategoryCode='';renderAll()}catch(e){msg('Could not save staff category: '+(e.message||e),'error')}};",
"$('saveStaffCategory').onclick=async()=>")

# Replace saveRule extraction and record construction.
replace_once('admin-leave-rules.html',
"const code=$('ruleCode').value.trim().toUpperCase(),name=$('ruleName').value.trim(),unlimited=$('ruleUnlimited').checked,active=$('ruleActive').checked,max=Number($('ruleMax').value||0),teaching=$('ruleTeaching').checked,admin=$('ruleAdmin').checked,nonTeaching=$('ruleNonTeaching').checked;",
"const code=$('ruleCode').value.trim().toUpperCase(),name=$('ruleName').value.trim(),ruleType=$('ruleType').value||'regular',unlimited=$('ruleUnlimited').checked,active=$('ruleActive').checked,max=Number($('ruleMax').value||0),requiresIndividualEligibility=ruleType==='conditional'&&$('ruleIndividualEligibility').checked,applicableStaffCategories=[...document.querySelectorAll('[data-rule-staff-category]:checked')].map(x=>x.dataset.ruleStaffCategory);",
'applicableStaffCategories=[...document.querySelectorAll')
replace_once('admin-leave-rules.html',
"if(active&&!teaching&&!admin&&!nonTeaching){msg('Select at least one applicable staff category for an active rule.','error');return}",
"if(active&&!applicableStaffCategories.length){msg('Select at least one applicable staff category for a leave category available for new entries.','error');return}",
'leave category available for new entries')
replace_once('admin-leave-rules.html',
"const old=rules.find(r=>String(r.code)===editingCode),savedMax=unlimited?null:(Number.isFinite(max)&&max>0?max:(old?.max??null)),rec={...(old||{}),code:editingCode||code,name,unlimited,max:savedMax,teaching,admin,nonTeaching,active,sortOrder:old?.sortOrder||((rules.length+1)*10)};",
"const old=rules.find(r=>String(r.code)===editingCode),savedMax=unlimited?null:(Number.isFinite(max)&&max>0?max:(old?.max??null)),rec={...(old||{}),code:editingCode||code,name,ruleType,requiresIndividualEligibility,unlimited,max:savedMax,applicableStaffCategories,teaching:applicableStaffCategories.includes('teaching'),admin:applicableStaffCategories.includes('administrative'),nonTeaching:applicableStaffCategories.includes('non-teaching'),active,sortOrder:old?.sortOrder||((rules.length+1)*10)};",
'requiresIndividualEligibility,unlimited,max:savedMax,applicableStaffCategories')

# Save staff classification + conditional eligibility.
replace_once('admin-leave-rules.html',
"const map={};document.querySelectorAll('[data-staff-code]').forEach(sel=>{map[sel.dataset.staffCode]=sel.value});staffCategoryOverrides=map;",
"const map={};document.querySelectorAll('[data-staff-code]').forEach(sel=>{map[sel.dataset.staffCode]=sel.value});staffCategoryOverrides=map;const eligibility={};document.querySelectorAll('[data-conditional-staff][data-conditional-rule]').forEach(cb=>{const code=cb.dataset.conditionalStaff,rule=cb.dataset.conditionalRule;if(!eligibility[code])eligibility[code]={};eligibility[code][rule]=cb.checked===true});staffConditionalEligibility=eligibility;",
'staffConditionalEligibility=eligibility;')

# =============================================================================
# Leave Master Editor: dynamic staff categories + conditional eligibility.
# =============================================================================
replace_once('admin-leave-editor.html',
"let leaveRules=[],entitlementPeriod=null,leaveRulesLoadState='idle',staffCategoryOverrides={};",
"let leaveRules=[],entitlementPeriod=null,leaveRulesLoadState='idle',staffCategoryOverrides={},leaveStaffCategories=[],staffConditionalEligibility={};",
'leaveStaffCategories=[]')
replace_once('admin-leave-editor.html',
"function ruleComplete(rule){\n if(!rule||!String(rule.code||'').trim()||rule.active!==true)return false;\n if(!(rule.teaching===true||rule.admin===true||rule.nonTeaching===true))return false;\n const n=Number(rule.max);return rule.unlimited===true||(Number.isFinite(n)&&n>0&&Math.round(n*2)===n*2);\n}",
"function ruleApplicableCodes(rule){const a=Array.isArray(rule&&rule.applicableStaffCategories)?rule.applicableStaffCategories.map(String):[];if(a.length)return a;const out=[];if(rule?.teaching===true)out.push('teaching');if(rule?.admin===true)out.push('administrative');if(rule?.nonTeaching===true)out.push('non-teaching');return out}\nfunction ruleComplete(rule){\n if(!rule||!String(rule.code||'').trim()||rule.active!==true)return false;\n if(!ruleApplicableCodes(rule).length)return false;\n const n=Number(rule.max);return rule.unlimited===true||(Number.isFinite(n)&&n>0&&Math.round(n*2)===n*2);\n}\nfunction conditionalEligibilityRequired(rule){return String(rule&&rule.ruleType||'regular')==='conditional'&&rule.requiresIndividualEligibility===true}\nfunction conditionalEligible(code,category){return !!(staffConditionalEligibility&&staffConditionalEligibility[code]&&staffConditionalEligibility[code][String(category||'').toUpperCase()]===true)}",
'function conditionalEligibilityRequired(rule)')
replace_once('admin-leave-editor.html',
"const c=String(code||''),t=teacherByCode(c),explicit=String(t&&t.leaveStaffCategory||'');\n if(['teaching','administrative','non-teaching'].includes(explicit))return explicit;\n const override=String(staffCategoryOverrides[c]||'');\n if(['teaching','administrative','non-teaching'].includes(override))return override;",
"const c=String(code||''),t=teacherByCode(c),known=new Set((leaveStaffCategories||[]).map(x=>String(x.code))),explicit=String(t&&t.leaveStaffCategory||'');\n if(known.has(explicit)||['teaching','administrative','non-teaching'].includes(explicit))return explicit;\n const override=String(staffCategoryOverrides[c]||'');\n if(known.has(override)||['teaching','administrative','non-teaching'].includes(override))return override;",
'known=new Set((leaveStaffCategories||[])')
replace_once('admin-leave-editor.html',
"return !!rule&&((staffCategory==='teaching'&&rule.teaching===true)||(staffCategory==='administrative'&&rule.admin===true)||(staffCategory==='non-teaching'&&rule.nonTeaching===true));",
"return !!rule&&ruleApplicableCodes(rule).includes(String(staffCategory||''));",
'ruleApplicableCodes(rule).includes')
replace_once('admin-leave-editor.html',
"const applicable=ruleAppliesTo(rule,staffCategory);\n if(rule.unlimited===true){",
"const applicable=ruleAppliesTo(rule,staffCategory);\n if(conditionalEligibilityRequired(rule)&&!conditionalEligible(code,category))return{configError:`${leaveRuleLabel(category)} requires explicit individual eligibility for this staff member. Enable it in Leave Rules → Staff Leave Classification & Conditional Eligibility.`,rule,staffCategory,applicable:false,conditionalEligibilityMissing:true};\n if(rule.unlimited===true){",
'conditionalEligibilityMissing:true')
replace_once('admin-leave-editor.html',
"if(!s.exists()){leaveRules=[];entitlementPeriod=null;staffCategoryOverrides={};leaveRulesLoadState='missing'}\n   else{const d=s.data()||{};leaveRules=Array.isArray(d.categories)?d.categories:[];entitlementPeriod=d.entitlementPeriod||null;staffCategoryOverrides=d.staffCategoryOverrides||{};leaveRulesLoadState='ready'}",
"if(!s.exists()){leaveRules=[];entitlementPeriod=null;staffCategoryOverrides={};leaveStaffCategories=[];staffConditionalEligibility={};leaveRulesLoadState='missing'}\n   else{const d=s.data()||{};leaveRules=Array.isArray(d.categories)?d.categories:[];entitlementPeriod=d.entitlementPeriod||null;staffCategoryOverrides=d.staffCategoryOverrides||{};leaveStaffCategories=Array.isArray(d.staffCategories)?d.staffCategories:[];staffConditionalEligibility=d.staffConditionalEligibility||{};leaveRulesLoadState='ready'}",
'leaveStaffCategories=Array.isArray(d.staffCategories)')

# =============================================================================
# Homepage evaluation: dynamic applicability + conditional eligibility.
# =============================================================================
replace_once('v66-home-cloud.js',
"const data={categories:Array.isArray(rd.categories)?rd.categories:[],entitlementPeriod:rd.entitlementPeriod||null,staffCategoryOverrides:rd.staffCategoryOverrides||{},scheduled,manual,legacy,legacyAvailable,loadedAt:now};",
"const data={categories:Array.isArray(rd.categories)?rd.categories:[],entitlementPeriod:rd.entitlementPeriod||null,staffCategoryOverrides:rd.staffCategoryOverrides||{},staffCategories:Array.isArray(rd.staffCategories)?rd.staffCategories:[],staffConditionalEligibility:rd.staffConditionalEligibility||{},scheduled,manual,legacy,legacyAvailable,loadedAt:now};",
'staffConditionalEligibility:rd.staffConditionalEligibility')
replace_once('v66-home.js',
"function homeRuleApplies(rule,staffCat){if(staffCat==='teaching')return rule.teaching===true;if(staffCat==='administrative')return rule.admin===true;if(staffCat==='non-teaching')return rule.nonTeaching===true;return false}",
"function homeRuleApplicableCodes(rule){const a=Array.isArray(rule&&rule.applicableStaffCategories)?rule.applicableStaffCategories.map(String):[];if(a.length)return a;const out=[];if(rule?.teaching===true)out.push('teaching');if(rule?.admin===true)out.push('administrative');if(rule?.nonTeaching===true)out.push('non-teaching');return out}\nfunction homeRuleApplies(rule,staffCat){return homeRuleApplicableCodes(rule).includes(String(staffCat||''))}\nfunction homeConditionalEligible(code,rule,ctx=window.__homepageLeaveContext){if(String(rule&&rule.ruleType||'regular')!=='conditional'||rule.requiresIndividualEligibility!==true)return true;return !!(ctx&&ctx.staffConditionalEligibility&&ctx.staffConditionalEligibility[code]&&ctx.staffConditionalEligibility[code][String(rule.code||'').toUpperCase()]===true)}",
'function homeConditionalEligible')
replace_once('v66-home.js',
"const explicit=String(t.leaveStaffCategory||'');if(['teaching','administrative','non-teaching'].includes(explicit))return explicit;\n const ov=String(ctx&&ctx.staffCategoryOverrides&&ctx.staffCategoryOverrides[code]||'');if(['teaching','administrative','non-teaching'].includes(ov))return ov;",
"const known=new Set((ctx&&ctx.staffCategories||[]).map(x=>String(x.code))),explicit=String(t.leaveStaffCategory||'');if(known.has(explicit)||['teaching','administrative','non-teaching'].includes(explicit))return explicit;\n const ov=String(ctx&&ctx.staffCategoryOverrides&&ctx.staffCategoryOverrides[code]||'');if(known.has(ov)||['teaching','administrative','non-teaching'].includes(ov))return ov;",
'const known=new Set((ctx&&ctx.staffCategories')
replace_once('v66-home.js',
"if(!homeRuleApplies(rule,staffCat))return{kind:'blocked',message:`${leaveCategoryLabel(category)} is not applicable to this staff category.`};const u=homeLeaveUsage(code,category,ctx);",
"if(!homeRuleApplies(rule,staffCat))return{kind:'blocked',message:`${leaveCategoryLabel(category)} is not applicable to this staff category.`};if(!homeConditionalEligible(code,rule,ctx))return{kind:'config',message:`${leaveCategoryLabel(category)} is Conditional / Special Leave and individual eligibility has not been enabled for this staff member.`};const u=homeLeaveUsage(code,category,ctx);",
'is Conditional / Special Leave and individual eligibility has not been enabled')

print('VKVTT v66.2 terminology/staff-category patch completed.')
