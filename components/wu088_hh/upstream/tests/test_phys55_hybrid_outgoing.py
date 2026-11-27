"""New PHYS55 tests: exact source/proof bounds + noncert finite numerical."""
from fractions import Fraction as F
from pathlib import Path
import math
import numpy as np
import pytest
import mpmath as mp

from wu088_hh.phys55_hybrid_outgoing import (
    ORIGINAL_SHA, FIRST_HIGH, B, T, KAPPA, CERTIFIED_C_D,
    exp_lower, screen_collar_upper, barrier_a2, weighted_ratio2,
    collar_certificate, original_sha, central_impedance,
    fd_screened_collar_hybrid,
)

ORIGINAL = Path(__file__).resolve().parents[1] / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_source_sha_and_npz_integrity():
    assert original_sha(ORIGINAL) == ORIGINAL_SHA
    with np.load(ORIGINAL, allow_pickle=False) as z:
        assert len(z.files)>0


def test_original_tamper(tmp_path):
    p=tmp_path/'fake.npz';p.write_bytes(b'corrupted')
    with pytest.raises(ValueError,match='immutable'):
        collar_certificate(p)


@pytest.mark.parametrize('n',[26,30,35,42])
def test_screen_exponential_source_rational_upper(n):
    x=screen_collar_upper(n)
    assert x>0 and x<F(1,10**12)
    assert exp_lower(F(193,5),n)>0


def test_exponential_exact_monotone():
    vals=[screen_collar_upper(n) for n in (26,30,35,42)]
    assert all(a>b for a,b in zip(vals,vals[1:]))


def test_21_weighted_floor_and_exact_margin():
    a=barrier_a2(21)
    assert a==F(10629999999757,243000000000000)
    assert weighted_ratio2(21)-CERTIFIED_C_D**2==F(1103427999757,117612000000000000)


@pytest.mark.parametrize('ell',[21,22,23,28,29,40,64,128,256,1000,10000])
def test_all_high_harmonic_monotonic_samples(ell):
    assert barrier_a2(ell)>0
    assert weighted_ratio2(ell) >= weighted_ratio2(FIRST_HIGH)
    assert weighted_ratio2(ell)>CERTIFIED_C_D**2


def test_exact_all_l_claim_preserves_scope():
    c=collar_certificate(ORIGINAL)
    assert c['all_high_ell_from']==21
    assert c['all_m'] is True
    assert c['cD_certified_fraction']=='9/1000'
    assert 'CENTRAL' not in c['collar_TT']
    assert 'physical noncentral screened outer Z_S' in c['not_established']
    assert c['HH_R10']=='OFF'


@pytest.mark.parametrize('ell',[21,22,28,29,64,128,256])
def test_coulomb_finite_samples_and_positive_current(ell):
    z=central_impedance(ell,27,70)
    assert float(z['Re_Z_per_Bohr'])<0
    assert mp.mpf(z['Im_Z_per_Bohr_positive_Wronskian'])>0
    assert 0<float(z['weighted_negative_real_ratio'])<0.038
    assert math.isfinite(float(z['log10_Im_Z']))


def test_coulomb_ell21_reproduces_PHYS51_source_anchor():
    z=central_impedance(21,27,70)
    assert abs(float(z['Re_Z_per_Bohr'])+0.18253880022977345)<4e-15
    assert abs(float(z['Im_Z_per_Bohr_positive_Wronskian'])-0.12712470573077846)<4e-15


def test_coulomb_asymptotic_trend_exploratory_only():
    rows=[central_impedance(l,27,80) for l in (64,128,256)]
    errors=[abs(float(z['weighted_negative_real_ratio'])-1/27) for z in rows]
    assert errors[0]>errors[1]>errors[2]
    logs=[float(z['log10_Im_Z']) for z in rows]
    assert logs[0]>logs[1]>logs[2]
    assert logs[-1]<-308


@pytest.mark.parametrize('elements',[16,24,40,64])
def test_original_screened_fem_collared_hybrid(elements):
    z=fd_screened_collar_hybrid(elements=elements,ells=(21,22,23),m=0,nodes=96)
    assert z['min_eigen_weighted_collar']>float(CERTIFIED_C_D)
    assert z['min_singular_weighted_hybrid']>0
    assert z['screen_operator_norm_at_B']>0
    assert z['screen_offdiagonal_abs_at_B']>0
    assert z['imag_current_of_matched_test_g']>0
    assert z['scientific_status'].startswith('FINITE_ELEMENT_')


def test_finite_element_m_symmetry():
    a=fd_screened_collar_hybrid(elements=24,ells=(21,22),m=1,nodes=96)
    b=fd_screened_collar_hybrid(elements=24,ells=(21,22),m=-1,nodes=96)
    assert abs(a['min_eigen_weighted_collar']-b['min_eigen_weighted_collar'])<1e-13
    assert abs(a['min_singular_weighted_hybrid']-b['min_singular_weighted_hybrid'])<1e-13
    assert abs(a['screen_offdiagonal_abs_at_B']-b['screen_offdiagonal_abs_at_B'])<1e-28


def test_hybrid_exact_abstract_finite_linear_algebra():
    # Manufactured Hermitian positive lambda, complex outgoing Z with j_l>0.
    # This does not establish the infinite-dimensional theorem, whose proof uses
    # compactness and positivity at each Coulomb harmonic instead.
    ls=(21,22,23,29)
    cd=float(CERTIFIED_C_D)
    norm=np.sqrt(np.array([l+1 for l in ls],dtype=float))
    dtn=np.diag(norm) @ np.array([[cd+0.5,0.02,0.,0.],
                                [0.02,cd+0.6,0.01,0.],
                                [0.,0.01,cd+0.7,0.],
                                [0.,0.,0.,cd+0.8]]) @ np.diag(norm)
    diag=np.array([complex(float(central_impedance(l,27)['Re_Z_per_Bohr']),
                           float(central_impedance(l,27)['Im_Z_per_Bohr_positive_Wronskian'])) for l in ls])
    M=dtn-np.diag(diag)
    assert np.linalg.svd(M,compute_uv=False).min()>0
    h=np.array([1+1j,2-2j,0.4,1j],dtype=complex)
    g=np.linalg.solve(M,h)
    assert np.linalg.norm(M@g-h)<5e-14
    assert np.imag(np.vdot(g,M@g))<0


@pytest.mark.parametrize('bad',[20,-1])
def test_bad_ell_domain(bad):
    with pytest.raises(ValueError):barrier_a2(bad)


def test_zero_screen_delta_permitted():
    assert barrier_a2(21,F(0)) > 0


@pytest.mark.parametrize('d',[-1,10**-4])
def test_bad_screen_delta(d):
    with pytest.raises(ValueError):barrier_a2(21,F(str(d)))


def test_bad_coulomb_input():
    with pytest.raises(ValueError):central_impedance(21,19)
    with pytest.raises(ValueError):central_impedance(21,27,40)
    with pytest.raises(ValueError):central_impedance(1025,27)


def test_bad_finite_projection():
    with pytest.raises(ValueError):fd_screened_collar_hybrid(ells=(20,21))
    with pytest.raises(ValueError):fd_screened_collar_hybrid(ells=(21,21))
    with pytest.raises(ValueError):fd_screened_collar_hybrid(ells=(21,),m=22)
