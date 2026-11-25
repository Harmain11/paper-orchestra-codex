"""Check inline website JavaScript syntax with Node (CI safe on Windows/Linux)."""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

if not shutil.which('node'):
    print('Node missing; cannot validate documentation JavaScript.',file=sys.stderr)
    raise SystemExit(1)
html=(pathlib.Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
m=re.search(r'<script>(.*?)</script>',html,re.S)
if not m:
    raise SystemExit('No inline script found')
with tempfile.TemporaryDirectory() as work:
    path=pathlib.Path(work)/'site.js'
    path.write_text(m.group(1),encoding='utf-8')
    raise SystemExit(subprocess.run(['node','--check',str(path)],check=False).returncode)
