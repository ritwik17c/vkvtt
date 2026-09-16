(()=>{
  const STORAGE_KEY='vkvtt-exam-theme';
  const root=document.documentElement;
  const button=document.getElementById('examThemeToggle');

  function disableLegacyTheme(){
    document.querySelectorAll('link[data-vkv-black-gold-theme],link[href*="vkv-black-gold-screen.css"]').forEach(link=>{link.disabled=true;link.remove()});
  }

  function apply(theme,persist=false){
    const next=theme==='dark'?'dark':'light';
    disableLegacyTheme();
    root.dataset.theme=next;
    if(button){
      button.textContent=next==='dark'?'Light theme':'Dark theme';
      button.setAttribute('aria-pressed',String(next==='dark'));
      button.title=next==='dark'?'Switch to light theme':'Switch to dark theme';
    }
    if(persist){try{localStorage.setItem(STORAGE_KEY,next)}catch(error){}}
  }

  apply(root.dataset.theme);
  if(button) button.addEventListener('click',()=>apply(root.dataset.theme==='dark'?'light':'dark',true));
  new MutationObserver(disableLegacyTheme).observe(document.head,{childList:true});

  function admitUrl(){
    const name=(document.getElementById('workspaceName')||{}).value||'';
    return 'exam-admit-cards-v2.html?exam='+encodeURIComponent(name);
  }

  function installAdmitCardEntry(){
    const nav=document.querySelector('nav[aria-label="Examination Module sections"]');
    if(nav && !document.getElementById('bulkAdmitCardsNav')){
      const a=document.createElement('a');
      a.id='bulkAdmitCardsNav';
      a.className='navButton';
      a.href=admitUrl();
      a.innerHTML='<span>8</span> Admit Cards';
      a.addEventListener('click',()=>{a.href=admitUrl()});
      nav.appendChild(a);
    }

    const outputs=document.querySelector('[data-pane="outputs"] .buttonRow');
    if(outputs && !document.getElementById('bulkAdmitCardsOutput')){
      const a=document.createElement('a');
      a.id='bulkAdmitCardsOutput';
      a.className='button primary';
      a.href=admitUrl();
      a.textContent='Bulk Admit Cards';
      a.addEventListener('click',()=>{a.href=admitUrl()});
      outputs.appendChild(a);
    }
  }

  installAdmitCardEntry();
  document.addEventListener('DOMContentLoaded',installAdmitCardEntry,{once:true});
  setTimeout(installAdmitCardEntry,600);
})();
