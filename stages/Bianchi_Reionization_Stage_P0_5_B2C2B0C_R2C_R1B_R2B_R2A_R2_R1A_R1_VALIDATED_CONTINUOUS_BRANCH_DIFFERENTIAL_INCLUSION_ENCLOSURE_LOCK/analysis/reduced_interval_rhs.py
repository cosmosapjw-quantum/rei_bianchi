"""Directed-rounding interval extension of the reduced H/He/thermal RHS.

The internal state coordinates are
``(x_HI, x_HeI, r_HeIII, log_T)`` with

``q_He_ion = x_HeII + x_HeIII`` and
``r_HeIII = x_HeIII / q_He_ion``.

The two small neutral reservoirs are represented directly, together with the
conditional He III fraction.  This avoids both the ``(1-x)^{-1}`` amplification
of a near-unit logit and the division by a tiny neutral fraction in a log
coordinate.  The triangular parameterization preserves the helium simplex
structurally:
``x_HeI=1-q``, ``x_HeII=q(1-r)``, ``x_HeIII=q r``.  Independent boxes in
``(x_HeII,x_HeIII)`` lose their anticorrelation and can create a spurious
negative He I lower bound during interval propagation.  H and He nuclei totals
are immutable, so the two conservation laws remain structural rather than
numerical constraints.  The resolved owner currents use the analytic
cancellation of their global species measure; the subgrid node distribution
never enters this material RHS because its resolved H/He/thermal source is an
exact structural zero.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path) -> Any:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


iv = _load("r2_r1a_r1_interval_arithmetic", HERE / "interval_arithmetic.py")
pbounds = _load("r2_r1a_r1_pchip_bounds", HERE / "pchip_bounds.py")

KB_ERG = 1.380649e-16
EV_ERG = 1.602176634e-12
MPC_CM = 3.085677581491367e24
NH0_CM3 = 1.88e-7
YHE = 0.079
H0 = 67.4 * 1.0e5 / MPC_CM
OMEGA_M = 0.315
OMEGA_L = 0.685

CHI_H_EV = 13.598434599702
CHI_HEI_EV = 24.587389011
CHI_HEII_EV = 54.417760
HEII_LYA_EV = 0.75 * CHI_HEII_EV
ELL = 1.425
M_CAS = 0.737
P_EXC = 0.96

SIGMA_OTS_H24 = 1.2391519584513023e-18
SIGMA_OTS_HEI24 = 7.43469869411065e-18
SIGMA_OTS_H41 = 2.884642817876362e-19
SIGMA_OTS_HEI41 = 3.0402144676144673e-18
SIGMA_OTS_H54 = 1.2306959247142394e-19
SIGMA_OTS_HEI54 = 1.6907806870529807e-18
SIGMA_OTS_HEII54 = 1.5872802575386495e-18

GROUPS = ("G1", "G2a", "G2b", "G3")


@dataclass(frozen=True)
class ForcingBounds:
    current: tuple[iv.Interval, ...]
    external_subgrid: tuple[iv.Interval, ...]
    z: iv.Interval
    gamma_hi: iv.Interval
    hubble_s_inv: iv.Interval
    volume_cm3: iv.Interval


@dataclass(frozen=True)
class IntervalRHSResult:
    rhs: iv.Interval
    population_rhs: tuple[iv.Interval, ...]
    photo_hi: iv.Interval
    photo_hei: iv.Interval
    photo_heii: iv.Interval
    resolved_photoheat: iv.Interval
    unresolved_ots_energy_rate: iv.Interval
    escaped_ots_energy_rate: iv.Interval
    branch_A_H: iv.Interval
    branch_A_HeI: iv.Interval


def _zero(shape) -> iv.Interval:
    return iv.Interval(np.zeros(shape, dtype=np.float64))


def _point_sigmoid(x: np.ndarray) -> np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    out = np.empty_like(values)
    nonnegative = values >= 0.0
    out[nonnegative] = 1.0 / (1.0 + np.exp(-values[nonnegative]))
    expx = np.exp(values[~nonnegative])
    out[~nonnegative] = expx / (1.0 + expx)
    return out


def _sigmoid(x: iv.Interval) -> iv.Interval:
    """Monotone, outward-rounded logistic map.

    Evaluating the endpoint map directly is materially tighter near fully
    ionized states than composing generic interval ``exp`` and reciprocal
    primitives.  Monotonicity makes the endpoint enclosure exact up to one
    binary64 outward step.
    """

    return iv.Interval(
        np.nextafter(_point_sigmoid(x.lo), -np.inf),
        np.nextafter(_point_sigmoid(x.hi), np.inf),
    )


def _logit(x: np.ndarray) -> np.ndarray:
    values = np.asarray(x, dtype=np.float64)
    if np.any((values <= 0.0) | (values >= 1.0)):
        raise ValueError("logit input must lie strictly in (0,1)")
    return np.log(values) - np.log1p(-values)


def _alpha_b_hii(T: iv.Interval) -> iv.Interval:
    ll = 315614.0 / T
    return 2.753e-14 * iv.pow_const(ll, 1.5) / iv.pow_const(1.0 + iv.pow_const(ll / 2.740, 0.407), 2.242)


def _alpha_a_heii(T: iv.Interval) -> iv.Interval:
    ll = 570670.0 / T
    base = 3.0e-14 * iv.pow_const(ll, 0.654)
    dr = 1.9e-3 * iv.pow_const(T, -1.5) * iv.exp(-473638.0 / T) * (1.0 + 0.3 * iv.exp(-94728.0 / T))
    return base + _sigmoid((T - 1.5e4) / 250.0) * dr


def _alpha_b_heii(T: iv.Interval) -> iv.Interval:
    ll = 570670.0 / T
    base = 1.26e-14 * iv.pow_const(ll, 0.750)
    dr = 1.9e-3 * iv.pow_const(T, -1.5) * iv.exp(-473638.0 / T) * (1.0 + 0.3 * iv.exp(-94728.0 / T))
    return base + _sigmoid((T - 1.5e4) / 250.0) * dr


def _alpha_a_heiii(T: iv.Interval) -> iv.Interval:
    ll = 1263030.0 / T
    return 2.0 * 1.269e-13 * iv.pow_const(ll, 1.503) / iv.pow_const(1.0 + iv.pow_const(ll / 0.522, 0.470), 1.923)


def _alpha_b_heiii(T: iv.Interval) -> iv.Interval:
    ll = 1263030.0 / T
    return 2.0 * 2.753e-14 * iv.pow_const(ll, 1.5) / iv.pow_const(1.0 + iv.pow_const(ll / 2.740, 0.407), 2.242)


def _alpha_heiii_n2(T: iv.Interval) -> iv.Interval:
    return 3.4e-13 * iv.pow_const(T / 1.0e4, -0.6)


def _beta_hi(T: iv.Interval) -> iv.Interval:
    return 5.835e-11 * iv.sqrt(T) * iv.exp(-157804.0 / T)


def _beta_hei(T: iv.Interval) -> iv.Interval:
    return 2.71e-11 * iv.sqrt(T) * iv.exp(-285331.0 / T)


def _beta_heii(T: iv.Interval) -> iv.Interval:
    return 5.707e-12 * iv.sqrt(T) * iv.exp(-631495.0 / T)


def _multi_affine_branches(v: iv.Interval, f: iv.Interval, y: iv.Interval, z: iv.Interval) -> tuple[iv.Interval, iv.Interval]:
    ah_values = []
    ahe_values = []
    for vv in (v.lo, v.hi):
        for ff in (f.lo, f.hi):
            for yy in (y.lo, y.hi):
                for zz in (z.lo, z.hi):
                    w = (ELL - M_CAS) + M_CAS * yy
                    ah_values.append(vv * w + (1.0 - vv) * ff * zz)
                    ahe_values.append(vv * M_CAS * (1.0 - yy) + (1.0 - vv) * ff * (1.0 - zz))
    ah = np.stack(ah_values, axis=0)
    ahe = np.stack(ahe_values, axis=0)
    return (
        iv.Interval(np.nextafter(np.min(ah, axis=0), -np.inf), np.nextafter(np.max(ah, axis=0), np.inf)),
        iv.Interval(np.nextafter(np.min(ahe, axis=0), -np.inf), np.nextafter(np.max(ahe, axis=0), np.inf)),
    )


class ReducedIntervalModel:
    def __init__(self, *, repo_root: Path, inputs, forcing, solver, thermal, policy, event, excess_eV: np.ndarray) -> None:
        self.repo_root = Path(repo_root)
        self.inputs = inputs
        self.forcing = forcing
        self.solver = solver
        self.thermal = thermal
        self.policy = policy
        self.event = event
        self.excess_eV = np.asarray(excess_eV, dtype=np.float64)
        self.n_h = np.asarray(inputs.state0.values[0] + inputs.state0.values[1], dtype=np.float64)
        self.n_he = np.asarray(inputs.state0.values[2] + inputs.state0.values[3] + inputs.state0.values[4], dtype=np.float64)
        self.n_h_total = float(np.sum(self.n_h, dtype=np.float64))
        self.n_he_total = float(np.sum(self.n_he, dtype=np.float64))
        if self.excess_eV.shape != (3, 4):
            raise ValueError("excess-energy table must have shape (3,4)")

    @classmethod
    def from_repo(cls, repo_root: Path) -> "ReducedIntervalModel":
        repo = Path(repo_root).resolve()
        r2a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis"
        r1a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT"
        tensor = _load("r2_r1a_r1_reduced_tensor", r2a / "tensorized_inputs.py")
        forcing_mod = _load("r2_r1a_r1_reduced_forcing", r2a / "array_forcing.py")
        thermal = _load("r2_r1a_r1_reduced_thermal", r2a / "thermal_backends.py")
        trial_mod = _load("r2_r1a_r1_reduced_trial", r1a / "analysis/uncertainty_trial.py")
        policy = _load("r2_r1a_r1_reduced_policy", r1a / "analysis/uncertainty_policy.py")
        event = _load("r2_r1a_r1_reduced_event", r1a / "analysis/event_uncertainty_operator.py")
        inputs = tensor.load_tensorized_inputs(repo_root=repo)
        forcing = forcing_mod.ArrayContinuousForcing.from_repo(repo_root=repo, inputs=inputs)
        solver = trial_mod.UncertaintySecondOrderTrial.from_repo(
            repo_root=repo,
            lane="LOCAL_NEUTRAL_HAZARD_PRIMARY",
            v_policy="CELL_LOWER_STRICT",
            f_value=0.1,
        )
        source = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2/data/heating_lock/bdf_heating_moment_calibration.csv"
        frame = pd.read_csv(source)
        excess = np.zeros((3, 4), dtype=np.float64)
        for si, species in enumerate(("HI", "HeI", "HeII")):
            for gi, group in enumerate(GROUPS):
                row = frame[(frame.species == species) & (frame.group == group)]
                if len(row) != 1:
                    raise ValueError(f"missing excess-energy moment {species}/{group}")
                excess[si, gi] = float(row.iloc[0].canonical_excess_eV)
        return cls(repo_root=repo, inputs=inputs, forcing=forcing, solver=solver, thermal=thermal, policy=policy, event=event, excess_eV=excess)

    @staticmethod
    def point_box(values) -> iv.Interval:
        return iv.Interval(np.asarray(values, dtype=np.float64))

    @staticmethod
    def scalar_interval(value: float) -> iv.Interval:
        return iv.Interval(np.asarray(float(value)))

    def initial_coordinates(self) -> np.ndarray:
        y = self.inputs.state0.values
        x_hi = y[0] / self.n_h
        x_hei = y[2] / self.n_he
        r_heiii = y[4] / (y[3] + y[4])
        return np.ascontiguousarray(
            np.vstack(
                [
                    x_hi,
                    x_hei,
                    r_heiii,
                    np.log(self.inputs.state0.temperature_K),
                ]
            )
        )

    def source_v_point(self, log_temperature: np.ndarray) -> np.ndarray:
        return np.asarray(
            self.policy.build_v_field_from_temperature("CELL_LOWER_STRICT", np.exp(np.asarray(log_temperature))),
            dtype=np.float64,
        )

    def source_v_interval(self, coordinates: iv.Interval) -> iv.Interval:
        """Tight source-domain enclosure of the Hummer--Seaton branch probability.

        Inside the tabulated domain the source identifies only the two bracketing
        nodal values, not a continuous interpolant.  Below ``10^4 K`` the strict
        source-safe range is ``[0,1]``.  If one temperature box straddles that
        boundary, the union is likewise ``[0,1]``.  Above ``10^5 K`` remains a
        hard fail rather than an extrapolation.
        """

        logt = iv.Interval(coordinates.lo[3], coordinates.hi[3])
        temperature_lo = np.exp(logt.lo)
        temperature_hi = np.exp(logt.hi)
        if np.any(temperature_hi > 1.0e5 * (1.0 + 32.0 * np.finfo(float).eps)):
            raise ValueError("above-table Hummer--Seaton extrapolation is prohibited")
        # Round a last-bit overshoot at the exact upper knot back to the source
        # value only for policy evaluation; this is not a physical extrapolation.
        eval_hi = np.minimum(temperature_hi, 1.0e5)
        eval_lo = np.minimum(temperature_lo, 1.0e5)
        lower = np.asarray(
            self.policy.build_v_field_from_temperature("CELL_LOWER_STRICT", eval_lo),
            dtype=np.float64,
        )
        upper = np.asarray(
            self.policy.build_v_field_from_temperature("CELL_UPPER_STRICT", eval_hi),
            dtype=np.float64,
        )
        straddles_lower_boundary = (temperature_lo < 1.0e4) & (temperature_hi >= 1.0e4)
        lower = np.where(straddles_lower_boundary, 0.0, lower)
        upper = np.where(straddles_lower_boundary, 1.0, upper)
        return iv.Interval(
            np.maximum(0.0, np.nextafter(lower, -np.inf)),
            np.minimum(1.0, np.nextafter(upper, np.inf)),
        )

    def coordinates_to_state(self, coordinates: np.ndarray):
        tensor = sys.modules["r2b_r2a_tensorized"]
        c = np.asarray(coordinates, dtype=np.float64)
        x_hi, x_hei, rhe3, logt = c
        if np.any((x_hi <= 0.0) | (x_hi >= 1.0)):
            raise ValueError("x_HI must remain strictly inside (0,1)")
        if np.any((x_hei <= 0.0) | (x_hei >= 1.0)):
            raise ValueError("x_HeI must remain strictly inside (0,1)")
        if np.any((rhe3 <= 0.0) | (rhe3 >= 1.0)):
            raise ValueError("conditional HeIII fraction must remain inside (0,1)")
        xh = 1.0 - x_hi
        qhe = 1.0 - x_hei
        xheii = qhe * (1.0 - rhe3)
        xheiii = qhe * rhe3
        populations = np.vstack(
            [
                self.n_h * x_hi,
                self.n_h * xh,
                self.n_he * x_hei,
                self.n_he * xheii,
                self.n_he * xheiii,
            ]
        )
        T = np.exp(logt)
        nhi, nhii, nhei, nheii, nheiii = populations
        particles = self.n_h + self.n_he + nhii + nheii + 2.0 * nheiii
        energy = 1.5 * KB_ERG * particles * T
        return tensor.ArrayState(np.ascontiguousarray(np.vstack([populations, energy])), np.ascontiguousarray(T))

    def reconstruct_populations(self, coordinates: iv.Interval) -> tuple[iv.Interval, ...]:
        x_hi = iv.Interval(coordinates.lo[0], coordinates.hi[0])
        x_hei = iv.Interval(coordinates.lo[1], coordinates.hi[1])
        rhe3 = iv.Interval(coordinates.lo[2], coordinates.hi[2])
        for name, item in (("x_HI", x_hi), ("x_HeI", x_hei), ("r_HeIII", rhe3)):
            if np.any(item.lo <= 0.0) or np.any(item.hi >= 1.0):
                raise ValueError(f"{name} interval leaves the strict physical cone")
        xh = 1.0 - x_hi
        qhe = 1.0 - x_hei
        return (
            self.n_h * x_hi,
            self.n_h * xh,
            self.n_he * x_hei,
            self.n_he * qhe * (1.0 - rhe3),
            self.n_he * qhe * rhe3,
        )

    def physical_fraction_box(self, coordinates: iv.Interval) -> iv.Interval:
        """Map the internal triangular box to physical ionization fractions.

        The output ordering is ``(x_HII, x_HeII, x_HeIII, log_T)``.  This map
        is used for public uncertainty gates and comparison with the previous
        four-corner endpoint evidence.
        """

        x_hi = iv.Interval(coordinates.lo[0], coordinates.hi[0])
        x_hei = iv.Interval(coordinates.lo[1], coordinates.hi[1])
        rhe3 = iv.Interval(coordinates.lo[2], coordinates.hi[2])
        for name, item in (("x_HI", x_hi), ("x_HeI", x_hei), ("r_HeIII", rhe3)):
            if np.any(item.lo <= 0.0) or np.any(item.hi >= 1.0):
                raise ValueError(f"{name} interval leaves the strict physical cone")
        xh = 1.0 - x_hi
        qhe = 1.0 - x_hei
        logt = iv.Interval(coordinates.lo[3], coordinates.hi[3])
        xheii = qhe * (1.0 - rhe3)
        xheiii = qhe * rhe3
        return iv.Interval(
            np.vstack([xh.lo, xheii.lo, xheiii.lo, logt.lo]),
            np.vstack([xh.hi, xheii.hi, xheiii.hi, logt.hi]),
        )

    def forcing_bounds(self, time_lower_s: float, time_upper_s: float) -> ForcingBounds:
        lo, hi = float(time_lower_s), float(time_upper_s)
        model = self.forcing._models[0]
        current = []
        external = []
        for p in model["current"]:
            a, b = pbounds.ppoly_range(p, lo, hi)
            current.append(iv.Interval(max(0.0, a), max(0.0, b)))
        for p in model["external"]:
            a, b = pbounds.ppoly_range(p, lo, hi)
            external.append(iv.Interval(max(0.0, a), max(0.0, b)))
        zlo, zhi = pbounds.ppoly_range(model["z"], lo, hi)
        glo, ghi = pbounds.ppoly_range(model["gamma"], lo, hi)
        z = iv.Interval(max(0.0, zlo), max(0.0, zhi))
        gamma = iv.Interval(max(0.0, glo), max(0.0, ghi))
        hubble = H0 * iv.sqrt(OMEGA_M * iv.pow_const(1.0 + z, 3.0) + OMEGA_L)
        volume = self.inputs.comoving_volume_cm3 / iv.pow_const(1.0 + z, 3.0)
        return ForcingBounds(tuple(current), tuple(external), z, gamma, hubble, volume)

    def _explicit_photo_fields(self, populations: tuple[iv.Interval, ...], forcing: ForcingBounds):
        nhi, _nhii, nhei, nheii, _nheiii = populations
        sum_nhi = iv.sum_interval(nhi)
        sum_nhei = iv.sum_interval(nhei)
        sum_nheii = iv.sum_interval(nheii)
        scale_z = NH0_CM3 * iv.pow_const(1.0 + forcing.z, 2.0) * MPC_CM
        hi = _zero(self.n_h.shape)
        hei = _zero(self.n_h.shape)
        heii = _zero(self.n_h.shape)
        heat = _zero(self.n_h.shape)
        for gi in range(4):
            c_hi = scale_z * (self.inputs.sigma_cm2[0, gi] if self.inputs.owner_support[1, gi] else 0.0)
            c_hei = YHE * scale_z * (self.inputs.sigma_cm2[1, gi] if self.inputs.owner_support[2, gi] else 0.0)
            c_heii = YHE * scale_z * (self.inputs.sigma_cm2[2, gi] if self.inputs.owner_support[3, gi] else 0.0)
            raw_hi = c_hi * (sum_nhi / self.n_h_total)
            raw_hei = c_hei * (sum_nhei / self.n_he_total)
            raw_heii = c_heii * (sum_nheii / self.n_h_total)
            raw_total = forcing.external_subgrid[gi] + raw_hi + raw_hei + raw_heii
            if self.inputs.owner_support[1, gi]:
                node = forcing.current[gi] * c_hi * nhi / (self.n_h_total * raw_total)
                hi = hi + node
                heat = heat + node * (self.excess_eV[0, gi] * EV_ERG)
            if self.inputs.owner_support[2, gi]:
                node = forcing.current[gi] * c_hei * nhei / (self.n_he_total * raw_total)
                hei = hei + node
                heat = heat + node * (self.excess_eV[1, gi] * EV_ERG)
            if self.inputs.owner_support[3, gi]:
                node = forcing.current[gi] * c_heii * nheii / (self.n_h_total * raw_total)
                heii = heii + node
                heat = heat + node * (self.excess_eV[2, gi] * EV_ERG)
        return hi, hei, heii, heat

    def rhs_interval(
        self,
        *,
        coordinates: iv.Interval,
        time_lower_s: float,
        time_upper_s: float,
        v_interval: iv.Interval,
        f_interval: iv.Interval,
    ) -> iv.Interval:
        return self.rhs_details(
            coordinates=coordinates,
            time_lower_s=time_lower_s,
            time_upper_s=time_upper_s,
            v_interval=v_interval,
            f_interval=f_interval,
        ).rhs

    def rhs_details(
        self,
        *,
        coordinates: iv.Interval,
        time_lower_s: float,
        time_upper_s: float,
        v_interval: iv.Interval,
        f_interval: iv.Interval,
    ) -> IntervalRHSResult:
        forcing = self.forcing_bounds(time_lower_s, time_upper_s)
        populations = self.reconstruct_populations(coordinates)
        nhi, nhii, nhei, nheii, nheiii = populations
        T = iv.exp(iv.Interval(coordinates.lo[3], coordinates.hi[3]))
        volume = forcing.volume_cm3
        ne = (nhii + nheii + 2.0 * nheiii) / volume
        photo_hi, photo_hei, photo_heii, primary_heat = self._explicit_photo_fields(populations, forcing)

        n_hi = nhi / volume
        n_hei = nhei / volume
        n_heii = nheii / volume
        op_h24 = n_hi * SIGMA_OTS_H24
        op_hei24 = n_hei * SIGMA_OTS_HEI24
        y = op_h24 / (op_h24 + op_hei24 + 1.0e-300)
        op_h41 = n_hi * SIGMA_OTS_H41
        op_hei41 = n_hei * SIGMA_OTS_HEI41
        z_abs = op_h41 / (op_h41 + op_hei41 + 1.0e-300)
        op_h54 = n_hi * SIGMA_OTS_H54
        op_hei54 = n_hei * SIGMA_OTS_HEI54
        op_heii54 = n_heii * SIGMA_OTS_HEII54
        total54 = op_h54 + op_hei54 + op_heii54 + 1.0e-300
        p_h54 = op_h54 / total54
        p_hei54 = op_hei54 / total54
        p_heii54 = op_heii54 / total54
        A_H, A_HeI = _multi_affine_branches(v_interval, f_interval, y, z_abs)

        r_hi = photo_hi + nhi * ne * _beta_hi(T)
        r_hei = photo_hei + nhei * ne * _beta_hei(T)
        r_heii = photo_heii + nheii * ne * _beta_heii(T)
        a_a2 = _alpha_a_heii(T)
        a_b2 = _alpha_b_heii(T)
        a_a3 = _alpha_a_heiii(T)
        a_b3 = _alpha_b_heiii(T)
        a_n2 = iv.minimum(_alpha_heiii_n2(T), a_b3)
        a_cas = iv.maximum(a_b3 - a_n2, 0.0)
        r_hb = nhii * ne * _alpha_b_hii(T)
        r_he2g = nheii * ne * iv.maximum(a_a2 - a_b2, 0.0)
        r_he2b = nheii * ne * a_b2
        r_he3g = nheiii * ne * iv.maximum(a_a3 - a_b3, 0.0)
        r_he3n2 = nheiii * ne * a_n2
        r_he3cas = nheiii * ne * a_cas

        ion_h = r_hi + r_he2g * y + r_he2b * P_EXC + r_he3g * p_h54 + r_he3n2 + r_he3cas * A_H
        d_hii = ion_h - r_hb
        d_heiii = r_heii + r_he3g * p_heii54 - r_he3g - r_he3n2 - r_he3cas
        d_heii = (
            r_hei
            + r_he2g * (1.0 - y)
            + r_he3g * p_hei54
            + r_he3cas * A_HeI
            + r_he3g
            + r_he3n2
            + r_he3cas
            - r_he2g
            - r_he2b
            - r_heii
            - r_he3g * p_heii54
        )
        d_hi = -d_hii
        d_hei = -(d_heii + d_heiii)

        ots_heat_per_event = (1.0 - v_interval) * f_interval * (
            z_abs * (HEII_LYA_EV - CHI_H_EV)
            + (1.0 - z_abs) * (HEII_LYA_EV - CHI_HEI_EV)
        ) * EV_ERG
        resolved_ots_heat = r_he3cas * ots_heat_per_event
        resolved_heat = primary_heat + resolved_ots_heat
        escaped = r_he3cas * (1.0 - v_interval) * (1.0 - f_interval) * HEII_LYA_EV * EV_ERG

        # The total binding-energy remainder is retained as an unresolved OTS
        # radiation reservoir.  It is not fed back into resolved temperature.
        chemical = (
            r_hb * (-CHI_H_EV)
            + r_he2g * (-CHI_HEI_EV + y * CHI_H_EV + (1.0 - y) * CHI_HEI_EV)
            + r_he2b * (-CHI_HEI_EV + P_EXC * CHI_H_EV)
            + r_he3g * (-CHI_HEII_EV + p_h54 * CHI_H_EV + p_hei54 * CHI_HEI_EV + p_heii54 * CHI_HEII_EV)
            + r_he3n2 * (-CHI_HEII_EV + CHI_H_EV)
            + r_he3cas * (-CHI_HEII_EV + v_interval * (((ELL - M_CAS) + M_CAS * y) * CHI_H_EV + M_CAS * (1.0 - y) * CHI_HEI_EV)
                          + (1.0 - v_interval) * f_interval * (z_abs * CHI_H_EV + (1.0 - z_abs) * CHI_HEI_EV))
        ) * EV_ERG
        unresolved = -chemical - resolved_ots_heat - escaped

        ll_h = 315614.0 / T
        ll_hei = 570670.0 / T
        ll_heii = 1263030.0 / T
        rec_h = 3.435e-30 * T * iv.pow_const(ll_h, 1.970) / iv.pow_const(1.0 + iv.pow_const(ll_h / 2.250, 0.376), 3.720)
        rec_heii = KB_ERG * T * (1.26e-14 * iv.pow_const(ll_hei, 0.750))
        rec_heiii = 8.0 * 3.435e-30 * T * iv.pow_const(ll_heii, 1.970) / iv.pow_const(1.0 + iv.pow_const(ll_heii / 2.250, 0.376), 3.720)
        exc_h = 7.5e-19 * iv.exp(-118348.0 / T) / (1.0 + iv.sqrt(T / 1.0e5))
        exc_heii = 5.54e-17 * iv.pow_const(T, -0.397) * iv.exp(-473638.0 / T) / (1.0 + iv.sqrt(T / 1.0e5))
        log10_t = iv.log(T) / math.log(10.0)
        ff_cool = 1.42e-27 * iv.sqrt(T) * (1.1 + 0.34 * iv.exp(-iv.pow_const(5.5 - log10_t, 2.0) / 3.0))
        cool = (
            ne * nhii * rec_h
            + ne * nheii * rec_heii
            + ne * nheiii * rec_heiii
            + ne * nhi * exc_h
            + ne * nheii * exc_heii
            + ne * nhi * _beta_hi(T) * (13.598 * EV_ERG)
            + ne * nhei * _beta_hei(T) * (24.587 * EV_ERG)
            + ne * nheii * _beta_heii(T) * (54.416 * EV_ERG)
            + ne * (nhii + nheii + 4.0 * nheiii) * ff_cool
        )
        particles = self.n_h + self.n_he + nhii + nheii + 2.0 * nheiii
        expansion = 3.0 * forcing.hubble_s_inv * KB_ERG * T * particles
        thermal_rhs = resolved_heat - cool - expansion
        energy = 1.5 * KB_ERG * particles * T
        particle_rhs = d_hii + d_heii + 2.0 * d_heiii
        d_logt = thermal_rhs / energy - particle_rhs / particles

        x_hi = iv.Interval(coordinates.lo[0], coordinates.hi[0])
        x_hei = iv.Interval(coordinates.lo[1], coordinates.hi[1])
        qhe = 1.0 - x_hei
        rhe3 = iv.Interval(coordinates.lo[2], coordinates.hi[2])
        d_qhe = (d_heii + d_heiii) / self.n_he
        d_rhe3 = (d_heiii / self.n_he - rhe3 * d_qhe) / qhe
        d_xhi = d_hi / self.n_h
        d_xhei = d_hei / self.n_he
        reduced = iv.Interval(
            np.vstack([d_xhi.lo, d_xhei.lo, d_rhe3.lo, d_logt.lo]),
            np.vstack([d_xhi.hi, d_xhei.hi, d_rhe3.hi, d_logt.hi]),
        )
        # The authoritative float oracle applies one last-bit conservation
        # correction to the largest owner/node allocation.  The analytic
        # cancellation above represents the same real-valued operator but in a
        # different arithmetic order; cover that adapter-level rounding path.
        reduced = iv.inflate(reduced, relative=2.0e-9, absolute=1.0e-300)
        return IntervalRHSResult(
            rhs=reduced,
            population_rhs=(d_hi, d_hii, d_hei, d_heii, d_heiii),
            photo_hi=photo_hi,
            photo_hei=photo_hei,
            photo_heii=photo_heii,
            resolved_photoheat=resolved_heat,
            unresolved_ots_energy_rate=unresolved,
            escaped_ots_energy_rate=escaped,
            branch_A_H=A_H,
            branch_A_HeI=A_HeI,
        )

    def floating_reference_rhs(self, *, coordinates: np.ndarray, time_s: float, v: np.ndarray, f: float) -> np.ndarray:
        state = self.coordinates_to_state(coordinates)
        point = self.solver.forcing.point(interval=0, time_s=float(time_s))
        owner = self.solver._owner(state, point)
        photo = self.solver.backend.photo_fields(owner)
        volume = self.inputs.comoving_volume_cm3 / (1.0 + point.z) ** 3
        event = self.event.evaluate_event_flux(
            populations=state.values[:5].T,
            temperature_K=state.temperature_K,
            proper_volume_cm3=volume,
            photo_hi=photo.HI,
            photo_hei=photo.HeI,
            photo_heii=photo.HeII,
            v=np.asarray(v, dtype=np.float64),
            f=np.full(state.node_count, float(f), dtype=np.float64),
        )
        heat = photo.heating + event.resolved_ots_heating_erg_s
        pop = state.values[:5].T
        rhs = event.population_rhs
        thermal_rhs = self.thermal._thermal_rhs_numpy(
            np.log(state.temperature_K), pop, volume, heat, np.full(state.node_count, point.hubble_s_inv)
        )
        particles = self.n_h + self.n_he + pop[:, 1] + pop[:, 3] + 2.0 * pop[:, 4]
        energy = 1.5 * KB_ERG * particles * state.temperature_K
        particle_rhs = rhs[:, 1] + rhs[:, 3] + 2.0 * rhs[:, 4]
        x_hei = coordinates[1]
        qhe = 1.0 - x_hei
        rhe3 = coordinates[2]
        d_qhe = (rhs[:, 3] + rhs[:, 4]) / self.n_he
        d_rhe3 = (rhs[:, 4] / self.n_he - rhe3 * d_qhe) / qhe
        d_xhi = rhs[:, 0] / self.n_h
        d_xhei = rhs[:, 2] / self.n_he
        return np.ascontiguousarray(
            np.vstack(
                [
                    d_xhi,
                    d_xhei,
                    d_rhe3,
                    thermal_rhs / energy - particle_rhs / particles,
                ]
            )
        )


__all__ = ["ForcingBounds", "IntervalRHSResult", "ReducedIntervalModel"]
