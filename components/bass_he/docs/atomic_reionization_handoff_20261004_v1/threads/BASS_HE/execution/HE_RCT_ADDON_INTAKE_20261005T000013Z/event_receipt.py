"""Audit saved exploratory event-control records; no stepper or rate execution."""
import math


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    require(type(actual) is type(expected) and actual == expected, message)


def finite(value):
    require(type(value) in (int, float) and math.isfinite(value), "nonfinite or malformed number")
    return value


def audit(contract, receipt, rows, oracle):
    """Arithmetic/claim-boundary intake of the frozen 12-case evidence."""
    for key, value in {"gate": "SCOPED_ADDON_NATIVE_PASS__OWNER_ADOPTION_PENDING",
                       "dependency_commit": "41e4592aa494b48929dcd23fc8504c169a98a908"}.items():
        exact(contract[key], value, key)
    control = contract["event_error"]
    for key, value in {"example_absolute_per_h": 1e-14, "example_relative": 0.0002,
                       "required_caller_input": True, "strict_owner_adoption": False,
                       "exact_flow_certificate": False}.items():
        exact(control[key], value, key)
    exact(contract["inherited_limits"]["local_error_strict_less_than"], 0.0002, "state gate")
    exact(contract["inherited_limits"]["residual_default"], 1e-14, "residual gate")
    for key, value in {"addon_native_implemented": True, "actual_original_stepper_modified": False,
                       "full_current_consumer_crate_built": False, "HE_F2_global_completed": False,
                       "physical_admission": False, "consumer_remote_mutations": 0,
                       "native_tests_passed": 15, "adaptive_accepted_cases": 6,
                       "adaptive_rejected_cases": 6, "baseline_RCT": "OFF"}.items():
        exact(receipt[key], value, key)
    require(len(rows) == 13 and rows[0]["kind"] == "model", "record count/model")
    nh = finite(rows[0]["nh"])
    require(nh > 0, "proper hydrogen density")
    exact(oracle["status"], "FINITE_INDEPENDENT_EQUATION_CHECK_PASS", "oracle status")
    exact(oracle["endpoint_sites"], 36, "endpoint count")
    require(len(oracle["results"]) == 12, "oracle record count")
    accepted = rejected = 0
    output = []
    for index, (row, report) in enumerate(zip(rows[1:], oracle["results"])):
        exact(row["kind"], "step", "step record")
        dt = finite(row["dt"])
        require(dt == (1e8, 1e9, 1e10, 1e11)[index // 3], "missing/duplicate case")
        require(row["mean_ev"] == rows[0]["chi"][2] - rows[0]["chi"][0] + (index % 3 - 1), "explicit Ebar")
        full, half = finite(row["J_full"]), finite(row["J_half"])
        require(full >= 0 and half >= 0, "negative proper events")
        # Preserve both frozen arithmetic orders. The probe reports subtract-
        # then-divide; the API's actual decision normalizes first.
        logged_error = abs(full-half) / nh
        logged_allowed = 1e-14 + 2e-4 * max(full, half) / nh
        fc, hc = full / nh, half / nh
        api_error = abs(fc-hc)
        api_allowed = 1e-14 + 2e-4 * max(abs(fc), abs(hc))
        exact(finite(row["event_defect_per_h"]), logged_error, "probe arithmetic")
        exact(finite(row["event_allowed_per_h"]), logged_allowed, "probe budget")
        local = finite(row["local_error"])
        require(0 <= local < 2e-4, "state gate")
        status = "ACCEPT" if api_error <= api_allowed else "RCT_EVENT_LOCAL_ERROR"
        exact(row["status"], status, "API event gate status")
        exact(report["adaptive_status"], status, "oracle reported status")
        require(report["case"] == index and report["dt_s"] == dt and report["mean_ev"] == row["mean_ev"], "oracle case identity")
        accepted += status == "ACCEPT"
        rejected += status != "ACCEPT"
        output.append({"case": index, "dt_s": dt, "mean_ev": row["mean_ev"],
                       "status": status, "state_error_reported": local,
                       "api_event_error_per_h": api_error, "api_allowed_per_h": api_allowed,
                       "logged_event_error_per_h": logged_error,
                       "arithmetic_order_difference": api_error-logged_error,
                       "event_budget_ratio": api_error/api_allowed})
    require(accepted == rejected == 6, "acceptance count")
    return {"status": "PASS_SAVED_EVENT_GATE_ARITHMETIC", "cases": output,
            "accepted": accepted, "rejected": rejected,
            "production_budget_adopted": False, "owner_dispatcher_admitted": False,
            "exact_flow_certificate": False, "physical_admission": False}


def audit_static_scope(summary, receipt):
    """Receive the late static report without certifying a flow-error bound."""
    exact(summary["sum_estimator_is_certified_bound"], False, "estimator is not a flow bound")
    exact(summary["numeric_error_not_physical_uncertainty"], True, "numerical/physical distinction")
    exact(receipt["physical_admission"], False, "static physical admission")
    exact(receipt["interval_certificate"], False, "static interval certificate")
    exact(receipt["HE_F2_global"], False, "static HE-F2 completion")
    exact(receipt["full_live_crate_built"], False, "static current build")
    exact(receipt["native_histories"], 12, "static history count")
    exact(summary["direct_RCT_electron_term"], 0, "direct electron stoichiometry")
    delta = finite(float(summary["ON_OFF_electron_delta_per_H"]))
    require(delta != 0, "direct-zero must not erase the reported feedback")
    steps = [row["steps"] for row in summary["native"]]
    exact(steps, [100, 200, 400], "static refinements")
    exact(4*sum(steps), receipt["accepted_macro_steps_per_campaign"], "step accounting")
    return {"status": "RECEIVED_STATIC_AUTHOR_REPORT_SCOPE_ONLY", "native_histories_reported": 12,
            "macro_steps_per_campaign_reported": 2800, "electron_feedback_reported": delta,
            "raw_trajectory_or_reference_recomputed_here": False,
            "sum_estimator_certified_flow_bound": False, "physical_admission": False}
