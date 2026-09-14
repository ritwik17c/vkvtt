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
    .seatPlanSummarySheet{background:#fff;border:1px solid #20313c;padding:18px;color:#111}.seatPlanSummaryTable{width:100%;min-width:0}.seatPlanSummaryTable th,.seatPlanSummaryTable td{border:1px solid #222;padding:7px;text-align:center}.seatPlanSummaryTable th{background:#f0f0f0}.summaryRoom,.summaryGrand{font-weight:800}\n    .roomStickerPack{display:grid;gap:18px}.roomStickerSheet{background:#fff;border:2px solid #111;padding:18px;color:#111}.roomStickerTitle{text-align:center;margin:0 0 8px;font-size:1.15rem}.roomFront,.roomEntrance{text-align:center;border:1px solid #333;background:#f3f3f3;padding:5px;margin:8px 0;font-size:.72rem;font-weight:850;letter-spacing:.08em}.roomStickerSheet .benchGrid{grid-template-columns:repeat(var(--bench-cols,3),minmax(0,1fr))}\n    @media print{
      body.printingSeatingSummary .topbar,body.printingSeatingSummary .sidebar,body.printingSeatingSummary .pane:not([data-pane="seatingPlan"]),body.printingSeatingSummary [data-pane="seatingPlan"]>*:not(.surface:last-child),
      body.printingRoomStickers .topbar,body.printingRoomStickers .sidebar,body.printingRoomStickers .pane:not([data-pane="seatingPlan"]),body.printingRoomStickers [data-pane="seatingPlan"]>*:not(.surface:last-child){display:none!important}
      body.printingSeatingSummary .appShell,body.printingSeatingSummary .workspace,body.printingSeatingSummary [data-pane="seatingPlan"],body.printingSeatingSummary [data-pane="seatingPlan"]>.surface:last-child,
      body.printingRoomStickers .appShell,body.printingRoomStickers .workspace,body.printingRoomStickers [data-pane="seatingPlan"],body.printingRoomStickers [data-pane="seatingPlan"]>.surface:last-child{display:block!important;padding:0;margin:0;border:0;box-shadow:none}
      body.printingSeatingSummary .sectionTitle,body.printingSeatingSummary .roomStickerPack,
      body.printingRoomStickers .sectionTitle,body.printingRoomStickers .seatPlanSummarySheet{display:none!important}
      body.printingSeatingSummary .seatPlanSummarySheet{display:block!important;border:0;padding:8mm}
      body.printingRoomStickers .roomStickerPack{display:block!important}
      body.printingRoomStickers .roomStickerSheet{display:block!important;page-break-after:always;border:0;padding:8mm;min-height:270mm}
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
  const host=$('seatingPlanOutput'),summaryButton=$('printSeatingSummary'),stickerButton=$('printRoomStickers');if(!host)return;
  if(!plan?.rooms?.length){host.innerHTML='<div class="empty">Enter strengths and venue capacities, then generate the plan.</div>';if(summaryButton)summaryButton.disabled=true;if(stickerButton)stickerButton.disabled=true;return}
  const ws=workspace(),examName=safe(ws?.name||ws?.workspaceName||$('workspaceName')?.value||'Examination');
  const summaryRows=plan.rooms.flatMap(room=>{const ranges=roomRanges(room);return ranges.map((item,index)=>`<tr>${index===0?`<td class="summaryRoom" rowspan="${ranges.length}">${safe(room.venueName)}</td>`:''}<td>${safe(item.className+(item.sectionName?' - '+item.sectionName:'')}</td><td>${item.from===item.to?item.from:item.from+' - '+item.to}</td><td>${item.count}</td>${index===0?`<td class="summaryGrand" rowspan="${ranges.length}">${room.studentCount}</td>`:''}</tr>`)});
  const summary=`<section class="seatPlanSummarySheet"><header class="seatPlanSchool"><h2>Vivekananda Kendra Vidyalaya, Nalbari</h2><h3>SEAT PLAN</h3><p><b>${examName}</b></p></header><table class="seatPlanSummaryTable"><thead><tr><th>Class Room</th><th>Class</th><th>Roll No. Range</th><th>Total No.</th><th>Grand Total</th></tr></thead><tbody>${summaryRows.join('')}</tbody></table><footer class="seatPlanFoot"><span>Exam Dept.</span><span>VKV Nalbari</span></footer></section>`;
  const stickers=`<div class="roomStickerPack">${plan.rooms.map(room=>{const ranges=roomRanges(room);return `<section class="roomStickerSheet"><header class="seatPlanSchool"><h2>Vivekananda Kendra Vidyalaya, Nalbari</h2><h3>${examName}</h3></header><h3 class="roomStickerTitle">ROOM-WISE SEAT PLAN · ${safe(room.venueName)}</h3><div class="seatPlanMeta"><div><b>Students:</b> ${room.studentCount}</div><div><b>Room Capacity:</b> ${room.capacity}</div></div><table class="seatPlanRanges"><thead><tr><th>Class</th><th>Section / Stream</th><th>Roll Nos.</th><th>Total</th></tr></thead><tbody>${ranges.map(item=>`<tr><td>${safe(item.className)}</td><td>${safe(item.sectionName||'—')}</td><td>${item.from===item.to?item.from:item.from+' - '+item.to}</td><td>${item.count}</td></tr>`).join('')}</tbody></table><div class="roomFront">FRONT · INVIGILATOR'S TABLE / BOARD</div><div class="benchGrid" style="--bench-cols:${Math.max(1,Math.min(6,Number(room.benchesPerRow)||3))}">${room.benches.map(bench=>`<article class="benchCard"><div class="benchTitle">BENCH ${String(bench.number).padStart(2,'0')} · ${bench.size}-SEATER</div><div class="benchSeats ${bench.size===3?'three':'two'}">${bench.students.map(student=>`<div class="benchSeat ${student?'':'vacant'}">${safe(studentLabel(student))}</div>`).join('')}</div></article>`).join('')}</div><div class="roomEntrance">ENTRANCE</div></section>`}).join('')}</div>`;
  host.innerHTML=summary+stickers;
  if(plan.unseated?.length)host.insertAdjacentHTML('afterbegin',`<div class="seatPlanWarning"><b>${plan.unseated.length} student(s) could not be seated.</b> Add capacity and generate again.</div>`);
  if(summaryButton)summaryButton.disabled=false;if(stickerButton)stickerButton.disabled=false;
}
function render(){
  const seating=model(),ws=workspace(),pane=$('seatingPlanPane');if(!seating||!ws||!pane)return;
  const summary=seatingSummary(seating),strengthHost=$('seatingStrengthRows'),venueHost=$('seatingVenueRows');
  $('seatingClassCount').textContent=String(summary.classCount);$('seatingStudentTotal').textContent=String(summary.totalStudents);$('seatingSeatTotal').textContent=String(summary.totalSeats);
  $('seatingBalance').textContent=(summary.balance>=0?'+':'')+String(summary.balance);$('seatingBalance').className='seatingBalance '+(summary.balance>=0?'good':'bad');
  strengthHost.innerHTML=seating.sectionStrengths.length?seating.sectionStrengths.map((row,index)=>`<tr><td><b>${safe(row.className)}</b></td><td>${safe(row.sectionName||'Single section')}</td><td><input type="number" min="0" max="999" inputmode="numeric" data-strength-index="${index}" value="${Number(row.strength)||''}" placeholder="Enter strength"></td><td><input type="number" min="1" max="999" inputmode="numeric" data-roll-index="${index}" value="${Math.max(1,Number(row.startingRollNo)||1)}"></td></tr>`).join(''):'<tr><td colspan="4">Select at least one class in the Subjects step. Its section-strength rows will appear here automatically.</td></tr>';
  venueHost.innerHTML=seating.venues.length?seating.venues.map((venue,index)=>`<tr><td><input type="checkbox" data-venue-field="active" data-venue-index="${index}" ${venue.active!==false?'checked':''}></td><td><b>${safe(venue.name)}</b><br><span class="sourceBadge ${venue.source==='manual'?'manual':''}">${venue.source==='manual'?'Added venue':'Master timetable'}</span></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="twoSeaterBenches" data-venue-index="${index}" value="${Number(venue.twoSeaterBenches)||0}"></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="threeSeaterBenches" data-venue-index="${index}" value="${Number(venue.threeSeaterBenches)||0}"></td><td><input type="number" min="1" max="6" inputmode="numeric" data-venue-field="benchesPerRow" data-venue-index="${index}" value="${Math.max(1,Math.min(6,Number(venue.benchesPerRow)||3))}"></td><td><b>${capacity(venue)}</b></td><td>${venue.source==='manual'?'<button type="button" class="button" data-remove-venue="'+index+'">Remove</button>':'—'}</td></tr>`).join(''):'<tr><td colspan="7">No class venues were found. Add a venue below.</td></tr>';
  const status=summary.missingStrengths?'<b>'+summary.missingStrengths+' section strength(s) still need to be entered.</b>':summary.balance<0?'<b>Seating shortage: '+Math.abs(summary.balance)+' seat(s).</b> Add benches or venues before preparing the final plan.':summary.totalStudents?'<b>Capacity is sufficient.</b> '+summary.balance+' extra seat(s) available.':'<b>Total students will appear after class-section strengths are entered.</b>';
  const kind=summary.missingStrengths?'warn':summary.balance<0?'error':summary.totalStudents?'success':'info';const notice=$('seatingStatus');notice.className='notice '+kind;notice.innerHTML=status;
  renderPlan(seating.plan);renderReviewCard(summary);
}
function changed(message){
  const ws=workspace();if(ws?.seating){ws.seating.updatedAtMs=Date.now();ws.seating.plan=null}
  api()?.markDirty?.(message);render();
}
function buildStudentPools(rows){
  return rows.filter(row=>Number(row.strength)>0).map(row=>({key:rowLabel(row),items:Array.from({length:Number(row.strength)},(_,i)=>({className:row.className,sectionName:row.sectionName||'',rollNo:Math.max(1,Number(row.startingRollNo)||1)+i}))}));
}
function takeRoomStudents(pools,roomCapacity){
  const result=[];let last='';
  while(result.length<roomCapacity&&pools.some(pool=>pool.items.length)){
    const active=pools.filter(pool=>pool.items.length).sort((a,b)=>b.items.length-a.items.length);
    const used=new Set(result.map(student=>student.className+'|'+student.sectionName));
    let candidates=active.filter(pool=>used.has(pool.key));
    if(candidates.length<2){const newcomer=active.find(pool=>!used.has(pool.key));if(newcomer)candidates.push(newcomer)}
    candidates=candidates.filter(pool=>pool.items.length).sort((a,b)=>b.items.length-a.items.length);
    const pick=candidates.find(pool=>pool.key!==last)||candidates[0]||active[0];
    result.push(pick.items.shift());last=pick.key;
  }
  return result;
}
function generatePlan(){
  const seating=model(),summary=seatingSummary(seating);if(!seating)return;
  if(summary.missingStrengths){alert('Please enter every class-section strength before generating the seat plan.');return}
  if(!summary.venueCount||!summary.totalSeats){alert('Please select venues and enter bench numbers first.');return}
  const pools=buildStudentPools(seating.sectionStrengths),rooms=[];
  for(const venue of seating.venues.filter(item=>item.active!==false)){
    const sizes=[...Array(Number(venue.twoSeaterBenches)||0).fill(2),...Array(Number(venue.threeSeaterBenches)||0).fill(3)];
    const roomQueue=takeRoomStudents(pools,sizes.reduce((sum,size)=>sum+size,0)),benches=[];let studentCount=0;
    sizes.forEach((size,index)=>{const students=Array.from({length:size},()=>roomQueue.shift()||null);studentCount+=students.filter(Boolean).length;benches.push({number:index+1,size,students})});
    if(benches.length)rooms.push({venueId:venue.id,venueName:venue.name,capacity:capacity(venue),studentCount,benchesPerRow:Math.max(1,Math.min(6,Number(venue.benchesPerRow)||3)),benches});
  }
  const unseated=pools.flatMap(pool=>pool.items);
  seating.plan={schemaVersion:2,generatedAtMs:Date.now(),rooms,unseated,totalStudents:summary.totalStudents,totalSeats:summary.totalSeats};
  seating.updatedAtMs=Date.now();api()?.markDirty?.('Seat plan summary and room stickers generated');render();
}
function printOutput(kind){
  const seating=model();if(!seating?.plan?.rooms?.length){alert('Generate the seat plan first.');return}
  const className=kind==='summary'?'printingSeatingSummary':'printingRoomStickers';document.body.classList.add(className);
  window.addEventListener('afterprint',()=>document.body.classList.remove(className),{once:true});window.print();
}
function bind(){
  injectStyles();
  $('seatingStrengthRows')?.addEventListener('change',event=>{
    const strengthIndex=Number(event.target.dataset.strengthIndex),rollIndex=Number(event.target.dataset.rollIndex),seating=model();
    if(Number.isInteger(strengthIndex)&&seating?.sectionStrengths[strengthIndex])seating.sectionStrengths[strengthIndex].strength=Math.max(0,Number(event.target.value)||0);
    else if(Number.isInteger(rollIndex)&&seating?.sectionStrengths[rollIndex])seating.sectionStrengths[rollIndex].startingRollNo=Math.max(1,Number(event.target.value)||1);else return;
    changed('Class-section roll details updated');
  });
  $('seatingVenueRows')?.addEventListener('change',event=>{const index=Number(event.target.dataset.venueIndex),field=event.target.dataset.venueField;if(!Number.isInteger(index)||!field)return;const seating=model(),venue=seating?.venues[index];if(!venue)return;venue[field]=field==='active'?event.target.checked:field==='benchesPerRow'?Math.max(1,Math.min(6,Number(event.target.value)||3)):Math.max(0,Number(event.target.value)||0);changed('Seating venue capacity updated')});
  $('seatingVenueRows')?.addEventListener('click',event=>{const button=event.target.closest('[data-remove-venue]');if(!button)return;const seating=model(),index=Number(button.dataset.removeVenue);if(!seating?.venues[index])return;seating.venues.splice(index,1);changed('Added venue removed')});
  $('addSeatingVenue')?.addEventListener('click',()=>{const input=$('newSeatingVenue'),name=input.value.trim();if(!name){input.focus();return}const seating=model();if(seating.venues.some(item=>item.name.toLowerCase()===name.toLowerCase())){alert('This venue is already listed.');return}seating.venues.push({id:'VENUE_MANUAL_'+Date.now(),name,source:'manual',active:true,twoSeaterBenches:0,threeSeaterBenches:0,benchesPerRow:3});input.value='';changed('New seating venue added')});
  $('reimportSeatingVenues')?.addEventListener('click',()=>{const ws=workspace();ws.seating=reconcileSeating(ws.seating||{},selectedClasses(ws),importedVenues(ws));changed('Class venues refreshed from Master Timetable')});
  $('generateSeatingPlan')?.addEventListener('click',generatePlan);$('printSeatingSummary')?.addEventListener('click',()=>printOutput('summary'));$('printRoomStickers')?.addEventListener('click',()=>printOutput('stickers'));$('printSeatPlanSummaryReview')?.addEventListener('click',()=>printOutput('summary'));$('printRoomStickersReview')?.addEventListener('click',()=>printOutput('stickers'));
  document.addEventListener('vkv-exam-workspace-rendered',render);document.addEventListener('vkv-exam-workspace-subjects-applied',()=>setTimeout(render,0));
  document.addEventListener('change',event=>{if(event.target.closest?.('#paperRows,#majorClassGrid,#majorSubjectGrid'))setTimeout(render,40)});
  document.addEventListener('click',event=>{if(event.target.closest?.('[data-pane-target="seatingPlan"]'))setTimeout(render,0)});render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
