// Read-only UI enhancement for the Subject Coordinator review queue.
(function(){
  let selected='all';
  function enhance(){
    const panel=document.getElementById('review');
    const list=document.getElementById('reviewList');
    if(!panel||!list)return;
    if(!document.getElementById('qbReviewTools')){
      const box=document.createElement('div');
      box.id='qbReviewTools'; box.className='tip'; box.style.margin='10px 0';
      box.innerHTML='<b>Coordinator Inbox</b><div class="small" style="margin-top:4px">Check correctness, wording, marks, difficulty, learning outcome and answer or marking scheme before accepting.</div><div class="actions" style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;align-items:center"><button type="button" data-rf="all" class="primary">All Pending</button><button type="button" data-rf="today">Submitted Today</button><input id="qbReviewSearch" placeholder="Search question, class, subject or teacher" style="max-width:390px"><span id="qbReviewCount" class="badge"></span></div>';
      panel.querySelector('h2')?.insertAdjacentElement('afterend',box);
      box.querySelector('#qbReviewSearch')?.addEventListener('input',filter);
      box.addEventListener('click',e=>{const b=e.target.closest('[data-rf]');if(!b)return;selected=b.dataset.rf;box.querySelectorAll('[data-rf]').forEach(x=>x.classList.toggle('primary',x===b));filter()});
    }
    list.querySelectorAll('.qcard').forEach(card=>{
      card.querySelectorAll('.badge').forEach(b=>{if((b.textContent||'').trim()==='submitted')b.textContent='Unverified · Awaiting Verification'});
      const actions=card.querySelector('.actions');
      if(actions&&!actions.querySelector('.qbChecklist')){
        const note=document.createElement('span'); note.className='small qbChecklist'; note.textContent='Accept only after academic verification.'; actions.appendChild(note);
      }
    });
    filter();
  }
  function isToday(card){
    const t=(card.textContent||'').toLowerCase();
    const d=new Date(),dd=String(d.getDate()).padStart(2,'0'),mm=String(d.getMonth()+1).padStart(2,'0'),yyyy=d.getFullYear();
    return t.includes(dd+'/'+mm+'/'+yyyy)||t.includes(yyyy+'-'+mm+'-'+dd)||t.includes('today');
  }
  function filter(){
    const list=document.getElementById('reviewList'); if(!list)return;
    const term=(document.getElementById('qbReviewSearch')?.value||'').trim().toLowerCase(); let shown=0,total=0;
    list.querySelectorAll('.qcard').forEach(card=>{total++;const textOk=!term||(card.textContent||'').toLowerCase().includes(term),dateOk=selected==='all'||isToday(card),ok=textOk&&dateOk;card.style.display=ok?'':'none';if(ok)shown++});
    const count=document.getElementById('qbReviewCount'); if(count)count.textContent=shown+' of '+total+' pending';
  }
  function start(){const list=document.getElementById('reviewList'); if(list)new MutationObserver(enhance).observe(list,{childList:true,subtree:true}); enhance()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();