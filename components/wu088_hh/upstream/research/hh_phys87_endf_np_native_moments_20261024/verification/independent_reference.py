#!/usr/bin/env python3
"""PHYS87 independently parsed ENDF + SciPy reference, one admitted child only.

Prepared statically before S1. Importing this module performs no calculation.
The controller must dispatch main only after the primary under the pinned shared
lease, one worker/thread, CPU20s/wall60s. No production module is imported.
This compares a fixed finite-window rate and means at T=1e8 K only. It does not
validate low-T variance subtraction, source uncertainty, tails or a continuum
quadrature bound. The reference never infers daughter mass from recoil AWP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import resource
import signal
import sys
import time
import traceback
from decimal import Decimal
from pathlib import Path


CONTRACT_SHA256 = "464df6f83a7ac8bd64813dc9da3ca34f19398a2f970f3d69c706e3d089f6fd38"
RAW_SHA256 = "3024d8f0db604b074e33ed8b05027eb9f5a738614041ba44c83f048e0d0bc1af"
TABLE_SHA256 = "b14ad9b4a2379166ec2b2c04b2a77efb4c819498924682072d74a6b4e31c5014"
T_K = 100_000_000.0
EPSABS_SCALED = 1.0e-24
EPSREL = 2.0e-11
QUAD_LIMIT = 64
THREAD_ENV = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)
FIELDS = ("kappa_cm3_per_s", "mean_Kin_eV", "mean_Egamma_eV", "mean_Kd_eV")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def endf_number(field: str) -> Decimal:
    """Parse the original fixed-width numeric field, without production helpers."""
    value = field.strip()
    if not value:
        return Decimal(0)
    if "e" not in value.lower():
        value = re.sub(r"(?<=[0-9.])([+-][0-9]+)$", r"E\1", value)
    parsed = Decimal(value)
    need(parsed.is_finite(), "Nonfinite ENDF numeric field")
    return parsed


def fields(line: str) -> list[Decimal]:
    need(len(line) >= 75, "Truncated ENDF record")
    return [endf_number(line[start:start + 11]) for start in range(0, 66, 11)]


def integer(value: Decimal) -> int:
    need(value == value.to_integral_value(), "Nonintegral ENDF control field")
    return int(value)


def section(lines: list[str], mf: int, mt: int) -> list[str]:
    result = [line for line in lines if len(line) >= 75
              and int(line[70:72]) == mf and int(line[72:75]) == mt]
    need(bool(result), f"Missing MF{mf}/MT{mt}")
    need(all(int(line[66:70]) == 125 for line in result), "Unexpected material")
    return result


def values(records: list[str], start: int, count: int) -> tuple[list[Decimal], int]:
    stop = start + (count + 5) // 6
    need(stop <= len(records), "Truncated ENDF array")
    flattened = [v for line in records[start:stop] for v in fields(line)]
    need(all(v == 0 for v in flattened[count:]), "Unexpected nonzero padding")
    return flattened[:count], stop


def tab1(records: list[str], start: int) -> tuple[dict, int]:
    head = fields(records[start])
    nr, np = integer(head[4]), integer(head[5])
    interpolation, offset = values(records, start + 1, 2 * nr)
    xy, stop = values(records, offset, 2 * np)
    return {
        "head": head,
        "interpolation": [(integer(interpolation[i]), integer(interpolation[i + 1]))
                          for i in range(0, len(interpolation), 2)],
        "x": xy[0::2], "y": xy[1::2],
    }, stop


def parse_source(unit: Path) -> dict:
    raw = (unit / "source_data/n-001_H_001.endf").read_bytes()
    need(len(raw) == 671232 and sha256(raw) == RAW_SHA256, "Canonical raw identity mismatch")
    lines = raw.decode("ascii").splitlines()
    mf3 = section(lines, 3, 102)
    need(len(mf3) == 54, "Unexpected MF3 record count")
    h3 = fields(mf3[0])
    cross, end = tab1(mf3, 1)
    need(end == len(mf3), "Unconsumed MF3 records")
    need(h3[:2] == [Decimal(1001), Decimal("0.9991673")], "MF3 ZA/AWR mismatch")
    need(cross["head"][:4] == [Decimal(2224648), Decimal(2224648), Decimal(0), Decimal(0)],
         "MF3 QM/QI/LR mismatch")
    need(cross["interpolation"] == [(33, 5), (153, 2)], "MF3 interpolation mismatch")
    need(len(cross["x"]) == 153, "MF3 knot count mismatch")
    need(cross["x"][0] == Decimal("1e-5") and cross["x"][-1] == Decimal("2e7"),
         "Source window mismatch")
    need(all(a < b for a, b in zip(cross["x"], cross["x"][1:])), "Unordered source grid")
    need(all(v > 0 for v in cross["y"]), "Nonpositive cross section")

    # This independently reads MF6 to guard the scalar rotational reduction.
    # Its angular coefficients are audited, not fed into the scalar kernel.
    mf6 = section(lines, 6, 102)
    need(len(mf6) == 315, "Unexpected MF6 record count")
    h6 = fields(mf6[0])
    need(h6 == [Decimal(1001), Decimal("0.9991673"), Decimal(0), Decimal(2), Decimal(2), Decimal(0)],
         "MF6 frame or product-count mismatch")
    photon, offset = tab1(mf6, 1)
    need(photon["head"][:4] == [Decimal(0), Decimal(2223300), Decimal(0), Decimal(2)],
         "Photon LAW2/primary-energy metadata mismatch")
    need(photon["interpolation"] == [(2, 2)] and photon["x"] == [cross["x"][0], cross["x"][-1]]
         and photon["y"] == [Decimal(1), Decimal(1)], "Photon yield mismatch")
    ah = fields(mf6[offset])
    need(ah == [Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(1), Decimal(153)],
         "Angular TAB2 header mismatch")
    ai, offset = values(mf6, offset + 1, 2)
    need(ai == [Decimal(153), Decimal(2)], "Angular interpolation mismatch")
    angular = []
    for energy in cross["x"]:
        head = fields(mf6[offset])
        need(head == [Decimal(0), energy, Decimal(0), Decimal(0), Decimal(2), Decimal(2)],
             "Angular LANG/NL or grid mismatch")
        coeff, offset = values(mf6, offset + 1, 2)
        angular.append(coeff)
    recoil, offset = tab1(mf6, offset)
    need(offset == len(mf6), "Unconsumed MF6 records")
    need(recoil["head"][:4] == [Decimal(1002), Decimal("1.996256"), Decimal(0), Decimal(4)],
         "Recoil LAW4/AWP metadata mismatch")
    need(recoil["interpolation"] == [(2, 2)] and recoil["x"] == photon["x"]
         and recoil["y"] == [Decimal(1), Decimal(1)], "Recoil yield mismatch")

    # The frozen table is used only to compare the independently parsed raw data.
    table_raw = (unit / "source_data/SOURCE_TABLE.json").read_bytes()
    need(sha256(table_raw) == TABLE_SHA256, "Transcription table identity mismatch")
    table = json.loads(table_raw)
    need(table["incident_energy_frame"] == "laboratory target rest"
         and table["secondary_angle_frame"] == "center_of_mass", "Table frame mismatch")
    need(len(table["rows"]) == 153, "Table row count mismatch")
    for i, row in enumerate(table["rows"]):
        need(row["index1"] == i + 1, "Transcription index mismatch")
        actual = [cross["x"][i], cross["y"][i], *angular[i]]
        recorded = [Decimal(row[k]) for k in ("En_eV", "sigma_barn", "a1", "a2")]
        need(actual == recorded, f"Raw/table mismatch at source knot {i + 1}")
    return {"cross": cross, "AWR": h3[1], "Q": cross["head"][1],
            "audit": {"raw_sha256": RAW_SHA256, "table_sha256": TABLE_SHA256,
                      "raw_bytes": len(raw), "knots": 153, "cells": 152,
                      "MF3_interpolation": [[33, 5], [153, 2]],
                      "MF6_LCT": 2, "photon_LAW": 2, "recoil_LAW": 4,
                      "photon_yield": 1, "recoil_yield": 1,
                      "exact_raw_table_numeric_fields_compared": 612,
                      "angular_coefficients_used_in_scalar_kernel": False}}


def compute_reference(source: dict, contract: dict) -> dict:
    # Import only inside the budgeted child, after all identity checks.
    import scipy
    from scipy.integrate import quad
    from scipy.special import kve

    a = float(Decimal(contract["physical_model"]["epsilon_n_eV"]))
    b = float(Decimal(contract["physical_model"]["epsilon_n_eV"]) * source["AWR"])
    qvalue = float(source["Q"])
    total_mass = a + b
    theta = float(Decimal("1.380649e-23") / Decimal("1.602176634e-19")) * T_K
    c_cm_s = 29979245800.0
    a2, b2 = float(kve(2, a / theta)), float(kve(2, b / theta))
    need(all(math.isfinite(v) and v > 0 for v in (a2, b2)), "Invalid denominator Bessel value")
    cross = source["cross"]
    energies = [float(v) for v in cross["x"]]
    sigmas = [float(v) for v in cross["y"]]
    counts = {"callback_evaluations": 0, "exp_underflow_zero_callbacks": 0,
              "quad_calls": 0, "cells": 152, "integral_families": 4}
    cell_results = []
    accumulated = [[], [], [], []]
    errors = [[], [], [], []]

    for i in range(152):
        lo, hi = energies[i:i + 2]
        slo, shi = sigmas[i:i + 2]
        law = next(law for stop, law in cross["interpolation"] if i + 2 <= stop)
        power = math.log(shi / slo) / math.log(hi / lo) if law == 5 else None
        slope = (shi - slo) / (hi - lo) if law == 2 else None

        def integrand(x: float, component: int) -> float:
            counts["callback_evaluations"] += 1
            energy = x * theta
            sigma_b = slo * math.exp(power * math.log(energy / lo)) if law == 5 else slo + slope * (energy - lo)
            root_s = math.sqrt(total_mass * total_mass + 2.0 * b * energy)
            kinetic = 2.0 * b * energy / (root_s + total_mass)
            w = total_mass + kinetic
            boltzmann = math.exp(-kinetic / theta)
            if boltzmann == 0.0:
                counts["exp_underflow_zero_callbacks"] += 1
                return 0.0
            z = w / theta
            need(z >= 1.0e5 and math.isfinite(z), "Bessel argument guard failed")
            k1 = float(kve(1, z))
            need(math.isfinite(k1) and k1 > 0, "Invalid numerator Bessel value")
            # x=E_lab/theta and lambda/(4 a^2 b^2)=E_lab*(2a+E_lab)/a^2.
            # dK/dE_lab=b/W. This form independently cancels the rate's factor4.
            weight = sigma_b * (energy / a) * (2.0 + energy / a) * (b / w) * k1 * boltzmann
            if component == 0:
                value = weight
            else:
                k2 = float(kve(2, z))
                need(math.isfinite(k2) and k2 > 0, "Invalid moment Bessel value")
                # Only the highest T is admitted here; G-1 is O(1e-5).
                # No subtraction of two O(1) variance terms is performed.
                gm1 = (k2 - k1) / k1
                available = qvalue + kinetic
                recoil_star = available * available / (2.0 * w)
                photon_star = available - recoil_star
                if component == 1:
                    moment = (kinetic + w * gm1) / theta
                elif component == 2:
                    moment = photon_star * (1.0 + gm1) / qvalue
                else:
                    moment = (recoil_star + (w - photon_star) * gm1) / theta
                value = weight * moment
            need(math.isfinite(value) and value >= 0, "Invalid adaptive integrand")
            return value

        entry = {"index1": i + 1, "lo_E_lab_eV": lo, "hi_E_lab_eV": hi, "INT": law,
                 "scaled_integrals": [], "quad_error_estimates": [], "neval": []}
        for component in range(4):
            outcome = quad(integrand, lo / theta, hi / theta, args=(component,),
                           epsabs=EPSABS_SCALED, epsrel=EPSREL, limit=QUAD_LIMIT, full_output=1)
            counts["quad_calls"] += 1
            need(len(outcome) == 3, f"QUADPACK warning in cell {i + 1}, component {component}: {outcome[3:]}")
            value, error, info = outcome
            need(math.isfinite(value) and value >= 0 and math.isfinite(error), "Invalid integral result")
            accumulated[component].append(value)
            errors[component].append(error)
            entry["scaled_integrals"].append(value)
            entry["quad_error_estimates"].append(error)
            entry["neval"].append(int(info["neval"]))
        cell_results.append(entry)

    integrals = [math.fsum(v) for v in accumulated]
    need(integrals[0] > 0, "Reference normalizer vanished")
    result = {
        "T_K": T_K,
        "kappa_cm3_per_s": c_cm_s * 1.0e-24 * integrals[0] / (a2 * b2),
        "mean_Kin_eV": theta * integrals[1] / integrals[0],
        "mean_Egamma_eV": qvalue * integrals[2] / integrals[0],
        "mean_Kd_eV": theta * integrals[3] / integrals[0],
    }
    need(all(math.isfinite(result[k]) and result[k] > 0 for k in FIELDS), "Invalid reference moments")
    result["energy_closure_eV"] = math.fsum([result["mean_Kin_eV"], qvalue,
                                           -result["mean_Egamma_eV"], -result["mean_Kd_eV"]])
    result["scaled_integrals"] = integrals
    result["summed_quad_error_estimates"] = [math.fsum(v) for v in errors]
    result["quad_error_interpretation"] = "QUADPACK estimates only; not rigorous global error bounds"
    result["scipy_version"] = scipy.__version__
    result["counts"] = counts
    result["cell_results"] = cell_results
    result["method"] = {"variable": "x=E_lab/(k_B T)", "integrator": "scipy.integrate.quad per native cell",
                        "bessel": "actual scipy.special.kve", "epsabs_scaled": EPSABS_SCALED,
                        "epsrel": EPSREL, "limit_per_quad": QUAD_LIMIT,
                        "variance_computed": False, "mpmath_checks": 0}
    return result


def wall_deadline(_signum, _frame) -> None:
    raise TimeoutError("Frozen reference wall budget60s exhausted; no automatic retry")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--expected-primary-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--controller-admission-receipt", type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "Reference output exists; do not replay this identity")
    need(args.output.parent.is_dir(), "Controller must prepare the output directory")
    start_wall, start_cpu = time.monotonic(), time.process_time()
    record = {"schema": "PHYS87_INDEPENDENT_REFERENCE_V1", "status": "FAIL_CLOSED",
              "contract_sha256": CONTRACT_SHA256, "reference_code_sha256": sha256(Path(__file__).read_bytes()),
              "scientific_child_attempts": 1, "automatic_retries": 0,
              "scope": "T=1e8K; source-native finite-window rate and three means; no continuum/tail/uncertainty/variance certificate",
              "production": "NOT_ISSUED", "HH_R10": "OFF"}
    try:
        for key in THREAD_ENV:
            os.environ[key] = "1"
        resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
        signal.signal(signal.SIGALRM, wall_deadline)
        signal.alarm(60)
        contract_raw = (args.unit / "CONTRACT.json").read_bytes()
        need(sha256(contract_raw) == CONTRACT_SHA256, "Frozen contract mismatch")
        contract = json.loads(contract_raw)
        need(contract["budget"]["reference_cpu_s"] == 20 and contract["budget"]["reference_wall_s"] == 60,
             "Reference budget mismatch")
        need(args.controller_admission_receipt.is_file(), "Controller lease/admission receipt required")
        admission_raw = args.controller_admission_receipt.read_bytes()
        json.loads(admission_raw)
        record["controller_admission_receipt_sha256"] = sha256(admission_raw)
        record["controller_admission_note"] = "Controller owns fresh actual resources, pinned shared lease and CPU affinity; this child retains its receipt, does not infer authorization from JSON contents."
        primary_raw = args.primary.read_bytes()
        need(sha256(primary_raw) == args.expected_primary_sha256, "Primary result byte identity mismatch")
        primary = json.loads(primary_raw)
        rows = [row for row in primary["thermal_results"]
                if row["T_K"] == T_K and row["order"] == 32 and row["rate_only"] is False]
        need(len(rows) == 1, "Expected one completed highest-T order32 primary row")
        selected = rows[0]
        need(all(math.isfinite(selected[k]) and selected[k] > 0 for k in FIELDS), "Invalid primary values")
        record["primary_sha256"] = args.expected_primary_sha256
        record["primary_row"] = {key: selected[key] for key in ("T_K", "order", "rate_only", *FIELDS)}
        source = parse_source(args.unit)
        record["source_audit"] = source["audit"]
        reference = compute_reference(source, contract)
        record["reference"] = reference
        tolerance = contract["acceptance"]["independent_relative_rate_and_means"]
        need(tolerance == 1.0e-7, "Frozen independent comparison tolerance changed")
        comparisons = {}
        for key in FIELDS:
            relative = abs(selected[key] - reference[key]) / abs(reference[key])
            comparisons[key] = {"primary": selected[key], "reference": reference[key],
                                "relative_difference": relative, "tolerance": tolerance,
                                "pass": relative <= tolerance}
        record["comparisons"] = comparisons
        record["reference_energy_closure_pass"] = abs(reference["energy_closure_eV"]) <= contract["acceptance"]["energy_closure_abs_eV"]
        all_pass = all(v["pass"] for v in comparisons.values()) and record["reference_energy_closure_pass"]
        record["status"] = "PASS_SCOPED" if all_pass else "FAIL_COMPARISON"
    except Exception as exc:
        record["exception"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    finally:
        signal.alarm(0)
        record["wall_s"] = time.monotonic() - start_wall
        record["cpu_s"] = time.process_time() - start_cpu
        record["thread_environment"] = {key: os.environ.get(key) for key in THREAD_ENV}
        record["cpu_affinity"] = sorted(os.sched_getaffinity(0))
        # Exclusive create preserves the first result, including a failed attempt.
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
    print(json.dumps({"status": record["status"], "output": str(args.output),
                      "cpu_s": record["cpu_s"], "wall_s": record["wall_s"]}))
    return 0 if record["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    sys.exit(main())
