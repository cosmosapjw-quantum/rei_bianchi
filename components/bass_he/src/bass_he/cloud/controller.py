"""DR11 replay stage barriers over immutable independently computed cases."""
from __future__ import annotations
from dataclasses import dataclass
import time
from .contracts import CaseSpec, task_id, digest
from .supervisor import Supervisor
from bass_he.replay_contract import BRANCHES, CONTROL_PAIR, WRONG_PAIR, CONTROL_SEED, DEPTH, FRACTIONS, PANELS, panel_limit

@dataclass(frozen=True)
class RunReturn:
    status: str
    stage: str
    completed: int
    failures: dict
    scientific_PROMOTE: str='HOLD_PENDING_RE_REVIEW'

class Controller:
    def __init__(self,store,workers=1,supervisor=None,worker_cap=None,retry_failed=False,checkpoint=None):
        self.store=store;self.workers=workers;self.supervisor=supervisor or Supervisor(store.binding);self.worker_cap=worker_cap or (lambda ready:min(workers,ready));self.retry_failed=retry_failed;self.dispatch_deadline=None
        if checkpoint is None and hasattr(store,'root'):
            from .export import export_checkpoint
            checkpoint=lambda:export_checkpoint(store,store.root/'exports')
        self.checkpoint=checkpoint
        self.source=store.binding.scientific_source_id or store.binding.source_commit+':'+store.binding.source_tree
    def _common(self,pair,seed):return {'source':self.source,'backend':'python','depth':DEPTH,'pair':pair,'seed':{'complex':[seed.real,seed.imag]}}
    def initial_specs(self):
        return [CaseSpec('wrong_pair_check',self._common(WRONG_PAIR,CONTROL_SEED)),CaseSpec('control',self._common(CONTROL_PAIR,CONTROL_SEED))]
    def endpoint_specs(self):return {name:CaseSpec('endpoint',self._common((a,b),seed)) for name,(a,b,seed) in BRANCHES.items()}
    def geometry_specs(self,eps,fractions):
        specs={}
        for name,(a,b,seed) in BRANCHES.items():
            ep=eps[name].payload['ep'];cert=digest(ep);rho_base=ep['R']['complex'][0]
            for fraction in fractions:
                rho=float(fraction*rho_base)
                for panels in PANELS:
                    key=(name,fraction,panels)
                    specs[key]=CaseSpec('geometry',{'source':self.source,'backend':'python','depth':DEPTH,'pair':(a,b),'endpoint':ep,'certificate_sha256':cert,'rho':rho,'panels':panels,'path':'named_sheet_continuation'})
        return specs
    def _stage(self,specs,expected='PASS'):
        values=list(specs.values()) if isinstance(specs,dict) else list(specs)
        prior={task_id(s):self.store.failure(task_id(s)) for s in values if self.store.failure(task_id(s)) is not None}
        if prior and not self.retry_failed:return None,prior
        ready=sum(self.store.load(task_id(s)) is None for s in values)
        cap=self.worker_cap(ready) if ready else 1
        if cap<1:return None,{'_stage':{'status':getattr(self.worker_cap,'pause_reason',None) or 'RESOURCE_PAUSED','remaining':ready}}
        report=self.supervisor.run_ready(values,cap,self.store,retry_failed=self.retry_failed,dispatch_limit=self.worker_cap,dispatch_deadline=self.dispatch_deadline,checkpoint=self.checkpoint)
        if report.failures:return None,report.failures
        for spec in (specs.values() if isinstance(specs,dict) else specs):
            out=report.outcomes.get(task_id(spec))
            want='WRONG_PAIR' if spec.kind=='wrong_pair_check' else expected
            if out is None or out.status!=want:return None,{task_id(spec):{'status':'STAGE_GATE_FAILED','observed':out.status if out else None}}
        return report.outcomes,{}
    def _panels_pass(self,specs,outcomes):
        for name in BRANCHES:
            for fraction in sorted({k[1] for k in specs}):
                a=outcomes[task_id(specs[(name,fraction,32)])].payload['delta'];b=outcomes[task_id(specs[(name,fraction,64)])].payload['delta']
                if abs(a-b)/b>panel_limit(fraction):return False
        return True
    def run(self):
        total=0;self.dispatch_deadline=time.monotonic()+3600
        try:
            specs=self.initial_specs();results,fail=self._stage(specs)
            if fail:return RunReturn('BLOCKED','source_control',total,fail)
            total+=len(specs)
            if self.checkpoint:self.checkpoint()
            epspecs=self.endpoint_specs();results,fail=self._stage(epspecs)
            if fail:return RunReturn('BLOCKED','endpoints',total,fail)
            eps={name:results[task_id(s)] for name,s in epspecs.items()};total+=len(epspecs)
            if self.checkpoint:self.checkpoint()
            d0=self.geometry_specs(eps,(0.0,));results,fail=self._stage(d0)
            if fail:return RunReturn('BLOCKED','d0',total,fail)
            if not self._panels_pass(d0,results):return RunReturn('BLOCKED','d0_gate',total,{'panel_convergence':'FAILED'})
            total+=len(d0)
            if self.checkpoint:self.checkpoint()
            finite=self.geometry_specs(eps,FRACTIONS[1:]);results,fail=self._stage(finite)
            if fail:return RunReturn('BLOCKED','finite_rho',total,fail)
            if not self._panels_pass(finite,results):return RunReturn('BLOCKED','finite_rho_gate',total,{'panel_convergence':'FAILED'})
            total+=len(finite)
            if self.checkpoint:self.checkpoint()
            return RunReturn('PASS','closeout',total,{})
        finally:self.supervisor.close()
