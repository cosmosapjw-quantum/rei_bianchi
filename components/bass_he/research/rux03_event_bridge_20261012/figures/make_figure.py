#!/usr/bin/env python3
"""Render existing event-bridge results; no native execution or integration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, LogFormatterMathtext, NullLocator
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INPUTS = {
    "probe_validation": ROOT / "event_bridge_02_work/evidence/probe_v2_complete_inputs/VALIDATION.json",
    "initial_native_events": ROOT / "event_bridge_02_work/evidence/probe_v2_complete_inputs/initial_IC/EVENTS.response.json",
    "production_interval": ROOT / "event_bridge_02_work/evidence/production_interval_v2/production_interval.json",
    "production_dataset": ROOT / "event_bridge_02_work/evidence/production_interval_v2/production_dataset.npz",
    "independent_decimal60_oracle": ROOT / "event_bridge_preparation_02/EVENT_REFERENCE_1STAGE.json",
}


def read_json(name):
    return json.loads(INPUTS[name].read_text())


def identity(path):
    payload = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


validation = read_json("probe_validation")
events = np.asarray(read_json("initial_native_events")["values"], dtype=float)
interval = read_json("production_interval")
oracle = read_json("independent_decimal60_oracle")
initial = next(s for s in validation["stages"] if s["label"] == "initial_IC")
checks = {c["id"]: c for c in initial["checks"]}
group_order = ["CI", "RR", "DR", "PI", "RR_kinetic", "DR_kinetic", "PI_heat", "PI_absorbed_energy"]
errors = [float(checks[f"Decimal60/primitive/{g}"]["scaled_max"]) for g in group_order]
tolerance = float(checks["Decimal60/primitive/CI"]["limit"])
primitive_count = sum(len(checks[f"Decimal60/primitive/{g}"]["actual"]) for g in group_order)
with np.load(INPUTS["production_dataset"], allow_pickle=False) as dataset:
    times = dataset["times_s"].copy()
    dataset_shapes = {key: list(dataset[key].shape) for key in dataset.files}
history_times = np.asarray([row["time_s"] for row in interval["history"]])
temperature = np.asarray([row["T_K"] for row in interval["history"]])
if not np.array_equal(times, history_times):
    raise ValueError("The existing JSON history and NPZ output-time coordinates differ.")
delta_temperature = temperature - temperature[0]
rates = {
    "CI": events[0:3].tolist(),
    "RR": events[3:6].tolist(),
    "PI": events[8:11].tolist(),
    "DR": [None, float(events[6] + events[7]), None],
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.linewidth": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "savefig.facecolor": "white",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})
colors = {"CI": "#0072B2", "RR": "#D55E00", "PI": "#009E73", "DR": "#CC79A7"}
fig = plt.figure(figsize=(12.5, 4.8), facecolor="white")
gs = fig.add_gridspec(1, 3, left=0.063, right=0.985, bottom=0.24, top=0.775,
                      wspace=0.48, width_ratios=[1.05, 1.09, 1.0])
ax_rate, ax_error, ax_temp = [fig.add_subplot(gs[0, j]) for j in range(3)]
fig.text(0.063, 0.955, "Source-bound H/He event bridge", fontsize=16, weight="bold", va="top")
fig.text(0.063, 0.893,
         r"Case A escape  ·  $T_0=50{,}000\ \mathrm{K}$  ·  selected warm interval  ·  2,904 photon nodes",
         color="#444444", fontsize=10.5, va="top")

# (a) Gross positive reaction rates; DR is present only on the He I/He II edge.
x = np.arange(3, dtype=float)
width = 0.17
for j, group in enumerate(["CI", "RR", "PI", "DR"]):
    valid = [(k, value) for k, value in enumerate(rates[group]) if value is not None]
    ax_rate.bar([x[k] + (j - 1.5) * width for k, _ in valid],
                [value for _, value in valid], width=width * 0.93,
                color=colors[group], label=group, edgecolor="white", linewidth=0.3, zorder=3)
ax_rate.set_yscale("log")
ax_rate.set_ylim(1e-25, 1.2e-21)
ax_rate.set_xlim(-0.58, 2.56)
ax_rate.set_xticks(x, ["H I / H II", "He I / He II", "He II / He III"])
ax_rate.yaxis.set_major_locator(FixedLocator([1e-25, 1e-24, 1e-23, 1e-22, 1e-21]))
ax_rate.yaxis.set_major_formatter(LogFormatterMathtext())
ax_rate.yaxis.set_minor_locator(NullLocator())
ax_rate.grid(axis="y", color="#E1E4E7", linewidth=0.65, zorder=0)
ax_rate.set_ylabel(r"Gross rate $[\mathrm{cm}^{-3}\,\mathrm{s}^{-1}]$")
ax_rate.set_title("a   Initial reaction rates", loc="left", pad=12, weight="bold")
ax_rate.legend(loc="upper center", bbox_to_anchor=(0.48, 1.015), ncol=4,
               frameon=False, handlelength=0.85, handletextpad=0.35, columnspacing=0.65)

# (b) Report the recorded maximum within each primitive group (22 total values).
y = np.arange(len(group_order))
error_labels = ["CI", "RR", "DR", "PI", "RR kinetic", "DR kinetic", "PI heat", "PI absorbed E"]
for yy, group, value in zip(y, group_order, errors):
    color = colors[group.split("_")[0]]
    ax_error.hlines(yy, 8e-17, value, color=color, linewidth=1.0, alpha=0.7)
    ax_error.plot(value, yy, "o", color=color, markersize=5.2, zorder=4)
ax_error.axvline(tolerance, color="#252525", linestyle=(0, (4, 3)), linewidth=1.05, zorder=2)
ax_error.text(tolerance * 0.76, -0.8, r"$3\times10^{-11}$ limit", ha="right", va="bottom",
              fontsize=9, color="#252525")
ax_error.set_xscale("log")
ax_error.set_xlim(8e-17, 7e-11)
ax_error.set_ylim(7.55, -1.13)
ax_error.set_yticks(y, error_labels)
ax_error.xaxis.set_major_locator(FixedLocator([1e-16, 1e-14, 1e-12, 1e-10]))
ax_error.xaxis.set_major_formatter(LogFormatterMathtext())
ax_error.xaxis.set_minor_locator(NullLocator())
ax_error.tick_params(axis="y", length=0)
ax_error.grid(axis="x", color="#E1E4E7", linewidth=0.65)
ax_error.set_xlabel("Maximum component relative error")
ax_error.set_title("b   Native vs Decimal60", loc="left", pad=12, weight="bold")

# (c) Connect only the 17 saved outputs of the actual newly integrated interval.
ax_temp.plot(times / 1e11, delta_temperature, color="#233B64", linewidth=1.7,
             marker="o", markersize=3.0, markerfacecolor="white", markeredgewidth=0.85)
ax_temp.set_xlim(-0.025, 1.025)
ax_temp.set_ylim(-0.253, 0.018)
ax_temp.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
ax_temp.set_yticks([0.0, -0.05, -0.10, -0.15, -0.20, -0.25])
ax_temp.grid(color="#E1E4E7", linewidth=0.65)
ax_temp.set_xlabel(r"Time $t/(10^{11}\ \mathrm{s})$")
ax_temp.set_ylabel(r"$T(t)-T_0\ [\mathrm{K}]$")
ax_temp.set_title("c   New production interval", loc="left", pad=12, weight="bold")
ax_temp.annotate(f"{delta_temperature[-1]:.4f} K", xy=(1.0, delta_temperature[-1]),
                 xytext=(0.98, -0.109), textcoords="data", ha="right", va="center",
                 color="#233B64", weight="bold", fontsize=10,
                 arrowprops={"arrowstyle": "-", "color": "#233B64", "lw": 0.8})

notes = [
    "CI / PI: ionization; RR / DR: recombination.\nDR sums the two He II → He I channels.",
    "Eight group maxima over 22 primitive values.\nLargest error: " + f"{max(errors):.3e} (limit {tolerance:.0e}).",
    "17 saved outputs from the new integration.\n" + f"Final temperature: {temperature[-1]:.7f} K.",
]
for ax, note in zip((ax_rate, ax_error, ax_temp), notes):
    fig.text(ax.get_position().x0, 0.153, note, va="top", fontsize=8.7,
             color="#444444", linespacing=1.4)
fig.text(0.063, 0.045,
         "Scope: the selected finite discretization. Numerical agreement is not a physical or continuum certificate.",
         fontsize=9, color="#444444")

base = OUT / "EVENT_BRIDGE_SCIENTIFIC_SUMMARY"
outputs = []
for extension in ("png", "svg", "pdf"):
    path = base.with_suffix("." + extension)
    fig.savefig(path, dpi=300)
    outputs.append(identity(path))
plt.close(fig)

figure_data = {
    "task": "HERE_RUX03_EVENT_BRIDGE_02",
    "artifact": "Existing actual result scientific figure",
    "source_files": {name: identity(path) for name, path in INPUTS.items()},
    "figure_files": outputs,
    "generator": identity(Path(__file__)),
    "scientific_scope": {
        "closure": "HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE",
        "scenario": "Selected retained warm extended 10..50000 eV interval, T0=50000 K",
        "photon_nodes": int(oracle["input"]["photon_nodes"]),
        "q_eV_band": oracle["input"]["q_eV_band"],
        "meaning": "Initial native gross events and component agreement with a separately prepared Decimal60 source-formula oracle; temperature is from the actual newly integrated production interval.",
        "limits": "Agreement preserves the selected finite discrete model; it does not establish physical accuracy, continuum convergence, global admission, or a cold-temperature scenario.",
        "production_validation_scope": interval["validation"]["scope"],
        "presentation_execution": "Read existing JSON/NPZ and render only; no Rust execution, integration, oracle replay, or candidate modification.",
        "final_admission_review": "Separate independent review; this figure supplies numerical evidence only.",
    },
    "panels": {
        "a": {
            "quantity": "Initial proper gross event rates",
            "units": "cm^-3 s^-1",
            "edge_order": ["HI<->HII", "HeI<->HeII", "HeII<->HeIII"],
            "direction": {"CI": "lower->upper", "PI": "lower->upper", "RR": "upper->lower", "DR": "HeII->HeI"},
            "rates": rates,
            "DR_uncombined_channels": events[6:8].tolist(),
            "null_semantics": "The selected primitive bundle defines DR only for HeII->HeI; other edges are not plotted.",
        },
        "b": {
            "quantity": "Recorded maximum component relative error within each primitive group",
            "formula": "max_j abs(native_j-oracle_j)/abs(oracle_j), within each displayed group",
            "primitive_count": primitive_count,
            "group_order": group_order,
            "maximum_relative_errors": errors,
            "tolerance": tolerance,
            "comparison_stage": "initial_IC only",
            "precision_scope": oracle["precision_scope"],
        },
        "c": {
            "quantity": "Temperature change of the actual new production integration",
            "time_s": times.tolist(),
            "temperature_K": temperature.tolist(),
            "delta_temperature_K": delta_temperature.tolist(),
            "plotting_rule": "Straight line joins between the 17 saved integration outputs; no fitted trajectory or new solve.",
            "dataset_shapes": dataset_shapes,
        },
    },
    "derived_displayed_numbers": {
        "initial_temperature_K": float(temperature[0]),
        "final_temperature_K": float(temperature[-1]),
        "final_delta_temperature_K": float(delta_temperature[-1]),
        "delta_temperature_label": f"{delta_temperature[-1]:.4f} K",
        "maximum_component_relative_error": max(errors),
        "maximum_error_label": f"{max(errors):.3e}",
        "component_tolerance": tolerance,
        "DR_sum_cm3_s": rates["DR"][1],
        "saved_output_count": len(times),
        "time_start_s": float(times[0]),
        "time_end_s": float(times[-1]),
    },
    "additional_context_not_shown_as_physical_certificate": {
        "production_status": interval["validation"]["status"],
        "probe_status": validation["status"],
        "reported_preserved_solution_state_scaled_max": interval["validation"]["state_scaled_max"],
        "reported_preserved_observable_max_error": max(interval["validation"]["observable_errors"].values()),
        "relative_temperature_change": float(delta_temperature[-1] / temperature[0]),
        "tolerance_over_maximum_component_error": tolerance / max(errors),
    },
}
data_path = OUT / "FIGURE_DATA.json"
data_path.write_text(json.dumps(figure_data, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"figure_data": identity(data_path), "figures": outputs,
                  "displayed_numbers": figure_data["derived_displayed_numbers"]}, indent=2))
