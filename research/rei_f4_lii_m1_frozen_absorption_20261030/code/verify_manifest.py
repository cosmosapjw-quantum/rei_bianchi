import hashlib,json,pathlib,sys
p=pathlib.Path(__file__).resolve().parents[1];m=json.loads((p/'MANIFEST.json').read_text())
for f,digest in m['files'].items():
 q=p/f
 if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=digest:
  raise SystemExit('MANIFEST_FAIL:'+f)
expected={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.name!='MANIFEST.json'}
if set(m['files'])!=expected:raise SystemExit('MANIFEST_EXTRA_OR_MISSING')
print(f'MANIFEST_SHA_PASS={len(m["files"])}/{len(m["files"])}')
