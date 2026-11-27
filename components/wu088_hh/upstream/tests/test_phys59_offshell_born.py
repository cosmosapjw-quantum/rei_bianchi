from fractions import Fraction as F
from pathlib import Path
import math
import pytest
import mpmath as mp
from wu088_hh.phys59_negative_exterior import B,ORIGINAL_SHA
from wu088_hh.phys59_offshell_born import (born_remainder_fraction_certification,central_decaying_poisson,physical_2S_angular_matrix_element, first_born_21_20_gl,numerical_witness)

SRC=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_exact_allangular_Born_remainder():
 r=born_remainder_fraction_certification()
 assert F(r['allangular_Born_operator_remainder_exact_upper'])<F(7,10**45)
 assert F(r['raw_offdiagonal_ell21_ell20_m0_remainder_exact_upper'])<F(154,10**45)

@pytest.mark.parametrize('ell',[0,20,21,50])
def test_exact_offshell_poisson_at_boundary(ell):
 assert abs(central_decaying_poisson(ell,27,dps=70)-1)<mp.mpf('1e-55')

@pytest.mark.parametrize('ell',[20,21])
def test_radial_positive_and_decay_and_barrier_comparison(ell):
 with mp.workdps(72):
  kap=mp.mpf(7)/10
  beta=mp.mpf(1123)/2700
  alpha=mp.sqrt(kap*kap+ell*(ell+1)/mp.mpf(27)**2)
  for r in (mp.mpf('27.25'),mp.mpf('28'),mp.mpf('29.5')):
   p=central_decaying_poisson(ell,float(r),dps=72)
   assert p>0
   assert mp.exp(-alpha*(r-27)) <= p+mp.mpf('1e-62')
   assert p <=mp.exp(-mp.sqrt(beta)*(r-27))+mp.mpf('1e-62')


def test_whittaker_actual_reduced_radial_ODE_residual():
 with mp.workdps(65):
  kap=mp.mpf(7)/10
  for ell in [20,21]:
   def f(rr):return mp.whitw(1/kap,ell+mp.mpf(1)/2,2*kap*rr)
   r=mp.mpf('28.5')
   q=kap*kap-2/r+ell*(ell+1)/r**2
   assert abs(-mp.diff(f,r,2)+q*f(r))/abs(f(r))<mp.mpf('1e-53')


def test_true_screened_angular_qp_not_erased():
 for m in (0,1,2):
  a=physical_2S_angular_matrix_element(21,20,m,27,128)
  b=physical_2S_angular_matrix_element(21,20,m,27,256)
  assert a>0 and b>0
  assert abs(a-b)/b<1e-11
  if m==0:assert b>6e-24


def test_angular_symmetry_and_same_m():
 for m in (-2,-1,0,1,2):
  a=physical_2S_angular_matrix_element(20,21,m,27,192)
  b=physical_2S_angular_matrix_element(21,20,m,27,192)
  assert abs(a-b)<1e-35
  assert abs(a-physical_2S_angular_matrix_element(21,20,-m,27,192))<1e-35


def test_direct_Born_integral_strictly_positive():
 d=first_born_21_20_gl(18,128,12,dps=70)
 value=mp.mpf(d['born_GL_noncertifying'])
 assert value>0
 assert value>mp.mpf('1e-29')
 assert mp.mpf(d['rigorous_radial_tail_bound_decimal'])>0


def test_independent_radial_angular_grid_refinement():
 a=first_born_21_20_gl(18,128,12,70)
 b=first_born_21_20_gl(26,192,12,70)
 va,vb=mp.mpf(a['born_GL_noncertifying']),mp.mpf(b['born_GL_noncertifying'])
 assert va>0 and vb>0
 assert abs(va-vb)/vb<mp.mpf('2e-4')


def test_error_paths():
 with pytest.raises(ValueError):central_decaying_poisson(20,26)
 with pytest.raises(ValueError):central_decaying_poisson(-1,27)
 with pytest.raises(ValueError):physical_2S_angular_matrix_element(21,20,22,27)
 with pytest.raises(ValueError):first_born_21_20_gl(2,64,12,75)

@pytest.fixture(scope='module')
def result():return numerical_witness(SRC)

def test_full_actual_original_source_lock_and_result(result):
 assert result['original_SHA256']==ORIGINAL_SHA
 assert result['HH_R10']=='OFF'
 assert len(result['GL_radial_angular_noncertifying_rows'])==4
 assert float(result['finest_refinement_relative'])<2e-4

def test_distinct_energy_and_no_scattering_claim(result):
 assert all(x['physics']=='E_NEGATIVE_OFFSHELL_NOT_SCATTERING' for x in result['GL_radial_angular_noncertifying_rows'])
 assert 'positive real scattering energy outgoing Z_S^+' in result['not_admitted']
