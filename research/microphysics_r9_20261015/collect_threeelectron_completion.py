#!/usr/bin/env python3
"""Collect the authorized running case once complete, backup, publish raw unreviewed receipt.
No new physics run and no promotion of unreviewed science."""
import datetime,hashlib,json,os,shlex,subprocess,tarfile,time,traceback
from pathlib import Path
R=Path(__file__).resolve().parent
REPO=R.parents[1]
RECORD=REPO/'research/axbi_goal_20261014/execution/NCP_ACCESS_RECOVERY_20261014.json'
s=json.loads(RECORD.read_text());v=shlex.split(s['command'])
ssh=['ssh','-T','-i',v[v.index('-i')+1],'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ControlMaster=no','-o','ControlPath=none',s['user']+'@'+s['host']]
REMOTE='/root/REI_MICROPHYSICS_R9_20261015'
CASE='runs/threeelectron_v6/quench_Li_Be_union_aug_TZ_occ_list_v6'
NAME='REIONIZATION_R9_UNIT3_THREEE_RAW_20261015.tar.gz'
DRIVE='1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI'
def run(args,**kw):return subprocess.run(args,capture_output=True,check=True,**kw).stdout
def state(status,**extra):
 j={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'case':CASE,**extra}
 (R/'THREEE_COLLECTION_STATUS.json').write_text(json.dumps(j,indent=2)+'\n')
 print(json.dumps(j),flush=True)
try:
 parent_deadline=time.monotonic()+1200
 while not (R/'PUBLISH_UNIT2.json').exists():
  if time.monotonic()>parent_deadline:raise RuntimeError('Unit2 publication did not finish; collector not started')
  time.sleep(5)
 state('watching_existing_run',collector_pid=os.getpid())
 deadline=time.monotonic()+10800
 while time.monotonic()<deadline:
  ready="import json,pathlib,sys;p=pathlib.Path('"+REMOTE+'/'+CASE+"/receipt.json');sys.exit(0 if p.exists() and 'exit_code' in json.loads(p.read_text()) else 1)"
  p=subprocess.run(ssh+['python3 -c '+shlex.quote(ready)],capture_output=True,timeout=30)
  if p.returncode==0:break
  if p.returncode not in (0,1):state('transient_connection_error',exit_code=p.returncode)
  time.sleep(60)
 else:
  state('collection_deadline_reached',result_claimed=False);raise SystemExit(2)
 archive=R/NAME
 with archive.open('wb') as f:
  p=subprocess.run(ssh+['cd '+REMOTE+' && tar -czf - '+CASE+' code/microphysics_driver_v6.py CONTRACT_MICROPHYSICS_V6_THREEE.json'],stdout=f,stderr=subprocess.PIPE,timeout=180)
 assert p.returncode==0,p.stderr.decode()
 with tarfile.open(archive) as tf:tf.extractall(R/'ncp_results',filter='data')
 receipt=R/'ncp_results'/CASE/'receipt.json'
 j=json.loads(receipt.read_text())
 npz=receipt.parent/'data.npz'
 if j.get('data_sha256'):
  candidates=[p for p in receipt.parent.glob('*.npz') if hashlib.sha256(p.read_bytes()).hexdigest()==j['data_sha256']]
  assert candidates,'Declared NPZ hash did not match any extracted data file'
 b=archive.read_bytes();h={'sha256':hashlib.sha256(b).hexdigest(),'md5':hashlib.md5(b).hexdigest(),'dropbox':hashlib.sha256(b''.join(hashlib.sha256(b[k:k+4194304]).digest() for k in range(0,len(b),4194304))).hexdigest()}
 dests={}
 for lab,dest,flags in [('dropbox','dbx:BASS_DERIVATION_DOSSIERS_20260912/'+NAME,[]),('drive','gdrv:'+NAME,['--drive-root-folder-id',DRIVE])]:
  run(['rclone','copyto',str(archive),dest]+flags)
  st=json.loads(run(['rclone','lsjson',dest,'--stat','--hash']+flags,text=True))
  assert st['Size']==len(b)
  assert h['md5' if lab=='drive' else 'dropbox'] in st['Hashes'].values()
  dests[lab]={'id':st.get('ID'),'path':dest,'hashes':st['Hashes'],'verified':True}
 delivery={'archive':NAME,'bytes':len(b),'hashes':h,'destinations':dests,'receipt_status':j.get('status'),'finite_model_numerics_passed':j.get('finite_model_numerics_passed'),'independent_review':'PENDING. Raw result only; Unit2 report unchanged.'}
 (R/'UNIT3_RAW_DELIVERY.json').write_text(json.dumps(delivery,indent=2)+'\n')
 note='# Unit3 raw return; scientific review pending\n\nThe already-running Li/Be union augTZ case has terminated. Its exact receipt and raw arrays have been collected; archive integrity was checked and both backups verified. This automated collector does not perform independent physical review or promote basis convergence. Unit2 report remains an earlier completed snapshot. Read UNIT3_RAW_DELIVERY.json and the raw receipt before the next bounded review.\n'
 (R/'UNIT3_RAW_RETURN.md').write_text(note)
 branch='research/microphysics-r9-ncp-20261015'
 prev=run(['git','rev-parse','refs/heads/'+branch],cwd=REPO,text=True).strip()
 remote=run(['git','ls-remote','origin','refs/heads/'+branch],cwd=REPO,text=True).split()[0]
 assert remote==prev,'Branch changed externally; backup retained, publication paused.'
 idx=R/'publish_unit3.index'
 if idx.exists():idx.unlink()
 env=dict(os.environ,GIT_INDEX_FILE=str(idx))
 run(['git','read-tree',prev],cwd=REPO,env=env)
 selected=[receipt,R/'UNIT3_RAW_DELIVERY.json',R/'UNIT3_RAW_RETURN.md']
 for p in receipt.parent.iterdir():
  if p.is_file() and p.suffix in ('.json','.log') and p not in selected:selected.append(p)
 for p in selected:
  blob=run(['git','hash-object','-w','--',str(p)],cwd=REPO,text=True).strip()
  run(['git','update-index','--add','--cacheinfo','100644,'+blob+','+str(p.relative_to(REPO))],cwd=REPO,env=env)
 tree=run(['git','write-tree'],cwd=REPO,env=env,text=True).strip()
 commit=run(['git','commit-tree',tree,'-p',prev],cwd=REPO,input=b'R9 Unit3 raw NCP return: archived receipt, independent review pending\n').decode().strip()
 run(['git','update-ref','refs/heads/'+branch,commit,prev],cwd=REPO)
 run(['git','push','origin',commit+':refs/heads/'+branch],cwd=REPO)
 state('raw_result_backed_up_and_published_review_pending',commit=commit,receipt_status=j.get('status'),destinations=dests)
except Exception as e:
 state('collection_or_publication_failed',error=type(e).__name__+': '+str(e))
 raise
