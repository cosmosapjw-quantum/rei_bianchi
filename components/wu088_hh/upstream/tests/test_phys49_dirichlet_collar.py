"""PHYS49 exact all-high-l Dirichlet collar Schur theorem, original frozen source."""
from __future__ import annotations

import copy
import hashlib
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path

import mpmath as mp
import pytest

from wu088_hh.phys49_dirichlet_collar import (
    B,T,R,L,FROZEN_SHA,
    barrier_floor,dirichlet_floor,original_screened_coupling_max,
    high_l_dirichlet_collar,_direct_pointwise
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


@pytest.fixture(scope="module")
def theorem():
    return high_l_dirichlet_collar(SOURCE)


def test_original_source_immutability_all_high_ell_exact_rational_floor(theorem):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==FROZEN_SHA
    assert theorem["original_source_sha256"]==FROZEN_SHA
    assert theorem["radius_interval_a0"]==["20","27"]
    assert barrier_floor(21)==F(1693,24300)
    assert dirichlet_floor(21)==F(301657,1190700)
    assert len(theorem["exact_outward_tail_rows"])==10
    assert theorem["scientific_status"].startswith("PROVED_INFINITE_ANGULAR_ZERO_DIRICHLET")


def test_tight_nonzero_screened_dirichlet_coercivity_and_source_ratio(theorem):
    lam=dirichlet_floor(21)
    delta=original_screened_coupling_max(192)
    q=delta/lam
    alpha=delta/(lam-delta)
    assert 0<delta<lam
    assert 0<q<F(1,10**14)
    assert D(theorem["infinite_high_ell_neumann_q_upper"])>=D(q.numerator)/D(q.denominator)
    assert D(theorem["whole_high_response_gain_to_low_u_P_upper"])>=D(alpha.numerator)/D(alpha.denominator)
    assert D(theorem["whole_high_response_gain_to_low_u_P_upper"])<D("1.431e-16")


@pytest.mark.parametrize("ell",[21,22,28,40,41,61,120])
def test_high_centrifugal_barrier_monotone_on_collar(ell):
    base=barrier_floor(ell)
    assert base>0
    assert dirichlet_floor(ell)==base+F(9,49)
    # q(r) negative and barrier decreasing on all rational sampled knots;
    # analytic derivative follows from 2(r-ell(ell+1))/r^3<0.
    samples=[B+(T-B)*F(i,64) for i in range(65)]
    vals=[F(ell*(ell+1),r*r)-F(2,r)-F(49,100) for r in samples]
    assert all(a>=b>=base for a,b in zip(vals,vals[1:]))


@pytest.mark.parametrize("N,expected_rho",[(4,7),(8,10),(12,14),(16,16),(20,18),(24,20),(40,24)])
def test_high_tail_original_physical_analytic_Cheb_direct_selection(theorem,N,expected_rho):
    row=next(r for r in theorem["exact_outward_tail_rows"] if r["N"]==N)
    eps,rho=_direct_pointwise(N,tuple(range(4,29)),192)
    assert rho==row["selected_ellipse_rho"]==expected_rho
    assert row["output_minimum_l"]==21+N
    assert D(row["direct_high_l_plus2S_pointwise_upper"])>=D(eps.numerator)/D(eps.denominator)
    delta=original_screened_coupling_max()
    lam=dirichlet_floor(21)
    lamT=dirichlet_floor(21+N)
    exact=(eps+delta*delta/(lam-delta))/(lamT-delta)
    assert D(row["high_l_conditional_response_L2_gain_upper"])>=D(exact.numerator)/D(exact.denominator)


def test_original_ell_greater_40_closure_scoped_to_zero_traces(theorem):
    row=next(r for r in theorem["exact_outward_tail_rows"] if r["N"]==20)
    assert row["output_minimum_l"]==41
    assert D(row["high_l_conditional_response_L2_gain_upper"])<D("2.617e-33")
    assert D(row["intermediate_multihop_source_upper"])>D(row["direct_high_l_plus2S_pointwise_upper"])
    assert "ZERO DIRICHLET" in theorem["radius_trace"]
    assert theorem["NOT_CERTIFIED"][0].startswith("original physical Coulomb outgoing")


def test_serial_parallel_same_original_mathematical_science(theorem):
    parallel=high_l_dirichlet_collar(SOURCE,workers=2)
    a=copy.deepcopy(theorem)
    for d in (a,parallel):
        d.pop("workers")
        d.pop("elapsed_s")
    assert a==parallel


def test_physical_bytelock_and_invalid_parameters_fail_closed(tmp_path):
    p=tmp_path/"mutated.npz"
    p.write_bytes(SOURCE.read_bytes()[:-5])
    with pytest.raises(ValueError,match="identity"):
        high_l_dirichlet_collar(p)
    for k in ({"Ns":()},{"Ns":(20,20)},{"Ns":(-1,)},{"rhos":(29,)},
              {"rhos":(10,10)},{"workers":8},{"digits":4},{"terms":8}):
        with pytest.raises(ValueError):
            high_l_dirichlet_collar(SOURCE,**k)
    with pytest.raises(ValueError):
        barrier_floor(20)
    with pytest.raises(ValueError):
        barrier_floor(2001)
