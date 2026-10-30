import hashlib,json,pathlib,sys,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((root/'MANIFEST.json').read_text())
assert manifest['schema']=='REI_F4_LII_2E1_CAUSAL_PACKAGE_MANIFEST_V1'
for rel,m in manifest['files'].items():
 p=root/rel
 if not p.is_file():raise RuntimeError('MISSING '+rel)
 raw=p.read_bytes()
 if len(raw)!=m['bytes'] or hashlib.sha256(raw).hexdigest()!=m['sha256']:raise RuntimeError('PAYLOAD_SHA '+rel)
 if rel.lower().endswith('.zip'):
  with zipfile.ZipFile(p) as z:
   if z.testzip() is not None:raise RuntimeError('CRC '+rel)
print('MANIFEST_PASS',len(manifest['files']))
