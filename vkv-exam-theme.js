(()=>{
  const STORAGE_KEY='vkvtt-exam-theme';
  const root=document.documentElement;
  const button=document.getElementById('examThemeToggle');

  function disableLegacyTheme(){
    document.querySelectorAll('link[data-vkv-black-gold-theme],link[href*="vkv-black-gold-screen.css"]').forEach(link=>{link.disabled=true;link.remove()});
  }

  function installContrastFix(){
    if(document.getElementById('vkvExamContrastFix')) return;
    const style=document.createElement('style');
    style.id='vkvExamContrastFix';
    style.textContent=`
      .topbar .brand h1{color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,.22)}
      .topbar .brand p{color:rgba(255,255,255,.94)!important;opacity:1!important}
      .topbar .saveState{color:#fff!important;border-color:rgba(255,255,255,.48)!important;background:rgba(10,35,52,.28)!important}
      .topbar .button.pale{color:#123d58!important;background:#f7fbfd!important;border-color:#d5e5ec!important}
      .workspaceBadge small,.paneHead p,.sectionTitle p,.tableHint,.metric span,.reviewCard span,.draftCard p,.empty,.majorCard small{color:#475f6e!important}
      label,legend{color:#405b6b!important}
      .navButton:not(.active){color:#294b5f!important}
      .sideNote{color:#355f49!important}
      input::placeholder,textarea::placeholder{color:#617786!important;opacity:1!important}
      .button:disabled{opacity:.72!important;color:#526777!important}
      .summaryCard.master p{color:#eef8fc!important}
      .summaryCard.master .eyebrow{color:#d4f1fb!important}
      html[data-theme="dark"] .topbar .brand p{color:rgba(255,255,255,.94)!important}
      html[data-theme="dark"] .workspaceBadge small,
      html[data-theme="dark"] .paneHead p,
      html[data-theme="dark"] .sectionTitle p,
      html[data-theme="dark"] .tableHint,
      html[data-theme="dark"] .metric span,
      html[data-theme="dark"] .reviewCard span,
      html[data-theme="dark"] .draftCard p,
      html[data-theme="dark"] .empty,
      html[data-theme="dark"] .majorCard small,
      html[data-theme="dark"] label,
      html[data-theme="dark"] legend{color:#c7d8e2!important}
      html[data-theme="dark"] .navButton:not(.active){color:#d0e0e7!important}
      html[data-theme="dark"] input::placeholder,
      html[data-theme="dark"] textarea::placeholder{color:#a9bec9!important;opacity:1!important}
      html[data-theme="dark"] .button:disabled{opacity:.76!important;color:#b9cad3!important}
      html[data-theme="dark"] .sideNote{color:#c0ddca!important}
    `;
    document.head.appendChild(style);
  }

  function apply(theme,persist=false){
    const next=theme==='dark'?'dark':'light';
    disableLegacyTheme();
    installContrastFix();
    root.dataset.theme=next;
    if(button){
      button.textContent=next==='dark'?'Light theme':'Dark theme';
      button.setAttribute('aria-pressed',String(next==='dark'));
      button.title=next==='dark'?'Switch to light theme':'Switch to dark theme';
    }
    if(persist){try{localStorage.setItem(STORAGE_KEY,next)}catch(error){}}
  }

  installContrastFix();
  apply(root.dataset.theme);
  if(button) button.addEventListener('click',()=>apply(root.dataset.theme==='dark'?'light':'dark',true));
  new MutationObserver(disableLegacyTheme).observe(document.head,{childList:true});

  function openAdmitCards(event){
    if(event)event.preventDefault();
    if(typeof window.vkvOpenAdmitCards==='function')return window.vkvOpenAdmitCards();
    location.href='exam-admit-cards-v2.html?v=20260919-native-workflow-1';
  }

  function installAdmitCardEntry(){
    const nav=document.querySelector('nav[aria-label="Examination Module sections"]');
    if(nav && !document.getElementById('bulkAdmitCardsNav')){
      const a=document.createElement('a');
      a.id='bulkAdmitCardsNav';
      a.className='navButton';
      a.href='exam-admit-cards-v2.html?v=20260919-native-workflow-1';
      a.innerHTML='<span>8</span> Admit Cards';
      a.addEventListener('click',openAdmitCards);
      nav.appendChild(a);
    }

    const outputs=document.querySelector('[data-pane="outputs"] .buttonRow');
    if(outputs && !document.getElementById('bulkAdmitCardsOutput')){
      const a=document.createElement('a');
      a.id='bulkAdmitCardsOutput';
      a.className='button primary';
      a.href='exam-admit-cards-v2.html?v=20260919-native-workflow-1';
      a.textContent='Bulk Admit Cards';
      a.addEventListener('click',openAdmitCards);
      outputs.appendChild(a);
    }
  }

  installAdmitCardEntry();
  document.addEventListener('DOMContentLoaded',installAdmitCardEntry,{once:true});
  setTimeout(installAdmitCardEntry,600);
})();
