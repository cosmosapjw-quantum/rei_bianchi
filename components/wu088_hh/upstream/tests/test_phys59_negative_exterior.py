from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import hashlib
import pytest
from wu088_hh.phys59_negative_exterior import (
 R,B,KAPPA,ORIGINAL_SHA,OFFSHELL_ENERGY_HARTREE,DELTA_UP,BETA_CERT,TRACE_ENERGY_UP,
 original_sha_guard, positive_exp_taylor_lower,rigorous_screen_upper,
 hat_width,lift_energy_normalized,exact_all_ell_lift_proof,
 exact_q_and_operator_gates,m0_l20_l21_dtn_lower,certificate
)
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_frozen_original_input_sha_guard():
 assert original_sha_guard(SOURCE)==ORIGINAL_SHA
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==ORIGINAL_SHA

def test_tampered_input_fails(tmp_path):
 p=tmp_path/'input.npz';p.write_bytes(b'fake')
 with pytest.raises(ValueError,match='original immutable'):original_sha_guard(p)

def test_original_physical_constants_and_negative_energy_gate():
 assert (R,B,KAPPA)==(F(7,10),F(27),F(7,10))
 assert OFFSHELL_ENERGY_HARTREE==F(-49,200)
 assert OFFSHELL_ENERGY_HARTREE<0

def test_rational_exponent_taylor_and_screen_upper():
 assert positive_exp_taylor_lower(F(263,5),160)>0
 assert rigorous_screen_upper(160)<DELTA_UP==F(3,10**23)

def test_allangular_coercive_energy_lower():
 gates=exact_q_and_operator_gates()
 assert F(gates['exterior_A_C_zeroDirichlet_floor_exact'])==F(1123,2700)
 assert F(gates['exterior_A_S_uniform_floor_lower_exact'])>BETA_CERT==F(2,5)
 assert F(gates['dtn_diff_full_angular_upper_exact'])==F(9,10**23)

def test_piecewise_exact_trace_lift_all_l():
 v=exact_all_ell_lift_proof()
 assert F(v['ell_0_to26_energy_ratio_max_upper'])<TRACE_ENERGY_UP
 assert F(v['ell_ge27_energy_ratio_max_upper'])<TRACE_ENERGY_UP

@pytest.mark.parametrize('ell',[0,1,19,20,21,26,27,28,29,50,100,10000])
def test_actual_hat_energy_vs_ceiling(ell):
 assert lift_energy_normalized(ell)<TRACE_ENERGY_UP
 assert hat_width(ell)==min(F(1),B/F(ell+1))

def test_scalar_offshell_dtn_sign_constant_barrier_example():
 # For A_C=-d²+k², A_S=A_C-V, Z=-sqrt(k²-V), exact sign.
 import mpmath as mp
 with mp.workdps(70):
  k=mp.mpf(7)/10;d=mp.mpf('0.01')
  zc=-k;zs=-mp.sqrt(k*k-d)
  assert zs-zc>0
  assert abs((zs-zc)-d/(k+mp.sqrt(k*k-d)))<mp.mpf('1e-65')

def test_very_small_true_m0_PQ_offshell_positive():
 d=m0_l20_l21_dtn_lower()
 lb=F(d['strict_full_original_screened_Zminus_PQ_lower_exact'])
 assert lb>0
 assert lb==F(1701,2216*3**60)
 assert lb>F(1,10**30)

def test_m0_allangular_triangular_Gaunt_selected_component():
 # Direct known n=1 coefficient; all n0 Gaunts are 3j squared.
 assert 41*43<42*42
 from sympy.physics.wigner import wigner_3j
 from sympy import Rational
 assert wigner_3j(20,21,1,0,0,0)**2 == Rational(21,41*43)
 assert float((41*43)**0.5) <42

def test_green_identity_finite_real_two_channel_algebra():
 import numpy as np
 A=np.array([[2.4,-0.08],[-0.08,3.1]])
 V=np.array([[0.010,0.004],[0.004,0.006]])
 assert np.min(np.linalg.eigvalsh(V))>0
 U=np.linalg.inv(A-V);C=np.linalg.inv(A)
 # exact resolvent difference A_S^-1-A_C^-1 = A_C^-1 V A_S^-1
 assert np.linalg.norm(U-C-C@V@U,ord=2)<1e-15
 assert np.min(np.linalg.eigvalsh(U-C))>=-1e-15

def test_certificate_consumable():
 c=certificate(SOURCE)
 assert c['full_m_all_ell'] is True
 assert c['production_HH_R10']=='OFF'
 assert c['physics'].endswith('NEGATIVE_ENERGY')
 assert 'positive-energy Coulomb outgoing LAP/Poisson constants' in c['not_proved']

@pytest.mark.parametrize('bad',[(-1,),('a',), (10**8,)])
def test_bad_angular_index_rejected(bad):
 with pytest.raises(ValueError):hat_width(bad[0])
