"""Render two HE34-SCR figure pairs from immutable saved results only.

No solver, transport calculation, IVP, or benchmark is imported or executed.
Matching input/code/environment/output identities reuse both existing pairs.
Execution attempts, failures, exact hashes, and layout checks are preserved.
"""

from contextlib import redirect_stderr, redirect_stdout
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shlex
import sys
import tempfile
import time
import traceback


UNIT = Path(__file__).resolve().parent
EVIDENCE = UNIT / "evidence" / "PLOT_EXECUTION.json"
INPUT_NAMES = (
    "results/MECHANICAL_CONTROLS.json",
    "results/NEUTRAL_H_HE_s07_m03_r03.csv",
    "results/NEUTRAL_TRANSPORT.json",
)
FIGURE_STEMS = ("MECHANICAL_ERROR_CERTIFICATE", "NEUTRAL_TRANSPORT_DIAGNOSTIC")
OUTPUT_NAMES = tuple(f"figures/{stem}.{suffix}" for stem in FIGURE_STEMS for suffix in ("png", "svg"))
FONT_PT = 10.5
WIDTH_MM = 90.0
PNG_DPI = 300


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _save_pair(fig, stem):
    directory = UNIT / "figures"
    directory.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg"):
        target = directory / f"{stem}.{suffix}"
        descriptor, temporary = tempfile.mkstemp(prefix=target.stem+".", suffix="."+suffix, dir=directory)
        os.close(descriptor)
        try:
            metadata = ({"Software": "HE34-SCR saved-results plotter"} if suffix == "png"
                        else {"Date": None, "Creator": "HE34-SCR saved-results plotter"})
            fig.savefig(temporary, format=suffix, dpi=PNG_DPI, facecolor="white",
                        bbox_inches=None, pad_inches=0.0, metadata=metadata)
            with open(temporary, "rb") as handle:
                os.fsync(handle.fileno())
            os.replace(temporary, target)
            print(f"SAVED {target.relative_to(UNIT)}", flush=True)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def _check_layout(fig, name, legends=()):
    """Verify all visible text lies inside the actual uncropped figure canvas."""
    from matplotlib.text import Text

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width, height = fig.bbox.width, fig.bbox.height
    clipped, sizes, checked = [], [], 0
    for artist in fig.findobj(match=Text):
        if not artist.get_visible() or not artist.get_text().strip():
            continue
        bbox = artist.get_window_extent(renderer)
        if bbox.width <= 0.0 or bbox.height <= 0.0:
            continue
        checked += 1
        sizes.append(float(artist.get_fontsize()))
        if bbox.x0 < -0.5 or bbox.y0 < -0.5 or bbox.x1 > width+0.5 or bbox.y1 > height+0.5:
            clipped.append({"text": artist.get_text(), "bbox_pixels": list(map(float, bbox.bounds))})
    legend_overlaps = []
    for legend in legends:
        bbox = legend.get_window_extent(renderer)
        for j, axis in enumerate(fig.axes):
            if bbox.overlaps(axis.get_window_extent(renderer)):
                legend_overlaps.append(j)
    report = {"figure": name, "width_mm": float(fig.get_figwidth()*25.4),
              "height_mm": float(fig.get_figheight()*25.4), "font_min_pt": min(sizes),
              "visible_text_items_checked": checked, "clipped_text": clipped,
              "legend_overlapping_data_axes": legend_overlaps,
              "save_policy": "fixed 90 mm canvas; no bbox_inches=tight resizing"}
    if clipped or legend_overlaps or min(sizes) < 10.0:
        raise ValueError(f"layout check failed: {json.dumps(report)}")
    print(f"LAYOUT PASS {name}: {checked} visible text items, minimum {min(sizes):g} pt", flush=True)
    return report


def _load_inputs():
    import numpy as np

    mechanical = json.loads((UNIT / INPUT_NAMES[0]).read_text())
    transport = json.loads((UNIT / INPUT_NAMES[2]).read_text())
    with (UNIT / INPUT_NAMES[1]).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if _sha(UNIT / INPUT_NAMES[1]) != transport["csv"]["sha256"]:
        raise ValueError("neutral CSV does not match its saved transport manifest")
    if mechanical["input"]["source_npz_sha256"] != transport["background"]["sha256"]:
        raise ValueError("mechanical and neutral results do not use the same saved background")
    runs = sorted(mechanical["runs"], key=lambda run: run["chi"])
    if [run["chi"] for run in runs] != [10.0, 100.0, 1000.0, 10000.0]:
        raise ValueError("mechanical controls differ from the four declared chi values")
    if [run["accepted_by_continuum_bound"] for run in runs] != [False, False, True, True]:
        raise ValueError("mechanical acceptance flags differ from the declared saved outcome")
    if mechanical["target"] != {"ratio_abs": 1.0e-6, "logp_abs": 1.0e-6}:
        raise ValueError("the fixed 1e-6 target changed")
    if transport["temperature_K"] != 20000.0 or transport["background"]["selected_species"] != ["H1_q0", "He4_q0"]:
        raise ValueError("neutral subset or common prescribed temperature changed")
    columns = {name: np.array([float(row[name]) for row in rows]) for name in
               ("z", "eta_neutral_Pa_s", "chi_match")}
    if len(rows) != 201 or np.any(np.diff(columns["z"]) >= 0.0):
        raise ValueError("expected 201 saved epochs with decreasing mean redshift")
    if not math.isclose(columns["z"][0], 20.0, abs_tol=1.0e-12) or not math.isclose(columns["z"][-1], 2.0, abs_tol=1.0e-12):
        raise ValueError("the redshift endpoints changed")
    if any(not np.all(np.isfinite(column)) or np.any(column <= 0.0) for column in columns.values()):
        raise ValueError("plot input has a nonfinite or nonpositive value")
    fields = ("max_ratio_error_at_saved_nodes", "max_logp_error_at_saved_nodes",
              "max_ratio_continuum_bound", "final_logp_continuum_bound")
    if any(not math.isfinite(run[key]) or run[key] <= 0.0 for run in runs for key in fields):
        raise ValueError("mechanical logarithmic plot inputs must be finite and positive")
    return mechanical, transport, runs, columns


def _style_axis(axis):
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(which="both", direction="out", width=0.7, pad=3.0)
    axis.grid(axis="y", which="major", color="0.88", linewidth=0.55)
    axis.set_axisbelow(True)


def _mechanical_figure(runs):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, LogFormatterMathtext, NullLocator

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(WIDTH_MM/25.4, 150.0/25.4))
    fig.subplots_adjust(left=0.245, right=0.965, bottom=0.285, top=0.975, hspace=0.13)
    chi = [run["chi"] for run in runs]
    handles = None
    for axis, observed, bound, ylabel in zip(axes,
            ("max_ratio_error_at_saved_nodes", "max_logp_error_at_saved_nodes"),
            ("max_ratio_continuum_bound", "final_logp_continuum_bound"),
            ("Absolute ratio error", "Absolute log-pressure error")):
        envelope, = axis.loglog(chi, [run[bound] for run in runs], color="#D55E00",
            linestyle="--", linewidth=1.35, marker="s", markersize=6.2,
            markerfacecolor="white", markeredgewidth=1.1, zorder=3, label="Continuum envelope")
        observed_line, = axis.loglog(chi, [run[observed] for run in runs], color="#0072B2",
            linestyle="-", linewidth=1.25, marker="o", markersize=3.7,
            markeredgewidth=0.6, zorder=4, label="Max. saved-node error")
        target = axis.axhline(1.0e-6, color="0.35", linestyle=":", linewidth=1.25,
                             zorder=2, label=r"Fixed $10^{-6}$ target")
        axis.set_ylim(5.0e-10, 2.0e-2)
        axis.set_xlim(5.0, 2.4e4)
        axis.set_ylabel(ylabel, labelpad=3.0)
        axis.yaxis.set_major_locator(FixedLocator([1.0e-8, 1.0e-6, 1.0e-4, 1.0e-2]))
        axis.yaxis.set_major_formatter(LogFormatterMathtext())
        axis.xaxis.set_minor_locator(NullLocator())
        axis.yaxis.set_minor_locator(NullLocator())
        _style_axis(axis)
        handles = [observed_line, envelope, target]
    axes[-1].set_xticks(chi, [r"$10^1$"+"\nrejected", r"$10^2$"+"\nrejected",
                             r"$10^3$"+"\naccepted", r"$10^4$"+"\naccepted"])
    axes[-1].set_xlabel(r"Prescribed $\chi$", labelpad=5.0)
    legend = fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.53, 0.018),
                        frameon=False, ncol=1, handlelength=2.2, handletextpad=0.7,
                        borderaxespad=0.0, labelspacing=0.35)
    layout = _check_layout(fig, FIGURE_STEMS[0], (legend,))
    _save_pair(fig, FIGURE_STEMS[0])
    plt.close(fig)
    return layout


def _neutral_figure(columns):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, LogFormatterMathtext, NullLocator

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(WIDTH_MM/25.4, 145.0/25.4))
    fig.subplots_adjust(left=0.245, right=0.965, bottom=0.215, top=0.975, hspace=0.13)
    z = columns["z"]
    axes[0].plot(z, 1.0e4*columns["eta_neutral_Pa_s"], color="#0072B2", linewidth=1.4,
                 linestyle="-", marker="o", markersize=3.5, markevery=20, markeredgewidth=0.6)
    axes[0].set_ylabel(r"$\eta_{\rm neutral}$ ($10^{-4}$ Pa s)", labelpad=5.0)
    axes[0].set_ylim(1.95, 4.65)
    axes[0].set_yticks([2.0, 3.0, 4.0])
    axes[0].text(0.035, 0.965, "Neutral ¹H + ⁴He only\nCommon T = 20 000 K",
                 transform=axes[0].transAxes, ha="left", va="top", linespacing=1.3)
    axes[1].semilogy(z, columns["chi_match"], color="#D55E00", linewidth=1.4,
                     linestyle="--", marker="s", markersize=3.8, markevery=20,
                     markerfacecolor="white", markeredgewidth=0.9)
    axes[1].axhline(1.0, color="0.35", linestyle=":", linewidth=1.25)
    axes[1].text(19.4, 1.7, r"$\chi=1$ (diagnostic)", ha="left", va="bottom", color="0.25")
    axes[1].set_ylabel(r"$\chi_{\rm match}=\nu_{\rm match}/H$", labelpad=5.0)
    axes[1].set_ylim(5.0e-4, 1.0e5)
    axes[1].yaxis.set_major_locator(FixedLocator([1.0e-3, 1.0e-1, 1.0e1, 1.0e3, 1.0e5]))
    axes[1].yaxis.set_major_formatter(LogFormatterMathtext())
    axes[1].yaxis.set_minor_locator(NullLocator())
    axes[1].set_xlabel(r"Mean redshift, $\bar z$", labelpad=5.0)
    axes[1].set_xlim(20.0, 2.0)
    axes[1].set_xticks([20.0, 15.0, 10.0, 5.0, 2.0])
    for axis in axes:
        _style_axis(axis)
    fig.text(0.245, 0.028, "Matching diagnostic only;\nχ = 1 is not a fluid certificate.",
             ha="left", va="bottom", linespacing=1.3)
    layout = _check_layout(fig, FIGURE_STEMS[1])
    _save_pair(fig, FIGURE_STEMS[1])
    plt.close(fig)
    return layout


def main():
    started, clock_start = _utc(), time.perf_counter()
    stdout_buffer, stderr_buffer = io.StringIO(), io.StringIO()
    existing = json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {}
    attempts = existing.get("attempts", [])
    overrides = {key: os.environ[key] for key in ("PYTHONDONTWRITEBYTECODE", "MPLBACKEND", "MPLCONFIGDIR") if key in os.environ}
    command = " ".join([*(f"{key}={shlex.quote(value)}" for key, value in overrides.items()),
                         shlex.join(getattr(sys, "orig_argv", [sys.executable, *sys.argv]))])
    attempt = {"started_utc": started, "command": command, "cwd": str(Path.cwd()),
               "argv": getattr(sys, "orig_argv", [sys.executable, *sys.argv]),
               "environment_overrides": overrides, "new_render_pairs": 0,
               "new_png_files": 0, "new_svg_files": 0, "reused_render_pairs": 0,
               "old_HE32_renders_repeated": 0, "new_IVPs": 0, "new_benchmarks": 0}
    code = {"plot_results.py": _sha(Path(__file__))}
    inputs, outputs, layout_reports = {}, {}, []
    identity, environment, exit_code = None, {}, 0
    matching_outputs = False
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.font_manager as fm
            import numpy as np
            import PIL
            from PIL import Image

            font = Path(fm.findfont("DejaVu Sans", fallback_to_default=False))
            environment = {"python": sys.version, "executable": sys.executable,
                           "platform": platform.platform(), "matplotlib": matplotlib.__version__,
                           "numpy": np.__version__, "pillow": PIL.__version__, "backend": matplotlib.get_backend(),
                           "font": {"family": "DejaVu Sans", "path": str(font), "sha256": _sha(font)},
                           "font_size_pt": FONT_PT, "png_dpi": PNG_DPI}
            inputs = {name: _sha(UNIT/name) for name in INPUT_NAMES}
            fingerprint = {"inputs": inputs, "code": code,
                           "render_environment": {key: environment[key] for key in
                               ("matplotlib", "numpy", "pillow", "backend", "font_size_pt", "png_dpi")},
                           "font_sha256": environment["font"]["sha256"]}
            identity = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()
            matching_outputs = all((UNIT/name).is_file() and _sha(UNIT/name) == existing.get("outputs", {}).get(name, {}).get("sha256")
                                   for name in OUTPUT_NAMES)
            if existing.get("cache_identity") == identity and existing.get("status") == "passed" and matching_outputs:
                attempt["reused_render_pairs"] = 2
                outputs, layout_reports = existing["outputs"], existing["layout_checks"]
                print("REUSE: inputs, code, render environment, and all four output hashes match; no renderer invoked.", flush=True)
            else:
                attempt["render_reason"] = "no matching complete content-identified figure cache"
                mechanical, transport, runs, columns = _load_inputs()
                matplotlib.rcParams.update({"font.family": "DejaVu Sans", "font.size": FONT_PT,
                    "axes.labelsize": FONT_PT, "axes.titlesize": FONT_PT,
                    "xtick.labelsize": FONT_PT, "ytick.labelsize": FONT_PT,
                    "legend.fontsize": FONT_PT, "figure.dpi": 100.0,
                    "axes.linewidth": 0.7, "svg.fonttype": "none", "svg.hashsalt": identity,
                    "savefig.bbox": None, "mathtext.fontset": "dejavusans"})
                layout_reports.append(_mechanical_figure(runs))
                attempt["new_render_pairs"] += 1
                attempt["new_png_files"] += 1
                attempt["new_svg_files"] += 1
                layout_reports.append(_neutral_figure(columns))
                attempt["new_render_pairs"] += 1
                attempt["new_png_files"] += 1
                attempt["new_svg_files"] += 1
                for name in OUTPUT_NAMES:
                    path = UNIT/name
                    outputs[name] = {"sha256": _sha(path), "bytes": path.stat().st_size}
                    if path.suffix == ".png":
                        with Image.open(path) as image:
                            outputs[name]["pixels"] = list(image.size)
                print("COMPLETE: exactly two new figure pairs from saved results; no IVP, transport solve, or benchmark.", flush=True)
        except Exception:
            exit_code = 1
            traceback.print_exc()
    attempt.update({"ended_utc": _utc(), "wall_seconds": time.perf_counter()-clock_start,
                    "exit_code": exit_code, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue(),
                    "inputs_sha256": inputs, "code_sha256": code, "cache_identity": identity,
                    "outputs": outputs, "environment": environment})
    attempts.append(attempt)
    evidence = {"schema": "he34_scr.saved_results_plot_execution.v1",
                "status": "passed" if exit_code == 0 else "failed", "cache_identity": identity,
                "inputs_sha256": inputs, "code_sha256": code, "outputs": outputs,
                "layout_checks": layout_reports,
                "figure_semantics": {
                    FIGURE_STEMS[0]: "Maximum saved-node errors versus continuum envelopes; fixed 1e-6 target. Discrete chi=10,100 rejected and chi=1000,10000 accepted by the saved continuum bounds. No interpolation of acceptance status is asserted.",
                    FIGURE_STEMS[1]: "Saved mean-redshift trajectory from 20 to 2; neutral H1/He4 subset, prescribed common T=20000 K. eta shown in 1e-4 Pa s; chi_match is hydrodynamic matching. The chi=1 line is diagnostic and is not a fluid-validity certificate."},
                "cumulative_counts": {key: sum(item.get(key, 0) for item in attempts) for key in
                    ("new_render_pairs", "new_png_files", "new_svg_files", "reused_render_pairs",
                     "old_HE32_renders_repeated", "new_IVPs", "new_benchmarks")},
                "attempts": attempts}
    if existing.get("visual_inspection") and existing.get("cache_identity") == identity and matching_outputs:
        evidence["visual_inspection"] = existing["visual_inspection"]
    _atomic_json(EVIDENCE, evidence)
    sys.stdout.write(attempt["stdout"])
    sys.stderr.write(attempt["stderr"])
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
