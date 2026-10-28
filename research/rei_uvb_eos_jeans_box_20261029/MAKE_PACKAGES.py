"""Create-only deterministic science source and per-completed-stage capsules."""
import zipfile,json,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'delivery';OUT.mkdir(exist_ok=True)
FILES=[]
for d in ['source','code','tests','results','stages']:
 for p in sorted((ROOT/d).rglob('*')):
  if p.is_file() and not p.name.endswith('.pyc') and '__pycache__' not in p.parts:
   FILES.append(p)
for n in ['README.md','THEORY_AND_CONTRACT_KO.md','REPORT_KO.md','HANDOFF_NEXT_THREAD_KO.md','FROZEN_EXECUTION.json','RESOURCE_ACCOUNTING_ADDENDUM.json','STAGE_LEDGER.json','BUILD_REPORTS.py']:
 FILES.append(ROOT/n)
manifest={'schema':'REI_EOS_JEANS_FULL_ORIGINAL_PAYLOAD_V1','source_pin':'PR253 21c695be2f672f5487e3fe1beb69b07af07a3c92','original_DAG_working':'33/88','original_DAG_central':'28/88','local_progress':'18/20 R6/C9 not native reviewed','entries':[]}
for p in sorted(FILES):
 b=p.read_bytes();manifest['entries'].append({'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
mb=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode()
def entry(f,n,data):
 info=zipfile.ZipInfo(n,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
 f.writestr(info,data)
core=OUT/'REI_EOS_JEANS_FULL_SOURCE_20261029.zip'
if core.exists():raise SystemExit('create-only full archive already exists')
with zipfile.ZipFile(core,'w') as f:
 for p in sorted(FILES):entry(f,str(p.relative_to(ROOT)),p.read_bytes())
 entry(f,'MANIFEST_INTERNAL.json',mb)
with zipfile.ZipFile(core) as f:
 assert f.testzip() is None
 for x in manifest['entries']:
  assert hashlib.sha256(f.read(x['path'])).hexdigest()==x['sha256']
sha=hashlib.sha256(core.read_bytes()).hexdigest()
core_id={'name':core.name,'sha256':sha,'bytes':core.stat().st_size,'files':len(FILES),'generated_2026_10_29_KST':True}
(OUT/'SCIENCE_SOURCE_IDENTITY.json').write_text(json.dumps(core_id,indent=2)+'\n')
pack=[]
for stage in [x for x in json.loads((ROOT/'STAGE_LEDGER.json').read_text())['stages'] if x['stage_status'].startswith('OUTPUT_COMPLETE')]:
 n=stage['stage'];p=OUT/('REI_EOS_JEANS_STAGE_'+n+'_20261029.zip')
 if p.exists():raise SystemExit('create-only stage archive already exists: '+n)
 with zipfile.ZipFile(p,'w') as f:
  entry(f,'STAGE.json',(ROOT/'stages'/(n+'.json')).read_bytes())
  entry(f,'SCIENCE_SOURCE_IDENTITY.json',(OUT/'SCIENCE_SOURCE_IDENTITY.json').read_bytes())
  entry(f,'FULL_SOURCE.zip',core.read_bytes())
 with zipfile.ZipFile(p) as f:
  assert f.testzip() is None
  assert f.read('FULL_SOURCE.zip')==core.read_bytes()
 pack.append({'stage':n,'progress':stage['stage_local_progress'],'stage_zip':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'scope':'OUTPUT_COMPLETE_SCOPED_NOT_NATIVE_REVIEWED','original_DAG_working':'33/88','original_DAG_central':'28/88','provider_ACKs':'PENDING_ACTUAL_UPLOAD'})
(OUT/'STAGE_PACKAGES_BEFORE_UPLOAD.json').write_text(json.dumps({'core':core_id,'stages':pack},indent=2)+'\n')
print(json.dumps({'core':core_id,'stages':len(pack),'total_stage_bytes':sum(x['bytes'] for x in pack)},indent=2))
