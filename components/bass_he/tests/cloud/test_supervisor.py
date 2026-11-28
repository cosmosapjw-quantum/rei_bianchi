import ctypes, os, time
from bass_he.cloud.contracts import CaseSpec,CaseOutcome,ExecutionBinding
from bass_he.cloud.store import ResultStore
from bass_he.cloud.supervisor import Supervisor
BIND=ExecutionBinding('c','t','r','python',{},'cpu',{})
def native_sleep(spec):
    ctypes.CDLL(None).sleep(5)
    return CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'})
def immediate(spec):return CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'})
def spec():return CaseSpec('wrong_pair_check',{'source':'s','backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
def test_native_sleep_timeout_reaped(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,deadline=.15,grace=.05,runner=native_sleep)
    start=time.monotonic();report=su.run_ready([spec()],1,st);e=next(iter(report.failures.values()))
    assert e['status']=='TIME_BUDGET_EXCEEDED' and e['alive'] is False and e['exit_code'] is not None
    assert time.monotonic()-start<4;su.close();st.close()
def test_shutdown_leaves_no_owned_workers(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,runner=immediate);report=su.run_ready([spec()],1,st)
    assert not report.failures;ps=[x['process'] for x in su.slots];su.close()
    assert all(not p.is_alive() for p in ps);st.close()

def selective(spec):
    if spec.science_fields['source']=='slow':ctypes.CDLL(None).sleep(5)
    return CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'})
def test_one_worker_kill_preserves_other_commits(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,deadline=.3,grace=.05,runner=selective)
    fast=spec();slow=CaseSpec('wrong_pair_check',{**fast.science_fields,'source':'slow'})
    report=su.run_ready([fast,slow],2,st)
    assert len(report.receipts)==1 and len(report.failures)==1
    assert next(iter(report.failures.values()))['alive'] is False
    su.close();st.close()

def two_calls(spec,on_call):
    on_call('first');time.sleep(.12)
    on_call('second');time.sleep(.12)
    return CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'})
def test_deadline_is_per_numerical_call(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,deadline=.2,runner=two_calls,heartbeat=True)
    report=su.run_ready([spec()],1,st)
    assert not report.failures and len(report.receipts)==1
    su.close();st.close()
def test_expired_pilot_budget_dispatches_nothing(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,runner=immediate)
    report=su.run_ready([spec()],1,st,dispatch_deadline=time.monotonic()-1)
    assert report.failures['_stage']['status']=='PILOT_DISPATCH_BUDGET'
    assert st.db.execute('SELECT count(*) FROM tasks').fetchone()[0]==0
    su.close();st.close()

def test_soft_limit_stops_new_dispatch(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,runner=immediate)
    first=spec();second=CaseSpec('wrong_pair_check',{**first.science_fields,'source':'second'})
    def limit(_ready):return 1 if st.db.execute("SELECT count(*) FROM tasks WHERE state='COMMITTED'").fetchone()[0]==0 else 0
    report=su.run_ready([first,second],1,st,dispatch_limit=limit)
    assert len(report.receipts)==1 and report.failures['_stage']['status']=='RESOURCE_PAUSED_OR_WORKERS_UNAVAILABLE'
    assert st.db.execute('SELECT count(*) FROM tasks').fetchone()[0]==1
    su.close();st.close()

def test_elapsed_checkpoint_occurs_during_active_case(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,deadline=1,runner=two_calls,heartbeat=True)
    times=[]
    report=su.run_ready([spec()],1,st,checkpoint=lambda:times.append(time.monotonic()),checkpoint_interval=.05)
    assert not report.failures and times
    su.close();st.close()

def test_zero_dynamic_capacity_starts_no_worker(tmp_path,monkeypatch):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,runner=immediate)
    monkeypatch.setattr(su,'_start',lambda: (_ for _ in ()).throw(AssertionError('worker started')))
    report=su.run_ready([spec()],1,st,dispatch_limit=lambda ready:0)
    assert report.failures['_stage']['status']=='RESOURCE_PAUSED'
    su.close();st.close()

def test_storage_soft_pause_preserves_committed_worker_result(tmp_path):
    st=ResultStore(tmp_path,BIND);su=Supervisor(BIND,runner=immediate)
    first=spec();second=CaseSpec('wrong_pair_check',{**first.science_fields,'source':'second'})
    class StorageCapacity:
        pause_reason=None
        def __call__(self,ready,active=0):
            if st.db.execute("SELECT count(*) FROM tasks WHERE state='COMMITTED'").fetchone()[0]:
                self.pause_reason='BLOCKED_STORAGE_HEADROOM';return 0
            return 1
    report=su.run_ready([first,second],1,st,dispatch_limit=StorageCapacity())
    assert len(report.receipts)==1
    assert report.failures['_stage']['status']=='BLOCKED_STORAGE_HEADROOM'
    assert st.load(next(iter(report.receipts))) is not None
    assert st.db.execute('SELECT count(*) FROM tasks').fetchone()[0]==1
    su.close();st.close()
