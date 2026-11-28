from pathlib import Path
from fractions import Fraction as F
import pytest
import mpmath as mp
from wu088_hh.phys65_exterior_bounds import ratio_certificate, exp_upper, exp_negative_upper, q_radial, K, B
from wu088_hh.phys65_exterior_bounds import certificate
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_actual_high_block_has_non_sampled_full_exterior_certificate():
    c=certificate(SOURCE,64,3,39)
    assert c['status']=='DERIVED_FINITE_L_FULL_RADIAL_ANALYTIC_BOUNDS'
    assert c['gamma']==32400
    assert 0<float(F(c['born_tail_after_N']))<2e-60
    assert c['numerical_discretization_certified'] is False

@pytest.mark.parametrize('ell',[0,1,19,20,21,28,40,64])
def test_allowed_or_forbidden_anchor_has_checked_sign(ell):
    row=ratio_certificate(ell)
    assert row['qmin']>0 and row['qmax']>=row['qmin']
    assert row['trace_bound']>=row['trace_raw_upper']>=2
    assert row['allowed_start']>=B
    if row['forbidden']:
        assert q_radial(ell,row['anchor'])<=0
        assert q_radial(ell,row['anchor']+F(1,16))>0
        assert row['lognorm_upper']>0
    else:
        assert q_radial(ell,B)>0

@pytest.mark.parametrize('x',[F(0),F(1,3),F(4),F(263,5),F(76)])
def test_outward_exponential_against_independent_high_precision(x):
    with mp.workdps(500):
        xx=mp.mpf(x.numerator)/x.denominator
        e=exp_upper(x,max(100,int(x)+2))
        upper=mp.mpf(e.numerator)/e.denominator
        neg=exp_negative_upper(x)
        assert upper>=mp.exp(xx)
        assert mp.mpf(neg.numerator)/neg.denominator>=mp.exp(-xx)

@pytest.mark.parametrize('ell',[0,20,28,64])
def test_original_coulomb_ratio_below_global_rational_bound(ell):
    with mp.workdps(55):
        row=ratio_certificate(ell); a=float(row['anchor'])
        rr=[27.0,max(27.,a),max(27.,a)+3.,max(27.,a)+15.]
        h=[mp.coulombg(ell,-mp.mpf(10)/7,mp.mpf(7)*mp.mpf(str(r))/10)
           +1j*mp.coulombf(ell,-mp.mpf(10)/7,mp.mpf(7)*mp.mpf(str(r))/10) for r in rr]
        for i in range(len(rr)):
            for j in range(i,len(rr)):
                assert abs(h[j]/h[i])**2<=row['trace_bound']**2

def test_catalan_and_radial_error_components_not_conflated():
    c=certificate(SOURCE,64,3,39); fine=certificate(SOURCE,64,3,65)
    assert F(c['born_tail_after_N'])==F(fine['born_tail_after_N'])
    assert F(fine['radial_screen_cutoff_bound'])<F(1,10**50)
    assert F(c['radial_screen_cutoff_bound'])>F(1,10**30)
    assert c['excluded_angular_error'] is None
    assert c['numerical_discretization_error'] is None
    assert not c['total_error_certified']

def test_source_tamper_rejected(tmp_path):
    p=tmp_path/'bad.npz';p.write_bytes(b'wrong original')
    with pytest.raises(ValueError,match='SHA256'): certificate(p)

@pytest.mark.parametrize('kwargs',[{'max_ell':65},{'max_ell':-1},{'max_ell':True},{'orders':0},{'orders':6},{'outer':26}])
def test_scope_violations_rejected(kwargs):
    with pytest.raises(ValueError): certificate(SOURCE,**kwargs)

def test_cached_evidence_is_not_mutable():
    r=ratio_certificate(64);r['trace_bound']=0
    assert ratio_certificate(64)['trace_bound']==180

def test_increasing_born_order_improves_only_analytic_tail():
    c1=certificate(SOURCE,28,1,39);c2=certificate(SOURCE,28,2,39)
    assert 0<F(c2['born_tail_after_N'])<F(c1['born_tail_after_N'])
    assert c1['radial_screen_cutoff_bound']==c2['radial_screen_cutoff_bound']
