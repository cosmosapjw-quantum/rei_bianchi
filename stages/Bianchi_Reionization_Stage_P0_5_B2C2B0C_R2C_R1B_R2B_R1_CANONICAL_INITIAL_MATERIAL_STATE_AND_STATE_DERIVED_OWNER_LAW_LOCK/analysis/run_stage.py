#!/usr/bin/env python3
"""Build the full R2B-R1 material-state/owner-law evidence matrix.

This stage evaluates 85 canonical BDF forcing nodes as independent snapshots.
It does not integrate a history.  The five midpoint rows receive predeclared
H/He/thermal perturbations and the three subgrid shape lanes are compared
without post-hoc selection.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]
R1 = REPO / "stages" / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
R2A = REPO / "stages" / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


initial_mod = load("r2b_r1_initial_material_state_stage", HERE / "initial_material_state.py")
law_mod = load("r2b_r1_state_derived_owner_law_stage", HERE / "state_derived_owner_law.py")


def rel(a: float, b: float, floor: float = 1.0e-300) -> float:
    return abs(float(a) - float(b)) / max(abs(float(a)), abs(float(b)), floor)


def normalized(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    total = math.fsum(float(v) for v in x)
    return x / total if total > 0.0 else np.zeros_like(x)


def save_initial_state(state: Any, output: Path) -> None:
    frame = state.frame
    arrays = {
        name: frame[name].to_numpy()
        for name in [
            "macro_index", "micro_index", "W_node", "W_macro", "w_micro",
            "delta_total", "N_HI", "N_HII", "N_HeI", "N_HeII",
            "N_HeIII", "U_resolved", "T_K",
        ]
    }
    np.savez_compressed(output / "initial_material_state_z6.npz", **arrays)
    (output / "initial_material_state_metadata.json").write_text(
        json.dumps(
            {**state.metadata, "array_hashes": state.array_hashes},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=STAGE / "data")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--stop-index", type=int, default=None)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    initial = initial_mod.build_initial_material_state(r1_root=R1, r2a_root=R2A)
    save_initial_state(initial, output)
    model = law_mod.StateDerivedOwnerLaw(r1_root=R1, r2a_root=R2A, initial_state=initial)

    owner_frames: list[pd.DataFrame] = []
    node_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []
    perturbation_rows: list[dict[str, Any]] = []
    tv_rows: list[dict[str, Any]] = []

    forcing_all = model.forcing.copy()
    stop_index = len(forcing_all) if args.stop_index is None else int(args.stop_index)
    start_index = int(args.start_index)
    if not (0 <= start_index < stop_index <= len(forcing_all)):
        raise ValueError(f"invalid chunk [{start_index}, {stop_index}) for {len(forcing_all)} rows")
    forcing = forcing_all.iloc[start_index:stop_index].copy()
    midpoint_keys = set(
        (int(r.interval_index), int(r.node_index))
        for r in forcing_all[np.isclose(forcing_all["fraction"], 0.5)].itertuples()
    )

    max_owner_kappa = 0.0
    max_owner_current = 0.0
    max_node_current = 0.0
    structural_zero_violations = 0
    negative_allocation_count = 0
    zero_support_nonzero_count = 0
    state_sensitivity_failures = 0

    for counter, rec in enumerate(forcing.to_dict(orient="records"), start=1):
        snapshot = initial_mod.build_material_snapshot_from_forcing_row(
            forcing_row=rec, r1_root=R1, r2a_root=R2A
        )
        result = model.evaluate(forcing_row=rec, state_frame=snapshot.frame)
        owner = result.owner_table.copy()
        owner.insert(0, "interval_index", int(rec["interval_index"]))
        owner.insert(1, "node_index", int(rec["node_index"]))
        owner.insert(2, "fraction", float(rec["fraction"]))
        owner.insert(3, "z_snapshot", float(snapshot.metadata["source_redshift"]))
        owner_frames.append(owner)

        h = float((snapshot.frame.N_HI + snapshot.frame.N_HII).sum())
        he = float(
            (snapshot.frame.N_HeI + snapshot.frame.N_HeII + snapshot.frame.N_HeIII).sum()
        )
        snapshot_rows.append(
            {
                "interval_index": int(rec["interval_index"]),
                "node_index": int(rec["node_index"]),
                "fraction": float(rec["fraction"]),
                "z_snapshot": float(snapshot.metadata["source_redshift"]),
                "H_nuclei_relative_residual": rel(h, snapshot.metadata["global_H_nuclei_cMpc-3"]),
                "He_nuclei_relative_residual": rel(he, snapshot.metadata["global_He_nuclei_cMpc-3"]),
                "xHII_relative_residual": rel(float(snapshot.frame.N_HII.sum() / h), float(rec["xHII"])),
                "xHeI_relative_residual": rel(float(snapshot.frame.N_HeI.sum() / he), float(rec["xHeI"])),
                "xHeII_relative_residual": rel(float(snapshot.frame.N_HeII.sum() / he), float(rec["xHeII"])),
                "xHeIII_relative_residual": rel(float(snapshot.frame.N_HeIII.sum() / he), float(rec["xHeIII"])),
                "U_relative_residual": rel(float(snapshot.frame.U_resolved.sum()), snapshot.metadata["global_U_resolved_erg_cMpc-3"]),
                "minimum_species": float(snapshot.frame[["N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII"]].min().min()),
                "minimum_temperature_K": float(snapshot.frame.T_K.min()),
                "thermal_normalization_factor": float(snapshot.metadata["thermal_normalization_factor"]),
            }
        )

        for group, sub in result.owner_table.groupby("group", sort=False):
            kappa_target = float(sub.authoritative_kappa_cMpc_inv.iloc[0])
            current_target = float(sub.authoritative_current_s_inv_cMpc3.iloc[0])
            max_owner_kappa = max(max_owner_kappa, rel(float(sub.conditioned_kappa_cMpc_inv.sum()), kappa_target))
            max_owner_current = max(max_owner_current, rel(float(sub.owner_current_s_inv_cMpc3.sum()), current_target, 1.0))

        for key, allocation in result.node_allocations.items():
            group, component = key
            row = result.owner_table[
                (result.owner_table.group == group)
                & (result.owner_table.component == component)
            ].iloc[0]
            target = float(row.owner_current_s_inv_cMpc3)
            support = result.node_support[key]
            node_residual = rel(float(math.fsum(float(x) for x in allocation)), target, 1.0)
            max_node_current = max(max_node_current, node_residual)
            negatives = int(np.count_nonzero(allocation < 0.0))
            zero_support_nonzero = int(np.count_nonzero((~support) & (allocation != 0.0)))
            negative_allocation_count += negatives
            zero_support_nonzero_count += zero_support_nonzero
            if (component, group) not in law_mod.SUPPORT and (
                float(row.conditioned_kappa_cMpc_inv) != 0.0
                or target != 0.0
                or np.any(allocation != 0.0)
            ):
                structural_zero_violations += 1
            node_rows.append(
                {
                    "interval_index": int(rec["interval_index"]),
                    "node_index": int(rec["node_index"]),
                    "fraction": float(rec["fraction"]),
                    "group": group,
                    "component": component,
                    "owner_total_s_inv_cMpc3": target,
                    "allocation_sum_relative_residual": node_residual,
                    "minimum_allocation": float(allocation.min()),
                    "negative_allocation_count": negatives,
                    "zero_support_nonzero_allocation_count": zero_support_nonzero,
                    "support_count": int(np.count_nonzero(support)),
                    "allocation_sha256": result.node_hashes[key],
                }
            )

        key = (int(rec["interval_index"]), int(rec["node_index"]))
        if key in midpoint_keys:
            baseline = result
            # Predeclared state perturbation 1: transfer 2% HeII to HeI.
            he_state = snapshot.frame.copy()
            transfer = 0.02 * he_state.N_HeII.to_numpy(dtype=float)
            he_state["N_HeII"] -= transfer
            he_state["N_HeI"] += transfer
            he_changed = model.evaluate(forcing_row=rec, state_frame=he_state)
            base_frac = float(
                baseline.owner_table.query(
                    "group == 'G2a' and component == 'EXPLICIT_HEI_ATOMIC'"
                ).conditioned_fraction.iloc[0]
            )
            changed_frac = float(
                he_changed.owner_table.query(
                    "group == 'G2a' and component == 'EXPLICIT_HEI_ATOMIC'"
                ).conditioned_fraction.iloc[0]
            )
            passed = changed_frac > base_frac and (
                he_changed.node_hashes[("G2a", "EXPLICIT_HEI_ATOMIC")]
                != baseline.node_hashes[("G2a", "EXPLICIT_HEI_ATOMIC")]
            )
            state_sensitivity_failures += int(not passed)
            perturbation_rows.append(
                {
                    "interval_index": key[0],
                    "node_index": key[1],
                    "perturbation": "TRANSFER_2_PERCENT_HEII_TO_HEI",
                    "observable": "G2a_EXPLICIT_HEI_FRACTION",
                    "baseline": base_frac,
                    "perturbed": changed_frac,
                    "expected_direction": "increase",
                    "pass": passed,
                }
            )

            # Predeclared state perturbation 2: transfer 2% HII to HI.
            h_state = snapshot.frame.copy()
            transfer_h = 0.02 * h_state.N_HII.to_numpy(dtype=float)
            h_state["N_HII"] -= transfer_h
            h_state["N_HI"] += transfer_h
            h_changed = model.evaluate(forcing_row=rec, state_frame=h_state)
            base_h = float(
                baseline.owner_table.query(
                    "group == 'G2b' and component == 'EXPLICIT_HI_ATOMIC'"
                ).conditioned_fraction.iloc[0]
            )
            changed_h = float(
                h_changed.owner_table.query(
                    "group == 'G2b' and component == 'EXPLICIT_HI_ATOMIC'"
                ).conditioned_fraction.iloc[0]
            )
            passed_h = changed_h > base_h and (
                h_changed.node_hashes[("G2b", "EXPLICIT_HI_ATOMIC")]
                != baseline.node_hashes[("G2b", "EXPLICIT_HI_ATOMIC")]
            )
            state_sensitivity_failures += int(not passed_h)
            perturbation_rows.append(
                {
                    "interval_index": key[0],
                    "node_index": key[1],
                    "perturbation": "TRANSFER_2_PERCENT_HII_TO_HI",
                    "observable": "G2b_EXPLICIT_HI_FRACTION",
                    "baseline": base_h,
                    "perturbed": changed_h,
                    "expected_direction": "increase",
                    "pass": passed_h,
                }
            )

            # Predeclared state perturbation 3: consistent 5% thermal rescaling.
            t_state = snapshot.frame.copy()
            t_state["T_K"] *= 1.05
            t_state["U_resolved"] *= 1.05
            t_changed = model.evaluate(forcing_row=rec, state_frame=t_state)
            thermal_pass = (
                t_changed.node_hashes[("G1", "EFFECTIVE_HI_SUBGRID")]
                != baseline.node_hashes[("G1", "EFFECTIVE_HI_SUBGRID")]
            )
            state_sensitivity_failures += int(not thermal_pass)
            perturbation_rows.append(
                {
                    "interval_index": key[0],
                    "node_index": key[1],
                    "perturbation": "RESCALE_T_AND_U_BY_1P05",
                    "observable": "G1_SUBGRID_NODE_HASH_CHANGED",
                    "baseline": baseline.node_hashes[("G1", "EFFECTIVE_HI_SUBGRID")],
                    "perturbed": t_changed.node_hashes[("G1", "EFFECTIVE_HI_SUBGRID")],
                    "expected_direction": "different",
                    "pass": thermal_pass,
                }
            )

            # Fixed three-lane subgrid envelope; no lane is promoted post hoc.
            for group in ("G1", "G2a"):
                lane_measure = model.subgrid_lane_measures(
                    forcing_row=rec, state_frame=snapshot.frame, group=group
                )
                for lane_a, lane_b in itertools.combinations(lane_measure, 2):
                    a = normalized(lane_measure[lane_a])
                    b = normalized(lane_measure[lane_b])
                    tv_rows.append(
                        {
                            "interval_index": key[0],
                            "node_index": key[1],
                            "group": group,
                            "lane_a": lane_a,
                            "lane_b": lane_b,
                            "total_variation": 0.5 * float(np.abs(a - b).sum()),
                        }
                    )

        if counter % 10 == 0 or counter == len(forcing):
            print(f"processed {counter}/{len(forcing)} forcing rows", flush=True)

    owner_matrix = pd.concat(owner_frames, ignore_index=True)
    node_audit = pd.DataFrame(node_rows)
    snapshot_audit = pd.DataFrame(snapshot_rows)
    perturbation = pd.DataFrame(perturbation_rows)
    tv = pd.DataFrame(tv_rows)
    chunk_dir = output / "chunks" / f"{start_index:03d}_{stop_index:03d}"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    owner_matrix.to_csv(chunk_dir / "owner_law_time_matrix.csv", index=False)
    node_audit.to_csv(chunk_dir / "node_allocation_audit.csv", index=False)
    snapshot_audit.to_csv(chunk_dir / "snapshot_closure_audit.csv", index=False)
    perturbation.to_csv(chunk_dir / "state_sensitivity_audit.csv", index=False)
    tv.to_csv(chunk_dir / "subgrid_lane_tv_audit.csv", index=False)
    chunk_summary = {
        "start_index": start_index,
        "stop_index": stop_index,
        "forcing_rows": len(forcing),
        "owner_rows": len(owner_matrix),
        "node_allocation_cases": len(node_audit),
        "snapshot_cases": len(snapshot_audit),
        "perturbation_cases": len(perturbation),
        "subgrid_tv_cases": len(tv),
        "max_owner_kappa_sum_relative_residual": max_owner_kappa,
        "max_owner_current_sum_relative_residual": max_owner_current,
        "max_node_allocation_sum_relative_residual": max_node_current,
        "structural_zero_violations": structural_zero_violations,
        "negative_allocation_count": negative_allocation_count,
        "zero_support_nonzero_allocation_count": zero_support_nonzero_count,
        "state_sensitivity_failures": state_sensitivity_failures,
    }
    (chunk_dir / "chunk_summary.json").write_text(
        json.dumps(chunk_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(chunk_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
