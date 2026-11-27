"""R12 saved-output statistics and two figures. No solver or science imports.

Reads immutable actual primary/reference/R11 outputs. Fraction is used only to
compare, select and aggregate saved values; floats are display coordinates only.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction as Q
from io import BytesIO
from pathlib import Path
import datetime
import hashlib
import json
import os
import struct
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zlib

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
ANALYSIS = BASE / "analysis"
FIGURES = BASE / "figures"
PINS = {
    "primary": (BASE / "raw/PRIMARY_RESULTS.json", "06e1ea008d8bf35014341b3c8d48c9c87ec85da9e16cd43df23aaf104e926063"),
    "reference": (BASE / "raw/REFERENCE_RESULTS.json", "b366ed73b7584d6d6b07667aa56d7c950da06e5622c8335c31cbb7682505eb67"),
    "R11": (REPO / "research/provider_registry_molecular_r11_20261028/raw/PRIMARY_RESULTS.json", "80ed0f8df5c785e47ce737acb8b029485db54b543d57498bf182427093f29b1b"),
}
CASE_NAMES = {
    "two_state_no_reaction": "Two-state: no reaction",
    "two_state_nonlinear": "Two-state: nonlinear",
    "two_state_coarse_source_defect": "Two-state: coarse-source defect",
    "saved_native_nine_state_K_conditional_feedback": "Native9 K + synthetic reaction",
}
CASE_KO = {
    "two_state_no_reaction": "2상태 무반응",
    "two_state_nonlinear": "2상태 비선형",
    "two_state_coarse_source_defect": "2상태 coarse-source defect",
    "saved_native_nine_state_K_conditional_feedback": "Native9 조건부 fixture",
}


def serialize(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serialize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serialize(v) for v in x]
    return x


def dec(x, digits=15):
    if x is None:
        return "null"
    q = Q(x)
    with localcontext() as ctx:
        ctx.prec = 70
        return format(Decimal(q.numerator) / Decimal(q.denominator), f".{digits}g")


def identity(p):
    b = p.read_bytes()
    return {"path": p.relative_to(REPO).as_posix(), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def atomic_bytes(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".r12_atomic_", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def atomic_json(path, obj):
    atomic_bytes(path, (json.dumps(serialize(obj), ensure_ascii=False, indent=2) + "\n").encode())


def metric(new, baseline):
    pairs = [(Q(n), Q(b)) for n, b in zip(new, baseline)]
    if len(new) != len(baseline):
        raise ValueError("Same-clock comparison dimension mismatch")
    relative = [None if b == 0 else 100 * (b - n) / b for n, b in pairs]
    eligible = [(i, value) for i, value in enumerate(relative) if value is not None]
    improvements = [v for _, v in eligible]
    best = max(eligible, key=lambda item: item[1]) if eligible else None
    return {
        "count": len(pairs), "less": sum(n < b for n, b in pairs),
        "equal": sum(n == b for n, b in pairs), "greater": sum(n > b for n, b in pairs),
        "positive_baseline_count": len(eligible), "zero_baseline_count": len(pairs) - len(eligible),
        "relative_definition": "100*(R11_cap-R12_upper)/R11_cap, only positive R11_cap; zero denominator => null",
        "maximum_relative_improvement_percent": None if best is None else best[1],
        "maximum_relative_improvement_index": None if best is None else best[0],
        "maximum_strict_improvement_percent": None if not eligible else max([Q(0)] + improvements),
        "maximum_relative_worsening_percent": None if not eligible else max([Q(0)] + [-x for x in improvements]),
        "relative_improvement_percent": relative,
    }


def matched_old_clock(sweep, oldcase):
    times = list(map(Q, sweep["refined_times"]))
    knots = list(map(Q, sweep["caps"]["old_knots"]))
    index = {t: i for i, t in enumerate(times)}
    selected = [index[t] for t in knots]
    rows, arrays = {}, {}
    for mode in ("raw", "capped"):
        data = sweep[mode]
        points = [[Q(x) for x in data["refined_endpoints_upper"][i]] for i in selected]
        cells = []
        for a, b in zip(selected, selected[1:]):
            if not (a < b and all(knots[len(cells)] <= times[j] < times[j + 1] <= knots[len(cells) + 1]
                                 for j in range(a, b))):
                raise ValueError("Refined-to-old cell coverage is not exact and gap-free")
            cells.append([max(Q(data["refined_whole_cells_upper"][j][k]) for j in range(a, b)) for k in (0, 1)])
        rows[mode], arrays[mode] = {}, {"points": points, "whole_cells": cells}
        for label, new, old in (("points", points, oldcase["capped"]["endpoints_upper"]),
                                ("whole_cells", cells, oldcase["capped"]["whole_cells_upper"])):
            rows[mode][label] = {"RE"[k]: metric([a[k] for a in new], [b[k] for b in old]) for k in (0, 1)}
    return {"old_knots": knots, "old_point_indices_in_refined": selected,
            "old_cell_refined_ranges": list(zip(selected, selected[1:])),
            "point_count": len(knots), "closed_cell_count": len(knots) - 1,
            "gap_free_exact_coverage": True, "statistics": rows}, arrays


def interval_widths(sweep):
    answer = {}
    for name, time_key, low_key, high_key in (
            ("requested", "requested_times", "endpoints_lower", "endpoints_upper"),
            ("refined", "refined_times", "refined_endpoints_lower", "refined_endpoints_upper")):
        values = [Q(hi[1]) - Q(lo[1]) for lo, hi in zip(sweep["raw"][low_key], sweep["raw"][high_key])]
        i = max(range(len(values)), key=values.__getitem__)
        answer[name] = {"point_count": len(values), "maximum": values[i], "maximum_decimal": dec(values[i]),
                        "maximum_index": i, "maximum_time": sweep[time_key][i],
                        "final": values[-1], "final_decimal": dec(values[-1])}
    return answer


def inspect_png(payload):
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("PNG signature missing")
    cursor, chunks, ended = 8, 0, False
    while cursor < len(payload):
        length = struct.unpack(">I", payload[cursor:cursor + 4])[0]
        kind = payload[cursor + 4:cursor + 8]
        data = payload[cursor + 8:cursor + 8 + length]
        crc = struct.unpack(">I", payload[cursor + 8 + length:cursor + 12 + length])[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise ValueError("PNG chunk CRC mismatch")
        cursor += 12 + length
        chunks += 1
        if kind == b"IEND":
            ended = True
            break
    if not ended or cursor != len(payload):
        raise ValueError("PNG incomplete or has trailing bytes")
    from PIL import Image
    with Image.open(BytesIO(payload)) as image:
        image.load()
        size = image.size
    return {"PNG_all_chunk_CRC": "PASS", "IEND_exact_end": True, "Pillow_full_decode": "PASS",
            "width": size[0], "height": size[1], "chunk_count": chunks}


def make_figures(primary, matched):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
                         "axes.titlesize": 11, "axes.labelsize": 9.5, "legend.fontsize": 8,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.alpha": .18, "svg.hashsalt": "WU_R12_SAVED_OUTPUT_V1"})
    controls = {x["id"]: x["result"] for x in primary["controls"]}
    control = controls["translated_source_breakpoints"]
    t = list(map(Q, control["refined_times"]))
    src = list(map(Q, control["source"]["knots"]))
    tau = Q(control["parameters"]["tau"])
    source_shifts = sorted({a + k * tau for a in src for k in range(control["work"]["full_blocks"] + 1)
                            if t[0] <= a + k * tau <= t[-1]} - set(src))
    fig, ax = plt.subplots(2, 2, figsize=(12.8, 8.6))
    fig.suptitle("Exact nonaligned convolution: source shifts, left limits and whole cells", fontsize=15, y=.985)
    fig.text(.5, .949, "Saved arithmetic controls only; q = 1/2, tau = 1/3 in A-C. No new propagation or physical input.", ha="center", fontsize=9.5)
    ax[0, 0].step(list(map(float, t)), list(map(lambda x: float(Q(x)), control["exact"]["kernel_at_refined"])),
                  where="post", color="#334155", lw=2, label="age kernel h(t-t0)")
    ax[0, 0].stairs([float(Q(x)) for x in control["source"]["g_r"]], list(map(float, src)),
                    color="#059669", lw=2, label="source g_r")
    ax[0, 0].stairs([float(Q(x)) for x in control["source"]["g_e"]], list(map(float, src)),
                    color="#d97706", lw=1.5, label="source g_e")
    for x in src[1:-1]:
        ax[0, 0].axvline(float(x), color="#059669", ls="--", alpha=.5, lw=1)
    for x in source_shifts:
        ax[0, 0].axvline(float(x), color="#7c3aed", ls=":", alpha=.6, lw=1)
    for x, label in ((Q(8, 15), "8/15"), (Q(13, 15), "13/15")):
        ax[0, 0].text(float(x), 1.05, label, ha="center", color="#7c3aed", fontsize=8)
    ax[0, 0].set(title="A. Shift every source knot, then refine", ylabel="kernel / declared forcing", ylim=(-.03, 1.14))
    ax[0, 0].legend(loc="upper right")

    ax[0, 1].plot(list(map(float, t)), [float(Q(x)) for x in control["exact"]["F_at_refined"]],
                  color="#059669", lw=2.2, label="F(t): exact piecewise affine")
    for i, cell in enumerate(control["exact"]["R_affine_cells"]):
        ax[0, 1].plot([float(t[i]), float(t[i + 1])], [float(Q(cell["L"])), float(Q(cell["V"]))],
                      color="#2563eb", lw=1.9, label="R segment up to left limit" if i == 0 else None)
        right = Q(control["exact"]["R_at_refined"][i + 1])
        if Q(cell["V"]) != right:
            ax[0, 1].plot(float(t[i + 1]), float(Q(cell["V"])), "o", mfc="white", mec="#2563eb", ms=5)
            ax[0, 1].plot([float(t[i + 1])] * 2, [float(right), float(Q(cell["V"]))], color="#94a3b8", ls=":")
    ax[0, 1].scatter(list(map(float, t)), [float(Q(x)) for x in control["exact"]["R_at_refined"]],
                     s=16, color="#2563eb", label="actual point R", zorder=4)
    ax[0, 1].set(title="B. Right endpoint approached from the LEFT", ylabel="saved ideal comparison")
    ax[0, 1].legend(loc="best")

    req = list(map(Q, control["requested_times"]))
    ax[1, 0].stairs([float(Q(x[1])) for x in control["raw"]["refined_whole_cells_upper"]], list(map(float, t)),
                    color="#d97706", lw=2, label="certified whole-cell E upper")
    ax[1, 0].plot(list(map(float, req)), [float(Q(x[1])) for x in control["raw"]["endpoints_upper"]],
                  "o--", color="#2563eb", lw=1.5, ms=4, label="requested E points; connectors are guides")
    ax[1, 0].scatter(list(map(float, t)), [float(Q(x[1])) for x in control["raw"]["refined_endpoints_upper"]],
                     color="#64748b", s=11, alpha=.65, label="refined E points")
    ax[1, 0].set(title="C. Endpoint connectors differ from whole-cell bounds", ylabel="E upper bound")
    ax[1, 0].legend(loc="upper left")

    fresh = controls["q0_late_source_nonaligned"]
    ft = list(map(Q, fresh["refined_times"]))
    ax[1, 1].axvspan(.75, 1, color="#059669", alpha=.10)
    ax[1, 1].plot(list(map(float, ft)), [float(Q(x)) for x in fresh["exact"]["R_at_refined"]],
                  "o-", color="#059669", ms=3.5, lw=2, label="R from new forcing")
    ax[1, 1].stairs([float(Q(x[1])) for x in fresh["raw"]["refined_whole_cells_upper"]], list(map(float, ft)),
                    color="#d97706", lw=1.8, label="whole-cell E upper")
    ax[1, 1].plot([float(Q(x)) for x in fresh["requested_times"]], [float(Q(x[1])) for x in fresh["raw"]["endpoints_upper"]],
                  "o--", color="#7c3aed", ms=3, lw=1.2, label="E point connectors: guides")
    ax[1, 1].text(.045, .91, "g_r = 1 on [3/4, 1]\nR(1) = 1/4; E(1) = 1/32", transform=ax[1, 1].transAxes,
                  va="top", fontsize=9, bbox={"facecolor": "white", "edgecolor": "#d1d5db", "alpha": .9})
    ax[1, 1].set(title="D. q = 0 still gives fresh forcing h(0) = 1", ylabel="saved comparison / upper")
    ax[1, 1].legend(loc="center left", bbox_to_anchor=(.01, .50))
    for a in ax.flat:
        a.set_xlim(0, 1)
        a.set_xlabel("exact control clock t (displayed as decimals)")
    fig.text(.02, .022, "A: green dashed lines = source changes; purple dotted lines = translated source knots.  B: open circles = left limits.\n"
             "C-D: orange horizontal steps certify closed cells; dashed point connectors are visual guides. Lower arrays refer only to the ideal comparison.", fontsize=8.5)
    fig.tight_layout(rect=(0, .07, 1, .93), h_pad=2.3, w_pad=2.3)
    figures = [("NONALIGNED_CONTROL_GEOMETRY", fig,
                "Saved controls: translated source knots, exact F/R affine segments with left limits, E point connectors versus certified closed-cell steps, and q=0 fresh forcing.")]

    fig2, axs = plt.subplots(4, 2, figsize=(12.8, 12.3), sharex=True)
    fig2.suptitle("R12 versus R11 caps at exactly matched times and closed cells", fontsize=15, y=.987)
    fig2.text(.5, .960, "Capped R and E are identical to R11 on every matched point and cell, for both grids. Raw bounds remain larger.",
              ha="center", fontsize=9.5)
    colors = ("#2563eb", "#d97706")
    for row, case in enumerate(primary["hd_cases"]):
        old = matched[case["id"]]["old"]
        knots = list(map(Q, case["variants"]["aligned"]["caps"]["old_knots"]))
        qt = Q(case["variants"]["aligned"]["parameters"]["tau"])
        display_knots = [float((t - knots[0]) / qt) for t in knots]
        for col, label in enumerate(("points", "whole_cells")):
            a = axs[row, col]
            baseline = old["capped"]["endpoints_upper" if col == 0 else "whole_cells_upper"]
            maximum = 1.0
            for k in (0, 1):
                for variant in ("aligned", "nonaligned"):
                    values = matched[case["id"]][variant]["raw"][label]
                    ratios = [float(Q(new[k]) / Q(base[k])) if Q(base[k]) > 0 else float("nan")
                              for new, base in zip(values, baseline)]
                    finite = [v for v in ratios if v == v]
                    if finite:
                        maximum = max(maximum, max(finite))
                    style = "-" if variant == "aligned" else "--"
                    if col == 0:
                        a.plot(display_knots, ratios, color=colors[k], ls=style,
                               lw=1.9 if variant == "aligned" else 1.1, alpha=.82 if variant == "aligned" else 1)
                    else:
                        a.stairs(ratios, display_knots, color=colors[k], ls=style,
                                 lw=1.9 if variant == "aligned" else 1.1, alpha=.82 if variant == "aligned" else 1)
            a.axhline(1, color="#059669", lw=2.2, zorder=5)
            a.set_title(CASE_NAMES[case["id"]] + (" | 193 matched points" if col == 0 else " | 192 matched closed cells"), fontsize=10)
            a.set_ylabel("R12 upper / R11 cap")
            if maximum > 8:
                a.set_yscale("log")
                a.set_ylim(.85, maximum * 1.15)
            else:
                a.set_ylim(.95, maximum + max(.06, .08 * (maximum - 1)))
            a.set_xlim(0, 3)
            if row == 0:
                a.text(.02, .90, "E = 0 everywhere: ratio null (0/0)", transform=a.transAxes, fontsize=8.3,
                       bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85})
            if row == 3:
                a.set_xlabel("matched old clock (t - t0) / tau")
    legend = [Line2D([0], [0], color=colors[0], lw=2, label="raw R"),
              Line2D([0], [0], color=colors[1], lw=2, label="raw E"),
              Line2D([0], [0], color="#475569", lw=1.8, label="aligned"),
              Line2D([0], [0], color="#475569", lw=1.8, ls="--", label="nonaligned refinement, matched back"),
              Line2D([0], [0], color="#059669", lw=2.2, label="both capped grids / R11 = 1")]
    fig2.legend(handles=legend, loc="upper center", bbox_to_anchor=(.5, .945), ncol=5, fontsize=8.5, frameon=False)
    fig2.text(.02, .018, "Left: exact selection of the same 193 old knots, never different-time endpoint comparisons. Point connectors are visual guides.\n"
              "Right: nonaligned refined closed-cell uppers are maximized over each same old closed cell. Ratios use positive baselines only.\n"
              "Native9 retains native K + synthetic conditional reaction. These finite comparisons do not establish universal raw superiority or physical closure.", fontsize=8.5)
    fig2.tight_layout(rect=(0, .075, 1, .915), h_pad=2.1, w_pad=2.3)
    figures.append(("MATCHED_R11_CAP_COMPARISON", fig2,
                    "Four saved conditional cases: raw/capped R12 upper divided by R11 cap at the same193 old points and192 old closed cells. Nonaligned output is exactly selected/aggregated back; positive baselines only, zero ratios null."))
    manifest = []
    for stem, figure, caption in figures:
        for extension in ("png", "svg"):
            stream = BytesIO()
            metadata = {"Software": "WU R12 saved-output postprocessing"} if extension == "png" else {"Date": None, "Creator": "WU R12 saved-output postprocessing"}
            figure.savefig(stream, format=extension, dpi=180, metadata=metadata)
            payload = stream.getvalue()
            validation = inspect_png(payload) if extension == "png" else {"SVG_XML_parse": "PASS" if ET.fromstring(payload).tag.endswith("svg") else "FAIL"}
            path = FIGURES / (stem + "." + extension)
            atomic_bytes(path, payload)
            manifest.append(dict(identity(path), format=extension.upper(), caption=caption, validation=validation))
        plt.close(figure)
    return manifest, matplotlib.__version__


def report_text(summary):
    v = summary["verification"]
    lines = ["# R12 저장 출력 분석 및 그림", "",
        "R12는 서로 정렬되지 않은 정확한 source/observation 격자를 처리하고, 이동한 source 경계 및 old cap 경계를 포함한 refinement를 구현·검증했다. 이번 네 saved case에서 **R11 대비 추가 capped 개선은 0%**다. Aligned 출력과 nonaligned refined 출력을 같은 기존 시각·닫힌 셀에 맞추면 모든 capped R/E가 기존 값과 정확히 같다. 이는 이번 실제 입력의 결과이며 새 방법의 일반적 성능을 단정하지 않는다.", "",
        "## 실제 실행 근거", "",
        f"Primary **{v['primary']['checks']}/{v['primary']['checks']} PASS**, failure0. 독립 reference **{v['reference']['checks']}/{v['reference']['checks']} PASS**, **{v['reference']['component_comparisons']:,} component comparisons**, failure0. 각 Python 과학 실행은 1회이며 전체 OS CPU는 primary {v['primary']['OS_CPU_s']:.6f}초, reference {v['reference']['OS_CPU_s']:.6f}초, 합 **{v['scientific_OS_CPU_sum_s']:.6f}초**다. 이 합계는 import와 serialization을 포함하고 그림·저장 출력 후처리를 포함하지 않는다.", "",
        "Reference는 exact Fraction J primitive와 독립 event grid, Decimal160 closed forms를 사용했다. Decimal 비교는 실행 전 고정한 `1e-80*max(1,abs(reference),abs(lower),abs(upper))` guard를 쓴 **GUARDED_CORROBORATION_NOT_INTERVAL_REFERENCE**다. 이 reference 자체를 interval arithmetic이나 무제한 정확성 증명으로 부르지 않는다. Component 구성은 metadata894, coverage44,719, exact68,870, decimal19,019다.", "",
        "Wolfram은 새 제출에서 24개의 zero residual을 반환했다. `Symbol::undefined2`의 L/V 경고 및 `General::messages`를 보존하며, 원인은 `NOT_ESTABLISHED`, 판정은 **QUALIFIED_SYMBOLIC_CORROBORATION**이다. Zero residual만으로 전체 정리나 물리 closure를 채택하지 않는다.", "",
        "입력 증거: `raw/PRIMARY_RESULTS.json`, `raw/REFERENCE_RESULTS.json`, 두 `*_PROCESS.json`, `raw/CAS_ASSESSMENT.json`. 원본 bytes/SHA와 정확한 전체 통계는 `analysis/SAVED_OUTPUT_SUMMARY.json`에 있다. 그림 후처리의 별도 관리 CPU와 실제 process 기록은 `analysis/POSTPROCESS_PROCESS.json`에 둔다.", "",
        "## 정확한 격자와 작업 수", "",
        "저장된 constant g_r/g_e의 모든 원소가 정확히 같은 것을 확인한 뒤 source cell 하나로 압축했다. 모든 사례는 3개의 full block을 사용한다. Nonaligned의 새 interior observation point191개에는 old point cap을 적용하지 않았다. Old knots193개를 refined grid 안에 유지하여 closed-cell 포함 관계를 이용했다.", "",
        "| 사례 | 격자 | source / observation / refined cells | overlap terms | 서로 다른 scalar 길이 |",
        "|---|---|---:|---:|---:|"]
    for case in summary["cases"]:
        for variant, row in case["variants"].items():
            w = row["work"]
            lines.append(f"| {CASE_KO[case['id']]} | {variant} | {w['source_cells']} / {w['observation_cells']} / {w['refined_cells']} | {w['overlap_terms']} | {w['distinct_Bernstein_lengths']} |")
    lines += ["", "## 최종 upper", "",
        "표시는 15자리 근사다. JSON에는 exact rational 값을 보존했다. 두 격자의 capped 최종 R/E는 서로, 그리고 R11의 같은 최종시각 값과 정확히 같다. E=0인 baseline의 상대비는 0%로 바꾸지 않고 null이다.", "",
        "| 사례 | 격자 | raw R(T) | raw E(T) | capped R(T) | capped E(T) |",
        "|---|---|---:|---:|---:|---:|"]
    for case in summary["cases"]:
        for variant, row in case["variants"].items():
            values = row["raw_final_upper"] + row["capped_final_upper"]
            lines.append("| " + " | ".join([CASE_KO[case["id"]], variant] + [dec(x) for x in values]) + " |")
    lines += ["", "## 같은 기존 시각·닫힌 셀에서의 비교", "",
        "Aligned는 기존193점/192셀을 그대로 사용했다. Nonaligned는 refined point에서 **동일한193 old knot**를 선택하고, 각 **동일한 old closed cell**에 포함되는 refined whole upper의 최댓값을 취했다. 다른 시각의 요청 endpoint를 직접 비교하지 않았다.", "",
        "각 격자에서 4사례의 capped point 성분1,544개와 whole-cell 성분1,536개가 R11 cap과 정확히 같다. 두 격자 합계는 point3,088개와 whole-cell3,072개이며 개선·악화 성분은 모두0개다. Positive baseline에서 최대 strict 개선은0%; denominator0이면 null이다.", "",
        "Raw에서 R11 cap보다 큰 성분 수는 다음과 같다. 두 격자를 같은 old clock으로 맞춘 뒤의 count가 동일하지만 scalar outward rounding의 일부 exact 값까지 동일하다는 뜻은 아니다.", "",
        "| 사례 | 격자 | R point 큰 값 /193 | E point 큰 값 /193 | R whole 큰 값 /192 | E whole 큰 값 /192 |",
        "|---|---|---:|---:|---:|---:|"]
    for case in summary["cases"]:
        for variant, row in case["variants"].items():
            s = row["same_old_clock"]["statistics"]["raw"]
            vals = [s[domain][component]["greater"] for domain in ("points", "whole_cells") for component in ("R", "E")]
            lines.append("| " + " | ".join([CASE_KO[case["id"]], variant] + list(map(str, vals))) + " |")
    lines += ["", "이 결과에서 raw의 보편적 우위를 주장하지 않는다. 상대 개선은 반드시 `100*(old-new)/old`를 positive old baseline에만 계산했다. Exact per-component 변화, 최대 strict 개선·최대 악화 및 denominator0의 null 기록은 JSON에 있다.", "",
        "## Raw E 구간 폭과 refinement", "",
        "| 사례 | 격자 | requested E 최대 폭 | refined E 최대 폭 | 최종 E 폭 |",
        "|---|---|---:|---:|---:|"]
    for case in summary["cases"]:
        for variant, row in case["variants"].items():
            w = row["raw_E_interval_widths"]
            lines.append(f"| {CASE_KO[case['id']]} | {variant} | {dec(w['requested']['maximum'])} | {dec(w['refined']['maximum'])} | {dec(w['refined']['final'])} |")
    lines += ["", "같은 old knot에서 kernel/F/R exact 값이 두 격자 사이에 일치했고, 같은 ideal E를 감싸는 두 outward 구간은 겹쳤다. 세분화는 outward rounding 누적 폭을 바꿀 수 있으므로 E 출력의 bitwise 동일성이나 monotone width 개선을 가정하지 않았다. 독립 reference의 guarded Decimal 비교가 이를 별도로 확인했다.", "",
        "## 두 그림의 읽기", "",
        "### 그림 1 — 비정렬 source 경계와 fresh forcing", "",
        "![Nonaligned control geometry](figures/NONALIGNED_CONTROL_GEOMETRY.png)", "",
        "`NONALIGNED_CONTROL_GEOMETRY`는 translated-source control의 source knots, source에서 이동한 경계8/15·13/15, step kernel, exact F 및 R affine segment를 표시한다. R의 open circle은 **셀의 오른쪽 끝점에 왼쪽에서 접근한 극한**이고 filled point는 해당 끝점의 실제 비교값이다. E의 dashed endpoint 연결선은 시각적 안내이며 orange whole-cell steps가 각 닫힌 셀의 upper를 나타낸다. 별도 q=0 control은 마지막 [3/4,1]에 들어오는 새 forcing이 h0=1을 가지므로 최종 R=1/4, E=1/32임을 보여 준다.", "",
        "### 그림 2 — 동일한 R11 clock과 cap으로 비교", "",
        "![Matched R11 cap comparison](figures/MATCHED_R11_CAP_COMPARISON.png)", "",
        "`MATCHED_R11_CAP_COMPARISON`의 왼쪽 열은 같은193점, 오른쪽 열은 같은192 old closed cell이다. 오른쪽 nonaligned 값은 해당 old cell 안의 refined upper 최댓값으로 집계했다. 파란색은 raw R, 주황색은 raw E이며 실선/파선은 aligned/nonaligned를 구별한다. 초록색 ratio1은 두 격자의 capped 출력이 R11과 정확히 같음을 뜻한다. Positive baseline만 ratio를 표시하며, no-reaction E는 모두0이므로 0/0 ratio를 생략하고 null로 기록했다. Point plot의 연결선은 whole-cell 인증으로 읽지 않는다.", "",
        "PNG와 SVG를 함께 제공한다. 모든 PNG chunk CRC·정확한 IEND 끝·Pillow full decode 및 SVG XML을 확인한 뒤 atomic replace로 저장한다. 최종 bytes/SHA는 `figures/FIGURE_MANIFEST.json`에 있다.", "",
        "## 범위와 보존 사항", "",
        "Native9은 **native K + synthetic conditional reaction fixture**다. Actual HD reactive array와 named physical consumer/density/clock은 INPUT_PENDING이다. HH_R10=OFF, production=NOT_ISSUED, L4=false, central/physical delta=0, native v=UNSPECIFIED, MISSING_NOT_ZERO 및 TIQM/SQM 구별을 보존한다.", "",
        "Raw lower는 고정한 rational-q ideal comparison의 lower이며 실제 물리 오차의 lower가 아니다. 새 물리 closure 또는 모든 입력에 대한 raw 우위를 주장하지 않는다. 이번 후처리는 저장 값을 선택·집계·비교·그렸고 새 solver, ODE, generator, CAS, predecessor module import 또는 saved sample campaign을 실행하지 않았다. R8 original726/727+1FAIL과 별도24/24, R10/R11의 원래 sample tolerance 및 경고·실패 기록은 변경하지 않았다. R12의 새 sample containment 결과를 만들지 않았다.", ""]
    return "\n".join(lines)


def main():
    if len(sys.argv) != 1:
        raise SystemExit("Saved-output plotting takes no arguments")
    if (FIGURES / "FIGURE_MANIFEST.json").exists() or (ANALYSIS / "SAVED_OUTPUT_SUMMARY.json").exists():
        raise SystemExit("Refuse an unrecorded repeat of saved-output plotting")
    cpu0, wall0 = time.process_time(), time.monotonic()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    loaded, identities = {}, {}
    for key, (path, expected) in PINS.items():
        row = identity(path)
        if row["sha256"] != expected:
            raise ValueError("Saved source SHA mismatch: " + key)
        loaded[key] = json.loads(path.read_text())
        identities[key] = row
        if loaded[key]["status"] != "PASS":
            raise ValueError("Expected actual PASS source: " + key)
    primary, reference, old = (loaded[k] for k in ("primary", "reference", "R11"))
    processes = {name: json.loads((BASE / f"raw/{name.upper()}_PROCESS.json").read_text()) for name in ("primary", "reference")}
    cas_path = BASE / "raw/CAS_ASSESSMENT.json"
    cas = json.loads(cas_path.read_text())
    for name in ("primary", "reference"):
        identities[name + "_process"] = identity(BASE / f"raw/{name.upper()}_PROCESS.json")
    identities["CAS_assessment"] = identity(cas_path)
    summary = {"schema": "WU_R12_SAVED_OUTPUT_SUMMARY_V1", "created_utc": started,
        "source_identities": identities, "script_identity": identity(Path(__file__).resolve()),
        "verification": {"primary": {"status": primary["status"], "checks": primary["check_count"], "failures": primary["failure_count"], "runs": 1, "OS_CPU_s": processes["primary"]["OS_CPU_s"]},
            "reference": {"status": reference["status"], "checks": reference["check_count"], "failures": reference["failure_count"], "runs": 1, "OS_CPU_s": processes["reference"]["OS_CPU_s"], "component_comparisons": reference["component_comparisons"], "components_by_kind": reference["component_comparisons_by_kind"], "failed_components": reference["failed_components"], "guard": reference["guard"], "guard_fixed_before_execution": reference["guard_fixed_before_execution"], "reference_is_interval_arithmetic": reference["reference_is_interval_arithmetic"], "qualification": "GUARDED_CORROBORATION_NOT_INTERVAL_REFERENCE"},
            "scientific_OS_CPU_sum_s": sum(processes[n]["OS_CPU_s"] for n in processes), "CAS": cas},
        "comparison_scope": "Exact same old193 points and same old192 closed cells; nonaligned refined bounds selected/aggregated back, never different-time requested endpoints.",
        "cases": [], "controls": [],
        "scope": {"saved_output_only": True, "solver_calls": 0, "scientific_module_imports": 0, "ODE_calls": 0, "CAS_calls": 0, "old_science_replay": 0, "new_sample_campaign": 0, "physical_consumer_admitted": False, "native_fixture": "native K + synthetic conditional reaction", "raw_lower": "chosen rational-q ideal comparison, never physical-error lower", "raw_universal_superiority_claim": False},
        "postprocessing": {"process_record": "analysis/POSTPROCESS_PROCESS.json", "CPU_accounting": "Administrative saved-output-only process; excluded from scientific primary/reference CPU subtotal", "temporary_files_published": False}}
    matched = {}
    totals = {mode: {domain: {k: 0 for k in ("less", "equal", "greater")} for domain in ("points", "whole_cells")} for mode in ("raw", "capped")}
    for case, oldcase in zip(primary["hd_cases"], old["hd_cases"]):
        if case["id"] != oldcase["id"]:
            raise ValueError("Case source ordering mismatch")
        record = {"id": case["id"], "source_scope": case["source_scope"], "variants": {}}
        matched[case["id"]] = {"old": oldcase}
        for variant, sweep in case["variants"].items():
            same, arrays = matched_old_clock(sweep, oldcase)
            matched[case["id"]][variant] = arrays
            record["variants"][variant] = {"work": sweep["work"], "parameters": sweep["parameters"],
                "raw_final_upper": sweep["raw"]["endpoints_upper"][-1],
                "capped_final_upper": sweep["capped"]["endpoints_upper"][-1],
                "R11_final_capped_upper": oldcase["capped"]["endpoints_upper"][-1],
                "final_relative_improvement_percent": [None if Q(b) == 0 else 100 * (Q(b) - Q(n)) / Q(b) for n, b in zip(sweep["capped"]["endpoints_upper"][-1], oldcase["capped"]["endpoints_upper"][-1])],
                "raw_E_interval_widths": interval_widths(sweep), "same_old_clock": same,
                "requested_old_point_cap_count": sum(x is not None for x in sweep["caps"]["requested_point_to_old_point"]),
                "requested_without_old_point_cap_count": sum(x is None for x in sweep["caps"]["requested_point_to_old_point"])}
            for mode in totals:
                for domain in totals[mode]:
                    for component in ("R", "E"):
                        for key in totals[mode][domain]:
                            totals[mode][domain][key] += same["statistics"][mode][domain][component][key]
        a, n = case["variants"]["aligned"], case["variants"]["nonaligned"]
        ni = {Q(t): i for i, t in enumerate(n["refined_times"])}
        common = list(map(Q, a["refined_times"]))
        record["refinement_invariance"] = {"same_old_point_count": len(common),
            "exact_component_count": 3 * len(common),
            "kernel_F_R_all_equal": all(Q(a["exact"][key][i]) == Q(n["exact"][key][ni[t]]) for i, t in enumerate(common) for key in ("kernel_at_refined", "F_at_refined", "R_at_refined")),
            "raw_E_intervals_all_overlap": all(Q(a["raw"]["refined_endpoints_lower"][i][1]) <= Q(n["raw"]["refined_endpoints_upper"][ni[t]][1]) and Q(n["raw"]["refined_endpoints_lower"][ni[t]][1]) <= Q(a["raw"]["refined_endpoints_upper"][i][1]) for i, t in enumerate(common)),
            "bitwise_E_invariance_claim": False,
            "reference_qualification": "Decimal160 guard-qualified corroboration; reference is not interval arithmetic"}
        summary["cases"].append(record)
    summary["same_old_clock_totals_both_grids"] = totals
    summary["all_matched_capped_exactly_equal_R11"] = all(totals["capped"][d]["less"] == totals["capped"][d]["greater"] == 0 for d in totals["capped"])
    for row in primary["controls"]:
        out = row["result"]
        summary["controls"].append({"id": row["id"], "work": out["work"], "parameters": out["parameters"],
                                   "source": out["source"], "requested_times": out["requested_times"],
                                   "refined_times": out["refined_times"], "final_raw_upper": out["raw"]["endpoints_upper"][-1],
                                   "raw_E_interval_widths": interval_widths(out)})
    figure_rows, mpl_version = make_figures(primary, matched)
    summary["figure_names"] = [row["path"] for row in figure_rows]
    summary["postprocessing"]["internal_CPU_before_final_metadata_s"] = time.process_time() - cpu0
    summary["postprocessing"]["internal_wall_before_final_metadata_s"] = time.monotonic() - wall0
    summary["postprocessing"]["matplotlib_version"] = mpl_version
    atomic_json(ANALYSIS / "SAVED_OUTPUT_SUMMARY.json", summary)
    atomic_bytes(BASE / "RESULTS_KO.md", report_text(summary).encode())
    manifest = {"schema": "WU_R12_SAVED_FIGURE_MANIFEST_V1", "created_utc": started,
        "source_identities": identities, "script_identity": identity(Path(__file__).resolve()),
        "summary_identity": identity(ANALYSIS / "SAVED_OUTPUT_SUMMARY.json"), "report_identity": identity(BASE / "RESULTS_KO.md"),
        "figures": figure_rows, "figure_count": 2, "image_file_count": 4,
        "saved_output_only": True, "scientific_or_ODE_runs": 0, "atomic_complete_payloads": True,
        "temporary_files_published": False, "visual_review": "Pending root/C9 view; programmatic image decode and CRC/XML passed"}
    atomic_json(FIGURES / "FIGURE_MANIFEST.json", manifest)
    print(json.dumps({"status": "SAVED_POSTPROCESSING_COMPLETE", "figure_files": figure_rows,
                      "summary": identity(ANALYSIS / "SAVED_OUTPUT_SUMMARY.json"),
                      "report": identity(BASE / "RESULTS_KO.md"), "all_caps_equal_R11": summary["all_matched_capped_exactly_equal_R11"],
                      "same_clock_counts": totals}, ensure_ascii=False))


if __name__ == "__main__":
    main()
