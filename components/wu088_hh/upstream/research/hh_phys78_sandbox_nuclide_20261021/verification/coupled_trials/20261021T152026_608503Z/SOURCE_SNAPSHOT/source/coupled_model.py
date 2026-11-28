"""Exploratory finite atomic/gray-radiation LRS Bianchi-I initial-value model.

The separately prepared collisionless matter/radiation moments source the
signed shear in one orthonormal normal frame. Reacting baryons and gray UV/
recombination escape radiation use explicit isotropic fluid closures. Source
photons draw their energy from a pressureless reservoir included in gravity.
No rate, source-history, angular/momentum continuum or production admission
follows from the sampled algebraic checks performed here. HH_R10 remains OFF.

Independent variable x=ln(a/a0), a0=1/21; proper-second rates enter divided by H.
The 33 physical state entries are [b,q=s/Href,Y21,u,N3,U3,R,Q,tau=H0*t].
u,U,R,Q are eV/reference-H; N is photon number/reference-H. The free electron
abundance is derived from charge neutrality. No accepted state is clipped.
"""
from __future__ import annotations

import os
for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                         "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_variable] = "1"

import math
import time
from typing import Mapping

import numpy as np
from scipy.constants import G, c, m_p, parsec
from scipy.integrate import solve_ivp
from scipy.special import expit

import atomic_network as atomic

H0 = 67.4*1000./(1e6*parsec)
OMEGA_M, OMEGA_B, OMEGA_R = .315, .0493, 9.2e-5
OMEGA_LAMBDA = 1.-OMEGA_M-OMEGA_R
OMEGA_WARM = .1*OMEGA_M
OMEGA_COLD = OMEGA_M-OMEGA_B-OMEGA_WARM
A0 = 1./21.
X_END = math.log(7.)
HREF = H0*math.sqrt(OMEGA_M/A0**3+OMEGA_R/A0**4+OMEGA_LAMBDA)
RHO_CRIT_J_M3 = 3*H0**2*c*c/(8*math.pi*G)
PROTON_REST_EV = m_p*c*c/atomic.EV_J
SOURCE_ENERGY_EV = np.array([18., 30., 60.])
SOURCE_WEIGHTS = np.array([.7, .25, .05])
DEFAULT_RTOL = 2e-7
DEFAULT_RESOLUTION = {"mass_over_Tref": 30., "radial_cells": 12,
                      "angular_cells": 12, "gauss_order": 3, "rad_ang_order": 32}

I_B, I_Q = 0, 1
S_Y = slice(2, 23)
I_U = 23
S_N = slice(24, 27)
S_U = slice(27, 30)
I_R, I_RESERVOIR, I_TAU = 30, 31, 32
N_STATE = 33

# Declared before any science run. These guard numerical stages/saved states;
# they are not an alternative scientific tolerance or state projection.
STAGE_NEGATIVE_ISOTOPE_RELATIVE = 1e-8
SAVED_NEGATIVE_ISOTOPE_RELATIVE = 2e-9
# Dormant n/T coordinates have zero physical inventories. BDF dense solves can
# introduce signed roundoff even when their exact derivatives vanish. These
# bounds only govern numerical acceptance; the raw values are never projected.
STAGE_ABSENT_ISOTOPE_ABSOLUTE = 1e-28
SAVED_ABSENT_ISOTOPE_ABSOLUTE = 1e-28
SAVED_ISOTOPE_CONSERVATION_RELATIVE = 1e-8
SAMPLED_ENERGY_IDENTITY_RELATIVE = 2e-11


class CoupledModel:
    def __init__(self, case: Mapping, resolution=None, *, kinetic_model=None):
        required = ("sigma0_F_signed", "A_m", "A_r", "uv_scale")
        missing = [name for name in required if name not in case]
        if missing:
            raise ValueError("MISSING_CASE_FIELDS:" + ",".join(missing))
        self.case = dict(case)
        for key in required:
            self.case[key] = float(case[key])
            if not math.isfinite(self.case[key]):
                raise ValueError("NONFINITE_CASE_FIELD:" + key)
        if not abs(self.case["sigma0_F_signed"]) < math.sqrt(6.):
            raise ValueError("INITIAL_SHEAR_HAMILTONIAN_DOMAIN")
        if not (-1 <= self.case["A_m"] <= 2 and -1 <= self.case["A_r"] <= 2):
            raise ValueError("NEGATIVE_ANGULAR_DISTRIBUTION")
        if self.case["uv_scale"] < 0:
            raise ValueError("NEGATIVE_UV_SOURCE")
        self.resolution = dict(DEFAULT_RESOLUTION)
        if resolution is not None:
            if not isinstance(resolution, Mapping) or set(resolution)-set(DEFAULT_RESOLUTION):
                raise ValueError("UNKNOWN_KINETIC_RESOLUTION")
            self.resolution.update(resolution)
        if kinetic_model is None:
            from kinetic import PreparedKinetic
            kinetic_model = PreparedKinetic(self.case["A_m"], self.case["A_r"],
                                             **self.resolution)
        self.kinetic = kinetic_model
        self.atomic = atomic.prepare_network(SOURCE_ENERGY_EV)
        self.initial_Y = atomic.neutral_abundances()
        hii = float(case.get("HII_initial", 2e-4))
        if not math.isfinite(hii) or not 0 <= hii <= 1:
            raise ValueError("INVALID_INITIAL_HII_FRACTION")
        self.initial_Y[atomic.SPECIES_INDEX["H1_I"]] -= hii
        self.initial_Y[atomic.SPECIES_INDEX["H1_II"]] += hii
        self.isotope_totals = atomic.ISOTOPE_SUM @ self.initial_Y
        self.isotope_scales = atomic.ISOTOPE_SUM.T @ self.isotope_totals
        self.stage_scales = np.where(
            self.isotope_scales > 0, self.isotope_scales,
            STAGE_ABSENT_ISOTOPE_ABSOLUTE/STAGE_NEGATIVE_ISOTOPE_RELATIVE)
        # A fixed diagonal coordinate change removes the 14-decade isotope
        # inventory contrast from BDF's Newton matrix. It changes neither the
        # physical IVP nor its componentwise absolute error tolerances.
        self.solver_scales = np.ones(N_STATE)
        self.solver_scales[S_Y] = self.stage_scales
        self.nucleons_per_H = float(atomic.MASS_NUMBER @ self.initial_Y)
        self.rest_energy_per_H = PROTON_REST_EV*self.nucleons_per_H
        # nH0 is the present-day reference-H proper density. m_p*A is the
        # explicitly chosen common rest-mass normalization; no isotope defects.
        self.nH0_cm3 = OMEGA_B*RHO_CRIT_J_M3/(m_p*c*c*self.nucleons_per_H)/1e6
        self.initial_temperature = float(case.get("T_initial_K", 300.))
        if not 3 <= self.initial_temperature <= 1e9:
            raise ValueError("INITIAL_TEMPERATURE_OUTSIDE_RR_DOMAIN")
        self.initial_reservoir = float(case.get("reservoir_initial_eV_per_H", 1000.))
        if not math.isfinite(self.initial_reservoir) or self.initial_reservoir <= 0:
            raise ValueError("INVALID_INITIAL_RESERVOIR")
        self.initial_photons = float(case.get("photon_initial_per_H", 1e-10))
        if not math.isfinite(self.initial_photons) or self.initial_photons <= 0:
            raise ValueError("INITIAL_GRAY_PHOTONS_MUST_BE_POSITIVE")
        self.rhs_calls = 0
        self.last_x = None
        self.last_state = None
        self.negative_stage_count = 0
        self.rejected_domain_stage_count = 0
        self.last_rejected_domain = None
        self.initial_state = self._initial_state()

    def _initial_state(self):
        y = np.zeros(N_STATE)
        y[S_Y] = self.initial_Y
        particle_count = float(self.initial_Y.sum()+atomic.CHARGE@self.initial_Y)
        y[I_U] = 1.5*atomic.KB_EV_K*self.initial_temperature*particle_count
        y[S_N] = self.initial_photons
        y[S_U] = self.initial_photons*SOURCE_ENERGY_EV
        y[I_RESERVOIR] = self.initial_reservoir
        env = self.environment(0., y)
        sigma = self.case["sigma0_F_signed"]
        y[I_Q] = sigma/math.sqrt(6.-sigma*sigma)*env["H"]/HREF
        return y

    def absolute_tolerances(self, rtol=DEFAULT_RTOL):
        """Trace nuclei retain relative fractional abundance resolution."""
        # Scale all absolute tolerances with requested rtol so a tight control
        # genuinely changes both parts of the numerical error controller.
        ratio = float(rtol)/DEFAULT_RTOL
        out = np.full(N_STATE, 1e-11)
        out[S_Y] = np.where(self.isotope_scales > 0, self.isotope_scales*1e-10, 1e-28)
        out[I_U] = 1e-9
        out[S_N] = 1e-14
        out[S_U] = 1e-13
        out[I_R] = 1e-10
        out[I_RESERVOIR] = 1e-6
        out[I_TAU] = 1e-10
        return ratio*out

    def source_per_x(self, x):
        z = 21.*math.exp(-float(x))-1.
        amplitude = self.case["uv_scale"]*8.*float(expit((8.-z)/1.5))
        return amplitude*SOURCE_WEIGHTS

    def environment(self, x, state):
        state = np.asarray(state, dtype=float)
        if state.shape != (N_STATE,) or not np.isfinite(state).all():
            raise ValueError("COUPLED_STATE_SHAPE_OR_NONFINITE")
        x = float(x)
        if not math.isfinite(x):
            raise ValueError("NONFINITE_TIME")
        b, q = state[I_B], state[I_Q]
        y, u = state[S_Y], state[I_U]
        if u <= 0 or state[I_RESERVOIR] < 0:
            raise ValueError("NONPOSITIVE_GAS_ENERGY_OR_DEPLETED_SOURCE_RESERVOIR")
        particles = float(y.sum()+atomic.CHARGE@y)
        if particles <= 0:
            raise ValueError("NONPOSITIVE_GAS_PARTICLE_COUNT")
        temperature = 2.*u/(3.*atomic.KB_EV_K*particles)
        a = A0*math.exp(x)
        nH = self.nH0_cm3/a**3
        ev_norm = nH*1e6*atomic.EV_J/RHO_CRIT_J_M3
        moments = self.kinetic.moments(x, b)
        warm_pref = OMEGA_WARM/A0**3
        rad_pref = OMEGA_R/A0**4
        rho_warm, p_warm, pi_warm = (warm_pref*float(moments[k])
                                      for k in ("rho_m", "pbar_m", "pi_m"))
        rho_free, p_free, pi_free = (rad_pref*float(moments[k])
                                      for k in ("rho_r", "pbar_r", "pi_r"))
        binding = float(self.atomic.binding_eV @ y)
        gas = ev_norm*(self.rest_energy_per_H+u+binding+state[I_RESERVOIR])
        gray_energy = float(state[S_U].sum()+state[I_R])
        gray = ev_norm*gray_energy
        p_isotropic = ev_norm*(2.*u+gray_energy)/3.
        cold = OMEGA_COLD/a**3
        rho = cold+rho_warm+rho_free+gas+gray
        s = HREF*q
        h2 = H0*H0*(rho+OMEGA_LAMBDA)+s*s
        if not math.isfinite(h2) or h2 <= 0 or rho < 0:
            raise ValueError("INVALID_FRIEDMANN_SOURCE")
        H = math.sqrt(h2)
        return {"a": a, "z": 1/a-1, "nH_cm3": nH, "eV_density_norm": ev_norm,
                "T_K": temperature, "particles_per_H": particles, "H": H,
                "s": s, "s_over_H": s/H, "rho_total": rho,
                "rho_cold": cold, "rho_baryon": gas, "rho_m_kinetic": rho_warm,
                "rho_r_free": rho_free, "rho_gray": gray,
                "pbar_total": p_warm+p_free+p_isotropic,
                "pi_m": pi_warm, "pi_r": pi_free, "binding_eV_per_H": binding}

    def evaluate(self, x, state, *, allow_solver_extension=True):
        env = self.environment(x, state)
        y = np.asarray(state, dtype=float)
        numbers, energies = y[S_N], y[S_U]
        if np.any(numbers <= 0) or np.any(energies <= 0):
            raise ValueError("GRAY_PHOTON_NUMBER_OR_ENERGY_NONPOSITIVE")
        mean_energy = energies/numbers
        point = self.atomic.rhs(
            env["T_K"], env["nH_cm3"], y[S_Y], env["nH_cm3"]*numbers,
            photon_energy_eV=mean_energy,
            allow_solver_extension=allow_solver_extension,
            solver_extension_relative_tolerance=STAGE_NEGATIVE_ISOTOPE_RELATIVE,
            solver_extension_scale_per_H=self.stage_scales)
        source = self.source_per_x(x)
        invh = 1./env["H"]
        out = np.empty(N_STATE)
        out[I_B] = env["s_over_H"]
        out[I_Q] = -3.*y[I_Q]+3.*H0**2*(env["pi_m"]+env["pi_r"])/(env["H"]*HREF)
        out[S_Y] = point.dsdt*invh
        out[I_U] = -2.*y[I_U]+point.heat_eV_per_H_s*invh
        out[S_N] = source-point.photon_absorption_per_H_s*invh
        out[S_U] = -energies+SOURCE_ENERGY_EV*source-mean_energy*point.photon_absorption_per_H_s*invh
        out[I_R] = -y[I_R]+point.rr_escape_eV_per_H_s*invh
        out[I_RESERVOIR] = -float(SOURCE_ENERGY_EV @ source)
        out[I_TAU] = H0*invh
        if not np.isfinite(out).all():
            raise ArithmeticError("NONFINITE_COUPLED_RHS")
        # Local source/atomic/gray exchange identity. The expansion terms are
        # evaluated separately to avoid rest-mass and Hubble-rate cancellation.
        exchange = (out[I_U]+self.atomic.binding_eV@out[S_Y]+out[S_U].sum()
                    +out[I_R]+out[I_RESERVOIR]+2.*y[I_U]+energies.sum()+y[I_R])
        scale = (abs(out[I_U])+abs(self.atomic.binding_eV@out[S_Y])
                 +float(np.abs(out[S_U]).sum())+abs(out[I_R])+abs(out[I_RESERVOIR])
                 +2.*abs(y[I_U])+float(np.abs(energies).sum())+abs(y[I_R]))
        energy_relative = 0. if scale == 0 else float(exchange/scale)
        env.update({"atomic": point, "UV_mean_eV": mean_energy,
                    "energy_balance_rel": energy_relative,
                    "energy_balance_abs_eV_per_H_x": float(exchange),
                    "source_per_H_x": source})
        return out, env

    def rhs(self, x, state):
        self.rhs_calls += 1
        self.last_x, self.last_state = float(x), np.asarray(state).copy()
        if np.any(np.asarray(state)[S_Y] < 0):
            self.negative_stage_count += 1
        return self.evaluate(x, state, allow_solver_extension=True)[0]

    def solver_rhs(self, x, scaled_state):
        """Exact scaled coordinates; reject invalid Newton trial states.

        SciPy BDF treats a nonfinite trial RHS as a failed Newton solve and
        reduces/retries the step. Only enumerated physical-domain exceptions
        take this route. No rejected state is clipped or accepted. Public
        evaluate/rhs and the saved-state postflight remain strict.
        """
        try:
            return self.rhs(x, np.asarray(scaled_state)*self.solver_scales)/self.solver_scales
        except ValueError as error:
            message = str(error)
            prefixes = (
                "NONPOSITIVE_GAS_ENERGY_OR_DEPLETED_SOURCE_RESERVOIR",
                "NONPOSITIVE_GAS_PARTICLE_COUNT", "INVALID_FRIEDMANN_SOURCE",
                "GRAY_PHOTON_NUMBER_OR_ENERGY_NONPOSITIVE",
                "SOLVER_EXTENSION_NEGATIVITY_BOUND_EXCEEDED",
                "NEGATIVE_DERIVED_ELECTRON_DENSITY",
                "RR_TEMPERATURE_OUTSIDE_3_TO_1E9_K", "PHOTO_FIT_EMAX_EXCEEDED:",
                "DYNAMIC_PHOTON_ENERGY_SHAPE_OR_DOMAIN",
                "COUPLED_STATE_SHAPE_OR_NONFINITE", "outside finite kinetic chart")
            if not message.startswith(prefixes):
                raise
            self.rejected_domain_stage_count += 1
            self.last_rejected_domain = {"x": float(x), "reason": message}
            return np.full(N_STATE, np.nan)

    def arrays(self, x, states):
        """Return time-leading arrays and preserve every raw saved state."""
        x = np.asarray(x, dtype=float)
        states = np.asarray(states, dtype=float)
        if states.shape != (len(x), N_STATE):
            raise ValueError("HISTORY_SHAPE")
        entries = [self.evaluate(t, y, allow_solver_extension=True)[1]
                   for t, y in zip(x, states)]
        values = lambda name: np.array([d[name] for d in entries])
        h = values("H")
        signed_m = math.sqrt(6.)*3*H0**2*values("pi_m")/h**2
        signed_r = math.sqrt(6.)*3*H0**2*values("pi_r")/h**2
        signed_total = signed_m+signed_r
        ratio = values("s_over_H")
        isotope = states[:, S_Y] @ atomic.ISOTOPE_SUM.T
        rel_errors = np.zeros_like(isotope)
        nonzero = self.isotope_totals > 0
        rel_errors[:, nonzero] = (isotope[:, nonzero]-self.isotope_totals[nonzero])/self.isotope_totals[nonzero]
        rel_errors[:, ~nonzero] = isotope[:, ~nonzero]  # absent slots use absolute zero.
        out = {
            "x": x, "z": values("z"), "b": states[:, I_B], "q": states[:, I_Q],
            "s_over_H": ratio, "signed_Sigma_F": math.sqrt(6.)*ratio,
            "Sigma_F": math.sqrt(6.)*np.abs(ratio),
            "Pi_m_F": np.abs(signed_m), "Pi_r_F": np.abs(signed_r),
            "Pi_total_F": np.abs(signed_total),
            "signed_Pi_m_F": signed_m, "signed_Pi_r_F": signed_r,
            "signed_Pi_total_F": signed_total,
            "Sigma_half": math.sqrt(3.)*np.abs(ratio),
            "Pi_m_half": np.abs(signed_m)/math.sqrt(2.),
            "Pi_r_half": np.abs(signed_r)/math.sqrt(2.),
            "Pi_total_half": np.abs(signed_total)/math.sqrt(2.),
            "H_per_s": h, "T_K": values("T_K"),
            "xe": np.array([d["atomic"].electron_abundance_per_H for d in entries]),
            "Y": states[:, S_Y], "species_names": np.array(atomic.SPECIES_NAMES),
            "rho_baryon": values("rho_baryon"),
            "rho_m_kinetic": values("rho_m_kinetic"), "rho_r_free": values("rho_r_free"),
            "rho_gray": values("rho_gray"), "rho_total": values("rho_total"),
            "pbar_total": values("pbar_total"),
            "UV_mean_eV": values("UV_mean_eV"), "UV_N_perH": states[:, S_N],
            "UV_U_eV_perH": states[:, S_U], "gas_u_eV_perH": states[:, I_U],
            "escape_R_eV_perH": states[:, I_R], "reservoir_Q_eV_perH": states[:, I_RESERVOIR],
            "binding_eV_perH": values("binding_eV_per_H"),
            "energy_balance_rel": values("energy_balance_rel"),
            "energy_balance_abs_eV_per_H_x": values("energy_balance_abs_eV_per_H_x"),
            "nuclei_rel_error": np.max(np.abs(rel_errors), axis=1),
            "isotope_rel_error": rel_errors, "isotope_names": np.array(atomic.ISOTOPES),
            "nH_cm3": values("nH_cm3"), "elapsed_seconds": states[:, I_TAU]/H0,
            "raw_states": states,
        }
        for name in ("rho_baryon", "rho_m_kinetic", "rho_r_free", "rho_gray", "rho_total"):
            out[name+"_J_m3"] = out[name]*RHO_CRIT_J_M3
        return out

    def postflight(self, arrays):
        for key, val in arrays.items():
            if np.asarray(val).dtype.kind in "fc" and not np.isfinite(val).all():
                raise ArithmeticError("NONFINITE_OUTPUT:" + key)
        y = arrays["Y"]
        bound = np.where(self.isotope_scales > 0,
                         SAVED_NEGATIVE_ISOTOPE_RELATIVE*self.isotope_scales,
                         SAVED_ABSENT_ISOTOPE_ABSOLUTE)
        if np.any(y < -bound[None, :]):
            raise ArithmeticError("SAVED_SPECIES_NEGATIVITY_BOUND_EXCEEDED")
        absent = self.isotope_totals == 0
        if np.any(np.abs(arrays["isotope_rel_error"][:, absent])
                  > SAVED_ABSENT_ISOTOPE_ABSOLUTE):
            raise ArithmeticError("SAVED_ABSENT_ISOTOPE_ABSOLUTE_BOUND_EXCEEDED")
        if np.any(arrays["UV_N_perH"] <= 0) or np.any(arrays["UV_U_eV_perH"] <= 0):
            raise ArithmeticError("SAVED_PHOTON_NONPOSITIVITY")
        if (np.any(arrays["reservoir_Q_eV_perH"] < 0)
                or np.any(arrays["gas_u_eV_perH"] <= 0)
                or np.any(arrays["escape_R_eV_perH"] < -1e-10)):
            raise ArithmeticError("SAVED_GAS_RESERVOIR_OR_ESCAPE_ENERGY_DOMAIN")
        if np.max(arrays["nuclei_rel_error"]) > SAVED_ISOTOPE_CONSERVATION_RELATIVE:
            raise ArithmeticError("SAVED_ISOTOPE_CONSERVATION_FAILED")
        if np.max(np.abs(arrays["energy_balance_rel"])) > SAMPLED_ENERGY_IDENTITY_RELATIVE:
            raise ArithmeticError("SAMPLED_ENERGY_EXCHANGE_IDENTITY_FAILED")
        if abs(arrays["z"][0]-20) > 1e-12 or abs(arrays["z"][-1]-2) > 1e-12:
            raise ArithmeticError("INCOMPLETE_REDSHIFT_RANGE")
        if abs(arrays["signed_Sigma_F"][0]-self.case["sigma0_F_signed"]) > 2e-13:
            raise ArithmeticError("INITIAL_SHEAR_AXIS_MISMATCH")
        return {"finite": True, "redshift_range": [float(arrays["z"][0]), float(arrays["z"][-1])],
                "max_isotope_relative_error": float(np.max(arrays["nuclei_rel_error"])),
                "max_sampled_energy_identity_relative": float(np.max(np.abs(arrays["energy_balance_rel"]))),
                "minimum_species_abundance_per_H": float(np.min(y)),
                "minimum_photon_number_per_H": float(np.min(arrays["UV_N_perH"])),
                "minimum_reservoir_eV_per_H": float(np.min(arrays["reservoir_Q_eV_perH"])),
                "temperature_range_K": [float(np.min(arrays["T_K"])), float(np.max(arrays["T_K"]))],
                "maximum_initial_axis_error": float(abs(arrays["signed_Sigma_F"][0]-self.case["sigma0_F_signed"]))}


def solve_case(case, rtol=DEFAULT_RTOL, resolution=None, samples=161):
    """One bounded scientific IVP; persistence/resume belongs to the caller."""
    rtol = float(rtol)
    if not math.isfinite(rtol) or not 1e-10 <= rtol <= 1e-4:
        raise ValueError("RTOL_OUTSIDE_BOUNDED_EXPLORATORY_RANGE")
    if not isinstance(samples, int) or not 3 <= samples <= 2001:
        raise ValueError("INVALID_SAVED_SAMPLE_COUNT")
    model = CoupledModel(case, resolution)
    start = time.monotonic()
    sol = solve_ivp(model.solver_rhs, (0., X_END), model.initial_state/model.solver_scales,
                    method="BDF", rtol=rtol, atol=model.absolute_tolerances(rtol)/model.solver_scales,
                    t_eval=np.linspace(0., X_END, samples), max_step=.04)
    wall = time.monotonic()-start
    if not sol.success or len(sol.t) != samples:
        raise RuntimeError("COUPLED_BDF_INCOMPLETE:" + sol.message)
    arrays = model.arrays(sol.t, sol.y.T*model.solver_scales)
    checks = model.postflight(arrays)
    meta = {
        "status": "COMPLETED_EXPLORATORY", "case": model.case,
        "model_scope": "FINITE_COLLISIONLESS_DM_RADIATION_ISOTROPIC_PI_RR_GAS_GRAY_UV",
        "method": "BDF", "rtol": rtol, "atol": model.absolute_tolerances(rtol).tolist(),
        "max_step_x": .04, "samples": samples, "resolution": model.resolution,
        "nfev": int(sol.nfev), "njev": int(sol.njev), "nlu": int(sol.nlu),
        "rhs_calls_including_jacobian": model.rhs_calls,
        "negative_solver_stage_evaluations": model.negative_stage_count,
        "rejected_domain_stage_evaluations": model.rejected_domain_stage_count,
        "last_rejected_domain_stage": model.last_rejected_domain,
        "solver_coordinate_scale": model.solver_scales.tolist(),
        "solver_coordinate_convention": "fixed diagonal scale; raw physical state equals scale times BDF state",
        "solve_wall_s": wall, "checks": checks,
        "constants": {"H0_per_s": H0, "Href_per_s": HREF, "rho_crit_J_m3": RHO_CRIT_J_M3,
                      "Omega_m": OMEGA_M, "Omega_b": OMEGA_B, "Omega_r": OMEGA_R,
                      "Omega_lambda": OMEGA_LAMBDA, "Omega_warm": OMEGA_WARM,
                      "G_SI": G, "c_m_s": c, "proton_mass_kg": m_p,
                      "nH0_cm3": model.nH0_cm3, "rest_mass_convention": "m_p times nuclear A"},
        "initial_conditions": {"T_K": model.initial_temperature,
                               "Y": model.initial_Y.tolist(),
                               "reservoir_eV_per_H": model.initial_reservoir,
                               "photon_numbers_per_H": [model.initial_photons]*3,
                               "photon_energy_eV": SOURCE_ENERGY_EV.tolist()},
        "numerical_domains": {"stage_negative_isotope_relative": STAGE_NEGATIVE_ISOTOPE_RELATIVE,
                              "saved_negative_isotope_relative": SAVED_NEGATIVE_ISOTOPE_RELATIVE,
                              "stage_absent_isotope_absolute_per_H": STAGE_ABSENT_ISOTOPE_ABSOLUTE,
                              "saved_absent_isotope_absolute_per_H": SAVED_ABSENT_ISOTOPE_ABSOLUTE,
                              "saved_isotope_conservation_relative": SAVED_ISOTOPE_CONSERVATION_RELATIVE,
                              "sampled_energy_identity_relative": SAMPLED_ENERGY_IDENTITY_RELATIVE},
        "array_units": {"rho_baryon": "rho_crit,0", "rho_m_kinetic": "rho_crit,0",
                        "rho_r_free": "rho_crit,0", "Y": "n_species/n_Hreference",
                        "raw_states": "[b,s/Href,Y21,u_eV/H,N3/H,U3_eV/H,R_eV/H,Q_eV/H,H0*t]"},
        "frame": "comoving orthonormal normal frame; sigma=diag(-s,-s,2s); pi_A=diag(-p_A,-p_A,2p_A)",
        "norm": "Frobenius; half-contraction columns smaller by sqrt(2)",
        "energy_check_scope": "SAMPLED_INSTANTANEOUS_EXCHANGE_IDENTITY_NOT_CONTINUUM_CERTIFICATE",
        "omitted_channels": ["CI", "DR", "CX", "CE", "free-free", "Compton", "molecules",
                             "nuclear", "beta_decay", "Thomson_angular_collision"],
        "gas_stress_closure": "isotropic pi_gas=0", "HH_R10": "OFF",
        "production_admission": False,
    }
    return arrays, meta
