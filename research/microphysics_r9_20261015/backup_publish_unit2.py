#!/usr/bin/env python3
"""Archive and publish only this additive research unit; preserve checkout/index."""
import hashlib,json,os,subprocess,tarfile,datetime
from pathlib import Path
R=Path(__file__).resolve().parent
REPO=R.parents[1]
NAME='REIONIZATION_R9_UNIT2_CORRELATED_RUST_20261015.tar.gz'
ARCHIVE=R/NAME
DRIVE='1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI'
def call(args,**kwargs):
 p=subprocess.run(args,capture_output=True,check=True,**kwargs)
 return p.stdout
def hashes(p):
 b=p.read_bytes();blocks=b''.join(hashlib.sha256(b[i:i+4194304]).digest() for i in range(0,len(b),4194304))
 return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'md5':hashlib.md5(b).hexdigest(),'dropbox':hashlib.sha256(blocks).hexdigest()}
def backup(p):
 h=hashes(p); dests=[('dropbox','dbx:BASS_DERIVATION_DOSSIERS_20260912/'+p.name,[]),('drive','gdrv:'+p.name,['--drive-root-folder-id',DRIVE])]
 out={'filename':p.name,**h,'destinations':{}}
 for label,dest,flags in dests:
  call(['rclone','copyto',str(p),dest]+flags)
  st=json.loads(call(['rclone','lsjson',dest,'--stat','--hash']+flags,text=True))
  assert st['Size']==h['bytes'],(label,'size')
  got={k.lower():v for k,v in st['Hashes'].items()}
  want=h['md5'] if label=='drive' else h['dropbox']
  assert want in got.values(),(label,'hash mismatch')
  out['destinations'][label]={'id':st.get('ID'),'path':dest,'hashes':st['Hashes'],'verified':True}
 return out
dirs=['code','tests','bridge_code','bridge_tests','ncp_results','review','intake','results']
files=[p for p in R.iterdir() if p.is_file() and (p.name.startswith('CONTRACT') or p.name in ['README.md','REPORT_EN.md','REPORT_EN.tex','REPORT_EN.pdf','report_header.tex','finalize_snapshot.py','backup_publish_unit2.py','RUN_CONTINUATION.md','UNIT1_DELIVERY.json'])]
with tarfile.open(ARCHIVE,'w:gz') as tf:
 for p in files:tf.add(p,arcname=p.name)
 for d in dirs:
  for p in sorted((R/d).rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc']:tf.add(p,arcname=str(p.relative_to(R)))
delivery={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':backup(ARCHIVE),'pdf':backup(R/'REPORT_EN.pdf'),'latex':backup(R/'REPORT_EN.tex'),'scope':'Unit2 completed finite-model results. LiBe union augTZ separately running; final review pending.'}
(R/'UNIT2_DELIVERY.json').write_text(json.dumps(delivery,indent=2)+'\n')
link='https://drive.google.com/file/d/'+delivery['pdf']['destinations']['drive']['id']+'/view'
with (R/'README.md').open('a') as f:f.write('\nVerified Unit2 raw archive and standalone PDF/LaTeX backups are recorded in [UNIT2_DELIVERY.json](UNIT2_DELIVERY.json). [PDF download]('+link+').\n')
previous=json.loads((R/'PUBLISH_UNIT1.json').read_text())['commit']
branch='research/microphysics-r9-ncp-20261015'
current=call(['git','rev-parse','refs/heads/'+branch],cwd=REPO,text=True).strip()
assert current==previous,('branch advanced; do not overwrite',current,previous)
idx=R/'publish_unit2.index'
if idx.exists():idx.unlink()
env=dict(os.environ,GIT_INDEX_FILE=str(idx))
call(['git','read-tree',previous],cwd=REPO,env=env)
selected=[]
for p in R.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(R);parts=rel.parts
 if any(x in parts for x in ['vendor_r8','pdf_preview','__pycache__']):continue
 if p.suffix in ['.gz','.zip','.npz','.npy','.so','.pyc','.index','.aux','.toc']:continue
 if p.name in ['stage_payload.json','mark_artifact_operation_started.mjs','REPORT_EN.log','REPORT_BUILD.log','REPORT_EN_FIRST_BUILD_FAILURE.log']:continue
 if p.suffix not in ['.md','.json','.csv','.py','.c','.h','.f90','.sh','.txt','.tex','.pdf','.log','.dat']:continue
 if p.stat().st_size>2000000:continue
 selected.append(p)
for p in selected:
 blob=call(['git','hash-object','-w','--',str(p)],cwd=REPO,text=True).strip()
 path=str(p.relative_to(REPO))
 call(['git','update-index','--add','--cacheinfo','100644,'+blob+','+path],cwd=REPO,env=env)
tree=call(['git','write-tree'],cwd=REPO,env=env,text=True).strip()
commit=call(['git','commit-tree',tree,'-p',previous],cwd=REPO,input=b'Research R9 Unit2: correlated NCP extensions, numerical review and Rust verification\n').decode().strip()
call(['git','update-ref','refs/heads/'+branch,commit,previous],cwd=REPO)
call(['git','push','origin',commit+':refs/heads/'+branch],cwd=REPO)
pub={'branch':branch,'parent':previous,'commit':commit,'files_selected':len(selected),'checkout_branch':call(['git','branch','--show-current'],cwd=REPO,text=True).strip(),'pdf_url':link,'archive_drive_url':'https://drive.google.com/file/d/'+delivery['archive']['destinations']['drive']['id']+'/view'}
(R/'PUBLISH_UNIT2.json').write_text(json.dumps(pub,indent=2)+'\n')
print(json.dumps({'delivery':delivery,'publication':pub},indent=2))
