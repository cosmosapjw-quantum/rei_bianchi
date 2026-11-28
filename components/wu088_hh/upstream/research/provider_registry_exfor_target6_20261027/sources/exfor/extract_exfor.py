#!/usr/bin/env python3
"""Extract four fixed-width, source-only EXFOR tables; never evaluate physics.

Only the pinned four official entries are read. Numeric cells remain strings.
The seven electric-quadrupole rows are auxiliary; CURVE rows stay raw only.
Run once with the R3 bounded runner. All outputs are create-only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
COMMIT = "939a14d7bba1ddce51975cb5e8711ce96b3b0871"
EXPECTED = {
    "M0011": ("20804471fb7584e07ab979ecad6a3e96cba0c6a2", "8d45af5ca4f0df3c000a5cf672cd84e2e8512b65b52b03a912c5080d2bf5d9b2"),
    "M0475": ("c49433293921dbb012d7f1b0387745732a598efa", "b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f"),
    "M0826": ("95010842754215e98eea8d99eff5f3de0799c666", "05ea65eaa1a7245f19fd47aa14e91bef3d706fe2a55c6d70a512808ee4e9284c"),
    "M0034": ("7bf684ee6f924c4a87d651a747bee08de1b8ae2d", "d1dbfa9e8899d91fa7c3993be6e22fd9d2aad0438084f09faf2906922eb3bd93"),
}
SELECTED = {
    "M0011002": (14, ["EN", "DATA", "ERR-S"], ["MEV", "MICRO-B", "MICRO-B"], "SIG", "AUTHOR_SUPPLIED_TABLE"),
    "M0475002": (12, ["EN", "ANG-CM", "DATA-CM", "ERR-S"], ["MEV", "ADEG", "NB/SR", "NB/SR"], "DA", "PUBLICATION_TABLE_1"),
    "M0475003": (6, ["EN", "DATA", "ERR-S"], ["MEV", "NB", "NB"], "SIG", "PUBLICATION_TABLE_2"),
    "M0826002": (4, ["EN-MIN", "EN-MAX", "DATA", "ERR-S"], ["MEV", "MEV", "MICRO-B", "MICRO-B"], "SIG", "PUBLICATION_TABLE_1"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def keyword(line):
    return line[:10].strip()


def blocks(lines):
    result = {}
    start = None
    for index, line in enumerate(lines):
        if keyword(line) == "SUBENT":
            require(start is None, "NESTED_SUBENTRY")
            identity = line.split()[1]
            start = index
        elif keyword(line) == "ENDSUBENT":
            require(start is not None and identity not in result, "INVALID_SUBENTRY_BOUNDARY")
            result[identity] = (start, index)
            start = None
    require(start is None, "UNCLOSED_SUBENTRY")
    return result


def selected_block(lines, start, end, begin_key, end_key):
    matches = [i for i in range(start, end + 1) if keyword(lines[i]) == begin_key]
    require(len(matches) == 1, "EXPECTED_ONE_BLOCK:" + begin_key)
    lo = matches[0]
    hi = next(i for i in range(lo + 1, end + 1) if keyword(lines[i]) == end_key)
    return {"line_start_1based": lo + 1, "line_end_1based": hi + 1,
            "raw_lines": lines[lo:hi + 1]}


def bib_fields(block):
    result = {}
    current = None
    for offset, line in enumerate(block["raw_lines"][1:-1], block["line_start_1based"] + 1):
        key = keyword(line)
        if key:
            require(key not in result, "UNEXPECTED_REPEATED_BIB_KEY:" + key)
            current = key
            result[key] = []
        require(current is not None, "BIB_CONTINUATION_WITHOUT_KEY")
        result[current].append({"line_1based": offset, "raw_line": line, "content": line[11:]})
    return result


def fixed_fields(line, count):
    require(count <= 6 and not line[66:].strip(), "SELECTED_TABLE_FORMAT_NOT_SUPPORTED")
    return [line.ljust(66)[11 * i:11 * (i + 1)] for i in range(count)]


def parse_table(lines, span):
    block = selected_block(lines, *span, "DATA", "ENDDATA")
    raw = block["raw_lines"]
    ncolumns, nrows = (int(x) for x in raw[0].split()[1:3])
    require(len(raw) == nrows + 4, "DATA_BLOCK_ROW_COUNT_MISMATCH")
    labels = [s.strip() for s in fixed_fields(raw[1], ncolumns)]
    units = [s.strip() for s in fixed_fields(raw[2], ncolumns)]
    require(len(set(labels)) == ncolumns, "DUPLICATED_DATA_HEADING")
    rows = []
    for index, line in enumerate(raw[3:-1]):
        cells = fixed_fields(line, ncolumns)
        values = dict(zip(labels, (cell.strip() for cell in cells)))
        require(all(re.fullmatch(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", x)
                    for x in values.values()), "NONLITERAL_OR_BLANK_SELECTED_CELL")
        rows.append({"source_line_1based": block["line_start_1based"] + 3 + index,
                     "source_row_1based": index + 1, "raw_line": line,
                     "fixed_width_cells": cells, "values": values})
    return {"columns": labels, "column_units": units, "row_count": nrows, "rows": rows,
            "header_line_1based": block["line_start_1based"] + 1,
            "units_line_1based": block["line_start_1based"] + 2,
            "DATA_line_1based": block["line_start_1based"],
            "ENDDATA_line_1based": block["line_end_1based"],
            "raw_header": raw[1], "raw_units": raw[2]}


def common_block(lines, span):
    lo, hi = span
    empty = [i for i in range(lo, hi + 1) if keyword(lines[i]) == "NOCOMMON"]
    if empty:
        require(len(empty) == 1, "MULTIPLE_NOCOMMON")
        return {"status": "NOCOMMON", "line_1based": empty[0] + 1, "raw_line": lines[empty[0]]}
    result = selected_block(lines, *span, "COMMON", "ENDCOMMON")
    result["status"] = "COMMON_NATIVE_BLOCK"
    return result


def source_record(entry, subentry, source, *, auxiliary=False):
    data, lines, subentries = source
    span, parent_span = subentries[subentry], subentries[entry + "001"]
    bib = selected_block(lines, *span, "BIB", "ENDBIB")
    parent_bib = selected_block(lines, *parent_span, "BIB", "ENDBIB")
    fields, parent_fields = bib_fields(bib), bib_fields(parent_bib)
    table = parse_table(lines, span)
    reaction = " ".join(row["content"].strip() for row in fields["REACTION"])
    require(reaction.startswith("(2-HE-4(G,D)1-H-2,"), "WRONG_EXCLUSIVE_SOURCE_REACTION")
    require("(TABLE)" in " ".join(row["content"] for row in fields["STATUS"]), "NON_TABLE_SOURCE_SELECTED")
    if auxiliary:
        quantity, status = "EP_SIG_POLAR2", "AUTHOR_SUPPLIED_E2_COMPONENT_TABLE"
        require(table["row_count"] == 7 and reaction == "(2-HE-4(G,D)1-H-2,EP,SIG)", "AUXILIARY_IDENTITY_CHANGED")
    else:
        nrows, columns, units, quantity, status = SELECTED[subentry]
        require((table["row_count"], table["columns"], table["column_units"]) == (nrows, columns, units), "SELECTED_HEADER_COUNT_OR_UNIT_CHANGED")
        require(reaction == "(2-HE-4(G,D)1-H-2,," + quantity + ")", "QUANTITY_CODE_CHANGED")
    energy_bin = "EN-MIN" in table["columns"]
    differential = quantity == "DA"
    beam_bound = None
    if entry == "M0826":
        beam_bound = {"quantity": "incident gamma beam intensity", "upper_bound_literal": "5.",
                      "unit": "percent", "relation": "not higher than", "EXFOR_code": "(ERR-SYS,,5.)",
                      "source_fields": parent_fields["ERR-ANALYS"],
                      "confidence_probability": None, "correlation_matrix": None,
                      "combined_with_statistical_error": False}
    native_units = dict(zip(table["columns"], table["column_units"]))
    url = f"https://github.com/IAEA-NDS/exfor_master/blob/{COMMIT}/exforall/{entry[:3]}/{entry}.x4"
    return {
        "id": "EXFOR_" + subentry, "record_class": "AUXILIARY_MULTIPOLE_SOURCE_ROW" if auxiliary else "PRIMARY_SOURCE_ROW",
        "source_kind": "OFFICIAL_EXFOR_AUTHOR_OR_PUBLICATION_TABLE", "source_status": status,
        "source_coverage": "EXCLUSIVE_CHANNEL_EXPERIMENTAL_TABLE", "exclusive_channel_binding": False,
        "source_reaction_identity_matches_target": True, "family_ids": ["d_d_gamma"], "target_ids": [6],
        "direction": "family_reverse", "target_directions": {"6": "target_forward"},
        "source_url": url, "source_file": f"raw/{entry}.x4", "source_SHA256": sha(data),
        "source_bytes": len(data), "source_git_blob_SHA1": EXPECTED[entry][0], "source_repository_commit": COMMIT,
        "source_entry_revision_date": lines[0].split()[2], "accession": entry, "subentry": subentry,
        "locator": {"subentry_line_start_1based": span[0] + 1, "subentry_line_end_1based": span[1] + 1,
                    "parent_subentry": entry + "001", "parent_line_start_1based": parent_span[0] + 1,
                    "parent_line_end_1based": parent_span[1] + 1,
                    "BIB": bib, "parent_BIB": parent_bib,
                    "COMMON": common_block(lines, span), "parent_COMMON": common_block(lines, parent_span)},
        "native_reaction": reaction, "native_BIB_fields": fields, "native_parent_BIB_fields": parent_fields,
        "raw_values": table, "units": native_units,
        "observable_kind": ("ELECTRIC_QUADRUPOLE_COMPONENT_SIG" if auxiliary else
                            "ANGULAR_DIFFERENTIAL_CROSS_SECTION_CM" if differential else
                            "ANGLE_AND_SECONDARY_ENERGY_INTEGRATED_SIG_WITH_INCIDENT_ENERGY_BIN" if energy_bin else
                            "ANGLE_AND_SECONDARY_ENERGY_INTEGRATED_SIG_AT_LISTED_EN"),
        "support": {"native_energy_headers": [key for key in table["columns"] if key.startswith("EN")],
                    "incident_energy_frame": "LAB_BY_EXFOR_HEADING_CONVENTION",
                    "angular_frame": "CM_EXPLICIT_ANG-CM_AND_DATA-CM" if differential else "NOT_AN_ANGULAR_DISTRIBUTION",
                    "native_energy_bin_edges_retained": energy_bin,
                    "incident_energy_response_or_bin_weights": None, "energy_resolution": None,
                    "angular_acceptance_width": None, "source_to_consumer_binding": False,
                    "energy_integral_sigma_dE": False, "interpolation_or_extrapolation_performed": False},
        "normalization": {"native_quantity": quantity, "native_data_heading": "DATA-CM" if differential else "DATA",
                          "definition_reference": "SEMANTICS_REFERENCE.json",
                          "identical_dd_particle_vs_event_counting": "UNRESOLVED_FROM_SELECTED_ENTRY",
                          "full_sphere_or_half_sphere_normalization": "UNRESOLVED_FROM_SELECTED_ENTRY",
                          "author_angular_integration_or_acceptance_extrapolation": "NOT_SPECIFIED_IN_SELECTED_ENTRY",
                          "new_factor_of_two_or_factorial_applied": False, "new_angular_integration_performed": False,
                          "native_coefficient_to_event_flux_binding": False},
        "uncertainty": {"statistical_column": "ERR-S", "native_unit": native_units["ERR-S"],
                        "literal_values": "raw_values.rows[*].values.ERR-S", "confidence_probability": None,
                        "source_ERR_ANALYS": parent_fields["ERR-ANALYS"], "beam_intensity_systematic_bound": beam_bound,
                        "other_systematic_uncertainty": None, "covariance": None, "combined_uncertainty": None,
                        "missing_uncertainty_is_zero": False},
        "state_resolution": {"source_target_nuclide": "2-HE-4", "source_emitted_particle": "D", "source_residual": "1-H-2",
                             "source_isotopes_explicit": True, "nuclear_isomer_or_excitation_binding": None,
                             "ionic_charge": None, "electronic_state": None, "source_native_state_bound_to_bare_projection": False},
        "branch": {"exclusive_nuclear_channel_identity": "He4(gamma,d)D", "products": {"D": 2},
                   "branch_fraction": None, "source_component": "E2" if auxiliary else "UNPARTITIONED_NATIVE_CHANNEL_SIG_OR_DA",
                   "auxiliary_added_to_total": False},
        "Q": {"value": None, "uncertainty": None, "mass_convention": None, "admitted": False},
        "primary_publication_references": parent_fields["REFERENCE"], "full_primary_paper_retrieved_for_this_packet": False,
        "source_license": "CC-BY-4.0; official EXFOR repository license, attribution retained in provenance/",
        "new_rate_admission": False, "new_Q_admission": False, "default_active": False, "activation": False,
        "source_value_evaluated_in_this_intake": False, "figure_digitization_performed": False,
    }


def main():
    sources, byte_checks = {}, []
    for entry, (blob, sha256) in EXPECTED.items():
        path = BASE / "raw" / (entry + ".x4")
        data = path.read_bytes()
        actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(sha(data) == sha256 and actual_blob == blob, "OFFICIAL_RAW_BYTE_IDENTITY_CHANGED:" + entry)
        require(data.endswith(b"\n") and b"\r" not in data, "RAW_LINE_ENDINGS_CHANGED")
        lines = data.decode("ascii").split("\n")[:-1]
        require(lines[0].split()[1] == entry and keyword(lines[-1]) == "ENDENTRY", "RAW_ENTRY_IDENTITY_CHANGED")
        sources[entry] = data, lines, blocks(lines)
        byte_checks.append({"file": str(path.relative_to(BASE)), "bytes": len(data), "sha256": sha256,
                            "git_blob_SHA1": blob, "both_identity_checks": "PASS"})
    rows = [source_record(subentry[:5], subentry, sources[subentry[:5]]) for subentry in SELECTED]
    auxiliary = source_record("M0011", "M0011003", sources["M0011"], auxiliary=True)
    require(auxiliary["locator"]["COMMON"]["raw_lines"][1:4] == ["POLAR", "NO-DIM", " 2."], "AUXILIARY_COMMON_CHANGED")
    main_count = sum(row["raw_values"]["row_count"] for row in rows)
    require(len(rows) == 4 and main_count == 36, "MAIN_PROVIDER_OR_ROW_COUNT_CHANGED")
    excluded = []
    for entry, subentry in (("M0826", "M0826003"), ("M0034", "M0034005"), ("M0034", "M0034006")):
        _data, lines, subentries = sources[entry]
        span = subentries[subentry]
        fields = bib_fields(selected_block(lines, *span, "BIB", "ENDBIB"))
        require("(CURVE" in " ".join(row["content"] for row in fields["STATUS"]), "EXCLUDED_STATUS_CHANGED")
        excluded.append({"accession": entry, "subentry": subentry, "source_file": f"raw/{entry}.x4",
                         "source_SHA256": EXPECTED[entry][1], "STATUS": fields["STATUS"],
                         "reason": "SOURCE_CURVE_ORIGIN; raw retained, no graph digitization or primary-table import",
                         "line_start_1based": span[0] + 1, "line_end_1based": span[1] + 1})
    outputs = {
        "PROVIDER_ROWS.json": {"schema": "WU_TARGET6_EXFOR_PRIMARY_ROWS_V1", "rows": rows,
                               "provider_variant_count": 4, "native_numeric_row_count": 36,
                               "integral_SIG_rows": 24, "angular_differential_DA_rows": 12,
                               "interpretation": "Source availability only; native observables remain distinct"},
        "AUXILIARY_ROWS.json": {"schema": "WU_TARGET6_EXFOR_AUXILIARY_ROWS_V1", "rows": [auxiliary],
                                "counted_as_primary_provider": False, "counted_in_36_rows": False,
                                "reason": "Electric quadrupole component, kept separate from unpartitioned channel SIG"},
        "EXCLUDED_ROWS.json": {"schema": "WU_TARGET6_EXFOR_EXCLUSION_RECORD_V1", "rows": excluded},
        "SOURCE_PARSE_RECEIPT.json": {"schema": "WU_TARGET6_EXFOR_SOURCE_PARSE_V1", "status": "PASS_SOURCE_TRANSCRIPTION",
                                     "raw_byte_checks": byte_checks, "main_variants": 4, "main_rows": 36,
                                     "auxiliary_variants": 1, "auxiliary_rows": 7, "numeric_cells_preserved_as_strings": True,
                                     "native_units_converted": 0, "new_rate_evaluations": 0, "new_Q_evaluations": 0,
                                     "new_angular_integrations": 0, "new_figures_digitized": 0,
                                     "historical_compiler_or_validation_imports": 0,
                                     "source_retrieval_and_preparation_cost": "UNMEASURED_NOT_ZERO"},
    }
    payloads = {name: json_bytes(value) for name, value in outputs.items()}
    manifest_files = []
    for path in sorted(BASE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.name not in payloads and path.name != "MANIFEST.json":
            data = path.read_bytes()
            manifest_files.append({"file": str(path.relative_to(BASE)), "bytes": len(data), "sha256": sha(data)})
    manifest_files.extend({"file": name, "bytes": len(data), "sha256": sha(data)} for name, data in sorted(payloads.items()))
    payloads["MANIFEST.json"] = json_bytes({"schema": "WU_TARGET6_EXFOR_SOURCE_PACKET_MANIFEST_V1",
        "provider_repository": "IAEA-NDS/exfor_master", "provider_commit": COMMIT,
        "data_license": "CC-BY-4.0", "files": sorted(manifest_files, key=lambda row: row["file"]),
        "main_provider_variants": 4, "main_numeric_rows": 36, "physical_rate_Q_activation": False,
        "manifest_self_hash_is_external": True})
    for name in payloads:
        require(not (BASE / name).exists(), "OUTPUT_ALREADY_EXISTS_PRESERVE_PRIOR_ATTEMPT:" + name)
    for name, data in payloads.items():
        with (BASE / name).open("xb") as handle:
            handle.write(data)
    print(json.dumps({"status": "PASS_SOURCE_TRANSCRIPTION", "main_variants": 4, "main_rows": 36,
                      "provider_rows_SHA256": sha(payloads["PROVIDER_ROWS.json"]),
                      "manifest_SHA256": sha(payloads["MANIFEST.json"]), "outputs": sorted(payloads)}))


if __name__ == "__main__":
    main()
