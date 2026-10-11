"""One frozen production interval with an external wall limit and raw capture."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BACKUP = Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_CR_FIRST_BUILD_RECEIPT_20261010_f9135ec')
CRATE = ROOT / 'rust/rei_microphysics'
sys.path.insert(0, str(CRATE / 'python'))
from conditional_build import validate_build_receipt
from source_bound_interval import preflight
import numpy
import scipy

if (HERE / 'PRELAUNCH.json').exists():
    raise SystemExit('ONE_EXECUTION_ALREADY_STARTED')
binary = BACKUP / 'target/release/axisym_conditional'
receipt = BACKUP / 'BUILD_RECEIPT.json'
build = validate_build_receipt(CRATE, binary, receipt)
inputs = preflight(ROOT / 'research/physical_provider_20261010')
command = [sys.executable, 'rust/rei_microphysics/python/source_bound_interval.py',
           '--binary', str(binary), '--build-receipt', str(receipt),
           '--output', str(HERE / 'output')]
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
prelaunch = {
    'task': 'P01-CERTIFIED-WARM-EXEC01',
    'current_branch': git('branch', '--show-current'),
    'current_commit': git('rev-parse', 'HEAD'),
    'current_tree': git('rev-parse', 'HEAD^{tree}'),
    'status_at_prelaunch': git('status', '--short'),
    'original_worktree_touched': False,
    'build_identity': build,
    'build_receipt_sha256': hashlib.sha256(receipt.read_bytes()).hexdigest(),
    'reference_json_sha256': hashlib.sha256((ROOT / 'research/physical_provider_20261010/evidence/extended.json').read_bytes()).hexdigest(),
    'input_sha256': inputs['identities'],
    'environment': {'python': sys.version, 'numpy': numpy.__version__,
                    'scipy': scipy.__version__, 'platform': platform.platform(),
                    'OMP_NUM_THREADS': os.environ.get('OMP_NUM_THREADS'),
                    'OPENBLAS_NUM_THREADS': os.environ.get('OPENBLAS_NUM_THREADS')},
    'command': command, 'cwd': str(ROOT),
    'harness': 'HARNESS_UNAVAILABLE: local AGENTS.md, tier policy and bounded RULES absent; parent frozen contract applied',
    'maxima': {'production_intervals': 1, 'native_rhs_calls': 10000, 'command_wall_s': 600, 'repair_rounds_used': 0},
    'scientific_admission': 'HOLD'
}
(HERE / 'PRELAUNCH.json').write_text(json.dumps(prelaunch, indent=2) + '\n')
start = time.monotonic()
before = resource.getrusage(resource.RUSAGE_CHILDREN)
timed_out = False
with (HERE / 'stdout.log').open('wb') as stdout, (HERE / 'stderr.log').open('wb') as stderr:
    proc = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                            start_new_session=True)
    try:
        code = proc.wait(timeout=600)
    except subprocess.TimeoutExpired:
        import signal
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        code = proc.wait()
after = resource.getrusage(resource.RUSAGE_CHILDREN)
execution = {'task': prelaunch['task'], 'command': command, 'cwd': str(ROOT),
             'exit_code': code, 'timed_out': timed_out,
             'wall_s': time.monotonic()-start,
             'user_cpu_s': after.ru_utime-before.ru_utime,
             'system_cpu_s': after.ru_stime-before.ru_stime,
             'solver_attempts': 1, 'repair_rounds_used': 0,
             'scientific_admission': 'HOLD'}
for name in ('stdout.log', 'stderr.log'):
    execution[name + '_sha256'] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
(HERE / 'EXECUTION.json').write_text(json.dumps(execution, indent=2) + '\n')
print(json.dumps(execution, indent=2))
raise SystemExit(code if code >= 0 else 1)
