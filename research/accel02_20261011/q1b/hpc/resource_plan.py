"""Conservative single-node process plan; no scientific work or cloud provisioning."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re

GIB = 1024 ** 3
THREAD_ENV = {
    name: "1" for name in (
        "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
    )
}


def cgroup_remaining_bytes(cgroup_file=Path('/proc/self/cgroup'),
                           mountinfo_file=Path('/proc/self/mountinfo')):
    """Resolve the current v2 cgroup and every visible limiting ancestor."""
    membership = [line[3:] for line in cgroup_file.read_text().splitlines() if line.startswith('0::')]
    if len(membership) != 1:
        raise RuntimeError('CGROUP_V2_REQUIRED_FOR_MEMORY_LIMIT_CHECK')
    group = Path(membership[0])
    candidates = []
    def unescape(value):
        return re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), value)
    for line in mountinfo_file.read_text().splitlines():
        before, after = line.split(' - ', 1)
        if after.split()[0] != 'cgroup2':
            continue
        fields = before.split()
        root, mount = Path(unescape(fields[3])), Path(unescape(fields[4]))
        if group.is_relative_to(root):
            candidates.append((len(root.parts), mount, mount/group.relative_to(root)))
    if not candidates:
        raise RuntimeError('CURRENT_CGROUP_MOUNT_NOT_RESOLVED')
    _, mount, current = max(candidates, key=lambda x: x[0])
    limits = []
    while True:
        maximum, used = current/'memory.max', current/'memory.current'
        if maximum.exists() and used.exists():
            raw = maximum.read_text().strip()
            if raw != 'max':
                limits.append(max(0, int(raw)-int(used.read_text())))
        elif current != mount:
            raise RuntimeError('CGROUP_MEMORY_CONTROLLER_UNREADABLE')
        if current == mount:
            break
        current = current.parent
    return min(limits) if limits else None


def memory_limit_bytes():
    """Use host available memory capped by current/ancestor cgroup headroom."""
    fields = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        fields[key] = int(value.strip().split()[0]) * 1024
    available = fields.get('MemAvailable', fields['MemTotal'])
    remaining = cgroup_remaining_bytes()
    if remaining is not None:
        available = min(available, remaining)
    return available


def plan(*, affinity_cpus, available_bytes, requested_workers=8,
         reserve_cores=2, coordinator_gib=8., worker_gib=1., reserve_gib=8.):
    """Allocation ceilings are conservative estimates, not measured RSS promises."""
    for value in (affinity_cpus, requested_workers, reserve_cores):
        if type(value) is not int or value < 0:
            raise ValueError('RESOURCE_INTEGER_DOMAIN')
    if affinity_cpus < 1 or requested_workers < 1 or available_bytes <= 0:
        raise ValueError('NO_USABLE_RESOURCE')
    if not all(math.isfinite(v) and v > 0 for v in (coordinator_gib, worker_gib, reserve_gib)):
        raise ValueError('MEMORY_ESTIMATE_DOMAIN')
    memory_workers = math.floor((available_bytes / GIB - coordinator_gib - reserve_gib) / worker_gib)
    cpu_workers = affinity_cpus - reserve_cores
    if cpu_workers < 1:
        raise ValueError('INSUFFICIENT_CPU_HEADROOM')
    workers = min(requested_workers, 48, cpu_workers, memory_workers)
    if workers < 1:
        raise ValueError('INSUFFICIENT_MEMORY_HEADROOM')
    return {
        'schema': 'rei.hpc.resource_plan.v1', 'workers': workers,
        'requested_workers': requested_workers, 'affinity_cpus': affinity_cpus,
        'available_memory_gib': available_bytes / GIB,
        'estimated_memory_gib': coordinator_gib + workers * worker_gib,
        'memory_reserve_gib': reserve_gib, 'reserve_cores': reserve_cores,
        'worker_upper_cap': 48, 'thread_environment': THREAD_ENV,
        'parallel_unit': 'ordered independent radiation cells within one map',
        'time_trajectory': 'sequential', 'coarse_fine_branches': 'sequential',
        'process_note': 'Each worker owns one SIGMA subprocess; coordinator owns gas RHS. IPC peers are not extra independent trajectories.',
        'memory_estimates_measured': False, 'speedup_measured': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--coordinator-gib', type=float, default=8.)
    parser.add_argument('--worker-gib', type=float, default=1.)
    parser.add_argument('--reserve-gib', type=float, default=8.)
    args = parser.parse_args()
    cpus = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count()
    print(json.dumps(plan(affinity_cpus=cpus, available_bytes=memory_limit_bytes(),
                         requested_workers=args.workers, coordinator_gib=args.coordinator_gib,
                         worker_gib=args.worker_gib, reserve_gib=args.reserve_gib), indent=2))


if __name__ == '__main__':
    main()
