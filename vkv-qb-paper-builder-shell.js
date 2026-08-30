// VKVTT QB Paper Builder — safe local-first foundation
// Phase E1: header + live marks + sections + normal questions. No Firestore writes yet.
(function(){
  const STORAGE='vkvtt.qb.paperDraft.v1';
  const $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const state={title:'',className:'',subject:'',exam:'',duration:'',target:0,sections:[]};
  function load(){try{Object.assign(state,JSON.parse(localStorage.getItem(STORAGE)||'{}'))}catch(_){}}
  function persist(){localStorage.setItem(STORAGE,JSON.stringify(state));const e=$('pbSaved');if(e){e.textContent='Saved just now';setTimeout(()=>e.textContent='Autosaved on this device',1800)}}
  function marks(){return state.sections.reduce((a,s)=>a+s.questions.reduce((x,q)=>x+(Number(q.marks)||0),0),0)}
  function render(){
    const used=marks(),remain=(Number(state.target)||0)-used;
    $('pbUsed').textContent=used;
    $('pbTargetView').textContent=Number(state.target)||0;
    $('pbRemaining').textContent=remain;
    $('pbRemaining').style.fontWeight='800';
    $('pbSections').innerHTML=state.sections.length?state.sections.map((s,si)=>`<div class="qcard"><div class="actions" style="justify-content:space-between"><b>Section ${String.fromCharCode(65+si)}${s.name?' · '+esc(s.name):''}</b><span class="small">${s.questions.reduce((a,q)=>a+(Number(q.marks)||0),0)} marks</span></div>${s.questions.map((q,qi)=>`<div style="display:grid;grid-template-columns:auto 1fr 90px auto;gap:8px;align-items:start;margin-top:9px"><b>${qi+1}.</b><textarea data-q="${si}:${qi}" style="min-height:58px">${esc(q.text)}</textarea><input data-m="${si}:${qi}" type="number" min="0" step="0.5" value="${Number(q.marks)||0}" aria-label="Marks"><button data-del="${si}:${qi}" title="Remove question">×</button></div>`).join('')}<div class="actions" style="margin-top:9px"><button data-addq="${si}">＋ Add Question</button></div></div>`).join(''):'<div class="empty">Add a section to begin building the paper.</div>';
    document.querySelectorAll('[data-addq]').forEach(b=>b.onclick=()=>{state.sections[+b.dataset.addq].questions.push({text:'',marks:1});persist();render()});
    document.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{const[s,q]=b.dataset.del.split(':').map(Number);state.sections[s].questions.splice(q,1);persist();render()});
    document.querySelectorAll('[data-q]').forEach(e=>e.oninput=()=>{const[s,q]=e.dataset.q.split(':').map(Number);state.sections[s].questions[q].text=e.value;persist()});
    document.querySelectorAll('[data-m]').forEach(e=>e.oninput=()=>{const[s,q]=e.dataset.m.split(':').map(Number);state.sections[s].questions[q].marks=Number(e.value)||0;persist();render()});
  }
  function init(){
    const app=$('app'); if(!app||$('paperBuilderTab'))return;
    const tabs=app.querySelector('.tabs'); if(!tabs)return;
    const tab=document.createElement('button');tab.id='paperBuilderTab';tab.dataset.panel='paperBuilder';tab.textContent='📝 Paper Builder';tabs.appendChild(tab);
    const panel=document.createElement('section');panel.id='paperBuilder';panel.className='card panel';panel.innerHTML=`<h2>Question Paper Builder</h2><div class="tip">Build the paper here while the engine keeps a live marks total. This first foundation autosaves only on this device; it does not publish or expose a draft paper.</div><div class="grid3" style="margin-top:10px"><div><label>Class</label><input id="pbClass"></div><div><label>Subject</label><input id="pbSubject"></div><div><label>Examination</label><input id="pbExam" placeholder="e.g. Half-Yearly Examination"></div></div><div class="grid3"><div><label>Target Marks</label><input id="pbTarget" type="number" min="0" step="0.5"></div><div><label>Duration</label><input id="pbDuration" placeholder="e.g. 3 hours"></div><div><label>Paper Title / Note</label><input id="pbTitle"></div></div><div class="metrics" style="margin-top:12px"><div class="metric"><div class="num"><span id="pbUsed">0</span> / <span id="pbTargetView">0</span></div><div class="lab">Marks Used / Target</div></div><div class="metric"><div class="num" id="pbRemaining">0</div><div class="lab">Marks Remaining</div></div><div class="metric"><div class="num" id="pbSectionCount">—</div><div class="lab">Sections</div></div><div class="metric"><div class="small" id="pbSaved">Autosaved on this device</div><div class="lab">Draft Safety</div></div></div><div class="actions" style="margin-top:12px"><button id="pbAddSection">＋ Add Section</button><button id="pbClear">Clear Local Draft</button></div><div id="pbSections" style="margin-top:10px"></div>`;
    tabs.after(panel);
    load();[['pbClass','className'],['pbSubject','subject'],['pbExam','exam'],['pbDuration','duration'],['pbTitle','title']].forEach(([id,k])=>{const e=$(id);e.value=state[k]||'';e.oninput=()=>{state[k]=e.value;persist()}});$('pbTarget').value=state.target||'';$('pbTarget').oninput=()=>{state.target=Number($('pbTarget').value)||0;persist();render()};
    $('pbAddSection').onclick=()=>{state.sections.push({name:'',questions:[{text:'',marks:1}]});persist();render()};$('pbClear').onclick=()=>{if(confirm('Clear this local paper draft?')){localStorage.removeItem(STORAGE);Object.assign(state,{title:'',className:'',subject:'',exam:'',duration:'',target:0,sections:[]});location.reload()}};
    tab.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('active',x===tab));document.querySelectorAll('.panel').forEach(x=>x.classList.toggle('active',x===panel));render()};
    const obs=new MutationObserver(()=>{$('pbSectionCount').textContent=state.sections.length});obs.observe($('pbSections'),{childList:true});render();$('pbSectionCount').textContent=state.sections.length;
  }
  const timer=setInterval(()=>{if($('app')&&$('app').style.display!=='none'){clearInterval(timer);init()}},300);setTimeout(()=>{clearInterval(timer);init()},7000);
})();
