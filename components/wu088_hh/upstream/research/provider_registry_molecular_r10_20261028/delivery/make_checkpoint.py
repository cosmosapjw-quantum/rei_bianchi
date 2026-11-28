from pathlib import Path
import json,hashlib,zipfile,sys,datetime
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(sys.argv[1]);pub=json.loads(PUB.read_text());stage=pub['stage'];commit=pub['source_commit']
L=ROOT/'research/provider_registry_molecular_r10_20261028'
deps=json.loads((L/'authority/INPUT_IDENTITY.json').read_text())['files']
paths=sorted(set(pub['files']+[x['path'] for x in deps]))
if any('PRIVATE_' in p or '__pycache__' in p for p in paths):raise ValueError('Non-public/non-source path')
rows=[];payload=[]
for p in paths:
 b=(ROOT/p).read_bytes();h=hashlib.sha256(b).hexdigest();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if p in [x['path'] for x in deps]:
  d=next(x for x in deps if x['path']==p);assert len(b)==d['bytes'] and h==d['sha256']
 if pub.get('identities') and p in pub['identities']:
  assert h==pub['identities'][p]['sha256'] and len(b)==pub['identities'][p]['bytes'],p
 rows.append({'path':p,'bytes':len(b),'sha256':h,'git_blob':blob,'mode':'100644','role':'new_source' if p in pub['files'] else 'pinned_inherited_input'})
 payload.append((p,b))
manifest={'schema':'WU_R10_SOURCE_CHECKPOINT_V1','stage':stage,'source_commit':commit,'source_tree':pub['source_tree'],'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'R10 published stage files + AGENTS + seven exact inherited R7-R9 input/evidence files','entire_git_repository_or_history':False,'files':rows,'manifest_self_hash_excluded':True,'runtime_outputs_outside_source':0}
out=ROOT.parent/'r10_checkpoints';out.mkdir(exist_ok=True)
name=f'WU_MOLECULAR_R10_{stage}_SOURCE_20261028_{commit[:12]}.zip';path=out/name
if path.exists():raise ValueError('Archive already exists; reuse actual identity')
with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,b in payload:
  info=zipfile.ZipInfo(p,(2026,10,28,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 z.writestr('CHECKPOINT_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 for r in rows:
  b=z.read(r['path']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
b=path.read_bytes();receipt={'stage':stage,'source_commit':commit,'source_tree':pub['source_tree'],'archive_name':name,'archive_path':str(path),'archive_bytes':len(b),'archive_sha256':hashlib.sha256(b).hexdigest(),'source_files':len(rows),'ZIP_CRC':'PASS','member_identity':'ALL_MATCH','scope':manifest['scope']}
(out/(stage+'_LOCAL.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
