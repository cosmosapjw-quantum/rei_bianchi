"""Read the saved PR81 return only; never import a solver or archived code.

This is a bounded consumer report, not a replacement for the producer's original
admission routines or a rigorous ODE error estimator. Output is create-only.
Run with Python -I -S so an archived sitecustomize cannot be imported.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path

CODE = "802a32361288bf5aa0e0d1f63c912768f1a1d407"
CORE = "a5d4711460c09b310b78c9692aa62534b7a843d3"
OWNER = "f7830e2f55e7a1938bc3c98f61b60651f8dae474"
VIGIL = "a21d573980f66fe02891bd216153443b5352f921"
BINARY = "a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9"
TABLE = "919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd"
BRIDGE = "28d637a9011ad0e23c087659cd07574cfb0ddc55511380c4c807165aee3123eb"
NATIVE_GZIP = "2e917706b6a17c928ed6df1eb2271897d68f8de6070d839313c4a98a01c9acc8"
LEDGERS = sorted("a_hei a_heii a_hi birth_e birth_n ci_hei ci_heii ci_hi cmb dr escape heat_hei heat_heii heat_hi rr_hei rr_heii rr_hi work_g work_p".split())


def reject_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def read(path):
    return json.loads(path.read_text(), parse_constant=reject_constant)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def difference(a, b):
    exact = Fraction.from_float(a) - Fraction.from_float(b)
    return {"exact_binary64_input_difference": str(exact), "display": float(exact)}


def inspect(args):
    root, returned = Path(args.he29_root), Path(args.return_root)
    canonical, outer = returned / "canonical", returned / "outer"
    case = canonical / "case"
    public = root / "results/hpc64_canary_20261021"
    baseline = root / "native_intake_20261020T1315Z/evidence/returned/execution/references"
    result, identity = read(case / "RESULT.json"), read(case / "IDENTITY.json")
    summary, native = read(public / "CANARY_SUMMARY.json"), read(case / "NATIVE_EVIDENCE.json")
    table, build = read(case / "TABLE.json"), read(canonical / "build/BUILD_IDENTITY.json")
    endpoint, metadata = result["result"], result["result"]["metadata"]
    failures, checks = [], []

    def check(name, value):
        checks.append({"name": name, "pass": bool(value)})
        if not value:
            failures.append(name)

    check("case", result["case"] == {"angles": 4, "m": 8, "q": 0.0, "r": 4, "table_nodes": 512})
    check("completed", result["status"] == "CANARY_COMPLETED_SCOPED")
    check("execution_pins", identity["adapter_publication"]["head"] == CODE and identity["packed_publication"]["head"] == CORE and identity["owner_source"] == OWNER and build["vigilode_source"] == VIGIL)
    check("original_tolerances_threads", metadata["rtol"] == 1e-10 and metadata["atol_scaled"] == 1e-12 and metadata["threads"] == identity["packed_threads"] == result["packed_threads"] == 1)
    check("all_19_ledgers", sorted(endpoint["ledger"]) == LEDGERS)
    check("reference_reuse_only", result["baseline_pairs_reused"] == 4 and result["new_baseline_pairs"] == result["transport_replays"] == result["source_only_suites_replayed"] == 0)
    for name in ("RESULT.json", "NATIVE_EVIDENCE.json"):
        check("public_canonical_bytes_" + name, (public / name).read_bytes() == (case / name).read_bytes())
    public_table = read(public / "TABLE.json")
    sanitized_table = json.loads(json.dumps(table))
    pids = sanitized_table["execution"].pop("worker_pids_observed")
    sanitized_table["execution"]["worker_pids_observed_count"] = len(set(pids))
    check("public_table_sanitized_pid_only", public_table == sanitized_table)
    check("bridge_identity_bytes", sha(canonical / "bridge_artifact/libhe29_optimized_bridge.so") == build["library_sha256"] == BRIDGE)
    check("native_owner_recorded_identity", identity["binary_sha256"] == native["binary_sha256"] == BINARY)
    check("table_recorded_identity", result["table_sha256"] == table["source_table_sha256"] == TABLE)

    # Compare the newly returned source and baseline reuse identities, not their
    # old scientific tests. The original 22 DATA bytes are not in this archive.
    for relative, digest in identity["new_adapter_sources"].items():
        check("adapter_source_" + relative, sha(root / "hpc64_20261021" / relative) == digest)
    for case_name, entries in identity["reused"]["all_pair_receipts"].items():
        for name, digest in entries.items():
            check("reused_receipt_" + case_name + "/" + name, sha(baseline / case_name / name) == digest)
    old_identity = read(baseline / "m8_r4_table512/IDENTITY.json")
    for key in ("runtime", "numerical_thread_environment", "input_sources", "parent_sources", "source_files"):
        check("cohort_" + key, identity[key] == old_identity[key])

    comparisons, gate_values = {}, []
    for method in ("Radau", "DOP853"):
        saved = read(baseline / ("m8_r4_table512/" + method + ".json"))["result"]
        frac = max(abs(endpoint["gas_final"][i] - saved["gas_final"][i]) for i in range(3))
        dt = abs(endpoint["temperature_K"] - saved["temperature_K"])
        comparison = result["comparison_to_saved_baseline"][method]
        check("saved_comparison_" + method, comparison["absolute_fraction_difference"] == frac and comparison["method_temperature_difference_K"] == dt and comparison["reference_stable"] and not comparison["error_radius_certified"])
        gate_values.append((frac, dt))
        comparisons[method] = {
            "reference_temperature_K": saved["temperature_K"],
            "temperature_K": difference(endpoint["temperature_K"], saved["temperature_K"]),
            "gas_final": [difference(a, b) for a, b in zip(endpoint["gas_final"], saved["gas_final"])],
            "ledgers_original_units": {k: difference(endpoint["ledger"][k], saved["ledger"][k]) for k in LEDGERS},
            "photon_number": difference(endpoint["photon_number"], saved["photon_number"]),
            "photon_energy_eV_per_H": difference(endpoint["photon_energy_ev"], saved["photon_energy_ev"]),
            "fraction_abs_max": frac, "temperature_abs_difference_K": dt,
        }
    gates = {
        "absolute_fraction": (max(v[0] for v in gate_values), 1e-11),
        "temperature_difference_K": (max(v[1] for v in gate_values), 1e-9),
        "number_defect_per_H": (abs(endpoint["number_defect"]), 3e-15),
        "energy_defect_eV_per_H": (abs(endpoint["energy_defect_ev"]), 3e-12),
        "species_defect": (max(abs(v) for v in endpoint["species_defect"]), 3e-12),
    }
    for name, (value, limit) in gates.items():
        check("gate_" + name, math.isfinite(value) and value <= limit)
    check("original_positivity", endpoint["gas_positive"] and endpoint["min_photon"] >= 0 and endpoint["temperature_K"] > 0)

    # Full gzip consumer readback, with no native calls. Verify every record's
    # source identity and finite wire values; do not regenerate any response.
    gzip_path = case / "native.jsonl.gz"
    check("gzip_raw_sha", sha(gzip_path) == native["gzip_sha256"] == NATIVE_GZIP)
    counts, shapes = Counter(), Counter()
    previous_ns, bad_records, first_handshake = -1, [], None
    with gzip.open(gzip_path, "rt", encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            row = json.loads(line, parse_constant=reject_constant)
            counts[row["kind"]] += 1
            good = row["binary_sha256"] == BINARY and row["source_commit"] == OWNER and row["monotonic_ns"] >= previous_ns
            previous_ns = row["monotonic_ns"]
            if row["kind"] == "handshake":
                first_handshake = row["response"]
                good = good and index == 0 and row["response"].startswith("HE25_OWNER_V1\t" + OWNER + "\t")
            elif row["kind"] == "point":
                request, response = row["request"].split("\t"), row["response"].split("\t")
                shapes[(len(request), len(response))] += 1
                good = good and response[0] == "POINT" and all(math.isfinite(float(v)) for v in request + response[1:])
            else:
                good = False
            if not good:
                bad_records.append(index)
    check("gzip_all_record_content", not bad_records)
    check("gzip_counts", counts == {"handshake": 1, "point": 182280} and native["verified_records"] == native["records_durable"] == 182281 and native["verified_point_records"] == native["point_records_durable"] == result["native_calls"] == 182280)
    check("native_success_receipt", native["complete_gzip_readback"] and not native["owner_failed"] and native["trace_error"] is None)

    # The one-run process exception is a returned execution-boundary artifact.
    # Read it as text/data only; never load sitecustomize or broaden its approval.
    allowlist = read(outer / "IDLE_CODEX_ALLOWLIST.json")
    process = read(outer / "PROCESS_BEFORE_DISPATCH.json")
    key = lambda row: (row["pid"], row["start_ticks"], row["cmdline_sha256"])
    allowed = {key(row) for row in allowlist["candidates"]}
    observed = {key(row) for row in process["user_approved_idle_candidates"]["observed_and_allowed"]}
    check("exact_process_approval", len(allowed) == 5 and observed == allowed and process["kill_or_signal_calls"] == 0 and process["execution_allowed"] and not process["hold_reasons"])
    check("allowlist_sha", sha(outer / "IDLE_CODEX_ALLOWLIST.json") == "48e171e31754e8a3ce6e43137fdd1eff1c3bc0b3cac56318a8d1cf3d08317c2f")
    check("shim_sha", sha(outer / "sitecustomize.py") == "1c2d17acac8538969766c53c75396a69b6faaa029822a5370a472b2f63702466")

    segments = metadata["segments"]
    counters, stats = Counter(), Counter()
    for segment in segments:
        counters.update(segment["evidence"]["telemetry"]["counters"])
        for name in ("accepted_macro_steps", "attempts", "rejected_macro_steps", "rhs_evaluations", "jvp_vectors", "linear_iterations"):
            stats[name] += segment["evidence"]["stats"][name]
    check("saved_segment_success", len(segments) == metadata["segment_count"] == 83 and all(s["evidence"]["telemetry"]["success"] and s["evidence"]["stats"]["dimension"] == 663 and s["evidence"]["requested_threads"] == 1 and not s["evidence"]["callback_failures"] for s in segments))
    check("segment_time_extent", segments[0]["left_s"] == 0 and segments[-1]["right_s"] == metadata["t_end_s"] and all(a["right_s"] == b["left_s"] for a, b in zip(segments, segments[1:])))
    old_temperatures = [v["reference_temperature_K"] for v in comparisons.values()]
    low, high = min(old_temperatures), max(old_temperatures)
    phases = result["phase_wall_s"]
    old_table = read(baseline / "m8_r4_table512/TABLE.json")["diagnostics"]["build_wall_s"]
    check("table_full_build_record", result["source_table_cache"]["status"] == "BUILT_AND_VERIFIED" and len(set(result["source_table_execution"]["worker_pids_observed"])) == 48)
    return {
        "schema": "he29.canary.saved_return.consumer.v1",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_SCOPED_SAVED_CANARY" if not failures else "HOLD_CONSUMER_MISMATCH",
        "source_pr": 81, "original_return_commit": "d6c1cf97ee216269114b1b0d1bb45984e2140f8b",
        "repaired_result_commit": "fcdf56d9a66b2d159d42a9a72131f94040cd5891",
        "execution_code": CODE, "checks": checks, "failed_checks": failures,
        "counts": {"reference_pairs_reused": 4, "imported_completed_canaries": 1, "consumer_NCP_submissions": 0, "consumer_solver_runs": 0, "consumer_native_calls": 0, "old_tests_replayed": 0},
        "identity_scope": {"new_bridge_binary_bytes": "READ_SHA256_PASS", "native_owner_binary_bytes": "NOT_PROVIDED_IN_NEW_ARCHIVE; prior admitted byte identity reused", "table_array_bytes": "NOT_PROVIDED; producer full hash gate and matching saved baseline table reused", "original_22_DATA_bytes": "NOT_PROVIDED; returned manifest/cohort hashes match admitted baseline", "six_new_adapter_files": "ACTUAL_GIT_SOURCE_BYTES_MATCH_RETURNED_IDENTITY"},
        "endpoint": {k: v for k, v in endpoint.items() if k != "metadata"},
        "gates": {k: {"observed": v, "original_limit": t, "pass": v <= t} for k, (v, t) in gates.items()},
        "canary_minus_saved_reference": comparisons,
        "candidate_temperature_hull": {"old_two_candidate_min_K": low, "old_two_candidate_max_K": high, "canary_in_old_hull": low <= endpoint["temperature_K"] <= high, "old_width_K": difference(high, low), "new_three_candidate_width_K": difference(max(high, endpoint["temperature_K"]), min(low, endpoint["temperature_K"])), "true_ODE_error_radius": "NOT_CERTIFIED"},
        "native_full_gzip_readback": {"sha256": NATIVE_GZIP, "bytes": gzip_path.stat().st_size, "counts": dict(counts), "point_wire_shapes": [{"request_fields": k[0], "response_fields": k[1], "count": v} for k, v in shapes.items()], "bad_record_indices": bad_records, "handshake": first_handshake, "complete_stream_eof_and_crc": True},
        "process_exception": {"exact_identity_count": len(allowed), "raw_process_observation_utc": process["observed_utc"], "signals_or_terminations": process["kill_or_signal_calls"], "host_plan_git_bytes_modified": False, "extra_runtime_shim_present": True, "future_allowance": "NONE; original one-run approval only", "current_live_process_census": "NOT_PERFORMED"},
        "saved_segment_summary": {"segments": len(segments), "full_state_dimension": 663, "stats": dict(stats), "counters": dict(counters)},
        "timing_s": {"bridge_build": build["build_receipt"]["wall_s"], "canary_watchdog": read(canonical / "SUMMARY.json")["process_receipt"]["wall_s"], "canary_worker": result["wall_s"], "worker_phases": phases, "table_pool": table["execution"]["build_wall_s"], "table_diagnostics": table["diagnostics"]["build_wall_s"], "historical_serial_table_diagnostics": old_table, "historical_old_over_new_table_diagnostics": old_table / table["diagnostics"]["build_wall_s"], "packed_solve_fraction_of_worker": phases["packed_solve_and_checkpoints_s"] / result["wall_s"]},
        "performance_scope": "Actual returned phase times; no matched before/after packed workload. Historical table ratio is not controlled scaling and pair/canary quotient is not a speedup.",
        "holds": ["continuous_spectrum", "global_gas_temperature_error_bound", "full_EoR", "whole_Grackle_equivalence", "observational_Bianchi_CMB", "matched_packed_speedup_factor"],
        "validation_counting": "Checks and 182281 trace records are data predicates, not new independent scientific test methods.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--he29-root", required=True)
    parser.add_argument("--return-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit("refuse to overwrite existing consumer report")
    try:
        report = inspect(args)
    except Exception as error:
        report = {"schema": "he29.canary.saved_return.consumer.v1", "status": "HOLD_READER_EXCEPTION", "error": repr(error), "consumer_native_calls": 0}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "failed_checks": report.get("failed_checks", []), "error": report.get("error"), "consumer_native_calls": 0}))
    return 0 if report["status"] == "PASS_SCOPED_SAVED_CANARY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
