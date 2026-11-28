from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib
import pytest
from wu088_hh.phys58_screen_multipoles import (
 R,B,C_LEGENDRE,FROZEN_SHA,M_MAJOR,ellipse_min_square,
 legendre_coefficient_upper,legendre_tail_upper,low_to_high_2s_bound,
 taylor_exp_lower,original_source_sha_guard,make_certificate,exact_r5_gates)
ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_original_source_sha():
 assert original_source_sha_guard(FROZEN)==FROZEN_SHA
 assert hashlib.sha256(FROZEN.read_bytes()).hexdigest()==FROZEN_SHA

def test_ellipse_min_square_exact():
 assert ellipse_min_square()==F(2693,5)>23**2

def test_taylor_positive_exp46_gate():
 assert taylor_exp_lower(F(46),46)>5*10**19
 assert taylor_exp_lower(F(46),45)<taylor_exp_lower(F(46),46)

def test_complex_ellipse_sup_rational():
 assert F(24,23)/F(5*10**19)<M_MAJOR
 assert M_MAJOR==F(1,4*10**19)

@pytest.mark.parametrize('n',[0,1,2,3,4,7,8,9,16,32])
def test_legendre_bounds_positive_and_monotone(n):
 v=legendre_coefficient_upper(n)
 assert v>0
 if n>=1:
  assert v==F(2*n+1)*C_LEGENDRE/10**n

@pytest.mark.parametrize('n',[0,1,2,4,6,8,10,12,16])
def test_exact_tail_closed_form_against_partial_sum(n):
 val=legendre_tail_upper(n)
 residual=sum((legendre_coefficient_upper(k) for k in range(n+1,n+51)),F(0))
 assert 0<residual<val
 assert (val-residual)/val < F(1,10**40)

@pytest.mark.parametrize('n',[0,2,4,6,8,10,12])
def test_lowhigh_certificate(n):
 x=low_to_high_2s_bound(n)
 assert x['physical_high_ell_min']==21+n
 assert F(x['physical_2S_low_to_far_high_op_norm_upper_exact'])==2*legendre_tail_upper(n)
 assert x['NOT_DTN_BOUND'] is True

def test_lowhigh_n8_is_below_3eminus27():
 assert 2*legendre_tail_upper(8)<F(3,10**27)

def test_degree_monotone_tail():
 assert all(legendre_tail_upper(i)>legendre_tail_upper(i+1) for i in range(16))

def test_frozen_tamper_rejected(tmp_path):
 p=tmp_path/'other.npz';p.write_bytes(b'not original')
 with pytest.raises(ValueError,match='frozen source'):
  original_source_sha_guard(p)

def test_negative_inputs_rejected():
 with pytest.raises(ValueError):legendre_tail_upper(-1)
 with pytest.raises(ValueError):legendre_coefficient_upper(-1)
 with pytest.raises(ValueError):low_to_high_2s_bound(8,low_l_max=-1)

def test_certificate_scope_and_identity():
 d=make_certificate(FROZEN)
 assert d['frozen_SHA256']==FROZEN_SHA
 assert d['HH_R10']=='OFF'
 assert 'screened outgoing DtN Z_S' in d['not_proved'][0]
 assert len(d['rows'])==7
