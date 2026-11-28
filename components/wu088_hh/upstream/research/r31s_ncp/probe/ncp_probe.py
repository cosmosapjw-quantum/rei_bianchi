#!/usr/bin/env python3
"""Read-only Linux/cgroup-v2 intake. No scientific runtime import or cloud API.

Outputs *candidate* configurations, never a selected/promoted configuration.
Cgroup-v1/ambiguous mount membership is explicitly blocked pending inspection.
Guest package/core/NUMA/L3 identifiers do not establish host physical topology.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys


def cpulist(text: str) -> list[int]:
    values = set()
    for part in text.strip().split(','):
        if not part:
            continue
        if not re.fullmatch(r'\d+(?:-\d+)?', part):
            raise ValueError('invalid CPU list')
        ends = [int(x) for x in part.split('-')]
        lo, hi = ends[0], ends[-1]
        if lo > hi or hi > 1048576:
            raise ValueError('invalid CPU range')
        values.update(range(lo, hi+1))
    return sorted(values)


def optional_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return None


def topology(root: Path, cpus: list[int]) -> dict:
    rows = {}
    for cpu in cpus:
        base = root/f'cpu{cpu}'
        row = {'core_id': None, 'package_id': None, 'siblings': None,
               'l3_cpus': None, 'numa_nodes': []}
        for key, filename in [('core_id','core_id'), ('package_id','physical_package_id')]:
            v = optional_text(base/'topology'/filename)
            row[key] = int(v) if v is not None else None
        v = optional_text(base/'topology'/'thread_siblings_list')
        row['siblings'] = cpulist(v) if v is not None else None
        for cache in sorted((base/'cache').glob('index*')):
            if optional_text(cache/'level') == '3':
                v = optional_text(cache/'shared_cpu_list')
                if v is not None:
                    row['l3_cpus'] = cpulist(v)
                    break
        row['numa_nodes'] = sorted(int(p.name[4:]) for p in base.glob('node[0-9]*'))
        rows[str(cpu)] = row
    return rows


def _unescape_mount(text: str) -> str:
    return re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), text)


def cgroup_paths(mountinfo: str, membership: str) -> tuple[list[Path], list[str]]:
    members = [line.split(':', 2)[2] for line in membership.splitlines()
               if line.startswith('0::')]
    if len(members) != 1:
        return [], ['NO_UNAMBIGUOUS_CGROUP_V2_MEMBERSHIP; NO_AUTOMATIC_PLAN']
    member = PurePosixPath(members[0])
    if '..' in member.parts:
        return [], ['UNRESOLVED_NAMESPACED_MEMBERSHIP; NO_AUTOMATIC_PLAN']
    possibilities = []
    for line in mountinfo.splitlines():
        before, sep, after = line.partition(' - ')
        if not sep or after.split()[0] != 'cgroup2':
            continue
        fields = before.split()
        if len(fields) < 5:
            continue
        root = PurePosixPath(_unescape_mount(fields[3]))
        mount = Path(_unescape_mount(fields[4]))
        try:
            relative = member.relative_to(root)
        except ValueError:
            continue
        child = mount/str(relative)
        if child.is_dir():
            possibilities.append((len(root.parts), mount, child))
    if not possibilities:
        return [], ['CGROUP_V2_MOUNT_MAPPING_UNRESOLVED; NO_AUTOMATIC_PLAN']
    _, mount, child = max(possibilities, key=lambda x: x[0])
    paths = [child]
    while paths[-1] != mount:
        paths.append(paths[-1].parent)
    return paths, []


def limits(paths: list[Path], mem_available: int) -> dict:
    quotas, memory_headrooms, rows = [], [mem_available], []
    for path in paths:
        row = {'path': str(path)}
        for name in ('cpu.max','cpu.stat','memory.max','memory.current','memory.high','memory.events'):
            row[name] = optional_text(path/name)
        if row['cpu.max'] is not None:
            fields = row['cpu.max'].split()
            if len(fields) != 2 or int(fields[1]) <= 0:
                raise ValueError('malformed discovered cpu.max')
            if fields[0] != 'max':
                q = int(fields[0])/int(fields[1])
                if q <= 0:
                    raise ValueError('nonpositive CPU quota')
                quotas.append(q)
        if row['memory.max'] not in (None, 'max'):
            hard = int(row['memory.max'])
            if hard < 0 or row['memory.current'] is None:
                raise ValueError('incomplete discovered memory limit')
            used = int(row['memory.current'])
            if used < 0:
                raise ValueError('negative memory usage')
            memory_headrooms.append(max(0, hard-used))
        rows.append(row)
    return {'quota_cpu_equivalents': min(quotas) if quotas else None,
            'memory_available_upper_bytes': min(memory_headrooms),
            'visible_hierarchy_only': True, 'ancestors': rows}


def candidates(budget: int, tasks: int = 144) -> list[dict]:
    if budget < 0 or tasks < 1:
        raise ValueError('invalid planning budget')
    if budget == 0:
        return []
    rows = {}
    for cap in sorted({max(1, budget//2), budget}):
        for threads in (1,2,4,8,12,16,24,32,48,64):
            processes = min(tasks, cap//threads)
            if processes:
                rows[processes, threads] = {
                    'processes': processes, 'kernel_threads': threads,
                    'logical_slots': processes*threads,
                    'legacy_12_pair_policy_eligible': processes <= 12,
                    'benchmark_only': True, 'production_execution_allowed': False}
    return [rows[k] for k in sorted(rows, key=lambda x: (x[0]*x[1], -x[0]))]


def _command(args: list[str], env: dict) -> dict:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=5, env=env)
        return {'returncode': p.returncode, 'stdout': p.stdout[:20000], 'stderr': p.stderr[:2000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'error': type(exc).__name__}


def probe(workspace: Path) -> dict:
    allowed = sorted(os.sched_getaffinity(0))
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemTotal','MemAvailable','SwapTotal','SwapFree'):
            mem[key+'_bytes'] = int(value.split()[0])*1024
    cgpaths, warnings = cgroup_paths(Path('/proc/self/mountinfo').read_text(),
                                    Path('/proc/self/cgroup').read_text())
    bound = limits(cgpaths, mem['MemAvailable_bytes'])
    budget = len(allowed)
    if bound['quota_cpu_equivalents'] is not None:
        budget = min(budget, math.floor(bound['quota_cpu_equivalents']))
    cpuinfo = Path('/proc/cpuinfo').read_text()
    model = next((s.split(':',1)[1].strip() for s in cpuinfo.splitlines()
                  if s.startswith('model name')), 'UNKNOWN')
    flags = next((s.split(':',1)[1].split() for s in cpuinfo.splitlines()
                  if s.startswith('flags')), [])
    env = dict(os.environ)
    for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH'):
        env.pop(key, None)
    compiler = shutil.which('g++')
    macros = _command([compiler,'-dM','-E','-x','c++','/dev/null'], env) if compiler else {}
    wanted = ('__LDBL_MANT_DIG__','__LDBL_MAX_EXP__','__SIZEOF_LONG_DOUBLE__',
              '__FLT128_MANT_DIG__','__SIZEOF_FLOAT128__')
    abi = {}
    for line in macros.get('stdout','').splitlines():
        pieces = line.split()
        if len(pieces) == 3 and pieces[1] in wanted:
            abi[pieces[1]] = pieces[2]
    # Bounds are observations, not a resource reservation or cross-host approval.
    r = {'schema':'WU088_NCP_READ_ONLY_PROBE_V1', 'status':'PROBED_NOT_BENCHMARKED',
         'python':sys.version, 'platform':platform.platform(), 'cpu_model':model,
         'visible_cpu_flags':flags, 'allowed_logical_cpus':allowed,
         'guest_topology':topology(Path('/sys/devices/system/cpu'), allowed),
         'host_physical_core_count':'NOT_ESTABLISHED_BY_GUEST',
         'memory':mem, 'cgroup':bound, 'planning_cpu_budget':budget,
         'filesystem_free_bytes':shutil.disk_usage(workspace).free,
         'compiler':_command([compiler,'--version'], env) if compiler else {'error':'MISSING'},
         'compiler_precision_macros':abi, 'warnings':warnings,
         'candidate_configurations':candidates(budget) if not warnings else [],
         'selected_configuration':None, 'heavy_execution_allowed':False,
         'native_cross_host_equivalence_verified':False,
         'production_admitted':False, 'cloud_instance_created':False}
    if warnings:
        r['status'] = 'PROBE_REQUIRES_CGROUP_INSPECTION'
    identity = {'cpu_model':model, 'allowed_cpus':allowed, 'topology':r['guest_topology'],
                'cpu_quota':bound['quota_cpu_equivalents'], 'abi':abi}
    r['observed_host_fingerprint'] = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    return r


def save_report(path: Path, report: dict) -> None:
    # O_EXCL: never overwrite a prior machine observation or follow a target symlink.
    with path.open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workspace', type=Path, default=Path.cwd())
    a = ap.parse_args()
    r = probe(a.workspace)
    save_report(a.out, r)
    print(json.dumps({'status':r['status'], 'report':str(a.out),
                      'planning_cpu_budget':r['planning_cpu_budget'],
                      'heavy_execution_allowed':False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
