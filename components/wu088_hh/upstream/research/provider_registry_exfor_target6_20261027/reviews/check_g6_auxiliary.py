"""Target only the diagnosed G6 classifier defect and unfinished auxiliary checks.

The original eight passing groups and the 36 main native rows are not rerun.
The original executable is the python -c argv in raw/independent01/REQUEST.json.
"""
import datetime
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "sources/exfor"
EXPECTED_PACKET = "d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2"
EXPECTED_MANIFEST = "a1c5d4009d0bfacc4edcb248a6878eef6cdafa9690b4ea0d0826dd5356052d06"
EXPECTED_INITIAL = "eb430e6ddbb0a6688b690b6d553f30a5b0d6e91a9a4e58873988b2fb39f4c654"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []


def check(ok, description, kind="targeted_condition"):
    checks.append({"description": description, "kind": kind,
                   "result": "pass" if ok else "fail"})


initial_path = BASE / "reviews/INTAKE_REVIEW.json"
initial = json.loads(initial_path.read_text())
packet = json.loads((SOURCE / "PROVIDER_ROWS.json").read_text())
auxiliary = json.loads((SOURCE / "AUXILIARY_ROWS.json").read_text())

check(sha(SOURCE / "PROVIDER_ROWS.json") == EXPECTED_PACKET,
      "Frozen provider packet is unchanged", "reuse_identity_guard")
check(sha(SOURCE / "MANIFEST.json") == EXPECTED_MANIFEST,
      "Frozen source manifest is unchanged", "reuse_identity_guard")
check(sha(initial_path) == EXPECTED_INITIAL,
      "Initial failed review is unchanged", "reuse_identity_guard")
old_pass = [g for g in initial["groups"] if g["id"] != "G6"]
old_g6 = next(g for g in initial["groups"] if g["id"] == "G6")
check(len(old_pass) == 8 and all(g["result"] == "pass_scoped" for g in old_pass),
      "Exactly the original eight passing groups are reused", "reuse_identity_guard")
check(old_g6["result"] == "fail" and old_g6["assertions"] == 29
      and old_g6["error"] == "record source class EXFOR_M0011003",
      "The recorded failure is exactly the diagnosed auxiliary classifier defect",
      "reuse_identity_guard")

for row in packet["rows"]:
    check(row["record_class"] == "PRIMARY_SOURCE_ROW",
          row["id"] + " retains the main primary record class")

row = auxiliary["rows"][0]
check(row["record_class"] == "AUXILIARY_MULTIPOLE_SOURCE_ROW",
      "EXFOR_M0011003 retains the separate auxiliary multipole record class")
check(row["target_ids"] == [6]
      and row["target_directions"] == {"6": "target_forward"}
      and row["family_ids"] == ["d_d_gamma"]
      and row["direction"] == "family_reverse",
      "Auxiliary source direction is preserved")
state = row["state_resolution"]
check(state["source_target_nuclide"] == "2-HE-4"
      and state["source_emitted_particle"] == "D"
      and state["source_residual"] == "1-H-2"
      and state["source_isotopes_explicit"] is True,
      "Auxiliary source isotope labels are explicit")
check(all(state[k] is None for k in ["electronic_state", "ionic_charge",
                                   "nuclear_isomer_or_excitation_binding"])
      and state["source_native_state_bound_to_bare_projection"] is False,
      "Auxiliary atomic and nuclear state binding is not promoted")
check(row["branch"]["products"] == {"D": 2}
      and row["branch"]["branch_fraction"] is None,
      "Auxiliary identical products remain distinct from a branch probability")
check(row["Q"]["value"] is None and row["Q"]["uncertainty"] is None
      and row["Q"]["mass_convention"] is None and row["Q"]["admitted"] is False,
      "Auxiliary Q remains unresolved")
check(all(row[k] is False for k in ["new_rate_admission", "new_Q_admission",
                                  "activation", "default_active",
                                  "exclusive_channel_binding",
                                  "source_value_evaluated_in_this_intake",
                                  "figure_digitization_performed"]),
      "Auxiliary rate/Q/activation gates remain false")

passed = all(x["result"] == "pass" for x in checks)
result = {
    "schema": "WU_TARGET6_EXFOR_INDEPENDENT_INTAKE_FINAL_V1",
    "reviewer": "/root/provider_rows",
    "source_author": "/root/molecule_sources",
    "created_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "decision": "PASS_SCOPED_SOURCE_INTAKE" if passed else "FAIL",
    "accepted_groups": 9 if passed else 8,
    "group_count": 9,
    "composition": "Original eight passing groups plus corrected G6; no full-suite replay",
    "reused_groups": old_pass,
    "corrected_G6": {
        "result": "pass_scoped" if passed else "fail",
        "main_nonclass_conditions_reused": 24,
        "new_targeted_conditions": sum(x["kind"] == "targeted_condition" for x in checks),
        "reuse_identity_guards": sum(x["kind"] == "reuse_identity_guard" for x in checks),
        "checks": checks,
        "scope": "Main-four and auxiliary-one class distinction, then only unfinished auxiliary state/admission conditions",
    },
    "source_packet_SHA256": sha(SOURCE / "PROVIDER_ROWS.json"),
    "source_manifest_SHA256": sha(SOURCE / "MANIFEST.json"),
    "source_commit": "939a14d7bba1ddce51975cb5e8711ce96b3b0871",
    "initial_failure": {
        "classification": "IMPLEMENTATION_CHECKER_EXPECTATION_FAILURE",
        "cause": "The checker mistakenly required PRIMARY_SOURCE_ROW for the deliberately separate AUXILIARY_MULTIPOLE_SOURCE_ROW",
        "source_packet_changed": False,
        "review": "INTAKE_REVIEW.json",
        "review_SHA256": EXPECTED_INITIAL,
        "receipt": "../raw/independent01/RECEIPT.json",
        "receipt_SHA256": "1bb229d82a4ccd1bd8821e851ff02614862b262118621935649051396212a4d4",
        "original_executable_argv": "../raw/independent01/REQUEST.json",
        "original_request_SHA256": "cf57f1001ae9e6b44bdae41c3cec5a405c9362a654da766a7dc659dce515faf4",
        "preserved": True,
    },
    "targeted_execution": {
        "receipt": "../raw/independent_g6fix01/RECEIPT.json",
        "script": "check_g6_auxiliary.py",
        "script_SHA256": sha(Path(__file__)),
        "previous_eight_groups_rerun": False,
        "main_native_rows_reparsed": 0,
    },
    "audited_source_counts_reused": initial["audited_source_counts"],
    "semantic_review_reused": initial["semantic_review"],
    "open_consumer_obligations": initial["open_consumer_obligations"],
    "overlay_code_review": "Separate authority_survey static review; this review does not execute the overlay checker",
    "new_rate_evaluations": 0,
    "new_Q_evaluations": 0,
    "new_angular_integrations": 0,
    "old_science_replays": 0,
    "old_compiler_calls": 0,
    "physical_rate_Q_consumer_admission": False,
}
out = BASE / "reviews/INTAKE_REVIEW_FINAL.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"decision": result["decision"],
                  "accepted_groups": result["accepted_groups"],
                  "group_count": 9,
                  "targeted_conditions": result["corrected_G6"]["new_targeted_conditions"],
                  "reuse_identity_guards": result["corrected_G6"]["reuse_identity_guards"],
                  "failures": [x for x in checks if x["result"] == "fail"],
                  "output": str(out.relative_to(BASE))}, ensure_ascii=False))
sys.exit(0 if passed else 1)
