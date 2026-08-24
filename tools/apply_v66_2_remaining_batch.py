from pathlib import Path
import re

# 1) Create a browser-safe Swamiji SVG from the already-approved embedded portrait.
src = Path('swamiji-gold.svg')
if src.exists():
    s = src.read_text(encoding='utf-8')
    s = re.sub(r'<filter\b.*?</filter>', '', s, flags=re.S|re.I)
    s = re.sub(r'\sfilter="url\([^\"]+\)"', '', s, flags=re.I)
    s = re.sub(r'\sstyle="[^"]*filter:[^"]*"', '', s, flags=re.I)
    Path('swamiji-clean.svg').write_text(s, encoding='utf-8')

# 2) Homepage: use the clean portrait and one final polish stylesheet.
p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = re.sub(r'src="swamiji-(?:portrait\.jpg|gold\.svg|clean\.svg)[^"]*"', 'src="swamiji-clean.svg?v=66.2-remain-1"', s)
css = '<link rel="stylesheet" href="v66-remaining-polish.css?v=66.2-remain-1">'
if css not in s:
    s = s.replace('</head>', css+'\n</head>', 1)
p.write_text(s, encoding='utf-8')

# 3) Admin dashboard: final polish + make auth restoration complete before first gate decision.
p = Path('admin-dashboard.html')
s = p.read_text(encoding='utf-8')
if css not in s:
    s = s.replace('</head>', css+'\n</head>', 1)
s = s.replace('setPersistence(auth,browserLocalPersistence).catch(()=>{});', "await setPersistence(auth,browserLocalPersistence).catch(()=>{});\nif(typeof auth.authStateReady==='function')await auth.authStateReady().catch(()=>{});")
p.write_text(s, encoding='utf-8')

# 4) Leave Master Editor: comprehensive filtering controls.
p = Path('admin-leave-editor.html')
s = p.read_text(encoding='utf-8')
old_block = re.compile(r'''<div class="grid4">\s*<div><label>Teacher</label><select id="filterTeacher"><option value="">All teachers</option></select></div>\s*<div><label>Category / status</label><select id="filterType">.*?</select></div>\s*<div><label>From date \(DD/MM/YYYY\)</label><input id="filterFrom"[^>]*></div>\s*<div><label>Search</label><input id="filterSearch"[^>]*></div>\s*</div>''', re.S)
new_block = '''<div class="leaveFilterPanel">
  <div class="grid4">
    <div><label>Staff</label><select id="filterTeacher"><option value="">All staff</option></select></div>
    <div><label>Leave category / status</label><select id="filterType"><option value="">All</option><option value="od">Duty Leave · OD</option><option value="special">Duty Leave · Special Assignment</option></select></div>
    <div><label>Date filter</label><select id="filterDateMode"><option value="all">All dates</option><option value="single">Single date</option><option value="range">From–To range</option><option value="month">Month wise</option><option value="recent">Recent / current / upcoming</option></select></div>
    <div><label>Record source</label><select id="filterSource"><option value="">All sources</option><option value="scheduled">Scheduled / approved</option><option value="daily">Daily approved status</option><option value="imported">Imported</option></select></div>
  </div>
  <div class="grid4 leaveDateFilters">
    <div><label>Single date (DD/MM/YYYY)</label><input id="filterSingle" class="dateInput" placeholder="DD/MM/YYYY" inputmode="numeric"></div>
    <div><label>From date (DD/MM/YYYY)</label><input id="filterFrom" class="dateInput" placeholder="DD/MM/YYYY" inputmode="numeric"></div>
    <div><label>To date (DD/MM/YYYY)</label><input id="filterTo" class="dateInput" placeholder="DD/MM/YYYY" inputmode="numeric"></div>
    <div><label>Month</label><input id="filterMonth" type="month"></div>
  </div>
  <div class="grid2">
    <div><label>Search</label><input id="filterSearch" placeholder="Staff, remarks, source…"></div>
    <div><label>Quick filters</label><div class="actions leaveFilterActions" style="margin-top:0"><button type="button" id="filterCurrentMonth">Current Month</button><button type="button" id="filterRecent">Recent</button><button type="button" id="filterShowAll">Show All</button><button type="button" id="filterReset">Reset</button></div></div>
  </div>
</div>'''
s, n = old_block.subn(new_block, s, count=1)
if n != 1:
    print('WARNING: filter UI block replacement count', n)

old_fn = re.compile(r'''function filteredRecords\(\)\{.*?\n\}''', re.S)
new_fn = r'''function filteredRecords(){
 let arr=[...activePlans().map(p=>({...p,_kind:'plan'})),...manualRecords.map(m=>({...m}))],
 tc=$('filterTeacher').value,ft=$('filterType').value,q=String($('filterSearch').value||'').trim().toLowerCase(),mode=String($('filterDateMode')?.value||'all'),single=dateToIso($('filterSingle')?.value||''),from=dateToIso($('filterFrom').value),to=dateToIso($('filterTo')?.value||''),month=String($('filterMonth')?.value||''),source=String($('filterSource')?.value||'');
 const dates=p=>(p._kind==='manual'?[p._date]:planDates(p)).filter(Boolean);
 if(tc)arr=arr.filter(p=>String(p.code)===tc);
 if(ft)arr=arr.filter(p=>(ft==='od'||ft==='special')?String(p.type||'')===ft:String(p.leaveCategory||'').toUpperCase()===ft);
 if(source)arr=arr.filter(p=>{const src=String(p._kind==='manual'?'daily':(p.source||'scheduled')).toLowerCase();return source==='daily'?p._kind==='manual':source==='imported'?src.includes('import'):p._kind!=='manual'&&!src.includes('import')});
 if(mode==='single'&&single)arr=arr.filter(p=>dates(p).includes(single));
 if(mode==='range'&&(from||to))arr=arr.filter(p=>dates(p).some(d=>(!from||d>=from)&&(!to||d<=to)));
 if(mode==='month'&&month)arr=arr.filter(p=>dates(p).some(d=>String(d).slice(0,7)===month));
 if(mode==='recent'){
   const now=new Date(),a=new Date(now);a.setDate(a.getDate()-60);const pad=n=>String(n).padStart(2,'0'),min=`${a.getFullYear()}-${pad(a.getMonth()+1)}-${pad(a.getDate())}`;
   arr=arr.filter(p=>dates(p).some(d=>d>=min));
 }
 if(mode==='all'&&from)arr=arr.filter(p=>dates(p).some(d=>d>=from));
 if(q)arr=arr.filter(p=>{const tt=teacherByCode(p.code);return[tt&&tt.name,p.code,p.note,p.remarks,p.source,p.leaveCategory,p._kind].some(v=>String(v||'').toLowerCase().includes(q))});
 return arr.sort((a,b)=>String((b._kind==='manual'?b._date:planDates(b)[0])||'').localeCompare(String((a._kind==='manual'?a._date:planDates(a)[0])||''))||String(a.code).localeCompare(String(b.code)));
}'''
s, n2 = old_fn.subn(new_fn, s, count=1)
if n2 != 1:
    print('WARNING: filteredRecords replacement count', n2)

wire = r'''
function wireExtendedLeaveFilters(){
 const rerender=()=>{recordRenderLimit=60;renderRecords()};
 ['filterTeacher','filterType','filterDateMode','filterSource','filterSingle','filterFrom','filterTo','filterMonth','filterSearch'].forEach(id=>{const el=$(id);if(!el||el.dataset.v66FilterWired)return;el.dataset.v66FilterWired='1';el.addEventListener(el.tagName==='SELECT'||el.type==='month'?'change':'input',rerender)});
 const setMode=(mode)=>{if($('filterDateMode'))$('filterDateMode').value=mode;rerender()};
 if($('filterCurrentMonth'))$('filterCurrentMonth').onclick=()=>{const d=new Date(),v=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;$('filterMonth').value=v;setMode('month')};
 if($('filterRecent'))$('filterRecent').onclick=()=>setMode('recent');
 if($('filterShowAll'))$('filterShowAll').onclick=()=>setMode('all');
 if($('filterReset'))$('filterReset').onclick=()=>{['filterTeacher','filterType','filterSource','filterSingle','filterFrom','filterTo','filterMonth','filterSearch'].forEach(id=>{const el=$(id);if(el)el.value=''});if($('filterDateMode'))$('filterDateMode').value='all';rerender()};
}
setTimeout(wireExtendedLeaveFilters,0);
'''
# Insert before last closing module script.
pos = s.rfind('</script>')
if pos != -1 and 'function wireExtendedLeaveFilters' not in s:
    s = s[:pos] + wire + '\n' + s[pos:]
if css not in s:
    s = s.replace('</head>', css+'\n</head>', 1)
p.write_text(s, encoding='utf-8')

# 5) Attendance page: explicit persistence before listener if the imports are already available.
for name in ['attendance.html','admin-attendance.html','admin-biometric-import.html','admin-leave.html']:
    p=Path(name)
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8')
    if 'browserLocalPersistence' in s:
        s=s.replace('setPersistence(auth,browserLocalPersistence).catch(()=>{});', "await setPersistence(auth,browserLocalPersistence).catch(()=>{});\nif(typeof auth.authStateReady==='function')await auth.authStateReady().catch(()=>{});")
    if css not in s and '</head>' in s:
        s=s.replace('</head>',css+'\n</head>',1)
    p.write_text(s,encoding='utf-8')

print('Applied remaining v66.2 batch')
