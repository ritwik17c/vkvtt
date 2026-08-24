/* VKVTT v66.2 — v60 premium tile feedback + deployed Swamiji portrait */
(function(){
  'use strict';
  const portraitUrl='https://raw.githubusercontent.com/ritwik17c/vkvtt-preview/main/Swami%20Vivekananda.png?v=swamiji-live-1';
  function applyPortrait(){
    const p=document.querySelector('.swamijiHomePortrait');
    if(p){
      p.src=portraitUrl;
      p.removeAttribute('srcset');
      const host=p.closest('.head')||p.parentElement;
      if(host){
        host.style.position='relative';
        host.style.setProperty('padding-right',window.matchMedia('(max-width:700px)').matches?'78px':'124px','important');
      }
      p.style.setProperty('position','absolute','important');
      p.style.setProperty('right','0','important');
      p.style.setProperty('top','50%','important');
      p.style.setProperty('transform','translateY(-50%)','important');
      p.style.setProperty('margin','0','important');
      p.style.setProperty('width',window.matchMedia('(max-width:700px)').matches?'68px':'112px','important');
      p.style.setProperty('height',window.matchMedia('(max-width:700px)').matches?'68px':'112px','important');
      p.style.setProperty('object-fit','contain','important');
    }
    const lp=document.querySelector('#vkvSlowLoader .vkvLoaderPortrait img');
    if(lp){lp.src=portraitUrl;lp.removeAttribute('srcset');}
  }
  function tileHost(el){return el&&el.closest&&el.closest('.myGrid>button,.nav>button,.opsGrid>button')}
  document.addEventListener('click',e=>{const b=tileHost(e.target);if(!b)return;b.classList.remove('v662-click-nudge');void b.offsetWidth;b.classList.add('v662-click-nudge');setTimeout(()=>b.classList.remove('v662-click-nudge'),220)},true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyPortrait);else applyPortrait();
  window.addEventListener('resize',applyPortrait);
})();
