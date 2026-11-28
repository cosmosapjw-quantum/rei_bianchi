import copy
import pytest

from bass_he.spectral import find_exceptional_point
from bass_he.sturm_geometry import contour_geometry

SEED = 1.2125718090356707 + 1.363814370435508j

@pytest.fixture(scope='module')
def ep():
    return find_exceptional_point((1,0,0),(2,1,0),SEED,depth=64)

@pytest.mark.parametrize('mutate', [
    lambda x: x.__setitem__('state_b',(2,0,0)),
    lambda x: x.__setitem__('R',x['R']*1.01),
    lambda x: x.__setitem__('p',x['p']*(1+1e-6)),
    lambda x: x.__setitem__('lam',x['lam']*(1+1e-6)),
    lambda x: x.__setitem__('depth',96),
    lambda x: x.__setitem__('Z1',x['Z1']+0.125),
    lambda x: x.__setitem__('Z2',x['Z2']+0.125),
])
def test_geometry_rejects_stale_pair_membership_certificate(ep,mutate):
    changed=copy.deepcopy(ep);mutate(changed)
    with pytest.raises(ValueError, match='pair membership certificate binding mismatch'):
        contour_geometry(changed,0.0,panels=8)


def test_constructor_membership_certificate_is_endpoint_and_policy_bound(ep):
    cert=ep['pair_membership']
    assert cert['passed'] is True
    assert cert['binding']['policy_id']=='FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2'
    assert cert['binding']['state_a']==[1,0,0]
    assert cert['binding']['state_b']==[2,1,0]
    assert len(cert['binding_sha256'])==64
    assert cert['claim']=='FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2'


def test_geometry_rejects_stale_policy_identity(ep):
    changed=copy.deepcopy(ep)
    changed['pair_membership']['binding']['policy_id']='STALE_POLICY'
    with pytest.raises(ValueError, match='pair membership certificate binding mismatch'):
        contour_geometry(changed,0.0,panels=8)
