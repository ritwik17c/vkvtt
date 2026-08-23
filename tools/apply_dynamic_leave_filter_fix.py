from pathlib import Path
p=Path('admin-leave-editor.html')
s=p.read_text(encoding='utf-8')
old='''<div><label>Category / status</label><select id="filterType"><option value="">All</option><option>VL</option><option>EL</option><option>CL</option><option>SEL</option><option>EOL</option><option value="MATERNITY">Maternity Leave</option><option value="od">OD</option><option value="special">Special Assignment</option></select></div>'''
new='''<div><label>Category / status</label><select id="filterType"><option value="">All</option><option value="od">Duty Leave · OD</option><option value="special">Duty Leave · Special Assignment</option></select></div>'''
if old not in s: raise SystemExit('hard-coded filter block not found')
s=s.replace(old,new,1)
anchor='''function leaveCategoryOptions(existingCategory=''){'''
insert='''function refreshCategoryStatusFilter(){
 const el=$('filterType');if(!el)return;
 const selected=String(el.value||'');
 const historicalCategories=new Set();
 for(const r of manualRecords||[]){const c=String(r&&r.category||'').trim().toUpperCase();if(c)historicalCategories.add(c)}
 for(const byDate of Object.values(plans||{})){for(const rec of Object.values(byDate||{})){const c=String(rec&&rec.category||'').trim().toUpperCase();if(c)historicalCategories.add(c)}}
 for(const r of legacy||[]){const c=String(r&&r.category||'').trim().toUpperCase();if(c)historicalCategories.add(c)}
 const configured=new Map((leaveRules||[]).map(r=>[String(r&&r.code||'').trim().toUpperCase(),r]).filter(([c])=>c));
 const codes=new Set([...configured.keys(),...historicalCategories]);
 const categories=[...codes].sort((a,b)=>leaveRuleLabel(a).localeCompare(leaveRuleLabel(b)));
 el.innerHTML='<option value="">All</option>'+categories.map(c=>`<option value="${safe(c)}">${safe(leaveRuleLabel(c)+(configured.has(c)&&configured.get(c).active===false?' · inactive':!configured.has(c)?' · historical':''))}</option>`).join('')+'<option value="od">Duty Leave · OD</option><option value="special">Duty Leave · Special Assignment</option>';
 if([...el.options].some(o=>o.value===selected))el.value=selected;
}

'''+anchor
if anchor not in s: raise SystemExit('leaveCategoryOptions anchor not found')
s=s.replace(anchor,insert,1)
# Hook refresh immediately after active rules are computed by the existing category option path, and on filter interaction via focus.
hook="""$('filterType')?.addEventListener('focus',refreshCategoryStatusFilter);"""
script_end='''</script>'''
pos=s.rfind(script_end)
if pos<0: raise SystemExit('script end not found')
s=s[:pos]+hook+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
