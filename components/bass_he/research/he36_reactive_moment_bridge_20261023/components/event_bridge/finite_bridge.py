"""Preserve the finite-source provider's temperature/mass/mapping identity.

The finite evaluator is copied unchanged. This adapter is not a microscopic
source admission or a physical high-energy-tail/error certificate. It never
interprets an underflowed positive moment as an all-zero physical channel.

``from_finite_evaluation`` returns a qualified record containing RawMoments.
Use ``record.binary_loss(...)`` for pair calculations: it retains the mapping
gate. Its raw values are exposed for audit/radial diagnostics, not as permission
to bypass that gate. The actual CCC fixed-target incident-electron convention
can only enter the radial-diagnostic route in this package. A finite-mass pair
requires an explicitly manufactured relative-energy table with matched mu.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math

import numpy as np

from .maxwellian_moments import MomentEvaluation, PreparedMaxwellianMoments
from .reactive_moments import (
    MOMENT_ROUNDOFF, RawMoments, MomentDomainError, MomentRepresentabilityError,
    _muldiv, _scalar, binary_loss, mass_fractions,
)
from .vendor.rei_resolved_local import Unresolved


RADIAL_DIAGNOSTIC = "finite_source_radial_diagnostic"
MANUFACTURED_PAIR = "manufactured_relative_energy_pair"


def _type_name(value):
    kind = type(value)
    return kind.__module__ + "." + kind.__qualname__


def _reduced_mass(ma, mb):
    ma = _scalar(ma, "ma", positive=True)
    mb = _scalar(mb, "mb", positive=True)
    a, b = mass_fractions(ma, mb)
    # min mass times the larger mass fraction avoids forming ma+mb or ma*mb.
    return _muldiv((ma, b), label="reduced_mass") if ma <= mb else _muldiv((mb, a), label="reduced_mass")


def _mass_match(ma, mb, expected):
    actual = _reduced_mass(ma, mb)
    scale = max(actual, expected)
    if abs(actual / scale - expected / scale) > MOMENT_ROUNDOFF:
        raise MomentDomainError("FINITE_SOURCE_REDUCED_MASS_IDENTITY_MISMATCH")


@dataclass(frozen=True, slots=True)
class FiniteMomentRecord:
    """A selected provider row with its original type and source conventions.

    Temperature is copied from the selected row; no replacement T is accepted
    during conversion. ``energy_mass_kg`` is intentionally not always called
    mu: the CCC branch uses electron incident lab energy and the fixed-target
    mass m_e. A generic finite-mass mapping is not inferred from that label.
    """
    raw_moments: RawMoments
    identity: str
    source_id: str
    original_evaluation_type: str
    original_prepared_type: str
    index: int
    temperature_K: float
    energy_mass_kg: float
    energy_mapping: str
    usage: str
    source_interval_eV: tuple[float, float]
    numerical_temperature_domain_K: tuple[float, float]
    source_coverage_json: str
    finite_source_partial: bool = True
    physical_tail_bound_established: bool = False
    full_physical_rate: bool = False

    def for_pair(self, ma, mb, T):
        """Return the audited RawMoments only after explicit pair-domain gates."""
        if self.usage != MANUFACTURED_PAIR or self.energy_mapping != "manufactured_relative_energy":
            raise Unresolved("ACTUAL_FIXED_TARGET_OR_DIAGNOSTIC_MOMENTS_NOT_ADMITTED_TO_FINITE_MASS_PAIR")
        temperature = _scalar(T, "T", positive=True)
        if temperature != self.temperature_K:
            raise MomentDomainError("FINITE_SOURCE_TEMPERATURE_IDENTITY_MISMATCH")
        _mass_match(ma, mb, self.energy_mass_kg)
        return self.raw_moments

    def binary_loss(self, na, nb, ma, mb, T, pi_a, pi_b, *, linear_response,
                    grad_budget=None):
        moments = self.for_pair(ma, mb, T)
        return binary_loss(na, nb, ma, mb, T, pi_a, pi_b, moments,
                           linear_response=linear_response, grad_budget=grad_budget)


def from_finite_evaluation(prepared, evaluation, index, *,
                           acknowledge_finite_source_partial,
                           usage, pair_masses_kg=None):
    """Convert one finite evaluator row without changing its T/energy meaning.

    ``usage`` is explicitly RADIAL_DIAGNOSTIC or MANUFACTURED_PAIR. The latter
    additionally requires ``pair_masses_kg=(ma,mb)`` and a manufactured relative
    energy mapping with its matching reduced mass. Actual fixed-target CCC
    moments cannot choose it, including via a numerically near-m_e mass pair.

    The primitive RawMoments' physical feasibility check is necessary, not a
    source validation. A genuinely all-zero table is a *declared finite-support
    zero* only, still partial; omitted physical source support remains unknown.
    """
    if not isinstance(prepared, PreparedMaxwellianMoments) or not isinstance(evaluation, MomentEvaluation):
        raise MomentDomainError("ORIGINAL_PREPARED_AND_MOMENT_EVALUATION_TYPES_REQUIRED")
    if acknowledge_finite_source_partial is not True:
        raise Unresolved("FINITE_SOURCE_PARTIAL_MUST_BE_ACKNOWLEDGED")
    if evaluation.finite_source_partial is not True or evaluation.physical_tail_bound_established is not False:
        raise MomentDomainError("FINITE_PROVIDER_SCOPE_METADATA_MISMATCH")
    if evaluation.identity != prepared.identity:
        raise MomentDomainError("PREPARED_EVALUATION_IDENTITY_MISMATCH")
    if isinstance(index, (bool, np.bool_)) or not isinstance(index, (int, np.integer)):
        raise MomentDomainError("INTEGER_NONNEGATIVE_ROW_INDEX_REQUIRED")
    temps = np.asarray(evaluation.temperature_K)
    if temps.ndim != 1 or temps.dtype.kind not in "fiu":
        raise MomentDomainError("ORIGINAL_TEMPERATURE_VECTOR_REQUIRED")
    n = len(temps)
    if index < 0 or index >= n:
        raise MomentDomainError("FINITE_EVALUATION_INDEX_OUT_OF_RANGE")
    index = int(index)
    temperature = _scalar(temps[index], "original_temperature_K", positive=True)
    lo, hi = prepared.temperature_domain_K
    if not lo <= temperature <= hi:
        raise MomentDomainError("ORIGINAL_TEMPERATURE_OUTSIDE_PROVIDER_DOMAIN")
    values = np.asarray(evaluation.moments_SI)
    logs = np.asarray(evaluation.log_moments_SI)
    underflow = np.asarray(evaluation.underflow)
    if (values.shape != (n, 4) or values.dtype.kind not in "fiu"
            or logs.shape != (n, 4) or logs.dtype.kind not in "fiu"
            or underflow.shape != (n, 4) or underflow.dtype.kind != "b"):
        raise MomentDomainError("ORIGINAL_MOMENT_OR_FLAG_SHAPE_TYPE_MISMATCH")
    if np.any(underflow[index, :3]):
        raise MomentRepresentabilityError("ALPHA_BETA_GAMMA_UNDERFLOW_CANNOT_BECOME_PHYSICAL_ZERO")
    moment_values = tuple(_scalar(value, "finite_moment", nonnegative=True)
                          for value in values[index, :3])
    if evaluation.zero_tabulated_integral != prepared.zero_tabulated_integral:
        raise MomentDomainError("DECLARED_ZERO_TABLE_IDENTITY_MISMATCH")
    if prepared.zero_tabulated_integral:
        if any(moment_values) or not np.all(np.isneginf(logs[index, :3])):
            raise MomentDomainError("DECLARED_ZERO_TABLE_HAS_NONZERO_MOMENT_OR_LOG")
        zero_reason = "declared zero tabulated finite integral; no full physical-rate zero claim"
    else:
        if any(value == 0 for value in moment_values):
            raise MomentRepresentabilityError("NONZERO_FINITE_TABLE_HAS_ZERO_ALPHA_BETA_OR_GAMMA")
        for value, log_value in zip(moment_values, logs[index, :3]):
            original_log = _scalar(log_value, "original_log_moment")
            if abs(math.log(value) - original_log) > MOMENT_ROUNDOFF * max(1.0, abs(original_log)):
                raise MomentDomainError("MOMENT_VALUE_LOG_IDENTITY_MISMATCH")
        zero_reason = None
    if usage not in (RADIAL_DIAGNOSTIC, MANUFACTURED_PAIR):
        raise MomentDomainError("EXPLICIT_FINITE_SOURCE_USAGE_REQUIRED")
    if usage == MANUFACTURED_PAIR:
        if prepared.energy_mapping != "manufactured_relative_energy":
            raise Unresolved("INCIDENT_LAB_ENERGY_CANNOT_BE_SILENTLY_RELABELLED_AS_RELATIVE_ENERGY")
        if not isinstance(pair_masses_kg, (tuple, list)) or len(pair_masses_kg) != 2:
            raise MomentDomainError("EXPLICIT_FINITE_PAIR_MASSES_REQUIRED")
        _mass_match(*pair_masses_kg, prepared.reduced_mass_kg)
    elif pair_masses_kg is not None:
        raise MomentDomainError("DIAGNOSTIC_ROUTE_DOES_NOT_ACCEPT_FINITE_PAIR_MASSES")
    metadata = dict(source_id=prepared.source_id, identity=prepared.identity,
        original_evaluation_type=_type_name(evaluation), original_prepared_type=_type_name(prepared),
        index=index, temperature_K=temperature, energy_mapping=prepared.energy_mapping,
        energy_mass_kg=prepared.reduced_mass_kg, usage=usage,
        finite_source_partial=True, full_physical_rate=False,
        physical_tail_bound_established=False)
    raw = RawMoments(*moment_values,
        provenance=json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        interpretation="finite_source_partial:" + usage,
        temperature_K=temperature, zero_reason=zero_reason)
    return FiniteMomentRecord(raw, prepared.identity, prepared.source_id,
        _type_name(evaluation), _type_name(prepared), index, temperature,
        prepared.reduced_mass_kg, prepared.energy_mapping, usage,
        (float(prepared.energy_eV[0]), float(prepared.energy_eV[-1])), (lo, hi),
        json.dumps(prepared.coverage(), sort_keys=True, separators=(",", ":")))
