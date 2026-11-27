from __future__ import annotations

import math
from numbers import Real


def _finite_nonnegative(x, name):
    if isinstance(x, bool) or not isinstance(x, Real):
        raise ValueError(name + " must be finite nonnegative real")
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise ValueError(name + " must be finite nonnegative real")
    return x


def _positive(x, name):
    x = _finite_nonnegative(x, name)
    if x <= 0:
        raise ValueError(name + " must be positive")
    return x


def classify_z25_protocol():
    return {
        "numerical_verdict": "PARETO_SUPPORTED_AT_Z25",
        "numerical_result_retained": True,
        "independent_validation_admitted": False,
        "independence_status": "PRE_OUTPUT_ADAPTER_LOCK_VIOLATED_BY_POST_OUTPUT_METADATA_RECOVERY",
        "recovery_scope": "metadata-only numeric normalization of producer z identity",
        "failed_comparator_read_direct_arrays": False,
        "retroactive_independence_repair": False,
        "eligible_for_successor_training": True,
    }


def midpoint_lower_bounds(E_O, E_K, h_t, h_z=1.0):
    EO = _finite_nonnegative(E_O, "E_O")
    EK = _finite_nonnegative(E_K, "E_K")
    ht = _positive(h_t, "h_t")
    hz = _positive(h_z, "h_z")
    return {
        "O_fourth_lower_per_t4": 384.0 * EO / ht**4,
        "K_second_lower_per_t3": 8.0 * EK / ht**2,
        "O_fourth_lower_per_z4": 384.0 * EO / hz**4,
        "K_second_lower_per_t_z2": 8.0 * EK / hz**2,
    }


def successor_training_policy():
    return {
        "model_name": "R31AK_ADAPTIVE_EIGHT_NODE_CUBIC_O_LINEAR_K",
        "training_nodes_z": [0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0],
        "cell_widths_z": [0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5],
        "z25_status": "PROTOCOL_DEVIATED_NUMERICAL_COMPARISON_CONSUMED_AS_R31AK_TRAINING",
        "independent_validation_points": [],
        "model_family_changed": False,
    }


def fresh_candidate_points():
    return [0.25, 0.75, 2.25, 2.75, 3.25, 3.75]


def select_candidate(rows):
    if not rows:
        raise ValueError("at least one fresh candidate row required")
    checked = []
    for r in rows:
        if not isinstance(r, dict) or not {"z", "DeltaK", "DeltaDmax"} <= set(r):
            raise ValueError("candidate row missing required fields")
        z = float(r["z"])
        dk = _finite_nonnegative(r["DeltaK"], "DeltaK")
        dd = _finite_nonnegative(r["DeltaDmax"], "DeltaDmax")
        if not math.isfinite(z):
            raise ValueError("z must be finite")
        checked.append({"z": z, "DeltaK": dk, "DeltaDmax": dd, "S": math.hypot(dk, dd)})
    best = max(checked, key=lambda r: (r["S"], -r["z"]))
    return {"rows": checked, "selected": best, "criterion": "max sqrt(DeltaK^2+DeltaDmax^2); exact tie -> lower z"}


def conditional_halving_coefficients():
    return {"O_cubic": 1 / 16, "K_linear": 1 / 4}
