"""Plot admitted callback raw values and the preserved finite-difference repair record.

This renderer does not import or call the native solver, donor reader, source
provider, or check runner. Run only after the targeted repair has raw results
and independent admission. Inputs remain separate and unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


SPECIES = ("n", "H1I", "H1II", "DI", "DII", "TI", "TII", "He3I", "He3II", "He3III",
           "He4I", "He4II", "He4III", "Li6I", "Li6II", "Li6III", "Li6IV",
           "Li7I", "Li7II", "Li7III", "Li7IV")
FD_NAMES = ("full_native_hydrogen_electron_feedback_JVP",
            "native_hydrogen_electron_feedback_electron_tangent")
FD_LIMIT = 2e-8


def _load(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _finite_vector(values: list, n: int, label: str) -> list[float]:
    if len(values) != n or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("Invalid recorded " + label)
    return values


def _fd(checks: dict) -> list[float]:
    indexed = {entry["name"]: entry for entry in checks["checks"]}
    result = []
    for name in FD_NAMES:
        check = indexed[name]
        if check["limit"] != FD_LIMIT or not math.isfinite(check["residual"]) or check["residual"] <= 0:
            raise ValueError("Invalid recorded finite-difference check: " + name)
        result.append(check["residual"])
    return result


def _plot_signed(ax, values: list[float], title: str):
    # The positive/negative sign is encoded in marker shape; the y coordinate
    # is magnitude for display only, with exact signed values kept in raw JSON.
    positive = [(i, abs(v)) for i, v in enumerate(values) if v > 0]
    negative = [(i, abs(v)) for i, v in enumerate(values) if v < 0]
    for points, marker, color, label in ((positive, "o", "#156a92", "positive"),
                                          (negative, "v", "#ba603d", "negative")):
        if points:
            ax.scatter([x for x, _ in points], [y for _, y in points], marker=marker,
                       color=color, s=48, label=label, zorder=3)
    ax.set_yscale("log")
    ax.set_xticks(range(21), SPECIES, rotation=70, ha="right", fontsize=7)
    ax.set_ylabel(r"$|dY_i/dt|$ [proper s$^{-1}$]")
    ax.set_title(title)
    ax.text(.02, .04, f"Recorded exact zeros: {values.count(0)} / 21", transform=ax.transAxes,
            fontsize=8, color="#53606d")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    ax.grid(axis="y", alpha=.18)
    ax.set_axisbelow(True)


def render(admitted_raw: Path, failed_checks: Path, repair_record: Path, output_prefix: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw, raw_sha = _load(admitted_raw)
    historical, historical_sha = _load(failed_checks)
    repaired, repaired_sha = _load(repair_record)
    snapshot, source = raw["snapshot"], raw["source"]
    if snapshot["source_z"] != 2.479 or source["route"] != "PW19_z2.479_HeII_exclusive":
        raise ValueError("Expected matched PW19 exact source z=2.479")
    if snapshot["representation"] != "adjacent_convex_eta_on_saved_x_and_T" or not snapshot["not_a_new_trajectory"]:
        raise ValueError("Expected labelled finite adjacent-snapshot representation")
    on = _finite_vector(raw["native_on"]["dY_dt"], 21, "full native RHS")
    delta = _finite_vector(raw["source_on_off_dY_dt"], 21, "recorded PW19 source-on/off delta")
    old_fd = _fd(historical)
    repair_tests = {entry["name"]: entry for entry in repaired["tests"]}
    new_fd = [repair_tests[name]["new_residual"] for name in FD_NAMES]
    if (historical["passed"] is not False or repaired["pass"] is not True or
        repaired["combined_evidence_passing_count"] != 84 or
        repaired["original_run01"]["reused_passing_checks"] != 82 or
        repaired["original_run01"]["callback_sha256"] != raw_sha or
        repaired["original_run01"]["checks_sha256"] != historical_sha or
        repaired["source_z"] != snapshot["source_z"] or
        repaired["source_or_native_physics_changed"] is not False or
        repaired["original_run01_rewritten"] is not False or
        repaired["old_h"] != 1e-4 or repaired["new_h"] != 1e-2 or
        any(repair_tests[name]["old_residual"] != old_fd[i] or
            repair_tests[name]["unchanged_limit"] != FD_LIMIT or
            repair_tests[name]["pass"] is not True or
            not math.isfinite(new_fd[i]) or new_fd[i] <= 0
            for i, name in enumerate(FD_NAMES))):
        raise ValueError("Expected preserved failed run and admitted repaired check record")
    total = raw["ledger"]["total"]
    powers = [total[key] for key in ("binding_W_m3", "primary_W_m3", "external_radiation_W_m3")]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in powers):
        raise ValueError("Invalid raw source-energy ledger")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 9.8))
    _plot_signed(axes[0, 0], on, "Full native REC 21-state abundance RHS")
    _plot_signed(axes[0, 1], delta, "PW19 source-on/off abundance difference")

    ax = axes[1, 0]
    labels = ("Ionization binding", "Primary electron", "Prescribed radiation")
    ax.barh(range(3), powers, color=("#377f9e", "#789b46", "#b96343"), height=.55)
    ax.set_yticks(range(3), labels)
    ax.invert_yaxis()
    ax.axvline(0, color="#52606e", lw=.8)
    ax.set_xlabel(r"Recorded signed power [W m$^{-3}$]")
    ax.set_title("Selected He II energy partner; primary is not heat")
    ax.grid(axis="x", alpha=.18)
    ax.set_axisbelow(True)

    ax = axes[1, 1]
    for i, (old, new) in enumerate(zip(old_fd, new_fd)):
        ax.scatter(i-.12, old, color="#b96343", marker="x", s=90,
                   label="Preserved run01 failure" if i == 0 else None, zorder=3)
        ax.scatter(i+.12, new, color="#267e74", marker="o", s=65,
                   label="Targeted repair raw result" if i == 0 else None, zorder=3)
    ax.axhline(FD_LIMIT, color="#575e67", ls="--", lw=1.1, label="Frozen 2×10⁻⁸ criterion")
    ax.set_yscale("log")
    ax.set_xticks((0, 1), ("Full H/e feedback JVP", "Electron tangent"))
    ax.set_ylabel("Recorded scaled FD residual")
    ax.set_title("h: 10⁻⁴ → 10⁻²; unchanged tolerance")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=.18)
    ax.set_axisbelow(True)

    fig.suptitle("Actual PW19 source in native REC callback", fontsize=16, weight="bold", y=.985)
    fig.text(.5, .955, f"Source and matched donor snapshot z = 2.479 · T = {snapshot['temperature_K']:.6g} K · "
             "finite adjacent-η interpolation on saved abundances and T", ha="center", color="#52606e")
    fig.text(.5, .025, "ElementalElectronicEquality for He-3/He-4 is conditional; this is a local finite counterfactual snapshot.\n"
             "No isotope-calibrated rate, time history, CMB observable, gas heat, or evolved radiation backreaction is inferred.",
             ha="center", va="bottom", fontsize=8.5, color="#52606e")
    fig.subplots_adjust(left=.14, right=.975, top=.91, bottom=.12, hspace=.58, wspace=.32)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for ext in ("png", "pdf", "svg"):
        dest = output_prefix.with_suffix("." + ext)
        fig.savefig(dest, dpi=170, facecolor="white",
                    metadata={"Creator": "REC PW19 raw-callback renderer"} if ext == "pdf" else None)
        payload = dest.read_bytes()
        outputs[ext] = {"path": str(dest), "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest()}
    plt.close(fig)
    return {"status": "presentation_of_admitted_local_callback_raw_result", "presentation_only": True,
            "science_evaluations": 0,
            "input_sha256": {"native_callback_run01": raw_sha, "preserved_failed_checks": historical_sha,
                             "targeted_repair": repaired_sha}, "outputs": outputs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("admitted_raw", type=Path)
    parser.add_argument("failed_checks", type=Path)
    parser.add_argument("repair_record", type=Path)
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.admitted_raw, args.failed_checks, args.repair_record, args.output_prefix), indent=2))
