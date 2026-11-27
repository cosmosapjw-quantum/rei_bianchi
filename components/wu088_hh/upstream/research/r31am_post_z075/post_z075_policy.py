from __future__ import annotations
import math

PRIMARY={"PARETO_SUPPORTED_AT_Z075","GLOBAL_SUPPORTED_AT_Z075","TRADEOFF_UNRESOLVED"}
SECONDARY={"REFINED_PARETO_SUPPORTED_AT_Z075","COARSE_PARETO_SUPPORTED_AT_Z075","REFINEMENT_TRADEOFF_UNRESOLVED"}

def post_z075_action(primary,secondary):
    if primary not in PRIMARY: raise ValueError("unknown primary verdict")
    if secondary not in SECONDARY: raise ValueError("unknown secondary verdict")
    common={"shared_direct_geometry":True,"primary_secondary_independent_evidence_count":1,
            "auto_consume_z075_as_training":False,"auto_add_knot":False,"auto_execute_next_node":False,
            "interval_wide_accuracy_admitted":False,"source_accuracy_admitted":False,"production_admitted":False}
    if primary=="PARETO_SUPPORTED_AT_Z075":
        if secondary=="REFINED_PARETO_SUPPORTED_AT_Z075":
            action="FREEZE_R31AK_LOCALLY_SUPPORTED__PIVOT_TO_REFERENCE_CERTIFICATION"
            rationale="R31AK beats R31Z and the local h-refinement beats its coarse predecessor at the same fresh point."
        elif secondary=="COARSE_PARETO_SUPPORTED_AT_Z075":
            action="STOP_H_REFINEMENT__REVIEW_LOCAL_KNOT_POLICY"
            rationale="R31AK beats R31Z but the inserted z0.5 knot worsens the local coarse predecessor comparison."
        else:
            action="FREEZE_R31AK_RELATIVE_SUPPORT__REFINEMENT_GAIN_UNRESOLVED__PIVOT_REFERENCE_REVIEW"
            rationale="R31AK beats R31Z but the local refinement gain is unresolved."
    elif primary=="GLOBAL_SUPPORTED_AT_Z075":
        action="STOP_FOR_MODEL_CLASS_REVIEW"
        rationale="R31Z is relatively supported at the fresh point; no automatic local refinement escalation is allowed."
    else:
        if secondary=="REFINED_PARETO_SUPPORTED_AT_Z075":
            action="STOP_EXTERNAL_COMPARATOR_UNRESOLVED__LOCAL_GAIN_ONLY"
            rationale="Local h-refinement gain is supported, but R31AK-vs-R31Z is unresolved."
        else:
            action="STOP_FOR_MODEL_CLASS_REVIEW"
            rationale="The external comparison is unresolved and there is no decisive refinement-gain basis for further automatic adaptation."
    return {**common,"action":action,"rationale":rationale}

def reference_margin_interval(observed_margin,epsilon):
    d=float(observed_margin);e=float(epsilon)
    if not (math.isfinite(d) and math.isfinite(e) and e>=0):
        raise ValueError("finite margin and nonnegative finite epsilon required")
    return [d-2*e,d+2*e]

def policy_table():
    return [{"primary":p,"secondary":s,**post_z075_action(p,s)}
            for p in sorted(PRIMARY) for s in sorted(SECONDARY)]
