"""One authorized launcher repair: wait4 final child CPU, no automatic retry."""
import json
import os
from pathlib import Path
import signal
import sys
import time

root = Path(__file__).resolve().parents[3]
output = root/'research/rei_loglog_20261029/outputs/main_structural_20261029'
output.mkdir(parents=True,exist_ok=True)
(output/'FAILED_TIME_LAUNCHER.json').write_text(json.dumps({
    'command_prefix':'/usr/bin/time -v', 'exit_code':127,
    'error':'/bin/bash: line 1: /usr/bin/time: No such file or directory',
    'scientific_child_started':False, 'shell_cpu_cost':'UNKNOWN; retained, not zeroed',
    'repair_authorization':'Root explicit targeted launcher repair; same 4 CPU reservation'})+'\n')
command = [sys.executable,str(Path(__file__).with_name('main_bounded.py')),
    '--go','ROOT_GO_620','--data',str(root/'research/rei_figure_set_20261029/outputs/plot_data.json'),
    '--old-metadata',str(root/'research/rei_figure_set_20261029/figures/FIGURE_METADATA.json'),
    '--out',str(output)]
started = time.monotonic()
pid = os.fork()
if pid == 0:
    os.execv(sys.executable,command)
def expired(signum,frame):
    os.kill(pid,signal.SIGKILL)
signal.signal(signal.SIGALRM,expired)
signal.alarm(35)
_, status, usage = os.wait4(pid,0)
signal.alarm(0)
receipt = {'exit_code':os.waitstatus_to_exitcode(status),'child_user_cpu_s':usage.ru_utime,
    'child_system_cpu_s':usage.ru_stime,'child_final_cpu_s':usage.ru_utime+usage.ru_stime,
    'child_wall_s':time.monotonic()-started,'max_rss_kib':usage.ru_maxrss,
    'starting_cumulative_cpu_s':608.750604,'temporary_ceiling_cpu_s':620.,
    'restored_policy_ceiling_cpu_s':600.,'reservation_cpu_s':4.,
    'unknown_historical_costs':'Preserved; failed initial shell launcher cost remains unknown',
    'automatic_retry':False,'scope':'structural fixed-field validation; no rendering or IVP'}
(output/'FINAL_RUSAGE.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(receipt['exit_code'])
