import math
import pytest
from wu088_hh.phys53_coulomb_tail import outgoing_cf,depth_comparison,mp_reference,asymptotic_log10_current,ETA,KAPPA

def test_locked_constants():
    assert KAPPA==0.7 and ETA==-10/7

@pytest.mark.parametrize('l,r',[(0,27),(21,27),(28,27),(29,27),(40,30),(64,43),(100,27)])
def test_rational_contfrac_high_precision_reference(l,r):
    a=depth_comparison(l,r)
    b=mp_reference(l,r,65)
    real=float(b['re_per_Bohr'])
    assert abs(real-a['re_per_Bohr']) < 1.5e-12*max(1,abs(real))
    assert a['complex_depth_delta'] < 1e-11*max(1,abs(real))
    if l<=29:
        assert abs(a['im_f64_per_Bohr']-float(b['im_per_Bohr']))<1e-12

def test_wu_original_ell21_r27():
    z=outgoing_cf(21,27)
    assert abs(z.real+0.1825388002297734527499)<3e-14
    assert abs(z.imag-0.127124705730778464612)<3e-14

@pytest.mark.parametrize('l',[21,28,29,64,128,256])
def test_current_log_and_large_l(l):
    d=mp_reference(l,27,68)
    logj=float(d['log10_current_per_Bohr'])
    assert math.isfinite(logj)
    if l>=128: assert logj<-120
    if l>=256: assert logj<-308
    asym=asymptotic_log10_current(l,27)
    assert math.isfinite(asym)
    if l>=128: assert abs((logj-asym)/logj)<0.1

def test_current_decreases_for_sampled_ell():
    vals=[float(mp_reference(l,27,64)['log10_current_per_Bohr']) for l in [29,40,64,100,128]]
    assert all(a>b for a,b in zip(vals,vals[1:]))

def test_reject_unsafe_inputs():
    with pytest.raises(ValueError):outgoing_cf(-1,27)
    with pytest.raises(ValueError):outgoing_cf(21,0)
    with pytest.raises(ValueError):outgoing_cf(21,27,50)