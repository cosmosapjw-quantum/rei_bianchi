#!/usr/bin/env python3
"""Render completed isolated controls from saved bytes only; never run an ODE."""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/hh_phys79_matplotlib")

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

UNIT = Path(__file__).resolve().parents[1]
SECONDS_PER_YEAR = 31557600.0
KB_EV_K = 1.380649e-23 / 1.602176634e-19
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#666666"
TASKS = ("C01_BASE", "C02_BASE", "C01_REFINED")
STEMS = ("03_c01_isolated_CI_CX_control", "04_c02_isolated_DCX_oracle")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def read_completed(results):
    """Check original receipt sidecars and NPZ bytes before decoding arrays."""
    results = Path(results)
    run_path = results / "ISOLATED_COMMAND_STDOUT.json"
    run_raw = run_path.read_bytes()
    run = json.loads(run_raw)
    if run.get("status") != "COMPLETE":
        raise ValueError("WAIT_FOR_COMPLETE_ISOLATED_RUN")
    task_records = {entry["task_id"]: entry for entry in run["results"]}
    if set(task_records) != set(TASKS) or len(run["results"]) != len(TASKS):
        raise ValueError("REQUIRE_EXACTLY_TWO_CONTROLS_AND_ONE_REFINEMENT")
    cases, evidence = {}, {"run_receipt": {
        "path": str(run_path.relative_to(UNIT)),
        "sha256": sha256(run_raw), "bytes": len(run_raw)}}
    isolated = results / "isolated"
    for name in TASKS:
        entry = task_records[name]
        key = entry["science_id"]
        receipt_path = isolated / "cases" / (key + ".json")
        receipt_raw = receipt_path.read_bytes()
        receipt_hash = sha256(receipt_raw)
        if receipt_path.with_suffix(".json.sha256").read_text().strip() != receipt_hash:
            raise ValueError("RECEIPT_HASH_MISMATCH:" + name)
        receipt = json.loads(receipt_raw)
        if receipt["status"] != "COMPLETE" or receipt["task_id"] != name or receipt["science_id"] != key:
            raise ValueError("CASE_NOT_COMPLETE_OR_ID_MISMATCH:" + name)
        if receipt["npz"] != entry["npz"]:
            raise ValueError("RUN_CASE_NPZ_BINDING_MISMATCH:" + name)
        payload_path = isolated / receipt["npz"]["path"]
        payload_raw = payload_path.read_bytes()
        if (len(payload_raw) != receipt["npz"]["bytes"]
                or sha256(payload_raw) != receipt["npz"]["sha256"]):
            raise ValueError("NPZ_BYTE_CHECK_FAILED:" + name)
        with np.load(io.BytesIO(payload_raw), allow_pickle=False) as saved:
            data = {k: np.array(saved[k], copy=True) for k in saved.files}
        species = [str(v) for v in data["species_names"]]
        if len(species) != 21 or len(set(species)) != 21 or data["Y"].shape != (161, 21):
            raise ValueError("UNEXPECTED_SPECIES_OR_SAMPLE_SHAPE:" + name)
        for field in ("proper_time_s", "theta", "T_K", "Y", "u_eV_per_H"):
            if not np.isfinite(data[field]).all():
                raise ValueError("NONFINITE_SAVED_PLOT_INPUT:" + name + ":" + field)
        if data["proper_time_s"].shape != (161,) or data["T_K"].shape != (161,):
            raise ValueError("CLOCK_OR_TEMPERATURE_SHAPE:" + name)
        if data["proper_time_s"][0] != 0 or np.any(np.diff(data["proper_time_s"]) <= 0):
            raise ValueError("CONTROL_CLOCK_NOT_FROM_ZERO_OR_NOT_INCREASING:" + name)
        cases[name] = {"receipt": receipt, "data": data,
                       "index": {v: i for i, v in enumerate(species)}}
        evidence[name] = {"science_id": key,
                          "physics_id": receipt["physics_id"],
                          "case_receipt": {"path": str(receipt_path.relative_to(UNIT)),
                                           "sha256": receipt_hash, "bytes": len(receipt_raw)},
                          "npz": {"path": str(payload_path.relative_to(UNIT)),
                                  "sha256": sha256(payload_raw), "bytes": len(payload_raw)}}
    baseline, refined = (cases[n] for n in ("C01_BASE", "C01_REFINED"))
    if baseline["receipt"]["physics_id"] != refined["receipt"]["physics_id"]:
        raise ValueError("REFINEMENT_PHYSICS_ID_CHANGED")
    if not np.array_equal(baseline["data"]["proper_time_s"], refined["data"]["proper_time_s"]):
        raise ValueError("REFINEMENT_SAVED_CLOCK_CHANGED")
    for name in TASKS:
        physics = cases[name]["receipt"]["binding"]["physics"]
        expected_rows = [] if name == "C02_BASE" else [0, 1, 3]
        if physics["ci_rows"] != expected_rows or physics["d_cx"] is not True:
            raise ValueError("CONTROL_CHANNEL_SELECTION_CHANGED:" + name)
        if physics["H_per_s"] != 0 or physics["PI"] or physics["RR"] or physics["external_heat_bath"]:
            raise ValueError("ISOLATED_SCOPE_CHANGED:" + name)
    if run["refinement"]["status"] != "PASS":
        raise ValueError("REFINEMENT_NOT_PASSED")
    return cases, run, evidence


def ion_fraction(case, isotopes):
    inventory = case["receipt"]["binding"]["physics"]["isotope_inventory_per_H"]
    denominator = sum(float(inventory[name]) for name in isotopes)
    if denominator <= 0:
        raise ValueError("NONPOSITIVE_FRACTION_INVENTORY")
    columns = [case["index"][name + "_II"] for name in isotopes]
    return case["data"]["Y"][:, columns].sum(axis=1) / denominator


def style(ax, clock, ylabel, time_unit):
    ax.set_xlim(0, float(clock[-1]))
    ax.set_xlabel("Proper time from control start [" + time_unit + "]")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=.23, linewidth=.6)
    ax.tick_params(labelsize=9)
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)


def save(fig, output, stem):
    fig.savefig(output / (stem + ".png"), dpi=180, facecolor="white")
    fig.savefig(output / (stem + ".pdf"), facecolor="white",
                metadata={"Creator": "PHYS79 saved isolated-control plots",
                          "CreationDate": None, "ModDate": None})
    plt.close(fig)


def plot_c01(cases, run, output):
    base, fine = (cases[name] for name in ("C01_BASE", "C01_REFINED"))
    time = base["data"]["proper_time_s"] / (1000 * SECONDS_PER_YEAR)
    values_base = (base["data"]["T_K"], ion_fraction(base, ("H1",)),
                   ion_fraction(base, ("Li6", "Li7")))
    values_fine = (fine["data"]["T_K"], ion_fraction(fine, ("H1",)),
                   ion_fraction(fine, ("Li6", "Li7")))
    labels = ("Gas temperature [K]", "H II / total H1", "Li II / total Li6 + Li7")
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 5.3))
    for ax, y, yfine, label in zip(axes, values_base, values_fine, labels):
        style(ax, time, label, "kyr")
        ax.plot(time, y, color=BLUE, linewidth=2, label="Baseline")
        ax.plot(time[::16], yfine[::16], linestyle="none", marker="o",
                markerfacecolor="white", markeredgecolor=ORANGE,
                markeredgewidth=1.3, markersize=4.4,
                label="Refined (every 16th saved point)")
    axes[0].legend(loc="upper right", fontsize=8, framealpha=.94)
    axes[2].set_ylim(0, 1.02)
    fig.suptitle("C01: isolated neutral CI + D/H charge exchange", y=.98,
                 fontsize=14, fontweight="bold")
    fig.text(.5, .88,
             "Fixed-density closed gas: nH = 0.001 cm⁻³; baseline and refinement share the same initial state.",
             ha="center", fontsize=10)
    delta = run["refinement"]["maximum_scaled_state_difference"]
    fig.text(.5, .045,
             f"Maximum saved scaled-state difference = {delta:.3e}. "
             "The small trace-CX step cap limits both solves; this is not a bound on model error.",
             ha="center", fontsize=8.8)
    fig.text(.5, .012,
             "Time is dimensional proper time. Li II is summed over Li6 and Li7. "
             "These isolated histories do not replace a PHYS78 cosmological trajectory.",
             ha="center", fontsize=8.8)
    fig.subplots_adjust(left=.075, right=.985, top=.78, bottom=.20, wspace=.30)
    save(fig, output, STEMS[0])
    return {"proper_time_end_kyr": float(time[-1]),
            "T_initial_K": float(values_base[0][0]), "T_final_K": float(values_base[0][-1]),
            "H1_II_fraction_initial": float(values_base[1][0]),
            "H1_II_fraction_final": float(values_base[1][-1]),
            "Li_II_fraction_initial": float(values_base[2][0]),
            "Li_II_fraction_final": float(values_base[2][-1]),
            "refinement_scaled_state_difference_from_run_receipt": delta}


def plot_c02(cases, output):
    case = cases["C02_BASE"]; data = case["data"]
    physics = case["receipt"]["binding"]["physics"]
    oracle = case["receipt"]["oracle"]
    if oracle is None or oracle["extra_ODE_calls"] != 0:
        raise ValueError("SCALAR_NO_ODE_ORACLE_MISSING")
    time = data["proper_time_s"] / SECONDS_PER_YEAR
    fraction = ion_fraction(case, ("D",))
    di = case["index"]["D_II"]
    Dtotal = float(physics["isotope_inventory_per_H"]["D"])
    eq_fraction = float(oracle["equilibrium_Y_per_H"][di]) / Dtotal
    extent = data["Y"][:, di] - float(physics["initial_Y_per_H"][di])
    # D/H charge exchange conserves the particle census. This independent
    # energy/extent relation uses only stored physical constants and states.
    N0 = float(physics["initial_u_eV_per_H"]) / (1.5 * KB_EV_K * float(physics["T_initial_K"]))
    extent_drop_mK = 1000 * 2 * float(oracle["Delta_eV_from_stored_global_potential"]) * extent / (3 * KB_EV_K * N0)
    stored_drop_mK = 1000 * (float(physics["T_initial_K"]) - data["T_K"])
    eq_drop_mK = 1000 * (float(physics["T_initial_K"]) - float(oracle["equilibrium_T_K"]))
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6))
    style(axes[0], time, "D II / total D", "yr")
    style(axes[1], time, "Thermal temperature drop T0 − T [mK]", "yr")
    axes[0].plot(time, fraction, color=BLUE, linewidth=2, label="Saved control")
    axes[0].axhline(eq_fraction, color=GREY, linestyle="--", linewidth=1.3,
                    label="Recorded scalar equilibrium oracle")
    axes[1].plot(time, stored_drop_mK, color=BLUE, linewidth=2,
                 label="Saved thermal state")
    axes[1].plot(time[::10], extent_drop_mK[::10], linestyle="none", marker="o",
                 markerfacecolor="white", markeredgecolor=ORANGE,
                 markeredgewidth=1.3, markersize=4.5,
                 label="Energy prediction from saved D extent")
    axes[1].axhline(eq_drop_mK, color=GREY, linestyle="--", linewidth=1.3,
                    label="Recorded equilibrium temperature")
    for ax in axes:
        ax.set_ylim(bottom=0)
        ax.legend(loc="lower right", fontsize=8.5, framealpha=.94)
    distance = case["receipt"]["checks"]["D_final_equilibrium_distance_over_inventory"]
    fig.suptitle("C02: isolated D/H charge exchange and its energy defect", y=.98,
                 fontsize=14, fontweight="bold")
    fig.text(.5, .875,
             "Fixed-density closed gas: nH = 1 cm⁻³, T0 = 300 K; ground-state D/H exchange only.",
             ha="center", fontsize=10)
    fig.text(.5, .06,
             f"Final D-ion fraction distance to the recorded equilibrium = {distance:.3e}; "
             f"final temperature drop = {stored_drop_mK[-1]:.9f} mK.",
             ha="center", fontsize=9)
    fig.text(.5, .018,
             "The equilibrium reference comes from the saved scalar DB oracle; markers use saved reaction extent. "
             "Finite-time and sampled agreement are not continuum certificates.",
             ha="center", fontsize=8.6)
    fig.subplots_adjust(left=.08, right=.98, top=.78, bottom=.20, wspace=.28)
    save(fig, output, STEMS[1])
    return {"proper_time_end_yr": float(time[-1]),
            "D_II_fraction_initial": float(fraction[0]), "D_II_fraction_final": float(fraction[-1]),
            "recorded_oracle_D_II_fraction": eq_fraction,
            "final_thermal_drop_mK": float(stored_drop_mK[-1]),
            "recorded_oracle_thermal_drop_mK": eq_drop_mK,
            "max_saved_temperature_minus_extent_relation_K": float(np.max(np.abs(stored_drop_mK - extent_drop_mK)) / 1000),
            "D_final_distance_over_inventory_from_case_receipt": distance,
            "oracle_scope": "Scalar equilibrium already recorded by the control run; not recomputed by plotting"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=UNIT / "results")
    parser.add_argument("--output", type=Path, default=UNIT / "figures")
    args = parser.parse_args(argv)
    manifest_path = args.output / "PLOT_CONTROLS_MANIFEST.json"
    products = [args.output / (stem + extension) for stem in STEMS for extension in (".png", ".pdf")]
    if manifest_path.exists() or any(path.exists() for path in products):
        raise FileExistsError("CREATE_ONLY_CONTROL_FIGURE_OUTPUT_ALREADY_EXISTS")
    cases, run, evidence = read_completed(args.results)
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.right": False, "axes.spines.top": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    numerical_display = {"C01": plot_c01(cases, run, args.output),
                         "C02": plot_c02(cases, args.output)}
    manifest = {"schema": "PHYS79_SAVED_CONTROL_PLOTS_V1",
                "status": "RENDERED_PENDING_VISUAL_REVIEW",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "source": {"path": "source/plot_controls.py",
                           "sha256": sha256(Path(__file__).read_bytes())},
                "inputs": evidence, "plotted_samples": 3 * 161,
                "seconds_per_Julian_year": SECONDS_PER_YEAR,
                "axis_zero_policy": "All axes are linear; physical zeros are drawn without floors.",
                "scope": "Isolated fixed-density controls; no cosmological correction or continuum certificate.",
                "control_dependency_identity_changed": False,
                "new_ODE_calls_by_plotting": 0,
                "existing_control_ODEs_from_run_receipt": run["new_ODE_calls_this_invocation"],
                "oracle_recomputed": False, "numerical_display": numerical_display,
                "files": {path.name: {"bytes": path.stat().st_size,
                                      "sha256": sha256(path.read_bytes())} for path in products},
                "visual_inspection": "PENDING"}
    with manifest_path.open("x") as stream:
        json.dump(manifest, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": manifest["status"], "figure_families": 2,
                      "formats": ["png", "pdf"], "new_ODE_calls_by_plotting": 0,
                      "numerical_display": numerical_display}))


if __name__ == "__main__":
    main()
