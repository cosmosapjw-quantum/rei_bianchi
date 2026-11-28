"""Read-only Linux intake and conservative single-host MPI rank planning."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess

GiB=1024**3


def read(path):
    p=Path(path)
    if p.stat().st_size>1024*1024:raise ValueError('metadata cap')
    return p.read_text().strip()


def cpulist(value):
    out=set()
    for part in value.split(','):
        if not part:continue
        ends=part.split('-');lo=int(ends[0]);hi=int(ends[-1])
        if lo<0 or hi<lo or hi>1048576:raise ValueError('CPU list bound')
        out.update(range(lo,hi+1))
    return sorted(out)


def identity(path):
    p=Path(path).resolve(strict=True)
    if not p.is_file() or p.stat().st_size>512*1024**2:raise ValueError('identity bound')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return {'path':str(p),'sha256':h.hexdigest(),'bytes':p.stat().st_size}


def ancestor_limits(leaf,root,version):
    leaf,root=Path(leaf),Path(root)
    if not leaf.is_relative_to(root):raise ValueError('cgroup outside mount')
    result=[]
    for p in (leaf,*leaf.parents):
        if not p.is_relative_to(root):break
        row={'path':str(p),'version':version}
        if version==2:
            if (p/'cpu.max').exists():
                q,period=read(p/'cpu.max').split()
                if q!='max':row['quota']=str(Fraction(int(q),int(period)))
            if (p/'memory.max').exists():
                n=read(p/'memory.max')
                if n!='max':row['memory_limit']=int(n);row['memory_current']=int(read(p/'memory.current'))
        else:
            if (p/'cpu.cfs_quota_us').exists():
                q=int(read(p/'cpu.cfs_quota_us'))
                if q>=0:row['quota']=str(Fraction(q,int(read(p/'cpu.cfs_period_us'))))
            if (p/'memory.limit_in_bytes').exists():
                n=int(read(p/'memory.limit_in_bytes'))
                if n<2**60:row['memory_limit']=n;row['memory_current']=int(read(p/'memory.usage_in_bytes'))
        result.append(row)
        if p==root:break
    return result


def cgroup_intake(proc=Path('/proc')):
    memberships=[]
    for line in read(proc/'self/cgroup').splitlines():
        _,ctls,path=line.split(':',2);memberships.append((set(ctls.split(',')),path))
    records=[];errors=[]
    for line in read(proc/'self/mountinfo').splitlines():
        left,right=line.split(' - ',1);a=left.split();b=right.split()
        if b[0] not in ('cgroup','cgroup2'):continue
        unescape=lambda s:re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),s)
        root,mount=unescape(a[3]),Path(unescape(a[4]));version=2 if b[0]=='cgroup2' else 1
        controllers=set(b[2].split(','))
        for ctls,path in memberships:
            if not ((version==2 and ctls=={''}) or (version==1 and ctls&controllers)):continue
            try:
                if '..' in Path(path).parts:raise ValueError('unresolved cgroup namespace path')
                relative=Path(path).relative_to(root)
                records.extend(ancestor_limits(mount/relative,mount,version))
            except (OSError,ValueError) as exc:errors.append(str(exc))
    return {'ancestors':records,'errors':errors,'scope':'all visible ancestors through each mounted hierarchy root; hidden host namespace ancestors not observable'}


def detect():
    allowed=sorted(os.sched_getaffinity(0));cpus=[];errors=[]
    for n in allowed:
        base=Path('/sys/devices/system/cpu')/('cpu'+str(n))
        try:
            nodes=sorted(int(p.name[4:]) for p in base.glob('node[0-9]*'))
            cpus.append({'os_cpu':n,'package':int(read(base/'topology/physical_package_id')),
                         'core':int(read(base/'topology/core_id')),'thread_siblings':cpulist(read(base/'topology/thread_siblings_list')),
                         'numa_nodes':nodes})
        except (OSError,ValueError) as exc:errors.append({'cpu':n,'error':str(exc)})
    mem={}
    for line in read('/proc/meminfo').splitlines():
        key,rest=line.split(':',1)
        if key in ('MemTotal','MemAvailable'):mem[key]=int(rest.split()[0])*1024
    cg=cgroup_intake()
    return {'affinity_os_cpus':allowed,'cpus':cpus,'memory_total_bytes':mem.get('MemTotal'),
            'memory_available_bytes':mem.get('MemAvailable'),'cgroup':cg,'errors':errors,
            'logical_cpu_count':len(allowed),'physical_cores_in_affinity':len({(x['package'],x['core']) for x in cpus})}


def plan(host,*,smt=False,reserve_bytes=16*GiB,worker_bytes=GiB,coordinator_bytes=GiB,requested_ranks=None):
    if type(smt) is not bool or not 0<=reserve_bytes<=16*GiB or not 16*1024**2<=worker_bytes<=GiB or not 16*1024**2<=coordinator_bytes<=GiB:
        raise ValueError('bounded integer resource policy required')
    if any(type(x) is not int for x in (reserve_bytes,worker_bytes,coordinator_bytes)):raise ValueError('integer byte caps required')
    reasons=[];groups={}
    for c in sorted(host['cpus'],key=lambda x:(x['package'],x['core'],x['os_cpu'])):
        if c['os_cpu'] not in host['affinity_os_cpus']:raise ValueError('CPU outside OS affinity')
        groups.setdefault((c['package'],c['core']),[]).append(c['os_cpu'])
    selected=([n for level in range(max(map(len,groups.values()),default=0)) for g in groups.values() if level<len(g) for n in [g[level]]]
              if smt else [g[0] for g in groups.values()])
    quotas=[Fraction(x['quota']) for x in host['cgroup']['ancestors'] if 'quota'in x]
    quota=min(quotas) if quotas else Fraction(len(host['affinity_os_cpus']))
    cpu_budget=min(64,len(host['affinity_os_cpus']),len(selected),quota.numerator//quota.denominator)
    mems=[128*GiB,host.get('memory_available_bytes'),host.get('memory_total_bytes')]
    if any(x is None for x in mems):reasons.append('MEMORY_OBSERVATION_MISSING');available=0
    else:
        mems += [max(0,x['memory_limit']-x['memory_current']) for x in host['cgroup']['ancestors'] if 'memory_limit'in x]
        available=min(mems)
    job_memory=max(0,min(112*GiB,available-reserve_bytes))
    memory_ranks=(1+(job_memory-coordinator_bytes)//worker_bytes) if job_memory>=max(coordinator_bytes,worker_bytes) else 0
    capacity=max(0,min(cpu_budget,memory_ranks))
    if host.get('errors') or host['cgroup'].get('errors'):reasons.append('TOPOLOGY_OR_CGROUP_INCOMPLETE')
    if len(host['cpus'])!=len(host['affinity_os_cpus']):reasons.append('CPU_TOPOLOGY_INCOMPLETE')
    if not cpu_budget:reasons.append('LESS_THAN_ONE_CPU_BUDGET')
    if not memory_ranks:reasons.append('MEMORY_RESERVE_LEAVES_NO_RANK')
    ranks=capacity
    if requested_ranks is not None:
        if type(requested_ranks)is not int or requested_ranks<1 or requested_ranks>64:raise ValueError('ranks must be 1..64')
        if requested_ranks>capacity:reasons.append('REQUESTED_RANKS_EXCEED_RESOURCE_BUDGET')
        ranks=min(requested_ranks,capacity)
    workers=(ranks-1 if ranks>1 else ranks)
    return {'schema':'WU088_NCP64_HOST_PLAN_V1','status':'BLOCKED' if reasons else 'PLAN_READY',
            'blocked_reasons':reasons,'mode':'SMT_EXPLICIT' if smt else 'PHYSICAL_ONLY',
            'rank_count':ranks,'worker_count':workers,'coordinator_reserved_ranks':int(ranks>1),
            'rank1_mode':'sequential coordinator/worker fallback','rank_os_cpus':selected[:ranks],
            'cpu_budget':cpu_budget,'quota_cpu_equivalent':str(quota),'job_memory_budget_bytes':job_memory,
            'observed_available_memory_bytes':available,'reserve_bytes':reserve_bytes,
            'worker_bytes':worker_bytes,'coordinator_bytes':coordinator_bytes,
            'threads_per_worker':1,'calibration_total_ranks':[n for n in (1,2,4,8,16,32,64) if n<=capacity],
            'precision_policy':'unchanged manifest/native precision at every calibration rank count',
            'binding_strategy':'OpenMPI unbound local slots, then rank_guard pins exact OS CPU before exec and records readback',
            'aggregate_memory_enforcement':'sampled RSS watchdog, not a newly created hard cgroup',
            'performance_claim':None,'host':host}


def mpi_tools():
    found={};blocked=[]
    for name,args in [('mpirun',['--version']),('mpifort',['--showme:version'])]:
        exe=shutil.which(name,path='/usr/local/bin:/usr/bin:/bin')
        if not exe:blocked.append('MISSING_'+name.upper());continue
        try:
            r=subprocess.run([exe,*args],capture_output=True,text=True,timeout=5,env={'PATH':'/usr/local/bin:/usr/bin:/bin','LC_ALL':'C'},check=False)
            text=(r.stdout+r.stderr)[:16384]
            match=re.search(r'(?:Open MPI|OpenRTE|Open MPI Fortran)[^\n]*?\b([45])\.\d+',text,re.I)
            if r.returncode or not match:blocked.append('UNSUPPORTED_'+name.upper());continue
            found[name]={**identity(exe),'command_path':str(Path(exe).absolute()),'version':text,'major':int(match[1])}
        except (OSError,subprocess.SubprocessError) as exc:blocked.append(name+':'+str(exc))
    if len(found)==2 and found['mpirun']['major']!=found['mpifort']['major']:blocked.append('MPI_WRAPPER_MAJOR_MISMATCH')
    return {'tools':found,'blocked_reasons':blocked,'version_scope':'OpenMPI 4 or 5; installation/library ABI still requires native build receipt'}


if __name__=='__main__':
    print(json.dumps({'plan':plan(detect()),'mpi':mpi_tools()},indent=2))
