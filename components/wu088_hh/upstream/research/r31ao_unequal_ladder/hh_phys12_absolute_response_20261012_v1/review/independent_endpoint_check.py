#!/usr/bin/env python3
"""Independent read-only PHYS12 evidence check. Does not import or rerun the candidate."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import csv
import hashlib
import json
import struct
import time
import resource

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review"
START = time.perf_counter()
CPU0 = time.process_time()
checks = []
counts = {"frozen_files": 0, "run_bindings": 0, "source_intervals": 0,
          "primary_intervals": 0, "mixed_intervals": 0, "ratio_intervals": 0,
          "output_exact_endpoints": 0, "outward_decimal_endpoints": 0,
          "csv_rows": 0}

def check(value, label):
    checks.append({"id": label, "passed": bool(value)})
    if not value:
        raise AssertionError(label)

def read(path):
    return json.loads((ROOT / path).read_text())

def exact(v):
    return tuple(F(int(v["exact"][s][0]), int(v["exact"][s][1]))
                 for s in ("lo", "hi"))

def source_interval(v, label):
    lo, hi = exact(v)
    check(lo <= hi, label + "/ordered")
    check(F(v["lo"]) <= lo and hi <= F(v["hi"]), label + "/binary64_outward")
    check(struct.pack(">d", v["lo"]).hex() == v["lo_bits"], label + "/lo_bits")
    check(struct.pack(">d", v["hi"]).hex() == v["hi_bits"], label + "/hi_bits")
    counts["source_intervals"] += 1
    return lo, hi

def check_output(v, expected, label, group):
    got = exact(v)
    check(got == expected, label + "/exact_endpoint_identity")
    lo, hi = got
    decimal_bounds = tuple(F(Decimal(t)) for t in v["outward_decimal"])
    check(decimal_bounds[0] <= lo <= hi <= decimal_bounds[1],
          label + "/decimal_outward")
    wanted = "STRICT_POSITIVE" if lo > 0 else "STRICT_NEGATIVE" if hi < 0 else "ZERO_CONTAINING"
    check(v["sign"] == wanted, label + "/sign")
    counts[group] += 1
    counts["output_exact_endpoints"] += 2
    counts["outward_decimal_endpoints"] += 2

freeze = read("review/REVIEW_INPUTS.json")
check(len(freeze["files"]) == 31, "freeze/31_named_files")
for item in freeze["files"]:
    content = (ROOT / item["path"]).read_bytes()
    check(len(content) == item["bytes"] and hashlib.sha256(content).hexdigest() == item["sha256"],
          "freeze/" + item["path"])
    counts["frozen_files"] += 1
source_path = ROOT / "inputs/phys09/PROJECTED_RESULTS.json"
source_bytes = source_path.read_bytes()
source_hash = hashlib.sha256(source_bytes).hexdigest()
source_git_blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
check(source_hash == "c6329fed8c411e1592bd1a0c63ebd9ca6151e81500ed1f46fb6b40f4b7758444",
      "source/prior_SHA256")
check(source_git_blob == "9dd38e85bd52aa5d9e367a84413b3c531272f0fe",
      "source/independently_observed_remote_git_blob")
source = json.loads(source_bytes)
final = read("results/absolute_v1/ABSOLUTE_RESULTS.json")
summary = read("results/absolute_v1/SUMMARY.json")
plan = read("inputs/PLAN_OBSERVABLE_CONTRACTS.json")
family = read("inputs/family/FROZEN_SOURCE_CONTRACT.json")
inherited_decision = read("inputs/phys09/DECISION.json")
check(inherited_decision["decision"] == "PROMOTE_SCOPED", "source/prior_scoped_decision")
check(family["theta"] == [[0,1],[0,1]], "source/whole_unit_rectangle")
check(plan["next_local_observables"]["fixed_b_amp"] == 1, "plan/fixed_b1")
check(final["source_sha256"] == source_hash, "output/source_SHA256")
check([r["stage"] for r in final["rows"]] == ["full","first_half"], "output/stage_order")
check(len(source["stages"]) == len(final["rows"]) == 2, "output/two_named_first_stages")

recorded_intervals = []
for stage, detail, row, display_row in zip(source["stages"], source["details"], final["rows"], summary["rows"]):
    name = stage["stage"]
    check(name == detail["stage"] == row["stage"] == display_row["stage"], name + "/stage_identity")
    check(detail["same_COMMON_first_stage"] is True, name + "/same_COMMON_first")
    check(detail["native_authority"] is False and all(v is None for v in detail["actual_native"].values()),
          name + "/native_ceiling")
    check(row["b_amp"] == 1 and row["lambda_path"] == [0,1], name + "/unit_path_at_b1")
    frozen_dt = family["stages"]["phys07_sourcebox_" + name + "_first"]
    check(row["dt_s"] == frozen_dt == plan["next_local_observables"]["stages_seconds"][name],
          name + "/duration_binding")
    gamma = source_interval(stage["gamma"], name + "/gamma")
    determinant = source_interval(stage["det_C"], name + "/det_C")
    check(gamma[1] < 1 and determinant[0] > 0, name + "/inherited_contraction_and_invertibility")
    for j, margin in enumerate(stage["margins"]):
        check(source_interval(margin, name + "/margin" + str(j))[0] > 0,
              name + "/strict_margin" + str(j))
    U = [source_interval(v, name + "/U" + str(j)) for j,v in enumerate(stage["U"])]
    W = [source_interval(v, name + "/W" + str(j)) for j,v in enumerate(stage["W"])]
    check(len(U) == len(W) == 4, name + "/four_component_order")
    for obs,j,unit in [("x_HII",0,"dimensionless HII fraction"),("w",3,"eV per H nucleus")]:
        check_output(row["absolute"][obs], U[j], name + "/absolute/" + obs, "primary_intervals")
        check_output(row["mixed_reused"][obs], W[j], name + "/mixed/" + obs, "mixed_intervals")
        check(exact(detail["finite_unit_square_interaction"]["gas"][j]) == W[j],
              name + "/prior_finite_interaction_matches_W/" + obs)
        for kind in ["absolute","mixed_reused"]:
            check(row[kind][obs]["unit"] == unit, name + "/" + kind + "/" + obs + "/units")
            for key in ["unit","sign","outward_decimal"]:
                check(row[kind][obs][key] == display_row[kind][obs][key],
                      name + "/summary/" + kind + "/" + obs + "/" + key)
            recorded_intervals.append({"stage":name,"kind":kind,"observable":obs,
                                       "display":row[kind][obs]["outward_decimal"],
                                       "sign":row[kind][obs]["sign"]})
    check(U[0][0] > 0 and U[3][1] < 0 and W[0][1] < 0 and W[3][0] > 0,
          name + "/four_required_signs")
    expected_rx = (-W[0][1] / U[0][1], -W[0][0] / U[0][0])
    expected_rw = (W[3][0] / (-U[3][0]), W[3][1] / (-U[3][1]))
    ratio = row["modulation_over_absolute_at_b1"]
    check_output(ratio["ionization_suppression"], expected_rx, name + "/ratio/rx", "ratio_intervals")
    check_output(ratio["thermal_loss_reduction"], expected_rw, name + "/ratio/rw", "ratio_intervals")
    check("b_amp=1" in ratio["denominator"] and ratio["cosmological_negligibility_claim"] is False,
          name + "/ratio_definition_and_ceiling")
    for key in ["ionization_suppression","thermal_loss_reduction"]:
        check(ratio[key]["outward_decimal"] == display_row["modulation_over_absolute_at_b1"][key]["outward_decimal"],
              name + "/summary_ratio/" + key)

with (ROOT / "results/absolute_v1/OBSERVABLES.csv").open(newline="") as f:
    csv_rows = list(csv.DictReader(f))
check(len(csv_rows) == 8, "csv/eight_primary_and_mixed_rows")
by_stage = {r["stage"]:r for r in final["rows"]}
for r in csv_rows:
    v = by_stage[r["stage"]][r["quantity_kind"]][r["observable"]]
    check([r["lower_outward"],r["upper_outward"]] == v["outward_decimal"]
          and r["sign"] == v["sign"] and r["unit"] == v["unit"]
          and int(r["b_amp"]) == 1 and int(r["dt_s"]) == by_stage[r["stage"]]["dt_s"],
          "csv/" + "/".join([r["stage"],r["quantity_kind"],r["observable"]]))
    counts["csv_rows"] += 1

before = read("evidence/absolute_v1/INPUTS_BEFORE.json")
after = read("evidence/absolute_v1/INPUTS_AFTER.json")
check(before == after and len(before) == 15, "execution/15_same_before_after_bindings")
for item in before:
    content=(ROOT/item["path"]).read_bytes()
    check(len(content) == item["bytes"] and hashlib.sha256(content).hexdigest() == item["sha256"],
          "execution/current_binding/" + item["path"])
    counts["run_bindings"] += 1
check((ROOT/"evidence/absolute_v1/CANDIDATE.py").read_bytes() == (ROOT/"code/analyze_absolute_hh.py").read_bytes(),
      "execution/frozen_program_snapshot")
check((ROOT/"evidence/absolute_v1/SCIENTIFIC_CONTRACT.md").read_bytes() == (ROOT/"SCIENTIFIC_CONTRACT.md").read_bytes(),
      "execution/frozen_contract_snapshot")
execution = read("evidence/absolute_v1/EXECUTION.json")
stdout = read("evidence/absolute_v1/stdout.txt")
check(execution["exit_code"] == 0 and execution["bound_files_unchanged"] is True,
      "execution/recorded_success")
check(execution["wall_seconds"] < 30 and execution["cpu_user_seconds"] + execution["cpu_system_seconds"] < 30
      and execution["peak_RSS_KiB_linux"] < 384*1024, "execution/recorded_resource_budget")
check((ROOT/"evidence/absolute_v1/stderr.txt").stat().st_size == 0, "execution/stderr_empty")
check(stdout["rows"] == summary["rows"], "execution/raw_stdout_rows_match_saved_summary")
check(len(final["checks"]) == final["checked_assertions"] == stdout["checked_assertions"] == summary["checked_assertions"] == 189,
      "execution/189_recorded_assertions")
check(all(c["passed"] for c in final["checks"]), "execution/all_recorded_assertions_true")
check(final["native_authority"] is False and final["actual_native_root_U_V_W_I"] is None
      and final["consumer_absolute_threshold"] is None and final["heavy_queue"] == [] and final["launch"] is False,
      "output/native_significance_and_NCP_ceiling")
for key in ["carried_second_half","time_remainder","continuum_remainder","global_conservation","full49","production"]:
    check(final[key] == "OPEN", "output/preserved_open/" + key)

result = {
    "schema":"HH_PHYS12_INDEPENDENT_READ_ONLY_ENDPOINT_CHECK_V1",
    "status":"PASS",
    "reviewer":"/root/remote_state",
    "candidate_code_imported_or_executed":False,
    "source_or_native_or_inverse_solve_calls":0,
    "counts":counts,
    "checks_are_data_integrity_checks_not_independent_physical_experiments":True,
    "checks":checks,
    "source_sha256":source_hash,
    "source_git_blob_sha":source_git_blob,
    "observed_interval_displays":recorded_intervals,
    "frozen_packet_sha256":hashlib.sha256((ROOT/"review/REVIEW_INPUTS.json").read_bytes()).hexdigest(),
    "wall_seconds":time.perf_counter()-START,
    "cpu_seconds":time.process_time()-CPU0,
    "peak_RSS_KiB_linux":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    "scope_limit":"This checks extraction/finite-FTC arithmetic and recorded evidence. The inherited interval producer, original U solver, and native authority are not newly proved."
}
(REVIEW/"INDEPENDENT_ENDPOINT_CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k not in ["checks","observed_interval_displays"]},indent=2))
