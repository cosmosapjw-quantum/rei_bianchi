import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"post_z075_policy.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_all_nine_cells_defined_and_stop_automatic_reuse():
    rows=m.policy_table()
    assert len(rows)==9
    assert all(r["auto_consume_z075_as_training"] is False for r in rows)
    assert all(r["auto_add_knot"] is False for r in rows)
    assert all(r["auto_execute_next_node"] is False for r in rows)
    assert all(r["primary_secondary_independent_evidence_count"]==1 for r in rows)

def test_strong_double_support_pivots():
    r=m.post_z075_action("PARETO_SUPPORTED_AT_Z075","REFINED_PARETO_SUPPORTED_AT_Z075")
    assert r["action"]=="FREEZE_R31AK_LOCALLY_SUPPORTED__PIVOT_TO_REFERENCE_CERTIFICATION"

def test_adaptive_support_but_coarse_wins_stops_refinement():
    r=m.post_z075_action("PARETO_SUPPORTED_AT_Z075","COARSE_PARETO_SUPPORTED_AT_Z075")
    assert r["action"]=="STOP_H_REFINEMENT__REVIEW_LOCAL_KNOT_POLICY"

def test_global_support_always_model_review():
    for s in m.SECONDARY:
        assert m.post_z075_action("GLOBAL_SUPPORTED_AT_Z075",s)["action"]=="STOP_FOR_MODEL_CLASS_REVIEW"

def test_primary_tradeoff_secondary_refined_is_local_gain_only():
    r=m.post_z075_action("TRADEOFF_UNRESOLVED","REFINED_PARETO_SUPPORTED_AT_Z075")
    assert r["action"]=="STOP_EXTERNAL_COMPARATOR_UNRESOLVED__LOCAL_GAIN_ONLY"

def test_reference_margin_interval_factor_two():
    assert m.reference_margin_interval(.2,.03)==pytest.approx([.14,.26])

def test_invalid():
    with pytest.raises(ValueError):m.post_z075_action("BAD","REFINED_PARETO_SUPPORTED_AT_Z075")
    with pytest.raises(ValueError):m.reference_margin_interval(.1,-.1)
