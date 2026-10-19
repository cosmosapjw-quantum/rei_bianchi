#!/usr/bin/env python3
"""Independent Decimal96 native ledger and the BR05 N16--32/r4--8 rectangle.

Reads serialized solver outputs; never executes the solver or declares an
absolute evolving-solution error. Preserves signed differences and mixed terms.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys

D = Decimal
ROOT = Path(__file__).resolve().parents[1]
TEXT = {"case", "split", "frozen", "birth_mode"}
OBS = (
    "photons_com3", "mean_age_s", "second_age_s2", "q2", "DI", "T_K",
    "survivor_age_com_s", "survivor_age2_com_s2", "energy_P2_com3",
    "gas_thermal_com3", "gas_binding_com3", "geom_work", "thermal_change_com3",
    "chemical_change_com3", "photon_energy_com3",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        require(reader.fieldnames is not None and len(reader.fieldnames) == 54,
                f"native 54-column schema: {path}")
    require(bool(rows), f"empty history: {path}; inspect solver work/error receipt")
    for row in rows:
        require(None not in row and None not in row.values(), f"partial row: {path}")
    return rows


def numbers(row):
    data = {k: D(v) for k, v in row.items() if k not in TEXT}
    require(all(x.is_finite() for x in data.values()), "nonfinite native output")
    return data


def observables(row):
    data = numbers(row)
    require(data["photons_com3"] > 0, "conditional age requires positive mass")
    data["mean_age_s"] = data["survivor_age_com_s"] / data["photons_com3"]
    data["second_age_s2"] = data["survivor_age2_com_s2"] / data["photons_com3"]
    data["energy_P2_com3"] = data["q2"] * data["photon_energy_com3"]
    return {k: data[k] for k in OBS}


def check_native(rows, n, refinement):
    ledger = []
    maxima = {k: D(0) for k in ("number_relative", "energy_relative", "species_relative")}
    fixed = {"case": "SIGNED_MINUS", "grid": "121", "split": "false",
             "frozen": "false", "birth_mode": "fitted"}
    require(len(rows) == n, "incomplete native history")
    for step, row in enumerate(rows, 1):
        require(all(row[k] == val for k, val in fixed.items()), "native configuration mismatch")
        v = numbers(row)
        require(v["step"] == step and v["nsteps"] == n and v["refinement"] == refinement,
                "native step/refinement mismatch")
        # These controls originate as binary64 and are printed with 17 digits.
        # Compare their round-trip values to the declared binary64 input, while
        # retaining Decimal arithmetic for physical differences and ledgers.
        require(v["birth_gl"] == 2 and v["opacity"] == 4 and float(row["cx_rtol"]) == 1e-12
                and float(row["cx_atol"]) == 1e-14, "native axes/precision mismatch")
        require(v["t0"] == 0 and v["duration"] == D("8e12")
                and v["time_s"] == D("8e12") * step / n, "native time mismatch")
        for k in ("photons_com3", "absorbed_com3", "source_count", "source_energy", "HI",
                  "HeI", "HeII", "DI", "DII_m3", "photon_energy_com3", "gas_thermal_com3",
                  "gas_binding_com3", "escaped_com3"):
            require(v[k] >= 0, f"negative exported population/energy: {k}")
        nr = v["photons_com3"] + v["absorbed_com3"] - v["source_count"]
        sr = sum(v[k] for k in ("HI", "HeI", "HeII", "DI")) - v["absorbed_com3"]
        energy = sum(v[k] for k in ("photon_energy_com3", "gas_thermal_com3", "gas_binding_com3",
                                    "escaped_com3", "cmb_reservoir_com3"))
        expected = v["initial_total_energy_com3"] + v["source_energy"] + v["geom_work"]
        ns = max(v["source_count"], D("1e-300"))
        es = max(abs(energy), abs(expected), abs(v["initial_total_energy_com3"]), D("1e-300"))
        values = {"number_relative": abs(nr) / ns, "energy_relative": abs(energy - expected) / es,
                  "species_relative": abs(sr) / ns}
        for key, value in values.items():
            maxima[key] = max(maxima[key], value)
        o = observables(row)
        require(0 <= o["mean_age_s"] <= v["time_s"], "age support")
        require(o["mean_age_s"]**2 <= o["second_age_s2"] + D("2e-12") * v["time_s"]**2,
                "negative age variance")
        require(o["second_age_s2"] <= v["time_s"] * o["mean_age_s"] + D("2e-12") * v["time_s"]**2,
                "second-age support")
        require(D("-.5") <= o["q2"] <= 1, "P2 support")
        ledger.append({"N_t": n, "r": refinement, "step": step, **values})
    require(all(v < D("3e-10") for v in maxima.values()), "independent ledger failed")
    return maxima, ledger


def ratio(a, b):
    return a / b if b else None


def rectangle(f00, f10, f01, f11):
    # Input order is N,r; 2N,r; N,2r; 2N,2r. No absolute values before subtraction.
    dt0, dt1 = f10 - f00, f11 - f01
    dr0, dr1 = f01 - f00, f11 - f10
    interaction = dt1 - dt0
    require(abs(interaction - (dr1 - dr0)) <= D("1e-85") * max(abs(x) for x in (f00, f10, f01, f11)),
            "rectangle identity")
    return {"time_at_r": dt0, "time_at_2r": dt1, "birth_at_N": dr0, "birth_at_2N": dr1,
            "D_tr": interaction, "D_tr_over_time_at_2r": ratio(interaction, dt1),
            "time_contraction_ratio": ratio(abs(dt1), abs(dt0)),
            "D_tr_over_binary64_eps_scale": ratio(abs(interaction), D(2)**-52 * max(abs(x) for x in (f00, f10, f01, f11)))}


def serial(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(x) for x in value]
    return value


def write_csv(path, rows):
    require(bool(rows), "empty result table")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(serial(rows))


def analyze(root, output):
    reuse = json.loads((root / "contracts/REUSED_EVIDENCE_SHA256.json").read_text())
    lookup = {r["new_path"]: r["sha256"] for r in reuse["files"]}
    locations = {(16, 4): root / "reused_br04/evidence/native/ap_n16_r4.csv",
                 (16, 8): root / "evidence/native/ap_n16_r8.csv"}
    for n, r in ((16, 2), (32, 2), (32, 4), (32, 8)):
        locations[n, r] = root / f"reused_br04/reused_br03/evidence/native/ap_n{n}_r{r}.csv"
    histories, identities, ledger_rows = {}, [], []
    maxima = {}
    for (n, r), path in sorted(locations.items()):
        relative = str(path.relative_to(root))
        actual = digest(path)
        reused = (n, r) != (16, 8)
        if reused:
            require(actual == lookup[relative], f"reused SHA mismatch: {path}")
        else:
            receipt = json.loads(path.with_suffix(".json").read_text())
            require(receipt["exit_code"] == 0 and receipt["rows"] == 16, "new execution incomplete")
            require(receipt["csv_sha256"] == actual, "new execution SHA mismatch")
        rows = read_rows(path)
        mx, lr = check_native(rows, n, r)
        maxima[f"N{n}r{r}"] = mx
        ledger_rows.extend(lr)
        histories[n, r] = observables(rows[-1])
        identities.append({"path": relative, "sha256": actual, "bytes": path.stat().st_size,
                           "N_t": n, "r": r, "reused": reused})
    pairs, comparison = [], []
    for field in OBS:
        records = {}
        for r in (2, 4):
            row = {"field": field, "N_coarse": 16, "r_coarse": r,
                   **rectangle(histories[16, r][field], histories[32, r][field],
                               histories[16, 2*r][field], histories[32, 2*r][field])}
            pairs.append(row)
            records[r] = row
        comparison.append({"field": field, "D_tr_r2_to4": records[2]["D_tr"],
                           "D_tr_r4_to8": records[4]["D_tr"],
                           "interaction_magnitude_ratio": ratio(abs(records[4]["D_tr"]), abs(records[2]["D_tr"])),
                           "same_interaction_sign": records[2]["D_tr"] * records[4]["D_tr"] > 0})
    final_rows = [{"N_t": n, "r": r, **data} for (n, r), data in sorted(histories.items())]
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "NATIVE_FINALS.csv", final_rows)
    write_csv(output / "NATIVE_RECTANGLES.csv", pairs)
    write_csv(output / "NATIVE_INTERACTION_COMPARISON.csv", comparison)
    write_csv(output / "NATIVE_LEDGER.csv", ledger_rows)
    summary = {"schema": "rei.br05.independent_pair.v1", "status": "PASS_SCOPED",
               "precision_decimal_digits": 96, "input_files": identities,
               "native_new_histories": 1, "native_new_macrosteps": 16,
               "reused_histories_in_this_comparison": 5,
               "ledger_maxima": maxima, "rectangles": pairs, "interaction_comparison": comparison,
               "scope": "Signed finite-grid differences; no absolute error or asymptotic convergence claim.",
               "script_sha256": digest(Path(__file__)), "python_version": sys.version}
    (output / "NATIVE_PAIR_VERIFICATION.json").write_text(json.dumps(serial(summary), indent=2) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with localcontext() as context:
        context.prec = 96
        result = analyze(args.root, args.output or args.root / "evidence/independent/pair")
    print(json.dumps(serial({"status": result["status"], "new_macrosteps": 16,
                             "new_ledger": result["ledger_maxima"]["N16r8"]}), indent=2))


if __name__ == "__main__":
    main()
