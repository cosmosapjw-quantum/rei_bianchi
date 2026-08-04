#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('output_dir',type=Path);a=p.parse_args()
m=json.loads(a.manifest.read_text());a.output_dir.mkdir(parents=True,exist_ok=True);out=a.output_dir/m['original_name']
h=hashlib.sha256()
with out.open('wb') as target:
 for part in m['parts']:
  path=a.manifest.parent/part['name'];data=path.read_bytes()
  if hashlib.sha256(data).hexdigest()!=part['sha256']:raise SystemExit(f'hash mismatch: {path}')
  target.write(data);h.update(data)
if h.hexdigest()!=m['sha256']:raise SystemExit('reassembled hash mismatch')
print(out)
