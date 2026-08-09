from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
STAGE = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_local_bilinear_bounds_are_outward_and_contain_all_corners() -> None:
    sparse = load_module("sparse_local_model_test", STAGE / "analysis/sparse_local_model.py")
    rng = np.random.default_rng(7201)
    center = rng.normal(size=(4, 17))
    local = rng.normal(scale=1e-3, size=(2, 4, 17))
    mixed = rng.normal(scale=1e-4, size=(4, 17))
    global_modes = rng.normal(scale=1e-5, size=(3, 4, 17))
    remainder_lo = -np.abs(rng.normal(scale=1e-7, size=(4, 17)))
    remainder_hi = np.abs(rng.normal(scale=1e-7, size=(4, 17)))
    model = sparse.SparseLocalTaylorModel(
        center=center,
        local_linear=local,
        local_mixed=mixed,
        global_generators=global_modes,
        remainder_lo=remainder_lo,
        remainder_hi=remainder_hi,
        coordinate_names=("x_HI", "x_HeI", "r_HeIII", "log_T"),
    )
    lower, upper = model.bounds()
    assert np.all(lower <= upper)
    for tv in (-1.0, 1.0):
        for tf in (-1.0, 1.0):
            for eta in (
                np.array([-1.0, -1.0, -1.0]),
                np.array([1.0, 1.0, 1.0]),
                np.array([1.0, -1.0, 1.0]),
            ):
                value = model.evaluate(
                    theta_v=np.full(17, tv),
                    theta_f=np.full(17, tf),
                    eta=eta,
                )
                assert np.all(value + remainder_lo >= lower)
                assert np.all(value + remainder_hi <= upper)
    assert model.storage_bytes < (center.size + local.size + mixed.size + global_modes.size + remainder_lo.size + remainder_hi.size + 16) * 8


def test_bounds_use_exact_bilinear_corner_range_not_independent_abs_sum() -> None:
    sparse = load_module("sparse_local_model_exact_test", STAGE / "analysis/sparse_local_model.py")
    center = np.zeros((1, 1))
    local = np.array([[[1.0]], [[1.0]]])
    mixed = np.array([[1.0]])
    model = sparse.SparseLocalTaylorModel(
        center=center,
        local_linear=local,
        local_mixed=mixed,
        global_generators=np.empty((0, 1, 1)),
        remainder_lo=np.zeros((1, 1)),
        remainder_hi=np.zeros((1, 1)),
        coordinate_names=("q",),
    )
    lower, upper = model.bounds()
    # q = theta_v + theta_f + theta_v theta_f has corner range [-1, 3],
    # whereas an independent absolute sum would incorrectly give [-3, 3].
    assert lower[0, 0] <= -1.0
    assert lower[0, 0] > -1.00000000000001
    assert upper[0, 0] >= 3.0
    assert upper[0, 0] < 3.00000000000001


def test_point_degenerate_model_is_exact() -> None:
    sparse = load_module("sparse_local_model_point_test", STAGE / "analysis/sparse_local_model.py")
    center = np.arange(12, dtype=float).reshape(3, 4)
    model = sparse.SparseLocalTaylorModel.point(center, coordinate_names=("a", "b", "c"))
    lo, hi = model.bounds()
    assert np.array_equal(lo, np.nextafter(center, -np.inf))
    assert np.array_equal(hi, np.nextafter(center, np.inf))
    assert np.array_equal(model.evaluate(theta_v=np.zeros(4), theta_f=np.zeros(4)), center)
    assert model.active_local_rank == 0
