"""Plot saved HE32 pilot results; never integrate or modify scientific inputs.

CLI: python src/plot_pilot.py --catalog results/CATALOG.json --out results/figures
The import API is render(catalog_path, out_dir).  Every plotted trajectory is an
actual saved case.  Parameter maps display discrete cells without interpolation.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "he32_matplotlib_cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np


SECONDS_PER_GYR = 365.25 * 86400.0 * 1e9
COLORS = ("#222222", "#0072B2", "#D55E00", "#009E73",
          "#CC79A7", "#56B4E9", "#E69F00", "#6F4C9B")
REQUIRED_OBSERVABLES = (
    "Sigma_F", "signed_Sigma", "P_m", "P_r", "Pi_m", "Pi_r", "P_gamma",
    "P_nu", "Pi_total", "z", "elapsed_s", "H_per_s", "ne_cm3", "tau_T", "b",
)
FIGURE_NAMES = (
    "parameter_sweep", "shear_planes", "time_evolution_z20_z2",
    "time_evolution_elapsed_gyr", "species_ionization", "stress_budget",
)


def _plain(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Not a JSON value: {type(value).__name__}")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(path: Path, base: Path) -> dict:
    return {"path": str(path.relative_to(base)), "bytes": path.stat().st_size,
            "sha256": _sha(path)}


def _atomic_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=_plain) + "\n")
    temporary.replace(path)


def _relative_input(base: Path, name: str) -> Path:
    path = (base / name).resolve()
    path.relative_to(base)
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


@dataclass
class Case:
    case_id: str
    config: dict
    path: Path
    receipt: Path | None
    x: np.ndarray
    observations: np.ndarray
    names: tuple[str, ...]

    def column(self, name: str) -> np.ndarray:
        return self.observations[:, self.names.index(name)]

    @property
    def parameters(self) -> tuple[float, float, float]:
        return tuple(float(self.config[k]) for k in ("Sigma_F", "P_m", "P_r"))

    def extra(self, *names: str) -> tuple[np.ndarray, ...]:
        with np.load(self.path, allow_pickle=False) as saved:
            return tuple(np.asarray(saved[name]) for name in names)


def _load(catalog_path: Path) -> tuple[dict, list[Case], list[dict]]:
    catalog = json.loads(catalog_path.read_text())
    base = catalog_path.parent
    cases, skipped, ids = [], [], set()
    for item in catalog["cases"]:
        if item.get("status") != "completed":
            skipped.append({"case_id": item.get("case_id"), "status": item.get("status")})
            continue
        case_id = str(item["case_id"])
        if case_id in ids:
            raise ValueError(f"Duplicate completed case id: {case_id}")
        ids.add(case_id)
        path = _relative_input(base, item["npz"])
        receipt = _relative_input(base, item["receipt"]) if item.get("receipt") else None
        with np.load(path, allow_pickle=False) as saved:
            x = np.asarray(saved["x"], dtype=float)
            obs = np.asarray(saved["observables"], dtype=float)
            names = tuple(str(v) for v in saved["observable_names"].tolist())
        if len(set(names)) != len(names):
            raise ValueError(f"Duplicate observable name in {case_id}")
        missing = sorted(set(REQUIRED_OBSERVABLES) - set(names))
        if missing:
            raise ValueError(f"{case_id}: missing observables {missing}")
        if x.ndim != 1 or len(x) < 2 or obs.shape != (len(x), len(names)):
            raise ValueError(f"{case_id}: incompatible x/observable shapes")
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(obs)):
            raise ValueError(f"{case_id}: nonfinite saved data")
        if not np.all(np.diff(x) > 0):
            raise ValueError(f"{case_id}: stored time coordinate is not increasing")
        case = Case(case_id, item["config"], path, receipt, x, obs, names)
        if not all(math.isfinite(v) for v in case.parameters):
            raise ValueError(f"{case_id}: nonfinite initial parameter")
        if np.any(np.diff(case.column("z")) > 1e-11):
            raise ValueError(f"{case_id}: redshift coordinate increases")
        if np.any(np.diff(case.column("elapsed_s")) < 0):
            raise ValueError(f"{case_id}: elapsed time decreases")
        cases.append(case)
    if not cases:
        raise ValueError("Catalog has no completed saved cases to plot")
    return catalog, cases, skipped


def _number(value: float) -> str:
    if value == 0:
        return "0"
    if .01 <= abs(value) < 10:
        return f"{value:g}"
    return f"{value:.2g}"


def _parameter_label(case: Case) -> str:
    s, m, r = case.parameters
    return rf"$\Sigma_0={_number(s)},\ P_{{m0}}={_number(m)},\ P_{{r0}}={_number(r)}$"


def _closest(cases: list[Case], targets: list[tuple[float, float, float]]) -> list[Case]:
    """Select actual saved cases; do not synthesize or interpolate trajectories."""
    selected, used = [], set()
    scale = np.asarray([1e-3, 1e-4, 1e-4])
    for target in targets:
        available = [case for case in cases if case.case_id not in used]
        if not available:
            break
        target_value = np.arcsinh(np.asarray(target) / scale)
        case = min(available, key=lambda c: float(np.sum(
            (np.arcsinh(np.asarray(c.parameters) / scale) - target_value) ** 2)))
        selected.append(case)
        used.add(case.case_id)
    return selected


def _style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.labelsize": 11, "axes.titlesize": 11,
        "figure.titlesize": 16, "legend.fontsize": 9,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": .17, "grid.linewidth": .6,
        "savefig.facecolor": "white", "svg.hashsalt": "he32-saved-pilot-v1",
    })


def _save(fig, out: Path, name: str) -> list[dict]:
    files = []
    for extension in ("png", "svg"):
        path = out / f"{name}.{extension}"
        temporary = path.with_name(path.name + ".tmp")
        metadata = {"Creator": "HE32 saved-output plot analyzer", "Date": None} if extension == "svg" else {
            "Software": "HE32 saved-output plot analyzer"}
        fig.savefig(temporary, format=extension, dpi=180, bbox_inches="tight", metadata=metadata)
        temporary.replace(path)
        files.append(_file_record(path, out))
    plt.close(fig)
    return files


def _nonnegative_scale(ax, axis: str, values, threshold: float) -> None:
    value = np.asarray(values)
    top = max(float(np.max(value)), threshold)
    getattr(ax, f"set_{axis}scale")("symlog", linthresh=threshold, linscale=1., base=10)
    getattr(ax, f"set_{axis}lim")(0., top * 1.17)
    # Include an explicit zero tick even when the logarithmic range is wide.
    minimum_power = int(math.floor(math.log10(threshold)))
    maximum_power = int(math.ceil(math.log10(top)))
    step = max(1, math.ceil((maximum_power - minimum_power + 1) / 5))
    ticks = [0.] + [10. ** exponent for exponent in range(minimum_power, maximum_power + 1, step)
                   if 10. ** exponent <= top * 1.17]
    getattr(ax, f"set_{axis}ticks")(ticks)


def _write_endpoints(cases: list[Case], out: Path) -> dict:
    names = sorted(set.intersection(*(set(case.names) for case in cases)))
    fields = ["case_id", "npz", "Sigma_F_config", "P_m_config", "P_r_config", "ellmax", "samples"]
    fields += [f"{edge}_{name}" for edge in ("initial", "final") for name in names]
    fields += [f"{extreme}_{name}" for name in ("Sigma_F", "Pi_m", "Pi_r", "Pi_total", "ne_cm3", "tau_T")
               for extreme in ("minimum", "maximum")]
    path = out / "endpoints.csv"
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            s, m, r = case.parameters
            row = {"case_id": case.case_id, "npz": str(case.path.relative_to(case.path.parent.parent)),
                   "Sigma_F_config": s, "P_m_config": m, "P_r_config": r,
                   "ellmax": case.config.get("ellmax"), "samples": len(case.x)}
            for name in names:
                row[f"initial_{name}"] = float(case.column(name)[0])
                row[f"final_{name}"] = float(case.column(name)[-1])
            for name in ("Sigma_F", "Pi_m", "Pi_r", "Pi_total", "ne_cm3", "tau_T"):
                row[f"minimum_{name}"] = float(np.min(case.column(name)))
                row[f"maximum_{name}"] = float(np.max(case.column(name)))
            writer.writerow(row)
    temporary.replace(path)
    return _file_record(path, out)


def _parameter_sweep(cases: list[Case], out: Path) -> dict:
    sigmas = sorted({case.parameters[0] for case in cases})
    cmap = plt.get_cmap("viridis")
    color_map = {s: cmap(i / max(len(sigmas) - 1, 1)) for i, s in enumerate(sigmas)}
    colors = [color_map[case.parameters[0]] for case in cases]
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 9.5))
    sig = np.array([[case.column("Sigma_F")[i] for case in cases] for i in (0, -1)])
    for row, (name, label) in enumerate((("Pi_m", r"$\Pi_m$"), ("Pi_r", r"$\Pi_r$"))):
        stress = np.array([[case.column(name)[i] for case in cases] for i in (0, -1)])
        for col, epoch in enumerate(("Initial: z = 20", "Final: z = 2")):
            ax = axes[row, col]
            ax.scatter(sig[col], stress[col], c=colors, s=26, alpha=.72,
                       edgecolors="white", linewidths=.25, rasterized=False)
            _nonnegative_scale(ax, "x", sig, 1e-5)
            _nonnegative_scale(ax, "y", stress, 1e-8)
            ax.set(xlabel=r"$\Sigma=\|\sigma_{ab}\|_F/H$", ylabel=label,
                   title=f"{epoch} | {'Matter' if row == 0 else 'Radiation'}")
    handles = [Line2D([], [], color=color_map[s], marker="o", linestyle="none",
                      label=rf"$\Sigma_0={_number(s)}$") for s in sigmas]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .025),
               ncol=min(len(handles), 4), frameon=False)
    fig.suptitle(f"LRS Bianchi I pilot | {len(cases)} saved parameter cases", y=.985)
    fig.text(.5, .002, "Norm axes use symlog with explicit zero. Color = initial shear. "
             "Overlapping points are separate signed-stress inputs; no interpolation.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .105, 1, .95))
    return {"figure": "parameter_sweep", "files": _save(fig, out, "parameter_sweep"),
            "initial_sigma_levels": sigmas, "plotted_cases": len(cases),
            "axis_norm": "Frobenius", "interpolation": None}


def _shear_planes(cases: list[Case], out: Path) -> dict:
    sigmas = sorted({case.parameters[0] for case in cases})
    matter = sorted({case.parameters[1] for case in cases})
    radiation = sorted({case.parameters[2] for case in cases})
    lookup = {}
    for case in cases:
        if case.parameters in lookup:
            raise ValueError(f"More than one completed case at parameter cell {case.parameters}")
        lookup[case.parameters] = case
    vmax = max(max(abs(float(case.column("signed_Sigma")[-1])) for case in cases), 1e-8)
    norm = SymLogNorm(linthresh=min(1e-4, vmax / 10), vmin=-vmax, vmax=vmax, base=10)
    columns = min(4, len(sigmas))
    rows = math.ceil(len(sigmas) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(4.1 * columns + .5, 3.9 * rows + .8), squeeze=False)
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#e4e4e4")
    missing = 0
    for panel, sigma in enumerate(sigmas):
        ax = axes.flat[panel]
        values = np.full((len(matter), len(radiation)), np.nan)
        for j, pm in enumerate(matter):
            for k, pr in enumerate(radiation):
                case = lookup.get((sigma, pm, pr))
                if case is not None:
                    values[j, k] = case.column("signed_Sigma")[-1]
        missing += int(np.count_nonzero(~np.isfinite(values)))
        artist = ax.pcolormesh(np.arange(len(radiation) + 1) - .5,
                              np.arange(len(matter) + 1) - .5,
                              np.ma.masked_invalid(values), cmap=cmap, norm=norm,
                              shading="flat", edgecolors="white", linewidth=.45)
        ax.set_xticks(range(len(radiation)), [_number(v) for v in radiation], rotation=40, ha="right")
        ax.set_yticks(range(len(matter)), [_number(v) for v in matter])
        ax.set(xlabel=r"Initial signed $P_r$ (sample values)",
               ylabel=r"Initial signed $P_m$ (sample values)",
               title=rf"$\Sigma_0={_number(sigma)}$")
        ax.grid(False)
    for index in range(len(sigmas), rows * columns):
        axes.flat[index].set_visible(False)
    fig.suptitle(r"Final signed shear $\sqrt{6}\,s/H$ | discrete parameter planes", y=.99)
    fig.subplots_adjust(left=.065, right=.9, bottom=.14, top=.91, wspace=.43, hspace=.6)
    colorbar = fig.colorbar(artist, cax=fig.add_axes((.925, .22, .015, .58)))
    colorbar.set_label(r"Signed $\Sigma$ at z = 2 (common symlog color scale)")
    fig.text(.5, .015, "One cell = one saved case; equal cell widths denote the discrete grid, "
             "not uniform parameter spacing. Grey = missing case. Preliminary finite model.",
             ha="center", fontsize=9)
    return {"figure": "shear_planes", "files": _save(fig, out, "shear_planes"),
            "sigma_levels": sigmas, "signed_matter_levels": matter,
            "signed_radiation_levels": radiation, "missing_cells": missing,
            "interpolation": None}


def _time_evolution(selected: list[Case], out: Path, elapsed: bool) -> dict:
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.8))
    keys = ("Sigma_F", "Pi_m", "Pi_r", "Pi_total")
    labels = (r"$\Sigma=\|\sigma_{ab}\|_F/H$", r"$\Pi_m$", r"$\Pi_r$", r"$\Pi_{\rm total}$")
    for panel, (key, label) in enumerate(zip(keys, labels)):
        ax = axes.flat[panel]
        all_y = []
        for index, case in enumerate(selected):
            coordinate = ((case.column("elapsed_s") - case.column("elapsed_s")[0]) / SECONDS_PER_GYR
                          if elapsed else case.column("z"))
            y = case.column(key)
            all_y.append(y)
            ax.plot(coordinate, y, color=COLORS[index], lw=1.65,
                    linestyle="--" if index == 0 else "-", label=_parameter_label(case))
        _nonnegative_scale(ax, "y", np.concatenate(all_y), 1e-6 if key == "Sigma_F" else 1e-8)
        if elapsed:
            ax.set_xlim(left=0.)
            ax.xaxis.set_major_locator(MaxNLocator(6))
        else:
            ax.set_xlim(max(case.column("z")[0] for case in selected),
                        min(case.column("z")[-1] for case in selected))
            ax.set_xticks([20, 16, 12, 8, 4, 2])
        ax.set(xlabel="Elapsed time since z = 20 [Gyr]" if elapsed else "Mean redshift z", ylabel=label)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .025),
               ncol=2, frameon=False, fontsize=9)
    title = "Actual elapsed-time evolution" if elapsed else "Evolution from z = 20 to z = 2"
    fig.suptitle(title + " | selected saved pilot trajectories", y=.985)
    fig.text(.5, .002, "Labels give signed initial stress inputs. Curves show nonnegative tensor norms; "
             "zero remains visible. Each time axis uses that case's stored clock.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .19, 1, .95))
    name = "time_evolution_elapsed_gyr" if elapsed else "time_evolution_z20_z2"
    return {"figure": name, "files": _save(fig, out, name),
            "case_ids": [case.case_id for case in selected],
            "time_coordinate": "(elapsed_s-elapsed_s_initial)/31557600000000000" if elapsed else "stored z",
            "norms": list(keys)}


def _species(cases: list[Case], reference: Case, out: Path) -> dict:
    z = reference.column("z")
    ion_min = np.full((9, len(z)), np.inf)
    ion_max = np.full((9, len(z)), -np.inf)
    for case in cases:
        if len(case.x) != len(reference.x) or not np.allclose(case.column("z"), z, rtol=0., atol=2e-12):
            raise ValueError("Species range requires common stored redshift nodes; interpolation is disabled")
        fractions, = case.extra("ion_fractions")
        if fractions.shape != ion_min.shape or not np.all(np.isfinite(fractions)):
            raise ValueError(f"{case.case_id}: invalid ion-fraction shape or nonfinite entry")
        ion_min = np.minimum(ion_min, fractions)
        ion_max = np.maximum(ion_max, fractions)
    fractions, abundance, species_names, electrons, nuclide_names = reference.extra(
        "ion_fractions", "abundance_per_H", "species_names", "electron_by_nuclide_cm3", "nuclide_names")
    if abundance.shape != (len(species_names), len(z)) or electrons.shape != (len(nuclide_names), len(z)):
        raise ValueError("Species/electron metadata do not match saved arrays")
    if not np.all(np.isfinite(abundance)) or not np.all(np.isfinite(electrons)):
        raise ValueError("Nonfinite abundance or electron component")
    if np.any(abundance < 0) or np.any(electrons < 0):
        raise ValueError("Negative species data cannot be presented as a positive abundance heatmap")
    fig = plt.figure(figsize=(16.8, 10.7))
    grid = fig.add_gridspec(2, 3, height_ratios=[1., 1.35], hspace=.38, wspace=.3)
    groups = (("Hydrogen isotopes: shared electronic fractions", (0, 1), ("H I", "H II")),
              ("Helium isotopes: shared electronic fractions", (2, 3, 4), ("He I", "He II", "He III")),
              ("Lithium isotopes: shared electronic fractions", (5, 6, 7, 8), ("Li I", "Li II", "Li III", "Li IV")))
    for panel, (title, indices, labels) in enumerate(groups):
        ax = fig.add_subplot(grid[0, panel])
        for color, index, label in zip(COLORS[1:], indices, labels):
            ax.fill_between(z, ion_min[index], ion_max[index], color=color, alpha=.16, linewidth=0)
            ax.plot(z, fractions[index], color=color, label=label, lw=1.65)
        ax.set(xlim=(z[0], z[-1]), ylim=(-.035, 1.055), xlabel="Mean redshift z",
               ylabel="Ion fraction within an isotope", title=title)
        ax.set_xticks([20, 15, 10, 5, 2])
        ax.legend(loc="best", fontsize=9, frameon=False)
        if panel == 2:
            exact_zero = [labels[j] for j, index in enumerate(indices) if np.all(ion_max[index] == 0)]
            if exact_zero:
                ax.text(.03, .52, "Exact zero: " + ", ".join(exact_zero) + "\n60 eV UV cutoff; CI excluded",
                        transform=ax.transAxes, fontsize=9,
                        bbox={"facecolor": "white", "alpha": .86, "edgecolor": "none"})
    ax = fig.add_subplot(grid[1, 0])
    zero_electrons = []
    nonzero_values = []
    for index, name in enumerate(nuclide_names):
        values = electrons[index]
        if np.all(values == 0):
            zero_electrons.append(str(name))
            continue
        nonzero_values.append(values)
        ax.plot(z, values, color=COLORS[index % len(COLORS)], label=str(name), lw=1.6)
    total = reference.column("ne_cm3")
    ax.plot(z, total, color="black", lw=1.3, linestyle="--", label="Total")
    positive = electrons[electrons > 0]
    threshold = max(1e-28, 10. ** math.floor(math.log10(float(positive.min())))) if positive.size else 1e-10
    _nonnegative_scale(ax, "y", np.r_[electrons.ravel(), total], threshold)
    ax.set(xlim=(z[0], z[-1]), xlabel="Mean redshift z", ylabel=r"Proper electron contribution [cm$^{-3}$]",
           title="Electrons resolved by nucleus / isotope")
    ax.set_xticks([20, 15, 10, 5, 2])
    ax.legend(loc="best", fontsize=8, ncol=2, frameon=False)
    if zero_electrons:
        ax.text(.02, .02, "Exact-zero contributors: " + ", ".join(zero_electrons),
                transform=ax.transAxes, fontsize=8,
                bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none"})
    ax = fig.add_subplot(grid[1, 1:])
    positive_abundance = abundance[abundance > 0]
    low = float(positive_abundance.min()) if positive_abundance.size else 1e-30
    high = float(positive_abundance.max()) if positive_abundance.size else 1.
    if high <= low:
        low = high / 10
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#e2e2e2")
    # Stored samples are uniform in eta, not z. Use their actual redshift cell
    # boundaries instead of an imshow extent, which would distort their timing.
    z_edges = np.r_[z[0] + .5 * (z[0] - z[1]), .5 * (z[:-1] + z[1:]),
                    z[-1] - .5 * (z[-2] - z[-1])]
    image = ax.pcolormesh(z_edges, np.arange(len(species_names) + 1) - .5,
                          np.ma.masked_equal(abundance, 0.), shading="flat",
                          cmap=cmap, norm=LogNorm(vmin=low, vmax=high))
    ax.set_yticks(range(len(species_names)), [str(name) for name in species_names], fontsize=8)
    ax.set(xlabel="Mean redshift z", xlim=(z[0], z[-1]),
           ylim=(len(species_names) - .5, -.5),
           title=f"All {len(species_names)} saved species | abundance per H nucleus")
    ax.set_xticks([20, 15, 10, 5, 2])
    ax.grid(False)
    cb = fig.colorbar(image, ax=ax, fraction=.035, pad=.025)
    cb.set_label("Number abundance / H nucleus")
    fig.suptitle("Isotope and ion census | prescribed UV + photo / total-RR pilot", y=.985)
    fig.text(.5, .048, f"Fraction shading = min–max across {len(cases)} saved cases; lines, electrons and abundance map use "
             + _parameter_label(reference) + ".", ha="center", fontsize=9)
    fig.text(.5, .023, "Grey abundance cells = exact zero, with no artificial floor. "
             "Isotope electronic rates are equal by assumption. n and T start at zero; the full 19-reaction network is not active.",
             ha="center", fontsize=9)
    fig.subplots_adjust(left=.065, right=.96, top=.91, bottom=.12)
    return {"figure": "species_ionization", "files": _save(fig, out, "species_ionization"),
            "reference_case_id": reference.case_id, "fraction_range_cases": len(cases),
            "species_names": species_names.tolist(), "nuclide_names": nuclide_names.tolist(),
            "exact_zero_electron_contributors": zero_electrons,
            "exact_zero_species": [str(name) for name, values in zip(species_names, abundance) if np.all(values == 0)],
            "interpolation": "none; flat cells use actual stored redshift node boundaries"}


def _integrated_budget(case: Case) -> tuple[dict[str, np.ndarray], str]:
    names = ("I_s_initial", "I_m", "I_gamma", "I_nu", "H_Href")
    if all(name in case.names for name in names):
        pieces = {name: case.column(name) for name in names[:-1]}
        pieces["lhs"] = np.exp(3 * case.x) * case.column("signed_Sigma") * case.column("H_Href") / math.sqrt(6)
        return pieces, "saved ODE-integrated components"
    # Diagnostic-only fallback from saved nodes.  The source equation is
    # d[exp(3 eta)s/Href]/deta = exp(3 eta)(H/Href) P_X/sqrt(6).
    # This integral does not claim the solver's integrated budget accuracy.
    h_ratio = case.column("H_per_s") / case.column("H_per_s")[0]
    factor = np.exp(3 * case.x) * h_ratio / math.sqrt(6)
    pieces = {"I_s_initial": np.full(len(case.x), case.column("signed_Sigma")[0] / math.sqrt(6))}
    for key, source in (("I_m", "P_m"), ("I_gamma", "P_gamma"), ("I_nu", "P_nu")):
        integrand = factor * case.column(source)
        pieces[key] = np.r_[0., np.cumsum(.5 * np.diff(case.x) * (integrand[:-1] + integrand[1:]))]
    pieces["lhs"] = factor * case.column("signed_Sigma")
    return pieces, "saved-node trapezoid diagnostic; not an ODE budget certificate"


def _stress_budget(selected: list[Case], out: Path) -> dict:
    fig, axes = plt.subplots(2, len(selected), figsize=(7.1 * len(selected), 9.), squeeze=False)
    evidence = []
    for col, case in enumerate(selected):
        z = case.column("z")
        ax = axes[0, col]
        for key, label, color in (("P_m", r"$P_m$", COLORS[1]), ("P_gamma", r"$P_\gamma$", COLORS[2]),
                                  ("P_nu", r"$P_\nu$", COLORS[3])):
            ax.plot(z, case.column(key), label=label, color=color, lw=1.6)
        signed_total = case.column("P_m") + case.column("P_gamma") + case.column("P_nu")
        ax.plot(z, signed_total, label=r"$P_m+P_\gamma+P_\nu$", color="black", lw=1.4, linestyle="--")
        ax.axhline(0, color="#666666", lw=.6)
        ax.set_yscale("symlog", linthresh=1e-7, base=10)
        ax.set(xlim=(z[0], z[-1]), xlabel="Mean redshift z", ylabel="Signed normalized stress",
               title=_parameter_label(case))
        ax.legend(frameon=False, fontsize=9, ncol=2)
        pieces, method = _integrated_budget(case)
        ax = axes[1, col]
        for key, label, color in (("I_s_initial", "Initial shear", "#888888"),
                                  ("I_m", "Matter source", COLORS[1]),
                                  ("I_gamma", "Photon source", COLORS[2]),
                                  ("I_nu", "Neutrino source", COLORS[3])):
            ax.plot(z, pieces[key], label=label, color=color, lw=1.5)
        summed = sum(pieces[key] for key in ("I_s_initial", "I_m", "I_gamma", "I_nu"))
        ax.plot(z, summed, color="#CC79A7", lw=2.4, label="Initial + sources")
        ax.plot(z, pieces["lhs"], color="black", lw=1.2, linestyle="--", label=r"$e^{3\eta}s/H_{\rm ref}$")
        residual = float(np.max(np.abs(summed - pieces["lhs"])))
        ax.axhline(0, color="#666666", lw=.6)
        ax.set(xlim=(z[0], z[-1]), xlabel="Mean redshift z", ylabel=r"$e^{3\eta}s/H_{\rm ref}$ source budget",
               title=f"{method}\nmax |sum − lhs| = {residual:.3e}")
        ax.legend(frameon=False, fontsize=8, ncol=2)
        evidence.append({"case_id": case.case_id, "method": method, "maximum_absolute_budget_residual": residual})
    fig.suptitle("Signed stress and accumulated shear source budgets", y=.985)
    fig.text(.5, .015, r"$\eta=\ln(a/a_{\rm ref})$; matter, photon and neutrino sources retain their signs. "
             "Cancellation is assessed with an absolute residual; this plot does not establish global IVP accuracy.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .95))
    return {"figure": "stress_budget", "files": _save(fig, out, "stress_budget"), "budgets": evidence}


def render(catalog_path: str | Path, out_dir: str | Path, *, overwrite: bool = False) -> dict:
    """Render six figure pairs, an endpoint CSV and a source-hashed manifest."""
    catalog_path = Path(catalog_path).resolve()
    out = Path(out_dir).resolve()
    expected = [out / (name + "." + ext) for name in FIGURE_NAMES for ext in ("png", "svg")]
    expected += [out / "endpoints.csv", out / "FIGURE_MANIFEST.json"]
    existing = [path for path in expected if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(f"Plot outputs already exist; use a new directory or --overwrite: {existing[0]}")
    out.mkdir(parents=True, exist_ok=True)
    catalog, cases, skipped = _load(catalog_path)
    _style()
    inputs = []
    for case in cases:
        item = {"case_id": case.case_id, "npz": _file_record(case.path, catalog_path.parent)}
        if case.receipt:
            item["receipt"] = _file_record(case.receipt, catalog_path.parent)
        inputs.append(item)
    selected = _closest(cases, [(0, 0, 0), (1e-3, 0, 0), (.6, 0, 0), (0, .0012, 0),
                                (0, -.0006, 0), (0, 0, .0048), (0, 0, -.0024), (.1, .0012, -.0024)])
    budget_cases = _closest(cases, [(.01, .0012, -.0024), (.6, 0, 0)])
    species_case = _closest(cases, [(0, 0, 0)])[0]
    manifest = {
        "schema": "he32.saved_pilot.figures.v1", "status": "rendering",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "catalog": _file_record(catalog_path, catalog_path.parent),
        "catalog_schema": catalog.get("schema"), "source_code_sha256": _sha(Path(__file__)),
        "completed_cases": len(cases), "skipped_cases": skipped, "inputs": inputs,
        "science_ivp_runs": 0, "benchmark_runs": 0,
        "model_scope": "Preliminary LRS Bianchi I finite model; prescribed UV photo + total RR; not an observational fit",
        "scope_notes": ["Matter and radiation norms are separate; signed components remain available for source budgets.",
                        "Elemental electronic rates are shared across isotopes.",
                        "The selected 60 eV UV support has zero LiII/LiIII photoionization; CI is excluded.",
                        "n and T start at zero; the complete 19-reaction nuclear network is not active.",
                        "Only saved completed cases are plotted; no synthetic case or parameter interpolation."],
        "selections": {"time_evolution": [c.case_id for c in selected],
                       "stress_budget": [c.case_id for c in budget_cases], "species": species_case.case_id},
        "endpoint_csv": _write_endpoints(cases, out), "figures": [],
    }
    manifest_path = out / "FIGURE_MANIFEST.json"
    _atomic_json(manifest_path, manifest)
    jobs = [lambda: _parameter_sweep(cases, out), lambda: _shear_planes(cases, out),
            lambda: _time_evolution(selected, out, False), lambda: _time_evolution(selected, out, True),
            lambda: _species(cases, species_case, out), lambda: _stress_budget(budget_cases, out)]
    for job in jobs:
        manifest["figures"].append(job())
        _atomic_json(manifest_path, manifest)
    manifest["status"] = "completed"
    _atomic_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true", help="Replace only named plot outputs, preserving all input data")
    args = parser.parse_args()
    result = render(args.catalog, args.out, overwrite=args.overwrite)
    print(json.dumps({"status": result["status"], "completed_cases": result["completed_cases"],
                      "figure_pairs": len(result["figures"]), "manifest": str(args.out / "FIGURE_MANIFEST.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
