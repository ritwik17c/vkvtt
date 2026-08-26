/* VKVTT v66.2 — v60 premium tile feedback + deployed Swamiji portrait */
(function(){
  'use strict';
  const portraitUrl='https://raw.githubusercontent.com/ritwik17c/vkvtt-preview/main/Swami%20Vivekananda.png?v=swamiji-live-1';
  function applyPortrait(){
    const isMobile=window.matchMedia('(max-width:700px)').matches;
    const p=document.querySelector('.swamijiHomePortrait');
    if(p){
      p.src=portraitUrl;
      p.removeAttribute('srcset');
      const host=p.closest('.head')||p.parentElement;
      if(host){
        host.style.position='relative';
        host.style.setProperty('padding-right',isMobile?'86px':'132px','important');
      }
      p.style.setProperty('position','absolute','important');
      p.style.setProperty('right','0','important');
      p.style.setProperty('top','50%','important');
      p.style.setProperty('transform','translateY(-50%)','important');
      p.style.setProperty('margin','0','important');
      p.style.setProperty('width',isMobile?'68px':'108px','important');
      p.style.setProperty('height',isMobile?'68px':'108px','important');
      p.style.setProperty('object-fit','contain','important');
      p.style.setProperty('z-index','1','important');
      const title=document.querySelector('.homeTitleBlock');
      if(title){
        title.style.setProperty('position','relative','important');
        title.style.setProperty('z-index','2','important');
        title.style.setProperty('max-width',isMobile?'calc(100% - 92px)':'calc(100% - 170px)','important');
        if(isMobile){title.style.setProperty('padding-right','78px','important');}
      }
    }
    const lp=document.querySelector('#vkvSlowLoader .vkvLoaderPortrait img');
    if(lp){lp.src=portraitUrl;lp.removeAttribute('srcset');}
  }
  function installStudentGrowthTile(){
    if(document.getElementById('studentGrowthBtn'))return;
    const grid=document.querySelector('.opsGrid');
    if(!grid)return;
    const b=document.createElement('button');
    b.id='studentGrowthBtn';
    b.type='button';
    b.innerHTML='🌱 Student Growth <span style="opacity:.72;font-size:.82em">· Skolens</span>';
    b.setAttribute('aria-label','Open Student Growth / Skolens');
    b.addEventListener('click',()=>{location.href='student-growth.html?v=1.0'});
    grid.appendChild(b);
  }
  function tileHost(el){return el&&el.closest&&el.closest('.myGrid>button,.nav>button,.opsGrid>button')}
  document.addEventListener('click',e=>{const b=tileHost(e.target);if(!b)return;b.classList.remove('v662-click-nudge');void b.offsetWidth;b.classList.add('v662-click-nudge');setTimeout(()=>b.classList.remove('v662-click-nudge'),220)},true);
  function init(){applyPortrait();installStudentGrowthTile()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
  window.addEventListener('resize',applyPortrait);
})();
