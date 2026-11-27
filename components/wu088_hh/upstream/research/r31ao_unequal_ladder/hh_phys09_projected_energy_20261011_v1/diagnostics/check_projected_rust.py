#!/usr/bin/env python3
"""Exact containment of supplied PHYS09 Rust output against its pinned oracle.

This checker does not execute Rust or attest the origin of the supplied output.
Compiler, binary, input identities and actual process records belong to the
separate bounded NCP receipt. No scientific source or solver is imported.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys

MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_RATIONAL_DIGITS = 4096
HEX64 = re.compile(r"[0-9a-f]{16}\Z")
HEX256 = re.compile(r"[0-9a-f]{64}\Z")
INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*\Z")
STAGES = ("full", "first_half")
TERMS = ("feedback", "hessian", "lambda_gradient_tail", "birth_gradient", "lambda_birth_tail")
SCALARS = ("gamma", "direct_energy", "projected_energy", "det_C")
VECTORS = ("margins", "U", "V", "W")
SEMANTIC_IDS = (
    "hh_reaction_cancellation", "five_term_sign_reversal", "zero_and_zero_touch",
    "coupled_neumann_tail", "signed_subnormal_and_zero_bits",
    "invalid_domain_and_contraction", "invalid_input_and_arithmetic",
)


class CheckFailure(Exception):
    def __init__(self, code, **details):
        super().__init__(code)
        self.code, self.details = code, details


def require(condition, code, **details):
    if not condition:
        raise CheckFailure(code, **details)


def exact_keys(obj, keys, where):
    require(isinstance(obj, dict), "EXPECTED_OBJECT", where=where)
    require(set(obj) == set(keys), "OBJECT_KEYS", where=where,
            missing=sorted(set(keys) - set(obj)), extra=sorted(set(obj) - set(keys)))


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "DUPLICATE_JSON_KEY", key=key)
        out[key] = value
    return out


def reject_constant(value):
    raise CheckFailure("NONSTANDARD_JSON_NUMBER", value=value)


def finite_float(text):
    value = float(text)
    require(math.isfinite(value), "NONFINITE_JSON_FLOAT", value=text)
    return value


def parse_json(text, where):
    try:
        return json.loads(text, object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant, parse_float=finite_float)
    except (json.JSONDecodeError, ValueError) as error:
        raise CheckFailure("INVALID_JSON", where=where, reason=str(error)) from error


def read_input(path, label, report):
    with path.open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    require(len(data) <= MAX_INPUT_BYTES, "INPUT_SIZE_LIMIT", label=label)
    report["inputs"][label] = {
        "path": str(path.resolve()), "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CheckFailure("INPUT_NOT_UTF8", label=label, offset=error.start) from error


def sign(interval):
    lo, hi = interval
    return "STRICT_NEGATIVE" if hi < 0 else "STRICT_POSITIVE" if lo > 0 else "ZERO_CONTAINING"


def from_bits(word, where):
    require(isinstance(word, str) and HEX64.fullmatch(word) is not None,
            "BINARY64_BITS_SCHEMA", where=where)
    value = struct.unpack(">d", bytes.fromhex(word))[0]
    require(math.isfinite(value), "NONFINITE_BINARY64", where=where)
    return value


def binary_interval(obj, where, output=True):
    if output:
        exact_keys(obj, ("lo_bits", "hi_bits", "sign"), where)
    lo = Fraction(from_bits(obj["lo_bits"], where + ".lo_bits"))
    hi = Fraction(from_bits(obj["hi_bits"], where + ".hi_bits"))
    require(lo <= hi, "REVERSED_BINARY_INTERVAL", where=where)
    if output:
        require(obj["sign"] == sign((lo, hi)), "OUTPUT_SIGN_ENDPOINT_MISMATCH", where=where)
    return lo, hi


def rational(pair, where):
    require(isinstance(pair, list) and len(pair) == 2, "RATIONAL_PAIR", where=where)
    num, den = pair
    require(isinstance(num, str) and len(num) <= MAX_RATIONAL_DIGITS
            and INTEGER.fullmatch(num) is not None, "RATIONAL_NUMERATOR", where=where)
    require(isinstance(den, str) and len(den) <= MAX_RATIONAL_DIGITS
            and POSITIVE_INTEGER.fullmatch(den) is not None, "RATIONAL_DENOMINATOR", where=where)
    return Fraction(int(num), int(den))


def oracle_interval(obj, where):
    exact_keys(obj, ("lo", "hi", "lo_bits", "hi_bits", "sign", "exact"), where)
    exact_keys(obj["exact"], ("lo", "hi"), where + ".exact")
    exact = (rational(obj["exact"]["lo"], where + ".exact.lo"),
             rational(obj["exact"]["hi"], where + ".exact.hi"))
    require(exact[0] <= exact[1], "REVERSED_EXACT_ORACLE", where=where)
    display = binary_interval(obj, where, output=False)
    for endpoint in ("lo", "hi"):
        value = obj[endpoint]
        require(type(value) in (int, float) and math.isfinite(value), "ORACLE_DISPLAY_TYPE", where=where)
        require(struct.pack(">d", value).hex() == obj[endpoint + "_bits"],
                "ORACLE_DISPLAY_BITS_MISMATCH", where=where, endpoint=endpoint)
    require(display[0] <= exact[0] and exact[1] <= display[1],
            "ORACLE_DISPLAY_NOT_OUTWARD", where=where)
    require(obj["sign"] == sign(exact), "ORACLE_SIGN_MISMATCH", where=where)
    return exact


def flatten_stage(stage, reader, output):
    keys = ("stage", *SCALARS, *VECTORS, "energy_terms")
    exact_keys(stage, ("type", *keys) if output else keys, "stage")
    name = stage["stage"]
    require(name in STAGES, "UNKNOWN_STAGE", stage=name)
    if output:
        require(stage["type"] == "stage", "OUTPUT_STAGE_TYPE", stage=name)
    result = {key: reader(stage[key], name + "." + key) for key in SCALARS}
    for key in VECTORS:
        values = stage[key]
        require(isinstance(values, list) and len(values) == 4, "VECTOR_DIMENSION", stage=name, field=key)
        for i, value in enumerate(values):
            result[f"{key}.{i}"] = reader(value, name + f".{key}.{i}")
    exact_keys(stage["energy_terms"], TERMS, name + ".energy_terms")
    for key in TERMS:
        result["energy_terms." + key] = reader(stage["energy_terms"][key], name + ".energy_terms." + key)
    return result


def load_oracle(text, vector_text, report):
    obj = parse_json(text, "oracle")
    require(isinstance(obj, dict), "ORACLE_OBJECT")
    required = {"schema", "stages", "gate_input", "comparison_rule", "native_authority"}
    require(required <= set(obj), "ORACLE_REQUIRED_FIELDS", missing=sorted(required - set(obj)))
    require(obj["schema"] == "PHYS09_PROJECTED_ENERGY_ORACLE_V1", "ORACLE_SCHEMA")
    require(obj["native_authority"] is False, "ORACLE_NATIVE_AUTHORITY_CEILING")
    require(isinstance(obj["comparison_rule"], str), "ORACLE_COMPARISON_RULE")
    exact_keys(obj["gate_input"], ("path", "rows", "bytes", "sha256"), "oracle.gate_input")
    pinned = obj["gate_input"]
    require(isinstance(pinned["path"], str) and not Path(pinned["path"]).is_absolute()
            and ".." not in Path(pinned["path"]).parts, "ORACLE_INPUT_RELATIVE_PATH")
    require(type(pinned["rows"]) is int and pinned["rows"] == 12594, "ORACLE_ROW_COUNT")
    require(type(pinned["bytes"]) is int and 0 < pinned["bytes"] <= MAX_INPUT_BYTES,
            "ORACLE_INPUT_BYTE_COUNT")
    require(isinstance(pinned["sha256"], str) and HEX256.fullmatch(pinned["sha256"]),
            "ORACLE_INPUT_HASH_SCHEMA")
    vector_id = report["inputs"]["vectors"]
    require(vector_id["sha256"] == pinned["sha256"] and vector_id["bytes"] == pinned["bytes"],
            "ORACLE_TSV_IDENTITY_MISMATCH")
    lines = vector_text.splitlines()
    require(lines and lines[0] == "stage\tkey\tlo_bits\thi_bits"
            and len(lines) - 1 == 12594, "BOUND_TSV_HEADER_OR_ROW_COUNT")
    require(isinstance(obj["stages"], list) and len(obj["stages"]) == 2, "ORACLE_STAGE_COUNT")
    result = {}
    for stage in obj["stages"]:
        flattened = flatten_stage(stage, oracle_interval, output=False)
        name = stage["stage"]
        require(name not in result, "DUPLICATE_ORACLE_STAGE", stage=name)
        result[name] = flattened
    require(set(result) == set(STAGES), "ORACLE_STAGE_SET")
    report["oracle_bound_gate_input"] = pinned
    return result


def load_output(text, report):
    lines = text.splitlines()
    require(len(lines) == 4 and all(line.strip() for line in lines), "OUTPUT_ROW_COUNT")
    rows = [parse_json(line, f"output.{i + 1}") for i, line in enumerate(lines)]
    require(all(isinstance(row, dict) for row in rows), "OUTPUT_ROW_OBJECT")
    semantic, full, first_half, summary = rows
    exact_keys(semantic, ("type", "status", "groups", "case_ids", "data_origin"), "semantic_checks")
    require(semantic["type"] == "semantic_checks" and semantic["status"] == "PASS"
            and type(semantic["groups"]) is int and semantic["groups"] == 7
            and semantic["case_ids"] == list(SEMANTIC_IDS)
            and semantic["data_origin"] == "HAND_DERIVED_SYNTHETIC_DISTINCT_FROM_ARCHIVED_STAGES",
            "SEMANTIC_CHECKS_SUMMARY")
    expected = {"semantic_groups": 7, "archived_stage_evaluations": 2,
                "semantic_gate_evaluations": 6, "input_rows": 12594,
                "source_routes": 0, "provider_routes": 0, "root_routes": 0}
    exact_keys(summary, ("type", "external_oracle_validation", *expected), "summary")
    require(summary["type"] == "summary"
            and summary["external_oracle_validation"] == "NOT_PERFORMED_BY_THIS_BINARY", "SUMMARY_TYPE")
    for key, value in expected.items():
        require(type(summary[key]) is int and summary[key] == value,
                "SUMMARY_VALUE", field=key, expected=value, actual=summary[key])
    require(full.get("stage") == "full" and first_half.get("stage") == "first_half",
            "OUTPUT_STAGE_ORDER")
    report["harness_reported_semantics"] = semantic
    report["harness_reported_summary"] = summary
    report["summary_provenance"] = "SUPPLIED_OUTPUT_CONTENT_NOT_RUNTIME_ATTESTATION"
    return {row["stage"]: flatten_stage(row, binary_interval, output=True)
            for row in (full, first_half)}, {row["stage"]: row for row in (full, first_half)}


def compare(oracle, output, raw, report):
    for stage in STAGES:
        checked = {"stage": stage, "intervals": {}, "contains_all_exact_oracle_intervals": False}
        require(set(output[stage]) == set(oracle[stage]), "COMPARISON_FIELD_SET", stage=stage)
        for field, expected in oracle[stage].items():
            actual = output[stage][field]
            require(actual[0] <= expected[0] and expected[1] <= actual[1],
                    "EXACT_ORACLE_NOT_CONTAINED", stage=stage, field=field,
                    rule="output.lo <= exact.lo AND exact.hi <= output.hi")
            checked["intervals"][field] = {"contains_exact_oracle": True,
                "actual_endpoint_sign": sign(actual), "exact_oracle_sign": sign(expected),
                "strict_sign_lost_to_widening": sign(expected) != "ZERO_CONTAINING"
                    and sign(actual) == "ZERO_CONTAINING"}
        actual = output[stage]
        require(0 <= actual["gamma"][0] <= actual["gamma"][1] < 1,
                "RUST_CONTRACTION_NOT_STRICT", stage=stage)
        require(all(actual[f"margins.{i}"][0] > 0 for i in range(4)),
                "RUST_IMAGE_MARGIN_NOT_STRICT", stage=stage)
        require(sign(actual["det_C"]) != "ZERO_CONTAINING", "RUST_C_NONSINGULARITY_OPEN", stage=stage)
        term_lo = sum((actual["energy_terms." + name][0] for name in TERMS), Fraction(0))
        term_hi = sum((actual["energy_terms." + name][1] for name in TERMS), Fraction(0))
        require(actual["projected_energy"][0] <= term_lo and term_hi <= actual["projected_energy"][1],
                "REPORTED_PROJECTED_SUM_NOT_CONTAINED", stage=stage)
        projected_sign = sign(actual["projected_energy"])
        checked["contains_all_exact_oracle_intervals"] = True
        checked["projected_energy_actual_sign"] = projected_sign
        checked["conditional_saved_source_sign"] = projected_sign
        checked["native_implicit_authority"] = False
        checked["rust_stage_output"] = raw[stage]
        report["stages"].append(checked)
    signs = [stage["projected_energy_actual_sign"] for stage in report["stages"]]
    report["projected_energy_claim"] = (
        "BOTH_SAVED_SOURCE_FAMILIES_STRICT_NEGATIVE_CONDITIONAL_ON_SOURCE_PREMISES"
        if signs == ["STRICT_NEGATIVE", "STRICT_NEGATIVE"]
        else "USE_REPORTED_ENDPOINT_SIGNS_ZERO_CONTAINING_REMAINS_OPEN")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--vectors", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        print("REPORT_ALREADY_EXISTS: create-only output required", file=sys.stderr)
        return 2
    report = {"schema": "PHYS09_RUST_PROJECTED_OUTPUT_CHECK_V1", "status": "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(), "inputs": {}, "stages": [], "failures": [],
        "comparison": "EXACT_RATIONAL_CONTAINMENT_NOT_OVERLAP_OR_EQUALITY",
        "rust_execution_attested": False, "binary_binding_attested": False,
        "native_implicit_authority": False, "actual_native_root": None,
        "actual_native_U": None, "actual_native_V": None, "actual_native_W": None, "actual_native_I": None,
        "source_evaluation": "NOT_PERFORMED_BY_THIS_CHECKER",
        "limits": ["Saved-output checks require the separate compiler/binary/input execution receipt.",
                   "The original source inclusion, fixed-coefficient C2 chart and parameter coverage are inherited premises.",
                   "A zero-containing scalar remains OPEN; a successful containment check does not invent a strict sign."]}
    code = 1
    try:
        oracle_text = read_input(args.oracle, "oracle", report)
        vector_text = read_input(args.vectors, "vectors", report)
        output_text = read_input(args.output, "rust_output", report)
        oracle = load_oracle(oracle_text, vector_text, report)
        output, raw = load_output(output_text, report)
        compare(oracle, output, raw, report)
        report["status"] = "PASS_SCOPED_OUTPUT_CONTAINMENT"
        report["verified_stage_count"] = len(report["stages"])
        report["verified_interval_count"] = sum(len(stage["intervals"]) for stage in report["stages"])
        code = 0
    except CheckFailure as error:
        report["failures"].append({"class": "VALIDATION_REJECTION", "code": error.code,
                                   "details": error.details})
    except OSError as error:
        report["failures"].append({"class": "RUNTIME_IO", "code": type(error).__name__,
                                   "details": {"message": str(error)}})
        code = 2
    try:
        with args.report.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write("\n")
    except OSError as error:
        print(f"REPORT_WRITE_FAILURE: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "report": str(args.report.resolve()),
                      "verified_stage_count": len(report["stages"])}))
    return code


if __name__ == "__main__":
    sys.exit(main())
