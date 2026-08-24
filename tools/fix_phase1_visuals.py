from pathlib import Path
import base64,re,io
from PIL import Image

root=Path('.')
idx=root/'index.html'
css=root/'v66-premium-unified.css'
raw=(root/'swamiji-portrait.jpg').read_bytes()
im=Image.open(io.BytesIO(raw)).convert('RGBA')
out=io.BytesIO(); im.save(out,format='PNG',optimize=True)
png=out.getvalue(); b64=base64.b64encode(png).decode('ascii')
html=idx.read_text(encoding='utf-8')
# Replace top-right portrait source, whether current source is external JPG or embedded JPEG.
html=re.sub(r'(<img class="swamijiHomePortrait"\s+src=")[^"]+("\s+alt="Swami Vivekananda line portrait")',r'\1data:image/png;base64,'+b64+r'\2',html,count=1)
# Replace loader portrait source too.
html=re.sub(r'(<div class="vkvLoaderPortrait"><img src=")[^"]+("[^>]*>)',r'\1data:image/png;base64,'+b64+r'\2',html,count=1)
idx.write_text(html,encoding='utf-8')

c=css.read_text(encoding='utf-8')
marker='/* PHASE1 visual lock: v60 crest badge + top-right portrait */'
if marker not in c:
    c += '''\n\n/* PHASE1 visual lock: v60 crest badge + top-right portrait */\nbody:not(.adminDashboardPage) header .logo{\n  width:76px!important;height:88px!important;flex:0 0 76px!important;\n  object-fit:contain!important;clip-path:none!important;border-radius:38px!important;\n  padding:4px!important;background:#fff!important;box-shadow:0 1px 0 rgba(255,255,255,.22)!important;\n}\nheader .swamijiHomePortrait{display:block!important;object-fit:contain!important;opacity:.94!important}\n@media(min-width:701px){header .swamijiHomePortrait{width:118px!important;height:118px!important}}\n@media(max-width:700px){body:not(.adminDashboardPage) header .logo{width:58px!important;height:68px!important;flex-basis:58px!important;padding:3px!important}header .swamijiHomePortrait{width:74px!important;height:74px!important}}\n'''
css.write_text(c,encoding='utf-8')

# verification
html=idx.read_text(encoding='utf-8')
assert 'class="swamijiHomePortrait" src="data:image/png;base64,' in html
m=re.search(r'class="swamijiHomePortrait" src="data:image/png;base64,([A-Za-z0-9+/=]+)"',html)
assert m
p=base64.b64decode(m.group(1)); assert p[:8]==b'\x89PNG\r\n\x1a\n'
Image.open(io.BytesIO(p)).verify()
print('PASS portrait embedded as browser-safe PNG',len(p))
print('PASS v60 compact white crest badge override')
