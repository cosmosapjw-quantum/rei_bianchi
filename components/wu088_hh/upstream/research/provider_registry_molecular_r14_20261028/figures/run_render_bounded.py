#!/usr/bin/env python3
"""One bounded saved-output rendering process; no scientific rerun."""
from pathlib import Path
import datetime, decimal, hashlib, json, os, resource, subprocess, sys, time

root = Path(__file__).resolve().parents[1]
folder = root / 'figures'
source = folder / 'render_saved.py'
command = [sys.executable, str(source), '--root', str(root)]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
attempt = {'schema': 'WU_R14_RENDER_ATTEMPT_V1', 'attempt': 1,
           'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'command': command, 'started_utc': started,
           'CPU_limit_s': 10, 'wall_limit_s': 30, 'memory_limit_bytes': 1073741824,
           'new_science_runs': 0, 'new_ODE_runs': 0}
with (folder / 'RENDER_ATTEMPT.json').open('x') as handle:
    handle.write(json.dumps(attempt, indent=2) + '\n')

def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))

env = dict(os.environ)
env.update(PYTHONDONTWRITEBYTECODE='1', MPLCONFIGDIR='/tmp/wu_r14_matplotlib',
           OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
before = resource.getrusage(resource.RUSAGE_CHILDREN)
t = time.monotonic()
process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, preexec_fn=limits)
timeout = False
try:
    stdout, stderr = process.communicate(timeout=30)
except subprocess.TimeoutExpired:
    timeout = True
    process.kill()
    stdout, stderr = process.communicate()
wall = time.monotonic() - t
after = resource.getrusage(resource.RUSAGE_CHILDREN)
user = decimal.Decimal(str(after.ru_utime)) - decimal.Decimal(str(before.ru_utime))
system = decimal.Decimal(str(after.ru_stime)) - decimal.Decimal(str(before.ru_stime))
(folder / 'RENDER_STDOUT.txt').write_bytes(stdout)
(folder / 'RENDER_STDERR.txt').write_bytes(stderr)
result = dict(attempt, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              returncode=process.returncode, timeout=timeout,
              OS_user_CPU_s=str(user), OS_system_CPU_s=str(system),
              OS_CPU_s=str(user + system), wall_s=wall, max_rss_KiB=after.ru_maxrss,
              includes_imports_and_serialization=True,
              source_results_recomputed=False)
(folder / 'RENDER_PROCESS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
sys.exit(0 if process.returncode == 0 and not timeout else 1)
