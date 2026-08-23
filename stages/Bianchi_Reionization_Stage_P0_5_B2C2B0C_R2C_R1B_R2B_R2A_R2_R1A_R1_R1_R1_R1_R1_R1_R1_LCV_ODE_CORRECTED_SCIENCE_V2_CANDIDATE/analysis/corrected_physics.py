"""Single-convention per-hydrogen opacity and direct-share shadow kernel."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import math
from typing import Sequence

import verified_backend as vb


ATOMIC_SPECIES = ("HI", "HeI", "HeII")


class _NonfinitePhysicalInput(ValueError):
    pass


class PhysicsStatus(StrEnum):
    OK = "OK"
    AMBIGUOUS_NUMERIC_PROVENANCE = "AMBIGUOUS_NUMERIC_PROVENANCE"
    INVALID_SHAPE = "INVALID_SHAPE"
    NONFINITE_INPUT = "NONFINITE_INPUT"
    NEGATIVE_POPULATION = "NEGATIVE_POPULATION"
    NEGATIVE_CROSS_SECTION = "NEGATIVE_CROSS_SECTION"
    NEGATIVE_CURRENT = "NEGATIVE_CURRENT"
    HYDROGEN_REFERENCE_VACUUM = "HYDROGEN_REFERENCE_VACUUM"
    ABUNDANCE_CONVENTION_MISMATCH = "ABUNDANCE_CONVENTION_MISMATCH"
    ZERO_OPACITY_VACUUM = "ZERO_OPACITY_VACUUM"
    NONZERO_CURRENT_WITH_ZERO_OPACITY = "NONZERO_CURRENT_WITH_ZERO_OPACITY"
    NUMERIC_OVERFLOW = "NUMERIC_OVERFLOW"
    EXACT_RESOURCE_LIMIT = "EXACT_RESOURCE_LIMIT"
    VACUUM_POLICY_UNRESOLVED = "VACUUM_POLICY_UNRESOLVED"


@dataclass(frozen=True)
class AtomicOpacityResult:
    status: PhysicsStatus
    species: tuple[str, ...]
    per_h_abundance_exact: tuple[Fraction, ...] | None
    raw_exact: tuple[Fraction, ...] | None
    raw_binary64: tuple[vb.Binary64Interval, ...] | None
    detail: str = ""


@dataclass(frozen=True)
class OpacityPartition:
    status: PhysicsStatus
    owner_names: tuple[str, ...]
    raw_exact: tuple[Fraction, ...] | None
    total_exact: Fraction | None
    shares_exact: tuple[Fraction, ...] | None
    shares_binary64: tuple[vb.Binary64Interval, ...] | None
    detail: str = ""


def _fraction(value) -> Fraction:
    if isinstance(value, vb.ExactScalar):
        exact = value.value
        if not vb.fraction_within_resource(exact):
            raise OverflowError("exact physical scalar exceeds fixed resource ceiling")
        return exact
    if isinstance(value, Fraction):
        if not vb.fraction_within_resource(value):
            raise OverflowError("exact physical scalar exceeds fixed resource ceiling")
        return value
    if isinstance(value, bool):
        raise TypeError("boolean has ambiguous physical provenance")
    if isinstance(value, int):
        exact = Fraction(value)
        if not vb.fraction_within_resource(exact):
            raise OverflowError("exact physical scalar exceeds fixed resource ceiling")
        return exact
    if isinstance(value, float):
        if not math.isfinite(value):
            raise _NonfinitePhysicalInput("raw binary64 physics input is nonfinite")
        raise TypeError("raw binary64 physics input must be explicitly provenance-tagged")
    raise TypeError("physical scalar must be ExactScalar, Fraction, or integer")


def _atomic_failure(status: PhysicsStatus, detail: str) -> AtomicOpacityResult:
    return AtomicOpacityResult(status, ATOMIC_SPECIES, None, None, None, detail)


def _partition_failure(status: PhysicsStatus, names: tuple[str, ...], detail: str, raw=None, total=None) -> OpacityPartition:
    return OpacityPartition(status, names, raw, total, None, None, detail)


def _convert_all(values: Sequence[Fraction]):
    converted = []
    for value in values:
        result = vb.outward_binary64(value)
        if result.status is not vb.NumericStatus.OK:
            return result.status, None, result.detail
        converted.append(result.value)
    return vb.NumericStatus.OK, tuple(converted), ""


def atomic_opacity_per_h(
    *,
    absorber_counts,
    hydrogen_nuclei_total,
    sigma_cm2,
    geometric_scale,
    helium_nuclei_total=None,
    declared_yhe=None,
) -> AtomicOpacityResult:
    """Compute each atomic opacity from ``N_species/N_H`` exactly.

    No literal helium abundance occurs in the formula.  A pure-He absorber
    carries one abundance factor because it is already present in ``N_s/N_H``.
    """

    try:
        counts = tuple(_fraction(item) for item in absorber_counts)
        sigma = tuple(_fraction(item) for item in sigma_cm2)
        hydrogen = _fraction(hydrogen_nuclei_total)
        scale = _fraction(geometric_scale)
        helium = None if helium_nuclei_total is None else _fraction(helium_nuclei_total)
        convention = None if declared_yhe is None else _fraction(declared_yhe)
    except _NonfinitePhysicalInput as exc:
        return _atomic_failure(PhysicsStatus.NONFINITE_INPUT, str(exc))
    except OverflowError as exc:
        return _atomic_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, str(exc))
    except TypeError as exc:
        return _atomic_failure(PhysicsStatus.AMBIGUOUS_NUMERIC_PROVENANCE, str(exc))
    if len(counts) != len(ATOMIC_SPECIES) or len(sigma) != len(ATOMIC_SPECIES):
        return _atomic_failure(PhysicsStatus.INVALID_SHAPE, "three atomic species are required")
    if any(value < 0 for value in counts) or hydrogen < 0 or (helium is not None and helium < 0):
        return _atomic_failure(PhysicsStatus.NEGATIVE_POPULATION, "population/count input is negative")
    if any(value < 0 for value in sigma) or scale < 0:
        return _atomic_failure(PhysicsStatus.NEGATIVE_CROSS_SECTION, "cross section/geometric scale is negative")
    if hydrogen == 0:
        return _atomic_failure(PhysicsStatus.HYDROGEN_REFERENCE_VACUUM, "per-H normalization is undefined at N_H=0")
    if (helium is None) != (convention is None):
        return _atomic_failure(PhysicsStatus.INVALID_SHAPE, "helium total and declared YHE must be provided together")
    if helium is not None and helium / hydrogen != convention:
        return _atomic_failure(
            PhysicsStatus.ABUNDANCE_CONVENTION_MISMATCH,
            "exact helium/hydrogen inventory ratio differs from declared YHE",
        )
    abundances = tuple(value / hydrogen for value in counts)
    raw = tuple(scale * abundance * cross_section for abundance, cross_section in zip(abundances, sigma))
    if any(not vb.fraction_within_resource(item) for item in abundances + raw):
        return _atomic_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, "exact opacity exceeds fixed resource ceiling")
    status, binary, detail = _convert_all(raw)
    if status is vb.NumericStatus.BINARY64_OVERFLOW:
        return _atomic_failure(PhysicsStatus.NUMERIC_OVERFLOW, detail)
    if status is not vb.NumericStatus.OK:
        return _atomic_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, detail)
    return AtomicOpacityResult(
        PhysicsStatus.OK,
        ATOMIC_SPECIES,
        abundances,
        raw,
        binary,
        "opacity uses N_species/N_H exactly once",
    )


def direct_opacity_partition(
    *,
    owner_names,
    raw_opacity,
    authoritative_current=None,
) -> OpacityPartition:
    """Normalize nonnegative opacity measures with no complement or floor."""

    names = tuple(str(item) for item in owner_names)
    try:
        raw = tuple(_fraction(item) for item in raw_opacity)
        current = None if authoritative_current is None else _fraction(authoritative_current)
    except _NonfinitePhysicalInput as exc:
        return _partition_failure(PhysicsStatus.NONFINITE_INPUT, names, str(exc))
    except OverflowError as exc:
        return _partition_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, names, str(exc))
    except TypeError as exc:
        return _partition_failure(PhysicsStatus.AMBIGUOUS_NUMERIC_PROVENANCE, names, str(exc))
    if not names or len(names) != len(raw) or len(set(names)) != len(names):
        return _partition_failure(PhysicsStatus.INVALID_SHAPE, names, "owner names and measures must be unique and aligned")
    if any(value < 0 for value in raw):
        return _partition_failure(PhysicsStatus.NEGATIVE_CROSS_SECTION, names, "raw opacity is negative")
    if current is not None and current < 0:
        return _partition_failure(PhysicsStatus.NEGATIVE_CURRENT, names, "authoritative current is negative")
    total = sum(raw, Fraction(0))
    if not vb.fraction_within_resource(total):
        return _partition_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, names, "exact opacity total exceeds fixed resource ceiling")
    if total == 0:
        if current is not None and current != 0:
            return _partition_failure(
                PhysicsStatus.NONZERO_CURRENT_WITH_ZERO_OPACITY,
                names,
                "nonzero current has no absorbing support",
                raw,
                total,
            )
        return _partition_failure(
            PhysicsStatus.ZERO_OPACITY_VACUUM,
            names,
            "shares are undefined in zero opacity; no normalized zero vector is emitted",
            raw,
            total,
        )
    shares = tuple(value / total for value in raw)
    if any(not vb.fraction_within_resource(item) for item in shares):
        return _partition_failure(PhysicsStatus.EXACT_RESOURCE_LIMIT, names, "exact share exceeds fixed resource ceiling", raw, total)
    status, binary, detail = _convert_all(shares)
    if status is not vb.NumericStatus.OK:
        mapped = PhysicsStatus.NUMERIC_OVERFLOW if status is vb.NumericStatus.BINARY64_OVERFLOW else PhysicsStatus.EXACT_RESOURCE_LIMIT
        return _partition_failure(mapped, names, detail, raw, total)
    return OpacityPartition(
        PhysicsStatus.OK,
        names,
        raw,
        total,
        shares,
        binary,
        "all owner shares are direct raw_i/sum(raw); no subtractive complement",
    )


__all__ = [
    "ATOMIC_SPECIES",
    "AtomicOpacityResult",
    "OpacityPartition",
    "PhysicsStatus",
    "atomic_opacity_per_h",
    "direct_opacity_partition",
]
