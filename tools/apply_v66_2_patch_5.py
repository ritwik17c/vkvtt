from pathlib import Path
import re


def replace_once(path, old, new, marker):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if marker in s:
        print(f'{path}: already patched {marker}'); return
    if old not in s: raise SystemExit(f'{path}: anchor not found {marker}')
    p.write_text(s.replace(old,new,1),encoding='utf-8'); print(f'{path}: patched {marker}')

# -----------------------------------------------------------------------------
# 1. Leave Rules: visible dates dd/mm/yyyy, internal values remain ISO.
# -----------------------------------------------------------------------------
replace_once('admin-leave-rules.html',
'<div><label>Start date</label><input id="periodStart" type="date"></div>\n      <div><label>End date</label><input id="periodEnd" type="date"></div>',
'<div><label>Start date (dd/mm/yyyy)</label><input id="periodStart" type="text" inputmode="numeric" maxlength="10" placeholder="dd/mm/yyyy"></div>\n      <div><label>End date (dd/mm/yyyy)</label><input id="periodEnd" type="text" inputmode="numeric" maxlength="10" placeholder="dd/mm/yyyy"></div>',
'Start date (dd/mm/yyyy)')

replace_once('admin-leave-rules.html',
"function periodKey(p=entitlementPeriod){return p&&p.startDate&&p.endDate?String(p.key||`${p.startDate}__${p.endDate}`):''}",
"function displayDate(k){const m=String(k||'').match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);return m?`${m[3]}/${m[2]}/${m[1]}`:String(k||'')}\nfunction inputDate(v){const m=String(v||'').trim().match(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})$/);if(!m)return'';const iso=`${m[3]}-${m[2]}-${m[1]}`,d=new Date(iso+'T00:00:00');return d.getFullYear()===Number(m[3])&&d.getMonth()+1===Number(m[2])&&d.getDate()===Number(m[1])?iso:''}\nfunction periodKey(p=entitlementPeriod){return p&&p.startDate&&p.endDate?String(p.key||`${p.startDate}__${p.endDate}`):''}",
'function inputDate(v)')

p=Path('admin-leave-rules.html'); s=p.read_text(encoding='utf-8')
s=s.replace("$('periodStart').value=entitlementPeriod?.startDate||'';$('periodEnd').value=entitlementPeriod?.endDate||'';","$('periodStart').value=displayDate(entitlementPeriod?.startDate||'');$('periodEnd').value=displayDate(entitlementPeriod?.endDate||'');",1)
s=s.replace("$('periodState').textContent=periodValid()?`${entitlementPeriod.startDate} → ${entitlementPeriod.endDate}`:'Not configured';","$('periodState').textContent=periodValid()?`${displayDate(entitlementPeriod.startDate)} → ${displayDate(entitlementPeriod.endDate)}`:'Not configured';",1)
old="const type=$('periodType').value,startDate=$('periodStart').value,endDate=$('periodEnd').value,description=$('periodDescription').value.trim();\n if(!type||!startDate||!endDate){msg('Period type, start date and end date are required.','error');return}\n if(startDate>endDate){msg('Entitlement period start date cannot be later than the end date.','error');return}"
new="const type=$('periodType').value,startDate=inputDate($('periodStart').value),endDate=inputDate($('periodEnd').value),description=$('periodDescription').value.trim();\n if(!type||!startDate||!endDate){msg('Period type and valid Start/End dates in dd/mm/yyyy are required.','error');return}\n if(startDate>endDate){msg('Entitlement period start date cannot be later than the end date.','error');return}"
if old not in s and 'valid Start/End dates in dd/mm/yyyy' not in s: raise SystemExit('admin-leave-rules.html: period save anchor not found')
s=s.replace(old,new,1)
s=s.replace("Period: ${entitlementPeriod.startDate} to ${entitlementPeriod.endDate}","Period: ${displayDate(entitlementPeriod.startDate)} to ${displayDate(entitlementPeriod.endDate)}")
s=s.replace("Verified range: ${safe(x.vlFromDate)} → ${safe(x.vlToDate)}","Verified range: ${safe(displayDate(x.vlFromDate))} → ${safe(displayDate(x.vlToDate))}")
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 2. Selected buttons: preserve original card colour/text and use gold outline.
# -----------------------------------------------------------------------------
p=Path('v66-home.css'); s=p.read_text(encoding='utf-8')
# Remove the old blanket blue selected-state block and specialised blue active rules.
s=re.sub(r'/\* Selected-state accessibility fix \*/\s*button\.active,.*?button\.active \* \{ color:#ffffff !important; \}\s*', '', s, count=1, flags=re.S)
s=re.sub(r'\.leaveBtns button\[data-leave-type\]\.active\{.*?\}\s*', '', s, count=1, flags=re.S)
s=re.sub(r'\.myModeBtns button\.active\{.*?\}', '', s, count=1, flags=re.S)
s=re.sub(r'\.durationBtns button\.active\{.*?\}', '', s, count=1, flags=re.S)
s=re.sub(r'\.leaveDateModes button\.active\{.*?\}', '', s, count=1, flags=re.S)
s=re.sub(r'#publishedProxyBtn\.active\{.*?\}', '', s, count=1, flags=re.S)
if 'vkv-selected-gold-outline' not in s:
    s += '''\n/* v66.2 unified selected-state: retain each button's own colour and content. */\n@keyframes vkvSelectedNudge{0%,100%{transform:translateX(0)}32%{transform:translateX(-1.5px)}68%{transform:translateX(1.5px)}}\nbutton.active,\n.nav button.active,\n.quick button.active,\n.opsGrid button.active,\n.myGrid button.active,\n.myModeBtns button.active,\n.leaveBtns button.active,\n.leaveDateModes button.active,\n.durationBtns button.active{\n  outline:2px solid #c88a18 !important;\n  outline-offset:2px;\n  border-color:#d6a23b !important;\n  box-shadow:0 0 0 3px rgba(200,138,24,.14),0 6px 18px rgba(11,43,66,.08) !important;\n  color:var(--ink) !important;\n  animation:vkvSelectedNudge .20s ease;\n}\nbutton.active *{color:inherit !important}\n/* marker: vkv-selected-gold-outline */\n'''
p.write_text(s,encoding='utf-8')

p=Path('v66-design-system.css'); s=p.read_text(encoding='utf-8')
old='''html.v66-ui .primary,\nhtml.v66-ui button.primary,\nhtml.v66-ui .btn.primary,\nhtml.v66-ui button.active,\nhtml.v66-ui [aria-pressed="true"] {\n  border-color: var(--vkv-navy-800) !important;\n  background: var(--vkv-navy-800) !important;\n  color: #fff !important;\n}\n'''
new='''html.v66-ui .primary,\nhtml.v66-ui button.primary,\nhtml.v66-ui .btn.primary {\n  border-color: var(--vkv-navy-800) !important;\n  background: var(--vkv-navy-800) !important;\n  color: #fff !important;\n}\nhtml.v66-ui button.active,\nhtml.v66-ui [aria-pressed="true"] {\n  outline: 2px solid var(--vkv-gold-500) !important;\n  outline-offset: 2px;\n  border-color: #d8a640 !important;\n  box-shadow: 0 0 0 3px rgba(200,138,24,.13), var(--vkv-shadow-sm) !important;\n}\n'''
if 'outline: 2px solid var(--vkv-gold-500)' not in s:
    if old not in s: raise SystemExit('v66-design-system.css: active-state anchor not found')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 3. Same-tab Admin navigation. Replace new-tab admin dashboard openings if any.
# -----------------------------------------------------------------------------
for fname in ['v66-home.js','v66-home-cloud.js','index.html']:
    p=Path(fname); s=p.read_text(encoding='utf-8')
    before=s
    # Common window.open forms specifically targeting admin-dashboard.
    s=re.sub(r"window\.open\((['\"]admin-dashboard\.html[^'\"]*['\"]),\s*['\"]_blank['\"]\)", r"location.href=\1", s)
    s=re.sub(r"window\.open\((['\"]admin-dashboard\.html[^'\"]*['\"])\)", r"location.href=\1", s)
    if s!=before: print(f'{fname}: changed Admin Dashboard navigation to same tab')
    p.write_text(s,encoding='utf-8')

# Admin's Timetable Home already uses location.href; make any index target=_blank links same-tab.
for fname in ['admin-dashboard.html','admin-leave.html','admin-leave-editor.html','admin-leave-rules.html']:
    p=Path(fname); s=p.read_text(encoding='utf-8')
    s=re.sub(r'(<a[^>]+href=["\']index\.html[^"\']*["\'][^>]*)\s+target=["\']_blank["\']',r'\1',s,flags=re.I)
    p.write_text(s,encoding='utf-8')

# Small stale wording in My Area.
p=Path('index.html'); s=p.read_text(encoding='utf-8').replace('Loading your approved Leave / OD / Special Assignment records…','Loading your approved Leave and Duty Leave records…')
p.write_text(s,encoding='utf-8')

print('VKVTT v66.2 date/button/navigation patch completed.')
