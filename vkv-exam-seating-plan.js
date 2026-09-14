import {deriveMasterVenues,logicalClassName,reconcileSeating,seatingSummary} from './exam-seating-core.js?v=20260914-printable-seat-plan-2';

const $=id=>document.getElementById(id);
const safe=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const api=()=>window.vkvExamWorkspace;
const workspace=()=>api()?.getWorkspace?.();

function selectedClasses(ws){
  return [...new Set((ws?.papers||[]).filter(item=>item.included!==false).map(item=>logicalClassName(item.className)).filter(Boolean))];
}
function importedVenues(ws){
  const fallbacks=[...(ws?.classes||[]),...(ws?.papers||[]).map(item=>item.roomId||item.className)];
  return deriveMasterVenues(api()?.getMaster?.()||{},fallbacks);
}
function model(){
  const ws=workspace();if(!ws)return null;
  ws.seating=reconcileSeating(ws.seating||{},selectedClasses(ws),importedVenues(ws));
  return ws.seating;
}
function capacity(venue){return 2*(Number(venue.twoSeaterBenches)||0)+3*(Number(venue.threeSeaterBenches)||0)}
function rowLabel(row){return row.className+(row.sectionName?' · '+row.sectionName:'')}
function studentLabel(student){return student?student.className+(student.sectionName?' '+student.sectionName:'')+' · Roll '+student.rollNo:'Vacant'}

function injectStyles(){
  if($('examSeatingStyles'))return;
  const style=document.createElement('style');style.id='examSeatingStyles';style.textContent=`
    .seatingMetrics{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:12px;margin:14px 0}
    .seatingMetric{border:1px solid var(--line,#d9e2ea);border-radius:14px;padding:14px;background:var(--surface,#fff)}
    .seatingMetric strong{display:block;font-size:1.55rem}.seatingMetric span{font-size:.82rem;opacity:.75}
    .sourceBadge{display:inline-block;border-radius:999px;padding:3px 8px;background:#e7f4ff;color:#075985;font-size:.72rem;font-weight:700}
    .sourceBadge.manual{background:#f4e8ff;color:#6b21a8}.seatingBalance.good{color:#166534}.seatingBalance.bad{color:#b91c1c}
    .seatPlanOutput{display:grid;gap:18px;margin-top:14px}.seatPlanSheet{background:#fff;border:1px solid #20313c;padding:18px;color:#111}
    .seatPlanSchool{text-align:center;font-family:Georgia,serif}.seatPlanSchool h2{margin:0;font-size:1.2rem;text-transform:uppercase}.seatPlanSchool h3{margin:3px 0;font-size:1rem}.seatPlanSchool p{margin:2px 0;font-size:.82rem}
    .seatPlanMeta{display:grid;grid-template-columns:1fr 1fr;border:1px solid #333;margin:12px 0}.seatPlanMeta div{padding:6px 8px;border-right:1px solid #333;font-size:.82rem}.seatPlanMeta div:last-child{border-right:0}
    .seatPlanRanges{width:100%;min-width:0;margin-bottom:10px}.seatPlanRanges th,.seatPlanRanges td{border:1px solid #333;font-size:.74rem;padding:5px}
    .benchGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.benchCard{border:1px solid #333;break-inside:avoid}.benchTitle{text-align:center;border-bottom:1px solid #333;padding:3px;font-weight:800;font-size:.7rem;background:#f2f2f2}
    .benchSeats{display:grid}.benchSeats.two{grid-template-columns:repeat(2,1fr)}.benchSeats.three{grid-template-columns:repeat(3,1fr)}.benchSeat{min-height:44px;padding:5px 3px;text-align:center;font-size:.68rem;border-right:1px solid #555;display:grid;place-items:center}.benchSeat:last-child{border-right:0}.benchSeat.vacant{color:#777}
    .seatPlanFoot{display:flex;justify-content:space-between;margin-top:22px;font-size:.76rem}.seatPlanWarning{padding:10px;border:1px solid #d97706;background:#fff7ed;color:#9a3412;border-radius:8px}
    @media(max-width:760px){.seatingMetrics{grid-template-columns:repeat(2,minmax(0,1fr))}.benchGrid{grid-template-columns:1fr 1fr}}
    @media print{
      body.printingSeatPlan .topbar,body.printingSeatPlan .sidebar,body.printingSeatPlan .pane:not([data-pane="seatingPlan"]),body.printingSeatPlan [data-pane="seatingPlan"]>*:not(.surface:last-child){display:none!important}
      body.printingSeatPlan .appShell,body.printingSeatPlan .workspace,body.printingSeatPlan [data-pane="seatingPlan"],body.printingSeatPlan [data-pane="seatingPlan"]>.surface:last-child{display:block!important;padding:0;margin:0;border:0;box-shadow:none}
      body.printingSeatPlan .sectionTitle,body.printingSeatPlan .seatPlanOutput>.empty{display:none!important}
      body.printingSeatPlan .seatPlanSheet{page-break-after:always;border:0;padding:8mm;min-height:270mm}.benchGrid{grid-template-columns:repeat(3,1fr)}
    }
  `;document.head.appendChild(style);
}

function renderReviewCard(summary){
  const host=$('reviewSummary');if(!host)return;
  host.querySelector('[data-seating-review]')?.remove();
  const card=document.createElement('div');card.className='reviewCard '+(summary.ready?'good':'bad');card.dataset.seatingReview='true';
  card.innerHTML=`<strong>${summary.ready?'Ready':summary.totalStudents?summary.totalSeats+'/'+summary.totalStudents+' seats':'Incomplete'}</strong><span>Seating capacity</span>`;
  host.appendChild(card);
}

function roomRanges(room){
  const map=new Map();
  room.benches.flatMap(bench=>bench.students).filter(Boolean).forEach(student=>{
    const key=student.className+'|'+student.sectionName;
    const old=map.get(key)||{className:student.className,sectionName:student.sectionName,rolls:[]};old.rolls.push(student.rollNo);map.set(key,old);
  });
  return [...map.values()].map(item=>({...item,from:Math.min(...item.rolls),to:Math.max(...item.rolls),count:item.rolls.length}));
}
function renderPlan(plan){
  const host=$('seatingPlanOutput'),button=$('printSeatingPlan');if(!host)return;
  if(!plan?.rooms?.length){host.innerHTML='<div class="empty">Enter strengths and venue capacities, then generate the plan.</div>';if(button)button.disabled=true;return}
  const ws=workspace(),examName=safe(ws?.name||ws?.workspaceName||$('workspaceName')?.value||'Examination');
  host.innerHTML=plan.rooms.map(room=>{
    const ranges=roomRanges(room);
    return `<section class="seatPlanSheet"><header class="seatPlanSchool"><h2>Vivekananda Kendra Vidyalaya, Nalbari</h2><h3>${examName}</h3><p><b>ROOM-WISE SEATING PLAN</b></p></header>
      <div class="seatPlanMeta"><div><b>Venue / Room:</b> ${safe(room.venueName)}</div><div><b>Students allotted:</b> ${room.studentCount} &nbsp; | &nbsp; <b>Capacity:</b> ${room.capacity}</div></div>
      <table class="seatPlanRanges"><thead><tr><th>Class</th><th>Section / Stream</th><th>Roll Nos.</th><th>Total</th></tr></thead><tbody>${ranges.map(item=>`<tr><td>${safe(item.className)}</td><td>${safe(item.sectionName||'—')}</td><td>${item.from===item.to?item.from:item.from+'–'+item.to}</td><td>${item.count}</td></tr>`).join('')}</tbody></table>
      <div class="benchGrid">${room.benches.map(bench=>`<article class="benchCard"><div class="benchTitle">BENCH ${String(bench.number).padStart(2,'0')} · ${bench.size}-SEATER</div><div class="benchSeats ${bench.size===3?'three':'two'}">${bench.students.map(student=>`<div class="benchSeat ${student?'':'vacant'}">${safe(studentLabel(student))}</div>`).join('')}</div></article>`).join('')}</div>
      <footer class="seatPlanFoot"><span>Prepared by: ____________________</span><span>Invigilator: ____________________</span><span>Principal: ____________________</span></footer></section>`;
  }).join('');
  if(plan.unseated?.length)host.insertAdjacentHTML('afterbegin',`<div class="seatPlanWarning"><b>${plan.unseated.length} student(s) could not be seated.</b> Add capacity and generate again.</div>`);
  if(button)button.disabled=false;
}
function render(){
  const seating=model(),ws=workspace(),pane=$('seatingPlanPane');if(!seating||!ws||!pane)return;
  const summary=seatingSummary(seating),strengthHost=$('seatingStrengthRows'),venueHost=$('seatingVenueRows');
  $('seatingClassCount').textContent=String(summary.classCount);$('seatingStudentTotal').textContent=String(summary.totalStudents);$('seatingSeatTotal').textContent=String(summary.totalSeats);
  $('seatingBalance').textContent=(summary.balance>=0?'+':'')+String(summary.balance);$('seatingBalance').className='seatingBalance '+(summary.balance>=0?'good':'bad');
  strengthHost.innerHTML=seating.sectionStrengths.length?seating.sectionStrengths.map((row,index)=>`<tr><td><b>${safe(row.className)}</b></td><td>${safe(row.sectionName||'Single section')}</td><td><input type="number" min="0" max="999" inputmode="numeric" data-strength-index="${index}" value="${Number(row.strength)||''}" placeholder="Enter strength"></td><td><input type="number" min="1" max="999" inputmode="numeric" data-roll-index="${index}" value="${Math.max(1,Number(row.startingRollNo)||1)}"></td></tr>`).join(''):'<tr><td colspan="4">Select at least one class in the Subjects step. Its section-strength rows will appear here automatically.</td></tr>';
  venueHost.innerHTML=seating.venues.length?seating.venues.map((venue,index)=>`<tr><td><input type="checkbox" data-venue-field="active" data-venue-index="${index}" ${venue.active!==false?'checked':''}></td><td><b>${safe(venue.name)}</b><br><span class="sourceBadge ${venue.source==='manual'?'manual':''}">${venue.source==='manual'?'Added venue':'Master timetable'}</span></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="twoSeaterBenches" data-venue-index="${index}" value="${Number(venue.twoSeaterBenches)||0}"></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="threeSeaterBenches" data-venue-index="${index}" value="${Number(venue.threeSeaterBenches)||0}"></td><td><b>${capacity(venue)}</b></td><td>${venue.source==='manual'?'<button type="button" class="button" data-remove-venue="'+index+'">Remove</button>':'—'}</td></tr>`).join(''):'<tr><td colspan="6">No class venues were found. Add a venue below.</td></tr>';
  const status=summary.missingStrengths?'<b>'+summary.missingStrengths+' section strength(s) still need to be entered.</b>':summary.balance<0?'<b>Seating shortage: '+Math.abs(summary.balance)+' seat(s).</b> Add benches or venues before preparing the final plan.':summary.totalStudents?'<b>Capacity is sufficient.</b> '+summary.balance+' extra seat(s) available.':'<b>Total students will appear after class-section strengths are entered.</b>';
  const kind=summary.missingStrengths?'warn':summary.balance<0?'error':summary.totalStudents?'success':'info';const notice=$('seatingStatus');notice.className='notice '+kind;notice.innerHTML=status;
  renderPlan(seating.plan);renderReviewCard(summary);
}
function changed(message){
  const ws=workspace();if(ws?.seating){ws.seating.updatedAtMs=Date.now();ws.seating.plan=null}
  api()?.markDirty?.(message);render();
}
function buildMixedStudents(rows){
  const pools=rows.filter(row=>Number(row.strength)>0).map(row=>({key:rowLabel(row),items:Array.from({length:Number(row.strength)},(_,i)=>({className:row.className,sectionName:row.sectionName||'',rollNo:Math.max(1,Number(row.startingRollNo)||1)+i}))}));
  const result=[];let last='';
  while(pools.some(pool=>pool.items.length)){
    pools.sort((a,b)=>b.items.length-a.items.length);
    const pick=pools.find(pool=>pool.items.length&&pool.key!==last)||pools.find(pool=>pool.items.length);
    result.push(pick.items.shift());last=pick.key;
  }
  return result;
}
function generatePlan(){
  const seating=model(),summary=seatingSummary(seating);if(!seating)return;
  if(summary.missingStrengths){alert('Please enter every class-section strength before generating the seat plan.');return}
  if(!summary.venueCount||!summary.totalSeats){alert('Please select venues and enter bench numbers first.');return}
  const queue=buildMixedStudents(seating.sectionStrengths),rooms=[];
  for(const venue of seating.venues.filter(item=>item.active!==false)){
    const sizes=[...Array(Number(venue.twoSeaterBenches)||0).fill(2),...Array(Number(venue.threeSeaterBenches)||0).fill(3)],benches=[];let studentCount=0;
    sizes.forEach((size,index)=>{const students=Array.from({length:size},()=>queue.shift()||null);studentCount+=students.filter(Boolean).length;benches.push({number:index+1,size,students})});
    if(benches.length)rooms.push({venueId:venue.id,venueName:venue.name,capacity:capacity(venue),studentCount,benches});
  }
  seating.plan={schemaVersion:1,generatedAtMs:Date.now(),rooms,unseated:queue,totalStudents:summary.totalStudents,totalSeats:summary.totalSeats};
  seating.updatedAtMs=Date.now();api()?.markDirty?.('Room-wise seating plan generated');render();
}
function printPlan(){
  const seating=model();if(!seating?.plan?.rooms?.length){alert('Generate the seat plan first.');return}
  document.body.classList.add('printingSeatPlan');window.addEventListener('afterprint',()=>document.body.classList.remove('printingSeatPlan'),{once:true});window.print();
}
function bind(){
  injectStyles();
  $('seatingStrengthRows')?.addEventListener('change',event=>{
    const strengthIndex=Number(event.target.dataset.strengthIndex),rollIndex=Number(event.target.dataset.rollIndex),seating=model();
    if(Number.isInteger(strengthIndex)&&seating?.sectionStrengths[strengthIndex])seating.sectionStrengths[strengthIndex].strength=Math.max(0,Number(event.target.value)||0);
    else if(Number.isInteger(rollIndex)&&seating?.sectionStrengths[rollIndex])seating.sectionStrengths[rollIndex].startingRollNo=Math.max(1,Number(event.target.value)||1);else return;
    changed('Class-section roll details updated');
  });
  $('seatingVenueRows')?.addEventListener('change',event=>{const index=Number(event.target.dataset.venueIndex),field=event.target.dataset.venueField;if(!Number.isInteger(index)||!field)return;const seating=model(),venue=seating?.venues[index];if(!venue)return;venue[field]=field==='active'?event.target.checked:Math.max(0,Number(event.target.value)||0);changed('Seating venue capacity updated')});
  $('seatingVenueRows')?.addEventListener('click',event=>{const button=event.target.closest('[data-remove-venue]');if(!button)return;const seating=model(),index=Number(button.dataset.removeVenue);if(!seating?.venues[index])return;seating.venues.splice(index,1);changed('Added venue removed')});
  $('addSeatingVenue')?.addEventListener('click',()=>{const input=$('newSeatingVenue'),name=input.value.trim();if(!name){input.focus();return}const seating=model();if(seating.venues.some(item=>item.name.toLowerCase()===name.toLowerCase())){alert('This venue is already listed.');return}seating.venues.push({id:'VENUE_MANUAL_'+Date.now(),name,source:'manual',active:true,twoSeaterBenches:0,threeSeaterBenches:0});input.value='';changed('New seating venue added')});
  $('reimportSeatingVenues')?.addEventListener('click',()=>{const ws=workspace();ws.seating=reconcileSeating(ws.seating||{},selectedClasses(ws),importedVenues(ws));changed('Class venues refreshed from Master Timetable')});
  $('generateSeatingPlan')?.addEventListener('click',generatePlan);$('printSeatingPlan')?.addEventListener('click',printPlan);$('printSeatPlanReview')?.addEventListener('click',printPlan);
  document.addEventListener('vkv-exam-workspace-rendered',render);document.addEventListener('vkv-exam-workspace-subjects-applied',()=>setTimeout(render,0));
  document.addEventListener('change',event=>{if(event.target.closest?.('#paperRows,#majorClassGrid,#majorSubjectGrid'))setTimeout(render,40)});
  document.addEventListener('click',event=>{if(event.target.closest?.('[data-pane-target="seatingPlan"]'))setTimeout(render,0)});render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
