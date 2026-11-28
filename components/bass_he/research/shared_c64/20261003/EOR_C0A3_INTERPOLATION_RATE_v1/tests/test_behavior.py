from pathlib import Path
from decimal import Decimal
import math
import pytest
from bass_he_liu import Dataset, parse_csv, load_dataset, ContractError, SourceUnavailable, DomainError
from bass_he_liu_interp import Interpolator, KinematicBinding, maxwell_weights
ROOT=Path(__file__).resolve().parents[1]

def real():return load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')
def tiny(values='1,1,9,1,1,1\n4,9,1,1,1,1\n'):
    return Dataset([parse_csv('H1s-Excitation cross sections.csv',('keV/u,2s,2p,3s,3p,3d\n'+values).encode())])

def make(d=None,method='linear_E',scope='paper_domain'):
    return Interpolator(d or real(),method=method,scope=scope)

@pytest.mark.parametrize('method',[None,'PCHIP','automatic'])
def test_method_never_implicit(method):
    with pytest.raises(ContractError):Interpolator(real(),method=method)

def test_linear_midpoint_real_separate_grid():
    r=make().evaluate('NR_CX:1s:1s','56.25');assert r is not None
    assert r['data_kind']=='INTERPOLATED_VALUE'
    assert r['bracket_energies']==['47.61','64']
    expect=2.34e-17+(56.25-47.61)/(64-47.61)*(2.10e-17-2.34e-17)
    assert float(r['value'])==pytest.approx(expect,rel=2e-15)
    assert r['source_uncertainty'] is None and not r['physical_certificate']

@pytest.mark.parametrize('method',['linear_E','loglog'])
def test_native_token_returned_unchanged(method):
    r=make(method=method).evaluate('NR_CX:1s:1s','100');assert r is not None
    assert r['value_token']=='1.15E-17' and r['data_kind']=='SOURCE_NATIVE_SAMPLE'
    assert not r['interpolated']

def test_loglog_power_reproduction():
    r=make(tiny('1,1,1,1,1,1\n4,16,1,1,1,1\n'),method='loglog').evaluate('EXC:1s:2s','2');assert r is not None
    assert float(r['value'])==pytest.approx(4.,rel=2e-15)

def test_derived_is_sum_of_interpolants_not_interpolated_sum():
    r=make(tiny(),method='loglog').aggregate(['EXC:1s:2s','EXC:1s:2p'],'2');assert r is not None
    assert float(r['value'])==pytest.approx(6,rel=2e-15)
    assert float(r['value'])!=10

@pytest.mark.parametrize('ids',[
 ['NR_CX:1s:2s','NR_CX:1s:n2'],['NR_CX:1s:total','NR_CX:1s:2p'],
 ['NR_CX:1s:1s','NR_CX:1s:n1'],['NR_CX:1s:2s','EXC:1s:2s'],
 ['NR_CX:1s:2s','NR_CX:2s:3s']])
def test_aggregation_ownership(ids):
    with pytest.raises(ContractError):make().aggregate(ids,'95')

@pytest.mark.parametrize('cid,e',[('EXC:1s:2s','4'),('EXC:1s:2s','5'),('NR_CX:1s:1s','1')])
def test_missing_and_outside_support_are_not_zero(cid,e):
    with pytest.raises(ContractError):make().evaluate(cid,e)

def test_explicit_interior_missing_forbids_bridging():
    d=tiny('1,1,1,1,1,1\n2,,1,1,1,1\n4,4,1,1,1,1\n')
    with pytest.raises(SourceUnavailable,match='MISSING'):make(d).evaluate('EXC:1s:2s','3')

@pytest.mark.parametrize('e',['200','210','225'])
def test_paper_scope_restricts_both_anchor_nodes(e):
    with pytest.raises(ContractError):make().evaluate('EXC:1s:2p',e)

def test_payload_scope_makes_200_explicit_interpolation():
    r=make(scope='payload_domain').evaluate('EXC:1s:2p','200');assert r is not None
    assert r['bracket_energies']==['196','210.25'] and r['uses_outside_paper_anchor']

@pytest.mark.parametrize('e',[100.0,True,'NaN','-1','0'])
def test_exact_axis_and_positive_query(e):
    with pytest.raises(ContractError):make().evaluate('NR_CX:1s:1s',e)

def test_contextual_unit_required():
    with pytest.raises(ContractError,match='UNIT'):make().evaluate('EXC:1s:2p','95',unit='m2')
    r=make().evaluate('EXC:1s:2p','95',unit='m2',accept_contextual_unit=True);assert r is not None
    assert 1e-20<float(r['value'])<2e-20

def test_loglog_zero_anchor_refused_linear_allowed():
    d=tiny('1,0,1,1,1,1\n4,9,1,1,1,1\n')
    with pytest.raises(ContractError,match='POSITIVE'):make(d,method='loglog').evaluate('EXC:1s:2s','2')
    r=make(d).evaluate('EXC:1s:2s','2');assert r is not None
    assert float(r['value'])==3.

@pytest.mark.parametrize('a,b',[(0.,1.),(1.,2.),(100.,101.),(1.,1.00000001)])
def test_positive_maxwell_weights_sum(a,b):
    w=maxwell_weights(a,b);assert w is not None
    assert w[0]>0 and w[1]>0
    # Narrow panel has independent leading asymptotic, not subtracting exponentials.
    if b-a<1e-6:expected=math.exp(-a)*a*(b-a)
    else:expected=(1+a)*math.exp(-a)-(1+b)*math.exp(-b)
    assert sum(w)==pytest.approx(expected,rel=2e-8 if b-a<1e-6 else 2e-14)

@pytest.mark.parametrize('a,b',[(1,1),(2,1),(-1,1),(0,float('nan')),(1000,1001)])
def test_invalid_or_underflow_weights_fail(a,b):
    with pytest.raises(ContractError):maxwell_weights(a,b)

def test_exact_constant_sigma_partial_functional():
    d=tiny('1,2,2,2,2,2\n4,2,2,2,2,2\n')
    r=make(d).maxwell_functional('EXC:1s:2s','1','4',theta_native=2.);assert r is not None
    expect=2*((1+.5)*math.exp(-.5)-(1+2)*math.exp(-2))
    assert r['value']==pytest.approx(expect,rel=2e-14)
    assert r['full_functional'] is None and r['tail_bound'] is None
    assert r['renormalized_to_support'] is False

def test_full_rate_request_refused_and_no_binding_guess():
    with pytest.raises(ContractError):make().maxwell_partial_rate('EXC:1s:2p','10','100',theta_J=1e-15,binding=None)
    with pytest.raises(SourceUnavailable):make().maxwell_partial_rate('EXC:1s:2p','10','100',theta_J=1e-15,binding=KinematicBinding(1e-16,1e-27,'MANUFACTURED'),require_full=True)

def test_explicit_mapping_and_scaling():
    d=tiny('1,2,2,2,2,2\n4,2,2,2,2,2\n');i=make(d)
    r=i.maxwell_partial_rate('EXC:1s:2s','1','4',theta_J=2.,binding=KinematicBinding(1.,3.,'MANUFACTURED'),accept_contextual_unit=True);assert r is not None
    expect=2e-4*math.sqrt(16/(3*math.pi))*(1.5*math.exp(-.5)-3*math.exp(-2))
    assert r['partial_rate_m3_s']==pytest.approx(expect,rel=3e-14)
    assert r['full_rate_m3_s'] is None and not r['physical_certificate']
    assert r['binding_status']=='CONDITIONAL_USER_MAPPING'

def test_moment_or_unsupported_interpolant_rate_is_not_fabricated():
    with pytest.raises(ContractError):make(method='loglog').maxwell_functional('EXC:1s:2p','10','100',theta_native=10.)

def test_interval_missing_blocks_integral():
    d=tiny('1,1,1,1,1,1\n2,,1,1,1,1\n4,4,1,1,1,1\n')
    with pytest.raises(SourceUnavailable):make(d).maxwell_functional('EXC:1s:2s','1','4',theta_native=1.)
