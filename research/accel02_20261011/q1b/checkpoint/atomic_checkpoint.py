"""Complete segment-boundary snapshots. No physical provider is supplied here.

Linux renameat2(RENAME_NOREPLACE) is required for atomic create-only publication.
All arithmetic is delegated to the bound caller validator, which runs on write
and on every load. A self-consistent manifest never grants scientific admission.
"""
from __future__ import annotations
import ctypes
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import uuid

import numpy as np

SCHEMA = 'rei.complete_checkpoint.v1'
IDENTITIES = {'source', 'grid', 'binary', 'control', 'physics_contract', 'physical_validator'}
ARRAYS = {'state', 'scales', 'counter_origins', 'prefix_clock', 'prefix_state',
          'scheduled_clock', 'segment_edges', 'accepted_min', 'accepted_max'}
FILES = {'arrays.npz', 'metadata.json', 'identity.json'}


class CheckpointError(ValueError):
    pass


def _require(condition, message):
    if not condition: raise CheckpointError(message)


def _json_bytes(value):
    try:
        return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    except (TypeError, ValueError) as exc:
        raise CheckpointError('Metadata must be finite JSON') from exc


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(identity):
    _require(isinstance(identity, dict) and set(identity) == IDENTITIES,
             'Exactly the declared source/grid/binary/control/contract/validator identities are required')
    _require(all(isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v)
                 for v in identity.values()), 'Identities must be SHA-256 hex strings')


def _name(generation):
    _require(type(generation) is int and 0 <= generation <= 99999999, 'Invalid generation')
    return f'gen-{generation:08d}'


def _strict_sequence(a):
    return a.ndim == 1 and a.size > 0 and np.all(np.diff(a) > 0)


def _validate(arrays, meta, identity, physical_validator):
    _identity(identity)
    _require(callable(physical_validator), 'A caller-selected physical validator is mandatory')
    validator_file = inspect.getsourcefile(physical_validator)
    _require(validator_file is not None and Path(validator_file).is_file(), 'Validator source unavailable')
    _require(_sha(Path(validator_file)) == identity['physical_validator'], 'Physical validator source identity mismatch')
    _json_bytes(meta)
    _require(isinstance(arrays, dict) and set(arrays) == ARRAYS, 'Missing or unexpected arrays')
    for key, array in arrays.items():
        _require(isinstance(array, np.ndarray) and array.dtype == np.dtype('float64') and
                 np.all(np.isfinite(array)), f'{key}: finite float64 ndarray required; no coercion')
    state = arrays['state']; d = state.size
    _require(state.ndim == 1 and d > 0, 'State shape')
    for key in ('scales', 'accepted_min', 'accepted_max'):
        _require(arrays[key].shape == (d,), f'{key}: shape')
    _require(np.all(arrays['scales'] > 0), 'Scales must be positive')
    fields = meta.get('state_fields'); units = meta.get('state_units')
    _require(isinstance(fields, list) and len(fields) == d and
             all(isinstance(x, str) and x for x in fields) and len(set(fields)) == d,
             'State field declaration')
    _require(isinstance(units, list) and len(units) == d and
             all(isinstance(x, str) and x for x in units), 'State units declaration')
    indices = meta.get('counter_indices')
    _require(isinstance(indices, list) and len(indices) > 0 and
             all(type(i) is int and 0 <= i < d for i in indices) and
             len(set(indices)) == len(indices), 'Counter indices')
    _require(arrays['counter_origins'].shape == (len(indices),), 'Counter origins shape')
    for key in ('prefix_clock', 'scheduled_clock', 'segment_edges'):
        _require(_strict_sequence(arrays[key]), f'{key}: strict ascending sequence required')
    prefix = arrays['prefix_clock']; schedule = arrays['scheduled_clock']; edges = arrays['segment_edges']
    _require(edges.size >= 2 and schedule[0] == edges[0] and schedule[-1] == edges[-1],
             'Schedule must include both complete-run endpoints')
    completed = meta.get('completed_segments'); nxt = meta.get('next_segment_index')
    _require(type(completed) is int and 0 <= completed < edges.size and nxt == completed,
             'Segment cursor must identify a natural completed boundary')
    clock = meta.get('current_clock')
    _require(type(clock) in (int, float) and np.isfinite(clock) and clock == edges[completed],
             'Checkpoint must be exactly at the declared natural segment boundary')
    expected_next = None if completed == edges.size - 1 else [float(edges[completed]), float(edges[completed + 1])]
    _require(meta.get('next_segment') == expected_next, 'Next segment bounds mismatch')
    expected_prefix = schedule[schedule <= clock]
    _require(np.array_equal(prefix, expected_prefix), 'Prefix is not the full exact scheduled prefix through clock')
    history = arrays['prefix_state']
    _require(history.shape == (prefix.size, d), 'Prefix state shape')
    _require(np.array_equal(history[0, indices], arrays['counter_origins']), 'Counter origins do not match initial prefix')
    if prefix[-1] == clock:
        _require(np.array_equal(history[-1], state), 'Boundary sample differs from accepted state')
    minimum = arrays['accepted_min']; maximum = arrays['accepted_max']
    _require(np.all(minimum <= maximum) and np.all(minimum <= state) and np.all(state <= maximum)
             and np.all(minimum <= history.min(axis=0)) and np.all(history.max(axis=0) <= maximum),
             'Accepted extrema must enclose all preserved states')
    flags = meta.get('accepted_domain_flags')
    _require(isinstance(flags, dict) and flags and all(type(v) is bool for v in flags.values()),
             'Explicit accepted domain flags required')
    _require(all(flags.values()), 'Failed physical domain may be archived but is not a restart generation')
    for key in ('ledger_max', 'ledger_origins'):
        item = meta.get(key)
        _require(isinstance(item, dict) and set(item) == {'number', 'energy'} and
                 all(type(v) in (int, float) and np.isfinite(v) for v in item.values()), f'{key}: number and energy required')
    _require(all(v >= 0 for v in meta['ledger_max'].values()), 'Ledger maxima must be nonnegative')
    _require(all(v > 0 for v in meta['ledger_origins'].values()), 'Ledger normalization origins must be positive')
    _require(meta.get('restart_kind') == 'FRESH_BDF_AT_NATURAL_SEGMENT_BOUNDARY', 'Restart type must be explicit')
    _require(isinstance(meta.get('physical_binding'), str) and meta['physical_binding'], 'Physical binding scope required')
    # Callback is required on load as well as publish. Its result is not trusted
    # from a manifest, and hashes do not authorize the validator or physics.
    result = physical_validator(arrays, meta)
    _require(isinstance(result, dict) and result.get('domain_checked') is True and
             result.get('ledgers_checked') is True and isinstance(result.get('scope'), str),
             'Validator must explicitly check domain and carried ledgers')
    return result


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def _write_bytes(path, data):
    with path.open('xb') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


def _rename_no_replace(source, target):
    libc = ctypes.CDLL(None, use_errno=True)
    rename = getattr(libc, 'renameat2', None)
    _require(rename is not None, 'Atomic create-only publication requires Linux renameat2')
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(target), 1) != 0:
        error = ctypes.get_errno()
        raise CheckpointError(f'Atomic create-only rename failed: {os.strerror(error)}')


def publish_generation(root, generation, arrays, metadata, expected_identity, physical_validator):
    """Validate a complete owned snapshot, fsync, atomically publish without overwrite.

    The caller must synchronize copying from a live solver. Arrays are copied
    immediately; this function cannot make concurrent solver mutations atomic.
    Temporary directories are intentionally retained after unexpected I/O errors.
    """
    root = Path(root); name = _name(generation)
    _require(isinstance(arrays, dict) and all(isinstance(value, np.ndarray)
             for value in arrays.values()), 'Snapshot arrays must be ndarrays')
    arrays = {key: value.copy() for key, value in arrays.items()}
    metadata = json.loads(_json_bytes(metadata))
    identity = json.loads(_json_bytes(expected_identity))
    _validate(arrays, metadata, identity, physical_validator)
    missing = []
    ancestor = root
    while not ancestor.exists():
        missing.append(ancestor)
        ancestor = ancestor.parent
    root.mkdir(parents=True, exist_ok=True)
    # Persist newly created path components from leaf through its existing
    # parent; no assumption that root was already provisioned durably.
    for directory in missing:
        _fsync_dir(directory)
        _fsync_dir(directory.parent)
    _require(not root.is_symlink(), 'Checkpoint root cannot be a symlink')
    target = root / name
    _require(not target.exists(), 'Create-only generation collision')
    temp = root / f'.tmp-{name}-{uuid.uuid4().hex}'
    temp.mkdir()
    with (temp / 'arrays.npz').open('xb') as handle:
        np.savez_compressed(handle, **arrays); handle.flush(); os.fsync(handle.fileno())
    _write_bytes(temp / 'metadata.json', _json_bytes(metadata))
    _write_bytes(temp / 'identity.json', _json_bytes(identity))
    manifest = {
        'schema': SCHEMA, 'generation': generation,
        'files': {name: {'sha256': _sha(temp / name), 'bytes': (temp / name).stat().st_size}
                  for name in sorted(FILES)},
        'internal_integrator_state_saved': False,
        'scientific_admission': False,
        'publication_semantics': 'fsync_files_then_directory_then_atomic_rename_noreplace_then_parent_fsync',
        'remote_durability': 'NOT_ESTABLISHED_BY_LOCAL_PUBLICATION',
    }
    _write_bytes(temp / 'manifest.json', _json_bytes(manifest))
    _fsync_dir(temp)
    _rename_no_replace(temp, target)
    _fsync_dir(root)
    return target


def _read_checked(path, generation):
    _require(path.is_dir() and not path.is_symlink(), 'Missing or symlink generation')
    _require({p.name for p in path.iterdir()} == FILES | {'manifest.json'}, 'Torn or unexpected generation contents')
    for p in path.iterdir(): _require(p.is_file() and not p.is_symlink(), 'Generation members must be regular files')
    try: manifest = json.loads((path / 'manifest.json').read_text())
    except (OSError, ValueError) as exc: raise CheckpointError('Unreadable manifest') from exc
    _require(isinstance(manifest, dict), 'Manifest must be an object')
    _require(manifest.get('schema') == SCHEMA and manifest.get('generation') == generation
             and isinstance(manifest.get('files'), dict) and set(manifest['files']) == FILES and
             manifest.get('scientific_admission') is False and
             manifest.get('internal_integrator_state_saved') is False, 'Manifest schema or scope mismatch')
    for name in FILES:
        info = manifest['files'][name]; p = path / name
        _require(isinstance(info, dict) and info.get('bytes') == p.stat().st_size
                 and info.get('sha256') == _sha(p), f'Corrupt member: {name}')
    return manifest


def discover_generations(root):
    """Return structurally complete, hash-consistent generations; not physics GO."""
    root = Path(root)
    if not root.exists(): return []
    complete = []
    for path in root.iterdir():
        if not re.fullmatch(r'gen-[0-9]{8}', path.name): continue
        generation = int(path.name[4:])
        try: _read_checked(path, generation)
        except (CheckpointError, OSError, TypeError): continue
        complete.append(generation)
    return sorted(complete)


def load_generation(root, generation, expected_identity, physical_validator, *, expected_manifest_sha256=None):
    """Restore bytes and revalidate binding/domain; no solver is started here."""
    path = Path(root) / _name(generation)
    manifest = _read_checked(path, generation)
    if expected_manifest_sha256 is not None:
        _require(_sha(path/'manifest.json') == expected_manifest_sha256, 'Generation manifest identity mismatch')
    try:
        identity = json.loads((path / 'identity.json').read_text())
        metadata = json.loads((path / 'metadata.json').read_text())
        with np.load(path / 'arrays.npz', allow_pickle=False) as handle:
            arrays = {key: handle[key].copy() for key in handle.files}
    except (OSError, ValueError, KeyError) as exc:
        raise CheckpointError('Invalid serialized snapshot') from exc
    _identity(expected_identity)
    _require(identity == expected_identity, 'Stale or incompatible source/grid/binary/control identity')
    validation = _validate(arrays, metadata, identity, physical_validator)
    return {'arrays': arrays, 'metadata': metadata, 'identity': identity,
            'manifest': manifest, 'current_validation': validation}
