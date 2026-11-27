"""Display actual finite-window inputs, angular integral and scalar box ranges."""
import json
import os
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ddcs_window import UNIT, atomic_json, load_source


def save_atomic(fig, path, fmt):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.stem + ".", suffix="." + fmt, dir=path.parent)
    os.close(fd)
    try:
        fig.savefig(name, format=fmt, dpi=240, facecolor="white")
        with open(name, "rb") as f:
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    s = load_source()
    m = json.loads((UNIT / "results/moments.json").read_text())
    v = json.loads((UNIT / "results/validation.json").read_text())
    if v["status"] != "PASS":
        raise ValueError("analysis validation must PASS before plot")
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10, "legend.fontsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8, "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 3, figsize=(10.2, 6.5))
    fig.subplots_adjust(left=.075, right=.975, bottom=.19, top=.84, wspace=.43, hspace=.60)
    fig.suptitle("20 eV H ionization: detected-electron window", fontsize=14, y=.975)
    fig.text(.5, .915, r"$E=3$–$6$ eV, $\theta=15$–$120^\circ$; axisymmetric linear-$\mu$ model", ha="center", fontsize=10)
    theta = np.rad2deg(np.arccos(s.mu))[::-1]
    dense = np.linspace(15, 120, 250)
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    ax = axes[0, 0]
    for j, (e, color) in enumerate(zip(s.energy, colors)):
        y = s.values[::-1, j]
        ax.errorbar(theta, y, yerr=y * s.uncertainty_percent[::-1] / 100, fmt="o", ms=2.5, capsize=1.8, lw=.65, color=color)
        ax.plot(dense, np.interp(np.cos(np.deg2rad(dense)), s.mu, s.values[:, j]), color=color, lw=1.1, label=f"{e:g} eV")
    ax.set(xlim=(10, 125), xlabel=r"Detected $\theta$ (degree)", ylabel=r"DDCS ($10^{-19}$ cm$^2$/sr/eV)", title="(a) Source DDCS and quoted errors")
    ax.set_xticks([15, 40, 60, 90, 120])
    ax.legend(frameon=False, ncol=2, handlelength=1.2)
    ax = axes[0, 1]
    ax.plot(s.energy, [r["J_r_m2_per_eV"]["0"] / 1e-21 for r in m["per_energy"]], "o-", color="#0072B2", ms=4, lw=1.4)
    ax.set(xlabel="Detected energy (eV)", ylabel=r"$J_0(E)$ ($10^{-21}$ m$^2$/eV)", title="(b) Angular-window integral", xticks=[3, 4, 5, 6])
    quantities = [("mean_mu", r"$\langle\mu\rangle$", ""), ("mean_P2", r"$\langle P_2(\mu)\rangle$", ""),
                  ("mean_E_eV", r"$\langle E\rangle$", "eV"), ("mean_sqrtE_mu", r"$\langle\sqrt{E}\mu\rangle$", r"eV$^{1/2}$")]
    for idx, (ax, (name, title, unit)) in enumerate(zip([axes[0, 2], *axes[1]], quantities)):
        b = m["conditional_deterministic_box_not_CI"][name]
        value = m["conditional"][name]
        alternative = m["linear_theta_alternative"]["conditional"][name]
        ax.plot([b["minimum"], b["maximum"]], [0, 0], lw=4, color="#0072B2", alpha=.55, solid_capstyle="butt")
        ax.plot([b["minimum"], b["maximum"]], [0, 0], "|", color="#0072B2", ms=14)
        ax.plot(value, 0, "o", color="#111111", ms=5, label=r"linear $\mu$")
        ax.plot(alternative, 0.17, "D", color="#D55E00", ms=4, label=r"linear $\theta$")
        span = max(b["maximum"] - b["minimum"], abs(value) * .05, .01)
        ax.set_xlim(min(b["minimum"], alternative) - .12 * span, max(b["maximum"], alternative) + .12 * span)
        ax.set(ylim=(-.22, .36), yticks=[], xlabel=title + (" (" + unit + ")" if unit else ""), title=f"({chr(99 + idx)}) Scalar deterministic box")
        if idx == 0:
            ax.legend(frameon=False, loc="upper left", ncol=1, fontsize=8)
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", alpha=.15, lw=.6)
    fig.text(.075, .105, "Source bars: quoted row 1σ (reference-DCS error excluded; covariance unknown).", fontsize=9)
    fig.text(.075, .069, "Blue ranges: chosen cellwise deterministic box extrema, not confidence intervals.", fontsize=9)
    fig.text(.075, .033, "Each scalar has its own extremizer. No full-domain, event-law or recoil inference. Childers et al. (2004), Table IV.", fontsize=8.5)
    for fmt in ("png", "svg"):
        save_atomic(fig, UNIT / f"figures/ddcs20_window.{fmt}", fmt)
    plt.close(fig)
    atomic_json(UNIT / "results/figure_metadata.json", {"figure_inches": [10.2, 6.5], "target_review_width_mm": 180,
                "source_errorbars": "quoted one-sigma row percentages; not propagated CI", "blue_ranges": "deterministic scalar box extrema, not CI; witnesses differ by scalar",
                "interpolation_lines": "linear mu evaluated on physical theta axis", "alternative_marker": "linear theta, actual sin(theta) Jacobian; no error bound inferred", "visual_review": "pending root"})
    print("PNG/SVG created from actual results; root visual review pending.")


if __name__ == "__main__":
    main()
