"""Attach a supplied net kinetic tensor to the unchanged REI scalar event.

This is a unit/frame/ownership adapter, not a daughter-spectrum, nuclear-rate,
stopping, or reaction-gain provider.  The donor's ``ResolvedEvent.evaluate``
owns its event rate, stoichiometry, electron census, and signed energy ledger.
The exact donor is ``vendor/rei_resolved_local.py``; pin and byte hashes are in
DONOR_PROVENANCE.json.  Its execution contract section 3 specifies J/event for
all nine ledger terms, and events/(baryon s) for a row rate when Y_i=n_i/n_B.

For a fully supplied *net* central kinetic second moment C_event [J/event],

    S = n_B * row.rate * C_event                  [Pa/s]
    Q = tr(S)/2 = n_B * row.rate * dEth           [W/m^3]
    J = S - (2Q/3) I                             [Pa/s]
    Rpart = n_B * row.thermal_particle_source    [m^-3/s].

Here pi is the STF part of the pressure tensor and J=dpi/dt is its reaction
source in the specified common bulk frame.  The input includes all incoming
removal AND all outgoing thermal gain for this single resolved event.  It may
be signed/indefinite; it is a source, not a covariance.  If those parts were
computed separately, their signed tensors and Q values must first be summed;
tr(C_event)/2 must equal the donor's *net* dEth.  Removed-parent Q is not net
cooling.  The returned Q and the donor dEth reservoir have ONE owner and must
never be added to one another.  Unknown product/birth moments remain unresolved
even when the scalar event rate happens to vanish at the supplied state.

The 21-state charge census is explicitly neutral and excludes positrons and
negative ions. Rpart is a *thermal* count only when all retained nuclei and
free electrons are thermal. This adapter requires that declaration and dEfast=0.
A separate fast-particle number source would have to be subtracted from the
thermal count; a fast energy reservoir alone cannot supply that number.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from collections.abc import Mapping

import numpy as np

from .reactive_moments import (
    MOMENT_ROUNDOFF, MomentDomainError, MomentRepresentabilityError,
    _matrix, _muldiv, _readonly, _scalar, _sum,
)
from .vendor.rei_resolved_local import Coefficient, ResolvedEvent, Unresolved


NET_TENSOR_SCOPE = "complete_net_thermal_central_second_moment"
CENTRAL_FRAME = "common_bulk_central"
EVENT_ENERGY_UNIT = "J/event"
ALL_RETAINED_THERMAL = "all_retained_nuclei_and_free_electrons_thermal"
NEUTRAL_21_STATE_CENSUS = "charge_neutral_21state_no_positrons_or_negative_ions"


def _real_array(value, shape, name):
    original = np.asarray(value)
    if original.dtype.kind not in "fiu" or original.shape != shape:
        raise MomentDomainError(name + ": REAL_ARRAY_WITH_REQUIRED_SHAPE")
    array = np.asarray(original, dtype=float)
    if not np.isfinite(array).all():
        raise MomentDomainError(name + ": FINITE_VALUES_REQUIRED")
    return _readonly(array)


def _half_trace(matrix, *, label):
    # Avoid forming tr(matrix) before division: it can overflow although Q fits.
    scale = max(abs(float(matrix[i, i])) for i in range(3))
    if scale == 0:
        return 0.0
    trace_scaled = math.fsum(float(matrix[i, i]) / scale for i in range(3))
    return _muldiv((scale, trace_scaled), (2.0,), label=label)


def _energy_match(actual, expected, *, label):
    scale = max(abs(actual), abs(expected))
    defect = 0.0 if scale == 0 else abs(actual / scale - expected / scale)
    if defect > MOMENT_ROUNDOFF:
        raise MomentDomainError(label + ": TENSOR_TRACE_DOES_NOT_MATCH_DETH")
    return defect


def _freeze(value):
    if isinstance(value, np.ndarray):
        result = np.asarray(value)
        return np.frombuffer(result.tobytes(), dtype=result.dtype).reshape(result.shape)
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class EventTensorSource:
    """A single resolved event's net thermal pressure/number sources.

    ``row`` is an immutable snapshot of the actual donor result. ``Q`` and
    ``reservoir_sources_W_m3['dEth']`` are two views of the same energy owner.
    There is no extra EOS dilution term inside Q; the number change Rpart is
    separately available to an explicitly chosen temperature/EOS equation.
    """
    row: Mapping
    S: np.ndarray
    Q: float
    J: np.ndarray
    Rpart: float
    Rnucleus: float
    Relectron: float
    R_species: np.ndarray
    volumetric_event_rate: float
    reservoir_sources_W_m3: Mapping
    per_event_tensor_J: np.ndarray
    tensor_provenance: str
    per_event_energy_normalized_defect: float
    volume_energy_normalized_defect: float
    stf_trace_normalized_to_source: float
    tensor_scope: str = NET_TENSOR_SCOPE
    central_frame: str = CENTRAL_FRAME
    event_energy_unit: str = EVENT_ENERGY_UNIT
    pressure_source_unit: str = "Pa/s"
    heat_source_unit: str = "W/m^3"
    number_source_unit: str = "m^-3/s"
    thermal_inventory_scope: str = ALL_RETAINED_THERMAL
    charge_census_scope: str = NEUTRAL_21_STATE_CENSUS
    scope: str = "supplied_net_event_tensor_only_no_physical_provider_admission"


def attach_event_tensor(event, Y, nb, *, per_event_tensor_J=None,
                        energy_unit=None, tensor_scope=None,
                        central_frame=None, tensor_provenance="",
                        thermal_inventory_scope=None, charge_census_scope=None):
    """Attach one explicit complete net central tensor to one donor event.

    Required labels are ``energy_unit='J/event'``,
    ``tensor_scope=NET_TENSOR_SCOPE``, and ``central_frame=CENTRAL_FRAME``.
    Also require ``thermal_inventory_scope=ALL_RETAINED_THERMAL`` and
    ``charge_census_scope=NEUTRAL_21_STATE_CENSUS``; nonzero dEfast is unresolved
    here because it does not specify a separate fast-particle number source.
    The adapter performs no unit conversion and no reaction-gain inference.
    A missing tensor raises donor ``Unresolved`` rather than choosing J=0.
    An unrepresentable positive donor rate or reservoir source is rejected;
    it is not reclassified as physical/support zero. Finite subnormals survive.

    ``event`` must be the vendored donor class. Caller-owned donor events must
    not be mutated after construction; their construction validates scalar
    conservation/energy rules in the unchanged donor code.
    """
    if not isinstance(event, ResolvedEvent):
        raise MomentDomainError("PINNED_REI_RESOLVED_EVENT_REQUIRED")
    if per_event_tensor_J is None:
        raise Unresolved("MISSING_COMPLETE_NET_PRODUCT_AND_REMOVAL_TENSOR")
    if energy_unit != EVENT_ENERGY_UNIT:
        raise MomentDomainError("EXPLICIT_J_PER_EVENT_LABEL_REQUIRED_NO_CONVERSION")
    if tensor_scope != NET_TENSOR_SCOPE:
        raise Unresolved("COMPLETE_NET_THERMAL_TENSOR_SCOPE_REQUIRED")
    if central_frame != CENTRAL_FRAME:
        raise Unresolved("EXPLICIT_COMMON_BULK_CENTRAL_FRAME_REQUIRED")
    if not isinstance(tensor_provenance, str) or not tensor_provenance.strip():
        raise Unresolved("MISSING_SUPPLIED_TENSOR_PROVENANCE")
    if thermal_inventory_scope != ALL_RETAINED_THERMAL:
        raise Unresolved("EXPLICIT_ALL_RETAINED_PARTICLES_THERMAL_SCOPE_REQUIRED")
    if charge_census_scope != NEUTRAL_21_STATE_CENSUS:
        raise Unresolved("EXPLICIT_NEUTRAL_21_STATE_NO_POSITRON_NEGATIVE_ION_CENSUS_REQUIRED")
    if event.energy["dEfast"] != 0:
        raise Unresolved("FAST_ENERGY_RESERVOIR_DOES_NOT_SUPPLY_FAST_PARTICLE_NUMBER_SOURCE")
    density = _scalar(nb, "nb", nonnegative=True)
    y = _real_array(Y, (21,), "Y")
    if np.any(y < 0):
        raise MomentDomainError("Y: NONNEGATIVE_ABSOLUTE_ABUNDANCES_REQUIRED")
    per_event, _, _, _ = _matrix(per_event_tensor_J,
                                 "per_event_tensor_J", traceless=False)
    dEth = _scalar(event.energy["dEth"], "dEth_J_per_event")
    heat_per_event = _half_trace(per_event, label="event_half_trace")
    per_defect = _energy_match(heat_per_event, dEth, label="per_event_energy")

    # This call is the scalar donor; no rates, stoichiometry or energy algebra
    # are reimplemented here. The row is retained with its original statuses.
    row = event.evaluate(y, density)
    if row["status"] == "REPRESENTATIONAL_UNDERFLOW":
        raise MomentRepresentabilityError("DONOR_EVENT_RATE_UNDERFLOW_NOT_SUPPORT_ZERO")
    if row["status"] not in ("POSITIVE", "SUPPORT_ZERO", "ZERO_DENSITY", "ZERO_REACTANT"):
        raise Unresolved("UNADMITTED_DONOR_ROW_STATUS:" + str(row["status"]))
    rate = _scalar(row["rate"], "donor_row_rate", nonnegative=True)
    if (row["status"] == "POSITIVE") != (rate > 0):
        raise MomentDomainError("INCOHERENT_DONOR_RATE_STATUS")
    for name, value in row["reservoir_sources"].items():
        _scalar(value, "donor_reservoir_" + name)
        if value == 0 and rate != 0 and event.energy[name] != 0:
            raise MomentRepresentabilityError("DONOR_RESERVOIR_UNDERFLOW:" + name)

    s = np.array([[_muldiv((density, rate, float(per_event[i, j])),
                           label="event_tensor_source")
                   for j in range(3)] for i in range(3)])
    heat = _half_trace(s, label="volume_half_trace")
    reservoirs = {name: _muldiv((density, float(value)),
                                label="volume_reservoir_" + name)
                  for name, value in row["reservoir_sources"].items()}
    volume_defect = _energy_match(heat, reservoirs["dEth"], label="volume_energy")
    isotropic = _muldiv((2.0, heat), (3.0,), label="event_isotropic_pressure_source")
    j = np.array(s, copy=True)
    for i in range(3):
        j[i, i] = _sum((float(j[i, i]), -isotropic), label="event_STF")
    # Projection roundoff is measured against the original source scale, not
    # the possibly vanishing STF remainder. No extra trace repair is applied.
    j, _, _, _ = _matrix(j, "event_J", traceless=False)
    source_scale = float(np.max(np.abs(s)))
    stf_defect = 0.0 if source_scale == 0 else abs(math.fsum(float(j[i, i]) / source_scale for i in range(3)))
    if stf_defect > MOMENT_ROUNDOFF:
        raise MomentDomainError("STF_PROJECTION_RESIDUAL_EXCEEDS_SOURCE_SCALED_ROUNDOFF")
    species = [_muldiv((density, float(v)), label="species_number_source")
               for v in row["source"]]
    return EventTensorSource(
        _freeze(row), _readonly(s), heat, j,
        _muldiv((density, float(row["thermal_particle_source"])), label="Rpart"),
        _muldiv((density, float(row["nucleus_source"])), label="Rnucleus"),
        _muldiv((density, float(row["electron_source"])), label="Relectron"),
        _readonly(species), _muldiv((density, rate), label="volume_event_rate"),
        MappingProxyType(reservoirs), per_event, tensor_provenance,
        per_defect, volume_defect, stf_defect,
    )
