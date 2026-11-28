#!/usr/bin/env python3
"""Render or reuse a hash-identified scientific PNG/SVG pair without rerunning moments."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import platform
import resource
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from run_diagnostic import ROOT, atomic_write, sha, utc_now, write_json


def main():
    start_ns = time.perf_counter_ns()
    started_utc = utc_now()
    numerical_receipt = json.loads((ROOT / "outputs/DIAGNOSTIC.json").read_text())
    assert numerical_receipt["status"] == "PASS_SCOPED"
    for row in numerical_receipt["payloads"]:
        assert sha(ROOT / row["path"]) == row["sha256"]
    source = json.loads((ROOT / "outputs/ccc_moments.json").read_text())
    assert source["identity"] == numerical_receipt["identity"]
    code_inputs = {
        "render_script_sha256": sha(__file__),
        "helper_script_sha256": sha(ROOT / "run_diagnostic.py"),
        "contract_sha256": sha(ROOT / "CONTRACT.json"),
        "data_sha256": sha(ROOT / "outputs/ccc_moments.json"),
        "numerical_identity": numerical_receipt["identity"],
        "frozen_module_sha256": sha(ROOT / "vendor/maxwellian_moments.py"),
        "source_table_sha256": sha(ROOT / "data/CCC_TICS_1S.txt"),
        "python": platform.python_version(), "matplotlib": matplotlib.__version__,
        "numpy": np.__version__, "backend": matplotlib.get_backend(),
        "plot_contract": {"figsize_inches": [13.2, 5.7], "dpi": 180,
            "style": "DejaVu Sans; three panels; explicit finite-source caption",
            "physical_errorbars": False},
    }
    identity = hashlib.sha256(json.dumps(code_inputs, sort_keys=True).encode()).hexdigest()
    complete = ROOT / "plots/RENDER_RECEIPT.json"
    if complete.exists():
        prior = json.loads(complete.read_text())
        assert prior["identity"] == identity, "render identity changed; preserve completed files"
        for item in prior["outputs"]:
            assert sha(ROOT / item["path"]) == item["sha256"]
        cache_receipt = {"status": "REUSED_COMPLETE_RENDER", "identity": identity,
            "utc": utc_now(), "verified_output_count": 2, "new_renders": 0,
            "new_moment_evaluations": 0, "new_IVPs": 0,
            "elapsed_seconds": (time.perf_counter_ns() - start_ns) / 1e9}
        # Preserve every reuse invocation without touching the original render receipt.
        write_json(ROOT / "receipts" / ("RENDER_CACHE_HIT_" + str(time.time_ns()) + ".json"), cache_receipt)
        print(json.dumps(cache_receipt))
        return

    data = source["rows"]
    temperature = np.array([row["temperature_K"] for row in data])
    alpha = np.array([row["alpha_partial_m3_s"] for row in data])
    k2_ratio = np.array([row["kappa2_over_alpha"] for row in data])
    mean_energy = np.array([row["reaction_weighted_mean_energy_eV"] for row in data])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.0,
        "axes.titlesize": 12, "axes.labelsize": 11, "svg.hashsalt": identity,
        "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.7))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.29, top=0.78, wspace=0.33)
    colors = ["#17599D", "#AB4A19", "#18745B"]
    for ax, color, values in zip(axes, colors, (alpha, k2_ratio, mean_energy)):
        ax.plot(temperature, values, color=color, lw=2.25)
        ax.scatter([temperature[64]], [values[64]], color=color, s=30, zorder=4)
        ax.axvline(20000.0, color="#858585", lw=0.85, ls=(0, (3, 4)), alpha=0.75)
        ax.set_xscale("log")
        ax.set_xlim(2000.0, 200000.0)
        ax.set_xlabel("Temperature T [K]")
        ax.grid(True, which="major", color="#D8DEE5", lw=0.7)
        ax.tick_params(which="both", direction="out")
    axes[0].set_yscale("log")
    axes[0].set_ylabel(r"$\alpha_{\rm partial}$ [m$^3$ s$^{-1}$]")
    axes[0].set_title("(a) Finite-source reaction rate", loc="left")
    axes[1].set_yscale("log")
    axes[1].set_ylabel(r"$\kappa_2/\alpha = 4\gamma/(15\theta^2\alpha)$")
    axes[1].set_title("(b) Incoming-electron loss ratio", loc="left")
    axes[2].set_ylabel(r"$\langle E\rangle_{\rm reaction}=\beta/\alpha$ [eV]")
    axes[2].set_title("(c) Energy selected by reactions", loc="left")
    axes[2].axhline(13.6058, color="#777777", lw=0.9, ls=":")
    axes[2].text(0.02, 0.08, "Threshold: 13.6058 eV", transform=axes[2].transAxes,
                 color="#555555", fontsize=8.5)
    fig.suptitle("HE36  |  Hydrogen CCC finite-source Maxwellian moments", x=0.07,
                 y=0.965, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.07, 0.885,
        "129 unique temperatures  ·  positive piecewise-linear cross section  ·  GL16 per source interval",
        fontsize=11, color="#3E4C5C")
    fig.text(0.07, 0.155,
        r"Source interval: 13.6058–968.61 eV (87 rows). Heavy fixed target: μ = mₑ.  $\theta = k_B T$.  Markers: T = 20,000 K.",
        fontsize=10, color="#3E4C5C")
    fig.text(0.07, 0.105,
        "All curves are partial incoming moments; the high-energy tail and source interpolation error are unquantified.",
        fontsize=10, color="#3E4C5C")
    fig.text(0.07, 0.055,
        "κ₂ describes incoming-electron loss only. It is not the net CI pressure relaxation frequency. No IVP or closure activation.",
        fontsize=10, color="#3E4C5C")
    outputs = []
    for ext in ("png", "svg"):
        stream = io.BytesIO()
        metadata = {"Software": "HE36 finite-source moment diagnostic"} if ext == "png" else {
            "Date": None, "Creator": "HE36 finite-source moment diagnostic"}
        fig.savefig(stream, format=ext, dpi=180, facecolor="white", metadata=metadata)
        dest = ROOT / "plots" / ("ccc_finite_moments." + ext)
        atomic_write(dest, stream.getvalue())
        outputs.append({"path": str(dest.relative_to(ROOT)), "sha256": sha(dest),
                        "bytes": dest.stat().st_size})
    plt.close(fig)
    receipt = {
        "schema": "he36.render_receipt.v1", "status": "RENDERED_NEW",
        "identity": identity, "inputs": code_inputs, "started_utc": started_utc,
        "completed_utc": utc_now(), "outputs": outputs,
        "elapsed_seconds": (time.perf_counter_ns() - start_ns) / 1e9,
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "new_renders": 1, "files_rendered": 2, "new_moment_evaluations": 0,
        "new_IVPs": 0, "visual_inspection": "PENDING_SEPARATE_RECEIPT",
    }
    write_json(complete, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
