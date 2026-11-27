"""Render already saved samples; never call the source evaluator."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]


def main():
    src = BASE / "registry/fit_diagnostics.json"
    data = json.loads(src.read_text())
    reference_path = BASE / "raw/INDEPENDENT_RESULTS.json"
    reference = json.loads(reference_path.read_text())
    if reference["status"] != "PASS_SCOPED":
        raise ValueError("INDEPENDENT_REFERENCE_NOT_ACCEPTED")
    refs = next(g["detail"]["rows"] for g in reference["groups"] if g["id"].startswith("G5_"))
    refs = {(r["provider_id"], r["row_id"]): r for r in refs}
    panels = [("BENNETT2003", "LiH spontaneous association", "27 original table nodes"),
              ("GONZALEZ_LEZANA2022", "Thermal HD destruction", "2 printed SQM comparison points")]
    fig, axs = plt.subplots(2, 2, figsize=(11.6, 7.7), constrained_layout=True,
                            gridspec_kw={"height_ratios": [1.4, 1]})
    for column, (prefix, title, scope) in enumerate(panels):
        rows = [r for r in data["rows"] if r["provider_id"].startswith(prefix)]
        T = [float(r["native_T_literal"]) for r in rows]
        table = [r["native_k_float"] for r in rows]
        fit = [r["k_cm3_s"] for r in rows]
        residual = [100 * r["signed_relative_residual"] for r in rows]
        fit_residual = [100 * float(refs[(r["provider_id"], r["native_row_id"])]["r_fit_saved_binary64"]) for r in rows]
        a, e = axs[0, column], axs[1, column]
        a.scatter(T, table, color="#214f73", s=30, label="Printed source values", zorder=3)
        a.scatter(T, fit, color="#b65b31", s=35, marker="x", label="Published formula samples", zorder=4)
        a.set_title(title + "\n" + scope, loc="left", fontsize=12)
        a.set_ylabel(r"Coefficient (cm$^3$ s$^{-1}$)")
        a.set_yscale("log")
        a.legend(loc="best", fontsize=9)
        e.axhline(0, color="#59636b", linewidth=1)
        e.scatter(T, residual, color="#6f4c83", s=30, label="Printed value denominator")
        e.scatter(T, fit_residual, edgecolors="#2d8175", facecolors="none", marker="^", s=40, label="Formula denominator")
        e.set_ylabel("(Formula − printed value) / denominator (%)")
        e.set_xlabel("Kinetic temperature (K)")
        worst = max(rows, key=lambda r: abs(r["signed_relative_residual"]))
        e.text(0.03, 0.97, f"Max |table-normalized residual|: {100*abs(worst['signed_relative_residual']):.3f}%\nat {float(worst['native_T_literal']):g} K", transform=e.transAxes, fontsize=9, va="top", bbox={"facecolor":"white", "edgecolor":"none", "alpha":0.85})
        e.legend(loc="lower right", fontsize=8)
        for axis in (a, e):
            axis.grid(alpha=0.2)
            if column == 0:
                axis.set_xscale("log")
    fig.suptitle("Source formula diagnostics at original nodes", fontsize=15)
    fig.supxlabel("Both residual denominators are explicit; neither is a physical uncertainty bound. No new fit or interpolation is performed.", fontsize=9)
    (BASE / "figures").mkdir(exist_ok=True)
    files = []
    for suffix in ("png", "svg"):
        dest = BASE / "figures" / ("source_fit_diagnostics." + suffix)
        if dest.exists():
            raise ValueError("FIGURE_EXISTS_REUSE_WITH_INPUT_IDENTITY")
        fig.savefig(dest, dpi=160)
        files.append({"path": str(dest.relative_to(BASE)), "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(), "bytes": dest.stat().st_size})
    plt.close(fig)
    record = {"source": str(src.relative_to(BASE)), "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
              "independent_reference": str(reference_path.relative_to(BASE)), "independent_reference_sha256": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
              "files": files, "new_source_formula_evaluations": 0, "sample_points": 29,
              "interpolation_or_extrapolation": False, "physical_uncertainty_interpretation": False}
    (BASE / "figures/FIGURE_MANIFEST.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
