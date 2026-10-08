#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
files=[p for p in (r/'vendor').rglob('*') if p.is_file() and p.suffix in ['.rs','.cfg','.toml','.csv','.tsv'] and p.name!='build_identity.rs']
files.append(r/'oracle.py')
manifest={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
pin=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
(r/'vendor/frozen-panel-fixed-j32-final-interval-v1/src/build_identity.rs').write_text(f'const BUILD_PIN:&str="{pin}";\n')
(r/'evidence/BUILD_IDENTITY.json').write_text(json.dumps({'build_pin':pin,'source_files':manifest,'compiler_contract':'cargo offline dev opt-level2; one-core scalar ordered reductions; unchanged physics/gates','scope':'FROZEN_K3_K4_ONLY; BE_HANDOFF_REFUSED'},indent=2)+'\n')
print(pin)
