#!/usr/bin/env python3
"""Pure photon-owner split used by the R1B-R2A preflight.

The operator allocates opacity and absorbed current by competing non-negative
hazards before any material or thermal source is formed.  It deliberately does
not perform chemistry integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import math
import numpy as np

COMPONENT_OWNER = {
    "EFFECTIVE_HI_SUBGRID": "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC": "RESOLVED_HI",
    "EXPLICIT_HEI_ATOMIC": "RESOLVED_HeI",
    "EXPLICIT_HEII_ATOMIC": "RESOLVED_HeII",
}

SOURCE_COEFFICIENTS = {
    "EFFECTIVE_HI_SUBGRID": {
        "resolved_H": 0,
        "resolved_He": 0,
        "resolved_thermal": 0,
    },
    "EXPLICIT_HI_ATOMIC": {
        "resolved_H": 1,
        "resolved_He": 0,
        "resolved_thermal": 1,
    },
    "EXPLICIT_HEI_ATOMIC": {
        "resolved_H": 0,
        "resolved_He": 1,
        "resolved_thermal": 1,
    },
    "EXPLICIT_HEII_ATOMIC": {
        "resolved_H": 0,
        "resolved_He": 1,
        "resolved_thermal": 1,
    },
}


@dataclass(frozen=True)
class OwnerRow:
    component: str
    owner: str
    kappa: float
    current: float
    fraction: float


@dataclass(frozen=True)
class CapacityCertificate:
    assigned_absorption: float
    capacity: float
    slack: float
    overshoot: float
    feasible: bool


def resolved_source_coefficients(component: str) -> dict[str, int]:
    """Return exact integer material/thermal ownership flags."""
    return dict(SOURCE_COEFFICIENTS[component])


def split_group_by_owner(
    *,
    total_kappa: float,
    total_current: float,
    component_kappa: Mapping[str, float],
    relative_tolerance: float = 1.0e-11,
) -> list[OwnerRow]:
    """Split group opacity/current by competing component hazards.

    The common incident flux is preserved.  A nonzero target on zero support is
    rejected rather than assigned by a fallback prior.
    """
    if not math.isfinite(total_kappa) or not math.isfinite(total_current):
        raise ValueError("non-finite total")
    if total_kappa < 0.0 or total_current < 0.0:
        raise ValueError("negative total")
    unknown = set(component_kappa) - set(COMPONENT_OWNER)
    if unknown:
        raise KeyError(f"unknown components: {sorted(unknown)}")
    values = {name: float(component_kappa.get(name, 0.0)) for name in COMPONENT_OWNER}
    if any((not math.isfinite(v)) or v < 0.0 for v in values.values()):
        raise ValueError("component opacity must be finite and nonnegative")
    support = math.fsum(values.values())
    scale = max(abs(total_kappa), abs(support), 1.0)
    if abs(support - total_kappa) > relative_tolerance * scale:
        raise ValueError(
            f"component opacity does not close: sum={support}, target={total_kappa}"
        )
    if support == 0.0:
        if total_current != 0.0:
            raise ValueError("nonzero current on zero opacity support")
        return [
            OwnerRow(name, COMPONENT_OWNER[name], 0.0, 0.0, 0.0)
            for name in COMPONENT_OWNER
        ]
    phi = total_current / total_kappa if total_kappa > 0.0 else 0.0
    rows = []
    for name, kappa in values.items():
        frac = kappa / support
        rows.append(
            OwnerRow(
                component=name,
                owner=COMPONENT_OWNER[name],
                kappa=kappa,
                current=phi * kappa,
                fraction=frac,
            )
        )
    # One floating-point closure correction is applied to the last supported
    # component; opacity and current retain the same common flux.
    supported = [i for i, r in enumerate(rows) if r.kappa > 0.0]
    if supported:
        i = supported[-1]
        k_correction = total_kappa - math.fsum(r.kappa for r in rows)
        kappa = rows[i].kappa + k_correction
        rows[i] = OwnerRow(
            rows[i].component,
            rows[i].owner,
            kappa,
            phi * kappa,
            kappa / total_kappa if total_kappa > 0.0 else 0.0,
        )
    return rows


def capacity_certificate(
    *,
    assigned_absorption: float,
    initial_reservoir: float,
    recombination_supply: float = 0.0,
    material_inflow: float = 0.0,
    material_outflow: float = 0.0,
    tolerance: float = 1.0e-12,
) -> CapacityCertificate:
    vals = [assigned_absorption, initial_reservoir, recombination_supply, material_inflow, material_outflow]
    if any((not math.isfinite(float(v))) or float(v) < 0.0 for v in vals):
        raise ValueError("capacity inputs must be finite and nonnegative")
    capacity = initial_reservoir + recombination_supply + material_inflow - material_outflow
    if capacity < 0.0:
        raise ValueError("negative net material capacity")
    difference = capacity - assigned_absorption
    scale = max(capacity, assigned_absorption, 1.0)
    feasible = difference >= -tolerance * scale
    return CapacityCertificate(
        assigned_absorption=float(assigned_absorption),
        capacity=float(capacity),
        slack=float(max(difference, 0.0)),
        overshoot=float(max(-difference, 0.0)),
        feasible=bool(feasible),
    )


def disintegrate_owner_current(*, owner_total: float, measure: np.ndarray) -> np.ndarray:
    h = np.asarray(measure, dtype=float)
    if not math.isfinite(float(owner_total)) or owner_total < 0.0:
        raise ValueError("owner total must be finite and nonnegative")
    if h.ndim != 1 or np.any(~np.isfinite(h)) or np.any(h < 0.0):
        raise ValueError("measure must be a finite nonnegative vector")
    support = float(math.fsum(float(x) for x in h))
    if support == 0.0:
        if owner_total != 0.0:
            raise ValueError("nonzero owner total on zero node support")
        return np.zeros_like(h)
    allocation = owner_total * h / support
    positive = np.flatnonzero(h > 0.0)
    allocation[positive[-1]] += owner_total - float(math.fsum(float(x) for x in allocation))
    return allocation
