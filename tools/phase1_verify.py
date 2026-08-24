from pathlib import Path
import re,subprocess,base64
checks=[]
def ck(n,c): checks.append((n,bool(c)))
idx=Path('index.html').read_text(encoding='utf-8',errors='ignore')
cloud=Path('v66-home-cloud.js').read_text(encoding='utf-8',errors='ignore')
home=Path('v66-home.js').read_text(encoding='utf-8',errors='ignore')
css=Path('v66-premium-unified.css').read_text(encoding='utf-8',errors='ignore')
ck('inline portrait', 'class="swamijiHomePortrait" src="data:image/jpeg;base64,' in idx)
ck('no portrait path dependency', 'swamiji-portrait.jpg?v=66.2-premium-1' not in idx)
ck('delayed loader', 'id="vkvSlowLoader"' in idx and '1800' in idx and 'vkvBlink' in idx)
ck('homepage auth waits persistence', 'await setPersistence(auth,browserLocalPersistence)' in cloud and 'await auth.authStateReady()' in cloud)
ck('conditional categories filtered', "String(r.ruleType||'regular')==='conditional'" in home and 'homeConditionalEligible(code,r,ctx)' in home)
ck('staff applicability filtered', '!homeRuleApplies(r,staff)' in home)
ck('no general unlimited wording', "value='Subject to approval'" in home)
ck('admin motif restrained','Phase-1 admin motif restraint' in css and 'opacity:.72' in css)
ck('crest refined','Phase-1 crest badge refinement' in css)
for n in ['v66-home.js','v66-home-cloud.js','period-notifications.js']:
 r=subprocess.run(['node','--check',n],capture_output=True,text=True);ck('syntax '+n,r.returncode==0)
# inline data decodes to jpeg
m=re.search(r'class="swamijiHomePortrait" src="data:image/jpeg;base64,([^"]+)',idx)
try:
 b=base64.b64decode(m.group(1));ck('inline portrait jpeg',b[:3]==b'\xff\xd8\xff' and b[-2:]==b'\xff\xd9')
except Exception: ck('inline portrait jpeg',False)
print('\n'.join(('PASS' if ok else 'FAIL')+' '+n for n,ok in checks))
if not all(ok for _,ok in checks): raise SystemExit(1)