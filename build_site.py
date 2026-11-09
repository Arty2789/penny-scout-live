from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1]
out=r/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for name in ('index.html','manifest.webmanifest','sw.js','icon-192.png','icon-512.png','apple-touch-icon.png'):
    shutil.copy2(r/name,out/name)
(out/'data').mkdir()
shutil.copy2(r/'data'/'leads.json',out/'data'/'leads.json')
(out/'.nojekyll').touch()
print('Static site assembled in _site/')
