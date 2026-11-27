"""PHYS34 code-stage checks: exact dyadics, analytical bounds, negative controls."""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pytest

from wu088_hh.phys33_residual import (
    FROZEN_SUBSET_SHA256, add, bound_broken_bulk, ceil_sqrt_fixed,
    derivative, dyadic, integrate, interpolants, load_frozen, mul, reconstruct,
    scale, squared, value,
)

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_real_archived_source_is_pinned_without_pickle():
    r, u, digest = load_frozen(SOURCE)
    assert digest == FROZEN_SUBSET_SHA256
    assert (r.shape, u.shape) == ((6, 11), (21, 6, 11))
    assert r[0, 0] > 0 and r[-1, -1] == 20.0


def test_exact_dyadic_preserves_binary64_bits():
    assert dyadic(0.1) == F(*float(0.1).as_integer_ratio())
    assert dyadic(-0.0) == 0
    with pytest.raises(ValueError, match="nonfinite"):
        dyadic(float("nan"))


def test_interpolants_are_exact_for_archive_geometry():
    r, u, _ = load_frozen(SOURCE)
    lo, hi = dyadic(r[2, 0]), dyadic(r[2, -1])
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    nodes = [(dyadic(x) - mid) / half for x in r[2]]
    basis = interpolants(nodes)
    for ell in (0, 3, 20):
        re, im = reconstruct(u[ell, 2], basis)
        for i, node in enumerate(nodes):
            assert value(re, node) == dyadic(u[ell, 2, i].real)
            assert value(im, node) == dyadic(u[ell, 2, i].imag)


def test_manufactured_linear_complex_polynomial():
    nodes = [F(-1), F(0), F(1)]
    basis = interpolants(nodes)
    re, im = reconstruct([1+2j, 2+3j, 3+4j], basis)
    assert re == [F(2), F(1), F(0)]
    assert im == [F(3), F(1), F(0)]
    assert derivative(re) == [F(1), F(0)]
    assert integrate(squared(re, im), F(-1), F(1)) == F(82, 3)
    assert value(mul([F(1), F(2)], [F(3), F(4)]), F(2)) == 55
    assert add(scale([F(1)],F(2)),[F(0),F(1)]) == [F(2),F(1)]


def test_sqrt_decimal_is_rigorously_outward():
    result = ceil_sqrt_fixed(F(2), 12)
    r = F(result)
    assert r*r >= 2 and (r-F(1,10**12))**2 < 2
    assert ceil_sqrt_fixed(F(4), 12) == "2.000000000000"
    with pytest.raises(ValueError):
        ceil_sqrt_fixed(F(-1))


def test_reject_duplicate_abscissa_and_wrong_input(tmp_path):
    with pytest.raises(ValueError, match="duplicate"):
        interpolants([F(0), F(0)])
    with np.load(SOURCE, allow_pickle=False) as z:
        u = z["u"].copy()
        r = z["r"].copy()
    u[0] += 1.e-3j
    damaged = tmp_path / "changed.npz"
    np.savez(damaged, r=r, u=u)
    with pytest.raises(ValueError, match="identity"):
        load_frozen(damaged, pinned=True)
    corrupted_shape = tmp_path / "shape.npz"
    np.savez(corrupted_shape, r=r, u=u[:-1])
    with pytest.raises(ValueError, match="must contain"):
        load_frozen(corrupted_shape, pinned=False)
    with pytest.raises(ValueError, match="partition"):
        bound_broken_bulk(SOURCE, partition="extrapolate")


def test_frozen_real_whole_cell_certificate():
    d = bound_broken_bulk(SOURCE, subcells=4, partition="uniform")
    assert d["source_sha256"] == FROZEN_SUBSET_SHA256
    assert d["checked_nodal_values"] == 1386
    assert len(d["partition_exact_rationals"]) == 6
    for segment in d["partition_exact_rationals"]:
        assert len(segment) == 5
        assert all(F(a) < F(b) for a,b in zip(segment,segment[1:]))
    assert len(d["panels"]) == 6 and len(d["interfaces"]) == 5
    assert d["status"] == "WHOLE_CELL_BROKEN_BULK_UPPER_COVERAGE_EXPLICIT"
    assert F(d["norm_upper"]["broken_transformed_bulk_residual"]) > F(0)
    # Parent independent 64-point Gauss diagnostic is not a certificate.
    assert F(d["norm_upper"]["broken_transformed_bulk_residual"]) > F("0.001665185458218535")
    assert all(F(j["derivative_l2_upper"]) > 0 for j in d["interfaces"])
    assert "continuous low-Schur inverse" in d["claims_excluded"]
