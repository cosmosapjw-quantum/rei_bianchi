# BR04 age-distribution diagnostics: implementation contract

The additive `br04/Cargo.toml` target imports `crate/ap_lib.rs` through the new
`crate/br04_lib.rs` wrapper. Its existing 118 input files, including all 105 BR03
crate files, retain their SHA-256 identities in `contracts/PARENT_INPUT_SHA256.json`.
No native transport update, source owner, CX flow, timestep controller, or photon
cohort is modified by the new diagnostic module.

## Public API and units

```rust
compare_nodes(tau: f64, born: f64, nodes: &[(f64, f64)])
    -> Result<BirthAgeCertificate, NetworkError>;
compare_fitted(tau: f64, born: f64, refinement: usize)
    -> Result<BirthAgeCertificate, NetworkError>;
```

Each input pair is `(x, w)`, with age `x=(T-t_birth)/T` in `[0,1]` and nonnegative
emitted weight `w`. The source amplitude `born` is the exact emitted count over
the entire interval, in the caller's volume convention. `tau=kappa*T` is finite
and nonnegative. `compare_nodes` accepts actual nodes from any positive rule,
including original GL2/GL4 nodes and unions of timestep nodes expressed in global
age units. The diagnostic privately sorts copied nodes; input storage is untouched.

The reference emitted density is uniform. Its survivor density is proportional
to `exp(-tau*x)`. Each of the two output measures reports absolute mass, relative
mass defect, log mass ratio, normalized CDF supremum, W1 distance, and first/second
normalized moments and their signed differences. To obtain a physical-age W1,
multiply the reported distance by `T`; multiply first and second normalized
moments by `T` and `T^2`, respectively. For a normalized observable with Lipschitz
constant `L` with respect to physical age, the corresponding shape bound is
`L*T*W1`. Mass mismatch is a separate contribution.

Zero source has exactly zero counts and `shape=None`. An empty rule with positive
source reports relative mass defect `-1` and undefined normalized shape. Negative
or nonfinite source/weights and ages outside `[0,1]` are rejected without clipping.
The original fitted rule's errors propagate from `compare_fitted`; the diagnostic
does not substitute nodes when the rule reaches an age-representation limit.

## Numerical evaluation

CDF extrema are evaluated immediately before and after every discrete jump.
W1 is the sum of positive closed integrals of the CDF discrepancy between adjacent
atoms. The mathematical formulas and proof are in `AGE_CERTIFICATE_THEORY.md`.
The code uses a small-optical-depth series and a large-optical-depth scaling that
avoids `sinh`, `exp(tau)`, and an underflowing intermediate `1/tau^2` in W1.
Normalized discrete weights are formed after a log-weight shift. A mathematically
positive absolute mass may therefore round to zero while its normalized shape
remains defined; `absolute_mass_underflow` explicitly records that circumstance.
Moments below the representable f64 range can still round to zero.

These outputs evaluate exact-arithmetic identities in f64. They do not provide
directed-rounding enclosures. The independent high-precision checks evaluate the
actual exported node coordinates and weights. The reference assumption is
constant emission and opacity; applying the result to evolving gas or geometry
requires the separate variation and response assumptions described in the theory.

## Actual study outputs

`birth_age_study` produces 84 comparisons: scalar optical depths
`0, 1e-8, 1, 93, 1e3, 1e12`, and at global `tau=93` the time grid
`Nt=1,2,4,8,16,32,64`. Each comparison includes AP refinements `1,2,4,8,16`
or the unchanged GL2/GL4 rule. Local nodes are mapped into global age as
`x_global=(elapsed_cells+x_local)/Nt`, with global emitted weight `w_local/Nt`.
Every actual node is exported in `AGE_ACTUAL_NODES.csv`. Five separate cases at
`tau=1e300` preserve the original fitted rule's `NoForwardProgress` outcome as
`NUMERICAL_REPRESENTATION_LIMIT`.

`birth_age_source_study` reads the exact BR03 frozen-source inventory copied to
`inputs/AP_FROZEN_SOURCE_INPUTS.csv`. The 384 row identities, their source counts,
energy labels and four-channel opacities are retained. At `T=8e12 s` and `Nt=32`,
the study evaluates AP refinements `1,2,4,8` and GL2/GL4, giving 2304 labelled
comparisons. Identical scalar rule inputs may reuse a read-only certificate, so
288 distinct scalar rules generate 137152 exported node rows. This computational
reuse does not combine physical cohorts or source labels.

The source-inventory CLI requires strictly positive label masses. Independent
review found that a synthetic zero-born row could otherwise display the cached
unit-source conditional shape. The CLI now rejects that row explicitly; the core
API continues to handle zero source with `shape=None`. The original384-label
outputs were regenerated after the fix and all3 CSVs are byte-identical.
Post-review source hashes and repeat full-test results are recorded separately
in `SOURCE_IDENTITY_POST_REVIEW.json` and `POST_REVIEW_EXECUTIONS.json`.

For mixture bounds let `p_l` and `q_l` be exact and discrete normalized label
masses. The file `AGE_SOURCE_MIXTURE_BOUNDS.csv` reports
`sum_l p_l*d_l + 0.5*sum_l |p_l-q_l|`, separately for local CDF and W1 defects
`d_l`. This is a triangle upper bound on the actual unlabelled mixture discrepancy.
The exact mixture distance is not evaluated. A CDF bound exceeding one is a
valid but uninformative triangle bound; it may be replaced by the known upper
bound one when presenting a final estimate.

## Execution and failure record

The actual all-target run passed 224 Rust tests, including 15 new diagnostic
tests; strict Clippy and scoped rustfmt passed. Commands, exit codes, timing,
compiler identities and source identities are recorded under
`evidence/implementation/`.

The first new-test run found one subnormal-opacity conditioning error: directly
evaluating `-log1p(-p*D)/tau` lost the product `p*D` to underflow. The corrected
small-depth expression is `p*phi(tau)*[-log1p(-z)/z]`, with its removable `z=0`
limit. The failing input and original log are retained in `INITIAL_FAILURE.json`
and `AGE_TESTS_INITIAL.log`; the focused rerun and full test suite verified the
correction. This was a diagnostic implementation defect, with no change to the
original quadrature, source owner, or native gas histories.

Reproduction commands from the unit root, after activating Rust 1.94.1:

```bash
cargo test --manifest-path br04/Cargo.toml --offline --locked --all-targets
cargo clippy --manifest-path br04/Cargo.toml --offline --locked --all-targets -- -D warnings
cargo run --release --manifest-path br04/Cargo.toml --offline --locked --example birth_age_study -- OUTPUT_DIRECTORY
cargo run --release --manifest-path br04/Cargo.toml --offline --locked --example birth_age_source_study -- inputs/AP_FROZEN_SOURCE_INPUTS.csv OUTPUT_DIRECTORY
```

Use a target directory outside the package for generated build products. The
source/diagnostic evidence is sufficient to rebuild; compiler distributions and
Cargo target directories are excluded from the research archive.
