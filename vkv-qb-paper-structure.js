// VKVTT QB Paper Builder — Phase E4 local-only structure checks
// Surgical enhancement: no Firestore reads/writes; works only with the existing local draft UI.
(function(){
 const $=id=>document.getElementById(id), num=v=>Number(v)||0;
 function analyse(){
  const panel=$('paperBuilder'), host=$('pbStructure'); if(!panel||!host)return;
  const target=num($('pbTarget')?.value), sections=[...panel.querySelectorAll('#pbSections > .qcard')];
  let questions=0, blank=0, zero=0, choices=0, used=0; const sectionTotals=[];
  sections.forEach((s,si)=>{let st=0;const texts=[...s.querySelectorAll('[data-q]')],marks=[...s.querySelectorAll('[data-m]')],ors=[...s.querySelectorAll('[data-c]')];questions+=texts.length;texts.forEach(x=>{if(!x.value.trim())blank++});marks.forEach(x=>{const m=num(x.value);st+=m;used+=m;if(m<=0)zero++});ors.forEach(x=>{if(x.value.trim())choices++});sectionTotals.push({name:String.fromCharCode(65+si),marks:st})});
  const remain=target-used, issues=[];
  if(target&&remain!==0)issues.push(remain>0?`${remain} mark(s) still need to be allocated.`:`Paper is ${Math.abs(remain)} mark(s) over target.`);
  if(blank)issues.push(`${blank} blank question slot(s) remain.`); if(zero)issues.push(`${zero} question(s) have zero marks.`);
  const emptySections=sectionTotals.filter(x=>x.marks===0).map(x=>x.name);if(emptySections.length)issues.push(`Section ${emptySections.join(', ')} currently has no marks.`);
  host.innerHTML=`<div class="grid3"><div class="metric"><div class="num">${questions}</div><div class="lab">Questions</div></div><div class="metric"><div class="num">${choices}</div><div class="lab">Internal Choices</div></div><div class="metric"><div class="num">${blank+zero}</div><div class="lab">Items to Check</div></div></div><div class="${issues.length?'warning':'tip'}" style="margin-top:9px"><b>${issues.length?'Paper check':'✓ Basic structure check passed'}</b>${issues.length?'<br>'+issues.map(x=>'• '+x).join('<br>'):'<br>Target marks, blank slots and zero-mark questions are clear.'}</div>`;
 }
 function init(){const panel=$('paperBuilder');if(!panel||$('pbStructure'))return false;const balance=$('pbBalance');if(!balance)return false;const box=document.createElement('div');box.id='pbStructure';box.style.marginTop='10px';balance.insertAdjacentElement('afterend',box);panel.addEventListener('input',()=>setTimeout(analyse,0));panel.addEventListener('click',()=>setTimeout(analyse,0));analyse();return true}
 let n=0,t=setInterval(()=>{if(init()||++n>40)clearInterval(t)},300);window.addEventListener('load',()=>setTimeout(init,700));
})();