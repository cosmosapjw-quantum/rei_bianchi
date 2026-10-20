#!/usr/bin/env python3
"""Independent read-only checks; only the audit receipt is written.

Does not import the native/atomic author's generators or validators. This check
compares selected raw coefficient columns with generated Rust and reconstructs
the limited native RHS substitution after reading both actual source files.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOMIC = ROOT / "brperf01/atomic_theory"
NATIVE = ROOT / "brperf01/native_rates"
PARENT = ROOT / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/parent/crate"


def normalized(text):
    return re.sub(r"\s+", "", text)


def function(text, marker):
    start = text.index(marker)
    begin = text.index("{", start)
    depth = 1
    index = begin + 1
    while depth:
        depth += (text[index] == "{") - (text[index] == "}")
        index += 1
    return text[start:index], text[begin:index]


def main():
    original = (PARENT / "src/midpoint_gas.rs").read_text()
    native = (NATIVE / "src/lib.rs").read_text()
    before = original[original.index("fn atomic_values"):original.index("pub fn scale_budget")]
    after = native[native.index("fn atomic_values"):native.index("/// Reuse one source-bound bundle")]
    replacements = [
        ("pub fn rhs(s: &FullState, c: &NetworkConfig) -> Result<GasRhs, NetworkError> {", "fn rhs_core<F>(s: &FullState, c: &NetworkConfig, evaluator: &mut F) -> Result<GasRhs, NetworkError> where F: FnMut(f64) -> Result<IgmRates, NetworkError>, {"),
        ("let r = igm_rates(t).map_err(|_| NetworkError::TemperatureOutsideSource)?;", "let r = evaluator(t)?;"),
        ("let d = d_atomic_rhs( c.deuterium, &s.gas.nuclei, t, &no_d_photo, DChargeExchange::Disabled, ) .map_err(|_| NetworkError::InputOutsideDomain)?;", "let d = collision::collision_rhs(c.deuterium, &s.gas.nuclei, t, &no_d_photo, &r) .map_err(|_| NetworkError::InputOutsideDomain)?;"),
        ("d_net = d.species_m3_s[S::DIonized as usize];", "d_net = d.d_net;"),
    ]
    transformed = normalized(before)
    for old, new in replacements:
        assert transformed.count(normalized(old)) == 1
        transformed = transformed.replace(normalized(old), normalized(new))
    assert transformed == normalized(after)
    _, old_step = function(original, "pub fn step(")
    _, new_step = function(native, "pub fn step_with_evaluator")
    new_step = new_step.replace("parent::midpoint_gas::apply", "apply")
    new_step = new_step.replace("rhs_with_evaluator(s, c, evaluator)", "rhs(s, c)")
    new_step = new_step.replace("rhs_with_evaluator(&mid, c, evaluator)", "rhs(&mid, c)")
    assert normalized(old_step) == normalized(new_step)
    _, old_strang = function(original, "pub fn step_strang(")
    _, new_strang = function(native, "pub fn step_strang_with_evaluator")
    new_strang = new_strang.replace("parent::midpoint_gas::", "")
    new_strang = new_strang.replace("step_with_evaluator(&a.state, &nc, h, evaluator)", "step(&a.state, &nc, h)")
    assert normalized(old_strang) == normalized(new_strang).replace("a.budget,b.budget),d.budget,)", "a.budget,b.budget),d.budget)")
    original_d = (PARENT / "owner_src/deuterium_atomic.rs").read_text()
    collision = (NATIVE / "src/collision.rs").read_text()
    for name in ["nonnegative", "arithmetic", "product", "ev_j"]:
        a, _ = function(original_d, "fn " + name + "(")
        b, _ = function(collision, "fn " + name + "(")
        assert normalized(a) == normalized(b)
    energy_a = original_d[original_d.index("    let chi = provider.chi_d_ev * ev_j();"):original_d.index("    let mut species_m3_s = [0.0; 13];")]
    energy_b = collision[collision.index("    let chi = provider.chi_d_ev() * ev_j();"):collision.index("    let particles = arithmetic(")]
    energy_b = energy_b.replace("provider.chi_d_ev()", "provider.chi_d_ev")
    for field in ["heat_j_per_absorber_s", "energy_j_per_absorber_s"]:
        energy_b = energy_b.replace("photo." + field + "()", "photo." + field)
    assert normalized(energy_a) == normalized(energy_b)
    generated = (ATOMIC / "catalog/src/generated.rs").read_text()
    blocks = re.findall(r"IonFit \{\s*ion: Ion \{\s*atomic_number: (\d+),\s*electrons: (\d+),\s*\},\s*photo: PhotoFit \{\s*coeff: \[([^\]]+)\],\s*\},\s*ci: CiFit \{\s*coeff: \[([^\]]+)\],\s*\},\s*rr_toward: (None|Some\(RrFit \{\s*coeff: \[[^\]]+\],\s*\}\)),\s*\}", generated, re.S)
    assert len(blocks) == 24
    pi = {}
    for line in (ATOMIC / "data/photo.dat").read_text().splitlines():
        values = line.split()
        pi[int(values[0]), int(values[1])] = list(map(float, values[2:]))
    ci = {}
    for line in (ATOMIC / "data/cfit.dat").read_text().splitlines():
        ci[int(line[6:8]), int(line[9:11])] = [float(line[a:b]) for a, b in [(12, 19), (20, 21), (22, 31), (32, 38), (39, 43), (44, 48), (49, 53)]]
    rr = {}
    for line in (ATOMIC / "data/rec_table1.dat").read_text().splitlines():
        key = int(line[9:11]), int(line[12:14])
        if key[0] in [3, 6, 7, 8]:
            rr[key] = [float(line[a:b]) for a, b in [(16, 25), (27, 33), (35, 44), (46, 55)]]
    def numbers(value):
        return [float(x.strip()) for x in value.split(",") if x.strip()]
    keys = set()
    max_u = 0.0
    for zs, ns, pis, cis, rrs in blocks:
        key = int(zs), int(ns)
        assert key not in keys
        keys.add(key)
        assert numbers(pis) == pi[key]
        assert numbers(cis) == ci[key]
        if key in rr:
            assert numbers(re.search(r"coeff: \[([^\]]+)\]", rrs, re.S).group(1)) == rr[key]
        else:
            assert rrs == "None"
        max_u = max(max_u, ci[key][0] / ci[key][5])
    assert keys == {(z, n) for z in [3, 6, 7, 8] for n in range(1, z + 1)}
    assert max_u < 80.0
    source_hashes = []
    for record in json.loads((ATOMIC / "data/PROVENANCE.json").read_text()):
        path = ATOMIC / "data" / record["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == record["sha256"] and path.stat().st_size == record["bytes"]
        source_hashes.append({"path": record["path"], "sha256": actual})
    result = {
        "status": "PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW",
        "reviewer": "/root/opt_photon", "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "native_rhs_only_four_allowed_substitutions": True,
        "native_midpoint_body_original_after_evaluator_substitution": True,
        "native_strang_body_original_after_evaluator_substitution": True,
        "D_arithmetic_helpers_original": True,
        "D_all_six_energy_rows_order_and_net_original": True,
        "atomic_selected_ions_raw_to_Rust_matched": len(keys), "atomic_selected_rr_raw_to_Rust_matched": len(rr),
        "atomic_max_U_on_source_domain": max_u, "source_records_hash_verified": source_hashes,
        "independence": "New read-only comparison script, original owner and raw source columns, no imports of author generators or validators; no rerun of new crate test suites",
        "limitations": ["Whole f64 semantics outside tested/admitted source domains are not proven by text comparison", "Source lookup establishes published domain and attribution request; explicit redistribution grant remains unobserved"],
    }
    (HERE / "INDEPENDENT_SOURCE_CHECKS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
