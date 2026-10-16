"""Independent binary64 recomputation of the native source-row geometry checks."""
import csv
import hashlib
import json
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "bass_dynamic_20261016/source_grids/matched_n121_241_481_retry/n0481/PROPOSED_REI_BACKGROUND.csv"
expected = "1104845a34658b7c99ba4d7731a955c11457cf5c9ab92b1cf49117de462b663f"
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
h0, om, orad, ol = 2.1842852410855026e-18, 0.315, 0.000092, 0.6849080000000001
report = {"schema": "rei.bass.geometry_independent_binary64.v1", "source_csv_sha256": expected,
          "note": "Python operation ordering may differ by a few ulps from Rust; this is an independent source-row recomputation.",
          "cases": {}}
for row in csv.DictReader(source.open()):
    case = row["case"]
    if case not in ("COLD_FLRW", "SIGNED_MINUS"):
        continue
    a, h, s = (float(row[k]) for k in ("a", "H_mean_per_s", "s_per_s"))
    rho = float(row["massive_rho_norm"])
    pressure = float(row["massive_pbar_norm"])
    fm = 0.0 if case == "COLD_FLRW" else 0.1
    expected_h2 = h0*h0*(om*(1.0-fm)/a**3 + orad/a**4 + ol + rho) + s*s
    h_raw = abs(h*h-expected_h2)
    h_den = max(abs(h*h), abs(expected_h2))
    hp = (h0*h0*(-3.0*om*(1.0-fm)/a**3 -4.0*orad/a**4 -3.0*(rho+pressure))-6.0*s*s)/(2.0*h)
    r_raw = abs(float(row["dH_dln_a_per_s"])-hp)
    r_den = max(abs(hp), 1e-300)
    c = report["cases"].setdefault(case, {"rows": 0, "max_signed_s_over_h_raw": 0.0,
                                            "max_sigma_raw": 0.0, "min_proper_increment_s": None})
    c["rows"] += 1
    t = float(row["proper_elapsed_s"])
    if "previous_t" in c:
        increment = t-c["previous_t"]
        c["min_proper_increment_s"] = increment if c["min_proper_increment_s"] is None else min(c["min_proper_increment_s"], increment)
    c["previous_t"] = t
    c["max_signed_s_over_h_raw"] = max(c["max_signed_s_over_h_raw"],abs(float(row["signed_s_over_H"])-s/h))
    c["max_sigma_raw"] = max(c["max_sigma_raw"],abs(float(row["Sigma"])-(3.0**0.5)*abs(float(row["signed_s_over_H"]))))
    for name, raw, den, tolerance, unit in (
        ("hamiltonian", h_raw, h_den, 3e-12*h_den, "s^-2"),
        ("raychaudhuri", r_raw, r_den, 1e-26+3e-12*abs(hp), "s^-1"),
    ):
        entry = {"raw": raw, "denominator": den, "normalized": raw/den,
                 "raw_tolerance": tolerance, "unit": unit, "a": a}
        old = c.get(name)
        if old is None or entry["normalized"] > old["normalized"]:
            c[name] = entry
for case in report["cases"].values():
    case.pop("previous_t")
out = Path(__file__).with_name("evidence") / "GEOMETRY_RESIDUAL_RECOMPUTE.json"
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(out)
