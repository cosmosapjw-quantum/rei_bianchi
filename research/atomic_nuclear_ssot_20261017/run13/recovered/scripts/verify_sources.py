from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];rec=json.loads((R/'contracts/UNCHANGED_SOURCE_RUN09.json').read_text())
for q in rec['rust_files']+rec['input_and_reference_files']:
 b=(R/q['path']).read_bytes()
 if q.get('relation')=='exact_prefix':
  assert b[q['prefix_bytes']:].decode()==q['suffix_utf8'];b=b[:q['prefix_bytes']]
 assert hashlib.sha256(b).hexdigest()==q['sha256'],q['path']
print(json.dumps({'status':'PASS_SOURCE_IDENTITIES','native_owner_count':rec['native_owner_count'],'retained_Rust':len(rec['rust_files']),'inputs_and_reference':len(rec['input_and_reference_files'])}))
