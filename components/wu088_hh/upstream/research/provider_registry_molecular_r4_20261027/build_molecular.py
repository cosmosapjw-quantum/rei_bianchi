"""Build only the six changed-source columns and 29 published-formula samples."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import molecular_operator as mo

BASE = Path(__file__).resolve().parent
ADAPTER = BASE.parent / "provider_registry_20261025/registry_adapter.py"
ADAPTER_SHA256 = "9a093eed42f9ff5858d7bae11c726988ddbde4feeed38888b1c90fe329be816c"


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def serial(obj):
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serial(x) for x in obj]
    return obj


def write_new(name, obj):
    dest = BASE / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x") as f:
        json.dump(serial(obj), f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    existing = sorted(str(p.relative_to(BASE)) for p in (BASE / "registry").rglob("*") if p.is_file())
    if existing:
        raise ValueError("EXISTING_OUTPUT_REUSE_COMPLETE_OR_REVIEW_PARTIAL_NO_RECOMPUTE:" + ",".join(existing))
    packet = mo.load_packet()
    if hashlib.sha256(ADAPTER.read_bytes()).hexdigest() != ADAPTER_SHA256:
        raise ValueError("FROZEN_ADAPTER_CHANGED")
    spec = importlib.util.spec_from_file_location("r4_frozen_adapter", ADAPTER)
    adapter = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = adapter
    spec.loader.exec_module(adapter)
    species, families = {}, {}
    comp = {"Li": [(3, 7, 1)], "H": [(1, 1, 1)], "LiH": [(1, 1, 1), (3, 7, 1)],
            "H2": [(1, 1, 2)], "D+": [(1, 2, 1)], "HD": [(1, 1, 1), (1, 2, 1)], "H+": [(1, 1, 1)]}

    def sp(family, state):
        q = 1 if family in ("D+", "H+") else 0
        record = {"composition": [{"Z": z, "A": a, "isomer": "ground", "count": n} for z, a, n in comp[family]],
                  "charge": q, "state": state, "pool": "material"}
        sid = "sp_" + digest(record)[:20]
        species[sid] = {"id": sid, "compiler_record": record, "material_family": family,
                        "qualification": ["DECLARED_H1_D2_LI7_GROUND_NUCLEAR_INTEGER_MODEL", "SOURCE_ISOTOPE_AND_STATE_QUALIFICATION_RETAINED_PER_EVENT"],
                        "source_mass_or_state_transfer_admitted": False}
        families[sid] = family
        return sid

    # Source ensembles have separate state identities; they are not co-evolved.
    li_ra, h_ra, lih_ra = sp("Li", "Bennett_Li_2s"), sp("H", "Bennett_H_1s"), sp("LiH", "Bennett_X1Sigma_bound_quasibound_survival_aggregate")
    lih_b, h_b, li_b = sp("LiH", "Bovino_ground_PES_initial_v_j_UNSPECIFIED"), sp("H", "Bovino_atomic_state_UNSPECIFIED"), sp("Li", "Bovino_product_atomic_state_UNSPECIFIED")
    h2o, h2p = sp("H2", "Bovino_ortho_products_vj_SUM"), sp("H2", "Bovino_para_products_vj_SUM")
    dp, hp = sp("D+", "bare_nucleus"), sp("H+", "bare_nucleus")
    h2_hs, hd_hs = sp("H2", "Honvault_para_v0_j0"), sp("HD", "Honvault_product_vj_UNRESOLVED_SUM")
    hd_gl, h2_gl = sp("HD", "GL2022_v0_j0to8_Boltzmann_at_kinetic_T"), sp("H2", "GL2022_v0_j0to9_source_spin_weighted_SUM")
    sides = {
        mo.RA: ([li_ra, h_ra], [lih_ra], "radiative_association", "survival_weighted_total", [["gamma:escaping", 1]]),
        mo.ORTHO: ([lih_b, h_b], [li_b, h2o], "neutral_exchange", "source_product_ortho_normalization_UNBOUND", []),
        mo.PARA: ([lih_b, h_b], [li_b, h2p], "neutral_exchange", "source_product_para_normalization_UNBOUND", []),
        mo.TIQM: ([dp, h2_hs], [hd_hs, hp], "ion_exchange_HD_formation", "source_product_sum", []),
        mo.SQM: ([dp, h2_hs], [hd_hs, hp], "ion_exchange_HD_formation", "source_product_sum", []),
        mo.HD: ([hp, hd_gl], [dp, h2_gl], "ion_exchange_HD_destruction", "source_spin_weighted_product_sum", [])}
    events, compiled, projected = [], [], []
    for row in packet["rows"]:
        left, right, process, branch, photons = sides[row["id"]]
        event = {"id": row["id"], "source_id": row["id"], "source_identity": digest(row),
                 "branch_id": branch, "activation": False, "empirical_rate_admitted": False, "nuclear_Q_admitted": False,
                 "reactants": [[s, 1] for s in left], "products": [[s, 1] for s in right], "kind": "chemical",
                 "domain": "SOURCE_NATIVE_SUPPORT_AND_EXPLICIT_STATE_ENSEMBLE; CONSUMER_UNBOUND",
                 "frame": "source_thermal_collision_convention; consumer_frame_UNBOUND", "process": process,
                 "state_resolution": "SOURCE_LABELLED_ENSEMBLES_NOT_RESOLVED_POPULATION_CLOSURE",
                 "ownership_slot": "one_physical_event_per_process_state_branch",
                 "external_reactants": [], "external_products": photons,
                 "primary_emission_count": 1 if photons else 0,
                 "total_cascade_photon_yield": None,
                 "escaped_photon_yield": None,
                 "escaped_photon_energy": None,
                 "external_label_qualification": "legacy gamma:escaping is external particle bookkeeping, not a photon transport or escape fraction admission" if photons else "no primary photon declared",
                 "radiation_count_qualification": "ONE_PRIMARY_ASSOCIATION_TRANSITION; TOTAL_CASCADE_PHOTON_YIELD_UNBOUND" if photons else "NO_PRIMARY_RADIATIVE_EVENT_DECLARED",
                 "projection_qualification": "DECLARED_ISOTOPE_INTEGER_MODEL; SOURCE_STATE_ISOTOPE_TRANSFER_NOT_ADMITTED",
                 "native_Q_record": row["Q"], "native_uncertainty_record": row["uncertainty"],
                 "source_isotopic_qualification": row["isotopic_qualification"], "consumer_ACK": None}
        result = adapter.compile_event(event, species)
        result["energy"] = None  # The unchanged adapter already asserted this.
        result["source_formula_samples_separate"] = row["id"] in (mo.RA, mo.HD)
        result["native_rate_evaluated_field_scope"] = "finite event operator binding only; offline source formula samples are separately typed in fit_diagnostics.json"
        # Exactly one compiler invocation per new variant; saved parent columns reused.
        proj = {}
        for sid, count in result["stoichiometry"].items():
            family = families[sid]
            proj[family] = proj.get(family, 0) + count
        result["material_family_projection"] = {k: v for k, v in proj.items() if v}
        result["thermal_material_particle_delta"] = sum(result["stoichiometry"].values())
        events.append(event)
        compiled.append(result)
        projected.append({"event_id": event["id"], "material_projection": result["material_family_projection"],
                          "Delta_Ng": result["thermal_material_particle_delta"], "physical_rate_binding": False})
    diagnostics = []
    for provider in packet["rows"]:
        if provider["id"] not in (mo.RA, mo.HD):
            continue
        for native in provider["native_rows"]:
            sample = mo.evaluate_source_fit(provider["id"], native["T"])
            table = mo.native_value(native)
            diagnostics.append({**sample, "native_row_id": native["row_id"], "native_T_literal": native["T"],
                                "native_k_exact": str(table), "native_k_float": float(table),
                                "signed_relative_residual": (sample["k_cm3_s"] - float(table)) / float(table),
                                "residual_is_physical_uncertainty": False})
    summaries = []
    for pid in (mo.RA, mo.HD):
        rows = [d for d in diagnostics if d["provider_id"] == pid]
        worst = max(rows, key=lambda v: abs(v["signed_relative_residual"]))
        summaries.append({"provider_id": pid, "nodes": len(rows), "max_abs_relative_residual": abs(worst["signed_relative_residual"]),
                          "worst_T_K": worst["native_T_literal"], "original_source_uncertainty": mo.source_index(packet)[pid]["uncertainty"]})
    examples = {"class": "EXACT_RATIONAL_THEORY_EXAMPLES_NOT_SOURCE_RATES",
                "sharp_bound": mo.destruction_defect(["1", "0"], ["1/2", "1/2"], ["1", "3"], "1"),
                "same_total_other_state": mo.destruction_defect(["0", "1"], ["1/2", "1/2"], ["1", "3"], "1"),
                "constant_coefficients": mo.destruction_defect(["3/4", "1/4"], ["1/2", "1/2"], ["2", "2"], "1"),
                "zero_collider": mo.destruction_defect(["1", "0"], ["1/2", "1/2"], ["1", "3"], "0")}
    write_new("registry/species.json", {"rows": species, "co_evolution": "NOT_ADMITTED; overlapping ensembles require partition map"})
    write_new("registry/events.json", {"rows": events})
    write_new("registry/compiled.json", {"compiler_sha256": adapter.COMPILER_SHA256, "adapter_sha256": ADAPTER_SHA256,
                                        "new_compiler_calls": 6, "old_compiler_checks_replayed": 0, "rows": compiled})
    write_new("registry/projections.json", {"rows": projected, "coarse_projection_only": True})
    write_new("registry/fit_diagnostics.json", {"scope": "29_SOURCE_FORMULA_SAMPLES_ONLY", "new_primary_formula_samples": len(diagnostics),
                                               "rows": diagnostics, "summary": summaries})
    write_new("registry/lift_examples.json", examples)
    old_catalog = BASE.parent / "provider_registry_exfor_target6_20261027/registry/provider_catalog.json"
    write_new("registry/provider_overlay.json", {"parent_catalog": "../provider_registry_exfor_target6_20261027/registry/provider_catalog.json",
            "path_base": "R4 leaf root, not registry subdirectory",
            "parent_catalog_sha256": hashlib.sha256(old_catalog.read_bytes()).hexdigest(),
            "new_packet": "sources/MOLECULAR_SOURCE_PACKET.json", "new_packet_sha256": mo.PACKET_SHA256,
            "new_variants": [r["id"] for r in packet["rows"]], "new_native_rate_cells": 77,
            "new_number_columns": 6, "saved_number_columns_reused": 149,
            "original_target_IDs_preserved": 19, "original_direction_source_references_preserved": 28,
            "physical_global_completeness": None, "new_active_providers": 0})
    outputs = sorted((BASE / "registry").glob("*.json"))
    write_new("registry/COMPLETE.json", {"state": "COMPLETE_SCOPED_SOURCE_BUILD",
              "source_packet_sha256": mo.PACKET_SHA256, "new_compiler_calls": 6,
              "new_primary_source_formula_samples": len(diagnostics),
              "members": [{"path": str(p.relative_to(BASE)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],
              "physical_rate_Q_consumer_admitted": False})
    print(json.dumps({"new_variants": 6, "native_rate_cells": 77, "new_columns": len(compiled),
                      "formula_samples": len(diagnostics), "summary": summaries, "old_science_replay": 0}))


if __name__ == "__main__":
    main()
