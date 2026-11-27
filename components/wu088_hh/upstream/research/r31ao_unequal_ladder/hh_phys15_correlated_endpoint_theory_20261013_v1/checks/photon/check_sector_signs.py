#!/usr/bin/env python3
"""Verify exact captured-leaf inequalities used by PHYS15 sector theorems."""
import argparse
import hashlib
import json
from pathlib import Path
from fractions import Fraction as Q
import struct
import time


def qbits(s):
    return Q(struct.unpack(">d", bytes.fromhex(s))[0])


def exact(q):
    return {"numerator": str(q.numerator), "denominator": str(q.denominator)}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(project, output):
    started = time.perf_counter()
    paths = [
        project/"inputs/ncp07/results/first_half/SOURCE_BOX.json",
        project/"inputs/ncp07/results/full/SOURCE_BOX.json",
        project/"inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json",
    ]
    half, full, native = [json.loads(p.read_text()) for p in paths]
    h = qbits(half["dt_bits"])
    c, nH = qbits(native["c_bits"]), qbits(full["nH_bits"])
    sigma = [qbits(r[0]) for r in full["sigma_bits"]]
    heat = [qbits(r[0]) for r in full["heat_bits"]]
    energy = [qbits(r) for r in full["energy_bits"]]
    chi = qbits(native["CHI_bits"][0])
    eta_max = h*c*nH
    max_product = eta_max**2*sigma[23]*sigma[24]
    assert 0 < max_product < 1
    assert all(sigma[j] > sigma[j+1] > 0 for j in range(16,32))
    assert all(sigma[j] == 0 for j in range(16))
    assert sigma[23] > sigma[24] > 0
    assert 0 < heat[23]*sigma[23] < heat[24]*sigma[24]
    assert all(chi <= energy[j] < 2*chi for j in range(16,33))
    assert all(heat[j] == energy[j]-chi for j in range(16,33))

    # After multiplying by the common positive denominator, the thermal
    # difference is eta*(c0+c1*eta+c2*eta^2), all coefficients strictly negative.
    s0,s1,e0,e1 = sigma[23],sigma[24],heat[23],heat[24]
    heat_coeffs = [e0*s0-e1*s1,
                   2*s0*s1*(e0-e1),
                   s0*s1*(e0*s1-e1*s0)]
    assert all(v < 0 for v in heat_coeffs)
    # The number difference is eta*(s0-s1)*(1-eta^2*s0*s1).
    number_coeffs = [s0-s1, Q(0), -s0*s1*(s0-s1)]
    assert number_coeffs[0] > 0
    assert number_coeffs[0]+number_coeffs[2]*eta_max**2 > 0
    result = {
        "schema": "WU088_HH_PHYS15_SECTOR_SIGN_LEAVES_V1",
        "status": "completed",
        "result": "pass_scoped",
        "scope": "Exact source-leaf inequalities and polynomial coefficients; physical x2 in [0,1]; original birth node 24 and original redshift branch",
        "scientific_history_runs": 0,
        "candidate_imports": 0,
        "formula_ref": "PHOTON_DEFECT_THEOREM_KO.md equations (20)-(29), (38)",
        "active_sigma_strictly_decreasing": True,
        "inactive_sigma_exact_zero": True,
        "commutator_absorption_sector": {
            "pointwise_sign": "componentwise nonnegative",
            "conditions": ["Q1>=0", "0<=x2<=1", "original active sigma order",
                           "same captured source density in compared A entries"],
            "proof": "Rij>=0, Ai=A(kappa_i), sigma_i>sigma_j on active downward edges; inactive/guard B_i=0"
        },
        "birth_redshift_sector": {
            "eta_max_exact": exact(eta_max),
            "max_tau23_tau24_exact": exact(max_product),
            "max_tau23_tau24_display": float(max_product),
            "strict_less_than_one": True,
            "heat_sigma_23_lt_24": True,
            "number_numerator_after_factoring_eta_coefficients": [exact(x) for x in number_coeffs],
            "thermal_numerator_after_factoring_eta_coefficients": [exact(x) for x in heat_coeffs],
            "thermal_coefficients_all_strictly_negative": True,
            "ionization_absorption_sign": "positive when b>0 and x2<1",
            "thermal_deposition_sign": "negative when b>0 and x2<1",
            "direct_temperature_covector_sign": "negative when additionally w>0 and particle_count>0",
            "zero_boundaries": ["b=0", "x2=1"]
        },
        "heat_capture": {
            "active_nodes": list(range(16,33)),
            "active_heat_equals_exact_energy_minus_CHI": True,
            "Sterbenz_factor_two_conditions": True,
            "range_and_equality_checked_from_captured_bits": True
        },
        "inputs": [{"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in paths],
        "script_sha256": sha(Path(__file__)),
        "elapsed_seconds": time.perf_counter()-started
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"status": "completed", "result": "pass_scoped",
                      "physical_range": "0<=x2<=1",
                      "max_tau23_tau24": float(max_product),
                      "scientific_history_runs": 0,
                      "elapsed_seconds": result["elapsed_seconds"],
                      "output_sha256": sha(output)}))


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a=p.parse_args()
    main(a.project,a.output)

