// VKVTT · read-only leave history context
// Additive UI only. No leave/status writes are performed here.
import{initializeApp,getApps,getApp}from'https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js';
import{getAuth,setPersistence,browserLocalPersistence}from'https://www.gstatic.com/firebasejs/12.17.1/firebase-auth.js';
import{getFirestore,doc,getDoc,collection,getDocs}from'https://www.gstatic.com/firebasejs/12.17.1/firebase-firestore-lite.js';

const cfg={apiKey:'AIzaSyDheZpyXghd1aQ9_RLhwpacVriG__wNZW4',authDomain:'vkv-nalbari-timetable.firebaseapp.com',projectId:'vkv-nalbari-timetable',storageBucket:'vkv-nalbari-timetable.firebasestorage.app',messagingSenderId:'791432856951',appId:'1:791432856951:web:61324065a54bef30f98d72'};
const app=getApps().length?getApp():initializeApp(cfg),auth=getAuth(app),db=getFirestore(app);
await setPersistence(auth,browserLocalPersistence).catch(()=>{});if(auth.authStateReady)await auth.authStateReady().catch(()=>{});
const safe=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=s=>{const m=String(s||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);return m?`${m[3]}/${m[2]}/${m[1]}`:String(s||'—')};
let approved=[],requests=[],loadError='';

function datesOf(p){
 if(Array.isArray(p?.dates)&&p.dates.length)return[...new Set(p.dates.filter(Boolean))].sort();
 const a=p?.startDate||p?.date||'',b=p?.endDate||a;if(!a)return[];
 if(!b||a===b)return[a];
 const out=[],d=new Date(a+'T00:00:00'),z=new Date(b+'T00:00:00');
 for(let i=0;d<=z&&i<370;i++,d.setDate(d.getDate()+1))out.push(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'));
 return out;
}
function label(p){
 const t=String(p?.type||p?.statusType||'').toLowerCase();
 if(t==='od')return'On Duty (OD)';if(t==='special')return'Special Assignment';
 const c=String(p?.leaveCategory||p?.category||'').trim();return c?(c.toUpperCase()==='MATERNITY'?'Maternity Leave':c):'Regular Leave';
}
function coverage(p){
 const t=String(p?.type||'').toLowerCase();if(t==='full')return'Full day';
 if(t==='half')return p.from&&p.to?`P${p.from}–P${p.to}`:'Half day';
 if(p?.duration==='half')return p.from&&p.to?`P${p.from}–P${p.to}`:'Half day';
 if(p?.from&&p?.to)return`P${p.from}–P${p.to}`;return'Full day';
}
function historyFor(code){return approved.filter(p=>p&&p.active!==false&&String(p.code||p.teacherCode||'')===String(code||'')).sort((a,b)=>String(datesOf(b).at(-1)||'').localeCompare(String(datesOf(a).at(-1)||'')))}
function pendingFor(code){return requests.filter(r=>r&&String(r.code||r.teacherCode||'')===String(code||'')&&['provisional','returned'].includes(String(r.approvalStatus||'provisional').toLowerCase())).sort((a,b)=>Number(b.createdAtMs||0)-Number(a.createdAtMs||0))}
function categorySummary(rows){
 const map=new Map();
 for(const p of rows){const t=String(p?.type||p?.statusType||'').toLowerCase();if(t==='od'||t==='special')continue;const k=String(p?.leaveCategory||p?.category||'Regular Leave').trim()||'Regular Leave',u=Number(p?.leaveUnits);map.set(k,(map.get(k)||0)+(Number.isFinite(u)&&u>0?u:datesOf(p).length||1))}
 return [...map.entries()].sort((a,b)=>a[0].localeCompare(b[0]));
}
function pendingSummary(rows){
 return rows.map(r=>{const es=Array.isArray(r.entries)?r.entries:[],parts=es.map(e=>`${label(e)}${Number(e.leaveUnits)>0?` · ${Number(e.leaveUnits)} unit${Number(e.leaveUnits)===1?'':'s'}`:''}`);return `<div class="vkh-pending-row"><b>${safe(parts.join(' + ')||'Pending Leave / Duty')}</b><span>${safe(String(r.approvalStatus||'provisional').toUpperCase())}</span></div>`}).join('');
}
function historyHtml(code,compact=false){
 if(!code)return'<div class="vkh-empty">Select a staff member first. Their approved and pending leave context will appear here before you choose the new leave category.</div>';
 if(loadError)return`<div class="vkh-warn">Approved leave history could not be loaded for this account. ${safe(loadError)}</div>`;
 const rows=historyFor(code),pending=pendingFor(code),shown=rows.slice(0,compact?6:12),summary=categorySummary(rows);
 let html='';
 if(summary.length)html+=`<div class="vkh-usage"><div class="vkh-usage-title">Category-wise approved usage</div><div class="vkh-chips">${summary.map(([k,v])=>`<span class="vkh-chip"><b>${safe(k)}</b> ${safe(v)}</span>`).join('')}</div></div>`;
 else html+='<div class="vkh-empty">No approved Regular Leave usage found for this staff member yet.</div>';
 if(pending.length)html+=`<div class="vkh-pending"><div class="vkh-pending-title">⚠ Pending / returned request${pending.length===1?'':'s'} already exist</div>${pendingSummary(pending.slice(0,4))}<div class="vkh-help">Check these before creating another request to avoid duplication or selecting the wrong category.</div></div>`;
 if(!rows.length)return html+'<div class="vkh-empty">No approved Leave / OD / Special Assignment history found for this staff member.</div>';
 html+=`<div class="vkh-summary"><b>${rows.length}</b> approved record${rows.length===1?'':'s'} found${rows.length>shown.length?` · showing latest ${shown.length}`:''}</div><div class="vkh-list">${shown.map(p=>{const ds=datesOf(p),dateText=ds.length>1?`${fmt(ds[0])} → ${fmt(ds.at(-1))} · ${ds.length} day${ds.length===1?'':'s'}`:fmt(ds[0]);const units=Number(p.leaveUnits)>0?` · ${Number(p.leaveUnits)} unit${Number(p.leaveUnits)===1?'':'s'}`:'';return`<div class="vkh-row"><div><b>${safe(label(p))}</b><span>${safe(dateText)}</span></div><small>${safe(coverage(p))}${safe(units)}${p.note||p.remarks?` · ${safe(p.note||p.remarks)}`:''}</small></div>`}).join('')}</div>`;
 return html;
}
function ensureStyle(){if(document.getElementById('vkh-style'))return;const s=document.createElement('style');s.id='vkh-style';s.textContent=`.vkh-panel{border:1px solid #bcd5df;border-radius:14px;background:#f7fbfd;padding:13px;margin:12px 0}.vkh-title{font-weight:850;color:#17364f;margin-bottom:3px}.vkh-help,.vkh-empty{font-size:.83rem;color:#617685;line-height:1.45}.vkh-summary{font-size:.82rem;color:#476575;margin:8px 0}.vkh-list{display:grid;gap:7px}.vkh-row{border:1px solid #dce8ed;border-radius:10px;background:#fff;padding:9px 10px}.vkh-row>div{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}.vkh-row b{color:#17364f;font-size:.87rem}.vkh-row span,.vkh-row small{color:#617685;font-size:.8rem}.vkh-row small{display:block;margin-top:3px}.vkh-warn{font-size:.82rem;color:#76570f;background:#fff7df;border:1px solid #e4c873;border-radius:9px;padding:9px}.vkh-usage{margin:9px 0 10px}.vkh-usage-title{font-size:.78rem;font-weight:800;color:#476575;margin-bottom:6px}.vkh-chips{display:flex;gap:6px;flex-wrap:wrap}.vkh-chip{padding:5px 8px;border-radius:999px;background:#e9f3f7;border:1px solid #c9dfe9;color:#294f68;font-size:.78rem}.vkh-pending{margin:10px 0;padding:10px;border:1px solid #e4c873;background:#fff7df;border-radius:10px}.vkh-pending-title{font-weight:850;color:#76570f;font-size:.84rem;margin-bottom:6px}.vkh-pending-row{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:5px 0;border-bottom:1px dashed #dfc879;font-size:.8rem}.vkh-pending-row:last-of-type{border-bottom:0}.vkh-pending-row span{font-weight:800;color:#76570f}`;document.head.appendChild(s)}
function mountQuick(){
 const sel=document.getElementById('teacher')||document.getElementById('editTeacher'),form=document.getElementById('formCard')||document.getElementById('editorPanel');if(!sel||!form)return;
 let p=document.getElementById('vkh-quick');if(!p){p=document.createElement('div');p.id='vkh-quick';p.className='vkh-panel';p.innerHTML='<div class="vkh-title">📚 Leave History & Category Check</div><div class="vkh-help"><b>Review this before choosing a new leave category.</b> It shows approved category-wise usage, recent Leave / OD / Special Assignment records, and pending requests for the selected staff member.</div><div id="vkh-quick-body"></div>';const firstGrid=form.querySelector('.grid2');firstGrid?.insertAdjacentElement('afterend',p)}
 const render=()=>{const b=document.getElementById('vkh-quick-body');if(b)b.innerHTML=historyHtml(sel.value,false)};sel.addEventListener('change',render);window.vkvRenderLeaveHistory=render;
 document.addEventListener('click',event=>{if(event.target.closest?.('[data-edit-key],[data-resolve],[data-final],#newBtn'))setTimeout(render,60)});render();
}
function requestCode(id){const r=requests.find(x=>String(x.id)===String(id));return String(r?.code||r?.teacherCode||'')}
function mountApprovalCards(){
 document.querySelectorAll('#queue .req').forEach(card=>{if(card.querySelector('.vkh-approval'))return;const btn=card.querySelector('[data-a],[data-r]'),id=btn?.dataset?.a||btn?.dataset?.r;if(!id)return;const code=requestCode(id);const p=document.createElement('div');p.className='vkh-panel vkh-approval';p.innerHTML=`<div class="vkh-title">📚 Leave History Before Decision</div><div class="vkh-help">Read-only context for this staff member. The current provisional request is excluded from the approved usage below.</div>${historyHtml(code,true)}`;const ta=card.querySelector('textarea');if(ta)card.insertBefore(p,ta);else card.appendChild(p)})
}
async function loadData(){
 const merged=new Map(),results=await Promise.allSettled([getDocs(collection(db,'approvedStatusPlans')),getDoc(doc(db,'dailyRecords','__leavePlans')),getDocs(collection(db,'provisionalLeavePlans'))]);
 if(results[0].status==='fulfilled')results[0].value.forEach(d=>merged.set(d.id,{id:d.id,...(d.data()||{})}));
 if(results[1].status==='fulfilled'&&results[1].value.exists())for(const [id,p] of Object.entries(results[1].value.data().plans||{}))if(p&&p.active!==false&&!merged.has(id))merged.set(id,{id,...p});
 approved=[...merged.values()];
 if(results[2].status==='fulfilled'){requests=[];results[2].value.forEach(d=>requests.push({id:d.id,...(d.data()||{})}))}
 if(!approved.length&&results[0].status==='rejected')loadError=String(results[0].reason?.code==='permission-denied'?'Approved-history read permission is not enabled for this role.':(results[0].reason?.message||results[0].reason));
}
ensureStyle();await loadData();mountQuick();mountApprovalCards();
const q=document.getElementById('queue');if(q)new MutationObserver(()=>mountApprovalCards()).observe(q,{childList:true,subtree:true});
import('./vkv-leave-official-conflict-cleanup.js?v=20260908-conflict-clean-1').catch(console.warn);
