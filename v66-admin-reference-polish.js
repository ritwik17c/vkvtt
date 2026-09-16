/* v66.4 admin dashboard reference + unified Leave Management entry · safe one-shot */
(function(){
  'use strict';
  function consolidate(){
    const primary=document.getElementById('openLeaveManager');
    if(!primary)return false;
    const b=primary.querySelector('b'),s=primary.querySelector('span');
    if(b)b.textContent='🗂 Leave Management';
    if(s)s.textContent='One complete leave workspace: review history, prepare entries, approve, search, edit/delete approved records, rules, import, reconciliation and audit.';
    primary.style.display='';
    primary.onclick=()=>location.href='./leave-manager.html?v=20260916-unified-leave-2';
    ['openLeaveMasterEditor','openLeaveApprovals','openLeaveRules','openSuperLeaveFilter','openLeaveRegister','openLeaveImport'].forEach(id=>{
      const x=document.getElementById(id);if(x)x.style.display='none';
    });
    return true;
  }
  function run(){
    if(consolidate())return;
    setTimeout(()=>{if(consolidate())return;setTimeout(consolidate,900)},350);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
