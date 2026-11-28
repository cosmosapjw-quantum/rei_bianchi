import hashlib, json, tarfile
from pathlib import Path
from bass_he.cloud.contracts import CaseSpec,CaseOutcome,ExecutionBinding,outcome_document,task_id
from bass_he.cloud.store import ResultStore
from bass_he.cloud.export import export_checkpoint
BIND=ExecutionBinding('c','t','r','python',{},'cpu',{})
def test_export_only_complete_artifacts(tmp_path):
    st=ResultStore(tmp_path/'run',BIND);st.begin_epoch()
    s=CaseSpec('wrong_pair_check',{'source':'s','backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
    a=st.claim(s);p=st.attempt_path(a);p.write_text(json.dumps(outcome_document(s,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),BIND,a))+'\n');st.commit(a,p)
    receipt=export_checkpoint(st,tmp_path/'export')
    assert receipt.artifacts==1 and hashlib.sha256(__import__('pathlib').Path(receipt.segment).read_bytes()).hexdigest()==receipt.sha256
    with tarfile.open(receipt.segment) as tar:
        names=tar.getnames();assert 'RUN_BINDING.json' in names and f'results/{task_id(s)}/result.json' in names and 'controller.sqlite' in names
    assert receipt.provider_uploads=='NOT_RUN' and receipt.restore=='NOT_RUN'
    st.close()

def test_checkpoint_segments_have_unique_create_only_names(tmp_path):
    st=ResultStore(tmp_path/'run',BIND);st.begin_epoch()
    (st.root/'RUN_PROFILE.json').write_text('{"storage_mode":"local_sandbox"}\n')
    first=export_checkpoint(st,tmp_path/'export')
    second=export_checkpoint(st,tmp_path/'export')
    assert first.segment!=second.segment
    assert Path(first.segment).name.startswith('checkpoint-')
    assert Path(second.segment).name.startswith('checkpoint-')
    st.close()
