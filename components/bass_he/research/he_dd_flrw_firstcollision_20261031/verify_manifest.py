import json, pathlib,hashlib,sys
root=pathlib.Path(__file__).resolve().parent
m=json.loads((root/'MANIFEST_SHA256.json').read_text())
fail=[]
for name,sha in m['SHA256'].items():
 p=root/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:fail.append(name)
print('MANIFEST',len(m['SHA256'])-len(fail),'/',len(m['SHA256']), 'PASS' if not fail else 'FAIL '+str(fail))
if fail:sys.exit(1)
