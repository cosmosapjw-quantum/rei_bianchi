from pathlib import Path
import hashlib,json,sys,os,subprocess,time,datetime
R=Path(__file__).resolve().parent;E=R/'evidence';OLD=R.parent;REPO=OLD/'w3/recovered/repo';L=REPO/'research/r31ao_unequal_ladder';NODE=L/'w3_coverage_contract_20261002_v1';PILOT=OLD/'runtime_work/pilot';WORKER=OLD/'prep_r2/worker';BACKEND=OLD/'prep_r2/backend';REVIEW=OLD/'fd2_prep_20261004_v1/input/WU088_HH_FD2_ROOT_CAUSE_20261004_v1';BRANCH='research/r31ao-unequal-order-ladder-20260930';HEAD='af2d2d42c68e0c8866b4030d271232af2cffa395'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):p=Path(p);return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def write(p,obj):
 with Path(p).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def run(label,args,cwd=None,timeout=180,env=None):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
 with (E/(label+'.stdout.log')).open('xb') as so,(E/(label+'.stderr.log')).open('xb') as se:
  try:cp=subprocess.run(args,cwd=cwd,timeout=timeout,env=env,stdout=so,stderr=se);rc=cp.returncode
  except subprocess.TimeoutExpired:rc=124
 row=dict(command=args,cwd=str(cwd) if cwd else None,start_utc=start,elapsed_seconds=time.monotonic()-t,exit_status=rc,stdout=label+'.stdout.log',stderr=label+'.stderr.log')
 with (E/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps(row),flush=True);return rc
sys.path.insert(0,str(NODE));import coverage_contract as c;import runtime_adapter as a

FD1=OLD/'fd1_prep_20261003_v3';CANDIDATE=REVIEW/'candidate/research/r31ao_unequal_ladder'
