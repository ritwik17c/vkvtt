/* Production QB subject dropdown compatibility: merge master, QB config and safe school subjects into teacher workspace. */
(async()=>{'use strict';
const fallback=['English','Assamese','Hindi','Sanskrit','Mathematics','Environmental Studies','EVS','Science','Social Science','Physics','Chemistry','Biology','History','Geography','Political Science','Economics','Accountancy','Business Studies','Computer Science','Informatics Practices','Artificial Intelligence','Information Technology','Physical Education','Art Education','Work Experience','Value Education','General Knowledge','Music','Yoga'];
const clean=v=>String(v||'').trim();
const add=(set,v)=>{v=clean(v);if(v&&v.length<100)set.add(v)};
async function subjects(){
  const A=await import('https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js');
  const F=await import('https://www.gstatic.com/firebasejs/12.17.1/firebase-firestore-lite.js');
  const cfg={apiKey:'AIzaSyDheZpyXghd1aQ9_RLhwpacVriG__wNZW4',authDomain:'vkv-nalbari-timetable.firebaseapp.com',projectId:'vkv-nalbari-timetable',storageBucket:'vkv-nalbari-timetable.firebasestorage.app',messagingSenderId:'791432856951',appId:'1:791432856951:web:61324065a54bef30f98d72'};
  const app=A.getApps().length?A.getApp():A.initializeApp(cfg),db=F.getFirestore(app);
  const [ms,cs]=await Promise.all([F.getDoc(F.doc(db,'master','current')),F.getDoc(F.doc(db,'qbConfig','current')).catch(()=>null)]);
  const raw=ms.exists()?ms.data()||{}:{},m=raw.data&&typeof raw.data==='object'?{...raw,...raw.data}:raw,c=cs&&cs.exists()?cs.data()||{}:{};
  const set=new Set();
  (m.subjects||[]).forEach(x=>add(set,typeof x==='string'?x:(x?.name||x?.subject||x?.subjectName)));
  (m.records||[]).forEach(x=>{add(set,x?.subject);add(set,x?.subjectName)});
  (m.assignmentCards||[]).forEach(x=>{add(set,x?.subject);add(set,x?.subjectName)});
  (c.extraSubjects||[]).forEach(x=>add(set,x));
  fallback.forEach(x=>add(set,x));
  return [...set].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true,sensitivity:'base'}));
}
function install(list){
  const frame=document.querySelector('iframe[name="qbframe"]');if(!frame)return;
  const apply=()=>{
    let doc;try{doc=frame.contentDocument}catch(_){return}
    const sel=doc?.getElementById('sub');if(!sel)return false;
    const current=sel.value;
    const merged=new Set([...Array.from(sel.options).map(o=>clean(o.value||o.textContent)).filter(Boolean),...list]);
    sel.innerHTML=[...merged].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true,sensitivity:'base'})).map(x=>{const o=doc.createElement('option');o.value=x;o.textContent=x;return o.outerHTML}).join('');
    if(current&&[...sel.options].some(o=>o.value===current))sel.value=current;
    return true;
  };
  frame.addEventListener('load',()=>{let n=0;const t=setInterval(()=>{if(apply()||++n>30)clearInterval(t)},150)});
  let n=0;const t=setInterval(()=>{if(apply()||++n>30)clearInterval(t)},150);
}
try{install(await subjects())}catch(e){console.warn('QB production subject options:',e)}
})();
