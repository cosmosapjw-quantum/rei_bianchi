from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_normalization_jvp_is_local_plus_one_rank_one_mode() -> None:
    mod = _load("sparse_global_coupling", STAGE / "analysis/global_coupling.py")
    rng = np.random.default_rng(20260809)
    h = 0.1 + rng.random(64)
    dh = rng.normal(size=64)
    actual = mod.normalized_measure_jvp(h, dh)
    local, global_mode = mod.normalized_measure_jvp_decomposition(h, dh)
    assert np.allclose(actual, local + global_mode, rtol=2e-15, atol=2e-15)
    eps = 2e-7
    fd = ((h + eps * dh) / np.sum(h + eps * dh) - (h - eps * dh) / np.sum(h - eps * dh)) / (2 * eps)
    assert np.allclose(actual, fd, rtol=2e-8, atol=2e-10)
    assert abs(float(np.sum(actual))) < 2e-15
    # The nonlocal term is a scalar times the fixed normalized measure.
    q = h / np.sum(h)
    mask = q > 0
    ratios = global_mode[mask] / q[mask]
    assert np.max(ratios) - np.min(ratios) < 2e-15


def test_owner_amplitude_moment_jacobian_has_rank_three() -> None:
    mod = _load("sparse_global_coupling_rank", STAGE / "analysis/global_coupling.py")
    audit = mod.audit_global_coupling(REPO)
    assert audit.owner_amplitude_moment_names == ("global_x_HII", "global_x_HeI", "global_x_HeII_per_H")
    assert audit.owner_amplitude_jacobian_rank == 3
    assert audit.owner_amplitude_rank_upper_bound == 3
    assert audit.maximum_owner_jacobian_relative_residual < 2e-7


def test_supported_allocation_channels_are_exactly_eight() -> None:
    mod = _load("sparse_global_coupling_support", STAGE / "analysis/global_coupling.py")
    audit = mod.audit_global_coupling(REPO)
    assert audit.normalization_channel_count == 8
    assert audit.normalization_channel_names == (
        "EFFECTIVE_HI_SUBGRID:G1",
        "EFFECTIVE_HI_SUBGRID:G2a",
        "EXPLICIT_HI_ATOMIC:G2b",
        "EXPLICIT_HI_ATOMIC:G3",
        "EXPLICIT_HEI_ATOMIC:G2a",
        "EXPLICIT_HEI_ATOMIC:G2b",
        "EXPLICIT_HEI_ATOMIC:G3",
        "EXPLICIT_HEII_ATOMIC:G3",
    )
    assert audit.global_rank_upper_bound == 11
    assert audit.dense_global_matrix_required is False


def test_global_coupling_contract_is_small_relative_to_local_rank() -> None:
    mod = _load("sparse_global_coupling_ratio", STAGE / "analysis/global_coupling.py")
    audit = mod.audit_global_coupling(REPO)
    assert audit.source_safe_local_rank_lower_bound == 92003
    assert audit.global_rank_upper_bound == 11
    assert audit.global_rank_upper_bound / audit.source_safe_local_rank_lower_bound < 1.3e-4
