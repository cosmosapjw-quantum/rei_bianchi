"""PHYS36 C7 exact source cancellation, frozen input, continuum-scope tests."""
from fractions import Fraction as Q
from pathlib import Path
import json
import mpmath as mp
import pytest

from wu088_hh.phys33_coupled_source import (
    exp_negative_bounds, outward_decimal, poly_to_radius_x,
    _moment_exp_one, _source_sq_interval,
    radial_source_cancellation, bound_coupled_source,
)
from wu088_hh.phys33_coupled_preview import coupled_residual_preview

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def exact_to_mp(a):
    return mp.mpf(a.numerator)/mp.mpf(a.denominator)


@pytest.mark.parametrize("x",[
    Q(0),Q(1,10000),Q(7,10),Q(5),Q(20),Q(40)])
def test_nonnegative_exponential_bounds_are_outward(x):
    # Compare a separately controlled, resolvable-width rational bracket:
    # the scientific calculation still uses 256 positive Taylor terms.
    terms=20 if x<=Q(1,100) else (64 if x<=1 else 128)
    lo,hi=exp_negative_bounds(x,terms)
    mp.mp.dps=200
    exact=mp.exp(-exact_to_mp(x))
    assert exact_to_mp(lo)<=exact<=exact_to_mp(hi)
    assert lo<=hi and lo>=0 and hi<=1
    with pytest.raises(ValueError):
        exp_negative_bounds(Q(-1))


@pytest.mark.parametrize("left,right,n",[
    (Q(1,10000),Q(1,10),0),
    (Q(1,10),Q(7,10),2),
    (Q(7,10),Q(2),8),
    (Q(5),Q(10),11),
    (Q(10),Q(20),4)
])
def test_exponential_radial_moments_independent_high_precision(left,right,n):
    mp.mp.dps=170
    terms=32 if right<=Q(1,10) else (80 if right<=2 else 128)
    lo,hi=_moment_exp_one(n,left,right,terms)
    actual=mp.gammainc(n+1,exact_to_mp(left),exact_to_mp(right))
    assert exact_to_mp(lo) <= actual <= exact_to_mp(hi)
    assert hi>=lo>=0


def test_rational_to_physical_polynomial_and_outward_signed_printing():
    assert poly_to_radius_x([Q(2),Q(3),Q(-4)],Q(1),Q(2)) == [
        Q(-1,2), Q(7,2), Q(-1)]
    assert outward_decimal(Q(-1,3),6,False)=="-0.333334"
    assert outward_decimal(Q(-1,3),6,True)=="-0.333333"
    with pytest.raises(ValueError):
        outward_decimal(Q(1),30,True)


def test_source_squared_exact_positive_with_high_precision_quadrature():
    mp.mp.dps=160
    scale=(Q(149,100))**2
    left,right=Q(7,10),Q(2)
    lo,hi=_source_sq_interval(left,right,256)
    actual=4*exact_to_mp(scale)*mp.quad(
        lambda r:r**2*mp.exp(-2*r),[exact_to_mp(left),exact_to_mp(right)])
    assert exact_to_mp(lo)<=actual<=exact_to_mp(hi)


def test_exact_angular_convolution_norm_at_R_07():
    R=Q(7,10)
    phiE2=(3+6*R+4*R*R)/24
    elo,ehi=exp_negative_bounds(2*R,256)
    mp.mp.dps=120
    computed=exact_to_mp(phiE2)*mp.exp(-2*exact_to_mp(R))
    assert exact_to_mp(phiE2*elo)<=computed<=exact_to_mp(phiE2*ehi)
    # Independent one-dimensional angular-reduced source convolution formula.
    def sphere(r):
        a=abs(r-exact_to_mp(R));b=r+exact_to_mp(R)
        return ((1+2*a)*mp.exp(-2*a)-(1+2*b)*mp.exp(-2*b))/(8*r*exact_to_mp(R))
    independent=4*mp.quad(lambda r:r*r*mp.exp(-2*r)*sphere(r),
                          [mp.mpf("1e-20"),exact_to_mp(R),mp.mpf(2),
                           mp.mpf(10),mp.mpf(40)])
    assert abs(independent-computed)<mp.mpf("1e-30")


def test_source_overlap_parallel_and_serial_match_mathematical_intervals():
    serial=radial_source_cancellation(FROZEN,workers=1)
    parallel=radial_source_cancellation(FROZEN,workers=2)
    for k in ("overlap_lower","overlap_upper","source_squared_lower",
              "source_squared_upper","panels","input_sha256"):
        assert serial[k]==parallel[k]
    # Each endpoint displayed outward, no global huge Fraction serialization.
    assert Q(outward_decimal(serial["overlap_lower"],12,False)) <= serial["overlap_lower"]
    assert Q(outward_decimal(serial["overlap_upper"],12,True)) >= serial["overlap_upper"]


def test_completed_FROZEN_source_certificate_improves_screened_triangle():
    r=bound_coupled_source(FROZEN,workers=2,screen_cells=8)
    assert r["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert Q(r["norm_upper"]["screened_broken_bulk_admitted"])<Q("2.61")
    assert Q(r["norm_upper"]["screened_broken_bulk_with_direct_source"])<Q(
        r["norm_upper"]["screened_broken_bulk_previous"])
    assert Q(r["norm_upper"]["radial_Coulomb_minus_bare_source"])<Q("0.726")
    assert r["chosen"]=="direct_coulomb_source_overlap"
    assert any("continuous low-Schur inverse" in note for note in r["NOT_CERTIFIED"])


def test_independent_vectorized_angular_diagnostic_is_not_an_enclosure():
    p=coupled_residual_preview(FROZEN,nr=64,nmu=96)
    q=coupled_residual_preview(FROZEN,nr=96,nmu=160)
    assert p["status"].endswith("NOT_CERTIFIED")
    assert abs(p["sampled_D_minus_source_l2"]-0.7255185696194)<1e-9
    assert abs(q["sampled_D_minus_source_l2"]-0.7255185696194)<1e-9
    assert p["sampled_coupled_l2"]<0.003 and q["sampled_coupled_l2"]<0.003
    assert q["source_sha256"]==p["source_sha256"]
    with pytest.raises(ValueError):
        coupled_residual_preview(FROZEN,nr=8)
