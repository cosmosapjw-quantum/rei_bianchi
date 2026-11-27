from pathlib import Path
import json,base64,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];L=ROOT/'research/provider_registry_molecular_r10_20261028';stage=sys.argv[1]
n=99 if stage=='FINAL' else int(stage[1:]);state=ROOT.parent/'r10_published_state.json';old=json.loads(state.read_text())['files'] if state.exists() else {}
base={'CONTRACT.json','DAG.json','WORKFLOW_RECORD.json','EXECUTION_LEDGER.json','RESUME_KO.md'}
paths=[ROOT/'AGENTS.md']
for p in L.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts:continue
 r=p.relative_to(L).as_posix()
 yes=r in base or r.startswith('authority/') or (r.startswith('delivery/') and p.suffix=='.json')
 if n<2 and r.startswith('authority/'):yes=r=='authority/INPUT_IDENTITY.json'
 if n>=3 and (r=='theory/PREMISES_AND_MAP_KO.md' or r in ['verification/PRIMARY_INPUT.json','verification/REFERENCE_INPUT.json']):yes=True
 if n>=4 and (r=='theory/CONSTRUCTION_KO.md' or r.startswith('delivery/') or r=='verification/EXECUTION_PLAN.json'):yes=True
 if n>=5 and (r.startswith('theory/') or r.startswith('src/') or r.startswith('verification/') or r.startswith('reviews/') or r.startswith('raw/')):yes=True
 if n>=8:yes=True
 if yes:paths.append(p)
files={};changes={}
for p in sorted(paths):
 r=p.relative_to(ROOT).as_posix();b=p.read_bytes();encoding='base64' if p.suffix in ['.gz','.png','.pdf','.zip'] else 'utf-8';h=hashlib.sha256(b).hexdigest()
 files[r]={'bytes':len(b),'sha256':h,'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'encoding':encoding}
 if old.get(r,{}).get('sha256')!=h:changes[r]={'content':base64.b64encode(b).decode() if encoding=='base64' else b.decode(),'encoding':encoding}
print(json.dumps({'stage':stage,'files':files,'changes':changes},ensure_ascii=False,separators=(',',':')))
