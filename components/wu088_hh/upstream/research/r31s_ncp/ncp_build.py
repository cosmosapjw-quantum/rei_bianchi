#!/usr/bin/env python3
"""Fresh, host-bound native build outside the repository; no provider promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
FLAGS = ('-O3', '-std=c++17', '-fPIC', '-shared', '-fno-fast-math',
         '-ffp-contract=off', '-fopenmp')
SOURCES = ('r31a/hybrid12_wide_h_v2.cpp', 'r31a/continuation.hpp',
           'radial/analytic_wide.cpp')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trusted_env(source: dict[str, str]) -> dict[str, str]:
    env = {k: v for k, v in source.items() if k not in ('LD_PRELOAD', 'LD_LIBRARY_PATH')}
    env['OMP_NUM_THREADS'] = '1'
    env['OPENBLAS_NUM_THREADS'] = '1'
    env['MKL_NUM_THREADS'] = '1'
    return env


def validate_probe(report: dict) -> int:
    if report.get('schema') != 'WU088_NCP_READ_ONLY_PROBE_V1':
        raise ValueError('unsupported probe schema')
    if report.get('status') != 'PROBED_NOT_BENCHMARKED' or report.get('warnings'):
        raise ValueError('probe requires cgroup inspection')
    allowed = report.get('allowed_logical_cpus')
    budget = report.get('planning_cpu_budget')
    if (not isinstance(allowed, list) or not allowed or
            any(not isinstance(x, int) for x in allowed) or len(set(allowed)) != len(allowed) or
            not isinstance(budget, int) or not 1 <= budget <= len(allowed)):
        raise ValueError('invalid probe CPU budget')
    cg = report.get('cgroup', {})
    quota = cg.get('quota_cpu_equivalents')
    if quota is not None and budget > int(quota):
        raise ValueError('probe budget exceeds cgroup quota')
    if not cg.get('ancestors') or not cg.get('visible_hierarchy_only'):
        raise ValueError('ambiguous cgroup mapping')
    return budget


def command(args: list[str], env: dict[str, str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          env=env, timeout=120).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--probe', type=Path, required=True)
    ap.add_argument('--work-root', type=Path, required=True)
    args = ap.parse_args()
    report = json.loads(args.probe.read_text())
    validate_probe(report)
    work = args.work_root.resolve()
    if work == ROOT or ROOT in work.parents:
        raise ValueError('work root must be outside repository')
    if Path(sys.prefix) == Path(sys.base_prefix):
        raise RuntimeError('run with fresh project-local venv Python')
    env = trusted_env(os.environ)
    compiler = shutil.which('g++', path=env.get('PATH'))
    if compiler is None:
        raise RuntimeError('missing system dependency: g++')
    manifest = json.loads((ROOT/'evidence/BASELINE_SOURCE_MANIFEST.json').read_text())
    for name, expected in manifest.items():
        if name.startswith('native/reference/') and sha(ROOT/name) != expected:
            raise ValueError(f'frozen source changed: {name}')
    sources = {f'{lane}/{name}': sha(ROOT/'native'/lane/name)
               for lane in ('reference', 'candidate') for name in SOURCES}
    import numpy as np
    import scipy
    versions = {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
                'compiler': command([compiler, '--version'], env).splitlines()[0],
                'ld': command(['ld', '--version'], env).splitlines()[0],
                'as': command(['as', '--version'], env).splitlines()[0]}
    macros = command([compiler, '-dM', '-E', '-x', 'c++', '/dev/null'], env)
    wanted = {'__LDBL_MANT_DIG__', '__LDBL_MAX_EXP__', '__SIZEOF_LONG_DOUBLE__',
              '__FLT128_MANT_DIG__', '__SIZEOF_FLOAT128__'}
    precision = {parts[1]: parts[2] for line in macros.splitlines()
                 if len(parts := line.split()) == 3 and parts[1] in wanted}
    if precision != report.get('compiler_precision_macros'):
        raise ValueError('precision macros differ from ingested probe')
    identity = {'probe_sha256': sha(args.probe), 'host_fingerprint': report['observed_host_fingerprint'],
                'compiler_path': compiler, 'versions': versions, 'precision_macros': precision,
                'flags': FLAGS, 'sources': sources, 'platform': platform.platform()}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    folder = work/'build'/key
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder/'BUILD.json'
    if receipt.exists():
        old = json.loads(receipt.read_text())
        if old['identity'] != identity or any(sha(Path(v['path'])) != v['sha256']
                                              for v in old['libraries'].values()):
            raise ValueError('build cache identity mismatch')
        print(json.dumps(old, indent=2))
        return 0
    libs = {}
    for lane in ('reference', 'candidate'):
        source = ROOT/'native'/lane/'r31a/hybrid12_wide_h_v2.cpp'
        binary = folder/f'{lane}.so'
        cmd = [compiler, *FLAGS, str(source), '-o', str(binary)]
        subprocess.run(cmd, check=True, capture_output=True, text=True, env=env, timeout=180)
        libs[lane] = {'path': str(binary), 'sha256': sha(binary), 'command': cmd}
    result = {'schema': 'WU088_R31S_NCP_BUILD_V1', 'identity': identity,
              'build_key': key, 'libraries': libs, 'production_admitted': False}
    with receipt.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
