"""Present the preserved native coupled-source JSON without scientific imports.

No source, network, donor, integration or quadrature code is called here.
All plotted measurements and validation residuals come from the raw result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def number(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"Nonfinite or nonnumeric raw {label}")
    return float(value)


def render(input_path: Path, output_prefix: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw_bytes = input_path.read_bytes()
    data = json.loads(raw_bytes)
    if data["status"] != "PASS_SCOPED_IF_EXECUTED" or len(data["source"]) != 25 or len(data["physical_density_source"]) != 25:
        raise ValueError("Unexpected raw selected coupled-source result")
    checks = {entry["name"]: entry for entry in data["checks"]}
    expected = ("thermal_count_source", "energy_total", "energy_jvp",
                "aggregate_source_FD_counts", "clock_FD_counts")
    if any(key not in checks or "residual" not in checks[key] for key in expected):
        raise ValueError("Selected validation residuals absent from raw result")
    event = number(data["physical_density_source"][21], "electron birth density")
    power = number(data["physical_density_source"][22], "primary power density")
    lo, hi = (number(v, "pressure interval") for v in data["pressure_interval_W_m3"])
    proper = number(data["thermal"]["correct_logT_source_s"], "correct thermal rate")
    bad = number(data["thermal"]["bad_allthermal_logT_s"], "all-thermal comparator")
    source_event = number(data["source"][21], "nonthermal electron source")
    if not (event > 0 and power > 0 and 0 < lo <= hi and proper == 0 and bad < 0 and source_event > 0):
        raise ValueError("Unexpected signs in the preserved source result")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.3))
    blue, teal, orange = "#245b84", "#238878", "#c3713e"
    ax = axes[0, 0]
    ax.barh([2, 1], [event, event], color=[blue, teal], height=.55)
    ax.scatter([0], [0], color=orange, s=60, marker="|", linewidths=3)
    ax.set_yticks([2, 1, 0], ["Total electron birth", "Nonthermal primary birth", "Thermal electron birth"])
    ax.set_xlabel(r"Number source  m$^{-3}$ s$^{-1}$")
    ax.set_title("One electron counted once")
    ax.set_xlim(0, 1.27 * event)
    ax.text(.98 * event, 1.5, f"{event:.4g}", ha="right", va="center", fontsize=8)
    ax.text(.025 * event, 0, "0", va="center", fontsize=8)

    ax = axes[0, 1]
    ax.barh([1], [power], color=teal, height=.34, label="Primary kinetic power")
    ax.barh([0], [hi - lo], left=[lo], color=blue, height=.34,
            label="Isotropic pressure-source interval")
    ax.plot([lo, lo], [-0.21, .21], color=blue, lw=1.4)
    ax.set_yticks([1, 0], ["Primary source", "Pressure interval"])
    ax.set_xlabel(r"J m$^{-3}$ s$^{-1}$ = W m$^{-3}$")
    ax.set_title("Matter source and diagnostic bound")
    ax.set_xlim(0, 1.25 * power)
    ax.text(.98 * power, 1, f"{power:.4g}", ha="right", va="center", color="white", fontsize=8)
    ax.text(hi + .035 * power, 0, f"[{lo:.3g}, {hi:.3g}]", ha="left", va="center", fontsize=8)

    ax = axes[1, 0]
    ax.scatter([proper, bad], [1, 0], s=90, color=[teal, orange], zorder=3)
    ax.axvline(0, color="#7c8690", lw=1)
    ax.set_yticks([1, 0], ["Correct pre-assimilation", "Inconsistent all-thermal count"])
    ax.set_xlabel(r"Source contribution to $d\log T/dt$  s$^{-1}$")
    ax.set_title("Temperature bookkeeping at the actual snapshot")
    ax.set_xlim(1.18 * bad, -.18 * bad)
    ax.annotate(f"{bad:.4g} s⁻¹", (bad, 0), xytext=(0, 10), textcoords="offset points",
                ha="left", fontsize=8)
    ax.annotate("0", (0, 1), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=8)

    ax = axes[1, 1]
    vals = [number(checks[k]["residual"], k) for k in expected]
    labels = ["Thermal count", "Energy", "Energy JVP", "Source JVP FD", "Clock JVP FD"]
    display = [max(v, 1e-20) for v in vals]
    ax.barh(range(5), display, color=[blue, teal, teal, orange, orange], height=.58)
    ax.set_yticks(range(5), labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(1e-20, max(1e-12, 20 * max(display)))
    ax.set_xlabel("Stored normalized residual (zero shown at plotting floor)")
    ax.set_title("Selected raw validation residuals")
    for i, value in enumerate(vals):
        ax.text(max(display[i] * 1.4, 1.4e-20), i, f"{value:.2g}", va="center", fontsize=7.5)

    for ax in axes.flat:
        ax.grid(axis="x", alpha=.17)
        ax.set_axisbelow(True)
    fig.suptitle("Native PW19 He II source → selected coupled particle and energy boundary",
                 fontsize=14, weight="bold", y=.985)
    fig.text(.5, .941, "Saved z = 2.479 donor snapshot · proper-second source · newly born primary electrons stay nonthermal",
             ha="center", color="#465363")
    fig.text(.5, .027, "25 coordinates: 21 native species + nonthermal count, kinetic energy, external transfer and log T.\n"
             "Instantaneous pre-assimilation only; pressure is a bound, not evolved stress. History and full pilot remain open.",
             ha="center", va="bottom", color="#465363", fontsize=8)
    fig.subplots_adjust(top=.87, bottom=.15, left=.22, right=.97, hspace=.51, wspace=.37)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("png", "pdf", "svg"):
        target = output_prefix.with_suffix("." + suffix)
        fig.savefig(target, dpi=170, facecolor="white",
                    metadata={"Creator": "REI raw coupled-source presentation"} if suffix == "pdf" else None)
        payload = target.read_bytes()
        outputs[suffix] = {"path": str(target), "bytes": len(payload),
                           "sha256": hashlib.sha256(payload).hexdigest()}
    plt.close(fig)
    return {"raw_result": str(input_path), "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "presentation_only": True, "scientific_evaluations": 0, "outputs": outputs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.raw_result, args.output_prefix), indent=2))
