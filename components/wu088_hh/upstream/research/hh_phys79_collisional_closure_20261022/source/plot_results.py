"""Two source-bound figures of saved PHYS78 CI-domain and local-rate diagnostics."""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/hh_phys79_matplotlib")

import argparse
import datetime as dt
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

UNIT = Path(__file__).resolve().parents[1]
KB_EV_K = 1.380649e-23 / 1.602176634e-19
COLORS = ("#0072B2", "#D55E00", "#009E73")
CASES = ("P013", "P030")
LABELS = {"P013": "P013 · UV source scale 1", "P030": "P030 · UV source scale 2"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_analysis(directory):
    directory = Path(directory)
    summary_bytes = (directory/"SUMMARY.json").read_bytes()
    summary = json.loads(summary_bytes)
    if summary["status"] != "COMPLETED_SCOPED_SAVED_OPERATOR_DIAGNOSTIC":
        raise ValueError("ANALYSIS_NOT_COMPLETED")
    data, hashes = {}, {"SUMMARY.json": digest(summary_bytes)}
    for case in CASES:
        path = directory/(case+".npz"); raw = path.read_bytes()
        if digest(raw) != summary["outputs"][path.name]["sha256"]:
            raise ValueError("ANALYSIS_PAYLOAD_HASH_MISMATCH:"+case)
        with np.load(io.BytesIO(raw), allow_pickle=False) as f:
            data[case] = {k: np.array(f[k], copy=True) for k in f.files}
        hashes[path.name] = digest(raw)
    return data, summary, hashes


def redshift_axis(ax, data):
    """Map labelled redshifts to this case's stored proper-time clock."""
    redshifts = np.array([20., 10., 6., 4., 2.])
    times = np.interp(redshifts, data["z"][::-1], data["elapsed_Myr"][::-1])
    top = ax.twiny()
    top.set_xlim(ax.get_xlim())
    top.set_xticks(times, [f"{z:g}" for z in redshifts])
    top.set_xlabel("Mean redshift z", labelpad=7)
    top.tick_params(axis="x", labelsize=9)
    top.spines["bottom"].set_visible(False)
    return top


def excluded_saved_bins(ax, data):
    x = data["elapsed_Myr"]; valid = data["neutral_CI_valid"]
    edges = np.r_[x[0], .5*(x[1:]+x[:-1]), x[-1]]
    invalid = ~valid
    starts = np.flatnonzero(invalid & np.r_[True, ~invalid[:-1]])
    ends = np.flatnonzero(invalid & np.r_[~invalid[1:], True])
    for j, (a, b) in enumerate(zip(starts, ends)):
        ax.axvspan(edges[a], edges[b+1], color="#c8cdd2", alpha=.48,
                   zorder=0, label="Excluded saved-epoch bins" if j == 0 else None)


def style_axis(ax, data, ylabel):
    ax.set_xlim(0, data["elapsed_Myr"][-1])
    ax.set_xlabel("Elapsed proper time since z = 20 [Myr]")
    ax.set_ylabel(ylabel)
    ax.set_yscale("log")
    ax.grid(True, which="major", alpha=.23, linewidth=.6)
    ax.grid(True, which="minor", axis="y", alpha=.10, linewidth=.4)
    ax.tick_params(labelsize=9)


def save_figure(fig, output, stem):
    fig.savefig(output/(stem+".png"), dpi=180, facecolor="white")
    fig.savefig(output/(stem+".pdf"), facecolor="white",
                metadata={"Creator": "PHYS79 source-bound saved-state diagnostics",
                          "CreationDate": None, "ModDate": None})
    plt.close(fig)


def temperature_domains(data, output):
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.6))
    for ax, case in zip(axes, CASES):
        d = data[case]; x = d["elapsed_Myr"]
        style_axis(ax, d, "Gas temperature [K]")
        ax.set_ylim(200., 8e4)
        ax.axhspan(200, 1/KB_EV_K, color="#c8cdd2", alpha=.48)
        ax.plot(x, d["T_K"], color="#28374d", linewidth=2.1,
                label="Stored PI + RR trajectory", zorder=3)
        for ev, text, color, ls in (
            (1., "1 eV · H I / He I / Li I", "#0072B2", "--"),
            (3., "3 eV · He II", "#D55E00", ":"),
            (4., "4 eV · Li II", "#009E73", "-."),
            (5., "5 eV · Li III", "#7b61a8", ":"),
        ):
            threshold = ev/KB_EV_K
            ax.axhline(threshold, color=color, linestyle=ls, linewidth=1.1)
            ax.annotate(text, (x[-1]*.97, threshold), xytext=(0, 3),
                        textcoords="offset points", ha="right", va="bottom",
                        fontsize=8.4, color=color,
                        bbox={"facecolor":"white", "edgecolor":"none", "alpha":.85, "pad":1.5})
        ax.text(.04, .17, "Below 1 eV: no CI fit evaluation", transform=ax.transAxes,
                fontsize=9, color="#4b5158")
        ax.text(.04, .89, LABELS[case], transform=ax.transAxes,
                fontsize=10.3, fontweight="bold")
        imax = int(np.argmax(d["T_K"]))
        ax.plot(x[imax], d["T_K"][imax], "o", color="#28374d", ms=4)
        ax.annotate(f"max {d['T_K'][imax]:,.0f} K", (x[imax], d["T_K"][imax]),
                    xytext=(0,-24), textcoords="offset points", ha="center",
                    fontsize=9, color="#28374d")
        redshift_axis(ax, d)
    fig.suptitle("Stored PHYS78 temperatures and author CI fit domains", y=.99,
                 fontsize=14, fontweight="bold")
    fig.text(.5, .012,
             "Thresholds are source applicability limits, not physical zero-rate temperatures. "
             "He II / Li II / Li III are outside their fit domains at every saved epoch.",
             ha="center", fontsize=9)
    fig.subplots_adjust(left=.075, right=.98, bottom=.15, top=.80, wspace=.22)
    save_figure(fig, output, "01_temperature_and_fit_domains")


def instantaneous_comparison(data, output):
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.7))
    for row, case in enumerate(CASES):
        d = data[case]; x = d["elapsed_Myr"]
        a, b = axes[row]
        style_axis(a, d, "CI / PI event-rate ratio")
        style_axis(b, d, "CI threshold cooling / reference energy rate")
        for ax in (a,b):
            excluded_saved_bins(ax, d)
            ax.axhline(1., color="#555555", linewidth=.9, linestyle="--", zorder=1)
            ax.text(.965, .94, LABELS[case], transform=ax.transAxes,
                    ha="right", va="top", fontsize=10, fontweight="bold")
            redshift_axis(ax, d)
        for color, element_row, name in zip(COLORS, (0,1,3), ("H I", "He I", "Li I")):
            a.plot(x, d["CI_over_PI"][:, element_row], color=color, linewidth=1.8,
                   label=name)
        b.plot(x, d["CI_cooling_over_PI_heat"], color=COLORS[0], linewidth=1.8,
               label="/ old PI excess heating")
        b.plot(x, d["CI_cooling_over_RR_kinetic"], color=COLORS[1], linewidth=1.8,
               label="/ old RR kinetic cooling")
        a.legend(loc="lower right", framealpha=.94, fontsize=9)
        b.legend(loc="lower right", framealpha=.94, fontsize=9)
    fig.suptitle("Local collision strength on unchanged stored states", y=.995,
                 fontsize=14, fontweight="bold")
    fig.text(.5, .012,
             "Only source-admitted neutral CI is evaluated; gaps are excluded values, never zero rates. "
             "Ratios diagnose the local operator, not a corrected trajectory or causal effect.",
             ha="center", fontsize=8.8)
    fig.subplots_adjust(left=.078, right=.98, bottom=.09, top=.89, hspace=.56, wspace=.26)
    save_figure(fig, output, "02_instantaneous_CI_PI_RR_comparison")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=UNIT/"analysis"/"saved_operator")
    parser.add_argument("--output", type=Path, default=UNIT/"figures")
    args = parser.parse_args(argv)
    stems = ("01_temperature_and_fit_domains", "02_instantaneous_CI_PI_RR_comparison")
    paths = [args.output/(s+ext) for s in stems for ext in (".png", ".pdf")]
    if any(p.exists() for p in paths) or (args.output/"FIGURE_MANIFEST.json").exists():
        raise FileExistsError("CREATE_ONLY_FIGURE_OUTPUT_ALREADY_EXISTS")
    args.output.mkdir(parents=True, exist_ok=True)
    data, summary, hashes = load_analysis(args.input)
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10,
                         "axes.spines.right":False, "axes.titlepad":12,
                         "pdf.fonttype":42, "ps.fonttype":42})
    temperature_domains(data, args.output)
    instantaneous_comparison(data, args.output)
    manifest = {"scope": summary["scope"], "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "plot_source_sha256": digest(Path(__file__).read_bytes()),
                "analysis_inputs_sha256": hashes,
                "redshift_clock": "each case's own saved elapsed_seconds; ticks interpolated for display only",
                "zero_policy": "unsupported CI NaN and explicit mask; no floor or gap filling",
                "new_ODE":0, "plot_data_rows":322,
                "files":{p.name:{"bytes":p.stat().st_size,"sha256":digest(p.read_bytes())} for p in paths},
                "visual_inspection":"PENDING"}
    (args.output/"FIGURE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"status":"RENDERED", "figure_families":2,
                      "formats":["png","pdf"], "new_ODE":0}))


if __name__ == "__main__":
    main()
