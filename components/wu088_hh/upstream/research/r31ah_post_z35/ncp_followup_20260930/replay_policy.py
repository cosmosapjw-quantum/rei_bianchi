from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY_DIR = ROOT / "research/r31ah_post_z35"
POLICY_PATH = POLICY_DIR / "POST_Z35_DECISION_POLICY.json"
spec = importlib.util.spec_from_file_location("post_validation_policy", POLICY_DIR / "post_validation_policy.py")
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
verdicts = set(policy["verdicts"])
assert verdicts == module.VALID_VERDICTS == {
    "PARETO_SUPPORTED_AT_Z35",
    "GLOBAL_SUPPORTED_AT_Z35",
    "TRADEOFF_UNRESOLVED",
}
actions = {verdict: module.post_z35_action(verdict) for verdict in sorted(verdicts)}
assert actions["PARETO_SUPPORTED_AT_Z35"]["next_fresh_validation_z"] == 2.5
assert actions["PARETO_SUPPORTED_AT_Z35"]["z35_role_if_successor_built"] == policy["verdicts"]["PARETO_SUPPORTED_AT_Z35"]["if_successor_built_z35_role"]
assert all(not action["auto_execute_next_node"] and not action["auto_retune"] for action in actions.values())
assert all(actions[v]["action"] == "STOP_FOR_MODEL_CLASS_REVIEW" for v in ("GLOBAL_SUPPORTED_AT_Z35", "TRADEOFF_UNRESOLVED"))
assert all(not policy["verdicts"][v]["automatic_refinement"] for v in verdicts)
assert policy["auto_execute_any_science_node"] is False

h_t = 2.2358772390338113
bounds = module.midpoint_lower_bounds(1.0, 1.0, h_t, 1.0)
assert math.isclose(bounds["O_fourth_lower_per_t4"], 384.0 / h_t**4)
assert math.isclose(bounds["K_second_lower_per_t3"], 8.0 / h_t**2)
assert bounds["O_fourth_lower_per_z4"] == 384.0
assert bounds["K_second_lower_per_t_z2"] == 8.0
assert module.conditional_halving_factors() == {"O_cubic_remainder_factor": 1 / 16, "K_linear_remainder_factor": 1 / 4}

z25 = module.z25_information()
for key in ("DeltaK_per_ta", "DeltaDmax_per_ta", "S_design_only_per_ta", "K_half_gap_per_ta", "Dmax_half_gap_per_ta"):
    assert math.isclose(z25[key], policy["z25_preserved_fresh"][key], rel_tol=1e-15)
assert z25["winner_prediction"] is False
assert policy["direct_z35_output_accessed"] is False

print(json.dumps({
    "schema": "WU088_R31AH_POLICY_REPLAY_V1",
    "policy_sha256": hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest(),
    "verdict_actions": actions,
    "unit_error_lower_bound_coefficients": bounds,
    "conditional_halving_factors": module.conditional_halving_factors(),
    "z25_preoutput_information": z25,
    "source_error_enclosure_certified": False,
    "empirical_HH_error_reduction_claimed": False,
    "direct_z35_output_accessed": False,
    "direct_z25_output_accessed": False,
    "science_node_count": 0,
}, indent=2, sort_keys=True))
