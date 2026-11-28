"""Additive source-registry builder for the recovered nineteen target IDs.

Only new declared number projections call the unchanged R1 adapter/compiler.
The builder does not evaluate coefficients, Q values, reverse rates or old checks.
Preparation is inert: execution is solely through the explicit main entry point.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
R1 = BASE.parent / "provider_registry_20261025"
RECOVERED = BASE / "sources/recovered_network"
PRIMARY = BASE / "sources/primary/PROVIDER_ROWS.json"
R1_SOURCE_COMMIT = "18a6804d7cbe4879701e83631f7e908bbb84cef1"
COMPILER_SHA256 = "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af"
FROZEN_INPUTS = {
    "CONTRACT.json": "d4e89c891ec114ce911cb7e4dfc4779a8d19b2735d00cebe3fc07b2d718c21a4",
    "authority/AGENTS_AT_INPUT_FREEZE.md": "95851155333f8e9f532fe7f0fd353494f4403bc419019fff90d97fed58c7e189",
    "../provider_registry_20261025/registry_adapter.py": "9a093eed42f9ff5858d7bae11c726988ddbde4feeed38888b1c90fe329be816c",
    "../provider_registry_20261025/registry/species.json": "a18052f6db432192e1e0d4c75f8f2d49c71f3a5eb7cac206e7bc445fec2e8f80",
    "../provider_registry_20261025/registry/providers.json": "23d5bee7323a083d23a8a811eb7312a35c0eb613381ce28a22a5f989b1077664",
    "../provider_registry_20261025/registry/events.json": "abeea067660b0898315935ffd07bb6a443bbb1bd6111c700215b72be220baa90",
    "../provider_registry_20261025/registry/compiled.json": "d4836befd465ebd8130e5fd1f910b1fea30348c5e5785bfc66f8275735123f8c",
    "../rei_chem_ledger_20261025/chem_ledger.py": COMPILER_SHA256,
    "sources/recovered_network/TARGET_NETWORK_19_c9deb93.json": "96466ae646905c7f47509ea30898f677d12b922571e23d166426bf223fbf889a",
    "sources/recovered_network/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json": "68f69ea6288f3ba45abe4ef9416b3d0cbe507f61543a4ff045ad914061acbe3c",
    "sources/recovered_network/primordial_target_network.png": "472ba6be633d2b5fc05fc1e0e88f965ff3c0311b0697e3c35c05bbca1629e6f9",
}
PHOTONUCLEAR_IDS = {4, 5, 6, 7, 8, 11}
PRIMARY_CLASSES = {"PRIMARY_SOURCE_ROW", "REUSED_CONDITIONAL_MODEL_OUTPUT"}
PHOTO_SOURCE_COVERAGE = {
    "EXCLUSIVE_NATIVE_CHANNEL", "FACTORIZED_EXCLUSIVE_CANDIDATE", "INCLUSIVE_ONLY",
    "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT",
}
TARGET_URL = (
    "https://github.com/cosmosapjw-quantum/rei_bianchi/blob/"
    "c9deb933761a8d2593d1176aee028cd423bdbc05/"
    "research/atomic_nuclear_ssot_20261017/run19/metals/network/TARGET_NETWORK_19.json"
)
MODEL_URL = (
    "https://github.com/cosmosapjw-quantum/rei_bianchi/blob/"
    "9620e1fcc4bdda76e0311206f614234926600381/"
    "research/rei_tritium_production_audit_20261022/NUCLEAR_NETWORK_CONTRACT.json"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def raw_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def unique_rows(rows, id_key):
    result = {}
    for row in rows:
        identity = row[id_key]
        require(identity not in result, "DUPLICATE_RECORD_ID:" + str(identity))
        result[identity] = row
    return result


def frozen_input_receipt(primary_sha256, additional_packets=()):
    receipt = []
    for relative, expected in FROZEN_INPUTS.items():
        path = BASE / relative
        actual = raw_sha(path)
        require(actual == expected, "FROZEN_INPUT_CHANGED:" + relative)
        receipt.append({"file": relative, "bytes": path.stat().st_size,
                        "sha256": actual, "expected_sha256_match": True})
    if PRIMARY.exists():
        require(bool(primary_sha256), "EXPLICIT_FINAL_PRIMARY_PACKET_SHA256_REQUIRED")
        require(re.fullmatch(r"[0-9a-f]{64}", primary_sha256) is not None,
                "INVALID_PRIMARY_PACKET_SHA256")
        actual = raw_sha(PRIMARY)
        require(actual == primary_sha256, "PRIMARY_PACKET_CHANGED_AFTER_FREEZE")
        receipt.append({"file": "sources/primary/PROVIDER_ROWS.json",
                        "bytes": PRIMARY.stat().st_size, "sha256": actual,
                        "expected_sha256_match": True})
    else:
        require(primary_sha256 is None, "FROZEN_PRIMARY_PACKET_NOT_FOUND")
    seen = {PRIMARY.resolve()}
    for relative, expected in additional_packets:
        path = (BASE / relative).resolve()
        require(not Path(relative).is_absolute() and (BASE / "sources") in path.parents,
                "ADDITIONAL_PACKET_MUST_BE_EXPLICIT_R2_SOURCE_PATH")
        require(path not in seen, "DUPLICATE_ADDITIONAL_PROVIDER_PACKET")
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                "INVALID_ADDITIONAL_PACKET_SHA256")
        seen.add(path)
        actual = raw_sha(path)
        require(actual == expected, "ADDITIONAL_PACKET_CHANGED_AFTER_FREEZE:" + relative)
        receipt.append({"file": relative, "bytes": path.stat().st_size,
                        "sha256": actual, "expected_sha256_match": True})
    return receipt


def load_r1_adapter():
    # Import only the adapter, never R1's builder or its validation suites.
    sys.dont_write_bytecode = True
    name = "frozen_r1_registry_adapter_for_network19"
    spec = importlib.util.spec_from_file_location(name, R1 / "registry_adapter.py")
    require(spec is not None and spec.loader is not None, "R1_ADAPTER_NOT_LOADABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    require(module.COMPILER_SHA256 == COMPILER_SHA256, "COMPILER_BINDING_CHANGED")
    return module


def make_source_ref(file, sha256, locator, url):
    return {"file": file, "sha256": sha256, "locator": locator, "url": url}


def primary_records(families, targets, packet_paths):
    """Keep native primary/derived records intact; bind only explicit direction IDs."""
    result = {}
    verified_files = {}
    for packet_path in packet_paths:
        payload = read_json(packet_path)
        require(isinstance(payload.get("rows"), list), "PRIMARY_ROWS_MUST_BE_A_LIST")
        for row in payload["rows"]:
            for key in ("id", "record_class", "family_ids", "target_ids", "direction",
                        "raw_values", "uncertainty", "source_url",
                        "source_SHA256", "source_file", "locator", "new_rate_admission", "new_Q_admission"):
                require(key in row, "PRIMARY_ROW_MISSING:" + key)
            units_key = "units" if "units" in row else "native_units"
            support_key = "support" if "support" in row else "native_support"
            require(units_key in row and support_key in row, "NATIVE_UNITS_AND_SUPPORT_REQUIRED")
            pid = row["id"]
            require(isinstance(pid, str) and pid and pid not in result,
                    "INVALID_OR_DUPLICATE_PRIMARY_ID:" + str(pid))
            require(row["record_class"] in PRIMARY_CLASSES, "UNKNOWN_PRIMARY_RECORD_CLASS:" + pid)
            require(row["direction"] in ("family_forward", "family_reverse", "target_forward"),
                    "UNSUPPORTED_PRIMARY_DIRECTION:" + pid)
            require(row["new_rate_admission"] is False and row["new_Q_admission"] is False,
                    "PRIMARY_PACKET_CANNOT_ACTIVATE_PHYSICS:" + pid)
            require(row.get("default_active", False) is False,
                    "PRIMARY_SOURCE_CANNOT_BE_DEFAULT_ACTIVE:" + pid)
            require(row.get("activation", False) is False, "PRIMARY_SOURCE_CANNOT_ACTIVATE:" + pid)
            require(isinstance(row["source_SHA256"], str)
                    and re.fullmatch(r"[0-9a-f]{64}", row["source_SHA256"]) is not None,
                    "EXPLICIT_RAW_SOURCE_SHA256_REQUIRED:" + pid)
            source_path = (packet_path.parent / row["source_file"]).resolve()
            require(packet_path.parent.resolve() in source_path.parents,
                    "PRIMARY_RAW_SOURCE_MUST_BE_IN_PACKET:" + pid)
            if source_path.exists():
                if source_path not in verified_files:
                    verified_files[source_path] = raw_sha(source_path)
                require(verified_files[source_path] == row["source_SHA256"],
                        "PRIMARY_RAW_SOURCE_IDENTITY_MISMATCH:" + pid)
                source_check = "PACKAGED_RAW_BYTES_HASH_VERIFIED"
            else:
                # A public source subset may omit non-CC full text while retaining
                # numeric excerpts and the frozen intake/review provenance.
                availability = row.get("publication_source_availability", {})
                require(availability.get("original_bytes_bundled") is False,
                        "MISSING_RAW_SOURCE_WITHOUT_EXPLICIT_PUBLICATION_OMISSION:" + pid)
                source_check = "RAW_SOURCE_NOT_PACKAGED; RETAINED_HASH_AND_INTAKE_REVIEW_REQUIRED"
            require(isinstance(row["family_ids"], list) and row["family_ids"],
                    "EXPLICIT_FAMILY_BINDING_REQUIRED:" + pid)
            require(len(set(row["family_ids"])) == len(row["family_ids"]),
                    "DUPLICATE_PRIMARY_FAMILY_BINDING:" + pid)
            allowed_targets = set()
            for fid in row["family_ids"]:
                require(fid in families, "UNKNOWN_PRIMARY_FAMILY:" + str(fid))
                allowed_targets.update(families[fid]["dossier_ids"])
            require(isinstance(row["target_ids"], list)
                    and all(type(t) is int and t in targets for t in row["target_ids"]),
                    "INVALID_PRIMARY_TARGET_IDS:" + pid)
            require(len(set(row["target_ids"])) == len(row["target_ids"]),
                    "DUPLICATE_PRIMARY_TARGET_BINDING:" + pid)
            require(set(row["target_ids"]) <= allowed_targets,
                    "PRIMARY_TARGET_FAMILY_MISMATCH:" + pid)
            if row["direction"] == "family_forward":
                directions = {str(t): ("target_reverse" if t in PHOTONUCLEAR_IDS
                                       else "target_forward") for t in row["target_ids"]}
            elif row["direction"] == "family_reverse":
                require(bool(row["target_ids"]), "EXPLICIT_REVERSE_SOURCE_TARGETS_REQUIRED:" + pid)
                directions = {str(t): ("target_forward" if t in PHOTONUCLEAR_IDS
                                       else "target_reverse") for t in row["target_ids"]}
            else:
                require(bool(row["target_ids"]) and set(row["target_ids"]) <= PHOTONUCLEAR_IDS,
                        "DIRECT_PHOTONUCLEAR_PACKET_REQUIRES_EXPLICIT_TARGETS:" + pid)
                directions = {str(t): "target_forward" for t in row["target_ids"]}
            if "target_directions" in row:
                require(row["target_directions"] == directions,
                        "PRIMARY_DIRECTION_ALIAS_MISMATCH:" + pid)
            binds_photo_forward = any(int(tid) in PHOTONUCLEAR_IDS and direction == "target_forward"
                                      for tid, direction in directions.items())
            if binds_photo_forward:
                require(row.get("source_coverage") in PHOTO_SOURCE_COVERAGE,
                        "EXPLICIT_PHOTO_SOURCE_COVERAGE_REQUIRED:" + pid)
                expected_exclusive = row["source_coverage"] == "EXCLUSIVE_NATIVE_CHANNEL"
                require(row.get("exclusive_channel_binding") is expected_exclusive,
                        "PHOTONUCLEAR_EXCLUSIVE_BINDING_CONTRADICTION:" + pid)
            result[pid] = {
                "id": pid, "record_class": row["record_class"],
                "record_sha256": digest(row), "native_record": deepcopy(row),
                "payload_ref": {"file": str(packet_path.relative_to(BASE)),
                                "container": "rows", "match": {"id": pid}},
                "raw_source_byte_check": source_check,
                "native_field_names": {"units": units_key, "support": support_key},
                "target_direction_bindings": directions,
                "binding_qualification": "REACTION_FAMILY_AND_DIRECTION_ONLY; STATE_BRANCH_DOMAIN_NOT_ADMITTED",
                "new_rate_admission": False, "new_Q_admission": False,
            }
    return result


def assemble(primary_sha256=None, additional_provider_packets=()):
    input_files = frozen_input_receipt(primary_sha256, additional_provider_packets)
    contract = read_json(BASE / "CONTRACT.json")
    target_document = read_json(RECOVERED / "TARGET_NETWORK_19_c9deb93.json")
    model_path = RECOVERED / "REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json"
    model_text = model_path.read_text(encoding="utf-8")
    model = json.loads(model_text)
    targets = unique_rows(target_document["reactions"], "id")
    families = unique_rows(model["families"], "id")
    require(set(targets) == set(range(1, 20)), "ALL_ORIGINAL_19_IDS_REQUIRED")
    require(len(families) == 18 and model["family_count"] == 18, "CONDITIONAL_18_REQUIRED")
    require(contract["base_source_commit"] == R1_SOURCE_COMMIT, "R1_SOURCE_COMMIT_CHANGED")
    require(target_document["source_image"]["bytes"] == 1856861,
            "UNEXPECTED_IMAGE_BYTE_IDENTITY")
    require(target_document["source_image"]["sha256"] == raw_sha(RECOVERED / "primordial_target_network.png"),
            "IMAGE_CONTRACT_IDENTITY_MISMATCH")
    target_to_family = {}
    for fid, family in families.items():
        for tid in family["dossier_ids"]:
            require(tid not in target_to_family, "AMBIGUOUS_DOSSIER_FAMILY:" + str(tid))
            target_to_family[tid] = fid
    require(set(target_to_family) == set(range(4, 20)), "NUCLEAR_TARGET_ALIAS_COVERAGE_CHANGED")

    r1_species = read_json(R1 / "registry/species.json")["rows"]
    r1_providers = read_json(R1 / "registry/providers.json")["rows"]
    r1_events = unique_rows(read_json(R1 / "registry/events.json")["rows"], "id")
    r1_compiled = unique_rows(read_json(R1 / "registry/compiled.json")["rows"], "event_id")
    require(isinstance(r1_species, dict) and isinstance(r1_providers, dict), "R1_MAPPING_SCHEMA_CHANGED")
    adapter = load_r1_adapter()

    # These are declared structural coordinates. The image and inclusive source
    # tables do not themselves select bare, nuclear-ground product states.
    species = {}
    bare_ids = {}
    for label, a, z in zip(model["nuclear_state_order"], model["A"], model["Z"]):
        wanted = {"composition": [{"Z": z, "A": a, "isomer": "ground", "count": 1}],
                  "charge": z, "state": "bare_nucleus", "pool": "material"}
        matches = [sid for sid, row in r1_species.items() if row["compiler_record"] == wanted]
        require(len(matches) == 1, "UNAMBIGUOUS_REUSED_BARE_IDENTITY_REQUIRED:" + label)
        bare_ids[label] = matches[0]
        species[matches[0]] = deepcopy(r1_species[matches[0]])
    electron_record = {"composition": [], "charge": -1, "state": "free_electron", "pool": "electron_fast"}
    electron_ids = [sid for sid, row in r1_species.items() if row["compiler_record"] == electron_record]
    require(len(electron_ids) == 1, "UNAMBIGUOUS_REUSED_BETA_ELECTRON_IDENTITY_REQUIRED")
    beta_electron = electron_ids[0]
    species[beta_electron] = deepcopy(r1_species[beta_electron])

    def material_side(native):
        result = defaultdict(int)
        for label, count in native.items():
            require(type(count) is int and count > 0, "POSITIVE_INTEGER_MULTIPLICITY_REQUIRED")
            normalized = "H1" if label == "p" else label
            require(normalized in bare_ids, "UNRESOLVED_DECLARED_NUCLEUS:" + label)
            result[bare_ids[normalized]] += count
        return sorted(result.items())

    packet_paths = ([PRIMARY] if PRIMARY.exists() else []) + [
        (BASE / relative).resolve() for relative, _sha in additional_provider_packets]
    primary = primary_records(families, targets, packet_paths)
    primary_by_family = defaultdict(list)
    primary_by_family_reverse = defaultdict(list)
    primary_by_photo_target = defaultdict(list)
    for pid, record in primary.items():
        if record["native_record"]["direction"] == "family_forward":
            for fid in record["native_record"]["family_ids"]:
                primary_by_family[fid].append(pid)
        else:
            for fid in record["native_record"]["family_ids"]:
                primary_by_family_reverse[fid].append(pid)
            for tid_string, direction in record["target_direction_bindings"].items():
                tid = int(tid_string)
                if tid in PHOTONUCLEAR_IDS and direction == "target_forward":
                    primary_by_photo_target[tid].append(pid)

    declarations = {}
    for tid, native in targets.items():
        pid = f"USER_TARGET19:{tid:02d}"
        declarations[pid] = {
            "id": pid, "record_class": "USER_TARGET_DECLARATION", "target_id": tid,
            "record_sha256": digest(native), "native_record": deepcopy(native),
            "source": make_source_ref("sources/recovered_network/TARGET_NETWORK_19_c9deb93.json",
                                      raw_sha(RECOVERED / "TARGET_NETWORK_19_c9deb93.json"),
                                      f"/reactions/{tid - 1}", TARGET_URL),
            "empirical_coefficient_supplied_by_image": False,
            "new_rate_admission": False, "new_Q_admission": False,
        }

    model_rows, events = {}, []
    model_event_ids, photo_event_ids = {}, {}
    state_assumptions = {
        "charge": "all material nuclei bare; chosen number projection, not image ionic placement",
        "nuclear_state": "R1 ground nuclear labels reused as declared coordinates; source isomer/state not thereby qualified",
        "inclusive_primary_states": "primary ground-plus-excited channels remain inclusive; no branch fractions or ground-only source binding",
        "beta_electron": "existing electron_fast count carrier; no energy distribution or thermal deposition assigned",
        "photons": "one schematic gamma token where declared; physical total multiplicity/cascade and energy unqualified",
        "normalization": "compiler reference-nucleus/proper-second event operator; no native coefficient normalization binding",
        "material_pools": "number projection only; instant thermalization is the historical conditional model assumption",
    }

    def event_row(eid, source, left, right, *, process, branch, external_in=(), external_out=(),
                  qualifier, source_class, family_id=None, target_id=None, native_rate=None):
        return {
            "id": eid, "source_id": source["id"], "source_identity": source["record_sha256"],
            "source_record_class": source_class, "family_id": family_id, "target_id": target_id,
            "reactants": left, "products": right, "kind": "nuclear", "process": process,
            "branch_id": branch, "external_reactants": list(external_in),
            "external_products": list(external_out),
            "domain": ("declared_model_T100_to_10000K_not_primary_validity" if family_id
                       else "user_target_declaration_no_cross_section_support"),
            "frame": "DECLARED_BARE_NUMBER_VERTEX_PHYSICAL_FRAME_UNBOUND",
            "state_resolution": "declared_bare_nuclear_ground_coordinates; source_state_branch_unqualified",
            "projection_qualification": qualifier,
            "projection_assumptions": deepcopy(state_assumptions),
            "ownership_slot": "one_physical_event_per_process_state_branch",
            "radiation_count_qualification": ("SCHEMATIC_GAMMA_TOKEN; TOTAL_MULTIPLICITY_AND_CASCADE_UNQUALIFIED"
                                                if external_in or process == "nuclear_capture"
                                                else "NO_PHOTON_MULTIPLICITY_ASSIGNED"),
            "physical_total_photon_count": None, "branch_fraction": None,
            "native_rate_record": native_rate, "native_Q_record": None,
            "source_uncertainty": {"parameter_covariance": None, "branch_probabilities": None,
                                   "Q_uncertainty": None, "absence_is_not_zero": True},
            "linked_primary_packet_record_refs": sorted(
                primary_by_family.get(family_id, []) if family_id
                else primary_by_photo_target.get(target_id, [])),
            "primary_binding_qualification": "FAMILY_AND_DIRECTION_ONLY; STATE_BRANCH_DOMAIN_NOT_BOUND",
            "remaining_obligations": ["source-native state and isotope/isomer binding",
                                      "actual daughter branching and radiation multiplicity",
                                      "native domain, rate normalization and consumer",
                                      "mass convention, physical Q and energy partitions"],
            "activation": False, "empirical_rate_admitted": False, "nuclear_Q_admitted": False,
            "rate_normalization_bound": False, "consumer_ACK": None,
            "reverse_rate_inferred": False,
        }

    for index, (fid, family) in enumerate(families.items()):
        pid = "COND18:" + fid
        lines = [(number, line) for number, line in enumerate(model_text.splitlines(), 1)
                 if re.search(r'"id"\s*:\s*"' + re.escape(fid) + r'"', line)]
        require(len(lines) == 1, "EXACT_CONDITIONAL_ROW_LOCATOR_REQUIRED:" + fid)
        number, raw_line = lines[0]
        literals = {}
        for key in ("S0_keV_b", "sigma2200_b"):
            if key in family:
                match = re.search(r'"' + key + r'"\s*:\s*([^,}]+)', raw_line)
                require(match is not None, "NUMERIC_LITERAL_NOT_FOUND:" + fid)
                literals[key] = match.group(1).strip()
        row = {
            "id": pid, "family_id": fid, "record_class": "DECLARED_CONDITIONAL_MODEL_ROW",
            "record_sha256": digest(family), "native_record": deepcopy(family),
            "source": make_source_ref("sources/recovered_network/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json",
                                      raw_sha(model_path), f"/families/{index}; line {number}", MODEL_URL),
            "raw_line_number": number, "raw_line": raw_line,
            "raw_numeric_literals": literals, "native_units": deepcopy(model["units"]),
            "conditional_temperature_K": deepcopy(model["temperature_K"]),
            "primary_validity_interval_inferred": False,
            "model_mode": model["mode"], "model_admission": model["admission"],
            "original_target_ids": list(family["dossier_ids"]),
            "additional_closure_only": not family["dossier_ids"],
            "source_state_resolution": "all-bare mode explicit; nuclear isomer/product excitation branches not resolved",
            "primary_record_refs": sorted(primary_by_family.get(fid, [])),
            "uncertainty": None, "uncertainty_absence_means_zero": False,
            "new_rate_admission": False, "new_Q_admission": False,
        }
        model_rows[pid] = row
        left = material_side(family["reactants"])
        right = material_side(family["products"])
        external = []
        if family["kind"] == "beta_minus":
            require(family.get("electrons_created") == 1 and family.get("antineutrinos_created") == 1,
                    "EXPLICIT_BETA_LEPTONS_REQUIRED:" + fid)
            right = sorted(right + [(beta_electron, 1)])
            external = [("antinu_e:escaping", 1)]
            process, branch = "weak_beta_minus", "beta_minus"
        elif family["kind"] == "radiative_capture":
            external = [("gamma:escaping", 1)]
            process, branch = "nuclear_capture", "nuclear_capture"
        else:
            require(family["kind"] == "binary_transfer", "UNKNOWN_CONDITIONAL_KIND:" + fid)
            process, branch = "nuclear_transfer", "declared_transfer:" + fid
        eid = "COND18_FORWARD:" + fid
        model_event_ids[fid] = eid
        events.append(event_row(
            eid, row, left, right, process=process, branch=branch, external_out=external,
            qualifier="DECLARED_CONDITIONAL_MODEL_FORWARD_NUMBER_PROJECTION_ONLY",
            source_class=row["record_class"], family_id=fid,
            native_rate={"conditional_record_ref": pid, "model": family["model"],
                         "raw_parameter_literals": literals, "evaluation": "NOT_EVALUATED",
                         "historical_inverse_rule_not_executed": family["reverse"]},
        ))

    for tid in sorted(PHOTONUCLEAR_IDS):
        native = targets[tid]
        sides = native["nuclear_stoichiometry"]
        eid = f"TARGET19_PHOTONUCLEAR:{tid:02d}"
        photo_event_ids[tid] = eid
        events.append(event_row(
            eid, declarations[f"USER_TARGET19:{tid:02d}"],
            material_side(sides["reactants"]), material_side(sides["products"]),
            process="nuclear_photodisintegration", branch=f"listed_target_branch:{tid:02d}",
            external_in=[("gamma:incident", 1)],
            qualifier="USER_DECLARATION_WITH_SEPARATE_BARE_GROUND_NUMBER_PROJECTION; NO_PHYSICAL_PHOTO_RATE_ADMISSION",
            source_class="USER_TARGET_DECLARATION", target_id=tid,
        ))

    # Only these 24 changed projections enter the frozen compiler. Reused R1
    # compiled rows are read as evidence and are never recompiled.
    compiled = [adapter.compile_event(event, species) for event in events]
    require(len(events) == 24 and len(compiled) == 24, "NEW_PROJECTION_COUNT_CHANGED")
    require(all(row["energy_status"] == "UNQUALIFIED:ENERGY" and row["Q_approved"] is False
                and row["activation"] is False and row["native_rate_evaluated"] is False
                for row in compiled), "NUMBER_PROJECTION_PROMOTED_PHYSICS")

    reused_events = {}

    def reuse(eid, role, projection_relation):
        require(eid in r1_events and eid in r1_compiled, "R1_REFERENCE_NOT_FOUND:" + eid)
        event, checked = r1_events[eid], r1_compiled[eid]
        pid = event["source_id"]
        require(pid in r1_providers, "R1_PROVIDER_REFERENCE_NOT_FOUND:" + pid)
        reused_events[eid] = {
            "id": eid, "record_class": "REUSED_R1_COMPILED_EVIDENCE", "source_commit": R1_SOURCE_COMMIT,
            "event_ref": {"file": "../provider_registry_20261025/registry/events.json", "match": {"id": eid}},
            "compiled_ref": {"file": "../provider_registry_20261025/registry/compiled.json", "match": {"event_id": eid}},
            "event_record_sha256": digest(event), "compiled_record_sha256": digest(checked),
            "provider_id": pid, "provider_record_sha256": r1_providers[pid]["record_sha256"],
            "physical_event_key_sha256": checked["physical_event_key_sha256"],
            "ownership_group_sha256": checked["ownership_group_sha256"],
            "projection_qualification": event["projection_qualification"],
            "state_resolution": event["state_resolution"], "recompiled": False,
        }
        return {"event_id": eid, "evidence_role": role, "projection_relation": projection_relation}

    r1_by_family = {
        "t_beta": [("NUBASE2020_T_beta_minus", "PRIMARY_SOURCE_ALREADY_RECOVERED"),
                   ("LiveChart_ENSDF_T_beta_minus", "PRIMARY_SOURCE_ALREADY_RECOVERED")],
        "n_beta": [("NUBASE2020_n_beta_minus", "PRIMARY_SOURCE_ALREADY_RECOVERED"),
                   ("LiveChart_ENSDF_n_beta_minus", "PRIMARY_SOURCE_ALREADY_RECOVERED")],
        "p_n_gamma": [("ENDF_B_VIII1_H1_MT102", "PRIMARY_SOURCE_ALREADY_RECOVERED"),
                      ("PHYS81_COLD_np_d_gamma", "REUSED_COLD_KINEMATICS_NO_RATE")],
        "p_d_gamma": [("PHYS81_COLD_pd_h_gamma", "REUSED_COLD_KINEMATICS_NO_RATE")],
        "d_n_gamma": [("PHYS81_COLD_nd_t_gamma", "REUSED_COLD_KINEMATICS_NO_RATE")],
    }

    def family_references(fid):
        relation = ("SAME_NUCLEAR_TRANSFORMATION_DIFFERENT_NEUTRAL_SPECTATOR_VS_BARE_PROJECTION"
                    if fid == "t_beta" else "REACTION_IDENTITY_REFERENCE; SOURCE_STATE_AND_DOMAIN_OBLIGATIONS_RETAINED")
        return [reuse(eid, role, relation) for eid, role in r1_by_family.get(fid, [])]

    def electronic_references(tid, direction):
        isotopes = ["H1", "D", "T"] if tid == 1 else ["He3", "He4"]
        if direction == "target_forward":
            prefix = {1: ["VF96_PI_Z1_N1"], 2: ["VF96_PI_Z2_N2"], 3: ["VF96_PI_Z2_N1"]}[tid]
        else:
            prefix = {1: ["VF96_RR_Z1_N1"], 2: ["VF96_RR_Z2_N2_fit_a", "VF96_RR_Z2_N2_fit_b"],
                      3: ["VF96_RR_Z2_N1"]}[tid]
        return [reuse(pid + ":" + isotope, "PRIMARY_ELECTRONIC_SOURCE_ALREADY_RECOVERED",
                      "EXPLICIT_ISOTOPE_BLIND_MODEL; PI_GROUND_AND_RR_TOTAL_CASE_A_NOT_EXACT_STATE_INVERSES")
                for pid in prefix for isotope in isotopes]

    target_rows = []
    for tid, native in targets.items():
        directions = ["target_forward"] + (["target_reverse"] if native["reversible_arrow_as_listed"] else [])
        fid = target_to_family.get(tid)
        direction_rows = []
        for direction in directions:
            new_events, conditional_refs, reused = [], [], []
            family_forward = direction == ("target_reverse" if tid in PHOTONUCLEAR_IDS else "target_forward")
            if tid <= 3:
                reused = electronic_references(tid, direction)
            elif family_forward:
                new_events = [model_event_ids[fid]]
                conditional_refs = ["COND18:" + fid]
                reused = family_references(fid)
            else:
                require(tid in photo_event_ids, "UNMAPPED_TARGET_DIRECTION")
                new_events = [photo_event_ids[tid]]
            provider_refs = {kind: [] for kind in PRIMARY_CLASSES}
            for pid, record in primary.items():
                if record["target_direction_bindings"].get(str(tid)) == direction:
                    provider_refs[record["record_class"]].append(pid)
            has_r1_rate_source = any("PRIMARY_" in row["evidence_role"] for row in reused)
            has_new_primary = bool(provider_refs["PRIMARY_SOURCE_ROW"])
            exclusive, factorized, inclusive, beam_averaged = [], [], [], []
            for pid in provider_refs["PRIMARY_SOURCE_ROW"]:
                source_coverage = primary[pid]["native_record"].get("source_coverage")
                if source_coverage == "EXCLUSIVE_NATIVE_CHANNEL":
                    exclusive.append(pid)
                elif source_coverage == "FACTORIZED_EXCLUSIVE_CANDIDATE":
                    factorized.append(pid)
                elif source_coverage == "INCLUSIVE_ONLY":
                    inclusive.append(pid)
                elif source_coverage == "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT":
                    beam_averaged.append(pid)
            status = ("SOURCE_RECORD_PRESENT_PHYSICAL_BINDING_UNISSUED" if has_new_primary or has_r1_rate_source
                      else "DECLARED_CONDITIONAL_MODEL_ONLY" if conditional_refs
                      else "TARGET_DECLARED_PRIMARY_SUPPLIER_MISSING")
            if tid in PHOTONUCLEAR_IDS and direction == "target_forward":
                status = ("EXCLUSIVE_NATIVE_CHANNEL_SOURCE_REFERENCE_PRESENT" if exclusive
                          else "EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT_POINTWISE_BINDING_UNRESOLVED" if beam_averaged
                          else "FACTORIZED_EXCLUSIVE_CANDIDATE_UNEVALUATED" if factorized
                          else "INCLUSIVE_SOURCE_ONLY_EXCLUSIVE_TARGET_UNRESOLVED" if inclusive
                          else "TARGET_DECLARED_PRIMARY_SUPPLIER_MISSING")
            direction_rows.append({
                "id": f"TARGET19:{tid:02d}:{direction}", "direction": direction,
                "meaning": "equation_as_listed" if direction == "target_forward" else "reverse_of_listed_arrow",
                "new_number_projection_event_ids": new_events,
                "conditional_forward_model_record_refs": conditional_refs,
                "primary_provider_refs": sorted(provider_refs["PRIMARY_SOURCE_ROW"]),
                "reused_conditional_model_output_refs": sorted(provider_refs["REUSED_CONDITIONAL_MODEL_OUTPUT"]),
                "reused_R1_event_refs": reused,
                "supplier_status": status,
                "has_primary_source_record_reference": has_new_primary or has_r1_rate_source,
                "exclusive_native_channel_source_refs": sorted(exclusive),
                "factorized_exclusive_candidate_refs": sorted(factorized),
                "inclusive_only_provider_refs": sorted(inclusive),
                "beam_averaged_provider_refs": sorted(beam_averaged),
                "factorized_source_product_evaluated": False,
                "selected_rate_provider": None, "branch_fraction": None, "physical_Q": None,
                "conditional_soft_field_zero_is_not_cross_section_zero": tid in PHOTONUCLEAR_IDS,
                "conditional_inverse_rule_reference_only": ("COND18:" + fid if tid in PHOTONUCLEAR_IDS
                                                              and direction == "target_forward" else None),
                "inverse_rate_generated": False, "physical_rate_admission": False,
                "physical_Q_admission": False, "activation": False,
                "state_branch_domain_admission": False,
            })
        additional_direction_evidence = []
        for direction in ("target_forward", "target_reverse"):
            if direction in directions:
                continue
            refs = sorted(pid for pid, record in primary.items()
                          if record["target_direction_bindings"].get(str(tid)) == direction)
            if refs:
                related_photo_events = [photo_event_ids[photo_id] for photo_id in sorted(PHOTONUCLEAR_IDS)
                                        if target_to_family[photo_id] == fid]
                additional_direction_evidence.append({
                    "direction": direction, "provider_record_refs": refs,
                    "related_number_projection_event_ids": related_photo_events,
                    "qualification": "ACTUAL_SOURCE_REFERENCE_BEYOND_LISTED_ARROW; NOT_AN_ADDITIONAL_ORIGINAL_TARGET_OBLIGATION",
                    "new_rate_admission": False, "new_Q_admission": False,
                })
        target_rows.append({
            "id": tid, "source_record_id": f"USER_TARGET19:{tid:02d}",
            "equation_as_listed": native["equation_as_listed"], "kind": native["kind"],
            "reversible_arrow_as_listed": native["reversible_arrow_as_listed"],
            "conditional_family_id": fid, "target_obligation_retained": True,
            "authoritative_scope": "right-hand user-image equation; source charge/isomer/branch not inferred",
            "directions": direction_rows,
            "additional_direction_evidence": additional_direction_evidence,
        })

    family_aliases = []
    for fid, family in families.items():
        family_aliases.append({
            "family_id": fid, "original_target_ids": family["dossier_ids"],
            "extra_conditional_closure": not family["dossier_ids"],
            "closure_reason": family.get("closure_reason"),
            "model_record_id": "COND18:" + fid, "new_model_event_id": model_event_ids[fid],
            "family_forward_primary_packet_record_refs": sorted(primary_by_family.get(fid, [])),
            "family_reverse_primary_packet_record_refs": sorted(primary_by_family_reverse.get(fid, [])),
            "reused_R1_event_refs": family_references(fid),
            "rate_selection": None,
            "rule": "one qualified rate source per event; target aliases and kinematic references are not additive event rates",
        })

    all_directions = [direction for row in target_rows for direction in row["directions"]]
    photo_directions = [direction for row in target_rows if row["id"] in PHOTONUCLEAR_IDS
                        for direction in row["directions"] if direction["direction"] == "target_forward"]
    require(len(all_directions) == 28, "ORIGINAL_DIRECTION_COUNT_CHANGED")
    primary_count = sum(row["record_class"] == "PRIMARY_SOURCE_ROW" for row in primary.values())
    output_class_counts = {kind: sum(row["record_class"] == kind for row in primary.values())
                           for kind in sorted(PRIMARY_CLASSES)}
    coverage = {
        "original_image_status": "RECOVERED_HASH_MATCHED_AND_VISUALLY_REVIEWED",
        "original_target_list_complete": True, "original_target_count": 19, "target_direction_count": 28,
        "original_target_ids_removed_by_deduplication": 0,
        "conditional_model_family_count": 18, "conditional_dossier_family_count": 13,
        "additional_model_closure_family_count": 5,
        "primary_packet_status": "PRESENT_FROZEN" if PRIMARY.exists() else "NOT_SUPPLIED_EXPLICIT_GAP",
        "explicit_additional_provider_packet_count": len(additional_provider_packets),
        "primary_packet_class_counts": output_class_counts, "new_primary_source_row_count": primary_count,
        "new_declared_photonuclear_number_projections": 6, "new_conditional_forward_number_projections": 18,
        "new_compiled_projection_count": len(compiled), "reused_species_identity_count": len(species),
        "new_species_identity_count": 0, "reused_R1_event_reference_count": len(reused_events),
        "target_directions_without_primary_source_record_reference": [
            r["id"] for r in all_directions if not r["has_primary_source_record_reference"]],
        "target_directions_with_only_declaration": [r["id"] for r in all_directions
                                                    if r["supplier_status"] == "TARGET_DECLARED_PRIMARY_SUPPLIER_MISSING"],
        "direct_photonuclear_source_coverage": {
            "listed_forward_direction_count": len(photo_directions),
            "exclusive_native_channel_source_count": sum(bool(r["exclusive_native_channel_source_refs"]) for r in photo_directions),
            "factorized_exclusive_candidate_count": sum(bool(r["factorized_exclusive_candidate_refs"]) for r in photo_directions),
            "inclusive_only_source_count": sum(bool(r["inclusive_only_provider_refs"]) for r in photo_directions),
            "beam_averaged_measurement_direction_count": sum(bool(r["beam_averaged_provider_refs"]) for r in photo_directions),
            "exclusive_source_binding_gaps": [r["id"] for r in photo_directions if not r["exclusive_native_channel_source_refs"]],
            "no_primary_source_record_reference": [r["id"] for r in photo_directions if not r["has_primary_source_record_reference"]],
            "factorization_products_evaluated": 0,
            "source_reference_is_not_physical_admission": True,
        },
        "physical_state_branch_domain_admissions": 0, "physical_rate_admissions": 0, "physical_Q_admissions": 0,
        "actual_rate_evaluations": 0, "actual_Q_evaluations": 0, "old_249_checks_replayed": 0,
        "R1_full_checks_replayed": 0, "new_IVPs": 0, "R1_source_commit": R1_SOURCE_COMMIT,
        "all_future_configured_species_processes_complete": False,
        "all_target_physical_source_coverage": False, "global_physical_completion": None,
        "HH_R10": "OFF", "L4_ready": False, "production": "NOT_ISSUED",
    }
    common = {"unit_id": contract["unit_id"], "R1_source_commit": R1_SOURCE_COMMIT}
    model_context = {key: deepcopy(model[key]) for key in (
        "mode", "mass_convention", "units", "rate_models", "source_sink_equation",
        "radiation_closure", "particle_closure", "electron_and_energy_closure",
        "outside_finite_network", "admission")}
    return {
        "inputs.json": {**common, "rows": input_files, "compiler_sha256": COMPILER_SHA256,
                        "scope": "new R2 projection build; frozen R1 results referenced without replay"},
        "target_declarations.json": {**common, "record_class": "USER_TARGET_DECLARATION", "rows": declarations},
        "targets.json": {**common, "rows": target_rows,
                         "overlaps": target_document["shared_forward_reverse_processes"],
                         "overlap_rule": target_document["overlap_rule"]},
        "conditional_models.json": {**common, "context": model_context, "rows": model_rows},
        "primary_providers.json": {**common, "rows": primary,
                                   "classes_are_distinct": True, "coefficient_evaluation": "NOT_RUN"},
        "species.json": {**common, "rows": species, "new_species_count": 0,
                         "projection_assumptions": state_assumptions},
        "events.json": {**common, "rows": events},
        "compiled.json": {**common, "rows": compiled, "only_changed_inputs_compiled": True},
        "reused_r1_evidence.json": {**common, "rows": reused_events, "recompiled_count": 0},
        "family_aliases.json": {**common, "rows": family_aliases,
                               "aliases_are_not_additive_event_rates": True},
        "coverage.json": coverage,
    }


def write_outputs(output_dir, outputs):
    output_dir = Path(output_dir).resolve()
    require(output_dir == BASE / "registry" or BASE in output_dir.parents,
            "R2_OUTPUT_MUST_STAY_IN_ADDITIVE_LEAF")
    require(not (output_dir == RECOVERED or RECOVERED in output_dir.parents
                 or output_dir == BASE / "sources" or BASE / "sources" in output_dir.parents),
            "OUTPUT_CANNOT_OVERWRITE_SOURCE_PACKET")
    payloads = {name: (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
                for name, value in outputs.items()}
    # Check every existing destination before writing any changed result.
    for name, payload in payloads.items():
        path = output_dir / name
        require(not path.exists() or path.read_bytes() == payload,
                "OUTPUT_DIFFERS_USE_NEW_ATTEMPT_DIRECTORY:" + str(path))
    output_dir.mkdir(parents=True, exist_ok=True)
    disposition = {}
    for name, payload in payloads.items():
        path = output_dir / name
        if path.exists():
            disposition[name] = "reused_unchanged"
        else:
            with path.open("xb") as handle:
                handle.write(payload)
            disposition[name] = "created"
    return disposition


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=BASE / "registry")
    parser.add_argument("--primary-sha256", help="Expected SHA256 of the finalized optional primary packet")
    parser.add_argument("--additional-provider-packet", action="append", default=[], metavar="RELATIVE_PATH=SHA256",
                        help="Explicit separate source packet; never changes the frozen primary packet")
    args = parser.parse_args()
    additional = []
    for item in args.additional_provider_packet:
        relative, separator, expected = item.rpartition("=")
        require(bool(separator and relative and expected), "ADDITIONAL_PACKET_PATH_AND_SHA256_REQUIRED")
        additional.append((relative, expected))
    outputs = assemble(primary_sha256=args.primary_sha256, additional_provider_packets=additional)
    disposition = write_outputs(args.output_dir, outputs)
    print(json.dumps({"output": str(args.output_dir), "files": disposition,
                      "coverage": outputs["coverage.json"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
