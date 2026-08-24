from pathlib import Path
import re, subprocess, tempfile, base64
checks=[]
def ck(name,cond,detail=''):
    checks.append((name,bool(cond),detail));
    if not cond: print('FAIL',name,detail)

# required files
for n in ['index.html','admin-dashboard.html','admin-leave-editor.html','admin-leave.html','period-notifications.js','v66-premium-unified.css','swamiji-portrait.jpg']:
    ck('file '+n,Path(n).exists())

if Path('swamiji-portrait.jpg').exists():
    b=Path('swamiji-portrait.jpg').read_bytes();ck('portrait jpeg magic',b.startswith(b'\xff\xd8\xff') and b.endswith(b'\xff\xd9'),f'{len(b)} bytes')
idx=Path('index.html').read_text(encoding='utf-8',errors='ignore')
ck('index uses binary portrait','swamiji-portrait.jpg?v=66.2-premium-1' in idx)
ck('index unified css','v66-premium-unified.css' in idx)
pr=Path('period-notifications.js').read_text(encoding='utf-8',errors='ignore')
ck('period reminder anchors grid',"document.querySelector('.myGrid')" in pr)
ck('period reminder compact markup','prOptions' in pr and 'prText' in pr)
ad=Path('admin-dashboard.html').read_text(encoding='utf-8',errors='ignore')
ck('admin workspace hero','adminWorkspaceHero' in ad)
le=Path('admin-leave-editor.html').read_text(encoding='utf-8',errors='ignore')
for term in ['legacyDatedRecoverySection','recoverVerifiedLegacy','explicitLegacyDateInfo','data-history-edit-key','historyEditBtn','filterDateMode','filterTo','filterMonth','bulkDeleteErroneous']:
    ck('leave editor '+term,term in le)
ck('compact record range',"p.mode!=='multiple'&&p.startDate" in le)
la=Path('admin-leave.html').read_text(encoding='utf-8',errors='ignore')
ck('approved leave edit action','Edit in Leave Master' in la)
# all active pages inherit premium shell
exclude={'admin-leave-editor-v63.html','admin-leave-editor-v64-clean.html'}
for p in Path('.').glob('*.html'):
    if p.name in exclude: continue
    s=p.read_text(encoding='utf-8',errors='ignore');ck('premium '+p.name,'v66-premium-unified.css' in s)
# auth persistence on targeted pages
for n in ['admin-leave-editor.html','admin-leave.html','admin-leave-rules.html','admin-schedules.html','admin-export.html','admin-import.html','admin-leave-import.html','admin-timetable-studio.html']:
    p=Path(n)
    if p.exists() and 'getAuth' in p.read_text(encoding='utf-8',errors='ignore'):
        s=p.read_text(encoding='utf-8',errors='ignore');ck('auth persistence '+n,'browserLocalPersistence' in s and 'authStateReady' in s)
# JS syntax check external JS and module scripts from changed pages
for n in ['period-notifications.js']:
    r=subprocess.run(['node','--check',n],capture_output=True,text=True);ck('node check '+n,r.returncode==0,(r.stderr or r.stdout)[-500:])
for n in ['admin-leave-editor.html','admin-leave.html','admin-dashboard.html']:
    s=Path(n).read_text(encoding='utf-8',errors='ignore')
    scripts=re.findall(r'<script\s+type=["\']module["\'][^>]*>(.*?)</script>',s,re.S|re.I)
    for i,js in enumerate(scripts):
        tmp=Path(f'/tmp/v66check_{Path(n).stem}_{i}.mjs');tmp.write_text(js,encoding='utf-8')
        r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);ck(f'node module {n}#{i}',r.returncode==0,(r.stderr or r.stdout)[-700:])
# ensure passed known features still present
ck('daily history live summary hook','renderHistoryLiveOperationalSummary' in Path('v66-home.js').read_text(encoding='utf-8',errors='ignore'))
ck('leave integrity section','Leave Integrity Checker & Duplicate Remover' in le and le.find('Leave Integrity Checker & Duplicate Remover')>le.find('Leave Reconciliation Control'))
passed=sum(1 for _,ok,_ in checks if ok);failed=len(checks)-passed
report=[f'V66.2 FINAL STATIC VERIFICATION: {passed} PASS / {failed} FAIL','']+[f'{"PASS" if ok else "FAIL"}\t{name}\t{detail}' for name,ok,detail in checks]
Path('V66_2_FINAL_VERIFICATION.txt').write_text('\n'.join(report),encoding='utf-8')
print('\n'.join(report))
if failed: raise SystemExit(1)
