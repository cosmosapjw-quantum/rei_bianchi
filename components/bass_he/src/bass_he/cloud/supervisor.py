"""Persistent spawned workers with owned-process deadline enforcement."""
from __future__ import annotations
from dataclasses import dataclass
import inspect, json, multiprocessing as mp, os, time, traceback
from pathlib import Path
from .contracts import CaseSpec, CaseOutcome, ExecutionBinding, Attempt, outcome_document, task_id

@dataclass(frozen=True)
class StageReport:
    outcomes: dict
    receipts: dict
    failures: dict


def _worker(conn,binding,runner,heartbeat):
    from .backend import prepare_environment
    prepare_environment() # before numerical imports
    try:
        from .backend import activate
        attestation=activate('python')
        if 'hashes' in binding.packages:
            from .runtime import binding as actual_binding
            if actual_binding(Path(__file__).resolve().parents[3]).identity()!=binding.identity():raise RuntimeError('worker source/environment fingerprint mismatch')
        attestation['binding']=binding.identity()
        conn.send(('READY',attestation))
    except BaseException as exc:
        conn.send(('INIT_FAILED',repr(exc)));conn.close();return
    while True:
        try: item=conn.recv()
        except EOFError:break
        if item is None: break
        spec,attempt,path=item
        try:
            outcome=runner(spec,on_call=lambda name:conn.send(('CALL_START',attempt.run_epoch,attempt.task_id,name))) if heartbeat else runner(spec)
            data=(json.dumps(outcome_document(spec,outcome,binding,attempt),sort_keys=True,allow_nan=False)+'\n').encode()
            with Path(path).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            conn.send(('DONE',attempt.run_epoch,attempt.task_id,str(path)))
        except BaseException as exc:
            conn.send(('ERROR',attempt.run_epoch,attempt.task_id,repr(exc),traceback.format_exc()))
    conn.close()

class Supervisor:
    def __init__(self,binding:ExecutionBinding,deadline=120.0,grace=2.0,runner=None,heartbeat=None):
        from .adapter import run_case
        self.binding=binding;self.deadline=deadline;self.grace=grace;self.runner=runner or run_case;self.heartbeat=(runner is None if heartbeat is None else heartbeat);self.ctx=mp.get_context('spawn');self.slots=[]
    def _start(self):
        parent,child=self.ctx.Pipe();p=self.ctx.Process(target=_worker,args=(child,self.binding,self.runner,self.heartbeat));p.start();child.close()
        if not parent.poll(15):
            self._reap(p);raise RuntimeError('worker initialization timeout')
        msg=parent.recv()
        if msg[0]!='READY':self._reap(p);raise RuntimeError(f'worker initialization failed: {msg}')
        if any(msg[1].get(k)!=self.binding.packages[k] for k in ('numpy','scipy') if k in self.binding.packages):
            self._reap(p);raise RuntimeError('worker environment differs from binding')
        return {'process':p,'conn':parent,'attestation':msg[1],'busy':None}
    def _reap(self,p):
        if p.is_alive():p.terminate();p.join(self.grace)
        if p.is_alive():p.kill()
        p.join()
        return {'pid':p.pid,'exit_code':p.exitcode,'alive':p.is_alive()}
    def close(self):
        for slot in self.slots:
            p=slot['process']
            if p.is_alive():
                try:slot['conn'].send(None)
                except (BrokenPipeError,OSError):pass
                p.join(self.grace)
            if p.is_alive():self._reap(p)
            slot['conn'].close()
        self.slots=[]
    def run_ready(self,specs:list[CaseSpec],workers:int,store,retry_failed=False,dispatch_limit=None,dispatch_deadline=None,checkpoint=None,checkpoint_interval=900,observe=None):
        if workers<1:raise ValueError('no eligible worker')
        failures={task_id(s):store.failure(task_id(s)) for s in specs if store.failure(task_id(s)) is not None and not retry_failed}
        pending=[s for s in specs if store.load(task_id(s)) is None and task_id(s) not in failures]
        outcomes={task_id(s):store.load(task_id(s)) for s in specs if store.load(task_id(s)) is not None}
        receipts={}
        if not pending:return StageReport(outcomes,receipts,failures)
        if store.epoch is None:store.begin_epoch()
        def capacity(ready,active):
            if dispatch_limit is None:return workers
            params=inspect.signature(dispatch_limit).parameters
            return dispatch_limit(ready,active) if len(params)>=2 else dispatch_limit(ready)
        initial=min(workers,len(pending),capacity(len(pending),0))
        if initial<1:return StageReport(outcomes,receipts,{'_stage':{'status':getattr(dispatch_limit,'pause_reason',None) or 'RESOURCE_PAUSED','remaining':len(pending)}})
        while len(self.slots)<initial:
            if len(self.slots)>=capacity(len(pending),len(self.slots)):break
            slot=self._start();self.slots.append(slot);store._event('WORKER_READY',**slot['attestation'])
        active={};next_checkpoint=time.monotonic()+checkpoint_interval
        while pending or active:
            budget_expired=dispatch_deadline is not None and time.monotonic()>=dispatch_deadline
            allowed=capacity(len(pending)+len(active),len(active))
            if observe is not None and observe(self.slots) is False:
                for tid,slot in list(active.items()):
                    spec,att,_=slot['busy'];evidence={'status':'BLOCKED_MEMORY_CALIBRATION',**self._reap(slot['process'])}
                    store.record_failure(att,evidence);failures[tid]=evidence;slot['busy']=None;del active[tid]
                failures['_stage']={'status':'BLOCKED_MEMORY_CALIBRATION','remaining':len(pending)}
                break
            for slot in self.slots:
                if not pending or budget_expired or len(active)>=allowed:break
                if slot['busy'] is None and slot['process'].is_alive():
                    spec=pending.pop(0);att=store.claim(spec,retry_failed=retry_failed);path=store.attempt_path(att)
                    slot['conn'].send((spec,att,str(path)));slot['busy']=(spec,att,time.monotonic());active[att.task_id]=slot
            for tid,slot in list(active.items()):
                spec,att,start=slot['busy'];p=slot['process'];conn=slot['conn']
                if conn.poll(0.01):
                    try:msg=conn.recv()
                    except EOFError:msg=('CRASH',)
                    if msg[0]=='CALL_START' and msg[1:3]==(att.run_epoch,att.task_id):
                        slot['busy']=(spec,att,time.monotonic());continue
                    if msg[0]=='DONE' and msg[1:3]==(att.run_epoch,att.task_id):
                        try:
                            receipt=store.commit(att,Path(msg[3]));receipts[tid]=receipt;outcomes[tid]=store.load(tid)
                        except (ValueError,OSError) as exc:failures[tid]={'status':'PAYLOAD_OR_BINDING_MISMATCH','reason':str(exc)}
                    elif msg[0]=='ERROR' and msg[1:3]==(att.run_epoch,att.task_id):
                        failures[tid]={'status':'CASE_EXCEPTION','reason':msg[3],'traceback':msg[4]}
                    else:failures[tid]={'status':'WORKER_CRASH','reason':'stale or malformed worker reply'}
                    if tid in failures:store.record_failure(att,failures[tid])
                    slot['busy']=None;del active[tid]
                elif not p.is_alive():
                    failures[tid]={'status':'WORKER_CRASH',**self._reap(p)};store.record_failure(att,failures[tid]);slot['busy']=None;del active[tid]
                elif time.monotonic()-start>self.deadline:
                    overshoot=time.monotonic()-start-self.deadline
                    evidence=self._reap(p)
                    failures[tid]={'status':'TIME_BUDGET_EXCEEDED','overshoot_seconds':overshoot,**evidence}
                    store.record_failure(att,failures[tid])
                    slot['busy']=None;del active[tid]
            if checkpoint and time.monotonic()>=next_checkpoint:
                checkpoint();next_checkpoint=time.monotonic()+checkpoint_interval
            if pending and not active and (budget_expired or allowed<=0 or all(not x['process'].is_alive() for x in self.slots)):
                failures['_stage']={'status':'PILOT_DISPATCH_BUDGET' if budget_expired else (getattr(dispatch_limit,'pause_reason',None) or 'RESOURCE_PAUSED_OR_WORKERS_UNAVAILABLE'),'remaining':len(pending)}
                break
            time.sleep(.01)
        return StageReport(outcomes,receipts,failures)
