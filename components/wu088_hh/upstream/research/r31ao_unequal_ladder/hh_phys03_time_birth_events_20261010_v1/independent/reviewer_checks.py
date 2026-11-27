"""Independent read-only audit of the frozen PHYS03 evidence.

No candidate checker is imported or executed.  The new arithmetic checks use
only exact fractions on saved endpoints and saved decimal witnesses.  This is
not a new evaluation of exp/log, a trajectory, or a native operation audit.
"""
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import platform


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "independent/REVIEWER_CHECKS.json"


def digest(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def dyadic(value):
    mantissa = int(value["mantissa"])
    exponent = int(value["exponent_2"])
    return (Fraction(mantissa * (1 << exponent)) if exponent >= 0
            else Fraction(mantissa, 1 << -exponent))


def main():
    target = json.loads((ROOT / "independent/REVIEW_TARGETS.json").read_text())
    critical = []
    for row in target["files"]:
        observed = digest(ROOT / row["path"])
        assert observed == {k: row[k] for k in ("bytes", "sha256")}, row["path"]
        critical.append({"path": row["path"], **observed, "matches_frozen_target": True})

    survey = ROOT / "inputs/source_survey"
    bindings = json.loads((survey / "SOURCE_LINE_BINDINGS.json").read_text())
    source_rows = []
    for row in bindings:
        raw = (survey / row["path"]).read_bytes()
        segment = raw[row["byte_start"]:row["byte_end_exclusive"]]
        assert sha256(raw).hexdigest() == row["file_sha256"], row["id"]
        assert sha256(segment).hexdigest() == row["segment_sha256"], row["id"]
        first, last = row["lines"]
        assert b"".join(raw.splitlines(keepends=True)[first - 1:last]) == segment, row["id"]
        source_rows.append({
            "id": row["id"], "path": row["path"], "lines": row["lines"],
            "file_sha256": row["file_sha256"],
            "segment_sha256": row["segment_sha256"],
            "hash_and_line_byte_binding_pass": True,
        })

    chronology = json.loads((ROOT / "results/CHRONOLOGY_256.json").read_text())
    selected = ROOT / "inputs/phys02/inputs/SELECTED_SOURCE.json"
    assert digest(selected)["sha256"] == chronology["selected_input_sha256"]
    intervals = {}
    endpoint_rows = []
    for name, ball in chronology["results"].items():
        lo, hi = dyadic(ball["exact_lower"]), dyadic(ball["exact_upper"])
        assert ball["finite"] is True
        assert Fraction(ball["lower"]) <= lo <= hi <= Fraction(ball["upper"]), name
        intervals[name] = lo, hi
        endpoint_rows.append({"name": name, "exact_order_and_outward_decimal": True})

    witnesses = []
    for name, row in chronology["independent_mpmath_110_dps"].items():
        value = Fraction(row["value"])
        lo, hi = intervals[name]
        assert lo <= value <= hi, name
        witnesses.append({"name": name, "stored_decimal_inside_exact_endpoints": True})

    def strictly_before(first, second):
        assert intervals[first][1] < intervals[second][0], (first, second)

    cutoff = Fraction.from_float(chronology["record"]["threshold_node_ev"])
    left = Fraction.from_float(chronology["record"]["left_node_ev"])
    assert left < intervals["characteristic_energy_full_ev"][0]
    strictly_before("characteristic_energy_full_ev", "characteristic_energy_half_ev")
    assert intervals["characteristic_energy_half_ev"][1] < cutoff
    assert 0 < intervals["active_weight_one_full"][0]
    strictly_before("active_weight_one_full", "active_weight_two_half")
    strictly_before("active_weight_two_half", "active_weight_one_half")
    assert intervals["active_weight_one_half"][1] < 1
    assert intervals["two_half_minus_full_active_weight"][0] > 0
    assert intervals["positive_factorized_weight_defect"][0] > 0
    assert intervals["two_half_minus_full_effective_sigma_cm2"][0] > 0
    strictly_before("free_energy_continuous_ev_per_h", "free_energy_two_endpoint_ev_per_h")
    strictly_before("free_energy_two_endpoint_ev_per_h", "free_energy_one_endpoint_ev_per_h")
    assert intervals["time_to_inactive_left_node_s"][0] > Fraction(1250000000)

    # Complete the newly important stage-photon identity from archived records;
    # no seed binary is decoded and no historical solver is executed.
    state = json.loads(selected.read_text())
    records = [json.loads(line) for line in
               (survey / "history/OWNER_PREBE_FINAL_BINARY.jsonl").read_text().splitlines()]
    record = records[4]
    assert record["member"] == 1 and record["label"] == "half1_preBE"
    old_photons = state["old_point_photons"]
    indices = record["indices"]
    assert len(old_photons) == len(indices) == 25 and indices == list(range(25))
    assert all(Fraction.from_float(a) == Fraction.from_float(record["groups"][i])
               for i, a in zip(indices, old_photons))

    additional = [
        "NOTATION_AND_INTERPRETATION_KO.md", "RUN_LEDGER.json",
        "logs/hybrid_initial.stderr", "logs/chronology_initial.stdout",
        "logs/chronology_initial.stderr", "smooth_theory/COMMAND_STATUS.json",
        "smooth_theory/checker.stdout", "smooth_theory/checker.stderr",
    ]
    additional_rows = [{"path": p, **digest(ROOT / p)} for p in additional]
    text_controls = []
    for row in critical + additional_rows:
        if row["path"].endswith(".md"):
            raw = (ROOT / row["path"]).read_bytes()
            invalid = [i for i, b in enumerate(raw) if (b < 32 and b != 10) or b == 127]
            assert not invalid, (row["path"], invalid)
            text_controls.append({"path": row["path"], "non_LF_control_characters": 0})

    result = {
        "schema": "HH-PHYS03-INDEPENDENT-REVIEWER-CHECKS-1",
        "status": "PASS",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "/root/decision_review",
        "arithmetic": "Python standard-library fractions.Fraction",
        "python_version": platform.python_version(),
        "scope": "frozen evidence identity, exact stored interval serialization and ordering, archived stage-photon linkage",
        "critical_target_count": len(critical),
        "critical_targets": critical,
        "review_target_manifest": digest(ROOT / "independent/REVIEW_TARGETS.json"),
        "source_segment_count": len(source_rows),
        "source_segments": source_rows,
        "outward_interval_count": len(endpoint_rows),
        "exact_endpoint_count": 2 * len(endpoint_rows),
        "outward_intervals": endpoint_rows,
        "stored_mpmath_witnesses": witnesses,
        "strict_interval_order_checks": {
            "cell_membership": True, "active_weight_order": True,
            "positive_opacity_defect": True, "free_energy_schedule_order": True,
            "left_knot_time_after_full_step": True,
        },
        "archived_stage_photon_linkage": {
            "selected_input": {"path": str(selected.relative_to(ROOT)), **digest(selected)},
            "record": "inputs/source_survey/history/OWNER_PREBE_FINAL_BINARY.jsonl line 5",
            "member": 1, "label": "half1_preBE", "exact_binary64_matches": 25,
            "gas_seed_redecoded": False,
        },
        "additional_reviewed_files": additional_rows,
        "text_control_character_checks": text_controls,
        "candidate_checkers_rerun": 0,
        "new_transcendental_evaluations": 0,
        "native_dispatches": 0,
        "IVP_trajectory_runs": 0,
        "nonlinear_BE_roots": 0,
        "NCP_runs": 0,
        "old_atomic_integrals": 0,
        "PHYS02_suite_reruns": 0,
    }
    with OUT.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "PASS", "critical_targets": len(critical),
                      "source_segments": len(source_rows),
                      "exact_intervals": len(endpoint_rows),
                      "saved_mpmath_witnesses": len(witnesses),
                      "archived_photon_bits": len(old_photons),
                      "output": str(OUT)}))


if __name__ == "__main__":
    main()
