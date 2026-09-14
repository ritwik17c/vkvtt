import {deriveMasterVenues,logicalClassName,reconcileSeating,seatingSummary} from './exam-seating-core.js?v=20260914-classwise-seating-1';

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
function label(row){return row.sectionName?row.className+' · '+row.sectionName:row.className}
function capacity(venue){return 2*(Number(venue.twoSeaterBenches)||0)+3*(Number(venue.threeSeaterBenches)||0)}

function injectStyles(){
  if($('examSeatingStyles'))return;
  const style=document.createElement('style');style.id='examSeatingStyles';style.textContent=`
    .seatingMetrics{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:12px;margin:14px 0}
    .seatingMetric{border:1px solid var(--line,#d9e2ea);border-radius:14px;padding:14px;background:var(--surface,#fff)}
    .seatingMetric strong{display:block;font-size:1.55rem}.seatingMetric span{font-size:.82rem;opacity:.75}
    .sourceBadge{display:inline-block;border-radius:999px;padding:3px 8px;background:#e7f4ff;color:#075985;font-size:.72rem;font-weight:700}
    .sourceBadge.manual{background:#f4e8ff;color:#6b21a8}.seatingBalance.good{color:#166534}.seatingBalance.bad{color:#b91c1c}
    @media(max-width:760px){.seatingMetrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;document.head.appendChild(style);
}

function renderReviewCard(summary){
  const host=$('reviewSummary');if(!host)return;
  host.querySelector('[data-seating-review]')?.remove();
  const card=document.createElement('div');card.className='reviewCard '+(summary.ready?'good':'bad');card.dataset.seatingReview='true';
  card.innerHTML=`<strong>${summary.ready?'Ready':summary.totalStudents?summary.totalSeats+'/'+summary.totalStudents+' seats':'Incomplete'}</strong><span>Seating capacity</span>`;
  host.appendChild(card);
}

function render(){
  const seating=model(),ws=workspace(),pane=$('seatingPlanPane');if(!seating||!ws||!pane)return;
  const summary=seatingSummary(seating),strengthHost=$('seatingStrengthRows'),venueHost=$('seatingVenueRows');
  $('seatingClassCount').textContent=String(summary.classCount);
  $('seatingStudentTotal').textContent=String(summary.totalStudents);
  $('seatingSeatTotal').textContent=String(summary.totalSeats);
  $('seatingBalance').textContent=(summary.balance>=0?'+':'')+String(summary.balance);
  $('seatingBalance').className='seatingBalance '+(summary.balance>=0?'good':'bad');
  strengthHost.innerHTML=seating.sectionStrengths.length?seating.sectionStrengths.map((row,index)=>`<tr><td><b>${safe(row.className)}</b></td><td>${safe(row.sectionName||'Single section')}</td><td><input type="number" min="0" max="999" inputmode="numeric" data-strength-index="${index}" value="${Number(row.strength)||''}" placeholder="Enter strength"></td></tr>`).join(''):'<tr><td colspan="3">Select at least one class in the Classes step. Its section-strength rows will appear here automatically.</td></tr>';
  venueHost.innerHTML=seating.venues.length?seating.venues.map((venue,index)=>`<tr><td><input type="checkbox" data-venue-field="active" data-venue-index="${index}" ${venue.active!==false?'checked':''}></td><td><b>${safe(venue.name)}</b><br><span class="sourceBadge ${venue.source==='manual'?'manual':''}">${venue.source==='manual'?'Added venue':'Master timetable'}</span></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="twoSeaterBenches" data-venue-index="${index}" value="${Number(venue.twoSeaterBenches)||0}"></td><td><input type="number" min="0" max="999" inputmode="numeric" data-venue-field="threeSeaterBenches" data-venue-index="${index}" value="${Number(venue.threeSeaterBenches)||0}"></td><td><b>${capacity(venue)}</b></td><td>${venue.source==='manual'?'<button type="button" class="button" data-remove-venue="'+index+'">Remove</button>':'—'}</td></tr>`).join(''):'<tr><td colspan="6">No class venues were found. Add a venue below.</td></tr>';
  const status=summary.missingStrengths?'<b>'+summary.missingStrengths+' section strength(s) still need to be entered.</b>':summary.balance<0?'<b>Seating shortage: '+Math.abs(summary.balance)+' seat(s).</b> Add benches or venues before preparing the final plan.':summary.totalStudents?'<b>Capacity is sufficient.</b> '+summary.balance+' extra seat(s) available.':'<b>Total students will appear after class-section strengths are entered.</b>';
  const kind=summary.missingStrengths?'warn':summary.balance<0?'error':summary.totalStudents?'success':'info';
  const notice=$('seatingStatus');notice.className='notice '+kind;notice.innerHTML=status;
  renderReviewCard(summary);
}

function changed(message){
  const ws=workspace();if(ws?.seating)ws.seating.updatedAtMs=Date.now();
  api()?.markDirty?.(message);render();
}

function bind(){
  injectStyles();
  $('seatingStrengthRows')?.addEventListener('change',event=>{
    const index=Number(event.target.dataset.strengthIndex);if(!Number.isInteger(index))return;
    const seating=model();if(!seating?.sectionStrengths[index])return;
    seating.sectionStrengths[index].strength=Math.max(0,Number(event.target.value)||0);changed('Class-section strength updated');
  });
  $('seatingVenueRows')?.addEventListener('change',event=>{
    const index=Number(event.target.dataset.venueIndex),field=event.target.dataset.venueField;if(!Number.isInteger(index)||!field)return;
    const seating=model(),venue=seating?.venues[index];if(!venue)return;
    venue[field]=field==='active'?event.target.checked:Math.max(0,Number(event.target.value)||0);changed('Seating venue capacity updated');
  });
  $('seatingVenueRows')?.addEventListener('click',event=>{
    const button=event.target.closest('[data-remove-venue]');if(!button)return;
    const seating=model(),index=Number(button.dataset.removeVenue);if(!seating?.venues[index])return;
    seating.venues.splice(index,1);changed('Added venue removed');
  });
  $('addSeatingVenue')?.addEventListener('click',()=>{
    const input=$('newSeatingVenue'),name=input.value.trim();if(!name){input.focus();return}
    const seating=model();if(seating.venues.some(item=>item.name.toLowerCase()===name.toLowerCase())){alert('This venue is already listed.');return}
    seating.venues.push({id:'VENUE_MANUAL_'+Date.now(),name,source:'manual',active:true,twoSeaterBenches:0,threeSeaterBenches:0});input.value='';changed('New seating venue added');
  });
  $('reimportSeatingVenues')?.addEventListener('click',()=>{const ws=workspace();ws.seating=reconcileSeating(ws.seating||{},selectedClasses(ws),importedVenues(ws));changed('Class venues refreshed from Master Timetable')});
  document.addEventListener('vkv-exam-workspace-rendered',render);
  document.addEventListener('vkv-exam-workspace-subjects-applied',()=>setTimeout(render,0));
  document.addEventListener('change',event=>{if(event.target.closest?.('#paperRows,#majorClassGrid,#majorSubjectGrid'))setTimeout(render,40)});
  document.addEventListener('click',event=>{if(event.target.closest?.('[data-pane-target="seatingPlan"]'))setTimeout(render,0)});
  render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
