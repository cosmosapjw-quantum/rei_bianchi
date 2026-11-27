"""Source-bound HE consumer inventory; no cross-section or rate evaluation.

WU owns species and elementary processes; REC owns molecular state adapters.
This module projects immutable supplier records and exposes their data type.
Thermal collision integrals never become energy-resolved angular moments here.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import resource
import tempfile
import time
import xml.etree.ElementTree as ET


class IntakeError(ValueError):
    """A source identity, type, or selected physical input is unresolved."""


INPUT_BLOBS = {
    "wu_chem_fixtures.json": "1c5bc6ce212a59364fa895fc24c7874cf64ee355",
    "wu78_atomic_network.py": "cbc9c5bd0e2a6f9a56b4afc0fbc5ad6f5cba2de2",
    "rec_atomic_model.json": "73285c1585f8edca92487effe95e68448f3163b8",
    "wu79_source_evidence.json": "4a70da48e40fe22f92a43f4403207d8f91c4fa90",
    "mutationpp_collisions.xml": "d86bf74e05e6bcac9db67cfc03055621ebed2f8c",
    "rec_hd_adapter_contract.json": "d1baee35670785cab7c7f8dc6a847ef07fae6198",
}
SELECTED_SOURCE_LABELS = frozenset({
    "e-", "H", "H+", "H-", "H2", "H2+", "H3+", "He", "He+", "He++"
})
FIT_ARITY = {"Bruno-Eq(11)": 7, "Bruno-Eq(17)": 3, "Bruno-Eq(19)": 8}
REGISTRY_SCOPE = "CONSUMER_SOURCE_INTAKE_ONLY"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_pinned(path: Path, expected_blob: str) -> bytes:
    data = path.read_bytes()
    if git_blob(data) != expected_blob:
        raise IntakeError("SOURCE_BLOB_MISMATCH:" + path.name)
    return data


def _integer(value, label, *, minimum=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise IntakeError("NONINTEGER:" + label)
    if minimum is not None and value < minimum:
        raise IntakeError("INTEGER_RANGE:" + label)
    return value


def identity_key(record):
    """Exact source identity including isomer, signed charge, state, and pool."""
    comp = record.get("composition")
    if not isinstance(comp, list):
        raise IntakeError("COMPOSITION_REQUIRED")
    parts = []
    seen = set()
    for item in comp:
        z = _integer(item.get("Z"), "Z", minimum=0)
        a = _integer(item.get("A"), "A", minimum=1)
        count = _integer(item.get("count"), "count", minimum=1)
        isomer = item.get("isomer")
        if z > a or not isinstance(isomer, str) or not isomer:
            raise IntakeError("NUCLEUS_IDENTITY_INVALID")
        nuclear_key = (z, a, isomer)
        if nuclear_key in seen:
            raise IntakeError("DUPLICATE_COMPOSITION_ENTRY")
        seen.add(nuclear_key)
        parts.append((z, a, isomer, count))
    charge = _integer(record.get("charge"), "charge")
    state, pool = record.get("state"), record.get("pool")
    if not isinstance(state, str) or not state or not isinstance(pool, str) or not pool:
        raise IntakeError("STATE_AND_POOL_REQUIRED")
    return (tuple(sorted(parts)), charge, state, pool)


def project_wu_species(document):
    """Keep every supplied row, including explicitly synthetic extension rows."""
    catalog = document.get("species")
    if not isinstance(catalog, dict) or not catalog:
        raise IntakeError("WU_SPECIES_OBJECT_REQUIRED")
    projected, seen = [], set()
    for sid, record in catalog.items():
        if not isinstance(sid, str) or not sid or not isinstance(record, dict):
            raise IntakeError("WU_ROW_INVALID")
        key = identity_key(record)
        if key in seen:
            raise IntakeError("DUPLICATE_FULL_IDENTITY:" + sid)
        seen.add(key)
        synthetic = (record["state"] == "synthetic" or
                     any("synthetic" in p[2] for p in key[0]))
        projected.append({
            "supplier_species_id": sid,
            "composition": record["composition"],
            "charge": record["charge"], "state": record["state"], "pool": record["pool"],
            "full_identity_key": key,
            "source_pointer": "/species/" + sid,
            "supplier_fixture_qualification": document.get("physical_qualification"),
            "synthetic_extension": synthetic,
            "physical_source_admitted": False,
            "mass_kg": None, "mass_status": "SOURCE_AND_STATE_BINDING_PENDING",
        })
    return projected


def literal_assignments(source: str, names):
    """Read literal tables from the WU source without importing its solver."""
    wanted, found = set(names), {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    found[target.id] = ast.literal_eval(node.value)
    if set(found) != wanted:
        raise IntakeError("WU_LITERAL_TABLE_MISSING")
    return found


def _expression(node):
    attrs = dict(node.attrib)
    raw = " ".join((node.text or "").split())
    row = {"tag": node.tag, "attributes": attrs, "source_text": raw,
           "children": [_expression(child) for child in node]}
    if attrs.get("type") in FIT_ARITY:
        tokens = raw.split()
        if len(tokens) != FIT_ARITY[attrs["type"]]:
            raise IntakeError("COLLISION_FIT_ARITY:" + node.tag)
        from decimal import Decimal, InvalidOperation
        try:
            finite = all(Decimal(token).is_finite() for token in tokens)
        except InvalidOperation as error:
            raise IntakeError("COLLISION_COEFFICIENT_NOT_DECIMAL") from error
        if not finite:
            raise IntakeError("COLLISION_COEFFICIENT_NONFINITE")
        row["coefficient_decimal_strings"] = tokens
    return row


def parse_collision_inventory(xml_bytes, labels=SELECTED_SOURCE_LABELS):
    """Extract explicit pair records, preserving nested fits and source labels.

    No default, copied-species fit, endpoint clipping, or isotope substitution
    is executed.  Q(l,s)(T) is a thermal integral; it is not sigma_l(E).
    """
    root = ET.fromstring(xml_bytes)
    if root.tag != "collisions":
        raise IntakeError("COLLISION_ROOT_INVALID")
    records, seen = [], set()
    for index, pair in enumerate(root.findall("pair")):
        first, second = pair.attrib.get("s1"), pair.attrib.get("s2")
        if first not in labels or second not in labels:
            continue
        key = tuple(sorted((first, second)))
        if key in seen:
            raise IntakeError("DUPLICATE_EXPLICIT_PAIR:" + repr(key))
        seen.add(key)
        expressions = [_expression(child) for child in pair]
        records.append({
            "source_pair": [first, second], "source_pair_index": index,
            "source_xpath": f"/collisions/pair[@s1='{first}'][@s2='{second}']",
            "quantity_class": "THERMAL_COLLISION_INTEGRALS_AND_AUXILIARY_FITS",
            "expressions": expressions,
            "explicit_Q_tags": [x["tag"] for x in expressions if x["tag"].startswith("Q")],
            "physical_angular_law": False,
            "energy_resolved_sigma_l": False,
            "isotope_state_assignment": "UNRESOLVED_SOURCE_LABEL_ONLY",
            "domain_and_normalization_admission": "PER_SELECTED_CONSUMER_CONTRACT",
        })
    return {
        "schema": "he.explicit_thermal_source_inventory.v1",
        "source_blob": git_blob(xml_bytes),
        "source_sha256": hashlib.sha256(xml_bytes).hexdigest(),
        "source_labels": sorted(labels), "records": records,
        "defaults_evaluated": False, "coefficients_evaluated": False,
        "upstream_table_clip_option_executed": False,
        "missing_pair_policy": "INPUT_PENDING; no default or zero substitution",
        "source_quantity_boundary": "Qbar_l_s(T) is neither differential d_sigma/d_Omega nor sigma_l(E)",
    }


def require_quantity(provider, quantity):
    """Reject a requested observable that the supplied record does not carry."""
    if quantity not in provider.get("available_quantities", ()):
        raise IntakeError("SOURCE_QUANTITY_UNAVAILABLE:" + quantity)
    return provider


def require_physical_species(row):
    if row.get("synthetic_extension") or not row.get("physical_source_admitted"):
        raise IntakeError("PHYSICAL_SPECIES_BINDING_PENDING:" + row["supplier_species_id"])
    return row


def require_isotope_alias_assumption(row, source_label, assumption=None):
    """Require an explicit approximate mapping before using elemental labels.

    This is a consumer mapping request, not physical admission of isotope rates
    or a finite-mass kernel. Source mass/state and error evidence remain open.
    """
    comp = row["composition"]
    if row.get("synthetic_extension") or len(comp) != 1 or comp[0]["count"] != 1:
        raise IntakeError("ISOTOPE_ALIAS_REQUIRES_NUCLEAR_STATE")
    expected = row.get("transport_source_label_candidate")
    if not expected or source_label != expected:
        raise IntakeError("ISOTOPE_ALIAS_SOURCE_LABEL_MISMATCH")
    if (not isinstance(assumption, dict)
            or assumption.get("supplier_species_id") != row["supplier_species_id"]
            or assumption.get("source_label") != source_label
            or assumption.get("approximation") != "elemental_transport_reuse"
            or assumption.get("scope") != "consumer_mapping_only"):
        raise IntakeError("EXPLICIT_ISOTOPE_REUSE_ASSUMPTION_REQUIRED")
    return {"supplier_species_id": row["supplier_species_id"], "source_label": source_label,
            "assumption": dict(assumption), "status": "CONDITIONAL_ALIAS_ONLY",
            "mass_state_error_evidence": "PENDING", "physical_source_admitted": False}


def require_hd_source_node(contract, collider_id, temperature_K):
    """Validate a consumer request against the REC owner contract only.

    The returned object is a source pointer; no rates, level parser, inverse
    transition, p/o mixture, interpolation, or population evolution is computed.
    """
    shape, species = contract["inputs"]["shape"], contract["inputs"]["species"]
    if (isinstance(collider_id, bool) or not isinstance(collider_id, int)
            or collider_id not in species["collider_ids"]):
        raise IntakeError("HD_COLLIDER_ID_UNSUPPORTED")
    if isinstance(temperature_K, bool) or temperature_K not in shape["temperature_nodes_K"]:
        raise IntakeError("HD_EXACT_SOURCE_T_NODE_REQUIRED")
    return {"owner": contract["lead_repo"], "collider_id": collider_id,
            "temperature_K": temperature_K, "adapter_state": contract["current_status"],
            "rate_supplied": False}


def _atomic_providers(tables, ci_evidence):
    out = []
    for i, (z, bound_electrons) in enumerate(tables["ELEMENT_IONS"]):
        photo, rr = tables["PHOTO_COEFFICIENTS"][i], tables["RR_COEFFICIENTS"][i]
        out.extend([
            {"id": f"WU78_PI_Z{z}_N{bound_electrons}", "process": "photoionization",
             "Z": z, "incoming_charge": z-bound_electrons,
             "available_quantities": ["elemental_total_photoabsorption_fit_parameters"],
             "parameters": dict(zip(("Eth_eV", "Emax_eV", "E0_eV", "sigma0_Mb", "ya", "P", "yw", "y0", "y1"), photo)),
             "source_file": "wu78_atomic_network.py", "source_symbol": "PHOTO_COEFFICIENTS", "source_row": i,
             "literature": "Verner et al. 1996 DOI:10.1086/177435",
             "isotope_policy": "ElementalElectronicEquality is an explicit approximation",
             "differential_or_recoil_provider": False},
            {"id": f"WU78_RR_Z{z}_N{bound_electrons}", "process": "radiative_recombination",
             "Z": z, "incoming_charge": z-bound_electrons+1,
             "available_quantities": ["case_A_thermal_number_rate_fit_parameters"],
             "parameters": dict(zip(("A_cm3_s", "b", "T0_K", "T1_K"), rr)),
             "supplier_runtime_temperature_domain_K": [3, 1000000000],
             "source_file": "wu78_atomic_network.py", "source_symbol": "RR_COEFFICIENTS", "source_row": i,
             "literature": "Verner & Ferland 1996 DOI:10.1086/192284",
             "isotope_policy": "ElementalElectronicEquality is an explicit approximation",
             "differential_or_recoil_provider": False},
        ])
    vor = next(x for x in ci_evidence["sources"] if x["id"] == "VORONOV1997")
    from decimal import Decimal
    for i, text in enumerate(vor["numeric_excerpt_verbatim"]):
        fields = text.split()[-9:]
        z, bound_electrons = int(fields[0]), int(fields[1])
        for token in fields[2:]:
            if not Decimal(token).is_finite():
                raise IntakeError("CI_COEFFICIENT_NONFINITE")
        out.append({
            "id": f"WU79_CI_Z{z}_N{bound_electrons}", "process": "electron_impact_ionization",
            "Z": z, "incoming_charge": z-bound_electrons,
            "available_quantities": ["Maxwellian_thermal_number_rate_fit_parameters"],
            "parameter_decimal_strings": dict(zip(("dE_eV", "P", "A_cm3_s", "X", "K", "Tmin_eV", "Tmax_keV"), fields[2:])),
            "source_file": "wu79_source_evidence.json", "source_pointer": f"/sources/0/numeric_excerpt_verbatim/{i}",
            "original_remote_bytes_verified": False,
            "source_qualification": "preserved WU primary-text extraction, not original ASCII byte recovery",
            "literature": "Voronov 1997 DOI:10.1006/adnd.1997.0732",
            "domain_convention": "Tmin in eV; Tmax in keV; fit dE is not substituted into binding ledger",
            "isotope_policy": "ElementalElectronicEquality is an explicit approximation",
            "differential_or_recoil_provider": False,
        })
    return out


def build(source_directory: Path):
    raw = {name: read_pinned(source_directory/"raw"/name, blob)
           for name, blob in INPUT_BLOBS.items()}
    wu = json.loads(raw["wu_chem_fixtures.json"])
    rows = project_wu_species(wu)
    tables = literal_assignments(raw["wu78_atomic_network.py"].decode(),
                                ("_ISOTOPE_DATA", "ELEMENT_IONS", "PHOTO_COEFFICIENTS", "RR_COEFFICIENTS"))
    rec = json.loads(raw["rec_atomic_model.json"])
    providers = _atomic_providers(tables, json.loads(raw["wu79_source_evidence.json"]))
    by_nucleus = {(z, a): name for name, a, z in tables["_ISOTOPE_DATA"]}
    roman = ("I", "II", "III", "IV")
    rec_seen = set()
    for row in rows:
        comp, charge = row["composition"], row["charge"]
        single = (len(comp) == 1 and comp[0]["count"] == 1 and comp[0]["isomer"] == "ground")
        nucleus = (comp[0]["Z"], comp[0]["A"]) if single else None
        iso = by_nucleus.get(nucleus)
        baseline = (not row["synthetic_extension"] and single and iso is not None
                    and 0 <= charge <= nucleus[0])
        neutron = row["supplier_species_id"] == "n" and nucleus == (0, 1) and charge == 0
        electron = not comp and charge == -1 and row["pool"] in ("electron_thermal", "electron_fast")
        row["catalog_role"] = ("initial_atomic_view" if baseline else "neutron" if neutron
                               else "free_electron_pool" if electron else "synthetic_extension" if row["synthetic_extension"]
                               else "additional_supplier_row_pending")
        row["scalar_provider_ids"] = [p["id"] for p in providers if baseline and p["Z"] == nucleus[0] and p["incoming_charge"] == charge]
        row["differential_exchange_status"] = "SOURCE_INPUT_PENDING"
        row["mass_number_is_mass_kg"] = False
        if baseline or neutron:
            label = iso + roman[charge] if baseline else "n"
            if label not in rec["species_order"]:
                raise IntakeError("REC_BASELINE_IDENTITY_MISSING:" + label)
            rec_seen.add(label)
            row["rec_population_crosswalk"] = {"label": label, "index": rec["species_order"].index(label),
                                              "source_file": "rec_atomic_model.json", "source_pointer": "/species_order"}
        if electron:
            row["rec_population_crosswalk"] = {"label": "derived charge-neutrality electron count",
                                              "index": None, "qualification": "REC119 has no independent fast-electron population; do not map e_fast into e_th"}
        row["transport_source_label_candidate"] = (
            "e-" if electron else ("H" if nucleus[0] == 1 else "He" if nucleus[0] == 2 else "Li") + "+"*charge if baseline else None)
        row["transport_candidate_binding"] = "requires explicit source isotope/state/mass and distribution convention"
    if rec_seen != set(rec["species_order"]):
        raise IntakeError("REC_BASELINE_COVERAGE_MISMATCH")
    molecular = json.loads(raw["rec_hd_adapter_contract.json"])
    summary = {"all_supplied_rows": len(rows),
               "initial_atomic_charge_states": sum(r["catalog_role"] == "initial_atomic_view" for r in rows),
               "neutron_slots": sum(r["catalog_role"] == "neutron" for r in rows),
               "electron_pool_slots": sum(r["catalog_role"] == "free_electron_pool" for r in rows),
               "synthetic_extensions": sum(r["synthetic_extension"] for r in rows),
               "elemental_scalar_provider_records": len(providers),
               "source_qualified_full_differential_providers": 0}
    registry = {
        "schema": "he.wu_consumer_provider_inventory.v1", "scope": REGISTRY_SCOPE,
        "authority": {"species_and_elementary_events": "cosmosapjw-quantum/WU088_HH",
                      "spectra_and_molecular_adapter": "cosmosapjw-quantum/rec_bianchi",
                      "consumer": "cosmosapjw-quantum/BASS_HE"},
        "source_inputs": {name: {"git_blob": blob, "sha256": hashlib.sha256(raw[name]).hexdigest(),
                                 "local_path": "../sources/raw/" + name} for name, blob in INPUT_BLOBS.items()},
        "summary": summary, "species": rows, "scalar_provider_records": providers,
        "REC_HD_owner_pointer": {
            "contract_file": "../sources/raw/rec_hd_adapter_contract.json", "lead": molecular["lead_repo"],
            "observed_contract_status": molecular["current_status"],
            "source_dataset": molecular["inputs"]["dataset"],
            "target_and_colliders": molecular["inputs"]["species"],
            "quantity": "source-selected level-to-level Maxwellian rates; no differential collision law",
            "HE_action": "consume REC output after its own source/state/domain admission; do not duplicate parser",
            "p_o_mix_performed": False, "extrapolation_performed": False,
            "WU_H1D_synthetic_state_relabelled": False,
        },
        "unresolved": {
            "all_target_joint_laws": "same-event electron/recoil correlation, count, spin/exchange, support and source uncertainty",
            "finite_mass": "actual species/charge/state masses and source-consistent isotope dependence; A is not a mass in kg",
            "thermalization": "distribution-dependent transfer kernel; rate/cross-section/heat-capacity are distinct",
            "remaining_species": "source-selected nuclei/isomers/anions/molecules remain extensible; synthetic fixtures retain their type",
        },
        "physical_provider_admitted": False, "global_physical_completion": None,
        "historical_compiler_checks_rerun": False, "scientific_solve_or_fit_evaluation": False,
    }
    return registry, parse_collision_inventory(raw["mutationpp_collisions.xml"])


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        name = handle.name
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(name, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, default=Path(__file__).resolve().parents[1]/"sources")
    parser.add_argument("--output-directory", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    registry, transport = build(args.source_directory)
    products = {"SPECIES_PROVIDER_REGISTRY.json": registry,
                "EXPLICIT_TRANSPORT_SOURCE_INVENTORY.json": transport}
    for filename, obj in products.items():
        _atomic_write(args.output_directory/filename, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    receipt = {"schema": "he.source_extraction_receipt.v1", "scope": "source parsing and immutable metadata extraction",
               "status": "completed", "exit_code": 0, "scientific_evaluation_count": 0,
               "summary": registry["summary"], "explicit_transport_pairs": len(transport["records"]),
               "cpu_s": time.process_time()-cpu_start, "wall_s": time.perf_counter()-wall_start,
               "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "measurement_scope": "build-and-save interval inside this Python process; interpreter startup excluded",
               "validation_suite": "NOT_RUN_BY_BUILDER", "HE101_replay": 0,
               "products": {name: {"sha256": hashlib.sha256((args.output_directory/name).read_bytes()).hexdigest(),
                                    "bytes": (args.output_directory/name).stat().st_size} for name in products}}
    _atomic_write(args.output_directory/"SOURCE_EXTRACTION_RECEIPT.json", json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
