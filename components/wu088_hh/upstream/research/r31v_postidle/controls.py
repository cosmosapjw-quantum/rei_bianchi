"""Opt-in benchmark controls. No native calls, process kills, or cgroup writes.

ReferenceCache is a trusted-local integrity cache, not a cryptographic proof
of correctness against a malicious writer. Its read path never computes.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time
import numpy as np

COMPONENTS = ('H0', 'H0_sumabs', 'foreign', 'foreign_sumabs')


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest_json(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def _pair(pair) -> tuple[int, int]:
    if not isinstance(pair, (tuple, list)) or len(pair) != 2 or any(type(i) is not int or i < 0 for i in pair):
        raise ValueError('pair requires two nonnegative integer indices')
    return tuple(pair)


def balanced_workload(pairs) -> list[tuple[int, int]]:
    pairs = [_pair(p) for p in pairs]
    if len(pairs) != 12 or len(set(pairs)) != 12:
        raise ValueError('this bounded comparison requires exactly 12 unique pairs')
    return pairs*11


def workload_identity(tasks) -> dict:
    tasks = [_pair(p) for p in tasks]
    return {'ordered_task_sha256': digest_json(tasks), 'count': len(tasks),
            'histogram': [{'pair': list(p), 'count': tasks.count(p)} for p in sorted(set(tasks))]}


def parse_cpu_max(text: str) -> float:
    fields = text.split()
    if len(fields) != 2:
        raise ValueError('cpu.max must have quota and period')
    try:
        period = int(fields[1])
        quota = math.inf if fields[0] == 'max' else int(fields[0])
    except (ValueError, OverflowError) as e:
        raise ValueError('invalid cpu.max') from e
    if period <= 0 or quota <= 0:
        raise ValueError('nonpositive CPU quota/period')
    return quota/period


def hierarchy_limits(root: Path, leaf: Path, affinity_count: int, mem_available: int) -> dict:
    """Combine visible cgroup-v2 ancestors. Reject missing non-root controls.

    Caller must independently establish visibility of the true hierarchy root;
    a delegated/cgroup-namespaced view is not a host-wide quota certificate.
    """
    root, leaf = Path(root).resolve(), Path(leaf).resolve()
    if not leaf.is_relative_to(root) or not leaf.is_dir():
        raise ValueError('unresolved cgroup path')
    if type(affinity_count) is not int or affinity_count < 1 or type(mem_available) is not int or mem_available < 1:
        raise ValueError('invalid live resource limits')
    quotas, available, rows = [float(affinity_count)], [mem_available], []
    path = leaf
    while True:
        names = ('cpu.max', 'memory.max', 'memory.current')
        if path != root and any(not (path/n).is_file() for n in names):
            raise ValueError('incomplete cgroup controller visibility: '+str(path))
        row = {'path': str(path)}
        if (path/'cpu.max').exists():
            text = (path/'cpu.max').read_text().strip()
            quota = parse_cpu_max(text); quotas.append(quota); row['cpu.max'] = text
        if (path/'memory.max').exists():
            limit = (path/'memory.max').read_text().strip()
            current = int((path/'memory.current').read_text())
            if current < 0:
                raise ValueError('negative memory.current')
            if limit != 'max':
                upper = int(limit)
                if upper < 0:
                    raise ValueError('negative memory.max')
                available.append(max(0, upper-current))
            row.update(memory_max=limit, memory_current=current)
        rows.append(row)
        if path == root:
            break
        path = path.parent
    return {'cpu_budget': math.floor(min(quotas)),
            'memory_available_bytes': min(available), 'ancestors': rows}


def live_resources() -> dict:
    """Read-only Linux VM probe; intentionally fail on delegated mount roots.

    A '/' mount root is necessary, not sufficient to prove that no outer
    namespace quota exists. This implementation is for the admitted NCP VM;
    operator census and host identity remain required.
    """
    if not hasattr(os, 'sched_getaffinity'):
        raise ValueError('Linux sched_getaffinity required')
    mounts = []
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        left, right = line.split(' - ', 1)
        f = left.split()
        if right.split()[0] == 'cgroup2':
            mounts.append((f[3], f[4]))
    groups = [s.split(':', 2)[2] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')]
    if len(mounts) != 1 or mounts[0][0] != '/' or len(groups) != 1 or '..' in Path(groups[0]).parts:
        raise ValueError('unverified cgroup root/namespace; cannot admit allocation')
    root = Path(mounts[0][1]); leaf = root/groups[0].lstrip('/')
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[2] == 'kB':
            mem[fields[0].rstrip(':')] = int(fields[1])*1024
    allowed = sorted(os.sched_getaffinity(0))
    limits = hierarchy_limits(root, leaf, len(allowed), mem['MemAvailable'])
    return {**limits, 'allowed_cpus': allowed, 'cgroup_path': str(leaf),
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'sampled_unix': time.time(), 'pid': os.getpid(),
            'visibility_scope': 'VISIBLE_V2_HIERARCHY__OPERATOR_VM_ATTESTATION_REQUIRED'}


def validate_grant(grant: dict, live: dict, layouts, *, now=None) -> dict:
    """Validate a supplied allocation, never create or infer authorization.

    idle_census_confirmed is operator evidence, not independently proved here.
    It does not prevent another session from starting work later.
    """
    now = time.time() if now is None else now
    expires = grant.get('expires_unix', float('nan'))
    if not isinstance(expires, (int, float)) or isinstance(expires, bool) or not math.isfinite(expires) or expires <= now:
        raise ValueError('expired/malformed allocation')
    if (grant.get('schema') != 'WU088_R31V_GRANT_V1' or not grant.get('epoch_id')
        or grant.get('mode') != 'BENCHMARK_EXCLUSIVE'
        or grant.get('fixed_workload_132_approved') is not True
        or grant.get('idle_census_confirmed') is not True
        or grant.get('boot_id') != live.get('boot_id')):
        raise ValueError('allocation identity, mode, or owner evidence absent')
    cpus = grant.get('cpus', [])
    if (not isinstance(cpus, list) or not cpus or any(type(c) is not int or c < 0 for c in cpus)
        or len(set(cpus)) != len(cpus) or not set(cpus) <= set(live['allowed_cpus'])):
        raise ValueError('CPU grant is not a unique subset of live affinity')
    reserve = grant.get('memory_reserve_bytes')
    if type(reserve) is not int or reserve < 0 or reserve >= live['memory_available_bytes']:
        raise ValueError('missing or infeasible memory reserve')
    if not layouts or any(len(x) != 2 or any(type(i) is not int or i <= 0 for i in x) for x in layouts):
        raise ValueError('positive integer P,T layouts required')
    layouts = [tuple(x) for x in layouts]
    if len(set(layouts)) != len(layouts):
        raise ValueError('duplicate layouts')
    budget = min(len(cpus), int(live['cpu_budget']))
    if budget < 1 or any(p*t > budget for p, t in layouts):
        raise ValueError('layout exceeds current grant/affinity/quota intersection')
    return {'cpus': sorted(cpus), 'budget': budget,
            'memory_available_bytes': live['memory_available_bytes']-reserve,
            'epoch_id': grant['epoch_id'], 'mode': grant['mode']}


def atomic_json(path: Path, value, *, create_only=False) -> None:
    """Publish one complete JSON object; never expose a partial cache entry."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    content = canonical(value)+b'\n'
    fd, name = tempfile.mkstemp(prefix='.'+path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        if create_only:
            os.link(name, path)
        else:
            os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        Path(name).unlink(missing_ok=True)


class ReferenceCache:
    """Path-independent numeric context key; exact dtype/shape/byte integrity.

    Context is an explicit caller contract. Hash equality does not establish
    that the caller included every necessary dependency, or reviewer independence.
    """
    def __init__(self, root: Path, context: dict):
        self.context = json.loads(canonical(context))
        self.key = digest_json(self.context)
        self.root = Path(root)/self.key

    def path(self, pair) -> Path:
        i, j = _pair(pair)
        return self.root/f'pair_{i}_{j}.json'

    @staticmethod
    def _encode(values: dict) -> dict:
        if set(values) != set(COMPONENTS):
            raise ValueError('unexpected full-pair components')
        out = {}
        for name in COMPONENTS:
            a = np.ascontiguousarray(values[name])
            if a.dtype.kind not in 'fc' or not a.size or not np.isfinite(a).all():
                raise ValueError('reference arrays must be finite nonempty float/complex arrays')
            out[name] = {'dtype': a.dtype.str, 'shape': list(a.shape), 'hex': a.tobytes().hex()}
        return out

    def write(self, pair, arrays: dict) -> None:
        payload = self._encode(arrays)
        atomic_json(self.path(pair), {'schema': 'WU088_R31V_REFERENCE_V1',
                    'context': self.context, 'context_sha256': self.key,
                    'pair': list(_pair(pair)), 'arrays': payload,
                    'payload_sha256': digest_json(payload)}, create_only=True)

    def read(self, pair) -> dict:
        path = self.path(pair)
        if path.is_symlink() or (path.exists() and path.stat().st_size > 16*1024*1024):
            raise ValueError('invalid cache entry type/size')
        d = json.loads(path.read_text())
        if (d.get('schema') != 'WU088_R31V_REFERENCE_V1' or d.get('context') != self.context
            or d.get('context_sha256') != self.key or d.get('pair') != list(_pair(pair))
            or digest_json(d.get('arrays')) != d.get('payload_sha256')):
            raise ValueError('cache identity or payload hash mismatch')
        values = {}
        if set(d['arrays']) != set(COMPONENTS):
            raise ValueError('wrong reference components')
        for name, row in d['arrays'].items():
            dtype = np.dtype(row['dtype']); shape = row['shape']
            if dtype.kind not in 'fc' or not isinstance(shape, list) or any(type(n) is not int or n < 0 for n in shape):
                raise ValueError('invalid cached dtype/shape')
            raw = bytes.fromhex(row['hex'])
            if math.prod(shape)*dtype.itemsize != len(raw) or not raw:
                raise ValueError('cached shape/byte-count mismatch')
            a = np.frombuffer(raw, dtype=dtype).reshape(shape).copy()
            if not np.isfinite(a).all():
                raise ValueError('nonfinite cached array')
            values[name] = a
        return values
