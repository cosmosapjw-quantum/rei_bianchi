#!/usr/bin/env python3
"""Render frozen RUN19 coefficient timings; performs no coefficient/RHS evaluation."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
if not os.environ.get("MPLCONFIGDIR"):
    os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp(prefix="rei_run19_plot_mpl_")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def identity(path):
    b = path.read_bytes()
    return {"path": str(path), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run19-root", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    source = args.run19_root / "execution/unit_b_root/coeff_measure01"
    summary = json.loads((source / "SUMMARY.json").read_text())
    raw = list(csv.DictReader((source / "stdout.csv").open()))
    rows = [r for r in summary["rows"] if r["workers"] == 1]
    assert len(rows) == 9
    for row in rows:
        values = [float(x["ns_per_query"]) for x in raw
                  if x["pattern"] == row["pattern"] and x["backend"] == row["backend"] and int(x["workers"]) == 1]
        assert len(values) == 5
        assert (min(values), statistics.median(values), max(values)) == (row["min_ns"], row["median_ns"], row["max_ns"])
    args.output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
        "svg.fonttype": "none", "pdf.fonttype": 42, "axes.spines.top": False,
        "axes.spines.right": False, "axes.spines.left": False})
    fig, ax = plt.subplots(figsize=(10.6, 6.3))
    fig.subplots_adjust(left=0.18, right=0.96, top=0.78, bottom=0.29)
    colors = {"direct": "#52616D", "loglinear": "#A95A12", "cubic": "#237B57"}
    labels = {"direct": "Direct", "loglinear": "Loglinear 65,537", "cubic": "Cubic 32,769"}
    patterns = ["ordered_logT", "random_logT", "local_10000K"]
    ys = np.arange(3, dtype=float) * 1.2
    for j, backend in enumerate(["direct", "loglinear", "cubic"]):
        data = [next(r for r in rows if r["backend"] == backend and r["pattern"] == pat) for pat in patterns]
        med = np.array([r["median_ns"] for r in data]);low=np.array([r["min_ns"] for r in data]);high=np.array([r["max_ns"] for r in data])
        y = ys + (j-1)*0.28
        ax.barh(y, med, height=0.22, color=colors[backend], label=labels[backend], zorder=2)
        ax.errorbar(med, y, xerr=[med-low,high-med], fmt="none", ecolor="#20272D", elinewidth=1.1, capsize=3, zorder=3)
        for xx, yy in zip(med,y):
            ax.text(xx-9, yy, f"{xx:.1f}", ha="right", va="center", fontsize=9.5, color="white", fontweight="bold", zorder=4)
    ax.set_yticks(ys, ["Ordered log T", "Random log T", "Local near 10,000 K"])
    ax.invert_yaxis()
    ax.set_xlim(0,760)
    ax.set_xlabel("Nanoseconds per 15-coefficient query (lower is faster)", labelpad=10)
    ax.grid(axis="x", color="#DDE2E5", linewidth=0.7, zorder=0)
    ax.tick_params(axis="y", length=0, pad=10)
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0,1.07), frameon=False,
              handlelength=1.5, columnspacing=1.8, borderaxespad=0)
    fig.text(0.04,0.955,"RUN19 coefficient lookup — one worker",fontsize=18,fontweight="bold",ha="left")
    fig.text(0.04,0.907,"N = 32,768 · five repeats · matched inputs and worker count · target-cpu=native",fontsize=11,color="#45515A")
    fig.text(0.18,0.04,
        "Bars: median. Whiskers: observed min–max, not confidence intervals.\n"
        "Coefficient-query timing only; native gas RHS and trajectory timings are separate.\n"
        "Fixed loop order on a shared host. Table construction is excluded.",
        fontsize=9.5,color="#45515A",linespacing=1.4,va="bottom")
    outputs=[]
    for suffix in ("svg","pdf","png"):
        path=args.output/("COEFFICIENT_QUERY_ONE_WORKER."+suffix)
        metadata={"Date":None} if suffix=="svg" else {"CreationDate":None,"ModDate":None} if suffix=="pdf" else None
        fig.savefig(path,dpi=180,metadata=metadata)
        outputs.append(identity(path))
    plt.close(fig)
    record={"schema":"REI_RUN19_COEFFICIENT_FIGURE_V1","argv":[sys.executable,*sys.argv],
        "inputs":[identity(source/"SUMMARY.json"),identity(source/"stdout.csv"),identity(source/"COMMAND.json")],
        "script":identity(Path(__file__)),"plotted_rows":rows,"raw_repeat_reduction_matches":True,
        "units":"ns per 15-coefficient query","outputs":outputs,"native_rhs_calls":0,"ivps":0}
    with (args.output/"PLOT_DATA_AND_IDENTITY.json").open("x") as f:json.dump(record,f,indent=2);f.write("\n")
    print(json.dumps({"outputs":outputs,"native_rhs_calls":0,"ivps":0},indent=2))


if __name__ == "__main__":
    main()
