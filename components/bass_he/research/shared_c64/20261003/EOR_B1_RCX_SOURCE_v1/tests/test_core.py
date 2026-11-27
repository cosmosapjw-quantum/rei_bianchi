import cmath, math
import numpy as np
import pytest
from bass_he_rcx import ContractError,NumericalFailure,solve_partial_wave,partial_sum,physical_scales

def exact_s0(e,V,g,R):
    k=math.sqrt(e);q=cmath.sqrt(e-V+1j*g/2)
    u=cmath.sin(q*R)/q if q else R;p=cmath.cos(q*R)
    return cmath.exp(-2j*k*R)*(p+1j*k*u)/(p-1j*k*u)

@pytest.mark.parametrize('ell',[0,1,3,6])
def test_free_scattering(ell):
    x=solve_partial_wave(1.3,ell,[0.,1.,2.5],[0.,0.],[[0.],[0.]])
    assert x is not None and abs(complex(*x['S'])-1)<2e-9
    assert x['loss_probability']==0. and x['RCT_cross_section'] is None

@pytest.mark.parametrize('V,g,E,R',[(-2.,.1,.7,1.),(3.,.2,1.,2.),(0.,1.,2.,1.4),(-10.,.5,.2,1.)])
def test_absorbing_square_well_exact(V,g,E,R):
    out=solve_partial_wave(E,0,[0.,R],[V],[[g]])
    assert out is not None
    s=exact_s0(E,V,g,R)
    assert abs(complex(*out['S'])-s)<2e-9
    assert abs(out['loss_probability']-(1-abs(s)**2))<2e-9
    assert out['sigma_partial_over_L2']==pytest.approx(math.pi/E*out['loss_probability'])

def test_rare_loss_not_smatrix_cancellation():
    out=solve_partial_wave(1.,0,[0.,1.],[0.],[[1e-30]])
    assert out is not None and out['loss_probability']>0
    # first-order exact limit: 2*g/k* integral sin²(kx) dx for incoming coefficient1/2
    expected=1e-30*(1-math.sin(2)/2)
    assert out['loss_probability']==pytest.approx(expected,rel=2e-10,abs=0)
    assert out['loss_formula']=='positive_flux_integral'

def test_component_flux_partition():
    out=solve_partial_wave(.8,2,[0.,1.,3.],[-1.,.2],[[.02,.06],[.04,.12]])
    assert out is not None
    p=out['component_loss_probabilities']
    assert p[1]==pytest.approx(3*p[0],rel=2e-10)
    assert math.fsum(p)==out['loss_probability']

def test_same_operator_split_shells():
    a=solve_partial_wave(.9,3,[0.,2.],[-2.],[[.03]])
    b=solve_partial_wave(.9,3,[0.,.5,1.,1.5,2.],[-2.]*4,[[.03]]*4)
    assert a is not None and b is not None
    assert abs(complex(*a['S'])-complex(*b['S']))<3e-9
    assert b['loss_probability']==pytest.approx(a['loss_probability'],rel=2e-8)

def test_zero_internal_wavenumber():
    out=solve_partial_wave(1.,0,[0.,1.],[1.],[[0.]])
    assert out is not None and abs(abs(complex(*out['S']))-1)<1e-12

@pytest.mark.parametrize('args',[
    (0.,0,[0.,1.],[0.],[[1.]]),
    (1.,True,[0.,1.],[0.],[[1.]]),
    (1.,-1,[0.,1.],[0.],[[1.]]),
    (1.,0,[.1,1.],[0.],[[1.]]),
    (1.,0,[0.,1.,1.],[0.,0.],[[1.],[1.]]),
    (1.,0,[0.,1.],[0.],[[-.1]]),
    (1.,0,[0.,1.],[float('nan')],[[1.]]),
    (1.,0,[0.,1.,2.],[0.,0.],[[1.],[1.,2.]]),
])
def test_bad_models_refused(args):
    with pytest.raises(ContractError):solve_partial_wave(*args)

def test_unlabelled_sink_not_physical_rct():
    o=solve_partial_wave(1.,0,[0.,1.],[0.],[[.1]])
    assert o is not None and o['data_kind']=='DECLARED_OPTICAL_MODEL_PARTIAL_WAVE'
    assert not o['physical_source_admitted'] and o['photon_energy_moment'] is None
    assert o['outer_boundary']=='exactly_free_beyond_last_edge_by_model_definition'

def test_explicit_dimensional_scale():
    o=physical_scales(2.,3.,4.)
    assert o is not None and o['energy_J']==pytest.approx(2/3)
    assert o['area_m2']==4.

def test_sum_is_partial_not_full():
    rows=[solve_partial_wave(1.,l,[0.,2.],[-1.],[[.1]]) for l in (0,1,2)]
    x=partial_sum(rows)
    assert x is not None and x['full_cross_section'] is None
    assert x['l_tail_bound'] is None and x['ell_values']==[0,1,2]

def test_duplicate_partial_wave_refused():
    a=solve_partial_wave(1.,0,[0.,1.],[0.],[[.1]])
    with pytest.raises(ContractError):partial_sum([a,a])
