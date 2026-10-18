"""Independent scalar/neutral-feedback controls, not native execution certificates."""
import math
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from birth_reference import birth_nodes, linear_history, nonlinear_history

@pytest.mark.parametrize('j',range(4))
def test_gl2_birth_moments(j):
    ns=birth_nodes('gl2')
    assert math.isclose(sum(w*c**j for c,w in ns),1/(j+1),rel_tol=2e-15,abs_tol=2e-15)

@pytest.mark.parametrize('rule',['midpoint','gl2','common_halves'])
def test_positive_source_and_all_energy_owners(rule):
    r=linear_history(rule,8,0.8,1.7,lambda x:1+.3*x)
    assert r['N']>=0 and r['U']>=0 and r['absorbed_N']>=0
    assert abs(r['N']+r['absorbed_N']-r['born_N'])<2e-14
    assert abs(r['U']+r['absorbed_U']+r['work_U']-r['born_U'])<2e-12

@pytest.mark.parametrize('k',[0.,.1,2.,20.])
def test_constant_linear_exact_quadrature(k):
    truth=quad(lambda x:math.exp(-k*(1-x)),0,1,epsabs=1e-14)[0]
    r=linear_history('gl2',64,1,k,lambda x:1.)
    assert abs(r['N']-truth)<max(2e-7,2e-6*truth)


def test_scalar_gl2_fourth_order_is_not_a_nonlinear_order_claim():
    k=2.;truth=-math.expm1(-k)/k
    errors=[abs(linear_history('gl2',n,1,k,lambda x:1.)['N']-truth) for n in (2,4,8,16)]
    p=[math.log2(a/b) for a,b in zip(errors,errors[1:])]
    assert all(3.9<v<4.1 for v in p),p


def test_nonlinear_gl2_midpoint_second_order_against_direct_radau():
    def rhs(x,y):
        rate=(1+.2*x+.3*x*x)*y[0]*y[1]
        return [(.3+.1*x)-rate,-rate,rate]
    truth=solve_ivp(rhs,(0,1),[.2,1.,0.],method='Radau',rtol=1e-12,atol=1e-14).y[:,-1]
    errors=[]
    for n in (8,16,32,64):
        r=nonlinear_history('gl2',n,1,lambda x:.3+.1*x,lambda x:1+.2*x+.3*x*x)
        errors.append(np.max(np.abs(np.array([r['N'],r['M'],r['events']])-truth)))
        assert min(r['N'],r['M'],r['events'])>=0
        assert abs(r['M']+r['events']-1)<2e-14
        assert abs(r['N']+r['events']-.2-r['born_N'])<2e-14
    assert all(1.95<math.log2(a/b)<2.05 for a,b in zip(errors,errors[1:])),errors


def test_gl2_stiff_source_boundary_layer_is_not_uniformly_accurate():
    r=linear_history('gl2',1,1,1000.,lambda x:1.)
    true=-math.expm1(-1000.)/1000.
    assert r['N']>=0
    assert abs(r['N']-true)/true>.99


def test_equal_photon_birth_count_does_not_equal_redshift_energy():
    a=linear_history('gl2',1,1,0.,lambda x:1.)
    b=linear_history('common_halves',1,1,0.,lambda x:1.)
    assert a['born_N']==b['born_N']==1.
    assert abs(a['U']-b['U'])>1.

@pytest.mark.parametrize('bad',['start_mid_fake','', 'GL2'])
def test_bad_rule(bad):
    with pytest.raises(ValueError):birth_nodes(bad)
