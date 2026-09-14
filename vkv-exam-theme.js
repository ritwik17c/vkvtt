(()=>{
  const STORAGE_KEY='vkvtt-theme';
  const root=document.documentElement;
  const button=document.getElementById('examThemeToggle');
  if(!button)return;

  function apply(theme,persist=false){
    const next=theme==='dark'?'dark':'light';
    root.dataset.theme=next;
    button.textContent=next==='dark'?'Light theme':'Dark theme';
    button.setAttribute('aria-pressed',String(next==='dark'));
    button.title=next==='dark'?'Switch to light theme':'Switch to dark theme';
    if(persist){try{localStorage.setItem(STORAGE_KEY,next)}catch(error){}}
  }

  apply(root.dataset.theme);
  button.addEventListener('click',()=>apply(root.dataset.theme==='dark'?'light':'dark',true));
})();
