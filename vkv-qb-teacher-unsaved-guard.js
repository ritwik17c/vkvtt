/* Safe client-side guard against accidental loss of a typed/dictated QB question. No Firestore access. */
(() => {
  const $ = id => document.getElementById(id);
  let mounted = false;

  function hasUnsavedQuestion(){
    const q = $('qText');
    return !!(q && q.value.trim());
  }

  function ensureIndicator(){
    if(mounted) return;
    const msg = $('editorMsg');
    const question = $('qText');
    if(!msg || !question) return;

    const note = document.createElement('div');
    note.id = 'qbUnsavedQuestionNote';
    note.className = 'small';
    note.style.marginTop = '6px';
    note.style.display = 'none';
    note.textContent = '● Unsaved question — save as Draft or Submit before leaving this page.';
    msg.insertAdjacentElement('afterend', note);

    const refresh = () => {
      note.style.display = hasUnsavedQuestion() ? '' : 'none';
    };
    question.addEventListener('input', refresh);
    question.addEventListener('change', refresh);
    refresh();
    mounted = true;
  }

  window.addEventListener('beforeunload', event => {
    if(!hasUnsavedQuestion()) return;
    event.preventDefault();
    event.returnValue = '';
  });

  const observer = new MutationObserver(() => ensureIndicator());
  observer.observe(document.documentElement, {childList:true, subtree:true});
  ensureIndicator();
})();
