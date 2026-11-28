from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import shutil

import pytest
import sympy as sp

from wu088_hh import phys69_angular_tail as tail


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("ell", [20, 29, 36, 65, 128, 1024])
def test_all_mode_anchor_identities(ell):
    w = tail.mode_witness(ell)
    assert w["nu_anchor"] == -F(7*ell+91, 100*(ell-1)**2)
    assert w["nu_allowed"] == F(189, 100*(ell+1))
    direct = (ell*(ell+1)/w["anchor"]**2 - 2/w["anchor"])/tail.K
    direct *= w["allowed_start"] - w["anchor"]
    assert direct == w["lognorm_exponent"]
    assert 100*F(ell+1, 189)*w["exp_rational_upper"] < tail.mode_ratio_bound(ell)


def test_uniform_polynomial_sign_proof():
    n = sp.Symbol("n", nonnegative=True)
    j = n+20
    # This coefficient certificate applies to every real n>=0, not a sample grid.
    p = sp.Poly(sp.expand(49*j*j-378*j-3591), n)
    assert p.all_coeffs() == [49, 1582, 8449]
    assert all(c > 0 for c in p.all_coeffs())


@pytest.mark.parametrize("cutoff", [19, 28, 36, 64])
def test_tail_telescopes_one_exact_mode(cutoff):
    x = F(1, 100)
    assert (tail.quadratic_geometric_tail(cutoff)
            - tail.quadratic_geometric_tail(cutoff+1)) == (cutoff+2)**2*x**(cutoff+1)


def test_geometric_sum_independent_symbolic_derivative():
    x = sp.Symbol("x", positive=True)
    start = 29
    g = x**start/(1-x)
    s = sp.expand(x*sp.diff(x*sp.diff(g, x)+g, x)+x*sp.diff(g, x)+g)
    exact = s.subs(x, sp.Rational(1, 100))
    assert F(int(sp.numer(exact)), int(sp.denom(exact))) == tail.quadratic_geometric_tail(28)


@pytest.mark.parametrize("m", [0, 1, 2])
def test_angular_selection_exact_associated_basis(m):
    x = sp.Symbol("x", real=True)
    # The discarded comparison polynomial degree1 cannot connect ell2 to j4.
    product = sp.expand(sp.assoc_legendre(2, m, x)*sp.assoc_legendre(4, m, x))
    assert sp.integrate(product*x, (x, -1, 1)) == 0
    # Degree2 is the first allowed coupling; test is sensitive to an off-by-one.
    assert sp.integrate(product*x*x, (x, -1, 1)) != 0


def test_normalization_of_single_mode_majorant():
    j = 36
    v1 = tail.angular_offdiagonal_multiplier(21, j)
    v2 = tail.angular_offdiagonal_multiplier(20, j)
    one = tail.external_ratio_product(21, 20)*tail.mode_ratio_bound(j)**2*v1*v2/16
    assert tail.excluded_second_born_bound(j-1)-tail.excluded_second_born_bound(j) == one


@pytest.mark.parametrize("m", [-20, -7, 0, 7, 20])
def test_same_tail_all_signed_m(m):
    assert tail.excluded_second_born_bound(36, m=m) == tail.excluded_second_born_bound(36)


def test_fixed_goal_chooses_36_without_relaxation():
    assert tail.excluded_second_born_bound(35) > F("1e-62")
    assert tail.excluded_second_born_bound(36) < F("1e-63")
    assert tail.minimum_cutoff_for_angular_goal("1e-62") == 36
    assert tail.minimum_cutoff_for_angular_goal("1e-63") == 36
    assert tail.minimum_cutoff_for_angular_goal("1e-62", maximum=35) is None


def test_low_external_ratio_reuses_saved_gamma():
    saved, _ = tail.inherit(ROOT)
    g = saved["analytic_radial_cutoff"]["gamma"]
    assert F(int(g["numerator_hex"], 16), int(g["denominator_hex"], 16)) == 5929
    assert tail.external_ratio_product(21, 20) == 5929
    assert tail.external_ratio_product(64, 20) == 32400


def test_coarse_all_angular_contains_old_and_has_strict_signs():
    result = tail.coarse_all_angular_from_saved(ROOT)
    assert result["new_radial_integrations"] == 0
    assert result["real_part_strictly_positive"] is True
    assert result["imag_part_strictly_positive"] is True
    assert tail.read_rational(result["total_error"]) == (
        tail.read_rational(result["inherited_full_radial_error"])
        + tail.read_rational(result["excluded_angular_error"]))
    assert result["nonlinear_response_error"] is None
    assert result["HH_R10"] == "OFF"


def test_bound_survives_binary64_underflow():
    value = tail.excluded_second_born_bound(512)
    display = tail.upward_decimal(value)
    assert F(display) >= value > 0
    assert float(value) == 0
    assert tail.read_rational(tail.rational_record(value)) == value


def test_inherited_proof_tamper_refused(tmp_path):
    _, pins = tail.inherit(ROOT)
    for path in pins:
        target = tmp_path/path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/path, target)
    target = tmp_path/"research/hh_phys66_20261018/r5/PROOF.md"
    target.write_bytes(target.read_bytes()+b"changed")
    with pytest.raises(ValueError, match="identity mismatch"):
        tail.inherit(tmp_path)


@pytest.mark.parametrize("call", [
    lambda: tail.mode_ratio_bound(19),
    lambda: tail.mode_ratio_bound(True),
    lambda: tail.excluded_second_born_bound(20),
    lambda: tail.excluded_second_born_bound(36, ell=65),
    lambda: tail.excluded_second_born_bound(36, m=21),
    lambda: tail.angular_offdiagonal_multiplier(21, 21),
    lambda: tail.minimum_cutoff_for_angular_goal(1e-62),
    lambda: tail.minimum_cutoff_for_angular_goal("0"),
    lambda: tail.quadratic_geometric_tail(28, 1),
    lambda: tail.quadratic_geometric_tail(28, 0.01),
])
def test_domain_refuses_unproved_or_inexact_input(call):
    with pytest.raises(ValueError):
        call()
