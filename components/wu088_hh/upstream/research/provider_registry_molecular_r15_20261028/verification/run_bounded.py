#!/usr/bin/env python3
"""R15 base-attempt envelope; measured child CPU includes imports and serialization."""
import argparse
import datetime
import decimal
import hashlib
import json
import os
import pathlib
import platform
import resource
import subprocess
import sys
import time

sys.set_int_max_str_digits(6000)
p = argparse.ArgumentParser()
p.add_argument('lane', choices=['primary', 'reference', 'renderer'])
p.add_argument('--source-commit', required=True)
a = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
raw = root / ('figures' if a.lane == 'renderer' else 'raw')
raw.mkdir(exist_ok=True)
manifest_path = root / 'verification/FROZEN_FILES.json'
manifest_bytes = manifest_path.read_bytes()
manifest = json.loads(manifest_bytes)
for item in manifest['files']:
    body = (root / item['path']).read_bytes()
    if len(body) != item['bytes'] or hashlib.sha256(body).hexdigest() != item['sha256']:
        raise RuntimeError('Frozen input mismatch: ' + item['path'])
contract = json.loads((root / 'CONTRACT.json').read_text())
budget = contract['execution_budget'][a.lane]
cpu_limit = budget.get('CPU_s_per_attempt', budget.get('CPU_s'))
wall_limit = budget.get('wall_s_per_attempt', budget.get('wall_s'))
name = a.lane.upper()
attempt_path = raw / (name + '_ATTEMPT.json')
output_path = raw / (name + '_RESULTS.json')
if attempt_path.exists() or output_path.exists():
    raise RuntimeError('Base attempt already recorded. Preserve it; a diagnosed repair requires an explicit amendment.')
dependent = None
if a.lane == 'reference':
    source = raw / 'PRIMARY_RESULTS.json'
    body = source.read_bytes()
    dependent = {'path': str(source.relative_to(root)), 'bytes': len(body),
                 'sha256': hashlib.sha256(body).hexdigest()}
elif a.lane == 'renderer':
    dependent = []
    for filename in ('PRIMARY_RESULTS.json', 'REFERENCE_RESULTS.json'):
        source = root / 'raw' / filename
        body = source.read_bytes()
        dependent.append({'path': str(source.relative_to(root)), 'bytes': len(body),
                          'sha256': hashlib.sha256(body).hexdigest()})
script = root / 'figures/render_saved.py' if a.lane == 'renderer' else root / 'verification' / ('run_' + a.lane + '.py')
command = [sys.executable, str(script),
           '--root', str(root), '--output', str(output_path)]
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
started = now()
record = {'lane': a.lane, 'attempt': 1, 'source_commit': a.source_commit,
          'command': command, 'started_utc': started,
          'CPU_limit_s': cpu_limit,
          'wall_limit_s': wall_limit,
          'memory_limit_bytes': budget['memory_bytes'],
          'frozen_manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
          'frozen_file_count': len(manifest['files']),
          'saved_primary_identity': dependent}
with attempt_path.open('x') as out:
    json.dump(record, out, ensure_ascii=False, indent=2)
    out.write('\n')
ledger_path = root / 'EXECUTION_LEDGER.json'
ledger = json.loads(ledger_path.read_text())
assert ledger['remaining_base'][a.lane] == 1
ledger['remaining_base'][a.lane] = 0
ledger['actual_runs'][a.lane] += 1
ledger['events'].append({**record, 'status': 'STARTED'})
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')

def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    resource.setrlimit(resource.RLIMIT_AS, (budget['memory_bytes'], budget['memory_bytes']))

env = dict(os.environ)
env['PYTHONDONTWRITEBYTECODE'] = '1'
env['OMP_NUM_THREADS'] = '1'
env['OPENBLAS_NUM_THREADS'] = '1'
if a.lane == 'renderer':
    env['MPLCONFIGDIR'] = '/tmp/wu_r15_matplotlib_' + str(os.getpid())
before = resource.getrusage(resource.RUSAGE_CHILDREN)
clock = time.monotonic()
timeout = False
proc = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, preexec_fn=limits)
try:
    out, err = proc.communicate(timeout=wall_limit)
except subprocess.TimeoutExpired:
    timeout = True
    proc.kill()
    out, err = proc.communicate()
wall = time.monotonic() - clock
after = resource.getrusage(resource.RUSAGE_CHILDREN)
(raw / (name + '_STDOUT.txt')).write_bytes(out)
(raw / (name + '_STDERR.txt')).write_bytes(err)
user_cpu = decimal.Decimal(str(after.ru_utime)) - decimal.Decimal(str(before.ru_utime))
system_cpu = decimal.Decimal(str(after.ru_stime)) - decimal.Decimal(str(before.ru_stime))
result = {**record, 'schema': 'WU_R15_ACTUAL_PROCESS_V1', 'finished_utc': now(),
          'returncode': proc.returncode, 'timeout': timeout,
          'OS_user_CPU_s': str(user_cpu), 'OS_system_CPU_s': str(system_cpu),
          'OS_CPU_s': str(user_cpu + system_cpu), 'wall_s': wall,
          'max_rss_KiB': after.ru_maxrss, 'includes_imports_and_serialization': True,
          'python': sys.version, 'platform': platform.platform(),
          'old_science_replay': 0, 'new_ODE_runs': 0,
          'output_present': output_path.is_file()}
if output_path.is_file():
    body = output_path.read_bytes()
    result['output_identity'] = {'path': str(output_path.relative_to(root)),
                                 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
(raw / (name + '_PROCESS.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
ledger = json.loads(ledger_path.read_text())
ledger['events'][-1] = {**result, 'status': 'FINISHED'}
cpu_field = 'new_render_CPU_s' if a.lane == 'renderer' else 'new_scientific_CPU_s'
ledger[cpu_field] = str(decimal.Decimal(ledger.get(cpu_field, '0')) + user_cpu + system_cpu)
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
sys.exit(0 if proc.returncode == 0 and not timeout else 1)
