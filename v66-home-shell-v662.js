/* VKVTT v66.2 — v60 premium tile feedback + robust Swamiji portrait */
(function(){
  'use strict';
  const portraitUrl='https://wsrv.nl/?url=raw.githubusercontent.com/ritwik17c/vkvtt/v66-2-refinement/swamiji-portrait.jpg&output=png';
  function applyPortrait(){
    const p=document.querySelector('.swamijiHomePortrait');
    if(p){p.src=portraitUrl;p.removeAttribute('srcset');}
    const lp=document.querySelector('#vkvSlowLoader .vkvLoaderPortrait img');
    if(lp){lp.src=portraitUrl;lp.removeAttribute('srcset');}
  }
  function tileHost(el){return el&&el.closest&&el.closest('.myGrid>button,.nav>button,.opsGrid>button')}
  document.addEventListener('click',e=>{const b=tileHost(e.target);if(!b)return;b.classList.remove('v662-click-nudge');void b.offsetWidth;b.classList.add('v662-click-nudge');setTimeout(()=>b.classList.remove('v662-click-nudge'),220)},true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyPortrait);else applyPortrait();
})();
