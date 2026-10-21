"""Offline, read-only renderer for the completed isotope quotient pilot.

Usage: python pilot/code/render.py [--allow-partial]
Reads immutable results/*.npz + receipts. Never integrates or modifies raw data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures_final"
GYR_S = 365.25 * 86400 * 1e9
THRESHOLD = 2e-5
ELEMENTS = ("H1", "D", "T", "He3", "He4", "Li6", "Li7")
COLORS = ("#006D77", "#E29578", "#7353BA", "#D1495B")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load():
    records = []
    for receipt_path in sorted(RESULTS.glob("quotient_*.json")):
        receipt = json.loads(receipt_path.read_text())
        path = receipt_path.with_suffix(".npz")
        if receipt.get("status") != "PASS":
            continue
        if not path.is_file() or digest(path) != receipt.get("npz_sha256"):
            raise RuntimeError(f"missing/hash-mismatched completed raw: {path}")
        with np.load(path, allow_pickle=True) as raw:
            keys = ("x", "z", "census", "census_names", "conditional",
                    "diagnostics", "diagnostic_names", "abundances")
            data = {key: raw[key].copy() for key in keys}
        names = list(data["diagnostic_names"])
        if data["census"].shape != (257, 21) or data["diagnostics"].shape[0] != 257:
            raise RuntimeError(f"unexpected array shape: {path}")
        if not np.allclose(data["z"], 21 * np.exp(-data["x"]) - 1, atol=2e-14):
            raise RuntimeError(f"redshift mismatch: {path}")
        data["age"] = data["diagnostics"][:, names.index("elapsed_s")] / GYR_S
        records.append((receipt, data, path))
    return records


def col(item, name):
    data = item[1]
    return data["diagnostics"][:, list(data["diagnostic_names"]).index(name)]


def pick(records, *, sigma, am, ar, ellmax=16):
    matches = [r for r in records if r[0]["model"]["ellmax"] == ellmax
               and np.isclose(r[0]["model"]["Sigma_F0"], sigma, atol=1e-12)
               and np.isclose(r[0]["model"]["A_m"], am, atol=1e-12)
               and np.isclose(r[0]["model"]["A_r"], ar, atol=1e-12)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one case for {(sigma,am,ar,ellmax)}; got {len(matches)}")
    return matches[0]


def save(fig, stem, selected, columns, manifest, note):
    fig.savefig(FIGURES / f"{stem}.png", dpi=190, facecolor="white")
    fig.savefig(FIGURES / f"{stem}.pdf", facecolor="white")
    plt.close(fig)
    for item in selected:
        manifest.append(dict(figure=stem, case=item[0]["case"],
                             npz=str(item[2].relative_to(ROOT)), sha256=digest(item[2]),
                             source_columns=";".join(columns), transformation=note))


def top_redshift(ax, data):
    age, z = data["age"], data["z"]
    marks = (20, 15, 10, 7, 5, 3, 2)
    ticks = np.interp(marks, z[::-1], age[::-1])
    top = ax.secondary_xaxis("top")
    top.set_xticks(ticks, [str(v) for v in marks])
    top.set_xlabel("Redshift z (same sampled trajectory)", labelpad=7)


def banner(fig, title, subtitle):
    fig.suptitle(title, x=.06, y=.99, ha="left", fontsize=17, weight="semibold")
    fig.text(.06, .953, subtitle, fontsize=9.3, color="#455A64", va="top")


def stress_history(item, manifest):
    r, data, _ = item
    age = data["age"]
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.0), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.13]})
    banner(fig, "Shear and anisotropic stress across z = 20 → 2",
           "Strong positive-shear case; Frobenius magnitudes below. Matter and radiation are resolved on their own scale.")
    axes[0].plot(age, col(item, "Sigma_F"), color="#122A3A", lw=2.5, label=r"$\Sigma=|S|$")
    axes[0].plot(age, col(item, "signed_Sigma"), color="#18A999", ls="--", lw=1.5,
                 label=r"signed $S$", alpha=.8)
    axes[0].set_ylabel("Shear / H, full Frobenius")
    axes[0].legend(loc="upper right", ncol=2)
    for key, label, color in (("Pi_m", r"$\Pi_m$", COLORS[0]),
                              ("Pi_r", r"$\Pi_r=|P_\gamma+P_\nu|$", COLORS[1]),
                              ("Pi_total", r"$\Pi_{\rm total}=|P_m+P_\gamma+P_\nu|$", COLORS[3])):
        axes[1].plot(age, col(item, key), lw=2, color=color, label=label)
    axes[1].set_ylabel("Stress / H², full Frobenius")
    axes[1].legend(loc="best", fontsize=9)
    axes[1].set_xlabel("Elapsed cosmic time since z = 20 [Gyr]")
    top_redshift(axes[0], data)
    for ax in axes:
        ax.axhline(0, color="#9AA7AD", lw=.7)
        ax.grid(alpha=.18)
    fig.tight_layout(rect=(0, 0, 1, .90))
    save(fig, "01_shear_stress_history", [item],
         ["elapsed_s", "z", "Sigma_F", "signed_Sigma", "Pi_m", "Pi_r", "Pi_total"],
         manifest, "elapsed_s/(365.25*86400*1e9); no resampling")


def signed_history(item, manifest, stem, title):
    data = item[1]
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.9), sharex=True)
    banner(fig, title, "Signed stresses retain orientation and cancellation; Pᵣ = Pγ + Pν and Ptotal = Pₘ + Pᵣ.")
    age = data["age"]
    for key, label, color in (("P_m", "$P_m$", COLORS[0]),
                              ("P_gamma", "$P_\\gamma$", COLORS[1]),
                              ("P_nu", "$P_\\nu$", COLORS[2]),
                              ("P_r", "$P_r$", "#8B5E34"),
                              ("signed_Sigma", "signed $S$", "#122A3A")):
        ax = axes[1] if key == "signed_Sigma" else axes[0]
        ax.plot(age, col(item, key), label=label, color=color, lw=1.8)
    total = col(item, "P_m") + col(item, "P_gamma") + col(item, "P_nu")
    axes[0].plot(age, total, color="black", lw=2.5, label="$P_{total}$ signed")
    axes[0].set_ylabel("Signed matter / photon / neutrino stress")
    axes[1].set_ylabel("Signed shear $S$")
    axes[1].set_xlabel("Elapsed time since z = 20 [Gyr]")
    for ax in axes:
        ax.axhline(0, color="#9AA7AD", lw=.8)
        ax.grid(alpha=.18)
        ax.legend(ncol=3, fontsize=9)
    top_redshift(axes[0], data)
    fig.tight_layout(rect=(0, 0, 1, .90))
    save(fig, stem, [item], ["elapsed_s", "z", "P_m", "P_gamma", "P_nu", "P_r", "signed_Sigma"],
         manifest, "signed total recomputed P_m+P_gamma+P_nu from same NPZ rows; no interpolation")


def map_sweep(records, manifest):
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.7), constrained_layout=False)
    banner(fig, "Final signed shear on the realized initial stress plane",
           "Five Σ₀ slices of the 75 nominal grid cases. Points are measured integrations; each colorbar spans its attained range.")
    used = []
    for ax, sigma in zip(axes.flat, (0, .01, .05, .2, .6)):
        subset = [r for r in records if r[0]["model"]["ellmax"] == 16
                  and np.isclose(r[0]["model"]["Sigma_F0"], sigma, atol=1e-12)
                  and any(np.isclose(r[0]["model"]["A_m"], v, atol=1e-12) for v in (-.8, 0., 1.6))
                  and any(np.isclose(r[0]["model"]["A_r"], v, atol=1e-12)
                          for v in (-.8, -.4, 0., .4, 1.6))]
        if len(subset) != 15:
            raise RuntimeError(f"incomplete Sigma0={sigma} grid: {len(subset)}/15")
        x = [r[0]["initial_axes"][1] for r in subset]
        y = [r[0]["initial_axes"][2] for r in subset]
        v = np.asarray([r[0]["final_axes"][0] for r in subset])
        lo, hi = float(v.min()), float(v.max())
        if lo == hi:
            hi = np.nextafter(hi, np.inf)
        sc = ax.scatter(x, y, c=v, norm=Normalize(vmin=lo, vmax=hi), cmap="coolwarm",
                        s=115, edgecolor="black", linewidth=.5)
        cb = fig.colorbar(sc, ax=ax, shrink=.80, pad=.02)
        cb.set_label("Attained final signed $S$")
        ax.set_title(fr"Initial $\Sigma_0={sigma:g}$ · final S [{lo:.3g}, {float(v.max()):.3g}]")
        ax.set_xlabel("Realized initial signed $P_m$")
        ax.set_ylabel("Realized initial signed $P_r$")
        ax.set_xticks((-.0005, 0, .001))
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-3, -3), useMathText=True)
        ax.grid(alpha=.15)
        used.extend(subset)
    axes.flat[-1].axis("off")
    axes.flat[-1].text(.05, .88, "Grid only: 3 matter × 5 radiation\namplitudes in each Σ₀ slice.\n\nSpecial cancellation points and negative\nshear orientation controls are shown\nin separate histories.",
                       va="top", fontsize=12, linespacing=1.7)
    fig.tight_layout(rect=(0, 0, 1, .90), h_pad=2)
    save(fig, "02_signed_final_maps", used, ["initial_axes[1:3]", "final_axes[0]"],
         manifest, "receipt values only; 15 points/slice; five independent attained-range colorbars")


def species(item, manifest, axis_name):
    data = item[1]
    x = data["age"] if axis_name == "time" else data["z"]
    x_label = "Elapsed time since z = 20 [Gyr]" if axis_name == "time" else "Redshift z"
    names = list(data["census_names"])
    fig, axes = plt.subplots(4, 2, figsize=(15, 15), sharex=True)
    banner(fig, f"All 21 isotope-ion populations vs {axis_name}",
           "n_Aq / n_B, logarithmic positive values only. Zero/absent curves are stated in each panel; no floor or clipping.")
    for ax, isotope in zip(axes.flat, ELEMENTS):
        qnames = [v for v in names if v.startswith(isotope + "_")]
        notes = []
        for j, name in enumerate(qnames):
            y = data["census"][:, names.index(name)]
            positive = np.where(y > 0, y, np.nan)
            if np.any(np.isfinite(positive)):
                ax.plot(x, positive, lw=1.8, color=COLORS[j], label=name.replace("_", " "))
            else:
                notes.append(name.replace("_", " ") + " = 0 throughout")
            neg = int(np.count_nonzero(y < 0))
            if neg:
                notes.append(f"{name}: {neg} negative sampled values omitted on log axis")
        ax.set_title(isotope + " isotope", loc="left", fontsize=12, weight="semibold")
        if ax.lines:
            ax.set_yscale("log")
            ax.set_ylabel(r"$n_{Aq}/n_B$ (positive)")
            ax.grid(alpha=.15)
        else:
            ax.set_yticks([])
            ax.set_ylabel("No populated states")
        if axis_name == "redshift":
            ax.invert_xaxis()
        if ax.lines:
            ax.legend(ncol=min(4, len(ax.lines)), fontsize=8, loc="best")
        if notes:
            ax.text(.5 if not ax.lines else .025, .5 if not ax.lines else .025,
                    "\n".join(notes), transform=ax.transAxes, fontsize=10 if not ax.lines else 8,
                    ha="center" if not ax.lines else "left",
                    va="center" if not ax.lines else "bottom", color="#8C3842",
                    bbox={"facecolor":"white", "alpha":.82, "edgecolor":"none"})
    # The eighth panel explicitly accounts for the requested unpopulated n and T.
    ax = axes.flat[-1]
    ax.axis("off")
    ax.text(.04, .94, "Census accounting", fontsize=14, weight="semibold", va="top")
    ax.text(.04, .80, "n⁰: exactly zero · absent initial/source inventory\nT⁰, T⁺: exactly zero · absent initial/source inventory\n\nLi6²⁺/³⁺ and Li7²⁺/³⁺ (LiIII/IV): exactly zero\nin this soft-UV atomic pilot (Li panels).\n\nSeven isotope panels + n⁰ = 21 outputs.\nOnly 9 elemental conditional fractions evolve;\nisotope rates and initial fractions are shared.",
            fontsize=11, va="top", linespacing=1.55)
    for ax in (axes[3,0], axes[2,1]):
        ax.set_xlabel(x_label)
        ax.tick_params(axis="x", labelbottom=True)
    fig.tight_layout(rect=(0, 0, 1, .92), h_pad=1.8)
    save(fig, "03_census_" + axis_name, [item],
         ["elapsed_s" if axis_name == "time" else "z", "census", "census_names", "abundances"],
         manifest, "direct 21-column n_Aq/n_B; positive-only log mask; exact zeros annotated; no floor")


def charge_fractions(item, manifest):
    data = item[1]
    f = data["conditional"]
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    banner(fig, "Elemental conditional charge fractions",
           "Nine integrated fractions, shared by isotopes of H, He and Li. Fixed prescribed T = 100–10,000 K; 5–60 eV UV.")
    for ax, (element, a, b) in zip(axes, (("H (H1, D)", 0, 2), ("He (He3, He4)", 2, 5),
                                          ("Li (Li6, Li7)", 5, 9))):
        for j in range(a, b):
            ax.plot(data["age"], f[:, j], color=COLORS[j-a], lw=2, label=f"charge +{j-a}")
        ax.set_ylabel(element + " fraction")
        ax.set_ylim(bottom=-.03, top=1.05)
        ax.grid(alpha=.2)
        ax.legend(ncol=4, fontsize=8)
    axes[2].text(.015, .02, "LiIII and LiIV = 0 exactly throughout in the soft-UV nominal pilot",
                 transform=axes[2].transAxes, fontsize=9, color="#8C3842")
    axes[-1].set_xlabel("Elapsed time since z = 20 [Gyr]")
    top_redshift(axes[0], data)
    fig.tight_layout(rect=(0, 0, 1, .90))
    save(fig, "04_elemental_conditional", [item], ["elapsed_s", "z", "conditional"],
         manifest, "direct nine conditional columns; shared isotope rates; zero charge states labelled")


def controls(records, manifest):
    cancellation = [r for r in records if r[0]["model"]["ellmax"] == 16
                    and np.isclose(r[0]["model"]["Sigma_F0"], 0, atol=1e-12)
                    and np.isclose(r[0]["model"]["A_m"], 1.6, atol=1e-12)
                    and not any(np.isclose(r[0]["model"]["A_r"], v, atol=1e-12)
                                for v in (-.8, -.4, 0., .4, 1.6))]
    if len(cancellation) != 1:
        raise RuntimeError(f"expected one positive-matter cancellation control: {len(cancellation)}")
    base = [pick(records, sigma=0, am=0, ar=0),
            pick(records, sigma=.6, am=1.6, ar=-.8), cancellation[0]]
    high = []
    for b in base:
        matches = [r for r in records if r[0]["model"]["ellmax"] == 24 and
                   np.allclose(r[0]["initial_axes"], b[0]["initial_axes"], atol=2e-10)]
        if len(matches) != 1:
            raise RuntimeError(f"missing control for {b[0]['case']}")
        high.append(matches[0])
    rows = []
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    banner(fig, "Tighter L24 controls against nominal L16",
           "Actual common 257-point grid; absolute differences below frozen 2×10⁻⁵ ceiling. No tolerance relaxation.")
    maxima = {}
    for ax, (b, h) in zip(axes, zip(base, high)):
        fields = {}
        for key in ("signed_Sigma", "P_m", "P_r"):
            fields[key] = np.abs(col(h, key) - col(b, key))
        fields["max conditional fraction"] = np.max(np.abs(h[1]["conditional"] - b[1]["conditional"]), axis=1)
        maximum = max(float(np.max(v)) for v in fields.values())
        maxima[h[0]["case"]] = {"nominal":b[0]["case"], "max_abs":maximum, "pass":maximum <= THRESHOLD}
        for j, (key, values) in enumerate(fields.items()):
            ax.plot(b[1]["age"], values, lw=1.8, color=COLORS[j], label=key)
        ax.axhline(THRESHOLD, ls="--", lw=1.5, color="#8C3842", label="control ceiling")
        ax.set_ylabel("Absolute difference")
        ax.set_title(f"{b[0]['case']} → L24  ·  maximum {maximum:.3g}", loc="left", fontsize=10)
        ax.grid(alpha=.17)
        ax.legend(fontsize=8, ncol=5)
        for i in range(len(b[1]["age"])):
            rows.append([b[0]["case"], h[0]["case"], i, b[1]["z"][i], b[1]["age"][i],
                         *(float(v[i]) for v in fields.values())])
    axes[-1].set_xlabel("Elapsed time since z = 20 [Gyr]")
    fig.tight_layout(rect=(0, 0, 1, .92))
    save(fig, "06_tighter_controls", base + high,
         ["elapsed_s", "z", "signed_Sigma", "P_m", "P_r", "conditional"], manifest,
         "absolute L24-tight minus L16-nominal at identical output index; derived rows controls_differences.csv")
    with (FIGURES / "controls_differences.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["nominal", "control", "index", "z", "elapsed_Gyr", "abs_S", "abs_P_m", "abs_P_r", "max_abs_conditional"])
        writer.writerows(rows)
    return maxima


def energy(item, manifest):
    data = item[1]
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    banner(fig, "Prescribed thermal/UV forcing and energy ledger",
           "Atomic test-fluid bookkeeping, not a solved thermal evolution. Background energy includes the prescribed cosmology.")
    age = data["age"]
    axes[0].plot(age, col(item, "T_K"), color="#D1495B", lw=2.2, label="prescribed T")
    axes[0].set_ylabel("Gas temperature [K]")
    axes[0].legend()
    for key, label, color in (("Q_gas_required_W_m3", "required gas exchange", COLORS[0]),
                              ("P_photo_W_m3", "photoionization input", COLORS[1]),
                              ("bath_minus_escape_W_m3", "remaining bath − escape", COLORS[2])):
        axes[1].plot(age, col(item, key), color=color, lw=1.9, label=label)
    axes[1].set_yscale("symlog", linthresh=1e-37)
    axes[1].set_ylabel("Energy rate [W m⁻³], signed symlog")
    axes[1].legend(ncol=3, fontsize=8)
    # E=3 H²/K is critical-equivalent, not a matter density. Subtract shear
    # and cosmological-constant terms from Einstein's constraint explicitly.
    lock = json.loads((ROOT / "vendor/REI_BACKGROUND_FAMILY_LOCK.json").read_text())["cosmology"]
    h0 = float(lock["H0_per_s"])
    lam = float(lock["Omega_lambda"])
    from scipy.constants import G, c
    kappa = 8 * math.pi * G / c**2
    H = col(item, "H_per_s")
    S = col(item, "signed_Sigma")
    shear_sq = (S * H)**2 / 6
    matter_energy = 3 * (H**2 - shear_sq - h0**2 * lam) / kappa
    if not np.all(matter_energy > 0):
        raise RuntimeError("non-positive matter-energy denominator")
    material = col(item, "U_thermal_J_m3") + col(item, "U_binding_J_m3")
    ratio = material / matter_energy
    axes[2].plot(age, ratio, color="#122A3A", lw=2.2,
                 label="atomic thermal + binding / non-Λ, non-shear total")
    axes[2].plot(age, col(item, "U_UV_J_m3") / col(item, "background_J_m3"),
                 color="#7353BA", lw=1.6, label="prescribed UV / critical equivalent")
    axes[2].set_ylabel("Explicit energy ratios")
    axes[2].set_xlabel("Elapsed time since z = 20 [Gyr]")
    axes[2].legend()
    for ax in axes:
        ax.grid(alpha=.18)
    top_redshift(axes[0], data)
    fig.tight_layout(rect=(0, 0, 1, .90))
    save(fig, "07_energy_thermal_uv", [item],
         ["elapsed_s", "z", "T_K", "H_per_s", "signed_Sigma", "Q_gas_required_W_m3", "P_photo_W_m3",
          "bath_minus_escape_W_m3", "U_thermal_J_m3", "U_binding_J_m3",
          "U_UV_J_m3", "background_J_m3"], manifest,
         "signed rates unaltered; denominator=3*(H^2-(S*H)^2/6-H0^2*Omega_lambda)/K includes material+radiation, excludes Lambda/shear; no thermal evolution")
    return {"atomic_thermal_binding_to_nonlambda_nonshear_total_min":float(np.min(ratio)),
            "atomic_thermal_binding_to_nonlambda_nonshear_total_max":float(np.max(ratio)),
            "nonlambda_nonshear_total_min_J_m3":float(np.min(matter_energy)),
            "nonlambda_nonshear_total_max_J_m3":float(np.max(matter_energy)),
            "source_lock_cosmology":{"H0_per_s":h0,"Omega_lambda":lam}}


def all_case_energy_scope(records):
    """Read-only maximum of all three prescribed test-fluid energy terms."""
    lock = json.loads((ROOT / "vendor/REI_BACKGROUND_FAMILY_LOCK.json").read_text())["cosmology"]
    from scipy.constants import G, c
    kappa = 8 * math.pi * G / c**2
    h0sq_lambda = float(lock["H0_per_s"])**2 * float(lock["Omega_lambda"])
    rows = []
    for item in records:
        H = col(item, "H_per_s")
        S = col(item, "signed_Sigma")
        denominator = 3*(H*H*(1-S*S/6)-h0sq_lambda)/kappa
        if np.any(denominator <= 0) or not np.isfinite(denominator).all():
            raise RuntimeError("invalid all-case non-Lambda/non-shear denominator: " + item[0]["case"])
        numerator = (col(item, "U_thermal_J_m3") + col(item, "U_binding_J_m3") +
                     col(item, "U_UV_J_m3"))
        ratio = numerator / denominator
        i = int(np.argmax(np.abs(ratio)))
        rows.append(dict(case=item[0]["case"], max_abs_ratio=float(abs(ratio[i])),
                         signed_ratio_at_max=float(ratio[i]), z_at_max=float(item[1]["z"][i]),
                         numerator_J_m3=float(numerator[i]), denominator_J_m3=float(denominator[i])))
    with (FIGURES / "all_case_energy_ratios.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    winner = max(rows, key=lambda row:row["max_abs_ratio"])
    return {"case_count":len(rows), "max_abs_ratio":winner,
            "denominator":"3*(H²−s²−H0²ΩΛ)/K, total non-Lambda and non-shear material+radiation energy; s=S H/sqrt(6)",
            "numerator":"U_thermal + U_binding + prescribed U_UV",
            "per_case_csv":"figures_final/all_case_energy_ratios.csv"}


def baseline_response(isotropic, strong, manifest):
    a, b = isotropic[1], strong[1]
    if not np.array_equal(a["z"], b["z"]):
        raise RuntimeError("baseline and strong redshift grids differ")
    if list(a["census_names"]) != list(b["census_names"]):
        raise RuntimeError("baseline census mismatch")
    dS = col(strong, "signed_Sigma") - col(isotropic, "signed_Sigma")
    dm = col(strong, "P_m") - col(isotropic, "P_m")
    dr = col(strong, "P_r") - col(isotropic, "P_r")
    fdelta = np.max(np.abs(b["conditional"] - a["conditional"]), axis=1)
    iso_age, strong_age = a["age"], b["age"]
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    banner(fig, "Physical response relative to the isotropic zero-stress pilot",
           "Same redshift samples, no time interpolation. Elapsed clocks differ and are displayed separately below.")
    axes[0].plot(a["z"], dS, color="#122A3A", lw=2.2, label="Δ signed shear S")
    axes[0].set_ylabel("Δ signed shear S")
    axes[0].legend()
    axes[1].plot(a["z"], dm, color=COLORS[0], lw=1.7, label="Δ signed Pₘ")
    axes[1].plot(a["z"], dr, color=COLORS[1], lw=1.7, label="Δ signed Pᵣ")
    axes[1].set_ylabel("Δ signed stresses")
    axes[1].legend(ncol=2)
    axes[2].plot(a["z"], fdelta, color="#7353BA", lw=2.3,
                 label="max |Δ conditional charge fraction|")
    axes[2].set_ylabel("Charge fraction response")
    axes[2].legend()
    axes[3].plot(a["z"], iso_age, label="isotropic t − t₂₀", lw=2, color=COLORS[0])
    axes[3].plot(a["z"], strong_age, label="strong-shear t − t₂₀", lw=2, color=COLORS[3])
    axes[3].set_ylabel("Elapsed time [Gyr]")
    axes[3].legend(ncol=2)
    axes[3].set_xlabel("Redshift z")
    for ax in axes:
        ax.grid(alpha=.18)
    axes[-1].invert_xaxis()
    fig.tight_layout(rect=(0, 0, 1, .90))
    save(fig, "08_isotropic_baseline_response", [isotropic, strong],
         ["z", "elapsed_s", "signed_Sigma", "P_m", "P_r", "conditional"], manifest,
         "strong minus isotropic at identical z indices; each elapsed clock shown directly; no interpolation")
    with (FIGURES / "baseline_differences.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("z", "elapsed_iso_Gyr", "elapsed_strong_Gyr", "delta_elapsed_Gyr",
                         "delta_signed_S", "delta_P_m", "delta_P_r", "max_abs_conditional_fraction_delta"))
        writer.writerows(zip(a["z"], iso_age, strong_age, strong_age-iso_age, dS, dm, dr, fdelta))
    fd = np.abs(b["conditional"] - a["conditional"])
    return {"z2_delta_signed_S":float(dS[-1]), "z2_delta_P_m":float(dm[-1]),
            "z2_delta_P_r":float(dr[-1]), "z2_max_abs_conditional_delta":float(fdelta[-1]),
            "max_abs_conditional_delta_over_history":float(fd.max()),
            "max_abs_by_element_over_history":{
                "H":float(fd[:,0:2].max()), "He":float(fd[:,2:5].max()),
                "Li":float(fd[:,5:9].max())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-partial", action="store_true", help="preview available full selections only")
    args = parser.parse_args()
    records = load()
    nominal = [r for r in records if r[0]["model"]["ellmax"] == 16]
    tight = [r for r in records if r[0]["model"]["ellmax"] == 24]
    if not args.allow_partial and (len(nominal), len(tight)) != (79, 3):
        raise RuntimeError(f"need 79 nominal + 3 tight passing raw results; found {len(nominal)} + {len(tight)}")
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10, "axes.titlesize":11,
                         "axes.labelsize":10, "axes.spines.top":False,
                         "axes.spines.right":False, "savefig.bbox":"tight"})
    manifest = []
    strong = pick(records, sigma=.6, am=1.6, ar=-.8)
    stress_history(strong, manifest)
    signed_history(strong, manifest, "05a_strong_signed_stress", "Signed photon, neutrino and matter stresses")
    species(strong, manifest, "time")
    species(strong, manifest, "redshift")
    charge_fractions(strong, manifest)
    energy_report = energy(strong, manifest)
    all_energy_report = all_case_energy_scope(records)
    baseline_report = baseline_response(pick(records, sigma=0, am=0, ar=0), strong, manifest)
    if len(nominal) == 79:
        map_sweep(records, manifest)
        # Special cancellation points have S0=0 and non-grid radiation amplitudes.
        cancellation = [r for r in nominal if r[0]["model"]["Sigma_F0"] == 0
                        and not any(np.isclose(r[0]["model"]["A_r"], v, atol=1e-12)
                                    for v in (-.8, -.4, 0., .4, 1.6))]
        if len(cancellation) != 2:
            raise RuntimeError(f"expected two off-grid cancellation points: {len(cancellation)}")
        for i, item in enumerate(sorted(cancellation, key=lambda r:r[0]["model"]["A_m"])):
            signed_history(item, manifest, f"05b_cancellation_{i+1}",
                           f"Cancellation configuration {i+1}: signed stresses")
        # Negative signed-S orientation controls are never plotted in grid-map slices.
        negative = [r for r in nominal if r[0]["model"]["Sigma_F0"] < 0]
        if len(negative) != 2:
            raise RuntimeError(f"expected two negative-shear controls: {len(negative)}")
        for i, item in enumerate(sorted(negative, key=lambda r:r[0]["model"]["A_m"])):
            signed_history(item, manifest, f"05c_negative_shear_{i+1}",
                           f"Negative initial shear orientation {i+1}")
    control_report = controls(records, manifest) if len(tight) == 3 else {}
    with (FIGURES / "PLOT_SELECTION_MANIFEST.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("figure", "case", "npz", "sha256", "source_columns", "transformation"))
        writer.writeheader()
        writer.writerows(manifest)
    report = {"status":"COMPLETE" if (len(nominal),len(tight))==(79,3) else "PARTIAL_PREVIEW",
              "nominal_pass_raw_count":len(nominal), "tight_control_pass_raw_count":len(tight),
              "figure_count":len({r["figure"] for r in manifest}),
              "figures":sorted({r["figure"] for r in manifest}),
              "manifest":"figures_final/PLOT_SELECTION_MANIFEST.csv",
              "raw_data":"results/quotient_*.npz, verified against corresponding immutable JSON SHA256",
              "control_differences":control_report, "energy_diagnostic_selected_case":energy_report,
              "energy_diagnostic_all_cases":all_energy_report,
              "isotropic_baseline_response":baseline_report,
              "interpretation":"Prescribed 100–10000 K thermal and 5–60 eV UV atomic test-fluid; 21 census outputs, 9 evolving conditional fractions. No nuclear channels, independent thermal closure, observational or production admission.",
              "command":"python pilot/code/render.py",
              "raw_overwritten":False, "integrations_performed":0}
    (FIGURES / "PLOT_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    (FIGURES / "PLOT_REPORT.md").write_text(
        "# Pilot figure readback\n\n" +
        f"Status: **{report['status']}**. Read {len(nominal)} nominal and {len(tight)} tighter-control SHA-matched original trajectories; no IVPs.\n\n" +
        "Every PNG has a PDF companion. Exact selected source files, SHA-256 values, columns and transformations are in `PLOT_SELECTION_MANIFEST.csv`; derived control and isotropic-baseline differences are also in `controls_differences.csv` and `baseline_differences.csv`.\n\n" +
        "The figures display 21 n_Aq/n_B outputs, while the inherited equality closure evolves nine independent charge fractions. " +
        "n and T have zero inventory. Nominal LiIII/IV remain zero in the fixed soft-UV atomic model. " +
        "Temperature (100–10000 K) and 5–60 eV UV are prescribed; gas/radiation energy is test-fluid bookkeeping. " +
        "No thermal or nuclear closure, production admission, or observational reionization inference is made.\n\n" +
        "Run offline with `python pilot/code/render.py` from this package.\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
