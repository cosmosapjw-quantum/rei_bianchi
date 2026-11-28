"""PHYS41: exact Bernstein identity, source enclosure, six-panel safety."""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import json

import mpmath as mp
import pytest

from wu088_hh.phys33_panel_bernstein import (
    bernstein_sup, _bernstein_transform, radial_cuts,
    source_numerator_polynomial, upper_exp_minus, whole_panel_certificate,
)
from wu088_hh.phys33_residual import value
from wu088_hh.phys33_full_coupled_shell import R

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
PHYS40=ROOT/"research/hh_phys40_20261015/results"


def test_bernstein_coefficients_exact_sampled_convex_hull():
    _bernstein_transform.cache_clear()
    for n in [0,1,2,4,10,27]:
        poly=[F((-1)**i*(3*i+2),i+3) for i in range(n+1)]
        for a,b in [(F(-1),F(1)),(F(1,5),F(11,12)),(F(17,4),F(29,6))]:
            upper=bernstein_sup(poly,a,b)
            assert upper>=0
            assert all(abs(value(poly,a+(b-a)*F(k,45)))<=upper
                       for k in range(46))
    # A second call must reuse the identical exact rational transform.
    bernstein_sup([F(1),F(2)],F(1,5),F(11,12))
    info=_bernstein_transform.cache_info()
    assert info.hits>0 and info.currsize>=1


@pytest.mark.parametrize("lo,hi,first",[
    (F(1,10000),F(1,10),True),
    (F(1,10),F(7,10),False),
    (F(7,10),F(2),False),
])
def test_radial_cut_covering(lo,hi,first):
    cuts=radial_cuts(lo,hi,6,first)
    assert cuts[0]==lo and cuts[-1]==hi
    assert all(x<y for x,y in zip(cuts,cuts[1:]))
    assert sum((y-x for x,y in zip(cuts,cuts[1:])),F(0))==hi-lo


def test_source_taylor_error_is_physically_valid_and_not_overweighted():
    mp.mp.dps=85
    a,b=F(7,10),F(4,5)
    mid,half=F(7,5),F(13,20)
    poly,err=source_numerator_polynomial(a,b,mid,half)
    for i in range(11):
        r=a+(b-a)*F(i,10)
        x=(r-mid)/half
        approx=value(poly,x)/r**3
        exact=mp.mpf(298)/100*mp.exp(-mp.mpf(r.numerator)/r.denominator)
        deviation=abs(exact-mp.mpf(approx.numerator)/approx.denominator)
        assert deviation<=mp.mpf(err.numerator)/err.denominator


def test_exponential_rational_upper_conservative():
    mp.mp.dps=80
    for a in [F(0),F(1,100),F(7,10),F(5),F(20)]:
        b=upper_exp_minus(a,24)
        assert mp.mpf(b.numerator)/b.denominator>=mp.exp(-mp.mpf(a.numerator)/a.denominator)


@pytest.fixture(scope="module")
def all_four():
    return whole_panel_certificate(FROZEN,pieces=4,workers=1,digits=12)


def test_frozen_exact_six_panel_coverage_and_scoped_result(all_four):
    d=all_four
    assert d["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert d["original_input_values_checked"]==1386
    assert d["tiles"]>24
    assert len(d["panels"])==6
    assert d["certified_broken_strong_L2_upper"]==d["certified_full_H1_dual_bulk_upper"]
    assert F(d["gradient_only_Hminus1_bulk_upper"]) > F(d["certified_broken_strong_L2_upper"])
    assert d["not_certified"] and "physical ionization intensity or rate" in d["not_certified"]
    for j,p in enumerate(d["panels"]):
        assert p["actual_input_complex_values_checked"]==231
        assert len(p["cells"])==p["cell_count"]
        assert sum((F(c["radial_interval_a0"][1])-F(c["radial_interval_a0"][0])
                    for c in p["cells"]),F(0))== (
                        F(p["radial_interval_a0"][1])-F(p["radial_interval_a0"][0]))
        if j<5:
            assert F(p["radial_interval_a0"][1])==F(d["panels"][j+1]["radial_interval_a0"][0])


@pytest.mark.parametrize("r,filename",[
    (F(1,2),"SHELL_Q64_r1_2_auto.json"),
    (F(1),"SHELL_Q64_r1_1_auto.json"),
])
def test_coupled_original_PHYS40_shell_below_radial_uniform(all_four,r,filename):
    previous=json.loads((PHYS40/filename).read_text())
    p=all_four["panels"][previous["chosen_panel"]]
    cell=next(c for c in p["cells"] if
              F(c["radial_interval_a0"][0])<=r<=F(c["radial_interval_a0"][1]))
    assert F(previous["angular_norm_L2_upper"]) <= F(cell["angular_L2_uniform_upper"])


def test_validate_inputs_and_no_implicit_float():
    with pytest.raises(ValueError):
        bernstein_sup([F(1)],F(1),F(1))
    with pytest.raises(ValueError):
        bernstein_sup([],F(0),F(1))
    with pytest.raises(ValueError):
        radial_cuts(F(0),F(1),2,True)
    with pytest.raises(ValueError):
        whole_panel_certificate(FROZEN,pieces=True,workers=1)
    with pytest.raises(ValueError):
        whole_panel_certificate(FROZEN,pieces=0,workers=1)
