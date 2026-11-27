"""Create PHYS83 figures from saved CSVs only; never evaluate science kernels.

Inputs are rate_grid.csv, steady_grid.csv, and transient_grid.csv. All output
files are create-only. A different output directory is required for a later
figure revision. No matched_ce/frozen_star imports, quadratures, rate callbacks,
population solves, or historical identity replay occur in this script.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


UNIT = Path(__file__).resolve().parents[1]
FIGURE_STEMS = (
    "01_finite_matched_rates",
    "02_steady_coronal_suppression",
    "03_transient_energy_accounting",
)
INPUT_COLUMNS = {
    "rate_grid.csv": (
        "upper_level", "temperature_K", "q_up_cm3_s", "q_down_cm3_s",
    ),
    "steady_grid.csv": (
        "temperature_K", "electron_density_cm3", "exact_to_coronal_2s",
        "exact_to_coronal_2p", "critical_density_2s_cm3", "critical_density_2p_cm3",
    ),
    "transient_grid.csv": (
        "temperature_K", "electron_density_cm3", "time_s", "atomic_excitation_eV",
        "escaped_radiation_eV", "heat_withdrawal_eV", "thermal_change_eV",
        "normalized_raw_energy_residual",
    ),
}
EXPECTED_ROWS = {"rate_grid.csv": 132, "steady_grid.csv": 324, "transient_grid.csv": 732}


def _identity(path: Path) -> dict:
    blob = path.read_bytes()
    return {"path": str(path.resolve()), "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}


def _read_csv(path: Path, required: tuple[str, ...], expected_rows: int) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or not set(required).issubset(reader.fieldnames):
            missing = sorted(set(required).difference(reader.fieldnames or []))
            raise ValueError(f"PLOT_INPUT_COLUMNS_MISSING:{path.name}:{missing}")
        rows = list(reader)
    if len(rows) != expected_rows:
        raise ValueError(f"PLOT_INPUT_ROW_COUNT:{path.name}:{len(rows)}!={expected_rows}")
    for row in rows:
        for name in required:
            if name == "upper_level":
                if row[name] not in ("2S", "2P"):
                    raise ValueError("PLOT_UNKNOWN_UPPER_LEVEL")
                continue
            number = float(row[name])
            if not math.isfinite(number):
                raise ValueError(f"PLOT_NONFINITE_INPUT:{path.name}:{name}")
            row[name] = number
    return rows


def _group(rows: list[dict], keys: tuple[str, ...], sort_key: str) -> dict[tuple, list[dict]]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    for key, values in groups.items():
        values.sort(key=lambda row: row[sort_key])
        coordinates = [row[sort_key] for row in values]
        if len(set(coordinates)) != len(coordinates):
            raise ValueError(f"PLOT_DUPLICATE_SAVED_COORDINATE:{keys}:{key}")
    return groups


def _validate_saved_tables(rate_rows, steady_rows, transient_rows) -> dict:
    """Check plot inputs and record sampled metadata; no scientific re-evaluation."""
    rate_groups = _group(rate_rows, ("upper_level",), "temperature_K")
    if set(rate_groups) != {("2S",), ("2P",)} or any(len(rows) != 66 for rows in rate_groups.values()):
        raise ValueError("PLOT_RATE_GRID_NOT_TWO_BY_66")
    rate_temperatures = [[row["temperature_K"] for row in rate_groups[(level,)]] for level in ("2S", "2P")]
    if rate_temperatures[0] != rate_temperatures[1] or rate_temperatures[0][0] != 255.0 or rate_temperatures[0][-1] != 50000.0:
        raise ValueError("PLOT_RATE_T_GRID_MISMATCH")
    if any(row["q_up_cm3_s"] <= 0 or row["q_down_cm3_s"] <= 0 for row in rate_rows):
        raise ValueError("PLOT_LOG_RATE_REQUIRES_POSITIVE_SAVED_VALUES")

    steady_groups = _group(steady_rows, ("temperature_K",), "electron_density_cm3")
    expected_steady_t = {5000.0, 10000.0, 25370.66308424773, 50000.0}
    if {key[0] for key in steady_groups} != expected_steady_t or any(len(rows) != 81 for rows in steady_groups.values()):
        raise ValueError("PLOT_STEADY_GRID_NOT_FOUR_BY_81")
    for values in steady_groups.values():
        if any(row["electron_density_cm3"] <= 0 for row in values):
            raise ValueError("PLOT_LOG_DENSITY_REQUIRES_POSITIVE_SAVED_VALUES")
        for upper in ("2s", "2p"):
            ncrit = [row[f"critical_density_{upper}_cm3"] for row in values]
            if min(ncrit) <= 0 or any(value != ncrit[0] for value in ncrit):
                raise ValueError("PLOT_CRITICAL_DENSITY_NOT_CONSTANT_AT_FIXED_T")
            ratios = [row[f"exact_to_coronal_{upper}"] for row in values]
            if min(ratios) <= 0 or max(ratios) > 1 + 2e-12:
                raise ValueError("PLOT_INVALID_SAVED_SUPPRESSION_RATIO")

    transient_groups = _group(transient_rows, ("temperature_K", "electron_density_cm3"), "time_s")
    expected_profiles = {(t, ne) for t in (10000.0, 25370.66308424773) for ne in (1.0, 1e8, 1e12)}
    if set(transient_groups) != expected_profiles or any(len(rows) != 122 for rows in transient_groups.values()):
        raise ValueError("PLOT_TRANSIENT_GRID_NOT_SIX_BY_122")
    energy_names = ("atomic_excitation_eV", "escaped_radiation_eV", "heat_withdrawal_eV")
    for values in transient_groups.values():
        if values[0]["time_s"] != 0.0 or any(values[0][name] != 0.0 for name in energy_names):
            raise ValueError("PLOT_INITIAL_GROUND_ENERGY_ROW_MISMATCH")
        if any(row["time_s"] <= 0.0 for row in values[1:]):
            raise ValueError("PLOT_TRANSIENT_POSITIVE_TIMES_REQUIRED")
        if any(row[name] <= 0.0 for row in values[1:] for name in energy_names):
            raise ValueError("PLOT_LOG_ENERGY_REQUIRES_POSITIVE_SAVED_VALUES")
        if any(row["thermal_change_eV"] != -row["heat_withdrawal_eV"] for row in values):
            raise ValueError("PLOT_THERMAL_SIGN_CONVENTION_MISMATCH")
    return {
        "rate_rows": len(rate_rows),
        "steady_rows": len(steady_rows),
        "transient_rows": len(transient_rows),
        "transient_profiles": len(transient_groups),
        "zero_time_rows_checked_and_omitted_from_log_axes": len(transient_groups),
        "max_abs_saved_normalized_raw_energy_residual": max(abs(row["normalized_raw_energy_residual"]) for row in transient_rows),
        "scope": "stored-array plot validation; not an independent scientific or continuum certificate",
    }


def _style_axes(ax):
    ax.grid(which="major", color="#d8dce3", linewidth=0.6, alpha=0.8)
    ax.grid(which="minor", color="#edf0f4", linewidth=0.35, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(which="both", labelsize=10)


def _rates_figure(plt, rows):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    groups = _group(rows, ("upper_level",), "temperature_K")
    colors = {"2S": "#1870a8", "2P": "#c65b18"}
    for ax, field, title in zip(axes, ("q_up_cm3_s", "q_down_cm3_s"), ("Excitation: 1s to upper state", "Deexcitation: upper state to 1s")):
        for upper in ("2S", "2P"):
            values = groups[(upper,)]
            ax.loglog([r["temperature_K"] for r in values], [r[field] for r in values],
                      color=colors[upper], linewidth=2.0, label=upper.lower())
        ax.set_title(title, fontsize=12, pad=10)
        ax.set_xlabel(r"Prescribed electron temperature $T$ [K]", fontsize=11)
        ax.set_ylabel(r"Finite rate coefficient [cm$^3$ s$^{-1}$]", fontsize=11)
        ax.set_xlim(255.0, 50000.0)
        ax.legend(frameon=False, fontsize=11, loc="best")
        _style_axes(ax)
    fig.suptitle("H I matched finite CCC rates", fontsize=17, y=0.97)
    fig.text(0.5, 0.025,
             "Source-native gap 10.20435 eV; W piecewise linear on the fixed finite source interval.\n"
             "Paired excitation/deexcitation share one Maxwell moment. Curves show the adopted operator.",
             ha="center", va="bottom", fontsize=9, color="#434c59")
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.20, top=0.84, wspace=0.30)
    return fig


def _steady_figure(plt, rows):
    fig, axes = plt.subplots(1, 2, figsize=(14.1, 6.1))
    groups = _group(rows, ("temperature_K",), "electron_density_cm3")
    colors = ("#1675a9", "#d47217", "#20835f", "#974ea0")
    for ax, upper in zip(axes, ("2s", "2p")):
        for ((temperature,), values), color in zip(sorted(groups.items()), colors):
            ncrit = values[0][f"critical_density_{upper}_cm3"]
            label = f"T = {temperature:,.0f} K;  ncrit = {ncrit:.3g} cm^-3"
            ax.loglog([r["electron_density_cm3"] for r in values],
                      [r[f"exact_to_coronal_{upper}"] for r in values],
                      color=color, linewidth=1.9, label=label)
            ax.axvline(ncrit, color=color, linewidth=1.0, linestyle=":", alpha=0.8)
        ax.axhline(1.0, color="#4f5967", linewidth=0.9, linestyle="--")
        ax.set_title(f"{upper}: radiative emission / ground-reservoir coronal reference", fontsize=11, pad=10)
        ax.set_xlabel(r"Prescribed electron density $n_e$ [cm$^{-3}$]", fontsize=11)
        ax.set_ylabel("Exact stationary / coronal emission", fontsize=11)
        ax.set_xlim(1e-8, 1e18)
        ax.set_ylim(top=1.5)
        ax.legend(frameon=False, fontsize=8.7, loc="lower left")
        _style_axes(ax)
    fig.suptitle("Radiative suppression in the finite three-level star", fontsize=16, y=0.97)
    fig.text(0.5, 0.027,
             "Dotted vertical lines: same-channel ncrit = A / qdown. Fixed T, optically thin spontaneous escape.\n"
             "High-density values diagnose the restricted 1s / 2s / 2p star; mixing, higher levels and opacity remain separate inputs.",
             ha="center", va="bottom", fontsize=9, color="#434c59")
    fig.subplots_adjust(left=0.075, right=0.98, bottom=0.19, top=0.84, wspace=0.27)
    return fig


def _transient_figure(plt, rows):
    fig, axes = plt.subplots(2, 3, figsize=(15.3, 8.6), sharex=True)
    groups = _group(rows, ("temperature_K", "electron_density_cm3"), "time_s")
    temperatures = sorted({key[0] for key in groups})
    densities = sorted({key[1] for key in groups})
    styles = (
        ("atomic_excitation_eV", "Atomic excitation store", "#1870a8", "-"),
        ("escaped_radiation_eV", "Escaped radiation", "#d07b21", "-"),
        ("heat_withdrawal_eV", "Thermal withdrawal", "#202934", "--"),
    )
    for i, temperature in enumerate(temperatures):
        for j, density in enumerate(densities):
            ax = axes[i, j]
            values = groups[(temperature, density)]
            positive_times = values[1:]
            for field, label, color, line_style in styles:
                ax.loglog([r["time_s"] for r in positive_times], [r[field] for r in positive_times],
                          color=color, linestyle=line_style, linewidth=1.65, label=label)
            max_residual = max(abs(r["normalized_raw_energy_residual"]) for r in values)
            ax.set_title(f"T = {temperature:,.0f} K;  ne = {density:.0e} cm^-3", fontsize=10.5, pad=9)
            ax.text(0.025, 0.04, f"Saved max normalized residual: {max_residual:.2e}",
                    transform=ax.transAxes, fontsize=7.6, color="#4b5563")
            ax.set_xlim(1e-12, 1e3)
            if i == 1:
                ax.set_xlabel("Local proper time [s]", fontsize=10.5)
            if j == 0:
                ax.set_ylabel("Energy per initial H I atom [eV]", fontsize=10.5)
            _style_axes(ax)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.935),
               ncol=3, frameon=False, fontsize=11)
    fig.suptitle("Atomic buildup, escaped radiation and thermal exchange", fontsize=17, y=0.985)
    fig.text(0.5, 0.022,
             "Ground-state start; prescribed T and ne. Thermal withdrawal = atomic store + escaped radiation.\n"
             "A two-photon decay carries total energy Delta, with two photons per event; the separate M1 branch carries one photon.\n"
             "Six saved zero-time rows are checked and omitted from logarithmic axes. Residuals describe the sampled numerical records.",
             ha="center", va="bottom", fontsize=9, color="#434c59")
    fig.subplots_adjust(left=0.068, right=0.985, bottom=0.16, top=0.85, hspace=0.27, wspace=0.26)
    return fig


def _save_pair(fig, output_directory: Path, stem: str) -> list[dict]:
    identities = []
    for extension in ("png", "pdf"):
        path = output_directory / f"{stem}.{extension}"
        metadata = ({"Software": "PHYS83 saved-data plotter"} if extension == "png"
                    else {"Creator": "PHYS83 saved-data plotter", "CreationDate": None, "ModDate": None})
        with path.open("xb") as stream:
            fig.savefig(stream, format=extension, dpi=180, facecolor="white", metadata=metadata)
        identities.append(_identity(path))
    return identities


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-directory", type=Path, default=UNIT / "results")
    parser.add_argument("--output-directory", type=Path, default=UNIT / "figures")
    args = parser.parse_args(argv)
    outputs = [args.output_directory / f"{stem}.{ext}" for stem in FIGURE_STEMS for ext in ("png", "pdf")]
    receipt_path = args.output_directory / "PLOT_RUN_RECEIPT.json"
    existing = [str(path) for path in outputs + [receipt_path] if path.exists()]
    if existing:
        raise FileExistsError(f"CREATE_ONLY_PLOT_OUTPUT_EXISTS:{existing}")
    inputs = {name: _identity(args.input_directory / name) for name in INPUT_COLUMNS}
    tables = {name: _read_csv(args.input_directory / name, columns, EXPECTED_ROWS[name])
              for name, columns in INPUT_COLUMNS.items()}
    validation = _validate_saved_tables(tables["rate_grid.csv"], tables["steady_grid.csv"], tables["transient_grid.csv"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.unicode_minus": True, "pdf.fonttype": 42,
                         "savefig.bbox": None})
    args.output_directory.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "PHYS83_SAVED_DATA_PLOT_RECEIPT_V1",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "script": _identity(Path(__file__)),
        "inputs": inputs,
        "saved_input_validation": validation,
        "matplotlib_version": matplotlib.__version__,
        "scientific_kernel_imports": 0,
        "rate_callbacks": 0,
        "population_solves": 0,
        "new_scientific_runs": 0,
        "historical_replays": 0,
        "outputs": [],
        "visual_audit": "PENDING",
    }
    try:
        constructors = (_rates_figure, _steady_figure, _transient_figure)
        filenames = ("rate_grid.csv", "steady_grid.csv", "transient_grid.csv")
        for constructor, filename, stem in zip(constructors, filenames, FIGURE_STEMS):
            fig = constructor(plt, tables[filename])
            receipt["outputs"].extend(_save_pair(fig, args.output_directory, stem))
            plt.close(fig)
        receipt["status"] = "PLOTS_CREATED_AWAITING_VISUAL_AUDIT"
        receipt["completed_utc"] = datetime.now(timezone.utc).isoformat()
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
    except Exception as exc:
        receipt["status"] = "FAILED_PARTIAL_OUTPUTS_PRESERVED"
        receipt["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        receipt["completed_utc"] = datetime.now(timezone.utc).isoformat()
        if not receipt_path.exists():
            with receipt_path.open("x", encoding="utf-8") as stream:
                json.dump(receipt, stream, indent=2)
                stream.write("\n")
        raise
    print(json.dumps({"status": receipt["status"], "outputs": len(receipt["outputs"]),
                      "receipt": str(receipt_path.resolve()), "scientific_runs": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
