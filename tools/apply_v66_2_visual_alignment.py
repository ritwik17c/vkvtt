from pathlib import Path

link='<link rel="stylesheet" href="v66-visual-alignment-fix.css?v=66.2-align-1">'

# Homepage: include the precise visual override.
p=Path('index.html')
s=p.read_text(encoding='utf-8')
if link not in s:
    s=s.replace('</head>',link+'\n</head>')
p.write_text(s,encoding='utf-8')

# Admin Dashboard: include the override and give the page a narrow scope class.
p=Path('admin-dashboard.html')
s=p.read_text(encoding='utf-8')
if link not in s:
    s=s.replace('</head>',link+'\n</head>')
s=s.replace('<body>','<body class="adminDashboardPage">',1)
p.write_text(s,encoding='utf-8')

print('Applied logo geometry and dashboard heading alignment fix')
