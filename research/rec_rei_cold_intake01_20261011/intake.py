"""Four saved REC rows -> public REI isotope/EOS/FLRW APIs; no evolution."""
import copy
import hashlib
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KB = 1.380649e-23
BOUND = Decimal(64) * Decimal.from_float(sys.float_info.epsilon)
PINS = {
    "inputs/baseline.json": "f39c09cac72359ecff4366ba5e0828d75c7d44185d126fd499f9e741bfb5005e",
    "inputs/refined.json": "4204d0ea44b23c868e5c5e330029bc35303ae85466cdb4671e60ba9d4a140611",
    "inputs/REC_CONTRACT.json": "07630cbd86d6a8cc314e513a252dd582bab80b5153247c07e51a7c9195452f28",
}
SOURCE_PINS = {
    "rust/rei_microphysics/src/atomic_provider.rs": "b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
    "rust/rei_microphysics/src/isotope_state.rs": "a3a750c3751ea30621482c341e89f690e517c3ad122e56231d2810c62afe8708",
}

def require(condition, tag):
    if not condition:
        raise ValueError(tag)

def verify_bytes(payload, sha):
    require(hashlib.sha256(payload).hexdigest() == sha, "SOURCE_BYTE_MISMATCH")

def load_rows():
    for path, sha in PINS.items():
        verify_bytes((HERE / path).read_bytes(), sha)
    for path, sha in SOURCE_PINS.items():
        verify_bytes((ROOT / path).read_bytes(), sha)
    rows = []
    for history in ("baseline", "refined"):
        saved = json.loads((HERE / "inputs" / (history + ".json")).read_text())
        require(len(saved) == 2, "EXACT_ROW_COUNT")
        for z, row in zip((20.0, 15.9), saved):
            require(row["endpoint"]["z"] == z, "SAVED_EPOCH")
            require(row["helium_mapping"] == "neutral-after-original-HyRec-cutoff", "HELIUM_MAPPING")
            ep = row["endpoint"]
            require(all(math.isfinite(v) for v in ep.values()), "INPUT_FINITE")
            require(0 < ep["xe_per_H"] < 1 and 0 < ep["Tm_K"] < 100, "INPUT_DOMAIN")
            require(ep["xHeI"] == 1 and ep["xHeII"] == ep["xHeIII"] == 0, "HELIUM_STATE")
            rows.append({"history": history, "saved_endpoint": ep,
                         "helium_mapping": row["helium_mapping"],
                         "xe_semantics": "electrons per hydrogen nucleus; local xHII under neutral-He mapping",
                         "density_units": "proper m-3"})
    return rows

def near(value, expected, tag, errors):
    require(math.isfinite(value), tag + "_FINITE")
    v = Decimal.from_float(value)
    if expected == 0:
        require(value == 0.0, tag + "_STRUCTURAL_ZERO")
        errors[tag] = 0.0
    else:
        err = abs(v - expected) / abs(expected)
        require(err <= BOUND, tag + "_DECIMAL80")
        errors[tag] = float(err)

def validate_row(row):
    ep, out = row["saved_endpoint"], row["consumer"]
    require(row["density_units"] == "proper m-3", "DENSITY_UNITS")
    require("QHII" not in row and "QHII" not in out, "XE_IS_NOT_QHII")
    require(row["xe_semantics"] == "electrons per hydrogen nucleus; local xHII under neutral-He mapping", "XE_SEMANTICS")
    require(row["helium_mapping"] == "neutral-after-original-HyRec-cutoff", "HELIUM_MAPPING")
    require(out["provider"] == {"status": "UNAVAILABLE", "error": "RAW_TEMPERATURE_DOMAIN", "process": "K2", "case": "A"}, "PROVIDER_REJECT")
    errors = {}
    with localcontext() as ctx:
        ctx.prec = 80
        d = lambda x: Decimal.from_float(x)
        nh, he, xe, t, kb = map(d, (ep["nH_m3"], ep["nHe_m3"], ep["xe_per_H"], ep["Tm_K"], KB))
        ne = nh * xe
        particles = nh + he + ne
        u = Decimal("1.5") * kb * t * particles
        expected_species = [Decimal(0)] * 13
        expected_species[1] = nh * (1 - xe)
        expected_species[2] = ne
        expected_species[10] = he
        require(len(out["species_m3"]) == 13, "SPECIES_COUNT")
        require(all(math.isfinite(v) and v >= 0 for v in out["species_m3"]), "SPECIES_DOMAIN")
        for i, (v, exp) in enumerate(zip(out["species_m3"], expected_species)):
            near(v, exp, f"species_{i}", errors)
        expected = {"baryons_m3": nh + 4 * he, "heavy_m3": nh + he, "ne_m3": ne,
                    "particles_m3": particles, "u_J_m3": u, "nH_cm3": nh / 1000000,
                    "nHe_cm3": he / 1000000, "u_erg_cm3": 10 * u, "Tm_roundtrip_K": t}
        for key, exp in expected.items():
            near(out[key], exp, key, errors)
        near(sum(out["species_m3"]), nh + he, "species_normalization", errors)
        near(ep["ne_m3"], ne, "saved_charge", errors)
        near(out["species_m3"][2], d(out["ne_m3"]), "charge_neutrality", errors)
        for i in range(3):
            near(out["fractions"][i], xe if i == 0 else Decimal(0), f"fraction_{i}", errors)
            near(out["scale"][i], d(ep["a"]), f"scale_{i}", errors)
            near(out["rate_s1"][i], d(ep["H_s1"]), f"rate_{i}", errors)
    return errors

def validate(rows):
    require(len(rows) == 4, "FOUR_ROWS_ONLY")
    checks = [validate_row(row) for row in rows]
    differences = {}
    for i, z in enumerate((20.0, 15.9)):
        a, b = rows[i]["saved_endpoint"], rows[i + 2]["saved_endpoint"]
        for key in ("xe_per_H", "Tm_K", "nH_m3", "nHe_m3", "ne_m3", "H_s1"):
            diff = abs(a[key] - b[key]) / abs(b[key])
            require(diff <= 1e-4, "REFINEMENT_" + key)
            differences[f"z{z}_{key}"] = diff
    return {"intake": "PASS_SCOPED", "provider": "HOLD_RAW_TEMPERATURE_DOMAIN",
            "low_temperature_physical": "HOLD", "Bianchi_adoption": "HOLD",
            "row_count": 4, "Decimal80_checks": checks,
            "maximum_Decimal80_relative_error": max(max(e.values()) for e in checks),
            "bound_64epsilon": float(BOUND), "refinement": differences,
            "maximum_refinement_relative_difference": max(differences.values()),
            "refinement_bound": 1e-4, "science_history_runs": 0, "intake_campaigns": 1}

def run_command(command, stem, limit, stdin=None):
    start = time.monotonic()
    result = subprocess.run(command, input=stdin, text=True, capture_output=True, timeout=limit, cwd=ROOT)
    evidence = HERE / "evidence"
    (evidence / (stem + ".stdout")).write_text(result.stdout)
    (evidence / (stem + ".stderr")).write_text(result.stderr)
    receipt = {"command": command, "cwd": str(ROOT), "exit": result.returncode,
               "wall_s": time.monotonic() - start, "wall_limit_s": limit}
    (evidence / (stem + ".receipt.json")).write_text(json.dumps(receipt, indent=2) + "\n")
    require(result.returncode == 0, stem + "_EXIT")
    return result.stdout

def main():
    evidence = HERE / "evidence"
    repair = sys.argv[1:] == ["--repair-closeout"]
    require(not sys.argv[1:] or repair, "UNKNOWN_ARGUMENT")
    if repair:
        require(evidence.exists(), "FIRST_BUILD_EVIDENCE_REQUIRED")
        verify_bytes((evidence / "build.stderr").read_bytes(), "a1678fada617734b43b7e22eb93e4c1093ae0a5103996609701baacc2038cb2d")
        require(not (evidence / "build_repaired.receipt.json").exists(), "REPAIR_ALREADY_RUN")
        require(not (evidence / "campaign.receipt.json").exists(), "CAMPAIGN_ALREADY_RUN")
        require((HERE / "REPAIR_AUTHORIZATION.json").exists(), "ASTRA_REPAIR_AUTHORIZATION_REQUIRED")
    else:
        require(not evidence.exists(), "CAMPAIGN_ALREADY_EXISTS")
    rows = load_rows()
    if not repair:
        evidence.mkdir()
    manifest = HERE / "native/Cargo.toml"
    command = ["cargo", "build", "--release", "--locked", "--manifest-path", str(manifest)]
    toolchain = subprocess.run(["rustc", "--version", "--verbose"], text=True, capture_output=True, check=True).stdout
    (evidence / ("toolchain_repaired.txt" if repair else "toolchain.txt")).write_text(toolchain)
    run_command(command, "build_repaired" if repair else "build", 300)
    binary = HERE / "native/target/release/rec_rei_cold_intake01"
    binary_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    lines = []
    for row in rows:
        e = row["saved_endpoint"]
        lines.append(" ".join(repr(v) for v in (e["a"], e["H_s1"], e["Tm_K"], e["nH_m3"], e["nHe_m3"], e["xe_per_H"], KB)))
    stdout = run_command([str(binary)], "campaign", 120, "\n".join(lines) + "\n")
    outputs = [json.loads(line) for line in stdout.splitlines()]
    require(len(outputs) == 4, "NATIVE_FOUR_ROWS")
    for row, out in zip(rows, outputs):
        row["consumer"] = out
    (evidence / "RESULTS.json").write_text(json.dumps(rows, indent=2) + "\n")
    result = validate(rows)
    result["input_sha256"] = PINS
    result["source_sha256"] = SOURCE_PINS
    result["binary_sha256"] = binary_sha
    result["builds_started"] = 2 if repair else 1
    result["repair_closeouts"] = 1 if repair else 0
    (evidence / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("Decimal80_checks", "refinement")}, indent=2))

if __name__ == "__main__":
    main()
