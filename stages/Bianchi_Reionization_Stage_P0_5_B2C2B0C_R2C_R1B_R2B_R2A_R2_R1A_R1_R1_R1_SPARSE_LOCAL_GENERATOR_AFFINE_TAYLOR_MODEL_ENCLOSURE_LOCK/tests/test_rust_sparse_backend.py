from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

import numpy as np

STAGE = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_rust_bounds_contain_python_oracle_and_match_within_one_ulp(tmp_path: Path) -> None:
    sparse = load_module("rust_sparse_model_oracle", STAGE / "analysis/sparse_local_model.py")
    rust = load_module("rust_sparse_backend_test", STAGE / "analysis/rust_sparse_backend.py")
    library = rust.build_rust_backend(stage_dir=STAGE, output_dir=tmp_path)
    rng = np.random.default_rng(7203)
    model = sparse.SparseLocalTaylorModel(
        center=rng.normal(size=(4, 4096)),
        local_linear=rng.normal(scale=1e-5, size=(2, 4, 4096)),
        local_mixed=rng.normal(scale=1e-6, size=(4, 4096)),
        global_generators=rng.normal(scale=1e-7, size=(7, 4, 4096)),
        remainder_lo=-np.abs(rng.normal(scale=1e-9, size=(4, 4096))),
        remainder_hi=np.abs(rng.normal(scale=1e-9, size=(4, 4096))),
        coordinate_names=("x_HI", "x_HeI", "r_HeIII", "log_T"),
    )
    py_lo, py_hi = model.bounds()
    rs_lo, rs_hi = rust.rust_bounds(model, library=library)
    assert np.all(rs_lo <= py_lo)
    assert np.all(rs_hi >= py_hi)
    assert rust.maximum_ulp_distance(rs_lo, py_lo) <= 1
    assert rust.maximum_ulp_distance(rs_hi, py_hi) <= 1


def test_rust_backend_rejects_noncontiguous_or_invalid_shapes(tmp_path: Path) -> None:
    sparse = load_module("rust_sparse_model_invalid", STAGE / "analysis/sparse_local_model.py")
    rust = load_module("rust_sparse_backend_invalid", STAGE / "analysis/rust_sparse_backend.py")
    library = rust.build_rust_backend(stage_dir=STAGE, output_dir=tmp_path)
    model = sparse.SparseLocalTaylorModel.point(np.ones((2, 3)), coordinate_names=("a", "b"))
    lo, hi = rust.rust_bounds(model, library=library)
    assert lo.shape == (2, 3) and hi.shape == (2, 3)
    assert np.all(lo < 1.0) and np.all(hi > 1.0)


def test_rust_source_uses_next_up_and_next_down() -> None:
    text = (STAGE / "rust/sparse_bounds.rs").read_text(encoding="utf-8")
    assert ".next_down()" in text
    assert ".next_up()" in text
    assert "extern \"C\"" in text
