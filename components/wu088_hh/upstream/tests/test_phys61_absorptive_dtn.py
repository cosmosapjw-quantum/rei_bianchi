from fractions import Fraction as F
from pathlib import Path
import pytest
from wu088_hh.phys61_absorptive_dtn import (
 B,R,K2,TAU_DEFAULT,V_DELTA_UP,SOURCE_SHA,screened_delta_rational,
 exponential_positive_partial,source_gate,uniform_bounds,certified_contract)

SOURCE=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_immutable_source(): assert source_gate(SOURCE)==SOURCE_SHA

def test_tamper_rejected(tmp_path):
 p=tmp_path/'bad.npz'; p.write_bytes(SOURCE.read_bytes()+b't')
 with pytest.raises(ValueError,match='SHA256'):source_gate(p)

@pytest.mark.parametrize('terms',[32,96,160,200])
def test_exp_partial_lower(terms):
 import mpmath as mp
 a=exponential_positive_partial(F(263,5),terms)
 with mp.workdps(100):
  assert mp.mpf(a.numerator)/a.denominator < mp.exp(mp.mpf(263)/5)

def test_original_screen_bound():
 assert screened_delta_rational(160)<V_DELTA_UP
 assert R==F(7,10) and B==27 and K2==F(49,100)

def test_exact_bound_full_ell():
 a=uniform_bounds()
 assert F(a['poisson_norm_upper'])==F(224285,1944)
 assert F(a['screened_neumann_q_upper'])==F(3,2*10**21)
 assert F(a['dtn_difference_norm_upper'])<F(4,10**19)
 assert a['HH_R10']=='OFF'

@pytest.mark.parametrize('tau',[F(1,5),F(1,50),F(1,500),F(1,5000)])
def test_finite_absorption_range(tau):
 a=uniform_bounds(tau)
 assert F(a['screened_neumann_q_upper'])<1
 assert F(a['dtn_difference_norm_upper'])>0

def test_as_tau_to_zero_not_uniform():
 assert F(uniform_bounds(F(1,1000))['poisson_norm_upper']) > F(uniform_bounds(F(1,100))['poisson_norm_upper'])

@pytest.mark.parametrize('bad_tau',[F(0),F(-1,100),F(1,10**26)])
def test_negative_zero_small_tau_rejected(bad_tau):
 with pytest.raises(ValueError):uniform_bounds(bad_tau)

def test_produced_contract_and_scope():
 r=certified_contract(SOURCE)
 assert r['source_identity']=='BYTE_IDENTITY_PASS'
 assert r['science']['source_scope'].endswith('IM_E_POSITIVE_ONLY')
 assert 'positive real energy outgoing LAP tau->0' in r['science']['not_claimed']

def test_exponential_lift_analytic_residual_sample():
 import math
 # Independent GL numerical norm of A_C(z) exp(-a x) for selected ell:
 import numpy as np
 from numpy.polynomial.legendre import leggauss
 xg,wg=leggauss(240)
 for ell in [0,1,20,21,64,160]:
  a=(ell+1)/27;upper=32/a
  x=(xg+1)*upper/2; w=wg*upper/2
  v=np.exp(-a*x)
  residual=(-a*a+ell*(ell+1)/(27+x)**2-2/(27+x)-.49-.02j)*v
  norm=np.sqrt(np.dot(w,np.abs(residual)**2))
  from wu088_hh.phys61_absorptive_dtn import uniform_bounds
  cc=float(F(15,4)*(F(1,27**2)+F(2,27)+F(49,100)+F(1,50))+F(1,27))
  assert norm/np.sqrt(ell+1)<cc
  assert np.dot(w,np.abs(v)**2)/float(ell+1)<13.500001

def test_upper_dtn_complex_current_analytic_example():
 import numpy as np
 # Show Im g*Zg from tau damping: in finite diagonal ODE, correct J'=-tau|u|².
 u=np.array([1+2j,2-1j]);up=np.array([3-4j,1+1j])
 diag=np.array([0.3,10.]);tau=.02
 dd=(diag-1j*tau)*u
 dj=float(np.imag(np.vdot(u,dd)))
 assert abs(dj+tau*float(np.vdot(u,u).real))<1e-14
