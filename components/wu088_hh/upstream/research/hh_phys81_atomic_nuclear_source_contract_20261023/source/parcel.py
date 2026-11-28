"""PHYS81 fixed-density, common-temperature finite-CI parcel.

The three hazard coordinates are an exact continuous-model reduction of
six neutral/ion abundances and thermal energy.  A separate normalized
seven-state RHS retains those original equations without a conservation
projection.  Abundances are per reference H, nref is in cm^-3, time is in
seconds, and thermal energy u is in eV per reference H.

Only stationary-target finite-window CI rates are active.  All outgoing
electrons and recoil join the common thermal pool.  Expansion, PI, RR, CX
and collisional excitation are off.  These are selected model assumptions,
not a physical admission of omitted processes or thermalization dynamics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

if __package__:
    from .finite_ci import FiniteWindowCI, KB_EV_K, _immutable, _real_scalar, _real_vector
else:
    from finite_ci import FiniteWindowCI, KB_EV_K, _immutable, _real_scalar, _real_vector


def _state_vector(values, length: int, name: str) -> np.ndarray:
    state = _real_vector(values, name)
    if state.shape != (length,):
        raise ValueError(f"{name}_REQUIRES_{length}_COMPONENTS")
    if np.any(state < 0.0):
        raise ValueError(f"{name}_MUST_BE_NONNEGATIVE_NO_PROJECTION")
    return state


@dataclass(frozen=True, slots=True, eq=False)
class HazardParcel:
    """Three independently supplied neutral-to-singly-ionized CI models.

    Every chemical defect is read from the corresponding rate object's
    Ichemical_eV.  No isotope energy or source-window threshold is hardcoded.
    All solver trial states are checked; negative entries are rejected, not
    clipped.  Saturated neutral populations can underflow and are flagged.
    """

    rates: tuple[FiniteWindowCI, FiniteWindowCI, FiniteWindowCI]
    abundance_total: np.ndarray
    initial_ions: np.ndarray
    T0_K: float
    nref_cm3: float
    N0: np.ndarray = field(init=False)
    Ichemical_eV: np.ndarray = field(init=False)
    u0: float = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.rates, tuple) or len(self.rates) != 3:
            raise ValueError("RATES_MUST_BE_TUPLE_OF_THREE_FINITE_WINDOW_CI_MODELS")
        if not all(isinstance(rate, FiniteWindowCI) for rate in self.rates):
            raise ValueError("RATES_MUST_BE_FINITE_WINDOW_CI_MODELS")
        total = _state_vector(self.abundance_total, 3, "ABUNDANCE_TOTAL")
        ions = _state_vector(self.initial_ions, 3, "INITIAL_IONS")
        if np.any(total <= 0.0) or np.any(ions >= total):
            raise ValueError("INITIAL_ABUNDANCES_REQUIRE_B_POSITIVE_AND_0_LE_X0_LT_B")
        temperature = _real_scalar(self.T0_K, "T0_K")
        density = _real_scalar(self.nref_cm3, "NREF_CM3")
        if density <= 0.0:
            raise ValueError("NREF_CM3_MUST_BE_POSITIVE")
        for rate in self.rates:
            rate._temperature(temperature)
        with np.errstate(over="raise", invalid="raise"):
            electrons = float(np.sum(ions))
            particles = float(np.sum(total)) + electrons
            neutral = total - ions
        if not math.isfinite(electrons) or electrons <= 0.0:
            raise ValueError("INITIAL_ELECTRON_ABUNDANCE_MUST_BE_POSITIVE_FINITE")
        if not math.isfinite(particles) or particles <= 0.0:
            raise ValueError("INITIAL_PARTICLE_ABUNDANCE_MUST_BE_POSITIVE_FINITE")
        u0 = 1.5 * KB_EV_K * temperature * particles
        if not math.isfinite(u0) or u0 <= 0.0:
            raise ValueError("INITIAL_THERMAL_ENERGY_MUST_BE_POSITIVE_FINITE")
        chemical = np.asarray([rate.Ichemical_eV for rate in self.rates], dtype=np.float64)
        if not np.all(np.isfinite(chemical)) or not np.all(chemical > 0.0):
            raise ValueError("RATE_CHEMICAL_DEFECTS_MUST_BE_POSITIVE_FINITE")
        object.__setattr__(self, "abundance_total", total)
        object.__setattr__(self, "initial_ions", ions)
        object.__setattr__(self, "T0_K", temperature)
        object.__setattr__(self, "nref_cm3", density)
        object.__setattr__(self, "N0", _immutable(neutral))
        object.__setattr__(self, "Ichemical_eV", _immutable(chemical))
        object.__setattr__(self, "u0", u0)

    @property
    def B(self) -> np.ndarray:
        return self.abundance_total

    @property
    def X0(self) -> np.ndarray:
        return self.initial_ions

    def _temperature_from_energy(self, u: float, particles: float) -> float:
        if not math.isfinite(u) or u <= 0.0:
            raise ValueError("PARCEL_THERMAL_ENERGY_MUST_BE_POSITIVE_FINITE")
        if not math.isfinite(particles) or particles <= 0.0:
            raise ValueError("PARCEL_PARTICLE_ABUNDANCE_MUST_BE_POSITIVE_FINITE")
        temperature = u / (1.5 * KB_EV_K * particles)
        for rate in self.rates:
            rate._temperature(temperature)
        return temperature

    def _coefficients(self, temperature: float) -> tuple[np.ndarray, np.ndarray]:
        evaluations = tuple(rate.evaluate(temperature) for rate in self.rates)
        coefficients = np.asarray([r.K_cm3_s for r in evaluations], dtype=np.float64)
        derivatives = np.asarray([r.dK_dT_cm3_s_K for r in evaluations], dtype=np.float64)
        if (not np.all(np.isfinite(coefficients)) or np.any(coefficients < 0.0)
                or not np.all(np.isfinite(derivatives))):
            raise ArithmeticError("PARCEL_INVALID_FINITE_CI_COEFFICIENTS")
        return coefficients, derivatives

    def lift(self, z) -> dict:
        """Decode nonnegative hazards with stable neutral/ion increments.

        The energy decrement uses the expm1-derived ion increment directly;
        subtracting rounded X-X0 would lose an initially tiny increment.
        No neutral floor or clipping is applied.
        """
        hazard = _state_vector(z, 3, "HAZARD")
        with np.errstate(over="raise", invalid="raise", under="ignore"):
            neutral = self.N0 * np.exp(-hazard)
            increment = self.N0 * (-np.expm1(-hazard))
            ions = self.initial_ions + increment
            electrons = float(np.sum(ions))
            particles = float(np.sum(self.abundance_total)) + electrons
            chemical_increment = float(np.dot(self.Ichemical_eV, increment))
            u = self.u0 - chemical_increment
        if (not np.all(np.isfinite(neutral)) or np.any(neutral < 0.0)
                or not np.all(np.isfinite(ions)) or np.any(ions < 0.0)
                or not math.isfinite(electrons) or electrons < 0.0):
            raise ArithmeticError("PARCEL_NONFINITE_OR_NEGATIVE_LIFTED_POPULATION")
        temperature = self._temperature_from_energy(u, particles)
        underflow = (neutral == 0.0) & (self.N0 > 0.0)
        return {
            "neutral_abundance": neutral,
            "ion_abundance": ions,
            "ion_increment": increment,
            "xe": electrons,
            "N_g": particles,
            "u": u,
            "T": temperature,
            "chemical_energy_increment_eV_per_reference_H": chemical_increment,
            "neutral_underflow": bool(np.any(underflow)),
            "neutral_underflow_mask": underflow,
        }

    def rhs(self, t, z) -> np.ndarray:
        """Hazard derivative in proper seconds: nref * xe * K(T)."""
        _real_scalar(t, "TIME_S")
        state = self.lift(z)
        coefficients, _ = self._coefficients(state["T"])
        with np.errstate(over="raise", invalid="raise", under="ignore"):
            result = self.nref_cm3 * state["xe"] * coefficients
        if not np.all(np.isfinite(result)) or np.any(result < 0.0):
            raise ArithmeticError("PARCEL_INVALID_HAZARD_RHS")
        return result

    def jac(self, t, z) -> np.ndarray:
        """Analytic 3x3 Jacobian, the sum of two outer products (rank <= 2)."""
        _real_scalar(t, "TIME_S")
        state = self.lift(z)
        coefficients, derivatives = self._coefficients(state["T"])
        neutral = state["neutral_abundance"]
        temperature = state["T"]
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            dTdz = (-neutral * (self.Ichemical_eV + 1.5 * KB_EV_K * temperature)
                    / (1.5 * KB_EV_K * state["N_g"]))
            result = self.nref_cm3 * (
                np.outer(coefficients, neutral)
                + state["xe"] * np.outer(derivatives, dTdz)
            )
        if not np.all(np.isfinite(result)):
            raise ArithmeticError("PARCEL_NONFINITE_HAZARD_JACOBIAN")
        return result

    def initial_full(self) -> np.ndarray:
        """Fresh normalized original state [neutral/B, ion/B, u/u0]."""
        return np.concatenate((self.N0 / self.B, self.X0 / self.B, np.asarray([1.0])))

    def full_lift(self, w) -> dict:
        """Decode all seven independent coordinates without using invariants.

        Fractions may exceed one in an unconserved trial.  They must remain
        nonnegative, and the decoded particles, energy and rate temperature
        must satisfy their domains.  Neutral and ion sums are not projected
        back to B; u is decoded from w[6], not from the hazard first integral.
        """
        full = _state_vector(w, 7, "FULL_STATE")
        with np.errstate(over="raise", invalid="raise", under="ignore"):
            neutral = self.B * full[:3]
            ions = self.B * full[3:6]
            electrons = float(np.sum(ions))
            particles = float(np.dot(self.B, full[:3] + full[3:6])) + electrons
            u = self.u0 * float(full[6])
        if (not np.all(np.isfinite(neutral)) or not np.all(np.isfinite(ions))
                or not math.isfinite(electrons)):
            raise ArithmeticError("PARCEL_NONFINITE_FULL_POPULATION")
        temperature = self._temperature_from_energy(u, particles)
        underflow = (neutral == 0.0) & (full[:3] > 0.0)
        return {
            "neutral_abundance": neutral,
            "ion_abundance": ions,
            "xe": electrons,
            "N_g": particles,
            "u": u,
            "T": temperature,
            "neutral_underflow": bool(np.any(underflow)),
            "neutral_underflow_mask": underflow,
        }

    def full_rhs(self, t, w) -> np.ndarray:
        """Independent original seven-state abundance/thermal equations.

        F_i is a neutral-fraction loss rate, so each actual event rate per
        reference H is B_i*F_i.  Only Ichemical_i is debited from thermal
        energy; incoming electron energy is not counted as extra cooling.
        """
        _real_scalar(t, "TIME_S")
        full = _state_vector(w, 7, "FULL_STATE")
        state = self.full_lift(full)
        coefficients, _ = self._coefficients(state["T"])
        with np.errstate(over="raise", invalid="raise", under="ignore"):
            fraction_flux = self.nref_cm3 * state["xe"] * coefficients * full[:3]
            energy_derivative = -float(np.dot(self.Ichemical_eV * self.B, fraction_flux)) / self.u0
            result = np.concatenate((-fraction_flux, fraction_flux, np.asarray([energy_derivative])))
        if not np.all(np.isfinite(result)) or np.any(fraction_flux < 0.0):
            raise ArithmeticError("PARCEL_INVALID_FULL_RHS")
        return result

    def energy_conventions(self) -> dict:
        """Explicit CI event owners and coordinate units for the caller."""
        return {
            "abundance_unit": "per reference H nucleus",
            "time_unit": "proper seconds",
            "nref_unit": "cm^-3",
            "thermal_u_unit": "eV per reference H nucleus",
            "chemical_I_eV": self.Ichemical_eV.tolist(),
            "species": [rate.species for rate in self.rates],
            "source_identities": [rate.source_identity for rate in self.rates],
            "per_CI_event": {
                "neutral": -1,
                "singly_ionized": 1,
                "free_electron": 1,
                "gas_particle_count": 1,
                "thermal_energy_eV": "-Ichemical[species]",
                "ionic_binding_energy_eV": "+Ichemical[species]",
                "escaped_radiation_energy_eV": 0,
            },
            "thermal_pool": "all outgoing electrons and recoil share one imposed temperature",
            "incoming_energy_mean": "rate diagnostic only; not an additional event heat loss",
            "active_processes": ["source-bound finite-window CI"],
            "inactive_processes": ["expansion", "PI", "RR", "CX", "CE"],
            "numerical_claim": "first-integral residual is not independent trajectory accuracy evidence",
        }
