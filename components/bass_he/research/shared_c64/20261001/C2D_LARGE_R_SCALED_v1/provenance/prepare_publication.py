"""Prepare a text-only, additive public namespace; never upload private PDFs."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
p=argparse.ArgumentParser();p.add_argument('--namespace',required=True);a=p.parse_args()
if not a.namespace.startswith('research/shared_c64/20261001/') or '..' in a.namespace:raise ValueError('invalid publication namespace')
selected=set()
for directory in ('code','reference','native','math','tests','inputs','review'):
 for path in (ROOT/directory).rglob('*'):
  if path.is_file() and '__pycache__' not in path.parts and path.suffix in ('.py','.f90','.md','.json'):selected.add(path)
for name in ('CONTRACT.json','CLAIMS.json','REPORT_KO.md','NEXT_HANDOFF_KO.md','runenv.sh'):
 path=ROOT/name
 if not path.is_file():raise FileNotFoundError(path)
 selected.add(path)
for name in ('FINAL_AUDIT.json','INITIAL_STATE_AUDIT.json','INHERITED_POINT_SCALARS.json','RECOVERY_LEDGER.json'):
 path=ROOT/'evidence'/name
 if path.is_file():selected.add(path)
for path in (ROOT/'evidence').glob('*MPI_LAUNCH.json'):selected.add(path)
for path in (ROOT/'evidence').glob('*MPI_PREFLIGHT.json'):selected.add(path)
for path in (ROOT/'evidence').glob('*MPI/BATCH_SUMMARY.json'):selected.add(path)
for path in (ROOT/'evidence').glob('*MPI/PARTIAL_BATCH_INDEX.json'):selected.add(path)
for path in (ROOT/'evidence').glob('*MPI/RUN_IDENTITY.json'):selected.add(path)
for path in (ROOT/'evidence').glob('*TEST*LOG.txt'):selected.add(path)
for name in ('AGENTS_AT_PARENT.md','PARENT_INPUTS.json','CONTRACT_IDENTITY.json','CONTRACT_IDENTITY_INITIAL.json','CONTRACT_IDENTITY_V1.json','CONTRACT_PRELAUNCH_V0.json','MAIN_CODE_IDENTITY.json','FOLLOWUP_CODE_IDENTITY.json','RECOVERY_CODE_IDENTITY.json','AFFECTED_TEST_ATTESTATIONS.json','RUNTIME_RECOVERY.json','RUNTIME_RECOVERY.md','FINAL_SOURCE_SCOPE.json','THEORY_SOURCE_IDENTITY.json','plot_results.py','prepare_followup.py','snapshot_sources.py','prepare_publication.py'):
 path=ROOT/'provenance'/name
 if path.is_file():selected.add(path)
for name in ('RECOVERY_SOURCE_INSTALL.json','RECOVERY_STAGED_DELIVERY.json','RECOVERY_IMPLEMENTATION_README.md','RECOVERY_PREPARATION_FAILURE.json','RECOVERY_STAGE2_INSTALL.json','RECOVERY_STAGE2_DELIVERY.json','RECOVERY_STAGE2_README.md','write_report.py','build_archive.py'):
 path=ROOT/'provenance'/name
 if path.is_file():selected.add(path)
elements=[];expected={}
for path in sorted(selected):
 if path.is_symlink():raise RuntimeError('symlink not allowed')
 raw=path.read_bytes();content=raw.decode('utf-8');public=a.namespace+'/'+str(path.relative_to(ROOT))
 elements.append({'path':public,'mode':'100644','type':'blob','content':content})
 expected[public]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}
payload=json.dumps(elements,ensure_ascii=True,separators=(',',':')).encode()
atomic_create(ROOT.parent/'C2D_PUBLIC_TREE_PAYLOAD.json',payload)
atomic_create(ROOT/'provenance/PUBLIC_EXPECTED.json',json_bytes(expected))
print(json.dumps({'files':len(elements),'payload_bytes':len(payload),'namespace':a.namespace}))
