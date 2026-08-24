from pathlib import Path
CSS='<link rel="stylesheet" href="v66-final-sixpoint.css?v=66.2-final-1">'
JS='<script src="v66-final-sixpoint.js?v=66.2-final-1" defer></script>'
for p in Path('.').glob('*.html'):
    s=p.read_text(encoding='utf-8')
    if 'v66-design-system.css' not in s and p.name not in {'index.html','admin-dashboard.html','attendance.html','admin-leave-editor.html','admin-attendance.html','admin-biometric-import.html'}:
        continue
    if CSS not in s:
        s=s.replace('</head>',CSS+'\n</head>',1)
    if JS not in s:
        s=s.replace('</body>',JS+'\n</body>',1)
    p.write_text(s,encoding='utf-8')
# Homepage exact asset refresh and version bump.
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=s.replace('swamiji-portrait.jpg?v=66.2-sync-1','swamiji-portrait.jpg?v=66.2-final-1')
p.write_text(s,encoding='utf-8')
print('Applied final six-point CSS/runtime references')
