from pathlib import Path
import json,hashlib,os,sys,subprocess,datetime,time
R=Path(__file__).resolve().parent;E=R/'evidence';OLD=R.parent;REPO=OLD/'w3/recovered/repo';L=REPO/'research/r31ao_unequal_ladder';REVIEW=R/'review/WU088_NCP_PREP_R2_REVIEW_20261003_v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def write(name,value):
 with (E/name).open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def run(label,args,cwd=None,timeout=300,env=None):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
 with (E/(label+'.stdout.log')).open('xb') as so,(E/(label+'.stderr.log')).open('xb') as se:
  try: cp=subprocess.run(args,cwd=cwd,env=env,stdout=so,stderr=se,timeout=timeout);code=cp.returncode
  except subprocess.TimeoutExpired:code=124
 row=dict(start_utc=start,command=args,cwd=str(cwd) if cwd else None,exit_status=code,elapsed_seconds=time.monotonic()-t,stdout=label+'.stdout.log',stderr=label+'.stderr.log')
 with (E/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps(row),flush=True);return code
def snapshot():
 out=[]
 for root in (OLD/'runtime_work',OLD/'evidence',REPO,OLD/'prep_r1'):
  for p in sorted(root.rglob('*')):
   if p.is_symlink():out.append(dict(path=str(p),kind='symlink',target=os.readlink(p),mtime_ns=p.lstat().st_mtime_ns,mode=p.lstat().st_mode&0o777))
   elif p.is_file():out.append(dict(path=str(p),kind='file',bytes=p.stat().st_size,sha256=sha(p),mtime_ns=p.stat().st_mtime_ns,mode=p.stat().st_mode&0o777))
 return out
if __name__=='__main__':
 write('PRESERVATION_BEFORE.json',snapshot())
 assert run('candidate_payload_verify',['/usr/bin/python3','-B',str(REVIEW/'verify_delivery.py')])==0
 assert run('candidate_12_tests',['/usr/bin/python3','-B','-m','unittest','test_release_extract','-v'],cwd=REVIEW)==0
