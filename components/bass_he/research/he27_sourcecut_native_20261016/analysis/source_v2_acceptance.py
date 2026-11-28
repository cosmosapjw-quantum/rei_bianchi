"""Create-only raw evidence writer for the bounded HE27 source-v2 tests."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_create(path, payload):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.partial')
    with temporary.open('x') as handle:
        json.dump(payload, handle, indent=2, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.link(temporary, path)
    temporary.unlink()
    parent_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def record_snapshot(output, package, source_sha_at_start, observations, models):
    package = Path(package).resolve()
    source = package / 'src' / 'sourcecut_v2.py'
    current_sha = sha256(source)
    payload = {
        'schema': 'bass_he.he27.source_v2_acceptance.v1',
        'scope': 'opt-in source table construction, physical birth moments, '
                 'one-sided cutoff, local regularity, and 512-to-1024 refinement; '
                 'no native ODE claim',
        'source_sha256_at_start': source_sha_at_start,
        'source_sha256_at_end': current_sha,
        'source_identity_stable': source_sha_at_start == current_sha,
        'he26_donor_sha256': sha256(package.parent /
                                   'he26_moving_cutoff_20261016/src/portable_cut_core.py'),
        'he21_source_sha256': sha256(package.parent /
                                    'he23_density_contract_20261016/src/he21_photo.py'),
        'he25_physics_sha256': sha256(package.parent /
                                     'he25_proper_birth_20261016/src/physics.py'),
        'tests_sha256': sha256(package / 'tests/test_source_v2.py'),
        'model_tables': [
            {'key': str(key), 'q': model.q, 'm': model.m, 'angles': model.angles,
             'source_table_nodes': model.source_table_nodes,
             'source_table_sha256': model.source_table_sha256,
             'source_table_diagnostics': model.source_table_diagnostics}
            for key, model in models.items()],
        'observations': observations,
    }
    atomic_create(output, payload)
