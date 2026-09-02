/* Preview 2 only: browser-local recovery for unsaved teacher QB editing. No Firestore writes. */
const IDS=['qClass','qSection','qSubject','qChapter','qTopic','qOutcome','qMarks','qDifficulty','qType','qText','qAnswer','qMarking'];
const KEY='vkvtt:qb:preview2:teacher-draft:v1';
const $=id=>document.getElementById(id);
function read(){try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch{return null}}
function capture(){const values={};for(const id of IDS){const el=$(id);if(el)values[id]=el.value}return{values,savedAt:Date.now()}}
function meaningful(d){return !!String(d?.values?.qText||'').trim()}
function persist(){const d=capture();if(meaningful(d))localStorage.setItem(KEY,JSON.stringify(d));else localStorage.removeItem(KEY)}
function clear(){localStorage.removeItem(KEY)}
function restore(d){for(const[id,value]of Object.entries(d?.values||{})){const el=$(id);if(el&&value!=null)el.value=value;el?.dispatchEvent(new Event('change',{bubbles:true}))}}
function stamp(ms){try{return new Date(ms).toLocaleString('en-GB',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}catch{return''}}
function offer(){const d=read(),host=$('editorMsg');if(!meaningful(d)||!host||String($('qText')?.value||'').trim())return;host.innerHTML=`<div class="warning"><b>Unsaved question recovered from this device.</b> Saved ${stamp(d.savedAt)}. <div class="actions" style="justify-content:flex-start;margin-top:8px"><button id="qbRestoreLocal">Restore</button><button id="qbDiscardLocal">Discard</button></div></div>`;$('qbRestoreLocal').onclick=()=>{restore(d);host.innerHTML='<div class="tip">Recovered your unsaved question. Please review it before saving or submitting.</div>'};$('qbDiscardLocal').onclick=()=>{clear();host.innerHTML=''}}
function boot(){const form=$('qText');if(!form)return setTimeout(boot,300);let timer;for(const id of IDS){const el=$(id);if(!el)continue;el.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(persist,350)});el.addEventListener('change',persist)}
for(const id of ['saveDraft','submitQ']){$(id)?.addEventListener('click',()=>setTimeout(()=>{if(!String($('qText')?.value||'').trim())clear()},1200))}
window.addEventListener('beforeunload',persist);offer()}
boot();
