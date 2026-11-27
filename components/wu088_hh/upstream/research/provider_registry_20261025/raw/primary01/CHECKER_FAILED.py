#!/usr/bin/env python3
"""Primary bounded implementation validation for the source-only registry.

This checker reads frozen source packets and the completed registry. It invokes
only the immutable finite number compiler through registry_adapter; it does not
import the builder, evaluate a provider coefficient/Q, integrate, or replay the
historical 249 checks. Run once through verification/run_bounded.py. Output is
create-only so a failure cannot be silently replaced by a retry.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
FROZEN_COMPILER = "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def object_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode())


class Checks:
    def __init__(self, args):
        self.args = args
        self.results = []
        self.inputs = {}
        self.cache = {}

    def read_bytes(self, relative):
        path = BASE / relative
        if path.exists():
            data = path.read_bytes()
        else:
            path = Path(str(path) + ".gz")
            data = gzip.decompress(path.read_bytes())
        self.inputs[str(path.relative_to(BASE))] = sha(path.read_bytes())
        return data

    def read(self, relative):
        if relative not in self.cache:
            self.cache[relative] = json.loads(self.read_bytes(relative))
        return self.cache[relative]

    def run(self, name, function):
        try:
            detail = function()
            self.results.append({"id": name, "status": "PASS", "detail": detail})
        except Exception as error:
            self.results.append({"id": name, "status": "FAIL",
                                 "error_type": type(error).__name__,
                                 "error": str(error),
                                 "traceback": traceback.format_exc()})

    def initialize(self):
        sys.path.insert(0, str(BASE))
        import registry_adapter
        self.adapter = registry_adapter
        self.read_bytes("registry_adapter.py")
        self.read_bytes("verification/check_registry.py")
        self.species_doc = self.read("registry/species.json")
        self.providers_doc = self.read("registry/providers.json")
        self.events_doc = self.read("registry/events.json")
        self.compiled_doc = self.read("registry/compiled.json")
        self.coverage = self.read("registry/coverage.json")
        self.species = self.species_doc["rows"]
        self.providers = self.providers_doc["rows"]
        self.events = self.events_doc["rows"]
        self.compiled = self.compiled_doc["rows"]
        self.event_by_id = {row["id"]: row for row in self.events}
        self.compiled_by_id = {row["event_id"]: row for row in self.compiled}
        return {"registry_files": 5, "builder_imported": False}

    def storage_identity(self):
        counts = {}
        for index_path in sorted((BASE / "sources").glob("*/STORAGE_INDEX.json")):
            entries = self.read(str(index_path.relative_to(BASE)))
            seen = set()
            for row in entries:
                original, stored = row["original_relative_path"], row["stored_relative_path"]
                require(original not in seen, "duplicate storage entry: " + original)
                seen.add(original)
                target = (index_path.parent / stored).resolve()
                require(target.is_relative_to(index_path.parent.resolve()), "storage path escape")
                raw = target.read_bytes()
                require(sha(raw) == row["storage_sha256"], "stored SHA: " + str(target))
                # A source packet can already contain a .gz file. Decode only
                # a compression layer introduced by the storage projection.
                restored = gzip.decompress(raw) if stored != original else raw
                require(len(restored) == row["uncompressed_bytes"], "restored bytes: " + original)
                require(sha(restored) == row["sha256"], "restored SHA: " + original)
                self.inputs[str(target.relative_to(BASE))] = sha(raw)
            counts[index_path.parent.name] = len(entries)
        require({"atomic_nuclear", "molecular"} <= counts.keys(), "missing storage indexes")
        correction = self.read("sources/atomic_nuclear_correction/MANIFEST.json")
        for row in correction["files"]:
            raw = self.read_bytes("sources/atomic_nuclear_correction/" + row["path"])
            require(len(raw) == row["bytes"] and sha(raw) == row["sha256"],
                    "correction source identity: " + row["path"])
        receipts = self.read("sources/voronov1997/RETRIEVAL.json")
        for row in receipts:
            raw = self.read_bytes("sources/voronov1997/" + row["path"])
            require(row["status"] == 200 and len(raw) == row["bytes"]
                    and sha(raw) == row["sha256"], "Voronov retrieval identity")
        return {"indexed_files_by_packet": counts, "correction_files": len(correction["files"]),
                "Voronov_retrieval_files": len(receipts), "interpretation": "byte identity only"}

    def counts_and_species(self):
        require(len(self.providers) == self.args.expected_providers, "provider variant count")
        require(len(self.events) == self.args.expected_events, "event projection count")
        require(len(self.event_by_id) == len(self.events), "duplicate event id")
        require(len(self.compiled_by_id) == len(self.compiled) == len(self.events), "compiled identity count")
        require(set(self.event_by_id) == set(self.compiled_by_id), "compiled/event id mismatch")
        require(self.coverage["provider_variant_count"] == len(self.providers), "coverage provider count")
        require(self.coverage["compiled_projection_count"] == len(self.events), "coverage projection count")
        identities = set()
        for sid, row in self.species.items():
            require(sid == row["id"], "species id mismatch")
            record = row["compiler_record"]
            require(type(record["charge"]) is int and record["state"] and record["pool"], "species fields")
            identity = object_sha(record)
            require(identity not in identities, "duplicate species definition")
            identities.add(identity)
            for atom in record["composition"]:
                require(all(type(atom[k]) is int for k in ("Z", "A", "count")), "nucleus integers")
                require(atom["Z"] >= 0 and atom["A"] >= max(1, atom["Z"])
                        and atom["count"] > 0 and atom["isomer"], "nucleus definition")
        self.adapter.core.catalog({k: v["compiler_record"] for k, v in self.species.items()})
        return {"provider_variants": len(self.providers), "candidate_projections": len(self.events),
                "species_keys_observed": len(self.species), "counts_are_not_physical_results": True}

    def payload_selectors(self):
        resolved = []
        for pid, provider in self.providers.items():
            require(pid == provider["id"], "provider id mismatch")
            native = provider["native_record"]
            require(object_sha(native) == provider["record_sha256"], "provider digest: " + pid)
            ref = provider["payload_ref"]
            require(set(ref) == {"file", "container", "match"}, "payload selector schema: " + pid)
            path = (BASE / ref["file"]).resolve()
            require(path.is_relative_to(BASE / "sources"), "payload outside source packet")
            doc = self.read(ref["file"])
            rows = [doc] if ref["container"] is None else doc[ref["container"]]
            require(isinstance(rows, list) and isinstance(ref["match"], dict), "payload container: " + pid)
            matches = [row for row in rows if all(key in row and row[key] == value
                       for key, value in ref["match"].items())]
            require(len(matches) == 1, "payload must resolve uniquely: " + pid)
            selected = matches[0]
            if pid.startswith("LAMDA_HD_"):
                require(native["row"] == selected and native["source_sha256"] == doc["source_sha256"],
                        "HD payload wrapper: " + pid)
            elif pid.startswith("PHYS81_COLD_"):
                require(native["stored_result"] == selected and native["source"] == doc["source"],
                        "cold stored-result wrapper: " + pid)
            elif pid == "LEIDEN_LiH_PD":
                require(native == {k: v for k, v in selected.items() if k != "points"}, "LiH metadata wrapper")
                require(len(selected["points"]) == native["sample_count"] == 1562, "LiH raw points")
            else:
                require(native == selected, "source payload differs from native row: " + pid)
            resolved.append({"provider": pid, "payload_sha256": object_sha(selected)})
        return {"unique_provider_payloads": len(resolved), "selector_results_sha256": object_sha(resolved)}

    def all_number_ledgers(self):
        require(sha(self.adapter.COMPILER.read_bytes()) == FROZEN_COMPILER, "immutable compiler SHA")
        require(self.compiled_doc["frozen_compiler_sha256"] == FROZEN_COMPILER, "compiled source SHA")
        external = {"gamma:incident": (0, 0, 0), "gamma:escaping": (0, 0, 0),
                    "antinu_e:escaping": (0, 0, -1), "nu_e:escaping": (0, 0, 1),
                    "cosmic_ray_field": (0, 0, 0), "CR_induced_UV_field": (0, 0, 0)}
        checked = []
        for event in self.events:
            eid = event["id"]
            require(event["source_id"] in self.providers, "unknown source: " + eid)
            require(event["source_identity"] == self.providers[event["source_id"]]["record_sha256"],
                    "event/provider identity: " + eid)
            sides = []
            for side in (event["reactants"], event["products"]):
                counts = Counter()
                for sid, n in side:
                    require(sid in self.species and type(n) is int and n > 0, "unknown or invalid participant: " + eid)
                    counts[sid] += n
                sides.append(counts)
            left, right = sides
            nu = {sid: right[sid] - left[sid] for sid in left.keys() | right.keys()
                  if right[sid] != left[sid]}
            isotope = Counter()
            baryon = charge = lepton = 0
            for sid, n in nu.items():
                record = self.species[sid]["compiler_record"]
                bound = sum(a["Z"] * a["count"] for a in record["composition"]) - record["charge"]
                lepton += n * bound
                charge += n * record["charge"]
                for atom in record["composition"]:
                    isotope[(atom["Z"], atom["A"], atom["isomer"])] += n * atom["count"]
                    baryon += n * atom["A"] * atom["count"]
            for sign, side in ((-1, event["external_reactants"]), (1, event["external_products"])):
                for name, n in side:
                    require(name in external and type(n) is int and n > 0, "external particle: " + eid)
                    a, q, l = external[name]
                    baryon += sign * n * a
                    charge += sign * n * q
                    lepton += sign * n * l
            require((baryon, charge, lepton) == (0, 0, 0), "independent number ledger: " + eid)
            if event["kind"] == "chemical":
                require(not any(isotope.values()), "chemical isotope ledger: " + eid)
            stored = self.compiled_by_id[eid]
            require(stored["stoichiometry"] == nu, "number column: " + eid)
            require(stored["isotope_delta"] == {str(k): v for k, v in isotope.items()}, "isotope column: " + eid)
            require(stored == self.adapter.compile_event(event, self.species), "stored/core compilation mismatch: " + eid)
            checked.append(eid)
        return {"exact_integer_projections_checked": len(checked), "includes_frozen_core": True,
                "electron_lepton_ledger": "bound electrons + free electrons + external neutrinos",
                "physical_rate_or_Q_certificate": False}

    def expect_rejection(self, event, required_message):
        try:
            self.adapter.compile_event(event, self.species)
        except ValueError as error:
            require(required_message in str(error), "wrong rejection: " + str(error))
            return str(error)
        raise AssertionError("malformed event was accepted: " + required_message)

    def malformed_guards(self):
        base = self.event_by_id["VF96_PI_Z1_N1:H1"]
        rejected = {}
        bad = deepcopy(base)
        bad["products"].append(["unknown_species_key", 1])
        rejected["unknown_species"] = self.expect_rejection(bad, "UNKNOWN_SPECIES")
        bad = deepcopy(base)
        bad["products"] = [[s, n] for s, n in bad["products"]
                           if self.species[s]["compiler_record"]["composition"]]
        rejected["missing_electron"] = self.expect_rejection(bad, "CHARGE_NOT_CONSERVED")
        bad = deepcopy(self.event_by_id["LiveChart_ENSDF_n_beta_minus"])
        bad["external_products"] = []
        rejected["missing_antineutrino"] = self.expect_rejection(bad, "ELECTRON_LEPTON_NUMBER_NOT_CONSERVED")
        for field, value, message in (("branch_id", "", "EXPLICIT_BRANCH_ID_REQUIRED"),
                ("source_identity", "", "SOURCE_IDENTITY_REQUIRED"),
                ("activation", True, "SOURCE_INGESTION_CANNOT_ACTIVATE_PROVIDER"),
                ("empirical_rate_admitted", True, "SOURCE_INGESTION_CANNOT_ISSUE_PHYSICAL_ADMISSION"),
                ("nuclear_Q_admitted", True, "SOURCE_INGESTION_CANNOT_ISSUE_PHYSICAL_ADMISSION")):
            bad = deepcopy(base)
            bad[field] = value
            rejected[field] = self.expect_rejection(bad, message)
        for count in (-1, 0, True, "1"):
            bad = deepcopy(base)
            bad["external_reactants"] = [["gamma:incident", count]]
            rejected["external_count_" + repr(count)] = self.expect_rejection(bad, "INVALID_EXTERNAL_MULTIPLICITY")
        bad = deepcopy(base)
        bad["external_products"] = [["unknown_external", 1]]
        rejected["unknown_external"] = self.expect_rejection(bad, "UNSUPPORTED_EXTERNAL_PARTICLE")
        return rejected

    def canonical_external_and_branch(self):
        event = deepcopy(self.event_by_id["CHIANTI_A_2s_two_photon_per_s"])
        original = self.adapter.compile_event(event, self.species)
        event["external_products"] = [["gamma:escaping", 1], ["gamma:escaping", 1]]
        split = self.adapter.compile_event(event, self.species)
        for key in ("physical_event_key_sha256", "ownership_group_sha256"):
            require(original[key] == split[key], "external split representation changed identity")
        event["branch_id"] += "_distinct_branch"
        branch = self.adapter.compile_event(event, self.species)
        require(branch["physical_event_key_sha256"] != original["physical_event_key_sha256"], "branch omitted from identity")
        require(branch["ownership_group_sha256"] != original["ownership_group_sha256"], "branch omitted from ownership")
        return {"split_and_aggregate_identical": True, "distinct_branch_distinct_identity": True}

    def atomic_variants_and_helium(self):
        original = self.read("sources/atomic_nuclear/provider_rows.json")
        correction = self.read("sources/atomic_nuclear_correction/CORRECTION_V1.json")
        expected = {r["id"] for r in original["rows"]} - {"VF96_RR_Z2_N2"}
        expected |= {r["id"] for r in correction["corrected_source_rows"]}
        actual = {pid for pid, p in self.providers.items() if p["payload_ref"]["file"] in
                  ("sources/atomic_nuclear/provider_rows.json", "sources/atomic_nuclear_correction/CORRECTION_V1.json")}
        require(expected == actual and len(expected) == 29, "atomic source variants incomplete")
        require(correction["first_failure_preserved"] is True
                and correction["failure_class"] == "implementation extraction coverage failure", "extraction failure erased")
        require(self.providers_doc["aliases"]["VF96_RR_Z2_N2"] == "VF96_RR_Z2_N2_fit_b", "legacy HeI alias")
        for suffix, upper, rms, selected in (("a", "1000000", "2.5", False), ("b", "10000000000", "4.7", True)):
            row = self.providers["VF96_RR_Z2_N2_fit_" + suffix]["native_record"]
            require(row["temperature_fit_domain_K"] == {"lower": "3", "upper": upper,
                    "lower_inclusive": False, "upper_inclusive": False}, "HeI row-specific fit domain")
            require(row["fit_residual_rms_percent"] == rms and row["historical_PHYS78_selected"] is selected,
                    "HeI fit metadata")
            require("covariance" in row["fit_residual_qualification"], "fit residual qualification")
        pair = [deepcopy(self.event_by_id["VF96_RR_Z2_N2_fit_" + s + ":He4"]) for s in ("a", "b")]
        for event in pair:
            event["activation"] = True  # hypothetical choices only; never persisted
        try:
            self.adapter.verify_active_ownership(pair, self.compiled)
        except ValueError as error:
            require("OWNER_OVERLAP_UNRESOLVED" in str(error), "wrong HeI owner rejection")
        else:
            raise AssertionError("HeI alternative fits could jointly own the same event")
        pair[1]["activation"] = False
        require(len(self.adapter.verify_active_ownership(pair, self.compiled)) == 1, "single hypothetical owner rejected")
        return {"atomic_nuclear_source_variants": 29, "HeI_source_rows": 2, "historical_selection": "b",
                "joint_owner_rejected": True, "registry_mutated": False}

    def historical_coverage(self):
        historical = self.species_doc["historical_view"]
        require(len(historical) == 21 == self.coverage["historical_population_count"], "historical population")
        require(len({r["label"] for r in historical}) == 21, "historical labels duplicate")
        require(all(r["species_id"] in self.species for r in historical), "historical unknown species")
        cells = self.coverage["historical_direction_cells"]
        require(len(cells) == 39 and len({c["id"] for c in cells}) == 39, "historical direction cells")
        require(Counter(c["process"] for c in cells) == {"CI": 13, "PI": 13, "RR": 13}, "direction process coverage")
        missing = {c["id"] for c in cells if c["provider_id"] is None}
        expected = {"CI:D:0", "CI:T:0", "CI:He3:0", "CI:He3:1", "CI:He4:1",
                    "CI:Li6:0", "CI:Li6:1", "CI:Li6:2", "CI:Li7:1", "CI:Li7:2"}
        require(missing == expected == set(self.coverage["missing_CI_source_directions"]), "legacy missing CI cells")
        require(self.coverage["historical_directions_with_source"] == 29, "legacy source status changed")
        require(self.coverage["historical_directions_with_any_sourced_candidate"] == 39
                and self.coverage["missing_any_sourced_candidate_directions"] == [], "candidate source coverage")
        for cell in cells:
            require(cell["rate_value"] is None and cell["missing_is_not_zero"] is True
                    and cell["new_full_physical_admission"] is False, "physical cell promotion")
            if cell["process"] == "CI":
                refs = cell["additional_source_candidates"]
                require(len(refs) == 1 and refs[0] in self.providers and refs[0].startswith("V97_CI_"), "CI candidate reference")
                require("UNAPPROVED" in cell["candidate_qualification"], "CI isotope admission relabelled")
            if cell["id"] in expected:
                require(cell["status"] == "MISSING_PROVIDER_NULL", "legacy missing status overwritten")
        return {"population": 21, "direction_cells": 39, "legacy_source_cells": 29,
                "legacy_null_cells_with_new_inactive_candidates": 10}

    def recombination_radiation(self):
        rr_cells = [c for c in self.coverage["historical_direction_cells"] if c["process"] == "RR"]
        rr_events = [e for e in self.events if e["process"] == "RR"]
        require(len(rr_cells) == 13 and len(rr_events) == 15, "RR source/alternative projection count")
        for cell in rr_cells:
            require(cell["total_photon_count"] is None and "UNRESOLVED" in cell["radiation_status"], "RR total count asserted")
            require("gamma:escaping" not in cell["products"], "legacy primary photon mislabelled total")
        for event in rr_events:
            require(event["external_products"] == [] and "TOTAL_ESCAPE_UNRESOLVED" in event["radiation_count_qualification"],
                    "RR cascade multiplicity invented")
        return {"historical_RR_cells": 13, "candidate_RR_projections_with_alternatives": 15,
                "total_emitted_photon_multiplicity": None}

    def voronov_native_fields(self):
        source = self.read("sources/voronov1997/SELECTED_ROWS.json")
        raw = self.read_bytes("sources/voronov1997/cfit.dat")
        lines = raw.decode().splitlines()
        rows = source["rows"]
        require(source["source_total_rows"] == len(lines) == 406, "Voronov full source table")
        require(source["configured_elemental_rows"] == len(rows) == 6, "Voronov selected rows")
        require(len([e for e in self.events if e["source_id"].startswith("V97_CI_")]) == 13, "Voronov projection count")
        for row in rows:
            require(row["raw_row"] == lines[row["source_line1"] - 1], "Voronov raw row locator")
            require(sha(row["raw_row"].encode()) == row["raw_row_sha256_without_newline"], "Voronov row bytes")
            domain = row["native_temperature_domain"]
            require(domain["Tmin_unit"] == "eV" and domain["Tmax_unit"] == "keV", "native energy/temperature units changed")
            require(row["coefficient_units"]["A"] == "cm^3 s^-1" and row["coefficient_units"]["dE"] == "eV", "CI coefficient units")
            require(row["physical_admission"] is False and row["dE_is_approved_chemical_Q"] is False
                    and row["new_rate_evaluations"] == 0 and row["parameter_covariance"] is None, "CI source promoted")
            require(row["source_Fortran"]["T_input_unit"] == "K"
                    and "not measured physical zero" in row["source_Fortran"]["cutoff_qualification"], "Fortran convention lost")
        return {"source_rows": 406, "configured_elemental_fit_rows": 6, "candidate_isotope_projections": 13,
                "fit_evaluation": False, "temperature_limit_units": ["eV", "keV"]}

    def umist_native_gap(self):
        native = self.providers["UMIST22_74"]["native_record"]
        fits = native["fits_original_decimal_strings"]
        intervals = [(r["Tmin_K"], r["Tmax_K"]) for r in fits]
        require(intervals == [("10", "100"), ("101", "3000")], "native intervals changed")
        contains = self.adapter.within_native_intervals
        require(contains("100", intervals) and not contains("100.5", intervals)
                and contains("101", intervals), "UMIST interval gap bridged")
        rows = [p["native_record"] for pid, p in self.providers.items() if pid.startswith("UMIST22_")]
        require(len(rows) == 37, "UMIST selected rows")
        for row in rows:
            require(sha(row["raw_row_utf8"].encode()) == row["raw_row_sha256"], "UMIST raw row identity")
            require(row["Q_value"] is None and row["gamma_is_Q"] is False
                    and row["rate_admission"] is False and row["temperature_extrapolation"] is False,
                    "UMIST fit/Q qualification")
            require("isotope substitutions are not supplied" in row["isotope_source_labels"], "UMIST source isotope relabelled")
        return {"native_rows": 37, "T_100_5_K_supported": False, "gap_filled_or_rate_evaluated": False}

    def multiplicity_and_colliders(self):
        native = self.providers["UMIST22_145"]["native_record"]
        require(native["reactants_ordered"] == ["H2", "H2"]
                and native["products_ordered"] == ["H2", "H", "H"], "source repeated participants")
        event = self.event_by_id["UMIST22_145"]
        left, right = dict(event["reactants"]), dict(event["products"])
        h2 = next(s for s in left if "H2" in self.species[s]["source_labels"])
        hydrogen = next(s for s in right if "H" in self.species[s]["source_labels"])
        require(left == {h2: 2} and right == {h2: 1, hydrogen: 2}, "repeated H/H2 count lost")
        require(self.compiled_by_id[event["id"]]["stoichiometry"] == {h2: -1, hydrogen: 2}, "H2 number column")
        stripped = deepcopy(event)
        stripped["reactants"] = [[h2, 1]]
        stripped["products"] = [[hydrogen, 2]]
        result = self.adapter.compile_event(stripped, self.species)
        require(result["stoichiometry"] == self.compiled_by_id[event["id"]]["stoichiometry"], "collider comparison setup")
        require(result["physical_event_key_sha256"] != self.compiled_by_id[event["id"]]["physical_event_key_sha256"],
                "collider erased from physical identity")
        require(result["ownership_group_sha256"] != self.compiled_by_id[event["id"]]["ownership_group_sha256"],
                "collider erased from ownership identity")
        neutralization = self.event_by_id["UMIST22_6353"]
        require(list(dict(neutralization["products"]).values()) == [2], "H- + H+ -> 2H multiplicity")
        return {"repeated_participants_retained": True, "common_collider_present_in_identity": True}

    def molecular_isotope_labels(self):
        row = self.providers["LEIDEN_LiH_PD"]["native_record"]
        require(row["isotope"]["H"] is None and row["isotope"]["Li"] is None and row["state"] is None,
                "LiH native isotope/state fabricated")
        require("NOT_SPECIFIED" in row["isotope"]["qualification"], "LiH isotope qualification")
        require(row["source_support_nm"] == ["91.2000000", "351.1000000"], "LiH tabulated support")
        require(row["source_discrepancy"]["summary_pd_threshold_nm"] == "579", "LiH source discrepancy hidden")
        projections = [e for e in self.events if e["source_id"] == "LEIDEN_LiH_PD"]
        require(len(projections) == 2 and all("ISOTOPE" in e["projection_qualification"] for e in projections), "LiH candidate mapping")
        return {"native_Li_isotope": None, "native_H_isotope": None, "candidate_projections": 2,
                "native_metadata_not_relabelled": True}

    def hd_separate_colliders(self):
        collisions = [e for e in self.events if e["id"].startswith("LAMDA_HD_C_")]
        require(len(collisions) == 18, "HD collision rows")
        collider_states = set()
        for event in collisions:
            left, right = dict(event["reactants"]), dict(event["products"])
            common = set(left) & set(right)
            require(len(common) == 1, "HD explicit catalyst missing")
            sid = next(iter(common))
            require(left[sid] == right[sid] == 1 and sid not in self.compiled_by_id[event["id"]]["stoichiometry"], "HD catalyst number ledger")
            collider_states.add(self.species[sid]["compiler_record"]["state"])
        require(collider_states == {"para_H2;source_state_as_tabulated", "ortho_H2;source_state_as_tabulated"}, "HD p/o colliders collapsed")
        p, o = (self.providers["LAMDA_HD_C_" + x + "_1"]["native_record"]["row"] for x in ("2", "3"))
        require(p["q_cm3_s"] == o["q_cm3_s"] == ["2.2e-11", "2.7e-11", "3.9e-11"], "HD source rates changed")
        require(p["T_nodes_K"] == o["T_nodes_K"] == ["50.0", "100.0", "200.0"], "HD nodes changed")
        pc, oc = (self.compiled_by_id["LAMDA_HD_C_" + x + "_1"] for x in ("2", "3"))
        require(pc["physical_event_key_sha256"] != oc["physical_event_key_sha256"]
                and pc["reversible_material_pair_sha256"] != oc["reversible_material_pair_sha256"], "HD source identities collapsed")
        return {"collision_rows": 18, "catalyst_states": sorted(collider_states), "equal_rate_literals_do_not_merge_events": True}

    def nuclear_catalogue_scope(self):
        manifest = self.read("sources/atomic_nuclear/nuclear_catalogue_manifest.json")
        compressed = self.read_bytes("sources/atomic_nuclear/nuclear_catalogue.jsonl.gz")
        rows = [json.loads(line) for line in gzip.decompress(compressed).splitlines() if line]
        selected = manifest["selected_configured_ground_rows"]
        require(len(rows) == manifest["catalogue_rows"] == 5843, "NUBASE catalogue count")
        require(sum(r["state_class"] == "ground" for r in rows) == manifest["ground_rows"] == 3558, "NUBASE ground count")
        require(manifest["non_ground_rows"] == 2285 and len(selected) == 8, "NUBASE configured/catalogue distinction")
        require({(r["Z"], r["A"]) for r in selected} == {(0, 1), (1, 1), (1, 2), (1, 3),
                (2, 3), (2, 4), (3, 6), (3, 7)}, "configured nuclide set")
        require(all(r in rows for r in selected), "configured NUBASE row missing from full catalogue")
        require(manifest["nuclide_catalogue_is_not_population_network"] is True
                and manifest["all_non_ground_are_isomers"] is False, "catalogue promoted to population")
        require(self.coverage["nuclear_catalogue_is_active_network"] is False
                and self.coverage["all_configured_network_reactions_known"] is False
                and "UNRESOLVED_INPUT_LOCATOR" in self.coverage["original_nuclear_network"], "network dependency hidden")
        return {"source_catalogue_rows": 5843, "configured_ground_nuclides": 8,
                "all_non_ground_are_isomers": False, "catalogue_is_active_network": False}

    def weak_charge_and_source_alternatives(self):
        for prefix in ("NUBASE2020", "LiveChart_ENSDF"):
            event = self.event_by_id[prefix + "_T_beta_minus"]
            parent = [self.species[s]["compiler_record"] for s, n in event["reactants"]]
            daughter = [self.species[s]["compiler_record"] for s, n in event["products"]
                        if self.species[s]["compiler_record"]["composition"]]
            require(len(parent) == len(daughter) == 1 and parent[0]["charge"] == 0 and daughter[0]["charge"] == 1,
                    "neutral tritium spectator electron lost")
            require("one_bound_electron" in daughter[0]["state"], "tritium daughter unresolved state lost")
            require(event["external_products"] == [["antinu_e:escaping", 1]], "beta lepton source")
        nubase = self.providers["NUBASE2020_n_beta_minus"]["native_record"]
        ensdf = self.providers["LiveChart_ENSDF_n_beta_minus"]["native_record"]
        require(nubase["half_life_literal"] == "609.8" and ensdf["half_life_literal"] == "613.9", "source alternatives conflated")
        require(ensdf["Q_keV_literal"] == "782.347" and "atomic ground-state" in ensdf["Q_convention"], "atomic Q source relabelled")
        return {"neutral_T_daughter_charge": 1, "neutron_half_life_literals_preserved_s": ["609.8", "613.9"],
                "alternative_selected_or_Q_converted": False}

    def endf_and_reused_cold_records(self):
        endf = self.providers["ENDF_B_VIII1_H1_MT102"]["native_record"]
        require(endf["nominal_knots"] == len(endf["raw_table"]) == 153
                and endf["nominal_cells"] == 152, "ENDF source knots")
        require(endf["native_Q_eV"] == "2.224648e+6" and endf["atomic_to_bare_map"] == "UNRESOLVED", "ENDF native Q mapping")
        require(endf["native_Q_physical_event_admission"] == "NOT_ISSUED", "ENDF Q admission")
        expected = {"np_d_gamma": "2.22456637", "nd_t_gamma": "6.25723026", "pd_h_gamma": "5.49342331"}
        for channel, value in expected.items():
            record = self.providers["PHYS81_COLD_" + channel]["native_record"]["stored_result"]
            require(record["Q_MeV"] == value and record["K_MeV"] == "0", "stored cold result changed")
        return {"ENDF_knots": 153, "stored_cold_rows_reused": 3, "Q_recomputed": False}

    def no_physical_activation(self):
        for pid, provider in self.providers.items():
            require(provider["new_empirical_rate_admission"] is False
                    and provider["new_nuclear_Q_admission"] is False, "provider activated: " + pid)
        for event in self.events:
            require(event["activation"] is False and event["empirical_rate_admitted"] is False
                    and event["nuclear_Q_admitted"] is False and event["rate_normalization_bound"] is False
                    and event["consumer_ACK"] is None and event["branch_id"], "event activated: " + event["id"])
        for record in self.compiled:
            require(record["energy_status"] == "UNQUALIFIED:ENERGY", "synthetic energy promotion")
            for field in ("Q_approved", "activation", "native_rate_evaluated", "rate_normalization_bound", "reverse_rate_inferred"):
                require(record[field] is False, "compiled physical promotion: " + field)
        c = self.coverage
        require(c["active_new_rates"] == c["new_physical_Q_approvals"] == c["old_249_checks_replayed"] == 0,
                "coverage physical activity")
        require(c["HH_R10"] == "OFF" and c["production"] == "NOT_ISSUED" and c["L4_ready"] is False
                and c["global_physical_completion"] is None, "scope ceiling changed")
        contract = self.read("CONTRACT.json")
        require(all(v == 0 for v in contract["original_budget"]["PHYS91"].values()), "inherited PHYS91 budget changed")
        require(contract["original_budget"]["global_remaining"] is None, "unknown global budget set to zero")
        return {"new_rate_evaluations": 0, "new_Q_evaluations": 0, "new_IVP": 0,
                "historical_249_replay": 0, "physical_admission_issued": False}

    def read_only_identity(self):
        for relative, initial_sha in self.inputs.items():
            require(sha((BASE / relative).read_bytes()) == initial_sha, "input changed during validation: " + relative)
        return {"input_files_unchanged": len(self.inputs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BASE / "raw/PRIMARY_RESULTS.json")
    parser.add_argument("--expected-providers", type=int, default=102)
    parser.add_argument("--expected-events", type=int, default=125)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else BASE / args.output
    if output.exists():
        parser.error("output already exists; preserve the prior attempt and use a new explicit path")
    checks = Checks(args)
    checks.run("initialize_frozen_inputs", checks.initialize)
    if checks.results[0]["status"] == "PASS":
        for name, function in (
            ("source_storage_raw_and_gzip_identity", checks.storage_identity),
            ("registry_counts_and_explicit_species", checks.counts_and_species),
            ("every_provider_payload_resolves_uniquely", checks.payload_selectors),
            ("all_events_independent_integer_ledgers_and_frozen_core", checks.all_number_ledgers),
            ("malformed_particles_branch_and_admission_fail_closed", checks.malformed_guards),
            ("external_canonical_identity_and_branch_separation", checks.canonical_external_and_branch),
            ("all_atomic_variants_and_HeI_alternative_ownership", checks.atomic_variants_and_helium),
            ("historical_21_39_and_new_CI_candidates", checks.historical_coverage),
            ("total_recombination_photon_count_unresolved", checks.recombination_radiation),
            ("Voronov_native_source_units_and_missing_uncertainty", checks.voronov_native_fields),
            ("UMIST_native_support_gap_and_source_fields", checks.umist_native_gap),
            ("multiplicity_and_common_collider_identity", checks.multiplicity_and_colliders),
            ("native_molecular_isotopes_not_fabricated", checks.molecular_isotope_labels),
            ("HD_para_ortho_catalysts_remain_distinct", checks.hd_separate_colliders),
            ("NUBASE_catalogue_not_configured_reaction_network", checks.nuclear_catalogue_scope),
            ("weak_bound_electron_and_source_alternatives", checks.weak_charge_and_source_alternatives),
            ("ENDF_native_knots_and_reused_cold_results", checks.endf_and_reused_cold_records),
            ("no_physical_activation_or_old_budget_transfer", checks.no_physical_activation),
            ("validation_inputs_unchanged", checks.read_only_identity),
        ):
            checks.run(name, function)
    failures = [r["id"] for r in checks.results if r["status"] != "PASS"]
    result = {
        "schema": "WU_PROVIDER_REGISTRY_PRIMARY_IMPLEMENTATION_CHECK_V1",
        "role": "PRIMARY; independent review is a separate receipt",
        "finished_UTC": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "checks": checks.results, "failed_check_ids": failures,
        "implementation_check_groups": len(checks.results),
        "input_storage_sha256": checks.inputs,
        "frozen_compiler_sha256": FROZEN_COMPILER,
        "scope": "source-byte integrity, provenance, finite integer projections and guards only",
        "counting_policy": "provider variants, candidate projections and validation groups are distinct; never sum as physical results",
        "new_scientific_rate_evaluations": 0, "new_physical_Q_evaluations": 0,
        "new_IVP": 0, "old_249_checks_replayed": 0,
        "physical_rate_or_nuclear_Q_admission": False,
        "automatic_retry": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "implementation_check_groups": len(checks.results),
                      "failed_check_ids": failures, "output": str(output)}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
