"""Render a completed native PW19 result without invoking any science provider.

Input is the unmodified JSON object returned by native_pw19_moments.calculate().
All plotted coordinates and signed defects are read from that object; this
presentation step does not integrate, interpolate, refit, or derive moments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


BANDS = ((54.42, 204.42), (204.42, 2000.0), (2000.0, 50000.0))
MOMENTS = (
    ("Gamma_s", r"Ionization rate $\Gamma$", r"s$^{-1}$ per He II"),
    ("K_eV_s", r"Primary kinetic supply $K$", r"eV s$^{-1}$ per He II"),
    ("A_eV_s", r"Absorbed photon energy $A$", r"eV s$^{-1}$ per He II"),
)


def _positive(row: dict, key: str) -> float:
    value = row[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"Expected positive finite raw result: {key}")
    return value


def _raw_result(data: dict) -> tuple[list[dict], dict, dict, dict, dict]:
    source = data["source"]
    if source["redshift"] != 2.479 or source["frame"] != "isotropic_bath_rest" or source["time_basis"] != "proper_second":
        raise ValueError("Expected exact PW19 z=2.479 bath-rest, proper-second output")
    parts = data["partition_moments"]
    if len(parts) != 3 or any(tuple(p["band_eV"]) != band for p, band in zip(parts, BANDS)):
        raise ValueError("Expected the three frozen, ordered atomic support partitions")
    late = data["late_band_moments"]
    lumina = data["lumina_late"]
    defects = data["template_signed_relative_defect"]
    tails = data["radiation_exposure_outside_atomic"]
    if tails["below_threshold"]["atomic_status"] != "physically_zero_below_threshold":
        raise ValueError("Below-threshold status is missing")
    if tails["above_atomic_domain"]["atomic_status"] != "unknown_above_50000_eV" or tails["above_atomic_domain"]["HeII_primary_Gamma_s"] is not None:
        raise ValueError("Above-domain HeII atomic rate must be unknown, not zero")
    for key, _, _ in MOMENTS:
        _positive(late, key)
        _positive(lumina, key)
        for part in parts:
            _positive(part, key)
    for row in (*parts, tails["below_threshold"], tails["above_atomic_domain"]):
        _positive(row, "Phi_cm2_s") if "Phi_cm2_s" in row else _positive(row, "number_cm2_s")
        _positive(row, "Psi_eV_cm2_s") if "Psi_eV_cm2_s" in row else _positive(row, "energy_eV_cm2_s")
    for key in ("delta_Gamma", "delta_K", "delta_abs"):
        value = defects[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Invalid stored signed template defect: " + key)
    return parts, late, lumina, defects, tails


def render(input_path: Path, output_prefix: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw_bytes = input_path.read_bytes()
    data = json.loads(raw_bytes)
    parts, late, lumina, defects, tails = _raw_result(data)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, axes = plt.subplots(4, 2, figsize=(13.0, 13.2))
    native_color, template_color = "#185b88", "#c47337"
    support_colors = ("#26877c", "#7b639f", "#9b6b3f")
    support_labels = ("54.42–204.42 eV", "204.42–2,000 eV", "2,000–50,000 eV")
    defect_keys = ("delta_Gamma", "delta_K", "delta_abs")

    for row_index, ((key, title, unit), defect_key) in enumerate(zip(MOMENTS, defect_keys)):
        ax, support_ax = axes[row_index]
        ax.scatter([0, 1], [late[key], lumina[key]], color=[native_color, template_color], s=105, zorder=3)
        ax.set_xticks([0, 1], ["Native PW19", "Frozen late Lumina"])
        ax.set_yscale("log")
        ax.set_ylabel(unit)
        ax.set_title(title)
        ax.text(.03, .97, f"Stored signed defect: {defects[defect_key]:+.4g}",
                transform=ax.transAxes, va="top", fontsize=8,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85})

        support_ax.scatter(range(3), [part[key] for part in parts], color=support_colors, s=105, marker="s", zorder=3)
        support_ax.set_yscale("log")
        support_ax.set_xticks(range(3), support_labels, rotation=14, ha="right")
        support_ax.set_ylabel(unit)
        support_ax.set_title("Native atomic support partitions: " + title.split(" $")[0])
        for panel in (ax, support_ax):
            panel.grid(axis="y", alpha=.18)
            panel.set_axisbelow(True)

    below, above = tails["below_threshold"], tails["above_atomic_domain"]
    exposure_rows = (below, *parts, above)
    exposure_labels = ("Below He II threshold", *support_labels, "Above 50 keV atomic domain")
    exposure_colors = ("#a3abb2", *support_colors, "#a3abb2")
    for ax, key, fallback, title, unit in (
        (axes[3, 0], "Phi_cm2_s", "number_cm2_s", "Incident photon exposure $\\Phi$", r"cm$^{-2}$ s$^{-1}$"),
        (axes[3, 1], "Psi_eV_cm2_s", "energy_eV_cm2_s", "Incident energy exposure $\\Psi$", r"eV cm$^{-2}$ s$^{-1}$"),
    ):
        ax.scatter([r[key] if key in r else r[fallback] for r in exposure_rows], range(5), color=exposure_colors, s=105, marker="D", zorder=3)
        ax.set_xscale("log")
        ax.set_yticks(range(5), exposure_labels)
        ax.invert_yaxis()
        ax.set_xlabel(unit)
        ax.set_title(title)
        ax.grid(axis="x", alpha=.18)
        ax.set_axisbelow(True)

    fig.suptitle("PW19 native He II source vs frozen late Lumina moment", weight="bold", fontsize=16, y=.985)
    fig.text(.5, .959, "Exact source node z = 2.479 · same native late-band photon exposure · proper-second, bath-rest-frame rates",
             ha="center", color="#485260", fontsize=9.5)
    fig.text(.5, .03, "Below 54.42 eV: He II ionization is physically zero. Above 50 keV: radiation exposure known, atomic rate unknown.\n"
             "Local spectral-operator comparison only; no gas history, heating deposition, Lumina cell, or observed reionization curve.",
             ha="center", va="bottom", fontsize=8.5, color="#485260")
    fig.subplots_adjust(top=.925, bottom=.105, left=.17, right=.97, hspace=.65, wspace=.34)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("png", "pdf", "svg"):
        target = output_prefix.with_suffix("." + suffix)
        fig.savefig(target, dpi=160, facecolor="white",
                    metadata={"Creator": "PW19 native/Lumina raw-result renderer"} if suffix == "pdf" else None)
        payload = target.read_bytes()
        outputs[suffix] = {"path": str(target), "bytes": len(payload),
                           "sha256": hashlib.sha256(payload).hexdigest()}
    plt.close(fig)
    return {"raw_result": str(input_path), "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "status": "raw_native_local_operator_comparison", "presentation_only": True,
            "science_evaluations": 0, "outputs": outputs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_result", type=Path, help="Unmodified calculate() result JSON")
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.raw_result, args.output_prefix), indent=2))
