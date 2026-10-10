"""Frozen 5000 K raw-value audit; never evolves or admits a cold history."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HANDOFF = "docs/atomic_reionization_handoff_20261004_v1/"
CSOURCE = HANDOFF + "runtime_returns/evidence/F01_reference/selected_original_functions.c"
PINS = {
    "rust/rei_microphysics/src/atomic_provider.rs": "b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
    CSOURCE: "8150f4e7bead09b67fae70c13c3d3df74d70aac1d4fc47f2272c24411a1bba6c",
    HANDOFF + "common/external_reference/grackle_3_4_1/rate_functions.c": "a900e726413da39bb24fc506846a09f7e0e4addbd5152197ca76d0e22ad02cea",
}
NAMES = ["k1", "k2", "k3", "k4", "k5", "k6", "ceHI", "ceHeI", "ceHeII",
         "ciHeIS", "ciHI", "ciHeI", "ciHeII", "reHII", "reHeII1", "reHeII2",
         "reHeIII", "brem"]
T = 5000.0
TOLERANCE = 3e-12


def verify_sources(root=ROOT):
    actual = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in PINS}
    if actual != PINS:
        raise ValueError("IMMUTABLE_SOURCE_IDENTITY_MISMATCH")
    return actual


def unclipped_expressions():
    """Evaluate vendor algebra without its floor/cap/branch substitutions.

    These expressions are diagnostic extensions, not atomic predictions at T.
    Other literal factors, including Grackle's raw HeIII 8*T, are retained.
    """
    te = T / 11605.0
    l = math.log(te)

    def polynomial(coefs):
        return math.exp(sum(c * l**i for i, c in enumerate(coefs)))

    k1 = polynomial([-32.71396786375, 13.53655609057, -5.739328757388,
                     1.563154982022, -.2877056004391, .03482559773736999,
                     -.00263197617559, .0001119543953861, -2.039149852002e-6])
    k2 = polynomial([-28.61303380689232, -.7241125657826851, -.02026044731984691,
                     -.002380861877349834, -.0003212605213188796, -.00001421502914054107,
                     4.989108920299513e-6, 5.755614137575758e-7, -1.856767039775261e-8,
                     -3.071135243196595e-9])
    k3 = polynomial([-44.09864886561001, 23.91596563469, -10.75323019821,
                     3.058038757198, -.5685118909884001, .06795391233790001,
                     -.005009056101857001, .0002067236157507, -3.649161410833e-6])
    k4 = (1.54e-9 * (1 + .3 / math.exp(8.099328789667 / te)) /
          (math.exp(40.49664394833662 / te) * te**1.5) + 3.92e-13 / te**.6353)
    k5 = polynomial([-68.71040990212001, 43.93347632635, -18.48066993568,
                     4.701626486759002, -.7692466334492, .08113042097303,
                     -.005324020628287001, .0001975705312221, -3.165581065665e-6])
    lam = 2 * 157807.0 / T
    lamhe = 2 * 631515.0 / T
    return dict(zip(NAMES, [
        k1, k2, k3, k4, k5,
        3.36e-10 / math.sqrt(T) / (T / 1e3)**.2 / (1 + (T / 1e6)**.7),
        7.5e-19 * math.exp(-118348 / T) / (1 + math.sqrt(T / 1e5)),
        9.1e-27 * math.exp(-13179 / T) * T**(-.1687) / (1 + math.sqrt(T / 1e5)),
        5.54e-17 * math.exp(-473638 / T) * T**(-.3970) / (1 + math.sqrt(T / 1e5)),
        5.01e-27 * T**(-.1687) * math.exp(-55338 / T) / (1 + math.sqrt(T / 1e5)),
        2.18e-11 * k1, 3.94e-11 * k3, 8.72e-11 * k5,
        1.778e-29 * T * lam**1.965 / (1 + (lam / .541)**.502)**2.697,
        3e-14 * 1.3806504e-16 * T * (2 * 285335 / T)**.654,
        1.24e-13 * T**(-1.5) * math.exp(-470000 / T) * (1 + .3 * math.exp(-94000 / T)),
        8 * 1.778e-29 * T * lamhe**1.965 / (1 + (lamhe / .541)**.502)**2.697,
        1.43e-27 * math.sqrt(T) * (1.1 + .34 * math.exp(-(5.5 - math.log10(T))**2 / 3)),
    ]))


BRANCHES = {
    "k1": "T_eV<=0.8; max(1e-20, polynomial) floor active",
    "k2": "T<=5500; alias k4 instead of HII polynomial",
    "k3": "T_eV<=0.8; constant tiny=1e-20",
    "k4": "T_eV<=0.8; RR-only branch; DR term omitted",
    "k5": "T_eV<=0.8; constant tiny=1e-20",
    "ceHeII": "473638/T > ln(1e30); exponential argument capped",
    "ciHI": "2.18e-11 times floored k1",
    "ciHeI": "3.94e-11 times constant k3",
    "ciHeII": "8.72e-11 times constant k5",
    "reHeII2": "470000/T > ln(1e30); first exponential capped; second uncapped",
    "reHeIII": "Case-A raw 8*T prefactor preserved",
}


def hg_rr():
    lam = 2 * 157807.0 / T
    return {
        "HII": 1.269e-13 * lam**1.503 / (1 + (lam / .522)**.470)**1.923,
        "HeII": 3e-14 * (2 * 285335.0 / T)**.654,
    }


def parse_rust(stdout):
    rows = list(csv.reader(io.StringIO(stdout)))
    if [r[0] for r in rows] != [n + "_rate" for n in NAMES] or any(len(r) != 6 for r in rows):
        raise ValueError("RUST_PROBE_SCHEMA")
    return {name: {"rust": float(r[1]), "unit": r[2], "density_prefactor": r[3],
                   "consumer_admission": r[4] == "true", "physical_support_resolved": r[5] == "true"}
            for name, r in zip(NAMES, rows)}


def validate_rows(rows, c_values):
    if set(rows) != set(NAMES) or set(c_values) != set(NAMES):
        raise ValueError("COEFFICIENT_SET")
    expected_units = {n: ("cm3/s" if n.startswith("k") else
                          "erg*cm6/s" if n in ("ceHeI", "ciHeIS") else "erg*cm3/s") for n in NAMES}
    expr = unclipped_expressions()
    for n in NAMES:
        row = rows[n]
        c = c_values[n]
        if not (math.isfinite(row["rust"]) and row["rust"] > 0 and math.isfinite(c) and c > 0):
            raise ValueError("NONFINITE_OR_NONPOSITIVE_COEFFICIENT:" + n)
        error = abs(row["rust"] - c) / abs(c)
        if error > TOLERANCE:
            raise ValueError("C_PARITY:" + n)
        if row["unit"] != expected_units[n] or row["consumer_admission"] or row["physical_support_resolved"]:
            raise ValueError("RAW_PROVIDER_METADATA:" + n)
        row.update(c=c, relative_c_error=error, branch=BRANCHES.get(n, "enabled Case-A expression; no active cap/floor"),
                   unclipped_expression=expr[n], raw_to_unclipped=row["rust"] / expr[n])
    if rows["k2"]["rust"] != rows["k4"]["rust"]:
        raise ValueError("EXPECTED_K2_K4_ALIAS")
    if not all(rows[n]["rust"] == 1e-20 for n in ("k1", "k3", "k5")):
        raise ValueError("EXPECTED_TINY_FLOORS")
    return rows


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    commands = []

    def command(argv, label, **kwargs):
        proc = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=120, **kwargs)
        (output / (label + ".stdout.log")).write_text(proc.stdout)
        (output / (label + ".stderr.log")).write_text(proc.stderr)
        commands.append({"argv": argv, "exit_code": proc.returncode, "stdout": label + ".stdout.log", "stderr": label + ".stderr.log"})
        (output / "EXECUTION.json").write_text(json.dumps({"commands": commands}, indent=2) + "\n")
        proc.check_returncode()
        return proc.stdout

    pins = verify_sources()
    with tempfile.TemporaryDirectory(prefix="rei-p02a-") as temp:
        temp = Path(temp)
        # Source inclusion retains the archived original function bodies and license.
        driver = '#include <stdio.h>\n#include "' + str(ROOT / CSOURCE) + '"\nint main(void) {\nchemistry_data flags = {0,1,1,1,1};\n'
        driver += "\n".join('printf("' + n + ',%.17e\\n", ' + n + '_rate(5000.0, 1.0, &flags));' for n in NAMES)
        driver += "\nreturn 0;\n}\n"
        # This is generated build input, not a source/repository edit.
        (temp / "probe.c").write_text(driver)
        command(["cc", "-std=c99", "-O2", str(temp / "probe.c"), "-lm", "-o", str(temp / "probe")], "c_build")
        c_stdout = command([str(temp / "probe")], "c_probe")
        rust_stdout = command(["cargo", "run", "--release", "--locked", "--manifest-path", "rust/rei_microphysics/Cargo.toml",
                               "--example", "atomic_lowt_probe", "--target-dir", str(temp / "target")], "rust_probe")
    c_rows = list(csv.reader(io.StringIO(c_stdout)))
    if len(c_rows) != 18 or [r[0] for r in c_rows] != NAMES:
        raise ValueError("C_PROBE_SCHEMA")
    rows = validate_rows(parse_rust(rust_stdout), {r[0]: float(r[1]) for r in c_rows})
    hg = hg_rr()
    result = {
        "status": "PASS_DIAGNOSTIC", "temperature_k": T, "recombination_case": "A", "c_units": 1.0,
        "low_t_physical_provider_admission": "HOLD", "comparator_domain": "COMPARATOR_DOMAIN_PARTIAL",
        "source_sha256": pins, "relative_tolerance": TOLERANCE,
        "coefficient_count": len(rows), "maximum_relative_c_error": max(r["relative_c_error"] for r in rows.values()),
        "coefficients": rows,
        "HG97_RR_comparison": {species: {"HG97_cm3_per_s": value, "raw_grackle_cm3_per_s": rows[n]["rust"],
                                          "signed_relative_difference": rows[n]["rust"] / value - 1}
                               for species, n, value in (("HII", "k2", hg["HII"]), ("HeII", "k4", hg["HeII"]))},
        "scientific_limit": "Clipping ratios and prescription differences are implementation diagnostics, not physical errors or cold-history certification.",
        "thermal_and_binding_ledger": "NOT_EVALUATED; no density state, thermal closure or photon history supplied",
        "coupled_intervals": 0, "convergence": "NOT_APPLICABLE: one fixed-temperature coefficient evaluation",
        "python": platform.python_version(),
    }
    (output / "VALIDATION.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "coefficient_count", "maximum_relative_c_error", "low_t_physical_provider_admission")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new evidence directory; never overwrite")
    run(parser.parse_args().output)
