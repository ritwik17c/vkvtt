import {initializeApp} from 'https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js';
import {getAuth,GoogleAuthProvider,signInWithPopup,onAuthStateChanged,setPersistence,browserLocalPersistence} from 'https://www.gstatic.com/firebasejs/12.17.1/firebase-auth.js';
import {getFirestore,doc,getDoc} from 'https://www.gstatic.com/firebasejs/12.17.1/firebase-firestore-lite.js';
import {candidateExamDates,createWorkspaceFromMaster,dayName,displayDate,generateExamTimetable,generateDutyRoster,validateExamTimetable,validateDutyRoster} from './exam-scheduler-core.js?v=1.0.0';

const firebaseConfig={apiKey:'AIzaSyDheZpyXghd1aQ9_RLhwpacVriG__wNZW4',authDomain:'vkv-nalbari-timetable.firebaseapp.com',projectId:'vkv-nalbari-timetable',storageBucket:'vkv-nalbari-timetable.firebasestorage.app',messagingSenderId:'791432856951',appId:'1:791432856951:web:61324065a54bef30f98d72'};
const app=initializeApp(firebaseConfig),auth=getAuth(app),db=getFirestore(app),provider=new GoogleAuthProvider();setPersistence(auth,browserLocalPersistence).catch(()=>{});
const $=id=>document.getElementById(id),safe=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const clone=value=>JSON.parse(JSON.stringify(value));
const state={user:null,profile:null,master:null,workspace:null,dirty:false,visiblePapers:[],visibleTeachers:[]};
const WEEKDAYS=[['0','Sunday'],['1','Monday'],['2','Tuesday'],['3','Wednesday'],['4','Thursday'],['5','Friday'],['6','Saturday']];

function setSaveState(message,dirty=false){$('saveState').textContent=message;$('saveState').dataset.dirty=dirty?'true':'false'}
function markDirty(message='Unsaved changes'){state.dirty=true;if(state.workspace)state.workspace.updatedAtMs=Date.now();setSaveState(message,true);renderReview()}
function showNotice(id,message,kind='info'){const el=$(id);el.className='notice '+kind;el.innerHTML=message}
function listValues(value){return [...new Set(String(value||'').split(/[\n,;]+/).map(item=>item.trim()).filter(Boolean))]}
function slotById(id){return state.workspace.slots.find(item=>item.id===id)}
function teacherName(code){const item=state.workspace.teachers.find(teacher=>teacher.code===code);return item?item.name:code}
function timeText(slot){return slot?(slot.startTime&&slot.endTime?slot.startTime+'–'+slot.endTime:(slot.startTime||slot.endTime||'')):''}

function bindNavigation(){
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-pane-target]');if(!button)return;
    document.querySelectorAll('.navButton').forEach(item=>item.classList.toggle('active',item===button));
    document.querySelectorAll('.pane').forEach(item=>item.classList.toggle('active',item.dataset.pane===button.dataset.paneTarget));
    if(button.dataset.paneTarget==='outputs')renderReview();
  });
}

async function verifyAccess(user){
  state.user=user;$('signInButton').hidden=true;
  if(!user){$('gateMessage').textContent='Sign in with an authorised Google account.';$('signInButton').hidden=false;return}
  $('gateMessage').textContent='Checking Examination Department permission…';
  try{
    const profileSnap=await getDoc(doc(db,'authorizedUsers',user.uid)),profile=profileSnap.exists()?profileSnap.data():null;
    const allowed=profile&&profile.active===true&&(profile.role==='admin'||profile.permissions?.examDepartment===true);
    if(!allowed){$('gateMessage').innerHTML='<b>Examination Department access is not enabled for this account.</b><br>Ask the Principal/Admin to delegate this workspace in User Access & Roles.';return}
    state.profile=profile;
    const masterSnap=await getDoc(doc(db,'master','current'));if(!masterSnap.exists())throw new Error('The active master timetable was not found.');
    state.master=masterSnap.data();state.workspace=createWorkspaceFromMaster(state.master);
    $('authGate').hidden=true;$('examApp').hidden=false;$('saveDraft').hidden=false;renderAll();renderDraftList();setSaveState('New unsaved draft',true);state.dirty=true;
  }catch(error){$('gateMessage').textContent='Could not open the Examination Department: '+(error.message||error)}
}

$('signInButton').onclick=async()=>{await setPersistence(auth,browserLocalPersistence);provider.setCustomParameters({prompt:'select_account'});await signInWithPopup(auth,provider)};
onAuthStateChanged(auth,verifyAccess);bindNavigation();

function renderAll(){
  renderMasterSummary();renderSetup();renderSessions();renderPapers();renderTeachers();renderTimetable();renderDuties();renderReview();
}

function renderMasterSummary(){
  const master=state.master||{},data=master.data&&typeof master.data==='object'?{...master,...master.data}:master,source=state.workspace.sourceSchedule||{};
  $('masterName').textContent=source.name||master.activeTimetableVersionName||'Activated Schedule';
  $('masterMeta').textContent='Read-only source · '+(master.activeTimetableVersionName||'Operational master timetable');
  $('masterStats').innerHTML=[`${state.workspace.classes.length} classes`,`${state.workspace.papers.length} class-subject papers`,`${state.workspace.teachers.length} teachers`,`${(data.records||[]).length} timetable entries`].map(value=>'<span class="chip">'+safe(value)+'</span>').join('');
  $('sideSource').textContent=source.name||'Activated Schedule';
}

function renderSetup(){
  const workspace=state.workspace,settings=workspace.settings;
  $('workspaceName').value=workspace.name;$('workspaceDescription').value=workspace.description||'';$('sideName').textContent=workspace.name;
  $('startDate').value=settings.startDate||'';$('endDate').value=settings.endDate||'';$('cadence').value=settings.cadence||'continuous';$('maxPerDay').value=settings.maxExamsPerClassPerDay||1;
  $('excludedDates').value=(settings.excludedDates||[]).join(', ');$('customDates').value=(settings.customDates||[]).join(', ');
  $('weekdayChecks').innerHTML=WEEKDAYS.map(([number,name])=>`<label><input type="checkbox" data-weekday="${number}" ${(settings.excludedWeekdays||[]).map(Number).includes(Number(number))?'checked':''}> ${name}</label>`).join('');
  renderDatePreview();
}

function syncSetup(){
  const workspace=state.workspace,settings=workspace.settings;
  workspace.name=$('workspaceName').value.trim()||'Untitled Examination Schedule';workspace.description=$('workspaceDescription').value.trim();$('sideName').textContent=workspace.name;
  settings.startDate=$('startDate').value;settings.endDate=$('endDate').value;settings.cadence=$('cadence').value;settings.maxExamsPerClassPerDay=Math.max(1,Number($('maxPerDay').value)||1);
  settings.excludedDates=listValues($('excludedDates').value);settings.customDates=listValues($('customDates').value);settings.excludedWeekdays=[...document.querySelectorAll('[data-weekday]:checked')].map(item=>Number(item.dataset.weekday));
  renderDatePreview();markDirty();
}

['workspaceName','workspaceDescription','startDate','endDate','cadence','maxPerDay','excludedDates','customDates'].forEach(id=>$(id).addEventListener('change',syncSetup));
$('weekdayChecks').addEventListener('change',syncSetup);

function renderDatePreview(){
  const dates=candidateExamDates(state.workspace.settings),settings=state.workspace.settings;
  const sample=dates.slice(0,7).map(value=>displayDate(value)+' '+dayName(value)).join(' · ');
  showNotice('datePreview',dates.length?`<b>${dates.length} eligible examination date(s).</b> ${safe(sample)}${dates.length>7?' …':''}`:'<b>No eligible examination dates.</b> Check the date range, cadence and exclusions.',dates.length?'info':'warn');
}

function renderSessions(){
  const options=state.workspace.slots;
  $('sessionRows').innerHTML=options.map((slot,index)=>`<div class="sessionRow" data-session-row="${safe(slot.id)}"><label>Session name<input data-session-field="name" value="${safe(slot.name)}"></label><label>Starts<input data-session-field="startTime" type="time" value="${safe(slot.startTime)}"></label><label>Ends<input data-session-field="endTime" type="time" value="${safe(slot.endTime)}"></label><label>Duration (minutes)<input data-session-field="durationMinutes" type="number" min="15" value="${Number(slot.durationMinutes)||0}"></label><button class="button" data-remove-session="${safe(slot.id)}" ${options.length===1?'disabled':''}>Remove</button></div>`).join('');
}
$('addSession').onclick=()=>{const number=state.workspace.slots.length+1;state.workspace.slots.push({id:'SESSION_'+Date.now(),name:'Session '+number,startTime:'09:00',endTime:'12:00',durationMinutes:180});renderSessions();renderPapers();markDirty('Session added')};
$('sessionRows').addEventListener('change',event=>{const row=event.target.closest('[data-session-row]'),field=event.target.dataset.sessionField;if(!row||!field)return;const slot=slotById(row.dataset.sessionRow);if(!slot)return;slot[field]=field==='durationMinutes'?Math.max(15,Number(event.target.value)||15):event.target.value;markDirty()});
$('sessionRows').addEventListener('click',event=>{const button=event.target.closest('[data-remove-session]');if(!button||state.workspace.slots.length===1)return;const id=button.dataset.removeSession;state.workspace.slots=state.workspace.slots.filter(item=>item.id!==id);for(const paper of state.workspace.papers)if(paper.fixedSlotId===id)paper.fixedSlotId='';state.workspace.timetable={events:[],unplaced:[],dates:[],slots:[]};state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderSessions();renderPapers();renderTimetable();renderDuties();markDirty('Session removed; schedules need regeneration')});

function filteredPapers(){const search=$('paperSearch').value.trim().toLowerCase(),className=$('paperClassFilter').value;return state.workspace.papers.filter(item=>(!className||item.className===className)&&(!search||(item.className+' '+item.subject+' '+(item.teacherCodes||[]).join(' ')).toLowerCase().includes(search)))}
function renderPapers(){
  const current=$('paperClassFilter').value;$('paperClassFilter').innerHTML='<option value="">All classes</option>'+state.workspace.classes.map(value=>`<option value="${safe(value)}" ${value===current?'selected':''}>${safe(value)}</option>`).join('');
  const papers=filteredPapers();state.visiblePapers=papers.map(item=>item.id);const slotOptions='<option value="">Any session</option>'+state.workspace.slots.map(slot=>`<option value="${safe(slot.id)}">${safe(slot.name)}</option>`).join('');
  $('paperRows').innerHTML=papers.length?papers.map(item=>`<tr data-paper="${safe(item.id)}"><td><input type="checkbox" data-paper-field="included" ${item.included!==false?'checked':''}></td><td><b>${safe(item.className)}</b></td><td>${safe(item.subject)}</td><td>${safe((item.teacherCodes||[]).map(teacherName).join(', ')||'—')}</td><td><input data-paper-field="roomId" value="${safe(item.roomId||item.className)}"></td><td><input type="date" data-paper-field="fixedDate" value="${safe(item.fixedDate||'')}"></td><td><select data-paper-field="fixedSlotId">${slotOptions.replace(`value="${safe(item.fixedSlotId||'')}"`,`value="${safe(item.fixedSlotId||'')}" selected`)}</select></td></tr>`).join(''):'<tr><td colspan="7">No subjects match this filter.</td></tr>';
  const included=state.workspace.papers.filter(item=>item.included!==false).length;showNotice('paperCounts',`<b>${included}</b> of ${state.workspace.papers.length} class-subject papers included · ${papers.length} visible`,'info');
}
$('paperSearch').addEventListener('input',renderPapers);$('paperClassFilter').addEventListener('change',renderPapers);
$('paperRows').addEventListener('change',event=>{const row=event.target.closest('[data-paper]'),field=event.target.dataset.paperField;if(!row||!field)return;const paper=state.workspace.papers.find(item=>item.id===row.dataset.paper);if(!paper)return;paper[field]=field==='included'?event.target.checked:event.target.value;state.workspace.timetable={events:[],unplaced:[],dates:[],slots:[]};state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderPapers();renderTimetable();renderDuties();markDirty('Subjects changed; schedules need regeneration')});
function setVisiblePapers(included){for(const id of state.visiblePapers){const paper=state.workspace.papers.find(item=>item.id===id);if(paper)paper.included=included}state.workspace.timetable={events:[],unplaced:[],dates:[],slots:[]};state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderPapers();renderTimetable();renderDuties();markDirty(included?'Visible subjects included':'Visible subjects excluded')}
$('includeVisible').onclick=()=>setVisiblePapers(true);$('excludeVisible').onclick=()=>setVisiblePapers(false);

function renderTimetable(){
  const result=state.workspace.timetable||{events:[],unplaced:[]},validation=validateExamTimetable(state.workspace),events=result.events||[];
  $('examRows').innerHTML=events.length?events.map(item=>{const slot=slotById(item.slotId);return `<tr><td>${displayDate(item.date)}</td><td>${safe(item.day)}</td><td>${safe(slot?.name||item.slotId)}</td><td>${safe(timeText(slot))}</td><td><b>${safe(item.className)}</b></td><td>${safe(item.subject)}</td></tr>`}).join(''):'<tr><td colspan="6">No timetable generated.</td></tr>';
  $('timetableMetrics').innerHTML=[['Eligible dates',(result.dates||[]).length],['Included papers',validation.total],['Scheduled',validation.scheduled],['Unplaced',validation.unplaced]].map(([label,value])=>`<div class="metric"><strong>${value}</strong><span>${label}</span></div>`).join('');
  if(events.length)showNotice('timetableStatus',validation.valid?'<b>Timetable passes the current hard-rule checks.</b> Continue to staff availability and duty allocation.':'<b>Timetable needs attention.</b> '+validation.issues.map(item=>safe(item.message)).join(' '),validation.valid?'success':'error');
  else showNotice('timetableStatus','Complete Exam Setup and Subjects, then generate a draft timetable.','info');
  $('unplacedBlock').innerHTML=(result.unplaced||[]).length?`<div class="notice error"><b>Unscheduled papers</b><ul class="issueList">${result.unplaced.map(item=>`<li>${safe(item.className)} · ${safe(item.subject)} — ${safe(item.reason)}</li>`).join('')}</ul></div>`:'';
}
$('generateTimetable').onclick=()=>{syncSetup();state.workspace.timetable=generateExamTimetable(state.workspace);state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderTimetable();renderDuties();markDirty('Exam timetable generated');document.querySelector('[data-pane="timetable"]').scrollIntoView({behavior:'smooth'})};

function filteredTeachers(){const search=$('teacherSearch').value.trim().toLowerCase();return state.workspace.teachers.filter(item=>!search||(item.name+' '+item.code).toLowerCase().includes(search))}
function renderTeachers(){
  const teachers=filteredTeachers();state.visibleTeachers=teachers.map(item=>item.code);
  $('teacherRows').innerHTML=teachers.length?teachers.map(item=>`<tr data-teacher="${safe(item.code)}"><td><input type="checkbox" data-teacher-field="active" ${item.active!==false?'checked':''}></td><td><b>${safe(item.name)}</b></td><td>${safe(item.code)}</td><td><input type="number" min="1" max="50" data-teacher-field="maxInvigilationDuties" value="${Number(item.maxInvigilationDuties)||4}"></td><td><input type="number" min="1" max="50" data-teacher-field="maxReliefDuties" value="${Number(item.maxReliefDuties)||3}"></td><td><input data-teacher-field="unavailableSlots" value="${safe((item.unavailableSlots||[]).join(', '))}" placeholder="2026-09-03, 2026-09-05|SESSION_1"></td></tr>`).join(''):'<tr><td colspan="6">No teachers match this filter.</td></tr>';
}
$('teacherSearch').addEventListener('input',renderTeachers);
$('teacherRows').addEventListener('change',event=>{const row=event.target.closest('[data-teacher]'),field=event.target.dataset.teacherField;if(!row||!field)return;const teacher=state.workspace.teachers.find(item=>item.code===row.dataset.teacher);if(!teacher)return;if(field==='active')teacher.active=event.target.checked;else if(field==='unavailableSlots')teacher.unavailableSlots=listValues(event.target.value);else teacher[field]=Math.max(1,Number(event.target.value)||1);state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderDuties();markDirty('Staff availability changed; duties need regeneration')});
function setVisibleTeachers(active){for(const code of state.visibleTeachers){const teacher=state.workspace.teachers.find(item=>item.code===code);if(teacher)teacher.active=active}state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderTeachers();renderDuties();markDirty(active?'Visible teachers enabled':'Visible teachers disabled')}
$('enableVisibleTeachers').onclick=()=>setVisibleTeachers(true);$('disableVisibleTeachers').onclick=()=>setVisibleTeachers(false);

function syncDutySettings(){const settings=state.workspace.settings;settings.invigilatorsPerRoom=Math.max(1,Number($('invigilatorsPerRoom').value)||1);settings.maxInvigilationPerDay=Math.max(1,Number($('maxInvigPerDay').value)||1);settings.relieversPerSession=Math.max(0,Number($('relieversPerSession').value)||0);settings.avoidOwnSubject=$('avoidOwnSubject').checked;settings.relieverStartTime=$('relieverStart').value;settings.relieverEndTime=$('relieverEnd').value}
['invigilatorsPerRoom','maxInvigPerDay','relieversPerSession','avoidOwnSubject','relieverStart','relieverEnd'].forEach(id=>$(id).addEventListener('change',()=>{syncDutySettings();state.workspace.duties={invigilation:[],relievers:[],unfilled:[]};renderDuties();markDirty('Duty rules changed; allocation needs regeneration')}));

function renderDuties(){
  const settings=state.workspace.settings,duties=state.workspace.duties||{invigilation:[],relievers:[],unfilled:[]};
  $('invigilatorsPerRoom').value=settings.invigilatorsPerRoom||1;$('maxInvigPerDay').value=settings.maxInvigilationPerDay||1;$('relieversPerSession').value=settings.relieversPerSession??1;$('avoidOwnSubject').checked=settings.avoidOwnSubject===true;$('relieverStart').value=settings.relieverStartTime||'';$('relieverEnd').value=settings.relieverEndTime||'';
  const validation=validateDutyRoster(state.workspace);
  $('invigilationRows').innerHTML=duties.invigilation?.length?duties.invigilation.map(item=>`<tr><td>${displayDate(item.date)}<br><small>${safe(item.day)}</small></td><td>${safe(item.session)}</td><td>${safe(item.roomId)}</td><td><b>${safe(item.teacherName)}</b></td><td>${safe(item.teacherCode)}</td></tr>`).join(''):'<tr><td colspan="5">No allocation generated.</td></tr>';
  $('relieverRows').innerHTML=duties.relievers?.length?duties.relievers.map(item=>`<tr><td>${displayDate(item.date)}<br><small>${safe(item.day)}</small></td><td>${safe(item.session)}</td><td>${safe(item.startTime)}–${safe(item.endTime)}</td><td><b>${safe(item.teacherName)}</b></td><td>${safe(item.teacherCode)}</td></tr>`).join(''):'<tr><td colspan="5">No allocation generated.</td></tr>';
  $('dutyMetrics').innerHTML=[['Invigilation duties',validation.invigilation],['Reliever duties',validation.relievers],['Unfilled duties',validation.unfilled],['Eligible teachers',state.workspace.teachers.filter(item=>item.active!==false).length]].map(([label,value])=>`<div class="metric"><strong>${value}</strong><span>${label}</span></div>`).join('');
  if(duties.invigilation?.length||duties.relievers?.length||duties.unfilled?.length)showNotice('dutyStatus',validation.valid?'<b>Duty allocation passes all current hard-rule checks.</b> Invigilators and relievers are separated by date.':`<b>${validation.unfilled} duty position(s) remain unfilled.</b><ul class="issueList">${validation.issues.map(item=>'<li>'+safe(item.message)+'</li>').join('')}</ul>`,validation.valid?'success':'error');
  else showNotice('dutyStatus',state.workspace.timetable?.events?.length?'Set availability and duty rules, then generate the allocation.':'Generate the exam timetable before allocating duties.','info');
}
$('generateDuties').onclick=()=>{if(!state.workspace.timetable?.events?.length){showNotice('dutyStatus','<b>No exam timetable is available.</b> Generate it first.','warn');return}syncDutySettings();state.workspace.duties=generateDutyRoster(state.workspace);renderDuties();renderReview();markDirty('Duty lists generated')};

function renderReview(){
  if(!state.workspace)return;const exam=validateExamTimetable(state.workspace),duty=validateDutyRoster(state.workspace),hasDuty=!!(state.workspace.duties?.invigilation?.length||state.workspace.duties?.relievers?.length||state.workspace.duties?.unfilled?.length);
  const cards=[{label:'Exam timetable',value:exam.valid&&exam.scheduled?'Ready':exam.scheduled?'Issues':'Not generated',good:exam.valid&&exam.scheduled},{label:'Papers scheduled',value:exam.scheduled+'/'+exam.total,good:exam.valid&&exam.total>0},{label:'Duty allocation',value:hasDuty?(duty.valid?'Ready':'Issues'):'Not generated',good:hasDuty&&duty.valid},{label:'Unfilled positions',value:duty.unfilled,good:hasDuty&&duty.unfilled===0}];
  $('reviewSummary').innerHTML=cards.map(item=>`<div class="reviewCard ${item.good?'good':'bad'}"><strong>${safe(item.value)}</strong><span>${safe(item.label)}</span></div>`).join('');
}

function storageKey(){return 'vkv_exam_department_drafts_v1_'+(state.user?.uid||'anonymous')}
function readDrafts(){try{const value=JSON.parse(localStorage.getItem(storageKey())||'[]');return Array.isArray(value)?value:[]}catch(_){return []}}
function writeDrafts(value){localStorage.setItem(storageKey(),JSON.stringify(value))}
function saveDraft(){
  syncSetup();syncDutySettings();const drafts=readDrafts(),snapshot={id:'EXAM_DRAFT_'+Date.now(),name:state.workspace.name,savedAtMs:Date.now(),workspace:clone(state.workspace)};drafts.unshift(snapshot);writeDrafts(drafts.slice(0,30));state.dirty=false;setSaveState('Draft snapshot saved',false);renderDraftList();
}
$('saveDraft').onclick=saveDraft;
function renderDraftList(){if(!state.user)return;const drafts=readDrafts();$('draftList').innerHTML=drafts.length?drafts.map(item=>`<div class="draftCard"><h4>${safe(item.name)}</h4><p>${new Date(item.savedAtMs).toLocaleString('en-GB')}</p><p>${item.workspace?.timetable?.events?.length||0} papers · ${item.workspace?.duties?.invigilation?.length||0} invigilation duties</p><div class="buttonRow"><button class="button" data-open-draft="${safe(item.id)}">Open Snapshot</button></div></div>`).join(''):'<div class="empty">No saved examination drafts on this device.</div>'}
$('draftList').addEventListener('click',event=>{const button=event.target.closest('[data-open-draft]');if(!button)return;const draft=readDrafts().find(item=>item.id===button.dataset.openDraft);if(!draft)return;if(state.dirty&&!confirm('Open this saved snapshot and discard the current unsaved changes?'))return;state.workspace=clone(draft.workspace);state.dirty=false;renderAll();setSaveState('Saved snapshot opened',false);document.querySelector('[data-pane-target="setup"]').click()});
$('newDraft').onclick=()=>{if(state.dirty&&!confirm('Start a new draft from the active master and discard current unsaved changes?'))return;state.workspace=createWorkspaceFromMaster(state.master);state.dirty=true;renderAll();setSaveState('New unsaved draft',true);document.querySelector('[data-pane-target="setup"]').click()};

function csvCell(value){const text=String(value??'');return /[",\n]/.test(text)?'"'+text.replace(/"/g,'""')+'"':text}
function download(name,rows){const csv='\ufeff'+rows.map(row=>row.map(csvCell).join(',')).join('\r\n'),blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
$('downloadExamCsv').onclick=()=>download('exam-timetable.csv',[['Date','Day','Session','Start','End','Class','Subject'],...(state.workspace.timetable?.events||[]).map(item=>{const slot=slotById(item.slotId)||{};return [item.date,item.day,slot.name||item.slotId,slot.startTime||'',slot.endTime||'',item.className,item.subject]})]);
$('downloadDutyCsv').onclick=()=>download('exam-duty-lists.csv',[['Role','Date','Day','Session','Time','Room / Class','Teacher','Code'],...(state.workspace.duties?.invigilation||[]).map(item=>['Invigilator',item.date,item.day,item.session,'',item.roomId,item.teacherName,item.teacherCode]),...(state.workspace.duties?.relievers||[]).map(item=>['Reliever',item.date,item.day,item.session,item.startTime+'-'+item.endTime,'',item.teacherName,item.teacherCode])]);
function printPane(name){const pane=document.querySelector(`[data-pane="${name}"]`);document.querySelectorAll('.pane').forEach(item=>item.classList.remove('printing'));pane.classList.add('printing');window.print();setTimeout(()=>pane.classList.remove('printing'),500)}
$('printExam').onclick=()=>printPane('timetable');$('printDuties').onclick=()=>printPane('duties');window.addEventListener('afterprint',()=>document.querySelectorAll('.pane').forEach(item=>item.classList.remove('printing')));
window.addEventListener('beforeunload',event=>{if(state.dirty){event.preventDefault();event.returnValue=''}});
