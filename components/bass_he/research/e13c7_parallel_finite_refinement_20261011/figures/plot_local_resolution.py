#!/usr/bin/env python3
"""Plot completed E13C7 measurements without importing scientific kernels.

Run from any working directory: python3 /absolute/path/to/this/script.py
Only files under this script's figures/ directory are written.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NODES = (105, 409, 1162, 1976)
ANALYSIS_PATH = ROOT / "analysis/LOCAL/LOCAL_ANALYSIS.json"
RESOURCE_PATH = ROOT / "analysis/RESOURCE_ALLOCATION.json"
STEM = "E13C7_LOCAL_N512_TO_N1024"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)


def decimal_text(value: Fraction, digits: int = 30) -> str:
    with localcontext() as context:
        context.prec = digits
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def main() -> None:
    analysis = read_json(ANALYSIS_PATH)
    allocation = read_json(RESOURCE_PATH)
    assert analysis["schema"] == "bass-he-e13c7-local-analysis-v1"
    assert analysis["full_2331_refinement"] == "NOT_RUN"
    assert allocation["ncp_new_paths_executed_here"] == 0
    assert allocation["chosen_N"] == 1024

    source_inputs = [identity(ANALYSIS_PATH), identity(RESOURCE_PATH)]
    comparisons = {entry["node"]: entry for entry in analysis["resolution_comparison"]}
    assert set(comparisons) == set(NODES)
    resources = {
        (entry["node"], entry["N"], entry["precision"]): entry
        for entry in analysis["resource_rows"]
    }
    numeric_rows = []
    exact_values = []

    for node in NODES:
        comparison = comparisons[node]
        assert comparison["raw_N1024_eligible_over_N512"] is True
        assert len(comparison["rows_N512_to_N1024"]) == 34
        assert all(
            entry["nested"] and entry["width_nonincreasing"] and entry["overlap"]
            for entry in comparison["rows_N512_to_N1024"]
        )
        selected = {
            entry["quantity"]: entry
            for entry in comparison["rows_N512_to_N1024"]
            if entry["kind"] == "absolute" and entry["quantity"] in {"P_final", "H_total_eV"}
        }
        assert set(selected) == {"P_final", "H_total_eV"}
        row = {"node": node, "N_reference": 512, "N_refined": 1024, "precision": 60}
        exact = {"node": node, "quantities": {}}
        for quantity, column in (("P_final", "photon"), ("H_total_eV", "heat")):
            entry = selected[quantity]
            width512 = Fraction(entry["old_width"])
            width1024 = Fraction(entry["new_width"])
            assert width512 == Fraction(entry["old"]["hi"]) - Fraction(entry["old"]["lo"])
            assert width1024 == Fraction(entry["new_raw"]["hi"]) - Fraction(entry["new_raw"]["lo"])
            assert 0 < width1024 <= width512
            retained = width1024 / width512
            assert 1 - retained == Fraction(entry["gain_fraction"])
            row.update({
                f"{column}_width_N512_exact": str(width512),
                f"{column}_width_N1024_exact": str(width1024),
                f"{column}_retained_width_exact": str(retained),
                f"{column}_retained_width_decimal": decimal_text(retained),
                f"{column}_removed_width_percent_decimal": decimal_text(100 * (1 - retained)),
            })
            exact["quantities"][quantity] = {
                "kind": "absolute",
                "width_N512": str(width512),
                "width_N1024": str(width1024),
                "retained_width_ratio_exact": str(retained),
                "plotted_float": float(retained),
                "nested": True,
                "width_nonincreasing": True,
            }

        for N in (512, 1024):
            resource = resources[(node, N, 60)]
            path = ROOT / resource["path"]
            result_path = path / "RESULT.json"
            complete_path = path / "COMPLETE.json"
            result = read_json(result_path)
            complete = read_json(complete_path)
            assert result["work"] == {"N": N, "mode": "OFF", "node": node, "precision": 60}
            assert complete["status"] == "COMPLETE"
            assert complete["result_sha256"] == sha256(result_path)
            assert complete["semantic_sha256"] == resource["semantic_sha256"]
            assert complete["source_lock_sha256"] == analysis["source_lock_sha256"]
            assert result["elapsed_seconds"] == complete["elapsed_seconds"] == resource["seconds"]
            assert resource["seconds"] == comparison[f"seconds_N{N}"]
            row[f"elapsed_seconds_N{N}_recorded"] = str(resource["seconds"])
            row[f"result_N{N}_path"] = result_path.relative_to(ROOT).as_posix()
            row[f"result_N{N}_sha256"] = sha256(result_path)
            row[f"semantic_N{N}_sha256"] = complete["semantic_sha256"]
            source_inputs.extend([identity(result_path), identity(complete_path)])

        observed_ratio = comparison["observed_time_ratio"]
        t512 = comparison["seconds_N512"]
        t1024 = comparison["seconds_N1024"]
        assert float(observed_ratio) == float(t1024) / float(t512)
        row["elapsed_time_multiplier_recorded"] = str(observed_ratio)
        row["elapsed_time_ratio_of_recorded_decimal_seconds_exact"] = str(Fraction(t1024) / Fraction(t512))
        exact["elapsed_seconds_N512_recorded"] = str(t512)
        exact["elapsed_seconds_N1024_recorded"] = str(t1024)
        exact["elapsed_time_multiplier_recorded"] = str(observed_ratio)
        exact["elapsed_time_multiplier_plotted_float"] = float(observed_ratio)
        exact_values.append(exact)
        numeric_rows.append(row)

    csv_path = HERE / f"{STEM}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(numeric_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(numeric_rows)

    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#48525F",
        "axes.linewidth": 0.7,
        "xtick.color": "#333B46",
        "ytick.color": "#333B46",
        "text.color": "#202936",
        "axes.labelcolor": "#202936",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.8))
    figure.subplots_adjust(left=0.080, right=0.976, top=0.775, bottom=0.235, wspace=0.28)
    figure.suptitle("Local resolution refinement: N = 512 → 1024", x=0.080, y=0.960,
                    ha="left", fontsize=17, fontweight="semibold")
    figure.text(0.080, 0.895, "Four fixed OFF paths  ·  Decimal precision 60  ·  Completed local measurements",
                ha="left", va="center", fontsize=11, color="#536171")

    x = list(range(len(NODES)))
    photon = [v["quantities"]["P_final"]["plotted_float"] for v in exact_values]
    heat = [v["quantities"]["H_total_eV"]["plotted_float"] for v in exact_values]
    timing = [v["elapsed_time_multiplier_plotted_float"] for v in exact_values]
    width = 0.32
    left, right = axes
    photon_bars = left.bar([v - width / 2 for v in x], photon, width=width,
                           color="#286C9A", label=r"Photon stock, $P_{\mathrm{final}}$", zorder=3)
    heat_bars = left.bar([v + width / 2 for v in x], heat, width=width,
                         color="#CF7239", label=r"Total heat, $H_{\mathrm{total}}$", zorder=3)
    left.set_title("A   Enclosure width retained (%)", loc="left", pad=13, fontweight="semibold")
    left.set_ylabel(r"Width ratio, $W_{1024}/W_{512}$")
    left.set_ylim(0, 1.12)
    left.set_yticks([0, 0.25, 0.50, 0.75, 1.0])
    left.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    left.axhline(1.0, color="#7A8794", linestyle=(0, (4, 3)), linewidth=0.9, zorder=2)
    left.text(3.52, 1.025, "N512 reference", ha="right", va="bottom", fontsize=9, color="#606D7B")
    left.legend(loc="upper left", bbox_to_anchor=(0.02, 0.87), frameon=False,
                fontsize=9.5, borderaxespad=0, handlelength=1.2, handletextpad=0.6)
    for bars in (photon_bars, heat_bars):
        for bar in bars:
            left.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.020,
                      f"{100 * bar.get_height():.1f}", ha="center", va="bottom", fontsize=9.5)

    time_bars = right.bar(x, timing, width=0.58, color="#485C70", zorder=3)
    right.set_title("B   Elapsed time multiplier", loc="left", pad=13, fontweight="semibold")
    right.set_ylabel(r"Time ratio, $t_{1024}/t_{512}$")
    right.set_ylim(0, 2.8)
    right.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    right.axhline(1, color="#7A8794", linestyle=(0, (4, 3)), linewidth=0.9, zorder=4)
    right.text(3.48, 1.045, "Equal runtime", ha="right", va="bottom", fontsize=9, color="#606D7B",
               bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
    for bar, value in zip(time_bars, exact_values):
        center = bar.get_x() + bar.get_width() / 2
        right.text(center, bar.get_height() + 0.05, f"{bar.get_height():.2f}×",
                   ha="center", va="bottom", fontsize=11, fontweight="semibold")

    for axis in axes:
        axis.set_xticks(x, [str(node) for node in NODES])
        axis.set_xlabel("OFF path node", labelpad=8)
        axis.set_xlim(-0.60, 3.60)
        axis.grid(axis="y", color="#E4E9EE", linewidth=0.7, zorder=0)
        axis.tick_params(axis="both", length=3, width=0.6)

    figure.text(0.080, 0.135,
                "N1024 removes 55.6–68.0% of the N512 photon / heat width at 2.17–2.27× the observed elapsed time.",
                ha="left", va="center", fontsize=10.3, color="#293749")
    figure.text(0.080, 0.079,
                "Widths are raw absolute enclosures; ratios use exact rational widths. One timing per setting; no 64-rank scaling measurement.",
                ha="left", va="center", fontsize=8.8, color="#657383")
    png_path = HERE / f"{STEM}.png"
    pdf_path = HERE / f"{STEM}.pdf"
    figure.savefig(png_path, dpi=300, metadata={"Title": "E13C7 local resolution refinement", "Author": "BASS_HE"})
    figure.savefig(pdf_path, metadata={
        "Title": "E13C7 local resolution refinement: N512 to N1024",
        "Author": "BASS_HE",
        "Subject": "Completed local fixed OFF paths; exact interval widths and recorded elapsed times",
        "Creator": "plot_local_resolution.py / matplotlib",
        "CreationDate": datetime(2026, 10, 11, tzinfo=timezone.utc),
        "ModDate": datetime(2026, 10, 11, tzinfo=timezone.utc),
    })
    plt.close(figure)

    provenance = {
        "schema": "bass-he-e13c7-local-resolution-figure-v1",
        "role": "author-side visualization; no scientific decision or independent review",
        "scope": "four completed local OFF paths, N512 and N1024, Decimal precision 60",
        "nodes": list(NODES),
        "new_scientific_invocations": 0,
        "new_coefficient_evaluations": 0,
        "kernel_imports": 0,
        "NCP_new_batch_paths": 0,
        "NCP_64_rank_scaling": "NOT_RUN; no performance projection is plotted",
        "source_analysis_status": analysis["status"],
        "source_lock_sha256": analysis["source_lock_sha256"],
        "source_inputs": source_inputs,
        "analysis_field": "resolution_comparison[node].rows_N512_to_N1024[kind=absolute,quantity=P_final or H_total_eV]",
        "time_field": "resolution_comparison[node].observed_time_ratio, cross-checked against resource_rows and each RESULT/COMPLETE",
        "width_definition": "W = hi - lo; exact Fraction arithmetic; retained ratio = W1024 / W512; no interval intersection",
        "arithmetic": "input interval widths and width ratios remain exact rationals; conversion to binary64 occurs only for plotting",
        "timing_definition": "recorded elapsed seconds per path, one local timing for each N; no replicate distribution or uncertainty bar",
        "interpretation": {
            "width_retained_range": [min(photon + heat), max(photon + heat)],
            "width_removed_percent_range": [100 * (1 - max(photon + heat)), 100 * (1 - min(photon + heat))],
            "observed_time_multiplier_range": [min(timing), max(timing)],
            "claim_ceiling": "measured four paths only; no full 2331-path width reduction or actual NCP speedup inferred",
        },
        "exact_data": exact_values,
        "outputs": [identity(csv_path), identity(png_path), identity(pdf_path), identity(Path(__file__).resolve())],
        "rendering": {
            "python": platform.python_version(),
            "matplotlib": matplotlib.__version__,
            "backend": matplotlib.get_backend(),
            "figure_inches": [11.8, 5.8],
            "PNG_dpi": 300,
            "PDF_vector": True,
        },
        "visual_inspection": "recorded separately in FIGURE_VISUAL_QA.json; valid only for the image SHA listed there",
    }
    provenance_path = HERE / "FIGURE_PROVENANCE.json"
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files": [identity(p) for p in (png_path, pdf_path, csv_path, provenance_path, Path(__file__).resolve())],
                      "interpretation": provenance["interpretation"]}, indent=2))


if __name__ == "__main__":
    main()
