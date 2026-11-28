"""Append-only measured changed-input execution, including failed launches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parents[1]


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--kind', required=True, choices=['source_build', 'implementation', 'independent', 'plot'])
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.attempt.replace('_', '').isalnum():
        parser.error('SIMPLE_ATTEMPT_IDENTIFIER_REQUIRED')
    cmd = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not cmd:
        parser.error('EXPLICIT_COMMAND_REQUIRED_BEFORE_ATTEMPT_CREATION')
    dest = BASE / 'raw' / args.attempt
    if dest.exists():
        raise ValueError('ATTEMPT_ALREADY_EXISTS_NO_REPLAY')
    dest.mkdir(parents=True)
    hashes = {str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in BASE.rglob('*.py') if '__pycache__' not in p.parts}
    request = {'command': cmd, 'cwd': str(BASE), 'code_sha256': hashes,
               'execution_class': args.kind, 'python': platform.python_version(),
               'cpu_cap_s': 30, 'wall_cap_s': 120, 'memory_MiB': 512, 'workers': 1, 'threads': 1}
    (dest / 'REQUEST.json').write_text(json.dumps(request, indent=2) + '\n')
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    own_start = time.process_time()
    start = time.monotonic()
    env = dict(os.environ)
    env.update({'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'MPLCONFIGDIR': '/tmp/wu_r4_mpl'})
    child = None
    code = None
    timed_out = False
    launch_error = None
    with (dest / 'stdout.txt').open('w') as out, (dest / 'stderr.txt').open('w') as err:
        try:
            child = subprocess.Popen(cmd, cwd=BASE, env=env, stdout=out, stderr=err, preexec_fn=limits)
            try:
                code = child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                timed_out = True
                child.kill()
                code = child.wait()
        except (OSError, subprocess.SubprocessError) as exc:
            launch_error = {'type': type(exc).__name__, 'message': str(exc)}
            err.write(json.dumps(launch_error) + '\n')
        finally:
            if child is not None and child.poll() is None:
                child.kill()
                code = child.wait()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {**request, 'exit_code': code, 'child_spawned': child is not None,
               'launch_error': launch_error, 'timed_out': timed_out,
               'cpu_s': after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
               'cpu_measurement_scope': 'RUSAGE_CHILDREN delta for this attempt, including attempted launch; coordinator separately measured',
               'coordinator_CPU_s': time.process_time() - own_start,
               'wall_s': time.monotonic() - start, 'max_RSS_KiB': after.ru_maxrss,
               'source_formula_sample_count': 'actual stdout/result records; never assumed zero',
               'physical_rate_admissions': 0, 'new_IVP': 0, 'historical_science_replays': 0,
               'network_tool_and_prior_costs': 'UNMEASURED_NOT_ZERO',
               'stdout_sha256': hashlib.sha256((dest / 'stdout.txt').read_bytes()).hexdigest(),
               'stderr_sha256': hashlib.sha256((dest / 'stderr.txt').read_bytes()).hexdigest()}
    (dest / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('exit_code', 'cpu_s', 'wall_s', 'max_RSS_KiB', 'timed_out', 'launch_error')}))
    print((dest / 'stdout.txt').read_text())
    if code != 0 or launch_error:
        print((dest / 'stderr.txt').read_text(), file=sys.stderr)
    raise SystemExit(0 if code == 0 and launch_error is None else 1)


if __name__ == '__main__':
    main()
