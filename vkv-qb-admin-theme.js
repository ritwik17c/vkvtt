(()=>{
  const KEY='vkvtt-qb-admin-theme',root=document.documentElement;
  const css=`
html[data-qb-theme="light"]{color-scheme:light}
html[data-qb-theme="light"] body{background:#edf6f1!important;color:#263d4e!important}
html[data-qb-theme="light"] body>header{background:#1d638e!important;color:#fff!important}
html[data-qb-theme="light"] body h1,html[data-qb-theme="light"] body h2,html[data-qb-theme="light"] body h3,html[data-qb-theme="light"] body h4,html[data-qb-theme="light"] body strong{color:#17364f!important}
html[data-qb-theme="light"] header h1,html[data-qb-theme="light"] header h2,html[data-qb-theme="light"] header strong{color:#fff!important}
html[data-qb-theme="light"] .card,html[data-qb-theme="light"] .panel{background:#fff!important;color:#263d4e!important;border-color:#cbdce5!important;box-shadow:0 4px 16px #17324d0d!important}
html[data-qb-theme="light"] .metric,html[data-qb-theme="light"] .qcard,html[data-qb-theme="light"] .leader,html[data-qb-theme="light"] .empty{background:#f8fbfc!important;color:#263d4e!important;border-color:#dbe6eb!important}
html[data-qb-theme="light"] .leader *,html[data-qb-theme="light"] .qcard *{text-shadow:none!important}
html[data-qb-theme="light"] .leader b,html[data-qb-theme="light"] .leader strong,html[data-qb-theme="light"] .qcard b,html[data-qb-theme="light"] .qcard strong{color:#17364f!important}
html[data-qb-theme="light"] .small,html[data-qb-theme="light"] .sub,html[data-qb-theme="light"] .lab,html[data-qb-theme="light"] label{color:#617685!important}
html[data-qb-theme="light"] .leader .small,html[data-qb-theme="light"] .qcard .small{color:#5f6f79!important}
html[data-qb-theme="light"] input,html[data-qb-theme="light"] select,html[data-qb-theme="light"] textarea{background:#fbfefd!important;color:#263d4e!important;border-color:#c6d7e0!important}
html[data-qb-theme="light"] option{background:#fff!important;color:#263d4e!important}
html[data-qb-theme="light"] .btn,html[data-qb-theme="light"] button{background:#e7f2f7!important;color:#17364f!important;border-color:#b9ced9!important}
html[data-qb-theme="light"] .primary,html[data-qb-theme="light"] .tabs button.active{background:#236d99!important;color:#fff!important;border-color:#236d99!important}
html[data-qb-theme="light"] .green{background:#e7f6ea!important;color:#245c34!important}
html[data-qb-theme="light"] .danger{background:#fdecec!important;color:#8b2d2d!important}
html[data-qb-theme="light"] .tip{background:#eef7fb!important;border-color:#bfdae7!important;color:#345d73!important}
html[data-qb-theme="light"] .warn{background:#fff7df!important;border-color:#e5cd8c!important;color:#745917!important}
html[data-qb-theme="light"] .badge{background:#eaf3f7!important;color:#17364f!important;border-color:#cbdce5!important}
html[data-qb-theme="light"] .rank,html[data-qb-theme="light"] .num,html[data-qb-theme="light"] .qtext{color:#236d99!important}
html[data-qb-theme="light"] table{background:#fff!important;color:#263d4e!important}
html[data-qb-theme="light"] th{background:#edf5f9!important;color:#17364f!important;border-color:#dfe8ed!important}
html[data-qb-theme="light"] td{background:#fff!important;color:#263d4e!important;border-color:#dfe8ed!important}
html[data-qb-theme="light"] tr:hover td{background:#f7fafb!important}
html[data-qb-theme="light"] a{color:#1d638e!important}
html[data-qb-theme="light"] header a,html[data-qb-theme="light"] header .btn{color:#17364f!important}
html[data-qb-theme="dark"]{color-scheme:dark}
html[data-qb-theme="dark"] body{background:#0f1720!important;color:#d9e5ec!important}
html[data-qb-theme="dark"] .card{background:#17222d!important;border-color:#314250!important;box-shadow:0 4px 16px #0004!important}
html[data-qb-theme="dark"] .metric,html[data-qb-theme="dark"] .qcard,html[data-qb-theme="dark"] .leader,html[data-qb-theme="dark"] .empty{background:#111c25!important;border-color:#314250!important;color:#d9e5ec!important}
html[data-qb-theme="dark"] .small,html[data-qb-theme="dark"] .sub,html[data-qb-theme="dark"] .lab,html[data-qb-theme="dark"] label{color:#a9bac6!important}
html[data-qb-theme="dark"] input,html[data-qb-theme="dark"] select,html[data-qb-theme="dark"] textarea{background:#111c25!important;color:#eaf2f6!important;border-color:#405463!important}
html[data-qb-theme="dark"] .btn,html[data-qb-theme="dark"] button{background:#223342!important;color:#eaf2f6!important;border-color:#405463!important}
html[data-qb-theme="dark"] .primary,html[data-qb-theme="dark"] .tabs button.active{background:#2f7fae!important;color:#fff!important;border-color:#2f7fae!important}
html[data-qb-theme="dark"] .green{background:#244d35!important;color:#dff5e7!important}
html[data-qb-theme="dark"] .danger{background:#4a262b!important;color:#ffd9de!important}
html[data-qb-theme="dark"] .tip{background:#162a36!important;border-color:#355367!important;color:#c9e0eb!important}
html[data-qb-theme="dark"] .warn{background:#3a301c!important;border-color:#6b5a2b!important;color:#f1dfaa!important}
html[data-qb-theme="dark"] .badge{background:#223746!important;color:#dceaf1!important}
html[data-qb-theme="dark"] th{background:#1c2a35!important;color:#eaf2f6!important}
html[data-qb-theme="dark"] td,html[data-qb-theme="dark"] th{border-color:#344653!important}
html[data-qb-theme="dark"] .qtext,html[data-qb-theme="dark"] .rank,html[data-qb-theme="dark"] .num{color:#78c4ec!important}
#qbThemeToggle{min-width:98px}`;
  function installCss(){if(document.getElementById('qbThemeStyles'))return;const s=document.createElement('style');s.id='qbThemeStyles';s.textContent=css;document.head.appendChild(s)}
  function systemDark(){return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches}
  function current(){const saved=localStorage.getItem(KEY);return saved==='dark'||saved==='light'?saved:(systemDark()?'dark':'light')}
  function apply(theme){root.dataset.qbTheme=theme;localStorage.setItem(KEY,theme);const b=document.getElementById('qbThemeToggle');if(b){b.textContent=theme==='dark'?'☀️ Light':'🌙 Dark';b.setAttribute('aria-label',theme==='dark'?'Switch to light theme':'Switch to dark theme');b.title=b.getAttribute('aria-label')}}
  function inject(){installCss();if(document.getElementById('qbThemeToggle'))return;const host=document.querySelector('header .actions');if(!host)return;const b=document.createElement('button');b.type='button';b.id='qbThemeToggle';b.className='btn';b.style.width='auto';b.addEventListener('click',()=>apply(root.dataset.qbTheme==='dark'?'light':'dark'));host.prepend(b);apply(current())}
  installCss();apply(current());if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',inject,{once:true});else inject();
})();
