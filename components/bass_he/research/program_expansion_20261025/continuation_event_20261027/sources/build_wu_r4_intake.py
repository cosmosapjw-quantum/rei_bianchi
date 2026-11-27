#!/usr/bin/env python3
"""Source-only WU R4 consumer intake. No compiler, fit or physics is executed."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from time import perf_counter, process_time

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_wu_r4"
PREVIOUS = HERE.parent.parent / "continuation_20261027" / "sources"
PREVIOUS_REL = "../../continuation_20261027/sources/"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def role(record):
    c = record["composition"]
    if not c:
        return "electron"
    if sum(x["count"] for x in c) > 1:
        return "molecular"
    if c[0]["Z"] == 0:
        return "neutron"
    return "anion" if record["charge"] < 0 else "atomic"


def main():
    cpu0, wall0 = process_time(), perf_counter()
    checks = []

    def check(name, truth):
        if not truth:
            raise ValueError(name)
        checks.append({"name": name, "pass": True})

    manifest = read(RAW / "SOURCE_MANIFEST.json")
    m = {x["local_path"]: x for x in manifest["files"]}
    check("13_minimal_source_files", len(m) == len(manifest["files"]) == 13)
    for rel, row in m.items():
        data = (RAW / rel).read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        check("source_bytes:" + rel,
              len(data) == row["bytes"] == row["expected_bytes"]
              and hashlib.sha256(data).hexdigest() == row["sha256"]
              and git_blob == row["git_blob"] == row["expected_git_blob"])

    def source_ref(rel, pointer="/"):
        entry = m[rel]
        return {"local_path": "raw_wu_r4/" + rel, "json_pointer": pointer,
                "repository": entry["repository"], "commit": entry["commit"],
                "path": entry["path"], "git_blob": entry["git_blob"],
                "sha256": entry["sha256"], "url": entry["url"]}

    base_path = PREVIOUS / "CONSUMER_PROJECTION.json"
    r3_path = PREVIOUS / "r3_update" / "OVERLAY.json"
    base, r3 = read(base_path), read(r3_path)
    base_hash, r3_hash = digest(base_path), digest(r3_path)
    check("frozen_source_projection_unchanged",
          base_hash == "e10b896d11863cfac9bb1e457bf539d4ed577fae289f3775ee957d0555bfe368")
    check("frozen_R3_overlay_unchanged",
          r3_hash == "7041ae9cc5653b40485b77aaf1ac5d0ac4dee8280492fc7f2bcfa3812da7cd37")
    old_ref = lambda ptr: {"local_path": PREVIOUS_REL + "CONSUMER_PROJECTION.json",
                           "json_pointer": ptr, "sha256": base_hash}
    r3_ref = lambda ptr: {"local_path": PREVIOUS_REL + "r3_update/OVERLAY.json",
                          "json_pointer": ptr, "sha256": r3_hash}

    r4s = read(RAW / "registry/species.json")
    provider_overlay = read(RAW / "registry/provider_overlay.json")
    events = read(RAW / "registry/events.json")["rows"]
    compiled = read(RAW / "registry/compiled.json")
    packet = read(RAW / "sources/MOLECULAR_SOURCE_PACKET.json")
    admission = read(RAW / "SCIENTIFIC_ADMISSION.json")
    accepted = admission["scientific_payload"]
    complete = read(RAW / "registry/COMPLETE.json")
    diagnostics = read(RAW / "registry/fit_diagnostics.json")
    independent = read(RAW / "raw/INDEPENDENT_RESULTS.json")
    implementation = read(RAW / "verification/IMPLEMENTATION_RESULT.json")
    check("exact_accepted_source_packet",
          digest(RAW / "sources/MOLECULAR_SOURCE_PACKET.json")
          == accepted["source_packet"]["sha256"] == provider_overlay["new_packet_sha256"]
          == complete["source_packet_sha256"] == independent["source_packet_sha256"])
    check("exact_accepted_C9", digest(RAW / "reviews/C9_FINAL.json") == admission["independent_C9"]["sha256"])
    for member in complete["members"]:
        if member["path"] in m:
            check("saved_output:" + member["path"], digest(RAW / member["path"]) == member["sha256"])

    union = {}
    for i, row in enumerate(base["species"]):
        sid = row["wu_species_id"]
        union[sid] = {"id": sid, "compiler_record": row["compiler_record"],
                      "inventory_role": row["inventory_role"], "source_refs": [old_ref(f"/species/{i}")],
                      "new_to_HE": False, "base_source_labels": row["source_labels"],
                      "base_qualification": row["qualification"], "R4_qualification": None}
    check("base_92_unique_IDs", len(union) == len(base["species"]) == 92)
    reused = []
    for sid, row in r4s["rows"].items():
        check("R4_key_matches_authority_ID:" + sid, sid == row["id"])
        ref = source_ref("registry/species.json", "/rows/" + sid)
        if sid in union:
            check("reused_exact_compiler_record:" + sid,
                  union[sid]["compiler_record"] == row["compiler_record"])
            union[sid]["source_refs"].append(ref)
            union[sid]["R4_qualification"] = row["qualification"]
            reused.append({"id": sid, "material_family": row["material_family"],
                           "compiler_record_identical": True})
        else:
            union[sid] = {"id": sid, "compiler_record": row["compiler_record"],
                          "inventory_role": role(row["compiler_record"]), "source_refs": [ref],
                          "new_to_HE": True, "base_source_labels": None,
                          "base_qualification": None, "R4_qualification": row["qualification"]}
    check("14_records_2_reused_12_new_104_union",
          len(r4s["rows"]) == 14 and len(reused) == 2 and len(union) == 104
          and sum(x["new_to_HE"] for x in union.values()) == 12)
    check("only_Hplus_Dplus_ID_reuse", {x["id"] for x in reused}
          == {"sp_4efa39d0560d4d0f0f09", "sp_67e18c83359dac9a96d8"})

    providers = [{"id": x["id"], "source_refs": [old_ref(f"/providers/{i}")], "release": x["release"]}
                 for i, x in enumerate(base["providers"])]
    providers += [{"id": x["id"], "source_refs": [r3_ref(f"/new_provider_index/{i}")], "release": "R3"}
                  for i, x in enumerate(r3["new_provider_index"])]
    check("base132_provider_refs", len(providers) == len({x["id"] for x in providers}) == 132)
    old_provider_ids = {x["id"] for x in providers}
    rows_by_id = {x["id"]: x for x in packet["rows"]}
    check("6_distinct_new_provider_refs", len(rows_by_id) == 6
          and not old_provider_ids.intersection(rows_by_id)
          and set(rows_by_id) == set(provider_overlay["new_variants"]))
    providers += [{"id": x["id"], "source_refs": [source_ref("sources/MOLECULAR_SOURCE_PACKET.json", f"/rows/{i}")],
                   "release": "R4", "physical_rate_admitted": False}
                  for i, x in enumerate(packet["rows"])]
    event_refs = [{"id": x["id"], "source_refs": [old_ref(f"/events/{i}")], "release": x["release"]}
                  for i, x in enumerate(base["events"])]
    check("base149_event_refs", len(event_refs) == len({x["id"] for x in event_refs}) == 149)
    check("6_distinct_new_event_refs", len(events) == len({x["id"] for x in events}) == 6
          and not {x["id"] for x in events}.intersection(x["id"] for x in event_refs))
    event_refs += [{"id": x["id"], "source_refs": [source_ref("registry/events.json", f"/rows/{i}")],
                    "release": "R4", "activation": False} for i, x in enumerate(events)]
    check("138_provider_155_event_union", len(providers) == 138 and len(event_refs) == 155)
    check("77_source_rate_cells_no_evaluation", sum(len(x["native_rows"]) for x in packet["rows"]) == 77)
    check("saved29_formula_samples_only", len(diagnostics["rows"]) == diagnostics["new_primary_formula_samples"] == 29)
    check("saved6_compiler_rows_only", len(compiled["rows"]) == compiled["new_compiler_calls"] == 6
          and compiled["old_compiler_checks_replayed"] == 0)

    common_obligations = {
        "DCS": "State/branch resolved nonnegative differential law with native normalization and support; scalar thermal rate is insufficient.",
        "angular": "Source frame, angular law or necessary moments, azimuth/symmetry assumptions and mass-dependent frame conversion are unbound.",
        "mass": "Actual isotope/electronic/rovibrational masses, composition-mass convention, state energies and covariance require explicit binding; no automatic mass assignment.",
        "joint_final_state": "Correlated branch, outgoing energies and directions are absent; aggregate products cannot be independently sampled into a complete event law.",
        "deposition": "Named thermal/fast/radiation consumer, source distribution, proper event flux and single energy/momentum ownership remain unbound.",
    }
    by_compiled = {x["event_id"]: x for x in compiled["rows"]}
    by_event = {x["id"]: x for x in events}
    supply = []
    for i, row in enumerate(packet["rows"]):
        pid = row["id"]
        event, saved = by_event[pid], by_compiled[pid]
        check("event_participants_exist:" + pid,
              all(sid in r4s["rows"] for side in ("reactants", "products") for sid, _ in event[side]))
        check("source_event_identity:" + pid,
              saved["provider_record_sha256"] == event["source_identity"])
        check("physical_gates_off:" + pid,
              not event["activation"] and not event["empirical_rate_admitted"] and not event["nuclear_Q_admitted"]
              and saved["energy"] is None and saved["energy_status"] == "UNQUALIFIED:ENERGY"
              and not saved["rate_normalization_bound"])
        incoming = sum(count for _, count in event["reactants"])
        outgoing = sum(count for _, count in event["products"])
        is_ra = event["process"] == "radiative_association"
        check("declared_channel_shape:" + pid,
              (incoming, outgoing, event["primary_emission_count"]) == ((2, 1, 1) if is_ra else (2, 2, 0)))
        supply.append({
            "provider_id": pid, "native_rate_cells": len(row["native_rows"]),
            "native_first_row": row["native_rows"][0], "native_last_row": row["native_rows"][-1],
            "native_support": row["native_support"], "native_fit": row.get("native_fit"),
            "source_id": row["source_id"], "source_reference": packet["sources"][row["source_id"]],
            "source_reactants": row["reactants"], "source_products": row["products"],
            "isotopic_qualification": row["isotopic_qualification"],
            "statistical_factor": row.get("statistical_factor"),
            "number_density_convention": row["number_density_convention"],
            "event_id": event["id"], "process": event["process"],
            "channel_kind": "MATERIAL_2_TO_1_PLUS_PRIMARY_PHOTON" if is_ra else "MATERIAL_2_TO_2_DECLARED",
            "NR_2to2_theory_candidate_only": not is_ra,
            "NR_2to2_theory_physically_bound": False,
            "ownership_group_sha256": saved["ownership_group_sha256"],
            "physical_event_key_sha256": saved["physical_event_key_sha256"],
            "ownership_slot": event["ownership_slot"],
            "primary_emission_count": event["primary_emission_count"],
            "total_cascade_photon_yield": event["total_cascade_photon_yield"],
            "escaped_photon_yield": event["escaped_photon_yield"],
            "escaped_photon_energy": event["escaped_photon_energy"],
            "external_label_qualification": event["external_label_qualification"],
            "native_Q_record": event["native_Q_record"], "native_uncertainty_record": event["native_uncertainty_record"],
            "source_refs": [source_ref("sources/MOLECULAR_SOURCE_PACKET.json", f"/rows/{i}"),
                            source_ref("registry/events.json", f"/rows/{events.index(event)}"),
                            source_ref("registry/compiled.json", f"/rows/{compiled['rows'].index(saved)}")],
            "remaining_provider_obligations": common_obligations,
            "physical_admission": False,
        })
    groups = {x["ownership_group_sha256"] for x in supply}
    check("5_ownership_groups_6_variants", len(groups) == 5)
    h = [x for x in supply if x["provider_id"].startswith("HONVAULT")]
    check("TIQM_SQM_same_ownership_and_event", len(h) == 2
          and h[0]["ownership_group_sha256"] == h[1]["ownership_group_sha256"]
          and h[0]["physical_event_key_sha256"] == h[1]["physical_event_key_sha256"])
    counts = {"base_species": 92, "r4_species_records": 14, "reused_species": 2,
              "new_unique_species": 12, "union_species": 104,
              "base_provider_variants": 132, "new_provider_variants": 6, "union_provider_variants": 138,
              "base_event_columns": 149, "new_event_columns": 6, "union_event_columns": 155,
              "ownership_groups_R4": 5, "native_R4_rate_cells": 77,
              "RA_variant_rows": 1, "material_2to2_variant_rows": 5,
              "union_inventory_roles": dict(Counter(x["inventory_role"] for x in union.values()))}
    flags = {"source_only": True, "populations_admitted": False, "physical_rates_admitted": False,
             "energy_Q_admitted": False, "DCS_admitted": False, "activation": False,
             "automatic_rate_DCS_mass_binding": False, "new_configured_populations": 0,
             "co_evolution_admitted": False, "source_state_transfer_admitted": False,
             "named_consumer_ACK": None, "global_physical_completion": None}
    refs = {"schema": "he.event03.source_refs.v1", "pinned_WU_commit": manifest["pinned_commit"],
            "pinned_WU_tree": manifest["pinned_tree"],
            "raw_manifest": {"local_path": "raw_wu_r4/SOURCE_MANIFEST.json", "sha256": digest(RAW / "SOURCE_MANIFEST.json")},
            "documents": [source_ref(k) for k in m],
            "baseline": [old_ref("/"), r3_ref("/")],
            "original_HE_source_commit": "76beebc67493c7d931fa3eea35a1d3f362a55805",
            "unbundled_complete_members": [x for x in complete["members"] if x["path"] not in m]}
    result = {"schema": "he.event03.wu_r4_consumer_union.v1", "unit": "HE-EXP-EVENT-03",
              "authority": "WU owns source species/event identities; HE holds this additive consumer reference view.",
              "counts": counts, "species": sorted(union.values(), key=lambda x: x["id"]),
              "reused_species": reused, "provider_refs": providers, "event_refs": event_refs,
              "provider_supply": supply, "intake_flags": flags,
              "provenance": refs,
              "source_count_note": "R4 has 14 records, including existing H+ and D+ IDs; unique increment12. This union is not a partition of simultaneously evolvable populations.",
              "reused_upstream_acceptance": {"decision": admission["decision"], "accepted_scopes": accepted["accepted_scopes"],
                  "evidence": accepted["evidence"], "physical_flags": accepted["physical_admission_flags"],
                  "saved_independent_status": independent["status"], "saved_implementation_passed": implementation["passed"],
                  "source_formula_samples_replayed_here": 0, "compiler_calls_here": 0, "old_tests_replayed_here": 0},
              "preserved": {"HE101_C8": "OPEN", "HE101_budget_changed": False, "PHYS91_remaining": [0, 0, 0],
                  "old_DRIFT02_replayed": 0, "old_WU249_replayed": 0, "HH_R10": "OFF", "L4_ready": False,
                  "production": "NOT_ISSUED", "original19_targets": 19, "original28_source_references": 28}}
    write("SOURCE_REFS.json", refs)
    write("WU_R4_CONSUMER_UNION.json", result)
    check("old_projection_still_unchanged", digest(base_path) == base_hash and digest(r3_path) == r3_hash)
    receipt = {"schema": "he.event03.source_intake_receipt.v1", "status": "PASS_SOURCE_ONLY_RELATIONAL_INTAKE",
               "source_files": len(m), "source_bytes": sum(x["bytes"] for x in m.values()),
               "checks": checks, "check_count": len(checks), "counts": counts, "intake_flags": flags,
               "union_sha256": digest(HERE / "WU_R4_CONSUMER_UNION.json"),
               "source_refs_sha256": digest(HERE / "SOURCE_REFS.json"),
               "CPU_seconds": process_time() - cpu0, "wall_seconds": perf_counter() - wall0,
               "scientific_or_formula_evaluations": 0, "compiler_invocations": 0, "old_tests_replayed": 0,
               "preserved_mechanical_inspection_failure": {"exception": "KeyError: photon_ledger",
                   "cause": "A read-only display assumed an optional RA-specific key existed on all provider records.",
                   "science_started": False, "targeted_fix": "Use optional native packet field and declared event primary-emission fields; infer no missing radiation data."}}
    write("SOURCE_INTAKE_RESULT.json", receipt)
    print(json.dumps({"status": receipt["status"], "checks": len(checks), "counts": counts,
                      "science": 0, "union_sha256": receipt["union_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
