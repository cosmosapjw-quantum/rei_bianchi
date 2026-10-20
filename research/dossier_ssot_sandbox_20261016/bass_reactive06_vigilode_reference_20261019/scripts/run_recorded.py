"""Run one declared command and retain timing, status and exact output hashes."""
import argparse,datetime,hashlib,json,os,subprocess,time
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--cwd',type=Path,required=True)
p.add_argument('--receipt',type=Path,required=True)
p.add_argument('--timeout',type=float,default=600)
p.add_argument('command',nargs=argparse.REMAINDER)
a=p.parse_args();command=a.command[1:] if a.command[:1]==['--'] else a.command
assert command and not a.receipt.exists()
a.receipt.parent.mkdir(parents=True,exist_ok=True)
start=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.perf_counter()
out=a.receipt.with_suffix('.stdout.log');err=a.receipt.with_suffix('.stderr.log')
record={'status':'RUNNING','command':command,'cwd':str(a.cwd.resolve()),'started_utc':start,'timeout_s':a.timeout}
a.receipt.write_text(json.dumps(record,indent=2)+'\n')
with out.open('xb') as stdout,err.open('xb') as stderr:
    try:
        done=subprocess.run(command,cwd=a.cwd,stdout=stdout,stderr=stderr,timeout=a.timeout)
        code=done.returncode;status='COMPLETED' if code==0 else 'COMMAND_FAILED'
    except subprocess.TimeoutExpired:
        code=None;status='WORK_BUDGET_TIMEOUT'
record.update({'status':status,'exit_code':code,'wall_s':time.perf_counter()-clock,
 'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'stdout':str(out),'stderr':str(err),'stdout_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'stderr_sha256':hashlib.sha256(err.read_bytes()).hexdigest()})
a.receipt.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
raise SystemExit(code if code is not None else 124)
