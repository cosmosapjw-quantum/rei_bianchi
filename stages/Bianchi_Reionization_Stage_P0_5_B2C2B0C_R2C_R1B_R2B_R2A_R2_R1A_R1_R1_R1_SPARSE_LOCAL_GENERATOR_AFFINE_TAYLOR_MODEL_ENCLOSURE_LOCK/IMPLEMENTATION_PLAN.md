# Sparse Local-Generator Enclosure Implementation Plan

1. Add RED tests for sparse polynomial storage, local support, bounds, generator-wise nuclei invariants, and event distances.
2. Implement the Python oracle data model and exact local branch source generators.
3. Add RED tests for optional Rust parity; implement a standard-library `cdylib` with `next_up/next_down` outward bounds.
4. Implement low-rank owner coupling metadata and validated one-step propagation with an outward interval remainder.
5. Reproduce inherited point/corner/coherent/interior trajectories and run all three lanes.
6. Generate residual, width, event-distance, and performance plots; perform PHYS-MATH and PHYS-MATH-CODE audits.
7. Seal results, manifests, receipts, compact artifact, commit/tag/bundle, then attempt remote push/PR only if network and credentials are available.
