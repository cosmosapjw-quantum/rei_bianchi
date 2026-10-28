"""Render the extracted original n/T stock and beta-event log histories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def render(source: Path, destination: Path) -> None:
    data = json.loads(source.read_text(encoding="utf-8"))
    if data["case_name"] != "quotient_L16_S-0.6_Am0_Ar0" or data["epoch_count"] != 257:
        raise ValueError("projection result case/epoch mismatch")
    t = np.asarray(data["elapsed_s"], dtype=float)
    if t.shape != (257,) or t[0] != 0 or not np.all(np.diff(t) > 0):
        raise ValueError("projection elapsed time mismatch")
    series = (
        ("log10_Y_n", "neutron n / baryon", "#1769aa"),
        ("log10_Y_T", "tritium T / baryon", "#bc5a28"),
        ("log10_C_n_beta_forward", "n → p beta events / baryon", "#1769aa"),
        ("log10_C_t_beta_forward", "T → He3 beta events / baryon", "#bc5a28"),
    )
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 7.4), sharex=True, constrained_layout=True)
    for ax, subset in ((axes[0], series[:2]), (axes[1], series[2:])):
        for key, label, color in subset:
            raw = data[key]
            if len(raw) != len(t) or raw[0] is not None:
                raise ValueError(f"saved series length/initial zero mismatch: {key}")
            y = np.asarray([np.nan if value is None else value for value in raw], dtype=float)
            if np.isfinite(y[1:]).sum() < 2:
                raise ValueError(f"saved series has too few finite points: {key}")
            style = "--" if key == "log10_C_t_beta_forward" else "-"
            ax.plot(t, y, label=label, color=color, linestyle=style, linewidth=1.8)
        ax.grid(alpha=0.25)
        ax.legend(loc="best", frameon=False)
        ax.set_ylabel("log₁₀(saved quantity)")
    axes[0].set_title("Saved conditional n/T stocks and beta-decay events\nquotient_L16_S-0.6_Am0_Ar0")
    axes[0].text(0.012, 0.04, "t = 0: exact zero (−∞), omitted from log-value curves", transform=axes[0].transAxes, fontsize=8)
    axes[1].set_xlabel("Saved elapsed proper time (s); not cosmic age")
    axes[1].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
    fig.get_layout_engine().set(rect=(0, 0.075, 1, 0.925))
    fig.text(0.5, 0.015, "18-family all-bare, instantaneously thermalized, passive-reservoir sensitivity; separate from ANGTHERM01 ionic histories.", ha="center", fontsize=8)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=OUTPUTS / "nt_saved_projection.json")
    parser.add_argument("--output", type=Path, default=OUTPUTS / "nt_saved_projection.png")
    args = parser.parse_args()
    render(args.source, args.output)
    print(json.dumps({"figure": str(args.output), "source": str(args.source)}))


if __name__ == "__main__":
    main()
