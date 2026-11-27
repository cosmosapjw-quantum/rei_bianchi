#!/usr/bin/env python3
"""Render R13 figures and a summary from saved primary/reference results only.

This script imports no production, predecessor, ODE or scientific runner module.
Displayed curves evaluate already-saved exact polynomial coefficients as floats.
No solver or convolution is rerun. Endpoint connectors are visual guides; closed
cell bounds are shown separately. Root performs PNG/SVG and visual verification.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time


BLUE = "#2463a7"
GREEN = "#15775e"
ORANGE = "#c56b20"
PURPLE = "#7f4b9e"
GRAY = "#5f6872"


def frac(value):
    return Fraction(value)


def decimal_text(value, precision=40):
    value = frac(value)
    with localcontext() as context:
        context.prec = precision
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def safe_ratio(numerator, denominator):
    numerator, denominator = frac(numerator), frac(denominator)
    if denominator == 0:
        return None
    ratio = numerator / denominator
    return {"exact": str(ratio), "decimal": decimal_text(ratio)}


def interval_ratio(numerator, denominator):
    n0, n1 = map(frac, numerator)
    d0, d1 = map(frac, denominator)
    if d0 <= 0:
        return {"lower": None, "upper": None, "reason": "Denominator interval contains zero; ratio is undefined here."}
    return {
        "lower": str(n0 / d1), "upper": str(n1 / d0),
        "reason": "Ratio of nonnegative saved endpoint enclosures.",
    }


def digest(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def style_axis(ax, ylabel, title):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Normalized time")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.2, linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def source_plot(ax, record):
    source = record["input"]
    knots = list(map(float, map(frac, source["source_knots"])))
    for i, pair in enumerate(source["g_r"]):
        ax.plot(knots[i:i + 2], list(map(float, map(frac, pair))),
                color=GRAY, linewidth=2.6, marker="o",
                label="Declared affine forcing bound" if i == 0 else None)
    style_axis(ax, r"$g_r$  [residual / normalized time]",
               "(a) Triangular source: q = 0, tau = 1")
    ax.set_ylim(bottom=-0.04)
    ax.legend(loc="upper right", fontsize=9, frameon=False)


def polynomial_r_plot(ax, record, label="Stored exact R polynomial"):
    result = record["result"]
    for index, cell in enumerate(result["exact"]["R_quadratic_cells"]):
        left, right = frac(cell["left"]), frac(cell["right"])
        p0, p1, p2 = map(float, map(frac, cell["coefficients_local"]))
        span = float(right - left)
        local = [span * i / 100 for i in range(101)]
        values = [p0 + p1 * u + p2 * u * u for u in local]
        ax.plot([float(left) + u for u in local], values, color=GREEN,
                linewidth=2.5, label=label if index == 0 else None, zorder=3)


def whole_steps(ax, record, component, label):
    result = record["result"]
    times = list(map(float, map(frac, result["requested_times"])))
    whole = result["raw"]["whole_cells_upper"]
    for i, row in enumerate(whole):
        value = float(frac(row[component]))
        ax.hlines(value, times[i], times[i + 1], color=ORANGE, linewidth=3,
                  alpha=0.85, label=label if i == 0 else None, zorder=2)
        ax.vlines([times[i], times[i + 1]], value - 0.008, value + 0.008,
                  color=ORANGE, alpha=0.8, linewidth=1.2, zorder=2)


def vertex_figure(plt, cases):
    triangle = cases["triangle_q0"]
    jump = cases["initial_jump_unattained"]
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 10.5), constrained_layout=True)
    fig.suptitle("R13: affine forcing, interior extrema and one-sided limits",
                 fontsize=18, fontweight="bold")
    source_plot(axes[0, 0], triangle)

    ax = axes[0, 1]
    polynomial_r_plot(ax, triangle)
    whole_steps(ax, triangle, 0, "Closed-cell R upper (supremum)")
    result = triangle["result"]
    requested = list(map(frac, result["requested_times"]))
    refined = list(map(frac, result["refined_times"]))
    exact_r = list(map(frac, result["exact"]["R_at_refined"]))
    lookup = dict(zip(refined, exact_r))
    ax.scatter(list(map(float, requested)), [float(lookup[t]) for t in requested],
               s=45, color=BLUE, label="Requested endpoint values", zorder=5)
    vertices = list(map(frac, result["vertex_times"]))
    if vertices:
        ax.scatter(list(map(float, vertices)), [float(lookup[t]) for t in vertices],
                   s=85, marker="D", color=PURPLE, label="Exact inserted vertex", zorder=6)
    if Fraction(3, 2) in lookup:
        value = lookup[Fraction(3, 2)]
        ax.annotate(f"t = 3/2, R = {value}", xy=(1.5, float(value)),
                    xytext=(0.82, 0.94), fontsize=10,
                    arrowprops={"arrowstyle": "->", "color": PURPLE},
                    color=PURPLE)
    style_axis(ax, "R comparison", "(b) A vertex exceeds both cell endpoints")
    ax.set_ylim(-0.04, 1.1)
    ax.legend(loc="lower right", fontsize=9, frameon=False)

    ax = axes[1, 0]
    raw = result["raw"]
    times = list(map(float, requested))
    upper_e = [float(frac(row[1])) for row in raw["endpoints_upper"]]
    lower_e = [float(frac(row[1])) for row in raw["endpoints_lower"]]
    ax.plot(times, upper_e, "--", color=BLUE, linewidth=1.6,
            label="Endpoint connector: visual guide only", zorder=3)
    ax.errorbar(times, upper_e,
                yerr=[[max(0.0, hi - lo) for lo, hi in zip(lower_e, upper_e)],
                      [0.0] * len(times)], fmt="o", color=BLUE, capsize=4,
                label="Endpoint enclosures (width not resolved)", zorder=5)
    whole_steps(ax, triangle, 1, "Certified closed-cell E upper")
    style_axis(ax, "E comparison", "(c) Endpoint values and whole-cell bounds")
    ax.set_ylim(bottom=-0.04)
    ax.legend(loc="upper left", fontsize=9, frameon=False)

    ax = axes[1, 1]
    polynomial_r_plot(ax, jump, "Stored polynomial on 0 <= t < 1")
    whole_steps(ax, jump, 0, "Closed-cell R supremum")
    jr = jump["result"]
    final_time = float(frac(jr["requested_times"][-1]))
    final_value = float(frac(jr["exact"]["R_at_refined"][-1]))
    left_limit = float(frac(jr["exact"]["R_quadratic_cells"][-1]["bernstein"][-1]))
    ax.scatter([final_time], [left_limit], facecolors="white", edgecolors=GREEN,
               s=105, linewidths=2.4, zorder=7, label="Excluded left-limit point")
    ax.scatter([final_time], [final_value], color=BLUE, s=65, zorder=7,
               label="Actual value at t = 1")
    left_limit_text = jr["exact"]["R_quadratic_cells"][-1]["bernstein"][-1]
    actual_text = jr["exact"]["R_at_refined"][-1]
    ax.annotate(f"sup R = {left_limit_text}; not attained", xy=(0.72, left_limit),
                xytext=(0.18, 2.19), fontsize=10, color=ORANGE,
                arrowprops={"arrowstyle": "->", "color": ORANGE})
    ax.annotate(f"R(1) = {actual_text}", xy=(final_time, final_value),
                xytext=(0.55, 1.16), fontsize=10, color=BLUE,
                arrowprops={"arrowstyle": "->", "color": BLUE})
    style_axis(ax, "R comparison", "(d) Downward jump and an unattained supremum")
    ax.set_xlim(-0.04, 1.1)
    ax.set_ylim(0.85, 2.42)
    ax.text(0.03, 0.96, "Solid: t < 1; open marker: left limit",
            transform=ax.transAxes, fontsize=9, va="top", color=GRAY)
    fig.supxlabel(
        "SYNTHETIC ARITHMETIC CONTROLS  |  Curves evaluate saved coefficients; "
        "dashed endpoint connectors do not certify interiors.",
        fontsize=10)
    return fig


def endpoint_comparison_figure(plt, cases, widths):
    fig = plt.figure(figsize=(14.5, 13.7), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 3.0])
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])]
    ids = ["ramp_q1", "ramp_supremum_constant"]
    labels = ["Affine bound: g(t) = t", "Cell supremum: g = 1"]
    colors = [GREEN, GRAY]
    for component, ax in enumerate(axes):
        upper, lower = [], []
        for cid in ids:
            raw = cases[cid]["result"]["raw"]
            lower.append(frac(raw["endpoints_lower"][-1][component]))
            upper.append(frac(raw["endpoints_upper"][-1][component]))
        ax.bar([0, 1], list(map(float, upper)), color=colors, width=0.55, alpha=0.9)
        ax.errorbar([0, 1], list(map(float, upper)),
                    yerr=[[max(0.0, float(hi - lo)) for lo, hi in zip(lower, upper)], [0.0, 0.0]],
                    fmt="none", ecolor="black", capsize=5)
        ax.set_xticks([0, 1], labels, fontsize=10)
        ax.set_ylabel(("R" if component == 0 else "E") + " at t = 1")
        ax.set_title("(a) Residual endpoint" if component == 0 else "(b) Scalar endpoint",
                     loc="left", fontsize=13, fontweight="bold")
        ax.set_ylim(0, float(max(upper)) * 1.35)
        key = "R" if component == 0 else "E"
        expected = [cases[cid]["input"]["controls"]["endpoint"][key] for cid in ids]
        for i, value in enumerate(upper):
            ax.text(i, float(value) + float(max(upper)) * 0.06, expected[i],
                    ha="center", fontsize=13, fontweight="bold")
        ratio_exact = frac(expected[0]) / frac(expected[1])
        reduction = 100 * (1 - ratio_exact)
        ratio = str(ratio_exact) + " (" + format(float(reduction), ".6g") + "% reduction)"
        ax.text(0.5, 0.95, "Ideal affine / constant = " + ratio,
                transform=ax.transAxes, ha="center", va="top", fontsize=10)
        ax.grid(axis="y", alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax = fig.add_subplot(grid[1, :])
    positive = [frac(row["max_refined_endpoint_E_width"]) for row in widths
                if frac(row["max_refined_endpoint_E_width"]) > 0]
    display_floor = min(map(float, positive)) / 10 if positive else 1e-40
    plot_values = [float(frac(row["max_refined_endpoint_E_width"]))
                   if frac(row["max_refined_endpoint_E_width"]) > 0 else display_floor
                   for row in widths]
    positions = list(range(len(widths)))
    ax.barh(positions, plot_values, color=BLUE, alpha=0.82, height=0.67)
    ax.set_yticks(positions, [row["id"] for row in widths], fontsize=9)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(display_floor / 2, max(plot_values) * 12)
    for i, row in enumerate(widths):
        if frac(row["max_refined_endpoint_E_width"]) == 0:
            ax.scatter([display_floor], [i], marker="x", s=35, color="black", zorder=4)
            ax.annotate("exactly 0", (display_floor, i), xytext=(7, 0),
                        textcoords="offset points", va="center", fontsize=8)
    ax.set_xlabel("Largest saved E endpoint enclosure width in each case (log scale)")
    ax.set_title(f"(c) Outward enclosure widths across {len(widths)} saved cases",
                 loc="left", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", which="both", alpha=0.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.suptitle("R13: affine bounds versus cell suprema",
                 fontsize=18, fontweight="bold")
    fig.supxlabel(
        "SYNTHETIC ARITHMETIC CONTROLS  |  Bars show saved outward upper endpoints; "
        "analytic control values are annotated.\n"
        "This comparison does not assign a physical HD closure. "
        "Zero widths are marked explicitly; undefined 0/0 ratios remain null.",
        fontsize=10)
    return fig


def summarize(primary, reference):
    cases = {row["id"]: row for row in primary["cases"]}
    widths = []
    for row in primary["cases"]:
        result, cid = row["result"], row["id"]
        raw = result["raw"]
        refined_widths = [frac(hi[1]) - frac(lo[1]) for lo, hi in
                          zip(raw["refined_endpoints_lower"], raw["refined_endpoints_upper"])]
        requested_widths = [frac(hi[1]) - frac(lo[1]) for lo, hi in
                            zip(raw["endpoints_lower"], raw["endpoints_upper"])]
        if min(refined_widths + requested_widths) < 0:
            raise ValueError("Saved enclosure has a negative width: " + cid)
        terminal = [raw["endpoints_lower"][-1][1], raw["endpoints_upper"][-1][1]]
        terminal_width = frac(terminal[1]) - frac(terminal[0])
        terminal_scale = max(abs(frac(terminal[0])), abs(frac(terminal[1])))
        widths.append({
            "id": cid,
            "max_refined_endpoint_E_width": str(max(refined_widths)),
            "max_refined_endpoint_E_width_decimal": decimal_text(max(refined_widths)),
            "max_requested_endpoint_E_width": str(max(requested_widths)),
            "terminal_E_interval": terminal,
            "terminal_E_width": str(terminal_width),
            "terminal_E_relative_width": safe_ratio(terminal_width, terminal_scale),
            "refined_cells": len(result["refined_times"]) - 1,
        })
    affine = cases["ramp_q1"]
    constant = cases["ramp_supremum_constant"]
    comparison = {}
    for component, key in enumerate(("R", "E")):
        a = [affine["result"]["raw"]["endpoints_lower"][-1][component],
             affine["result"]["raw"]["endpoints_upper"][-1][component]]
        b = [constant["result"]["raw"]["endpoints_lower"][-1][component],
             constant["result"]["raw"]["endpoints_upper"][-1][component]]
        ideal_a = frac(affine["input"]["controls"]["endpoint"][key])
        ideal_b = frac(constant["input"]["controls"]["endpoint"][key])
        comparison[key] = {
            "affine_saved_endpoint_interval": a,
            "constant_saved_endpoint_interval": b,
            "saved_ratio_enclosure": interval_ratio(a, b),
            "predeclared_analytic_values": [str(ideal_a), str(ideal_b)],
            "analytic_values_contained_in_saved_intervals":
                frac(a[0]) <= ideal_a <= frac(a[1]) and frac(b[0]) <= ideal_b <= frac(b[1]),
            "ideal_affine_over_constant": safe_ratio(ideal_a, ideal_b),
            "ideal_reduction_percent": safe_ratio(100 * (ideal_b - ideal_a), ideal_b),
            "scope": "Same q/tau/initial/c/d, declared synthetic affine bounds versus their cell suprema.",
        }
    triangle = cases["triangle_q0"]["result"]
    jump = cases["initial_jump_unattained"]["result"]
    lookup = dict(zip(map(frac, triangle["refined_times"]),
                      map(frac, triangle["exact"]["R_at_refined"])))
    summary = {
        "schema": "WU_R13_SAVED_OUTPUT_SUMMARY_V1",
        "source_scope": "Saved primary/reference outputs only; no solver, convolution, ODE or CAS call.",
        "primary_status": primary["status"],
        "reference_status": reference["status"],
        "case_count": len(cases),
        "per_case_widths": widths,
        "maximum_refined_endpoint_E_width": str(max(frac(row["max_refined_endpoint_E_width"]) for row in widths)),
        "ramp_control_comparison": comparison,
        "triangle_control": {
            "saved_vertex_times": triangle["vertex_times"],
            "R_at_3_over_2": str(lookup[Fraction(3, 2)]),
            "saved_observation_whole_R": [row[0] for row in triangle["raw"]["whole_cells_upper"]],
            "saved_endpoint_E_interval": [triangle["raw"]["endpoints_lower"][-1][1],
                                          triangle["raw"]["endpoints_upper"][-1][1]],
            "saved_last_observation_whole_E_upper": triangle["raw"]["whole_cells_upper"][-1][1],
            "interpretation": "Attained interior maximum at t=3/2; finite endpoint connectors alone do not certify this maximum.",
        },
        "unattained_supremum_control": {
            "actual_right_R": jump["exact"]["R_at_refined"][-1],
            "right_left_limit_R": jump["exact"]["R_quadratic_cells"][-1]["bernstein"][-1],
            "closed_cell_R_upper": jump["raw"]["whole_cells_upper"][-1][0],
            "interpretation": "Left-limit supremum at t=1 is not attained by the actual right-continuous R function.",
        },
        "plot_conventions": {
            "solid_R_curves": "Floating display evaluation of saved exact local quadratic coefficients.",
            "endpoint_E_connectors": "Visual guides only, not interior certification.",
            "orange_steps": "Saved closed-cell upper bounds; R upper uses supremum convention.",
            "ratio_zero_denominator": None,
            "physical_source": "SYNTHETIC_ARITHMETIC_CONTROLS; actual HD and named consumer remain INPUT_PENDING.",
        },
        "reference_component_counts": reference.get("component_counts"),
        "reference_component_comparisons": reference.get("component_comparisons"),
    }
    return cases, widths, summary


def main():
    started_cpu = time.process_time()
    started_wall = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    primary_path = root / "raw" / "PRIMARY_RESULTS.json"
    reference_path = root / "raw" / "REFERENCE_RESULTS.json"
    primary = json.loads(primary_path.read_bytes())
    reference = json.loads(reference_path.read_bytes())
    if primary.get("status") != "PASS_SCOPED" or reference.get("status") != "PASS":
        raise ValueError("Figures require primary PASS_SCOPED and reference PASS saved outputs; inspect failed outputs first.")
    figures = root / "figures"
    analysis = root / "analysis"
    outputs = [
        figures / (stem + extension)
        for stem in ("AFFINE_VERTEX_AND_JUMP", "AFFINE_CONSTANT_COMPARISON")
        for extension in (".png", ".svg")
    ]
    summary_path = analysis / "SAVED_OUTPUT_SUMMARY.json"
    manifest_path = figures / "FIGURE_MANIFEST.json"
    for path in outputs + [summary_path, manifest_path]:
        if path.exists():
            raise FileExistsError("Preserve prior output bytes before any replacement: " + str(path))
    figures.mkdir(parents=True, exist_ok=True)
    analysis.mkdir(parents=True, exist_ok=True)
    cases, widths, summary = summarize(primary, reference)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "svg.fonttype": "none", "svg.hashsalt": "WU_R13_SAVED_FIGURES",
        "axes.unicode_minus": False, "savefig.facecolor": "white",
    })
    first = vertex_figure(plt, cases)
    second = endpoint_comparison_figure(plt, cases, widths)
    for figure, stem in ((first, "AFFINE_VERTEX_AND_JUMP"),
                         (second, "AFFINE_CONSTANT_COMPARISON")):
        figure.savefig(figures / (stem + ".png"), dpi=170, bbox_inches="tight",
                       metadata={"Title": stem, "Description": "WU R13 saved-output synthetic arithmetic controls."})
        figure.savefig(figures / (stem + ".svg"), bbox_inches="tight",
                       metadata={"Title": stem, "Description": "WU R13 saved-output synthetic arithmetic controls."})
        plt.close(figure)
    summary["source_files"] = {
        "primary": digest(primary_path),
        "reference": digest(reference_path),
        "plot_script": digest(Path(__file__).resolve()),
    }
    summary["postprocessing_resources"] = {
        "internal_CPU_s": time.process_time() - started_cpu,
        "internal_wall_s": time.monotonic() - started_wall,
        "scope": "Saved-output rendering/summary only; separate from scientific execution CPU.",
        "whole_OS_process_CPU_s": None,
    }
    with summary_path.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    manifest = {
        "schema": "WU_R13_FIGURE_MANIFEST_V1",
        "source_inputs": summary["source_files"],
        "artifacts": [digest(path) for path in outputs + [summary_path]],
        "scientific_computation_reexecuted": False,
        "validation": {
            "PNG_CRC_and_full_decode": "PENDING_ROOT_VERIFICATION",
            "SVG_XML": "PENDING_ROOT_VERIFICATION",
            "visual_inspection": "PENDING_ROOT_VERIFICATION",
        },
        "scope": "Saved-output figures; endpoint connectors and closed-cell certification explicitly distinguished.",
    }
    with manifest_path.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"status": "RENDERED_PENDING_ROOT_VERIFICATION",
                      "figures": [str(path) for path in outputs],
                      "summary": str(summary_path),
                      "postprocessing_CPU_s": summary["postprocessing_resources"]["internal_CPU_s"]}))


if __name__ == "__main__":
    main()
