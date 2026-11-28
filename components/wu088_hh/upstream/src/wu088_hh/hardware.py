"""Linux affinity/topology/quota intake. No machine-name or historical-RAM assumptions."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import platform
import subprocess


def select_resources(topology: dict, allowed: set, quota: float|None, *, requested_workers: int=12,
                     kernel_threads: int=1, use_smt: bool=False) -> dict:
    if not allowed or not allowed<=topology.keys() or kernel_threads<1 or requested_workers<0:
        raise ValueError('invalid affinity/topology/worker request')
    if quota is not None and (not math.isfinite(quota) or quota<=0):
        raise ValueError('invalid CPU quota')
    by_core={}
    for cpu in sorted(allowed): by_core.setdefault(tuple(topology[cpu]),cpu)
    cpus=sorted(allowed) if use_smt else sorted(by_core.values())
    budget=min(len(cpus),max(1,math.floor(quota))) if quota is not None else len(cpus)
    if kernel_threads>budget:
        raise ValueError('kernel threads exceed effective CPU budget')
    workers=min(requested_workers or budget//kernel_threads,len(cpus)//kernel_threads)
    if kernel_threads==1: workers=min(workers,budget)
    if workers*kernel_threads>budget:
        raise ValueError('nested workers*threads exceed effective CPU budget')
    return dict(cpus=cpus,workers=workers,kernel_threads=kernel_threads,effective_cpu_budget=budget,
                physical_allowed=len(by_core),logical_allowed=len(allowed),quota_cores=quota,
                smt_requested=use_smt)


def read_cpu_quota(cgroup_root: Path=Path('/sys/fs/cgroup')) -> tuple[float|None,list]:
    # Current membership plus visible parents. Namespace-root cpu.max is also checked.
    dirs={cgroup_root}
    try:
        for line in Path('/proc/self/cgroup').read_text().splitlines():
            parts=line.split(':',2)
            if parts[0]=='0' and not parts[1]:
                rel=parts[2].lstrip('/')
                if '..' not in Path(rel).parts:
                    p=cgroup_root/rel
                    while p==cgroup_root or cgroup_root in p.parents:
                        dirs.add(p)
                        if p==cgroup_root: break
                        p=p.parent
    except OSError: pass
    quotas=[]; sources=[]
    for d in sorted(dirs):
        f=d/'cpu.max'
        if f.exists():
            fields=f.read_text().split()
            if len(fields)!=2: raise ValueError(f'invalid cpu.max: {f}')
            if fields[0]!='max':
                q=float(fields[0])/float(fields[1]);quotas.append(q);sources.append(dict(path=str(f),cores=q))
    # Common cgroup-v1 fallback, without silently ignoring a discovered bound.
    for d in (cgroup_root/'cpu',cgroup_root/'cpu,cpuacct'):
        qf,pf=d/'cpu.cfs_quota_us',d/'cpu.cfs_period_us'
        if qf.exists() and pf.exists():
            q,p=int(qf.read_text()),int(pf.read_text())
            if q>0: quotas.append(q/p);sources.append(dict(path=str(qf),cores=q/p))
    return (min(quotas) if quotas else None),sources


def inspect_host(*, requested_workers: int=12,kernel_threads: int=1,use_smt: bool=False) -> dict:
    allowed=set(os.sched_getaffinity(0)); topology={}
    for cpu in sorted(allowed):
        base=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
        topology[cpu]=(int((base/'physical_package_id').read_text()),int((base/'core_id').read_text()))
    quota,sources=read_cpu_quota()
    r=select_resources(topology,allowed,quota,requested_workers=requested_workers,
                       kernel_threads=kernel_threads,use_smt=use_smt)
    mem={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        k,v=line.split(':',1)
        if k in ('MemTotal','MemAvailable','SwapTotal','SwapFree'):
            mem[k+'_bytes']=int(v.split()[0])*1024
    for key in ('memory.max','memory.current'):
        f=Path('/sys/fs/cgroup')/key
        if f.exists(): mem['cgroup_'+key]=f.read_text().strip()
    cpuinfo=Path('/proc/cpuinfo').read_text()
    model=next((x.split(':',1)[1].strip() for x in cpuinfo.splitlines() if x.startswith('model name')),'unknown')
    meta=read_linux_cpu_metadata(Path('/sys/devices/system/cpu'),allowed)
    r.update(cpu_model=model,platform=platform.platform(),quota_sources=sources,memory=mem,
             topology={str(k):list(v) for k,v in topology.items()},
             allowed_logical_cpus=sorted(allowed),
             thread_siblings={str(k):v for k,v in meta['thread_siblings'].items()},
             l3_by_cpu={str(k):v for k,v in meta['l3_by_cpu'].items()},
             l3_groups=meta['l3_groups'],hardware_benchmark_performed=False)
    return r


def partition_affinity_groups(topology: dict, allowed: set, *, workers: int, kernel_threads: int,
                              use_smt: bool=False, l3_by_cpu: dict|None=None) -> list[set[int]]:
    """Partition an allowed CPU set into disjoint worker affinities.

    Whole worker groups are kept inside one L3 group whenever possible.  With
    SMT enabled, siblings from the same physical core stay adjacent so a
    12-thread worker on a 6-core/2-way-SMT CCD consumes that CCD as one unit.
    """
    if workers < 1 or kernel_threads < 1 or not allowed or not allowed <= topology.keys():
        raise ValueError('invalid affinity group request')
    by_core: dict[tuple, list[int]] = {}
    for cpu in sorted(allowed):
        by_core.setdefault(tuple(topology[cpu]), []).append(cpu)
    core_rows=[]
    for core,cpus in sorted(by_core.items()):
        chosen=sorted(cpus) if use_smt else [min(cpus)]
        if l3_by_cpu is None:
            l3=('NO_L3',core[0])
        else:
            vals={l3_by_cpu[c] for c in chosen}
            if len(vals)!=1:
                raise ValueError('physical core spans multiple L3 groups')
            l3=next(iter(vals))
        core_rows.append((l3,core,chosen))
    buckets: dict[object,list[int]]={}
    for l3,core,cpus in core_rows:
        buckets.setdefault(l3,[]).extend(cpus)
    need=workers*kernel_threads
    available=sum(len(v) for v in buckets.values())
    if need>available:
        raise ValueError(f'requested slots {need} exceed available {available}')
    if not use_smt:
        for v in buckets.values():
            v.sort()
    groups=[]
    for _ in range(workers):
        enough=[k for k,v in buckets.items() if len(v)>=kernel_threads]
        if enough:
            key=sorted(enough,key=lambda k:(-len(buckets[k]),str(k)))[0]
            group=set(buckets[key][:kernel_threads]);del buckets[key][:kernel_threads]
        else:
            group=set();remaining=kernel_threads
            for key in sorted(buckets,key=lambda k:(-len(buckets[k]),str(k))):
                if not remaining:break
                take=min(remaining,len(buckets[key]))
                group.update(buckets[key][:take]);del buckets[key][:take];remaining-=take
            if remaining:
                raise ValueError('could not form complete affinity group')
        groups.append(group)
    if any(len(g)!=kernel_threads for g in groups) or len(set().union(*groups))!=need:
        raise RuntimeError('affinity partition is not disjoint and complete')
    return groups


def _parse_cpu_list(text:str) -> list[int]:
    out=[]
    for field in text.strip().split(','):
        if not field:continue
        if '-' in field:
            a,b=(int(x) for x in field.split('-',1));out.extend(range(a,b+1))
        else:out.append(int(field))
    return sorted(set(out))


def read_linux_cpu_metadata(sys_cpu_root: Path, allowed: set[int]) -> dict:
    if not allowed:
        raise ValueError('empty allowed CPU set')
    siblings={};l3_by_cpu={}
    for cpu in sorted(allowed):
        base=sys_cpu_root/f'cpu{cpu}'
        sf=base/'topology'/'thread_siblings_list'
        sib=[x for x in _parse_cpu_list(sf.read_text()) if x in allowed] if sf.exists() else [cpu]
        siblings[cpu]=sib or [cpu]
        found=None
        cache=base/'cache'
        if cache.exists():
            for idx in sorted(cache.glob('index*')):
                try:
                    if (idx/'level').read_text().strip()!='3':continue
                    typ=(idx/'type').read_text().strip()
                    if typ not in ('Unified','Data'):continue
                    vals=[x for x in _parse_cpu_list((idx/'shared_cpu_list').read_text()) if x in allowed]
                    if vals:
                        found=','.join(str(x) for x in vals);break
                except OSError:
                    continue
        if found is None:
            found=f'cpu{cpu}'
        l3_by_cpu[cpu]=found
    unique={tuple(_parse_cpu_list(v)) for v in l3_by_cpu.values()}
    return dict(thread_siblings=siblings,l3_by_cpu=l3_by_cpu,l3_groups=[list(x) for x in sorted(unique)])

if __name__=='__main__':
    print(json.dumps(inspect_host(),indent=2))
