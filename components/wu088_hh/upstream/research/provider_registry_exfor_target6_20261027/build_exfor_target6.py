#!/usr/bin/env python3
"""Add the frozen EXFOR target-6 references; reuse every saved number column.

This is a create-only reference overlay. It imports no compiler, fits no values,
and evaluates no cross section, rate, Q, inverse reaction, or physical history.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
R2 = BASE.parent / "provider_registry_network19_20261025"
SOURCE = BASE / "sources/exfor"
UNIT = "WU_TARGET6_EXFOR_SOURCE_R3"
PACKET_SHA = "d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2"
MANIFEST_SHA = "a1c5d4009d0bfacc4edcb248a6878eef6cdafa9690b4ea0d0826dd5356052d06"
LOCKS = {
    "../provider_registry_network19_20261025/registry/targets.json": "3aea45c576e5c1f8720bd8ade5e41f21ed0171e1f20893c1208742a2d3925c04",
    "../provider_registry_network19_20261025/registry/coverage.json": "8c07c9523753f93f673acfda86a16538172f776d6c527fcc3e26a4fee9e637aa",
    "../provider_registry_network19_20261025/registry/compiled.json": "96136267eb7fffd2ccf448fb2537a2c34f529a1109186871a5cf5ead8aeb8150",
    "../provider_registry_network19_20261025/registry/primary_providers.json": "33bfaa56538fefc793cd03751a9dce2e4bc3c9ddb8fede0c774583058b66ded9",
    "../provider_registry_network19_20261025/registry/species.json": "c4e7e52b954934d6484fbe1e0fb3909fd4532a8c824b802328f34bcdab4ff0b8",
    "../provider_registry_network19_20261025/SCIENTIFIC_ADMISSION.json": "7e80b1d378503e06a029c60c468b5397b96034b9959a168b111e467ab5a38be2",
    "../provider_registry_20261025/registry/species.json": "a18052f6db432192e1e0d4c75f8f2d49c71f3a5eb7cac206e7bc445fec2e8f80",
    "../provider_registry_20261025/registry/providers.json": "23d5bee7323a083d23a8a811eb7312a35c0eb613381ce28a22a5f989b1077664",
    "../rei_chem_ledger_20261025/chem_ledger.py": "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af",
    "sources/exfor/PROVIDER_ROWS.json": PACKET_SHA,
    "sources/exfor/MANIFEST.json": MANIFEST_SHA,
}
EXPECTED_PROVIDERS = ["EXFOR_M0011002", "EXFOR_M0475002", "EXFOR_M0475003", "EXFOR_M0826002"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def read_json(path):
    return json.loads(path.read_bytes())


def main():
    inputs = []
    for relative, expected in LOCKS.items():
        data = (BASE / relative).read_bytes()
        require(digest(data) == expected, "DEPENDENCY_CHANGED:" + relative)
        inputs.append({"file": relative, "sha256": expected, "bytes": len(data), "action": "READ_ONLY_REUSE"})
    manifest = read_json(SOURCE / "MANIFEST.json")
    for row in manifest["files"]:
        data = (SOURCE / row["file"]).read_bytes()
        require(len(data) == row["bytes"] and digest(data) == row["sha256"], "PACKET_MEMBER_CHANGED:" + row["file"])
    packet = read_json(SOURCE / "PROVIDER_ROWS.json")
    providers = packet["rows"]
    require([p["id"] for p in providers] == EXPECTED_PROVIDERS, "PROVIDER_SET_CHANGED")
    require([p["raw_values"]["row_count"] for p in providers] == [14, 12, 6, 4], "NATIVE_ROW_COUNT_CHANGED")
    for row in providers:
        require(row["record_class"] == "PRIMARY_SOURCE_ROW" and row["target_ids"] == [6], "INVALID_PRIMARY_TARGET")
        require(row["target_directions"] == {"6": "target_forward"}, "WRONG_DIRECTION")
        require(row["source_reaction_identity_matches_target"] is True, "WRONG_REACTION")
        require(row["source_coverage"] == "EXCLUSIVE_CHANNEL_EXPERIMENTAL_TABLE", "UNEXPECTED_OBSERVABLE_CLASS")
        require(row["exclusive_channel_binding"] is False, "UNREVIEWED_CHANNEL_BINDING")
        require(not any(row[key] for key in ("new_rate_admission", "new_Q_admission", "default_active", "activation")), "PHYSICAL_ADMISSION_FORBIDDEN")

    original = read_json(R2 / "registry/targets.json")
    targets = copy.deepcopy(original)
    target = next(r for r in targets["rows"] if r["id"] == 6)
    direction = next(d for d in target["directions"] if d["id"] == "TARGET19:06:target_forward")
    require(direction["primary_provider_refs"] == [] and not direction["has_primary_source_record_reference"], "SOURCE_GAP_ALREADY_CHANGED")
    before = copy.deepcopy(direction)
    direction["primary_provider_refs"] = EXPECTED_PROVIDERS.copy()
    direction["has_primary_source_record_reference"] = True
    direction["supplier_status"] = "PRIMARY_EXPERIMENTAL_TABLE_REFERENCES_PRESENT_PHYSICAL_BINDING_OPEN"
    direction["experimental_table_provider_refs"] = EXPECTED_PROVIDERS.copy()
    direction["source_reaction_identity_matches_target"] = True
    targets["unit_id"] = UNIT
    targets["R2_targets_source"] = {"file": "../provider_registry_network19_20261025/registry/targets.json",
                                    "sha256": LOCKS["../provider_registry_network19_20261025/registry/targets.json"],
                                    "commit": "71019bb469c92d1ea665155ed98c472b362d6706"}
    targets["R3_change_scope"] = "Only target6 forward source-reference metadata; all prior rows and physical fields inherited"
    directions = [d for t in targets["rows"] for d in t["directions"]]
    require(len(targets["rows"]) == 19 and len(directions) == 28, "TARGET_IDENTITY_LOSS")
    missing = [d["id"] for d in directions if not d["has_primary_source_record_reference"]]
    require(missing == [], "UNEXPECTED_REMAINING_SOURCE_REFERENCE_GAP")

    compiled = read_json(R2 / "registry/compiled.json")
    saved = next(r for r in compiled["rows"] if r["event_id"] == "TARGET19_PHOTONUCLEAR:06")
    require(saved["number_operator_status"] == "EXACT_INTEGER_PROJECTION_CHECKED", "MISSING_SAVED_NUMBER_ACCEPTANCE")
    photo = copy.deepcopy(read_json(R2 / "registry/coverage.json")["direct_photonuclear_source_coverage"])
    photo["no_primary_source_record_reference"] = []
    photo["experimental_table_direction_count"] = 1
    photo["experimental_table_provider_variant_count"] = 4
    photo["experimental_table_native_numeric_row_count"] = 36
    photo["target6_exclusive_reaction_identity_present"] = True
    photo["target6_pointwise_event_rate_binding"] = False
    coverage = {
        "schema": "WU_TARGET6_EXFOR_COVERAGE_R3_V1", "unit_id": UNIT,
        "original_target_count": 19, "target_direction_count": 28,
        "directions_with_any_primary_source_record_reference": len(directions) - len(missing),
        "target_directions_without_primary_source_record_reference": missing,
        "target_directions_with_only_declaration": [],
        "new_actual_source_variants": 4, "new_native_numeric_rows": 36,
        "native_SIG_rows": 24, "native_DA_rows": 12,
        "auxiliary_E2_rows_not_in_main_count": 7,
        "direct_photonuclear_source_coverage": photo,
        "new_species_identities": 0, "new_compiled_projection_count": 0,
        "R1_saved_column_count": 125, "R2_saved_column_count": 24,
        "target6_saved_column_referenced": "TARGET19_PHOTONUCLEAR:06",
        "old_249_checks_replayed": 0, "R1_R2_science_replayed": 0,
        "actual_rate_evaluations": 0, "actual_Q_evaluations": 0, "new_IVPs": 0,
        "physical_rate_admissions": 0, "physical_Q_admissions": 0,
        "physical_state_branch_domain_admissions": 0, "consumer_admissions": 0,
        "all_target_physical_source_coverage": False,
        "all_future_configured_species_processes_complete": False,
        "new_source_availability_scope": "Original19 listed targets/28 directions only; no claim of every future isotope/state/molecular process",
        "HH_R10": "OFF", "production": "NOT_ISSUED", "L4_ready": False,
        "global_physical_completion": None,
    }
    index = [{"id": p["id"], "record_class": p["record_class"], "packet": "sources/exfor/PROVIDER_ROWS.json",
              "packet_sha256": PACKET_SHA, "row_locator": {"id": p["id"]},
              "native_numeric_rows": p["raw_values"]["row_count"], "observable_kind": p["observable_kind"],
              "native_units": p["units"], "source_url": p["source_url"],
              "source_reaction_identity_matches_target": True, "physical_binding": False} for p in providers]
    catalog = {
        "schema": "WU_COMPOSITE_PROVIDER_CATALOG_R3_V1", "path_base": "This R3 leaf",
        "provider_packets": [
            {"scope": "R1 actual source variants", "file": "../provider_registry_20261025/registry/providers.json", "variant_count": 102,
             "sha256": LOCKS["../provider_registry_20261025/registry/providers.json"]},
            {"scope": "R2 original target19 suppliers", "file": "../provider_registry_network19_20261025/registry/primary_providers.json", "variant_count": 26,
             "sha256": LOCKS["../provider_registry_network19_20261025/registry/primary_providers.json"]},
            {"scope": "R3 target6 direct EXFOR tables", "file": "sources/exfor/PROVIDER_ROWS.json", "variant_count": 4, "sha256": PACKET_SHA}],
        "R3_provider_index": index,
        "species_registry": {"file": "../provider_registry_20261025/registry/species.json", "identity_count": 92,
                             "sha256": LOCKS["../provider_registry_20261025/registry/species.json"]},
        "bare_projection_species": {"file": "../provider_registry_network19_20261025/registry/species.json", "reused_count": 9,
                                    "sha256": LOCKS["../provider_registry_network19_20261025/registry/species.json"]},
        "new_species_identities": 0, "new_active_provider_selection": None,
        "deduplication": "Source alternatives remain variants; no physical-channel, isotope, ionic, molecular or state merging",
        "primary_reference_does_not_admit_rate_Q_or_consumer": True,
    }
    outputs = {
        "registry/targets.json": targets,
        "registry/coverage.json": coverage,
        "registry/provider_catalog.json": catalog,
        "registry/target6_overlay.json": {
            "schema": "WU_TARGET6_EXFOR_ADDITIVE_PATCH_V1", "unit_id": UNIT,
            "base_targets": targets["R2_targets_source"], "target_id": 6,
            "direction_id": "TARGET19:06:target_forward", "before": before, "after": direction,
            "changed_keys": sorted(k for k in set(before) | set(direction) if before.get(k) != direction.get(k)),
            "new_physical_admission": False,
        },
        "registry/reused_target6_event.json": {
            "schema": "WU_TARGET6_SAVED_COLUMN_REFERENCE_V1",
            "source_file": "../provider_registry_network19_20261025/registry/compiled.json",
            "source_sha256": LOCKS["../provider_registry_network19_20261025/registry/compiled.json"],
            "source_commit": "71019bb469c92d1ea665155ed98c472b362d6706",
            "saved_row": saved, "new_compiler_invocations": 0,
            "new_source_rows_change_number_stoichiometry": False,
            "photon_absorption_per_event_if_bound": 1,
            "photon_energy_or_consumer_binding": False,
        },
        "registry/inputs.json": {"schema": "WU_TARGET6_R3_INPUT_LOCK_V1", "files": inputs,
                                 "packet_manifest": "sources/exfor/MANIFEST.json", "packet_manifest_sha256": MANIFEST_SHA},
    }
    payloads = {name: encoded(value) for name, value in outputs.items()}
    for name in payloads:
        require(not (BASE / name).exists(), "PRESERVE_PRIOR_OUTPUT:" + name)
    for name, data in payloads.items():
        with (BASE / name).open("xb") as handle:
            handle.write(data)
    print(json.dumps({"status": "BUILT_SOURCE_REFERENCE_OVERLAY", "unit_id": UNIT,
                      "source_references": "28/28", "new_source_variants": 4, "new_numeric_rows": 36,
                      "new_compiler_invocations": 0, "new_rate_Q_evaluations": 0,
                      "outputs": {name: digest(data) for name, data in payloads.items()}}))


if __name__ == "__main__":
    main()
