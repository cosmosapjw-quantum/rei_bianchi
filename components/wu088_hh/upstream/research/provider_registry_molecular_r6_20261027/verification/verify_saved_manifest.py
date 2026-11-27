"""Validate saved bytes and local DAG semantics; do not execute scientific code."""
from pathlib import Path
import hashlib, json
P=Path(__file__).resolve().parents[1]
m=json.loads((P/'SCIENTIFIC_PAYLOAD_MANIFEST.json').read_text())
for r in m['files']:
    b=(P/r['path']).read_bytes()
    if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:
        raise ValueError('Frozen scientific payload changed: '+r['path'])
digest=hashlib.sha256(json.dumps(m['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
if digest!=m['payload_sha256']:raise ValueError('Manifest digest mismatch')
d=json.loads((P/'DAG.json').read_text())
old=json.loads((P.parent/'provider_registry_molecular_r5_20261027/DAG.json').read_text())
if d['nodes'][:26]!=old['nodes']:raise ValueError('Inherited DAG object changed')
ids=[n['id'] for n in d['nodes']]
if len(ids)!=len(set(ids)):raise ValueError('Duplicate DAG identity')
complete=sum(str(n.get('status',n.get('current_status',''))).startswith('COMPLETE') for n in d['nodes'])
if {'complete':complete,'total':len(ids)}!=d['counts']:raise ValueError('DAG count mismatch')
print(json.dumps({'status':'PASS_METADATA_ONLY','payload_sha256':digest,'frozen_files':len(m['files']),
                  'DAG':d['counts'],'inherited_nodes_unchanged':26,'scientific_executions':0}))
