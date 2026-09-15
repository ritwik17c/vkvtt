(()=>{
  const STORAGE_KEY='vkvtt-exam-theme';
  const root=document.documentElement;
  const button=document.getElementById('examThemeToggle');
  if(!button)return;

  function disableLegacyTheme(){
    document.querySelectorAll('link[data-vkv-black-gold-theme],link[href*="vkv-black-gold-screen.css"]').forEach(link=>{link.disabled=true;link.remove()});
  }

  function apply(theme,persist=false){
    const next=theme==='dark'?'dark':'light';
    disableLegacyTheme();
    root.dataset.theme=next;
    button.textContent=next==='dark'?'Light theme':'Dark theme';
    button.setAttribute('aria-pressed',String(next==='dark'));
    button.title=next==='dark'?'Switch to light theme':'Switch to dark theme';
    if(persist){try{localStorage.setItem(STORAGE_KEY,next)}catch(error){}}
  }

  apply(root.dataset.theme);
  button.addEventListener('click',()=>apply(root.dataset.theme==='dark'?'light':'dark',true));
  new MutationObserver(disableLegacyTheme).observe(document.head,{childList:true});
})();
