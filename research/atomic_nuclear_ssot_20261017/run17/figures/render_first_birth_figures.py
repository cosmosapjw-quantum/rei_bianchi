#!/usr/bin/env python3
"""Plot only frozen RUN17 JSON values; no native call or numerical integration."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

sys.dont_write_bytecode = True


def identity(path):
    p = Path(path)
    return {"path": str(p.resolve()), "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def save_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--residual-result", required=True, type=Path)
    ap.add_argument("--control-a", required=True, type=Path)
    ap.add_argument("--control-b", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(out / "render_cache")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator, FormatStrFormatter

    source = json.loads(args.residual_result.read_text())
    controls = [json.loads(p.read_text()) for p in (args.control_a, args.control_b)]
    if source["status"] != "NUMERICALLY_CHECKED" or any(
            c["status"] != "NUMERICALLY_CHECKED" for c in controls):
        raise ValueError("completed frozen input results required")
    if identity(args.control_b)["sha256"] != source["input_control"]["sha256"]:
        raise ValueError("residual reference does not match the supplied control B")
    if any(c["interval_z"] != source["interval_z"] for c in controls):
        raise ValueError("control/residual interval mismatch")
    rows = source["uniform_samples"]
    left, right = source["interval_z"]
    if len(rows) != 17 or rows[0]["z"] != left or rows[-1]["z"] != right:
        raise ValueError("expected 17 actually evaluated samples over this first-birth interval")
    x = [(row["z"]-left)/(right-left) for row in rows]
    hi = [row["P_minus_R_HI_relative"]*1e6 for row in rows]
    temp = [row["P_minus_R_T_K"] for row in rows]
    q10 = next(q for q in source["quadrature_settings"] if q["order"] == 10)
    b_input = args.control_b.parent / "INPUT_IDENTITY.json"
    if identity(b_input)["sha256"] != controls[1]["input"]["sha256"]:
        raise ValueError("control B invariant normalization input identity mismatch")
    norm = json.loads(b_input.read_text())["q_scale"][0]
    denominator = rows[-1]["R_HI_per_initial_H"]
    # All endpoint contributions use the SAME endpoint R-HI denominator.
    # They differ from the initial sample's relative normalization.
    term_keys = ["initial_delta_q_P_minus_R", "native_gas_difference_integral_q",
                 "photo_difference_integral_q", "P_gas_residual_integral_q",
                 "minus_R_gas_residual_integral_q"]
    endpoint_terms = [{"source_field": key, "delta_qH": q10[key][0],
                       "delta_HI_per_initial_H": -norm*q10[key][0],
                       "ppm_of_endpoint_R_HI": -norm*q10[key][0]/denominator*1e6}
                      for key in term_keys]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 9.5, "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.7, "svg.fonttype": "none", "svg.hashsalt": "rei-run17-first-birth",
        "figure.facecolor": "white", "savefig.facecolor": "white"})

    outputs = []
    for layout in ("180mm", "90mm"):
        if layout == "180mm":
            fig = plt.figure(figsize=(180/25.4, 3.60))
            grid = fig.add_gridspec(1, 2, left=.095, right=.98, bottom=.26, top=.79, wspace=.40)
            fig.suptitle("RUN17  |  First-birth gas-path differences", y=.99, fontsize=11, weight="semibold")
            fig.text(.5, .908, "P: invariant checkpoint path     R: native control B",
                     ha="center", fontsize=9)
            fig.text(.5, .109, "17 evaluated samples; straight segments are visual guides.",
                     ha="center", fontsize=8.5)
            fig.text(.5, .045, "Original finite M2, all 48 cells; first birth to second birth (incoming).",
                     ha="center", fontsize=8.5)
        else:
            fig = plt.figure(figsize=(90/25.4, 5.65))
            grid = fig.add_gridspec(2, 1, left=.225, right=.97, bottom=.20, top=.81, hspace=.57)
            fig.suptitle("RUN17: first-birth interval", y=.993, fontsize=10.5, weight="semibold")
            fig.text(.5, .944, "Gas-path difference P − R", ha="center", fontsize=9)
            fig.text(.5, .909, "P: invariant checkpoint path; R: native B", ha="center", fontsize=8.5)
            fig.text(.5, .067, "17 samples; segments are visual guides.", ha="center", fontsize=8)
            fig.text(.5, .034, "All 48 cells; first-to-second birth only.", ha="center", fontsize=8)
        axes = [fig.add_subplot(grid[j]) for j in range(2)]
        colors = ["#156A86", "#AF5215"]
        for j, (axis, y) in enumerate(zip(axes, [hi, temp])):
            axis.plot(x, y, "-", color=colors[j], linewidth=1.15, alpha=.78, zorder=2)
            axis.plot(x, y, "o", color=colors[j], markersize=3.8,
                      markeredgecolor="white", markeredgewidth=.35, zorder=3)
            axis.grid(axis="y", color="#D8DDE1", linewidth=.55, zorder=0)
            axis.set_xlim(-.025, 1.025)
            axis.set_xticks([0, .25, .5, .75, 1])
            axis.set_xticklabels(["0", ".25", ".5", ".75", "1"])
            axis.set_xlabel("Interval fraction, u")
            axis.yaxis.set_major_locator(MaxNLocator(5))
            axis.tick_params(length=3, width=.7)
        axes[0].set_title("(a) Neutral hydrogen", loc="left", pad=7)
        axes[0].set_ylabel("HI difference (ppm of R)")
        axes[0].yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        axes[0].set_ylim(min(hi)-.30, max(hi)+.22)
        axes[0].text(.035, .035, f"Endpoint: {hi[-1]:+.6f} ppm",
            transform=axes[0].transAxes, fontsize=8,
            bbox={"facecolor":"white", "edgecolor":"none", "alpha":.95, "pad":1.5})
        axes[1].set_title("(b) Gas temperature", loc="left", pad=7)
        axes[1].set_ylabel("Temperature difference (K)")
        axes[1].yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        axes[1].set_ylim(min(temp)-.014, max(temp)+.013)
        axes[1].text(.035, .035, f"Endpoint: {temp[-1]:+.6f} K",
            transform=axes[1].transAxes, fontsize=8,
            bbox={"facecolor":"white", "edgecolor":"none", "alpha":.95, "pad":1.5})
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        xlabel_box = axes[-1].xaxis.label.get_window_extent(renderer)
        footer_texts = [t for t in fig.texts if t.get_position()[1] < .12]
        if any(xlabel_box.overlaps(t.get_window_extent(renderer)) for t in footer_texts):
            raise AssertionError("xlabel overlaps footer after scoped spacing repair")
        for ext in ("png", "svg"):
            path = out / f"RUN17_FIRST_BIRTH_GAS_DIFFERENCE_{layout}.{ext}"
            if path.exists():
                raise FileExistsError(path)
            metadata = {"Title": "RUN17 first-birth finite-packet gas-path differences"}
            if ext == "svg":
                metadata["Date"] = None
            fig.savefig(path, dpi=300, metadata=metadata)
            outputs.append({**identity(path), "layout": layout, "width_mm": 180 if layout=="180mm" else 90})
        plt.close(fig)

    record = {"schema":"rei.run17.figure-values.v1", "status":"RENDERED_FROM_FROZEN_VALUES",
        "input_results":[identity(args.residual_result), identity(args.control_a), identity(args.control_b)],
        "normalization_input":identity(b_input), "source_packet":source["source"]["packet"],
        "definition_P":source["definition_P"], "definition_R":"stored native control B dense polynomial",
        "interval_code_z":[left,right], "code_z_definition":"(X-0.7)/(0.7004-0.7), an integration coordinate",
        "u_definition":"(code_z-first_birth_code_z)/(second_birth_code_z-first_birth_code_z)",
        "endpoint_sides":["outgoing first birth","incoming second birth"],
        "plotted_samples":[{"code_z":r["z"],"u":u,"HI_P_minus_R_ppm_of_local_R":h,
                            "T_P_minus_R_K":t} for r,u,h,t in zip(rows,x,hi,temp)],
        "endpoint_HI_signed_balance_GL10":{
            "normalization":"all terms in ppm of endpoint R HI, including the initial term",
            "H_total_per_initial_H":norm,"endpoint_R_HI_per_initial_H":denominator,
            "HI_delta_from_qH":"-H_total*delta_qH", "terms":endpoint_terms,
            "endpoint_from_qH_ppm":-norm*q10["endpoint_delta_q_P_minus_R"][0]/denominator*1e6,
            "endpoint_plotted_direct_HI_ppm":hi[-1],
            "sum_of_terms_ppm":sum(t["ppm_of_endpoint_R_HI"] for t in endpoint_terms),
            "q_balance_closure_to_HI_ppm":-norm*q10["balance_closure_q"][0]/denominator*1e6,
            "not_plotted_as_near_zero_bars":"Tiny signed terms are retained numerically to avoid misleading visual comparisons"},
        "scope":"First-birth finite M2 gas-path diagnostic, all48cells; no full-history sub-H or continuum bound claim",
        "drawing_semantics":{"markers":"17 actual evaluated samples","segments":"straight visual guides only",
            "error_bars":False,"continuous_suprema_or_enclosures":False},
        "new_native_calls":0,"new_quadrature_calls":0,"new_IVP_solves":0,"new_tests":0,
        "outputs":outputs,"script":identity(__file__),"command_argv":sys.argv,
        "environment":{"python":sys.version,"matplotlib":matplotlib.__version__,"platform":platform.platform()},
        "cache_excluded":"render_cache contains plotting runtime cache only, not scientific payload"}
    save_json(out/"PLOTTED_VALUES_AND_PROVENANCE.json",record)
    print(json.dumps({"outputs":outputs,"HI_endpoints_ppm":[hi[0],hi[-1]],
        "T_endpoints_K":[temp[0],temp[-1]],"endpoint_HI_terms":endpoint_terms,
        "new_native_calls":0,"new_quadrature_calls":0},allow_nan=False))


if __name__ == "__main__":
    main()
