#!/usr/bin/env python3
"""Primary changed-input audit of saved R2 registry outputs, without compilation.

Read only the explicit frozen packets, the generated R2 JSONs and the referenced
R1 identities. Do not import either builder, adapter or finite compiler. Integer
number/charge/lepton sums are checked directly; no source rate, Q, inverse rate,
interpolation, spectrum fold or historical validation suite is evaluated.

Use the same explicit packet pins as the builder. The default result is the
create-only raw/PRIMARY_RESULTS.json; a failed result must never be overwritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import traceback

BASE = Path(__file__).resolve().parents[1]
R1 = BASE.parent / "provider_registry_20261025"
R1_COMMIT = "18a6804d7cbe4879701e83631f7e908bbb84cef1"
COMPILER_SHA = "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af"
BUILDER_SHA = "96778246c7db1366689da360050dc7c73045668ef08c39324ac7e2e7e34bfdaf"
DEFAULT_PRIMARY_SHA = "9878f53c509ddaaa0317df2349913040dfd01425bc318d66cca0fd307bed33e3"
FROZEN_INPUTS = {
    "CONTRACT.json": "d4e89c891ec114ce911cb7e4dfc4779a8d19b2735d00cebe3fc07b2d718c21a4",
    "authority/AGENTS_AT_INPUT_FREEZE.md": "95851155333f8e9f532fe7f0fd353494f4403bc419019fff90d97fed58c7e189",
    "../provider_registry_20261025/registry_adapter.py": "9a093eed42f9ff5858d7bae11c726988ddbde4feeed38888b1c90fe329be816c",
    "../provider_registry_20261025/registry/species.json": "a18052f6db432192e1e0d4c75f8f2d49c71f3a5eb7cac206e7bc445fec2e8f80",
    "../provider_registry_20261025/registry/providers.json": "23d5bee7323a083d23a8a811eb7312a35c0eb613381ce28a22a5f989b1077664",
    "../provider_registry_20261025/registry/events.json": "abeea067660b0898315935ffd07bb6a443bbb1bd6111c700215b72be220baa90",
    "../provider_registry_20261025/registry/compiled.json": "d4836befd465ebd8130e5fd1f910b1fea30348c5e5785bfc66f8275735123f8c",
    "../rei_chem_ledger_20261025/chem_ledger.py": COMPILER_SHA,
    "sources/recovered_network/TARGET_NETWORK_19_c9deb93.json": "96466ae646905c7f47509ea30898f677d12b922571e23d166426bf223fbf889a",
    "sources/recovered_network/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json": "68f69ea6288f3ba45abe4ef9416b3d0cbe507f61543a4ff045ad914061acbe3c",
    "sources/recovered_network/primordial_target_network.png": "472ba6be633d2b5fc05fc1e0e88f965ff3c0311b0697e3c35c05bbca1629e6f9",
}
OUTPUT_NAMES = (
    "inputs", "target_declarations", "targets", "conditional_models", "primary_providers",
    "species", "events", "compiled", "reused_r1_evidence", "family_aliases", "coverage",
)
PHOTO_IDS = {4, 5, 6, 7, 8, 11}
REVERSIBLE_IDS = set(range(1, 9)) | {11}
FAMILY_TARGETS = {
    "he3_n_gamma": [4], "p_t_gamma": [5], "d_d_gamma": [6],
    "p_d_gamma": [7, 13], "p_n_gamma": [8, 12], "t_beta": [9], "n_beta": [10],
    "t_alpha_gamma": [11, 19], "d_d_p": [14], "d_d_n": [15], "d_t_n": [16],
    "d_he3_p": [17], "n_he3_p": [18], "d_alpha_gamma": [], "p_li6_alpha": [],
    "n_li6_alpha": [], "p_li7_alpha": [], "d_n_gamma": [],
}
TARGET_FAMILY = {tid: fid for fid, tids in FAMILY_TARGETS.items() for tid in tids}
NUCLEI = {"n": (1, 0), "H1": (1, 1), "D": (2, 1), "T": (3, 1),
          "He3": (3, 2), "He4": (4, 2), "Li6": (6, 3), "Li7": (7, 3)}
PHOTO_FIELDS = {
    "EXCLUSIVE_NATIVE_CHANNEL": "exclusive_native_channel_source_refs",
    "FACTORIZED_EXCLUSIVE_CANDIDATE": "factorized_exclusive_candidate_refs",
    "INCLUSIVE_ONLY": "inclusive_only_provider_refs",
    "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT": "beam_averaged_provider_refs",
}
EXPECTED_PHOTO_CLASS = {
    4: "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT",
    5: "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT", 6: None,
    7: "FACTORIZED_EXCLUSIVE_CANDIDATE", 8: "EXCLUSIVE_NATIVE_CHANNEL", 11: "INCLUSIVE_ONLY",
}
EXTERNAL_LEDGER = {"gamma:incident": (0, 0, 0), "gamma:escaping": (0, 0, 0),
                   "antinu_e:escaping": (0, 0, -1)}
NORMALIZATION = "events_per_reference_nucleus_per_proper_second"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def object_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode("utf-8"))


def indexed(rows, key):
    require(isinstance(rows, list), "Expected row list: " + key)
    result = {}
    for row in rows:
        require(row[key] not in result, "Duplicate identity: " + str(row[key]))
        result[row[key]] = row
    return result


def counts(side):
    require(isinstance(side, list), "Material/external side must be an explicit pair list")
    result = Counter()
    for name, value in side:
        require(isinstance(name, str) and type(value) is int and value > 0,
                "Positive integer participant multiplicity required")
        result[name] += value
    return dict(result)


def expected_directions(native):
    direction = native["direction"]
    require(direction in {"family_forward", "family_reverse", "target_forward"},
            "Unsupported source direction: " + native["id"])
    result = {}
    for tid in native["target_ids"]:
        if direction == "target_forward":
            require(tid in PHOTO_IDS, "Direct target-forward source is not a photonuclear target")
            result[str(tid)] = "target_forward"
        else:
            forward = (tid not in PHOTO_IDS) == (direction == "family_forward")
            result[str(tid)] = "target_forward" if forward else "target_reverse"
    return result


class Audit:
    def __init__(self, args, packet_pins):
        self.args = args
        self.packet_pins = packet_pins
        self.results = []
        self.input_sha256 = {}
        self.cache = {}

    def read_bytes(self, path):
        path = Path(path).resolve()
        data = path.read_bytes()
        self.input_sha256[os.path.relpath(path, BASE)] = sha(data)
        return data

    def read(self, path):
        path = Path(path).resolve()
        if path not in self.cache:
            self.cache[path] = json.loads(self.read_bytes(path))
        return self.cache[path]

    def run(self, name, function):
        try:
            detail = function()
            self.results.append({"id": name, "status": "PASS", "detail": detail})
            return True
        except Exception as error:
            self.results.append({"id": name, "status": "FAIL", "error_type": type(error).__name__,
                                 "error": str(error), "traceback": traceback.format_exc()})
            return False

    def initialize(self):
        self.docs = {name: self.read(self.args.registry_dir / (name + ".json")) for name in OUTPUT_NAMES}
        self.contract = self.read(BASE / "CONTRACT.json")
        self.target_source = self.read(BASE / "sources/recovered_network/TARGET_NETWORK_19_c9deb93.json")
        self.model_source = self.read(BASE / "sources/recovered_network/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json")
        self.targets_native = indexed(self.target_source["reactions"], "id")
        self.families = indexed(self.model_source["families"], "id")
        self.targets = indexed(self.docs["targets"]["rows"], "id")
        self.events = indexed(self.docs["events"]["rows"], "id")
        self.compiled = indexed(self.docs["compiled"]["rows"], "event_id")
        self.aliases = indexed(self.docs["family_aliases"]["rows"], "family_id")
        self.models = self.docs["conditional_models"]["rows"]
        self.declarations = self.docs["target_declarations"]["rows"]
        self.primary = self.docs["primary_providers"]["rows"]
        self.species = self.docs["species"]["rows"]
        self.reused = self.docs["reused_r1_evidence"]["rows"]
        self.coverage = self.docs["coverage"]
        for name in ("models", "declarations", "primary", "species", "reused"):
            require(isinstance(getattr(self, name), dict), "Mapping required: " + name)
        self.r1_species = self.read(R1 / "registry/species.json")["rows"]
        self.r1_providers = self.read(R1 / "registry/providers.json")["rows"]
        self.r1_events = indexed(self.read(R1 / "registry/events.json")["rows"], "id")
        self.r1_compiled = indexed(self.read(R1 / "registry/compiled.json")["rows"], "event_id")
        self.packet_rows = {}
        for relative in self.packet_pins:
            for row in self.read(BASE / relative)["rows"]:
                require(row["id"] not in self.packet_rows, "Duplicate ID across frozen packets: " + row["id"])
                self.packet_rows[row["id"]] = (relative, row)
        return {"generated_JSON_files": len(OUTPUT_NAMES), "explicit_provider_packets": list(self.packet_pins),
                "source_record_count": len(self.packet_rows), "builder_adapter_compiler_imports": 0}

    def frozen_identities(self):
        expected = {**FROZEN_INPUTS, **self.packet_pins}
        receipts = indexed(self.docs["inputs"]["rows"], "file")
        require(set(receipts) == set(expected), "Build receipt differs from explicitly frozen input set")
        for relative, expected_sha in expected.items():
            data = self.read_bytes(BASE / relative)
            require(sha(data) == expected_sha, "Frozen input changed: " + relative)
            receipt = receipts[relative]
            require(receipt["sha256"] == expected_sha and receipt["bytes"] == len(data)
                    and receipt["expected_sha256_match"] is True, "Input receipt mismatch: " + relative)
        require(sha(self.read_bytes(BASE / "build_network19.py")) == BUILDER_SHA, "Reviewed builder changed")
        require(self.docs["inputs"]["compiler_sha256"] == COMPILER_SHA, "Compiler receipt identity changed")
        require(self.contract["base_source_commit"] == R1_COMMIT, "R1 source commit changed")
        require(self.target_source["source_image"]["bytes"] == 1856861
                and self.target_source["source_image"]["sha256"] == FROZEN_INPUTS[
                    "sources/recovered_network/primordial_target_network.png"], "Image/target contract mismatch")
        for name, doc in self.docs.items():
            if name != "coverage":
                require(doc["unit_id"] == self.contract["unit_id"] and doc["R1_source_commit"] == R1_COMMIT,
                        "Output lineage mismatch: " + name)
        return {"frozen_inputs": len(expected), "builder_SHA256": BUILDER_SHA, "compiler_SHA256": COMPILER_SHA,
                "AGENTS_binding": "immutable input snapshot; latest authority remains root preflight obligation"}

    def original_target_map(self):
        require(set(self.targets) == set(self.targets_native) == set(range(1, 20)), "Original 19 IDs not intact")
        require(set(self.declarations) == {f"USER_TARGET19:{tid:02d}" for tid in range(1, 20)},
                "Target declaration identities changed")
        direction_ids = []
        for tid, native in self.targets_native.items():
            target = self.targets[tid]
            declaration = self.declarations[f"USER_TARGET19:{tid:02d}"]
            require(declaration["native_record"] == native and declaration["record_sha256"] == object_sha(native),
                    "Target declaration changed: " + str(tid))
            require(declaration["record_class"] == "USER_TARGET_DECLARATION"
                    and declaration["empirical_coefficient_supplied_by_image"] is False, "Image promoted to coefficient")
            for key in ("equation_as_listed", "kind", "reversible_arrow_as_listed"):
                require(target[key] == native[key], "Original target field changed: " + str(tid) + ":" + key)
            require(native["reversible_arrow_as_listed"] is (tid in REVERSIBLE_IDS), "Original arrow map changed")
            require(target["target_obligation_retained"] is True
                    and target["source_record_id"] == declaration["id"], "Target identity discarded")
            require(target["conditional_family_id"] == TARGET_FAMILY.get(tid), "Wrong target-family alias")
            directions = indexed(target["directions"], "direction")
            expected = {"target_forward", "target_reverse"} if tid in REVERSIBLE_IDS else {"target_forward"}
            require(set(directions) == expected, "Listed target direction added or lost: " + str(tid))
            for direction, row in directions.items():
                identity = f"TARGET19:{tid:02d}:{direction}"
                require(row["id"] == identity, "Wrong original direction ID")
                direction_ids.append(identity)
                if tid <= 3:
                    require(not row["new_number_projection_event_ids"]
                            and not row["conditional_forward_model_record_refs"], "Electronic evidence was recompiled")
                else:
                    fid = TARGET_FAMILY[tid]
                    photo = tid in PHOTO_IDS and direction == "target_forward"
                    expected_event = f"TARGET19_PHOTONUCLEAR:{tid:02d}" if photo else "COND18_FORWARD:" + fid
                    require(row["new_number_projection_event_ids"] == [expected_event], "Reversed/wrong event binding")
                    require(row["conditional_forward_model_record_refs"] == ([] if photo else ["COND18:" + fid]),
                            "Capture model bound to listed photodisintegration")
        require(len(direction_ids) == len(set(direction_ids)) == 28, "Original 28 directions not intact")
        require(self.docs["targets"]["overlaps"] == self.target_source["shared_forward_reverse_processes"]
                and self.docs["targets"]["overlap_rule"] == self.target_source["overlap_rule"], "Overlap provenance changed")
        require({tuple(row["listed_ids"]) for row in self.docs["targets"]["overlaps"]}
                == {(7, 13), (8, 12), (11, 19)}, "Original overlap sets changed")
        return {"original_targets": 19, "listed_directions": 28, "retained_overlap_pairs": [[7, 13], [8, 12], [11, 19]]}

    def conditional_models_and_aliases(self):
        require(set(self.families) == set(self.aliases) == set(FAMILY_TARGETS), "Conditional family set changed")
        require(set(self.models) == {"COND18:" + fid for fid in FAMILY_TARGETS}, "Conditional row identity count changed")
        raw = self.read_bytes(BASE / "sources/recovered_network/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json").decode()
        closure_ids = []
        for fid, native in self.families.items():
            model = self.models["COND18:" + fid]
            alias = self.aliases[fid]
            require(native["dossier_ids"] == FAMILY_TARGETS[fid], "Source family alias changed: " + fid)
            require(model["record_class"] == "DECLARED_CONDITIONAL_MODEL_ROW"
                    and model["native_record"] == native and model["record_sha256"] == object_sha(native),
                    "Model row changed or relabelled primary: " + fid)
            line = raw.splitlines()[model["raw_line_number"] - 1]
            require(model["raw_line"] == line and json.loads(line.strip().rstrip(",")) == native,
                    "Conditional literal locator mismatch: " + fid)
            literals = {}
            for key in ("S0_keV_b", "sigma2200_b"):
                if key in native:
                    match = re.search(r'"' + key + r'"\s*:\s*([^,}]+)', line)
                    require(match is not None, "Conditional source literal missing: " + fid)
                    literals[key] = match.group(1).strip()
            require(model["raw_numeric_literals"] == literals and model["native_units"] == self.model_source["units"],
                    "Conditional literals/units were converted")
            require(model["conditional_temperature_K"] == self.model_source["temperature_K"]
                    and model["primary_validity_interval_inferred"] is False, "Model domain promoted to primary support")
            require(model["model_mode"] == self.model_source["mode"]
                    and model["model_admission"] == self.model_source["admission"], "Conditional mode/admission lost")
            require(model["original_target_ids"] == alias["original_target_ids"] == FAMILY_TARGETS[fid], "Alias drops original IDs")
            is_closure = not FAMILY_TARGETS[fid]
            require(model["additional_closure_only"] is is_closure
                    and alias["extra_conditional_closure"] is is_closure, "Closure conflated with image target")
            require(alias["model_record_id"] == model["id"]
                    and alias["new_model_event_id"] == "COND18_FORWARD:" + fid, "Wrong conditional event reference")
            require(alias["closure_reason"] == native.get("closure_reason") and alias["rate_selection"] is None,
                    "Closure reason changed or a rate was selected")
            if is_closure:
                closure_ids.append(fid)
                require(bool(alias["closure_reason"]), "Closure lacks declared origin")
            forward = sorted(pid for pid, record in self.primary.items()
                             if fid in record["native_record"]["family_ids"]
                             and record["native_record"]["direction"] == "family_forward")
            reverse = sorted(pid for pid, record in self.primary.items()
                             if fid in record["native_record"]["family_ids"]
                             and record["native_record"]["direction"] != "family_forward")
            require(model["primary_record_refs"] == alias["family_forward_primary_packet_record_refs"] == forward,
                    "Wrong family-forward source association")
            require(alias["family_reverse_primary_packet_record_refs"] == reverse, "Wrong family-reverse source association")
        require(len(closure_ids) == 5, "Five extra closure families required")
        for key, value in self.docs["conditional_models"]["context"].items():
            require(value == self.model_source[key], "Historical conditional context modified: " + key)
        require(self.docs["family_aliases"]["aliases_are_not_additive_event_rates"] is True, "Aliases duplicate rate ownership")
        return {"conditional_records": 18, "dossier_families": 13, "extra_closures": sorted(closure_ids),
                "conditional_parameters_evaluated": 0}

    def native_primary_records(self):
        require(set(self.primary) == set(self.packet_rows), "Source variants lost, invented or duplicated")
        class_counts, omitted, verified = Counter(), set(), set()
        for pid, (relative, native) in self.packet_rows.items():
            row = self.primary[pid]
            require(native["record_class"] in {"PRIMARY_SOURCE_ROW", "REUSED_CONDITIONAL_MODEL_OUTPUT"}, "Unknown source class")
            require(row["id"] == pid and row["record_class"] == native["record_class"], "Source class/identity changed")
            require(row["native_record"] == native and row["record_sha256"] == object_sha(native),
                    "Native source values, units, support or uncertainty changed: " + pid)
            require(row["payload_ref"] == {"file": relative, "container": "rows", "match": {"id": pid}},
                    "Wrong packet/row locator: " + pid)
            units = "units" if "units" in native else "native_units"
            support = "support" if "support" in native else "native_support"
            require(units in native and support in native
                    and row["native_field_names"] == {"units": units, "support": support}, "Native field alias changed")
            require(native["family_ids"] and len(set(native["family_ids"])) == len(native["family_ids"]), "Family refs ambiguous")
            allowed = {tid for fid in native["family_ids"] for tid in FAMILY_TARGETS[fid]}
            require(set(native["target_ids"]) <= allowed and len(set(native["target_ids"])) == len(native["target_ids"]),
                    "Source target aliases do not belong to supplied families")
            expected = expected_directions(native)
            require(native["target_directions"] == row["target_direction_bindings"] == expected,
                    "Native source forward/reverse mapping changed: " + pid)
            require(row["binding_qualification"] == "REACTION_FAMILY_AND_DIRECTION_ONLY; STATE_BRANCH_DOMAIN_NOT_ADMITTED",
                    "Source linked as physical state/branch admission")
            packet_dir = (BASE / relative).parent.resolve()
            raw_path = (packet_dir / native["source_file"]).resolve()
            require(packet_dir in raw_path.parents, "Raw source path escaped its own packet")
            require(native["source_url"] and native["locator"] and re.fullmatch(r"[0-9a-f]{64}", native["source_SHA256"]),
                    "Missing exact source provenance")
            if raw_path.exists():
                if raw_path not in verified:
                    data = self.read_bytes(raw_path)
                    require(sha(data) == native["source_SHA256"], "Packaged raw source hash mismatch: " + pid)
                    if "source_bytes" in native:
                        require(len(data) == native["source_bytes"], "Packaged raw source byte count mismatch")
                    verified.add(raw_path)
                require(row["raw_source_byte_check"] == "PACKAGED_RAW_BYTES_HASH_VERIFIED", "Raw byte check overstated/omitted")
            else:
                availability = native.get("publication_source_availability", {})
                require(availability.get("original_bytes_bundled") is False, "Missing source without explicit public omission")
                if "original_source_SHA256" in availability:
                    require(availability["original_source_SHA256"] == native["source_SHA256"], "Omitted source identity changed")
                require(row["raw_source_byte_check"] == "RAW_SOURCE_NOT_PACKAGED; RETAINED_HASH_AND_INTAKE_REVIEW_REQUIRED",
                        "Absent original bytes represented as locally checked")
                omitted.add(str(raw_path))
            class_counts[native["record_class"]] += 1
        require(self.docs["primary_providers"]["classes_are_distinct"] is True
                and self.docs["primary_providers"]["coefficient_evaluation"] == "NOT_RUN", "Primary wrapper admission changed")
        return {"native_rows_equal_frozen_packets": len(self.primary), "record_classes": dict(class_counts),
                "distinct_packaged_raw_sources_verified": len(verified), "explicit_public_original_omissions": len(omitted),
                "unit_conversions": 0, "source_numeric_evaluations": 0}

    def species_and_declared_vertices(self):
        require(len(self.species) == 9 and self.docs["species"]["new_species_count"] == 0, "Unexpected new species")
        self.species_for_label = {}
        for label, (a, z) in NUCLEI.items():
            record = {"composition": [{"Z": z, "A": a, "isomer": "ground", "count": 1}],
                      "charge": z, "state": "bare_nucleus", "pool": "material"}
            matches = [sid for sid, row in self.r1_species.items() if row["compiler_record"] == record]
            require(len(matches) == 1, "Unresolved bare coordinate: " + label)
            self.species_for_label[label] = matches[0]
        matches = [sid for sid, row in self.r1_species.items() if row["compiler_record"] == {
            "composition": [], "charge": -1, "state": "free_electron", "pool": "electron_fast"}]
        require(len(matches) == 1, "Unresolved beta electron coordinate")
        self.electron = matches[0]
        require(set(self.species) == set(self.species_for_label.values()) | {self.electron}, "Extra/missing R1 number coordinate")
        for sid, row in self.species.items():
            require(row == self.r1_species[sid], "Reused R1 species record changed: " + sid)
        assumptions = self.docs["species"]["projection_assumptions"]
        require(set(assumptions) == {"charge", "nuclear_state", "inclusive_primary_states", "beta_electron", "photons",
                                     "normalization", "material_pools"}, "Projection assumptions incomplete")
        for key, phrase in {"charge": "chosen number projection", "nuclear_state": "declared coordinates",
                            "inclusive_primary_states": "no branch fractions", "photons": "unqualified",
                            "normalization": "no native coefficient normalization binding"}.items():
            require(phrase in assumptions[key], "Declared projection promoted to source state: " + key)
        expected_events = {"COND18_FORWARD:" + fid for fid in FAMILY_TARGETS} | {
            f"TARGET19_PHOTONUCLEAR:{tid:02d}" for tid in PHOTO_IDS}
        require(set(self.events) == set(self.compiled) == expected_events, "Exactly 24 new columns required")
        def material(native):
            return {self.species_for_label["H1" if label == "p" else label]: n for label, n in native.items()}
        for eid, event in self.events.items():
            if eid.startswith("COND18_FORWARD:"):
                fid = eid.split(":", 1)[1]
                native = self.families[fid]
                left, right = material(native["reactants"]), material(native["products"])
                external_in, external_out = {}, {}
                kind = native["kind"]
                if kind == "beta_minus":
                    right[self.electron] = 1
                    external_out = {"antinu_e:escaping": 1}
                    process, branch = "weak_beta_minus", "beta_minus"
                elif kind == "radiative_capture":
                    external_out = {"gamma:escaping": 1}
                    process, branch = "nuclear_capture", "nuclear_capture"
                else:
                    require(kind == "binary_transfer", "Unknown model vertex kind")
                    process, branch = "nuclear_transfer", "declared_transfer:" + fid
                source = self.models["COND18:" + fid]
                require(event["family_id"] == fid and event["target_id"] is None, "Conditional/target declaration conflated")
                require(event["native_rate_record"]["evaluation"] == "NOT_EVALUATED"
                        and event["native_rate_record"]["historical_inverse_rule_not_executed"] == native["reverse"],
                        "Conditional inverse rule executed/relabelled")
                refs = sorted(pid for pid, row in self.primary.items() if fid in row["native_record"]["family_ids"]
                              and row["native_record"]["direction"] == "family_forward")
            else:
                tid = int(eid.rsplit(":", 1)[1])
                native = self.targets_native[tid]["nuclear_stoichiometry"]
                left, right = material(native["reactants"]), material(native["products"])
                external_in, external_out = {"gamma:incident": 1}, {}
                process, branch = "nuclear_photodisintegration", f"listed_target_branch:{tid:02d}"
                source = self.declarations[f"USER_TARGET19:{tid:02d}"]
                require(event["family_id"] is None and event["target_id"] == tid
                        and event["native_rate_record"] is None, "Declared photo event acquired a rate")
                refs = sorted(pid for pid, row in self.primary.items()
                              if row["target_direction_bindings"].get(str(tid)) == "target_forward")
            require(counts(event["reactants"]) == left and counts(event["products"]) == right,
                    "Source stoichiometry or multiplicity changed: " + eid)
            require(counts(event["external_reactants"]) == external_in
                    and counts(event["external_products"]) == external_out, "Wrong explicit photon/lepton participants")
            require(event["process"] == process and event["branch_id"] == branch and event["kind"] == "nuclear",
                    "Wrong process/branch identity")
            require(event["source_id"] == source["id"] and event["source_identity"] == source["record_sha256"]
                    and event["source_record_class"] == source["record_class"], "Column source provenance mismatch")
            require(event["projection_assumptions"] == assumptions
                    and "source_state_branch_unqualified" in event["state_resolution"], "Source state qualification inflated")
            require(event["linked_primary_packet_record_refs"] == refs, "Wrong source-family/direction association")
        return {"reused_material_nuclei": 8, "reused_free_electron": 1, "new_species": 0,
                "conditional_forward_columns": 18, "declared_photonuclear_columns": 6,
                "source_native_states_admitted": 0}

    def exact_new_column_ledgers(self):
        details = []
        for eid, event in self.events.items():
            left, right = counts(event["reactants"]), counts(event["products"])
            nu = {sid: right.get(sid, 0) - left.get(sid, 0) for sid in left.keys() | right.keys()
                  if right.get(sid, 0) != left.get(sid, 0)}
            saved = self.compiled[eid]
            require(saved["stoichiometry"] == nu and all(type(v) is int for v in saved["stoichiometry"].values()),
                    "Saved integer column mismatch: " + eid)
            baryon = charge = material_lepton = 0
            isotope = Counter()
            for sid, n in nu.items():
                record = self.r1_species[sid]["compiler_record"]
                nuclear_z = 0
                for part in record["composition"]:
                    require(all(type(part[key]) is int for key in ("A", "Z", "count")), "Noninteger nuclear identity")
                    baryon += n * part["A"] * part["count"]
                    nuclear_z += part["Z"] * part["count"]
                    isotope[(part["Z"], part["A"], part["isomer"])] += n * part["count"]
                require(type(record["charge"]) is int, "Noninteger electric charge")
                charge += n * record["charge"]
                material_lepton += n * (nuclear_z - record["charge"])
            external = [0, 0, 0]
            for sign, side in ((-1, event["external_reactants"]), (1, event["external_products"])):
                for label, n in counts(side).items():
                    require(label in EXTERNAL_LEDGER, "Undeclared external particle")
                    for axis, value in enumerate(EXTERNAL_LEDGER[label]):
                        external[axis] += sign * n * value
            totals = (baryon + external[0], charge + external[1], material_lepton + external[2])
            require(totals == (0, 0, 0), "Baryon/charge/electron-lepton conservation failed: " + eid)
            require(saved["baryon_delta"] == baryon == 0 and saved["charge_delta"] == charge == 0
                    and saved["electron_lepton_delta"] == totals[2] == 0, "Saved conserved totals mismatch")
            require(saved["isotope_delta"] == {str(key): value for key, value in isotope.items()},
                    "Nuclear isotope-change vector was altered/zeroed")
            require(saved["source_id"] == event["source_id"]
                    and saved["provider_record_sha256"] == event["source_identity"]
                    and saved["compiler_sha256"] == COMPILER_SHA, "Compiled source/compiler binding mismatch")
            details.append({"event_id": eid, "baryon_delta": totals[0], "charge_delta": totals[1],
                            "material_electron_lepton_delta": material_lepton,
                            "external_electron_lepton_delta": external[2], "electron_lepton_delta": totals[2]})
        require(len(details) == 24 and sum(row["material_electron_lepton_delta"] == 1 for row in details) == 2,
                "New-column or explicit weak-lepton count changed")
        return {"method": "direct integer sums from frozen R1 composition/charge and explicit external leptons",
                "compiler_calls": 0, "columns": details}

    def physical_admission_boundary(self):
        event_false = ("activation", "empirical_rate_admitted", "nuclear_Q_admitted", "rate_normalization_bound", "reverse_rate_inferred")
        compiled_false = ("Q_approved", "native_rate_evaluated", "rate_normalization_bound", "activation", "reverse_rate_inferred")
        direction_false = ("factorized_source_product_evaluated", "inverse_rate_generated", "physical_rate_admission",
                           "physical_Q_admission", "activation", "state_branch_domain_admission")
        for eid, event in self.events.items():
            require(all(event[key] is False for key in event_false), "Event acquired physical admission: " + eid)
            require(all(event[key] is None for key in ("native_Q_record", "physical_total_photon_count", "branch_fraction", "consumer_ACK")),
                    "Unqualified event received Q/branch/photon/deposition assignment")
            require("photon_energy_eV" not in event and "photon_count_per_event" not in event, "Schematic photon promoted to energy payload")
            require(event["source_uncertainty"]["absence_is_not_zero"] is True
                    and all(event["source_uncertainty"][key] is None for key in ("Q_uncertainty", "branch_probabilities", "parameter_covariance")),
                    "Unknown uncertainty promoted to zero/assigned value")
            saved = self.compiled[eid]
            require(all(saved[key] is False for key in compiled_false), "Compiled output promoted physical approval")
            require(saved["energy_status"] == "UNQUALIFIED:ENERGY" and saved.get("energy") is None
                    and saved["number_operator_status"] == "EXACT_INTEGER_PROJECTION_CHECKED", "Energy boundary changed")
            require(saved["event_rate_unit_if_later_bound"] == NORMALIZATION, "Operator unit relabelled as native coefficient")
        for target in self.targets.values():
            for row in target["directions"]:
                require(all(row[key] is False for key in direction_false), "Target direction activated")
                require(all(row[key] is None for key in ("selected_rate_provider", "branch_fraction", "physical_Q")),
                        "Target direction selected an unqualified source/energy")
            for row in target["additional_direction_evidence"]:
                require(row["new_rate_admission"] is False and row["new_Q_admission"] is False, "Extra source relation promoted")
        for container in (self.declarations, self.models, self.primary):
            for row in container.values():
                require(row["new_rate_admission"] is False and row["new_Q_admission"] is False, "Source wrapper promoted")
        for row in self.primary.values():
            native = row["native_record"]
            require(native["new_rate_admission"] is False and native["new_Q_admission"] is False
                    and native.get("activation", False) is False and native.get("default_active", False) is False,
                    "Source-native admission flag active")
        return {"inactive_new_columns": len(self.events), "energy_unqualified_columns": len(self.compiled),
                "physical_rate_Q_state_admissions": 0, "schematic_photons_promoted_to_physical_counts": 0}

    def photon_source_coverage(self):
        details = []
        for tid in sorted(PHOTO_IDS):
            row = indexed(self.targets[tid]["directions"], "direction")["target_forward"]
            expected_refs = sorted(pid for pid, record in self.primary.items()
                                   if record["record_class"] == "PRIMARY_SOURCE_ROW"
                                   and record["target_direction_bindings"].get(str(tid)) == "target_forward")
            require(row["primary_provider_refs"] == expected_refs, "Wrong primary photo references")
            class_refs = {kind: [] for kind in PHOTO_FIELDS}
            for pid in expected_refs:
                native = self.primary[pid]["native_record"]
                kind = native["source_coverage"]
                require(kind in PHOTO_FIELDS and native["exclusive_channel_binding"] is (kind == "EXCLUSIVE_NATIVE_CHANNEL"),
                        "Exclusive/factorized/inclusive/beam source class conflated")
                class_refs[kind].append(pid)
            for kind, field in PHOTO_FIELDS.items():
                require(row[field] == class_refs[kind], "Photo reference partition changed: " + str(tid) + ":" + kind)
            present_classes = {kind for kind, refs in class_refs.items() if refs}
            expected_class = EXPECTED_PHOTO_CLASS[tid]
            require(present_classes == ({expected_class} if expected_class else set()),
                    "Reviewed photon source coverage changed: target " + str(tid))
            require(row["has_primary_source_record_reference"] is bool(expected_refs)
                    and not row["reused_R1_event_refs"], "Capture/R1 evidence used as direct photo supplier")
            require(row["conditional_soft_field_zero_is_not_cross_section_zero"] is True
                    and row["conditional_inverse_rule_reference_only"] == "COND18:" + TARGET_FAMILY[tid],
                    "Soft-field zero promoted to universal cross-section zero")
            if tid == 6:
                require(row["supplier_status"] == "TARGET_DECLARED_PRIMARY_SUPPLIER_MISSING"
                        and row["selected_rate_provider"] is None, "Actual target 6 supplier gap erased")
            details.append({"target_id": tid, "source_class": expected_class,
                            "primary_source_refs": expected_refs, "exclusive_native_binding": bool(class_refs["EXCLUSIVE_NATIVE_CHANNEL"])})
        photo = self.coverage["direct_photonuclear_source_coverage"]
        require(photo["listed_forward_direction_count"] == 6 and photo["exclusive_native_channel_source_count"] == 1
                and photo["factorized_exclusive_candidate_count"] == 1 and photo["inclusive_only_source_count"] == 1
                and photo["beam_averaged_measurement_direction_count"] == 2, "Direct photo class coverage counts inflated")
        require(photo["no_primary_source_record_reference"] == ["TARGET19:06:target_forward"]
                and photo["exclusive_source_binding_gaps"] == [f"TARGET19:{tid:02d}:target_forward" for tid in (4, 5, 6, 7, 11)],
                "Photo source availability confused with exclusive channel binding")
        require(photo["factorization_products_evaluated"] == 0
                and photo["source_reference_is_not_physical_admission"] is True, "Factorized data multiplied or admitted")
        return {"target_forward_relations": details, "target6_actual_primary_gap": True,
                "pointwise_binding_of_beam_averages": False}

    def native_units_support_and_MT5_Q(self):
        nacre = [row["native_record"] for pid, row in self.primary.items() if pid.startswith("NACREII2013_")]
        require(len(nacre) == 10, "Frozen base NACRE source rows changed")
        total = 0
        domains = []
        for row in nacre:
            units, support, values = row["units"], row["support"], row["raw_values"]
            require(units["native_rate"] == "cm^3 mol^-1 s^-1" and units["native_rate_quantity"] == "N_A <sigma v>"
                    and units["temperature"] == "T9 = T/(10^9 K)", "Native NACRE coefficient/temperature unit converted")
            require(support["native_table_interpolation_performed"] is False
                    and support["native_grid_overlaps_100_to_10000_K"] is False, "NACRE support extended to conditional domain")
            require(values["native_rate_table_count"] == len(values["native_rate_table"]), "Native rate table length changed")
            require(values["native_rate_table"][0]["T9"] == support["native_T9_min"]
                    and values["native_rate_table"][-1]["T9"] == support["native_T9_max"], "NACRE native grid endpoints changed")
            require(all(isinstance(point[key], str) for point in values["native_rate_table"] for key in ("T9", "adopted", "low", "high")),
                    "Native printed literals replaced by evaluated numbers")
            total += len(values["native_rate_table"])
            domains.append({"id": row["id"], "T9_min_literal": support["native_T9_min"], "T9_max_literal": support["native_T9_max"]})
        require(total == 598, "Frozen NACRE native point count changed")
        lih = self.primary["NACREII2013_t_alpha_gamma_TABLE8"]["native_record"]
        require(lih["branch"]["status"] == "INCLUSIVE_GROUND_AND_FIRST_EXCITED_NO_FRACTIONS"
                and lih["branch"]["inclusive_daughter_states"] == ["ground", "first_excited"]
                and lih["branch"]["branch_fraction"] is None, "Inclusive Li7 source became ground-only/fraction-resolved")
        mt5 = []
        for pid in ("ENDFBVIII1_GAMMA_MAT225_MF3MT5_MF6_NATIVE", "ENDFBVIII1_GAMMA_MAT328_MF3MT5_MF6_NATIVE"):
            native = self.primary[pid]["native_record"]
            tab, q = native["raw_values"]["cross_section_TAB1"], native["Q"]
            require(tab["header_fields"][:2] == ["0.000000+0", "0.000000+0"], "Native MT5 zero fields altered")
            require(q["value"] is None and q["mass_difference_field"] is None
                    and q["qualification"] == "MT5_ZERO_FIELDS_ARE_NOT_EXCLUSIVE_REACTION_Q"
                    and q["Q_admitted"] is False and q["new_Q_computation"] is False, "MT5 zero promoted to exclusive Q")
            require(native["new_cross_section_products_evaluated"] == 0
                    and native["new_rate_evaluations"] == 0, "Native photon data evaluated")
            require(native["native_units"]["x"] == "eV incident photon energy"
                    and native["native_units"]["MF3_y"] == "barn", "Native ENDF units converted")
            mt5.append({"id": pid, "native_sigma_points": tab["NP"], "exclusive_Q": None})
        h2 = self.primary["ENDFBVIII1_GAMMA_MAT128_MF3MT50_MF6_NATIVE"]["native_record"]
        require(h2["Q"]["value"] == "-2.224600+6" and h2["Q"]["Q_admitted"] is False,
                "D native Q literal changed/promoted")
        return {"unchanged_NACRE_native_grid_points": total, "native_domains": domains,
                "MT5_Q_qualification": mt5, "native_rate_Q_evaluations": 0, "normalization_conversions": 0}

    def provider_directions_and_additional_aliases(self):
        all_direction_rows = []
        for tid, target in self.targets.items():
            listed = {row["direction"] for row in target["directions"]}
            for row in target["directions"]:
                all_direction_rows.append(row)
                for klass, field in (("PRIMARY_SOURCE_ROW", "primary_provider_refs"),
                                     ("REUSED_CONDITIONAL_MODEL_OUTPUT", "reused_conditional_model_output_refs")):
                    expected = sorted(pid for pid, record in self.primary.items() if record["record_class"] == klass
                                      and record["target_direction_bindings"].get(str(tid)) == row["direction"])
                    require(row[field] == expected, "Wrong source-class/target-direction relationship")
                has_r1_primary = any(ref["evidence_role"].startswith("PRIMARY_") for ref in row["reused_R1_event_refs"])
                require(row["has_primary_source_record_reference"] is bool(row["primary_provider_refs"] or has_r1_primary),
                        "Model/cold-kinematic row represented as actual rate supplier")
            extra = indexed(target["additional_direction_evidence"], "direction")
            expected_extra = {}
            for direction in {"target_forward", "target_reverse"} - listed:
                refs = sorted(pid for pid, record in self.primary.items()
                              if record["target_direction_bindings"].get(str(tid)) == direction)
                if refs:
                    expected_extra[direction] = refs
            require(set(extra) == set(expected_extra), "Unlisted alias direction added/lost")
            for direction, refs in expected_extra.items():
                row = extra[direction]
                related = [f"TARGET19_PHOTONUCLEAR:{photo_id:02d}" for photo_id in sorted(PHOTO_IDS)
                           if TARGET_FAMILY.get(tid) == TARGET_FAMILY[photo_id]]
                require(row["provider_record_refs"] == refs and row["related_number_projection_event_ids"] == related,
                        "Additional alias source linked to wrong photo column")
                require(row["qualification"] == "ACTUAL_SOURCE_REFERENCE_BEYOND_LISTED_ARROW; NOT_AN_ADDITIONAL_ORIGINAL_TARGET_OBLIGATION",
                        "Extra source reference promoted to original target obligation")
        require(self.coverage["target_directions_without_primary_source_record_reference"] == [
            row["id"] for row in all_direction_rows if not row["has_primary_source_record_reference"]], "Source gap list inconsistent")
        return {"listed_direction_records": len(all_direction_rows),
                "additional_source_directions": [{"target_id": tid, "direction": row["direction"]}
                                                for tid, target in self.targets.items()
                                                for row in target["additional_direction_evidence"]],
                "additional_original_obligations": 0}

    def unchanged_R1_references(self):
        expected = {"NUBASE2020_T_beta_minus", "LiveChart_ENSDF_T_beta_minus", "NUBASE2020_n_beta_minus",
                    "LiveChart_ENSDF_n_beta_minus", "ENDF_B_VIII1_H1_MT102", "PHYS81_COLD_np_d_gamma",
                    "PHYS81_COLD_pd_h_gamma", "PHYS81_COLD_nd_t_gamma"}
        electronic = {
            (1, "target_forward"): ("VF96_PI_Z1_N1",), (1, "target_reverse"): ("VF96_RR_Z1_N1",),
            (2, "target_forward"): ("VF96_PI_Z2_N2",), (2, "target_reverse"): ("VF96_RR_Z2_N2_fit_a", "VF96_RR_Z2_N2_fit_b"),
            (3, "target_forward"): ("VF96_PI_Z2_N1",), (3, "target_reverse"): ("VF96_RR_Z2_N1",),
        }
        for (tid, direction), prefixes in electronic.items():
            isotope_labels = ["H1", "D", "T"] if tid == 1 else ["He3", "He4"]
            ids = {prefix + ":" + isotope for prefix in prefixes for isotope in isotope_labels}
            actual = indexed(self.targets[tid]["directions"], "direction")[direction]["reused_R1_event_refs"]
            require({row["event_id"] for row in actual} == ids, "Electronic R1 isotope/fit alternatives lost")
            expected.update(ids)
        require(set(self.reused) == expected, "Required R1 read-only evidence set changed")
        for eid, row in self.reused.items():
            event, compiled = self.r1_events[eid], self.r1_compiled[eid]
            require(row["record_class"] == "REUSED_R1_COMPILED_EVIDENCE" and row["source_commit"] == R1_COMMIT
                    and row["recompiled"] is False, "R1 evidence rerun/relabelled")
            require(row["event_record_sha256"] == object_sha(event) and row["compiled_record_sha256"] == object_sha(compiled),
                    "R1 event/compiled row hash mismatch")
            require(row["provider_id"] == event["source_id"]
                    and row["provider_record_sha256"] == self.r1_providers[event["source_id"]]["record_sha256"], "R1 provider identity changed")
            require(row["physical_event_key_sha256"] == compiled["physical_event_key_sha256"]
                    and row["ownership_group_sha256"] == compiled["ownership_group_sha256"], "R1 ownership reference changed")
        referenced = {ref["event_id"] for target in self.targets.values() for direction in target["directions"]
                      for ref in direction["reused_R1_event_refs"]}
        referenced.update(ref["event_id"] for row in self.aliases.values() for ref in row["reused_R1_event_refs"])
        require(referenced == expected, "Dangling or omitted R1 evidence association")
        require(self.docs["reused_r1_evidence"]["recompiled_count"] == 0, "R1 recompilation recorded")
        # Read current bytes again at the end: only immutable scientific inputs,
        # not the root's legitimate later delivery/priority metadata, are pinned.
        for relative, expected_sha in FROZEN_INPUTS.items():
            if relative.startswith("../"):
                require(sha(self.read_bytes(BASE / relative)) == expected_sha, "Frozen R1/compiler bytes changed during audit")
        return {"saved_R1_references": len(expected), "R1_compiler_calls": 0,
                "old_249_suite_calls": 0, "R1_full_suite_calls": 0, "immutable_R1_hashes_unchanged": True}

    def coverage_and_budget_boundary(self):
        expected_counts = {"original_target_count": 19, "target_direction_count": 28,
                           "original_target_ids_removed_by_deduplication": 0, "conditional_model_family_count": 18,
                           "conditional_dossier_family_count": 13, "additional_model_closure_family_count": 5,
                           "new_declared_photonuclear_number_projections": 6, "new_conditional_forward_number_projections": 18,
                           "new_compiled_projection_count": 24, "reused_species_identity_count": 9, "new_species_identity_count": 0,
                           "reused_R1_event_reference_count": len(self.reused),
                           "explicit_additional_provider_packet_count": len(self.packet_pins) - 1}
        for key, value in expected_counts.items():
            require(self.coverage[key] == value, "Coverage count mismatch: " + key)
        counts_by_class = {kind: sum(row["record_class"] == kind for row in self.primary.values())
                           for kind in ("PRIMARY_SOURCE_ROW", "REUSED_CONDITIONAL_MODEL_OUTPUT")}
        require(self.coverage["primary_packet_class_counts"] == counts_by_class
                and self.coverage["new_primary_source_row_count"] == counts_by_class["PRIMARY_SOURCE_ROW"], "Dynamic provider counts inflated")
        for key in ("physical_state_branch_domain_admissions", "physical_rate_admissions", "physical_Q_admissions",
                    "actual_rate_evaluations", "actual_Q_evaluations", "old_249_checks_replayed", "R1_full_checks_replayed", "new_IVPs"):
            require(self.coverage[key] == 0, "Scientific admission/replay boundary changed: " + key)
        require(self.coverage["original_target_list_complete"] is True
                and self.coverage["all_target_physical_source_coverage"] is False
                and self.coverage["all_future_configured_species_processes_complete"] is False
                and self.coverage["global_physical_completion"] is None, "Target-list recovery promoted to full physical coverage")
        require(self.coverage["R1_source_commit"] == R1_COMMIT and self.coverage["HH_R10"] == "OFF"
                and self.coverage["L4_ready"] is False and self.coverage["production"] == "NOT_ISSUED", "Consumer/production boundary changed")
        require(self.docs["compiled"]["only_changed_inputs_compiled"] is True, "Old results included as new compilation")
        budget = self.contract["budgets"]
        require(all(budget[key] == 0 for key in ("PHYS91_primary_remaining", "PHYS91_reference_remaining", "PHYS91_Wolfram_remaining"))
                and all(budget[key] is None for key in ("historical_global_CPU_s", "historical_global_money", "global_remaining"))
                and budget["inherited_budget_reset"] is False, "Historical budgets reset/transferred")
        return {"coverage_counts": expected_counts, "dynamic_provider_classes": counts_by_class,
                "old_budgets_preserved": True, "admission": "source provenance and finite number columns only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry-dir", type=Path, default=BASE / "registry")
    parser.add_argument("--output", type=Path, default=BASE / "raw/PRIMARY_RESULTS.json")
    parser.add_argument("--primary-sha256", default=DEFAULT_PRIMARY_SHA)
    parser.add_argument("--additional-provider-packet", action="append", default=[], metavar="RELATIVE_PATH=SHA256")
    args = parser.parse_args()
    args.registry_dir = args.registry_dir.resolve()
    args.output = args.output.resolve()
    require(BASE in args.registry_dir.parents and not (BASE / "sources" in args.registry_dir.parents), "Expected additive R2 registry directory")
    require(BASE / "raw" in args.output.parents and args.output.name == "PRIMARY_RESULTS.json", "Result must be raw/[attempt/]PRIMARY_RESULTS.json")
    require(not args.output.exists(), "Result exists: preserve prior attempt; choose a new reviewed attempt path")
    packet_pins = {"sources/primary/PROVIDER_ROWS.json": args.primary_sha256}
    for argument in args.additional_provider_packet:
        relative, separator, expected_sha = argument.rpartition("=")
        path = (BASE / relative).resolve()
        require(separator and relative and not Path(relative).is_absolute() and BASE / "sources" in path.parents,
                "Explicit additional source packet path required")
        canonical_relative = str(path.relative_to(BASE))
        require(canonical_relative == relative and relative not in packet_pins, "Duplicate/noncanonical provider packet path")
        packet_pins[relative] = expected_sha
    require(all(re.fullmatch(r"[0-9a-f]{64}", value) for value in packet_pins.values()), "Exact expected packet SHA256 required")
    audit = Audit(args, packet_pins)
    audit.read_bytes(Path(__file__))
    if audit.run("LOAD_GENERATED_R2_OUTPUTS_ONLY", audit.initialize):
        for name, function in (
            ("FROZEN_INPUT_AND_BUILDER_IDENTITIES", audit.frozen_identities),
            ("ORIGINAL_19_IDS_28_DIRECTIONS_AND_OVERLAPS", audit.original_target_map),
            ("CONDITIONAL_18_FAMILIES_5_CLOSURES_AND_NATIVE_LITERALS", audit.conditional_models_and_aliases),
            ("NATIVE_PRIMARY_ROWS_PROVENANCE_UNITS_SUPPORT_AND_CLASSES", audit.native_primary_records),
            ("REUSED_SPECIES_AND_24_DECLARED_VERTICES", audit.species_and_declared_vertices),
            ("EXACT_NEW_BARYON_CHARGE_ELECTRON_LEPTON_COLUMNS", audit.exact_new_column_ledgers),
            ("PHYSICAL_FALSE_ENERGY_UNQUALIFIED_AND_PHOTON_BOUNDARY", audit.physical_admission_boundary),
            ("FOUR_PHOTON_SOURCE_CLASSES_AND_TARGET6_GAP", audit.photon_source_coverage),
            ("NACRE_NATIVE_SUPPORT_AND_MT5_ZERO_Q_NOT_PROMOTED", audit.native_units_support_and_MT5_Q),
            ("PROVIDER_DIRECTION_BINDINGS_AND_UNLISTED_ALIAS_EVIDENCE", audit.provider_directions_and_additional_aliases),
            ("UNCHANGED_R1_HASHED_REFERENCES_WITHOUT_RECOMPILATION", audit.unchanged_R1_references),
            ("DYNAMIC_COVERAGE_COUNTS_AND_PRESERVED_BUDGET_BOUNDARY", audit.coverage_and_budget_boundary),
        ):
            audit.run(name, function)
    passed = sum(row["status"] == "PASS" for row in audit.results)
    failed = sum(row["status"] == "FAIL" for row in audit.results)
    report = {"schema": "WU_TARGET19_PRIMARY_CHANGED_INPUT_AUDIT_V1", "status": "PASS_SCOPED" if not failed else "FAIL",
              "observed_UTC": datetime.now(timezone.utc).isoformat(), "check_groups": audit.results,
              "passed_groups": passed, "failed_groups": failed, "input_file_SHA256": audit.input_sha256,
              "explicit_packet_SHA256": packet_pins, "registry_directory": os.path.relpath(args.registry_dir, BASE),
              "scope": "saved R2 source/number outputs only; no rate/Q/state/consumer admission",
              "execution": {"builder_imports": 0, "compiler_imports": 0, "new_column_recompilations": 0,
                            "R1_recompilations": 0, "old_249_replays": 0, "R1_full_suite_replays": 0,
                            "native_rate_evaluations": 0, "physical_Q_evaluations": 0, "new_IVP": 0}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({"status": report["status"], "passed_groups": passed, "failed_groups": failed,
                      "output": str(args.output)}, ensure_ascii=False))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
