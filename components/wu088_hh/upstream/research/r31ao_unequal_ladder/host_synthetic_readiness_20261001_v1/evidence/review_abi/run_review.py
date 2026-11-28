"""Run focused ABI review under per-process 20s/1024MiB hard guards."""
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGETS = ('abi_witness.py', 'test_abi_witness.py', 'TASK_CONTRACT.json')


def hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in TARGETS}


def restrict():
    resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))


def main():
    before = hashes()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    results = []
    for label, cmd in [('focused_suite', [sys.executable, '-m', 'unittest', '-v', 'test_abi_witness.py']),
                       ('independent_check', [sys.executable, str(HERE/'independent_check.py')])]:
        start = time.monotonic()
        p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=20, preexec_fn=restrict)
        (HERE/(label+'.log')).write_text(p.stdout + p.stderr)
        results.append({'label': label, 'command': cmd, 'cwd': str(ROOT), 'exit_code': p.returncode,
                        'elapsed_seconds': time.monotonic()-start,
                        'hard_wall_timeout_seconds': 20, 'address_space_bytes': 1024*1024*1024})
        if p.returncode:
            break
    after = hashes()
    result = {'source_sha256_before': before, 'source_sha256_after': after,
              'source_unchanged': before == after, 'commands': results,
              'status': 'PASS' if before == after and len(results) == 2 and all(x['exit_code'] == 0 for x in results) else 'FAIL'}
    (HERE/'EXECUTION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
