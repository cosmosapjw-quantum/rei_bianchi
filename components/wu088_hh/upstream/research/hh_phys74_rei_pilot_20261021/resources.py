"""Linux advisory cooperative capacity leases. Never inspect process names or kill peers.

A lease limits cooperating launchers, not arbitrary noncooperating processes.
Kernel free-memory and sampled busy CPU observations constrain each new admission.
Existing work is not cancelled when another session becomes busy.
"""
from __future__ import annotations
import contextlib,fcntl,json,math,os,time,uuid
from pathlib import Path

GIB=1024**3

def _start(pid):
    try:
        text=Path(f'/proc/{pid}/stat').read_text()
        return text[text.rfind(')')+2:].split()[19]
    except (FileNotFoundError,ProcessLookupError):return 'DEAD'
    except (PermissionError,OSError):return None


def _cgroups():
    root=Path('/sys/fs/cgroup')
    try:
        rel=next(x.split(':',2)[2] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
        leaf=root/rel.lstrip('/')
        if not leaf.is_dir():leaf=root
        return [leaf,*[p for p in leaf.parents if p==root or root in p.parents]]
    except (OSError,StopIteration):return [root]


def cpu_limit():
    cpus=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1
    for p in _cgroups():
        try:
            quota,period=(p/'cpu.max').read_text().split()
            if quota!='max':cpus=min(cpus,max(1,math.floor(int(quota)/int(period))))
        except (OSError,ValueError):pass
    return max(1,cpus)


def memory_available():
    info={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines())}
    avail=info['MemAvailable'];capacity=info['MemTotal']
    for p in _cgroups():
        try:
            limit=(p/'memory.max').read_text().strip()
            if limit!='max':
                limit=int(limit);used=int((p/'memory.current').read_text())
                capacity=min(capacity,limit);avail=min(avail,max(0,limit-used))
        except (OSError,ValueError):pass
    return avail,capacity


def _cpu_snapshot():
    ids=set(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else set(range(os.cpu_count() or 1))
    out={}
    for line in Path('/proc/stat').read_text().splitlines():
        fields=line.split();tag=fields[0] if fields else ''
        if tag.startswith('cpu') and tag[3:].isdigit() and int(tag[3:]) in ids:
            v=list(map(int,fields[1:9]));out[tag]=(sum(v),v[3]+v[4])
    return out


def busy_cores(interval=.08):
    try:
        a=_cpu_snapshot();time.sleep(interval);b=_cpu_snapshot()
        return sum(max(0.,1-(b[k][1]-v[1])/(b[k][0]-v[0])) for k,v in a.items() if k in b and b[k][0]>v[0])
    except (OSError,ValueError):return max(0.,os.getloadavg()[0])


def slots(cap,busy,available_gib,capacity_gib,reserve_gib,job_gib,leased_cpus,leased_gib):
    if cap<1 or job_gib<=0 or reserve_gib<0:raise ValueError('invalid resource budget')
    # Existing resource use and cooperative reservations are independent ceilings.
    c=min(max(0,cap-leased_cpus),max(0,math.floor(cap-busy)))
    m=min(max(0.,available_gib-reserve_gib),max(0.,capacity_gib-reserve_gib-leased_gib))
    return max(0,min(c,math.floor(m/job_gib)))


class LeasePool:
    def __init__(self,path,*,max_cpus=64,memory_gib=128.,reserve_gib=16.,job_gib=1.):
        self.path=Path(path).resolve();self.path.mkdir(parents=True,exist_ok=True)
        self.capacity=cpu_limit();self.cap=min(max_cpus,self.capacity);self.memory_gib=memory_gib
        self.reserve=reserve_gib;self.job=job_gib
        if self.cap<1 or self.job<=0 or self.reserve<0:raise ValueError('invalid budgets')
        self.owner=f'{os.getpid()}-{uuid.uuid4().hex}'
        self.start=_start(os.getpid())
        self.boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()

    @contextlib.contextmanager
    def locked(self):
        with (self.path/'leases.lock').open('a+') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(stream,fcntl.LOCK_UN)

    def _live(self):
        live=[]
        for p in self.path.glob('lease-*.json'):
            try:r=json.loads(p.read_text())
            except (OSError,ValueError):raise RuntimeError('unreadable cooperative lease: '+str(p))
            tick=_start(r['pid'])
            dead=r['boot']!=self.boot or tick=='DEAD' or (tick is not None and r['start'] is not None and tick!=r['start'])
            if dead:p.unlink(missing_ok=True)
            else:live.append(r)
        return live

    def acquire(self,task):
        busy=busy_cores();free,total=memory_available()
        with self.locked():
            live=self._live()
            affinity=len(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else os.cpu_count() or 1
            effective_busy=max(0.,self.capacity-max(0.,affinity-busy))
            n=slots(self.capacity,effective_busy,free/GIB,min(total/GIB,self.memory_gib),self.reserve,self.job,
                    sum(x['cpus'] for x in live),sum(x['gib'] for x in live))
            if n==0:return None,dict(cap=self.cap,allocation_cpus=self.capacity,busy_cores=busy,available_gib=free/GIB,capacity_gib=min(total/GIB,self.memory_gib),slots=0)
            key=uuid.uuid4().hex
            r=dict(owner=self.owner,pid=os.getpid(),start=self.start,boot=self.boot,cpus=1,gib=self.job,task=task)
            (self.path/f'lease-{key}.json').write_text(json.dumps(r,sort_keys=True)+'\n')
            return key,dict(cap=self.cap,allocation_cpus=self.capacity,busy_cores=busy,available_gib=free/GIB,capacity_gib=min(total/GIB,self.memory_gib),slots=n)

    def release(self,key):
        with self.locked():
            p=self.path/f'lease-{key}.json'
            if not p.exists():return
            r=json.loads(p.read_text())
            if r['owner']!=self.owner:raise RuntimeError('foreign lease release refused')
            p.unlink()
