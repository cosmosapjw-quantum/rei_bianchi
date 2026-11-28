#!/usr/bin/env python3
"""Plot stored PHYS70 measurements only; never launch an integration."""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / "research/hh_phys70_20261020"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.png, args.svg):
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    review = json.loads((UNIT / "verification/PERFORMANCE_REVIEW.json").read_text())
    parallel = json.loads((UNIT / "benchmark/parallel_trajectories/SUMMARY.json").read_text())
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "figure.facecolor": "#ffffff"})
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.3), constrained_layout=True)
    fig.suptitle("PHYS70 | Faster HH integration from its exact block structure\n"
                 "L28, m=0, T=65, 96 angular nodes; one sandbox host; HH_R10=OFF", fontsize=16)
    engines = ["legacy_gmres", "block_scalar", "block_simd"]
    labels = ["Original GMRES", "Block scalar", "Block + SIMD"]
    colors = ["#6d7383", "#2495a1", "#cf562d"]
    ax = axes[0, 0]
    for j, (engine, label, color) in enumerate(zip(engines, labels, colors)):
        for i, group in enumerate(review["groups"]):
            x = i + (j - 1) * .22
            y = group["solver_setup_and_solve_median_seconds"][engine]
            ax.bar(x, y, width=.19, color=color, label=label if i == 0 else None)
            samples = [r["solver_setup_and_solve_elapsed_seconds"] for r in review["rows"]
                       if r["engine"] == engine and r["rtol"] == group["rtol"]]
            ax.scatter([x - .03, x, x + .03], samples, color="black", s=12, zorder=3)
            ax.annotate(f"{y:.4g} s", (x, max(samples)), xytext=(0, 6),
                        textcoords="offset points", ha="center", fontsize=9)
    ax.set_yscale("log"); ax.set_ylim(.016, 20)
    ax.set_xticks([0, 1], ["rtol = 3e-10", "rtol = 3e-12"])
    ax.set_ylabel("Model setup + solve time (s)")
    ax.set_title("A  Same requests and accepted step counts; 3 samples")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", alpha=.2)
    ax = axes[0, 1]
    for engine, label, color in zip(engines, labels, colors):
        xs = [g["solver_setup_and_solve_median_seconds"][engine] for g in review["groups"]]
        ys = [g["relative_D2_point_error_upper_by_engine"][engine] for g in review["groups"]]
        ax.loglog(xs, ys, "o-", label=label, color=color, linewidth=2)
    for y, label in [(3e-10, "looser comparison goal"), (3e-12, "tighter comparison goal")]:
        ax.axhline(y, color="#87909e", ls=":", lw=1)
        ax.text(.013, y * 1.2, label, fontsize=8, color="#56606e")
    ax.set_xlim(.012, 14); ax.set_ylim(6e-13, 8e-10)
    ax.set_xlabel("Model setup + solve time (s)")
    ax.set_ylabel("Certified relative error of stored D2 point")
    ax.set_title("B  Work versus achieved point accuracy")
    ax.grid(alpha=.18); ax.legend(fontsize=8)
    ax = axes[1, 0]
    memory = review["micro"]["memory"]
    values = [memory["legacy_driver_retained_bytes"], memory["structured_driver_and_frozen_retained_bytes"],
              memory["structured_kernel_tables_and_rows_retained_bytes"]]
    bars = ax.bar([0, 1, 2], np.array(values) / 1000, color=[colors[0], colors[2], "#e5b492"], width=.6)
    ax.bar_label(bars, labels=[f"{x / 1000:.3f} KB" for x in values], padding=4)
    ax.set_xticks([0, 1, 2], ["Old driver", "New driver\n+ frozen Jacobian", "New kernel tables\n(separate)"])
    ax.set_ylim(0, 300); ax.set_ylabel("Retained vector capacity (decimal KB)")
    ax.set_title("C  Driver storage falls 88.05%; RSS not measured")
    ax.text(.43, .83, "New driver + tables: 83.368 KB\nOld model/table storage is\noutside the driver report.",
            transform=ax.transAxes, fontsize=9)
    ax.grid(axis="y", alpha=.18)
    ax = axes[1, 1]
    threads = [r["threads"] for r in parallel["rows"]]
    ax.plot(threads, [r["speedup_vs_threads_1"] for r in parallel["rows"]], "o-", color=colors[2],
            label="4 full trajectories (1 batch per setting)")
    micro = review["micro"]["parallel_frozen_callbacks"]
    ax.plot(threads, [micro["speedup_over_one_worker"][str(t)] for t in threads], "s-", color=colors[1],
            label="8 frozen RHS jobs (median of 5)")
    ax.plot(threads, threads, ":", color="#89919d", label="Ideal linear scaling")
    ax.set_xticks(threads); ax.set_xlabel("Rayon worker threads"); ax.set_ylabel("Speedup over one worker")
    ax.set_title("D  Independent jobs; radial carry stays sequential")
    ax.set_ylim(.8, 4.2); ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=.18)
    fig.savefig(args.svg, metadata={"Date": "2026-10-20"})
    fig.savefig(args.png, dpi=170)
    print(json.dumps({"status": "PLOTTED_STORED_DATA_ONLY", "svg": str(args.svg),
                      "png": str(args.png), "new_integrations": 0}))


if __name__ == "__main__":
    main()
