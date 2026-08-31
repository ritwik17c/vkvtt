// VKVTT QB Paper Builder — local manual checkpoint / restore
// Progressive enhancement only. No Firestore access or writes.
(function(){
  const DRAFT='vkvtt.qb.paperDraft.v1';
  const CHECKPOINT='vkvtt.qb.paperCheckpoint.v1';
  const $=id=>document.getElementById(id);
  const fmt=ms=>{try{return new Date(ms).toLocaleString('en-IN',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}catch(_){return''}};
  function readCheckpoint(){try{return JSON.parse(localStorage.getItem(CHECKPOINT)||'null')}catch(_){return null}}
  function validDraft(v){return v&&typeof v==='object'&&Array.isArray(v.sections)}
  function ensure(){
    const panel=$('paperBuilder');if(!panel||$('pbCheckpointBox'))return;
    const actions=$('pbClear')?.parentElement;if(!actions)return;
    const save=document.createElement('button');save.id='pbCheckpointSave';save.textContent='💾 Save Checkpoint';save.title='Keep a manual safety copy of this local paper draft';
    const restore=document.createElement('button');restore.id='pbCheckpointRestore';restore.textContent='↶ Restore Checkpoint';restore.title='Restore the last manual checkpoint';
    actions.insertBefore(save,$('pbClear'));actions.insertBefore(restore,$('pbClear'));
    const box=document.createElement('div');box.id='pbCheckpointBox';box.className='small';box.style.marginTop='7px';actions.insertAdjacentElement('afterend',box);
    function refresh(){const cp=readCheckpoint();restore.disabled=!validDraft(cp?.state);box.textContent=validDraft(cp?.state)?'Manual checkpoint saved '+fmt(cp.savedAt)+'. Autosave continues separately.':'No manual checkpoint saved yet.'}
    save.onclick=()=>{let state=null;try{state=window.__vkvQbPaperBuilder?.getState?.()}catch(_){}if(!validDraft(state)){box.textContent='Paper Builder state is not ready yet.';return}try{localStorage.setItem(CHECKPOINT,JSON.stringify({savedAt:Date.now(),state}));refresh();box.textContent='✓ Manual checkpoint saved '+fmt(Date.now())+'. Autosave remains active.'}catch(e){box.textContent='Could not save checkpoint on this device.'}};
    restore.onclick=()=>{const cp=readCheckpoint();if(!validDraft(cp?.state))return;if(!confirm('Restore the last manual checkpoint? Your current autosaved local draft will be replaced.'))return;try{localStorage.setItem(DRAFT,JSON.stringify(cp.state));location.reload()}catch(e){box.textContent='Could not restore checkpoint on this device.'}};
    refresh();
  }
  window.addEventListener('vkv-qb-paper-ready',ensure);
  const timer=setInterval(()=>{if(window.__vkvQbPaperBuilder&&$('paperBuilder')){clearInterval(timer);ensure()}},350);
  setTimeout(()=>{clearInterval(timer);ensure()},8000);
})();
