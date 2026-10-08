"""Exact conditional affine-family photo-source enclosure at one fixed state.

An affine family is center + sum_j u_j generator_j, -1 <= u_j <= 1.
The SAME u_j is used for Gamma and incident-energy moments.  This module
neither establishes that an external uncertainty family is true nor supplies
a history, quadrature, provider, or chemistry error certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from typing import Mapping, Sequence

from .vendor.source_transfer import ContractError, MissingPremise, Moments, State, project

GAMMA_UNIT = "absorber^-1 s^-1"
ENERGY_UNIT = "eV absorber^-1 s^-1"
CLOCK = "s=ln a"
INPUT_KIND = "instantaneous_per_absorber_moment_rates"
SPECIES = ("HI", "HeI", "HeII")


def _label(value: object, code: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(code)


def _moments(value: object) -> None:
    if not isinstance(value, Moments):
        raise ContractError("MOMENTS_REQUIRED")
    # Recheck because the vendored dataclass accepts mutable sequences at runtime.
    if not isinstance(value.gamma, tuple) or not isinstance(value.energy_ev_s, tuple):
        raise ContractError("IMMUTABLE_MOMENT_TUPLES_REQUIRED")
    if len(value.gamma) != 3 or len(value.energy_ev_s) != 3:
        raise ContractError("THREE_SPECIES_REQUIRED")
    if any(not isinstance(v, F) for v in (*value.gamma, *value.energy_ev_s)):
        raise ContractError("EXACT_FRACTION_REQUIRED")


@dataclass(frozen=True)
class FixedContext:
    source_id: str
    clock_id: str
    state_id: str
    provider_id: str
    bound_state: State
    epoch_ln_a: F
    chi_ev: tuple[F, F, F]
    clock: str = CLOCK

    def __post_init__(self) -> None:
        for name in ("source_id", "clock_id", "state_id", "provider_id"):
            _label(getattr(self, name), "EXPLICIT_" + name.upper() + "_REQUIRED")
        if self.clock != CLOCK:
            raise ContractError("LN_A_CLOCK_REQUIRED")
        if not isinstance(self.epoch_ln_a, F):
            raise ContractError("EXACT_LN_A_EPOCH_REQUIRED")
        if (not isinstance(self.chi_ev, tuple) or len(self.chi_ev) != 3 or
                any(not isinstance(v, F) or v <= 0 for v in self.chi_ev)):
            raise ContractError("THREE_EXACT_POSITIVE_CONTEXT_THRESHOLDS_REQUIRED")
        if not isinstance(self.bound_state, State):
            raise ContractError("EXACT_FIXED_STATE_REQUIRED")
        # State already checks its physical domain, including H > 0.
        self.bound_state.__post_init__()


@dataclass(frozen=True)
class JointMomentFamily:
    center: Moments
    generators: tuple[Moments, ...]
    context: FixedContext
    family_id: str
    family_kind: str
    generator_ids: tuple[str, ...]
    gamma_unit: str = GAMMA_UNIT
    energy_unit: str = ENERGY_UNIT
    input_kind: str = INPUT_KIND

    def __post_init__(self) -> None:
        _moments(self.center)
        if not isinstance(self.generators, tuple) or len(self.generators) > 6:
            raise ContractError("AT_MOST_SIX_SHARED_GENERATORS_REQUIRED")
        for generator in self.generators:
            _moments(generator)
        if not isinstance(self.generator_ids, tuple) or len(self.generator_ids) != len(self.generators):
            raise ContractError("ONE_EXPLICIT_ID_PER_SHARED_GENERATOR_REQUIRED")
        for generator_id in self.generator_ids:
            _label(generator_id, "NONEMPTY_GENERATOR_ID_REQUIRED")
        if len(set(self.generator_ids)) != len(self.generator_ids):
            raise ContractError("UNIQUE_GENERATOR_IDS_REQUIRED")
        if not isinstance(self.context, FixedContext):
            raise ContractError("EXPLICIT_FIXED_CONTEXT_REQUIRED")
        _label(self.family_id, "EXPLICIT_FAMILY_ID_REQUIRED")
        if self.family_kind not in ("finite_rule_envelope", "supplied_uncertainty"):
            raise ContractError("EXPLICIT_ALLOWED_FAMILY_KIND_REQUIRED")
        if self.gamma_unit != GAMMA_UNIT or self.energy_unit != ENERGY_UNIT:
            raise ContractError("PER_ABSORBER_GAMMA_AND_EV_RATE_UNITS_REQUIRED")
        if self.input_kind != INPUT_KIND:
            raise ContractError("INSTANTANEOUS_MOMENT_FAMILY_REQUIRED_NOT_OWNER_RECORDS")


# q_ell is already a contribution to a derivative in ln a. Do not divide again.
DLN_A_NAMES = {
    "h_dt_s": "h_dln_a",
    "heii_dt_s": "heii_dln_a",
    "heiii_dt_s": "heiii_dln_a",
    "electron_dt_per_h_s": "electron_dln_a_per_h",
    "heat_erg_h_s": "heat_erg_h_dln_a",
    "binding_erg_h_s": "binding_erg_h_dln_a",
    "absorbed_erg_h_s": "absorbed_erg_h_dln_a",
    "temperature_dt_k_s": "temperature_dln_a_k",
    "heating_temperature_dt_k_s": "heating_temperature_dln_a_k",
    "particle_temperature_dt_k_s": "particle_temperature_dln_a_k",
}


@dataclass(frozen=True)
class ConditionalEnclosure:
    context: FixedContext
    family_id: str
    family_kind: str
    generator_ids: tuple[str, ...]
    chi_ev: tuple[F, F, F]
    premises: tuple[str, ...]
    center_native: Mapping[str, F]
    generators_native: tuple[Mapping[str, F], ...]
    bounds_native: Mapping[str, tuple[F, F]]
    bounds_dln_a: Mapping[str, tuple[F, F]]
    minimum_gamma: tuple[F, F, F]
    minimum_excess_ev_rate: tuple[F, F, F]
    algebra_status: str = "conditional_exact_affine_image"
    physical_status: str = "HOLD"
    uncertainty_truth: str = "UNVERIFIED_EXTERNAL_PREMISES"
    joint_image_retained: bool = True
    history_integrated: bool = False
    common_spectrum_realizability: str = "NOT_ESTABLISHED_NECESSARY_MARGINAL_CHECKS_ONLY"

    def as_json(self) -> dict:
        """Lossless rational serialization; no implicit binary64 conversion."""
        def rat(x: F) -> str:
            return str(x.numerator) + "/" + str(x.denominator)
        def bounds(values):
            return {k: [rat(a), rat(b)] for k, (a, b) in values.items()}
        return {
            "schema": "igm-conditional-joint-moment/v1",
            "context": {
                **{k: getattr(self.context, k) for k in
                   ("source_id", "clock_id", "state_id", "provider_id", "clock")},
                "bound_state": {k: rat(v) for k, v in self.context.bound_state.__dict__.items()},
                "epoch_ln_a": rat(self.context.epoch_ln_a),
                "chi_ev": [rat(v) for v in self.context.chi_ev],
            },
            "premises": list(self.premises),
            "family_id": self.family_id,
            "family_kind": self.family_kind,
            "generator_ids": list(self.generator_ids),
            "input_kind": INPUT_KIND,
            "input_units": {"gamma": GAMMA_UNIT, "incident_energy": ENERGY_UNIT},
            "chi_ev": [rat(v) for v in self.chi_ev],
            "center_native": {k: rat(v) for k, v in self.center_native.items()},
            "generators_native": [{k: rat(v) for k, v in g.items()} for g in self.generators_native],
            "bounds_native": bounds(self.bounds_native),
            "bounds_dln_a": bounds(self.bounds_dln_a),
            "minimum_gamma": [rat(v) for v in self.minimum_gamma],
            "minimum_excess_ev_rate": [rat(v) for v in self.minimum_excess_ev_rate],
            "algebra_status": self.algebra_status,
            "physical_status": self.physical_status,
            "uncertainty_truth": self.uncertainty_truth,
            "joint_image_retained": self.joint_image_retained,
            "history_integrated": self.history_integrated,
            "common_spectrum_realizability": self.common_spectrum_realizability,
        }


def conditional_joint_enclosure(
    state: State,
    chi_ev: Sequence[F],
    family: JointMomentFamily,
    *,
    context: FixedContext,
    premises: Sequence[str] | None,
) -> ConditionalEnclosure:
    """Return an exact linear image, conditional on explicitly supplied premises.

    Necessary marginal conditions are imposed on the ENTIRE affine family.
    This does not establish realization by one common nonnegative spectrum.
    Positivity is imposed without clipping
    or intersecting it with a smaller feasible set. For a linear constraint its
    minimum is center - sum(abs(generator)), exactly the minimum over all 2**m
    vertices. Thus nonnegative minima certify every vertex, including m=0.
    Per-output bounds are marginal extrema; the retained projected generators
    encode their joint correlation. Independent endpoint choices are not a
    claim of a jointly realizable output vector.
    """
    if (not isinstance(premises, (tuple, list)) or not premises or
            any(not isinstance(p, str) or not p.strip() for p in premises)):
        raise MissingPremise("NONEMPTY_EXPLICIT_EXTERNAL_PREMISES_REQUIRED")
    if not isinstance(family, JointMomentFamily):
        raise ContractError("JOINT_AFFINE_MOMENT_FAMILY_REQUIRED")
    family.__post_init__()
    if not isinstance(context, FixedContext):
        raise ContractError("EXPLICIT_FIXED_CONTEXT_REQUIRED")
    context.__post_init__()
    if family.context != context:
        raise ContractError("SOURCE_CLOCK_STATE_PROVIDER_CONTEXT_MISMATCH")
    if not isinstance(state, State) or state != context.bound_state:
        raise ContractError("SAME_FIXED_STATE_REQUIRED")
    if not isinstance(chi_ev, (tuple, list)) or len(chi_ev) != 3 or any(not isinstance(v, F) or v <= 0 for v in chi_ev):
        raise ContractError("THREE_EXACT_POSITIVE_THRESHOLDS_REQUIRED")
    if tuple(chi_ev) != context.chi_ev:
        raise ContractError("FIXED_CONTEXT_THRESHOLD_MISMATCH")
    minima_gamma = tuple(
        family.center.gamma[i] - sum((abs(g.gamma[i]) for g in family.generators), F(0))
        for i in range(3))
    minima_excess = tuple(
        family.center.energy_ev_s[i] - chi_ev[i] * family.center.gamma[i]
        - sum((abs(g.energy_ev_s[i] - chi_ev[i] * g.gamma[i])
               for g in family.generators), F(0))
        for i in range(3))
    if any(v < 0 for v in minima_gamma):
        raise ContractError("NEGATIVE_GAMMA_IN_AFFINE_FAMILY")
    if any(v < 0 for v in minima_excess):
        raise ContractError("SUBTHRESHOLD_EXCESS_IN_AFFINE_FAMILY")
    # A zero rate cannot carry positive incident energy under the same finite,
    # nonnegative spectral weights. Testing vertices covers every zero-rate
    # face because both moments are affine and Gamma is nonnegative throughout.
    for signs in product((-1, 1), repeat=len(family.generators)):
        for i in range(3):
            gamma = family.center.gamma[i] + sum(
                (s*g.gamma[i] for s, g in zip(signs, family.generators)), F(0))
            energy = family.center.energy_ev_s[i] + sum(
                (s*g.energy_ev_s[i] for s, g in zip(signs, family.generators)), F(0))
            if gamma == 0 and energy != 0:
                raise ContractError("ZERO_GAMMA_REQUIRES_ZERO_INCIDENT_ENERGY")
    center = project(state, family.center, chi_ev)
    generators = tuple(project(state, g, chi_ev) for g in family.generators)
    radii = {k: sum((abs(g[k]) for g in generators), F(0)) for k in center}
    native = {k: (v-radii[k], v+radii[k]) for k, v in center.items()}
    dln_a = {DLN_A_NAMES[k]: (lo/state.hubble_s, hi/state.hubble_s)
             for k, (lo, hi) in native.items() if k != "photo_q_ell_source"}
    dln_a["photo_q_ell_source"] = native["photo_q_ell_source"]
    return ConditionalEnclosure(context, family.family_id, family.family_kind,
                                family.generator_ids, tuple(chi_ev), tuple(premises), center, generators,
                                native, dln_a, minima_gamma, minima_excess)
