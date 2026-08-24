/* VKVTT v66.2 — approved v66.0 school landing shell + tile click feedback */
(function(){
  'use strict';
  function illustration(){return '<svg class="v662-school-illustration" viewBox="0 0 460 142" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 119h430" opacity=".32"/><path class="soft" d="M31 119V58h118v61M21 58l69-41 69 41M63 119V91h54v28"/><path d="M31 119V58h118v61M21 58l69-41 69 41M63 119V91h54v28M52 70h17v16H52zM111 70h17v16h-17z"/><path class="gold" d="M90 17v19M80 27h20"/><rect class="soft" x="190" y="30" width="105" height="77" rx="5"/><path d="M190 30h105v77H190zM205 49h75M205 66h75M205 83h75M225 30v77M258 30v77"/><circle class="goldfill" cx="349" cy="59" r="31"/><circle cx="349" cy="59" r="31"/><path class="gold" d="M349 42v18l13 8"/><path class="goldfill" d="M372 101c17-10 34-10 51 0v25c-17-10-34-10-51 0-17-10-34-10-51 0v-25c17-10 34-10 51 0Z"/><path d="M372 101c17-10 34-10 51 0v25c-17-10-34-10-51 0-17-10-34-10-51 0v-25c17-10 34-10 51 0ZM372 101v25"/></g></svg>'}
  function addRibbon(){
    if(document.querySelector('.v662-school-ribbon'))return;
    const anchor=document.getElementById('activeScheduleBanner');
    if(!anchor)return;
    const r=document.createElement('section');
    r.className='v662-school-ribbon';
    r.innerHTML='<div class="v662-school-copy"><div class="v662-eyebrow">Vivekananda Kendra Vidyalaya, Nalbari</div><strong>School Day Operations</strong><p>Timetables, classes, teachers, leave and daily school coordination at a glance.</p></div>'+illustration();
    anchor.insertAdjacentElement('afterend',r);
  }
  function tileHost(el){return el&&el.closest&&el.closest('.myGrid>button,.nav>button,.opsGrid>button')}
  document.addEventListener('click',e=>{const b=tileHost(e.target);if(!b)return;b.classList.remove('v662-click-nudge');void b.offsetWidth;b.classList.add('v662-click-nudge');setTimeout(()=>b.classList.remove('v662-click-nudge'),220)},true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addRibbon);else addRibbon();
})();
