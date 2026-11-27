#!/usr/bin/env python3
"""Create PHYS81 figures from saved JSON/NPZ data only.

No rate, cross-section, RHS, nuclear-event, or ODE module is imported.  Array
differences, display-unit conversions and summaries of saved samples are the
only numerical operations.  Existing outputs are never overwritten.  A failed
render preserves its claim and partial outputs; use a new output directory for
a separately authorized corrected rendering.

Default invocation from any directory: python source/plot_saved.py
The three figure types are each written as PNG and vector PDF, followed by a
manifest binding every loaded input and every figure by SHA256.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import traceback

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPECIES = ("H1", "He4", "Li7")
SPECIES_LABELS = {"H1": r"$^1\mathrm{H}$", "He4": r"$^4\mathrm{He}$", "Li7": r"$^7\mathrm{Li}$"}
COLORS = ("#0072B2", "#D55E00", "#009E73")  # Okabe-Ito palette.
MARKERS = ("o", "s", "^")
STYLES = ("-", "--", "-.")
TASK_LABELS = ("hazard_base", "hazard_refined", "original7_reference")
FIGURE_STEMS = ("finite_rates_and_Bell_window", "parcel_saved_trajectories", "cold_capture_energies")
GATE = 1e-7
TIME_SCALE_S = 1e13


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def write_json_once(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


class SavedInputs:
    """Hash the exact bytes parsed, avoiding a separate hash/load race."""

    def __init__(self):
        self.records = {}

    def read_bytes(self, path, role):
        path = Path(path).resolve()
        raw = path.read_bytes()
        self.records[str(path)] = {"role": role, "sha256": sha_bytes(raw), "bytes": len(raw)}
        return raw

    def json(self, path, role):
        return json.loads(self.read_bytes(path, role))

    def npz(self, path, expected_sha):
        raw = self.read_bytes(path, "saved parcel trajectory")
        require(sha_bytes(raw) == expected_sha, "TRAJECTORY_SHA256_MISMATCH:" + str(path))
        with np.load(io.BytesIO(raw), allow_pickle=False) as loaded:
            arrays = {name: np.array(loaded[name], copy=True)
                      for name in ("s", "t_s", "scaled7", "T_K", "xe")}
        for name, array in arrays.items():
            require(np.issubdtype(array.dtype, np.number) and not np.iscomplexobj(array),
                    "TRAJECTORY_REQUIRES_REAL_NUMERIC_ARRAY:" + name)
            require(np.all(np.isfinite(array)), "NONFINITE_SAVED_ARRAY:" + name)
        n = len(arrays["s"])
        require(n >= 2 and arrays["scaled7"].shape == (n, 7), "SAVED_STATE_SHAPE_MISMATCH")
        require(all(arrays[name].shape == (n,) for name in ("s", "t_s", "T_K", "xe")),
                "SAVED_TIME_SERIES_SHAPE_MISMATCH")
        require(np.all(np.diff(arrays["s"]) > 0) and np.all(np.diff(arrays["t_s"]) > 0),
                "SAVED_TIME_NOT_STRICTLY_INCREASING")
        return arrays


def load_saved(args, inputs):
    profile = inputs.json(args.rate_profiles, "saved finite/Bell rate profiles")
    require(profile.get("schema") == "PHYS81_RATE_PROFILE_V2", "UNSUPPORTED_RATE_PROFILE_SCHEMA")
    require(profile.get("status") == "COMPLETE_SCOPED", "RATE_PROFILE_NOT_COMPLETE_SCOPED")
    registry_raw = inputs.read_bytes(args.registry, "admitted finite-source windows and chemical registry")
    require(sha_bytes(registry_raw) == profile["source_registry_sha256"], "RATE_REGISTRY_BINDING_MISMATCH")
    registry = json.loads(registry_raw)
    require(registry.get("status") == "ADMITTED_EXPLICIT_FINITE_MODEL_ONLY", "REGISTRY_SCOPE_MISMATCH")
    windows = {r["project_label"]: tuple(r["allowed_window_eV"]) for r in registry["source_curves"]}
    rate_rows = {}
    require({r["species"] for r in profile["rows"]} == set(SPECIES), "PROFILE_SPECIES_MISMATCH")
    for species in SPECIES:
        rows = sorted((r for r in profile["rows"] if r["species"] == species), key=lambda r: r["T_K"])
        require(len(rows) >= 2, "INSUFFICIENT_RATE_SAMPLES:" + species)
        for row in rows:
            require(all(math.isfinite(float(row[k])) for k in
                        ("T_K", "finite_log10_K", "Bell_model_window_fraction")), "NONFINITE_RATE_PLOT_INPUT")
            require(row["T_K"] > 0 and row["Bell_model_window_fraction"] >= 0, "INVALID_RATE_PLOT_INPUT")
            require(isinstance(row["finite_underflow"], bool), "UNDERFLOW_FLAG_MUST_BE_BOOLEAN")
        require(all(b["T_K"] > a["T_K"] for a, b in zip(rows[:-1], rows[1:])), "DUPLICATE_RATE_TEMPERATURE")
        require([r["T_K"] for r in rows] == profile["identity"]["temperatures_K"], "PROFILE_TEMPERATURE_IDENTITY_MISMATCH")
        rate_rows[species] = rows

    parcel_root = args.parcel_root.resolve()
    plan = inputs.json(parcel_root / "PLAN.json", "saved parcel plan and comparison gates")
    summary = inputs.json(parcel_root / "SCIENCE_SUMMARY.json", "saved parcel cohort decision")
    require(summary.get("status") in ("PASS_SCOPED", "FAILED_COMPARISON"), "PARCEL_COHORT_NOT_COMPLETE")
    require(sha_bytes(canonical(plan["binding"])) == summary["binding_SHA256"], "PARCEL_PLAN_BINDING_MISMATCH")
    gates = plan["binding"]["gates"]
    require(gates["maximum_normalized_7state_comparison"] == GATE
            and gates["maximum_T_fraction_of_T0"] == GATE, "SAVED_COMPARISON_GATE_IS_NOT_1E_MINUS_7")
    model = plan["binding"]["model"]
    require(math.isfinite(model["T0_K"]) and model["T0_K"] > 0, "INVALID_SAVED_T0")
    records = {r["label"]: r for r in summary["records"]}
    require(set(records) == set(TASK_LABELS) and len(summary["records"]) == 3, "PARCEL_COHORT_LABEL_MISMATCH")
    trajectories = {}
    for label in TASK_LABELS:
        key = records[label]["science_id"]
        require(len(key) == 64 and all(c in "0123456789abcdef" for c in key), "INVALID_SCIENCE_ID")
        complete = inputs.json(parcel_root / key / "COMPLETE.json", "saved complete record: " + label)
        require(complete["status"] == "COMPLETE" and complete["science_id"] == key
                and complete["label"] == label, "SAVED_COMPLETE_RECORD_MISMATCH")
        require(sha_bytes(canonical(complete["identity"])) == key, "SAVED_SCIENCE_IDENTITY_MISMATCH")
        require({k: v for k, v in complete["identity"].items() if k != "solver"} == plan["binding"],
                "SAVED_TRAJECTORY_PLAN_MISMATCH")
        expected_sha = summary["trajectory_SHA256_by_id"][key]
        require(complete["trajectory_SHA256"] == expected_sha, "COHORT_TRAJECTORY_BINDING_MISMATCH")
        trajectories[label] = inputs.npz(parcel_root / key / "trajectory.npz", expected_sha)
    reference = trajectories["hazard_refined"]
    comparisons = {}
    saved_pairs = {tuple(r["pair"]): r for r in summary["comparisons"]}
    for label in ("hazard_base", "original7_reference"):
        current = trajectories[label]
        require(np.array_equal(current["s"], reference["s"])
                and np.array_equal(current["t_s"], reference["t_s"]), "SAVED_COMPARISON_GRID_MISMATCH")
        state_error = np.max(np.abs(current["scaled7"] - reference["scaled7"]), axis=1)
        temperature_error = np.abs(current["T_K"] - reference["T_K"]) / model["T0_K"]
        saved = saved_pairs[(label, "hazard_refined")]
        require(math.isclose(float(np.max(state_error)), saved["max_scaled7_error"], rel_tol=5e-13, abs_tol=0)
                and math.isclose(float(np.max(temperature_error)), saved["max_T_fraction_T0"], rel_tol=5e-13, abs_tol=0),
                "SAVED_COMPARISON_SUMMARY_MISMATCH")
        comparisons[label] = {"state": state_error, "temperature": temperature_error}

    cold = inputs.json(args.cold_rows, "saved cold-capture row extraction")
    require(cold.get("schema") == "PHYS81_COLD_ROWS_RECEIPT_EXTRACTION_V1", "UNSUPPORTED_COLD_ROW_SCHEMA")
    nuclear_receipt_path = args.cold_rows.parent / "NUMERIC_RECEIPT_001.json"
    nuclear_raw = inputs.read_bytes(nuclear_receipt_path, "original saved nuclear numerical receipt")
    require(sha_bytes(nuclear_raw) == cold["source_receipt_sha256"], "COLD_ROW_RECEIPT_SHA256_MISMATCH")
    original_events = json.loads(nuclear_raw)["event_results"]
    require(len(cold["rows"]) == 3, "THREE_COLD_CAPTURE_ROWS_REQUIRED")
    expected_reactions = {"np_d_gamma", "nd_t_gamma", "pd_h_gamma"}
    require({r["reaction"] for r in cold["rows"]} == expected_reactions, "COLD_REACTION_SET_MISMATCH")
    for row in cold["rows"]:
        require(float(row["K_MeV"]) == 0, "COLD_CAPTURE_REQUIRES_SAVED_K_ZERO")
        keys = ("reaction", "K_MeV", "Q_MeV", "photon_MeV", "recoil_MeV")
        require(any(all(event[k] == row[k] for k in keys) for event in original_events), "COLD_EXTRACTED_STRINGS_MISMATCH")
        require(all(math.isfinite(float(row[k])) and float(row[k]) > 0 for k in ("photon_MeV", "recoil_MeV")),
                "INVALID_SAVED_CAPTURE_ENERGY")
    return {"profile": profile, "rate_rows": rate_rows, "windows": windows, "plan": plan,
            "summary": summary, "model": model, "trajectories": trajectories,
            "comparisons": comparisons, "cold": cold}


def style_axis(ax, *, xgrid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="both" if xgrid else "y", color="#dce1e6", linewidth=0.65, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=9)


def rate_figure(data, plt):
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.1))
    fig.subplots_adjust(left=0.065, right=0.98, bottom=0.28, top=0.80, wspace=0.30)
    fig.suptitle("Finite-source ionization rates and Bell-model window fractions", x=0.05, y=0.97,
                 ha="left", fontsize=17, fontweight="bold")
    fig.text(0.05, 0.90, "Stationary-target Maxwell operator | markers are saved samples; segments guide the eye", fontsize=10)
    for species, color, marker, line in zip(SPECIES, COLORS, MARKERS, STYLES):
        rows = data["rate_rows"][species]
        T = np.array([r["T_K"] for r in rows])
        logK = np.array([r["finite_log10_K"] for r in rows])
        fraction = np.array([r["Bell_model_window_fraction"] for r in rows])
        underflow = np.array([r["finite_underflow"] for r in rows], dtype=bool)
        options = dict(color=color, marker=marker, linestyle=line, markersize=4.5, linewidth=1.8,
                       label=SPECIES_LABELS[species])
        axes[0].plot(T, logK, **options)
        axes[0].scatter(T[underflow], logK[underflow], s=95, facecolors="none", edgecolors=color, linewidths=1.3)
        warm = T >= 10000
        axes[1].plot(T[warm], logK[warm], **options)
        axes[2].plot(T, np.ma.masked_where(fraction == 0, fraction), **options)
    axes[0].set_xscale("log")
    axes[2].set_xscale("log")
    axes[2].set_yscale("log", nonpositive="mask")
    axes[0].set_title("A. All saved temperatures", loc="left", fontsize=11)
    axes[1].set_title("B. Saved samples at T >= 10,000 K", loc="left", fontsize=11)
    axes[2].set_title("C. Fraction inside the selected window", loc="left", fontsize=11)
    for ax in axes[:2]:
        ax.set_ylabel(r"$\log_{10}[K/(\mathrm{cm^3\,s^{-1}})]$")
    axes[2].set_ylabel(r"$K_{\rm Bell,window}/K_{\rm Bell,full}$")
    axes[2].axhline(1.0, color="#555555", linestyle=":", linewidth=1, label="Full Bell support")
    axes[2].set_ylim(top=max(1.2, 1.15 * max(r["Bell_model_window_fraction"] for r in data["profile"]["rows"])))
    for ax in axes:
        ax.set_xlabel("Temperature (K)")
        style_axis(ax)
    axes[0].legend(frameon=False, loc="lower right", fontsize=10)
    zero_fractions = sum(r["Bell_model_window_fraction"] == 0 for r in data["profile"]["rows"])
    if zero_fractions:
        axes[2].text(0.03, 0.03, f"{zero_fractions} exact-zero samples excluded from log axis", transform=axes[2].transAxes, fontsize=8)
    support = "; ".join(f"{name}: {float(data['windows'][key][0]):g}-{float(data['windows'][key][1]):g}"
                        for key, name in zip(SPECIES, ("H", "He", "Li")))
    fig.text(0.05, 0.18, "Finite incident-energy support (eV): " + support + ".  Open rings flag raw-rate underflow; saved log10 K is retained.", fontsize=9)
    fig.text(0.05, 0.125, "Bell fractions belong to the Bell analytic fit; they are not physical coverage fractions or error bounds.", fontsize=9)
    fig.text(0.05, 0.07, "Source limits: unpublished He author curve; omitted threshold intervals and upper tails; no isotope-resolved cross-section certificate.", fontsize=9)
    return fig


def error_panel(fig, slot, time_axis, comparisons, metric, title, ylabel):
    inner = slot.subgridspec(2, 1, height_ratios=(4, 1.15), hspace=0.12)
    ax = fig.add_subplot(inner[0])
    zeros = fig.add_subplot(inner[1], sharex=ax)
    descriptions = ("3-state base vs refined", "Original 7-state vs refined 3-state")
    short = ("3 vs 3", "7 vs 3")
    any_positive = False
    zero_counts = {}
    for row, (label, color, description) in enumerate(zip(("hazard_base", "original7_reference"), COLORS[:2], descriptions)):
        values = comparisons[label][metric]
        positive = values > 0
        any_positive = any_positive or bool(np.any(positive))
        ax.plot(time_axis, np.ma.masked_where(~positive, values), color=color, linestyle=STYLES[row],
                linewidth=1.6, label=description)
        is_zero = values == 0
        zeros.plot(time_axis[is_zero], np.full(np.count_nonzero(is_zero), row), linestyle="none",
                   marker="|", markersize=8, markeredgewidth=1.1, color=color)
        zero_counts[label] = int(np.count_nonzero(is_zero))
    ax.set_yscale("log", nonpositive="mask")
    ax.axhline(GATE, color="#333333", linewidth=1.2, linestyle=":", label=r"Saved gate $10^{-7}$")
    if not any_positive:
        ax.set_ylim(GATE / 10, GATE * 10)
        ax.text(0.03, 0.30, "All saved errors are exactly zero.\nSee the separate zero strip.", transform=ax.transAxes, fontsize=9)
    ax.set_title(title, loc="left", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.tick_params(labelbottom=False)
    ax.legend(loc="best", frameon=False, fontsize=8)
    style_axis(ax)
    zeros.set_facecolor("#f4f6f8")
    zeros.set_ylim(-0.65, 1.65)
    zeros.set_yticks((0, 1), [f"{short[i]}: n={zero_counts[label]}" for i, label in enumerate(("hazard_base", "original7_reference"))])
    zeros.tick_params(axis="y", length=0, labelsize=8)
    zeros.tick_params(axis="x", labelsize=9)
    zeros.set_ylabel("Exact zero", fontsize=8)
    zeros.set_xlabel(r"Time ($10^{13}$ s)")
    for spine in zeros.spines.values():
        spine.set_color("#dce1e6")
    return zero_counts


def parcel_figure(data, plt):
    fig = plt.figure(figsize=(13.8, 10.6))
    grid = fig.add_gridspec(2, 2, left=0.085, right=0.975, bottom=0.19, top=0.84,
                          hspace=0.42, wspace=0.31, height_ratios=(1.05, 1))
    fig.suptitle("Saved CI-only parcel evolution and coordinate comparisons", x=0.05, y=0.975,
                 ha="left", fontsize=17, fontweight="bold")
    model = data["model"]
    fig.text(0.05, 0.925, f"T0 = {model['T0_K']:.6g} K | nref = {model['nref_cm3']:g} cm^-3 | saved cohort: {data['summary']['status']}", fontsize=10)
    fig.text(0.05, 0.885, "Fixed density; shared thermal reservoir; finite CI only. Ion fractions use each species' own total abundance.", fontsize=9)
    reference = data["trajectories"]["hazard_refined"]
    time_axis = reference["t_s"] / TIME_SCALE_S
    axT = fig.add_subplot(grid[0, 0])
    for label, description, color, line, marker in (
        ("hazard_base", "3-state Radau, base", COLORS[0], "--", "o"),
        ("original7_reference", "Original 7-state DOP853", COLORS[1], ":", "s"),
        ("hazard_refined", "3-state Radau, refined", "#222222", "-", None),
    ):
        axT.plot(time_axis, data["trajectories"][label]["T_K"], label=description, color=color,
                 linestyle=line, linewidth=1.5, marker=marker, markersize=3, markevery=20,
                 markerfacecolor="none")
    axT.set_title("A. Saved temperature", loc="left", fontsize=11)
    axT.set_ylabel("Temperature (K)")
    axT.set_xlabel(r"Time ($10^{13}$ s)")
    axT.legend(frameon=False, fontsize=8.5)
    style_axis(axT)
    ion_grid = grid[0, 1].subgridspec(3, 1, hspace=0.28)
    for index, (species, color) in enumerate(zip(SPECIES, COLORS)):
        ax = fig.add_subplot(ion_grid[index])
        ax.plot(time_axis, reference["scaled7"][:, index + 3], color=color, linewidth=1.7)
        ax.set_ylabel(SPECIES_LABELS[species] + r" $X_s/B_s$", fontsize=10)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3), useOffset=False)
        ax.yaxis.get_offset_text().set_fontsize(8)
        if index == 0:
            ax.set_title("B. Refined ion fractions: separate linear scales", loc="left", fontsize=11)
        if index < 2:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel(r"Time ($10^{13}$ s)")
        style_axis(ax)
    zero_counts = {
        "state": error_panel(fig, grid[1, 0], time_axis, data["comparisons"], "state",
                             "C. Maximum of the seven normalized state errors", r"$\max_j |w_j-w_{j,\rm refined}|$"),
        "temperature": error_panel(fig, grid[1, 1], time_axis, data["comparisons"], "temperature",
                                   "D. Temperature comparison", r"$|T-T_{\rm refined}|/T_0$"),
    }
    fig.text(0.05, 0.115, r"Normalized state: $w=(N_s/B_s,\ X_s/B_s,\ u/u_0)$. Original 7-state coordinates are saved without conservation projection.", fontsize=9)
    fig.text(0.05, 0.075, "Only positive errors appear on log axes; exact zeros are separate ticks with counts. No positive floor or smoothing is applied.", fontsize=9)
    fig.text(0.05, 0.035, "Comparisons use the saved common sample grid. The gate concerns these samples; it is not a continuum or physical-model accuracy certificate.", fontsize=9)
    return fig, zero_counts


def capture_figure(data, plt):
    names = {"np_d_gamma": r"$n+p\ \to\ d+\gamma$", "nd_t_gamma": r"$n+d\ \to\ t+\gamma$",
             "pd_h_gamma": r"$p+d\ \to\ {}^3\mathrm{He}+\gamma$"}
    rows = sorted(data["cold"]["rows"], key=lambda r: ("np_d_gamma", "nd_t_gamma", "pd_h_gamma").index(r["reaction"]))
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.6), sharey=True)
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.27, top=0.77, wspace=0.24)
    fig.suptitle("Cold-COM radiative capture: photon and nuclear recoil", x=0.05, y=0.96,
                 ha="left", fontsize=16, fontweight="bold")
    fig.text(0.05, 0.875, "K = 0; energies read from the saved independently checked event receipt", fontsize=10)
    y = np.arange(len(rows))
    for ax, field, scale, title, xlabel in (
        (axes[0], "photon_MeV", 1.0, "A. Escaping photon", "Photon energy (MeV)"),
        (axes[1], "recoil_MeV", 1e6, "B. Daughter-nucleus recoil", "Recoil kinetic energy (eV)"),
    ):
        values = np.array([float(row[field]) * scale for row in rows])
        ax.barh(y, values, height=0.52, color=COLORS, alpha=0.90)
        ax.set_xlim(0, float(np.max(values)) * 1.28)
        for height, value in zip(y, values):
            ax.text(value + float(np.max(values)) * 0.025, height, f"{value:.6g}", va="center", fontsize=10)
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_xlabel(xlabel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#dce1e6", linewidth=0.65)
        ax.tick_params(labelsize=10)
    axes[0].set_yticks(y, [names[row["reaction"]] for row in rows])
    axes[0].invert_yaxis()
    axes[1].tick_params(axis="y", labelleft=False)
    fig.text(0.05, 0.17, "Stored arithmetic from rounded CODATA mass entries; labels are rounded for display. Physical uncertainties and covariance are not propagated.", fontsize=9)
    fig.text(0.05, 0.105, "Recoil is the available daughter kinetic energy; its thermal deposition requires an explicit supplied fraction, not shown here.", fontsize=9)
    fig.text(0.05, 0.045, "Cold center-of-momentum event kinematics only: no nuclear rate activation, finite-temperature average, or photon transport calculation.", fontsize=9)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rate-profiles", type=Path, default=ROOT / "results/RATE_PROFILES.json")
    parser.add_argument("--registry", type=Path, default=ROOT / "source_data/ADMITTED_FINITE_CI_REGISTRY.json")
    parser.add_argument("--parcel-root", type=Path, default=ROOT / "results/parcel")
    parser.add_argument("--cold-rows", type=Path, default=ROOT / "verification/nuclear/COLD_ROWS_FROM_RECEIPT.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "figures")
    args = parser.parse_args()
    args.cold_rows = args.cold_rows.resolve()
    out = args.output_dir.resolve()
    names = [stem + "." + suffix for stem in FIGURE_STEMS for suffix in ("png", "pdf")]
    require(not any((out / name).exists() for name in names + ["PLOT_CLAIM.json", "PLOT_MANIFEST.json", "PLOT_FAILED.json"]),
            "CREATE_ONLY_PLOT_OUTPUT_ALREADY_EXISTS")
    inputs = SavedInputs()
    data = load_saved(args, inputs)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    binding = {"schema": "PHYS81_SAVED_DATA_PLOT_V1", "created_utc": started,
               "plotter_sha256": sha_bytes(Path(__file__).read_bytes()), "inputs": inputs.records,
               "operations": ["read and validate saved JSON/NPZ", "differences of saved common-grid arrays",
                              "MeV-to-eV and seconds-to-axis-unit display conversion", "render saved samples"],
               "new_rate_evaluations": 0, "new_RHS_evaluations": 0, "new_nuclear_event_evaluations": 0,
               "new_ODEs": 0, "positive_floors": False, "smoothing_or_resampling": False,
               "comparison_gate": GATE, "time_axis_unit_s": TIME_SCALE_S,
               "source_profile_meaning": data["profile"]["meaning"],
               "nuclear_precision_scope": data["cold"]["physical_uncertainty"]}
    write_json_once(out / "PLOT_CLAIM.json", binding)
    figures = []
    outputs = []
    try:
        import matplotlib
        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                             "axes.labelsize": 10, "axes.titlesize": 11,
                             "figure.facecolor": "white", "savefig.facecolor": "white",
                             "pdf.fonttype": 42, "ps.fonttype": 42})
        figures.append((FIGURE_STEMS[0], rate_figure(data, plt)))
        parcel_fig, zero_counts = parcel_figure(data, plt)
        figures.append((FIGURE_STEMS[1], parcel_fig))
        figures.append((FIGURE_STEMS[2], capture_figure(data, plt)))
        for stem, fig in figures:
            for extension in ("png", "pdf"):
                path = out / (stem + "." + extension)
                with path.open("xb") as stream:
                    fig.savefig(stream, format=extension, dpi=240, facecolor="white")
                raw = path.read_bytes()
                outputs.append({"path": str(path), "figure_type": stem, "format": extension,
                                "bytes": len(raw), "sha256": sha_bytes(raw)})
            plt.close(fig)
        result = {**binding, "status": "COMPLETE_SAVED_DATA_RENDER", "command_argv": sys.argv,
                  "runtime": {"python": sys.version, "numpy": np.__version__, "matplotlib": matplotlib.__version__},
                  "rate_saved_rows": len(data["profile"]["rows"]),
                  "parcel_saved_samples_per_trajectory": len(data["trajectories"]["hazard_refined"]["s"]),
                  "parcel_saved_cohort_status": data["summary"]["status"],
                  "error_exact_zero_counts": zero_counts, "cold_saved_rows": len(data["cold"]["rows"]),
                  "outputs": outputs, "output_count": len(outputs),
                  "completed_utc": datetime.now(timezone.utc).isoformat(),
                  "visual_inspection": "NOT_PERFORMED_BY_SCRIPT; inspect the saved PNGs separately",
                  "scope": "Visualization of existing saved evidence; scientific admission is unchanged"}
        write_json_once(out / "PLOT_MANIFEST.json", result)
        print(json.dumps({"status": result["status"], "output_dir": str(out), "figures": 3,
                          "files": len(outputs), "new_science_evaluations": 0}))
    except Exception as exc:
        write_json_once(out / "PLOT_FAILED.json", {**binding, "status": "RENDER_FAILED_PARTIAL_OUTPUTS_PRESERVED",
                        "exception": repr(exc), "traceback": traceback.format_exc(), "completed_outputs": outputs})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
