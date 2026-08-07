#!/usr/bin/env python3
"""Run the R1B-R2B owner-correct photon pipeline over the canonical tables.

What this driver does run on canonical data:
  * the R1B-R2A conditional owner split, per interval and group;
  * photon-conserving absorbed counts over the canonical interval dt;
  * the ten separate ledgers;
  * the 1,2,4,8 refinement matrix as a budget-additivity test;
  * the exact-zero subgrid resolved-source certificate on every owner row.

What it does not run, and why:
  * the material H/He update and the resolved thermal update. The durable
    inputs carry no locked initial material state vector
    (N_HI, N_HII, N_HeI, N_HeII, N_HeIII, U_resolved); the macro parcel
    template holds weights, not species counts. Manufacturing one would be a
    fabricated initial condition.
  * a nonautonomous state-derived fraction law. R1B-R1 fail-closed established
    that the durable inputs do not identify a dynamic-opacity operator, and the
    input lock forbids the kappa=J/Phi inversion that would fake one. The
    locked component table gives a per-interval frozen law, which is autonomous
    within a slab.

Both omissions are recorded in the emitted results rather than papered over.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pandas as pd

STAGE_DIR = Path(__file__).resolve().parents[1]
REPO = STAGE_DIR.parents[1]
R2A = (
    REPO
    / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"
)

MYR_SECONDS = 3.155814954e13  # Julian megayear


def _load(stem: str):
    name = f"r2b_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, STAGE_DIR / "analysis" / f"{stem}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


owner_mod = _load("owner_conservation")
ledgers_mod = _load("ledgers")

COMPONENT_OWNER = {
    "EFFECTIVE_HI_SUBGRID": "EFFECTIVE_HI_SUBGRID",
    "EXPLICIT_HI_ATOMIC": "RESOLVED_HI",
    "EXPLICIT_HEI_ATOMIC": "RESOLVED_HeI",
    "EXPLICIT_HEII_ATOMIC": "RESOLVED_HeII",
}


def owner_fractions(rows: pd.DataFrame) -> dict[str, float]:
    """Conditional owner fractions from the locked raw component table.

    Only the ratio is used. The raw amplitude is never allowed to override the
    authoritative group total, matching the R1B-R2A treatment.
    """
    raw = {
        COMPONENT_OWNER[c]: float(v)
        for c, v in zip(rows["component"], rows["absorption_rate_s-1_cMpc-3"])
    }
    for owner in owner_mod.OWNERS:
        raw.setdefault(owner, 0.0)
    support = math.fsum(raw.values())
    if support == 0.0:
        return {o: 0.0 for o in owner_mod.OWNERS}
    return {o: raw[o] / support for o in owner_mod.OWNERS}


def main() -> int:
    totals = pd.read_csv(R2A / "inputs/upstream/reconciled_group_total_absorption.csv")
    comps = pd.read_csv(
        R2A / "inputs/upstream/reconciled_physical_component_absorption.csv"
    )
    ledger_tbl = pd.read_csv(R2A / "inputs/upstream/canonical_direct_photon_ledger.csv")
    dt_by_interval = {
        int(r.interval_index): float(r.dt_Myr) * MYR_SECONDS
        for r in ledger_tbl.itertuples()
    }

    ledger = ledgers_mod.LedgerSet()
    owner_rows = 0
    group_cases = 0
    worst_owner_residual = 0.0
    worst_refinement_delta = 0.0
    zero_subgrid_violations = 0
    zero_support_cases = 0

    for (interval, group), block in comps.groupby(["interval_index", "group"]):
        total_row = totals[
            (totals["interval_index"] == interval) & (totals["group"] == group)
        ]
        if total_row.empty:
            raise SystemExit(f"no authoritative total for interval {interval} {group}")
        total_current = float(total_row["total_absorption_rate_s-1_cMpc-3"].iloc[0])
        dt = dt_by_interval[int(interval)]

        fractions = owner_fractions(block)
        group_cases += 1
        if math.fsum(fractions.values()) == 0.0:
            zero_support_cases += 1
            if total_current != 0.0:
                raise SystemExit(
                    f"nonzero total on zero component support: {interval} {group}"
                )
            continue

        currents = {o: total_current * p for o, p in fractions.items()}
        counts = owner_mod.absorbed_counts_by_owner(
            owner_currents=currents, dt_seconds=dt
        )
        total_count = owner_mod.absorbed_count_total(
            total_current=total_current, dt_seconds=dt
        )
        summed = math.fsum(counts.values())
        scale = max(abs(summed), abs(total_count), 1.0)
        worst_owner_residual = max(worst_owner_residual, abs(summed - total_count) / scale)

        # Exact-zero subgrid certificate on every owner row.
        for owner, count in counts.items():
            owner_rows += 1
            sources = owner_mod.resolved_sources_for_owner(
                owner=owner, absorbed_count=count
            )
            if owner == "EFFECTIVE_HI_SUBGRID" and not (
                sources.resolved_H == 0.0
                and sources.resolved_He == 0.0
                and sources.resolved_U == 0.0
            ):
                zero_subgrid_violations += 1
            ledger.post_owner_absorption(
                owner=owner, count=count, absorbed_energy=0.0
            )

        # Refinement matrix: budget additivity at dt, dt/2, dt/4, dt/8.
        reference = summed
        for n in (2, 4, 8):
            sub_total = math.fsum(
                math.fsum(
                    owner_mod.absorbed_counts_by_owner(
                        owner_currents=currents, dt_seconds=dt / n
                    ).values()
                )
                for _ in range(n)
            )
            denom = max(abs(reference), 1.0)
            worst_refinement_delta = max(
                worst_refinement_delta, abs(sub_total - reference) / denom
            )

    results = {
        "classification": "R1B_R2B_OWNER_CORRECT_PHOTON_PIPELINE_AUDIT",
        "canonical_source": "CANONICAL_DIRECT_REEVOLVED",
        "group_cases": group_cases,
        "owner_rows": owner_rows,
        "zero_component_support_cases": zero_support_cases,
        "max_owner_closure_relative_residual": worst_owner_residual,
        "max_refinement_relative_delta": worst_refinement_delta,
        "exact_zero_subgrid_resolved_source_violations": zero_subgrid_violations,
        "photon_ledger_total": ledger.photon_total(),
        "ledger_snapshot": ledger.snapshot(),
        "not_executed": {
            "material_H_He_update": "no locked initial material state vector in durable inputs",
            "resolved_thermal_history": "depends on the absent material state",
            "nonautonomous_state_derived_fraction_law": (
                "R1B-R1 fail-closed: durable inputs do not identify a dynamic-opacity "
                "operator; kappa=J/Phi inversion is forbidden by the input lock"
            ),
        },
        "production_history_integrated": False,
    }

    out = STAGE_DIR / "results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "ledger_snapshot"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
