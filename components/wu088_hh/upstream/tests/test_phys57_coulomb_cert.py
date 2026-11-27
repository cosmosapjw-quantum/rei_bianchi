"""PHYS57 focused finite symbolic checks for the all-l analytic proof."""
import hashlib
from pathlib import Path
from fractions import Fraction as F
import json
import pytest
from wu088_hh.phys57_coulomb_cert import (
 ABS_ETA,RHO,L,K,C_D,C_TRACE,ANGULAR_MAX,SCHEMA,FROZEN_SHA,
 source_sha_guard,nicholson_rational_certificate,
 finite_channel_flux_certificate,hybrid_inverse_certificate,
)

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'


def test_frozen_original_sha_bytes():
 assert source_sha_guard(SRC)==FROZEN_SHA
 assert hashlib.sha256(SRC.read_bytes()).hexdigest()==FROZEN_SHA


def test_bad_original_rejected(tmp_path):
 f=tmp_path/'wrong.npz';f.write_bytes(b'wrong')
 with pytest.raises(ValueError,match='frozen'): source_sha_guard(f)


def test_exact_tail_minimum_ratio():
 t=nicholson_rational_certificate()
 p=F(t['positive_integral_lower_at_cutoff_exact'])
 n=F(t['negative_integral_upper_at_cutoff_exact'])
 assert p>n>0
 assert p>F(1)
 assert F(t['relative_margin_floor_at_cutoff_exact'])==p/n


def test_pi_and_small_region_exponent():
 assert 4*RHO+ABS_ETA*F(22,7)<81
 assert 2*ABS_ETA+3*ABS_ETA**2/L<3
 assert ABS_ETA/L<1

@pytest.mark.parametrize('l',[128,129,130,150,256,4096])
def test_all_l_monotonic_analytic_majorants_samples(l):
 # These finite tests are sanity checks. The theorem derives monotonicity
 # for ALL integers l>=128 by the exact ratio in the report.
 assert l>=L
 p=F(2,5)*(l-ABS_ETA)*2**l/F(3**81)
 n=27*ABS_ETA**3/l**2
 assert p>n


def test_all_integer_ell_monotonic_formula():
 # P_(ell+1)/P_ell=2*(ell+1-a)/(ell-a)>1,
 # N_(ell+1)/N_ell=ell²/(ell+1)²<1, ell>=128.
 assert L>ABS_ETA
 assert F(2)*(L+1-ABS_ETA)/(L-ABS_ETA)>1
 assert F(L*L,(L+1)**2)<1


def test_energy_bounds_and_quadratic_form():
 f=finite_channel_flux_certificate()
 assert F(f['qmin_lower_reference_exact'])>F(1,4)
 assert F(f['total_variation_bound_exact'])<F(1,8)
 assert ANGULAR_MAX==127*128
 assert F(f['lognorm_integral_up_exact'])==F(311215,756)
 assert f['twice_lognorm_ceiling_integer']==824
 assert F(8,3)**3==F(512,27)
 assert F(f['finite_channel_flux_jstar_exact'])>0


def test_source_gated_bound_and_science_scope():
 d=hybrid_inverse_certificate(SRC)
 assert d['schema']==SCHEMA
 assert d['status']=='RIGOROUS_QUANTIFIED_INFINITE_HIGH_HYBRID_INVERSE'
 jstar=F(d['finite_exception_current_certificate']['finite_channel_flux_jstar_exact'])
 expected=(1+C_TRACE/C_D)**2*max(1/C_D,1/jstar)
 assert F(d['hybrid_inverse_norm_upper_exact'])==expected
 assert jstar < C_D
 assert 'HH_R10' in ' '.join(d['not_certified'])


def test_negative_rational_substitution_cannot_fake_certificate():
 q=F(2,5)*(L-ABS_ETA)*2**L/F(3**81)
 # If the positive-interval exponential floor is arbitrarily weakened
 # by 10^7, the current exact margin is no longer certifiable.
 assert q/10**7 < 27*ABS_ETA**3/L**2


def test_old_PHYS56_conditional_constants_exact():
 assert C_D==F(9,1000)
 assert C_TRACE==F(4849,16800)
 assert L==128
