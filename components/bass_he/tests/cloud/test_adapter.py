from bass_he.cloud.adapter import run_case
from bass_he.cloud.contracts import CaseSpec
from bass_he.replay_contract import WRONG_PAIR,CONTROL_PAIR,CONTROL_SEED

def fields(pair):return {'source':'test','backend':'python','depth':64,'pair':pair,'seed':{'complex':[CONTROL_SEED.real,CONTROL_SEED.imag]}}
def test_wrong_pair_is_rejected():
    assert run_case(CaseSpec('wrong_pair_check',fields(WRONG_PAIR))).status=='WRONG_PAIR'
def test_one_control_roundtrip():
    out=run_case(CaseSpec('control',fields(CONTROL_PAIR)))
    assert out.status=='PASS'
    assert out.payload['ep']['pair_membership']['passed'] is True

def test_endpoint_seed_roundtrip():
    from bass_he.replay_contract import BRANCHES
    a,b,seed=next(iter(BRANCHES.values()))
    spec=CaseSpec('endpoint',{'source':'test','backend':'python','depth':64,'pair':(a,b),'seed':{'complex':[seed.real,seed.imag]}})
    out=run_case(spec)
    assert out.status=='PASS' and out.payload['distance']<=1e-8
