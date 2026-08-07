#!/usr/bin/env python3
"""Owner-conserving absorbed-count accounting for R1B-R2B.

Absorbed counts are formed per owner from the owner currents produced by the
R1B-R2A competing-hazard split.  Nothing here reassigns photons between owners
and nothing here integrates chemistry.

The resolved-source flags are ownership statements taken from the R1B-R2A
owner registry.  For `EFFECTIVE_HI_SUBGRID` they are exact integer zero, not a
small number: unresolved absorption removes photons and fills the unresolved
energy ledger, and contributes nothing whatsoever to resolved H, He or thermal
state until a separately locked subgrid reservoir and exchange law exist.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

OWNERS = (
    "EFFECTIVE_HI_SUBGRID",
    "RESOLVED_HI",
    "RESOLVED_HeI",
    "RESOLVED_HeII",
)

# (resolved_H, resolved_He, resolved_thermal) ownership flags, exact integers.
SOURCE_FLAGS: dict[str, tuple[int, int, int]] = {
    "EFFECTIVE_HI_SUBGRID": (0, 0, 0),
    "RESOLVED_HI": (1, 0, 1),
    "RESOLVED_HeI": (0, 1, 1),
    "RESOLVED_HeII": (0, 1, 1),
}

OWNER_RELATIVE_RESIDUAL = 1.0e-11


@dataclass(frozen=True)
class ResolvedSources:
    """Absorbed counts routed to each resolved reservoir by ownership.

    `resolved_U` is the absorbed photon count *eligible* to deposit into the
    resolved thermal variable.  Conversion to energy uses the locked R1B-R1
    heating moments downstream; this class only decides ownership.
    """

    owner: str
    resolved_H: float
    resolved_He: float
    resolved_U: float


def _checked(value: object, label: str) -> float:
    x = float(value)  # type: ignore[arg-type]
    if not math.isfinite(x) or x < 0.0:
        raise ValueError(f"{label} must be finite and nonnegative, got {value!r}")
    return x


def absorbed_count_total(*, total_current: float, dt_seconds: float) -> float:
    """Integrate the authoritative group current over the interval."""
    return _checked(total_current, "total_current") * _checked(dt_seconds, "dt_seconds")


def absorbed_counts_by_owner(
    *, owner_currents: Mapping[str, float], dt_seconds: float
) -> dict[str, float]:
    """Integrate each owner current over the interval.

    No owner is invented and none is dropped: the returned mapping has exactly
    the keys it was given.
    """
    dt = _checked(dt_seconds, "dt_seconds")
    unknown = set(owner_currents) - set(OWNERS)
    if unknown:
        raise KeyError(f"unknown owners: {sorted(unknown)}")
    return {
        owner: _checked(current, f"owner current {owner}") * dt
        for owner, current in owner_currents.items()
    }


def owner_counts_close(
    counts: Mapping[str, float],
    total: float,
    *,
    relative_tolerance: float = OWNER_RELATIVE_RESIDUAL,
) -> bool:
    """Test sum_o N_o == N_tot to the locked owner residual tolerance."""
    summed = math.fsum(float(v) for v in counts.values())
    scale = max(abs(summed), abs(float(total)), 1.0)
    return abs(summed - float(total)) <= relative_tolerance * scale


def resolved_sources_for_owner(*, owner: str, absorbed_count: float) -> ResolvedSources:
    """Route an owner's absorbed count to resolved reservoirs by ownership flag."""
    if owner not in SOURCE_FLAGS:
        raise KeyError(f"unknown owner: {owner!r}")
    count = _checked(absorbed_count, "absorbed_count")
    f_h, f_he, f_u = SOURCE_FLAGS[owner]
    # Multiplying by an exact integer flag keeps the zero exact.
    return ResolvedSources(
        owner=owner,
        resolved_H=f_h * count,
        resolved_He=f_he * count,
        resolved_U=f_u * count,
    )
