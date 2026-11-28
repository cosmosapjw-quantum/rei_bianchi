import json,pytest
from bass_he.cloud.contracts import CaseSpec,CaseOutcome,ExecutionBinding,outcome_document,task_id
from bass_he.cloud.store import ResultStore
BIND=ExecutionBinding('c','t','r','python',{},'cpu',{})
def case():return CaseSpec('wrong_pair_check',{'source':'s','backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
def test_final_before_ledger_no_recompute(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=case();a=st.claim(s);p=st.attempt_path(a)
    p.write_text(json.dumps(outcome_document(s,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),BIND,a))+'\n')
    dest=st._final(task_id(s));dest.parent.mkdir(parents=True);dest.hardlink_to(p)
    st.close();again=ResultStore(tmp_path,BIND)
    assert again.reconcile().recovered==1
    with pytest.raises(FileExistsError):
        again.begin_epoch();again.claim(s)
    again.close()
def test_second_controller_rejected(tmp_path):
    first=ResultStore(tmp_path,BIND)
    with pytest.raises(RuntimeError,match='already owns'):ResultStore(tmp_path,BIND)
    first.close()

def test_stale_epoch_final_is_rejected(tmp_path):
    st=ResultStore(tmp_path,BIND);st.begin_epoch();s=case();a=st.claim(s);p=st.attempt_path(a)
    doc=outcome_document(s,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),BIND,a)
    doc['attempt']['run_epoch']='old-epoch'
    p.write_text(json.dumps(doc)+'\n')
    dest=st._final(task_id(s));dest.parent.mkdir(parents=True);dest.hardlink_to(p)
    with pytest.raises(ValueError,match='mismatch'):st.reconcile()
    st.close()
