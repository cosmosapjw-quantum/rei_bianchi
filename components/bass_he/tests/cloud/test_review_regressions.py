import json, os, time, tarfile
from pathlib import Path
import pytest
from bass_he.cloud.contracts import CaseSpec,CaseOutcome,ExecutionBinding,outcome_document,task_id
from bass_he.cloud.store import ResultStore
from bass_he.cloud.export import export_checkpoint
from bass_he.cloud.resources import inventory
from bass_he.cloud.supervisor import Supervisor
from bass_he.cloud.benchmark import benchmark,PerfWorkload
BIND=ExecutionBinding('c','t','r','python',{},'cpu',{})
def spec(source='s'):
    return CaseSpec('wrong_pair_check',{'source':source,'backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
def prepare(st):
    st.begin_epoch();s=spec();a=st.claim(s);p=st.attempt_path(a)
    p.write_text(json.dumps(outcome_document(s,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),BIND,a))+'\n')
    return s,a,p

def test_cgroup_root_without_limit_files_is_valid(tmp_path,monkeypatch):
    proc=tmp_path/'proc';proc.mkdir();(proc/'meminfo').write_text('MemTotal: 1024000 kB\n');(proc/'self').mkdir();(proc/'self'/'cgroup').write_text('0::/job\n')
    cg=tmp_path/'cgroup';cg.mkdir();(cg/'cgroup.controllers').write_text('cpu memory');job=cg/'job';job.mkdir()
    (job/'cpu.max').write_text('200000 100000');(job/'memory.max').write_text('1000000000');(job/'memory.current').write_text('1000')
    monkeypatch.setattr(os,'sched_getaffinity',lambda pid:{1,2,3,4})
    host=inventory(tmp_path,proc_root=proc,cgroup_root=cg)
    assert host.quota_cpus==2 and host.effective_memory==1000000000 and not host.unknown_limits

def test_calibration_deadline_is_forwarded_into_arm():
    class Host:usable_cpus=1
    class Work:
        cases=[1]
        def __init__(self):self.deadlines=[]
        def run_fresh(self,w,r,dispatch_deadline):
            self.deadlines.append(dispatch_deadline)
            return {'valid':True,'throughput':1.,'elapsed':.01}
    w=Work();start=time.monotonic();benchmark({},Host(),w,budget=5)
    assert len(w.deadlines)==3 and all(start<d<=start+5.1 for d in w.deadlines)

def fail_then_long(s):
    if s.science_fields['source']=='fail':raise RuntimeError('injected')
    time.sleep(.3);Path(s.science_fields['marker']).write_text('done')
    return CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'})
def test_failure_is_persisted_before_other_worker_finishes(tmp_path):
    marker=tmp_path/'other-done';st=ResultStore(tmp_path/'run',BIND);su=Supervisor(BIND,deadline=2,runner=fail_then_long)
    first=spec('fail');second=CaseSpec('wrong_pair_check',{**spec('other').science_fields,'marker':str(marker)})
    observed=[];original=st.record_failure
    def record(attempt,evidence):observed.append(marker.exists());return original(attempt,evidence)
    st.record_failure=record
    try:
        report=su.run_ready([first,second],2,st)
        assert report.failures and observed==[False]
    finally:su.close();st.close()

def test_new_result_directories_are_fsynced(tmp_path,monkeypatch):
    st=ResultStore(tmp_path/'run',BIND);s,a,p=prepare(st);seen=[];actual=os.fsync
    def fsync(fd):
        seen.append(Path(os.readlink(f'/proc/self/fd/{fd}')))
        return actual(fd)
    monkeypatch.setattr(os,'fsync',fsync)
    try:
        st.commit(a,p)
        assert st.root in seen and st.root/'results' in seen
    finally:st.close()

def test_checkpoint_restores_profile_events_and_result(tmp_path):
    st=ResultStore(tmp_path/'run',BIND);s,a,p=prepare(st);st.commit(a,p)
    (st.root/'RUN_PROFILE.json').write_text('{"storage_mode":"local_sandbox"}\n')
    receipt=export_checkpoint(st,tmp_path/'exports');st.close()
    restored=tmp_path/'restored';restored.mkdir()
    with tarfile.open(receipt.segment) as tar:tar.extractall(restored,filter='data')
    assert (restored/'RUN_PROFILE.json').exists() and (restored/'EVENTS.jsonl').exists()
    again=ResultStore(restored,BIND)
    assert again.load(task_id(s)).status=='WRONG_PAIR';again.close()

def test_calibration_rejects_numerical_rejection(tmp_path,monkeypatch):
    import bass_he.cloud.store as storemod,bass_he.cloud.supervisor as supmod
    class FakeStore:
        def __init__(self,*args):pass
        def close(self):pass
    class FakeSupervisor:
        def __init__(self,*args):pass
        def run_ready(self,*args,**kw):
            return type('Report',(),{'failures':{},'outcomes':{task_id(spec()):CaseOutcome('NUMERICAL_REJECTED',{}, {})}})()
        def close(self):pass
    monkeypatch.setattr(storemod,'ResultStore',FakeStore);monkeypatch.setattr(supmod,'Supervisor',FakeSupervisor)
    workload=PerfWorkload([spec()],BIND,tmp_path)
    assert workload.run_fresh(1,0,time.monotonic()+5)['valid'] is False

def test_controller_checkpoints_each_completed_stage():
    from bass_he.cloud.controller import Controller
    from bass_he.replay_contract import BRANCHES
    class Store:
        binding=BIND
    calls=[]
    class Fake(Controller):
        def _stage(self,specs,expected='PASS'):
            values=specs.values() if isinstance(specs,dict) else specs
            outcomes={}
            for s in values:
                if s.kind=='endpoint':payload={'ep':{'R':{'complex':[1.,1.]},'certificate':{'simple_fold':True},'pair_membership':{'passed':True}}}
                elif s.kind=='geometry':payload={'delta':1.}
                else:payload={}
                outcomes[task_id(s)]=CaseOutcome('WRONG_PAIR' if s.kind=='wrong_pair_check' else 'PASS',payload,{})
            return outcomes,{}
    c=Fake(Store(),checkpoint=lambda: calls.append('checkpoint'))
    assert c.run().status=='PASS'
    assert calls==['checkpoint']*4
