#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
manifest=json.loads((P/'contracts/SOURCE_IDENTITY.json').read_text())
for name,expected in manifest['owner_blobs'].items():
    path=P/'rust/rei_iso_couple_p3/owner_src'/name
    if not path.exists(): raise SystemExit('MISSING_OWNER:'+name)
    got=subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
    if got!=expected:raise SystemExit('OWNER_GIT_BLOB_CHANGED:'+name+' '+got+' != '+expected)
print('PASS_FROZEN_PR150_OWNER_GIT_BLOBS',len(manifest['owner_blobs']))
