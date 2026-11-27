#!/usr/bin/env python3
"""READY_NOT_RUN consumer for PHYS08's saved Rust gate JSONL output.

This compares supplied output with an exact rational oracle. It neither runs
Rust nor attests that the file came from a particular executable or input.
The bounded NCP execution receipt must separately bind those identities.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from exact_weighted import E, unbits


EXPECTED_ROLES = {
    "full_P_N": "P_N",
    "full_P_M": "P_M",
    "first_half_P_N": "P_N",
    "first_half_P_M": "P_M",
    "small_hot_tail": "SIGNED_VECTOR",
    "large_hot_tail": "SIGNED_VECTOR",
    "zero": "SIGNED_VECTOR",
    "touch_zero": "SIGNED_VECTOR",
    "signed_He_changes_sign": "SIGNED_VECTOR",
    "positive_scaling": "SIGNED_VECTOR",
    "minsubnormal_signed": "SIGNED_VECTOR",
}
SIGN_MAP = {
    "NEGATIVE": "STRICT_NEGATIVE",
    "POSITIVE": "STRICT_POSITIVE",
    "UNRESOLVED": "ZERO_CONTAINING",
}
HEX64 = re.compile(r"[0-9a-fA-F]{16}\Z")
INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*\Z")
MAX_INPUT_BYTES = 8 * 1024 * 1024


class CheckFailure(Exception):
    def __init__(self, code, **details):
        super().__init__(code)
        self.code = code
        self.details = details


def require(condition, code, **details):
    if not condition:
        raise CheckFailure(code, **details)


def exact_keys(obj, keys, where):
    require(isinstance(obj, dict), "EXPECTED_OBJECT", where=where)
    require(set(obj) == set(keys), "OBJECT_KEYS", where=where,
            missing=sorted(set(keys) - set(obj)), extra=sorted(set(obj) - set(keys)))


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "DUPLICATE_JSON_KEY", key=key)
        obj[key] = value
    return obj


def reject_constant(value):
    raise CheckFailure("NONSTANDARD_JSON_NUMBER", value=value)


def finite_json_float(text):
    value = float(text)
    require(math.isfinite(value), "NONFINITE_JSON_FLOAT", value=text)
    return value


def parse_json(text, where):
    try:
        return json.loads(text, object_pairs_hook=unique_pairs, parse_constant=reject_constant,
                          parse_float=finite_json_float)
    except json.JSONDecodeError as error:
        raise CheckFailure("INVALID_JSON", where=where, line=error.lineno,
                           column=error.colno, message=error.msg) from error
    except ValueError as error:
        raise CheckFailure("INVALID_JSON_VALUE", where=where, message=str(error)) from error


def read_input(path, label, report):
    with path.open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    require(len(data) <= MAX_INPUT_BYTES, "INPUT_SIZE_LIMIT", input=label, bytes=len(data))
    report["inputs"][label] = {
        "path": str(path.resolve()), "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CheckFailure("INPUT_NOT_UTF8", input=label, offset=error.start) from error


def bits_interval(obj, where):
    exact_keys(obj, ("lo_bits", "hi_bits"), where)
    for key in ("lo_bits", "hi_bits"):
        value = obj[key]
        require(isinstance(value, str) and HEX64.fullmatch(value) is not None,
                "ENDPOINT_BITS_SCHEMA", where=where, endpoint=key)
    try:
        return E(unbits(obj["lo_bits"]), unbits(obj["hi_bits"]))
    except ValueError as error:
        raise CheckFailure("INVALID_BINARY_INTERVAL", where=where, reason=str(error)) from error


def rational_endpoint(pair, where):
    require(isinstance(pair, list) and len(pair) == 2, "RATIONAL_PAIR", where=where)
    numerator, denominator = pair
    require(isinstance(numerator, str) and INTEGER.fullmatch(numerator) is not None,
            "RATIONAL_NUMERATOR", where=where)
    require(isinstance(denominator, str) and POSITIVE_INTEGER.fullmatch(denominator) is not None,
            "RATIONAL_DENOMINATOR", where=where)
    return Fraction(int(numerator), int(denominator))


def oracle_interval(obj, where):
    exact_keys(obj, ("lo", "hi", "lo_bits", "hi_bits", "sign", "exact"), where)
    exact_keys(obj["exact"], ("lo", "hi"), where + ".exact")
    try:
        value = E(rational_endpoint(obj["exact"]["lo"], where + ".lo"),
                  rational_endpoint(obj["exact"]["hi"], where + ".hi"))
        display = E.saved(obj)
    except (ValueError, OverflowError, TypeError) as error:
        raise CheckFailure("INVALID_ORACLE_INTERVAL", where=where, reason=str(error)) from error
    require(display.contains(value), "ORACLE_DISPLAY_NOT_OUTWARD", where=where)
    require(obj["sign"] == value.sign(), "ORACLE_SIGN_MISMATCH", where=where)
    return value


def load_oracle(text):
    oracle = parse_json(text, "oracle")
    exact_keys(oracle, ("schema", "fixtures", "comparison"), "oracle")
    require(oracle["schema"] == "PHYS08_RUST_SAVED_FIXTURE_ORACLE_V1",
            "ORACLE_SCHEMA")
    require(isinstance(oracle["comparison"], str), "ORACLE_COMPARISON_SCHEMA")
    fixtures = oracle["fixtures"]
    require(isinstance(fixtures, list) and len(fixtures) == 11, "ORACLE_FIXTURE_COUNT")
    result = {}
    fixture_keys = ("case_id", "role", "input_endpoint_bits", "oracle_B", "oracle_DT",
                    "expected_balance_sign", "expected_dt_sign", "strict_match_required")
    for fixture in fixtures:
        exact_keys(fixture, fixture_keys, "oracle.fixture")
        case_id = fixture["case_id"]
        require(isinstance(case_id, str) and case_id in EXPECTED_ROLES,
                "EXTRANEOUS_ORACLE_FIXTURE", case_id=case_id)
        require(case_id not in result, "DUPLICATE_ORACLE_FIXTURE", case_id=case_id)
        require(fixture["role"] == EXPECTED_ROLES[case_id], "ORACLE_ROLE_MISMATCH", case_id=case_id)
        expected_strict = case_id != "minsubnormal_signed"
        require(type(fixture["strict_match_required"]) is bool
                and fixture["strict_match_required"] == expected_strict,
                "ORACLE_STRICT_POLICY", case_id=case_id)
        words = fixture["input_endpoint_bits"]
        require(isinstance(words, list) and len(words) == 16,
                "ORACLE_INPUT_WORD_COUNT", case_id=case_id)
        input_intervals = [bits_interval({"lo_bits": words[i], "hi_bits": words[i + 1]},
                                        case_id + f".input[{i // 2}]")
                           for i in range(0, 16, 2)]
        require(input_intervals[0].lo > 0 and input_intervals[1].lo > 0
                and input_intervals[7].lo > 0, "ORACLE_POSITIVE_DOMAIN", case_id=case_id)
        balance = oracle_interval(fixture["oracle_B"], case_id + ".oracle_B")
        dt = oracle_interval(fixture["oracle_DT"], case_id + ".oracle_DT")
        require(fixture["expected_balance_sign"] == balance.sign()
                and fixture["expected_dt_sign"] == dt.sign(),
                "ORACLE_EXPECTED_SIGN_MISMATCH", case_id=case_id)
        result[case_id] = {"fixture": fixture, "B": balance, "DT": dt}
    require(set(result) == set(EXPECTED_ROLES), "MISSING_ORACLE_FIXTURE",
            missing=sorted(set(EXPECTED_ROLES) - set(result)))
    return result


def parse_output(text, report):
    lines = text.splitlines()
    rows = []
    for line_number, line in enumerate(lines, 1):
        require(bool(line.strip()), "EMPTY_OUTPUT_ROW", line=line_number)
        row = parse_json(line, f"output.line[{line_number}]")
        require(isinstance(row, dict), "OUTPUT_ROW_NOT_OBJECT", line=line_number)
        require(row.get("kind") in ("semantic_checks", "gate", "summary"),
                "EXTRANEOUS_OUTPUT_ROW", line=line_number, kind=row.get("kind"))
        rows.append(row)
    gates = [r for r in rows if r["kind"] == "gate"]
    ids = []
    for row in gates:
        require(isinstance(row.get("case_id"), str), "OUTPUT_CASE_ID_SCHEMA")
        ids.append(row["case_id"])
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    missing = sorted(set(EXPECTED_ROLES) - set(ids))
    extra = sorted(set(ids) - set(EXPECTED_ROLES))
    require(not duplicates and not missing and not extra and len(gates) == 11,
            "OUTPUT_FIXTURE_SET", duplicates=duplicates, missing=missing, extra=extra,
            gate_rows=len(gates))
    require(len(rows) == 13 and rows[0]["kind"] == "semantic_checks"
            and rows[-1]["kind"] == "summary"
            and all(row["kind"] == "gate" for row in rows[1:-1]),
            "OUTPUT_ROW_ORDER_OR_COUNT", rows=len(rows))
    builtins = rows[0]
    exact_keys(builtins, ("kind", "status", "groups"), "output.semantic_checks")
    require(builtins["status"] == "PASS" and type(builtins["groups"]) is int
            and builtins["groups"] == 7, "BUILTIN_SUMMARY_FAILURE", observed=builtins)
    summary = rows[-1]
    expected_summary = {
        "semantic_groups": 7, "gate_evaluations": 26, "returned_gate_errors": 7,
        "vector_rows": 11, "source_calls": 0, "transport_calls": 0,
        "provider_calls": 0, "root_calls": 0,
    }
    exact_keys(summary, ("kind", "external_oracle_validation", *expected_summary), "output.summary")
    require(summary["external_oracle_validation"] == "NOT_PERFORMED_BY_THIS_BINARY",
            "HARNESS_ORACLE_CLAIM_MISMATCH")
    for key, value in expected_summary.items():
        require(type(summary[key]) is int and summary[key] == value,
                "HARNESS_SUMMARY_MISMATCH", field=key, expected=value, observed=summary[key])
    report["harness_reported_summary"] = summary
    report["harness_reported_builtins"] = builtins
    report["summary_provenance"] = "CONTENT_OF_SUPPLIED_OUTPUT_ONLY_NOT_RUNTIME_ATTESTATION"
    return gates


def compare_rows(gates, oracle, report):
    row_keys = ("kind", "case_id", "role", "status", "B", "B_sign", "DT", "DT_sign")
    for row in gates:
        case_id = row["case_id"]
        fixture = oracle[case_id]["fixture"]
        require(row.get("role") == fixture["role"], "OUTPUT_ROLE_MISMATCH", case_id=case_id)
        require(row.get("status") == "OK", "GATE_RESULT_FAILURE", case_id=case_id,
                observed_status=row.get("status"), reported_error=row.get("error"))
        exact_keys(row, row_keys, "output." + case_id)
        checked = {"case_id": case_id, "role": row["role"],
                   "strict_match_required": fixture["strict_match_required"]}
        for name, sign_key, expected_key in (("B", "B_sign", "expected_balance_sign"),
                                               ("DT", "DT_sign", "expected_dt_sign")):
            value = bits_interval(row[name], case_id + "." + name)
            reported_sign = row[sign_key]
            require(isinstance(reported_sign, str) and reported_sign in SIGN_MAP,
                    "OUTPUT_SIGN_SCHEMA", case_id=case_id, quantity=name)
            normalized = value.sign()
            require(SIGN_MAP[reported_sign] == normalized, "OUTPUT_SIGN_ENDPOINT_MISMATCH",
                    case_id=case_id, quantity=name, reported=reported_sign, derived=normalized)
            require(value.contains(oracle[case_id][name]), "EXACT_ORACLE_NOT_CONTAINED",
                    case_id=case_id, quantity=name,
                    required="output.lo <= oracle.exact.lo AND oracle.exact.hi <= output.hi")
            expected_sign = fixture[expected_key]
            if fixture["strict_match_required"]:
                require(normalized == expected_sign, "REQUIRED_SIGN_MISMATCH",
                        case_id=case_id, quantity=name, expected=expected_sign, observed=normalized)
            else:
                require(normalized in (expected_sign, "ZERO_CONTAINING"),
                        "UNSAFE_SUBNORMAL_SIGN", case_id=case_id, quantity=name,
                        expected=expected_sign, observed=normalized)
            checked[name] = {
                "rust_interval_bits": row[name], "normalized_sign": normalized,
                "oracle_exact_sign": expected_sign, "contains_exact_oracle": True,
                "safe_widening_to_zero": normalized == "ZERO_CONTAINING" and normalized != expected_sign,
            }
        report["fixtures"].append(checked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        print("REPORT_ALREADY_EXISTS: create-only report required", file=sys.stderr)
        return 2
    report = {
        "schema": "PHYS08_RUST_SAVED_OUTPUT_CHECK_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL",
        "scope": "Supplied saved JSONL scalar interval containment against exact rational oracle",
        "inputs": {}, "fixtures": [], "failures": [],
        "rust_execution_attested": False,
        "binary_and_input_binding_attested": False,
        "native_authority": False,
        "physics_source_evaluation": "NOT_PERFORMED_BY_THIS_CHECKER",
        "limits": [
            "The output file alone does not prove a Rust build or execution occurred.",
            "Executable identity, input identity, process exit and resource observations belong to the separate bounded-run receipt.",
            "Matching labels and output schemas do not attest source tuple, C2, parameter coverage, root or mixed response.",
        ],
    }
    exit_code = 1
    try:
        oracle = load_oracle(read_input(args.oracle, "oracle", report))
        gates = parse_output(read_input(args.output, "rust_output", report), report)
        compare_rows(gates, oracle, report)
        report["status"] = "PASS_SCOPED_OUTPUT_CONTAINMENT"
        report["verified_fixture_count"] = len(report["fixtures"])
        report["comparison"] = "EXACT_RATIONAL_CONTAINMENT_NOT_OVERLAP_OR_EQUALITY"
        exit_code = 0
    except CheckFailure as error:
        report["failures"].append({"class": "VALIDATION_REJECTION", "code": error.code,
                                   "details": error.details})
    except OSError as error:
        report["failures"].append({"class": "RUNTIME_IO", "code": type(error).__name__,
                                   "details": {"message": str(error)}})
        exit_code = 2
    try:
        with args.report.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    except OSError as error:
        print(f"REPORT_WRITE_FAILURE: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "report": str(args.report.resolve()),
                      "verified_fixture_count": len(report["fixtures"])}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
