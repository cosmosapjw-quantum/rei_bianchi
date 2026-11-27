#!/usr/bin/env python3
"""Project frozen WU source identities for HE without compiling or running science.

Only JSON parsing, source hashes and relational inventory checks are performed.
This consumer view does not replace the WU species/event authority.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def write_json(name, value):
    (ROOT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def composition_key(record):
    return tuple(sorted((x["Z"], x["A"], x["isomer"], x["count"])
                        for x in record["composition"]))


def nonstate_key(record):
    return composition_key(record), record["charge"], record["pool"]


def role(record):
    c = record["composition"]
    if not c:
        return "electron"
    if sum(x["count"] for x in c) > 1:
        return "molecular"
    if c[0]["Z"] == 0:
        return "neutron"
    if record["charge"] < 0:
        return "anion"
    return "atomic"


def main():
    cpu0, wall0 = process_time(), perf_counter()
    checks = []

    def check(name, condition):
        if not condition:
            raise ValueError(name)
        checks.append({"name": name, "pass": True})

    manifest = read_json("SOURCE_MANIFEST.json")
    source_by_local = {v["local_path"]: v for v in manifest["files"]}
    check("source_paths_unique", len(source_by_local) == len(manifest["files"]))
    for local, record in source_by_local.items():
        data = (ROOT / local).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        check("pinned_bytes:" + local,
              len(data) == record["bytes"] and sha == record["sha256"]
              and git_blob == record["expected_git_blob"] == record["git_blob"])
    transcription = manifest["supplemental_primary_field_transcription"]
    check("neutral_transcription_bytes",
          hashlib.sha256((ROOT / transcription["local_path"]).read_bytes()).hexdigest()
          == transcription["sha256"])

    def source_ref(local, pointer):
        s = source_by_local[local]
        return {"local_path": local, "json_pointer": pointer,
                "repository": s["repository"], "commit": s["commit"],
                "path": s["path"], "git_blob": s["git_blob"], "sha256": s["sha256"]}

    s1 = read_json("raw/WU_R1_species.json")
    s2 = read_json("raw/WU_R2_species.json")
    species = s1["rows"]
    check("R1_92_source_identities", len(species) == 92)
    check("R2_nine_exact_R1_rows",
          len(s2["rows"]) == 9 and s2["new_species_count"] == 0
          and all(species.get(k) == v for k, v in s2["rows"].items()))
    check("R1_keys_equal_authority_ids", all(k == v["id"] for k, v in species.items()))
    historical = s1["historical_view"]
    check("historical_source21_exists",
          len(historical) == 21 and len({v["species_id"] for v in historical}) == 21
          and all(v["species_id"] in species for v in historical))
    role_counts = Counter(role(v["compiler_record"]) for v in species.values())
    check("source_role_partition",
          role_counts == {"atomic": 70, "molecular": 17, "neutron": 1,
                          "anion": 1, "electron": 3})
    historical_role_counts = Counter(role(species[v["species_id"]]["compiler_record"])
                                     for v in historical)
    check("historical20atomic_plus_neutron",
          historical_role_counts == {"atomic": 20, "neutron": 1})

    providers, events = [], []
    species_events = defaultdict(list)
    provider_events = defaultdict(list)
    for release in ("R1", "R2"):
        pfile, efile = f"raw/WU_{release}_providers.json", f"raw/WU_{release}_events.json"
        rows = read_json(pfile)["rows"]
        erows = read_json(efile)["rows"]
        check(release + "_provider_event_counts",
              (len(rows), len(erows)) == ((102, 125) if release == "R1" else (26, 24)))
        for key, record in rows.items():
            native = record["native_record"]
            providers.append({
                "id": key, "release": release,
                "native_process": native.get("process"),
                "native_record_sha256": record["record_sha256"],
                "record_class": record.get("record_class", "SOURCE_PROVIDER_VARIANT"),
                "source_record": source_ref(pfile, "/rows/" + key),
                "source_payload_ref": record.get("payload_ref"),
                "physical_rate_admitted_by_HE_intake": False,
                "full_differential_law_admitted_by_HE_intake": False,
                "new_nuclear_Q_admitted_by_HE_intake": False,
            })
        for index, event in enumerate(erows):
            eid = event["id"]
            participants = {k for side in ("reactants", "products")
                            for k, _ in event[side]}
            check(release + ":" + eid + ":participants_exist", participants <= species.keys())
            check(release + ":" + eid + ":admission_remains_off",
                  event["activation"] is False
                  and event["empirical_rate_admitted"] is False
                  and event["nuclear_Q_admitted"] is False
                  and event["rate_normalization_bound"] is False)
            linked = [event["source_id"]] + event.get("linked_primary_packet_record_refs", [])
            for sid in participants:
                species_events[sid].append({"release": release, "event_id": eid})
            for pid in set(linked):
                provider_events[pid].append({"release": release, "event_id": eid})
            events.append({
                "id": eid, "release": release,
                "process": event["process"], "kind": event["kind"],
                "reactants": event["reactants"], "products": event["products"],
                "external_reactants": event.get("external_reactants", []),
                "external_products": event.get("external_products", []),
                "source_ids": linked, "source_identity": event["source_identity"],
                "source_record": source_ref(efile, f"/rows/{index}"),
                "projection_qualification": event["projection_qualification"],
                "state_resolution": event["state_resolution"],
                "ownership_slot": event["ownership_slot"],
                "remaining_obligations": event["remaining_obligations"],
                "consumer_ACK": None, "activation": False,
                "energy_admission": "UNQUALIFIED", "physical_rate_admission": False,
            })
    check("128_distinct_provider_variants",
          len(providers) == len({v["id"] for v in providers}) == 128)
    check("149_distinct_event_references",
          len(events) == len({v["id"] for v in events}) == 149)
    for p in providers:
        p["referencing_events"] = provider_events[p["id"]]

    bare = read_json("raw/WU_R1_bare_masses.json")
    neutral = read_json("NEUTRAL_H1_HE4_MASS_CANDIDATES.json")
    mass_refs = defaultdict(list)
    for i, mass in enumerate(bare["rows"]):
        ids = [sid for sid, v in species.items()
               if mass["species_key"] in v["source_labels"]
               and v["compiler_record"]["state"] == "bare_nucleus"]
        check("bare_mass_exact_state:" + mass["species_key"], len(ids) == 1)
        mass_refs[ids[0]].append({
            "type": "BARE_NUCLEAR_GROUND_SOURCE_ROW",
            "mass_kg_source_literal": mass["provider_row"]["kg"],
            "source": source_ref("raw/WU_R1_bare_masses.json", f"/rows/{i}"),
            "joint_covariance_supplied": False,
        })
    for i, mass in enumerate(neutral["mass_rows"]):
        sid = mass["wu_species_id"]
        record = species[sid]["compiler_record"]
        check("neutral_mass_exact_state:" + sid,
              all(record[k] == mass[k] for k in ("composition", "charge", "state", "pool")))
        mass_refs[sid].append({
            "type": "NEUTRAL_GROUND_SOURCE_FIELD_TRANSCRIPTION",
            "source": {"local_path": "NEUTRAL_H1_HE4_MASS_CANDIDATES.json",
                       "json_pointer": f"/mass_rows/{i}",
                       "sha256": transcription["sha256"]},
            "mass_kg": None, "conversion_expression": mass["kg_expression"],
            "joint_covariance_supplied": False,
        })
    check("mass_rows_not_bare_neutral_substitutions",
          len(bare["rows"]) == 5 and len(neutral["mass_rows"]) == 2
          and len(mass_refs) == 7)
    by_nonstate = defaultdict(list)
    for sid, value in species.items():
        by_nonstate[nonstate_key(value["compiler_record"])].append(sid)
    species_projection = []
    for sid, value in species.items():
        record = value["compiler_record"]
        species_projection.append({
            "wu_species_id": sid, "compiler_record": record,
            "source_labels": value["source_labels"],
            "qualification": value["qualification"], "views": value["views"],
            "inventory_role": role(record),
            "source": source_ref("raw/WU_R1_species.json", "/rows/" + sid),
            "present_in_R2_number_projection": sid in s2["rows"],
            "event_references": species_events[sid],
            "mass_source_candidates": mass_refs[sid],
            "missing_mass_source_is_not_mass_number": True,
            "source_qualified_full_differential_provider": None,
            "finite_recoil_angular_thermalization_admission": "SOURCE_AND_CONSUMER_BINDING_PENDING",
            "population_alias_merge_permitted": False,
        })

    old = read_json("raw/HE_PREVIOUS_FIXTURE_INVENTORY.json")
    check("legacy_fixture32_not_current_authority",
          len(old["species"]) == 32
          and sum(v["synthetic_extension"] for v in old["species"]) == 9)
    legacy = []
    for i, value in enumerate(old["species"]):
        candidates = by_nonstate.get(nonstate_key(value), [])
        exact = [sid for sid in candidates
                 if species[sid]["compiler_record"]["state"] == value["state"]]
        legacy.append({
            "legacy_fixture_id": value["supplier_species_id"],
            "legacy_synthetic_extension": value["synthetic_extension"],
            "legacy_state": value["state"],
            "source": source_ref("raw/HE_PREVIOUS_FIXTURE_INVENTORY.json", f"/species/{i}"),
            "same_composition_charge_pool_candidates": candidates,
            "exact_state_matches": exact,
            "qualification": "CANDIDATE_CROSSWALK_ONLY; state partition or explicit binding required",
            "new_physical_coverage_inferred_from_count_difference": False,
        })
    historical_projection = [{
        **value,
        "source_registry_record": source_ref("raw/WU_R1_species.json", f"/historical_view/{i}"),
        "same_composition_charge_pool_state_siblings":
            by_nonstate[nonstate_key(species[value["species_id"]]["compiler_record"])],
        "state_siblings_are_not_merged": True,
    } for i, value in enumerate(historical)]

    c1, c2 = read_json("raw/WU_R1_coverage.json"), read_json("raw/WU_R2_coverage.json")
    target = read_json("raw/WU_R2_targets.json")
    dirs = [d for row in target["rows"] for d in row["directions"]]
    missing = [d["id"] for d in dirs if not d["has_primary_source_record_reference"]]
    check("target19_directions28_reference27_gap6",
          len(target["rows"]) == 19 and len(dirs) == 28
          and missing == ["TARGET19:06:target_forward"])
    check("R2_image_recovery_supersedes_stale_R1_locator",
          c2["original_image_status"] == "RECOVERED_HASH_MATCHED_AND_VISUALLY_REVIEWED")
    nuclear = read_json("raw/WU_R1_nuclear_catalogue_manifest.json")
    check("nuclear_catalogue_remains_separate",
          (nuclear["catalogue_rows"], nuclear["ground_rows"], nuclear["non_ground_rows"])
          == (5843, 3558, 2285)
          and nuclear["all_non_ground_are_isomers"] is False)
    active_non_ground = [sid for sid, v in species.items()
                         if any(c["isomer"] != "ground" for c in v["compiler_record"]["composition"])]
    check("no_active_nuclear_isomer_in_current92", not active_non_ground)

    output = {
        "schema": "he.wu_consumer_projection.v2", "unit_id": "HE-EXP-DRIFT-02-SOURCE-INTAKE",
        "date": "2026-10-27", "scope": "FROZEN_SOURCE_PROJECTION_ONLY",
        "authority": {"species_events": "cosmosapjw-quantum/WU088_HH",
                      "molecular_spectral_adapter": "cosmosapjw-quantum/rec_bianchi",
                      "nonthermal_energy_consumer": "cosmosapjw-quantum/bass_cr",
                      "this_view": "cosmosapjw-quantum/BASS_HE"},
        "WU_provider_branch_observed": "research/provider-registry-20261025",
        "WU_provider_HEAD_observed": "87933da5654bb2e4d93f7de4341df5e0fa0f8716",
        "WU_R1_source_commit": "18a6804d7cbe4879701e83631f7e908bbb84cef1",
        "WU_R2_source_commit": "71019bb469c92d1ea665155ed98c472b362d6706",
        "summary": {"source_species_identities": len(species),
                    "species_roles": dict(role_counts),
                    "pools": dict(Counter(v["compiler_record"]["pool"] for v in species.values())),
                    "historical_atomic_charge_states": 20, "historical_neutron_slots": 1,
                    "R2_reused_species": 9, "R2_new_species": 0,
                    "provider_variants": {"R1": 102, "R2": 26, "total": 128},
                    "event_columns_referenced": {"R1": 125, "R2": 24, "total": 149},
                    "legacy_fixture_rows": 32, "legacy_synthetic_extensions": 9,
                    "mass_bare_source_rows": 5, "mass_neutral_ground_candidates": 2,
                    "unlisted_mass_sources_are_not_zero": True,
                    "new_full_differential_admissions": 0,
                    "active_nuclear_isomer_identities": 0,
                    "global_physical_completion": None},
        "species": species_projection, "historical21_view": historical_projection,
        "legacy_fixture_crosswalk": legacy, "providers": providers, "events": events,
        "original_targets": {"source": source_ref("raw/WU_R2_targets.json", "/rows"),
                             "target_ids_preserved": [r["id"] for r in target["rows"]],
                             "direction_count": 28, "directions_with_primary_reference": 27,
                             "missing_primary_reference_directions": missing,
                             "image_status": c2["original_image_status"],
                             "direct_photonuclear_source_coverage": c2["direct_photonuclear_source_coverage"],
                             "physical_rate_Q_state_branch_admission": False},
        "nuclear_catalogue": {"source": source_ref("raw/WU_R1_nuclear_catalogue_manifest.json", "/"),
                              "rows": 5843, "ground": 3558, "non_ground": 2285,
                              "all_non_ground_are_isomers": False,
                              "active_population_network": False,
                              "no_active_species_added_by_catalogue": True},
        "source_limits": {
            "aggregation": s1["aggregation"],
            "R2_projection_assumptions": s2["projection_assumptions"],
            "electron_UMIST": "Source pool unresolved; electron_thermal coordinate is not a new thermalization admission.",
            "molecules": "17 identities include H2, ortho/para H2, H2+, H3+, HeH+, HD J0..8 and Li6H1/Li7H1; unresolved electronic/vibrational/isotope qualifications remain.",
            "anions": "One source H- candidate; no molecular or other anion catalogue completeness claim.",
            "isomers": "Electronic excited states are not nuclear isomers; no non-ground nuclear isomer is active among the 92.",
            "scalar_sources": "Thermal rates, total cross sections, A-values, branch/yield and beam-averaged records do not supply full joint differential collision laws.",
            "R1_finite_CI_gaps": c1["missing_CI_source_directions"],
            "bare_missing_mass_rows": bare["missing_bare_mass_rows"],
            "neutral_H_He_source": "Additional two-ground-state NIST field transcription; WU bare mass records remain unchanged.",
        },
        "reused_owner_results": {
            "REC_HD": {"source": source_ref("raw/REC_HD_H5_HANDOFF_KO.md", "/"),
                       "levels": 9, "lines": 8, "colliders": 2, "collision_pairs": 18, "rates": 54,
                       "collision_temperature_K": [50, 100, 200],
                       "ortho_para_H2_separate": True,
                       "line_frequency_bridge": "HOLD_SOURCE_DISCREPANCY_UNQUALIFIED",
                       "line_frequency_bridge_passed": 1, "line_frequency_bridge_failed": 7,
                       "HD_H5_physical_error_budget": None, "HD_H5_physically_covered_queries": 0,
                       "HD_H5_total_queries": 313, "replayed": False},
            "CR_HE4": {"source": source_ref("raw/CR_HE4_EXTERNAL_HANDOFF_KO.md", "/"),
                       "status": "He4 ground capture and external consumer interface completed scoped",
                       "physical_channel": "He4+ ground 1s + e -> He4 ground singlet + spontaneous photon",
                       "native_threshold_eV": "24.59", "stationary_heavy_target_recoil": 0,
                       "single_event_energy": "fast electron loses E; internal binding loses I; photon receives E+I",
                       "finite_recoil_admitted": False, "replayed": False},
        },
        "thermodynamic_contract": {
            "heat_capacity": "Cv is a partial derivative of thermal internal energy at fixed independent population coordinates.",
            "particle_count": "Thermal particle count and its source term remain separate from Cv.",
            "binding_internal_energy": "Explicit excitation, ionization, molecular and nuclear energy coordinates each have one owner.",
            "nonthermal_energy": "Fast pools are not thermal energy until a qualified deposition event transfers energy.",
            "molecular_heat_capacity": "Resolved internal populations and unresolved partition contributions require a non-overlapping convention.",
            "bulk_energy": "Bulk momentum work and thermal heating are separate projections of the same event exchange.",
            "source_ownership": "A provider candidate or rate table is not a second energy ledger owner.",
        },
        "protected_results": {"HE101_C8_export": "OPEN", "HE101_budgets_changed": False,
                              "WU_PHYS91_primary_reference_Wolfram_remaining": [0, 0, 0],
                              "WU_249_checks_replayed": 0, "HE_old_science_replayed": 0,
                              "new_rates_Q_fits_IVPs": 0, "global_historical_budget": None,
                              "HH_R10": "OFF", "production": "NOT_ISSUED", "L4_ready": False},
        "new_scientific_admission": False,
    }
    write_json("CONSUMER_PROJECTION.json", output)
    projection_bytes = (ROOT / "CONSUMER_PROJECTION.json").read_bytes()
    receipt = {
        "schema": "he.source_intake_execution_receipt.v1",
        "status": "PASS_SOURCE_IDENTITY_AND_RELATIONAL_PROJECTION",
        "execution_class": "JSON_PARSE_HASH_AND_RELATIONAL_INVENTORY_ONLY",
        "source_files_verified": len(manifest["files"]),
        "source_bytes_verified": sum(v["bytes"] for v in manifest["files"]),
        "checks": checks, "check_count": len(checks),
        "projection_sha256": hashlib.sha256(projection_bytes).hexdigest(),
        "projection_bytes": len(projection_bytes),
        "CPU_seconds": process_time() - cpu0, "wall_seconds": perf_counter() - wall0,
        "scientific_evaluations": 0, "mass_conversions_evaluated": 0,
        "compiler_execution": 0, "old_tests_replayed": 0,
        "preserved_mechanical_failures": [{
            "action": "Initial large source write through shell heredoc",
            "result": "Process creation rejected: Argument list too long",
            "scientific_execution_started": False,
            "targeted_fix": "Write verified source content via apply_patch, then verify hashes.",
        }],
        "direct_NIST_HTTP_receipts": "NIST_HTTP_RECEIPTS.json",
        "remaining": ["Independent review", "Parent scoped physics validation", "Parent publication and backup"],
    }
    write_json("SOURCE_INTAKE_RESULT.json", receipt)
    print(json.dumps({"status": receipt["status"], "checks": len(checks),
                      "source_files": len(manifest["files"]),
                      "species": len(species), "providers": len(providers), "event_refs": len(events),
                      "mass_conversions": 0, "scientific_evaluations": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
