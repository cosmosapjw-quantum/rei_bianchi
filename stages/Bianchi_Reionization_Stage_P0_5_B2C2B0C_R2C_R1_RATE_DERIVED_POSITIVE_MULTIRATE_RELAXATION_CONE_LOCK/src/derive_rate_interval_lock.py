"""Derive and freeze R2C-R1 macro-shared rate intervals before feasibility."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rate_interval_model import (  # noqa: E402
    K_B_ERG_PER_K,
    derive_positive_interval,
    family_attenuation_inverse,
    macro_process_evidence,
    secant_turnover_myr_inv,
)

FAMILIES = ("M", "I", "U", "C", "J_G1", "J_G2a")
PHYSICAL = {"M": "PHYSICAL", "I": "PHYSICAL", "U": "PHYSICAL", "C": "NUISANCE_INTERVAL", "J_G1": "NUISANCE_INTERVAL", "J_G2a": "NUISANCE_INTERVAL"}
SHAPE_LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
NODES_PER_MACRO = 2560
MACROS_PER_CASE = 18


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_r2c_api(repo: Path):
    src = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_MOMENT_CONSTRAINED_NODE_CHEMISTRY_RELAXATION_AUDIT/src"
    sys.path.insert(0, str(src))
    import run_relaxation_audit as api  # type: ignore
    return api


def load_transfer_ledger(repo: Path) -> pd.DataFrame:
    artifact = repo / "artifacts/compact/Bianchi_Reionization_Stage_P0_5_B2C2B0C_JOINT_CHEMISTRY_SINK_RESERVOIR_HISTORY_LOCK_compact_bundle.zip"
    with zipfile.ZipFile(artifact) as z:
        member = next(name for name in z.namelist() if name.endswith("data/primary_joint_ledger.csv"))
        with z.open(member) as f:
            frame = pd.read_csv(f)
    return frame[["interval_index", "substep", "mass_transfer_ionized_fraction", "mass_transfer_temperature"]].copy()


def family_totals(endpoint) -> dict[str, float]:
    return {
        "M": float(np.sum(endpoint.mass)),
        "I": float(np.sum(endpoint.ionized)),
        "U": float(np.sum(endpoint.thermal)),
        "C": float(np.sum(endpoint.capacity)),
        "J_G1": float(np.sum(endpoint.current[:, 0])),
        "J_G2a": float(np.sum(endpoint.current[:, 1])),
    }


def endpoint_changed(y0: float, y1: float) -> bool:
    return abs(y1 - y0) > 1.0e-14 * max(abs(y0), abs(y1), 1.0)


def transfer_slice(frame: pd.DataFrame, macro_index: int) -> tuple[np.ndarray, np.ndarray]:
    subset = frame[frame["macro_index"] == macro_index].sort_values("micro_index")
    if len(subset) != NODES_PER_MACRO:
        raise RuntimeError("transfer support mismatch")
    return (
        subset["mass_transfer_positive_H_s_inv_cMpc3"].to_numpy(float),
        subset["mass_transfer_negative_H_s_inv_cMpc3"].to_numpy(float),
    )


def process_for_macro(endpoint, transfer_frame: pd.DataFrame | None, macro_index: int, transfer_x: float, transfer_t: float):
    start = macro_index * NODES_PER_MACRO
    stop = start + NODES_PER_MACRO
    if transfer_frame is None:
        tp = np.zeros(NODES_PER_MACRO)
        tn = np.zeros(NODES_PER_MACRO)
    else:
        tp, tn = transfer_slice(transfer_frame, macro_index)
    return macro_process_evidence(
        mass=endpoint.mass[start:stop],
        x_hii=endpoint.x_hii[start:stop],
        temperature_k=endpoint.temperature_k[start:stop],
        n_h_cm3=endpoint.n_h_cm3[start:stop],
        capacity=endpoint.capacity[start:stop],
        current=endpoint.current[start:stop],
        phi=endpoint.phi,
        transfer_positive=tp,
        transfer_negative=tn,
        z=endpoint.z,
        transfer_x_hii=transfer_x,
        transfer_temperature_k=transfer_t,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--state-input", type=Path, required=True)
    parser.add_argument("--group-input", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    stage = args.stage.resolve()
    api = load_r2c_api(repo)

    nodes = api.load_node_tables(args.state_input, args.group_input)
    transfer_cols = [
        "shape_lane", "interval_index", "substep", "macro_index", "micro_index",
        "mass_transfer_positive_H_s_inv_cMpc3", "mass_transfer_negative_H_s_inv_cMpc3",
    ]
    transfer = pd.read_csv(
        args.state_input,
        usecols=transfer_cols,
        dtype={"shape_lane": "category", "interval_index": "int16", "substep": "int8", "macro_index": "int8", "micro_index": "int16"},
    )
    for key in ("shape_lane", "interval_index", "substep", "macro_index", "micro_index"):
        a = nodes[key].astype(str).to_numpy() if key == "shape_lane" else nodes[key].to_numpy()
        b = transfer[key].astype(str).to_numpy() if key == "shape_lane" else transfer[key].to_numpy()
        if not np.array_equal(a, b):
            raise RuntimeError(f"transfer alignment mismatch: {key}")
    nodes = nodes.copy()
    nodes["mass_transfer_positive_H_s_inv_cMpc3"] = transfer["mass_transfer_positive_H_s_inv_cMpc3"].to_numpy(float)
    nodes["mass_transfer_negative_H_s_inv_cMpc3"] = transfer["mass_transfer_negative_H_s_inv_cMpc3"].to_numpy(float)

    global_df = pd.read_csv(repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data/global_moment_lock.csv").sort_values(["interval_index", "substep"])
    transfer_ledger = load_transfer_ledger(repo)
    transfer_lookup = {(int(r.interval_index), int(r.substep)): (float(r.mass_transfer_ionized_fraction), float(r.mass_transfer_temperature)) for r in transfer_ledger.itertuples(index=False)}
    initial = api.load_initial_global(repo)

    rows: list[dict[str, object]] = []
    endpoint_keys = [(int(r.interval_index), int(r.substep), float(r.dt_Myr), float(r.z_mid)) for r in global_df.itertuples(index=False)]
    for lane in SHAPE_LANES:
        lane_nodes = nodes[nodes["shape_lane"].astype(str) == lane]
        i0, s0, _, _ = endpoint_keys[0]
        first_frame = lane_nodes[(lane_nodes["interval_index"] == i0) & (lane_nodes["substep"] == s0)]
        first_endpoint = api.endpoint_from_frame(first_frame)
        previous = api.construct_initial_endpoint(first_endpoint, initial, nodes_per_macro=NODES_PER_MACRO)
        previous_transfer_frame = None
        previous_transfer_x = 1.0
        previous_transfer_t = float(initial.temperature_sink_k)

        for interval_index, substep, dt_myr, z_mid in endpoint_keys:
            frame = lane_nodes[(lane_nodes["interval_index"] == interval_index) & (lane_nodes["substep"] == substep)].copy()
            target = api.endpoint_from_frame(frame)
            transfer_x, transfer_t = transfer_lookup[(interval_index, substep)]
            for macro in range(MACROS_PER_CASE):
                start = macro * NODES_PER_MACRO
                stop = start + NODES_PER_MACRO
                p0 = api.slice_macro(previous, macro)
                p1 = api.slice_macro(target, macro)
                ev0 = process_for_macro(previous, previous_transfer_frame, macro, previous_transfer_x, previous_transfer_t)
                ev1 = process_for_macro(target, frame, macro, transfer_x, transfer_t)
                totals0 = family_totals(p0)
                totals1 = family_totals(p1)
                for family in FAMILIES:
                    secant = secant_turnover_myr_inv(totals0[family], totals1[family], dt_myr)
                    interval = derive_positive_interval(
                        family=family,
                        estimates_myr_inv={"secant": secant, "start_process": ev0[family], "end_process": ev1[family]},
                        endpoint_changed=endpoint_changed(totals0[family], totals1[family]),
                        dt_myr=dt_myr,
                        identifiability=PHYSICAL[family],
                    )
                    row = {
                        "shape_lane": lane,
                        "interval_index": interval_index,
                        "substep": substep,
                        "z_mid": z_mid,
                        "dt_Myr": dt_myr,
                        "macro_index": macro,
                        "family": family,
                        "identifiability": interval.identifiability,
                        "status": interval.status,
                        "usable": interval.usable,
                        "endpoint_changed": interval.endpoint_changed,
                        "endpoint_previous": totals0[family],
                        "endpoint_target": totals1[family],
                        "evidence_secant_Myr_inv": secant,
                        "evidence_start_process_Myr_inv": ev0[family],
                        "evidence_end_process_Myr_inv": ev1[family],
                        "k_min_Myr_inv": interval.k_min_myr_inv,
                        "k_max_Myr_inv": interval.k_max_myr_inv,
                    }
                    if interval.usable:
                        row["a_lower_fast"] = family_attenuation_inverse(interval.k_max_myr_inv, dt_myr)
                        row["a_upper_slow"] = family_attenuation_inverse(interval.k_min_myr_inv, dt_myr)
                    else:
                        row["a_lower_fast"] = np.nan
                        row["a_upper_slow"] = np.nan
                    rows.append(row)
            previous = target
            previous_transfer_frame = frame
            previous_transfer_x = transfer_x
            previous_transfer_t = transfer_t

    out = pd.DataFrame(rows).sort_values(["shape_lane", "interval_index", "substep", "macro_index", "family"]).reset_index(drop=True)
    if len(out) != 3 * 10 * 18 * 6:
        raise RuntimeError(f"unexpected rate lock row count: {len(out)}")
    data_dir = stage / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "rate_interval_lock.csv"
    out.to_csv(path, index=False, float_format="%.17e")
    summary = {
        "classification": "PRE_FEASIBILITY_RATE_INTERVAL_LOCK",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "row_count": int(len(out)),
        "macro_cases": 540,
        "families": list(FAMILIES),
        "unusable_rows": int((~out["usable"]).sum()),
        "status_counts": {str(k): int(v) for k, v in out["status"].value_counts().items()},
        "family_ranges_Myr_inv": {
            family: {
                "global_min": float(out.loc[(out.family == family) & out.usable, "k_min_Myr_inv"].min()),
                "global_max": float(out.loc[(out.family == family) & out.usable, "k_max_Myr_inv"].max()),
            }
            for family in FAMILIES
        },
        "feasibility_examined": False,
        "node_rate_fitting_used": False,
        "mode_lock": {
            "one_mode_first": True,
            "two_mode_allowed_only_after_one_mode_trajectory_failure": True,
            "two_mode_rates": "exact prelocked family k_min/k_max",
            "maximum_modes": 2,
        },
        "rate_lock_sha256": sha256(path),
    }
    (data_dir / "rate_interval_lock_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (stage / "state/RATE_INTERVAL_LOCK_RECEIPT.json").write_text(json.dumps({**summary, "status": "LOCKED_BEFORE_FEASIBILITY"}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
