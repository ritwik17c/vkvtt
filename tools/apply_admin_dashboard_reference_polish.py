from pathlib import Path
p=Path('admin-dashboard.html')
s=p.read_text(encoding='utf-8')
css='<link rel="stylesheet" href="v66-admin-reference-polish.css?v=66.2-adminref-1">'
js='<script src="v66-admin-reference-polish.js?v=66.2-adminref-1" defer></script>'
if css not in s:s=s.replace('</head>',css+'\n</head>',1)
if js not in s:s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('wired admin dashboard reference polish')
