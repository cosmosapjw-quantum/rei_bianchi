"""Run bounded implementation checks. This never certifies native MPI/Arb or HH."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SUITES = {
    'native_cache': 'STATIC_SOURCE_AND_EXACT_RATIONAL_EXPRESSION_MODEL',
    'backend_build': 'PURE_BUILD_PLAN_AND_PRIOR_INPUT_LOCK',
    'mpi_fortran': 'ACTUAL_GCC_C_PROCESS_BRIDGE_NO_FORTRAN_OR_MPI',
    'host_plan': 'HOST_PLANNING_AND_SYNTHETIC_LAUNCHER_TEST_DOUBLES',
    'executor': 'REAL_LOCAL_SUBPROCESS_EXACT_PAYLOAD_AND_FAILURE_CHECKS',
}


def run_one(item):
    name, layer = item
    cmd = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_*.py', '-v']
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=HERE/name, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                            capture_output=True, text=True, timeout=90)
    log = result.stdout + result.stderr
    path = HERE/'evidence'/('FINAL_'+name+'.log')
    path.write_text(log)
    match = re.search(r'Ran (\d+) tests? in', log)
    return {'suite': name, 'layer': layer, 'argv': cmd, 'exit_code': result.returncode,
            'tests': int(match.group(1)) if match else None, 'wall_seconds': time.monotonic()-start,
            'log': str(path.relative_to(HERE)), 'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    (HERE/'evidence').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(run_one, SUITES.items()))
    passed = all(x['exit_code'] == 0 and x['tests'] for x in results)
    source_hashes = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(HERE.rglob('*')) if p.is_file() and p.suffix in ('.py', '.cpp', '.hpp', '.c', '.h', '.f90', '.sh')
                     and not (p.is_relative_to(HERE/'review') and len(p.relative_to(HERE/'review').parts)>1)}
    report = {'schema': 'WU088_NCP64_LOCAL_VERIFICATION_V1', 'implementation_tests_passed': passed,
              'test_count': sum(x['tests'] or 0 for x in results), 'suites': results,
              'source_sha256': source_hashes, 'python': sys.version, 'platform': platform.platform(),
              'available_tools': {x: shutil.which(x) for x in ('gcc', 'g++', 'gfortran', 'mpifort', 'mpirun', 'pkg-config')},
              'native_cache_execution_verified': False, 'Fortran_compiled': False, 'MPI_executed': False,
              'NCP_measured': False, 'actual_HH_runs': 0, 'scientific_promotion': False}
    (HERE/'evidence/FINAL_VERIFICATION.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'implementation_tests_passed': passed, 'test_count': report['test_count'],
                      'suites': [{'suite': x['suite'], 'tests': x['tests'], 'exit_code': x['exit_code']} for x in results]}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
