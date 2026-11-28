"""Bounded synthetic descendant-survival probe; no science commands."""
from pathlib import Path
import json
import os
import signal
import sys
import tempfile
import time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from host_guard.run_guarded import run_guarded

with tempfile.TemporaryDirectory(prefix='review_guard_',dir=Path(__file__).resolve().parent) as scratch:
    sentinel=Path(scratch)/'descendant_finished'
    child_code='import time;from pathlib import Path;time.sleep(.6);Path('+repr(str(sentinel))+').write_text("finished_after_guard")'
    parent_code='import subprocess,sys,os;print(os.getpid(),flush=True);subprocess.Popen([sys.executable,"-B","-c",'+repr(child_code)+'])'
    result=run_guarded([sys.executable,'-B','-c',parent_code],wall_seconds=.2,memory_mib=128)
    leader=int(result['stdout'].strip())
    alive_after_return=False
    try:
        os.killpg(leader,0)
        alive_after_return=True
    except ProcessLookupError:
        pass
    time.sleep(.8)
    finished_after_return=sentinel.exists()
    try:os.killpg(leader,signal.SIGKILL)
    except ProcessLookupError:pass
    print(json.dumps({'scope':'BOUNDED_SYNTHETIC_ONLY','guard_status':result['status'],
      'guard_wall_seconds':result['wall_seconds'],'wall_budget_seconds':.2,
      'process_group_alive_after_guard_return':alive_after_return,
      'descendant_completed_after_wall_budget':finished_after_return,
      'descendant_did_not_escape_process_group':True},indent=2))
