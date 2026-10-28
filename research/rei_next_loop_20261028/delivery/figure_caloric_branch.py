"""Four-panel scientific figure from the accepted represented-law run.

Presentation only. Requires the preserved C7 calibration output and its
terminal supervisor record; never substitutes a physical recipient EOS.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import resource
import time


def q(record: dict) -> Fraction:
    return Fraction(int(record["num"]), int(record["den"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--supervisor", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()
    t0 = time.monotonic()
    r0 = resource.getrusage(resource.RUSAGE_SELF)
    data = json.loads(args.result.read_text())
    supervisor = json.loads(args.supervisor.read_text())
    if supervisor.get("status") != "EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION" or supervisor.get("exit_code") != 0:
        raise ValueError("A terminal, zero-exit calibration record is required")
    counts = data.get("manufactured_test_counts", {})
    if not counts.get("run") or counts.get("errors") != 0 or counts.get("failures") != 0:
        raise ValueError("Manufactured checks were not observed to pass")
    if data.get("status") != "REPRESENTED_SOURCE_CALIBRATION_ONLY":
        raise ValueError("Saved-source calibration output absent")
    if any(data.get(k) is not None for k in ("physical_temperature_interval", "actual_recipient_temperature", "actual_native25", "physical_radii")):
        raise ValueError("This figure assumes physical results remain null")
    if data.get("full_state_update") is not False or data.get("L4_ready") is not False or data.get("global_physical_completion") is not None:
        raise ValueError("Physical state/gate scope mismatch")
    E, D, cv, Ts = (q(data["operands"][key]) for key in ("E", "D", "cv", "saved_T"))
    if Ts != q(data["inverse_T"]) or Ts != q(data["independent_ideal_quotient_T"]) or E != cv * D * Ts:
        raise ValueError("C7 exact calibration identity mismatch")
    if data.get("represented_temperature_interval") != [data["inverse_T"], data["inverse_T"]]:
        raise ValueError("Represented interval mismatch")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    ink = "#14253b"
    blue = "#176f9e"
    orange = "#df7a35"
    pale = "#e6f3f8"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.edgecolor": "#8293a2", "axes.labelcolor": ink,
                         "text.color": ink, "xtick.color": ink, "ytick.color": ink,
                         "savefig.facecolor": "white"})
    fig, axs = plt.subplots(2, 2, figsize=(11.4, 7.2), constrained_layout=True)
    fig.suptitle("Supplied caloric branch: exact inverse and conditional enclosure", fontsize=16, fontweight="bold")
    ax = axs[0, 0]
    ax.plot([1, 2, 4], [2, 4, 10], color=blue, lw=2.5, marker="o", label=r"$F_0(T)$")
    ax.axhspan(4, 7, color=pale, zorder=0)
    ax.axvspan(2, 3, color=orange, alpha=.13, zorder=0)
    ax.hlines([4, 7], 1, 4, colors=orange, linestyles="dashed", linewidth=.9)
    ax.text(1.1, 7.3, r"$[E_{lo}-\eta,E_{hi}+\eta]=[4,7]$", fontsize=9, color=orange)
    ax.text(2.18, 2.8, r"$T_*\in[2,3]$", fontsize=10, color=ink)
    ax.set(xlim=(.9, 4.1), ylim=(1.4, 10.8), xlabel="Temperature T (K)", ylabel="Energy F (J / reference volume)",
           title="A  Exact manufactured inverse")
    ax.legend(frameon=False, loc="lower right")

    ax = axs[0, 1]
    xx = [1 + 2*i/200 for i in range(201)]
    actual = [x*x for x in xx]
    represented = [4*x-3 for x in xx]
    ax.plot(xx, actual, color=blue, lw=2.5, label=r"Actual manufactured $F_*=T^2$")
    ax.plot(xx, represented, color=orange, lw=2, label=r"Secant $F_0=4T-3$")
    ax.fill_between(xx, actual, represented, color=orange, alpha=.17)
    ax.hlines(4, 1, 3, color=ink, linestyle="dashed", lw=1)
    ax.axvspan(1.5, 2, color=pale, zorder=0)
    ax.plot([2], [4], "o", color=blue)
    ax.text(1.05, 7.7, r"$\eta=1,\ E=4$", fontsize=10)
    ax.text(1.51, 2, r"$T_*=2\in[3/2,2]$", fontsize=10)
    ax.set(xlim=(1, 3), ylim=(1, 9.5), xlabel="Temperature T (K)", ylabel="Energy (arbitrary manufactured units)",
           title="B  Nonlinear inclusion check")
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)

    ax = axs[1, 0]
    ts = float(Ts)
    ax.plot([0, 1.3], [0, 1.3], color=blue, lw=2.5)
    ax.plot([1], [1], "o", ms=8, color=orange)
    ax.axvline(1, color=orange, linestyle="dashed", lw=.8)
    ax.axhline(1, color=orange, linestyle="dashed", lw=.8)
    ax.text(.05, 1.13, r"$F_0(T)=c_vDT$, saved $E=c_vDT_{C7}$", fontsize=10)
    ax.text(.05, 1.02, r"$F_0^{-1}(E)=E/(c_vD)=T_{C7}$ (exact)", fontsize=10)
    ax.text(.05, .09, f"Saved C7 T = {ts:.8g} K; represented-law calibration only", fontsize=9)
    ax.set(xlim=(0, 1.3), ylim=(0, 1.3), xlabel=r"$T/T_{C7}$", ylabel=r"$F_0(T)/E_{C7}$",
           title="C  Preserved C7 source operands")

    ax = axs[1, 1]
    names = ["Working", "Central"]
    completed = [33, 28]
    ax.barh(names, [88, 88], color="#e5eaee", height=.52, label="Original 88 nodes")
    ax.barh(names, completed, color=[blue, orange], height=.52, label="Existing scoped status")
    for y, n in zip(names, completed):
        ax.text(n + 1.1, y, f"{n}/88", va="center", fontweight="bold")
    ax.set(xlim=(0, 91), xlabel="Original DAG nodes", title="D  Original DAG status unchanged")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
    # The two bars and counts carry the comparison without a low-edge legend.
    for panel in axs.flat:
        panel.grid(alpha=.13, axis="both")
        panel.set_axisbelow(True)
    fig.text(.5, -.02, "Enclosures require supplied uncertainty bounds; actual recipient EOS, physical radii and completion remain unresolved.",
             ha="center", fontsize=9, color="#566477")
    prefix = args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(prefix.with_suffix("."+extension), dpi=165, bbox_inches="tight")
    plt.close(fig)
    r1 = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"figure_png": str(prefix.with_suffix(".png")), "figure_svg": str(prefix.with_suffix(".svg")),
                      "source_calibration": str(args.result), "manufactured_checks": counts,
                      "cpu_s": (r1.ru_utime+r1.ru_stime)-(r0.ru_utime+r0.ru_stime),
                      "wall_s": time.monotonic()-t0, "physical_claim": None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
