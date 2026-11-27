from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp
import numpy as np
import pytest

from wu088_hh.phys58_exact_multipoles import (
    rational_exp_minus_interval,exact_legendre_coefficient_interval,
    independent_mp_angular_coeff,exact_neighbour_m0_lower,
    gaunt_legendre,truncated_original_screen_matrix,
    independent_numpy_angular_matrix,
    make_interval_rows,fraction_to_decimal)
from wu088_hh.phys58_screen_multipoles import (
  FROZEN_SHA,original_source_sha_guard,legendre_coefficient_upper,legendre_tail_upper)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'


def test_input_lock():assert original_source_sha_guard(SOURCE)==FROZEN_SHA

@pytest.mark.parametrize('x',[F(1),F(2),F(46),F(263,5),F(277,5)])
def test_exp_enclosure_against_mpmath(x):
 lo,hi=rational_exp_minus_interval(x,320)
 with mp.workdps(800):
  v=mp.exp(-mp.mpf(x.numerator)/x.denominator)
  assert mp.mpf(lo.numerator)/lo.denominator < v < mp.mpf(hi.numerator)/hi.denominator

@pytest.mark.parametrize('n',list(range(13)))
def test_original_legendre_exact_enclosures_versus_independent_integration(n):
 lo,hi=exact_legendre_coefficient_interval(n,F(27),320)
 val=independent_mp_angular_coeff(n,F(27),230)
 assert lo>0 and hi>lo
 assert hi<=legendre_coefficient_upper(n)
 with mp.workdps(230):
  assert mp.mpf(lo.numerator)/lo.denominator < val < mp.mpf(hi.numerator)/hi.denominator

@pytest.mark.parametrize('n',[0,1,2,4,8,12])
def test_refined_radius30_enclosure(n):
 lo,hi=exact_legendre_coefficient_interval(n,F(30),320)
 val=independent_mp_angular_coeff(n,F(30),230)
 assert lo>0 and hi>lo
 with mp.workdps(230):
  assert mp.mpf(lo.numerator)/lo.denominator < val < mp.mpf(hi.numerator)/hi.denominator


def test_exact_positive_noncircular_PQ_lower():
 q=exact_neighbour_m0_lower(F(27))
 assert q['physical_V_2S_P20_to_Q21_strict_gt']=='6/10^24'
 assert gaunt_legendre(20,21,1,0)>F(1,2)

@pytest.mark.parametrize('l,lp,n,m,zero',[(20,21,0,0,True),(20,21,1,0,False),(20,20,0,0,False),(21,21,1,0,True),(20,21,40,0,True),(2,3,1,1,False)])
def test_gaunt_selection_and_sign(l,lp,n,m,zero):
 g=gaunt_legendre(l,lp,n,m)
 assert (g==0)==zero
 if m==0 and not zero:assert g>0
 assert gaunt_legendre(l,lp,n,-m)==g

@pytest.mark.parametrize('m',[0,1,2])
def test_actual_original_three_channel_gaunt_matrix_vs_independent_GL(m):
 els=(20,21,22)
 A,width=truncated_original_screen_matrix(els,m,F(27),degree=12,terms=320,dps=85)
 B=independent_numpy_angular_matrix(els,m,27.0,256)
 assert width>0
 maxabs=max(abs(float(A[i,j]-B[i,j])) for i in range(3) for j in range(3))
 # Certified exact Legendre tail bound is separate from finite floating roundoff.
 assert maxabs <= 5e-35
 assert abs(float(A[0,1]))>6e-24 if m==0 else True
 assert max(abs(float(A[i,j]-A[j,i])) for i in range(3) for j in range(3))<1e-80


def test_different_quadratures_agree_with_identical_inputs():
 m=0;ells=(20,21,22)
 a=independent_numpy_angular_matrix(ells,m,27,128)
 b=independent_numpy_angular_matrix(ells,m,27,256)
 assert np.max(np.abs(a-b)) < 3e-35


def test_actual_PQ_nonzero_m0_numeric():
 a=independent_numpy_angular_matrix((20,21),0,27.0,192)
 assert a[0,1]>6e-24
 assert a[1,0]==a[0,1] or abs(a[1,0]-a[0,1])<1e-35


def test_source_bound_tail_n12():
 assert 2*legendre_tail_upper(12)<F(4,10**31)


def test_negative_exponential_input_and_bad_l_rejected():
 with pytest.raises(ValueError):rational_exp_minus_interval(F(-1))
 with pytest.raises(ValueError):exact_legendre_coefficient_interval(-1)
 with pytest.raises(ValueError):gaunt_legendre(21,20,1,21)
 with pytest.raises(ValueError):independent_numpy_angular_matrix((20,21),0,nodes=10)


def test_tampered_frozen_rejected(tmp_path):
 bad=tmp_path/'bad.npz';bad.write_bytes(b'bad')
 with pytest.raises(ValueError): make_interval_rows(bad,(0,))


def test_reproducible_json_scientific_status():
 a=make_interval_rows(SOURCE,ns=(0,1,2,3),r=F(27),dps=240)
 b=make_interval_rows(SOURCE,ns=(0,1,2,3),r=F(27),dps=240)
 assert a==b
 assert a['source_sha256']==FROZEN_SHA and a['HH_R10']=='OFF'
 assert all(v['strict_positive_exact_enclosure'] for v in a['rows'])


def test_rational_format_outward():
 assert F(fraction_to_decimal(F(1,7),6))<F(1,7)<F(fraction_to_decimal(F(1,7),6,upper=True))
 assert F(fraction_to_decimal(F(-1,7),6))<F(-1,7)<F(fraction_to_decimal(F(-1,7),6,upper=True))
