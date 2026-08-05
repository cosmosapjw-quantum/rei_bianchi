#!/usr/bin/env python3
"""Build a non-authorizing one-bound diagnostic from emitted Farkas rays.

This script does not modify the prelocked rate box.  For each single-row/box
Farkas certificate, it asks how far one attenuation coordinate alone would
have to leave [0,1] to remove that row obstruction.  The result helps classify
which physical operator family is missing; it is not a calibration procedure.
"""
from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"
RECEIPT = STAGE / "receipts/dual_missing_rate_diagnostic.json"
CSV_OUT = DATA / "dual_single_bound_extension_diagnostic.csv"
FAMILIES = ("M", "I", "U", "C", "J_G1", "J_G2a")


def finite_quantiles(series: pd.Series) -> dict[str, float | None]:
    values = series.replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return {key: None for key in ("min", "p10", "median", "p90", "max")}
    q = values.quantile([0.0, 0.1, 0.5, 0.9, 1.0])
    return {
        "min": float(q.loc[0.0]),
        "p10": float(q.loc[0.1]),
        "median": float(q.loc[0.5]),
        "p90": float(q.loc[0.9]),
        "max": float(q.loc[1.0]),
    }


def main() -> None:
    rates = pd.read_csv(DATA / "rate_interval_lock.csv")
    rate_index = {
        (
            row.shape_lane,
            int(row.interval_index),
            int(row.substep),
            int(row.macro_index),
            row.family,
        ): row
        for row in rates.itertuples()
    }

    records: list[dict[str, Any]] = []
    for line in (DATA / "dual_farkas_kkt_certificates.jsonl").read_text().splitlines():
        if not line:
            continue
        case = json.loads(line)
        lp = case["lp"]
        if lp["pass"]:
            continue
        cert = lp["farkas_certificate"]
        if cert["type"] != "SINGLE_ROW_BOX_FARKAS":
            raise AssertionError("diagnostic requires the emitted single-row/box certificate")
        row = np.asarray(cert["violated_row_coefficients"], dtype=float)
        deficit = float(cert["violated_row_minimum_minus_rhs"])
        if not deficit > 0.0:
            raise AssertionError("Farkas row must have a positive box deficit")
        constraint = str(cert["active_terms"][0]["constraint"])

        candidates: list[dict[str, Any]] = []
        for column, coefficient in enumerate(row):
            if coefficient == 0.0:
                continue
            extension = deficit / abs(float(coefficient))
            required_z = -extension if coefficient > 0.0 else 1.0 + extension
            family = FAMILIES[column]
            locked = rate_index[
                (
                    case["shape_lane"],
                    int(case["interval_index"]),
                    int(case["substep"]),
                    int(case["macro_index"]),
                    family,
                )
            ]
            a_lower = float(locked.a_lower_fast)
            a_upper = float(locked.a_upper_slow)
            required_a = a_lower + (a_upper - a_lower) * required_z
            required_k: float | None
            factor: float | None
            if required_a <= 1.0:
                required_k = None
                factor = None
            else:
                required_k = -math.log1p(-1.0 / required_a) / float(case["dt_Myr"])
                if required_z < 0.0:
                    factor = required_k / float(locked.k_max_Myr_inv)
                else:
                    factor = float(locked.k_min_Myr_inv) / required_k
            candidates.append(
                {
                    "extension": extension,
                    "family": family,
                    "direction": "z_below_0" if required_z < 0.0 else "z_above_1",
                    "required_z": required_z,
                    "required_a": required_a,
                    "required_k_Myr_inv": required_k,
                    "rate_factor_outside_locked_bound": factor,
                    "locked_k_min_Myr_inv": float(locked.k_min_Myr_inv),
                    "locked_k_max_Myr_inv": float(locked.k_max_Myr_inv),
                }
            )
        if not candidates:
            raise AssertionError("violated Farkas row has no nonzero coefficient")
        best = min(candidates, key=lambda item: item["extension"])
        records.append(
            {
                "shape_lane": case["shape_lane"],
                "interval_index": int(case["interval_index"]),
                "substep": int(case["substep"]),
                "macro_index": int(case["macro_index"]),
                "constraint": constraint,
                "box_deficit": deficit,
                "best_single_bound_family": best["family"],
                "best_single_bound_direction": best["direction"],
                "minimum_z_extension": best["extension"],
                "required_z": best["required_z"],
                "required_a": best["required_a"],
                "required_k_Myr_inv": best["required_k_Myr_inv"],
                "rate_factor_outside_locked_bound": best["rate_factor_outside_locked_bound"],
                "finite_positive_scalar_rate_exists": best["required_k_Myr_inv"] is not None,
                "locked_k_min_Myr_inv": best["locked_k_min_Myr_inv"],
                "locked_k_max_Myr_inv": best["locked_k_max_Myr_inv"],
            }
        )

    frame = pd.DataFrame.from_records(records)
    if len(frame) != 497:
        raise AssertionError(f"expected 497 equilibrium no-go cases, found {len(frame)}")
    expected_constraints = {
        "CYCLING_CAPACITY": 209,
        "J_G1_NONNEGATIVE": 125,
        "J_G2A_NONNEGATIVE": 157,
        "MACRO_MASS_CAP": 6,
    }
    observed_constraints = {str(k): int(v) for k, v in frame["constraint"].value_counts().items()}
    if observed_constraints != expected_constraints:
        raise AssertionError(f"constraint census changed: {observed_constraints}")

    CSV_OUT.write_text(frame.to_csv(index=False))
    constraint_rate_factors = {
        constraint: finite_quantiles(group["rate_factor_outside_locked_bound"])
        for constraint, group in frame.groupby("constraint", sort=True)
    }
    payload = {
        "classification": "DUAL_MISSING_RATE_DIAGNOSTIC_NON_AUTHORIZING",
        "status": "PASS",
        "case_count": len(frame),
        "constraint_counts": observed_constraints,
        "best_single_bound_family_counts": {
            str(k): int(v) for k, v in frame["best_single_bound_family"].value_counts().items()
        },
        "direction_counts": {
            str(k): int(v) for k, v in frame["best_single_bound_direction"].value_counts().items()
        },
        "finite_positive_scalar_rate_count": int(frame["finite_positive_scalar_rate_exists"].sum()),
        "no_finite_positive_scalar_rate_count": int((~frame["finite_positive_scalar_rate_exists"]).sum()),
        "minimum_z_extension": float(frame["minimum_z_extension"].min()),
        "median_z_extension": float(frame["minimum_z_extension"].median()),
        "maximum_z_extension": float(frame["minimum_z_extension"].max()),
        "finite_rate_factor_quantiles_by_constraint": constraint_rate_factors,
        "mass_cap_required_rate_factor_range": [
            float(frame.loc[frame["constraint"].eq("MACRO_MASS_CAP"), "rate_factor_outside_locked_bound"].min()),
            float(frame.loc[frame["constraint"].eq("MACRO_MASS_CAP"), "rate_factor_outside_locked_bound"].max()),
        ],
        "interpretation": (
            "For each emitted single-row/box Farkas ray, this reports the smallest one-coordinate "
            "extension outside z in [0,1]. It is diagnostic only. It neither proves that this is "
            "the unique repair nor authorizes any post-result widening of the physical rate lock."
        ),
        "all_rate_bound_changes_authorized": False,
        "node_rate_fitting_used": False,
        "output_csv": "data/dual_single_bound_extension_diagnostic.csv",
    }
    RECEIPT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
