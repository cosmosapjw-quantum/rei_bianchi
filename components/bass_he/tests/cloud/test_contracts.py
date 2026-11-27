import pytest
from bass_he.cloud.contracts import CaseSpec, task_id, digest

def spec(rho=0.0,cert='a',backend='python'):
    return CaseSpec('geometry',{'source':'s','backend':backend,'depth':160,'pair':[[3,1,0],[4,1,0]],'endpoint':{'R':{'complex':[1.,2.]}},'certificate_sha256':cert,'rho':rho,'panels':32,'path':'named_sheet_continuation'})

def test_identity_includes_endpoint_certificate_and_backend():
    assert len({task_id(spec()),task_id(spec(cert='b')),task_id(spec(backend='numba'))})==3

def test_nonfinite_rejected_and_neighboring_rho_not_aliased():
    assert task_id(spec(0.25))!=task_id(spec(0.25000000000000006))
    with pytest.raises(ValueError):spec(float('nan'))
    with pytest.raises(ValueError):CaseSpec('geometry',{**spec().science_fields,'panels':True})
