#!/usr/bin/env python3
"""Run the sparse-generator representation, performance, and control-gap audit."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import statistics
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
COORDINATES = ("x_HII", "x_HeII", "x_HeIII", "log_T")
VERDICT = (
    "DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_"
    "SPARSE_LOCAL_SOURCE_AND_LOW_RANK_GLOBAL_COUPLING_PASS_"
    "STATIC_SUBSTEP_CONTROL_ESCAPED_BY_ADMISSIBLE_STAGEWISE_SCHEDULE_"
    "VALIDATED_DISCRETE_MAP_REMAINDER_NOT_CLOSED"
)
NEXT_STAGE = (
    "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-"
    "EVALUATION-SITE-SPARSE-GENERATOR-VALIDATED-MPRK22-SDIRK2-"
    "DISCRETE-MAP-ENCLOSURE-LOCK"
)


def load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def timed_samples(function, *, warmup: int = 5, samples: int = 25) -> list[float]:
    for _ in range(warmup):
        function()
    rows = []
    for _ in range(samples):
        started = time.perf_counter()
        function()
        rows.append(time.perf_counter() - started)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    stage = args.stage.resolve()
    data_dir = stage / "data"
    plot_dir = stage / "plots"
    receipt_dir = stage / "receipts"
    for directory in (data_dir, plot_dir, receipt_dir):
        directory.mkdir(parents=True, exist_ok=True)

    source_mod = load("sparse_stage_source", stage / "analysis/source_generators.py")
    global_mod = load("sparse_stage_global", stage / "analysis/global_coupling.py")
    temporal_mod = load("sparse_stage_temporal", stage / "analysis/temporal_control_audit.py")
    eval_mod = load("sparse_stage_eval_sites", stage / "analysis/evaluation_site_contract.py")
    rust_mod = load("sparse_stage_rust", stage / "analysis/rust_sparse_backend.py")
    tensor_stage = next(repo.glob("stages/*R2A_ADAPTIVE_INTERNAL_MICROSTEP*"))
    tensor_mod = load("sparse_stage_tensorized", tensor_stage / "analysis/tensorized_inputs.py")

    source = source_mod.build_source_rhs_taylor(repo)
    global_audit = global_mod.audit_global_coupling(repo)
    temporal_rows = [
        temporal_mod.run_temporal_control_audit(repo, lane=lane).to_dict()
        for lane in LANES
    ]
    evaluation_sites = eval_mod.build_evaluation_site_contract(repo)
    inputs = tensor_mod.load_tensorized_inputs(repo_root=repo)

    library = stage / "data/rust/libsparse_local_bounds.so"
    py_lo, py_hi = source.model.bounds()
    rs_lo, rs_hi = rust_mod.rust_bounds(source.model, library=library)
    rust_contains = bool(np.all(rs_lo <= py_lo) and np.all(rs_hi >= py_hi))
    max_ulp = max(
        rust_mod.maximum_ulp_distance(rs_lo, py_lo),
        rust_mod.maximum_ulp_distance(rs_hi, py_hi),
    )
    python_times = timed_samples(source.model.bounds)
    rust_times = timed_samples(lambda: rust_mod.rust_bounds(source.model, library=library))
    py_median = float(statistics.median(python_times))
    rs_median = float(statistics.median(rust_times))
    speedup = float(py_median / rs_median)

    local_blocks = np.concatenate(
        [
            np.abs(source.model.local_linear).reshape(2 * source.model.n_coordinate, source.model.n_node),
            np.abs(source.model.local_mixed),
        ],
        axis=0,
    )
    generator_norm = np.max(local_blocks, axis=0)
    np.savez_compressed(
        data_dir / "sparse_generator_profile.npz",
        temperature_K=inputs.state0.temperature_K,
        generator_norm_s_inv=generator_norm,
        table_event_distance_logT=source.table_event_distance_logT,
        v_half_width=source.v_half_width,
    )

    prior = next(repo.glob("stages/*R2_R1A_FOUR_CORNER*"))
    with np.load(prior / "data/strict_corner_envelopes.npz", allow_pickle=False) as corner:
        strict_widths = []
        token = LANES[0].lower()
        for coordinate in COORDINATES:
            strict_widths.append(
                float(
                    np.max(
                        corner[f"{token}__{coordinate}_upper"]
                        - corner[f"{token}__{coordinate}_lower"]
                    )
                )
            )
    temporal_escape = temporal_rows[0]["maximum_outside_by_coordinate"]

    # Plot 1: source-local generator scale versus temperature.
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    positive = generator_norm > 0.0
    ax.scatter(inputs.state0.temperature_K[positive], generator_norm[positive], s=3, alpha=0.35)
    ax.set_yscale("log")
    ax.set_xlabel("Initial temperature [K]")
    ax.set_ylabel("max local branch-generator magnitude [s$^{-1}$]")
    ax.set_title("Sparse local source generators")
    fig.tight_layout()
    fig.savefig(plot_dir / "local_generator_norm_vs_temperature.png", dpi=180)
    plt.close(fig)

    # Plot 2: static hull widths and the constructive temporal escape.
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    x = np.arange(len(COORDINATES))
    bars = np.vstack([strict_widths, temporal_escape])
    width = 0.38
    ax.bar(x - width / 2, bars[0], width=width, label="static four-corner width")
    ax.bar(x + width / 2, bars[1], width=width, label="stagewise escape beyond hull")
    ax.set_yscale("log")
    ax.set_xticks(x, COORDINATES)
    ax.set_ylabel("absolute endpoint width / escape")
    ax.set_title("Static corners do not enclose an admissible stagewise schedule")
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_dir / "static_corner_width_vs_stagewise_escape.png", dpi=180)
    plt.close(fig)

    # Plot 3: optional Rust bounds hot loop against the Python oracle.
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(["Python oracle", "Rust optional"], [py_median * 1e3, rs_median * 1e3])
    ax.set_ylabel("median wall time [ms]")
    ax.set_title("Outward sparse-bounds kernel (46,080 nodes)")
    fig.tight_layout()
    fig.savefig(plot_dir / "python_rust_sparse_bounds_runtime.png", dpi=180)
    plt.close(fig)

    # Plot 4: distance to source-table event surfaces.
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.hist(source.table_event_distance_logT, bins=80)
    ax.set_yscale("log")
    ax.set_xlabel("nearest Hummer-Seaton knot distance in ln T")
    ax.set_ylabel("node count")
    ax.set_title("Event-localization margin at the canonical initial state")
    fig.tight_layout()
    fig.savefig(plot_dir / "table_event_distance_histogram.png", dpi=180)
    plt.close(fig)

    result = {
        "stage": stage.name,
        "verdict": VERDICT,
        "source_safe_local_rank_lower_bound": source.rank_lower_bound,
        "robust_rank2_nodes": source.robust_rank2_nodes,
        "rank1_nodes": source.rank1_nodes,
        "node_count": source.node_count,
        "below_source_table_nodes": source.below_table_nodes,
        "minimum_table_event_distance_logT": source.minimum_table_event_distance_logT,
        "fixed_site_sparse_storage_bytes": source.model.storage_bytes,
        "global_rank_upper_bound": global_audit.global_rank_upper_bound,
        "global_to_local_rank_ratio": global_audit.global_to_local_rank_ratio,
        "owner_amplitude_jacobian_rank": global_audit.owner_amplitude_jacobian_rank,
        "owner_amplitude_jacobian_residual": global_audit.maximum_owner_jacobian_relative_residual,
        "normalization_channel_count": global_audit.normalization_channel_count,
        "evaluation_site_count": evaluation_sites.evaluation_site_count,
        "evaluation_site_input_rank_lower_bound": evaluation_sites.source_safe_input_rank_lower_bound,
        "evaluation_site_sparse_storage_mib": evaluation_sites.local_polynomial_storage_mib,
        "evaluation_site_global_rank_upper_bound": evaluation_sites.global_rank_upper_bound,
        "static_parameter_enclosure_certified": False,
        "stagewise_witness_all_hard_gates_pass": bool(
            all(row["all_trial_hard_gates_pass"] for row in temporal_rows)
        ),
        "stagewise_witness_outside_coordinate": temporal_rows[0]["outside_coordinate"],
        "stagewise_witness_outside_node_count": temporal_rows[0]["outside_node_count"],
        "stagewise_witness_max_absolute": temporal_rows[0]["maximum_outside_absolute"],
        "stagewise_witness_max_fraction_of_static_width": temporal_rows[0][
            "maximum_outside_fraction_of_static_width"
        ],
        "temporal_control_lanes": temporal_rows,
        "rust_backend_load_bearing": False,
        "rust_bounds_contain_python": rust_contains,
        "rust_python_maximum_ulp_distance": max_ulp,
        "python_bounds_median_s": py_median,
        "rust_bounds_median_s": rs_median,
        "rust_bounds_speedup": speedup,
        "production_history_authorized": False,
        "production_node_chemistry_authorized": False,
        "R2C_R2_authorized": False,
        "B2C2B_authorized": False,
        "next_stage": NEXT_STAGE,
        "next_stage_authorized": True,
        "claim_boundary": (
            "The source operator and global normalization rank are represented exactly at one evaluation site. "
            "No validated remainder encloses independent source-safe branch selections across the four MPRK22/SDIRK2 evaluation sites."
        ),
        "plots": [
            "plots/local_generator_norm_vs_temperature.png",
            "plots/static_corner_width_vs_stagewise_escape.png",
            "plots/python_rust_sparse_bounds_runtime.png",
            "plots/table_event_distance_histogram.png",
        ],
    }
    (stage / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (data_dir / "source_generator_summary.json").write_text(
        json.dumps(
            {
                "node_count": source.node_count,
                "rank_lower_bound": source.rank_lower_bound,
                "rank2_nodes": source.robust_rank2_nodes,
                "rank1_nodes": source.rank1_nodes,
                "below_table_nodes": source.below_table_nodes,
                "storage_bytes": source.model.storage_bytes,
                "minimum_table_event_distance_logT": source.minimum_table_event_distance_logT,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (data_dir / "global_coupling_summary.json").write_text(
        json.dumps(global_audit.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "evaluation_site_contract.json").write_text(
        json.dumps(evaluation_sites.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "temporal_control_lanes.json").write_text(
        json.dumps(temporal_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (receipt_dir / "RUST_PERFORMANCE_RECEIPT.json").write_text(
        json.dumps(
            {
                "python_samples_s": python_times,
                "rust_samples_s": rust_times,
                "python_median_s": py_median,
                "rust_median_s": rs_median,
                "speedup": speedup,
                "rust_contains_python": rust_contains,
                "maximum_ulp_distance": max_ulp,
                "role": "OPTIONAL_ACCELERATOR_DIFFERENTIAL_AUDITOR",
                "load_bearing": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
