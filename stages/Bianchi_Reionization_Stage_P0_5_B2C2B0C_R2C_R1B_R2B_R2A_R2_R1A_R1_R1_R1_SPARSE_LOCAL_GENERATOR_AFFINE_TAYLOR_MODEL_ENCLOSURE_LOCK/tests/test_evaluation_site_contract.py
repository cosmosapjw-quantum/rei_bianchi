from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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


def test_mprk_sdirk_source_has_four_distinct_state_evaluation_sites() -> None:
    mod = _load("sparse_evaluation_site_contract", STAGE / "analysis/evaluation_site_contract.py")
    contract = mod.build_evaluation_site_contract(REPO)
    assert contract.evaluation_site_names == (
        "population_t0",
        "population_t1_predictor",
        "thermal_tgamma",
        "thermal_t1_final",
    )
    assert contract.evaluation_site_count == 4
    assert contract.source_safe_rank_lower_bound_per_site == 92003
    assert contract.source_safe_input_rank_lower_bound == 368012
    assert contract.local_polynomial_storage_mib == 16.875
    assert contract.global_rank_upper_bound == 44
    assert contract.fixed_substep_parameter_model_complete is False
    assert contract.temporal_control_witness_outside_static_hull is True
