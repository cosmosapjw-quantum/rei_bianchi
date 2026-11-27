#!/usr/bin/env python3
"""C8 presentation only: parse four saved JSON artifacts, summarize and plot.

This script never imports the production or reference scientific modules and
never calls an ODE solver, matrix exponential, or certificate calculator.
Stored samples are plotted as points; no additional trajectory is evaluated.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path


LEAF = Path(__file__).resolve().parents[1]
RESULTS = LEAF / "results"
PREVIEW = LEAF.parents[2] / "preview" / "nonlinear_feedback_bounds.png"
SOURCES = ("PRIMARY_RESULTS.json", "REFERENCE_RESULTS.json", "PRIMARY_PROCESS.json", "REFERENCE_PROCESS.json")


def number(value):
    return float(Fraction(value)) if isinstance(value, (str, int)) else float(value)


def sci(value):
    return "0" if value == 0 else f"{value:.8g}"


def scaled_rational(value, multiplier):
    q = Fraction(value) * multiplier
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    loaded = {name: json.loads((LEAF / "raw" / name).read_text()) for name in SOURCES}
    primary, reference = loaded[SOURCES[0]], loaded[SOURCES[1]]
    pcost, rcost = loaded[SOURCES[2]], loaded[SOURCES[3]]
    refs = {case["id"].removeprefix("HD:"): case for case in reference["hd_cases"]}
    checks = {item["name"]: item for item in reference["checks"]}
    labels = {
        "two_state_no_reaction": "2상태 무반응 대조",
        "two_state_nonlinear": "2상태 비선형 반응",
        "two_state_coarse_source_defect": "2상태 coarse source defect",
        "saved_native_nine_state_K_conditional_feedback": "9상태 저장 K + 조건부 합성 반응",
    }
    summary = {
        "schema": "WU_R7_C8_SAVED_RESULT_SUMMARY_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Presentation-only postprocessing of four saved JSON artifacts; no scientific execution",
        "new_scientific_runs": 0,
        "production_or_reference_imports": False,
        "solver_or_expm_calls": 0,
        "trajectory_interpolation": False,
        "source_files": [{"path": "../raw/" + name, "sha256": digest(LEAF / "raw" / name)} for name in SOURCES],
        "definitions": {
            "R": "l1 norm of HD population residual x_HD-pi*X",
            "E": "absolute scalar aggregate discrepancy |eta|=|X-Xbar|",
            "full_coarse_l1": "4E under the common exact H/D/charge invariant class",
            "endpoint": "valid only at the corresponding certified block end",
            "whole_block": "one upper vector valid over the entire closed block, using Bplus with d clipped to zero",
            "reference": "stored binary64 DOP853 values, an independent corroboration rather than a rigorous ODE enclosure",
            "units": "declared dimensionless fixture coordinates; no physical clock/density binding",
        },
        "verification": {
            "primary": {"status": primary["status"], "checks": primary["check_count"], "failures": primary["failure_count"]},
            "reference": {"status": reference["status"], "checks": reference["check_count"], "failures": reference["failure_count"]},
            "additional_C8_scientific_checks": 0,
        },
        "cost": {
            "primary": {"OS_process_CPU_s": pcost["OS_child_CPU_seconds"], "supervised_wall_s": pcost["wall_seconds"],
                        "result_finalize_CPU_s": primary["actual_process_cpu_seconds_at_finalize"],
                        "CPU_limit_s": primary["budget"]["CPU_limit_s"],
                        "includes_imports_and_serialization": pcost["CPU_includes_imports_and_serialization"],
                        "exit_code": pcost["exit_code"], "science_runs": pcost["science_runs"]},
            "reference": {"OS_process_CPU_s": rcost["OS_child_CPU_seconds"], "supervised_wall_s": rcost["wall_seconds"],
                          "result_finalize_CPU_s": reference["actual_process_CPU_s"],
                          "CPU_limit_s": reference["budget"]["CPU_limit_s"],
                          "includes_imports_and_serialization": rcost["CPU_includes_imports_and_serialization"],
                          "exit_code": rcost["exit_code"], "science_runs": rcost["science_runs"]},
            "combined_OS_process_CPU_s": pcost["OS_child_CPU_seconds"] + rcost["OS_child_CPU_seconds"],
            "scope": "Only the two saved supervised process records; CAS cost is not included here",
        },
        "hd_cases": [],
        "late_forcing_saved": deepcopy(primary["late_forcing"]),
        "limitations": [
            "Exact bounds are conditional on the recorded box, generator certificate, rate/source choices and common invariant class.",
            "Reference tolerances permit floating-point deviations; the reference is not interval integration.",
            "The native nine-state case reuses an excitation generator while formation/destruction and reservoirs remain declared synthetic controls.",
            "No physical IVP, source consumer, density or physical clock is admitted by these controls.",
            "The geometric Taylor tail is only one contributor to outward arithmetic width and is not the physical reduction error.",
        ],
    }
    for case in primary["hd_cases"]:
        ref = refs[case["id"]]
        prefix = ref["id"] + ": "
        final_actual = ref["R_E"][-1]
        final_exact = case["blocks"][-1]["certificate"]["w_next_upper"]
        final_upper = [number(value) for value in final_exact]
        invariants = {
            "exact_initial": ref["invariants_exact"],
            "fine_max_absolute_drift": checks[prefix + "conserved fine H/D/charge"]["evidence"]["max_absolute_drift"],
            "coarse_max_absolute_drift": checks[prefix + "conserved coarse H/D/charge"]["evidence"]["max_absolute_drift"],
            "coarse_direction_max_absolute_error": checks[prefix + "coarse error direction s*eta"]["evidence"]["max_absolute_error"],
            "coarse_l1_equals_4E_max_absolute_error": checks[prefix + "coarse l1 observable equals4E"]["evidence"]["max_absolute_error"],
            "provenance": "Copied from saved reference check evidence, not recomputed by C8",
        }
        row = {
            "id": case["id"], "label_ko": labels[case["id"]], "states": len(case["pi"]),
            "source_scope": case["source_scope"], "physical_consumer_admitted": ref["physical_consumer_admitted"],
            "H_exact": case["H"], "H_display": number(case["H"]), "rho_exact": case["rho"],
            "final_time_saved": ref["times"][-1], "reference_clock_count": len(ref["times"]),
            "solver_saved": ref["solver"], "coordinate_scales": case["coordinate_scales"],
            "rate_offset_exact": case["coarse_kf_offset"],
            "coarse_scalar_defect_upper_exact": case["coarse_scalar_defect_upper"],
            "final": {
                "reference_R_E": final_actual, "endpoint_upper_exact_R_E": final_exact,
                "endpoint_upper_display_R_E": final_upper,
                "reference_4E": 4 * final_actual[1],
                "endpoint_upper_exact_4E": scaled_rational(final_exact[1], 4),
                "endpoint_upper_display_4E": 4 * final_upper[1],
                "bound_over_reference_ratio_R_E": [upper / value if value > 0 else None for upper, value in zip(final_upper, final_actual)],
                "ratio_note": "Display postprocessing; null when the stored reference value is zero",
            },
            "invariants": invariants,
            "max_stored_reference_E": max(value[1] for value in ref["R_E"]),
            "blocks": [],
        }
        for pb, rb in zip(case["blocks"], ref["blocks"]):
            certificate = pb["certificate"]
            row["blocks"].append({
                "index": pb["index"], "t0_exact": pb["t0"], "H_exact": certificate["H"],
                "reference_endpoint_R_E": rb["actual_endpoint"],
                "endpoint_upper_exact_R_E": certificate["w_next_upper"],
                "endpoint_upper_display_R_E": [number(v) for v in certificate["w_next_upper"]],
                "whole_block_upper_exact_R_E": certificate["whole_block_upper"],
                "whole_block_upper_display_R_E": [number(v) for v in certificate["whole_block_upper"]],
                "reference_clock_count_inclusive": len(rb["saved_clock_indices"]),
                "production_query_count_inclusive": len(pb["queries"]),
                "endpoint_tail_certificate_saved": certificate["tail_certificate"],
                "whole_block_certificate_saved": certificate["whole_block_certificate"],
                "actual_endpoint_check_saved": checks[prefix + f"block{pb['index']} actual endpoint R/E"],
            })
        summary["hd_cases"].append(row)

    RESULTS.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    summary_path = RESULTS / "SAVED_RESULT_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n")

    # Plotting has no interpolation: all reference marks are stored sample pairs.
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/wu_r7_c8_matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 12, "axes.labelsize": 11,
                         "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "white",
                         "savefig.facecolor": "white"})
    figure, axes = plt.subplots(3, 2, figsize=(13.8, 12.5))
    figure.subplots_adjust(left=0.075, right=0.98, top=0.84, bottom=0.17, hspace=0.52, wspace=0.25)
    figure.suptitle("Nonlinear reaction feedback: saved errors and certified bounds", fontsize=17, fontweight="bold", y=0.982)
    figure.text(0.5, 0.946, "Three blocks · 193 saved reference clocks per fixture · dimensionless fixture coordinates", ha="center", fontsize=11, color="#48576B")
    colors = {"actual": "#225D91", "endpoint": "#087F5B", "whole": "#C26A13"}
    handles = [Line2D([], [], linestyle="None", marker="o", markersize=4, color=colors["actual"], label="Saved reference values"),
               Line2D([], [], linestyle="None", marker="D", markersize=6, color=colors["endpoint"], label="Certified endpoint upper"),
               Line2D([], [], linestyle=(0, (5, 2)), linewidth=1.8, color=colors["whole"], label="Certified whole-block upper")]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.923), frameon=False, ncol=3, columnspacing=2.7)
    plot_cases = ["two_state_nonlinear", "two_state_coarse_source_defect", "saved_native_nine_state_K_conditional_feedback"]
    titles = ["A  Nonlinear two-state", "B  Two-state with coarse source defect", "C  Native nine-state K + synthetic reactions"]
    by_primary = {case["id"]: case for case in primary["hd_cases"]}
    by_summary = {case["id"]: case for case in summary["hd_cases"]}
    for i, key in enumerate(plot_cases):
        case, ref, row = by_primary[key], refs[key], by_summary[key]
        H = number(case["H"])
        xs = [t / H for t in ref["times"]]
        for j in range(2):
            ax = axes[i][j]
            is_log = i == 2
            if is_log:
                ax.set_yscale("log")
            actual = [pair[j] for pair in ref["R_E"]]
            pairs = [(x, value) for x, value in zip(xs, actual) if value > 0 or not is_log]
            ax.scatter([x for x, _ in pairs], [value for _, value in pairs], s=7, color=colors["actual"], linewidths=0, zorder=3)
            for block in case["blocks"]:
                index, cert = block["index"], block["certificate"]
                whole = number(cert["whole_block_upper"][j])
                endpoint = number(cert["w_next_upper"][j])
                ax.plot([index, index + 1], [whole, whole], linestyle=(0, (5, 2)), color=colors["whole"], linewidth=1.7, zorder=2)
                ax.scatter([index + 1], [endpoint], marker="D", s=42, facecolor="white", edgecolor=colors["endpoint"], linewidth=1.6, zorder=4)
            for cut in (1, 2):
                ax.axvline(cut, color="#CFD6DF", linewidth=0.7, zorder=0)
            ax.grid(axis="y", color="#E7EBF0", linewidth=0.6)
            ax.set_xlim(-0.035, 3.06)
            ax.set_xticks((0, 1, 2, 3))
            ax.set_xlabel(r"$t/H$  (block units)")
            ax.set_ylabel(r"$R=\|x_{\rm HD}-\pi X\|_1$" if j == 0 else r"$E=|\eta|=|X-\bar X|$")
            ax.set_title(titles[i] if j == 0 else "Aggregate error; full coarse norm = 4E", loc="left", pad=11)
            if not is_log:
                ax.set_ylim(bottom=0)
                ax.yaxis.set_major_locator(MaxNLocator(5))
                if j == 1:
                    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
            else:
                ax.text(0.97, 0.74, "log scale" + ("; E(0) = 0 omitted" if j else ""),
                        transform=ax.transAxes, ha="right", color="#48576B", fontsize=9,
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9})
            if j == 0:
                ax.text(0.97, 0.93, f"H = {H:.6g}" + ("\nconditional fixture" if i == 2 else ""),
                        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#48576B",
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9})
    figure.text(0.075, 0.075,
                "Dots show stored solver samples only. Horizontal segments hold over a whole block; diamonds apply only at block ends.\n"
                "The native K row is a conditional mathematical control: physical reaction pools, densities and time conversion remain unbound.",
                fontsize=10, color="#35455B", linespacing=1.6)
    svg_path = RESULTS / "nonlinear_feedback_bounds.svg"
    figure.savefig(svg_path, format="svg", metadata={"Title": "WU R7 saved nonlinear feedback error bounds",
                   "Description": "Saved primary and independent reference arrays only; no new numerical evaluation or trajectory interpolation.",
                   "Creator": "WU R7 C8 saved-result postprocessing"})
    figure.savefig(PREVIEW, dpi=150)
    plt.close(figure)

    lines = [
        "# R7 저장 결과: 비선형 반응 피드백 오차와 인증 상계", "",
        "## 핵심 결과", "",
        f"고정 primary **{primary['check_count']}/{primary['check_count']} PASS**, 독립 reference **{reference['check_count']}/{reference['check_count']} PASS**를 저장 결과에서 확인했다. 두 결과 모두 실패 수는 0이다. 이 C8 작업은 저장 JSON의 표시·집계와 그림 작성만 수행했으며 과학 실행, core/reference import, ODE·행렬지수 계산 또는 새 궤적 보간을 수행하지 않았다. [P][R]", "",
        "주어진 네 HD 대조군은 동일한 H/D/전하 보존량류에서 출발한다. `R`은 HD 상태분포 residual의 l1 norm이고, `E=|eta|=|X-Xbar|`이다. **전체 coarse 4성분 오차의 l1 norm은 `4E`**이다. 따라서 아래 E 상계를 전체 coarse norm 상계로 해석할 때는 4를 곱한다. 정확한 유리수 인증값은 `SAVED_RESULT_SUMMARY.json`에 그대로 보존했고 표에는 표시용 근삿값을 썼다. [P][R]", "",
        "## 3블록 뒤의 최종 오차", "",
        "| 대조군 | 최종 fixture 시각 | R 참조값 | R 끝점 상계 | E 참조값 | E 끝점 상계 | 4E 참조값 | 4E 끝점 상계 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["hd_cases"]:
        final = row["final"]
        actual, upper = final["reference_R_E"], final["endpoint_upper_display_R_E"]
        lines.append(f"| {row['label_ko']} | {sci(row['final_time_saved'])} | {sci(actual[0])} | {sci(upper[0])} | {sci(actual[1])} | {sci(upper[1])} | {sci(final['reference_4E'])} | {sci(final['endpoint_upper_display_4E'])} |")
    native = summary["hd_cases"][-1]
    no_reaction = summary["hd_cases"][0]
    lines += ["", "표의 참조값은 독립 DOP853 계산이 저장한 binary64 값이다. 참조 ODE가 별도의 interval enclosure라는 의미는 아니다. reference의 PASS는 저장된 부동소수점 허용오차를 포함한다. 무반응 대조에서 수학적 E 상계는 정확히 0이고 최종 참조 E도 0이지만, 중간 저장 E의 최대값은 " + sci(no_reaction["max_stored_reference_E"]) + "이다. 이 크기의 반올림 차이를 물리적 오차로 해석하지 않는다. [R]", "",
        f"9상태 조건부 대조의 최종 상계/참조값 비율은 R에서 약 {native['final']['bound_over_reference_ratio_R_E'][0]:.3g}, E에서 약 {native['final']['bound_over_reference_ratio_R_E'][1]:.3g}이다. 인증이 유효하다는 결과와 상계가 날카롭다는 평가는 구별해야 한다. 이 대조에서는 공통 전역 상자와 안전한 반응 계수를 사용하는 상계가 실제 저장 오차보다 상당히 크다. 이 비율은 저장된 두 수의 표시용 나눗셈이며 추가 solver 결과가 아니다. [P][R]", "",
        "coarse source defect 대조의 양의 `kf` offset은 `1/10000`, 인증된 scalar defect 상계는 `9/40000`이다. 이 항을 포함하면 E 인증 상계는 증가한다. 이번 저장 궤적에서는 실제 E가 offset 없는 대조보다 작다. 절댓값을 취하기 전 오차 항의 상쇄가 가능하므로 이 한 대조의 실제 E를 offset에 대한 단조성이나 물리적 개선으로 해석하지 않는다. [P][R]", "",
        "## 끝점 상계와 블록 전체 상계", "",
        "끝점 재귀는 `T=W_upper-(1-rho)e1 e1^T`, `w_next=T w0+q`이다. `rho`는 초기 residual에만 적용된다. 표의 `끝점`은 해당 블록이 끝나는 시각에 유효하며 블록 내부 전체를 덮는 값이 아니다. `전체`는 감쇠 계수 d를 `max(d,0)`으로 올린 Bplus 비교계로 얻어 그 블록의 모든 시각을 덮는다. 초기 오차를 포함하므로 블록 전체 R 상계가 끝점 R 상계보다 큰 것이 정상이다. [P]", "",
        "| 대조군 | 블록 | R 끝점 상계 | R 블록 전체 상계 | E 끝점 상계 | E 블록 전체 상계 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["hd_cases"]:
        for block in row["blocks"]:
            end, whole = block["endpoint_upper_display_R_E"], block["whole_block_upper_display_R_E"]
            lines.append(f"| {row['label_ko']} | {block['index'] + 1} | {sci(end[0])} | {sci(whole[0])} | {sci(end[1])} | {sci(whole[1])} |")
    lines += ["", "각 HD 대조군은 3블록과 중복 끝점을 합친 193개 저장 reference 시각을 가진다. reference는 블록마다 끝점을 포함한 65개 시각을 사용했고, production은 `0,H/4,H/2,3H/4,H`의 5개 내부 질의값을 저장했다. 그림의 파란 점은 이 저장 reference 표본만 표시한다. 주황색 수평 구간은 블록 전체 인증 상계이고 초록색 마름모는 끝점 인증 상계이다. 참조 점을 잇거나 새 solver 값으로 채우지 않았다. native 행의 로그 축에서는 정확히 0인 초기 E를 표시할 수 없어 그 점만 생략하고 축에 명시했다. [P][R]", "",
        "![저장된 비선형 피드백 오차와 인증 상계](nonlinear_feedback_bounds.svg)", "",
        "## 보존량과 scalar 오차의 수치 잔차", "",
        "모든 대조의 정확한 초기 보존량은 `H=7/2`, `D=3/2`, `charge=2`이다. 아래 값은 저장 reference check의 evidence를 옮긴 것으로, 새 적분이나 재검사를 수행한 결과가 아니다. [R]", "",
        "| 대조군 | fine 보존량 최대 drift | coarse 보존량 최대 drift | s·eta 방향 최대 잔차 | coarse l1=4E 최대 잔차 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary["hd_cases"]:
        inv = row["invariants"]
        lines.append(f"| {row['label_ko']} | {sci(inv['fine_max_absolute_drift'])} | {sci(inv['coarse_max_absolute_drift'])} | {sci(inv['coarse_direction_max_absolute_error'])} | {sci(inv['coarse_l1_equals_4E_max_absolute_error'])} |")
    lines += ["", "## 산술 scale과 Taylor 꼬리 증거", "",
        "고정 대조의 오차 좌표 scale은 모두 `(1,1)`, Taylor degree는 48, dyadic 정밀도는 256 bits이다. 꼬리 계산은 실제 위쪽 반올림한 확대 행렬 C의 norm을 사용한다. 아래 값은 마지막 블록에 저장된 certificate를 요약한다. 동일 대조의 B,g,H가 고정되어 있으므로 블록마다 같은 지수 커널을 사용하고 초기 오차만 재귀로 갱신한다. [P]", "",
        "| 대조군 | 위쪽 scaled norm z | shift·H | exp factor 전 꼬리 상계 | 방식 |",
        "|---|---:|---:|---:|---|",
    ]
    for row in summary["hd_cases"]:
        tail = row["blocks"][-1]["endpoint_tail_certificate_saved"]
        tail_value = tail.get("tail_upper_before_exp_factor", tail.get("tail_upper", "0"))
        lines.append(f"| {row['label_ko']} | {sci(number(tail['scaled_norm_upper']))} | {sci(number(tail.get('shift_times_H', '0')))} | {sci(number(tail_value))} | {'정확한 B²=0 다항식' if tail['algorithm'] == 'exact_B_squared_zero' else '양의 급수 + 위쪽 반올림 + 기하급수 꼬리'} |")
    lines += ["", "양의 급수 대조의 저장 꼬리 상계는 정확히 `2^-255`이다. 이 값은 exp factor를 적용하기 전 확대 행렬 급수의 꼬리 항이다. 입력 격자화, 각 항의 반올림과 exp factor 포함구간이 별도로 존재하므로 이 숫자 하나가 전체 산술 오차를 나타내지 않는다. 특히 물리적 coarse-graining 오차나 E 자체와 동일한 양이 아니다. 무반응 대조는 정확한 다항식으로 꼬리 0을 갖는다. [P]", "",
        "## 실제 실행 비용", "",
        "| 실행 | 저장 check | OS 전체 process CPU | 감독 wall time | 개별 CPU 상한 | 종료 코드 |",
        "|---|---:|---:|---:|---:|---:|",
        f"| primary | {primary['check_count']}/{primary['check_count']} PASS | {pcost['OS_child_CPU_seconds']:.6f} s | {pcost['wall_seconds']:.6f} s | 60 s | {pcost['exit_code']} |",
        f"| reference | {reference['check_count']}/{reference['check_count']} PASS | {rcost['OS_child_CPU_seconds']:.6f} s | {rcost['wall_seconds']:.6f} s | 60 s | {rcost['exit_code']} |", "",
        f"두 OS process CPU의 합은 {summary['cost']['combined_OS_process_CPU_s']:.6f} s이다. OS 기록은 import와 결과 직렬화를 포함한다. JSON 내부 finalize 시점 CPU는 각각 {primary['actual_process_cpu_seconds_at_finalize']:.9f} s, {reference['actual_process_CPU_s']:.9f} s로 기록되어 있으나 전체 비용 표에는 감독 프로세스가 보존한 값을 사용했다. C8의 표시·집계는 신규 과학 실행 수에 포함되지 않으며 신규 과학 실행은 0회이다. 이 비용 표는 primary/reference 두 기록만 포함하고 CAS 비용은 별도 결과의 범위이다. [Pcost][Rcost]", "",
        "## 적용 범위", "",
        "9상태 행은 저장된 native excitation 생성자 구간의 한 K와 그 H/rho 인증을 재사용하고, 새로 선언한 합성 formation/destruction 및 저장소를 결합한 조건부 수학 대조이다. 원천 반응물 풀, 상태 정렬, 실제 밀도, branch, 물리적 시계 및 GL2022 소비자의 결합을 완료한 물리 계산으로 승격하지 않는다. 저장 reference도 `physical_consumer_admitted=false`를 유지한다. [P][R]", "",
        "유리수 상계의 유효성은 기록된 전역 양성 상자, 명목 생성자 인증, source 선택, 동일 초기 보존량류와 명시적 forcing/결함 상계에 조건부이다. binary64 reference는 이 조건부 구현을 독립적으로 뒷받침한다. 한정된 대조의 통과로 다른 입력, 다른 ensemble 또는 실제 물리 소비자에 대한 승인을 발급하지 않는다. [P][R]", "",
        "## 저장 증거", "",
        "- [P]: [PRIMARY_RESULTS.json](../raw/PRIMARY_RESULTS.json)",
        "- [R]: [REFERENCE_RESULTS.json](../raw/REFERENCE_RESULTS.json)",
        "- [Pcost]: [PRIMARY_PROCESS.json](../raw/PRIMARY_PROCESS.json)",
        "- [Rcost]: [REFERENCE_PROCESS.json](../raw/REFERENCE_PROCESS.json)",
        "- 정확한 수치와 출처 hash: [SAVED_RESULT_SUMMARY.json](SAVED_RESULT_SUMMARY.json)",
        "- 게시용 벡터 그림: [nonlinear_feedback_bounds.svg](nonlinear_feedback_bounds.svg)",
        "- 재현 가능한 저장 자료 집계: [build_saved_summary.py](build_saved_summary.py)", "",
    ]
    (RESULTS / "ERROR_BOUNDS_KO.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"new_scientific_runs": 0, "summary": str(summary_path),
                      "report": str(RESULTS / 'ERROR_BOUNDS_KO.md'), "svg": str(svg_path), "preview": str(PREVIEW),
                      "saved_final_rows": [{"id": row["id"], "actual_R_E": row["final"]["reference_R_E"],
                                            "upper_R_E": row["final"]["endpoint_upper_display_R_E"]} for row in summary["hd_cases"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
