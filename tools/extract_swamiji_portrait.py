from pathlib import Path
import re, base64
svg=Path('swamiji-gold.svg').read_text(encoding='utf-8')
m=re.search(r'data:image/jpeg;base64,([^\"]+)',svg)
if not m:
    raise SystemExit('Embedded portrait data not found')
Path('swamiji-portrait.jpg').write_bytes(base64.b64decode(m.group(1)))
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('src="swamiji-gold.svg?v=66.2"','src="swamiji-portrait.jpg?v=66.2-face-fix-1"')
p.write_text(s,encoding='utf-8')
print('Extracted approved portrait to standalone JPEG and updated index.html')
