"""Independent audit of saved R4 outputs; never imports producer/compiler code.

The sole new transcendental calculation is Decimal80 evaluation of the 29
contracted source-formula nodes. Table- and fit-normalized residuals reuse those
same references. All outputs are exclusive-create. Run only via the bounded
runner after root authorizes S07.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import traceback

BASE = Path(__file__).resolve().parents[1]
RA = "BENNETT2003_LIH_SPONTANEOUS_RA_TABLE3"
ORTHO = "BOVINO2009_LIH_H_TO_LI_ORTHO_H2_TABLE1"
PARA = "BOVINO2009_LIH_H_TO_LI_PARA_H2_TABLE1"
TIQM = "HONVAULT2013_CORRECTED_HD_FORMATION_TIQM"
SQM = "HONVAULT2013_CORRECTED_HD_FORMATION_SQM"
HD = "GONZALEZ_LEZANA2022_HD_HPLUS_DESTRUCTION_THERMAL"
IDS = [RA, ORTHO, PARA, TIQM, SQM, HD]
COUNTS = [27, 14, 14, 10, 10, 2]
FORMULA_LIMIT = Decimal("2e-14")
RESIDUAL_ABS_LIMIT = Decimal("2e-14")

PINS = {
    "sources/MOLECULAR_SOURCE_PACKET.json": "40e2fbd73d451c0c8116b4ca9bd4db4d2e43e4cdf8967988a2fea551f99ce35e",
    "molecular_operator.py": "c11bd7240039050e0a817d698e9a82517770081e56828c7b48b4492ec98ee4c5",
    "build_molecular.py": "5ba9d17f1a6c68f8fec5ac50d256448a2c502cef9114ed1f1dcb0bf285f50ff0",
    "verification/run_bounded.py": "b362521e75319816498cc0e3dd9382891bfb771cf988a963dadad83d0e616bdc",
    "CONTRACT.json": "6a40c43c04aa4506281f2021a6879e76e94d560ea3cc8af3c7cdfeffb15eb8bc",
    "../provider_registry_20261025/registry_adapter.py": "9a093eed42f9ff5858d7bae11c726988ddbde4feeed38888b1c90fe329be816c",
    "../rei_chem_ledger_20261025/chem_ledger.py": "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af",
    "../provider_registry_20261025/SCIENTIFIC_ADMISSION.json": "54a1710cc7a5455172c957dd2618d09568f44bd959e9be756a3ea960ac3d27b1",
    "../provider_registry_network19_20261025/SCIENTIFIC_ADMISSION.json": "7e80b1d378503e06a029c60c468b5397b96034b9959a168b111e467ab5a38be2",
    "../provider_registry_exfor_target6_20261027/SCIENTIFIC_ADMISSION.json": "9a23a79f9e958cc68aa1d9366829ccd73a0782ca05ebc46127e3ec8d3f46d1cf",
    "../provider_registry_exfor_target6_20261027/registry/provider_catalog.json": "e39ce3db6b7facd30a48229047193329ae833838cb429e6d4437e33df87cc86b",
    "sources/public_sources/bennett2003_table3.json": "d17365b148212af17da48c0618581d27a050a5ed4209f2306db7b36e83c87835",
    "sources/public_sources/bovino2009_table1.json": "5f950aecbcf8a5bb9d4180b607dd567ca5eb8fa4654870590acedc2f19f14648",
    "sources/public_sources/honvault2013_corrected_table1.json": "c0f6b65193a71132b7815eda3f1f3cdf99472e7773b486e21ae4fd4ab623a7d7",
    "sources/public_sources/gonzalezlezana2022_native_fit_points.json": "6a370ba76d6079d3d6b702d267c5f62d9f250130cdf5115103fceee1b1e010a2",
    "raw/primary01/RECEIPT.json": "a951e5dba47aea89b76457d5aea1474112acff6fa15df307ff872d0994a1c15b",
    "registry/COMPLETE.json": "84f3810641d4ed93aeb53bc4d130f92388340e98839b8388032057c0ebdf5762",
}
PAYLOADS = {
    "registry/compiled.json": "1caf331cd91918b28f22e9f6d3af0860a155833c3fceee804cbb0dfd208f66d3",
    "registry/events.json": "2203fcdd7ece309a7b2f9d7587f24009985c88a9d34118ec690d616c28268514",
    "registry/fit_diagnostics.json": "5f687fac3c21dc8a9747c45ac6558a4b9d7c107577d6d9eb9285bc13a9c7f599",
    "registry/lift_examples.json": "21820ecd8cbf3cce44c7095e8dd129b69af86329ae278784ac9e7964d07a0371",
    "registry/projections.json": "2a525f742d7d6d0674b382ae3ec0a7bd8f84f12ddb786fba460091810879d3a1",
    "registry/provider_overlay.json": "66ced34b9fd1d820a8dbdab9372d6132068d8c12d076cc261d38c8c068a8f395",
    "registry/species.json": "82139048baed52754d7718d1371e4a6ec2f0ea996b53e4ba463a81db19c66afe",
}
FAMILY_ORDER = ["H", "H+", "D+", "Li", "H2", "HD", "LiH"]
EXPECTED_MATRIX = [
    [-1, -1, -1, 0, 0, 0],
    [0, 0, 0, 1, 1, -1],
    [0, 0, 0, -1, -1, 1],
    [-1, 1, 1, 0, 0, 0],
    [0, 1, 1, -1, -1, 1],
    [0, 0, 0, 1, 1, -1],
    [1, -1, -1, 0, 0, 0],
]
COMPOSITIONS = {
    "H": {(1, 1, "ground"): 1},
    "H+": {(1, 1, "ground"): 1},
    "D+": {(1, 2, "ground"): 1},
    "Li": {(3, 7, "ground"): 1},
    "H2": {(1, 1, "ground"): 2},
    "HD": {(1, 1, "ground"): 1, (1, 2, "ground"): 1},
    "LiH": {(1, 1, "ground"): 1, (3, 7, "ground"): 1},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((BASE / name).read_text())


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def exact_table(row):
    if "k" in row:
        return Fraction(row["k"])
    return Fraction(row["k_mantissa"]) * Fraction(row["k_scale"])


class Audit:
    def __init__(self):
        self.assertions = 0
        self.groups = []
        self.data = {}
        self.references = []
        self.reference_evaluations = 0

    def require(self, condition, label):
        self.assertions += 1
        if not condition:
            raise AssertionError(label)

    def group(self, name, function):
        before = self.assertions
        try:
            detail = function()
            result = {"id": name, "status": "PASS", "assertions": self.assertions - before,
                      "detail": detail}
        except Exception as exc:
            result = {"id": name, "status": "FAIL", "assertions": self.assertions - before,
                      "error_type": type(exc).__name__, "error": str(exc),
                      "traceback": traceback.format_exc()}
        self.groups.append(result)
        return result["status"] == "PASS"

    def identities(self):
        for name, expected in {**PINS, **PAYLOADS}.items():
            self.require(sha(BASE / name) == expected, "HASH:" + name)
        marker = read("registry/COMPLETE.json")
        self.require(marker["state"] == "COMPLETE_SCOPED_SOURCE_BUILD", "completion_state")
        members = marker["members"]
        self.require(len(members) == 7, "seven_payloads")
        self.require({r["path"]: r["sha256"] for r in members} == PAYLOADS, "member_identity")
        self.require(marker["new_compiler_calls"] == 6 and
                     marker["new_primary_source_formula_samples"] == 29, "bounded_counts")
        self.require(marker["source_packet_sha256"] == PINS["sources/MOLECULAR_SOURCE_PACKET.json"],
                     "completion_packet")
        self.require(marker["physical_rate_Q_consumer_admitted"] is False, "completion_scope")
        packet = read("sources/MOLECULAR_SOURCE_PACKET.json")
        self.require([r["id"] for r in packet["rows"]] == IDS, "six_provider_order")
        self.data["packet"] = packet
        self.data["sources"] = {r["id"]: r for r in packet["rows"]}
        for name in ("species", "events", "compiled", "projections", "fit_diagnostics",
                     "lift_examples", "provider_overlay"):
            self.data[name] = read("registry/" + name + ".json")
        overlay = self.data["provider_overlay"]
        self.require(overlay["parent_catalog"] ==
                     "../provider_registry_exfor_target6_20261027/registry/provider_catalog.json",
                     "parent_catalog_path")
        self.require(overlay["path_base"] == "R4 leaf root, not registry subdirectory",
                     "parent_catalog_path_base")
        self.require(sha(BASE / overlay["parent_catalog"]) == overlay["parent_catalog_sha256"],
                     "parent_catalog_hash")
        self.require(overlay["new_variants"] == IDS and overlay["new_native_rate_cells"] == 77,
                     "overlay_source_counts")
        self.require(overlay["new_number_columns"] == 6 and
                     overlay["saved_number_columns_reused"] == 149, "overlay_column_scope")
        self.require(overlay["original_target_IDs_preserved"] == 19 and
                     overlay["original_direction_source_references_preserved"] == 28,
                     "original_network_scope")
        self.require(overlay["new_active_providers"] == 0 and
                     overlay["physical_global_completeness"] is None, "overlay_no_activation")
        return {"pinned_files": len(PINS) + len(PAYLOADS), "completion_payloads": 7,
                "old_science_recalculated": 0}

    def source_cells(self):
        bindings = {
            RA: ("bennett2003_table3.json", None),
            ORTHO: ("bovino2009_table1.json", "ortho_k"),
            PARA: ("bovino2009_table1.json", "para_k"),
            TIQM: ("honvault2013_corrected_table1.json", "TIQM_k_mantissa"),
            SQM: ("honvault2013_corrected_table1.json", "SQM_k_mantissa"),
            HD: ("gonzalezlezana2022_native_fit_points.json", None),
        }
        count = 0
        for pid, expected_count in zip(IDS, COUNTS):
            source = self.data["sources"][pid]
            filename, column = bindings[pid]
            public = read("sources/public_sources/" + filename)
            native = source["native_rows"]
            self.require(len(native) == expected_count, "cell_count:" + pid)
            self.require([r["T"] for r in native] == [r["T"] for r in public["rows"]],
                         "T_literals:" + pid)
            self.require(len({r["T"] for r in native}) == len(native), "unique_T:" + pid)
            self.require(source["payload_ref"]["file"] == "public_sources/" + filename,
                         "payload_file:" + pid)
            self.require(source["payload_ref"].get("value_column") == column,
                         "payload_column:" + pid)
            self.require(source["source_kind"] == "PUBLISHED_THEORETICAL_COEFFICIENT",
                         "theoretical_source_kind:" + pid)
            for flag in ("new_rate_admission", "new_Q_admission", "runtime_activation"):
                self.require(source[flag] is False, flag + ":" + pid)
            for flag in ("consumer_binding", "coefficient_covariance", "confidence_distribution"):
                self.require(source[flag] is None, flag + ":" + pid)
            self.require(public["T_unit"] == "K", "native_T_unit")
            if pid in (TIQM, SQM):
                self.require(public["k_unit_as_printed"] == "cm^3 molecule^-1 s^-1",
                             "native_molecule_unit")
            else:
                self.require(public["k_unit"] == "cm^3 s^-1", "native_k_unit")
            for r, q in zip(native, public["rows"]):
                self.require(type(r["T"]) is str, "native_T_string")
                if pid == RA:
                    self.require(all(r[k] == q[k] for k in
                                     ("row_id", "T", "k_mantissa", "k_scale", "source_text_line_1based")),
                                 "Bennett_literal:" + r["row_id"])
                elif pid in (ORTHO, PARA):
                    spin = "ortho" if pid == ORTHO else "para"
                    self.require(r["k"] == q[column], "Bovino_k:" + r["row_id"])
                    self.require(r["native_k_notation"] == q["native_" + spin + "_notation"],
                                 "Bovino_notation:" + r["row_id"])
                    self.require(r["source_text_line_1based"] == q["source_text_line_1based"],
                                 "Bovino_locator")
                elif pid in (TIQM, SQM):
                    self.require(r["k_mantissa"] == q[column] and
                                 r["k_scale"] == q["k_scale"] == "1e-9", "Honvault_scale_cell")
                    self.require(r["source_locator"] == q["source_locator"], "Honvault_locator")
                else:
                    self.require(r == q, "GL22_native_row")
                self.require(exact_table(r) > 0, "positive_native_cell")
                count += 1
        self.require(count == 77, "exact_77_native_cells")
        self.require(self.data["sources"][ORTHO]["native_fit"]["unit_conflict"] is True and
                     self.data["sources"][PARA]["native_fit"]["unit_conflict"] is True,
                     "Bovino_unit_conflict_preserved")
        self.require(self.data["sources"][RA]["statistical_factor"]["already_in_source_coefficient"]
                     is True, "Bennett_factor_already_included")
        self.require(self.data["sources"][HD]["aggregation"]["weights_already_in_aggregate"]
                     is True, "HD_weights_already_included")
        return {"native_rate_cells_compared": count, "provider_variants": 6,
                "raw_paper_reextractions": 0}

    def ledgers(self):
        species = self.data["species"]["rows"]
        events = self.data["events"]["rows"]
        columns = {c["event_id"]: c for c in self.data["compiled"]["rows"]}
        projections = {c["event_id"]: c for c in self.data["projections"]["rows"]}
        self.require(len(species) == 14 and len(events) == 6 and len(columns) == 6,
                     "fourteen_identities_six_events")
        self.require([e["id"] for e in events] == IDS, "event_order")
        for sid, row in species.items():
            record = row["compiler_record"]
            family = row["material_family"]
            comp = {}
            for atom in record["composition"]:
                self.require(all(type(atom[k]) is int for k in ("Z", "A", "count")),
                             "integer_nuclear_model")
                comp[(atom["Z"], atom["A"], atom["isomer"])] = atom["count"]
            self.require(comp == COMPOSITIONS[family], "family_composition:" + sid)
            self.require(record["charge"] == (1 if family in ("H+", "D+") else 0),
                         "family_charge")
            self.require(record["pool"] == "material" and row["id"] == sid, "material_identity")
            self.require("DECLARED_H1_D2_LI7_GROUND_NUCLEAR_INTEGER_MODEL" in row["qualification"],
                         "declared_model_label")
            self.require(row["source_mass_or_state_transfer_admitted"] is False,
                         "no_mass_state_transfer")
        matrix_columns = []
        report = []
        for event in events:
            nu = Counter()
            for side, sign in (("reactants", -1), ("products", 1)):
                for sid, number in event[side]:
                    self.require(sid in species and type(number) is int and number == 1,
                                 "single_declared_event_multiplicity")
                    nu[sid] += sign * number
            nu = {sid: number for sid, number in nu.items() if number}
            iso = Counter()
            baryon = charge = lepton = 0
            family_nu = Counter()
            for sid, number in nu.items():
                record = species[sid]["compiler_record"]
                nuclear_charge = 0
                for atom in record["composition"]:
                    key = (atom["Z"], atom["A"], atom["isomer"])
                    iso[key] += number * atom["count"]
                    baryon += number * atom["A"] * atom["count"]
                    nuclear_charge += atom["Z"] * atom["count"]
                charge += number * record["charge"]
                lepton += number * (nuclear_charge - record["charge"])
                family_nu[species[sid]["material_family"]] += number
            family_nu = {key: value for key, value in family_nu.items() if value}
            col = columns[event["id"]]
            prj = projections[event["id"]]
            self.require(all(value == 0 for value in iso.values()) and
                         baryon == charge == lepton == 0, "independent_B_q_Le_isotopes")
            self.require(col["stoichiometry"] == nu, "stored_stoichiometry")
            self.require(col["baryon_delta"] == baryon and col["charge_delta"] == charge and
                         col["electron_lepton_delta"] == lepton, "stored_ledger")
            self.require(all(Fraction(str(v)) == 0 for v in col["isotope_delta"].values()),
                         "stored_isotope_delta")
            self.require(col["material_family_projection"] == family_nu and
                         prj["material_projection"] == family_nu, "coarse_family_projection")
            expected_delta = -1 if event["id"] == RA else 0
            self.require(sum(nu.values()) == col["thermal_material_particle_delta"] ==
                         prj["Delta_Ng"] == expected_delta, "material_particle_count")
            matrix_columns.append([family_nu.get(f, 0) for f in FAMILY_ORDER])
            report.append({"event_id": event["id"], "baryon": baryon, "charge": charge,
                           "electron_lepton": lepton, "delta_material_particles": expected_delta})
        matrix = [list(row) for row in zip(*matrix_columns)]
        self.require(matrix == EXPECTED_MATRIX, "independent_7_by_6_matrix")
        claims = read("theory/CLAIMS.json")["claims"]
        c1 = next(c for c in claims if c["id"] == "C01_MATERIAL_STOICHIOMETRY")
        self.require(c1["species_order"] == FAMILY_ORDER and c1["matrix"] == matrix,
                     "theory_matrix_matches_outputs")
        return {"new_columns_independently_checked": 6, "rows": report,
                "old_columns_recompiled": 0}

    def ownership_energy(self):
        sources = self.data["sources"]
        events = self.data["events"]["rows"]
        columns = {c["event_id"]: c for c in self.data["compiled"]["rows"]}
        species = self.data["species"]["rows"]

        def side_signature(side):
            rows = []
            for sid, n in side:
                s = species[sid]["compiler_record"]
                atoms = sorted((a["Z"], a["A"], a["isomer"], a["count"])
                               for a in s["composition"])
                rows.append((atoms, s["charge"], s["state"], s["pool"], n))
            return sorted(rows)

        semantic = {}
        for e in events:
            pid = e["id"]
            c = columns[pid]
            source = sources[pid]
            self.require(e["source_identity"] == canonical_hash(source) ==
                         c["provider_record_sha256"], "per_source_record_identity")
            for k, raw in (("native_Q_record", "Q"), ("native_uncertainty_record", "uncertainty"),
                           ("source_isotopic_qualification", "isotopic_qualification")):
                self.require(e[k] == source[raw], "event_native_record:" + k)
            for k in ("activation", "empirical_rate_admitted", "nuclear_Q_admitted"):
                self.require(e[k] is False, "event_admission:" + k)
            self.require(e["consumer_ACK"] is None, "consumer_unbound")
            self.require(e["primary_emission_count"] == (1 if pid == RA else 0),
                         "primary_photon_only")
            self.require(e["total_cascade_photon_yield"] is None and
                         e["escaped_photon_yield"] is None and e["escaped_photon_energy"] is None,
                         "cascade_transport_energy_unknown")
            self.require(e["external_products"] == ([["gamma:escaping", 1]] if pid == RA else []),
                         "declared_external_number")
            if pid == RA:
                self.require("bookkeeping" in e["external_label_qualification"] and
                             "not a photon transport" in e["external_label_qualification"],
                             "legacy_external_label_qualified")
            self.require(c["energy"] is None and c["energy_status"] == "UNQUALIFIED:ENERGY",
                         "unqualified_energy")
            for flag in ("Q_approved", "activation", "rate_normalization_bound",
                         "reverse_rate_inferred", "native_rate_evaluated"):
                self.require(c[flag] is False, "operator_flag:" + flag)
            self.require(c["source_formula_samples_separate"] is (pid in (RA, HD)),
                         "offline_formula_scope")
            semantic[pid] = json.dumps([side_signature(e["reactants"]),
                                       side_signature(e["products"]), e["process"], e["branch_id"],
                                       e["external_reactants"], e["external_products"]],
                                      sort_keys=True)
        for i, left in enumerate(IDS):
            for right in IDS[i + 1:]:
                self.require((semantic[left] == semantic[right]) ==
                             (columns[left]["ownership_group_sha256"] ==
                              columns[right]["ownership_group_sha256"]),
                             "semantic_ownership_partition")
        self.require(columns[TIQM]["ownership_group_sha256"] == columns[SQM]["ownership_group_sha256"],
                     "method_alternative_same_owner")
        self.require(columns[TIQM]["reversible_material_pair_sha256"] !=
                     columns[HD]["reversible_material_pair_sha256"], "HD_ensemble_reverse_not_inferred")
        self.require("NOT_ADMITTED" in self.data["species"]["co_evolution"], "no_coevolution")
        return {"ownership_groups": len({c["ownership_group_sha256"] for c in columns.values()}),
                "primary_RA_emission": 1, "total_cascade_yield": None,
                "physical_energy_rate_consumer_admission": False}

    def formula_reference(self):
        rows = self.data["fit_diagnostics"]["rows"]
        saved = {(r["provider_id"], r["native_row_id"]): r for r in rows}
        self.require(len(rows) == len(saved) == 29, "unique_29_fit_rows")
        p = self.data["sources"][RA]["native_fit"]["parameters"]
        self.require(p == {"offset": "3.22", "a": "0.0657", "b": "-2.45",
                           "c": "0.00631", "d": "0.837", "T_scale_K": "1000",
                           "k_scale": "1e-20"}, "reviewed_Bennett_raw_parameters")
        fit_hd = self.data["sources"][HD]["native_fit"]
        self.require(fit_hd["alpha"] == "8.57e-10" and fit_hd["gamma"] == "405",
                     "reviewed_HD_raw_parameters")
        reference_keys = set()
        with localcontext() as ctx:
            ctx.prec = 80
            for pid in (RA, HD):
                source = self.data["sources"][pid]
                for raw in source["native_rows"]:
                    key = (pid, raw["row_id"])
                    reference_keys.add(key)
                    row = saved[key]
                    T = Decimal(raw["T"])
                    self.reference_evaluations += 1
                    if pid == RA:
                        theta = T / Decimal(p["T_scale_K"])
                        log_theta = theta.ln()
                        first = Decimal(p["a"]) * (Decimal(p["b"]) * log_theta).exp()
                        second = Decimal(p["c"]) * (Decimal(p["d"]) * log_theta).exp()
                        reference = (Decimal(p["offset"]) + Decimal(1) / (first + second)) * Decimal(p["k_scale"])
                    else:
                        reference = Decimal(fit_hd["alpha"]) * (-Decimal(fit_hd["gamma"]) / T).exp()
                    self.require(type(row["k_cm3_s"]) is float, "saved_binary64_type")
                    actual = Decimal.from_float(row["k_cm3_s"])
                    self.require(actual.is_finite() and actual > 0 and reference > 0,
                                 "finite_positive_formula")
                    error = abs(actual - reference) / abs(reference)
                    self.require(error <= FORMULA_LIMIT, "Decimal80_formula_tolerance:" + raw["row_id"])
                    table_fraction = exact_table(raw)
                    table = Decimal(table_fraction.numerator) / Decimal(table_fraction.denominator)
                    self.require(row["native_T_literal"] == raw["T"] and
                                 Fraction(row["T_K"]) == Fraction(raw["T"]), "sample_T_binding")
                    self.require(Fraction(row["native_k_exact"]) == table_fraction,
                                 "exact_native_table_binding")
                    self.require(row["source_packet_sha256"] ==
                                 PINS["sources/MOLECULAR_SOURCE_PACKET.json"], "sample_source_hash")
                    self.require(row["status"] == "SOURCE_FORMULA_SAMPLE", "sample_status")
                    for flag in ("physical_rate_admitted", "state_distribution_bound", "Q_admitted",
                                 "residual_is_physical_uncertainty"):
                        self.require(row[flag] is False, "sample_scope:" + flag)
                    self.references.append({
                        "provider_id": pid, "row_id": raw["row_id"], "T_literal": raw["T"],
                        "k_table_exact": str(table_fraction), "k_table_decimal": str(table),
                        "k_binary64_exact_decimal": str(actual), "k_reference_decimal80": str(reference),
                        "relative_binary64_error": str(error),
                        "r_table_reference": str((reference - table) / table),
                        "r_fit_reference": str((reference - table) / reference),
                        "r_table_saved_binary64": str((actual - table) / table),
                        "r_fit_saved_binary64": str((actual - table) / actual),
                    })
        self.require(set(saved) == reference_keys and self.reference_evaluations == 29,
                     "no_extra_or_missing_reference_nodes")
        return {"reference_precision_digits": 80, "reference_formula_evaluations": 29,
                "max_relative_binary64_error": str(max(Decimal(r["relative_binary64_error"])
                                                     for r in self.references)),
                "limit": str(FORMULA_LIMIT), "rows": self.references,
                "producer_imports": 0, "producer_formula_replays": 0}

    def residuals(self):
        self.require(len(self.references) == 29, "references_available_without_reevaluation")
        saved = {(r["provider_id"], r["native_row_id"]): r
                 for r in self.data["fit_diagnostics"]["rows"]}
        summaries = {r["provider_id"]: r for r in self.data["fit_diagnostics"]["summary"]}
        output = []
        with localcontext() as ctx:
            ctx.prec = 80
            for pid in (RA, HD):
                subset = [r for r in self.references if r["provider_id"] == pid]
                for r in subset:
                    row = saved[(pid, r["row_id"])]
                    observed = Decimal.from_float(row["signed_relative_residual"])
                    expected = Decimal(r["r_table_saved_binary64"])
                    self.require(abs(observed - expected) <= RESIDUAL_ABS_LIMIT,
                                 "saved_signed_residual:" + r["row_id"])
                    self.require(Fraction.from_float(row["native_k_float"]) ==
                                 Fraction(float(Fraction(r["k_table_exact"]))),
                                 "native_table_float_representation")
                table_worst = max(subset, key=lambda r: abs(Decimal(r["r_table_reference"])))
                fit_worst = max(subset, key=lambda r: abs(Decimal(r["r_fit_reference"])))
                saved_worst = max(subset, key=lambda r: abs(Decimal(r["r_table_saved_binary64"])))
                summary = summaries[pid]
                self.require(summary["nodes"] == len(subset) and
                             summary["worst_T_K"] == saved_worst["T_literal"], "saved_summary_location")
                self.require(abs(Decimal.from_float(summary["max_abs_relative_residual"]) -
                                 abs(Decimal(saved_worst["r_table_saved_binary64"]))) <= RESIDUAL_ABS_LIMIT,
                             "saved_summary_value")
                self.require(summary["original_source_uncertainty"] ==
                             self.data["sources"][pid]["uncertainty"], "source_wording_preserved")
                output.append({
                    "provider_id": pid, "nodes": len(subset),
                    "table_normalization": "(k_fit-k_table)/k_table",
                    "fit_normalization": "(k_fit-k_table)/k_fit",
                    "max_abs_r_table_reference": str(abs(Decimal(table_worst["r_table_reference"]))),
                    "max_abs_r_table_T_literal": table_worst["T_literal"],
                    "max_abs_r_fit_reference": str(abs(Decimal(fit_worst["r_fit_reference"]))),
                    "max_abs_r_fit_T_literal": fit_worst["T_literal"],
                    "source_wording_is_acceptance_gate": False,
                })
        row500 = next(r for r in self.references if r["provider_id"] == RA and r["T_literal"] == "500.0")
        return {"summaries": output, "Bennett_500K": row500,
                "original_error_denominator": "UNSPECIFIED_IN_REVIEWED_SOURCE_PARAGRAPH",
                "paper_contradiction_inferred": False, "physical_uncertainty_inferred": False,
                "new_formula_evaluations_in_this_group": 0}

    def rational_examples(self):
        examples = self.data["lift_examples"]
        self.require(examples["class"] == "EXACT_RATIONAL_THEORY_EXAMPLES_NOT_SOURCE_RATES",
                     "examples_not_source_data")
        # Independently read the closed-form worked examples in theory section9.
        fields = ["total", "effective_k_for_declared_lift", "exact_flux", "lift_flux",
                  "defect", "half_spread_L1_bound"]
        expected = {
            "sharp_bound": ([1, 2, 1, 2, -1, 1], False),
            "same_total_other_state": ([1, 2, 3, 2, 1, 1], False),
            "constant_coefficients": ([1, 2, 2, 2, 0, 0], True),
            "zero_collider": ([1, 2, 0, 0, 0, 0], True),
        }
        for name, (values, uniform) in expected.items():
            example = examples[name]
            self.require([Fraction(example[k]) for k in fields] == list(map(Fraction, values)),
                         "exact_worked_example:" + name)
            self.require(example["uniform_scalar_closure"] is uniform and
                         example["physical_source_binding"] is False, "example_scope")
            self.require(Fraction(example["defect"]) ==
                         Fraction(example["exact_flux"]) - Fraction(example["lift_flux"]),
                         "defect_identity")
            self.require(abs(Fraction(example["defect"])) <= Fraction(example["half_spread_L1_bound"]),
                         "half_spread_bound")
        return {"stored_constructed_examples": 4, "source_population_inferred": False,
                "production_functions_called": 0}

    def receipts_and_controls(self):
        receipt = read("raw/primary01/RECEIPT.json")
        self.require(receipt["exit_code"] == 0 and receipt["child_spawned"] is True and
                     receipt["launch_error"] is None and receipt["timed_out"] is False,
                     "actual_primary_completion")
        self.require(receipt["command"] == ["python", "build_molecular.py"], "reviewed_command")
        self.require(receipt["code_sha256"]["build_molecular.py"] == PINS["build_molecular.py"] and
                     receipt["code_sha256"]["molecular_operator.py"] == PINS["molecular_operator.py"],
                     "executed_code_identity")
        for key, expected in (("cpu_cap_s", 30), ("wall_cap_s", 120), ("memory_MiB", 512),
                              ("workers", 1), ("threads", 1)):
            self.require(receipt[key] == expected, "resource_contract:" + key)
        self.require(0 <= receipt["cpu_s"] <= 30 and 0 <= receipt["wall_s"] <= 120,
                     "actual_primary_within_caps")
        for name in ("stdout", "stderr"):
            self.require(sha(BASE / ("raw/primary01/" + name + ".txt")) ==
                         receipt[name + "_sha256"], "actual_" + name + "_hash")
        stdout = json.loads((BASE / "raw/primary01/stdout.txt").read_text())
        self.require(stdout["new_columns"] == 6 and stdout["formula_samples"] == 29 and
                     stdout["old_science_replay"] == 0, "actual_primary_stdout_scope")
        controls = read("verification/IMPLEMENTATION_RESULT.json")
        self.require(controls["passed"] == controls["total"] == len(controls["checks"]) and
                     all(c["pass"] is True for c in controls["checks"]), "saved_controls_all_pass")
        for flag in ("new_positive_source_formula_samples", "new_compiler_calls", "old249_replays"):
            self.require(controls[flag] == 0, "control_no_replay:" + flag)
        required = {
            "partial_output_stops_before_source_or_compiler", "failed_launch_has_actual_receipt",
            "empty_command_rejected_before_attempt_creation", "reject_T_bool", "reject_T_float",
            "reject_T_NaN", "reject_T_zero", "reject_T_negative", "reject_T_off_node",
            "reject_method_sum", "reject_unqualified_spin_sum", "reject_extra_statistical_weight",
            "reject_physical_rate_request", "reject_unnormalized_lift", "reject_negative_lift",
            "reject_missing_state_rates", "reject_quarantined_bovino_fit",
        }
        self.require(required <= {c["id"] for c in controls["checks"]}, "required_control_evidence")
        failed_launch = read("verification/EXPECTED_LAUNCH_FAILURE_RECEIPT.json")["receipt"]
        self.require(failed_launch["child_spawned"] is False and failed_launch["exit_code"] is None and
                     failed_launch["launch_error"]["type"] == "FileNotFoundError",
                     "expected_launch_failure_retained")
        self.require(failed_launch["cpu_s"] >= 0 and failed_launch["wall_s"] >= 0,
                     "failed_launch_measured_not_assumed")
        candidates = []
        for path in (BASE / "raw").glob("*/RECEIPT.json"):
            r = json.loads(path.read_text())
            if any(str(x).endswith("check_implementation.py") for x in r.get("command", [])):
                candidates.append((path, r))
        self.require(len(candidates) == 1, "one_implementation_attempt_receipt")
        impl_path, impl = candidates[0]
        self.require(impl["exit_code"] == 0 and impl["launch_error"] is None and
                     impl["timed_out"] is False, "implementation_child_pass")
        self.require(impl["code_sha256"]["verification/check_implementation.py"] ==
                     sha(BASE / "verification/check_implementation.py"), "control_code_identity")
        return {"primary_cpu_s": receipt["cpu_s"], "primary_wall_s": receipt["wall_s"],
                "primary_coordinator_execution_window_cpu_s": receipt["coordinator_CPU_s"],
                "implementation_result_sha256": sha(BASE / "verification/IMPLEMENTATION_RESULT.json"),
                "implementation_receipt": str(impl_path.relative_to(BASE)),
                "implementation_receipt_sha256": sha(impl_path),
                "controls_replayed_by_independent_checker": 0,
                "unmeasured_costs": "UNKNOWN_NOT_ZERO"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = BASE / output
    if output.exists():
        raise FileExistsError("EXISTING_INDEPENDENT_RESULT_DO_NOT_REPLAY")
    output.parent.mkdir(parents=True, exist_ok=True)
    audit = Audit()
    # Establish input identity before any new reference numerical work.
    valid = audit.group("G1_FROZEN_IDENTITIES_AND_COMPLETION", audit.identities)
    groups = [
        ("G2_NATIVE_77_CELL_INTEGRITY", audit.source_cells),
        ("G3_SIX_COLUMNS_INDEPENDENT_LEDGERS", audit.ledgers),
        ("G4_OWNERSHIP_RADIATION_AND_ENERGY", audit.ownership_energy),
        ("G5_INDEPENDENT_DECIMAL80_29_NODES", audit.formula_reference),
        ("G6_TWO_RESIDUAL_DENOMINATORS", audit.residuals),
        ("G7_EXACT_CONDITIONAL_EXAMPLES", audit.rational_examples),
        ("G8_ACTUAL_RECEIPTS_AND_REUSED_CONTROLS", audit.receipts_and_controls),
    ]
    for name, function in groups:
        if valid:
            audit.group(name, function)
        else:
            audit.groups.append({"id": name, "status": "SKIPPED_IDENTITY_FAILURE", "assertions": 0})
    passed = sum(g["status"] == "PASS" for g in audit.groups)
    result = {
        "schema": "WU_R4_INDEPENDENT_OUTPUT_AUDIT_V1",
        "status": "PASS_SCOPED" if passed == 8 else "FAIL_SCOPED",
        "groups_passed": passed, "groups_total": 8, "assertions_attempted": audit.assertions,
        "groups": audit.groups, "checker_sha256": sha(Path(__file__)),
        "source_packet_sha256": PINS["sources/MOLECULAR_SOURCE_PACKET.json"],
        "reference_precision_digits": 80, "formula_relative_limit": str(FORMULA_LIMIT),
        "residual_consistency_absolute_limit": str(RESIDUAL_ABS_LIMIT),
        "new_reference_formula_evaluations": audit.reference_evaluations,
        "new_producer_formula_samples": 0, "new_compiler_calls": 0, "old249_replays": 0,
        "producer_or_compiler_imports": 0, "physical_rate_Q_consumer_admitted": False,
        "source_wording_error_denominator": "UNSPECIFIED; both explicit conventions reported",
    }
    with output.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "groups_passed": passed, "groups_total": 8,
                      "assertions_attempted": audit.assertions,
                      "new_reference_formula_evaluations": audit.reference_evaluations,
                      "output": str(output), "sha256": sha(output)}))
    raise SystemExit(0 if passed == 8 else 1)


if __name__ == "__main__":
    main()

