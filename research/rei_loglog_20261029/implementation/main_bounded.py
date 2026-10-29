"""Single root-authorized structural validation; no rendering or IVP."""
import argparse
import json
import os
from pathlib import Path
import resource
import signal
import time

for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable] = '1'

parser = argparse.ArgumentParser()
parser.add_argument('--go', required=True, choices=['ROOT_GO_620'])
parser.add_argument('--data', required=True)
parser.add_argument('--old-metadata', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()
output = Path(args.out)
output.mkdir(parents=True, exist_ok=True)
proposal = {'original_cpu_ceiling_s':600., 'temporary_cpu_ceiling_s':620.,
            'starting_cumulative_cpu_s':608.750604, 'reservation_cpu_s':4.,
            'validation_target_cpu_s':3.5, 'receipt_tail_reserve_s':.5,
            'wall_ceiling_s':30, 'memory_bytes':536870912, 'threads':1,
            'automatic_retry':False, 'ivp_calls_permitted':0, 'rendering_permitted':False,
            'restoration':'Controller restores original 600 ceiling after final external-rusage debit; retain over-baseline balance.'}
with (output/'ATTEMPT_STARTED.json').open('x') as handle:
    json.dump(proposal, handle, indent=2)
resource.setrlimit(resource.RLIMIT_AS, (536870912,536870912))
resource.setrlimit(resource.RLIMIT_CPU, (4,4))
def limit_reached(signum, frame):
    raise TimeoutError('bounded validation execution ceiling reached')
signal.signal(signal.SIGALRM,limit_reached)
signal.signal(signal.SIGPROF,limit_reached)
signal.alarm(30)
usage = resource.getrusage(resource.RUSAGE_SELF)
signal.setitimer(signal.ITIMER_PROF, max(.001,3.4-usage.ru_utime-usage.ru_stime))
started = time.monotonic()
status, error = 'FAILED', None
try:
    from validation_driver import validate
    validate(args.data,args.old_metadata,output)
    status = 'STRUCTURAL_VALIDATION_PASS_PENDING_INDEPENDENT_REVIEW'
except BaseException as exc:
    error = type(exc).__name__+': '+str(exc)
finally:
    signal.alarm(0)
    signal.setitimer(signal.ITIMER_PROF,0)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    cpu = usage.ru_utime+usage.ru_stime
    if cpu > 3.5:
        status = 'CEILING_EXCEEDED'
    receipt = dict(proposal,status=status,error=error,cpu_before_receipt_s=cpu,
                   wall_before_receipt_s=time.monotonic()-started,
                   targeted_repair='start_audit physical23 assertion; audit physical[:17] only',
                   final_debit='Controller external rusage includes receipt tail; no budget reset or transfer')
    (output/'ATTEMPT_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if status != 'STRUCTURAL_VALIDATION_PASS_PENDING_INDEPENDENT_REVIEW':
    raise SystemExit(1)
