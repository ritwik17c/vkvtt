/* VKVTT Question Bank dictation helper: progressive enhancement only. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
function install(){
 const ta=$('qText'); if(!ta||document.getElementById('qbDictationBar')) return !!ta;
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 const wrap=document.createElement('div');wrap.id='qbDictationBar';wrap.style.cssText='display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:7px 0 9px';
 wrap.innerHTML=`<button type="button" id="qbMicBtn" title="Dictate question">🎙 Dictate Question</button><button type="button" id="qbStopMic" style="display:none">■ Stop</button><select id="qbSpeechLang" title="Dictation language" style="width:auto;min-width:145px"><option value="en-IN">English (India)</option><option value="as-IN">Assamese</option><option value="hi-IN">Hindi</option><option value="bn-IN">Bengali</option></select><span id="qbSpeechState" class="small">${SR?'Ready for dictation':'Speech recognition is not supported in this browser.'}</span>`;
 ta.parentNode.insertBefore(wrap,ta);
 const mic=$('qbMicBtn'),stop=$('qbStopMic'),state=$('qbSpeechState'),lang=$('qbSpeechLang');
 if(!SR){mic.disabled=true;return true}
 let rec=null,base='',interim='';
 function cleanJoin(a,b){a=String(a||'');b=String(b||'').trim();if(!b)return a;return a+(a&& !/\s$/.test(a)?' ':'')+b}
 function finish(){if(rec){try{rec.stop()}catch(_){}}}
 mic.onclick=()=>{
   try{
     base=ta.value;interim='';rec=new SR();rec.lang=lang.value;rec.continuous=true;rec.interimResults=true;
     rec.onstart=()=>{state.textContent='Listening… speak naturally.';mic.disabled=true;stop.style.display='inline-block'};
     rec.onresult=e=>{let finalText='',temp='';for(let i=e.resultIndex;i<e.results.length;i++){const s=e.results[i][0]?.transcript||'';if(e.results[i].isFinal)finalText+=s+' ';else temp+=s}if(finalText){base=cleanJoin(base,finalText);interim=''}else interim=temp;ta.value=cleanJoin(base,interim);ta.dispatchEvent(new Event('input',{bubbles:true}))};
     rec.onerror=e=>{state.textContent=e.error==='not-allowed'?'Microphone permission was not allowed. Please allow microphone access and try again.':'Dictation error: '+e.error};
     rec.onend=()=>{if(interim){base=cleanJoin(base,interim);ta.value=base;interim=''}state.textContent='Dictation stopped. Please review the text before submitting.';mic.disabled=false;stop.style.display='none';rec=null};
     rec.start();
   }catch(e){state.textContent='Could not start dictation: '+(e.message||e);mic.disabled=false;stop.style.display='none'}
 };
 stop.onclick=finish;
 const improve=document.createElement('div');improve.id='qbImproveBar';improve.style.cssText='display:flex;gap:7px;flex-wrap:wrap;margin:-2px 0 10px';
 improve.innerHTML='<span class="small" style="align-self:center">After dictation:</span><button type="button" data-qb-clean="punct">✓ Tidy punctuation</button><button type="button" data-qb-clean="capital">Aa Capitalise start</button><button type="button" data-qb-clean="trim">✂ Clean spacing</button><span class="small">Suggestions never submit automatically.</span>';
 wrap.parentNode.insertBefore(improve,ta.nextSibling);
 improve.onclick=e=>{const b=e.target.closest('[data-qb-clean]');if(!b)return;let v=ta.value;if(b.dataset.qbClean==='trim')v=v.replace(/[ \t]+/g,' ').replace(/\s+([,.?!:;])/g,'$1').trim();if(b.dataset.qbClean==='capital'){v=v.trim();if(v)v=v[0].toUpperCase()+v.slice(1)}if(b.dataset.qbClean==='punct'){v=v.replace(/[ \t]+/g,' ').replace(/\s+([,.?!:;])/g,'$1').trim();if(v)v=v[0].toUpperCase()+v.slice(1);if(v&&!/[.?!]$/.test(v))v+='.'}ta.value=v;ta.focus()};
 return true;
}
let n=0;const t=setInterval(()=>{if(install()||++n>40)clearInterval(t)},250);window.addEventListener('load',install);
})();