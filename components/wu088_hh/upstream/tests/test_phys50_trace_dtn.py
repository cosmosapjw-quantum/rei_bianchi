"""PHYS50: rigorous arbitrary high-ell nonzero trace and screened DtN."""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
from pathlib import Path
import hashlib
import math
import mpmath as mp
import pytest

from wu088_hh.phys50_trace_dtn import (
    B,T,D as WIDTH,C_TRACE,FROZEN_SHA,
    verified_high_trace_lifting,hat_width,
    hat_energy_bound_per_pair,sqrt_upper_fraction
)
from wu088_hh.phys49_dirichlet_collar import (
    barrier_floor,dirichlet_floor,original_screened_coupling_max
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


@pytest.fixture(scope="module")
def theorem():
    return verified_high_trace_lifting(SOURCE)


def test_original_frozen_1386_source_lock_and_exact_energy_trace(theorem):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==FROZEN_SHA
    assert theorem["source_sha256"]==FROZEN_SHA
    assert C_TRACE==F(4849,16800)
    assert theorem["exact_trace_energy_coefficient"]=="4849/16800"
    assert theorem["nonzero_trace_allowed"] is True
    assert theorem["physical_outgoing_high_trace"]=="UNKNOWN_NOT_SUPPLIED"
    assert theorem["radius_interval_a0"]==["20","27"]
    assert len(theorem["sample_high_ell_hats"])==6


@pytest.mark.parametrize("ell",[21,22,28,41,61,120,300,1000])
def test_all_ell_explicit_disjoint_hat_and_exact_energy_bound(ell):
    w=hat_width(ell)
    assert w==F(7,2*(ell+1))
    assert 2*w<F(7)
    E=hat_energy_bound_per_pair(ell)
    assert E==F(1,w)+F(ell*(ell+1),400)*w/3
    assert E<=C_TRACE*(ell+1)
    # independent exact primitive ∫_0^w (1-s/w)^2 ds=w/3
    assert F(w,3)==F(w,1)/3


@pytest.mark.parametrize("ell",[21,28,41,120])
def test_real_coulomb_high_potential_in_exact_positivity_region(ell):
    bar=barrier_floor(ell)
    assert bar>=barrier_floor(21)==F(1693,24300)
    d=original_screened_coupling_max()
    assert bar>d
    lam=dirichlet_floor(21)
    assert lam==F(301657,1190700)
    assert F(theorem_energy_factor(ell)).numerator>0


def theorem_energy_factor(ell):
    return hat_energy_bound_per_pair(ell)


@pytest.mark.parametrize("ell",[21,25,41,120])
def test_continuum_hat_energy_analytic_wolfram_parity(ell):
    """Independent mpmath quadrature for the two disjoint linear hat sections."""
    w=hat_width(ell)
    with mp.workdps(80):
        width=mp.mpf(w.numerator)/w.denominator
        lower=mp.mpf(20)
        upper=mp.mpf(27)
        L=ell*(ell+1)
        def grad(x):return -1/width
        def h(x):return 1-(x-lower)/width
        en=mp.quad(lambda x:grad(x)**2+(mp.mpf(L)/400)*h(x)**2,
                   [lower,lower+width])
        bound=hat_energy_bound_per_pair(ell)
        exact=mp.mpf(bound.numerator)/bound.denominator
        assert abs(en-exact)<mp.mpf("1e-65")


def test_full_energy_coercivity_and_upper_with_actual_screening(theorem):
    delta=original_screened_coupling_max()
    beta=barrier_floor(21)-delta
    assert beta>F(0)
    gamma=sqrt_upper_fraction(C_TRACE/beta,24)
    assert gamma*gamma>=C_TRACE/beta
    assert F(D(theorem["trace_to_high_homogeneous_L2_gain_upper"]))>=gamma
    assert F(D(theorem["screened_high_to_low_feedback_from_unknown_traces_upper"]))>=delta*gamma
    lam=dirichlet_floor(21)
    alpha=delta/(lam-delta)
    assert F(D(theorem["original_PHYS49_zero_trace_force_gain_upper"]))>=alpha
    assert F(D(theorem["screened_high_to_low_feedback_from_low_field_upper"]))>=delta*alpha


@pytest.mark.parametrize("decimals",[12,18,24,36])
def test_positive_isqrt_rigorous_upward_sqrt(decimals):
    x=F(4849,16800)/(F(1693,24300)-original_screened_coupling_max())
    v=sqrt_upper_fraction(x,decimals)
    assert v*v>=x
    assert (v-F(1,10**decimals))**2<x


def test_modified_original_bytes_fail_closed(tmp_path):
    bad=tmp_path/"fake.npz"
    bad.write_bytes(SOURCE.read_bytes()[:-1])
    with pytest.raises(ValueError,match="original immutable"):
        verified_high_trace_lifting(bad)
    for kwargs in ({"terms":7},{"digits":4},{"examples":()},{"examples":(21,21)},
                   {"examples":(20,)},{"examples":(21,2000000)}):
        with pytest.raises(ValueError):
            verified_high_trace_lifting(SOURCE,**kwargs)
    with pytest.raises(ValueError):
        sqrt_upper_fraction(F(-1))
    with pytest.raises(ValueError):
        hat_width(20)


def test_noncertifying_actual_screened_DtN_preview():
    import sys
    sys.path.insert(0,str(ROOT/"scripts"))
    from phys50_trace_preview import evaluate
    d=evaluate(SOURCE,nrad=32,nmu=128,last_ell=28,repeats=3)
    assert d["source_sha256"]==FROZEN_SHA
    assert d["radial_zero_Dirichlet_not_imposed"]
    assert d["discrete_DtN_eigen_min"]>0
    assert d["discrete_DtN_eigen_max"]<float(C_TRACE)
    assert d["energy_boundary_identity_abs_residual"]<1e-12
    assert d["measured_high_L2"]<d["rigorous_trace_to_high_L2_upper_for_prescribed_g"]
    assert d["matched_lu_rhs_max_difference"]<1e-12
