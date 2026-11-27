"""Recover literal configured Z=1..3 rows; never evaluate a rate."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
raw = (BASE / "cfit.dat").read_bytes()
rows = []
for line1, line in enumerate(raw.decode().splitlines(), 1):
    z, n = int(line[6:8]), int(line[9:11])
    if z > 3:
        continue
    rows.append({
        "id": f"V97_CI_Z{z}_N{n}", "process": "CI_direct_fit", "Z": z,
        "bound_electrons_lower_ion": n, "charge_lower": z-n,
        "provider_label": line[:5].strip(), "source_line1": line1, "raw_row": line,
        "raw_row_sha256_without_newline": hashlib.sha256(line.encode()).hexdigest(),
        "coefficients": {"dE": line[12:19].strip(), "P": line[20:21].strip(),
                         "A": line[22:31].strip(), "X": line[32:38].strip(), "K": line[39:43].strip()},
        "coefficient_units": {"dE": "eV", "P": "1", "A": "cm^3 s^-1", "X": "1", "K": "1"},
        "native_temperature_domain": {"Tmin": line[44:48].strip(), "Tmin_unit": "eV",
                                      "Tmax": line[49:53].strip(), "Tmax_unit": "keV",
                                      "variable": "electron_temperature_as_energy_kB_T",
                                      "endpoint_inclusion": "not declared by table description"},
        "formula": "k=A*(1+P*sqrt(u))/(X+u)*u^K*exp(-u);u=dE/(k_B*T expressed in eV)",
        "source_Fortran": {"version": "2, March24,1997", "T_input_unit": "K",
                           "legacy_eV_per_K_literal": "8.617385e-05", "u_greater_80_returns_zero": True,
                           "cutoff_qualification": "legacy numerical return rule, not measured physical zero"},
        "native_isotope_qualification": "elemental electronic coefficient; no isotope shift or isomer qualification",
        "state_qualification": "direct ionization aggregate; residual final-state branches unresolved",
        "dE_is_approved_chemical_Q": False, "parameter_covariance": None,
        "uncertainty_status": "not supplied by coefficient row; no physical confidence interval",
        "new_rate_evaluations": 0, "physical_admission": False,
        "source_url": "https://www.pa.uky.edu/~verner/dima/col//cfit.dat",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "format_url": "https://www.pa.uky.edu/~verner/dima/col//cfit.txt",
        "format_sha256": hashlib.sha256((BASE / "cfit.txt").read_bytes()).hexdigest(),
    })
out = {"source_total_rows": len(raw.decode().splitlines()), "configured_elemental_rows": len(rows), "rows": rows}
target = BASE / "SELECTED_ROWS.json"
payload = (json.dumps(out, ensure_ascii=False, indent=2) + "\n").encode()
if target.exists() and target.read_bytes() != payload:
    raise ValueError("SOURCE_EXTRACTION_CHANGED_PRESERVE_PREVIOUS_VERSION")
target.write_bytes(payload)
print(json.dumps({"rows": len(rows), "source_total_rows": out["source_total_rows"],
                  "sha256": hashlib.sha256(payload).hexdigest(), "rate_evaluations": 0}))
