"""Evaluation-site uncertainty contract for the locked MPRK22/SDIRK2 map.

Without a source-derived temporal regularity law, the branch values evaluated
at different thermochemical states cannot be identified with one fixed pair of
node-local coordinates.  The locked trial evaluates the event source at four
state/time sites.  A source-safe discrete-map enclosure therefore needs a
separate sparse local polynomial block at each site, or an outward remainder
proved to cover their independent variation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
from pathlib import Path
import sys


EVALUATION_SITES = (
    "population_t0",
    "population_t1_predictor",
    "thermal_tgamma",
    "thermal_t1_final",
)


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class EvaluationSiteContract:
    evaluation_site_names: tuple[str, ...]
    evaluation_site_count: int
    source_safe_rank_lower_bound_per_site: int
    source_safe_input_rank_lower_bound: int
    local_polynomial_storage_mib: float
    global_rank_upper_bound_per_site: int
    global_rank_upper_bound: int
    fixed_substep_parameter_model_complete: bool
    temporal_control_witness_outside_static_hull: bool
    source_temporal_regularization_available: bool
    required_next_representation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_evaluation_site_contract(repo_root: Path) -> EvaluationSiteContract:
    repo = Path(repo_root).resolve()
    stage = Path(__file__).resolve().parents[1]
    source = _load("sparse_eval_site_source", stage / "analysis/source_generators.py")
    global_mod = _load("sparse_eval_site_global", stage / "analysis/global_coupling.py")
    temporal = _load("sparse_eval_site_temporal", stage / "analysis/temporal_control_audit.py")
    source_audit = source.build_source_rhs_taylor(repo)
    global_audit = global_mod.audit_global_coupling(repo)
    witness = temporal.run_temporal_control_audit(
        repo, lane="LOCAL_NEUTRAL_HAZARD_PRIMARY"
    )
    site_count = len(EVALUATION_SITES)
    # Per site: two local linear generators plus one local mixed generator,
    # for four reduced coordinates and all physical nodes.
    storage_bytes = site_count * 3 * 4 * source_audit.node_count * 8
    return EvaluationSiteContract(
        evaluation_site_names=EVALUATION_SITES,
        evaluation_site_count=site_count,
        source_safe_rank_lower_bound_per_site=source_audit.rank_lower_bound,
        source_safe_input_rank_lower_bound=site_count * source_audit.rank_lower_bound,
        local_polynomial_storage_mib=float(storage_bytes / 2**20),
        global_rank_upper_bound_per_site=global_audit.global_rank_upper_bound,
        global_rank_upper_bound=site_count * global_audit.global_rank_upper_bound,
        fixed_substep_parameter_model_complete=False,
        temporal_control_witness_outside_static_hull=bool(
            witness.maximum_outside_fraction_of_static_width > 0.0
        ),
        source_temporal_regularization_available=False,
        required_next_representation=(
            "EVALUATION_SITE_LOCAL_GENERATORS_PLUS_VALIDATED_DISCRETE_MAP_REMAINDER"
        ),
    )


__all__ = ["EVALUATION_SITES", "EvaluationSiteContract", "build_evaluation_site_contract"]
