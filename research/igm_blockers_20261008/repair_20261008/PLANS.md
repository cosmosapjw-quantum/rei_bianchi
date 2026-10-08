# Repair milestones

1. `DONE`: implemented a dedicated photoheat sign/error operation and added its arithmetic bound once to the thermal residual gate.
2. `DONE`: targeted and locked library tests plus the exact fixture pass. The package-wide formatter still reports preserved pre-existing compact files; the new material implementation passes direct rustfmt check.
3. `DONE`: coarse k12, fine k23/k24 and tail k12 pass from copies of the pinned checkpoints.
4. `DONE`: the first repaired common epoch k12/24/12 passes all original 37-field, N/E and source comparisons. Coarse k13 also accepted. The following k14 exposes the paired N/E readout blocker and is preserved.
5. `DONE`: scoped independent review and reproducibility closeout completed with decision `HOLD_PAIRED_NODE_PATH_REQUIRED`.

Alternatives considered:

- Global acceptance of all finite subnormals: rejected because other guards protect distinct range transitions.
- Clamp heat to zero: rejected because it loses a positive contribution and changes the physical map.
- Full per-node scaled state first: deferred because the current saved failure reaches the heat check with NORMAL input and next N; it is larger than the demonstrated first repair.

Rollback is removal of the local `photoheat_term`/bound integration and its tests; checkpoint inputs are immutable during the first repair.
