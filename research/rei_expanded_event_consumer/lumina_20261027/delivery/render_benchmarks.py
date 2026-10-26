"""Render only immutable official source-table coordinates.

This is presentation, not a model, solver, interpolation, or independent fit.
Run from this unit with an explicit frozen input and output prefix.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCE_HASHES = {
    "HI_reion_lumina.txt": "e5f3b99fd5a99be26f7296d5624537e8db239111ebe52533dbb1d52fa22c0b70",
    "HeIII_reion_lumina.txt": "f7a465586a3247efe87c7e396d1bca179e330975af93c3ee6fe11b3320501714",
    "sfrd_lumina.txt": "a15cf35aa5004b09f1c2cd6c5c24cb7e927bcc85e3dfc4ec0bc319568679c2bd",
    "tau_cmb_vs_z_lumina.txt": "2dcc52854764c6a52f9f6bd98777e3b51804a057240d9b1dfe9a7d2939814386",
}


def literal_source_coordinates(data_dir: Path) -> tuple[dict, dict]:
    tables, identities = {}, {}
    for name, expected in SOURCE_HASHES.items():
        raw = (data_dir / name).read_bytes()
        observed = hashlib.sha256(raw).hexdigest()
        if observed != expected:
            raise ValueError("Frozen source byte mismatch: " + name)
        # Literal ASCII columns only. No adapter import or physical conversion.
        tables[name] = [list(map(float, line.split())) for line in
                        raw.decode("ascii").splitlines()
                        if line.strip() and not line.startswith("#")]
        identities[name] = {"sha256": observed, "bytes": len(raw),
                            "url": "https://lumina-simulation.com/data/" + name}
    hi, he, sfrd, tau = (tables[n] for n in SOURCE_HASHES)
    return {
        "HI_and_HII": {"z": [r[0] for r in hi], "HI": [r[1:] for r in hi]},
        "HeIII": {"z": [r[0] for r in he], "median_only": [r[1] for r in he]},
        "SFRD": {"z": [r[0] for r in sfrd], "value": [r[1] for r in sfrd]},
        "tau": {"z": [r[0] for r in tau], "value": [r[1] for r in tau],
                "paper_reported_Planck_reference_constraint": {"mean": .054, "sigma": .007}},
    }, identities


def render(input_path: Path, output_prefix: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels, identities = literal_source_coordinates(input_path)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2))
    blue, orange, green = "#1767a5", "#c45b24", "#25826c"
    hi = panels["HI_and_HII"]
    # Source-native column order: median, p15.87, p84.13, p2.275,
    # p97.725, min, max. No new physical coordinate is calculated.
    z, rows = hi["z"], hi["HI"]
    ax = axes[0, 0]
    ax.fill_between(z, [r[1] for r in rows], [r[2] for r in rows],
                    color=blue, alpha=.18, linewidth=0,
                    label="Spatial 15.87-84.13% interval")
    ax.plot(z, [r[0] for r in rows], color=blue, lw=2, label="H I median")
    ax.set(title="H I: simulated neutral fraction", ylabel=r"$x_{\rm HI}$")
    ax.legend(loc="best", fontsize=8.5, frameon=False)
    ax.text(.03, .04, "Subbox spatial spread; not a likelihood interval",
            transform=ax.transAxes, fontsize=8, color="#505964")

    he = panels["HeIII"]
    ax = axes[0, 1]
    ax.plot(he["z"], he["median_only"], color=orange, lw=2, label="He III median")
    ax.set(title="He III: simulated doubly ionized fraction", ylabel=r"$x_{\rm HeIII}$")
    ax.legend(loc="best", fontsize=8.5, frameon=False)
    ax.text(.12, .32, "Median only: interval labels unresolved\n"
            "Invalid quantile ordering: 203 rows", transform=ax.transAxes,
            fontsize=8, color="#9b4b22",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 2})

    sfrd = panels["SFRD"]
    ax = axes[1, 0]
    ax.plot(sfrd["z"], sfrd["value"], color=green, lw=2)
    ax.set(title="Simulated star-formation-rate density",
           ylabel=r"SFRD [$M_\odot\,\mathrm{yr}^{-1}\,\mathrm{cMpc}^{-3}$]")

    tau = panels["tau"]
    constraint = tau["paper_reported_Planck_reference_constraint"]
    mean, sigma = constraint["mean"], constraint["sigma"]
    ax = axes[1, 1]
    ax.axhspan(mean-sigma, mean+sigma, color="#7a818b", alpha=.18,
               label="Paper-reported Planck total constraint")
    ax.axhline(mean, color="#7a818b", lw=1, ls=":")
    ax.plot(tau["z"], tau["value"], color=blue, lw=2,
            label=r"Lumina cumulative $\tau(0\rightarrow z)$")
    ax.set(title="Simulated cumulative CMB optical depth", ylabel=r"$\tau_{\rm CMB}$")
    ax.legend(loc="best", fontsize=8, frameon=False)
    ax.text(.03, .04, r"$0.054\pm0.007$: contextual total constraint; no fit",
            transform=ax.transAxes, fontsize=8, color="#505964")

    for ax, panel in zip(axes.flat, (hi, he, sfrd, tau)):
        ax.set_xlabel("Redshift z")
        # Preserve each table's own endpoints; never extrapolate to z=0.
        ax.set_xlim(min(panel["z"]), max(panel["z"]))
        ax.grid(alpha=.15, linewidth=.6)
        if min(panel["z"]) <= 4.75 <= max(panel["z"]):
            ax.axvline(4.75, color="#656b75", ls="--", lw=.8)
            ax.text(4.75, .98, " Model switch z=4.75", fontsize=7,
                    color="#656b75", rotation=90, va="top", ha="left",
                    transform=ax.get_xaxis_transform())
    fig.suptitle("Lumina public simulation benchmarks", fontsize=17, weight="bold", y=.98)
    fig.text(.5, .936, "Official table coordinates on native grids - no new physical trajectory",
             ha="center", color="#505964", fontsize=10)
    fig.text(.5, .025, "Source: Lumina project, official public tables (lumina-simulation.com/data-access/). "
             "Dashed line: model switch, not an observed reionization time.",
             ha="center", fontsize=8, color="#505964")
    fig.subplots_adjust(left=.09, right=.98, bottom=.105, top=.87, hspace=.34, wspace=.28)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("png", "pdf", "svg"):
        target = output_prefix.with_suffix("." + suffix)
        fig.savefig(target, dpi=160, facecolor="white",
                    metadata={"Creator": "REI-LUMINA frozen-coordinate renderer"}
                    if suffix == "pdf" else None)
        data = target.read_bytes()
        outputs[suffix] = {"path": str(target), "bytes": len(data),
                           "sha256": hashlib.sha256(data).hexdigest()}
    plt.close(fig)
    return {"input": str(input_path), "source_files": identities,
            "status": "source_data_visualization; adapter_runtime_not_established",
            "presentation_only": True, "science_evaluations": 0, "outputs": outputs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.input, args.output_prefix), indent=2))
