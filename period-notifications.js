/* VKVTT v66.2 — personal period notification engine.
   Timing source: ACTIVE schedule profile only. No valid active timing => no announcement.
   The master timetable supplies assignment; active schedule supplies clock time.
   Browser limitation: exact background delivery is not guaranteed when the page/browser is suspended.
*/
(()=>{
'use strict';
const KEY='vkvttPeriodReminderPrefsV1', FIRED='vkvttPeriodReminderFiredV1';
const defaults={enabled:false,voice:true,notification:true,leadMinutes:1};
let timer=null;
function prefs(){try{return {...defaults,...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch(_){return {...defaults}}}
function savePrefs(v){localStorage.setItem(KEY,JSON.stringify({...prefs(),...v}));}
function parseStart(text){const m=String(text||'').trim().match(/(\d{1,2}):(\d{2})\s*(?:[–—-]|to)/i);if(!m)return null;const h=Number(m[1]),min=Number(m[2]);return h>=0&&h<24&&min>=0&&min<60?h*60+min:null}
function dayName(d=new Date()){return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][d.getDay()]}
function todayKey(d=new Date()){const p=n=>String(n).padStart(2,'0');return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}`}
function fired(){try{return JSON.parse(sessionStorage.getItem(FIRED)||'{}')}catch(_){return {}}}
function mark(id){const x=fired();x[id]=Date.now();sessionStorage.setItem(FIRED,JSON.stringify(x))}
function already(id){return !!fired()[id]}
function activeProfile(){if(typeof window.activeScheduleProfile==='function'){try{return window.activeScheduleProfile()}catch(_){}}const D=window.DATA;if(!D)return null;const id=D.activeScheduleProfileId||'normal',profiles=D.scheduleProfiles||{};return profiles[id]||profiles.normal||null}
function activeTime(period){if(typeof window.scheduleTime==='function'){try{return String(window.scheduleTime(period)||'')}catch(_){}}const p=activeProfile();if(!p)return '';return String(p.times?.[String(Number(period))]??p.times?.[Number(period)]??'')}
function classActive(cls,period){const p=activeProfile();if(!p)return false;if(p.classPeriods&&Array.isArray(p.classPeriods[cls]))return p.classPeriods[cls].map(Number).includes(Number(period));return true}
function myCode(){return String(window.__vkvMyTeacherCode||'').trim()}
function codeInRecord(r,code){if(Array.isArray(r.codes)&&r.codes.map(String).includes(code))return true;if(Array.isArray(r.teacherCodes)&&r.teacherCodes.map(String).includes(code))return true;return String(r.teacherCode||r.code||'')===code}
function effectiveRecords(date){const D=window.DATA,code=myCode();if(!D||!code)return[];let records=Array.isArray(D.records)?D.records:[];if(typeof window.operationalRecords==='function'){try{records=window.operationalRecords(date)}catch(_){}}
 return records.filter(r=>r.day===dayName()&&classActive(r.class,r.period)&&codeInRecord(r,code));}
function proxyFor(date,period,code){const sources=[window.__vkvPublishedProxy,window.__vkvMyProxyRecords,window.publishedProxy];for(const src of sources){const a=Array.isArray(src)?src:Object.values(src||{});const hit=a.find(x=>String(x.date||x.workDate||'')===date&&Number(x.period)===Number(period)&&String(x.proxyCode||x.teacherCode||x.code||'')===code);if(hit)return hit}return null}
function messageFor(r,proxy){const period=Number((proxy||r).period);const cls=(proxy&& (proxy.class||proxy.className))||r.class||'';const subject=(proxy&&(proxy.subject||proxy.assignment))||r.subject||String(r.entry||'').split('·')[0].trim();return proxy?`Proxy reminder. Next period: ${cls||'assigned class'}, Period ${period}.`:`Next period: ${cls||'assigned class'}, ${subject||'teaching assignment'}, Period ${period}.`}
async function announce(text){const p=prefs();if(p.notification&&'Notification'in window){try{if(Notification.permission==='granted')new Notification('VKVTT · Next Period',{body:text,tag:'vkvtt-next-period'});}catch(_){}}
 if(p.voice&&'speechSynthesis'in window){try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.rate=.95;speechSynthesis.speak(u)}catch(_){}}}
function check(){const p=prefs();if(!p.enabled)return;const prof=activeProfile();if(!prof)return;const code=myCode();if(!code)return;const now=new Date(),date=todayKey(now),minute=now.getHours()*60+now.getMinutes();const rows=effectiveRecords(date);for(const r of rows){const start=parseStart(activeTime(r.period));if(start===null)continue;if(minute!==start-Number(p.leadMinutes||1))continue;const proxy=proxyFor(date,r.period,code);const id=[date,code,r.period,r.class,start].join('|');if(already(id))continue;mark(id);announce(messageFor(r,proxy));}}
function installControls(){if(document.getElementById('periodReminderControl'))return;const anchor=document.querySelector('.myGrid')||document.getElementById('myTimetableBtn');if(!anchor)return;const box=document.createElement('div');box.id='periodReminderControl';box.className='periodReminderControl';box.style.cssText='';const p=prefs();box.innerHTML=`<b>🔔 Period Reminder</b><div class="prText">1-minute alert from the Activated Schedule.</div><div class="prOptions"><label><input id="prEnabled" type="checkbox" ${p.enabled?'checked':''}> Enabled</label><label><input id="prVoice" type="checkbox" ${p.voice?'checked':''}> Voice</label><label><input id="prNotify" type="checkbox" ${p.notification?'checked':''}> Notification</label><button id="prTest" type="button">Test Voice</button></div><div id="prStatus"></div>`;anchor.insertAdjacentElement('afterend',box);
 const status=box.querySelector('#prStatus');function sync(){savePrefs({enabled:box.querySelector('#prEnabled').checked,voice:box.querySelector('#prVoice').checked,notification:box.querySelector('#prNotify').checked});status.textContent=activeProfile()?`Timing source: ${activeProfile().name||window.DATA.activeScheduleProfileId}.`:'No valid Activated Schedule: reminders are suppressed.'}
 ['prEnabled','prVoice','prNotify'].forEach(id=>box.querySelector('#'+id).addEventListener('change',async()=>{sync();if(id==='prNotify'&&box.querySelector('#prNotify').checked&&'Notification'in window&&Notification.permission==='default'){try{await Notification.requestPermission()}catch(_){}}}));box.querySelector('#prTest').onclick=()=>announce('VKVTT period reminder test. Your next period begins in one minute.');sync();}
function boot(){installControls();if(timer)clearInterval(timer);timer=setInterval(check,15000);check();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(boot,1200));else setTimeout(boot,1200);
window.VKVTTPeriodReminder={check,prefs:()=>prefs(),set:s=>savePrefs(s),installControls};
})();
