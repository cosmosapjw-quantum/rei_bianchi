"""Durable two-attempt preparation envelope; no native owner allocation."""
import datetime
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

unit=Path(__file__).resolve().parent
root=unit.parents[1]
checkpoint=unit/'EXECUTION_CHECKPOINT.json'
state=json.loads(checkpoint.read_text())
assert state['test_commands_used'] < 2
assert state['test_wall_used'] < 360
attempt=state['test_commands_used']+1
directory=unit/f'focused_attempt_{attempt:02d}'
directory.mkdir()
argv=['/usr/bin/timeout','--signal=TERM','--kill-after=2s','178s',
      'cargo','test','--manifest-path','rust/rei_microphysics/Cargo.toml',
      '--target-dir','research/flrw_native_bounded_observer_20261016/target',
      '-j2','--test','axbi_bounded_stage_observer','--','--test-threads=1','--nocapture']
state.update(test_commands_used=attempt,status='TARGETED_COMMAND_RUNNING',active=True,
             active_allowance_seconds=180)
checkpoint.write_text(json.dumps(state,indent=2)+'\n')
start=time.time()
before=resource.getrusage(resource.RUSAGE_CHILDREN)
started=time.perf_counter()
with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
    process=subprocess.Popen(argv,cwd=root,stdout=stdout,stderr=stderr,start_new_session=True,
                             env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    try:
        code=process.wait(timeout=180)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGKILL)
        code=process.wait()
elapsed=time.perf_counter()-started
after=resource.getrusage(resource.RUSAGE_CHILDREN)
receipt=dict(kind='SYNTHETIC_CHANGED_SEAM_PREPARATION_ONLY',argv=argv,cwd=str(root),
    exit_code=code,normalized_shell_exit=code if code>=0 else 128-code,
    start_epoch=start,end_epoch=time.time(),wall_seconds=elapsed,
    user_cpu_seconds=after.ru_utime-before.ru_utime,
    system_cpu_seconds=after.ru_stime-before.ru_stime,
    peak_rss_kib_linux=after.ru_maxrss,attempt=attempt,per_attempt_wall_cap_seconds=180,
    aggregate_wall_cap_seconds=360,native_owner_launches=0,
    requested_model='gpt-6.1-sol/high',observed_model='NOT_INDEPENDENTLY_OBSERVED')
(directory/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
state.update(test_wall_used=state['test_wall_used']+elapsed,
             active=False,active_allowance_seconds=0,status='TARGETED_COMMAND_COMPLETE')
checkpoint.write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(0 if code==0 else 1)
