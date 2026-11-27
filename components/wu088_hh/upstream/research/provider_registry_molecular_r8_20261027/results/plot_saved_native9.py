#!/usr/bin/env python3
"""Plot retained native-nine-state arrays; no scientific runner is imported.

Run without arguments. The three input files are immutable by SHA256.
Fraction parses saved scalars before one final conversion for display.
This script does not integrate an ODE or evaluate a bound formula.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import sys
import time

WALL_START = time.monotonic()
RESULTS = Path(__file__).resolve().parent
LEAF = RESULTS.parent
RESEARCH = LEAF.parent
CASE = "saved_native_nine_state_K_conditional_feedback"
SOURCES = {
    "R8_primary": (
        LEAF / "raw/PRIMARY_RESULTS.json",
        "520110d1cae1677491aecd7216621c25f1098470c939ee027d5df3bde183686b",
    ),
    "R7_primary": (
        RESEARCH / "provider_registry_molecular_r7_20261027/raw/PRIMARY_RESULTS.json",
        "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15",
    ),
    "R7_reference": (
        RESEARCH / "provider_registry_molecular_r7_20261027/raw/REFERENCE_RESULTS.json",
        "e403c7803c080fd4f26be71a93b782b02d874f80ef11c85a706bea71e2a743cd",
    ),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exact(value):
    if isinstance(value, (bool, float)):
        raise ValueError("Parse JSON numeric literals as Decimal, never binary float")
    return Fraction(value)


def display(value):
    # Convert the complete rational, avoiding overflow in numerator/denominator.
    return float(exact(value))


def chosen(document, wanted):
    matches = [(i, item) for i, item in enumerate(document["hd_cases"]) if item["id"] == wanted]
    if len(matches) != 1:
        raise ValueError("Expected one retained case: " + wanted)
    return matches[0]


def main():
    if len(sys.argv) != 1:
        raise ValueError("This saved-data plot has no adaptive arguments")
    documents, provenance = {}, {}
    for label, (path, expected) in SOURCES.items():
        raw = path.read_bytes()
        actual = sha(raw)
        if actual != expected:
            raise ValueError("Saved input SHA256 mismatch: " + label)
        documents[label] = json.loads(raw, parse_float=Decimal)
        provenance[label] = {"path": str(path.relative_to(RESEARCH)), "sha256": actual, "bytes": len(raw)}
    i8, new = chosen(documents["R8_primary"], CASE)
    i7, old = chosen(documents["R7_primary"], CASE)
    ir, reference = chosen(documents["R7_reference"], "HD:" + CASE)
    cert = new["certificate"]
    H = exact(old["H"])
    endpoint_times = [exact(cert["delta"]) * k / H for k in range(len(cert["endpoints"]))]
    sample_times = [exact(value) / H for value in reference["times"]]
    if len(endpoint_times) != 193 or len(sample_times) != 193 or len(reference["R_E"]) != 193:
        raise ValueError("The fixed saved fixture must contain 193 clocks")
    query_times, query_caps, macro_times, macro_caps = [], [], [], []
    whole_edges, whole_values = [exact(old["blocks"][0]["t0"]) / H], []
    for block in old["blocks"]:
        start = exact(block["t0"])
        for query in block["queries"]:
            query_times.append((start + exact(query["t"])) / H)
            query_caps.append(query["bound"])
        stop = (start + exact(block["certificate"]["H"])) / H
        macro_times.append(stop)
        macro_caps.append(block["certificate"]["w_next_upper"])
        whole_edges.append(stop)
        whole_values.append(block["certificate"]["whole_block_upper"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogLocator, NullFormatter

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.titlesize": 13, "axes.labelsize": 11.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "svg.hashsalt": "WU_R8_NATIVE9_SAVED_PLOT_V1",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    })
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.4), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.28, top=0.77, wspace=0.24)
    blue, orange, green, grey = "#0072B2", "#D55E00", "#007A5E", "#7A8290"
    zero_masks = {}
    series = [
        ("R8 endpoint upper", endpoint_times, cert["endpoints"],
         {"marker": "o", "s": 12, "color": blue, "linewidths": 0, "zorder": 4}),
        ("R7 saved query upper", query_times, query_caps,
         {"marker": "s", "s": 32, "facecolors": "none", "edgecolors": orange, "linewidths": 1.0, "zorder": 5}),
        ("R7 contracted macro endpoint", macro_times, macro_caps,
         {"marker": "v", "s": 52, "color": orange, "linewidths": 0.7, "edgecolors": "white", "zorder": 6}),
        ("Saved R7 numerical samples", sample_times, reference["R_E"],
         {"marker": ".", "s": 11, "color": green, "linewidths": 0, "zorder": 3}),
    ]
    for component, ax in enumerate(axes):
        for label, times, pairs, style in series:
            values = [exact(pair[component]) for pair in pairs]
            if any(value < 0 for value in values):
                raise ValueError("A saved plotted error/bound is negative")
            visible = [j for j, value in enumerate(values) if value > 0]
            zero_masks[f"{'R' if component == 0 else 'E'}/{label}"] = {
                "saved_count": len(values), "drawn_count": len(visible),
                "masked_zero_indices": [j for j, value in enumerate(values) if value == 0],
            }
            ax.scatter([display(times[j]) for j in visible], [display(values[j]) for j in visible], label=label, **style)
        ax.stairs([display(pair[component]) for pair in whole_values], [display(t) for t in whole_edges],
                  baseline=None, color=grey, linestyle=(0, (5, 3)), linewidth=1.25,
                  label="R7 whole-block upper", zorder=2)
        ax.set_yscale("log")
        ax.set_xlim(-0.025, 3.025)
        ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
        ax.set_xlabel(r"Normalized saved clock $\tau/H$")
        ax.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(axis="y", which="major", color="#D9DEE5", linewidth=0.65)
        ax.grid(axis="x", which="major", color="#E9ECF0", linewidth=0.55)
        ax.tick_params(axis="both", labelsize=10)
        ax.set_axisbelow(True)
    axes[0].set_title(r"(a) Residual $R=\|x-\pi X\|_1$", loc="left", pad=12)
    axes[1].set_title(r"(b) Coarse scalar error $E=|\eta|$", loc="left", pad=12)
    axes[0].set_ylabel("Error or certified upper (declared density units)")
    axes[1].text(0.035, 0.055, r"$E(0)=0$ omitted on the log axis", transform=axes[1].transAxes,
                 fontsize=9, color="#505862", bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.92, "pad": 2})
    fig.suptitle("Conditional nominal native 9-state fixture", x=0.085, y=0.955, ha="left", fontsize=19, fontweight="semibold")
    fig.text(0.085, 0.895, "Three retained macroblocks | two Volterra passes | conditional method accepted", fontsize=11.5, color="#4A5562")
    fig.text(0.085, 0.845, "Markers certify or sample individual clocks; only the dashed R7 steps bound complete blocks.", fontsize=10, color="#4A5562")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.075, 0.115), ncol=3,
               frameon=False, fontsize=9.5, columnspacing=1.7, handletextpad=0.6, labelspacing=0.85)
    fig.text(0.085, 0.075, "C9 accepted conditionally; scalar repair 24/24 PASS. Original reference first FAIL preserved.", fontsize=9.2, color="#5A4553")
    fig.text(0.085, 0.038, "No physical time calibration. Saved numerical samples are corroboration, not rigorous ODE enclosures. Full coarse L1 error = 4E.", fontsize=8.9, color="#505862")
    svg_path = RESULTS / "NATIVE9_BOUNDS.svg"
    fig.savefig(svg_path, format="svg", metadata={"Date": None,
        "Title": "Conditional nominal native 9-state: retained error bounds and numerical samples",
        "Description": "R8 endpoint markers; source R7 query and contracted endpoint markers; saved numerical samples; R7 whole-block steps. C9 accepts the conditional method after 24/24 exact scalar repair checks; the original reference first FAIL is preserved. No physical consumer admission."})
    plt.close(fig)
    svg = svg_path.read_bytes()
    report = {
        "schema": "WU_R8_SAVED_NATIVE9_PLOT_PROVENANCE_V1",
        "status": "C9_ACCEPTED_SCOPED_CONDITIONAL_ORIGINAL_REFERENCE_FAIL_PRESERVED",
        "case_id": CASE,
        "script": {"path": "results/plot_saved_native9.py", "sha256": sha(Path(__file__).read_bytes())},
        "inputs": provenance,
        "outputs": {"results/NATIVE9_BOUNDS.svg": {"sha256": sha(svg), "bytes": len(svg)}},
        "source_pointers": {
            "R8_endpoints": f"/hd_cases/{i8}/certificate/endpoints",
            "R7_blocks_and_original_caps": f"/hd_cases/{i7}/blocks",
            "R7_saved_numeric_clocks": f"/hd_cases/{ir}/times",
            "R7_saved_numeric_errors": f"/hd_cases/{ir}/R_E",
        },
        "rendering": {"backend": "Matplotlib Agg to text SVG", "matplotlib_version": matplotlib.__version__,
            "endpoint_interpolation": False, "query_cap_interpolation": False, "numeric_sample_interpolation": False,
            "whole_block_steps": "Exact saved R7 whole_block_upper for each of three blocks",
            "x_axis": "tau/H dimensionless normalized saved clock; no physical seconds",
            "y_axes": ["R = l1 residual", "E = abs eta"], "full_coarse_l1": "4E",
            "rational_display_conversion": "Fraction parsed exactly, then float(Fraction); no separately converted large integers",
            "zero_masks": zero_masks},
        "scope": {"postprocessing_only": True, "new_ODE_runs": 0, "new_bound_evaluations": 0,
                  "scientific_runner_imports": 0, "scientific_core_imports": 0, "physical_consumer_admitted": False,
                  "final_adoption_claimed": True, "adoption_scope": "Conditional lag-kernel theory and code only; no physical admission",
                  "reference_status_at_authoring": "Original 726/727 PASS and 1 FAIL preserved; exact scalar re-adjudication 24/24 PASS; final C9 accepted"},
        "final_review_binding": {"source_commit": "eb437ab5ec60d3b503be115c5560a85172502aba",
            "C9": "PASS", "material_findings": 0, "targeted_scalar_checks": "24/24 PASS",
            "original_reference_status": "FAIL_PRESERVED", "scientific_DAG": {"complete": 17, "total": 32}},
        "previous_postprocessing_preserved": {
            "svg_sha256": "1813c529179757e77b8f0bbd7927d3723c1540d755e36bbafbb1d19261a8e007",
            "script_sha256": "0f6097cfa655db366c3fb93cbf5648a3b7e0c63b781a60d7238a50641cbf5c6c",
            "provenance_sha256": "8d59bf77c100fd920c0453eaa56fb74248a31981a073e4fbd26ab0a61c1607b6",
            "actual_postprocess_CPU_s_before_provenance_write": 4.317593619,
            "preservation": "Original S08/S09 Git source history; prior cost is retained separately",
            "change": "Final conditional-adoption status text and provenance only; plotted data, styling, and bounds unchanged"},
        "actual_postprocess_CPU_s_before_provenance_write": time.process_time(),
        "CPU_includes_interpreter_and_plotting_imports": True,
        "actual_postprocess_wall_s_before_provenance_write": time.monotonic() - WALL_START,
    }
    (RESULTS / "PLOT_PROVENANCE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "svg_sha256": sha(svg),
                     "postprocess_CPU_s": report["actual_postprocess_CPU_s_before_provenance_write"]}))


if __name__ == "__main__":
    main()
