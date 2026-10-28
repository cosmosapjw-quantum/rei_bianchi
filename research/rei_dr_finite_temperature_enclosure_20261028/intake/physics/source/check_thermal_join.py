"""Only the frozen new local thermal join; no inherited suite or IVP."""
from __future__ import annotations

# Install the child CPU limit before importing NumPy or any scientific source.
import signal
import time

CHILD_CPU_LIMIT_S = 1.25
signal.signal(signal.SIGPROF, signal.SIG_DFL)
remaining_cpu = CHILD_CPU_LIMIT_S - time.process_time()
if remaining_cpu <= 0:
    raise SystemExit("child CPU exhausted before scientific imports")
signal.setitimer(signal.ITIMER_PROF, remaining_cpu)

import json
import math
from pathlib import Path
import platform
import sys
import traceback

import numpy as np

from thermal_join import (
    ThermalJoin, zero_direction, reference_input_map, changing_reference_control,
    compton_component, CV, EMAX_J, KB_J_K, SIGMA_T_C_M3_S, MEC2_J,
    A_RAD_J_M3_K4, OWNER, ROOT, UNIT, BASE,
)
from pw19_rec_callback import PW19HeIINetwork, ROUTE, ISOTOPE_POLICY, EVENT_OWNER
from thermal_sources import ThermalSources

ALG = 2e-14
FD_TOL = 2e-8
FD_STEPS = (2e-4, 1e-4)
OUT = UNIT / "implementation/attempt01"
checks = []
observations = {}
trace = None


def plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def emit(row):
    checks.append(plain(row))
    if trace is not None:
        trace.write(json.dumps(plain(row), allow_nan=False) + "\n")
        trace.flush()


def compare(name, actual, expected, scale, limit=ALG):
    """Rowwise scales fixed from contributing operands, without a unit floor."""
    a, e, s = (np.atleast_1d(np.asarray(v, dtype=float))
               for v in (actual, expected, scale))
    if a.shape != e.shape or a.shape != s.shape:
        raise AssertionError(name + ": comparison shape mismatch")
    if not (np.all(np.isfinite(a)) and np.all(np.isfinite(e))
            and np.all(np.isfinite(s)) and np.all(s >= 0)):
        raise AssertionError(name + ": nonfinite value or invalid scale")
    zero = s == 0
    if np.any(a[zero] != 0) or np.any(e[zero] != 0):
        raise AssertionError(name + ": a zero contribution scale requires exact-zero operands")
    residual = np.zeros(a.shape)
    residual[~zero] = np.abs(a[~zero] - e[~zero]) / s[~zero]
    maximum = float(np.max(residual)) if residual.size else 0.0
    row = {"name": name, "residual_max": maximum, "limit": limit,
           "row_residuals": residual, "operand_scales": s,
           "exact_zero_rows": np.flatnonzero(zero), "pass": maximum <= limit}
    emit(row)
    if maximum > limit:
        raise AssertionError(f"{name}: residual {maximum!r} exceeds {limit!r}")
    return maximum


def truth(name, condition, **evidence):
    emit({"name": name, "pass": bool(condition), **evidence})
    if not condition:
        raise AssertionError(name)


def reject(name, operation):
    try:
        operation()
    except ValueError as error:
        emit({"name": name, "pass": True, "rejected": True,
              "error_type": type(error).__name__, "message": str(error)})
    else:
        raise AssertionError(name + ": rejected-domain input was accepted")


def changed(state, **fields):
    answer = dict(state)
    answer["Y"] = np.asarray(state["Y"]).copy()
    answer.update(fields)
    return answer


def oracle(net, state, direction, coefficients):
    """Independent transition-flux assembly and physical caloric derivative.

    This reuses admitted atomic coefficients, not their old test suite. It
    neither calls the new join nor multiplies its transition matrices.
    """
    Y, v = state["Y"], direction["v"]
    T, nb = state["T_K"], state["nb_m3"]
    zeta, w = state["zeta"], state["w_nt"]
    nu, lam = state["nu_s_inverse"], state["lambda_source"]
    g = math.fsum(float(net.q[i] * Y[i]) for i in range(21)) - zeta
    chi = math.fsum(float((1 + net.q[i]) * Y[i]) for i in range(21)) - zeta
    dg = math.fsum(float(net.q[i] * v[i]) for i in range(21)) - direction["dzeta"]
    dchi = math.fsum(float((1 + net.q[i]) * v[i]) for i in range(21)) - direction["dzeta"]
    ne, dne = nb * g, direction["dnb"] * g + nb * dg
    P, dP = np.zeros(21), np.zeros(21)
    for lower, upper in ((8, 9), (11, 12)):
        flux = lam * net.selected_Gamma_s * Y[lower]
        dflux = net.selected_Gamma_s * (lam * v[lower] + direction["dlambda"] * Y[lower])
        P[lower], P[upper] = -flux, flux
        dP[lower], dP[upper] = -dflux, dflux
    factor = lam * (Y[8] + Y[11])
    dfactor = lam * (v[8] + v[11]) + direction["dlambda"] * (Y[8] + Y[11])
    event, devent = net.selected_Gamma_s * factor, net.selected_Gamma_s * dfactor
    kinetic, dkinetic = net.selected_K_J_s * factor, net.selected_K_J_s * dfactor
    absorbed, dabsorbed = net.selected_A_J_s * factor, net.selected_A_J_s * dfactor
    parts = {}
    for name, rate, drate, loss, dloss in (
        ("rr", "rr_m3_s", "drr_dlogT", "rr_loss_J_m3_s", "drr_loss_dlogT"),
        ("dr", "dr_m3_s", "ddr_dlogT", "dr_loss_J_m3_s", "ddr_loss_dlogT"),
    ):
        R, dR = np.zeros(21), np.zeros(21)
        for index in net.recombination_indices:
            i = int(index)
            alpha, dalpha = coefficients[rate][i], coefficients[drate][i]
            flux = ne * alpha * Y[i]
            dflux = (dne * alpha * Y[i] + ne * alpha * v[i]
                     + ne * dalpha * Y[i] * direction["dell"])
            R[i] -= flux
            R[i - 1] += flux
            dR[i] -= dflux
            dR[i - 1] += dflux
        L = math.fsum(float(ne * Y[i] * coefficients[loss][i]) for i in range(21))
        dL = math.fsum(float(
            dne * Y[i] * coefficients[loss][i]
            + ne * v[i] * coefficients[loss][i]
            + ne * Y[i] * coefficients[dloss][i] * direction["dell"])
            for i in range(21))
        binding = math.fsum(float(net.ionization_energy_J[i] * R[i]) for i in range(21))
        dbinding = math.fsum(float(net.ionization_energy_J[i] * dR[i]) for i in range(21))
        parts[name] = {"R": R, "dR": dR, "L": L, "dL": dL,
                       "escape": L - binding, "descape": dL - dbinding}
    R, dR = parts["rr"]["R"] + parts["dr"]["R"], parts["rr"]["dR"] + parts["dr"]["dR"]
    L, dL = parts["rr"]["L"] + parts["dr"]["L"], parts["rr"]["dL"] + parts["dr"]["dL"]
    Tr = 2.7255 / state["a"]
    Ur = A_RAD_J_M3_K4 * Tr**4
    dTr = -Tr * direction["da"] / state["a"]
    dUr = -4 * Ur * direction["da"] / state["a"]
    factor_C = 4 * SIGMA_T_C_M3_S * KB_J_K / MEC2_J
    Qc = factor_C * ne * Ur * (Tr - T)
    dQc = factor_C * (dne * Ur * (Tr - T) + ne * dUr * (Tr - T)
                      + ne * Ur * (dTr - T * direction["dell"]))
    qC, dqC = Qc / nb, dQc / nb - Qc * direction["dnb"] / nb**2
    j, h = nu * zeta, nu * w
    dj = direction["dnu"] * zeta + nu * direction["dzeta"]
    dh = direction["dnu"] * w + nu * direction["dw_nt"]
    count = math.fsum(float(net.q[i] * R[i]) for i in range(21)) + j
    dcount = math.fsum(float(net.q[i] * dR[i]) for i in range(21)) + dj
    Q = nb * (h + qC - L)
    dQ = direction["dnb"] * (h + qC - L) + nb * (dh + dqC - dL)
    N = nb * chi
    dN = direction["dnb"] * chi + nb * dchi
    S = nb * count
    dS = direction["dnb"] * count + nb * dcount
    ell = Q / (CV * T * N) - S / N
    dell = (dQ / (CV * T * N) - Q * (direction["dell"] + dN / N) / (CV * T * N)
            - dS / N + S * dN / N**2)
    result = np.concatenate((P + R, [event - j, kinetic - h,
        -absorbed - qC + parts["rr"]["escape"] + parts["dr"]["escape"], ell]))
    tangent = np.concatenate((dP + dR, [devent - dj, dkinetic - dh,
        -dabsorbed - dqC + parts["rr"]["descape"] + parts["dr"]["descape"], dell]))
    return {"source": result, "jvp": tangent, "parts": parts, "P": P,
            "dP": dP, "qC": qC, "dqC": dqC,
            "physical_caloric": {"number_m3": N, "number_source_m3_s": S,
                                  "power_W_m3": Q, "dnumber_m3": dN,
                                  "dnumber_source_m3_s": dS, "dpower_W_m3": dQ}}


def perturb(state, direction, t):
    """The fixed-r0 path has the frozen first derivative, including n_b."""
    result = changed(state)
    result["Y"] += t * direction["v"]
    for field, dfield in (("zeta", "dzeta"), ("w_nt", "dw_nt"), ("w_ext", "dw_ext"),
                         ("a", "da"), ("H_s_inverse", "dH"), ("nu_s_inverse", "dnu"),
                         ("lambda_source", "dlambda"), ("beta", "dbeta")):
        result[field] += t * direction[dfield]
    result["T_K"] *= math.exp(t * direction["dell"])
    result["r_m3"] = state["r_m3"] * (state["a"] / result["a"])**3
    result["nb_m3"] = result["beta"] * result["r_m3"]
    return result


def main():
    saved = json.loads((BASE / "implementation/run01/CALLBACK.json").read_text())
    snapshot = saved["snapshot"]
    net = PW19HeIINetwork(source_z=2.479, source_route=ROUTE,
                         isotope_policy=ISOTOPE_POLICY, photo_owners=(EVENT_OWNER,))
    native_coefficients = ThermalSources(net, rr_closure="mao2017")
    join = ThermalJoin(net, native_coefficients)
    Y = np.asarray(snapshot["Y"], dtype=float)
    H = snapshot["geometry"]["H_s_inverse"]
    zeta = float(net.q @ Y) / 4
    mean_energy = net.selected_K_J_s / net.selected_Gamma_s
    state = {"Y": Y, "zeta": zeta, "w_nt": zeta * mean_energy, "w_ext": 0.0,
             "T_K": snapshot["temperature_K"], "nb_m3": snapshot["nb_m3"],
             "a": 1 / (1 + 2.479), "H_s_inverse": H,
             "nu_s_inverse": 8.160348695705333e-18, "lambda_source": 1.0,
             "beta": snapshot["beta_baryons_per_Href"], "r_m3": snapshot["reference_density_m3"]}
    direction = zero_direction()
    for lower, upper in ((1, 2), (8, 9), (11, 12)):
        amount = .1 * min(Y[lower], Y[upper])
        direction["v"][lower], direction["v"][upper] = amount, -amount
    direction.update(dzeta=.1 * zeta, dw_nt=-.07 * state["w_nt"], dell=.04,
        dnu=.08 * state["nu_s_inverse"], dlambda=.05, da=.02 * state["a"],
        dH=.06 * H, dbeta=.07 * state["beta"], dr=-.06 * state["r_m3"],
        dnb=.01 * state["nb_m3"])
    out = join.evaluate(state, direction)
    independent = oracle(net, state, direction, out["coefficients"])
    observations.update({"state": state, "direction": direction,
        "snapshot_source": "blocker_closure_20261026/implementation/run01/CALLBACK.json",
        "manufactured_reservoir": {"zeta_rule": "q_dot_Y/4", "w_rule": "zeta*K_J/Gamma",
            "mean_energy_J": mean_energy, "is_history": False},
        "joint": out, "independent_component_oracle": independent,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "executable": sys.executable},
        "scope": {"new_scientific_unit": "conditional_selected_local_thermal_join",
            "existing_source_or_suite_replay": False, "IVPs": 0,
            "source_integrations": 0, "physical_stopping_qualified": False,
            "original_completed_nodes": 32, "original_nodes": 88,
            "L4_ready": False, "global_physical_completion": None}})
    # Preserve forward/raw operands before acceptance so a later failure is reviewable.
    (OUT / "FORWARD_RAW.json").write_text(json.dumps(plain(observations), indent=2, allow_nan=False) + "\n")

    compare("new_join_independent_transition_oracle", out["source"], independent["source"], out["source_operand_scale"])
    compare("new_join_independent_physical_caloric_JVP", out["jvp"], independent["jvp"], out["jvp_operand_scale"])
    for name in ("rr", "dr"):
        actual, ref = out["recombination"][name], independent["parts"][name]
        compare(name + "_native_rate_and_helper_identity", actual["native_rate"], actual["helper_rate"],
                np.abs(actual["native_rate"]) + np.abs(actual["helper_rate"]))
        for title, key, rkey, skey in (
            ("thermal_electron_transition", "R", "R", "R_operand_scale"),
            ("thermal_electron_transition_JVP", "jvp_R", "dR", "jvp_R_operand_scale"),
            ("kinetic_cooling", "L_J_per_baryon_s", "L", "L_operand_scale"),
            ("kinetic_cooling_JVP", "jvp_L", "dL", "jvp_L_operand_scale"),
            ("one_escape_owner", "escape_J_per_baryon_s", "escape", "escape_operand_scale"),
            ("one_escape_owner_JVP", "jvp_escape", "descape", "jvp_escape_operand_scale"),
        ):
            compare(name + "_" + title, actual[key], ref[rkey], actual[skey])
    compare("native_Planck_power", out["compton"]["q_J_per_baryon_s"], independent["qC"],
            abs(out["compton"]["q_J_per_baryon_s"]) + abs(independent["qC"]))
    compare("native_Planck_quotient_JVP", out["compton"]["jvp"], independent["dqC"],
            out["compton"]["jvp_operand_scale"])
    truth("native_DR_masks_preserved", np.array_equal(
        out["coefficients"]["dr_structurally_absent_mask"], ~native_coefficients.moments.dr_present)
        and np.array_equal(out["coefficients"]["dr_numerical_zero_mask"],
            native_coefficients.moments.dr_present & (out["coefficients"]["dr_m3_s"] == 0)))

    F, dF = out["source"], out["jvp"]
    Fs, dFs = out["source_operand_scale"], out["jvp_operand_scale"]
    th = out["thermal"]
    compare("baryon_source", net.A @ F[:21], 0.0, np.abs(net.A) @ Fs[:21])
    compare("baryon_source_JVP", net.A @ dF[:21], 0.0, np.abs(net.A) @ dFs[:21])
    for name, indices in net.isotope_groups.items():
        ix = list(indices)
        compare("isotope_" + name, np.sum(F[ix]), 0.0, np.sum(Fs[ix]))
        compare("isotope_" + name + "_JVP", np.sum(dF[ix]), 0.0, np.sum(dFs[ix]))
    for weight, label in ((net.q, "thermal_electron_partition"), (1 + net.q, "thermal_particle_count")):
        compare(label, weight @ F[:21] - F[21], th["number_source_per_baryon_s"],
            np.abs(weight) @ Fs[:21] + Fs[21] + th["number_operand_scale"])
        compare(label + "_JVP", weight @ dF[:21] - dF[21], th["number_jvp"],
            np.abs(weight) @ dFs[:21] + dFs[21] + th["number_jvp_operand_scale"])
    thermal_energy = CV * state["T_K"] * (th["chi"] * F[24] + th["number_source_per_baryon_s"])
    thermal_energy_scale = CV * state["T_K"] * (th["chi"] * Fs[24] + th["number_operand_scale"])
    dthermal_energy = CV * state["T_K"] * (
        direction["dell"] * (th["chi"] * F[24] + th["number_source_per_baryon_s"])
        + th["dchi"] * F[24] + th["chi"] * dF[24] + th["number_jvp"])
    dthermal_energy_scale = CV * state["T_K"] * (
        abs(direction["dell"]) * (th["chi"] * Fs[24] + th["number_operand_scale"])
        + th["dchi_operand_scale"] * Fs[24] + th["chi"] * dFs[24]
        + th["number_jvp_operand_scale"])
    compare("caloric_energy_count_chain", thermal_energy, th["power_J_per_baryon_s"],
            thermal_energy_scale + th["power_operand_scale"])
    compare("caloric_energy_count_chain_JVP", dthermal_energy, th["power_jvp"],
            dthermal_energy_scale + th["power_jvp_operand_scale"])
    compare("all_single_owned_energy_stores", net.ionization_energy_J @ F[:21] + F[22] + F[23] + thermal_energy,
            0.0, np.abs(net.ionization_energy_J) @ Fs[:21] + Fs[22] + Fs[23] + thermal_energy_scale)
    compare("all_single_owned_energy_stores_JVP", net.ionization_energy_J @ dF[:21] + dF[22] + dF[23] + dthermal_energy,
            0.0, np.abs(net.ionization_energy_J) @ dFs[:21] + dFs[22] + dFs[23] + dthermal_energy_scale)
    compare("actual_HE_sink_logT", out["HE_logT_source"], F[24], 2 * Fs[24])
    compare("actual_HE_sink_count", out["HE_caloric"]["number_m3"], state["nb_m3"] * th["chi"],
            2 * state["nb_m3"] * th["chi"])
    compare("actual_HE_sink_number_source", out["HE_caloric"]["number_source_m3_s"],
            state["nb_m3"] * th["number_source_per_baryon_s"],
            state["nb_m3"] * (np.sum(Fs[:21]) + 2 * th["number_operand_scale"]))
    compare("named_external_ledger_once", math.fsum(out["external_ledger"].values()), F[23], 2 * Fs[23])

    beta, nb, r, H = state["beta"], state["nb_m3"], state["r_m3"], state["H_s_inverse"]
    compare("fixed_r0_density_tangent", direction["dnb"], r * direction["dbeta"] + beta * direction["dr"],
            abs(direction["dnb"]) + abs(r * direction["dbeta"]) + abs(beta * direction["dr"]))
    z = np.concatenate((Y, [state["zeta"], state["w_nt"], state["w_ext"], math.log(state["T_K"])]))
    dz = np.concatenate((direction["v"], [direction["dzeta"], direction["dw_nt"], direction["dw_ext"], direction["dell"]]))
    x, dx = z.copy(), dz.copy()
    x[:24] *= beta
    dx[:24] = beta * dz[:24] + direction["dbeta"] * z[:24]
    mapped = reference_input_map(net, x, dx)
    compare("all_reference_state_coordinates", mapped["native_coordinates"], z,
            np.abs(mapped["native_coordinates"]) + np.abs(z))
    compare("all_reference_reservoir_tangents", mapped["native_direction"], dz,
            mapped["direction_operand_scale"] + np.abs(dz))
    compare("reference_input_beta", mapped["beta"], beta, abs(mapped["beta"]) + beta)
    compare("reference_input_dbeta", mapped["dbeta"], direction["dbeta"],
            float(np.abs(net.A) @ np.abs(dx[:21])) + abs(direction["dbeta"]))
    for name, scale, dscale in (("physical", nb, direction["dnb"]), ("reference", beta, direction["dbeta"])):
        target, dtarget = F.copy(), dF.copy()
        target[:24] = np.asarray([scale * independent["source"][i] for i in range(24)])
        dtarget[:24] = np.asarray([scale * independent["jvp"][i] + dscale * independent["source"][i] for i in range(24)])
        compare(name + "_first24_map", out["maps"][name]["source"], target, out["maps"][name]["source_operand_scale"])
        compare(name + "_first24_map_JVP", out["maps"][name]["jvp"], dtarget, out["maps"][name]["jvp_operand_scale"])
        compare(name + "_logT_is_not_a_density", out["maps"][name]["source"][24], F[24], 2 * Fs[24])

    # The same predeclared analytic operand scales serve both FD step sizes.
    fixed_scales = {key: value["jvp_operand_scale"].copy() for key, value in out["maps"].items()}
    observations["FD_fixed_analytic_operand_scales"] = fixed_scales
    fd_results = {}
    for step in FD_STEPS:
        plus_state, minus_state = perturb(state, direction, step), perturb(state, direction, -step)
        plus, minus = join.evaluate(plus_state), join.evaluate(minus_state)
        fd_results[str(step)] = {}
        for name in out["maps"]:
            fd = (plus["maps"][name]["source"] - minus["maps"][name]["source"]) / (2 * step)
            residual = compare(f"new_assembly_FD_{name}_h{step:g}", fd, out["maps"][name]["jvp"],
                               fixed_scales[name], FD_TOL)
            fd_results[str(step)][name] = {"finite_difference": fd, "residual_max": residual}
    observations["finite_difference"] = fd_results
    observations["FD_same_direction_step_sensitivity"] = {
        name: np.abs(fd_results[str(FD_STEPS[0])][name]["finite_difference"]
                     - fd_results[str(FD_STEPS[1])][name]["finite_difference"])
        for name in out["maps"]}

    off = join.evaluate(changed(state, lambda_source=0.0))
    nu0 = join.evaluate(changed(state, nu_s_inverse=0.0))
    empty = join.evaluate(changed(state, zeta=0.0, w_nt=0.0))
    charge = float(net.q @ Y)
    exhausted = join.evaluate(changed(state, zeta=charge, w_nt=charge * mean_energy))
    compare("source_off_photo_rows", off["photo_source"], np.zeros(25), np.zeros(25))
    compare("source_on_off_ions", F[:21] - off["source"][:21], out["P"],
            Fs[:21] + off["source_operand_scale"][:21] + np.abs(out["P"]))
    compare("zero_nu_transfer", [nu0["assimilation"]["j_per_baryon_s"], nu0["assimilation"]["h_J_per_baryon_s"]],
            [0.0, 0.0], [0.0, 0.0])
    compare("empty_fast_pool_transfer", [empty["assimilation"]["j_per_baryon_s"], empty["assimilation"]["h_J_per_baryon_s"]],
            [0.0, 0.0], [0.0, 0.0])
    compare("g_zero_RR_DR", exhausted["R"], np.zeros(21), np.zeros(21))
    compare("g_zero_Compton", exhausted["compton"]["q_J_per_baryon_s"], 0.0, 0.0)
    compare("g_zero_inward_number_transfer", net.q @ exhausted["source"][:21] - exhausted["source"][21],
            exhausted["assimilation"]["j_per_baryon_s"],
            np.abs(net.q) @ exhausted["source_operand_scale"][:21] + exhausted["source_operand_scale"][21]
            + exhausted["assimilation"]["j_per_baryon_s"])
    truth("g_zero_boundary_points_inward", exhausted["assimilation"]["j_per_baryon_s"] >= 0)
    Tr = out["compton"]["T_r_K"]
    equilibrium = compton_component(th["g"], Tr, nb, state["a"], dg=.1 * th["g"],
                                    dell=.04, da=.02 * state["a"])
    compare("standalone_native_Planck_equilibrium", equilibrium["q_J_per_baryon_s"], 0.0, 0.0)
    equilibrium_derivative = (4 * SIGMA_T_C_M3_S * KB_J_K / MEC2_J * th["g"]
                              * equilibrium["U_r_J_m3"] * (-.02 * Tr - .04 * Tr))
    compare("standalone_native_Planck_equilibrium_derivative", equilibrium["jvp"], equilibrium_derivative,
            equilibrium["jvp_operand_scale"])
    truth("equilibrium_derivative_is_nonzero", equilibrium["jvp"] != 0,
          atomic_routine_called=False, T_K=Tr)
    observations["boundaries"] = {
        "source_off": off["source"], "nu_zero": nu0["source"], "empty_fast_pool": empty["source"],
        "zero_thermal_electrons": exhausted["source"], "standalone_Planck_equilibrium": equilibrium}

    reject("reject_temperature_below_native_domain", lambda: join.evaluate(changed(state, T_K=99.0)))
    reject("reject_temperature_above_native_domain", lambda: join.evaluate(changed(state, T_K=1000001.0)))
    reject("reject_nonthermal_count_above_charge", lambda: join.evaluate(changed(state, zeta=charge * 1.01)))
    reject("reject_first_moment_above_support", lambda: join.evaluate(changed(state, w_nt=1.01 * EMAX_J * zeta)))
    reject("reject_energy_without_fast_number", lambda: join.evaluate(changed(state, zeta=0.0)))
    reject("reject_wrong_source_owner", lambda: ThermalJoin(net, native_coefficients, photo_owners=("wrong_owner",)))
    reject("reject_unselected_UV_Compton", lambda: ThermalJoin(net, native_coefficients, compton_branch="UV"))
    reject("reject_prompt_thermalization", lambda: ThermalJoin(net, native_coefficients, prompt_thermalization=True))
    reject("reject_reference_density_mismatch", lambda: join.evaluate(changed(state, nb_m3=1.01 * nb)))
    for index in (0, 5, 6):
        bad = changed(state)
        bad["Y"][index] = 1e-8
        bad["Y"][2] -= net.A[index] * 1e-8
        reject(f"reject_nuclear_population_{index}", lambda bad=bad: join.evaluate(bad))
        bad_direction = {**direction, "v": direction["v"].copy()}
        bad_direction["v"][index] = 1e-8
        reject(f"reject_nuclear_tangent_{index}", lambda bad_direction=bad_direction: join.evaluate(state, bad_direction))

    discriminators = {}
    for name in ("rr", "dr"):
        actual = out["recombination"][name]
        all_thermal = empty["recombination"][name]
        difference = all_thermal["R"] - actual["R"]
        expected = actual["R"] * zeta / th["g"]
        compare(name + "_all_electrons_discriminator_value", difference, expected,
                all_thermal["R_operand_scale"] + actual["R_operand_scale"]
                + actual["R_operand_scale"] * zeta / th["g"])
        truth(name + "_all_electrons_error_detected", bool(np.any(difference != 0)))
        discriminators[name + "_all_electrons_difference"] = difference
    Cdiff = empty["compton"]["q_J_per_baryon_s"] - out["compton"]["q_J_per_baryon_s"]
    Cexpected = out["compton"]["q_J_per_baryon_s"] * zeta / th["g"]
    compare("Compton_all_electrons_discriminator_value", Cdiff, Cexpected,
            abs(empty["compton"]["q_J_per_baryon_s"]) + abs(out["compton"]["q_J_per_baryon_s"]) + abs(Cexpected))
    truth("Compton_all_electrons_error_detected", Cdiff != 0)
    isolated = F[24] - nu0["source"][24]
    heat_only = out["assimilation"]["h_J_per_baryon_s"] / (CV * state["T_K"] * th["chi"])
    number_term = out["assimilation"]["j_per_baryon_s"] / th["chi"]
    compare("omitted_number_transfer_term", heat_only - isolated, number_term,
            abs(heat_only) + Fs[24] + nu0["source_operand_scale"][24] + abs(number_term))
    truth("heat_only_error_detected", number_term != 0)
    discriminators.update(Compton_all_electrons_difference=Cdiff,
                          assimilation_logT=isolated, heat_only_logT=heat_only,
                          missing_caloric_count_term=number_term)
    for name, factor, dfactor in (("physical", nb, direction["dnb"]), ("reference", beta, direction["dbeta"])):
        wrong_log = factor * F[24]
        truth(name + "_wrong_logT_density_multiplication_detected", wrong_log != F[24],
              correct=F[24], wrong=wrong_log)
        missing = out["maps"][name]["jvp"][:24] - factor * dF[:24]
        compare(name + "_omitted_product_derivative", missing, dfactor * F[:24],
                out["maps"][name]["jvp_operand_scale"][:24] + factor * dFs[:24]
                + abs(dfactor) * Fs[:24])
        truth(name + "_omitted_product_derivative_detected", bool(np.any(missing != 0)))
        discriminators[name + "_omitted_product_derivative"] = missing
    clock_missing = out["maps"]["eta"]["jvp"] - dF / H
    compare("omitted_clock_quotient_derivative", clock_missing, -F * direction["dH"] / H**2,
            out["maps"]["eta"]["jvp_operand_scale"] + dFs / H + Fs * abs(direction["dH"]) / H**2)
    truth("clock_quotient_error_detected", bool(np.any(clock_missing != 0)))
    truth("nu_is_an_independent_parameter", direction["dnu"] != direction["dH"],
          nu=state["nu_s_inverse"], H=H, dnu=direction["dnu"], dH=direction["dH"])
    discriminators["omitted_clock_quotient_derivative"] = clock_missing

    # Labeled alternative-reference algebra; not another background execution.
    S = out["maps"]["physical"]["source"][:24]
    dS = out["maps"]["physical"]["jvp"][:24]
    Rr = .03 * r * H
    dRr = .04 * Rr
    ref = changing_reference_control(S, x[:24], r, Rr, dS, dx[:24], direction["dr"], dRr)
    expected_ref = np.asarray([S[i] / r - x[i] * Rr / r for i in range(24)])
    expected_dref = np.asarray([dS[i] / r - S[i] * direction["dr"] / r**2
        - dx[i] * Rr / r - x[i] * dRr / r + x[i] * Rr * direction["dr"] / r**2 for i in range(24)])
    compare("general_physical_reference_quotient", ref["source"], expected_ref, ref["source_operand_scale"])
    compare("general_physical_reference_full_differential", ref["jvp"], expected_dref, ref["jvp_operand_scale"])
    omitted_ref = ref["source"] - S / r
    omitted_dref = ref["jvp"] - dS / r
    truth("reference_source_correction_error_detected", bool(np.any(omitted_ref != 0)))
    truth("reference_differential_correction_error_detected", bool(np.any(omitted_dref != 0)))
    observations["general_reference_control"] = {
        "scope": "manufactured_algebra_only_no_alternative_background", "Rr": Rr, "dRr": dRr,
        "x": x[:24], "dx": dx[:24], "S": S, "dS": dS, "r": r, "dr": direction["dr"],
        "result": ref, "missing_value_correction": omitted_ref, "missing_derivative_correction": omitted_dref}

    # Exact dimensionless two-measure witness: finite moment closure is conditional.
    mu1 = ((1.0, 2.0),)
    mu2 = ((.5, 1.0), (.5, 3.0))
    moments = lambda mu: (math.fsum(n for n, e in mu), math.fsum(n * e for n, e in mu))
    constant_transfers = lambda mu: moments(mu)
    variable_transfers = lambda mu: (math.fsum(n * e for n, e in mu), math.fsum(n * e * e for n, e in mu))
    compare("two_measures_same_N_U", moments(mu1), moments(mu2), [2.0, 4.0], limit=0.0)
    compare("constant_nu_same_transfer_moments", constant_transfers(mu1), constant_transfers(mu2), [2.0, 4.0], limit=0.0)
    truth("energy_dependent_nu_requires_another_moment", variable_transfers(mu1)[1] == 4.0
          and variable_transfers(mu2)[1] == 5.0,
          first=variable_transfers(mu1), second=variable_transfers(mu2))
    observations["two_measure_control"] = {"first": mu1, "second": mu2,
        "constant_rate": [constant_transfers(mu1), constant_transfers(mu2)],
        "energy_dependent_rate": [variable_transfers(mu1), variable_transfers(mu2)],
        "claim": "selected constant-in-energy closure only; no strong no-go"}
    observations["discriminators"] = discriminators
    observations["component_plot_data"] = {
        "power_unit": "W/m^3", "number_unit": "m^-3/s", "logT_unit": "s^-1",
        "photo_primary": nb * out["photo_source"][22],
        "assimilation_heat": nb * out["assimilation"]["h_J_per_baryon_s"],
        "RR_kinetic_loss": -nb * out["recombination"]["rr"]["L_J_per_baryon_s"],
        "DR_kinetic_loss": -nb * out["recombination"]["dr"]["L_J_per_baryon_s"],
        "Compton_CMB": nb * out["compton"]["q_J_per_baryon_s"],
        "net_thermal_power": nb * th["power_J_per_baryon_s"],
        "thermal_electron_density": th["ne_m3"], "all_electron_density": nb * charge,
        "thermal_number_source": nb * th["number_source_per_baryon_s"],
        "proper_logT_source": F[24], "heat_only_assimilation_logT": heat_only,
        "correct_assimilation_logT": isolated, "missing_particle_count_term": number_term}


if __name__ == "__main__":
    exit_code = 0
    trace = (OUT / "CHECKS.jsonl").open("x")
    try:
        main()
        status = "PASS_PENDING_INDEPENDENT_REVIEW"
        failure = None
    except Exception as error:
        exit_code = 1
        status = "FAIL_STOP_NO_AUTOMATIC_RETRY"
        failure = {"type": type(error).__name__, "message": str(error)}
        traceback.print_exc(file=sys.stderr)
    finally:
        trace.close()
    payload = {"status": status, "failure": failure, "checks": checks,
        "check_count": len(checks), "observations": observations,
        "scientific_execution": "one new conditional local source unit",
        "no_old_suite_replay": True, "no_IVP": True,
        "algebra_tolerance": ALG, "FD_tolerance": FD_TOL, "FD_steps": FD_STEPS,
        "requested_executor_role": "lower-tier mechanical implementation",
        "observed_executor": "inherited GPT-6 Astra Pro /root/rei_baseline_intake under agent-capacity recovery"}
    print(json.dumps(plain(payload), indent=2, allow_nan=False), flush=True)
    raise SystemExit(exit_code)
