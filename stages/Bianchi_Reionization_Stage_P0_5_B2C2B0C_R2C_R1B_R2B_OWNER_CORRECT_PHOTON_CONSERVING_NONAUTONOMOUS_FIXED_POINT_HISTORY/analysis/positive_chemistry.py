#!/usr/bin/env python3
"""Positive H/He reaction map for R1B-R2B.

The material state is

    Y = (N_HI, N_HII, N_HeI, N_HeII, N_HeIII, U_resolved)

Nuclei totals are conserved *by construction*, not by tolerance: the partner
species is obtained by subtracting from the locked nuclei total rather than by
accumulating its own increment, so no floating-point drift can open a gap
between `N_HI + N_HII` and `N_H`.

Positivity is enforced by refusing infeasible demand. There is no clipping
anywhere in this module. A clipped state would silently violate nuclei
conservation while still looking physical to every downstream auditor, which is
precisely the failure mode the R1B-R2A owner split was introduced to remove.

Recombination and transfer counts are *inputs*. The input lock forbids a
recombination surrogate, so this module never models a rate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


class InfeasibleReaction(Exception):
    """Raised when demand exceeds interval capacity for some species.

    Carries the offending species so a caller can classify the failure without
    re-deriving it, and so a rejected substep records *why* it was rejected.
    """

    def __init__(self, species: str, deficit: float) -> None:
        super().__init__(
            f"{species} would go negative by {deficit!r}; no clipping is permitted"
        )
        self.species = species
        self.deficit = float(deficit)


def _checked(value: float, label: str) -> float:
    x = float(value)
    if not math.isfinite(x) or x < 0.0:
        raise ValueError(f"{label} must be finite and nonnegative, got {value!r}")
    return x


@dataclass(frozen=True)
class MaterialState:
    N_HI: float
    N_HII: float
    N_HeI: float
    N_HeII: float
    N_HeIII: float
    U_resolved: float

    def __post_init__(self) -> None:
        for name in (
            "N_HI",
            "N_HII",
            "N_HeI",
            "N_HeII",
            "N_HeIII",
            "U_resolved",
        ):
            _checked(getattr(self, name), name)

    @property
    def N_H(self) -> float:
        return math.fsum((self.N_HI, self.N_HII))

    @property
    def N_He(self) -> float:
        return math.fsum((self.N_HeI, self.N_HeII, self.N_HeIII))


def apply_reaction_map(
    *,
    state: MaterialState,
    absorbed_HI: float,
    absorbed_HeI: float,
    absorbed_HeII: float,
    recombination_HII_to_HI: float,
    recombination_HeII_to_HeI: float,
    recombination_HeIII_to_HeII: float,
    resolved_heating: float,
) -> MaterialState:
    """Advance the material state over one substep.

    Absorbed counts must already be owner-correct: subgrid absorption never
    reaches this function, because its resolved sources are exact zero.
    """
    a_hi = _checked(absorbed_HI, "absorbed_HI")
    a_hei = _checked(absorbed_HeI, "absorbed_HeI")
    a_heii = _checked(absorbed_HeII, "absorbed_HeII")
    r_hii = _checked(recombination_HII_to_HI, "recombination_HII_to_HI")
    r_heii = _checked(recombination_HeII_to_HeI, "recombination_HeII_to_HeI")
    r_heiii = _checked(recombination_HeIII_to_HeII, "recombination_HeIII_to_HeII")
    heating = _checked(resolved_heating, "resolved_heating")

    n_h = state.N_H
    n_he = state.N_He

    # Hydrogen: advance HI, then close HII against the locked nuclei total.
    hi = math.fsum((state.N_HI, -a_hi, r_hii))
    if hi < 0.0:
        raise InfeasibleReaction("N_HI", -hi)
    hii = n_h - hi
    if hii < 0.0:
        raise InfeasibleReaction("N_HII", -hii)

    # Helium: advance the two end members, then close HeII against the total.
    hei = math.fsum((state.N_HeI, -a_hei, r_heii))
    if hei < 0.0:
        raise InfeasibleReaction("N_HeI", -hei)
    heiii = math.fsum((state.N_HeIII, a_heii, -r_heiii))
    if heiii < 0.0:
        raise InfeasibleReaction("N_HeIII", -heiii)
    heii = n_he - hei - heiii
    if heii < 0.0:
        raise InfeasibleReaction("N_HeII", -heii)

    return MaterialState(
        N_HI=hi,
        N_HII=hii,
        N_HeI=hei,
        N_HeII=heii,
        N_HeIII=heiii,
        U_resolved=math.fsum((state.U_resolved, heating)),
    )
