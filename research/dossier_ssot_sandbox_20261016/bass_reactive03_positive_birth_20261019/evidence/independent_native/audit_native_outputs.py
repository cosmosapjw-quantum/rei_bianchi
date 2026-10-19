#!/usr/bin/env python3
"""Read-only independent audit of the BASS-REACTIVE-03 native matrix.

Input CSV/JSON/stderr files are never written. The sole output is a new JSON
report. All ledger residuals are recomputed from exported primitive quantities;
the driver's maxN/maxE fields are diagnostics, not the acceptance oracle.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import sys


HEADER = (
    "case,grid,nsteps,t0,duration,split,frozen,step,time_s,T_K,DII_m3,"
    "photons_com3,absorbed_com3,HI,HeI,HeII,DI,source_count,source_energy,"
    "geom_work,q2,H_perp,H_parallel,volume,cohorts,maxN,maxE,maxW,RR,CX_abs,"
    "FF,CMB_abs,hits,misses,cache_size,birth_gl,opacity,cx_rtol,cx_atol,"
    "threshold_crossings,wall_s,birth_mode,refinement,thermal_change_com3,"
    "chemical_change_com3,photo_energy_com3,survivor_age_com_s,"
    "survivor_age2_com_s2,photon_energy_com3,gas_thermal_com3,"
    "gas_binding_com3,escaped_com3,cmb_reservoir_com3,initial_total_energy_com3"
).split(",")

CASES = {
    "off_gl2_n32": {"n": 32, "r": 0},
    "off_gl4_n32": {"n": 32, "r": 0, "gl": 4},
    "ap_n16_r2": {"n": 16, "r": 2},
    "ap_n32_r2": {"n": 32, "r": 2},
    "ap_n64_r2": {"n": 64, "r": 2},
    "ap_n128_r2": {"n": 128, "r": 2},
    "ap_n32_r1": {"n": 32, "r": 1},
    "ap_n32_r4": {"n": 32, "r": 4},
    "ap_n32_r8": {"n": 32, "r": 8},
    "ap_n32_r2_spectrum": {"n": 32, "r": 2, "split": True},
    "ap_n32_r2_opacity8": {"n": 32, "r": 2, "opacity": 8},
    "ap_n32_r2_plus": {"n": 32, "r": 2, "case": "SIGNED_PLUS"},
    "ap_cx_worklimit": {"n": 32, "r": 2, "cx": 1e-14},
}
TEXT_FIELDS = {"case", "split", "frozen", "birth_mode"}
NONNEGATIVE = {
    "DII_m3", "photons_com3", "absorbed_com3", "HI", "HeI", "HeII", "DI",
    "source_count", "source_energy", "cohorts", "maxN", "maxE", "maxW",
    "RR", "CX_abs", "FF", "CMB_abs", "hits", "misses", "cache_size",
    "threshold_crossings", "wall_s", "photo_energy_com3",
    "survivor_age_com_s", "survivor_age2_com_s2", "photon_energy_com3",
    "gas_thermal_com3", "gas_binding_com3", "escaped_com3",
}
INTEGER_FIELDS = {
    "grid", "nsteps", "step", "cohorts", "hits", "misses", "cache_size",
    "birth_gl", "opacity", "threshold_crossings", "refinement",
}
CUMULATIVE = {
    "absorbed_com3", "HI", "HeI", "HeII", "DI", "source_count", "source_energy",
    "RR", "CX_abs", "FF", "CMB_abs", "photo_energy_com3",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fraction(residual: float, *values: float) -> float:
    return abs(residual) / max(*(abs(x) for x in values), 1e-300)


def audit_one(directory: Path, name: str, limit: float) -> dict:
    expected = CASES[name]
    result = {"name": name, "issues": [], "status": "UNREVIEWED"}

    def issue(code: str, detail: str, row: int | None = None) -> None:
        item = {"class": code, "detail": detail}
        if row is not None:
            item["row"] = row
        if len(result["issues"]) < 100:
            result["issues"].append(item)
        else:
            result["additional_issues"] = result.get("additional_issues", 0) + 1

    paths = {kind: directory / f"{name}.{kind}" for kind in ("csv", "json", "stderr")}
    if any(not p.is_file() for p in paths.values()):
        issue("MISSING_ARTIFACT", "Missing one of CSV, receipt JSON, or stderr.")
        result["status"] = "BLOCKED_MISSING_ARTIFACT"
        return result
    raw = {kind: p.read_bytes() for kind, p in paths.items()}
    result["identity"] = {
        kind: {"path": str(paths[kind]), "bytes": len(data), "sha256": sha(data)}
        for kind, data in raw.items()
    }
    try:
        receipt = json.loads(raw["json"])
        stderr = raw["stderr"].decode("utf-8")
        text = raw["csv"].decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        fields = reader.fieldnames
    except (ValueError, UnicodeError, csv.Error) as error:
        issue("ARTIFACT_PARSE_ERROR", repr(error))
        result["status"] = "FAIL_ARTIFACT"
        return result

    result["rows"] = len(rows)
    result["receipt_exit_code"] = receipt.get("exit_code")
    result["receipt_status"] = receipt.get("status")
    result["binary_sha256"] = receipt.get("binary_sha256")
    for condition, detail in [
        (receipt.get("name") == name, "Receipt name does not match filename."),
        (receipt.get("csv_sha256") == sha(raw["csv"]), "Receipt CSV SHA differs from raw bytes."),
        (receipt.get("rows") == len(rows), "Receipt row count differs from raw CSV."),
        (receipt.get("planned_rows") == expected["n"], "Receipt planned_rows differs from matrix."),
        (receipt.get("final") == (rows[-1] if rows else None), "Receipt final row differs from raw CSV."),
        (receipt.get("stderr") == stderr, "Receipt stderr differs from raw stderr bytes."),
    ]:
        if not condition:
            issue("ARTIFACT_IDENTITY_MISMATCH", detail)
    command = receipt.get("command")
    command_tail = [
        expected.get("case", "SIGNED_MINUS"), "121", str(expected["n"]), "0", "8e12",
        str(expected.get("split", False)).lower(), "false", str(expected.get("gl", 2)),
        str(expected.get("opacity", 4)), str(expected.get("cx", 1e-12)),
        "off" if expected["r"] == 0 else str(expected["r"]),
    ]
    if not isinstance(command, list) or len(command) != 12 or command[1:] != command_tail:
        issue("EXECUTION_CONTRACT_MISMATCH", "Receipt command does not match the planned independent axes.")

    expected_limit = name == "ap_cx_worklimit"
    if expected_limit:
        valid_limit = (
            receipt.get("exit_code") != 0
            and receipt.get("status") == "RESOURCE_LIMIT_CX"
            and receipt.get("failure_class")
            == "NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION"
            and "Cx(WorkLimit)" in stderr
            and len(rows) == 0
            and receipt.get("final") is None
        )
        if not valid_limit:
            issue("FAILURE_CLASS_MISMATCH", "Expected an explicit CX WorkLimit with zero committed rows.")
        if fields not in (None, HEADER):
            issue("CSV_SCHEMA_ERROR", "WorkLimit CSV must be empty or contain only the valid 54-column header.")
        result["failure_interpretation"] = "CX work budget exhausted; no accepted native history."
    else:
        if receipt.get("exit_code") != 0 or receipt.get("status") != "COMPLETED":
            issue("UNEXPECTED_EXECUTION_FAILURE", "Normal matrix case did not complete successfully.")
        if len(rows) != expected["n"]:
            issue("ARTIFACT_ROW_COUNT_MISMATCH", f"Expected {expected['n']} completed rows.")
        if fields != HEADER:
            issue("CSV_SCHEMA_ERROR", "Expected the exact ordered 54-column schema.")
        if receipt.get("failure_class") is not None:
            issue("FAILURE_CLASS_MISMATCH", "Completed case carries a failure classification.")

    maxima = {
        "number_ledger_relative": 0.0,
        "species_absorption_relative": 0.0,
        "total_energy_ledger_relative": 0.0,
        "reported_maxN": 0.0,
        "reported_maxE": 0.0,
        "reported_maxW": 0.0,
    }
    previous = None
    initial_energy = None
    final_numeric = None
    for index, row in enumerate(rows, 1):
        if set(row) != set(HEADER) or any(value is None for value in row.values()):
            issue("CSV_SCHEMA_ERROR", "Incomplete or overlong CSV row.", index)
            continue
        try:
            values = {key: float(value) for key, value in row.items() if key not in TEXT_FIELDS}
        except (ValueError, TypeError):
            issue("CSV_NUMERIC_PARSE_ERROR", "A numerical field cannot be parsed.", index)
            continue
        if not all(math.isfinite(x) for x in values.values()):
            issue("NONFINITE_EXPORTED_VALUE", "At least one numerical field is nonfinite.", index)
            continue
        for key in NONNEGATIVE:
            if values[key] < 0.0:
                issue("NEGATIVE_EXPORTED_QUANTITY", key, index)
        for key in INTEGER_FIELDS:
            if not values[key].is_integer():
                issue("NONINTEGER_DISCRETE_FIELD", key, index)
        for key in ("T_K", "volume", "cx_rtol", "cx_atol", "duration"):
            if values[key] <= 0.0:
                issue("NONPOSITIVE_EXPORTED_QUANTITY", key, index)
        if not (-0.5 - 1e-12 <= values["q2"] <= 1.0 + 1e-12):
            issue("ANGULAR_MOMENT_OUTSIDE_SUPPORT", "Energy-weighted P2 is outside [-1/2,1].", index)
        fixed_text = {
            "case": expected.get("case", "SIGNED_MINUS"),
            "split": str(expected.get("split", False)).lower(),
            "frozen": "false",
            "birth_mode": "off" if expected["r"] == 0 else "fitted",
        }
        fixed_numeric = {
            "grid": 121, "nsteps": expected["n"], "t0": 0, "duration": 8e12,
            "birth_gl": expected.get("gl", 2), "opacity": expected.get("opacity", 4),
            "refinement": expected["r"], "cx_rtol": expected.get("cx", 1e-12),
            "cx_atol": expected.get("cx", 1e-12) * 1e-2,
        }
        if any(row[k] != v for k, v in fixed_text.items()):
            issue("ROW_CONTROL_MISMATCH", "Text controls differ from the receipt contract.", index)
        if any(not math.isclose(values[k], v, rel_tol=2e-14, abs_tol=0.0)
               for k, v in fixed_numeric.items()):
            issue("ROW_CONTROL_MISMATCH", "Numerical controls differ from the matrix contract.", index)
        expected_time = 8e12 if index == expected["n"] else 8e12 * index / expected["n"]
        if values["step"] != index or abs(values["time_s"] - expected_time) > 8 * math.ulp(expected_time):
            issue("TIME_GRID_MISMATCH", "Step index or exported time is inconsistent.", index)
        if previous is not None:
            if values["time_s"] <= previous["time_s"]:
                issue("TIME_NOT_MONOTONE", "Accepted times must increase.", index)
            for key in CUMULATIVE:
                tolerance = 2e-14 * max(abs(values[key]), abs(previous[key]), 1e-300)
                if values[key] < previous[key] - tolerance:
                    issue("CUMULATIVE_EVENT_DECREASE", key, index)
        if initial_energy is None:
            initial_energy = values["initial_total_energy_com3"]
        elif values["initial_total_energy_com3"] != initial_energy:
            issue("INITIAL_ENERGY_IDENTITY_MISMATCH", "E_initial changes between rows.", index)

        number = math.fsum((values["photons_com3"], values["absorbed_com3"], -values["source_count"]))
        nrel = fraction(number, values["source_count"], values["photons_com3"] + values["absorbed_com3"])
        photo_events = math.fsum(values[key] for key in ("HI", "HeI", "HeII", "DI"))
        species_rel = fraction(photo_events - values["absorbed_com3"], values["source_count"])
        total_energy = math.fsum(values[key] for key in (
            "photon_energy_com3", "gas_thermal_com3", "gas_binding_com3",
            "escaped_com3", "cmb_reservoir_com3",
        ))
        expected_energy = math.fsum(values[key] for key in (
            "initial_total_energy_com3", "source_energy", "geom_work",
        ))
        erel = fraction(total_energy - expected_energy, total_energy, expected_energy, initial_energy)
        for key, value in (
            ("number_ledger_relative", nrel), ("species_absorption_relative", species_rel),
            ("total_energy_ledger_relative", erel),
        ):
            maxima[key] = max(maxima[key], value)
            if value > limit:
                issue("INDEPENDENT_LEDGER_FAILURE", f"{key}={value:.17e} exceeds {limit:.17e}.", index)
        for exported in ("maxN", "maxE", "maxW"):
            maxima["reported_" + exported] = max(maxima["reported_" + exported], values[exported])
        count = values["photons_com3"]
        age1, age2 = values["survivor_age_com_s"], values["survivor_age2_com_s2"]
        age_limit = values["time_s"] - values["t0"]
        if count > 0.0:
            mean, second = age1 / count, age2 / count
            slack = 2e-12 * max(age_limit, 1e-300)
            if mean < -slack or mean > age_limit + slack:
                issue("AGE_MOMENT_SUPPORT_FAILURE", "Mean surviving age is outside the represented history.", index)
            slack2 = 2e-12 * max(age_limit * age_limit, 1e-300)
            if second < mean * mean - slack2 or second > age_limit * mean + slack2:
                issue("AGE_MOMENT_REALIZABILITY_FAILURE", "First/second age moments violate support or variance bounds.", index)
        elif age1 != 0.0 or age2 != 0.0:
            issue("AGE_MOMENT_REALIZABILITY_FAILURE", "Zero surviving photons have nonzero age moments.", index)
        final_numeric = {
            "time_s": values["time_s"], "photons_com3": count,
            "total_energy_com3": total_energy, "expected_energy_com3": expected_energy,
            "number_ledger_relative": nrel, "energy_ledger_relative": erel,
            "age_mean_s": age1 / count if count > 0.0 else None,
            "age_second_moment_s2": age2 / count if count > 0.0 else None,
        }
        previous = values

    result["maxima"] = maxima
    result["final_recomputed"] = final_numeric
    result["schema_columns"] = len(fields) if fields is not None else 0
    for kind, path in paths.items():
        if path.read_bytes() != raw[kind]:
            issue("ARTIFACT_CHANGED_DURING_READ", f"{kind} bytes changed during independent audit.")
    result["status"] = (
        "FAIL" if result["issues"] else
        "PASS_EXPECTED_CX_WORKLIMIT" if expected_limit else
        "PASS_SCOPED"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New report path, created once.")
    parser.add_argument("--relative-limit", type=float, default=3e-10)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if not math.isfinite(args.relative_limit) or args.relative_limit <= 0.0:
        raise ValueError("relative-limit must be finite and positive")
    directory = args.native_dir.resolve(strict=True)
    if directory == args.output.parent.resolve() or directory in args.output.resolve().parents:
        raise ValueError("Write the reviewer report outside the read-only native data directory.")
    results = [audit_one(directory, name, args.relative_limit) for name in CASES]
    binary_hashes = sorted({r["binary_sha256"] for r in results if r.get("binary_sha256")})
    passed = all(r["status"] in ("PASS_SCOPED", "PASS_EXPECTED_CX_WORKLIMIT") for r in results)
    if len(binary_hashes) != 1:
        passed = False
    report = {
        "status": "PASS_SCOPED" if passed else "FAIL_OR_INCOMPLETE",
        "timestamp_utc": dt.datetime.now(dt.UTC).isoformat(),
        "auditor_sha256": sha(Path(__file__).read_bytes()),
        "input_directory": str(directory),
        "expected_cases": 13,
        "completed_cases": sum(r["status"] == "PASS_SCOPED" for r in results),
        "expected_work_limits": sum(r["status"] == "PASS_EXPECTED_CX_WORKLIMIT" for r in results),
        "accepted_rows": sum(r.get("rows", 0) for r in results if r["status"] == "PASS_SCOPED"),
        "unique_recorded_binary_hashes": binary_hashes,
        "same_recorded_binary_all_cases": len(binary_hashes) == 1,
        "relative_ledger_limit": args.relative_limit,
        "primitive_energy_formula": "photon + gas_thermal + gas_binding + escaped + signed_CMB_reservoir",
        "expected_energy_formula": "initial_total_energy + source_energy + signed_geometry_work",
        "number_formula": "surviving_photons + total_absorptions - source_count; initial photons=0 by native initial()",
        "species_formula": "HI + HeI + HeII + DI - total_absorptions",
        "driver_maxN_maxE_used_as_oracle": False,
        "negative_value_exemptions": ["geometry_work", "CMB_reservoir", "thermal_change", "chemical_change", "Hubble_components"],
        "population_scope": "DII population and all four cumulative photoevent channels are exported; full 13-species population vector is not exported.",
        "scientific_limit": "Conservation, positivity of exported quantities, age-moment support and artifact consistency; no claim of temporal/spectral/age convergence.",
        "source_directory_written": False,
        "cases": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        json.dump(report, output, indent=2, allow_nan=False)
        output.write("\n")
    print(json.dumps({key: report[key] for key in (
        "status", "completed_cases", "expected_work_limits", "accepted_rows",
        "same_recorded_binary_all_cases",
    )}))
    if not passed:
        print(json.dumps({r["name"]: r["issues"][:4] for r in results if r["issues"]}, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
