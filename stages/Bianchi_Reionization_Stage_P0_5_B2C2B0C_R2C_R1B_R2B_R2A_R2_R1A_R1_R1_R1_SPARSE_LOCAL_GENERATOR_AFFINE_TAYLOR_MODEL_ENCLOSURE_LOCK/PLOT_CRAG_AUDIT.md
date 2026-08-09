# Plot-driven CRAG adversarial audit

## Correctness

The generator plot uses the exact instantaneous source coefficients; the
stagewise-escape plot compares an actual accepted endpoint with the immutable
strict-corner arrays. The runtime plot compares the same arrays, outward rule,
and outputs.

## Retrieval

The observed need to retain polynomial dependence and avoid axis-aligned
wrapping agrees with validated Taylor-model and affine set-parameterization
literature. Rust `next_up`/`next_down` implement the IEEE-adjacent floating-point
steps used for outward post-rounding.

## Augmented checks

- all three shape lanes produced the same stagewise endpoint hash;
- all inherited thermochemistry and ledger gates passed;
- Rust bounds contain the Python bounds with maximum ULP distance zero;
- the escape survives a 128-ULP significance screen and occurs at 9691 entries.

## Generation / prediction

A four-evaluation-site sparse model should preserve the same local rank at each
site while increasing local polynomial storage only to `16.875 MiB`. If its
validated remainder is correct, it must include the stagewise witness and all
24 inherited static trajectories. Failure to include either is a hard rejection.

## Adversarial mutations

- **Global-coherence mutation:** rejected by the inherited rank theorem.
- **Static-control mutation:** rejected by the stagewise witness.
- **Rust-only authority mutation:** rejected; Python remains the oracle.
- **Tolerance dismissal:** rejected; the maximum escape is about 3.3% of the
  relevant strict-corner width, not a one-ULP artifact.

## Claim status

`narrowed claim`: instantaneous source and global coupling representations pass;
continuous/discrete-map enclosure remains uncertified.
