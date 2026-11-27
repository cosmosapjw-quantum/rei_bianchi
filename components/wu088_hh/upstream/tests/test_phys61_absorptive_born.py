import math
from pathlib import Path
from fractions import Fraction as F
import pytest
from wu088_hh.phys61_absorptive_born import (
 born_remainder_exact,born_tail_r39_exact,physical_screen_angular_coupling,
 central_outgoing_complex,born_first_grid,flux_identity_finite_interval,science_packet)
SOURCE=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_rigorous_full_all_angular_born_residual():
 q=born_remainder_exact(); assert q['rational_proved_lt_6e_minus40']
 assert q['raw_P20_Q21_lt_1p32e_minus38']
 assert F(q['all_angular_Born_remainder_X_to_Xstar'])<F(6,10**40)

def test_actual_born_r39_tail_rigorous():
 q=born_tail_r39_exact();assert q['operator_bound_lt_2e_minus29']
 assert F(q['operator_X_to_Xstar_born_tail_bound'])<F(2,10**29)

@pytest.mark.parametrize('m',[0,1,2])
def test_original_screen_sign_and_signed_m_symmetry(m):
 z=physical_screen_angular_coupling(27.0,m,96)
 assert z>0
 assert z==physical_screen_angular_coupling(27.0,-m,96)

@pytest.mark.parametrize('r',[27.0,28.0,35.0,39.0])
def test_normalized_complex_outgoing(r):
 p20=central_outgoing_complex(20,r)
 p21=central_outgoing_complex(21,r)
 assert math.isfinite(p20.real) and math.isfinite(p21.imag)
 if r==27:assert abs(p20-1)<1e-14 and abs(p21-1)<1e-14

@pytest.mark.parametrize('m',[0,1,2])
def test_complex_born_nonzero(m):
 z=born_first_grid(m,14,96,34)
 assert abs(z)>1e-25
 assert abs(z.imag)>1e-27
 assert z==born_first_grid(-m,14,96,34)

def test_finite_interval_l20_current_absorption():
 d=flux_identity_finite_interval(20,nodes=36)
 assert d['positive_J_B'] and d['relative_residual']<1e-8

def test_finite_interval_l21_current_absorption():
 d=flux_identity_finite_interval(21,nodes=36)
 assert d['positive_J_B'] and d['relative_residual']<1e-8

def test_noncertifying_full_packet_small_stage():
 # Full expensive 4-grid packets run as separate producer, not duplicate in tests.
 from wu088_hh.phys61_absorptive_dtn import source_gate
 assert source_gate(SOURCE)
 assert not born_remainder_exact()['spectral_scope'].endswith('I0')

def test_invalid_numerical_arguments():
 with pytest.raises(ValueError):physical_screen_angular_coupling(20,0,96)
 with pytest.raises(ValueError):born_first_grid(21,14,96)
 with pytest.raises(ValueError):central_outgoing_complex(120,27)
 with pytest.raises(ValueError):born_tail_r39_exact(terms=12)
