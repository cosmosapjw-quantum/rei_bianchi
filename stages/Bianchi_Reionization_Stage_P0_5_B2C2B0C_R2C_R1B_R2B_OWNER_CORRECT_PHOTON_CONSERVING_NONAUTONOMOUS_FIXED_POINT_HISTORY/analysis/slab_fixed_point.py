#!/usr/bin/env python3
"""Minimal owner-correct slab loop and refinement matrix for R1B-R2B.

Per slab the loop is

    owner-correct averaged opacity
      -> photon-conserving absorbed counts
      -> positive implicit H/He update
      -> resolved thermal update

iterated as a Picard fixed point. The owner-fraction law is evaluated at the
*current iterate*, which is what makes the step implicit and nonautonomous; the
material update is always applied from the parent state, so iterating never
accumulates absorption.

The fraction law is injected by the caller. This module does not contain one.
R1B-R1 showed `kappa = J/Phi` is not a state-derived dynamic-opacity law and the
input lock forbids inverting it, so authoring a law here would manufacture
exactly the operator R1B-R1 proved the durable inputs do not identify.

Everything runs inside a transaction: a slab that fails to converge or that
violates positivity is rejected whole, leaving the accepted history untouched.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence


def _load_sibling(stem: str):
    name = f"r2b_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).with_name(f"{stem}.py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_owner = _load_sibling("owner_conservation")
_chem = _load_sibling("positive_chemistry")
_txn = _load_sibling("transaction")

OWNERS = _owner.OWNERS
REFINEMENT_LEVELS = (1, 2, 4, 8)
REFINEMENT_RELATIVE_DELTA = 2.0e-4
FIXED_POINT_TOLERANCE = 1.0e-12
FRACTION_CLOSURE_TOLERANCE = 1.0e-12

# Which resolved species each owner ionizes. The subgrid owner is absent by
# construction, so no code path routes it into the reaction map.
OWNER_TO_SPECIES = {
    "RESOLVED_HI": "absorbed_HI",
    "RESOLVED_HeI": "absorbed_HeI",
    "RESOLVED_HeII": "absorbed_HeII",
}


@dataclass(frozen=True)
class SlabResult:
    converged: bool
    iterations: int
    fixed_point_residual: float
    photon_relative_residual: float
    tolerance: float
    absorbed_counts: dict[str, float]


@dataclass(frozen=True)
class RefinementRow:
    refinement: int
    converged: bool
    photon_total: float
    total_iterations: int


@dataclass(frozen=True)
class RefinementReport:
    rows: tuple[RefinementRow, ...]
    max_relative_delta: float


def _validate_fractions(fractions: Mapping[str, float]) -> dict[str, float]:
    unknown = set(fractions) - set(OWNERS)
    if unknown:
        raise KeyError(f"unknown owners in fraction law: {sorted(unknown)}")
    values = {}
    for owner in OWNERS:
        p = float(fractions.get(owner, 0.0))
        if not math.isfinite(p) or p < 0.0:
            raise ValueError(f"owner fraction {owner} must be finite and nonnegative")
        values[owner] = p
    total = math.fsum(values.values())
    if abs(total - 1.0) > FRACTION_CLOSURE_TOLERANCE:
        raise ValueError(f"owner fractions must close to 1, got {total!r}")
    return values


def _state_residual(a, b) -> float:
    worst = 0.0
    for name in ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved"):
        x, y = getattr(a, name), getattr(b, name)
        scale = max(abs(x), abs(y), 1.0)
        worst = max(worst, abs(x - y) / scale)
    return worst


def _one_pass(parent, fractions, total_current, dt_seconds, energy_per_absorption):
    """opacity -> counts -> positive chemistry -> thermal, from the parent state."""
    owner_currents = {o: total_current * p for o, p in fractions.items()}
    counts = _owner.absorbed_counts_by_owner(
        owner_currents=owner_currents, dt_seconds=dt_seconds
    )
    heating = math.fsum(
        counts[o] * float(energy_per_absorption[o]) for o in OWNER_TO_SPECIES
    )
    kwargs = {v: counts[k] for k, v in OWNER_TO_SPECIES.items()}
    new_state = _chem.apply_reaction_map(
        state=parent,
        recombination_HII_to_HI=0.0,
        recombination_HeII_to_HeI=0.0,
        recombination_HeIII_to_HeII=0.0,
        resolved_heating=heating,
        **kwargs,
    )
    return new_state, counts


def run_slab(
    *,
    history,
    total_current: float,
    dt_seconds: float,
    owner_fraction_law: Callable[[object], Mapping[str, float]],
    energy_per_absorption: Mapping[str, float],
    max_iterations: int = 50,
    tolerance: float = FIXED_POINT_TOLERANCE,
) -> SlabResult:
    """Advance one slab to a fixed point inside a transaction."""
    result: dict[str, object] = {}

    with history.attempt("slab") as scratch:
        parent = scratch.state
        iterate = parent
        converged = False
        iterations = 0
        residual = math.inf
        counts: dict[str, float] = {}

        while iterations < max_iterations:
            fractions = _validate_fractions(owner_fraction_law(iterate))
            iterations += 1
            candidate, counts = _one_pass(
                parent, fractions, total_current, dt_seconds, energy_per_absorption
            )
            residual = _state_residual(candidate, iterate)
            iterate = candidate
            if residual <= tolerance:
                converged = True
                break

        if not converged:
            raise _txn.AttemptRejected(
                f"slab fixed point did not converge in {max_iterations} iterations "
                f"(residual {residual!r})"
            )

        total_count = _owner.absorbed_count_total(
            total_current=total_current, dt_seconds=dt_seconds
        )
        if not _owner.owner_counts_close(counts, total_count):
            raise _txn.AttemptRejected("owner absorbed counts do not close on the total")
        summed = math.fsum(counts.values())
        scale = max(abs(summed), abs(total_count), 1.0)

        for owner, count in counts.items():
            scratch.ledger.post_owner_absorption(
                owner=owner,
                count=count,
                absorbed_energy=count * float(energy_per_absorption[owner]),
            )
        scratch.state = iterate

        result = {
            "iterations": iterations,
            "fixed_point_residual": residual,
            "photon_relative_residual": abs(summed - total_count) / scale,
            "absorbed_counts": dict(counts),
        }

    return SlabResult(
        converged=True,
        iterations=int(result["iterations"]),
        fixed_point_residual=float(result["fixed_point_residual"]),
        photon_relative_residual=float(result["photon_relative_residual"]),
        tolerance=tolerance,
        absorbed_counts=dict(result["absorbed_counts"]),  # type: ignore[arg-type]
    )


def run_refinement_matrix(
    *,
    make_history: Callable[[], object],
    total_current: float,
    dt_seconds: float,
    owner_fraction_law: Callable[[object], Mapping[str, float]],
    energy_per_absorption: Mapping[str, float],
    levels: Sequence[int] = REFINEMENT_LEVELS,
    max_iterations: int = 50,
    tolerance: float = FIXED_POINT_TOLERANCE,
) -> RefinementReport:
    """Re-run the same slab budget at dt, dt/2, dt/4, dt/8 on fresh histories.

    This is a budget-additivity test, not a chemistry convergence claim: with an
    exactly integrated forcing, partitioning the interval must not change the
    absorbed total.
    """
    rows = []
    for n in levels:
        history = make_history()
        iterations = 0
        converged = True
        for _ in range(n):
            outcome = run_slab(
                history=history,
                total_current=total_current,
                dt_seconds=dt_seconds / n,
                owner_fraction_law=owner_fraction_law,
                energy_per_absorption=energy_per_absorption,
                max_iterations=max_iterations,
                tolerance=tolerance,
            )
            iterations += outcome.iterations
            converged = converged and outcome.converged
        rows.append(
            RefinementRow(
                refinement=n,
                converged=converged,
                photon_total=history.ledger.photon_total(),  # type: ignore[attr-defined]
                total_iterations=iterations,
            )
        )

    reference = rows[0].photon_total
    scale = max(abs(reference), 1.0)
    worst = max(abs(row.photon_total - reference) / scale for row in rows)
    return RefinementReport(rows=tuple(rows), max_relative_delta=worst)
