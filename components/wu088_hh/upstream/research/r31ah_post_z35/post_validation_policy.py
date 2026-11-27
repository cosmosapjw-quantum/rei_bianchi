from __future__ import annotations
import math

VALID_VERDICTS = {
    "PARETO_SUPPORTED_AT_Z35",
    "GLOBAL_SUPPORTED_AT_Z35",
    "TRADEOFF_UNRESOLVED",
}

def midpoint_lower_bounds(E_O, E_K, h_t, h_z=1.0):
    E_O=float(E_O); E_K=float(E_K); h_t=float(h_t); h_z=float(h_z)
    if not all(math.isfinite(x) for x in [E_O,E_K,h_t,h_z]) or E_O < 0 or E_K < 0 or h_t <= 0 or h_z <= 0:
        raise ValueError("finite nonnegative errors and positive widths required")
    return {
        "O_fourth_lower_per_t4": 384.0*E_O/h_t**4,
        "K_second_lower_per_t3": 8.0*E_K/h_t**2,
        "O_fourth_lower_per_z4": 384.0*E_O/h_z**4,
        "K_second_lower_per_t_z2": 8.0*E_K/h_z**2,
    }

def post_z35_action(verdict):
    if verdict not in VALID_VERDICTS:
        raise ValueError("unknown verdict")
    if verdict == "PARETO_SUPPORTED_AT_Z35":
        return {
            "action": "REPORT_SUPPORT_THEN_OPTIONAL_LOCAL_REFINE_RIGHT_CELL",
            "z35_role_if_successor_built": "PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_SUCCESSOR_TRAINING",
            "next_fresh_validation_z": 2.5,
            "auto_execute_next_node": False,
            "auto_retune": False,
            "model_class_review_required": False,
        }
    return {
        "action": "STOP_FOR_MODEL_CLASS_REVIEW",
        "z35_role_if_successor_built": "DO_NOT_CONSUME_WITHOUT_NEW_MODEL_POLICY",
        "next_fresh_validation_z": None,
        "auto_execute_next_node": False,
        "auto_retune": False,
        "model_class_review_required": True,
    }

def z25_information():
    dk=0.1912237840334797
    dd=0.20561180584475613
    return {
        "DeltaK_per_ta": dk,
        "DeltaDmax_per_ta": dd,
        "S_design_only_per_ta": math.hypot(dk,dd),
        "K_half_gap_per_ta": dk/2,
        "Dmax_half_gap_per_ta": dd/2,
        "winner_prediction": False,
    }

def conditional_halving_factors():
    return {"O_cubic_remainder_factor": 1/16, "K_linear_remainder_factor": 1/4}
