#!/usr/bin/env python3
"""Check the new reference overlay only; never import or replay old science."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OLD = BASE.parent / "provider_registry_network19_20261025"
RESULT = BASE / "raw/PRIMARY_RESULTS.json"


def read(relative):
    return json.loads((BASE / relative).read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RESULT.exists():
        raise SystemExit("Preserve completed primary result; no replay")
    groups = []
    outputs = {p.name: json.loads(p.read_bytes()) for p in sorted((BASE / "registry").glob("*.json"))}
    packet = read("sources/exfor/PROVIDER_ROWS.json")
    original = json.loads((OLD / "registry/targets.json").read_bytes())
    resolved = outputs["targets.json"]
    overlay = outputs["target6_overlay.json"]
    expected_ids = ["EXFOR_M0011002", "EXFOR_M0475002", "EXFOR_M0475003", "EXFOR_M0826002"]

    def group(name, function):
        try:
            detail = function()
            groups.append({"group": name, "status": "PASS", "detail": detail})
        except Exception as error:
            groups.append({"group": name, "status": "FAIL", "error": repr(error)})

    def dependencies():
        locks = outputs["inputs.json"]["files"]
        for row in locks:
            path = BASE / row["file"]
            assert sha(path) == row["sha256"] and path.stat().st_size == row["bytes"], row["file"]
        manifest = read("sources/exfor/MANIFEST.json")
        for row in manifest["files"]:
            path = BASE / "sources/exfor" / row["file"]
            assert sha(path) == row["sha256"] and path.stat().st_size == row["bytes"], row["file"]
        return {"dependency_files": len(locks), "packet_members": len(manifest["files"]), "operation": "byte identity, no scientific rerun"}

    def exact_scope():
        before, after = copy.deepcopy(original["rows"]), copy.deepcopy(resolved["rows"])
        assert [r["id"] for r in before] == [r["id"] for r in after]
        target6 = next(t for t in after if t["id"] == 6)
        direction = next(d for d in target6["directions"] if d["id"] == "TARGET19:06:target_forward")
        assert direction == overlay["after"]
        assert overlay["changed_keys"] == sorted(["primary_provider_refs", "has_primary_source_record_reference", "supplier_status", "experimental_table_provider_refs", "source_reaction_identity_matches_target"])
        old_direction = next(d for t in before if t["id"] == 6 for d in t["directions"] if d["id"] == "TARGET19:06:target_forward")
        assert old_direction == overlay["before"]
        target6["directions"][target6["directions"].index(direction)] = copy.deepcopy(old_direction)
        assert before == after
        for key in original:
            if key != "unit_id" and key != "rows":
                assert resolved[key] == original[key], key
        return {"targets": 19, "directions": 28, "modified_direction": "TARGET19:06:target_forward", "modified_source_metadata_keys": 5}

    def physical_gates():
        count = 0
        for target in resolved["rows"]:
            for direction in target["directions"]:
                for key in ["activation", "physical_Q_admission", "physical_rate_admission", "state_branch_domain_admission", "inverse_rate_generated", "factorized_source_product_evaluated"]:
                    assert direction[key] is False, (direction["id"], key)
                for key in ["physical_Q", "branch_fraction", "selected_rate_provider"]:
                    assert direction[key] is None, (direction["id"], key)
                count += 1
        assert overlay["new_physical_admission"] is False
        return {"directions_preserving_false_or_null_physical_fields": count}

    def references():
        assert [r["id"] for r in packet["rows"]] == expected_ids
        assert overlay["after"]["primary_provider_refs"] == expected_ids
        assert overlay["after"]["experimental_table_provider_refs"] == expected_ids
        assert overlay["after"]["exclusive_native_channel_source_refs"] == []
        catalog = outputs["provider_catalog.json"]
        assert [r["id"] for r in catalog["R3_provider_index"]] == expected_ids
        for item in catalog["provider_packets"]:
            assert sha(BASE / item["file"]) == item["sha256"]
        assert catalog["new_species_identities"] == 0 and catalog["new_active_provider_selection"] is None
        return {"new_source_refs_resolve": 4, "previous_packets_retained": 2, "exclusive_native_class_unchanged": True}

    def observable_partition():
        p = {row["id"]: row for row in packet["rows"]}
        assert p["EXFOR_M0475002"]["raw_values"]["row_count"] == 12
        assert p["EXFOR_M0475002"]["units"]["DATA-CM"] == "NB/SR"
        assert p["EXFOR_M0475002"]["observable_kind"] == "ANGULAR_DIFFERENTIAL_CROSS_SECTION_CM"
        assert p["EXFOR_M0826002"]["support"]["native_energy_bin_edges_retained"] is True
        assert p["EXFOR_M0826002"]["support"]["energy_integral_sigma_dE"] is False
        assert sum(r["raw_values"]["row_count"] for r in packet["rows"]) == 36
        aux = read("sources/exfor/AUXILIARY_ROWS.json")
        assert aux["counted_in_36_rows"] is False and aux["rows"][0]["raw_values"]["row_count"] == 7
        assert aux["rows"][0]["branch"]["source_component"] == "E2"
        assert len(read("sources/exfor/EXCLUDED_ROWS.json")["rows"]) == 3
        return {"main_SIG": 24, "main_DA": 12, "auxiliary_E2": 7, "CURVE_subentries_excluded_from_main": 3}

    def uncertainty_state():
        for row in packet["rows"]:
            u = row["uncertainty"]
            assert u["statistical_column"] == "ERR-S"
            assert u["covariance"] is None and u["combined_uncertainty"] is None and u["confidence_probability"] is None
            assert row["normalization"]["new_factor_of_two_or_factorial_applied"] is False
            assert row["normalization"]["new_angular_integration_performed"] is False
            assert row["state_resolution"]["source_native_state_bound_to_bare_projection"] is False
            assert row["Q"]["value"] is None and row["Q"]["admitted"] is False
            b = u["beam_intensity_systematic_bound"]
            if row["id"] == "EXFOR_M0826002":
                assert b["upper_bound_literal"] == "5." and b["relation"] == "not higher than" and not b["combined_with_statistical_error"]
            else:
                assert b is None
        return "Statistical literals, one beam-systematic bound and unbound state/covariance preserved"

    def saved_column():
        old = json.loads((OLD / "registry/compiled.json").read_bytes())
        saved = next(r for r in old["rows"] if r["event_id"] == "TARGET19_PHOTONUCLEAR:06")
        reuse = outputs["reused_target6_event.json"]
        assert reuse["saved_row"] == saved
        assert reuse["source_sha256"] == sha(OLD / "registry/compiled.json")
        assert reuse["new_compiler_invocations"] == 0
        assert saved["energy_status"] == "UNQUALIFIED:ENERGY" and saved["Q_approved"] is False
        module = ast.parse((BASE / "build_exfor_target6.py").read_text())
        imports = {node.module for node in ast.walk(module) if isinstance(node, ast.ImportFrom)}
        imports |= {alias.name for node in ast.walk(module) if isinstance(node, ast.Import) for alias in node.names}
        assert imports == {"__future__", "copy", "hashlib", "json", "pathlib"}
        return {"saved_event_id": saved["event_id"], "compiler_imports_or_calls": 0, "old_checks_replayed": 0}

    def bounded_coverage():
        c = outputs["coverage.json"]
        assert (c["original_target_count"], c["target_direction_count"], c["directions_with_any_primary_source_record_reference"]) == (19, 28, 28)
        assert c["target_directions_without_primary_source_record_reference"] == []
        assert c["new_actual_source_variants"] == 4 and c["new_native_numeric_rows"] == 36
        old = json.loads((OLD / "registry/coverage.json").read_bytes())["direct_photonuclear_source_coverage"]
        assert c["direct_photonuclear_source_coverage"]["exclusive_source_binding_gaps"] == old["exclusive_source_binding_gaps"]
        for key in ["new_compiled_projection_count", "actual_rate_evaluations", "actual_Q_evaluations", "new_IVPs", "physical_rate_admissions", "physical_Q_admissions", "consumer_admissions"]:
            assert c[key] == 0, key
        assert c["all_target_physical_source_coverage"] is False and c["global_physical_completion"] is None
        assert (c["HH_R10"], c["production"], c["L4_ready"]) == ("OFF", "NOT_ISSUED", False)
        return "28/28 source-reference availability; five photo source bindings and all physical gates unchanged"

    for name, test in [("frozen_dependency_bytes", dependencies), ("exact_additive_scope", exact_scope),
                       ("unchanged_physical_gates", physical_gates), ("provider_reference_resolution", references),
                       ("native_observable_partition", observable_partition), ("uncertainty_and_state_boundaries", uncertainty_state),
                       ("saved_event_without_compiler_replay", saved_column), ("bounded_coverage_claim", bounded_coverage)]:
        group(name, test)
    result = {"schema": "WU_R3_TARGETED_PRIMARY_V1", "groups": groups,
              "passed_groups": sum(r["status"] == "PASS" for r in groups),
              "failed_groups": sum(r["status"] == "FAIL" for r in groups),
              "checker_sha256": sha(Path(__file__)),
              "reviewed_output_sha256": {str(p.relative_to(BASE)): sha(p) for p in sorted((BASE / "registry").glob("*.json"))},
              "scope": "New EXFOR reference overlay; no old scientific suite or numerical physics evaluation"}
    with RESULT.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(1 if result["failed_groups"] else 0)


if __name__ == "__main__":
    main()
