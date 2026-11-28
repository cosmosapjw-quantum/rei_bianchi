from bass_he.cloud.controller import Controller
from bass_he.cloud.contracts import ExecutionBinding, CaseOutcome,task_id
from bass_he.replay_contract import BRANCHES
class Store:
    binding=ExecutionBinding('c','t','r','python',{},'cpu',{})
class Outcome:
    def __init__(self):self.payload={'ep':{'R':{'complex':[1.,1.]},'certificate':{'simple_fold':True},'pair_membership':{'passed':True}}}

def test_exact_7_14_42_workload():
    c=Controller(Store())
    assert len(c.endpoint_specs())==7
    eps={n:Outcome() for n in BRANCHES}
    assert len(c.geometry_specs(eps,(0.,)))==14
    assert len(c.geometry_specs(eps,(.25,.5,.75)))==42

def test_panel_tasks_independent():
    c=Controller(Store());eps={n:Outcome() for n in BRANCHES};cases=c.geometry_specs(eps,(0.,))
    name=next(iter(BRANCHES));a=cases[name,0.,32];b=cases[name,0.,64]
    assert task_id(a)!=task_id(b) and a.science_fields['panels']==32 and b.science_fields['panels']==64

def test_no_finite_rho_before_full_d0_gate():
    class Fake(Controller):
        def __init__(self):super().__init__(Store());self.stages=[]
        def _stage(self,specs,expected='PASS'):
            self.stages.append(len(specs))
            if len(specs)==14:return None,{'d0':'FAILED'}
            if len(specs)==7:return {task_id(s):Outcome() for s in specs.values()},{}
            return {task_id(s):CaseOutcome('WRONG_PAIR' if s.kind=='wrong_pair_check' else 'PASS',{}, {}) for s in specs},{}
    c=Fake();result=c.run()
    assert result.stage=='d0' and c.stages==[2,7,14]

def test_cached_stage_advances_while_soft_memory_paused(tmp_path):
    import json
    from bass_he.cloud.contracts import CaseSpec,CaseOutcome,outcome_document
    from bass_he.cloud.store import ResultStore
    bind=ExecutionBinding('c','t','r','python',{},'cpu',{})
    st=ResultStore(tmp_path,bind);st.begin_epoch()
    spec=CaseSpec('wrong_pair_check',{'source':'s','backend':'python','depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
    attempt=st.claim(spec);path=st.attempt_path(attempt)
    path.write_text(json.dumps(outcome_document(spec,CaseOutcome('WRONG_PAIR',{}, {'reason':'pair membership rejected'}),bind,attempt))+'\n')
    st.commit(attempt,path)
    c=Controller(st,worker_cap=lambda ready:0)
    outcomes,fail=c._stage([spec])
    assert not fail and outcomes[task_id(spec)].status=='WRONG_PAIR'
    c.supervisor.close();st.close()
