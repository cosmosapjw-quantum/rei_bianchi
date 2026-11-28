"""New affected controls only. Authoring status: NOT_RUN; root owns execution.

Run once under the parent's shared CPU/wall budget. JSON includes every expected
and actual outcome; any failed control makes the process exit nonzero. No timer
or benchmark is implemented here, and no X1/HE38 code is imported.
"""
from collections import defaultdict
from contextlib import redirect_stdout
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import tempfile

from heang_contract import (ContractError, Event, RawMoments, exact, integrate_events,
                            cross_section_weighted, zero_cross_section, transform_raw,
                            serialize_bundle, precheck_provider)
from heang_contract.exact_events import numbers
from heang_contract.cli import (main as cli_main, strict_json_loads,
                                validate_fixture_payload, validate_fixture_bindings)

HERE = Path(__file__).resolve().parent


def witness(kind):
    events = []
    for s in (1, -1):
        for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if kind == "A":
                q1, q2, qp = (s*x, s*y, s), (-s*x, -s*y, s), (0, 0, -2*s)
            else:
                q1, q2, qp = (x, y, s), (x, y, -s), (-2*x, -2*y, 0)
            events.append(Event("1/8", q1, q2, qp))
    return events


def result(kind="A"):
    return integrate_events(witness(kind), 1, 3, "14/3", 2)


def physical_summary(kind):
    bundle = result(kind)
    return {"Ne": str(bundle.electron.N), "Np": str(bundle.proton.N),
            "Pe": numbers(bundle.electron.P), "Pp": numbers(bundle.proton.P),
            "Re": numbers(bundle.electron.R), "Rp": numbers(bundle.proton.R),
            "C12": numbers(bundle.C12), "Ke": str(bundle.electron.K), "Kp": str(bundle.proton.K),
            "De": str((3*bundle.electron.R[2][2]/2-bundle.electron.K)/2),
            "Jp": numbers(bundle.proton.J)}


def inclusive_comparison():
    histograms = []
    for kind in ("A", "B"):
        histogram = defaultdict(F)
        for event in witness(kind):
            histogram[event.q1] += event.weight
            histogram[event.q2] += event.weight
        histograms.append(dict(histogram))
    return {"equal": histograms[0] == histograms[1], "support_points": len(histograms[0]),
            "inclusive_count": str(sum(histograms[0].values(), F(0))),
            "each_point_count": sorted(set(str(value) for value in histograms[0].values()))}


def weighted_summary():
    bundle = cross_section_weighted(result(), "3/2")
    return {"Z": str(bundle.measure_mass), "Ne": str(bundle.electron.N),
            "Ke": str(bundle.electron.K), "Kp": str(bundle.proton.K),
            "ledger": serialize_bundle(bundle)["ledger"],
            "normalization": bundle.normalization}


def nonzero_cross_trace():
    event = Event(1, (1, 0, 0), (1, 0, 0), (-2, 0, 0))
    bundle = cross_section_weighted(integrate_events([event], 1, 2, 3, 1), 3)
    return {"C12": numbers(bundle.C12), "ledger": serialize_bundle(bundle)["ledger"],
            "Z": str(bundle.measure_mass), "Ne": str(bundle.electron.N)}


def boost_rotation():
    raw = transform_raw(result().electron, (1, 2, 0), ((0, -1, 0), (1, 0, 0), (0, 0, 1)))
    return {"N": str(raw.N), "P": numbers(raw.P), "R": numbers(raw.R), "K": str(raw.K)}


def signed_number():
    loss = RawMoments(2, -1, (-2, 0, 0), ((-2, 0, 0), (0, 0, 0), (0, 0, 0)),
                      "conditional_event", "signed_source")
    raw = transform_raw(loss, (1, 0, 0))
    return {"N": str(raw.N), "P": numbers(raw.P), "R": numbers(raw.R), "K": str(raw.K)}


def zero_sigma():
    bundle = zero_cross_section(1, 3, 1, 2)
    return {"Z": str(bundle.measure_mass), "Ne": str(bundle.electron.N),
            "Np": str(bundle.proton.N), "Re": numbers(bundle.electron.R),
            "normalization": bundle.normalization, "Kp": str(bundle.proton.K)}


def fixture_zero_sigma():
    payload = strict_json_loads((HERE / "example/law_payload.json").read_bytes())
    payload.update({"sigma": 0, "E": 1, "events": [], "normalization": "cross_section_weighted"})
    output = validate_fixture_payload(payload)
    return {"conditional_constructed": output["conditional_probability_constructed"],
            "conditional": output["conditional"],
            "Z": output["cross_section_weighted"]["measure_mass_Z"]}


def precheck_variant(change=None, payload_change=None, supply_bytes=True):
    metadata = strict_json_loads((HERE / "example/candidate.json").read_bytes())
    payload = (HERE / "example/law_payload.json").read_bytes()
    if change:
        change(metadata)
    if payload_change:
        payload = payload_change(payload)
    output = precheck_provider(metadata, {"law_payload.json": payload} if supply_bytes else None)
    return {"status": output["status"], "empirical_admission": output["empirical_admission"],
            "runtime_activation": output["runtime_activation"]}


def admission_status(status):
    return {"status": status, "empirical_admission": False, "runtime_activation": False}


def fixture_binding_variant(change):
    metadata = strict_json_loads((HERE / "example/candidate.json").read_bytes())
    payload = strict_json_loads((HERE / "example/law_payload.json").read_bytes())
    change(metadata)
    return validate_fixture_bindings(metadata, payload)


def cli_result(corrupt_identity=False):
    if not corrupt_identity:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = cli_main([str(HERE / "example/candidate.json")])
        data = strict_json_loads(stream.getvalue())
    else:
        metadata = strict_json_loads((HERE / "example/candidate.json").read_bytes())
        payload = strict_json_loads((HERE / "example/law_payload.json").read_bytes())
        payload["event_law_id"] = "different-law-in-actual-bytes"
        raw = json.dumps(payload, sort_keys=True).encode()
        for binding in metadata["bindings"].values():
            binding["sha256"] = hashlib.sha256(raw).hexdigest()
        metadata["x1"]["candidate_moments_sha256"] = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory(prefix="heang-control-") as directory:
            root = Path(directory)
            (root / "candidate.json").write_text(json.dumps(metadata), encoding="utf-8")
            (root / "law_payload.json").write_bytes(raw)
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = cli_main([str(root / "candidate.json")])
            data = strict_json_loads(stream.getvalue())
    output = {"exit_code": code, "empirical_admission": data["empirical_admission"],
              "runtime_activation": data["runtime_activation"]}
    if corrupt_identity:
        output["error_identifies_payload_identity"] = "payload content identity" in data.get("error", "")
    return output


def run_controls():
    outcomes = []
    def case(name, expected, action):
        try:
            actual = action()
            passed = actual == expected
        except Exception as exc:
            actual = {"exception": type(exc).__name__, "message": str(exc)}
            passed = False
        outcomes.append({"name": name, "expected": expected, "actual": actual, "pass": passed})
    def refused(name, action, phrase):
        try:
            action()
            actual = {"refused": False}
            passed = False
        except Exception as exc:
            actual = {"exception": type(exc).__name__, "message": str(exc)}
            passed = isinstance(exc, ContractError) and phrase in str(exc)
        outcomes.append({"name": name, "expected": {"exception": "ContractError", "message_contains": phrase},
                         "actual": actual, "pass": passed})

    common = {"Ne": "2", "Np": "1", "Pe": ["0", "0", "0"], "Pp": ["0", "0", "0"],
              "Re": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "2"]], "Ke": "2", "Kp": "2/3", "De": "1/2"}
    case("A_exact_event_moments", dict(common,
         Rp=[["0", "0", "0"], ["0", "0", "0"], ["0", "0", "4/3"]],
         C12=[["-1", "0", "0"], ["0", "-1", "0"], ["0", "0", "2"]],
         Jp=[["-4/9", "0", "0"], ["0", "-4/9", "0"], ["0", "0", "8/9"]]), lambda: physical_summary("A"))
    case("B_exact_event_moments", dict(common,
         Rp=[["2/3", "0", "0"], ["0", "2/3", "0"], ["0", "0", "0"]],
         C12=[["1", "0", "0"], ["0", "1", "0"], ["0", "0", "-2"]],
         Jp=[["2/9", "0", "0"], ["0", "2/9", "0"], ["0", "0", "-4/9"]]), lambda: physical_summary("B"))
    case("complete_discrete_inclusive_marginals_equal", {"equal": True, "support_points": 8,
         "inclusive_count": "2", "each_point_count": ["1/4"]}, inclusive_comparison)
    case("cross_section_event_mass_Z", {"Z": "3/2", "Ne": "3", "Ke": "3", "Kp": "1",
         "ledger": {"Kp_expected": "1", "Kp_actual": "1", "trace_C12_expected": "0",
                    "trace_C12_actual": "0", "ion_R_identity_exact": True},
         "normalization": "cross_section_weighted"}, weighted_summary)
    case("cross_section_nonzero_C12_trace", {"C12": [["6", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]],
         "ledger": {"Kp_expected": "3", "Kp_actual": "3", "trace_C12_expected": "6",
                    "trace_C12_actual": "6", "ion_R_identity_exact": True}, "Z": "3", "Ne": "6"}, nonzero_cross_trace)
    case("general_boost_then_rotation", {"N": "2", "P": ["4", "-2", "0"],
         "R": [["9", "-4", "0"], ["-4", "3", "0"], ["0", "0", "2"]], "K": "7"}, boost_rotation)
    case("signed_reactive_N_term", {"N": "-1", "P": ["0", "0", "0"],
         "R": [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]], "K": "0"}, signed_number)
    case("zero_sigma_without_conditional_probability", {"Z": "0", "Ne": "0", "Np": "0",
         "Re": [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]],
         "normalization": "cross_section_weighted", "Kp": "0"}, zero_sigma)
    case("zero_sigma_fixture_branch", {"conditional_constructed": False, "conditional": None, "Z": "0"}, fixture_zero_sigma)

    refused("refuse_binary_float", lambda: exact(0.5), "binary float")
    refused("refuse_nonfinite_float", lambda: exact(float("inf")), "binary float")
    refused("refuse_boolean_number", lambda: exact(True), "bool refused")
    refused("refuse_zero_denominator", lambda: exact("1/0"), "rational string")
    refused("refuse_non3D_momentum", lambda: Event(1, (0, 0), (0, 0, 0), (0, 0, 0)), "three components")
    refused("refuse_negative_weight", lambda: Event(-1, (0, 0, 0), (0, 0, 0), (0, 0, 0)), "nonnegative event weight")
    refused("refuse_non_normalized_weights", lambda: integrate_events(witness("A")[:1], 1, 3, "14/3", 2), "sum exactly")
    refused("refuse_momentum_support", lambda: integrate_events([Event(1, (1, 0, 0), (1, 0, 0), (0, 0, 0))], 1, 3, 3, 2), "momentum support")
    refused("refuse_energy_support", lambda: integrate_events(witness("A"), 1, 3, 5, 2), "energy support")
    refused("refuse_subthreshold_conditional", lambda: integrate_events(witness("A"), 1, 3, 1, 2), "E<I")
    refused("refuse_nonpositive_mass", lambda: integrate_events(witness("A"), 0, 3, "14/3", 2), "must be positive")
    refused("refuse_nonorthogonal_frame", lambda: transform_raw(result().electron, (0, 0, 0), ((2, 0, 0), (0, 1, 0), (0, 0, 1))), "orthogonal")
    refused("refuse_negative_sigma", lambda: cross_section_weighted(result(), -1), "nonnegative cross section")
    refused("refuse_double_sigma_weighting", lambda: cross_section_weighted(cross_section_weighted(result(), 2), 2), "double sigma")
    refused("refuse_nonsymmetric_raw_tensor", lambda: RawMoments(1, 1, (0, 0, 0), ((1, 1, 0), (0, 1, 0), (0, 0, 1)), "conditional_event"), "symmetry")
    refused("refuse_duplicate_JSON_keys", lambda: strict_json_loads('{"x":1,"x":2}'), "duplicate JSON key")
    refused("refuse_payload_metadata_mass_mismatch", lambda: fixture_binding_variant(lambda m: m["kinematics"].update(m_kg=2)), "payload kinematics differs")
    refused("refuse_payload_metadata_threshold_mismatch", lambda: fixture_binding_variant(lambda m: m["kinematics"].update(I_J=1)), "payload kinematics differs")
    refused("refuse_payload_outside_energy_domain", lambda: fixture_binding_variant(lambda m: m["kinematics"].update(incident_COM_energy_J=[5, 6])), "outside declared COM")
    refused("refuse_COM_payload_relabelled_LAB", lambda: fixture_binding_variant(lambda m: m["frame"].update(name="LAB", map_reference="unreviewed")), "COM momenta")
    refused("refuse_nonobject_payload", lambda: validate_fixture_bindings({}, []), "JSON object")

    case("manufactured_structural_ready_never_admitted", admission_status("STRUCTURALLY_READY_REQUIRES_SOURCE_REVIEW"), precheck_variant)
    case("actual_payload_digest_corruption", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(payload_change=lambda data: data + b" "))
    case("same_law_binding_mismatch", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["bindings"]["correlation"].update(event_law_id="unmatched-law")))
    case("angular_source_binding_mismatch", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["bindings"]["electron"].update(angle_source_id="unmatched-angles")))
    case("preparation_binding_mismatch", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["preparation"].update(id="different-preparation")))
    case("actual_payload_unavailable", admission_status("DEFERRED_DEPENDENCY"), lambda: precheck_variant(supply_bytes=False))
    case("partial_domain_remains_partial", admission_status("PARTIAL_SCOPED"),
         lambda: precheck_variant(lambda m: m["domain"].update(coverage="partial", missing_domain_reference="explicit omitted region")))
    case("missing_joint_correlation_remains_partial", admission_status("PARTIAL_SCOPED"),
         lambda: precheck_variant(lambda m: m["bindings"].pop("correlation")))
    case("fivefold_roots_and_Jacobian_missing", admission_status("DEFERRED_DEPENDENCY"),
         lambda: precheck_variant(lambda m: m["support"].update(coordinates="fivefold_joint_shell_density")))
    case("physical_uncertainty_unknown", admission_status("DEFERRED_DEPENDENCY"),
         lambda: precheck_variant(lambda m: m["uncertainty"]["physical"].update(status="unknown")))
    case("calibration_declaration_never_activates", admission_status("STRUCTURALLY_READY_REQUIRES_SOURCE_REVIEW"),
         lambda: precheck_variant(lambda m: m["uncertainty"]["physical"].update(status="calibrated", reference="unreviewed declaration")))
    case("X1_INDETERMINATE_is_preserved", admission_status("DEFERRED_DEPENDENCY"),
         lambda: precheck_variant(lambda m: m["x1"].update(decision="INDETERMINATE")))
    case("X1_FAIL_is_preserved", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["x1"].update(decision="FAIL")))
    case("old_X1_PASS_without_candidate_binding_deferred", admission_status("DEFERRED_DEPENDENCY"),
         lambda: precheck_variant(lambda m: m["x1"].pop("candidate_moments_sha256")))
    case("X1_stale_candidate_binding_refused", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["x1"].update(candidate_moments_sha256="0"*64)))
    case("declared_mass_domain_refused", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["kinematics"].update(m_kg=0)))
    case("declared_energy_interval_refused", admission_status("REJECTED_INCONSISTENT"),
         lambda: precheck_variant(lambda m: m["kinematics"].update(incident_COM_energy_J=[5, 4])))
    case("all_missing_metadata_never_passes", "DEFERRED_DEPENDENCY", lambda: precheck_provider({})["status"])
    case("malformed_metadata_refused", "REJECTED_INCONSISTENT", lambda: precheck_provider(True)["status"])
    case("CLI_fixture_success_has_no_admission", {"exit_code": 0, "empirical_admission": False, "runtime_activation": False}, cli_result)
    case("CLI_rebound_digest_does_not_hide_wrong_identity", {"exit_code": 2, "empirical_admission": False,
         "runtime_activation": False, "error_identifies_payload_identity": True}, lambda: cli_result(True))
    failed = [item["name"] for item in outcomes if not item["pass"]]
    return {"schema": "heang.affected_controls.raw.v1", "source_scope": "manufactured exact event contracts only",
            "cases": outcomes, "case_count": len(outcomes), "failure_count": len(failed), "failed_cases": failed,
            "empirical_admission": False, "runtime_activation": False,
            "old_X1_or_HE38_execution": 0, "provider_scan": 0, "IVP": 0}


if __name__ == "__main__":
    output = run_controls()
    print(json.dumps(output, sort_keys=True, indent=2, allow_nan=False))
    raise SystemExit(1 if output["failure_count"] else 0)
