import{initializeApp,getApps,getApp}from'https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js';
import{getAuth}from'https://www.gstatic.com/firebasejs/12.17.1/firebase-auth.js';

const cfg={apiKey:'AIzaSyDheZpyXghd1aQ9_RLhwpacVriG__wNZW4',authDomain:'vkv-nalbari-timetable.firebaseapp.com',projectId:'vkv-nalbari-timetable',storageBucket:'vkv-nalbari-timetable.firebasestorage.app',messagingSenderId:'791432856951',appId:'1:791432856951:web:61324065a54bef30f98d72'};
const app=getApps().length?getApp():initializeApp(cfg);
const auth=getAuth(app);

// Some mobile browser/WebView sessions can leave authStateReady() pending.
// The QB core already listens to onAuthStateChanged, so startup must never be
// blocked indefinitely waiting for this helper promise.
if(typeof auth.authStateReady==='function'){
  const original=auth.authStateReady.bind(auth);
  auth.authStateReady=()=>Promise.race([
    Promise.resolve().then(()=>original()).catch(()=>{}),
    new Promise(resolve=>setTimeout(resolve,1200))
  ]);
}
