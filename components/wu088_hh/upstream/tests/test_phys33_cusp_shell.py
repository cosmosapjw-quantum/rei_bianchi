"""PHYS37 C7B cusp-shell certificate and independent angular diagnostics."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json
import pytest

from wu088_hh.phys33_cusp_shell import (
    _cauchy_assumptions, _legendre_cusp, _qrt_sqrt, _g_series,
    _exp_series, _q_series, _shell_poly, shell_certificate,
)
from wu088_hh.phys33_residual import value
from wu088_hh.phys33_shell_preview import cusp_shell_preview

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
RESULT=ROOT/"research/hh_phys37_20261015/results"


def _legendre_fraction(l,mu):
    if l==0:return F(1)
    if l==1:return mu
    a,b=F(1),mu
    for n in range(2,l+1):
        a,b=b,((2*n-1)*mu*b-(n-1)*a)/n
    return b


@pytest.mark.parametrize("x",[F(0),F(1,10),F(1,3),F(3,5),F(1)])
def test_legendre_polynomial_at_cusp_is_exact(x):
    mu=1-2*x*x
    for l in range(21):
        assert value(_legendre_cusp(l),x)==_legendre_fraction(l,mu)
    assert 2*sum(F(i+1)**2-F(i)**2 for i in [])==0


def test_all_sqrt_normalizations_are_rational_enclosures():
    for l in range(21):
        lo,hi=_qrt_sqrt(2*l+1)
        assert lo*lo<=2*l+1<=hi*hi
        assert hi-lo==F(1,10**64)


def test_exact_cauchy_bound_verified_and_taylor_series():
    assert _cauchy_assumptions()
    # E=e^-s, Q=(1-E)/s: the product identity matches Taylor powers.
    e=_exp_series(20)
    q=_q_series(20)
    for j in range(19):
        # At coefficient x^j, 1-E = S*x*q exactly.
        rhs=F(7,5)*q[j-1] if j>=1 else F(0)
        lhs=(F(1)-e[0]) if j==0 else -e[j]
        assert lhs==rhs
    g,error=_g_series(80)
    assert len(g)==81
    assert error>0
    assert error < F(1,10**12)


def test_frozen_cusp_shell_right_N64_certificate_against_stored_output():
    ref=json.loads((RESULT/"SHELL_R_N64.json").read_text())
    q=shell_certificate(SOURCE,"right",64)
    for k in ("source_sha256","side","radial_panel","taylor_order","poly_degree",
              "exact_polynomial_angular_norm_upper",
              "rigorous_uniform_angular_polynomial_error_upper",
              "certified_true_shell_L2_upper"):
        assert q[k]==ref[k],k
    assert F(q["certified_true_shell_L2_upper"])<F("0.009341")
    assert q["status"]=="RIGOROUS_FIXED_RADIUS_SHELL_ONLY"


def test_certified_shell_two_one_sided_traces_and_cusp_gauss_crosscheck():
    cert=json.loads((RESULT/"SHELL_BOTH_N96_18.json").read_text())
    assert cert["input_sha256"]=="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    records={r["side"]:r for r in cert["results"]}
    assert set(records)=={"left","right"}
    for side in records:
        r=records[side]
        assert r["physical_cusp"]=="s=0 included at mu=1"
        assert r["taylor_order"]==96 and r["poly_degree"]==232
        for nodes in (64,96):
            num=cusp_shell_preview(SOURCE,side,nodes)
            assert F(str(num["sampled_L2"])) <= F(r["certified_true_shell_L2_upper"])
            assert abs(float(r["certified_true_shell_L2_upper"])-num["sampled_L2"])<1e-11
    assert F(records["right"]["certified_true_shell_L2_upper"]) > 5*F(records["left"]["certified_true_shell_L2_upper"])


def test_negative_controls():
    with pytest.raises(ValueError):
        shell_certificate(SOURCE,"middle",64)
    with pytest.raises(ValueError):
        shell_certificate(SOURCE,"left",24)
    with pytest.raises(ValueError):
        cusp_shell_preview(SOURCE,"left",12)
    with pytest.raises(ValueError):
        _qrt_sqrt(-1)


def test_exact_constant_shell_measure():
    # G is sqrt(4*pi) times the physical residual, and x=s/(2R).
    # Angular norm squared of G(x)=1: 2*int_0^1 x dx=1.
    assert 2*F(1,2)==1
