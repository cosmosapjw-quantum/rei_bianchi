"""Post-implementation invariants; not counted as red-green feature tests."""
import cmath, math
import pytest
from bass_he_west82 import ContractError,NumericalFailure,solve_partial_wave,partial_sum
from bass_he_west82.source import optical_point,radial_input_point,paper_k2

@pytest.mark.parametrize('params',[
    (0.,-.8,-1.6,[.1,0,0]),
    (1.,-2.,-1.,[.1,0,0]),
    (1.,-.8,-1.6,[.1,0]),
    (1.,-.8,-1.6,[float('inf'),0,0]),
])
def test_bad_electronic_inputs(params):
    with pytest.raises(ContractError):optical_point(*params,energy_unit='Hartree',c_atomic=100.)

def test_equal_gap_is_zero_not_missing_moment():
    d=optical_point(4.,-.8,-.8,[.1,0,0],energy_unit='Hartree',c_atomic=100.)
    assert d['A_atomic']==0 and d['photon_energy_moment'] is None

def test_factor8_ry_misinterpretation():
    kw=dict(R_bohr=4.,Eu=-1.6,El=-3.2,dipole=[.1,0,0],c_atomic=100.)
    h=optical_point(**kw,energy_unit='Hartree');ry=optical_point(**kw,energy_unit='Ry')
    assert h['A_atomic']/ry['A_atomic']==pytest.approx(8.)

def test_negative_A_not_admitted():
    with pytest.raises(ContractError):radial_input_point(1.,0.,-.01,1000.)

@pytest.mark.parametrize('e,m',[('0','1'),('1','0'),(True,'1'),(.1,'1')])
def test_paper_k_tokens_exact_positive(e,m):
    with pytest.raises(ContractError):paper_k2(e,m)

@pytest.mark.parametrize('ell',[0,3,38,48])
def test_partition_sinks_and_same_operator_split(ell):
    R=ell+4.
    a=solve_partial_wave(1.,ell,[0.,R],[-.15],[[.001,.003]])
    b=solve_partial_wave(1.,ell,[0.,R/2,R],[-.15,-.15],[[.001,.003]]*2)
    assert abs(complex(*a['S'])-complex(*b['S']))<3e-9
    assert a['loss_probability']==pytest.approx(b['loss_probability'],rel=3e-8)
    assert a['component_loss_probabilities'][1]==pytest.approx(3*a['component_loss_probabilities'][0],rel=3e-12)
    assert a['RCT_cross_section'] is None

def test_elementary_swave_regression():
    q=cmath.sqrt(1.2+.15+.001j);k=math.sqrt(1.2);R=3.
    u=cmath.sin(q*R)/q;p=cmath.cos(q*R)
    s=cmath.exp(-2j*k*R)*(p+1j*k*u)/(p-1j*k*u)
    a=solve_partial_wave(1.2,0,[0.,R],[-.15],[[.002]])
    assert abs(s-complex(*a['S']))<3e-12
    assert abs((1-abs(s)**2)-a['loss_probability'])<3e-12

def test_high_l_sum_stays_partial():
    rows=[solve_partial_wave(1.,l,[0.,51.],[0.],[[.001]]) for l in [33,48]]
    s=partial_sum(rows)
    assert s['ell_values']==[33,48] and s['l_tail_bound'] is None and s['full_cross_section'] is None
