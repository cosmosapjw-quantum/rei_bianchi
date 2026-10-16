#!/usr/bin/env python3
"""Factual comparison of V10 native histories; no scientific admission gate.

Accepts any numeric columns in the native CSV, keeping newly added component
columns visible.  Missing or malformed histories are reported, never replaced.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

LEVELS = (8, 16, 32, 64, 128)
OBSERVABLES = ("T_K", "HII", "HeII", "HeIII", "ne_cm3", "photon_n_per_h",
               "photon_u_ev_per_h", "thermal_ev_per_h", "source_n", "absorbed_n",
               "photo_HI", "photo_HeI", "photo_HeII", "rr_HII", "rr_HeII",
               "rr_HeIII", "dr_HeII", "escape_ev_per_h", "photon_work_ev_per_h",
               "thermal_work_ev_per_h", "chemical_ev_per_h", "photoheating_ev_per_h",
               "photo_binding_ev_per_h", "ci_HI", "ci_HeI", "ci_HeII")
LEDGER_FIELDS = ("number_residual", "energy_residual", "electron_event_residual_per_h",
                 "step_delta_number_residual", "step_delta_energy_residual")
EPS = sys.float_info.epsilon


def finite_number(value: str, path: Path, line: int, column: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{path}:{line}: nonnumeric {column}={value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{path}:{line}: nonfinite {column}={value!r}")
    return number


def load_history(path: Path, expected_n: int) -> dict:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path}: empty CSV")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"{path}: duplicate columns")
        for required in ("step", "a", "T_K", "HII", "HeII", "HeIII", "ne_cm3"):
            if required not in reader.fieldnames:
                raise ValueError(f"{path}: missing {required}")
        rows = []
        for line, raw in enumerate(reader, 2):
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError(f"{path}:{line}: malformed CSV row")
            rows.append({name: finite_number(raw[name], path, line, name)
                         for name in reader.fieldnames})
    if len(rows) != expected_n:
        raise ValueError(f"{path}: expected {expected_n} rows, got {len(rows)}")
    if any(row["step"] != index for index, row in enumerate(rows, 1)):
        raise ValueError(f"{path}: steps not consecutive 1..{expected_n}")
    if any(rows[i]["a"] <= rows[i - 1]["a"] for i in range(1, len(rows))):
        raise ValueError(f"{path}: scale factor not strictly increasing")
    final = rows[-1]
    maxima = {field: max(abs(row[field]) for row in rows) for field in LEDGER_FIELDS
              if field in final}
    maxima.update({field: max(row[field] for row in rows) for field in
                   ("max_newton_residual", "recomb_exposure_max") if field in final})
    sum_fields = {field: sum(row[field] for row in rows) for field in
                  ("proper_dt_s",) if field in final}
    # Cumulative event columns allow a rate-independent photon count check.
    if all(field in final for field in ("source_n", "absorbed_n", "photon_n_per_h")):
        deltas = [(rows[i]["photon_n_per_h"] - rows[i-1]["photon_n_per_h"])
                  - (rows[i]["source_n"] - rows[i-1]["source_n"])
                  + (rows[i]["absorbed_n"] - rows[i-1]["absorbed_n"])
                  for i in range(1, len(rows))]
        maxima["independent_photon_delta_residual_from_row_2"] = max(map(abs, deltas), default=None)
        if "boundary_n" in final:
            number_level = [row["photon_n_per_h"] + row["absorbed_n"]
                            + row["boundary_n"] - row["source_n"] for row in rows]
            maxima["independent_number_ledger_drift_from_row_2"] = max(
                (abs(value-number_level[0]) for value in number_level[1:]), default=None)
    energy_fields = ("thermal_ev_per_h", "chemical_ev_per_h", "photon_u_ev_per_h",
                     "escape_ev_per_h", "boundary_u", "thermal_work_ev_per_h",
                     "photon_work_ev_per_h", "source_u", "cmb_ev_per_h")
    if all(field in final for field in energy_fields):
        # Exact PR150 Driver::total_energy ownership equation, reconstructed
        # from emitted stocks and cumulative fluxes rather than its residual.
        energy_level = [sum(row[field] for field in energy_fields[:7])
                        - row["source_u"] - row["cmb_ev_per_h"] for row in rows]
        maxima["independent_energy_ledger_drift_from_row_2_ev_per_h"] = max(
            (abs(value-energy_level[0]) for value in energy_level[1:]), default=None)
        initial_key = next((key for key in ("initial_energy_ev_per_h",
                            "initial_total_energy_ev_per_h", "initial_energy_stock_ev_per_h")
                            if key in final), None)
        if initial_key:
            maxima["independent_energy_ledger_absolute_ev_per_h"] = max(
                abs(value-row[initial_key]) for row,value in zip(rows,energy_level))
    else:
        maxima["independent_energy_ledger"] = "NOT_EVALUABLE_MISSING_COLUMNS:" + ",".join(
            field for field in energy_fields if field not in final)
    # n_e = n_H (HII + Y_He (HeII + 2 HeIII)); compare with recorded n_He/n_H.
    if all(field in final for field in ("nh_cm3", "nhe_cm3")):
        maxima["independent_electron_census_cm3"] = max(abs(
            row["ne_cm3"] - row["nh_cm3"] * row["HII"]
            - row["nhe_cm3"] * (row["HeII"] + 2 * row["HeIII"])) for row in rows)
        maxima["helium_abundance_variation"] = max(
            abs(row["nhe_cm3"] / row["nh_cm3"] - rows[0]["nhe_cm3"] / rows[0]["nh_cm3"])
            for row in rows)
        maxima["total_H_comoving_density_variation"] = max(
            abs(row["nh_cm3"] * row["a"]**3 - rows[0]["nh_cm3"] * rows[0]["a"]**3)
            for row in rows)
        event_fields = ("photo_HI", "photo_HeI", "photo_HeII", "ci_HI", "ci_HeI",
                        "ci_HeII", "rr_HII", "rr_HeII", "rr_HeIII", "dr_HeII")
        if all(field in final for field in event_fields):
            electron_level = [row["HII"] + row["nhe_cm3"] / row["nh_cm3"] *
                              (row["HeII"] + 2*row["HeIII"])
                              - sum(row[field] for field in event_fields[:6])
                              + sum(row[field] for field in event_fields[6:]) for row in rows]
            maxima["independent_electron_event_ledger_drift_from_row_2_per_h"] = max(
                (abs(value-electron_level[0]) for value in electron_level[1:]), default=None)
    if all(field in final for field in ("proper_dt_s", "H_per_s")):
        x = math.log(final["a"] / rows[0]["a"])
        maxima["proper_time_s"] = sum_fields["proper_dt_s"]
        maxima["X_from_first_recorded_a"] = x
        maxima["max_step_Hdt_minus_dX"] = max(abs(
            row["H_per_s"] * row["proper_dt_s"] - math.log(row["a"] / rows[i-1]["a"]))
            for i, row in enumerate(rows) if i > 0)
    return {"path": str(path), "rows": len(rows), "final_a": final["a"],
            "final": final, "maxima": maxima, "sums": sum_fields}


def parse_input(spec: str) -> tuple[str, int, Path]:
    try:
        mode, number, filename = spec.split(":", 2)
        n = int(number)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("input must be MODE:N:CSV") from exc
    if not mode or n < 1 or not filename:
        raise argparse.ArgumentTypeError("input must be MODE:N:CSV")
    return mode, n, Path(filename)


def discover(directory: Path) -> list[tuple[str, int, Path]]:
    result = []
    for path in sorted(directory.glob("*.csv")):
        match = re.fullmatch(r"(.+?)_(\d+)", path.stem)
        if match:
            result.append((match.group(1), int(match.group(2)), path))
    return result


def observable_keys(final: dict) -> list[str]:
    base = list(OBSERVABLES)
    more = sorted(k for k in final if k not in base and k not in
                  {"step", "a", "proper_dt_s", "H_per_s", "nh_cm3", "nhe_cm3",
                   "rhs_evaluations", "max_newton_residual", "recomb_exposure_max"}
                  and not k.endswith("residual"))
    return [key for key in base + more if key in final]


def comparisons(histories: dict[int, dict]) -> dict:
    available = sorted(histories)
    reference_1024 = histories.get(1024)
    highest_n = max(available) if available else None
    highest_reference = histories.get(highest_n)
    out = {}
    for n in available:
        if n >= 128 and n not in (512, 1024):
            continue
        coarse = histories[n]
        fine = histories.get(2 * n)
        if fine is None:
            continue
        pair = {}
        for key in observable_keys(coarse["final"]):
            if key not in fine["final"]:
                continue
            value = abs(coarse["final"][key] - fine["final"][key])
            # Use the observable's own scale.  A universal floor of 1 falsely
            # hides resolved changes in small photon and electron densities.
            scale = max(abs(coarse["final"][key]), abs(fine["final"][key]),
                        sys.float_info.min)
            newton = max(coarse["maxima"].get("max_newton_residual", 0),
                         fine["maxima"].get("max_newton_residual", 0))
            floor = 20 * max(EPS * scale, newton * scale)
            item = {"self_difference": value, "floor_envelope": floor,
                    "floor_characteristic_scale": scale,
                    "floor_newton_residual": newton,
                    "floor_mapping": "20*max(binary64_eps,newton_residual)*own_final_magnitude",
                    "floor_flag": value <= floor}
            if reference_1024 is not None and key in reference_1024["final"]:
                item["difference_to_N1024"] = abs(coarse["final"][key] - reference_1024["final"][key])
                if 512 in histories:
                    item["fine_reference_uncertainty_N512_N1024"] = abs(
                        histories[512]["final"][key] - reference_1024["final"][key])
            if highest_reference is not None and key in highest_reference["final"]:
                item["highest_available_reference_N"] = highest_n
                item["difference_to_highest_available_reference"] = abs(
                    coarse["final"][key] - highest_reference["final"][key])
            if (1024 in histories and 2048 in histories
                    and key in histories[1024]["final"] and key in histories[2048]["final"]):
                uncertainty = abs(histories[1024]["final"][key] - histories[2048]["final"][key])
                item["fine_reference_uncertainty_N1024_N2048"] = uncertainty
                if (64 in histories and 128 in histories
                        and key in histories[64]["final"] and key in histories[128]["final"]):
                    denominator = abs(histories[64]["final"][key] - histories[128]["final"][key])
                    item["fine_uncertainty_to_N64_N128_gap"] = (
                        uncertainty / denominator if denominator else None)
            pair[key] = item
        out[str(n)] = {"fine_n": 2*n, "observables": pair}
    for n_text, entry in out.items():
        next_entry = out.get(str(2*int(n_text)))
        if not next_entry:
            continue
        for key, item in entry["observables"].items():
            other = next_entry["observables"].get(key)
            if not other or not item["self_difference"] or not other["self_difference"]:
                item["self_order"] = None
                continue
            item["self_order"] = math.log2(item["self_difference"] / other["self_difference"])
            item["order_floor_flag"] = item["floor_flag"] or other["floor_flag"]
    return out


def elapsed_time(path: Path) -> float | None:
    for sibling in (path.with_suffix(".time"), path.with_suffix(".stderr")):
        if not sibling.exists():
            continue
        data = sibling.read_text(errors="replace")
        for pattern in (r"wall_s=([0-9.eE+-]+)", r"(?:Elapsed \(wall clock\) time|wall_s):\s*([0-9.eE+-]+)"):
            match = re.search(pattern, data)
            if match:
                return float(match.group(1))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=parse_input, default=[],
                        metavar="MODE:N:CSV", help="explicit native history; repeat")
    parser.add_argument("--runs-dir", type=Path, help="discover MODE_N.csv in this directory")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    specs = list(args.input)
    if args.runs_dir:
        specs += discover(args.runs_dir)
    if not specs:
        parser.error("supply --input or --runs-dir")
    modes: dict[str, dict[int, dict]] = {}
    failures = []
    for mode, n, path in specs:
        if n in modes.setdefault(mode, {}):
            failures.append({"mode": mode, "n": n, "path": str(path), "error": "duplicate mode/N"})
            continue
        try:
            history = load_history(path, n)
            history["wall_s"] = elapsed_time(path)
            modes[mode][n] = history
        except (OSError, ValueError, ZeroDivisionError) as exc:
            failures.append({"mode": mode, "n": n, "path": str(path), "error": str(exc)})
    output = {"schema": "v10_native_matrix_factual_v2", "scientific_admission": "NOT_EVALUATED",
              "floor_interpretation": "heuristic diagnostic only; Newton residual is dimensionless and scaled by each observable's final magnitude, not a certified numerical error bound",
              "requested": [{"mode": m, "n": n, "path": str(p)} for m,n,p in specs],
              "failures": failures, "modes": {}}
    for mode, histories in modes.items():
        final_a = [item["final_a"] for item in histories.values()]
        spread = max(final_a)-min(final_a) if final_a else None
        # Repeated a *= exp(dX) accumulates O(N eps) rounding.  The observed
        # N2048 spread is 1134 eps relative; each multiplicative step can
        # contribute up to one binary64 rounding unit to accumulated a.
        final_a_relative_tolerance = max(64, max(histories, default=0))*EPS
        relative_spread = spread/max(map(abs, final_a)) if final_a else None
        mismatch = relative_spread > final_a_relative_tolerance if final_a else False
        output["modes"][mode] = {"available_n": sorted(histories),
            "required_levels_missing": [n for n in LEVELS if n not in histories],
            "final_a_mismatch": mismatch, "final_a_spread": spread,
            "final_a_relative_spread": relative_spread,
            "final_a_relative_tolerance": final_a_relative_tolerance,
            "histories": {str(n): v for n,v in histories.items()},
            "comparisons": {} if mismatch else comparisons(histories)}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "MATRIX_ANALYSIS.json").write_text(json.dumps(output, indent=2, sort_keys=True)+"\n")
    with (args.out_dir / "MATRIX_COMPARISONS.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("mode", "N", "fine_N", "observable", "self_difference", "self_order",
                         "floor_envelope", "floor_flag", "order_floor_flag", "difference_to_N1024",
                         "fine_reference_uncertainty_N512_N1024", "highest_available_reference_N",
                         "difference_to_highest_available_reference",
                         "fine_reference_uncertainty_N1024_N2048", "fine_uncertainty_to_N64_N128_gap"))
        for mode, data in output["modes"].items():
            for n, pair in data["comparisons"].items():
                for key, item in pair["observables"].items():
                    writer.writerow((mode,n,pair["fine_n"],key,item["self_difference"],
                        item.get("self_order"),item["floor_envelope"],item["floor_flag"],
                        item.get("order_floor_flag"),item.get("difference_to_N1024"),
                        item.get("fine_reference_uncertainty_N512_N1024"),
                        item.get("highest_available_reference_N"),
                        item.get("difference_to_highest_available_reference"),
                        item.get("fine_reference_uncertainty_N1024_N2048"),
                        item.get("fine_uncertainty_to_N64_N128_gap")))
    lines = ["# Native V10 factual matrix", "", "Scientific admission: NOT_EVALUATED.", ""]
    for mode, data in output["modes"].items():
        lines += [f"## {mode}", "", f"Available N: {data['available_n']}; missing required N: {data['required_levels_missing']}; final a mismatch: {data['final_a_mismatch']}.", ""]
        for n, pair in data["comparisons"].items():
            for key in ("T_K", "ne_cm3", "HII", "HeII", "HeIII", "photon_n_per_h"):
                item = pair["observables"].get(key)
                if item:
                    extra = ""
                    if "fine_reference_uncertainty_N1024_N2048" in item:
                        extra = (f"; Δ1024–2048={item['fine_reference_uncertainty_N1024_N2048']:.9g}"
                                 f"; ratio_to_Δ64–128={item.get('fine_uncertainty_to_N64_N128_gap')}")
                    lines.append(f"- N={n}→{pair['fine_n']} {key}: Δ={item['self_difference']:.9g}; p={item.get('self_order')}; floor={item['floor_flag']}{extra}.")
        lines.append("")
    if failures:
        lines += ["## Failed or missing histories", ""] + [f"- {f}" for f in failures]
    (args.out_dir / "MATRIX_SUMMARY.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"histories": sum(map(len,modes.values())), "failures": len(failures),
                      "out_dir": str(args.out_dir)}, sort_keys=True))
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
