#!/usr/bin/env python3
"""Write a pre-run record, execute one immutable run directory, record outputs."""
import argparse
import datetime
import hashlib
import json
import pathlib
import resource
import subprocess
import time

ap = argparse.ArgumentParser()
ap.add_argument('--run-id', required=True)
ap.add_argument('--source', type=pathlib.Path, required=True)
ap.add_argument('--parent15', type=pathlib.Path, required=True)
ap.add_argument('--parent16', type=pathlib.Path, required=True)
ap.add_argument('--reason', required=True)
args = ap.parse_args()
run = pathlib.Path(__file__).resolve().parent / args.run_id
run.mkdir(exist_ok=False)
cmd = ['python3', str(args.source.resolve()), '--parent15', str(args.parent15.resolve()),
       '--parent16', str(args.parent16.resolve()), '--output', str(run/'results')]
identity = lambda p: {'path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
pre = {'schema':'WU088_HH_PHYS17_PRE_RUN_V1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'command':cmd,'source':identity(args.source.resolve()),'reason':args.reason,
       'budget':{'timeout_seconds':20,'expected_peak_rss_MiB_below':128,'native_source_root_history_calls':0},
       'questions':['Do P2 correlated derivative transfer and P4 finite-temperature readout close uniformly?',
                    'What are the signs and widths of d_lambda,d_b and DeltaT_lambda,DeltaT_b?',
                    'Do the C2 density bridge and exact photon derivative graph preserve shared-stage correlations?'],
       'acceptance':'Report exact outward intervals and observed sign margins; independently review source correspondence and arithmetic.'}
(run/'PRE_RUN.json').write_text(json.dumps(pre,indent=2)+'\n')
tic = time.perf_counter()
try:
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=20)
    code, stdout, stderr = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    code, stdout, stderr = 124, e.stdout or '', e.stderr or ''
    if isinstance(stdout,bytes): stdout=stdout.decode(errors='replace')
    if isinstance(stderr,bytes): stderr=stderr.decode(errors='replace')
    stderr += '\nTIMEOUT after 20 seconds\n'
elapsed = time.perf_counter()-tic
(run/'STDOUT.txt').write_text(stdout)
(run/'STDERR.txt').write_text(stderr)
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
record = {'schema':'WU088_HH_PHYS17_RUN_RECORD_V1','command':cmd,'exit_code':code,
          'elapsed_seconds':elapsed,'cpu_seconds':usage.ru_utime+usage.ru_stime,'peak_rss_kib':usage.ru_maxrss,
          'source':pre['source'],'pre_run':identity(run/'PRE_RUN.json'),
          'outputs':[identity(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='PRE_RUN.json'],
          'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
result = run/'results/PARAMETER_RESPONSE_RESULTS.json'
if result.exists(): record['input_identities'] = json.loads(result.read_text())['input_identities']
(run/'RUN_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'run':str(run),'exit_code':code,'elapsed_seconds':elapsed,'peak_rss_kib':usage.ru_maxrss},indent=2))
print(stdout if code == 0 else stderr)
raise SystemExit(code)
