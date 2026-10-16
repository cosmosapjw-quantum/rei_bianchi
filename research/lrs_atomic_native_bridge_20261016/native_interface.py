"""V4 comoving-stock to PR150 IgmPhotoInput/igm_point_rhs point mapping.

This evaluates only the shared photo and Case-A RR/DR/cooling terms. Native
CI/CE/freefree/CMB/source terms remain separate owners and are not zeroed by
this adapter in a production integration.
"""
from __future__ import annotations
from math import exp, isfinite
from pathlib import Path
import sys

V4 = Path(__file__).resolve().parents[1] / "lrs_threshold_oracle_20261015"
sys.path.insert(0, str(V4))
from dynamic_chemistry import CHANNELS, TARGET, PRODUCT, Gas
from recomb_thermal import C_CM_PER_S, MB_CM2, NATIVE_BINDING_EV
from verner_angular import load_primary_fits

EV_ERG = 1.602176634e-12


def point_terms(rays, gas: Gas, x: float, n_star_cm3: float, h_s: float,
                temperature_k: float, atomic_rates, fits=None):
    """Return actual cgs native photo inputs and selected point RHS components.

    Gas and ray populations are per initial n_star comoving volume. Proper
    density is n_star exp(-3X); H is proper s^-1 and d/dX=(1/H)d/dt.
    Photon counts per hydrogen for native are N_ray/gas.hydrogen.
    """
    if not all(isfinite(v) and v > 0 for v in
               (n_star_cm3, h_s, temperature_k)) or not isfinite(x):
        raise ValueError("finite positive physical state required")
    fits = fits or load_primary_fits()
    c = tuple(float(v) for v in atomic_rates(temperature_k))
    if len(c) != 8:
        raise ValueError("Case-A provider must return eight coefficients")
    proper_scale = n_star_cm3 * exp(-3*x)
    stocks = gas.as_tuple()
    ne = proper_scale * gas.electrons
    absorber = tuple(proper_scale * stocks[i] for i in TARGET)
    ion = tuple(proper_scale * stocks[i] for i in PRODUCT)
    gamma = []
    heat = []
    for j, name in enumerate(CHANNELS):
        fit = fits[name]
        cross = [fit.sigma_mb(ray.geometry(x)[0]) * MB_CM2 for ray in rays]
        gamma.append(C_CM_PER_S * proper_scale *
                     sum(ray.photons0 * sigma for ray, sigma in zip(rays, cross)))
        heat.append(C_CM_PER_S * proper_scale * EV_ERG *
                    sum(ray.photons0 * sigma *
                        (ray.geometry(x)[0] - NATIVE_BINDING_EV[j])
                        for ray, sigma in zip(rays, cross)))
    rr_coeff = (c[0], c[1], c[2])
    rr = tuple(ne * ion[j] * rr_coeff[j] for j in range(3))
    dr = ne * ion[1] * c[3]
    rr_cool = tuple(ne * ion[j] * c[4+j] for j in range(3))
    dr_cool = ne * ion[1] * c[7]
    photo_events = tuple(a*g for a, g in zip(absorber, gamma))
    photo_heat = sum(a*q for a,q in zip(absorber,heat))
    photo_bind = sum(v*e*EV_ERG for v,e in zip(photo_events,NATIVE_BINDING_EV))
    capture_bind = sum(v*e*EV_ERG for v,e in zip(
        (rr[0],rr[1]+dr,rr[2]),NATIVE_BINDING_EV))
    radiative_kin = sum(rr_cool)+dr_cool
    return {
        "species_order": ("HI", "HII", "HeI", "HeII", "HeIII"),
        "x": x,
        "dt_dX_s": 1.0 / h_s,
        "proper_scale_cm3": proper_scale,
        "nh_cm3": proper_scale * gas.hydrogen,
        "nhe_cm3": proper_scale * gas.helium,
        "ne_cm3": ne,
        "gamma_s": tuple(gamma),
        "heat_erg_per_absorber_s": tuple(heat),
        "photo_events_cm3_s": photo_events,
        "rr_events_cm3_s": rr,
        "dr_HeII_events_cm3_s": dr,
        "rr_cooling_erg_cm3_s": rr_cool,
        "dr_HeII_cooling_erg_cm3_s": dr_cool,
        "photo_input_erg_cm3_s": photo_heat+photo_bind,
        "selected_thermal_micro_erg_cm3_s": photo_heat-radiative_kin,
        "selected_binding_micro_erg_cm3_s": photo_bind-capture_bind,
        "selected_escape_erg_cm3_s": capture_bind+radiative_kin,
        "rr_comoving_per_X": tuple((rr[j]+(dr if j == 1 else 0.0)) /
                                    (proper_scale*h_s) for j in range(3)),
        "cooling_comoving_ev_per_X":
            (sum(rr_cool)+dr_cool)/(proper_scale*h_s*EV_ERG),
    }
