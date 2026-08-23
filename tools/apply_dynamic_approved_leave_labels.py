from pathlib import Path
p=Path('admin-leave.html')
s=p.read_text(encoding='utf-8')
old="const CAT={VL:'VL',EL:'EL',CL:'CL',SEL:'SEL',EOL:'EOL',MATERNITY:'Maternity Leave'};\nlet user=null,profile=null,master=null,plans=[],daily=new Map(),legacyAccounting=[];"
new="let leaveRuleLabels=new Map();\nlet user=null,profile=null,master=null,plans=[],daily=new Map(),legacyAccounting=[];"
assert old in s, 'legacy CAT map not found'
s=s.replace(old,new,1)
old2="function catLabel(v){return CAT[String(v||'').toUpperCase()]||String(v||'')||'—'}"
new2="function catLabel(v){const raw=String(v||'').trim();if(!raw)return '—';return leaveRuleLabels.get(raw.toUpperCase())||raw}"
assert old2 in s, 'catLabel not found'
s=s.replace(old2,new2,1)
# Load optional configured labels without making register access depend on Leave Rules availability.
needle="master=m.data().data||m.data();$('gate').hidden=true;"
insert="master=m.data().data||m.data();try{const lr=await getDoc(doc(db,'leaveRules','current'));if(lr.exists()){const rd=lr.data()||{};const cats=Array.isArray(rd.categories)?rd.categories:[];leaveRuleLabels=new Map(cats.map(c=>[String(c.code||c.id||c.name||'').trim().toUpperCase(),String(c.label||c.name||c.code||c.id||'').trim()]).filter(x=>x[0]));}}catch(_){leaveRuleLabels=new Map();}$('gate').hidden=true;"
assert needle in s, 'master load insertion point not found'
s=s.replace(needle,insert,1)
p.write_text(s,encoding='utf-8')
print('approved leave labels made configurable')
