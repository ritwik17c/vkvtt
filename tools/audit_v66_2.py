from pathlib import Path
import re, json
out=[]
htmls=sorted(Path('.').glob('*.html'))
out.append('HTML FILES (%d)'%len(htmls))
for p in htmls:
    s=p.read_text(encoding='utf-8',errors='ignore')
    out.append(f'{p.name}\tdesign={"v66-design-system.css" in s}\tui={"v66-ui.js" in s}\tremaining={"v66-remaining-polish.css" in s}\tauthPersistence={"browserLocalPersistence" in s}\treturnAdmin={"Admin Dashboard" in s}\treturnHome={"Timetable Home" in s or "Return to Home" in s}')
le=Path('admin-leave-editor.html').read_text(encoding='utf-8',errors='ignore')
funcs=sorted(set(re.findall(r'function\s+([A-Za-z0-9_$]*(?:edit|Edit|start|Start)[A-Za-z0-9_$]*)\s*\(',le)))
out.append('\nLEAVE EDITOR EDIT/START FUNCTIONS')
out.extend(funcs)
out.append('\nLEAVE EDITOR MARKERS')
for term in ['data-edit','startEdit','editPlan','editManual','recordText','renderSelectedTeacherHistory','renderRecords','applyVlBulk','vlHasVerifiedRange','bulkDeleteErroneous','renderLeaveIntegrity']:
    out.append(f'{term}: {le.count(term)}')
idx=Path('index.html').read_text(encoding='utf-8',errors='ignore')
out.append('\nINDEX')
for term in ['swamiji-clean.svg','swamiji-portrait.jpg','periodReminderControl','v66-home-shell-v662','school-logo.jpg']:
    out.append(f'{term}: {idx.count(term)}')
pr=Path('period-notifications.js').read_text(encoding='utf-8',errors='ignore')
out.append('period anchor after first button: '+str("anchor.insertAdjacentElement('afterend',box)" in pr))
# asset decode check
import base64
for n in ['swamiji-gold.svg','swamiji-clean.svg']:
    p=Path(n)
    if p.exists():
        s=p.read_text(encoding='utf-8',errors='ignore')
        m=re.search(r'data:image/jpeg;base64,([^\"\']+)',s)
        if m:
            try:
                b=base64.b64decode(re.sub(r'\s+','',m.group(1)),validate=False)
                out.append(f'{n}: embedded jpeg bytes={len(b)} magic={b[:3].hex()} end={b[-2:].hex()}')
            except Exception as e: out.append(f'{n}: decode ERROR {e}')
Path('V66_2_AUDIT.txt').write_text('\n'.join(out),encoding='utf-8')
print('\n'.join(out))
