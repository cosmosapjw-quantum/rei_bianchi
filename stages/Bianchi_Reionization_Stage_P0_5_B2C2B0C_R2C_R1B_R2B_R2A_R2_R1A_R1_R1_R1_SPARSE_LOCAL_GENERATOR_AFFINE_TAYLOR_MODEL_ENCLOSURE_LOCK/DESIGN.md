# Sparse local-generator affine/Taylor enclosure design

## Architecture

Use structure-of-arrays storage for the reduced state center, two independent local first-order generators per node, one local mixed generator, a small separately named global-generator block, and an outward-rounded remainder. H/He conserved directions are eliminated analytically. The Python implementation remains the load-bearing oracle; an optional Rust `cdylib` implements only local polynomial evaluation and outward-rounded bounding, with differential tests.

## Validation ladder

1. algebraic generator invariants and exact local support;
2. Rust/Python parity and ULP containment;
3. point-degenerate parity;
4. 24 inherited branch trajectories and coherent/interior samples;
5. table-event distance and restart semantics;
6. three-lane set-valued ledger and width gates.

## Failure policy

Fail closed on uncontrolled remainder growth, generator proliferation, table-knot ambiguity, loss of outward inclusion, or any ledger interval excluding zero.
