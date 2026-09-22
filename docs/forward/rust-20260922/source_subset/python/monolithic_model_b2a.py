"""Durable monolithic P0.5-B2A residual.

This module is a post-interruption reconstruction. It does not inherit any
transcript-only P0.5-B2 formula or numerical result.

Unknown vector (unconstrained coordinates)
------------------------------------------
Z = [log N_gamma,1..4,
     logit x_HII,
     helium logits for HeII and HeIII with HeI baseline logit 0,
     log u_th,
     log Gamma_HI]

Physical vector
---------------
Y = [N_gamma,1..4, x_HII, x_HeII, x_HeIII, u_th, Gamma_HI].

The transform guarantees positivity, 0 < x_HII < 1, and
x_HeI+x_HeII+x_HeIII=1 algebraically.

The 9 residuals are:
  4 photon-group backward-Euler residuals,
  1 H chemistry residual,
  2 He chemistry residuals,
  1 thermal-internal-energy residual,
  1 Gamma_HI closure residual.
"""
from __future__ import annotations

from typing import Mapping

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

Array = jax.Array

# CGS constants retained explicitly.
C_LIGHT = 2.99792458e10
MPC_CM = 3.085677581491367e24
KB_ERG = 1.380649e-16
EV_ERG = 1.602176634e-12


def sigmoid(x: Array) -> Array:
    return jax.nn.sigmoid(x)


def transform_z_to_y(z: Array) -> Mapping[str, Array]:
    """Map unconstrained coordinates to the physical state."""
    n_gamma = jnp.exp(z[:4])
    x_hii = sigmoid(z[4])
    he_logits = jnp.array([0.0, z[5], z[6]], dtype=z.dtype)
    he = jax.nn.softmax(he_logits)
    u_th = jnp.exp(z[7])
    gamma_hi = jnp.exp(z[8])
    return {
        "N": n_gamma,
        "xHII": x_hii,
        "xHeI": he[0],
        "xHeII": he[1],
        "xHeIII": he[2],
        "u": u_th,
        "GammaHI": gamma_hi,
    }


def transform_y_to_z(
    n_gamma: Array,
    x_hii: Array,
    x_heii: Array,
    x_heiii: Array,
    u_th: Array,
    gamma_hi: Array,
) -> Array:
    """Inverse transform for strictly physical states."""
    x_hei = 1.0 - x_heii - x_heiii
    return jnp.concatenate(
        [
            jnp.log(n_gamma),
            jnp.array([jnp.log(x_hii / (1.0 - x_hii))]),
            jnp.array([jnp.log(x_heii / x_hei), jnp.log(x_heiii / x_hei)]),
            jnp.array([jnp.log(u_th), jnp.log(gamma_hi)]),
        ]
    )


def polyval(coeff: Array, x: Array) -> Array:
    out = jnp.asarray(0.0, dtype=x.dtype)
    for c in coeff:
        out = out * x + c
    return out


def pchip_eval(knots: Array, coeffs: Array, x: Array) -> Array:
    """Evaluate SciPy-PCHIP coefficients in JAX.

    coeffs has shape (4, n_intervals) and represents
    c0 dx^3 + c1 dx^2 + c2 dx + c3.
    """
    idx = jnp.clip(jnp.searchsorted(knots, x, side="right") - 1, 0, knots.shape[0] - 2)
    dx = x - knots[idx]
    c = coeffs[:, idx]
    return ((c[0] * dx + c[1]) * dx + c[2]) * dx + c[3]


def opacity_cMpc_inv(state: Mapping[str, Array], p: Mapping[str, Array]) -> Array:
    """Four-group opacity, preserving the H-I emulator/atomic firewall.

    G1 and G2a use a smooth polynomial fit to P0.4's PUBLIC_REPO_EXACT
    H-I opacity as a function of Gamma_HI. Explicit He I is added only in G2a.
    G2b and G3 are explicit atomic lanes.
    """
    gamma12 = state["GammaHI"] / 1.0e-12
    x = jnp.log(gamma12)
    log_kappa_low = jnp.array(
        [pchip_eval(p["log_kappa_knots"], p["log_kappa_pchip_coeffs"][i], x)
         for i in range(2)]
    )
    kappa_hi_effective = jnp.exp(log_kappa_low)

    n_h = p["nH_phys"]
    n_he = p["nHe_phys"]
    n_hi = n_h * (1.0 - state["xHII"])
    n_hei = n_he * state["xHeI"]
    n_heii = n_he * state["xHeII"]
    cMpc_per_cm = MPC_CM / (1.0 + p["z_cos"])

    k_hi = n_hi * p["sigma_HI"] * cMpc_per_cm
    k_hei = n_hei * p["sigma_HeI"] * cMpc_per_cm
    k_heii = n_heii * p["sigma_HeII"] * cMpc_per_cm

    return jnp.array(
        [
            kappa_hi_effective[0],
            kappa_hi_effective[1] + k_hei[1],
            k_hi[2] + k_hei[2],
            k_hi[3] + k_hei[3] + k_heii[3],
        ]
    )


def photon_rates(state: Mapping[str, Array], emissivity: Array, p: Mapping[str, Array]) -> Array:
    """Four-group comoving photon-number RHS."""
    n = state["N"]
    kappa = opacity_cMpc_inv(state, p)
    absorption = C_LIGHT * (1.0 + p["z_cos"]) / MPC_CM * kappa
    red_out = p["Hubble"] * p["redshift_coeff"]

    rhs = emissivity * p["source_fraction"] - (absorption + red_out) * n
    rhs = rhs.at[:3].add(red_out[1:] * n[1:])
    return rhs


def gamma_species(state: Mapping[str, Array], p: Mapping[str, Array]) -> tuple[Array, Array, Array, Array]:
    prefactor = C_LIGHT * (1.0 + p["z_cos"]) ** 3 / MPC_CM**3
    group_gamma_hi = prefactor * p["sigma_HI"] * state["N"]
    group_gamma_hei = prefactor * p["sigma_HeI"] * state["N"]
    group_gamma_heii = prefactor * p["sigma_HeII"] * state["N"]
    return (
        jnp.sum(group_gamma_hi),
        jnp.sum(group_gamma_hei),
        jnp.sum(group_gamma_heii),
        group_gamma_hi,
    )


def lambda_hi(T: Array) -> Array:
    return 315614.0 / T


def lambda_hei(T: Array) -> Array:
    return 570670.0 / T


def lambda_heii(T: Array) -> Array:
    return 1263030.0 / T


def alpha_a_hii(T: Array) -> Array:
    ll = lambda_hi(T)
    return 1.269e-13 * ll**1.503 / (1.0 + (ll / 0.522) ** 0.470) ** 1.923


def alpha_b_hii(T: Array) -> Array:
    ll = lambda_hi(T)
    return 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def alpha_a_heii(T: Array) -> Array:
    ll = lambda_hei(T)
    base = 3.0e-14 * ll**0.654
    dr = 1.9e-3 * T**-1.5 * jnp.exp(-473638.0 / T) * (1.0 + 0.3 * jnp.exp(-94728.0 / T))
    gate = sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def alpha_b_heii(T: Array) -> Array:
    ll = lambda_hei(T)
    base = 1.26e-14 * ll**0.750
    dr = 1.9e-3 * T**-1.5 * jnp.exp(-473638.0 / T) * (1.0 + 0.3 * jnp.exp(-94728.0 / T))
    gate = sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def alpha_a_heiii(T: Array) -> Array:
    ll = lambda_heii(T)
    return 2.0 * 1.269e-13 * ll**1.503 / (1.0 + (ll / 0.522) ** 0.470) ** 1.923


def alpha_b_heiii(T: Array) -> Array:
    ll = lambda_heii(T)
    return 2.0 * 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def alpha_heiii_n2(T: Array) -> Array:
    return 3.4e-13 * (T / 1.0e4) ** -0.6


def beta_hi(T: Array) -> Array:
    return 5.835e-11 * jnp.sqrt(T) * jnp.exp(-157804.0 / T)


def beta_hei(T: Array) -> Array:
    return 2.71e-11 * jnp.sqrt(T) * jnp.exp(-285331.0 / T)


def beta_heii(T: Array) -> Array:
    return 5.707e-12 * jnp.sqrt(T) * jnp.exp(-631495.0 / T)


def electron_density(state: Mapping[str, Array], p: Mapping[str, Array]) -> Array:
    return p["nH_phys"] * state["xHII"] + p["nHe_phys"] * (
        state["xHeII"] + 2.0 * state["xHeIII"]
    )


def temperature(state: Mapping[str, Array], p: Mapping[str, Array]) -> Array:
    ne = electron_density(state, p)
    npart = p["nH_phys"] + p["nHe_phys"] + ne
    return 2.0 * state["u"] / (3.0 * KB_ERG * npart)


def chemistry_rates(state: Mapping[str, Array], p: Mapping[str, Array]) -> Array:
    """Return dx_HII/dt, dx_HeII/dt, dx_HeIII/dt with full-OTS event vectors."""
    T = temperature(state, p)
    ne = electron_density(state, p)
    gH, gHeI, gHeII, _ = gamma_species(state, p)

    nH = p["nH_phys"]
    nHe = p["nHe_phys"]
    populations = jnp.array(
        [
            nH * (1.0 - state["xHII"]),
            nH * state["xHII"],
            nHe * state["xHeI"],
            nHe * state["xHeII"],
            nHe * state["xHeIII"],
        ]
    )

    # Primary/collisional ionization events.
    rates = [
        populations[0] * (gH + ne * beta_hi(T)),
        populations[2] * (gHeI + ne * beta_hei(T)),
        populations[3] * (gHeII + ne * beta_heii(T)),
    ]
    vectors = [
        jnp.array([-1.0, 1.0, 0.0, 0.0, 0.0]),
        jnp.array([0.0, 0.0, -1.0, 1.0, 0.0]),
        jnp.array([0.0, 0.0, 0.0, -1.0, 1.0]),
    ]

    # Opacity fractions used by the Friedrich-style OTS event algebra.
    floor = 1.0e-300
    op_h24 = populations[0] * p["sigma_ots_H24"]
    op_he24 = populations[2] * p["sigma_ots_HeI24"]
    y = op_h24 / (op_h24 + op_he24 + floor)

    op_h41 = populations[0] * p["sigma_ots_H41"]
    op_he41 = populations[2] * p["sigma_ots_HeI41"]
    zfrac = op_h41 / (op_h41 + op_he41 + floor)

    op_h54 = populations[0] * p["sigma_ots_H54"]
    op_he54 = populations[2] * p["sigma_ots_HeI54"]
    op_heii54 = populations[3] * p["sigma_ots_HeII54"]
    total54 = op_h54 + op_he54 + op_heii54 + floor
    y2a = op_heii54 / total54
    y2b = op_he54 / total54

    p_exc = 0.96
    l_cas = 1.425
    m_cas = 0.737
    vT = sigmoid((T - 2.0e4) / 4.0e3)
    fH = 1.0 - jnp.exp(-100.0 * (1.0 - state["xHII"]))
    w = (l_cas - m_cas) + m_cas * y
    A_H = vT * w + (1.0 - vT) * fH * zfrac
    A_HeI = vT * m_cas * (1.0 - y) + (1.0 - vT) * fH * (1.0 - zfrac)

    aA2 = alpha_a_heii(T)
    aB2 = alpha_b_heii(T)
    aA3 = alpha_a_heiii(T)
    aB3 = alpha_b_heiii(T)
    aN2 = jnp.minimum(alpha_heiii_n2(T), aB3)
    aCas = jnp.maximum(aB3 - aN2, 0.0)

    rates += [
        populations[1] * ne * alpha_b_hii(T),
        populations[3] * ne * jnp.maximum(aA2 - aB2, 0.0),
        populations[3] * ne * aB2,
        populations[4] * ne * jnp.maximum(aA3 - aB3, 0.0),
        populations[4] * ne * aN2,
        populations[4] * ne * aCas,
    ]
    vectors += [
        jnp.array([1.0, -1.0, 0.0, 0.0, 0.0]),
        jnp.array([-y, y, y, -y, 0.0]),
        jnp.array([-p_exc, p_exc, 1.0, -1.0, 0.0]),
        jnp.array([-(1.0 - y2a - y2b), 1.0 - y2a - y2b, -y2b, 1.0 + y2b - y2a, -1.0 + y2a]),
        jnp.array([-1.0, 1.0, 0.0, 1.0, -1.0]),
        jnp.array([-A_H, A_H, -A_HeI, 1.0 + A_HeI, -1.0]),
    ]

    dpop = jnp.zeros(5, dtype=populations.dtype)
    for rate, vector in zip(rates, vectors):
        dpop = dpop + rate * vector

    return jnp.array([dpop[1] / nH, dpop[3] / nHe, dpop[4] / nHe])


def thermal_rate(state: Mapping[str, Array], p: Mapping[str, Array]) -> Array:
    T = temperature(state, p)
    ne = electron_density(state, p)
    gH, gHeI, gHeII, group_gH = gamma_species(state, p)

    nH = p["nH_phys"]
    nHe = p["nHe_phys"]
    nHI = nH * (1.0 - state["xHII"])
    nHII = nH * state["xHII"]
    nHeI = nHe * state["xHeI"]
    nHeII = nHe * state["xHeII"]
    nHeIII = nHe * state["xHeIII"]

    prefactor = C_LIGHT * (1.0 + p["z_cos"]) ** 3 / MPC_CM**3
    group_gHeI = prefactor * p["sigma_HeI"] * state["N"]
    group_gHeII = prefactor * p["sigma_HeII"] * state["N"]

    heat = EV_ERG * (
        nHI * jnp.sum(group_gH * p["excess_HI_eV"])
        + nHeI * jnp.sum(group_gHeI * p["excess_HeI_eV"])
        + nHeII * jnp.sum(group_gHeII * p["excess_HeII_eV"])
    )

    llH = lambda_hi(T)
    llHeII = lambda_heii(T)
    recH = 3.435e-30 * T * llH**1.970 / (1.0 + (llH / 2.250) ** 0.376) ** 3.720
    recHeII = KB_ERG * T * (1.26e-14 * lambda_hei(T) ** 0.750)
    recHeIII = 8.0 * 3.435e-30 * T * llHeII**1.970 / (1.0 + (llHeII / 2.250) ** 0.376) ** 3.720
    excH = 7.5e-19 * jnp.exp(-118348.0 / T) / (1.0 + jnp.sqrt(T / 1.0e5))
    excHeII = 5.54e-17 * T**-0.397 * jnp.exp(-473638.0 / T) / (1.0 + jnp.sqrt(T / 1.0e5))
    ff = 1.42e-27 * jnp.sqrt(T) * (1.1 + 0.34 * jnp.exp(-(5.5 - jnp.log10(T)) ** 2 / 3.0))

    cool = (
        ne * nHII * recH
        + ne * nHeII * recHeII
        + ne * nHeIII * recHeIII
        + ne * nHI * excH
        + ne * nHeII * excHeII
        + ne * nHI * beta_hi(T) * 13.598 * EV_ERG
        + ne * nHeI * beta_hei(T) * 24.587 * EV_ERG
        + ne * nHeII * beta_heii(T) * 54.416 * EV_ERG
        + ne * (nHII + nHeII + 4.0 * nHeIII) * ff
    )

    npart = nH + nHe + ne
    pressure = npart * KB_ERG * T
    expansion = 3.0 * p["Hubble"] * pressure
    return heat - cool - expansion


def physical_rhs(state: Mapping[str, Array], emissivity: Array, p: Mapping[str, Array]) -> Mapping[str, Array]:
    return {
        "N": photon_rates(state, emissivity, p),
        "x": chemistry_rates(state, p),
        "u": thermal_rate(state, p),
    }


def residual(z: Array, log_emissivity: Array, p: Mapping[str, Array]) -> Array:
    state = transform_z_to_y(z)
    emissivity = jnp.exp(log_emissivity)
    rhs = physical_rhs(state, emissivity, p)
    gamma_calc = gamma_species(state, p)[0]

    fN = (state["N"] - p["N_prev"] - p["dt"] * rhs["N"]) / p["scale_N"]
    fx = (
        jnp.array([state["xHII"], state["xHeII"], state["xHeIII"]])
        - p["x_prev"]
        - p["dt"] * rhs["x"]
    ) / p["scale_x"]
    fu = (state["u"] - p["u_prev"] - p["dt"] * rhs["u"]) / p["scale_u"]
    fg = (state["GammaHI"] - gamma_calc) / p["scale_gamma"]
    return jnp.concatenate([fN, fx, jnp.array([fu, fg])])


def physical_vector(z: Array, p: Mapping[str, Array]) -> Array:
    state = transform_z_to_y(z)
    return jnp.concatenate(
        [
            state["N"],
            jnp.array([state["xHII"], state["xHeII"], state["xHeIII"], state["u"], state["GammaHI"]]),
        ]
    )
