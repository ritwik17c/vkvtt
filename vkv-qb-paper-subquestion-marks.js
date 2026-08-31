// VKVTT QB Paper Builder — safe subquestion marks drafting helper
// Progressive enhancement only. Stores optional part marks in localStorage; no Firestore/schema changes.
(function(){
  const STORAGE='vkvtt.qb.paperSubquestionMarks.v1';
  let data={};
  try{data=JSON.parse(localStorage.getItem(STORAGE)||'{}')||{}}catch(_){data={}}
  const save=()=>localStorage.setItem(STORAGE,JSON.stringify(data));
  const key=t=>'q:'+String(t.dataset.q||'');
  function parts(t){return String(t.value||'').split('\n').filter(x=>/^\s*\([a-z]\)\s+/i.test(x))}
  function enhance(){
    const panel=document.getElementById('paperBuilder');if(!panel)return;
    panel.querySelectorAll('textarea[data-q]').forEach(t=>{
      const box=t.nextElementSibling;if(!box||!box.querySelector?.('[data-subq-status]'))return;
      let host=box.querySelector('[data-subq-marks]');
      if(!host){host=document.createElement('span');host.dataset.subqMarks='1';host.className='small';box.appendChild(host)}
      const refresh=()=>{
        const ps=parts(t),k=key(t),vals=Array.isArray(data[k])?data[k]:[];
        if(!ps.length){host.innerHTML='';return}
        host.innerHTML=' · Part marks: '+ps.map((_,i)=>`<label style="display:inline-flex;align-items:center;gap:2px;margin:0 3px">(${String.fromCharCode(97+i)}) <input data-pm="${i}" type="number" min="0" step="0.5" value="${Number(vals[i])||''}" style="width:58px;padding:4px 6px"></label>`).join('')+' <b data-pmt></b>';
        const total=()=>{const xs=[...host.querySelectorAll('[data-pm]')].map(e=>Number(e.value)||0);host.querySelector('[data-pmt]').textContent=xs.some(Boolean)?`= ${xs.reduce((a,b)=>a+b,0)} marks`:'';data[k]=xs;save()};
        host.querySelectorAll('[data-pm]').forEach(e=>e.oninput=total);total();
      };
      if(t.dataset.subqMarksEnhanced!=='1'){t.dataset.subqMarksEnhanced='1';t.addEventListener('input',refresh)}
      refresh();
    });
  }
  window.addEventListener('vkv-qb-paper-rendered',enhance);
  window.addEventListener('vkv-qb-paper-ready',enhance);
  const timer=setInterval(enhance,600);setTimeout(()=>clearInterval(timer),10000);
})();
