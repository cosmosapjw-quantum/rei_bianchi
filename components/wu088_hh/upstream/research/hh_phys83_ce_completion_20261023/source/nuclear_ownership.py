"""Detached nuclear thermal/fast energy ledger, with supplied normal-frame data.

No mass table, PHYS81 kernel, empirical rate, stopping model or ODE is called.
Event energies must already refer to one normal orthonormal frame.  Scalar
closure validates those inputs; it does not verify their on-shell four-vectors.
Theory: NUCLEAR_THERMAL_FAST_OWNERSHIP_KO.md, equations (4), (8), (12)--(15).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
from typing import Iterable

NORMAL_FRAME = "normal_orthonormal"
ENERGY_REL_TOL = 2.0e-12
MEV_TO_ERG = 1.602176634e-6
KB_ERG_PER_K = 1.380649e-16
KB_MEV_PER_K = KB_ERG_PER_K / MEV_TO_ERG


def _scalar(value, name: str, *, nonnegative=False, positive=False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name}_REQUIRES_REAL_NONBOOL_SCALAR")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name}_OUT_OF_FLOAT_RANGE") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name}_MUST_BE_FINITE")
    if (positive and result <= 0) or (nonnegative and result < 0):
        raise ValueError(f"{name}_OUT_OF_DOMAIN")
    return result


def _frame(value: str) -> str:
    # Optional suffix identifies the particular shared frame, cell or epoch.
    if not isinstance(value, str) or not (
        value == NORMAL_FRAME
        or (value.startswith(NORMAL_FRAME + ":")
            and value[len(NORMAL_FRAME) + 1:].strip())
    ):
        raise ValueError("EXPLICIT_NORMAL_ORTHONORMAL_FRAME_REQUIRED")
    return value


def _signed_residual(values: tuple[float, ...]) -> tuple[float, float]:
    scale = max(abs(x) for x in values)
    if scale == 0:
        return 0.0, 0.0
    normalized = math.fsum(x / scale for x in values)
    return normalized * scale, normalized


@dataclass(frozen=True, slots=True)
class EventEnergy:
    """One supplied event or positive-weight mean; all energy fields are MeV.

    Kin and Kc may vanish; Egamma and Q must be strictly positive for the
    admitted exothermic two-to-one bare-nucleus radiative-capture channels.
    Averaging may combine channels for aggregate pool counts, not isotope
    stoichiometry.  Source/rate identity belongs to the supplying provider.
    """

    Kin_MeV: float
    Kc_MeV: float
    Egamma_MeV: float
    Q_MeV: float
    frame: str

    def __post_init__(self):
        for name in ("Kin_MeV", "Kc_MeV", "Egamma_MeV", "Q_MeV"):
            value = _scalar(getattr(self, name), name, nonnegative=True,
                            positive=name in ("Egamma_MeV", "Q_MeV"))
            object.__setattr__(self, name, value)
        _frame(self.frame)
        if abs(self.normalized_energy_residual) > ENERGY_REL_TOL:
            raise ValueError("SUPPLIED_EVENT_ENERGY_CLOSURE_FAILED")

    @property
    def energy_residual_MeV(self) -> float:
        return _signed_residual((self.Egamma_MeV, self.Kc_MeV,
                                 -self.Kin_MeV, -self.Q_MeV))[0]

    @property
    def normalized_energy_residual(self) -> float:
        return _signed_residual((self.Egamma_MeV, self.Kc_MeV,
                                 -self.Kin_MeV, -self.Q_MeV))[1]


def weighted_event_mean(events: Iterable[EventEnergy],
                        weights: Iterable[float]) -> EventEnergy | None:
    """Same normalized nonnegative weights for every energy; zero total -> None.

    Weights are supplied relative event-rate weights, not a nuclear rate model.
    Scaling by their maximum avoids overflowing an otherwise harmless sum.
    Even zero-weight records must be valid EventEnergy in the same frame.
    """
    records = tuple(events)
    ws = tuple(_scalar(x, "WEIGHT", nonnegative=True) for x in weights)
    if len(records) != len(ws):
        raise ValueError("EVENT_WEIGHT_LENGTH_MISMATCH")
    if any(not isinstance(e, EventEnergy) for e in records):
        raise ValueError("EVENTENERGY_RECORDS_REQUIRED")
    if records and any(e.frame != records[0].frame for e in records):
        raise ValueError("MIXED_NORMAL_FRAMES")
    largest = max(ws, default=0.0)
    if largest == 0:
        return None
    scaled = tuple(w / largest for w in ws)
    total = math.fsum(scaled)
    normalized = tuple(w / total for w in scaled)
    means = []
    for field in ("Kin_MeV", "Kc_MeV", "Egamma_MeV", "Q_MeV"):
        field_scale = max(getattr(e, field) for e in records)
        # Preserve a positive subnormal constant mean without multiplying
        # each subnormal input by a fractional normalized weight first.
        value = (field_scale * math.fsum(w * (getattr(e, field) / field_scale)
                 for e, w in zip(records, normalized)) if field_scale else 0.0)
        means.append(value)
    return EventEnergy(*means, frame=records[0].frame)


@dataclass(frozen=True, slots=True)
class Ledger:
    """Signed per-event or per-transfer increments; numbers are literal counts."""

    mode: str
    delta_N_thermal: int
    delta_N_fast: int
    delta_rest_MeV: float
    delta_thermal_MeV: float
    delta_fast_MeV: float
    delta_photon_MeV: float
    frame: str

    def __post_init__(self):
        if self.mode not in ("FAST_FIRST", "PROMPT_THERMAL", "STOPPING", "ASSIMILATION"):
            raise ValueError("UNKNOWN_LEDGER_MODE")
        _frame(self.frame)
        for name in ("delta_N_thermal", "delta_N_fast"):
            if type(getattr(self, name)) is not int:
                raise ValueError("LITERAL_INTEGER_PARTICLE_COUNTS_REQUIRED")
        for name in ("delta_rest_MeV", "delta_thermal_MeV", "delta_fast_MeV",
                     "delta_photon_MeV"):
            object.__setattr__(self, name, _scalar(getattr(self, name), name))

    @property
    def energy_residual_MeV(self) -> float:
        return _signed_residual((self.delta_rest_MeV, self.delta_thermal_MeV,
                                 self.delta_fast_MeV, self.delta_photon_MeV))[0]

    @property
    def normalized_energy_residual(self) -> float:
        return _signed_residual((self.delta_rest_MeV, self.delta_thermal_MeV,
                                 self.delta_fast_MeV, self.delta_photon_MeV))[1]


def capture_ledger(mean: EventEnergy, mode: str = "FAST_FIRST") -> Ledger:
    """Two thermal reactants; exclusive fast daughter or explicit prompt bath.

    No supplied residual is zeroed and no photon energy is inferred by closure.
    None (a zero-rate conditional mean) is rejected: assemble zero sources at
    the caller without inventing a conditional event.
    """
    if not isinstance(mean, EventEnergy):
        raise ValueError("NONZERO_RATE_EVENTENERGY_REQUIRED")
    if mode == "FAST_FIRST":
        return Ledger(mode, -2, 1, -mean.Q_MeV, -mean.Kin_MeV,
                      mean.Kc_MeV, mean.Egamma_MeV, mean.frame)
    if mode == "PROMPT_THERMAL":
        thermal = math.fsum((mean.Kc_MeV, -mean.Kin_MeV))
        return Ledger(mode, -1, 0, -mean.Q_MeV, thermal,
                      0.0, mean.Egamma_MeV, mean.frame)
    raise ValueError("CAPTURE_MODE_MUST_BE_FAST_FIRST_OR_PROMPT_THERMAL")


def stopping_transfer(energy_MeV: float, *, frame: str = NORMAL_FRAME) -> Ledger:
    """Supplied fast-to-bath energy only; no particle assimilation or stopping law."""
    energy = _scalar(energy_MeV, "STOPPING_ENERGY_MEV", nonnegative=True)
    return Ledger("STOPPING", 0, 0, 0.0, energy, -energy, 0.0, _frame(frame))


def assimilation_transfer(mean_kinetic_MeV: float, *,
                          frame: str = NORMAL_FRAME) -> Ledger:
    """Transfer one fast particle and its actual remaining kinetic energy once."""
    energy = _scalar(mean_kinetic_MeV, "MATCH_KINETIC_MEV", nonnegative=True)
    return Ledger("ASSIMILATION", 1, -1, 0.0, energy, -energy, 0.0, _frame(frame))


def thermal_temperature_source(T_K: float, nthermal_cm3: float,
                               thermal_power_MeV_cm3_s: float,
                               number_source_cm3_s: float,
                               theta_s_inv: float = 0.0) -> float:
    """Return dT/dt [K/s] from the monatomic EOS including number and expansion.

    Tdot=-(2/3)Theta*T+2*Qth/(3*n*kB)-T*Sn/n.  Only actual thermal
    members enter n; fast-particle or collisionless-DM heat capacities are absent.
    MeV -> erg uses the exact SI eV definition, represented as binary64 here.
    """
    temp = _scalar(T_K, "TEMPERATURE_K", positive=True)
    density = _scalar(nthermal_cm3, "THERMAL_DENSITY_CM3", positive=True)
    power = _scalar(thermal_power_MeV_cm3_s, "THERMAL_POWER_MEV_CM3_S")
    source = _scalar(number_source_cm3_s, "NUMBER_SOURCE_CM3_S")
    theta = _scalar(theta_s_inv, "THETA_S_INV")
    value = math.fsum((-(2.0 / 3.0) * theta * temp,
                       (2.0 / 3.0) * (power / density) * MEV_TO_ERG / KB_ERG_PER_K,
                       -temp * (source / density)))
    return _scalar(value, "TEMPERATURE_SOURCE_K_S")


def nr_selected_kinetic_mean(T_K: float, dlnK_dlnT: float, *,
                             temperature_independent_sigma: bool = False) -> float:
    """Conditional equal-T NR Maxwellian incoming-pair mean [MeV].

    Returns kB*T*(3+alpha), alpha=dln<sigma*v>/dlnT.  The caller must
    explicitly attest T-independent sigma and differentiation under the rate
    integral; equal T, zero drift and valid NR support are further preconditions.
    alpha>-3/2 encodes a strictly positive selected relative-energy mean.
    No rate, cross section, temperature history or relativistic measure is built.
    """
    if temperature_independent_sigma is not True:
        raise ValueError("EXPLICIT_T_INDEPENDENT_SIGMA_ATTESTATION_REQUIRED")
    temp = _scalar(T_K, "TEMPERATURE_K", positive=True)
    alpha = _scalar(dlnK_dlnT, "DLOG_RATE_DLOG_T")
    if alpha <= -1.5:
        raise ValueError("POSITIVE_SELECTED_RELATIVE_ENERGY_REQUIRES_ALPHA_GT_MINUS_1P5")
    return _scalar(KB_MEV_PER_K * temp * (3.0 + alpha),
                   "SELECTED_INCOMING_KINETIC_MEV", positive=True)
