#!/usr/bin/env python3
"""The ten separate R1B-R2B ledgers.

Photon and energy bookkeeping is kept in ten independent accounts. They are
never collapsed into a single total, because the defect R1B-R2A diagnosed —
unresolved subgrid absorption also driving resolved chemistry and heating — is
invisible in an aggregate and obvious in a split ledger.

`post_owner_absorption` is the only routing point. Owner routing is by exact
table lookup, so the subgrid owner cannot reach a resolved account by any code
path.
"""
from __future__ import annotations

import math
from typing import Mapping

LEDGER_NAMES = (
    "resolved_HI_absorption",
    "resolved_HeI_absorption",
    "resolved_HeII_absorption",
    "effective_subgrid_absorption",
    "boundary_redshift_storage",
    "resolved_photoheating",
    "unresolved_absorbed_energy",
    "cooling",
    "expansion_work",
    "mass_transfer_work",
)

# Photon-count accounts that must close against the authoritative group total.
PHOTON_LEDGERS = (
    "resolved_HI_absorption",
    "resolved_HeI_absorption",
    "resolved_HeII_absorption",
    "effective_subgrid_absorption",
    "boundary_redshift_storage",
)

# (count account, absorbed-energy account) per owner. The subgrid owner's
# energy goes to the unresolved account and never to resolved photoheating.
OWNER_ROUTING: dict[str, tuple[str, str]] = {
    "EFFECTIVE_HI_SUBGRID": (
        "effective_subgrid_absorption",
        "unresolved_absorbed_energy",
    ),
    "RESOLVED_HI": ("resolved_HI_absorption", "resolved_photoheating"),
    "RESOLVED_HeI": ("resolved_HeI_absorption", "resolved_photoheating"),
    "RESOLVED_HeII": ("resolved_HeII_absorption", "resolved_photoheating"),
}


def _checked(value: float, label: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite, got {value!r}")
    return x


class LedgerSet:
    """Ten independent accumulators with no cross-talk."""

    def __init__(self) -> None:
        self._values: dict[str, float] = {name: 0.0 for name in LEDGER_NAMES}

    def __getitem__(self, name: str) -> float:
        if name not in self._values:
            raise KeyError(f"unknown ledger: {name!r}")
        return self._values[name]

    def post(self, name: str, amount: float) -> None:
        if name not in self._values:
            raise KeyError(f"unknown ledger: {name!r}")
        self._values[name] = math.fsum((self._values[name], _checked(amount, name)))

    def post_owner_absorption(
        self, *, owner: str, count: float, absorbed_energy: float
    ) -> None:
        if owner not in OWNER_ROUTING:
            raise KeyError(f"unknown owner: {owner!r}")
        count_account, energy_account = OWNER_ROUTING[owner]
        self.post(count_account, count)
        self.post(energy_account, absorbed_energy)

    def photon_total(self) -> float:
        return math.fsum(self._values[name] for name in PHOTON_LEDGERS)

    def snapshot(self) -> dict[str, float]:
        """Return a detached copy; later posts must not mutate it."""
        return dict(self._values)

    def restore(self, snapshot: Mapping[str, float]) -> None:
        """Replace all accounts from a snapshot taken by `snapshot()`."""
        if set(snapshot) != set(LEDGER_NAMES):
            raise KeyError("snapshot does not cover exactly the ten ledgers")
        self._values = {name: float(snapshot[name]) for name in LEDGER_NAMES}
