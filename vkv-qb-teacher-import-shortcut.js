/* Preview 2: make teacher Excel/Word bulk import explicit and easy to find. */
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function openImport(){
  const tab=document.querySelector('.tabs button[data-panel="io"]');
  if(tab)tab.click();
  for(let i=0;i<20;i++){
    const target=document.getElementById('qbTeacherBulkImport')||document.getElementById('io');
    if(target){target.scrollIntoView({behavior:'smooth',block:'start'});return}
    await wait(100);
  }
}
function mount(){
  if(document.getElementById('qbTeacherImportShortcut'))return;
  const app=document.getElementById('app');
  if(!app)return;
  const hero=app.querySelector('.hero');
  if(!hero)return;
  const row=document.createElement('div');
  row.className='actions';
  row.style.marginTop='12px';
  const button=document.createElement('button');
  button.id='qbTeacherImportShortcut';
  button.type='button';
  button.className='primary';
  button.textContent='📥 Import Questions from Excel / Word';
  button.title='Bulk import questions from the VKVTT Excel template or a supported Word (.docx) question bank';
  button.onclick=openImport;
  row.appendChild(button);
  hero.appendChild(row);
  const tab=document.querySelector('.tabs button[data-panel="io"]');
  if(tab)tab.textContent='📥 Import Excel / Word';
}
const observer=new MutationObserver(()=>mount());
observer.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['style']});
mount();
setTimeout(mount,500);
setTimeout(mount,1500);
