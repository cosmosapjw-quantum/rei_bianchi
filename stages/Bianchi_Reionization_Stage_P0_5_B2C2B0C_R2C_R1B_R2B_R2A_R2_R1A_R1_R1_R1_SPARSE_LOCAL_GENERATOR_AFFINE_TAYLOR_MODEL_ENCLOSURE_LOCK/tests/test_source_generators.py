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


def test_source_rhs_generators_have_full_node_local_rank_and_invariants() -> None:
    source = load_module("sparse_source_generator_test", STAGE / "analysis/source_generators.py")
    result = source.build_source_rhs_taylor(ROOT)
    assert result.model.center.shape == (4, 46080)
    assert result.model.local_linear.shape == (2, 4, 46080)
    assert result.model.local_mixed.shape == (4, 46080)
    assert result.rank_lower_bound == 92003
    assert result.robust_rank2_nodes == 45923
    assert result.rank1_nodes == 157
    assert result.below_table_nodes == 21600
    assert result.population_linear.shape == (2, 5, 46080)
    assert result.population_mixed.shape == (5, 46080)
    assert np.max(np.abs(result.population_linear[:, 0] + result.population_linear[:, 1])) == 0.0
    assert np.max(np.abs(np.sum(result.population_linear[:, 2:5], axis=1))) == 0.0
    assert np.max(np.abs(result.population_mixed[0] + result.population_mixed[1])) == 0.0
    assert np.max(np.abs(np.sum(result.population_mixed[2:5], axis=0))) == 0.0
    assert result.model.active_local_rank == 92003
    assert result.model.global_rank == 0


def test_source_rhs_polynomial_matches_all_four_local_branch_corners() -> None:
    source = load_module("sparse_source_generator_corner_test", STAGE / "analysis/source_generators.py")
    result = source.build_source_rhs_taylor(ROOT)
    rng = np.random.default_rng(7202)
    nodes = rng.choice(result.node_count, size=64, replace=False)
    for tv in (-1.0, 1.0):
        for tf in (-1.0, 1.0):
            analytic = result.evaluate_local_rhs(nodes=nodes, theta_v=tv, theta_f=tf)
            direct = result.evaluate_direct_local_rhs(nodes=nodes, theta_v=tv, theta_f=tf)
            scale = np.maximum(np.abs(direct), 1e-300)
            assert np.max(np.abs(analytic - direct) / scale) < 5e-13


def test_hummer_seaton_event_distance_is_positive_or_exactly_on_knot() -> None:
    source = load_module("sparse_source_generator_event_test", STAGE / "analysis/source_generators.py")
    result = source.build_source_rhs_taylor(ROOT)
    assert result.table_event_distance_logT.shape == (46080,)
    assert np.all(result.table_event_distance_logT >= 0.0)
    assert np.count_nonzero(result.table_event_distance_logT == 0.0) == 0
    assert result.minimum_table_event_distance_logT > 0.0
