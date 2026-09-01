// VKVTT QB Paper Builder — local Paper Health advisory
// Safe progressive enhancement: reads only local builder/subquestion state; no Firestore access or writes.
(function(){
  const $=id=>document.getElementById(id),SUBMARKS='vkvtt.qb.paperSubquestionMarks.v1';
  function getState(){try{return window.__vkvQbPaperBuilder?.getState?.()||null}catch(_){return null}}
  function getSubmarks(){try{return JSON.parse(localStorage.getItem(SUBMARKS)||'{}')||{}}catch(_){return {}}}
  function partCount(text){return String(text||'').split('\n').filter(x=>/^\s*\([a-z]\)\s+/i.test(x)).length}
  function analyse(s){
    if(!s)return null;
    const sections=Array.isArray(s.sections)?s.sections:[],submarks=getSubmarks();
    const questions=sections.flatMap((sec,si)=>(sec.questions||[]).map((q,qi)=>({q,si,qi})));
    const used=questions.reduce((a,x)=>a+(Number(x.q.marks)||0),0),target=Number(s.target)||0;
    const blank=questions.filter(x=>!String(x.q.text||'').trim()).length,zero=questions.filter(x=>(Number(x.q.marks)||0)<=0).length;
    const untitled=sections.filter(sec=>!String(sec.name||'').trim()).length;
    const verified=questions.filter(x=>String(x.q.source||'')==='verified_bank'||String(x.q.sourceQuestionId||'').trim()).length;
    const choice=questions.filter(x=>String(x.q.choice||'').trim()).length;
    const sectionMismatch=sections.filter(sec=>{const t=Number(sec.targetMarks)||0;if(!t)return false;const u=(sec.questions||[]).reduce((a,q)=>a+(Number(q.marks)||0),0);return Math.abs(t-u)>0.001}).length;
    const partStatus=questions.map(x=>{const n=partCount(x.q.text);if(!n)return null;const vals=Array.isArray(submarks['q:'+x.si+':'+x.qi])?submarks['q:'+x.si+':'+x.qi]:[],entered=vals.slice(0,n).filter(v=>v!==''&&v!==null&&v!==undefined);if(entered.length<n)return{kind:'incomplete'};const sum=entered.reduce((a,v)=>a+(Number(v)||0),0);return Math.abs(sum-(Number(x.q.marks)||0))>0.001?{kind:'mismatch'}:{kind:'ok'}}).filter(Boolean);
    const incompleteParts=partStatus.filter(x=>x.kind==='incomplete').length,mismatchedParts=partStatus.filter(x=>x.kind==='mismatch').length;
    const missingMeta=[['Class',s.className],['Subject',s.subject],['Examination',s.exam],['Duration',s.duration]].filter(x=>!String(x[1]||'').trim()).map(x=>x[0]);
    const issues=[];
    if(!sections.length)issues.push('No section has been added yet.');
    if(blank)issues.push(blank+' blank question '+(blank===1?'row remains':'rows remain')+'.');
    if(zero)issues.push(zero+' question '+(zero===1?'has':'have')+' zero marks.');
    if(incompleteParts)issues.push(incompleteParts+' question '+(incompleteParts===1?'has':'have')+' incomplete subquestion marks.');
    if(mismatchedParts)issues.push(mismatchedParts+' question '+(mismatchedParts===1?'has':'have')+' subquestion marks that do not match the parent question total.');
    if(target&&Math.abs(target-used)>0.001)issues.push('Paper total is '+used+' marks against the '+target+'-mark target.');
    if(sectionMismatch)issues.push(sectionMismatch+' section '+(sectionMismatch===1?'does':'do')+' not match its section target.');
    if(missingMeta.length)issues.push('Missing paper details: '+missingMeta.join(', ')+'.');
    const notes=[];
    if(untitled)notes.push(untitled+' untitled section'+(untitled===1?'':'s'));
    if(verified)notes.push(verified+' verified-bank question'+(verified===1?'':'s'));
    if(choice)notes.push(choice+' internal choice'+(choice===1?'':'s'));
    if(partStatus.length&&!incompleteParts&&!mismatchedParts)notes.push(partStatus.length+' subquestion mark set'+(partStatus.length===1?'':'s')+' reconciled');
    let level='good',title='Ready for review';
    if(issues.length){level=blank||zero||!sections.length||incompleteParts||mismatchedParts?'warn':'check';title=level==='warn'?'Needs attention':'Check before finalising'}
    return{issues,notes,level,title,questions:questions.length,used,target};
  }
  function ensureBox(){const panel=$('paperBuilder');if(!panel)return null;let box=$('pbHealth');if(box)return box;box=document.createElement('div');box.id='pbHealth';box.className='tip';box.style.marginTop='10px';box.setAttribute('aria-live','polite');const anchor=$('pbBalance');if(anchor)anchor.insertAdjacentElement('afterend',box);else panel.prepend(box);return box}
  function render(){const box=ensureBox(),a=analyse(getState());if(!box||!a)return;const icon=a.level==='good'?'✓':a.level==='warn'?'⚠':'◌',summary=`${a.questions} question${a.questions===1?'':'s'} · ${a.used} marks${a.target?' / '+a.target:''}`;const issueHtml=a.issues.length?'<ul style="margin:7px 0 0 18px;padding:0">'+a.issues.map(x=>'<li>'+x+'</li>').join('')+'</ul>':'<div style="margin-top:5px">No structural issue detected in the current local draft.</div>';const noteHtml=a.notes.length?'<div class="small" style="margin-top:7px">Context: '+a.notes.join(' · ')+'</div>':'';box.innerHTML=`<b>${icon} Paper Health — ${a.title}</b><div class="small" style="margin-top:3px">${summary}. Advisory only; nothing is changed automatically.</div>${issueHtml}${noteHtml}`}
  window.addEventListener('vkv-qb-paper-ready',render);window.addEventListener('vkv-qb-paper-rendered',render);document.addEventListener('input',e=>{if(e.target?.matches?.('[data-pm]'))setTimeout(render,0)});
  const timer=setInterval(()=>{if(window.__vkvQbPaperBuilder){clearInterval(timer);render()}},350);setTimeout(()=>{clearInterval(timer);render()},8000);
})();
