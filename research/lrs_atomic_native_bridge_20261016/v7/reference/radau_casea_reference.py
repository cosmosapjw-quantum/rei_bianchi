#!/usr/bin/env python3
"""Independent source-free Case-A RR/DR plus cooling Radau reference.

This is a deliberately narrow reference for the V7 fixed-step experiment.
It reproduces the selected Grackle 3.4.1 literals in PR150's
``igm_rates.rs`` at owner commit 6ea2b1b4b3875c9163cafc45efe720afded43fc4.
It evolves only radiative recombination, HeII dielectronic recombination,
their radiative cooling, and FLRW adiabatic work.  In particular it contains
no source, photon transport/absorption, collisional ionization/excitation,
free-free cooling, CMB exchange, or recombination-photon retransport.

The state uses native fractions (HII, HeII, HeIII) and native thermal energy
per hydrogen nucleus (erg/H).  Proper densities are n0/a**3 and X=ln(a/a0),
with dt/dX=1/H.  It is therefore a continuous-RHS comparison instrument, not
a claim about the full PR150 source-on solver.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import quad, solve_ivp


HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]
REPOSITORY = HERE.parents[3]
TABLE = STUDY / "donor" / "owner_grackle_rates_129.csv"
NATIVE_RATES = REPOSITORY / "rust" / "rei_microphysics" / "src" / "igm_rates.rs"
OWNER_COMMIT = "6ea2b1b4b3875c9163cafc45efe720afded43fc4"
OWNER_IGM_RATES_SHA256 = "310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf"

KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
TEVK = 11605.0
# Exact ``Driver::new`` flat-FLRW literals (PR150 owner).  These replace the
# older V5 one-step bridge's 0.083 helium ratio and constant 1e-16 s^-1 H.
G_CGS = 6.67430e-8
PROTON_MASS_G = 1.672_621_925_95e-24
H0_S = 67.4 * 1e5 / 3.0856775814913673e24
OMEGA_R = 9.2e-5
OMEGA_M = 0.315
OMEGA_B = 0.0224 / 0.674**2
OMEGA_LAMBDA = 1.0 - OMEGA_M - OMEGA_R
HELIUM_MASS_FRACTION = 0.2454
RHO_CRIT0 = 3.0 * H0_S**2 / (8.0 * math.pi * G_CGS)
NH0_CM3 = (1.0 - HELIUM_MASS_FRACTION) * OMEGA_B * RHO_CRIT0 / PROTON_MASS_G
HE_H = HELIUM_MASS_FRACTION / (4.0 * (1.0 - HELIUM_MASS_FRACTION))
A0 = 1.0 / 21.0
X_END = 1.0e-5
INITIAL_FRACTIONS = (0.075, 0.12, 0.03)
T0_K = 15000.0
THRESHOLD_EV = (13.598434599702, 24.587389011, 54.41776)
T_DOMAIN = (10000.0, 24000.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_casea_rates(t: float) -> np.ndarray:
    """Literal selected branches of PR150 ``igm_rates`` at 10--24 kK.

    Order is RR HII, RR HeII, RR HeIII, DR HeII, then their matching
    cooling coefficients.  This deliberately omits every other native rate.
    """
    # The literal native implementation accepts 1..1e6 K.  This reference
    # admits its solution only on 10--24 kK; the small padding here permits
    # decimal roundoff in the immutable 129-row owner's endpoint text.
    if not math.isfinite(t) or not T_DOMAIN[0] - 1e-8 <= t <= T_DOMAIN[1] + 1e-8:
        raise ValueError(f"temperature outside V7 donor domain: {t!r}")
    te = t / TEVK
    logte = math.log(te)
    rr_hii = math.exp(
        -28.61303380689232 - 0.7241125657826851 * logte
        - 0.02026044731984691 * logte**2 - 0.002380861877349834 * logte**3
        - 0.0003212605213188796 * logte**4 - 0.00001421502914054107 * logte**5
        + 4.989108920299513e-6 * logte**6 + 5.755614137575758e-7 * logte**7
        - 1.856767039775261e-8 * logte**8 - 3.071135243196595e-9 * logte**9
    )
    rr_heii = 3.92e-13 / te**0.6353
    rr_heiii = 3.36e-10 / math.sqrt(t) / (t / 1.0e3)**0.2 / (1.0 + (t / 1.0e6)**0.7)
    dr_heii = 1.54e-9 * (1.0 + 0.3 / math.exp(8.099328789667 / te)) / (
        math.exp(40.49664394833662 / te) * te**1.5
    )
    lam_h = 2.0 * 157807.0 / t
    cool_hii = 1.778e-29 * t * lam_h**1.965 / (1.0 + (lam_h / 0.541)**0.502)**2.697
    lam_heii = 2.0 * 285335.0 / t
    cool_heii = 3.0e-14 * 1.3806504e-16 * t * lam_heii**0.654
    lam_heiii = 2.0 * 631515.0 / t
    cool_heiii = 8.0 * 1.778e-29 * t * lam_heiii**1.965 / (1.0 + (lam_heiii / 0.541)**0.502)**2.697
    cool_dr = 1.24e-13 * t**-1.5 * math.exp(-470000.0 / t) * (1.0 + 0.3 * math.exp(-94000.0 / t))
    out = np.array((rr_hii, rr_heii, rr_heiii, dr_heii, cool_hii, cool_heii, cool_heiii, cool_dr))
    if not np.all(np.isfinite(out)) or np.any(out <= 0.0):
        raise ArithmeticError("nonpositive/nonfinite selected native coefficient")
    return out


def table_parity() -> dict[str, float]:
    with TABLE.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    labels = tuple(rows[0])[1:]
    worst = 0.0
    for row in rows:
        observed = native_casea_rates(float(row["T_K"]))
        expected = np.array([float(row[label]) for label in labels])
        worst = max(worst, float(np.max(np.abs(observed - expected) / expected)))
    return {"points": len(rows), "max_relative_error": worst}


def density(a: float) -> tuple[float, float]:
    nh = NH0_CM3 / a**3
    return nh, HE_H * nh


def hubble(a: float) -> float:
    """Native ``Cosmology::hubble_flrw`` at q_ref=0, in proper s^-1."""
    return H0_S * math.sqrt(OMEGA_M / a**3 + OMEGA_R / a**4 + OMEGA_LAMBDA)


def temperature(y: np.ndarray, a: float) -> float:
    xhii, yheii, zheiii, w = y[:4]
    nh, nhe = density(a)
    ne = nh * xhii + nhe * (yheii + 2.0 * zheiii)
    return w * nh / (1.5 * KB_ERG_K * (nh + nhe + ne))


def binding_per_h(y: np.ndarray) -> float:
    xhii, yheii, zheiii = y[:3]
    chi_h, chi_hei, chi_heii = (q * EV_ERG for q in THRESHOLD_EV)
    return chi_h * xhii + HE_H * (chi_hei * (yheii + zheiii) + chi_heii * zheiii)


def rhs(x: float, y: np.ndarray) -> np.ndarray:
    a = A0 * math.exp(x)
    xhii, yheii, zheiii, w, _escaped, _work = y
    if min(xhii, yheii, zheiii, w) < 0.0 or xhii > 1.0 or yheii + zheiii > 1.0:
        raise ValueError("unphysical reference state")
    t = temperature(y, a)
    rates = native_casea_rates(t)
    rr_hii, rr_heii, rr_heiii, dr_heii, cool_hii, cool_heii, cool_heiii, cool_dr = rates
    nh, nhe = density(a)
    ne = nh * xhii + nhe * (yheii + 2.0 * zheiii)
    h = hubble(a)
    h_recomb = ne * xhii * rr_hii / h
    heii_recomb = ne * yheii * (rr_heii + dr_heii) / h
    heiii_recomb = ne * zheiii * rr_heiii / h
    cooling_per_h_x = ne / h * (
        xhii * cool_hii + HE_H * yheii * (cool_heii + cool_dr) + HE_H * zheiii * cool_heiii
    )
    bind_capture_per_h_x = ne / h * (
        xhii * rr_hii * THRESHOLD_EV[0] * EV_ERG
        + HE_H * yheii * (rr_heii + dr_heii) * THRESHOLD_EV[1] * EV_ERG
        + HE_H * zheiii * rr_heiii * THRESHOLD_EV[2] * EV_ERG
    )
    return np.array((
        -h_recomb,
        -heii_recomb + heiii_recomb,
        -heiii_recomb,
        -2.0 * w - cooling_per_h_x,
        bind_capture_per_h_x + cooling_per_h_x,
        2.0 * w,
    ))


def integrate(rtol: float) -> object:
    return solve_ivp(
        rhs, (0.0, X_END), initial_state(), method="Radau", rtol=rtol,
        atol=np.array((1e-14, 1e-14, 1e-14, 1e-28, 1e-28, 1e-28)),
        max_step=X_END / 32.0,
    )


def initial_state() -> np.ndarray:
    nh_start, nhe_start = density(A0)
    ne_start = nh_start * INITIAL_FRACTIONS[0] + nhe_start * (INITIAL_FRACTIONS[1] + 2.0 * INITIAL_FRACTIONS[2])
    w0 = 1.5 * KB_ERG_K * T0_K * (nh_start + nhe_start + ne_start) / nh_start
    return np.array((*INITIAL_FRACTIONS, w0, 0.0, 0.0), dtype=float)


def run() -> dict[str, object]:
    y0 = initial_state()
    nh_start, nhe_start = density(A0)
    solution = integrate(2.0e-12)
    if not solution.success:
        raise RuntimeError(f"Radau failed: {solution.message}")
    temperatures = [temperature(solution.y[:, i], A0 * math.exp(float(x))) for i, x in enumerate(solution.t)]
    final = solution.y[:, -1]
    a_final = A0 * math.exp(X_END)
    nh_final, nhe_final = density(a_final)
    initial_energy = y0[3] + binding_per_h(y0)
    final_energy = final[3] + binding_per_h(final) + final[4] + final[5]
    nuclei_h_residual = 0.0  # fractions encode HII and its HI complement exactly.
    nuclei_he_residual = 0.0  # HeI=1-HeII-HeIII at every RHS evaluation.
    electron_initial = INITIAL_FRACTIONS[0] + HE_H * (INITIAL_FRACTIONS[1] + 2.0 * INITIAL_FRACTIONS[2])
    electron_final = final[0] + HE_H * (final[1] + 2.0 * final[2])
    tighter = integrate(2.0e-13)
    if not tighter.success:
        raise RuntimeError(f"tight Radau failed: {tighter.message}")
    endpoint_delta = np.abs(tighter.y[:, -1] - final)
    scaled_endpoint_delta = endpoint_delta / np.maximum(np.abs(tighter.y[:, -1]), 1e-30)
    proper_duration_s = quad(lambda xx: 1.0 / hubble(A0 * math.exp(xx)), 0.0, X_END,
                             epsabs=0.1, epsrel=5e-13)[0]
    return {
        "schema": "rei.lrs.v7.radau_casea_source_free.1",
        "scope": "Independent continuous source-free Case-A RR/DR plus radiative-cooling reference; no source, transport, CI, CE, free-free, CMB, or recombination-photon retransport.",
        "native_comparison_status": "FLRW density and dt/dX use the PR150 Driver::new literals, but this calculation omits the native source-on photon/chemistry operator. It is not a direct source-on endpoint-accuracy comparison.",
        "native_owner_commit_declared": OWNER_COMMIT,
        "native_igm_rates_sha256": sha256(NATIVE_RATES),
        "declared_owner_igm_rates_sha256": OWNER_IGM_RATES_SHA256,
        "checkout_igm_rates_matches_declared_owner": sha256(NATIVE_RATES) == OWNER_IGM_RATES_SHA256,
        "owner_table_sha256": sha256(TABLE),
        "direct_literal_to_owner_table": table_parity(),
        "input": {
            "a0": A0, "x_end": X_END, "proper_duration_s_native_FLRW": proper_duration_s,
            "h0_s": H0_S, "H_start_s": hubble(A0), "H_end_s": hubble(a_final),
            "nh0_comoving_cm3": NH0_CM3, "nhe_over_nh": HE_H,
            "nh_start_cm3": nh_start, "nhe_start_cm3": nhe_start,
            "fractions_HII_HeII_HeIII": list(INITIAL_FRACTIONS), "T0_K": T0_K,
            "temperature_domain_K": list(T_DOMAIN),
        },
        "radau": {"rtol": 2e-12, "atol": [1e-14, 1e-14, 1e-14, 1e-28, 1e-28, 1e-28], "nfev": solution.nfev, "njev": solution.njev, "nlu": solution.nlu, "steps": len(solution.t) - 1},
        "radau_tolerance_refinement": {
            "tight_rtol": 2e-13, "tight_nfev": tighter.nfev,
            "endpoint_absolute_delta": endpoint_delta.tolist(),
            "endpoint_max_relative_delta": float(np.max(scaled_endpoint_delta)),
            "interpretation": "Numerical-reference sensitivity only; compare this value with a separately measured native midpoint-minus-Radau endpoint difference before assigning that difference to the native method.",
        },
        "final": {
            "a": a_final, "nh_cm3": nh_final, "nhe_cm3": nhe_final,
            "fractions_HII_HeII_HeIII": final[:3].tolist(), "Tgas_K": temperature(final, a_final),
            "w_erg_per_h": float(final[3]), "escaped_radiation_erg_per_h": float(final[4]),
            "adiabatic_work_erg_per_h": float(final[5]), "electron_per_h": float(electron_final),
        },
        "diagnostics": {
            "temperature_min_K": min(temperatures), "temperature_max_K": max(temperatures),
            "minimum_fraction_or_w": float(np.min(solution.y[:4])),
            "hydrogen_nuclei_residual": nuclei_h_residual, "helium_nuclei_residual": nuclei_he_residual,
            "electron_change_per_h": float(electron_final - electron_initial),
            "energy_residual_erg_per_h": float(initial_energy - final_energy),
            "energy_relative_residual": abs(float(initial_energy - final_energy)) / max(abs(initial_energy), 1e-300),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "radau_casea_reference.json")
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "Tgas_K": result["final"]["Tgas_K"], "energy_relative_residual": result["diagnostics"]["energy_relative_residual"], "nfev": result["radau"]["nfev"]}, sort_keys=True))


if __name__ == "__main__":
    main()
