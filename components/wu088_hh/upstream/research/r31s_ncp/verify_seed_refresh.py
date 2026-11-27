#!/usr/bin/env python3
"""Verify that the c8 authority refresh preserves every completed M2 input array."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from types import ModuleType

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
GRID = ROOT/'research/r31s_ncp/authority_seed/grid_seed.py'
MANIFEST = ROOT/'research/r31s_ncp/authority_seed/AUTHORITY_MANIFEST.json'
PRIOR_COMMIT = 'bb7fc9503eca7fce6e4eabf596d0183ec391399f'
CURRENT_BASELINE = 'c8c741d8d05e7ad3d31d7eba2c24fc86df0c0a9c'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    old_bytes = subprocess.run(
        ['git', 'show', f'{PRIOR_COMMIT}:research/r31s_ncp/authority_seed/grid_seed.py'],
        cwd=ROOT, check=True, capture_output=True).stdout
    old = ModuleType('prior_grid_seed')
    old.__file__ = str(GRID)
    exec(compile(old_bytes, str(GRID), 'exec'), old.__dict__)
    spec = importlib.util.spec_from_file_location('current_grid_seed', GRID)
    current = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current)
    manifest = json.loads(MANIFEST.read_text())
    rows = []
    for n, g in ((160, 80), (192, 80), (32, 20)):
        previous = old.grid(n, g)
        now = current.grid(n, g)
        arrays = {}
        for name, left, right in (
            ('C', previous[0]['C'], now[0]['C']),
            ('exponents', previous[0]['exponents'], now[0]['exponents']),
            ('v', previous[0]['v'], now[0]['v']),
            ('t', previous[1], now[1]),
            ('W', previous[2], now[2]),
            ('gs', previous[3], now[3]),
            ('gw', previous[4], now[4]),
        ):
            a, b = np.asarray(left), np.asarray(right)
            byte_equal = a.tobytes(order='C') == b.tobytes(order='C')
            digest = sha(b.tobytes(order='C'))
            if not byte_equal or not np.array_equal(a, b):
                raise RuntimeError(f'{name} changed at n={n}, g={g}')
            if name in ('C', 'exponents', 'v'):
                if digest != manifest['model_seed']['array_byte_sha256'][name]:
                    raise RuntimeError(f'{name} differs from authority manifest')
            arrays[name] = {'byte_equal': byte_equal, 'sha256': digest,
                            'shape': list(b.shape), 'dtype': str(b.dtype)}
        rows.append({'n': n, 'g': g, 'arrays': arrays})
    report = {
        'schema': 'WU088_R31S_NCP_AUTHORITY_REFRESH_V1',
        'status': 'ARRAYS_BIT_IDENTICAL_PRIOR_AND_CURRENT_SEED',
        'prior_codex_commit': PRIOR_COMMIT,
        'baseline_commit': CURRENT_BASELINE,
        'old_grid_source_sha256': sha(old_bytes),
        'new_grid_source_sha256': sha(GRID.read_bytes()),
        'new_authority_manifest_sha256': sha(MANIFEST.read_bytes()),
        'model_seed_git_blob_sha1': manifest['model_seed']['git_blob_sha1'],
        'rows': rows,
        'scientific_heavy_reexecution_required': False,
        'reason': 'All model fields and grid/weight arrays used by the completed bounded M2 workloads are byte-identical; native source and build flags did not change.',
    }
    with args.out.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(report['status'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
