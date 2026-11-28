from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[2]
f=Path(__file__).with_name('MANIFEST_SHA256.json')
d=json.loads(f.read_text())
missing=[]
wrong=[]
for name,sha in d.items():
 p=root/name
 if not p.is_file():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=sha:wrong.append(name)
print(f'MANIFEST {len(d)-len(missing)-len(wrong)}/{len(d)} PASS; missing={missing}; mismatches={wrong}')
if missing or wrong:sys.exit(1)
