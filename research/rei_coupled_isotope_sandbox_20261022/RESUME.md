# Resume: local sandbox source adapter

## Current scientific checkpoint

`PASS_SCOPED_CONDITIONAL_LOCAL_SANDBOX`, 2026-10-22.
See REVIEW.md and evidence/INDEPENDENT_REVIEW.json for the independent decision.
Theory R1–R10 and coding C3–C10 have been carried through for this finite unit;
C1/C2 baseline and source mappings are reused within their earlier scope.

First diagnostic: 156 PASS, zero failures, exit 0. One subsequently authorized
coverage addition: two manufactured n/T zero-onset checks PASS in a separate
invocation. All three original scientific code SHA256 values remain unchanged.
No full diagnostic rerun for the addition, helper validation, packaging or
publication. No historical C1/C2 execution, cosmological IVP or reset of an old
campaign budget. The finite local integrations are one atomic Radau oracle,
four atomic midpoint trajectories and six analytic scalar trace comparisons.

Local restored directory has no .git. The actually fetched remote starting
head was PR221 at `42e44494bd0956756d8c610e75da5b1cafe20d3c`, on
`research/rei-coupled-isotope-contract-20261022`. The pinned C2 scientific
commit is `c1714f82ea7de15fee230a1a995365970ee6dc02`; atomic donor is
`8be7533cc97b3302bf42608699d6e8313ed6af8a`. A subsequent delivery receipt
records the new published commit and acknowledged backups. Do not interpret
the remote branch identity as an observed local checkout HEAD.

## Reuse directly

- Immutable small input copies and source mappings; preserve older results.
- Shared charge blocks at fixed T/spectrum under the donor's isotope electronic
  equality model, with all 21 independent abundances retained.
- `J=B+(n_B RY)q^T`, fixed-fast-electron column, and the physical-domain d≥1
  denominator theorem. The theorem has its stated sign/domain restrictions.
- Positive second-order atomic midpoint at fixed T/UV/nB and zero fast pool.
- Supplied resolved-channel event algebra, zero-aware derivatives, log flux,
  explicit energy reservoir accounting and the supplied-Q temperature formula.
- Component scaling evidence at 1e-104 and 1e-120, without a population floor.
- Measured default: dense 21-state linear solve, prepared rates, vectorized
  batches where useful. Structured solve remains an exact checked alternative.

No new proof, literature search, full manifest or repeat diagnostic is needed
merely to resume or deliver identical work. New assumptions or changed code
require checking only the affected dependencies.

## Next scientifically useful unit

The next open dependency is **physical resolved-event/energy input followed by
a finite coupled local integration**. The present unit already calculates
local atomic, supplied-event and EOS pieces. It does not supply missing
charge-state branching, radiation retention, fast-electron stopping or nuclear
energy partitions.

1. Select a concrete local physical scenario and list its externally prescribed
   T/spectrum/density or its actual thermal evolution. Reuse the 21-state
   normalization and single beta ownership.
2. Identify the exact event coefficients and their applicability. For several
   branches of a parent, supply normalized probabilities and form resolved
   coefficients before calling this API. Supply a justified coefficient table
   or compute at supported temperatures; three saved knots alone do not admit
   off-grid interpolation accuracy.
3. Supply each event's signed energy ledger in the existing neutral-atom
   convention and any required fast-electron/radiation closure. Classify a
   manufactured scenario explicitly if these inputs are chosen for a numerical
   construction. Physical missing values are not silently replaced with zero.
4. Freeze the combined equations, energy and baryon invariants, initial/boundary
   values, event/thermal Jacobian requirements, solver and finite resource cap.
   The atomic-only positive midpoint and its d≥1 proof must not automatically
   be promoted to the augmented system.
5. Execute a bounded combined local trajectory and a refinement/reference
   comparison, checking energy, baryons, onset and componentwise trace accuracy.
   Compare runtime only for equivalent equations and accuracy. Review that new
   result once and advance according to observed evidence.

Entry point is R1/R3 for new physical assumptions and C2/C3 for newly connected
event/thermal dependencies, preserving completed atomic results. It is not a
reason to reopen all C1/C2 work. Full cosmological production and historical
campaigns require their own existing input/budget contracts.

## Reproduction and practical caveats

Run `bash research/rei_coupled_isotope_sandbox_20261022/run_fresh.sh` from the
project or extracted package root. It prints a new /tmp artifact-copy path,
preserves delivered evidence there and executes baseline156 then targeted2.
The source wrapper was checked with syntax/help/prepare-only; no scientific
replay was performed for that packaging check. Actual first-run commands and
versions are recorded in the execution receipts.

Reported 10.3994 s wall and 10.2784 s CPU are diagnostic body timers after
imports. Peak RSS 111128 KiB is the process peak. Local timing varies: preserve
raw repeat ranges. The Matplotlib cache warning and successful temporary-cache
fallback are in the original stderr.

Policy alignment with the user-selected built-in physmath workflow 1.0.0,
current AGENTS tiered roles and current no-new-worktree instruction is in the
frozen EXECUTION_CONTRACT. Historical artifacts are unchanged; this work adds
one owned directory.
