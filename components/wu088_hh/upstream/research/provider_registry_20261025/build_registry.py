"""Deterministic source-row assembly. No scientific rate/IVP execution."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import resource
import time

from registry_adapter import BASE, COMPILER_SHA256, compile_event, digest


def read_bytes(path):
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    return gzip.decompress(path.with_suffix(path.suffix + ".gz").read_bytes())


def read_json(path):
    return json.loads(read_bytes(path))


def write_json(path, data):
    value = (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != value:
            raise ValueError("OUTPUT_DIFFERS_USE_NEW_ATTEMPT_DIRECTORY:" + str(path))
        return "reused_unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    return "created"


def assemble():
    atomic = read_json(BASE / "sources/atomic_nuclear/provider_rows.json")
    targets = read_json(BASE / "sources/atomic_nuclear/configured_targets.json")
    correction = read_json(BASE / "sources/atomic_nuclear_correction/CORRECTION_V1.json")
    umist = read_json(BASE / "sources/molecular/umist_light_provider_rows.json")
    lih = read_json(BASE / "sources/molecular/lih_photoprocess_provider.json")
    hd = read_json(BASE / "sources/molecular/hd_provider_rows.json")
    cold = read_json(BASE / "sources/atomic_nuclear/reused_cold_kinematic_rows.json")
    catalogue = read_json(BASE / "sources/atomic_nuclear/nuclear_catalogue_manifest.json")
    voronov = read_json(BASE / "sources/voronov1997/SELECTED_ROWS.json")
    species, providers, events = {}, {}, []
    # The legacy target list is an input view, not a periodic-table ceiling.
    # A new configured nuclide must supply its own numeric and isomer identity.
    nuclides, isomers = {}, {}
    for target in targets["species"]:
        n, identity = target["nuclide"], (target["Z"], target["A"])
        if n in nuclides and (nuclides[n] != identity or isomers[n] != target["isomer"]):
            raise ValueError("AMBIGUOUS_CONFIGURED_NUCLIDE_ALIAS:" + n)
        nuclides[n], isomers[n] = identity, target["isomer"]

    def add_species(comp, q, state, pool="material", qualification="SOURCE_EXPLICIT", origin=None):
        comp = [{"Z": nuclides[n][0], "A": nuclides[n][1], "isomer": isomers[n], "count": k}
                for n, k in sorted(comp.items())]
        rec = {"composition": comp, "charge": q, "state": state, "pool": pool}
        sid = "sp_" + digest(rec)[:20]
        row = species.setdefault(sid, {"id": sid, "compiler_record": rec,
                                      "qualification": [], "source_labels": [], "views": []})
        if qualification not in row["qualification"]:
            row["qualification"].append(qualification)
        if origin and origin not in row["source_labels"]:
            row["source_labels"].append(origin)
        return sid

    def atom(label):
        if label.startswith("e:"):
            fast = label in ("e:beta", "e:fast")
            state = "source_pool_unresolved" if label == "e:umist" else "free_electron"
            return add_species({}, -1, state, "electron_fast" if fast else "electron_thermal",
                               "NUMBER_CARRIER_PROJECTION_POOL_UNBOUND" if label == "e:umist"
                               else "EXPLICIT_ELECTRON_POOL", label)
        terms = label.split(":")
        nuc, q = terms[0], int(terms[1])
        state = terms[2] if len(terms) > 2 else "population_aggregate_unresolved"
        if q == nuclides[nuc][0]:
            state = "bare_nucleus"
        elif state in ("ground", "neutral_ground", "1s"):
            state = "1s_ground" if nuc in ("H1", "D", "T") and q == 0 else "electronic_ground"
        elif state == "2p":
            state = "2p_LS_aggregate"
        return add_species({nuc: 1}, q, state, origin=label)

    baseline = []
    for target in targets["species"]:
        sid = atom(target["label"])
        species[sid]["views"].append("historical_21_population")
        baseline.append({"label": target["label"], "species_id": sid,
                         "source": target["source"]})
    atom("e:thermal")
    atom("e:fast")

    def source(pid, row, payload_ref):
        if pid in providers:
            raise ValueError("DUPLICATE_PROVIDER_ID:" + pid)
        providers[pid] = {"id": pid, "record_sha256": digest(row), "payload_ref": payload_ref,
                          "native_record": row, "new_empirical_rate_admission": False,
                          "new_nuclear_Q_admission": False}

    def make_event(eid, pid, reactants, products, *, process, kind="chemical", branch="as_supplied",
                   domain="SOURCE_NATIVE_DOMAIN_ONLY", state="SOURCE_NATIVE_STATE_RESOLUTION",
                   projection="SOURCE_PARTICIPANT_PROJECTION", frame="SOURCE_FRAME_OR_CONSUMER_UNBOUND",
                   external_in=(), external_out=(), radiation="UNRESOLVED_TOTAL_PHOTON_COUNT",
                   native_rate=None, Q=None, uncertainty=None, obligations=()):
        events.append({"id": eid, "source_id": pid, "source_identity": providers[pid]["record_sha256"],
                       "reactants": sorted(reactants.items()), "products": sorted(products.items()),
                       "external_reactants": sorted(external_in), "external_products": sorted(external_out),
                       "process": process, "kind": kind, "branch_id": branch,
                       "domain": domain, "frame": frame, "state_resolution": state,
                       "projection_qualification": projection,
                       "ownership_slot": "one_physical_event_per_process_state_branch",
                       "radiation_count_qualification": radiation,
                       "native_rate_record": native_rate, "native_Q_record": Q,
                       "source_uncertainty": uncertainty,
                       "remaining_obligations": list(obligations),
                       "activation": False, "empirical_rate_admitted": False, "nuclear_Q_admitted": False,
                       "rate_normalization_bound": False, "consumer_ACK": None})

    # All original provider variants, plus the independently discovered HeI a/b fix.
    for row in atomic["rows"]:
        if row["id"] == "VF96_RR_Z2_N2":
            continue
        source(row["id"], row, {"file": "sources/atomic_nuclear/provider_rows.json", "container": "rows", "match": {"id": row["id"]}})
    for row in correction["corrected_source_rows"]:
        source(row["id"], row, {"file": "sources/atomic_nuclear_correction/CORRECTION_V1.json", "container": "corrected_source_rows", "match": {"id": row["id"]}})
    aliases = {"VF96_RR_Z2_N2": "VF96_RR_Z2_N2_fit_b"}
    for row in voronov["rows"]:
        source(row["id"], row, {"file": "sources/voronov1997/SELECTED_ROWS.json", "container": "rows", "match": {"id": row["id"]}})

    # Raw electronic coefficients are reused by named isotope-blind model views.
    # They are NOT separate isotope-resolved measurements.
    for pid, entry in list(providers.items()):
        row = entry["native_record"]
        if not pid.startswith("VF96_"):
            continue
        for nuc, (z, _a) in nuclides.items():
            if z != row["Z"]:
                continue
            q = row["charge_lower"]
            if row["process"] == "PI":
                left = {atom(f"{nuc}:{q}:ground"): 1}
                right = {atom(f"{nuc}:{q+1}:residual_manifold_unresolved"): 1, atom("e:fast"): 1}
                extin = [("gamma:incident", 1)]
                extout = []
                rad = "ONE_ABSORBED_PHOTON_PER_DIRECT_PI_EVENT"
                resolution = "ground_initial; residual_ion_manifold_unresolved"
            else:
                left = {atom(f"{nuc}:{q+1}:parent_ion_unresolved"): 1, atom("e:thermal"): 1}
                right = {atom(f"{nuc}:{q}:Case_A_all_bound_levels"): 1}
                extin, extout = [], []
                rad = "PRIMARY_CAPTURE_ONE; CASCADE_AND_TOTAL_ESCAPE_UNRESOLVED"
                resolution = "total_Case_A_capture; final_bound_states_and_cascades_unresolved"
            make_event(pid + ":" + nuc, pid, left, right, process=row["process"],
                       branch="source_ground_PI" if row["process"] == "PI" else "Case_A_total_capture",
                       domain="native_electronic_fit_no_isotope_shift", state=resolution,
                       projection="EXPLICIT_ISOTOPE_BLIND_MODEL_REFERENCE; SOURCE_ISOTOPE_NOT_QUALIFIED",
                       external_in=extin, external_out=extout, radiation=rad,
                       native_rate={"coefficients": row["coefficients"], "units": row["coefficient_units"],
                                    "temperature_domain": row.get("temperature_fit_domain_K"),
                                    "fit_rms_percent": row.get("fit_residual_rms_percent")},
                       uncertainty={"parameter_covariance": None, "status": "NOT_SUPPLIED; fit_rms_not_physical_covariance"},
                       obligations=["isotope-specific source/transfer", "consumer distribution and normalization",
                                    "final-state energy and radiation branch ownership"])

    # Exact source-supplied atomic, radiative, nuclear and weak rows.
    for pid, entry in list(providers.items()):
        if pid.startswith(("VF96_", "V97_")):
            continue
        row = entry["native_record"]
        left, right, extin, extout = {}, {}, [], []
        for side, output, ext in ((row["reactants"], left, extin), (row["products"], right, extout)):
            for label, number in side.items():
                if label.startswith(("gamma:", "antinu_e:", "nu_e:")):
                    ext.append((label, number))
                else:
                    key = atom(label)
                    output[key] = output.get(key, 0) + number
        process = row["process"]
        kind = "nuclear" if process in ("weak_beta_minus", "nuclear_capture") else "chemical"
        branch = ("beta_minus" if process == "weak_beta_minus" else
                  "2s_M1" if "M1" in pid else "2s_two_photon" if "two_photon" in pid else process)
        radiation = ("SOURCE_SPECIFIED_LINE_PHOTON_MULTIPLICITY" if process == "radiative_decay" else
                     "NATIVE_NUCLEAR_PRODUCT_YIELD; ENERGY_UNBOUND" if process == "nuclear_capture" else
                     "NO_RADIATION_MULTIPLICITY_ASSIGNED")
        make_event(pid, pid, left, right, process=process, kind=kind, branch=branch,
                   domain=("evaluated_ground_state_beta_minus" if process == "weak_beta_minus"
                           else "source_native_finite_support_and_state"),
                   state=row.get("electronic_state_transfer", row.get("branch", "source_explicit_state_labels")),
                   projection=row.get("stoichiometry_qualification", "SOURCE_PARTICIPANTS_WITH_DECLARED_MATERIAL_STATES"),
                   frame=row.get("frame", "source_scalar_rest_frame_or_unbound"),
                   external_in=extin, external_out=extout, radiation=radiation,
                   native_rate={k: row[k] for k in ("rate_literal", "rate_unit", "half_life_literal", "half_life_unit",
                                "support_eV", "source_support_eV", "nominal_knots", "branch_fraction_literal") if k in row},
                   Q={k: row[k] for k in ("chemical_defect_eV", "native_gap_eV", "native_Q_eV", "Q_keV_literal",
                       "Q_convention", "atomic_to_bare_map") if k in row} or None,
                   uncertainty={k: row[k] for k in row if "uncertainty" in k or k == "covariance_status"},
                   obligations=["physical event energy and source-domain binding", "named thermal/fast/radiation consumer"])

    # A separately sourced direct-CI fit supplies every configured electronic
    # rung as a source candidate. No isotope transfer, evaluation, or replacement
    # of the three previously admitted finite CCC operators is performed.
    for row in voronov["rows"]:
        pid = row["id"]
        for nuc, (z, _a) in nuclides.items():
            if z != row["Z"]:
                continue
            q = row["charge_lower"]
            make_event(pid + ":" + nuc, pid,
                       {atom(f"{nuc}:{q}:ground"): 1, atom("e:thermal"): 1},
                       {atom(f"{nuc}:{q+1}:residual_manifold_unresolved"): 1, atom("e:thermal"): 2},
                       process="CI_direct_fit", branch="direct_ionization_aggregate",
                       domain="native_electron_temperature_eV_keV_interval", state=row["state_qualification"],
                       projection="SOURCE_ELEMENTAL_FIT; EXPLICIT_ISOTOPE_BLIND_CANDIDATE",
                       native_rate={"coefficients": row["coefficients"], "units": row["coefficient_units"],
                                    "temperature_domain": row["native_temperature_domain"], "formula": row["formula"]},
                       Q={"fit_dE_eV": row["coefficients"]["dE"], "chemical_Q_admission": False},
                       uncertainty={"status": row["uncertainty_status"], "covariance": None},
                       obligations=["source/isotope and state admission", "native validity interval", "thermal event normalization",
                                    "chemical energy defect and emitted-electron energy partition"])

    # Previously computed three cold kinematic values are copied, not recomputed.
    capture_sides = {"np_d_gamma": ({"n:0": 1, "H1:1": 1}, {"D:1": 1}),
                     "nd_t_gamma": ({"n:0": 1, "D:1": 1}, {"T:1": 1}),
                     "pd_h_gamma": ({"H1:1": 1, "D:1": 1}, {"He3:2": 1})}
    for row in cold["rows"]:
        pid = "PHYS81_COLD_" + row["reaction"]
        source(pid, {"stored_result": row, "source": cold["source"], "uncertainty": cold["uncertainty_reason"]},
               {"file": "sources/atomic_nuclear/reused_cold_kinematic_rows.json", "container": "rows", "match": {"reaction": row["reaction"]}})
        a, b = capture_sides[row["reaction"]]
        make_event(pid, pid, {atom(n): k for n, k in a.items()}, {atom(n): k for n, k in b.items()},
                   process="nuclear_capture_kinematics", kind="nuclear", branch="ground_capture",
                   domain="cold_isolated_bare_nuclei_K0", frame="center_of_mass",
                   external_out=[("gamma:escaping", 1)], radiation="REUSED_COLD_TWO_BODY_SINGLE_PHOTON",
                   native_rate=None, Q={"Q_MeV": row["Q_MeV"], "status": "REUSED_ROUNDED_MASS_KINEMATICS"},
                   uncertainty={"covariance": None, "status": cold["uncertainty_reason"]},
                   obligations=["physical reaction rate", "joint source mass covariance", "consumer binding"])

    # Molecular source isotope labels are kept in native records. These explicit
    # constituent mappings are candidate model projections, not isotope admission.
    molecular_map = {
        "H": ({"H1": 1}, 0), "H+": ({"H1": 1}, 1), "H-": ({"H1": 1}, -1),
        "H2": ({"H1": 2}, 0), "H2+": ({"H1": 2}, 1), "H3+": ({"H1": 3}, 1),
        "He": ({"He4": 1}, 0), "He+": ({"He4": 1}, 1), "HeH+": ({"He4": 1, "H1": 1}, 1),
    }

    def molecular(label, state="source_electronic_rovibrational_unresolved"):
        if label == "e-":
            return atom("e:umist")
        comp, q = molecular_map[label]
        return add_species(comp, q, state, qualification="MODEL_ISOTOPE_MAPPING; NATIVE_ISOTOPE_UNSPECIFIED", origin=label)

    for row in umist["rows"]:
        pid = "UMIST22_" + row["provider_row_id"]
        source(pid, row, {"file": "sources/molecular/umist_light_provider_rows.json", "container": "rows", "match": {"provider_row_id": row["provider_row_id"]}})
        left, right, extin, extout = {}, {}, [], []
        for labels, output, ext in ((row["reactants_ordered"], left, extin), (row["products_ordered"], right, extout)):
            for label in labels:
                if label == "PHOTON":
                    continue  # network marker is retained in raw source, not promoted to total photon count
                if label in ("CRP", "CRPHOT"):
                    ext.append(("cosmic_ray_field" if label == "CRP" else "CR_induced_UV_field", 1))
                    continue
                key = molecular(label)
                output[key] = output.get(key, 0) + 1
        make_event(pid, pid, left, right, process="UMIST_" + row["reaction_type"],
                   branch="source_product_channel_as_supplied",
                   domain="UMIST_native_piecewise_temperature_and_radiation_conventions",
                   state=row["state_qualification"],
                   projection="EXPLICIT_H1_HE4_NUMBER_PROJECTION; ELECTRON_POOL_UNBOUND; NO_ISOTOPE_RATE_TRANSFER",
                   external_in=extin, external_out=extout,
                   native_rate={"unit": row["rate_unit"], "fits": row["fits_original_decimal_strings"],
                                "formula": row["formula"], "external_driver": row["external_driver"]},
                   uncertainty={"status": row["uncertainty_status"], "covariance": None,
                                "provider_codes": [f["accuracy_code"] for f in row["fits_original_decimal_strings"]]},
                   obligations=["source isotope and state mapping", "electron product pool ownership", "proper event flux conversion",
                                "environment and shielding domain", "Q and energy partition"])

    # LiH source gives elemental labels; both configured Li isotope projections
    # remain explicit alternatives. Neither is an isotope-specific cross section.
    lih_metadata = {k: v for k, v in lih.items() if k != "points"}
    source("LEIDEN_LiH_PD", lih_metadata, {"file": "sources/molecular/lih_photoprocess_provider.json", "container": None, "match": {}})
    for nuc in ("Li6", "Li7"):
        a = add_species({nuc: 1, "H1": 1}, 0, "source_electronic_rovibrational_unresolved",
                        qualification="CANDIDATE_ISOTOPOLOGUE; NATIVE_LI_H_ISOTOPES_UNSPECIFIED", origin=nuc + "H1")
        b = add_species({nuc: 1}, 0, "source_fragment_state_unresolved", origin=nuc)
        h = add_species({"H1": 1}, 0, "source_fragment_state_unresolved", origin="H1")
        make_event("LEIDEN_LiH_PD:" + nuc, "LEIDEN_LiH_PD", {a: 1}, {b: 1, h: 1},
                   process="photodissociation", branch="dominant_threshold_fragments_only",
                   domain="tabulated91.2_to351.1nm; summary579nm_not_extended",
                   projection="ISOTOPOLOGUE_CANDIDATE_ONLY; FRAGMENT_BRANCH_UNRESOLVED",
                   external_in=[("gamma:incident", 1)], radiation="ABSORBED_PHOTON; FRAGMENT_BRANCH_UNRESOLVED",
                   native_rate={"kind": "cross_section", "unit": "cm^2", "samples": lih["sample_count"],
                                "support_nm": lih["source_support_nm"]}, uncertainty=lih["uncertainty"],
                   obligations=["isotope and rovibronic source identity", "wavelength-dependent branching", "source table/summary discrepancy"])

    # HD supplied J labels are retained; no invented v or electronic assignment.
    hd_species = {}
    for row in hd["levels"]:
        hd_species[row["level_id"]] = add_species({"H1": 1, "D": 1}, 0,
                  "HD:J=" + row["J"] + ";v=UNRESOLVED;electronic=UNRESOLVED",
                  qualification="LAMDA_HD_SUPPLIED_J_ONLY", origin="LAMDA_HD_level_" + str(row["level_id"]))
    for row in hd["radiative_lines"]:
        pid = "LAMDA_HD_A_" + str(row["transition_id"])
        source(pid, {"row": row, "source_url": hd["source_url"], "source_sha256": hd["source_sha256"],
                     "uncertainty": hd["uncertainty"]}, {"file": "sources/molecular/hd_provider_rows.json", "container": "radiative_lines", "match": {"transition_id": row["transition_id"]}})
        make_event(pid, pid, {hd_species[row["upper_id"]]: 1}, {hd_species[row["lower_id"]]: 1},
                   process="molecular_radiative_transition", branch="supplied_transition_" + str(row["transition_id"]),
                   domain="source_HD_levels", state="suppliedJ;v_electronic_unresolved", external_out=[("gamma:escaping", 1)],
                   radiation="SOURCE_SPECIFIED_SINGLE_BOUND_BOUND_LINE",
                   native_rate={"A_s-1": row["A_s-1"], "nu_GHz": row["nu_GHz"]}, uncertainty=hd["uncertainty"],
                   obligations=["REC-owned spectral and state binding; no duplicate WU evaluator"])
    for row in hd["collisions"]:
        collider_state = {2: "para_H2", 3: "ortho_H2"}.get(row["collider_id"])
        if collider_state is None:
            raise ValueError("UNKNOWN_HD_COLLIDER")
        collider = molecular("H2", state=collider_state + ";source_state_as_tabulated")
        pid = "LAMDA_HD_C_" + str(row["collider_id"]) + "_" + str(row["transition_id"])
        source(pid, {"row": row, "source_url": hd["source_url"], "source_sha256": hd["source_sha256"],
                     "uncertainty": hd["uncertainty"]}, {"file": "sources/molecular/hd_provider_rows.json", "container": "collisions", "match": {"collider_id": row["collider_id"], "transition_id": row["transition_id"]}})
        make_event(pid, pid, {hd_species[row["upper_id"]]: 1, collider: 1},
                   {hd_species[row["lower_id"]]: 1, collider: 1}, process="molecular_collision_down",
                   branch="supplied_downward_pair", domain="T_nodes50_100_200K_only", state="suppliedJ_and_explicit_collider_spin",
                   native_rate={"T_K": row["T_nodes_K"], "q_cm3_s": row["q_cm3_s"]}, uncertainty=hd["uncertainty"],
                   obligations=["REC-owned finite domain adapter", "no upward rates or interpolation supplied here"])

    compiled = [compile_event(e, species) for e in events]
    cells = deepcopy(atomic["historical39_direction_coverage"])
    for cell in cells:
        if cell["provider_id"] in aliases:
            cell["provider_id"] = aliases[cell["provider_id"]]
        if cell["process"] == "RR":
            cell["products"].pop("gamma:escaping", None)
            cell["total_photon_count"] = None
            cell["radiation_status"] = "TOTAL_CASE_A_CASCADES_UNRESOLVED"
        cell["new_full_physical_admission"] = False
        if cell["process"] == "CI":
            z = nuclides[cell["nuclide"]][0]
            n = z - cell["charge_lower"]
            cell["additional_source_candidates"] = [f"V97_CI_Z{z}_N{n}"]
            cell["candidate_qualification"] = "UNEVALUATED_ELEMENTAL_FIT; ISOTOPE_BINDING_UNAPPROVED"
    gaps = [c["id"] for c in cells if c["provider_id"] is None]
    coverage = {
        "historical_population_count": len(baseline), "historical_direction_cells": cells,
        "historical_directions_with_source": len(cells) - len(gaps), "missing_CI_source_directions": gaps,
        "historical_directions_with_any_sourced_candidate": sum(bool(c["provider_id"] or c.get("additional_source_candidates")) for c in cells),
        "missing_any_sourced_candidate_directions": [c["id"] for c in cells if not(c["provider_id"] or c.get("additional_source_candidates"))],
        "missing_CI_source_directions_semantics": "inherited finite-source admissions only; new V97 candidates are separate",
        "additional_CI_source_variants": len(voronov["rows"]), "additional_CI_candidate_projections": 13,
        "provider_variant_count": len(providers), "compiled_projection_count": len(compiled),
        "source_catalogue": {k: catalogue[k] for k in ("catalogue_rows", "ground_rows", "non_ground_rows")},
        "nuclear_catalogue_is_active_network": False, "all_non_ground_are_isomers": False,
        "all_configured_network_reactions_known": False,
        "original_nuclear_network": "UNRESOLVED_INPUT_LOCATOR; see source NETWORK_LOCATOR_STATUS.json",
        "future_isotopologues_isomers_daughters": "EXTENSIBLE_NOT_ENUMERATED_AS_CONFIGURED",
        "molecular_chemistry_missing": ["source isotope-specific HD formation/destruction", "LiH formation and non-photo destruction",
                                        "D/T negative ions and other requested isotope transfers when configured"],
        "unqualified_physical_source_gaps": ["mass covariance", "nuclear atomic-to-bare mapping", "MT102 B1 source covenant",
                                            "source-state energy partitions", "named consumer bindings"],
        "active_new_rates": 0, "new_physical_Q_approvals": 0, "old_249_checks_replayed": 0,
        "HH_R10": "OFF", "production": "NOT_ISSUED", "L4_ready": False,
        "global_physical_completion": None,
    }
    return {"species": {"rows": species, "historical_view": baseline,
                        "source_native_isotope_metadata": "native records preserved separately from candidate compiler mappings",
                        "aggregation": "unresolved aggregate and resolved states must not be evolved together without a partition map"},
            "providers": {"rows": providers, "aliases": aliases}, "events": {"rows": events},
            "compiled": {"rows": compiled, "frozen_compiler_sha256": COMPILER_SHA256}, "coverage": coverage}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=BASE / "registry")
    args = parser.parse_args()
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_SELF)
    result = assemble()
    statuses = {k: write_json(args.output_dir / (k + ".json"), v) for k, v in result.items()}
    after = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"status": "COMPLETED_SOURCE_ASSEMBLY", "files": statuses,
          "species": len(result["species"]["rows"]), "provider_variants": len(result["providers"]["rows"]),
          "events": len(result["events"]["rows"]), "cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
          "wall_s": time.monotonic() - start, "max_RSS_KiB": after.ru_maxrss,
          "rate_evaluations": 0, "new_Q_calculations": 0, "IVPs": 0, "historical_suite_replays": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
