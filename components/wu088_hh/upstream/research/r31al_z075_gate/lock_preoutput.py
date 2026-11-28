"""Create the secondary preregistration and one-shot scope before direct output."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True, allow_nan=False) + "\n")


def main():
    repo = Path(__file__).resolve().parents[2]
    base = repo / "research/r31al_z075_gate/ncp_followup_20260930"
    parent = repo / "research/r31ak_eight_node/ncp_followup_20260930"
    if not json.loads((base / "PRIMARY_LOCK_VERIFICATION.json").read_text())["parent_unchanged"]:
        raise ValueError("parent primary drift")
    check = json.loads((base / "REFINEMENT_PROPAGATION_CHECK.json").read_text())
    if check["status"] != "PASS" or max(check["identity_2norm_gaps"].values()) > 2e-12:
        raise ValueError("REFINE_PROPAGATION_CONTRACT_MISMATCH")
    rule = {"schema": "WU088_R31AL_SECONDARY_REFINEMENT_DECISION_RULE_V1",
            "models": ["R31AK_ADAPTIVE_EIGHT_NODE_CUBIC_O_LINEAR_K", "R31AD_FIVE_NODE_UNIT_CELL_CUBIC_O_LINEAR_K"],
            "primary_metrics": ["E_K", "E_Dmax"], "comparison_tolerance_per_ta": 1e-10,
            "pareto_rule": "both <= competitor+tol and at least one < competitor-tol",
            "verdicts": ["REFINED_PARETO_SUPPORTED_AT_Z075", "COARSE_PARETO_SUPPORTED_AT_Z075", "REFINEMENT_TRADEOFF_UNRESOLVED"],
            "mandatory_outputs": ["refined_E_O", "refined_E_dotO", "refined_E_K", "refined_E_Dcol", "refined_E_Drow", "refined_E_Dmax",
                                  "coarse_E_O", "coarse_E_dotO", "coarse_E_K", "coarse_E_Dcol", "coarse_E_Drow", "coarse_E_Dmax",
                                  "direct_metric_identity_residual", "refined_metric_identity_residual", "coarse_metric_identity_residual", "improvement_fractions"],
            "primary_result_order": "parent_primary_R31AK_vs_R31Z_first_then_secondary_R31AK_vs_R31AD",
            "overrides_parent_primary_verdict": False, "weighted_or_composite_score": False,
            "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE"}
    write(base / "SECONDARY_REFINEMENT_DECISION_RULE.json", rule)
    paths = {
        "parent_primary_prereg": parent / "NEXT_VALIDATION_PREREGISTRATION.json",
        "parent_primary_rule": parent / "FROZEN_HOLDOUT_DECISION_RULE.json",
        "parent_selection": parent / "HOLDOUT_SELECTION.json",
        "parent_primary_comparator": repo / "research/r31ak_eight_node/compare_future_holdout.py",
        "metadata_adapter": repo / "research/r31ak_eight_node/metadata_adapter.py",
        "R31AK_engine": repo / "research/r31ad_five_node/unit_cell_model.py",
        "R31AD_policy": repo / "research/r31ad_five_node/MODEL_POLICY.json",
        "R31Z_model": repo / "research/r31z_source_bound/source_bound.py",
        "eight_node_manifest": parent / "EIGHT_NODE_INPUT_MANIFEST.json",
        "R31AK_prediction_npz": parent / "FROZEN_HOLDOUT_PREDICTIONS.npz",
        "R31AD_coarse_npz": base / "Z075_COARSE_PREDICTION.npz",
        "R31AD_coarse_record": base / "Z075_COARSE_PREDICTION.json",
        "secondary_comparator": repo / "research/r31al_z075_gate/compare_secondary_refinement.py",
        "refinement_gain_helper": repo / "research/r31al_z075_gate/refinement_gain.py",
        "secondary_rule": base / "SECONDARY_REFINEMENT_DECISION_RULE.json",
    }
    locked = {key: {"path": str(path.relative_to(repo)), "sha256": sha(path)} for key, path in paths.items()}
    expected = {"parent_primary_prereg": "44b2273afeddb4a6befa73ce485ae84d8f8777a92ac75c4de2fd90d0fea74b81",
                "parent_primary_rule": "08ad89d35c31e133bce39da1f5c8b59eb782b647fb1e4e26da522e010ed6d995",
                "parent_selection": "f01460fe12920280f09281d0763c896986574061806eb0568839b50fcccd096e",
                "parent_primary_comparator": "5443b1ef98b1b70044b8a2e5e8bb065a1d927824066c6a142be3935bfc695394",
                "metadata_adapter": "41a8a67d0b3de90aa22ea4c1f011cbeb0cb48c417dd47b5d958ac26f52f63619",
                "R31AK_engine": "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0",
                "R31Z_model": "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034",
                "eight_node_manifest": "d978792bef0c3bf2b670d4e73d70dcea391645f38555f1070323037610162ece",
                "R31AK_prediction_npz": "6d29acbe1aee9bb34cf3627c04136d67e27b5a44b44ee7b3104cdcd3fe1ff88c"}
    for key, value in expected.items():
        if locked[key]["sha256"] != value:
            raise ValueError("authoritative lock drift: " + key)
    if locked["R31AD_policy"]["sha256"] != sha(paths["R31AD_policy"]):
        raise ValueError("R31AD policy drift")
    coarse = json.loads((base / "Z075_COARSE_PREDICTION.json").read_text())
    prereg = {"schema": "WU088_R31AL_Z075_SECONDARY_REFINEMENT_PREREGISTRATION_V1",
              "selected_z_a0": "0.75", "selected_time_ta": "1.6769079292753586", "radial_order": 192,
              "primary_parent_prereg_sha256": locked["parent_primary_prereg"]["sha256"],
              "primary_rule_sha256": locked["parent_primary_rule"]["sha256"],
              "primary_verdict_unchanged": True,
              "comparison_order": ["parent_primary_R31AK_vs_R31Z", "secondary_R31AK_vs_R31AD"],
              "secondary_models": rule["models"], "secondary_metrics": rule["primary_metrics"],
              "secondary_rule_sha256": locked["secondary_rule"]["sha256"],
              "comparison_tolerance_per_ta": "1e-10", "allowed_secondary_verdicts": rule["verdicts"],
              "mandatory_secondary_outputs": rule["mandatory_outputs"],
              "R31AK_model_aggregate_sha256": "50a5f0eeda63d6e04795e301f6b07a41fd11a4b145e267cfc608261356d49b30",
              "R31AK_selected_arrays_sha256": "66ff922f687a796417e23147e5720af9a467ef7d988b490a2709e0a2967c4010",
              "R31Z_selected_arrays_sha256": "4f7738094bf83c8ad6f01febabdc11f899465957a38a7e65632d63389a68d41c",
              "R31AD_coarse_arrays_sha256": coarse["selected_arrays_sha256"],
              "secondary_comparator_sha256": locked["secondary_comparator"]["sha256"],
              "locked_files": {key: value for key, value in locked.items() if key != "secondary_comparator"},
              "execution_authorized": False, "direct_output_accessed": False,
              "science_node_count": 0, "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE"}
    write(base / "SECONDARY_REFINEMENT_PREREGISTRATION.json", prereg)
    prelock = {"schema": "WU088_R31AL_Z075_REFINEMENT_PRE_OUTPUT_LOCK_V1", "direct_output_accessed": False,
               "execution_authorized": False, "primary_parent_lock_verified": True,
               "refinement_propagation_verified": True, "locked_files": locked,
               "secondary_preregistration_sha256": sha(base / "SECONDARY_REFINEMENT_PREREGISTRATION.json"),
               "R31AK_model_aggregate_sha256": prereg["R31AK_model_aggregate_sha256"],
               "R31AK_prediction_arrays_sha256": prereg["R31AK_selected_arrays_sha256"],
               "R31Z_prediction_arrays_sha256": prereg["R31Z_selected_arrays_sha256"],
               "R31AD_coarse_prediction_arrays_sha256": prereg["R31AD_coarse_arrays_sha256"],
               "primary_rule_sha256": prereg["primary_rule_sha256"],
               "secondary_rule_sha256": prereg["secondary_rule_sha256"]}
    write(base / "Z075_REFINEMENT_PRE_OUTPUT_LOCK.json", prelock)
    scope = {"schema": "WU088_R31AL_Z075_MINIMAL_MIXED_SCOPE_V1", "selected_z_a0": "0.75",
             "selected_time_ta": "1.6769079292753586", "radial_order_B": 192,
             "producer_time_rule": "tau=z/velocity_from_existing_producer",
             "required_outputs_only": ["mixed_O_47x2", "mixed_D_col_47x2", "mixed_D_row_2x47", "independent_mixed_dotO_47x2"],
             "one_shot_geometry": True, "first_scientific_output_identity_consumes_authorization": True,
             "forbidden": ["H", "neutral47", "ionic2", "full49", "trajectory", "other_z", "M3_reference", "post_output_model_rule_adapter_retuning"],
             "parent_primary_prereg_sha256": prereg["primary_parent_prereg_sha256"],
             "secondary_prereg_sha256": prelock["secondary_preregistration_sha256"],
             "R31AK_model_aggregate_sha256": prereg["R31AK_model_aggregate_sha256"],
             "R31Z_model_sha256": locked["R31Z_model"]["sha256"],
             "R31AD_engine_sha256": locked["R31AK_engine"]["sha256"],
             "R31AD_policy_git_blob": "aba52d2c8ffdf97079999cc5f54bd20154bdf4a2",
             "eight_node_manifest_sha256": locked["eight_node_manifest"]["sha256"],
             "metadata_adapter_sha256": locked["metadata_adapter"]["sha256"],
             "primary_comparator_sha256": locked["parent_primary_comparator"]["sha256"],
             "secondary_comparator_sha256": locked["secondary_comparator"]["sha256"],
             "R31AK_prediction_artifact_sha256": locked["R31AK_prediction_npz"]["sha256"],
             "R31AK_selected_prediction_arrays_sha256": prereg["R31AK_selected_arrays_sha256"],
             "R31Z_selected_prediction_arrays_sha256": prereg["R31Z_selected_arrays_sha256"],
             "R31AD_coarse_prediction_artifact_sha256": locked["R31AD_coarse_npz"]["sha256"],
             "R31AD_coarse_prediction_arrays_sha256": prereg["R31AD_coarse_arrays_sha256"],
             "primary_decision_rule_sha256": prereg["primary_rule_sha256"],
             "secondary_decision_rule_sha256": prereg["secondary_rule_sha256"],
             "primary_metrics": ["E_K", "E_Dmax"], "secondary_metrics": ["E_K", "E_Dmax"],
             "comparison_tolerance_per_ta": "1e-10", "future_result_order": prereg["comparison_order"],
             "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE"}
    write(base / "AUTHORIZATION_SCOPE.json", scope)
    spec = importlib.util.spec_from_file_location("r31aj_canonical", repo / "research/r31aj_z25_validation/validation_diagnostics.py")
    canon = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canon)
    blob = canon.canonical_scope_bytes(scope)
    canonical = base / "AUTHORIZATION_SCOPE_CANONICAL.json"
    if canonical.exists():
        raise FileExistsError(canonical)
    canonical.write_bytes(blob)
    scope_hash = hashlib.sha256(blob).hexdigest()
    (base / "AUTHORIZATION_SCOPE.sha256").write_text(scope_hash + "  AUTHORIZATION_SCOPE_CANONICAL.json\n")
    envelope = {"schema": "WU088_R31AL_Z075_MINIMAL_MIXED_AUTHORIZATION_V1", "authorize": True,
                "action": "AUTHORIZE_R31AL_Z075_MINIMAL_MIXED_NODE", "scope_sha256": scope_hash, "one_shot": True}
    write(base / "AUTHORIZATION_ENVELOPE_TEMPLATE.json", envelope)
    prompt = ("R31AL z=0.75 minimal mixed node를 한 번 실행하려면 아래 envelope를 현재 user instruction으로 명시적으로 승인하십시오.\n"
              "이 파일은 예시이며 실행 승인이 아닙니다. 승인 전에는 science command 0개입니다.\n\n```json\n"
              + json.dumps(envelope, indent=2) + "\n```\n\n승인 범위: z=0.75 a0, B192, tau=z/producer velocity; mixed O/D_col/D_row 및 independent mixed dotO만.\n"
              "H, neutral47, ionic2, full49, trajectory, 다른 z, M3/reference, 결과 후 수정은 제외됩니다.\n")
    (base / "USER_AUTHORIZATION_PROMPT_KO.md").write_text(prompt)
    print(json.dumps({"secondary_prereg_sha256": prelock["secondary_preregistration_sha256"],
                      "scope_sha256": scope_hash, "direct_output_accessed": False, "execution_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
