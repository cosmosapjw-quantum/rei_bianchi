#!/usr/bin/env python3
"""Pin this isolated derivative; never write any accepted input."""
import pathlib,json,hashlib
root=pathlib.Path(__file__).resolve().parent
files=[f for area in ['rei-next-nodes','rei-adaptive-loop'] for f in (root/area).rglob('*') if f.is_file() and 'target' not in f.parts and f.name!='build_identity.rs' and f.suffix in ['.rs','.toml','.cfg','.lock']]
data=[{'path':str(f.relative_to(root)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(files)]
pin=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
(root/'rei-next-nodes/short-hhe-midpoint/src/build_identity.rs').write_text('const BUILD_PIN:&str="'+pin+'";\n')
(root/'evidence/BUILD_IDENTITY.json').write_text(json.dumps({'pin':pin,'files':data},indent=2)+'\n')
print(pin)
