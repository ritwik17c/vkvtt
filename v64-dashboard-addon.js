/*
VKV Nalbari Timetable — Cloud v64.2 Dashboard Add-on
Adds Quick Add Leave only. No duplicate-remover card.

Place this file in the repository root and load it after the existing
admin-dashboard.html module script:

<script src="v64-dashboard-addon.js"></script>
*/
(() => {
  const VERSION='64.2';

  const style=document.createElement('style');
  style.textContent=`
    .tile,button:not(:disabled),.btn,a[href],[role="button"],summary,[onclick]{cursor:pointer!important}
    button:disabled{cursor:not-allowed!important}
    .v64QuickLeaveFrame{width:100%;min-height:900px;border:1px solid #cbdce5;border-radius:16px;background:#f7fbf9}
    @media(max-width:700px){.v64QuickLeaveFrame{min-height:1180px}}
  `;
  document.head.appendChild(style);

  function install(){
    const tiles=document.querySelector('#dashboardHome .tiles');
    if(!tiles||document.getElementById('v64QuickLeaveTile'))return;

    // Remove old experimental v63 cards if they are present.
    document.getElementById('v63DuplicateTile')?.remove();
    document.getElementById('v63QuickLeaveTile')?.remove();

    const quick=document.createElement('div');
    quick.className='tile';
    quick.id='v64QuickLeaveTile';
    quick.style.cssText='background:#eef8ff;border-color:#a9cfe2';
    quick.innerHTML='<b>➕ Quick Add Leave</b><span>Add an individual Date Row or Date-Range Row directly from the Admin Dashboard.</span>';

    const leaveEditor=document.getElementById('openLeaveEditor');
    if(leaveEditor)leaveEditor.insertAdjacentElement('afterend',quick);
    else tiles.appendChild(quick);

    const panel=document.createElement('section');
    panel.id='v64QuickLeavePanel';
    panel.className='card panel';
    panel.innerHTML=`
      <div class="sectionTop">
        <div>
          <div class="breadcrumb">Admin Dashboard → Quick Add Leave</div>
          <h2>➕ Quick Add Leave</h2>
        </div>
        <button type="button" data-v64-back>← Admin Dashboard</button>
      </div>
      <div class="help">This is the same Leave Editor and the same Firestore leave data. Each click adds one Date Row or one Date-Range Row, and all leave units are totalled together.</div>
      <iframe class="v64QuickLeaveFrame" title="Quick Add Leave" src="admin-leave-editor.html?v=${VERSION}&quick=1"></iframe>
    `;
    document.getElementById('app')?.appendChild(panel);

    function showQuick(){
      document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
      const home=document.getElementById('dashboardHome');
      if(home)home.style.display='none';
      panel.classList.add('active');
      panel.scrollIntoView({behavior:'smooth',block:'start'});
    }

    function back(){
      panel.classList.remove('active');
      const home=document.getElementById('dashboardHome');
      if(home)home.style.display='block';
      window.scrollTo({top:0,behavior:'smooth'});
    }

    quick.onclick=showQuick;
    panel.querySelector('[data-v64-back]')?.addEventListener('click',back);

    const sub=document.querySelector('header .subtitle');
    if(sub)sub.textContent=sub.textContent.replace(/Cloud v\d+(?:\.\d+)?/,'Cloud v64.2');
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);
  else install();
})();