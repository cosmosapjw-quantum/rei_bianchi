from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]


def _load():
    path = STAGE / "analysis" / "exact_validate.py"
    spec = importlib.util.spec_from_file_location("sparse_local_exact_validate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_exact_sparse_local_contract_closes() -> None:
    receipt = _load().validate_exact_contract()
    assert receipt["status"] == "PASS"
    assert receipt["branch_bilinear_expansion_residual"] == "0"
    assert receipt["hydrogen_generator_invariant_residuals"] == ["0", "0", "0"]
    assert receipt["helium_generator_invariant_residuals"] == ["0", "0", "0"]
    assert receipt["normalized_measure_jvp_sum_residual"] == "0"
    assert receipt["evaluation_site_count"] == 4
    assert receipt["source_safe_rank_lower_bound_per_site"] == 92003
    assert receipt["source_safe_input_rank_lower_bound"] == 368012
    assert receipt["local_polynomial_storage_bytes"] == 17694720
