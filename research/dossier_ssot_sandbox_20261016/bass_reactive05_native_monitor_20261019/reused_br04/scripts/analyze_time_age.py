#!/usr/bin/env python3
"""Read-only BR03/BR04 time-age crossed-grid analysis; no native execution.

Differences use Decimal(60) arithmetic on the actual serialized native values.
This avoids adding cancellation in the analysis; native discretization and
roundoff errors remain in the inputs. Finite differences are not error bounds.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, getcontext, localcontext
import hashlib
import io
import json
import math
from pathlib import Path
import sys

getcontext().prec = 60
D = Decimal
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BR03 = (ROOT / "reused_br03" if (ROOT / "reused_br03").is_dir()
                else ROOT.parent / "bass_reactive03_positive_birth_20261019")
BASE_GRID = ((16, 2), (32, 1), (32, 2), (32, 4), (32, 8), (64, 2), (128, 2))
EXTRA_GRID = ((16, 4), (64, 4))
TEXT_COLUMNS = {"case", "split", "frozen", "birth_mode"}
FIELDS = {
    "photons_com3": "reference-comoving m^-3",
    "mean_age_s": "s; photon-number weighted",
    "second_age_s2": "s^2; photon-number weighted raw second moment",
    "age_variance_s2": "s^2; photon-number weighted central moment",
    "survivor_age_com_s": "s reference-comoving m^-3",
    "survivor_age2_com_s2": "s^2 reference-comoving m^-3",
    "q2": "dimensionless; photon-energy weighted P2",
    "energy_P2_numerator_com3": "J reference-comoving m^-3; reconstructed E_gamma*q2",
    "DI": "DI photoabsorption events reference-comoving m^-3",
    "DII_m3": "proper m^-3",
    "T_K": "K",
    "gas_thermal_com3": "J reference-comoving m^-3",
    "thermal_change_com3": "J reference-comoving m^-3; signed cumulative native thermal change",
    "geom_work": "J reference-comoving m^-3; signed cumulative geometry work",
    "photon_energy_com3": "J reference-comoving m^-3",
    "gas_binding_com3": "J reference-comoving m^-3",
    "chemical_change_com3": "J reference-comoving m^-3; signed cumulative native binding change",
}
FIXED_CONFIG = (
    "case", "grid", "t0", "duration", "split", "frozen", "birth_gl",
    "opacity", "cx_rtol", "cx_atol", "birth_mode",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def name_for(n: int, r: int) -> str:
    return f"ap_n{n}_r{r}"


def observables(row: dict[str, str]) -> dict[str, Decimal]:
    values = {key: D(value) for key, value in row.items() if key not in TEXT_COLUMNS}
    require(all(value.is_finite() for value in values.values()), "non-finite native number")
    count = values["photons_com3"]
    require(count > 0, "mean/second age requires positive surviving photon count")
    values["mean_age_s"] = values["survivor_age_com_s"] / count
    values["second_age_s2"] = values["survivor_age2_com_s2"] / count
    values["age_variance_s2"] = values["second_age_s2"] - values["mean_age_s"] ** 2
    values["energy_P2_numerator_com3"] = values["photon_energy_com3"] * values["q2"]
    return {field: values[field] for field in FIELDS}


def safe_div(a: Decimal, b: Decimal) -> Decimal | None:
    return a / b if b else None


def difference(a: Decimal, b: Decimal) -> dict:
    delta = b - a
    scale = max(abs(a), abs(b))
    return {
        "absolute": delta,
        "relative_to_coarse_signed_value": safe_div(delta, a),
        "scaled_by_max_magnitude": safe_div(delta, scale),
        "difference_over_binary64_eps_scale": safe_div(delta, D(2) ** -52 * scale),
    }


def order(d0: Decimal, d1: Decimal) -> dict:
    if not d0 or not d1:
        return {"value": None, "status": "ZERO_DIFFERENCE"}
    if (d0 > 0) != (d1 > 0):
        return {"value": None, "status": "SIGN_CHANGE"}
    return {"value": float((abs(d0 / d1)).ln() / D(2).ln()),
            "status": "FORMAL_SAME_SIGN_RATIO"}


def series(values: list[Decimal]) -> dict:
    changes = [difference(a, b) for a, b in zip(values, values[1:])]
    deltas = [change["absolute"] for change in changes]
    return {"values": values, "changes": changes,
            "formal_orders": [order(a, b) for a, b in zip(deltas, deltas[1:])]}


def _mixed_at_precision(f00: Decimal, f10: Decimal, f01: Decimal, f11: Decimal) -> dict:
    """Corners are (N,r),(2N,r),(N,2r),(2N,2r), respectively."""
    time_coarse = f10 - f00
    time_refined = f11 - f01
    birth_coarse = f01 - f00
    birth_refined = f11 - f10
    interaction = time_refined - time_coarse
    require(interaction == birth_refined - birth_coarse, "mixed-difference identity")
    scale = max(abs(x) for x in (f00, f10, f01, f11))
    return {
        "corner_values_Nr_2Nr_N2r_2N2r": [f00, f10, f01, f11],
        "time_difference_at_r": time_coarse,
        "time_difference_at_2r": time_refined,
        "birth_difference_at_N": birth_coarse,
        "birth_difference_at_2N": birth_refined,
        "D_tr": interaction,
        "D_tr_scaled_by_max_corner_magnitude": safe_div(interaction, scale),
        "D_tr_over_time_difference_at_2r": safe_div(interaction, time_refined),
        "D_tr_over_birth_difference_at_N": safe_div(interaction, birth_coarse),
        "cancellation_condition_indicator": safe_div(sum(abs(x) for x in (f00, f10, f01, f11)), abs(interaction)),
        "D_tr_over_binary64_eps_corner_scale": safe_div(interaction, D(2) ** -52 * scale),
    }


def mixed(f00: Decimal, f10: Decimal, f01: Decimal, f11: Decimal) -> dict:
    # Derived observables have up to 60 significant decimal digits. Extra
    # working precision preserves their exact four-corner subtraction identity.
    with localcontext() as context:
        context.prec = 96
        return _mixed_at_precision(f00, f10, f01, f11)


def complete_rectangles(grid: set[tuple[int, int]]) -> list[tuple[int, int]]:
    return [(n, r) for n, r in sorted(grid)
            if {(n, r), (2*n, r), (n, 2*r), (2*n, 2*r)} <= grid]


def check_new_history(rows: list[dict[str, str]]) -> dict:
    """Independent primitive checks for genuinely new BR04 histories only."""
    maxima = {"number_relative": D(0), "energy_relative": D(0), "species_relative": D(0)}
    for row in rows:
        v = {k: D(s) for k, s in row.items() if k not in TEXT_COLUMNS}
        require(all(x.is_finite() for x in v.values()), "non-finite native data")
        for key in ("photons_com3", "source_count", "absorbed_com3", "HI", "HeI", "HeII", "DI", "DII_m3",
                    "gas_thermal_com3", "gas_binding_com3", "photon_energy_com3", "escaped_com3"):
            require(v[key] >= 0, f"negative exported native quantity: {key}")
        number = v["photons_com3"] + v["absorbed_com3"] - v["source_count"]
        species = sum(v[k] for k in ("HI", "HeI", "HeII", "DI")) - v["absorbed_com3"]
        total = sum(v[k] for k in ("photon_energy_com3", "gas_thermal_com3", "gas_binding_com3", "escaped_com3", "cmb_reservoir_com3"))
        expected = v["initial_total_energy_com3"] + v["source_energy"] + v["geom_work"]
        ns = max(abs(v["source_count"]), D("1e-300"))
        es = max(abs(total), abs(expected), abs(v["initial_total_energy_com3"]), D("1e-300"))
        maxima["number_relative"] = max(maxima["number_relative"], abs(number) / ns)
        maxima["species_relative"] = max(maxima["species_relative"], abs(species) / ns)
        maxima["energy_relative"] = max(maxima["energy_relative"], abs(total - expected) / es)
        o = observables(row)
        age = v["time_s"] - v["t0"]
        tol = D("2e-12") * age
        require(-tol <= o["mean_age_s"] <= age + tol, "mean-age support")
        require(o["age_variance_s2"] >= -D("2e-12") * age**2, "age variance")
        require(o["second_age_s2"] <= age * o["mean_age_s"] + D("2e-12") * age**2, "second-age support")
        require(D("-0.5") <= v["q2"] <= 1, "energy-weighted P2 support")
    require(all(x < D("3e-10") for x in maxima.values()), "independent native ledger failure")
    return {"status": "PASS_SCOPED", "maxima": maxima,
            "population_scope": "exported DII and four photoevent channels; no full 13-species export"}


def read_history(directory: Path, n: int, r: int, expected_sha: str | None = None) -> dict:
    name = name_for(n, r)
    paths = [directory / (name + suffix) for suffix in (".csv", ".json", ".stderr")]
    raw = [path.read_bytes() for path in paths]
    receipt = json.loads(raw[1])
    require(receipt["name"] == name, f"receipt name: {name}")
    require(sha(raw[0]) == receipt["csv_sha256"], f"receipt SHA: {name}")
    if expected_sha:
        require(sha(raw[0]) == expected_sha, f"BR03 reused audit SHA changed: {name}")
    reader = csv.DictReader(io.StringIO(raw[0].decode("utf-8")))
    rows = list(reader)
    require(reader.fieldnames is not None and len(reader.fieldnames) == 54, f"54-field schema: {name}")
    require(receipt["exit_code"] == 0 and receipt["status"] == "COMPLETED", f"native completion: {name}")
    require(receipt.get("failure_class") is None, f"unexpected failure classification: {name}")
    require(receipt["rows"] == receipt["planned_rows"] == len(rows) == n, f"row count: {name}")
    require(rows[-1] == receipt["final"], f"final row receipt: {name}")
    require(raw[2].decode("utf-8") == receipt["stderr"] == "", f"stderr: {name}")
    cmd = receipt["command"]
    require(len(cmd) == 12, f"native argument count: {name}")
    require(cmd[1:9] == ["SIGNED_MINUS", "121", str(n), "0", "8e12", "false", "false", "2"], f"native input identity: {name}")
    require(D(cmd[9]) == 4 and D(cmd[10]) == D("1e-12") and cmd[11] == str(r), f"native precision identity: {name}")
    config = {key: rows[-1][key] for key in FIXED_CONFIG}
    for step, row in enumerate(rows, 1):
        require(set(row) == set(reader.fieldnames) and None not in row.values(), f"partial row: {name}/{step}")
        require(D(row["step"]) == step and D(row["nsteps"]) == n and D(row["refinement"]) == r, f"grid fields: {name}/{step}")
        require({key: row[key] for key in FIXED_CONFIG} == config, f"changing config: {name}/{step}")
        require(D(row["time_s"]) == D(row["t0"]) + D(row["duration"]) * step / n, f"time grid: {name}/{step}")
    require(all(path.read_bytes() == value for path, value in zip(paths, raw)), f"input changed during read: {name}")
    return {"name": name, "N_t": n, "r": r, "config": config, "rows": rows,
            "final": observables(rows[-1]), "receipt": receipt,
            "identity": [{"path": str(path), "bytes": len(value), "sha256": sha(value)} for path, value in zip(paths, raw)],
            "reuse": "PR03_AUDIT_SAME_CSV_BYTES" if expected_sha else "NEW_BR04_NATIVE_HISTORY",
            "verification": {"status": "REUSED_SAME_CSV_IDENTITY"} if expected_sha else check_new_history(rows)}


def history_contrast(a: dict, b: dict) -> dict:
    fine = {D(row["time_s"]): observables(row) for row in b["rows"]}
    result = {field: {"max_absolute_at_common_times": D(0), "max_scaled_at_common_times": D(0), "common_times": 0} for field in FIELDS}
    for row in a["rows"]:
        time = D(row["time_s"])
        require(time in fine, "time comparison requires actual common endpoints; no interpolation")
        coarse = observables(row)
        for field in FIELDS:
            change = difference(coarse[field], fine[time][field])
            item = result[field]
            item["max_absolute_at_common_times"] = max(item["max_absolute_at_common_times"], abs(change["absolute"]))
            item["max_scaled_at_common_times"] = max(item["max_scaled_at_common_times"], abs(change["scaled_by_max_magnitude"] or 0))
            item["common_times"] += 1
    return result


def rectangle_result(grid: dict, n: int, r: int) -> dict:
    keys = ((n, r), (2*n, r), (n, 2*r), (2*n, 2*r))
    cases = [grid[key] for key in keys]
    maps = [{D(row["time_s"]): observables(row) for row in case["rows"]} for case in cases]
    common = sorted(set.intersection(*(set(item) for item in maps)))
    require(len(common) == n, "crossed rectangle common time count")
    history = []
    for time in common:
        history.append({"time_s": time, "fields": {field: mixed(*(item[time][field] for item in maps)) for field in FIELDS}})
    final = history[-1]["fields"]
    return {"N_pair": [n, 2*n], "r_pair": [r, 2*r], "corners": [case["name"] for case in cases],
            "final": final, "common_time_history": history,
            "max_abs_D_tr": {field: max(abs(row["fields"][field]["D_tr"]) for row in history) for field in FIELDS}}


def cost_proposal(br03: Path, grid: dict) -> dict:
    names = [name_for(32, r) for r in (1, 2, 4, 8)]
    receipts = [json.loads((br03 / "evidence/native" / (name + ".json")).read_text()) for name in names]
    walls = [D(str(receipt["wall_s"])) for receipt in receipts]
    ratios = [b / a for a, b in zip(walls, walls[1:])]
    proposals = []
    for n, r in EXTRA_GRID:
        base = grid[(n, 2)]["receipt"]
        wall = D(str(base["wall_s"]))
        proposals.append({"case": name_for(n, r), "status": "MEASURED" if (n, r) in grid else "PROPOSED_NOT_RUN",
                          "same_N_r2_measured_s": wall,
                          "point_estimate_s": wall * ratios[1],
                          "empirical_refinement_ratio_range_s": [wall * min(ratios), wall * max(ratios)],
                          "actual_s_if_available": grid.get((n, r), {}).get("receipt", {}).get("wall_s"),
                          "new_rectangle": [n, 32] if n == 16 else [32, n]})
    return {"measured_N32_refinement_wall_s": dict(zip(names, walls)), "measured_doubling_ratios": ratios,
            "assumption": "transfer observed N32 refinement cost ratio to each fixed N; wall measurements include earlier worker contention",
            "range_is": "empirical ratio envelope, not a probabilistic interval or resource guarantee",
            "proposals": proposals,
            "point_estimate_sum_s": sum(proposal["point_estimate_s"] for proposal in proposals)}


def serialize(value):
    if isinstance(value, D):
        return str(value)
    raise TypeError(type(value).__name__)


def generate(br03: Path, extra: Path | None) -> dict:
    audit_path = br03 / "evidence/independent_native/INDEPENDENT_NATIVE_AUDIT.json"
    audit_raw = audit_path.read_bytes()
    audit = json.loads(audit_raw)
    require(audit["status"] == "PASS_SCOPED", "prior independent native audit status")
    prior_sha = {case["name"]: case["identity"]["csv"]["sha256"] for case in audit["cases"]}
    science_path = br03 / "evidence/SCIENCE_RESULTS.json"
    science_raw = science_path.read_bytes()
    science = json.loads(science_raw)
    grid = {(n, r): read_history(br03 / "evidence/native", n, r, prior_sha[name_for(n, r)]) for n, r in BASE_GRID}
    for n, r in BASE_GRID:
        for field, value in grid[(n, r)]["final"].items():
            if field in science["finals"][name_for(n, r)]:
                old = float(science["finals"][name_for(n, r)][field])
                require(math.isclose(float(value), old, rel_tol=8e-15, abs_tol=0.0), f"SCIENCE_RESULTS semantic identity: {n}/{r}/{field}")
    if extra is not None:
        for n, r in EXTRA_GRID:
            receipt_path = extra / (name_for(n, r) + ".json")
            if receipt_path.exists():
                grid[(n, r)] = read_history(extra, n, r)
    reference_config = grid[(32, 2)]["config"]
    require(all(case["config"] == reference_config for case in grid.values()), "crossed native configurations differ")
    rectangles = {f"N{n}_{2*n}_r{r}_{2*r}": rectangle_result(grid, n, r) for n, r in complete_rectangles(set(grid))}
    time_slices = {}
    for r in sorted({r for _, r in grid}):
        ns = sorted(n for n, rr in grid if rr == r)
        if len(ns) > 1:
            time_slices[str(r)] = {"N_t": ns, "h_s": [D(reference_config["duration"]) / n for n in ns],
                                   "fields": {field: series([grid[(n, r)]["final"][field] for n in ns]) for field in FIELDS},
                                   "common_time_comparisons": {f"{a}_{b}": history_contrast(grid[(a, r)], grid[(b, r)]) for a, b in zip(ns, ns[1:])}}
    birth_slices = {}
    for n in sorted({n for n, _ in grid}):
        rs = sorted(r for nn, r in grid if nn == n)
        if len(rs) > 1:
            birth_slices[str(n)] = {"r": rs, "epsilon": [D(1) / r for r in rs],
                                    "fields": {field: series([grid[(n, r)]["final"][field] for r in rs]) for field in FIELDS},
                                    "common_time_comparisons": {f"{a}_{b}": history_contrast(grid[(n, a)], grid[(n, b)]) for a, b in zip(rs, rs[1:])}}
    interaction_orders = {}
    if "N16_32_r2_4" in rectangles and "N32_64_r2_4" in rectangles:
        for field in FIELDS:
            ds = [rectangles[key]["final"][field]["D_tr"] for key in ("N16_32_r2_4", "N32_64_r2_4")]
            interaction_orders[field] = {"D_tr_values": ds, "formal_h_order": order(*ds),
                                         "scope": "h dependence of interaction at fixed r pair 2,4; requires a dominant stable mixed error term"}
    reused = [{"name": case["name"], "N_t": case["N_t"], "r": case["r"],
               "final": case["final"], "wall_s": case["receipt"]["wall_s"],
               "recorded_binary_sha256": case["receipt"]["binary_sha256"],
               "identity": case["identity"], "reuse": case["reuse"], "verification": case["verification"]} for _, case in sorted(grid.items())]
    return {
        "schema": "rei.bass.reactive04.independent_time_age.v1",
        "status": "CROSSED_FINITE_GRID_DIFFERENCES_MEASURED" if rectangles else "BR03_AXES_REUSED_CROSSED_INPUTS_PENDING",
        "arithmetic": "Decimal(60) on serialized raw native values; JSON physical values/differences are decimal strings",
        "script_sha256": sha(Path(__file__).read_bytes()),
        "inputs": [{"path": str(audit_path), "sha256": sha(audit_raw)}, {"path": str(science_path), "sha256": sha(science_raw)}],
        "configuration": reference_config, "field_units": FIELDS,
        "baseline_grid": BASE_GRID, "available_grid": sorted(grid), "complete_rectangles": sorted(rectangles),
        "baseline_complete_rectangle_count": len(complete_rectangles(set(BASE_GRID))),
        "missing_recommended_cases": [name_for(n, r) for n, r in EXTRA_GRID if (n, r) not in grid],
        "cases": reused, "fixed_r_time_slices": time_slices, "fixed_N_birth_slices": birth_slices,
        "rectangles": rectangles, "conditional_interaction_orders": interaction_orders,
        "cost": cost_proposal(br03, grid),
        "mathematical_contract": {
            "coordinates": "h=T/N_t and epsilon=1/r; doubling N_t or r halves the corresponding coordinate",
            "exact_identity": "D_tr=(F(2N,2r)-F(N,2r))-(F(2N,r)-F(N,r))=Delta_r(2N)-Delta_r(N)",
            "conditional_expansion": "F=F_star+A*h^p+B*epsilon^q+C*h^p*epsilon^q+R",
            "conditional_mixed_term": "D_tr=C*h^p*epsilon^q*(2^(-p)-1)*(2^(-q)-1)+Delta_t Delta_r R",
            "assumptions_for_separation": [
                "same final physical time, source, spectrum, angles, geometry donor, initial state, opacity panels and native CX tolerance",
                "stable dominant powers p,q and coefficients over the compared grids; mixed remainder smaller than the retained term",
                "native solver/roundoff noise must be smaller than the observed differences; Decimal analysis does not certify that premise",
                "epsilon=1/r is a nominal parameter: tau=kappa*h changes the geometric panel partition when h changes",
                "ratio observables mean age, second age and q2 can have mixed differences generated by numerator/denominator coupling",
            ],
            "identified_now": "finite-grid sensitivity and a mixed defect for every complete rectangle; no exact evolving-reference error",
            "additional_inputs": [
                "one r8 case at N16 or N64 gives a second r-pair interaction to study its refinement dependence",
                "N128r4 extends the r4 time slice to the finest existing temporal level",
                "full age-energy-angle correlations or specified additional observables are needed beyond the currently exported marginal moments",
            ],
            "difference_precision_note": "binary64-epsilon and cancellation indicators describe arithmetic sensitivity only; no physical or solver error bound",
        },
        "scientific_decision": "SCOPED_DIAGNOSTICS_ONLY; LONGSPAN_SOLUTION remains NOT_ADMITTED pending the stated convergence obligations",
        "native_execution_by_this_script": False, "input_directories_written": False,
    }


def write_outputs(result: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    raw = json.dumps(result, default=serialize, indent=2, allow_nan=False) + "\n"
    (out / "TIME_AGE_ANALYSIS.json").write_text(raw)
    with (out / "FINAL_OBSERVABLES.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case", "N_t", "r", "wall_s", *FIELDS])
        writer.writeheader()
        for case in result["cases"]:
            writer.writerow({"case": case["name"], "N_t": case["N_t"], "r": case["r"], "wall_s": case["wall_s"], **case["final"]})
    with (out / "MIXED_DIFFERENCES.csv").open("x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rectangle", "field", "time_s", "D_tr", "D_tr_scaled", "delta_t_r", "delta_t_2r", "delta_r_N", "delta_r_2N"])
        for name, rect in result["rectangles"].items():
            for row in rect["common_time_history"]:
                for field, values in row["fields"].items():
                    writer.writerow([name, field, row["time_s"], values["D_tr"], values["D_tr_scaled_by_max_corner_magnitude"],
                                     values["time_difference_at_r"], values["time_difference_at_2r"],
                                     values["birth_difference_at_N"], values["birth_difference_at_2N"]])
    manifest = {p.name: {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in sorted(out.iterdir()) if p.is_file()}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--br03-root", type=Path, default=DEFAULT_BR03)
    p.add_argument("--extra-native", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    result = generate(args.br03_root.resolve(), args.extra_native.resolve() if args.extra_native else None)
    write_outputs(result, args.output_dir.resolve())
    print(json.dumps({"status": result["status"], "cases": len(result["cases"]),
                      "rectangles": result["complete_rectangles"], "missing": result["missing_recommended_cases"]}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"INPUT_OR_ANALYSIS_FAILURE: {exc}", file=sys.stderr)
        sys.exit(2)
