from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# force one coherent cache generation
repls={
 'v66-home.css?v=66.0-home-fix-1':'v66-home.css?v=66.2-sync-1',
 'v66-design-system.css?v=66.0-school-identity-1':'v66-design-system.css?v=66.2-sync-1',
 'v66-ui.js?v=66.0-school-identity-1':'v66-ui.js?v=66.2-sync-1',
 'period-notifications.js?v=66.2':'period-notifications.js?v=66.2-sync-1',
 'v66-home.js?v=66.0-home-fix-1':'v66-home.js?v=66.2-sync-1',
 'v66-home-cloud.js?v=66.0-home-fix-1':'v66-home-cloud.js?v=66.2-sync-1',
 'swamiji-gold.svg?v=66.2':'swamiji-portrait.jpg?v=66.2-sync-1',
 'swamiji-portrait.jpg?v=66.2-face-fix-1':'swamiji-portrait.jpg?v=66.2-sync-1'
}
for a,b in repls.items(): s=s.replace(a,b)
css='<link rel="stylesheet" href="v66-home-shell-v662.css?v=66.2-sync-1">'
js='<script src="v66-home-shell-v662.js?v=66.2-sync-1" defer></script>'
if css not in s: s=s.replace('</head>',css+'\n'+js+'\n</head>')
elif js not in s: s=s.replace('</head>',js+'\n</head>')
p.write_text(s,encoding='utf-8')

# service-worker cache generation so old preview shell cannot survive upload
p=Path('sw.js'); s=p.read_text(encoding='utf-8')
s=s.replace("vkvtt-shell-v66-2", "vkvtt-shell-v66-2-sync-1")
for f in ['v66-home-shell-v662.css','v66-home-shell-v662.js','swamiji-portrait.jpg']:
    if f not in s:
        # add safely to precache array before closing first ];
        pos=s.find('];')
        if pos!=-1: s=s[:pos]+f"  './{f}',\n"+s[pos:]
p.write_text(s,encoding='utf-8')
print('synchronised six-point preview package')
