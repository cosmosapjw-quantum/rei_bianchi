"""Invoke the approved original blueprint once; observe processes, never dispatch."""
from pathlib import Path
import sys,json,os,time,datetime,subprocess
TASK=Path(__file__).resolve().parent;E=TASK/'evidence';PREP=TASK.parent/'fd2_prep_20261004_v2'
sys.path.insert(0,str(PREP))
from support import c,ref,write
from diagnostic_adapter import unconsumed,authorization_check
def stamp():return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic_ns=time.monotonic_ns())
def main():
 proposal=c.load(PREP/'evidence/FD2_CANDIDATE_PROPOSAL.json');c.check_seal(proposal,'proposal_sha256')
 authorization=c.load(E/'AUTHORIZATION_RECORD.json');authorization_check(proposal,E/'AUTHORIZATION_RECORD.json',authorization['authorization_sha256']);unconsumed(proposal)
 command=c.load(E/'EXACT_EXECUTION_COMMAND.json')['command'];assert command==proposal['future_execution_blueprint'][:-3]+[proposal['proposal_sha256'],str(E/'AUTHORIZATION_RECORD.json'),authorization['authorization_sha256']]
 write(E/'COORDINATOR_ATTEMPT_STARTED.json',dict(start=stamp(),command=command,max_original_blueprint_attempts=1,scope_consumption_delegated_to_original_adapter=True,automatic_retry=False))
 write(E/'COORDINATOR_SOURCE_IDENTITY.json',dict(invocation_coordinator=ref(Path(__file__)),preflight_coordinator=ref(TASK/'preflight_authorization.py'),original_entrypoint_and_adapter_unmodified=True,new_dispatcher=False))
 observed={};start=stamp()
 with (E/'original_unit.stdout.log').open('xb') as stdout,(E/'original_unit.stderr.log').open('xb') as stderr:
  process=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  while process.poll() is None:
   for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
     argv=(p/'cmdline').read_bytes().split(b'\0')
     if not argv or argv[0].decode(errors='replace')!=proposal['binary']['path']:continue
     key=p.name;now=stamp()
     if key not in observed:observed[key]=dict(pid=int(key),first_observed=now,argv=[x.decode(errors='replace') for x in argv if x],proc_stat=(p/'stat').read_text(),proc_status=(p/'status').read_text(),membership=(p/'cgroup').read_text(),limits=(p/'limits').read_text(),namespace={n:os.readlink(p/'ns'/n) for n in ('mnt','cgroup','pid','user')})
     observed[key]['last_observed']=now
    except OSError:pass
   time.sleep(.005)
  rc=process.wait()
 end=stamp();row=dict(command=command,start=start,end=end,elapsed_seconds=(end['monotonic_ns']-start['monotonic_ns'])/1e9,launcher_pid=process.pid,exit_status=rc,stdout=ref(E/'original_unit.stdout.log'),stderr=ref(E/'original_unit.stderr.log'),original_blueprint_attempts=1,automatic_retry=False)
 write(E/'EXECUTION_COMMAND_RETURN.json',row)
 write(E/'NATIVE_PROCESS_OBSERVATIONS.json',dict(processes=list(observed.values()),observer_only=True,requested_sampling_delay_seconds=.005, actual_sampling_interval_includes_proc_scan=True,timing_is_first_and_last_observed_not_exact_start_stop=True,missed_short_lived_process_is_not_absence_of_execution=True))
 with (E/'COMMANDS.jsonl').open('x') as log:
  log.write(json.dumps(dict(command=['python3','-B',str(TASK/'preflight_authorization.py')],exit_status=0,science_calls=0))+'\n');log.write(json.dumps(row)+'\n')
 print(json.dumps(row));return rc
if __name__=='__main__':raise SystemExit(main())
