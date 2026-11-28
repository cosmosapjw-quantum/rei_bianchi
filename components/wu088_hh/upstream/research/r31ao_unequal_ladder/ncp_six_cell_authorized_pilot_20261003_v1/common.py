from pathlib import Path
import os,sys,json,hashlib,subprocess,time,datetime
R=Path(__file__).resolve().parent
E=R/'evidence'
OLD=R.parent
REPO=OLD/'w3/recovered/repo'
NODE=REPO/'research/r31ao_unequal_ladder/w3_coverage_contract_20261002_v1'
PILOT=OLD/'runtime_work/pilot'
PROPOSAL=OLD/'prep_r2/evidence/BINDING_PROPOSAL.json'
PROPOSAL_SHA='51a474d473a9a095a1bae68949e63bd1dfdc50d7b12c9a971a85323054f0b57c'
PROPOSAL_BYTES_SHA='cdaf21b33cfbf4a3abd1f977332ad983da84d4026b5601443f6b41fd0adeb116'
PREPARED_SHA='0e06c0f959684e808f1ef1f6d8465e00079e0b6401eba311b804e458bac0f3a0'
SCOPE_SHA='91f8f304f2c0aa8668a1d8bc18b1972348768772fa308d8b3c9483cc8c254a5b'
BUILD_SHA='51493d807432d46106cdee5e83ebc5d1830234fead90b28a0845915da148982e'
HEAD='80e87bcbad5d803e8010fa3c7190b7a425734445'
BRANCH='research/r31ao-unequal-order-ladder-20260930'
UNIT='wu088-six-cell-pilot-20261003-v1.service'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):
 p=Path(p);return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def write(p,value):
 p=Path(p)
 with p.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
def run(label,args,cwd=None,timeout=300,env=None):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
 with (E/(label+'.stdout.log')).open('xb') as so,(E/(label+'.stderr.log')).open('xb') as se:
  try:cp=subprocess.run(args,cwd=cwd,stdout=so,stderr=se,timeout=timeout,env=env);code=cp.returncode
  except subprocess.TimeoutExpired:code=124
 row=dict(start_utc=start,command=args,cwd=str(cwd) if cwd else None,exit_status=code,elapsed_seconds=time.monotonic()-t,stdout=label+'.stdout.log',stderr=label+'.stderr.log')
 with (E/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(row),flush=True);return code
sys.path.insert(0,str(NODE))
import coverage_contract as c
import runtime_adapter as a
def registry_inventory():
 hits=[];roots=[];scope_copies=[]
 for base in (OLD,Path('/root/WU088_HH')):
  for folder,dirs,files in os.walk(base,followlinks=False):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__','sources','metadata_probe','toolchain_sample')]
   p=Path(folder)
   if p.name=='run_registry':
    roots.append(str(p))
    if SCOPE_SHA+'.json' in files:hits.append(ref(p/(SCOPE_SHA+'.json')))
   if 'RUN_STARTED.json' in files or 'EXECUTION_BINDING.json' in files:
    for n in ('RUN_STARTED.json','EXECUTION_BINDING.json'):
     if n in files:
      try:
       o=c.load(p/n)
       if o.get('scope_sha256')==SCOPE_SHA:scope_copies.append(ref(p/n))
      except (ValueError,OSError):scope_copies.append(dict(path=str(p/n),reason='unreadable marker; fail closed'))
 markers=[ref(PILOT/n) for n in ('RUN_STARTED.json','EXECUTION_BINDING.json','RETURN.json') if (PILOT/n).exists()]
 payloads=[ref(p) for name in ('raw','attempts','normalized') for p in sorted((PILOT/name).rglob('*')) if p.is_file()]
 return dict(registry_roots=roots,registry_hits=hits,same_scope_markers=scope_copies,canonical_pilot_markers=markers,canonical_pilot_payloads=payloads,scope_consumed=bool(hits or markers or scope_copies or payloads),registry_is_distributed_lock=False)
def assert_unconsumed(inventory):
 if inventory['scope_consumed']:raise ValueError('RECOVERY_REQUIRED_NO_RERUN: existing registry/run/raw/attempt evidence')
