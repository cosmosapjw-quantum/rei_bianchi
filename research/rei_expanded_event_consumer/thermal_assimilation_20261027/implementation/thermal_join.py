"""Conditional local number/energy assimilation at the saved native PW19 node.

The 25 source rows are Y[21], zeta, w_nt, signed w_ext, and log(T/K).
Counts and energies are per baryon; rates use proper seconds. This is a local
source operator with a prescribed constant-in-energy relaxation rate, not a
qualified stopping law or an evolved cosmological history.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
UNIT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rei_expanded_event_consumer/blocker_closure_20261026"
PHOTO = ROOT / "research/rei_expanded_event_consumer/coupled_source_20261027/implementation"
REC_MOMENTS = UNIT / "vendor/rec124/rec_thermal_moments_20261022/code"
REC_COMPTON = UNIT / "vendor/rec124/rec_thermal_omitted_budget_20261022/code"
HE = UNIT / "vendor/he/exchange"
for directory in (BASE / "implementation", PHOTO, REC_MOMENTS, REC_COMPTON, HE):
    sys.path.insert(0, str(directory))

from coupled_photo_source import augmented_photo_source, OWNER, EV_J
from compton_budget import (
    planck_reference_power, KB_J_K, SIGMA_T_C_M3_S, MEC2_J,
    A_RAD_J_M3_K4,
)
from exchange_closure import monatomic_caloric, temperature_rhs

CV = 1.5 * KB_J_K
EMAX_J = 49945.58 * EV_J
ALG = 2e-14
ZERO_NUCLEAR = (0, 5, 6)
STATE_SCALARS = (
    "zeta", "w_nt", "w_ext", "T_K", "nb_m3", "a", "H_s_inverse",
    "nu_s_inverse", "lambda_source", "beta", "r_m3",
)
DIRECTION_SCALARS = (
    "dzeta", "dw_nt", "dw_ext", "dell", "dnb", "da", "dH",
    "dnu", "dlambda", "dbeta", "dr",
)


def _finite(value, name):
    if np.iscomplexobj(value):
        raise ValueError(name + " must be real")
    answer = float(value)
    if not math.isfinite(answer):
        raise ValueError(name + " must be finite")
    return answer


def _vector(value, size, name):
    if np.iscomplexobj(value):
        raise ValueError(name + " must be real")
    answer = np.asarray(value, dtype=float)
    if answer.shape != (size,) or not np.all(np.isfinite(answer)):
        raise ValueError(name + f" must be a finite length-{size} vector")
    return answer


def zero_direction():
    return {"v": np.zeros(21), **{name: 0.0 for name in DIRECTION_SCALARS}}


def compton_component(g, T, nb, a, *, dg=0.0, dell=0.0, da=0.0,
                      dg_operand_scale=None):
    """Native Planck-reference power and analytic baryon-normalized JVP.

    This component alone permits T below the atomic-rate domain, including the
    actual T=Tr equilibrium control. No RR/DR routine is called here.
    """
    g, T, nb, a = (_finite(x, name) for x, name in
                   ((g, "g"), (T, "T"), (nb, "nb"), (a, "a")))
    dg, dell, da = (_finite(x, name) for x, name in
                    ((dg, "dg"), (dell, "dell"), (da, "da")))
    if g < 0 or min(T, nb, a) <= 0:
        raise ValueError("nonnegative thermal electrons and positive T,nb,a required")
    Tr = 2.7255 / a
    U = A_RAD_J_M3_K4 * Tr**4
    tau = Tr / T
    coefficient = (8.0 / 3.0) * SIGMA_T_C_M3_S / MEC2_J
    B = coefficient * U * (tau - 1.0)
    dB_a = -coefficient * U * (5.0 * tau - 4.0) * da / a
    dB_T = -coefficient * U * tau * dell
    dB = dB_a + dB_T
    Q = planck_reference_power(nb * g, T, Tr)
    q = Q / nb
    dq = CV * T * (B * dg + g * dB + g * B * dell)
    gs = abs(dg) if dg_operand_scale is None else float(dg_operand_scale)
    dscale = CV * T * (abs(B) * gs + abs(g) * (abs(dB_a) + abs(dB_T))
                       + abs(g * B * dell))
    return {"Q_W_m3": Q, "q_J_per_baryon_s": q, "jvp": dq,
            "jvp_operand_scale": dscale, "B_s_inverse": B, "dB": dB,
            "T_r_K": Tr, "U_r_J_m3": U, "branch": "planck_reference",
            "physical_electron_density_m3": nb * g}


def map_sources(source, jvp, source_scale, jvp_scale, *, nb, dnb,
                beta, dbeta, H, dH):
    """Only the first24 rows are densities; all25 rows change to eta time."""
    output = {"proper": {"source": source.copy(), "jvp": jvp.copy(),
                         "source_operand_scale": source_scale.copy(),
                         "jvp_operand_scale": jvp_scale.copy()}}
    for name, factor, dfactor in (("physical", nb, dnb), ("reference", beta, dbeta)):
        value, tangent = source.copy(), jvp.copy()
        scale, dscale = source_scale.copy(), jvp_scale.copy()
        value[:24] *= factor
        tangent[:24] = factor * jvp[:24] + dfactor * source[:24]
        scale[:24] *= factor
        dscale[:24] = factor * jvp_scale[:24] + abs(dfactor) * source_scale[:24]
        output[name] = {"source": value, "jvp": tangent,
                        "source_operand_scale": scale, "jvp_operand_scale": dscale}
    output["eta"] = {
        "source": source / H,
        "jvp": jvp / H - source * (dH / H**2),
        "source_operand_scale": source_scale / H,
        "jvp_operand_scale": jvp_scale / H + source_scale * abs(dH) / H**2,
    }
    return output


def reference_input_map(network, x, dx):
    """Convert every reference-normalized reservoir and its input direction."""
    x, dx = _vector(x, 25, "x"), _vector(dx, 25, "dx")
    beta = float(network.A @ x[:21])
    dbeta = float(network.A @ dx[:21])
    if beta <= 0:
        raise ValueError("positive reference baryon count required")
    z = x.copy()
    z[:24] /= beta
    dz = dx.copy()
    dz[:24] = (dx[:24] - z[:24] * dbeta) / beta
    return {"native_coordinates": z, "native_direction": dz,
            "beta": beta, "dbeta": dbeta,
            "direction_operand_scale": np.concatenate((
                (np.abs(dx[:24]) + np.abs(z[:24] * dbeta)) / beta,
                [abs(dx[24])]))}


def changing_reference_control(S, x, r, Rr, dS, dx, dr, dRr):
    """Labeled source-only algebra for a general physical reference density.

    This does not activate another cosmological background or supply omitted
    kinetic pressure work. S and x have compatible same-row physical units.
    """
    S, x, dS, dx = (_vector(value, 24, name) for value, name in
                    ((S, "S"), (x, "x"), (dS, "dS"), (dx, "dx")))
    r, Rr, dr, dRr = (_finite(value, name) for value, name in
                      ((r, "r"), (Rr, "Rr"), (dr, "dr"), (dRr, "dRr")))
    if r <= 0:
        raise ValueError("positive physical reference required")
    value = (S - x * Rr) / r
    tangent = (dS - Rr * dx - x * dRr) / r - value * dr / r
    value_scale = (np.abs(S) + np.abs(x * Rr)) / r
    tangent_scale = (np.abs(dS) + np.abs(Rr * dx) + np.abs(x * dRr)) / r
    tangent_scale += value_scale * abs(dr) / r
    return {"source": value, "jvp": tangent,
            "source_operand_scale": value_scale, "jvp_operand_scale": tangent_scale,
            "scope": "manufactured_general_reference_algebra_only"}


class ThermalJoin:
    def __init__(self, network, thermal_coefficients, *, photo_owners=(OWNER,),
                 compton_branch="planck_reference", prompt_thermalization=False):
        if tuple(photo_owners) != (OWNER,):
            raise ValueError("one selected native photo owner required")
        if compton_branch != "planck_reference":
            raise ValueError("only separately prescribed Planck reference is selected")
        if prompt_thermalization:
            raise ValueError("prompt thermalization is incompatible with the fast pool")
        if thermal_coefficients.atomic is not network or thermal_coefficients.closure != "mao2017":
            raise ValueError("unchanged native Mao2017 hybrid coefficients required")
        self.network = network
        self.thermal_coefficients = thermal_coefficients

    def evaluate(self, state, direction=None):
        net = self.network
        y = _vector(state["Y"], 21, "Y")
        s = {name: _finite(state[name], name) for name in STATE_SCALARS}
        direction = zero_direction() if direction is None else direction
        v = _vector(direction["v"], 21, "v")
        d = {name: _finite(direction.get(name, 0.0), name)
             for name in DIRECTION_SCALARS}
        if np.any(y < 0) or any(y[i] != 0 or v[i] != 0 for i in ZERO_NUCLEAR):
            raise ValueError("nonnegative Y and zero neutron/tritium state and tangent required")
        baryons = float(net.A @ y)
        if abs(baryons - 1.0) > ALG * (float(np.abs(net.A) @ np.abs(y)) + 1.0):
            raise ValueError("A dot Y must be one; no renormalization is performed")
        if not 100.0 <= s["T_K"] <= 1e6:
            raise ValueError("native atomic temperature domain is100..1e6K")
        if min(s[k] for k in ("nb_m3", "a", "H_s_inverse", "beta", "r_m3")) <= 0:
            raise ValueError("positive density, a, H and reference factors required")
        if min(s["nu_s_inverse"], s["lambda_source"]) < 0:
            raise ValueError("nonnegative declared relaxation and source amplitude required")
        if abs(s["nb_m3"] - s["beta"] * s["r_m3"]) > ALG * (
                abs(s["nb_m3"]) + abs(s["beta"] * s["r_m3"])):
            raise ValueError("native density must equal beta times the reference density")
        charge = float(net.q @ y)
        zeta, w = s["zeta"], s["w_nt"]
        g = charge - zeta
        chi = float((1 + net.q) @ y) - zeta
        if zeta < 0 or g < 0 or w < 0 or w > EMAX_J * zeta or chi <= 0:
            raise ValueError("nonthermal subset, first-moment support or thermal count invalid")
        T, nb, nu = s["T_K"], s["nb_m3"], s["nu_s_inverse"]
        dg = float(net.q @ v) - d["dzeta"]
        dchi = float((1 + net.q) @ v) - d["dzeta"]
        dg_scale = float(np.abs(net.q) @ np.abs(v)) + abs(d["dzeta"])
        dchi_scale = float(np.abs(1 + net.q) @ np.abs(v)) + abs(d["dzeta"])
        ne = nb * g
        dne = d["dnb"] * g + nb * dg
        dne_scale = abs(d["dnb"] * g) + nb * dg_scale

        photo = augmented_photo_source(
            net, y, T, nb, s["lambda_source"], zeta_per_baryon=zeta,
            v=v, dlambda=d["dlambda"], dnb=d["dnb"], dzeta=d["dzeta"])
        P, dP = photo["source"][:21], photo["jvp"][:21]
        event, kinetic, minus_absorbed = photo["source"][21:24]
        devent, dkinetic, dminus_absorbed = photo["jvp"][21:24]
        pscale = s["lambda_source"] * (np.abs(net._Gphoto) @ np.abs(y))
        dpscale = (s["lambda_source"] * (np.abs(net._Gphoto) @ np.abs(v))
                   + abs(d["dlambda"]) * (np.abs(net._Gphoto) @ np.abs(y)))
        photo_factor_scale = (s["lambda_source"] * (abs(v[8]) + abs(v[11]))
                              + abs(d["dlambda"]) * (y[8] + y[11]))
        dkinetic_scale = net.selected_K_J_s * photo_factor_scale
        dabs_scale = net.selected_A_J_s * photo_factor_scale

        # Use only the native coefficient helper. Its evaluate() thermalizer
        # and the photo helper's all-electron side outputs are not assembled.
        coeff = self.thermal_coefficients.coefficients(T)
        rates = net.rates(T, s["lambda_source"])
        recombination = {}
        for name, Gname, rate_key, drate_key, loss_key, dloss_key in (
            ("rr", "Grr", "rr_m3_s", "drr_dlogT", "rr_loss_J_m3_s", "drr_loss_dlogT"),
            ("dr", "Gdr", "dr_m3_s", "ddr_dlogT", "dr_loss_J_m3_s", "ddr_loss_dlogT"),
        ):
            G = rates[Gname]
            Gl = net._transition_matrix(coeff[drate_key], upward=False)
            action = G @ y
            R = ne * action
            dR = dne * action + ne * (G @ v + (Gl @ y) * d["dell"])
            Rscale = ne * (np.abs(G) @ np.abs(y))
            dRscale = (dne_scale * (np.abs(G) @ np.abs(y))
                       + ne * (np.abs(G) @ np.abs(v))
                       + ne * abs(d["dell"]) * (np.abs(Gl) @ np.abs(y)))
            kappa, dkappa = coeff[loss_key], coeff[dloss_key]
            L = ne * float(y @ kappa)
            dL = dne * float(y @ kappa) + ne * float(v @ kappa + (y @ dkappa) * d["dell"])
            Lscale = ne * float(np.abs(y) @ np.abs(kappa))
            dLscale = (dne_scale * float(np.abs(y) @ np.abs(kappa))
                       + ne * float(np.abs(v) @ np.abs(kappa))
                       + ne * abs(d["dell"]) * float(np.abs(y) @ np.abs(dkappa)))
            binding = float(net.ionization_energy_J @ R)
            dbinding = float(net.ionization_energy_J @ dR)
            escape = L - binding
            descape = dL - dbinding
            escape_scale = Lscale + float(np.abs(net.ionization_energy_J) @ Rscale)
            descape_scale = dLscale + float(np.abs(net.ionization_energy_J) @ dRscale)
            recombination[name] = {
                "R": R, "jvp_R": dR, "R_operand_scale": Rscale,
                "jvp_R_operand_scale": dRscale,
                "L_J_per_baryon_s": L, "jvp_L": dL,
                "L_operand_scale": Lscale, "jvp_L_operand_scale": dLscale,
                "escape_J_per_baryon_s": escape, "jvp_escape": descape,
                "escape_operand_scale": escape_scale,
                "jvp_escape_operand_scale": descape_scale,
                "native_rate": rates[rate_key], "helper_rate": coeff[rate_key],
            }
        rr, dr = recombination["rr"], recombination["dr"]
        R, dR = rr["R"] + dr["R"], rr["jvp_R"] + dr["jvp_R"]
        Rscale = rr["R_operand_scale"] + dr["R_operand_scale"]
        dRscale = rr["jvp_R_operand_scale"] + dr["jvp_R_operand_scale"]
        L = rr["L_J_per_baryon_s"] + dr["L_J_per_baryon_s"]
        dL = rr["jvp_L"] + dr["jvp_L"]
        Lscale = rr["L_operand_scale"] + dr["L_operand_scale"]
        dLscale = rr["jvp_L_operand_scale"] + dr["jvp_L_operand_scale"]
        j, h = nu * zeta, nu * w
        dj, dh = d["dnu"] * zeta + nu * d["dzeta"], d["dnu"] * w + nu * d["dw_nt"]
        djscale = abs(d["dnu"] * zeta) + abs(nu * d["dzeta"])
        dhscale = abs(d["dnu"] * w) + abs(nu * d["dw_nt"])
        cmb = compton_component(g, T, nb, s["a"], dg=dg, dell=d["dell"],
                                da=d["da"], dg_operand_scale=dg_scale)
        qC, dqC = cmb["q_J_per_baryon_s"], cmb["jvp"]
        qthermal = h + qC - L
        dqthermal = dh + dqC - dL
        qthermal_scale = abs(h) + abs(qC) + Lscale
        dqthermal_scale = dhscale + cmb["jvp_operand_scale"] + dLscale
        count = float(net.q @ R) + j
        dcount = float(net.q @ dR) + dj
        count_scale = float(np.abs(net.q) @ Rscale) + abs(j)
        dcount_scale = float(np.abs(net.q) @ dRscale) + djscale
        ell = (qthermal / (CV * T) - count) / chi
        dell_source = ((dqthermal - qthermal * d["dell"]) / (CV * T) - dcount) / chi
        dell_source -= ell * dchi / chi
        ell_scale = qthermal_scale / (CV * T * chi) + count_scale / chi
        dell_scale = ((dqthermal_scale + qthermal_scale * abs(d["dell"])) / (CV * T)
                      + dcount_scale) / chi + ell_scale * dchi_scale / chi
        source = np.concatenate((P + R, [event - j, kinetic - h,
            minus_absorbed - qC + rr["escape_J_per_baryon_s"] + dr["escape_J_per_baryon_s"], ell]))
        tangent = np.concatenate((dP + dR, [devent - dj, dkinetic - dh,
            dminus_absorbed - dqC + rr["jvp_escape"] + dr["jvp_escape"], dell_source]))
        source_scale = np.concatenate((pscale + Rscale, [
            float(np.abs(net.q) @ pscale) + abs(j), abs(kinetic) + abs(h),
            abs(minus_absorbed) + abs(qC) + rr["escape_operand_scale"] + dr["escape_operand_scale"], ell_scale]))
        tangent_scale = np.concatenate((dpscale + dRscale, [
            float(np.abs(net.q) @ dpscale) + djscale, dkinetic_scale + dhscale,
            dabs_scale + cmb["jvp_operand_scale"] + rr["jvp_escape_operand_scale"] + dr["jvp_escape_operand_scale"], dell_scale]))

        caloric_rows = [monatomic_caloric(
            name, nb * y[i], nb * source[i], T, population_pool="thermal")
            for i, name in enumerate(net.names)]
        caloric_rows.append(monatomic_caloric(
            "electron_thermal", ne, nb * count, T, population_pool="thermal"))
        he = temperature_rhs(
            caloric_rows, temperature_k=T, expansion_s=0.0,
            pressure_pa=nb * chi * KB_J_K * T, centered_heat_w_m3=nb * qthermal,
            shear_work_w_m3=0.0, heat_flux_divergence_w_m3=0.0,
            common_temperature_contract="native_common_T_case_A_thermal_pool_only",
            independent_internal_components=("atomic_binding", "nonthermal_kinetic", "external_transfer"))
        maps = map_sources(source, tangent, source_scale, tangent_scale,
                           nb=nb, dnb=d["dnb"], beta=s["beta"], dbeta=d["dbeta"],
                           H=s["H_s_inverse"], dH=d["dH"])
        return {
            "maps": maps, "source": source, "jvp": tangent,
            "source_operand_scale": source_scale, "jvp_operand_scale": tangent_scale,
            "P": P, "jvp_P": dP, "R": R, "jvp_R": dR,
            "photo_source": photo["source"], "photo_jvp": photo["jvp"],
            "recombination": recombination, "compton": cmb,
            "coefficients": coeff,
            "thermal": {"g": g, "chi": chi, "ne_m3": ne,
                "dg": dg, "dchi": dchi, "dne_m3": dne,
                "dg_operand_scale": dg_scale, "dchi_operand_scale": dchi_scale,
                "number_source_per_baryon_s": count, "number_jvp": dcount,
                "number_operand_scale": count_scale, "number_jvp_operand_scale": dcount_scale,
                "power_J_per_baryon_s": qthermal, "power_jvp": dqthermal,
                "power_operand_scale": qthermal_scale, "power_jvp_operand_scale": dqthermal_scale,
                "RR_DR_loss_J_per_baryon_s": L},
            "assimilation": {"j_per_baryon_s": j, "h_J_per_baryon_s": h,
                "jvp_j": dj, "jvp_h": dh, "jvp_j_operand_scale": djscale,
                "jvp_h_operand_scale": dhscale,
                "closure": "constant_in_energy_prescribed_nu", "physical_rate_qualified": False},
            "external_ledger": {"photo": float(minus_absorbed), "Compton_CMB": -qC,
                "RR_escape": rr["escape_J_per_baryon_s"], "DR_escape": dr["escape_J_per_baryon_s"]},
            "external_ledger_jvp": {"photo": float(dminus_absorbed), "Compton_CMB": -dqC,
                "RR_escape": rr["jvp_escape"], "DR_escape": dr["jvp_escape"]},
            "HE_caloric": he, "HE_logT_source": he["temperature_rate_k_s"] / T,
            "HE_binding": {"supplier": "BASS_HE", "commit": "ac6042a6b0610b09d0576538767ee0299389a5eb",
                "ion_rows": 21, "explicit_thermal_electron_rows": 1,
                "thermal_electron_source_m3_s": nb * count, "centered_power_W_m3": nb * qthermal},
            "owners": {"photo_event": OWNER, "fast_kinetic": "declared_nonthermal_electron_pool",
                "thermal_kinetic": "HE_common_T_monatomic_pool", "binding": "REC119_population_derived_I_dot_Y",
                "external_transfer": "one_signed_aggregate_with_named_legs"},
            "source_only": True, "conditional_selected_closure": True,
            "physical_assimilation_uncertainty": None, "global_physical_completion": None,
        }
