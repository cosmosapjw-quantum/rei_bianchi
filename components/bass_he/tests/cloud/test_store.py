import hashlib, json
import pytest
from bass_he.cloud.contracts import CaseSpec,CaseOutcome,ExecutionBinding,outcome_document,task_id
from bass_he.cloud.store import ResultStore

BIND=ExecutionBinding('c','t','r','python',{},'cpu',{})
def spec():return CaseSpec('wrong_pair_check',{'source':'s','backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
def prepare(store,s):
    a=store.claim(s);p=store.attempt_path(a);p.write_text(json.dumps(outcome_document(s,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),BIND,a))+'\n');return a,p

def test_final_before_db_recovers_without_compute(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s)
    final=st._final(task_id(s));final.parent.mkdir(parents=True);final.hardlink_to(p)
    assert st.reconcile().recovered==1
    assert st.load(task_id(s)).status=='WRONG_PAIR';st.close()
def test_committed_missing_file_is_corrupt(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);st.commit(a,p);st._final(task_id(s)).unlink()
    with pytest.raises(ValueError,match='missing'):st.load(task_id(s))
    st.close()
def test_tampered_payload_is_rejected(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);st.commit(a,p);st._final(task_id(s)).write_text('{}')
    with pytest.raises(ValueError):st.load(task_id(s))
    st.close()
def test_duplicate_conflict_never_overwrites(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);st.commit(a,p)
    with pytest.raises(FileExistsError):st.claim(s)
    st.close()
def test_partial_write_is_not_committed(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a=st.claim(s);p=st.attempt_path(a);p.write_text('{')
    with pytest.raises(json.JSONDecodeError):st.commit(a,p)
    assert st.load(task_id(s)) is None;st.close()
def test_binding_mismatch_stops(tmp_path):
    st=ResultStore(tmp_path,BIND);st.close()
    with pytest.raises(ValueError,match='binding'):ResultStore(tmp_path,ExecutionBinding('other','t','r','python',{},'cpu',{}))
def test_sqlite_export_includes_wal_state(tmp_path):
    import sqlite3
    st=ResultStore(tmp_path/'run',BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);st.commit(a,p);snap=tmp_path/'snap.sqlite';st.snapshot(snap)
    assert sqlite3.connect(snap).execute('SELECT count(*) FROM tasks').fetchone()[0]==1;st.close()

def test_old_epoch_reply_rejected(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);st.begin_epoch()
    with pytest.raises(ValueError,match='stale epoch'):st.commit(a,p)
    st.close()

def test_resume_does_not_recompute_committed(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a,p=prepare(st,s);receipt=st.commit(a,p);st.close()
    again=ResultStore(tmp_path,BIND);again.begin_epoch()
    assert again.load(task_id(s)).status=='WRONG_PAIR'
    with pytest.raises(FileExistsError):again.claim(s)
    assert hashlib.sha256(again._final(task_id(s)).read_bytes()).hexdigest()==receipt.sha256
    again.close()

def test_failed_case_is_not_automatically_retried(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=spec();a=st.claim(s)
    st.record_failure(a,{'status':'TIME_BUDGET_EXCEEDED','pid':123})
    st.close();again=ResultStore(tmp_path,BIND);again.begin_epoch()
    assert again.failure(task_id(s))['pid']==123
    with pytest.raises(RuntimeError,match='explicit operator retry'):again.claim(s)
    again.close()
