"""Seeded bounded worker sweep; PERF computations bypass science result store."""
from dataclasses import dataclass
import random, time
CANDIDATES=(1,8,16,24,32,48,56,64)
@dataclass(frozen=True)
class SweepReport:
    status: str
    selected: int|None
    observations: tuple
    seed: int

def choose(observations):
    valid=[x for x in observations if x['valid']]
    if not valid:return None
    best=max(x['throughput'] for x in valid)
    return min(x['workers'] for x in valid if x['throughput']>=.95*best)

def benchmark(profile,host,workload,budget=900,seed=20260928):
    """workload(workers, repeat) performs fresh PERF-namespace cases and returns timing."""
    if budget>900:raise ValueError('calibration budget exceeds 900s')
    candidates=[x for x in CANDIDATES if x<=host.usable_cpus and x<=len(workload.cases)]
    arms=[(w,r) for w in candidates for r in range(3)];random.Random(seed).shuffle(arms)
    start=time.monotonic();rows=[]
    for workers,repeat in arms:
        if time.monotonic()-start>=budget:break
        result=workload.run_fresh(workers,repeat,start+budget)
        rows.append({'workers':workers,'repeat':repeat,'valid':result['valid'],'throughput':result['throughput'],'elapsed':result['elapsed'],'failures':result.get('failures',{}),'outcome_statuses':result.get('outcome_statuses',{})})
    grouped=[]
    for w in candidates:
        rs=[x for x in rows if x['workers']==w]
        if len(rs)==3:grouped.append({'workers':w,'valid':all(x['valid'] for x in rs),'throughput':sum(x['throughput'] for x in rs)/3})
    return SweepReport('COMPLETE' if len(rows)==len(arms) else 'PARTIAL_BEST_OBSERVED',choose(grouped),tuple(rows),seed)

class PerfWorkload:
    """Fresh result namespace per arm; never consults a science run store."""
    def __init__(self,cases,binding,root,worker_cap=None):
        self.cases=list(cases);self.binding=binding;self.root=root;self.worker_cap=worker_cap
    def run_fresh(self,workers,repeat,dispatch_deadline):
        from pathlib import Path
        from .store import ResultStore
        from .supervisor import Supervisor
        from .contracts import task_id
        root=Path(self.root)/f'arm-{workers}-{repeat}'
        if root.exists():raise FileExistsError('PERF arm already exists')
        start=time.monotonic();store=ResultStore(root,self.binding);supervisor=Supervisor(self.binding)
        try:
            report=supervisor.run_ready(self.cases,workers,store,dispatch_deadline=dispatch_deadline,dispatch_limit=self.worker_cap)
            elapsed=time.monotonic()-start
            valid=not report.failures and len(report.outcomes)==len(self.cases) and all(
                report.outcomes.get(task_id(s)) is not None and report.outcomes[task_id(s)].status==('WRONG_PAIR' if s.kind=='wrong_pair_check' else 'PASS') for s in self.cases)
            return {'valid':valid,'throughput':len(report.outcomes)/elapsed if valid and elapsed else 0.,'elapsed':elapsed,'failures':report.failures,'outcome_statuses':{tid:out.status for tid,out in report.outcomes.items()}}
        finally:supervisor.close();store.close()
