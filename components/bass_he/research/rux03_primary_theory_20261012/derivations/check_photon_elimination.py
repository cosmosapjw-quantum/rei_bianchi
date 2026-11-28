#!/usr/bin/env python3
"""Exact algebra for PHOTON_ELIMINATION.md; no physical model execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

import sympy as s


started = time.perf_counter()
checks = []


def zero(name, expression):
    reduced = s.cancel(s.together(expression))
    passed = reduced == 0
    checks.append({"id": name, "pass": bool(passed), "exact_remainder": str(reduced)})
    if not passed:
        raise AssertionError(name + ": " + str(reduced))


h, old, source = s.symbols("h N_old S_ref", positive=True)
l = s.symbols("lambda0:3", nonnegative=True)
total = sum(l)
denom = 1 + h * total
available = old + h * source
photons = available / denom
allocation = s.Matrix([h * channel * photons for channel in l])

zero("photon_BE_reverse_substitution", photons - old - h * (source - total * photons))
zero("reference_photon_budget", photons + sum(allocation) - available)
zero("photon_incoming_derivative", s.diff(photons, old) - 1 / denom)
zero("photon_source_derivative", s.diff(photons, source) - h / denom)
zero("photon_step_derivative", s.diff(photons, h) - (source - total * old) / denom**2)

jacobian = allocation.jacobian(s.Matrix(l))
for a in range(3):
    for b in range(3):
        expected = h * available / denom * (int(a == b) - h * l[a] / denom)
        zero(f"allocation_jacobian_{a}_{b}", jacobian[a, b] - expected)
for b in range(3):
    zero(f"allocation_column_sum_{b}", sum(jacobian[a, b] for a in range(3)) - h * available / denom**2)
zero("allocation_jacobian_determinant", jacobian.det() - (h * available)**3 / denom**4)

for a in range(3):
    reconstructed = allocation[a] / (h * (available - sum(allocation)))
    zero(f"allocation_inverse_{a}", reconstructed - l[a])
    zero(f"allocation_incoming_derivative_{a}", s.diff(allocation[a], old) - h * l[a] / denom)
    zero(f"allocation_source_derivative_{a}", s.diff(allocation[a], source) - h**2 * l[a] / denom)

x = s.symbols("x0:3", real=True)
nh, nhe, light = s.symbols("nH nHe c", positive=True)
sigma = s.symbols("sigma0:3", nonnegative=True)
lower = s.Matrix([nh * (1 - x[0]), nhe * (1 - x[1] - x[2]), nhe * x[1]])
channels_x = s.Matrix([light * sigma[a] * lower[a] for a in range(3)])
total_x = sum(channels_x)
denom_x = 1 + h * total_x
photons_x = available / denom_x
alloc_x = s.Matrix([h * channels_x[a] * photons_x for a in range(3)])
for j in range(3):
    lj = s.diff(total_x, x[j])
    zero(f"photon_fraction_derivative_{j}", s.diff(photons_x, x[j]) + h * available * lj / denom_x**2)
    zero(f"differentiated_budget_{j}", s.diff(photons_x + sum(alloc_x), x[j]))
    for k in range(3):
        lk = s.diff(total_x, x[k])
        zero(f"photon_fraction_hessian_{j}_{k}",
             s.diff(photons_x, x[j], x[k]) - 2 * h**2 * available * lj * lk / denom_x**3)
        for a in range(3):
            aj, ak = s.diff(channels_x[a], x[j]), s.diff(channels_x[a], x[k])
            expected = (-h**2 * available * (aj * lk + ak * lj) / denom_x**2
                        + 2 * h**3 * available * channels_x[a] * lj * lk / denom_x**3)
            zero(f"allocation_fraction_hessian_{a}_{j}_{k}", s.diff(alloc_x[a], x[j], x[k]) - expected)

volume_old, volume_new, proper_old, proper_source = s.symbols("V_old V_new n_old s_proper", positive=True)
proper_new = photons.subs({old: volume_old * proper_old, source: volume_new * proper_source}) / volume_new
zero("proper_reference_conversion",
     proper_new - ((volume_old / volume_new) * proper_old + h * proper_source) / denom)

old_h, ion_h, rr_h = s.symbols("old_H ion_H rr_H", nonnegative=True)
new_h = (old_h + h * ion_h) / (1 + h * (ion_h + rr_h))
zero("conditional_H_balance", new_h - old_h - h * (ion_h * (1 - new_h) - rr_h * new_h))

old_a, old_b, A, B, C, D = s.symbols("old_HeII old_HeIII A B C D", nonnegative=True)
old_z = 1 - old_a - old_b
new_a = (old_a + old_z * A / (1 + A) + old_b * D / (1 + D)) / (1 + B / (1 + A) + C / (1 + D))
new_b = (old_b + C * new_a) / (1 + D)
new_z = (old_z + B * new_a) / (1 + A)
zero("conditional_HeI_balance", new_z - old_z + A * new_z - B * new_a)
zero("conditional_HeII_balance", new_a - old_a - A * new_z + (B + C) * new_a - D * new_b)
zero("conditional_HeIII_balance", new_b - old_b - C * new_a + D * new_b)
zero("conditional_He_normalization", new_z + new_a + new_b - 1)

e_old, e_new, n_old, n_new, theta = s.symbols("E_old E_new Nminus Nplus theta", real=True)
product_change = e_new * n_new - e_old * n_old
zero("endpoint_energy_product_rule", product_change - e_new * (n_new - n_old) - (e_new - e_old) * n_old)
e_theta = (1 - theta) * e_old + theta * e_new
n_partner = theta * n_old + (1 - theta) * n_new
zero("general_energy_product_rule", product_change - e_theta * (n_new - n_old) - n_partner * (e_new - e_old))

gas_delta, binding_delta, escaped, gas_work, source_energy, absorbed_energy = s.symbols(
    "gas_delta binding_delta escaped gas_work source_energy absorbed_energy", real=True)
photon_micro_delta = source_energy - absorbed_energy
gas_and_binding_delta = absorbed_energy - escaped - gas_work
photon_history_delta = photon_micro_delta + (e_new - e_old) * n_old
geometry_work = -(e_new - e_old) * n_old
zero("shared_event_history_energy_ledger",
     gas_and_binding_delta + photon_history_delta + escaped + gas_work + geometry_work - source_energy)

nu = s.symbols("nu", real=True)
endpoint_work = h * nu * e_new * photons_x
correction = -(e_new - e_old) * old - endpoint_work
for j in range(3):
    zero(f"geometry_correction_derivative_{j}", s.diff(endpoint_work + correction, x[j]))

script = Path(__file__).resolve()
derivation = script.with_name("PHOTON_ELIMINATION.md")
receipt = {
    "task": "PRIMARY_THEORY_03_PHOTON_ELIMINATION",
    "status": "PASS_EXACT_ALGEBRA",
    "method": "SymPy exact rational simplification and symbolic differentiation",
    "sympy_version": s.__version__,
    "command": "python " + str(script),
    "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
    "derivation_sha256_at_execution": hashlib.sha256(derivation.read_bytes()).hexdigest(),
    "checks": checks,
    "check_count": len(checks),
    "elapsed_seconds": time.perf_counter() - started,
    "scope": "Algebraic verification of explicit formulae in PHOTON_ELIMINATION.md; no ODE, native binary, model calibration or history campaign.",
    "exit_code": 0,
}
out = script.with_name("SYMBOLIC_CHECK.json")
out.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "checks": len(checks),
                  "elapsed_seconds": receipt["elapsed_seconds"], "output": str(out)}, indent=2))
