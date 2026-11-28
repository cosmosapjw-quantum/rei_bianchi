"""Focused independent checks of the new exact angular error component."""
from fractions import Fraction as F
from pathlib import Path

import pytest
import sympy as sp

from wu088_hh.phys67_angular_certificate import (
    basis_product_degree, decimal_upper, exact_gauss_error_bound,
    json_safe, make_angular_certificate, polynomial_budget,
    screen_polynomial_tail, weighted_ellipse_gates,
)
from wu088_hh.phys66_order_tail import decode_fraction

SOURCE = (Path(__file__).resolve().parents[1]
          / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")


def test_canonical_L64_Q128_is_an_exact_nonzero_fraction():
    # Independent reduction: 8/(4*10^19)/9 * 10^-127.
    expected = F(2, 9*10**146)
    assert polynomial_budget(64, 128) == 127
    assert exact_gauss_error_bound(64, 128) == expected
    assert F(decimal_upper(expected)) >= expected


def test_higher_Q_is_not_silently_underflowed_to_zero():
    bound = exact_gauss_error_bound(64, 512)
    assert bound > 0
    assert F(decimal_upper(bound)) >= bound
    assert decode_fraction(json_safe(bound)) == bound


def test_exact_degree_budget_controls_convergence():
    assert exact_gauss_error_bound(64, 129)*100 == exact_gauss_error_bound(64, 128)
    assert exact_gauss_error_bound(63, 128)*100 == exact_gauss_error_bound(64, 128)
    assert exact_gauss_error_bound(64, 128, 126) == 10*exact_gauss_error_bound(64, 128)


@pytest.mark.parametrize("L,Q", [(64,64),(3,3),(1,1)])
def test_insufficient_Q_cannot_receive_exact_Gram_certificate(L,Q):
    with pytest.raises(ValueError, match="Q >= L\\+1"):
        exact_gauss_error_bound(L,Q)


@pytest.mark.parametrize("args", [(True,128),(64,128.0),(65,128),(-1,128),(64,513)])
def test_invalid_angular_indices_rejected(args):
    with pytest.raises(ValueError):
        exact_gauss_error_bound(*args)


def test_degree_overclaim_rejected():
    with pytest.raises(ValueError):
        exact_gauss_error_bound(64,128,128)
    with pytest.raises(ValueError):
        screen_polynomial_tail(10,"interpolation_without_a_bound")


def test_uniform_exterior_weight_is_a_polynomial_identity():
    r = sp.Symbol("r", real=True)
    q = r*r-sp.Rational(707,100)*r+sp.Rational(49,100)
    gap = sp.expand(q-(r-4)**2)
    assert gap == sp.Rational(93,100)*r-sp.Rational(1551,100)
    assert gap.subs(r,27) == sp.Rational(48,5)
    assert sp.diff(gap,r) > 0
    g = weighted_ellipse_gates()
    assert g["quadratic_gap_at_B"] == F(48,5)


@pytest.mark.parametrize("m", [-2,-1,0,1,2])
def test_associated_basis_Gram_and_polynomial_screen_exact_for_all_signed_m(m):
    # Q=3 exact algebraic GL nodes, L=2, N=1.  Odd-m individual
    # functions are not polynomials; equal-m products are polynomials.
    x = sp.Symbol("x", real=True)
    a = abs(m)
    nodes = [-sp.sqrt(15)/5,sp.Integer(0),sp.sqrt(15)/5]
    weights = [sp.Rational(5,9),sp.Rational(8,9),sp.Rational(5,9)]
    for l in range(a,3):
        for lp in range(a,3):
            norm2 = (sp.Rational(2*l+1,2)*sp.factorial(l-a)/sp.factorial(l+a)
                     *sp.Rational(2*lp+1,2)*sp.factorial(lp-a)/sp.factorial(lp+a))
            product = sp.expand(sp.sqrt(norm2)*(1-x*x)**a
                       *sp.diff(sp.legendre(l,x),x,a)*sp.diff(sp.legendre(lp,x),x,a))
            assert sp.Poly(product,x).degree() == basis_product_degree(l,lp,m)
            assert sp.integrate(product,(x,-1,1)) == int(l==lp)
            for screen in [sp.Integer(1), 2+x/3]:
                f = sp.expand(screen*product)
                exact = sp.integrate(f,(x,-1,1))
                gauss = sp.simplify(sum(w*f.subs(x,z) for w,z in zip(weights,nodes)))
                assert sp.simplify(exact-gauss) == 0


def test_L64_all_signed_m_product_degrees_fit_Q128():
    for m in range(-64,65):
        assert basis_product_degree(64,64,m)+127 == 255
    with pytest.raises(ValueError):
        basis_product_degree(20,21,21)


@pytest.mark.parametrize("degree", [0,1,8,127,255])
def test_reused_Legendre_bound_has_independently_summed_geometric_ratio(degree):
    cheb = 4*screen_polynomial_tail(degree,"chebyshev")
    leg = 4*screen_polynomial_tail(degree,"legendre")
    assert leg/cheb == F(180*degree+290,81)
    assert leg > cheb > 0


def test_original_source_guard_and_error_axes(tmp_path):
    cert = make_angular_certificate(SOURCE,64,128)
    assert cert["source_sha256"] == "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert cert["all_signed_m"]
    assert cert["channel_dimension_factor"] == 1
    assert cert["exact_gauss_quadrature_truncation_certified"]
    assert cert["floating_nodes_weights_basis_screen_roundoff_bound"] is None
    assert cert["excluded_angular_response_bound"] is None
    assert cert["total_numerical_error_bound"] is None
    assert cert["total_numerical_error_certified"] is False
    assert cert["HH_R10"] == "OFF"
    p = tmp_path/"tampered.npz"
    p.write_bytes(SOURCE.read_bytes()+b"tampered")
    with pytest.raises(ValueError,match="source SHA256"):
        make_angular_certificate(p,64,128)
