"""Selected PW19 HeII photo source at the REC119 native 21-state boundary.

All rates are per proper second and per baryon. The four extra coordinates are
nonthermal electron count, its kinetic energy, signed external photon energy,
and log(T/1 K); the latter has zero pre-assimilation photo source.
"""
from __future__ import annotations

import math
import numpy as np

HEII = (8, 11)
HEIII = (9, 12)
ROUTE = "PW19_z2.479_HeII_exclusive"
ISOTOPE_POLICY = "ElementalElectronicEquality_He3_He4_conditional"
OWNER = "REC119_photo_HeII_one_owner"
EV_J = 1.602176634e-19
CHI_J = 54.42 * EV_J


def _finite(value, name):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _vector(value, size, name):
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    out = np.asarray(value, dtype=float)
    if out.shape != (size,) or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite length-{size} vector")
    return out


def _owner(network):
    if (network.source_z != 2.479 or network.source_route != ROUTE or
            network.isotope_policy != ISOTOPE_POLICY or
            tuple(network.photo_owners) != (OWNER,) or
            tuple(network.names[i] for i in (*HEII, *HEIII)) !=
            ("He3II", "He4II", "He3III", "He4III") or
            any(network.transition_energy_eV[i] != 54.42 for i in HEII)):
        raise ValueError("selected native source, isotope policy, or owner mismatch")


def reference_state(network, x_per_reference, dx_per_reference=None):
    """Map a fixed comoving reference state and tangent to baryon normalization."""
    x = _vector(x_per_reference, 21, "reference state")
    dx = np.zeros(21) if dx_per_reference is None else _vector(dx_per_reference, 21, "reference tangent")
    beta = float(network.A @ x)
    dbeta = float(network.A @ dx)
    if not math.isfinite(beta) or beta <= 0:
        raise ValueError("positive reference baryon count required")
    Y = x / beta
    v = (dx - Y * dbeta) / beta
    return {"Y": Y, "v": v, "beta": beta, "dbeta": dbeta}


def augmented_photo_source(network, Y, T_K, nb_m3, lambda_source,
                           zeta_per_baryon=0.0, H_s_inverse=None, v=None,
                           dlambda=0.0, dnb=0.0, dzeta=0.0, dH=0.0,
                           beta_baryons_per_reference=None, dbeta=0.0,
                           full_rr_dr_thermal=False):
    """Native photo action, 25-state source/JVP and physical/reference maps.

    The 25 coordinates are Y[21], zeta, w_nt, w_ext, ell. No RR/DR, stopping,
    photon evolution, or geometric response is inserted by this operator.
    """
    if full_rr_dr_thermal:
        raise ValueError("full RR/DR thermal bath is outside selected photo source")
    _owner(network)
    y = _vector(Y, 21, "Y")
    direction = np.zeros(21) if v is None else _vector(v, 21, "v")
    T = _finite(T_K, "T_K")
    nb = _finite(nb_m3, "nb_m3")
    lam = _finite(lambda_source, "lambda_source")
    zeta = _finite(zeta_per_baryon, "zeta")
    dlambda = _finite(dlambda, "dlambda")
    dnb = _finite(dnb, "dnb")
    dzeta = _finite(dzeta, "dzeta")
    dH = _finite(dH, "dH")
    dbeta = _finite(dbeta, "dbeta")
    if T <= 0 or nb <= 0 or lam < 0 or np.any(y < 0):
        raise ValueError("physical T, nb, lambda, Y domain required")
    baryons = float(network.A @ y)
    if not math.isclose(baryons, 1.0, rel_tol=2e-14, abs_tol=2e-14):
        raise ValueError("A dot Y must be one")
    charge = float(network.q @ y)
    thermal_count = float(np.dot(1 + network.q, y)) - zeta
    if zeta < 0 or zeta > charge or thermal_count <= 0:
        raise ValueError("nonthermal electron subset or thermal count invalid")
    if H_s_inverse is not None:
        H = _finite(H_s_inverse, "H")
        if H <= 0:
            raise ValueError("positive H required")
    else:
        if dH != 0:
            raise ValueError("dH requires H")
        H = None
    beta = None if beta_baryons_per_reference is None else _finite(beta_baryons_per_reference, "beta")
    if beta is not None and beta <= 0:
        raise ValueError("positive beta required")
    if beta is None and dbeta != 0:
        raise ValueError("dbeta requires beta")

    native = network.evaluate(y, T, lam, nb)
    P = _vector(native["photo_rhs"], 21, "native photo_rhs")
    gy = network._Gphoto @ y
    dP = lam * (network._Gphoto @ direction) + dlambda * gy
    event = float(network.q @ P)
    devent = float(network.q @ dP)
    S = math.fsum((float(y[8]), float(y[11])))
    dS = math.fsum((float(direction[8]), float(direction[11])))
    factor = lam * S
    dfactor = lam * dS + dlambda * S
    kinetic = network.selected_K_J_s * factor
    absorbed = network.selected_A_J_s * factor
    dkinetic = network.selected_K_J_s * dfactor
    dabsorbed = network.selected_A_J_s * dfactor
    source = np.concatenate((P, [event, kinetic, -absorbed, 0.0]))
    tangent = np.concatenate((dP, [devent, dkinetic, -dabsorbed, 0.0]))
    bands = []
    for part in network.admitted_moments["partition_moments"]:
        g = part["Gamma_s"]
        k = part["K_eV_s"] * EV_J
        a = part["A_eV_s"] * EV_J
        bands.append({"band_eV": list(part["band_eV"]),
                      "events_per_baryon_s": factor*g,
                      "primary_J_per_baryon_s": factor*k,
                      "absorbed_J_per_baryon_s": factor*a,
                      "tangent_events_per_baryon_s": dfactor*g,
                      "tangent_primary_J_per_baryon_s": dfactor*k,
                      "tangent_absorbed_J_per_baryon_s": dfactor*a})
    binding = float(network.ionization_energy_J @ P)
    dbinding = float(network.ionization_energy_J @ dP)
    dthermal_count = float(np.dot(1 + network.q, P)) - event
    ddthermal_count = float(np.dot(1 + network.q, dP)) - devent
    volume = nb * source
    dvolume = dnb * source + nb * tangent
    reference = None if beta is None else beta * source
    dreference = None if beta is None else dbeta * source + beta * tangent
    eta = None if H is None else source / H
    deta = None if H is None else tangent / H - source * (dH / H**2)
    bad_count = float(np.dot(1 + network.q, y))
    bad_allthermal_logT_s = -event / bad_count
    return {
        "source": source, "jvp": tangent,
        "physical_density_source": volume, "physical_density_jvp": dvolume,
        "reference_source": reference, "reference_jvp": dreference,
        "eta_source": eta, "eta_jvp": deta,
        "native_photo_rhs": P, "native_on_components": {k: native[k] for k in ("rr_rhs", "dr_rhs", "decay_rhs")},
        "band_ledger": bands,
        "thermal_count": thermal_count, "thermal_electrons": charge-zeta,
        "total_charge_electrons": charge, "dthermal_count_source": dthermal_count,
        "dthermal_count_jvp": ddthermal_count,
        "binding_J_per_baryon_s": binding, "binding_jvp": dbinding,
        "energy_residual_J_per_baryon_s": binding+kinetic-absorbed,
        "energy_jvp_residual": dbinding+dkinetic-dabsorbed,
        "bad_allthermal_logT_s": bad_allthermal_logT_s,
        "bad_allthermal_dcount_s": event,
        "pressure_source_interval_W_m3": (volume[22]/3, 2*volume[22]/3),
        "isotropic_pressure_STF_source": 0.0,
        "owner": OWNER, "route": ROUTE, "isotope_policy": ISOTOPE_POLICY,
        "uncertainties": {k: None for k in ("provider", "model", "isotope", "continuum_interpolation")},
        "source_only": True,
    }
