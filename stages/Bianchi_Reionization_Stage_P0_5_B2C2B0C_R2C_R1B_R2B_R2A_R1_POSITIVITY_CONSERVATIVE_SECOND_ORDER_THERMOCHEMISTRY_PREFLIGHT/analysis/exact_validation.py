#!/usr/bin/env python3
"""Independent high-precision validation for the R2B-R2A-R1 preflight."""
from __future__ import annotations
from decimal import Decimal, getcontext
from pathlib import Path
import json
import numpy as np
import sympy as sp

getcontext().prec = 90
STAGE = Path(__file__).resolve().parents[1]
ATTEMPT = STAGE / "attempts/ATTEMPT_3_ANALYTIC_THERMAL_NEWTON_OPTIMIZATION"
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)


def d(x: object) -> Decimal:
    return Decimal(str(x))


def main() -> int:
    result = json.loads((ATTEMPT / "results.json").read_text())
    benchmark = json.loads((STAGE / "receipts/MATCHED_ACCURACY_BENCHMARK.json").read_text())
    rows = {(row["lane"], int(row["partition"])): row for row in result["rows"]}

    lane_checks = {}
    maxima = {
        "H": Decimal(0), "He": Decimal(0), "owner": Decimal(0),
        "photon": Decimal(0), "thermal": Decimal(0), "PDS": Decimal(0),
    }
    minimum_species: Decimal | None = None
    for lane in LANES:
        r1024 = rows[(lane, 1024)]
        r2048 = rows[(lane, 2048)]
        lane_checks[lane] = {
            "partition_1024_fails_local_error": not bool(r1024["passes_local_error"]),
            "partition_2048_passes_local_error": bool(r2048["passes_local_error"]),
            "partition_2048_all_gates_pass": bool(r2048["all_gates_pass"]),
            "partition_2048_local_error": r2048["local_error"],
        }
        maxima["H"] = max(maxima["H"], d(r2048["max_H_residual"]))
        maxima["He"] = max(maxima["He"], d(r2048["max_He_residual"]))
        maxima["owner"] = max(maxima["owner"], d(r2048["max_owner_residual"]))
        maxima["photon"] = max(maxima["photon"], d(r2048["max_photon_residual"]))
        maxima["thermal"] = max(maxima["thermal"], d(r2048["max_thermal_residual"]))
        maxima["PDS"] = max(maxima["PDS"], d(r2048["max_PDS_residual"]))
        species = d(r2048["minimum_species"])
        minimum_species = species if minimum_species is None else min(minimum_species, species)

    # Alexander SDIRK2 order and stiff-accuracy identities.  SymPy owns the
    # exact algebra; Decimal-90 is retained as an independent numerical replay.
    gamma_exact = sp.Integer(1) - sp.Integer(1) / sp.sqrt(2)
    order1_exact = sp.simplify((1 - gamma_exact) + gamma_exact - 1)
    order2_exact = sp.simplify((1 - gamma_exact) * gamma_exact + gamma_exact - sp.Rational(1, 2))
    sqrt2 = d(2).sqrt()
    gamma = d(1) - d(1) / sqrt2
    order1 = (d(1) - gamma) + gamma - d(1)
    order2 = (d(1) - gamma) * gamma + gamma - d("0.5")
    stiff_accuracy = {
        "b1_minus_a21": str((d(1) - gamma) - (d(1) - gamma)),
        "b2_minus_a22": str(gamma - gamma),
    }

    # Exact constructive nonuniqueness of a net helium RHS (-1,0,+1).
    direct = np.zeros((3, 3), dtype=np.int64)
    direct[2, 0] = 1  # HeI -> HeIII
    sequential = np.zeros((3, 3), dtype=np.int64)
    sequential[1, 0] = 1  # HeI -> HeII
    sequential[2, 1] = 1  # HeII -> HeIII
    rhs_direct = direct.sum(axis=1) - direct.sum(axis=0)
    rhs_sequential = sequential.sum(axis=1) - sequential.sum(axis=0)
    pds_nonuniqueness = {
        "target_rhs": [-1, 0, 1],
        "direct_flux": direct.tolist(),
        "sequential_flux": sequential.tolist(),
        "direct_rhs": rhs_direct.tolist(),
        "sequential_rhs": rhs_sequential.tolist(),
        "same_net_rhs": bool(np.array_equal(rhs_direct, rhs_sequential)),
        "different_flux_ownership": bool(not np.array_equal(direct, sequential)),
        "interpretation": (
            "A conservative net RHS does not uniquely identify event-resolved transfer "
            "or energy ownership in the three-state helium block."
        ),
    }

    checks = {
        "all_lanes_science_pass": bool(result["science_pass"]),
        "science_parity_pass": bool(result["science_parity"]["pass"]),
        "science_parity_difference_le_1e-10": (
            d(result["science_parity"]["maximum_absolute_science_metric_difference"])
            <= d("1e-10")
        ),
        "performance_promotion_pass": bool(benchmark["performance_promotion_pass"]),
        "matched_accuracy_both_pass": bool(
            benchmark["benchmark_pair"]["both_below_local_error_gate_2e-4"]
        ),
        "all_lane_2048_pass": all(
            item["partition_2048_passes_local_error"]
            and item["partition_2048_all_gates_pass"]
            for item in lane_checks.values()
        ),
        "all_lane_1024_fail_local_error": all(
            item["partition_1024_fails_local_error"] for item in lane_checks.values()
        ),
        "H_gate": maxima["H"] <= d("1e-11"),
        "He_gate": maxima["He"] <= d("1e-11"),
        "owner_gate": maxima["owner"] <= d("1e-11"),
        "photon_gate": maxima["photon"] <= d("1e-8"),
        "thermal_gate": maxima["thermal"] <= d("1e-10"),
        "PDS_reconstruction_gate": maxima["PDS"] <= d("1e-11"),
        "strict_positivity": minimum_species is not None and minimum_species > 0,
        "SDIRK_order1_exact": order1_exact == 0,
        "SDIRK_order2_exact": order2_exact == 0,
        "SDIRK_decimal90_replay": abs(order1) <= d("1e-80") and abs(order2) <= d("1e-80"),
        "PDS_nonuniqueness_certificate": (
            pds_nonuniqueness["same_net_rhs"]
            and pds_nonuniqueness["different_flux_ownership"]
        ),
    }
    passed = all(checks.values())
    output = {
        "classification": "R2B_R2A_R1_DECIMAL90_AND_EXACT_VALIDATION",
        "pass": passed,
        "checks": checks,
        "lane_checks": lane_checks,
        "maxima": {key: str(value) for key, value in maxima.items()},
        "minimum_species": str(minimum_species),
        "sdirk2": {
            "gamma": str(gamma),
            "order1_exact": str(order1_exact),
            "order2_exact": str(order2_exact),
            "order1_decimal90_residual": str(order1),
            "order2_decimal90_residual": str(order2),
            "stiff_accuracy_residuals": stiff_accuracy,
        },
        "pds_nonuniqueness": pds_nonuniqueness,
        "claim_boundary": (
            "The stage validates a deterministic net-RHS PDS closure. Event-resolved "
            "reaction ownership is not identified and remains a required next lock."
        ),
    }
    path = STAGE / "receipts/EXACT_VALIDATION.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": passed, "checks": checks}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
