#!/usr/bin/env python3
"""Compare one integrated consumer run to PR96's frozen extended candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def relative_difference(a: np.ndarray, b: np.ndarray) -> float:
    scale = np.maximum(np.maximum(np.abs(a), np.abs(b)), np.finfo(float).tiny)
    return float(np.max(np.abs(a - b) / scale)) if a.size else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-json", type=Path, required=True)
    parser.add_argument("--candidate-json", type=Path, required=True)
    parser.add_argument("--baseline-npz", type=Path, required=True)
    parser.add_argument("--candidate-npz", type=Path, required=True)
    args = parser.parse_args()

    baseline = json.loads(args.baseline_json.read_text())
    candidate = json.loads(args.candidate_json.read_text())
    if len(baseline["history"]) != len(candidate["history"]):
        raise SystemExit("history length mismatch")

    history = {}
    for key in baseline["history"][0]:
        a = np.asarray([row[key] for row in baseline["history"]], dtype=float)
        b = np.asarray([row[key] for row in candidate["history"]], dtype=float)
        history[key] = {
            "exact": bool(np.array_equal(a, b)),
            "max_abs": float(np.max(np.abs(a - b))),
            "max_relative": relative_difference(a, b),
        }

    arrays = {}
    baseline_arrays = {}
    candidate_arrays = {}
    with np.load(args.baseline_npz) as a_npz, np.load(args.candidate_npz) as b_npz:
        if set(a_npz.files) != set(b_npz.files):
            raise SystemExit("dataset member mismatch")
        for key in sorted(a_npz.files):
            a = a_npz[key].copy()
            b = b_npz[key].copy()
            baseline_arrays[key] = a
            candidate_arrays[key] = b
            if a.shape != b.shape or a.dtype != b.dtype:
                raise SystemExit(f"dataset schema mismatch: {key}")
            arrays[key] = {
                "shape": list(a.shape),
                "dtype": str(a.dtype),
                "exact": bool(np.array_equal(a, b)),
                "max_abs": float(np.max(np.abs(a - b))) if a.size else 0.0,
                "max_relative": relative_difference(a.astype(float), b.astype(float)),
            }

    identity = {
        key: candidate["metadata"][key] == baseline["metadata"][key]
        for key in (
            "method",
            "nfev",
            "rtol",
            "steps",
            "nodes",
            "band_eV",
            "order",
            "nmu",
            "shear_ratio",
            "source_scale",
            "source_sha256",
            "claim",
        )
    }
    all_exact = (
        all(row["exact"] for row in history.values())
        and all(row["exact"] for row in arrays.values())
        and all(identity.values())
    )
    time_field_target = 2e-6
    ledger_target = 1e-9
    geometry_target = 1e-11
    ordinary_history = {
        key: row
        for key, row in history.items()
        if key
        not in {
            "energy_ledger_scaled",
            "number_ledger_scaled",
            "delta_pressure_erg_cm3",
        }
    }
    baseline_pressure = np.asarray(
        [row["delta_pressure_erg_cm3"] for row in baseline["history"]]
    )
    candidate_pressure = np.asarray(
        [row["delta_pressure_erg_cm3"] for row in candidate["history"]]
    )
    candidate_photon_energy = np.asarray(
        [row["photon_erg_cm3"] for row in candidate["history"]]
    )
    if np.any(candidate_photon_energy <= 0):
        raise SystemExit("candidate photon energy must remain positive")
    pressure_difference_scaled = float(
        np.max(
            np.abs(baseline_pressure - candidate_pressure)
            / candidate_photon_energy
        )
    )
    candidate_ledger_max = {
        key: max(abs(row[key]) for row in candidate["history"])
        for key in ("energy_ledger_scaled", "number_ledger_scaled")
    }
    candidate_states = candidate_arrays["states"]
    node_count = int(candidate["metadata"]["nodes"])
    candidate_photons = candidate_states[4 : 4 + node_count]
    candidate_fractions = candidate_states[:3]
    numerical_checks = {
        "metadata_identity": all(identity.values()),
        "finite_states": bool(np.isfinite(candidate_states).all()),
        "positive_photons": bool(np.all(candidate_photons >= 0)),
        "ionic_domain": bool(
            np.all((candidate_fractions >= 0) & (candidate_fractions <= 1))
            and np.all(candidate_fractions[1] + candidate_fractions[2] <= 1)
        ),
        "temperature_domain": all(
            30000 <= row["T_K"] <= 110000 for row in candidate["history"]
        ),
        "saved_times_exact": bool(
            np.array_equal(
                baseline_arrays["times_s"], candidate_arrays["times_s"]
            )
        ),
        "saved_mu_exact": bool(
            np.array_equal(baseline_arrays["mu0"], candidate_arrays["mu0"])
        ),
        "saved_weights_exact": bool(
            np.array_equal(
                baseline_arrays["weights"], candidate_arrays["weights"]
            )
        ),
        "ordinary_history_relative": max(
            row["max_relative"] for row in ordinary_history.values()
        )
        <= time_field_target,
        "state_relative": arrays["states"]["max_relative"] <= time_field_target,
        "initial_state_relative": arrays["initial_state"]["max_relative"]
        <= time_field_target,
        "quadrature_energy_relative": arrays["q_eV"]["max_relative"]
        <= geometry_target,
        "pressure_difference_scaled": pressure_difference_scaled
        <= time_field_target,
        "candidate_ledgers": max(candidate_ledger_max.values()) <= ledger_target,
        "ledger_difference": max(
            history[key]["max_abs"]
            for key in ("energy_ledger_scaled", "number_ledger_scaled")
        )
        <= ledger_target,
    }
    numerical_pass = all(numerical_checks.values())
    result = {
        "schema": "rei-physical-provider-integration-comparison-v2-corrected",
        "status": "SCOPED_PASS" if numerical_pass else "FAIL",
        "claim": "New same-input compatibility checks after merging PR94 and PR95, using PR96's pre-existing numerical targets; not replay of the entire original contract, byte-exact reproducibility, independent physical validation, or production admission.",
        "history_epoch_count": len(candidate["history"]),
        "metadata_identity": identity,
        "history": history,
        "dataset_arrays": arrays,
        "all_compared_values_exact": all_exact,
        "numerical_targets": {
            "time_field_relative": time_field_target,
            "ledger_scaled": ledger_target,
            "geometry_identity": geometry_target,
        },
        "numerical_checks": numerical_checks,
        "candidate_ledger_max": candidate_ledger_max,
        "pressure_rule": "max_t(abs(deltaP_baseline(t)-deltaP_candidate(t))/u_gamma_candidate(t)) <= time_field_relative",
        "pressure_difference_scaled_to_candidate_photon_energy": pressure_difference_scaled,
        "environment_note": "Integrated comparison used Python 3.12.3 / NumPy 2.4.2 / SciPy 1.17.0; PR96 recorded Python 3.12.14 / NumPy 2.3.5 / SciPy 1.17.0. The preserved exact-comparison attempt found roundoff-scale deviations. The differing Python/NumPy versions are observations; the cause was not isolated.",
        "excluded_metadata": ["elapsed_wall_s"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not numerical_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
