// Read-only Coordinator Inbox helper: adds a client-side focus for questions resubmitted after correction.
// It reads only the already-rendered revision trail. No Firestore/network access and no workflow state change.
(function(){
  'use strict';

  const $=id=>document.getElementById(id);
  const cards=()=>[...document.querySelectorAll('#list .q')];
  const isResubmitted=card=>/Resubmitted after correction/i.test(String(card.textContent||''));

  function apply(){
    const select=$('qbCoordinatorFocus'),msg=$('qbCoordinatorFocusMsg');
    if(!select||!msg)return;
    const all=cards(),mode=select.value;
    let shown=0,resubmitted=0;
    all.forEach(card=>{
      const revised=isResubmitted(card);if(revised)resubmitted++;
      const visible=mode!=='resubmitted'||revised;
      card.style.display=visible?'':'none';
      if(visible)shown++;
    });
    if(!all.length){msg.textContent='Review focus will update after pending questions are loaded.';return}
    msg.innerHTML=mode==='resubmitted'
      ? `<b>Correction follow-up:</b> showing ${shown} resubmitted question${shown===1?'':'s'} of ${all.length} currently rendered. These have returned to the queue after teacher correction.`
      : `<b>Review focus:</b> ${all.length} pending question${all.length===1?'':'s'} shown · ${resubmitted} resubmitted after correction.`;
  }

  function install(){
    const search=$('search');if(!search)return;
    const host=search.closest('div');if(!host||$('qbCoordinatorFocus'))return;
    const wrap=document.createElement('div');
    wrap.innerHTML=`<label class="small">Review focus</label><select id="qbCoordinatorFocus"><option value="all">All pending questions</option><option value="resubmitted">Resubmitted after correction</option></select><div id="qbCoordinatorFocusMsg" class="small" style="margin-top:6px"></div>`;
    host.insertAdjacentElement('afterend',wrap);
    $('qbCoordinatorFocus').addEventListener('change',apply);
    const list=$('list');
    if(list)new MutationObserver(apply).observe(list,{childList:true,subtree:true});
    ['subjectFilter','sortOrder','search'].forEach(id=>$(id)?.addEventListener(id==='search'?'input':'change',()=>setTimeout(apply,0)));
    apply();
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();
