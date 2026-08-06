# Negative results

## N-001 — R2C-R1 common-equilibrium multirate cone

497/540 equilibrium boxes were infeasible.  This remains a valid rejection of
that surrogate.  It no longer carries a physical-history no-go interpretation.

## N-002 — unchanged node-local scalar-rate extension

Rejected before fitting because `C` is not a state and `J_g` is not a material
reservoir.  Per-node scalar fitting would be structurally unidentifiable.

## N-003 — endpoint-local reconstruction as a replacement budget

Not promoted.  The reconstruction shows 540/540 macro mismatches and 957,298
node rows where endpoint-local `N/dt+R` is below inherited `J`; it lacks the
required time averages and cannot replace the cumulative RT ledger.

## N-004 — symbolic fallback structural-equality false negative

Preserved under `ATTEMPT_1_SYMBOLIC_STRUCTURAL_EQUALITY_FALSE_NEGATIVE`.
SymPy produced algebraically identical but structurally different forms; the
validator now compares the simplified difference to exact zero.
