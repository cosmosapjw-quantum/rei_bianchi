import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("gate",HERE/"authorization_gate.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

scope={
 "schema":"WU088_R31AF_Z35_MINIMAL_MIXED_SCOPE_V1",
 "selected_z_a0":3.5,
 "selected_time_ta":7.825570336618339,
 "radial_order":192,
 "required_outputs_only":["mixed_O_47x2","mixed_D_col_47x2","mixed_D_row_2x47","independent_mixed_dotO_47x2"],
 "forbidden":["H","neutral47","ionic2","full49","trajectory","other_z","M3_reference","post_result_model_retuning"],
 "R31AF_engine_sha256":"ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0",
 "R31AF_policy_sha256":"720b221a9e01ab7fc1bbd482b600ea785fed0b8c6b80b5834c576a75c2b70756",
 "R31Z_model_sha256":"4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034",
 "six_node_manifest_sha256":"e444e9f1cff7d4cc9425a2f44ff45a6e87199c6bf31ca2b095010364379e7573",
 "selection_sha256":"546026387ecae9952b0397fb0dd26ad0633465739d8bbb82878f0f4c532c545e",
 "decision_rule_sha256":"52b995b2f5516cf586cf1cbcdb681ec521f1b911a7538e3999a11d0f3bd62560",
 "preregistration_sha256":"ec4613f5300ec38a488eae75f5c7267a2f1a166c34e45d54bb9fa8b449537447",
 "comparison_tolerance":1e-10,
 "one_shot":True,
 "post_result":"compare_once_and_stop"
}

def valid():
    return {
      "schema":m.SCHEMA,
      "authorize":True,
      "action":m.ACTION,
      "scope_sha256":m.EXPECTED_SCOPE_SHA256,
      "one_shot":True
    }

def test_scope_hash():
    assert m.canonical_sha256(scope)==m.EXPECTED_SCOPE_SHA256

def test_valid_envelope():
    assert m.validate_envelope(valid())==(True,"AUTHORIZED_ONE_SHOT")

def test_token_mention_is_not_envelope():
    assert m.validate_envelope("AUTHORIZE_R31AF_Z35_MINIMAL_MIXED_NODE")[0] is False

def test_scope_drift_and_negation_rejected():
    x=valid();x["scope_sha256"]="0"*64
    assert m.validate_envelope(x)[1]=="AUTHORIZATION_SCOPE_DRIFT"
    x=valid();x["authorize"]=False
    assert m.validate_envelope(x)[1]=="AUTHORIZATION_NOT_AFFIRMATIVE"

def test_information_value():
    x=m.information_value()
    assert abs(x["S_design_only_per_ta"]-0.2836776637729875)<1e-15
    assert abs(x["K_half_gap_per_ta"]-0.09561189201673982)<1e-15
    assert abs(x["Dmax_half_gap_per_ta"]-0.10476936735470115)<1e-15
    assert x["winner_prediction"] is False
