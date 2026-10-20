#!/usr/bin/env python3
"""Render three publication figures from existing BRPERF01 evidence only.

No simulation, scientific test suite, or benchmark is launched. Derived display
values are checked against retained summaries. All writes stay in figures/ and
figure_audit/. Relative evidence paths are recorded with byte hashes.
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import math
import os
import platform
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIT = ROOT / "figure_audit"
AUDIT.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(AUDIT / "mpl_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.ticker import NullLocator

SOURCES = {}
LAYOUT = {}
BLUE = "#176B9B"
ORANGE = "#B55C21"
GREEN = "#237C52"
GRAY = "#68727A"
BLACK = "#28333B"
NT_COLORS = {48: ORANGE, 96: GREEN, 192: BLUE}
NT_STYLES = {48: "--", 96: "-.", 192: "-"}
NT_MARKERS = {48: "o", 96: "s", 192: "^"}
WIDTH_IN = 180.0 / 25.4


def read_bytes(relative):
    path = ROOT / relative
    data = path.read_bytes()
    SOURCES[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    return data


def js(relative):
    return json.loads(read_bytes(relative))


def rows(relative):
    return list(csv.DictReader(read_bytes(relative).decode().splitlines()))


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=2e-13, abs_tol=1e-25), (a, b)


def summary(values):
    return {"median": statistics.median(values), "lo": min(values), "hi": max(values), "values": values}


def performance_data():
    rate_raw = rows("rates/evidence/BENCHMARK_ABBA.csv")
    rate_summary = js("rates/evidence/BENCHMARK_SUMMARY.json")
    rates = {}
    for candidate in ["legacy65537", "compact8193", "simd8193"]:
        values = []
        for block in range(6):
            selected = [r for r in rate_raw if r["candidate"] == candidate and int(r["block"]) == block]
            assert len(selected) == 4 and {int(r["queries"]) for r in selected} == {100000}
            a = [float(r["seconds"]) for r in selected if r["backend"] == "direct"]
            b = [float(r["seconds"]) for r in selected if r["backend"] == candidate]
            assert len(a) == len(b) == 2
            values.append(statistics.mean(a) / statistics.mean(b))
        rates[candidate] = summary(values)
        for key, actual in [("paired_speedup_median", rates[candidate]["median"]), ("paired_speedup_min", min(values)), ("paired_speedup_max", max(values))]:
            close(actual, rate_summary[candidate][key])
    native_base = "integration/evidence/native_rhs_abba_final"
    native_summary = js(native_base + "/RHS_TIMING_ANALYSIS.json")
    native_identity = js(native_base + "/IDENTITY.json")
    assert native_identity["binary_sha256"] == "957eb548de494c4f99eb6166846a338426d895f476e33297c2551599f5b81d81"
    per_process = collections.defaultdict(list)
    for process in range(5):
        raw = rows(native_base + f"/session_{process:02d}/RHS_TIMINGS.csv")
        for candidate in ["reused_direct", "legacy_65537", "compact_pchip", "compact_pchip_simd"]:
            pairs = []
            for pair in range(6):
                selected = [r for r in raw if r["comparison"] == candidate and int(r["pair"]) == pair]
                assert len(selected) == 4 and {int(r["iterations"]) for r in selected} == {32768}
                a = [float(r["seconds"]) / int(r["iterations"]) for r in selected if r["backend"] == "original_direct"]
                b = [float(r["seconds"]) / int(r["iterations"]) for r in selected if r["backend"] == candidate]
                assert len(a) == len(b) == 2
                if candidate == "reused_direct":
                    assert len({r["checksum"] for r in selected}) == 1
                pairs.append(statistics.mean(a) / statistics.mean(b))
            per_process[candidate].append(statistics.median(pairs))
    native = {key: summary(value) for key, value in per_process.items()}
    for key, value in native.items():
        rec = native_summary["comparisons"][key]
        close(value["median"], rec["median_process_speedup"])
        close(value["lo"], rec["process_speedup_range"][0])
        close(value["hi"], rec["process_speedup_range"][1])
    photon = {}
    for sign in ["minus", "plus"]:
        base = f"photon/evidence/bench_final_{sign}_r1"
        raw = rows(base + "/TIMINGS.csv")
        receipt = js(base + "/PYTHON_VERIFICATION.json")
        contract = js(base + "/CONTRACT.json")
        assert contract["templates"] == 384 and contract["unique_paths"] == 1824
        assert receipt["raw_byte_parity"] and receipt["ledger_raw_bytes_sha256"]
        assert len({r["checksum"] for r in raw}) == 1
        for mode in ["cached", "parallel"]:
            values = []
            for pair in range(7):
                selected = {int(r["position"]): r for r in raw if r["stage"] == "paired" and int(r["pair"]) == pair}
                assert len(selected) == 4
                if mode == "cached":
                    a, b = (0, 1) if pair % 2 == 0 else (3, 2)
                else:
                    a, b = (2, 3) if pair % 2 == 0 else (1, 0)
                assert selected[a]["mode"] == "baseline" and selected[b]["mode"] == mode
                values.append(float(selected[a]["seconds"]) / float(selected[b]["seconds"]))
            result = summary(values)
            result["median"] = math.exp(statistics.median(map(math.log, values)))
            for key, field in [("median", "median_log_speedup_exp"), ("lo", "min_pair_speedup"), ("hi", "max_pair_speedup")]:
                close(result[key], receipt["timing"][mode][field])
            photon[sign + "_" + mode] = result
    return {"rates": rates, "native": native, "photon": photon, "native_AA_controls": native_summary["AA_controls"]}


def accuracy_data():
    raw = rows("rates/evidence/RESOLUTION_SCAN.csv")
    legacy = js("rates/evidence/LEGACY_BASELINE.json")
    independent = js("rates/evidence/INDEPENDENT_PCHIP_VERIFICATION.json")
    result = [{"nodes": int(r["nodes"]), "bytes": int(r["storage_bytes"]), "error": float(r["max_relative_error"]), "legacy_error_on_same_probes": float(r["max_legacy_relative_error"]), "temperature_samples": int(r["samples"])} for r in raw]
    assert [r["nodes"] for r in result] == [1025, 2049, 4097, 8193]
    assert all(int(r["scalar_simd_mismatches"]) == 0 for r in raw)
    selected = result[-1]
    close(selected["error"], independent["sampled_error_selected"])
    assert result[-2]["error"] > 1e-4 > selected["error"]
    memory_reduction = 1.0 - selected["bytes"] / legacy["storage_bytes"]
    return {"compact": result, "legacy_nodes": legacy["nodes"], "legacy_bytes": legacy["storage_bytes"], "legacy_union_max_error": max(r["legacy_error_on_same_probes"] for r in result), "memory_reduction_fraction": memory_reduction, "target": 1e-4, "compiled_avx": legacy["compiled_avx"], "compiled_sse2": legacy["compiled_sse2"]}


def hot_data():
    base = "integration/evidence/science_8193"
    raw = rows(base + "/HISTORIES.csv")
    status = rows(base + "/HISTORY_STATUS.csv")
    differences = rows(base + "/BACKEND_DIFFERENCES.csv")
    time_grid = rows(base + "/TIME_GRID_DIFFERENCES.csv")
    analysis = js(base + "/INDEPENDENT_ANALYSIS.json")
    assert analysis["completed_histories"] == 45 and analysis["accepted_macrosteps"] == 5040
    assert all(r["status"] == "COMPLETE" for r in status)
    selected = collections.defaultdict(list)
    for r in raw:
        if r["case"] == "HOT_CI_60000" and r["backend"] in ["original_direct", "compact_pchip"]:
            selected[r["backend"], int(r["nsteps"])].append({k: (v if k in ["case", "backend", "status"] else float(v)) for k, v in r.items()})
    ev = 1.602176634e-19
    chi_h, chi_he1, chi_he2 = 13.598434599702, 24.587389011, 54.41776
    def binding(r):
        return ev * math.fsum([chi_h * r["N_HII"], chi_he1 * r["N_He4II"], (chi_he1 + chi_he2) * r["N_He4III"], (chi_h + .0037) * r["N_DII"]])
    output = {}
    for n in [48, 96, 192]:
        direct = selected["original_direct", n]
        compact = selected["compact_pchip", n]
        assert len(direct) == len(compact) == n + 1
        assert [r["step"] for r in direct] == list(range(n + 1))
        assert [r["elapsed_s"] for r in direct] == [r["elapsed_s"] for r in compact]
        assert direct[-1]["requested_span_s"] == 2e11
        rep = [r["temperature"] - a["temperature"] for a, r in zip(direct, compact)]
        initial = compact[0]
        b0 = binding(initial)
        e0 = math.fsum([initial["thermal"], b0, initial["escaped"], initial["cmb_reservoir"]])
        residual = {"total": [], "thermal": [], "chemical": []}
        for r in compact:
            b = binding(r)
            e = math.fsum([r["thermal"], b, r["escaped"], r["cmb_reservoir"]])
            residual["total"].append(abs(e - e0) / abs(e0))
            residual["thermal"].append(abs(r["thermal"] - initial["thermal"] - r["thermal_budget"]) / abs(initial["thermal"]))
            residual["chemical"].append(abs(b - b0 - r["chemical_budget"]) / abs(b0))
        rec = next(r for r in differences if r["case"] == "HOT_CI_60000" and r["backend"] == "compact_pchip" and int(r["nsteps"]) == n)
        close(abs(rep[-1]), rec["temperature_final_abs_error"])
        output[str(n)] = {"times_s": [r["elapsed_s"] for r in direct], "direct_T_K": [r["temperature"] for r in direct], "direct_T_end_K": direct[-1]["temperature"], "representation_difference_K": rep, "representation_max_abs_K": max(map(abs, rep)), "representation_final_relative": abs(rep[-1]) / abs(direct[-1]["temperature"]), "ledger_max_relative": {key: max(value) for key, value in residual.items()}}
    endpoints = [output[str(n)]["direct_T_end_K"] for n in [48, 96, 192]]
    d1, d2 = endpoints[0] - endpoints[1], endpoints[1] - endpoints[2]
    assert d1 * d2 > 0
    p = math.log2(abs(d1 / d2))
    rec = next(r for r in time_grid if r["case"] == "HOT_CI_60000" and r["backend"] == "original_direct" and r["field"] == "temperature")
    close(p, rec["formal_order"])
    close(d1, rec["delta_48_96"])
    close(d2, rec["delta_96_192"])
    return {"histories": output, "delta_48_96_K": d1, "delta_96_192_K": d2, "formal_three_grid_order": p, "finite_reference_T_end_K": endpoints[-1]}


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="both", which="major", labelsize=14, width=1, length=4)
    ax.grid(alpha=.18, color="#64748B", linewidth=.7)
    ax.set_axisbelow(True)


def save_figure(fig, name):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width, height = fig.canvas.get_width_height()
    labels = []
    outside = []
    for artist in fig.findobj(Text):
        if not artist.get_visible() or not artist.get_text():
            continue
        box = artist.get_window_extent(renderer)
        # A hidden/out-of-view log tick may remain in the artist tree. Only the
        # visible figure canvas range is relevant to the clipping report.
        if box.width == 0 or box.height == 0:
            continue
        record = {"text": artist.get_text(), "fontsize_pt_at180mm": artist.get_fontsize(), "box_px": [box.x0, box.y0, box.x1, box.y1]}
        labels.append(record)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > width + 1 or box.y1 > height + 1:
            outside.append(record)
    LAYOUT[name] = {"width_mm": 180, "height_mm": fig.get_size_inches()[1] * 25.4, "minimum_text_pt_at180mm": min(r["fontsize_pt_at180mm"] for r in labels), "minimum_text_pt_when_reduced_to90mm": min(r["fontsize_pt_at180mm"] for r in labels) / 2, "text_boxes_outside_canvas": outside, "text_boxes": labels}
    fig.savefig(HERE / (name + ".png"), dpi=300, facecolor="white")
    fig.savefig(HERE / (name + ".pdf"), metadata={"Title": name.replace("_", " "), "Author": "BRPERF01 research control", "Subject": "Existing evidence only; see CAPTIONS.md and SOURCE_INDEX.json"})
    # Actual90mm300dpi render for legibility inspection; all artists scale
    # together. The archival PDF retains its intended180mm physical width.
    fig.savefig(AUDIT / (name + "_90mm_preview.png"), dpi=150, facecolor="white", pil_kwargs={"dpi": (300, 300)})
    plt.close(fig)


def plot_performance(data):
    fig, axes = plt.subplots(3, 1, figsize=(WIDTH_IN, 9.35))
    fig.subplots_adjust(left=.34, right=.965, top=.88, bottom=.17, hspace=.64)
    fig.suptitle("Measured performance by workload", y=.979, fontsize=18, fontweight="bold")
    fig.text(.5, .929, "Independent scopes; no combined speedup", ha="center", fontsize=14)
    panels = [
        (axes[0], "(a) Rate query · 6 ABBA block ratios", [
            ("Legacy 65,537*", data["rates"]["legacy65537"], GRAY),
            ("Compact 8,193*", data["rates"]["compact8193"], BLUE),
            ("SIMD 8,193*", data["rates"]["simd8193"], ORANGE)], (.65, 7.2), [1, 2, 3, 4, 5, 6, 7]),
        (axes[1], "(b) Native RHS · 5 process medians", [
            ("Direct reuse", data["native"]["reused_direct"], GREEN),
            ("Legacy 65,537*", data["native"]["legacy_65537"], GRAY),
            ("Compact 8,193*", data["native"]["compact_pchip"], BLUE),
            ("SIMD 8,193*", data["native"]["compact_pchip_simd"], ORANGE)], (.7, 3.4), [1, 1.5, 2, 2.5, 3]),
        (axes[2], "(c) Frozen rays · 7 paired ratios", [
            ("2 workers, − shear", data["photon"]["minus_parallel"], BLUE),
            ("2 workers, + shear", data["photon"]["plus_parallel"], GREEN),
            ("Cached serial, −", data["photon"]["minus_cached"], GRAY),
            ("Cached serial, +", data["photon"]["plus_cached"], BLACK)], (.8, 2.2), [1, 1.5, 2]),
    ]
    for ax, title, items, limits, ticks in panels:
        style_axes(ax)
        ax.set_title(title, loc="left", pad=12, fontsize=14, fontweight="bold")
        ax.axvline(1.0, color="#91989F", linestyle="--", linewidth=1)
        positions = list(reversed(range(len(items))))
        for y, (label, rec, color) in zip(positions, items):
            ax.errorbar(rec["median"], y, xerr=[[rec["median"] - rec["lo"]], [rec["hi"] - rec["median"]]], fmt="o", color=color, markersize=7, elinewidth=1.7, capsize=4, capthick=1.5)
            ax.annotate(f'{rec["median"]:.2f}×', (rec["median"], y), xytext=(0, 8), textcoords="offset points", ha="center", va="bottom", fontsize=14, color=color)
        ax.set_yticks(positions, [item[0] for item in items])
        ax.tick_params(axis="y", length=0, pad=9)
        ax.set_xlim(*limits)
        ax.set_xticks(ticks)
        ax.set_ylim(-.55, len(items) - .25)
    axes[-1].set_xlabel("Original / candidate wall time", fontsize=14, labelpad=10)
    fig.text(.5, .070, "Spans show observed ranges, not confidence intervals.", ha="center", fontsize=14)
    fig.text(.5, .035, "*Tables approximate rates; no extra SIMD gain established.", ha="center", fontsize=14)
    save_figure(fig, "01_performance_scopes")


def plot_accuracy(data):
    fig, axes = plt.subplots(2, 1, figsize=(WIDTH_IN, 7.85), sharex=True)
    fig.subplots_adjust(left=.18, right=.955, top=.79, bottom=.195, hspace=.37)
    fig.suptitle("Coefficient accuracy and table storage", y=.979, fontsize=18, fontweight="bold")
    handles = [Line2D([], [], color=BLUE, marker="o", label="Compact scalar PCHIP", linewidth=1.7), Line2D([], [], color=ORANGE, marker="D", linestyle="None", label="Legacy log-linear")]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, .946), ncol=1, fontsize=14, frameon=False)
    nodes = [r["nodes"] for r in data["compact"]]
    errors = [r["error"] for r in data["compact"]]
    memory = [r["bytes"] / 2**20 for r in data["compact"]]
    for ax in axes:
        style_axes(ax)
        ax.set_xscale("log", base=2)
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlim(750, 90000)
    a, b = axes
    a.set_title("(a) Sampled coefficient error", loc="left", fontsize=14, fontweight="bold", pad=10)
    a.set_yscale("log")
    a.set_ylim(1.2e-7, 2e-2)
    a.plot(nodes, errors, "o-", color=BLUE, linewidth=1.8, markersize=7)
    a.plot(data["legacy_nodes"], data["legacy_union_max_error"], "D", color=ORANGE, markersize=8)
    a.axhline(data["target"], linestyle=":", linewidth=1.5, color=GRAY)
    a.text(70000, 1.65e-4, "Sampled target $10^{-4}$", ha="right", fontsize=14, color=GRAY)
    a.annotate("$1.30\\times10^{-5}$", (8193, errors[-1]), xytext=(18, 5), textcoords="offset points", fontsize=14, color=BLUE)
    a.text(15000, 1.8e-6, "Legacy has\nlower sampled error", fontsize=14, color=ORANGE)
    a.set_ylabel("Max. sampled relative error", fontsize=14)
    b.set_title("(b) Reported table storage", loc="left", fontsize=14, fontweight="bold", pad=10)
    b.plot(nodes, memory, "o-", color=BLUE, linewidth=1.8, markersize=7)
    legacy_mib = data["legacy_bytes"] / 2**20
    b.plot(data["legacy_nodes"], legacy_mib, "D", color=ORANGE, markersize=8)
    b.annotate(f"{memory[-1]:.2f} MiB", (8193, memory[-1]), xytext=(-4, 13), textcoords="offset points", ha="center", fontsize=14, color=BLUE)
    b.annotate(f"{legacy_mib:.2f} MiB", (data["legacy_nodes"], legacy_mib), xytext=(-8, -24), textcoords="offset points", ha="right", fontsize=14, color=ORANGE)
    b.text(1120, 7.2, f"8,193 vs legacy:\n{100 * data['memory_reduction_fraction']:.2f}% less storage", fontsize=14, color=BLACK)
    b.set_ylim(-.3, 10.4)
    b.set_yticks([0, 2, 4, 6, 8, 10])
    b.set_ylabel("Reported table storage [MiB]", fontsize=14)
    b.set_xticks(nodes + [data["legacy_nodes"]], ["1,025", "2,049", "4,097", "8,193", "65,537"])
    b.set_xlabel("Temperature nodes", fontsize=14, labelpad=10)
    fig.text(.5, .075, "Finite coefficient probes; no global error bound.", ha="center", fontsize=14)
    fig.text(.5, .040, "Storage excludes process peak RSS and allocator overhead.", ha="center", fontsize=14)
    save_figure(fig, "02_rate_accuracy_memory")


def plot_hot(data):
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_IN, 8.6))
    fig.subplots_adjust(left=.14, right=.97, top=.79, bottom=.18, hspace=.78, wspace=.69)
    fig.suptitle("Hot native H/He/D control", y=.98, fontsize=18, fontweight="bold")
    fig.text(.5, .930, "Fixed volume · photon source off", ha="center", fontsize=14)
    handles = [Line2D([], [], color=NT_COLORS[n], linestyle=NT_STYLES[n], linewidth=1.8, marker=NT_MARKERS[n], markersize=5, label=f"$N_t={n}$") for n in [48, 96, 192]]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.52, .891), ncol=3, fontsize=14, frameon=False, columnspacing=1.2, handlelength=2)
    a, b, c, d = axes.flat
    for ax in axes.flat:
        style_axes(ax)
    a.set_title("(a) Direct $T(t)$", loc="left", fontsize=14, fontweight="bold", pad=10)
    c.set_title("(c) Same-grid difference\ncompact − direct", loc="left", fontsize=14, fontweight="bold", pad=10)
    for n in [48, 96, 192]:
        h = data["histories"][str(n)]
        times = [t / 1e11 for t in h["times_s"]]
        a.plot(times, [t / 1e3 for t in h["direct_T_K"]], linestyle=NT_STYLES[n], color=NT_COLORS[n], linewidth=1.7, marker=NT_MARKERS[n], markersize=4, markevery=max(1, n // 6), markerfacecolor="white")
        c.plot(times, [t * 1e6 for t in h["representation_difference_K"]], linestyle=NT_STYLES[n], color=NT_COLORS[n], linewidth=1.6)
    for ax in [a, c]:
        ax.set_xlim(0, 2.03)
        ax.set_xticks([0, 1, 2])
        ax.set_xlabel("Time [$10^{11}$ s]", fontsize=14)
    a.set_ylim(41, 62)
    a.set_yticks([42, 48, 54, 60])
    a.set_ylabel("$T$ [$10^3$ K]", fontsize=14)
    b.set_title("(b) Endpoint shift", loc="left", fontsize=14, fontweight="bold", pad=10)
    shifts = [data["histories"][str(n)]["direct_T_end_K"] - data["finite_reference_T_end_K"] for n in [48, 96, 192]]
    b.plot([0, 1, 2], shifts, "o-", color=BLACK, linewidth=1.6, markersize=6)
    b.axhline(0, color=GRAY, linewidth=.9)
    b.set_xlim(-.2, 2.2)
    b.set_ylim(-.06, .93)
    b.set_yticks([0, .3, .6, .9])
    b.set_xticks([0, 1, 2], ["48", "96", "192"])
    b.set_xlabel("$N_t$", fontsize=14)
    b.set_ylabel("$T_{end}-T_{end,192}$\n[K]", fontsize=14)
    b.text(.08, .83, f"Formal $p={data['formal_three_grid_order']:.3f}$", transform=b.transAxes, fontsize=14)
    c.axhline(0, color=GRAY, linewidth=.9)
    c.set_ylabel("$T_{compact}-T_{direct}$\n[µK]", fontsize=14)
    c.set_ylim(-2.6, 2.1)
    c.set_yticks([-2, -1, 0, 1, 2])
    d.set_title("(d) Compact ledger", loc="left", fontsize=14, fontweight="bold", pad=10)
    ledger_handles = []
    for key, marker, ls, label in [("total", "o", "-", "Total / $E_0$"), ("thermal", "s", "--", "Thermal / $U_0$"), ("chemical", "^", ":", "Chemical / $B_0$")]:
        values = [data["histories"][str(n)]["ledger_max_relative"][key] * 1e15 for n in [48, 96, 192]]
        d.plot([0, 1, 2], values, marker=marker, linestyle=ls, color=BLACK, linewidth=1.6, markersize=6, markerfacecolor="white")
        ledger_handles.append(Line2D([], [], color=BLACK, marker=marker, linestyle=ls, linewidth=1.6, markersize=6, markerfacecolor="white", label=label))
    d.set_xlim(-.2, 2.2)
    d.set_ylim(0, 2.3)
    d.set_yticks([0, 1, 2])
    d.set_xticks([0, 1, 2], ["48", "96", "192"])
    d.set_xlabel("$N_t$", fontsize=14)
    d.set_ylabel("Max. relative residual\n[$10^{-15}$]", fontsize=14)
    fig.legend(handles=ledger_handles, loc="upper center", bbox_to_anchor=(.52, .12), ncol=3, fontsize=14, frameon=False, columnspacing=.9, handlelength=1.5)
    fig.text(.5, .040, "Finite-grid differences and conservation are separate checks.", ha="center", fontsize=14)
    save_figure(fig, "03_hot_native_control")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14, "axes.labelsize": 14, "axes.titlesize": 14, "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.unicode_minus": True, "axes.formatter.useoffset": False})
    performance = performance_data()
    accuracy = accuracy_data()
    hot = hot_data()
    host = js("runtime_evidence/RUNTIME_IDENTITY.json")
    # Preserve the raw host evidence without assuming its nested schema here.
    assert "avx512f" in json.dumps(host) and accuracy["compiled_avx"] is False and accuracy["compiled_sse2"] is True
    data = {"performance": performance, "accuracy": accuracy, "hot": hot}
    (HERE / "PLOT_DATA.json").write_text(json.dumps(data, indent=2) + "\n")
    plot_performance(performance)
    plot_accuracy(accuracy)
    plot_hot(hot)
    (HERE / "SOURCE_INDEX.json").write_text(json.dumps({"scope": "Existing evidence only; no new simulation, benchmark or scientific test", "sources": SOURCES, "exclusions": ["integration native_rhs_abba and native_rhs_abba_stale_launch", "photon pre-guard benchmark revisions"], "python": platform.python_version(), "matplotlib": matplotlib.__version__}, indent=2) + "\n")
    (AUDIT / "LAYOUT_CHECKS.json").write_text(json.dumps(LAYOUT, indent=2) + "\n")
    (AUDIT / "DISPLAY_VALUE_CHECKS.json").write_text(json.dumps({"status": "PASS_EXISTING_DATA_REDERIVATION", "rate_ratios": performance["rates"], "native_ratios": performance["native"], "photon_ratios": performance["photon"], "selected_error": accuracy["compact"][-1]["error"], "legacy_union_max_error": accuracy["legacy_union_max_error"], "memory_reduction_fraction": accuracy["memory_reduction_fraction"], "hot_three_grid_order": hot["formal_three_grid_order"], "hot_delta_96_192_K": hot["delta_96_192_K"], "hot_max_representation_difference_K": max(h["representation_max_abs_K"] for h in hot["histories"].values()), "new_benchmarks": 0, "new_scientific_test_suites": 0}, indent=2) + "\n")
    print(json.dumps({"status": "RENDERED_FOR_VISUAL_AUDIT", "source_files": len(SOURCES), "figures": list(LAYOUT), "outside_text_count": {key: len(value["text_boxes_outside_canvas"]) for key, value in LAYOUT.items()}}, indent=2))


if __name__ == "__main__":
    main()
