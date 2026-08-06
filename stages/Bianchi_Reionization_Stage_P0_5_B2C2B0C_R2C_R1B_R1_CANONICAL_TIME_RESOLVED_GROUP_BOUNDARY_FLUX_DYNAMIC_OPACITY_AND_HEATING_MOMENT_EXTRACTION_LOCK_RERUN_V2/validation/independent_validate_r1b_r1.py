#!/usr/bin/env python3
"""Independent replay of the R1B-R1 input-lock gates.

This validator does not call the stage production analysis functions.  Atomic
moments are recomputed with mpmath quadrature from an independently encoded
copy of the locked Verner parameters.  All remaining checks are algebraic
replays over the durable CSV/JSON outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
import pandas as pd

DENSE_GATE = 2.0e-4
NESTED_GATE = 2.0e-4
PHOTON_LEDGER_HARD_GATE = 1.0e-8
ATOMIC_HP_GATE = 2.0e-12
MOMENT_GATE = 1.0e-11
THERMAL_GATE = 2.0e-9

GROUPS = {
    "G1": ("13.6", "24.59"),
    "G2a": ("24.59", "39.5"),
    "G2b": ("39.5", "54.42"),
    "G3": ("54.42", "100.0"),
}
SUPPORT = {
    "HI": {"G1", "G2a", "G2b", "G3"},
    "HeI": {"G2a", "G2b", "G3"},
    "HeII": {"G3"},
}
VERNER = {
    "HI": {"Eth": "13.60", "E0": "0.4298", "sigma0": "5.475e4", "ya": "32.88", "p": "2.963", "yw": "0", "y0": "0", "y1": "0"},
    "HeI": {"Eth": "24.59", "E0": "13.61", "sigma0": "949.2", "ya": "1.469", "p": "3.188", "yw": "2.039", "y0": "0.4434", "y1": "2.136"},
    "HeII": {"Eth": "54.42", "E0": "1.720", "sigma0": "1.369e4", "ya": "32.88", "p": "2.963", "yw": "0", "y0": "0", "y1": "0"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(a: mp.mpf, b: mp.mpf) -> mp.mpf:
    return abs(a - b) / max(abs(a), abs(b), mp.mpf("1e-300"))


def mp_params(species: str) -> dict[str, mp.mpf]:
    return {k: mp.mpf(v) for k, v in VERNER[species].items()}


def sigma(species: str, energy: mp.mpf) -> mp.mpf:
    p = mp_params(species)
    if energy < p["Eth"]:
        return mp.mpf("0")
    x = energy / p["E0"] - p["y0"]
    y = mp.sqrt(x * x + p["y1"] ** 2)
    return (
        mp.mpf("1e-18")
        * p["sigma0"]
        * ((x - 1) ** 2 + p["yw"] ** 2)
        * y ** (p["p"] / 2 - mp.mpf("5.5"))
        / (1 + mp.sqrt(y / p["ya"])) ** p["p"]
    )


def integrate(f, lo: mp.mpf, hi: mp.mpf) -> mp.mpf:
    points = [lo + (hi - lo) * mp.mpf(i) / 8 for i in range(9)]
    return mp.fsum(mp.quad(f, [points[i], points[i + 1]]) for i in range(8))


def atomic_high_precision(stage: Path) -> dict[str, Any]:
    mp.mp.dps = 90
    table = pd.read_csv(stage / "data/atomic_moments/verner_gray_and_limit_moments.csv")
    rows: list[dict[str, Any]] = []
    max_residual = mp.mpf("0")
    for species in ("HI", "HeI", "HeII"):
        for group in ("G1", "G2a", "G2b", "G3"):
            row = table[(table.species == species) & (table.group == group)].iloc[0]
            if group not in SUPPORT[species]:
                assert row.gray_sigma_cm2 == 0.0
                assert row.thin_excess_eV == 0.0
                assert row.thick_excess_eV == 0.0
                rows.append({"species": species, "group": group, "supported": False, "structural_zero": True})
                continue
            lo, hi = map(mp.mpf, GROUPS[group])
            eth = mp_params(species)["Eth"]
            den = integrate(lambda e: e ** mp.mpf("-2.5"), lo, hi)
            sig_den = integrate(lambda e: e ** mp.mpf("-2.5") * sigma(species, e), lo, hi)
            gray = sig_den / den
            thin = integrate(lambda e: e ** mp.mpf("-2.5") * sigma(species, e) * (e - eth), lo, hi) / sig_den
            thick = integrate(lambda e: e ** mp.mpf("-2.5") * (e - eth), lo, hi) / den
            vals = {
                "gray_sigma_cm2": (gray, mp.mpf(str(row.gray_sigma_cm2))),
                "thin_excess_eV": (thin, mp.mpf(str(row.thin_excess_eV))),
                "thick_excess_eV": (thick, mp.mpf(str(row.thick_excess_eV))),
            }
            residuals = {name: rel(reference, stored) for name, (reference, stored) in vals.items()}
            max_residual = max(max_residual, *residuals.values())
            rows.append({
                "species": species,
                "group": group,
                "supported": True,
                "reference": {name: mp.nstr(pair[0], 60) for name, pair in vals.items()},
                "stored": {name: mp.nstr(pair[1], 25) for name, pair in vals.items()},
                "relative_residual": {name: mp.nstr(value, 25) for name, value in residuals.items()},
            })
    return {"precision_dps": 90, "gate": ATOMIC_HP_GATE, "max_relative_residual": float(max_residual), "pass": bool(max_residual < ATOMIC_HP_GATE), "rows": rows}


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    stage = args.stage.resolve()
    repo = stage.parents[1]
    output = args.output or stage / "validation/independent_validation_results.json"
    failures: list[str] = []
    results: dict[str, Any] = {"classification": "R1B_R1_INDEPENDENT_VALIDATION", "stage": stage.name}

    # Byte-locked source subset and canonical compact inputs.
    source_manifest = json.loads((stage / "inputs/CANONICAL_B2C2A_R1_SOURCE_MANIFEST.json").read_text())
    source_failures = []
    for rec in source_manifest["files"]:
        path = stage / "inputs/canonical_b2c2a_r1_src" / rec["path"]
        if not path.exists() or path.stat().st_size != rec["size_bytes"] or sha256(path) != rec["sha256"]:
            source_failures.append(rec["path"])
    check(not source_failures, f"source subset mismatch: {source_failures}", failures)
    lock = json.loads((stage / "INPUT_LOCK.json").read_text())
    compact_checks = []
    for name, rec in lock["canonical_inputs"].items():
        path_text = rec.get("path", "") if isinstance(rec, dict) else ""
        if not path_text.startswith("artifacts/compact/"):
            continue
        path = repo / path_text
        ok = path.exists() and path.stat().st_size == rec["size_bytes"] and sha256(path) == rec["sha256"]
        compact_checks.append({"name": name, "path": path_text, "pass": ok})
        check(ok, f"canonical compact input mismatch: {name}", failures)
    results["input_bytes"] = {"source_subset_pass": not source_failures, "compact_artifacts": compact_checks}

    # Canonical BDF replay and global time-grid selection.
    bdf = json.loads((stage / "data/bdf_replay/canonical_bdf_dense_replay_summary.json").read_text())
    selection = pd.read_csv(stage / "data/bdf_replay/global_quadrature_selection.csv")
    chosen = selection[selection.globally_selected]
    forcing = pd.read_csv(stage / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv")
    check(len(chosen) == 1 and int(chosen.iloc[0].node_count) == 17, "global quadrature did not select N=17", failures)
    check(not bool(selection.loc[selection.node_count == 9, "passes_dense"].iloc[0]), "N=9 unexpectedly passed dense gate", failures)
    check(not bool(selection.loc[selection.node_count == 9, "passes_nested"].iloc[0]), "N=9 unexpectedly passed nested gate", failures)
    check(bdf["history_replay_max_relative_residual"] < 1e-11, "BDF history replay gate failed", failures)
    check(bdf["ledger_replay_max_relative_residual"] < 1e-11, "BDF ledger replay gate failed", failures)
    check(bdf["canonical_ledger_max_relative_residual"] < PHOTON_LEDGER_HARD_GATE, "canonical photon ledger hard gate failed", failures)
    check(bdf["selected_dense_GL256_max_relative_residual"] < DENSE_GATE, "GL256 dense gate failed", failures)
    check(bdf["selected_nested_max_relative_delta"] < NESTED_GATE, "nested quadrature gate failed", failures)
    check(bdf["selected_GL512_max_relative_residual"] < DENSE_GATE, "GL512 independent gate failed", failures)
    check(len(forcing) == 85 and forcing.interval_index.nunique() == 5, "forcing grid shape is not 5x17", failures)
    weight_sums = forcing.groupby("interval_index").weight.sum().to_numpy()
    check(float(np.max(np.abs(weight_sums - 1.0))) < 3e-15, "Clenshaw-Curtis weights do not sum to one", failures)
    check(bool((forcing.N4_exact == 0.0).all()) and bool((forcing["Gamma_HeII_exact_s-1"] == 0.0).all()), "primary structural G3/HeII zeros failed", failures)
    results["bdf_replay"] = {**bdf, "weight_sum_max_residual": float(np.max(np.abs(weight_sums - 1.0))), "hard_photon_ledger_gate": PHOTON_LEDGER_HARD_GATE, "engineering_target_1e-10_pass": bool(bdf["canonical_ledger_max_relative_residual"] < 1e-10)}

    # Atomic moments: independent 90-digit integration.
    atomic_hp = atomic_high_precision(stage)
    check(atomic_hp["pass"], "90-digit atomic moment audit failed", failures)
    atomic_summary = json.loads((stage / "data/atomic_moments/atomic_moment_summary.json").read_text())
    check(atomic_summary["supported_pairs"] == 8, "supported pair count is not eight", failures)
    check(atomic_summary["unsupported_exact_zero"], "unsupported atomic pairs are not exact zero", failures)
    check(atomic_summary["heating_hardening_monotone"], "heating hardening curve is not monotone", failures)
    check(atomic_summary["primary_G3_source_occupation_exact_zero"], "primary G3 source occupation is not exact zero", failures)
    results["atomic_moments"] = {"summary": atomic_summary, "high_precision": atomic_hp}

    # Dynamic opacity and conditional RN disintegration.
    opacity = json.loads((stage / "data/dynamic_opacity/dynamic_opacity_partition_summary.json").read_text())
    audit = pd.read_csv(stage / "data/dynamic_opacity/dynamic_global_moment_audit.csv")
    macro = pd.read_csv(stage / "data/dynamic_opacity/dynamic_macro_disintegration.csv")
    hashes = pd.read_csv(stage / "data/dynamic_opacity/dynamic_node_measure_hashes.csv")
    hierarchy = pd.read_csv(stage / "data/dynamic_opacity/hierarchy_state_moment_audit.csv")
    check(len(audit) == 340 and len(macro) == 6120 and len(hashes) == 340, "opacity evidence row count mismatch", failures)
    for key in ("max_q_sum_residual", "max_kappa_moment_relative_residual", "max_current_moment_relative_residual", "max_common_flux_relative_residual"):
        check(opacity[key] < MOMENT_GATE, f"opacity gate failed: {key}", failures)
    check(opacity["negative_measure_count_total"] == 0, "negative state absorption measure found", failures)
    check(opacity["zero_support_nonzero_allocation_count_total"] == 0, "zero support received nonzero allocation", failures)
    grouped = macro.groupby(["interval_index", "node_index", "group"], sort=False).agg(
        q_macro=("q_macro", "sum"),
        kappa_macro=("kappa_macro_cMpc_inv", "sum"),
        current_macro=("current_macro_s_inv_cMpc3", "sum"),
    ).reset_index()
    merged = audit.merge(grouped, on=["interval_index", "node_index", "group"], validate="one_to_one")
    macro_q_res = float(np.max(np.abs(merged.q_macro - 1.0)))
    macro_k_res = float(np.max(np.abs(merged.kappa_macro - merged.global_kappa_cMpc_inv) / np.maximum(np.abs(merged.global_kappa_cMpc_inv), 1.0)))
    macro_j_res = float(np.max(np.abs(merged.current_macro - merged.global_current_s_inv_cMpc3) / np.maximum(np.abs(merged.global_current_s_inv_cMpc3), 1.0)))
    check(macro_q_res < MOMENT_GATE and macro_k_res < MOMENT_GATE and macro_j_res < MOMENT_GATE, "independent macro reduction failed", failures)
    check(bool(hashes.q_sha256.str.fullmatch(r"[0-9a-f]{64}").all()) and bool(hashes.tau_sha256.str.fullmatch(r"[0-9a-f]{64}").all()), "node logical hashes malformed", failures)
    h_res = {
        "weight": float(np.max(np.abs(hierarchy.weight_sum - 1.0))),
        "xHII": float(np.max(np.abs(hierarchy.mass_xHII - hierarchy.target_xHII))),
        "xHeII": float(np.max(np.abs(hierarchy.mass_xHeII - hierarchy.target_xHeII))),
        "xHeIII": float(np.max(np.abs(hierarchy.mass_xHeIII - hierarchy.target_xHeIII))),
        "temperature_relative": float(np.max(np.abs(hierarchy.temperature_weighted_mean - hierarchy.target_T_K) / np.maximum(np.abs(hierarchy.target_T_K), 1.0))),
    }
    check(max(h_res.values()) < 1e-10, "hierarchy state reconstruction gate failed", failures)
    results["dynamic_opacity"] = {**opacity, "independent_macro_q_residual": macro_q_res, "independent_macro_kappa_residual": macro_k_res, "independent_macro_current_residual": macro_j_res, "hierarchy_replay": h_res}

    # Heating and thermal ownership.
    heating = json.loads((stage / "data/heating_lock/heating_lock_summary.json").read_text())
    calibration = pd.read_csv(stage / "data/heating_lock/bdf_heating_moment_calibration.csv")
    thermal = pd.read_csv(stage / "data/heating_lock/time_resolved_thermal_forcing.csv")
    check(heating["max_calibration_relative_residual"] < THERMAL_GATE, "heating calibration gate failed", failures)
    check(heating["max_thermal_rhs_identity_relative_residual"] < THERMAL_GATE, "thermal RHS identity gate failed", failures)
    check(heating["hardening_coordinates_inside_unit_interval"], "hardening coordinate left [0,1]", failures)
    check(len(thermal) == 85 and int(calibration.supported.sum()) == 8, "heating evidence row count mismatch", failures)
    rhs = thermal["thermal_photoheat_erg_cm-3_s-1"] - thermal["thermal_cooling_total_erg_cm-3_s-1"] - thermal["thermal_expansion_work_erg_cm-3_s-1"]
    scale = np.maximum(np.abs(thermal["thermal_thermal_rhs_erg_cm-3_s-1"]), np.abs(thermal["thermal_photoheat_erg_cm-3_s-1"]) + np.abs(thermal["thermal_cooling_total_erg_cm-3_s-1"]) + np.abs(thermal["thermal_expansion_work_erg_cm-3_s-1"]))
    independent_rhs = float(np.max(np.abs(rhs - thermal["thermal_thermal_rhs_erg_cm-3_s-1"]) / np.maximum(scale, 1e-300)))
    check(independent_rhs < THERMAL_GATE, "independent thermal identity failed", failures)
    results["heating"] = {**heating, "independent_thermal_rhs_relative_residual": independent_rhs}

    # Dimensional ledger (declarative check against stored column units).
    expected_columns = {
        "N_G1_cMpc-3", "kappa_G1_cMpc-1", "absorption_G1_s-1_cMpc-3",
        "thermal_photoheat_erg_cm-3_s-1", "proper_cell_length_cm",
    }
    dimension_sources = set(forcing.columns) | set(audit.columns)
    check(expected_columns.issubset(dimension_sources), "dimension-bearing columns missing", failures)
    results["dimensions"] = {
        "tau": "n_s [cm^-3] sigma_sg [cm^2] Lproper [cm] is dimensionless",
        "q": "dimensionless conditional measure",
        "kappa": "cMpc^-1 inherited absolute normalization distributed by q",
        "J": "s^-1 cMpc^-3",
        "incident_flux": "s^-1 cMpc^-2",
        "thermal": "erg cm^-3 s^-1",
        "explicit_constants_policy": ["c", "hbar", "k_B"],
    }

    results["failed_checks"] = failures
    results["pass"] = not failures
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": not failures, "failed_checks": failures, "atomic_hp_max": atomic_hp["max_relative_residual"], "selected_N": bdf["selected_global_node_count"]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
