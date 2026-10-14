#!/usr/bin/env python3
"""Postprocess retained F08 endpoint data; never execute a scientific solver."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

SOURCE_DIR = Path("runs/rei_fastest_v1/paired")
SOURCE_NAMES = ("paired_history.csv", "campaign_summary.json", "difference_error_ledger.json")
OBSERVABLES = ("x_HII", "temperature_K", "gamma_HI_per_s", "photon_u_ev_per_h")
LABELS = ("xHII", "T (K)", "Gamma_HI (s^-1)", "photon_u (eV/H)")
RESOLUTIONS = ("T0", "T1", "T2", "S0", "S2", "A0", "A2")


class DataError(ValueError):
    pass


def finite(value, label):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DataError(f"{label}: not numeric") from exc
    if not math.isfinite(result):
        raise DataError(f"{label}: nonfinite")
    return result


def read_endpoints(path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise DataError("CSV has missing/duplicate columns")
        if not {"run", "time_s", *OBSERVABLES}.issubset(reader.fieldnames):
            raise DataError("CSV is missing required columns")
        records = {}
        for row in reader:
            name = row["run"]
            if not name or name in records:
                raise DataError(f"missing or duplicate run name: {name}")
            if None in row:
                raise DataError(f"{name}: malformed CSV row")
            records[name] = {key: finite(value, f"{name}.{key}") for key, value in row.items() if key != "run"}
    expected = {f"{resolution}_{geometry}" for resolution in RESOLUTIONS for geometry in ("FLRW", "BI")}
    if set(records) - expected - {"T0_EPS_HALF"}:
        raise DataError(f"unexpected endpoint names: {sorted(set(records) - expected - {'T0_EPS_HALF'})}")
    if expected - records.keys():
        raise DataError(f"missing paired endpoints: {sorted(expected - records.keys())}")
    times = {record["time_s"] for record in records.values()}
    if len(times) != 1 or next(iter(times)) != 1e13:
        raise DataError("paired endpoint times must all match retained endpoint 1e13 s")
    return records


def differences(records):
    result = []
    for resolution in RESOLUTIONS:
        bi, flrw = records[f"{resolution}_BI"], records[f"{resolution}_FLRW"]
        row = {"resolution": resolution, "time_s": bi["time_s"], "candidate": f"{resolution}_BI", "reference": f"{resolution}_FLRW"}
        for observable in OBSERVABLES:
            row[f"{observable}_BI"] = bi[observable]
            row[f"{observable}_FLRW"] = flrw[observable]
            delta = bi[observable] - flrw[observable]
            if not math.isfinite(delta):
                raise DataError(f"{resolution}.{observable}: nonfinite difference")
            row[f"{observable}_BI_minus_FLRW"] = delta
        result.append(row)
    return result


def inherited_metadata(summary, ledger):
    """Whitelist public scope/status fields; never reproduce raw-path receipts."""
    summary_keys = ("status", "runs", "accepted_trials", "completed_interval_s", "observational_reionization_claim", "physical_fit_error", "continuum_error_bound", "QV", "scientific_admission", "point_implementation_variants")
    ledger_keys = ("kind", "physical_fit_error", "model_error", "QV", "scientific_admission", "lower_guard_scope")
    return {"campaign_summary": {key: summary[key] for key in summary_keys if key in summary},
            "difference_error_ledger": {key: ledger[key] for key in ledger_keys if key in ledger}}


def recorded_comparisons(ledger):
    result = {}
    for key in ("geometry_difference", "weak_shear_half"):
        entry = ledger.get(key)
        if not isinstance(entry, dict) or not isinstance(entry.get("final_difference_by_observable"), dict) or not isinstance(entry.get("max_abs_by_observable"), dict):
            raise DataError(f"ledger missing recorded comparison: {key}")
        result[key] = {"candidate": entry.get("candidate"), "reference": entry.get("reference"),
                       "matched_endpoint_count": entry.get("matched_endpoint_count"),
                       "recorded_final_difference": {}, "recorded_max_abs_difference": {}}
        for observable in OBSERVABLES:
            result[key]["recorded_final_difference"][observable] = finite(entry["final_difference_by_observable"].get(observable), f"{key}.final.{observable}")
            result[key]["recorded_max_abs_difference"][observable] = finite(entry["max_abs_by_observable"].get(observable), f"{key}.max.{observable}")
    return result


def plot(rows, target):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.8), constrained_layout=True)
    categories = [row["resolution"] for row in rows]
    for ax, observable, label in zip(axes.flat, OBSERVABLES, LABELS):
        ax.scatter(categories, [row[f"{observable}_BI_minus_FLRW"] for row in rows], s=42, color="#245b85", zorder=3)
        ax.axhline(0, color="#777777", linewidth=0.7)
        ax.set_ylabel(f"BI - FLRW: {label}")
        ax.set_xlabel("Named resolution (categorical)")
        ax.grid(axis="y", alpha=0.2)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3), useOffset=False)
    fig.suptitle("SYNTHETIC / PRESCRIBED_DISCRETE\nSaved endpoints at t = 1e13 s; counterfactual shear response", fontsize=13)
    fig.savefig(target, dpi=170, metadata={"Description": "Saved-data postprocess; categorical endpoint dots, no time history or error bars."})
    plt.close(fig)


def generate(repo, output):
    paths = [repo / SOURCE_DIR / name for name in SOURCE_NAMES]
    # Read and validate every source before creating any deliverable.
    records = read_endpoints(paths[0])
    summary, ledger = [json.loads(path.read_text(encoding="utf-8")) for path in paths[1:]]
    if not isinstance(summary, dict) or not isinstance(ledger, dict):
        raise DataError("campaign summary and ledger must be objects")
    if summary.get("runs") != len(records):
        raise DataError("campaign summary run count differs from saved endpoint rows")
    rows = differences(records)
    comparisons = recorded_comparisons(ledger)
    metadata = inherited_metadata(summary, ledger)
    source_receipts = [{"path": (SOURCE_DIR / name).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in zip(SOURCE_NAMES, paths)]
    optional = None
    if "T0_EPS_HALF" in records:
        optional = {}
        for observable in OBSERVABLES:
            full = rows[0][f"{observable}_BI_minus_FLRW"]
            half = records["T0_EPS_HALF"][observable] - records["T0_FLRW"][observable]
            optional[observable] = {"EPS_HALF_minus_FLRW": half, "half_over_full_endpoint_ratio": half / full if full else None}
    output.mkdir(parents=True, exist_ok=True)
    with (output / "paired_endpoint_differences.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    plot(rows, output / "endpoint_response.png")
    lines = ["# 보존 F08 끝점 비교 — 저장 자료 후처리", "",
             "분류: **SYNTHETIC / PRESCRIBED_DISCRETE**. 이 보고서는 기존에 기록된 결과를 읽어 끝점 차이를 표시한 saved-data postprocess이다. 이전 ODE를 실행하거나 새 물리 계산을 승인하지 않았다.", "",
             f"원자료는 끝점 {len(records)}행이며 모두 t = 1e13 s이다. 7개 이름별 해상도에서 BI − FLRW를 비교한다. BI는 이 합성·처방 이산 모형 안의 counterfactual shear 비교이며 물리적 EoR, QV, 하늘 신호, 연속체 오차 상계 또는 새 scientific PASS를 뜻하지 않는다.", "",
             f"상속한 campaign status: `{summary.get('status')}`. 상속한 scientific_admission: `{summary.get('scientific_admission')}`. 새 후처리 status: `SAVED_DATA_POSTPROCESS_COMPLETE`; 새로운 scientific admission은 발급하지 않는다.", "",
             "## 끝점 차이", "", "아래 값은 저장된 BI 끝점에서 같은 해상도의 FLRW 끝점을 뺀 값이다. 그림의 가로축은 이름별 범주이며 시간축이 아니다. 끝점만으로 중간 시간 이력을 복원하지 않는다. 오차막대는 붙이지 않았다.", "",
             "| 해상도 | ΔxHII | ΔT (K) | ΔGamma_HI (s^-1) | Δphoton_u (eV/H) |", "|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append("| " + row["resolution"] + " | " + " | ".join(f"{row[f'{o}_BI_minus_FLRW']:.12g}" for o in OBSERVABLES) + " |")
    lines += ["", "![범주별 끝점 반응](endpoint_response.png)", "", "## 기존 ledger의 별도 기록", "",
              "다음 표는 원래 ledger에 기록된 T0 BI − FLRW의 final_difference와 max_abs를 그대로 구분해 옮겼다. max_abs는 기존 matched endpoint 집합에서 기록한 최대 절대 차이로, 이 15행 CSV로 재계산한 값이 아니다. final_difference와 max_abs는 서로 대체할 수 없고 물리적 불확실성 또는 오차막대가 아니다.", "",
              "| 관측량 | recorded final_difference | recorded max_abs |", "|---|---:|---:|"]
    for observable in OBSERVABLES:
        entry = comparisons["geometry_difference"]
        lines.append(f"| {observable} | {entry['recorded_final_difference'][observable]:.12g} | {entry['recorded_max_abs_difference'][observable]:.12g} |")
    if optional:
        lines += ["", "T0_EPS_HALF도 저장된 끝점 비교에 한해 사용했다. (EPS_HALF − FLRW)/(BI − FLRW) 비율은 아래의 범위 제한 진단이며 약한 전단 정리나 보편적 스케일링 증명이 아니다.", "", "| 관측량 | half/full 끝점 비율 |", "|---|---:|"]
        for observable, entry in optional.items():
            ratio = entry["half_over_full_endpoint_ratio"]
            lines.append(f"| {observable} | {ratio:.12g} |" if ratio is not None else f"| {observable} | undefined (zero denominator) |")
    lines += ["", "## 출처와 범위", "", "원본 receipt와 private raw 경로는 복사하지 않았다. 기존 source pin과 범위를 사용하며, 아래 SHA256은 이번에 읽은 공개 저장 파일의 byte identity만 기록한다.", "", "| 원본 경로 | SHA256 |", "|---|---|"]
    lines += [f"| `{item['path']}` | `{item['sha256']}` |" for item in source_receipts]
    lines += ["", f"상속한 ledger 설명: {ledger.get('kind')}", "",
              f"physical_fit_error: `{summary.get('physical_fit_error')}`; continuum_error_bound: `{summary.get('continuum_error_bound')}`; QV: `{summary.get('QV')}`. 원래 허용 범위를 확대하지 않는다.", ""]
    (output / "REPORT_KO.md").write_text("\n".join(lines), encoding="utf-8")
    receipt = {"schema": "rux_retained_endpoint_derivation.v1", "classification": "SYNTHETIC/PRESCRIBED_DISCRETE",
               "new_postprocess_status": "SAVED_DATA_POSTPROCESS_COMPLETE", "new_scientific_admission": "NOT_ISSUED",
               "source_files": source_receipts, "inherited_recorded_metadata": metadata,
               "operation": "BI minus FLRW subtraction of saved endpoints at matched 1e13 s; categorical dots; no error bars",
               "endpoint_row_count": len(records), "paired_resolution_count": len(rows), "endpoint_time_s": 1e13,
               "recorded_comparisons_not_recomputed": comparisons, "optional_EPS_HALF_scoped_endpoint_diagnostic": optional,
               "claim_exclusions": ["physical EoR", "QV", "sky", "continuum bound", "reconstructed history", "new scientific PASS"],
               "scientific_solver_executions": 0,
               "executor_identity": {"requested": "gpt-6.1-sol", "observed_runtime": None, "observed_runtime_note": "Runtime model identity unavailable to this tool; requested identity is not runtime evidence"},
               "outputs": ["paired_endpoint_differences.csv", "endpoint_response.png", "REPORT_KO.md", "DERIVATION_RECEIPT.json"]}
    (output / "DERIVATION_RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", required=True, type=Path, help="Explicit caller-selected output directory")
    args = parser.parse_args(argv)
    try:
        # Prevent accidental overwrite of immutable inputs/scientific source.
        output = args.output.resolve()
        for protected in (args.repo / "runs", args.repo / "rust", args.repo / "configs"):
            if output == protected.resolve() or protected.resolve() in output.parents:
                raise DataError("output directory must not overwrite runs, Rust sources, or configs")
        receipt = generate(args.repo, output)
        print(json.dumps({"new_postprocess_status": receipt["new_postprocess_status"], "output": str(output), "outputs": receipt["outputs"], "scientific_solver_executions": 0}, ensure_ascii=False, indent=2))
        return 0
    except (DataError, OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f"data error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
