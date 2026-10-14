# Rust first-interval development readiness — 2026-09-30

## Decision and claim ceiling

Development can start in this checkout on a **source-neutral, test-only joint-parent
error certificate**. The Rust implementation of a physical first interval is not
ready for execution or scientific admission. Keep the current three-lane,
four-site, full-versus-two-half, positivity, width, structural-ledger, and strict
local-error gates. No archived result is promoted by this packet.

This is a Host review of the inputs and the first bounded implementation task.
The cited dossiers are theory references, not instructions or source authority.

| Surface | Observed state | Consequence |
| --- | --- | --- |
| `rei_bianchi` | `forward/rust-reion-kernels-20260922` at `ab5a32465a1048fa5e0283d1fcb41538f7ec1aaa`; Rust source candidate `1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8` | Seven fixed-input APIs only; 26 integration and five example tests pass. |
| BASS host | Remote `forward/rust-microphysics-host-20260930` at `9c6506e4e2087129a8b674ff10438e5db1a55c9d` pins the REI candidate | Exact-revision integration is done for fixed inputs, not for a history. Uncommitted BASS follow-up files are outside this task. |
| First-interval R2 | Historical blocked branch `agent/implementation/rei-first-canonical-interval-20260829-r1` at `053b97c56e089e28a83f37d79a4128ed3cdae9f4` | The accepted prefix ends at tick 160; no full interval passed. |
| Primordial recombination | `external/rec_bianchi.lock.json` is unchanged; read-only `main` probe on 2026-09-30 returned `5a09f3797210284f83a1a1adb0e0092d1ac48475` | Review and lock the changed provider before a new coupled science stage. No REC rate or state is imported here. |

The current Rust crate is deliberately source-neutral. `coverage.rs` admits no
external physical rate, and the former Python/JAX source is historical. The
83/84 cross-runtime comparison is a preserved divergence, not an active Rust
gate. Do not change its fixture, tolerance, or subnormal behavior.

## Why the historical interval cannot simply resume

The R2 run accepted `0→64→128→160`, then bisected
`160→192→176→168→164→162→161`. At `[160,161]`, all three lanes rejected the
attempt with `VALIDATED_LOCAL_ERROR_GATE_FAILURE`: the `log_T` bound was
`2.1245050576368385e-4` against strict `<2e-4`. The maximum public width was
`2.257243260856967e-4 <2e-3`; the table-event check found no event. Candidate
states were not committed and the tick-160 parents were retained. The archive
belongs to the historical source and judge and must not be overwritten.

The historical worker forms separate interval images of the full step and two
half steps and compares their extreme endpoints. For a nonpoint parent, that
cross-box distance includes inherited uncertainty from *both* boxes, even when
the maps agree at every common parent realization. This conservative quantity
cannot be replaced with a pointwise difference by subtracting box widths,
intersecting them, comparing midpoints, or relaxing the threshold. A new
validated joint propagation and independent remainder check are required.

Source identity for this diagnosis: audit source commit
`ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e`; executed runtime source
`11030b860989916d2c84ae0177ef8bfa3eb2b7dc`; predecessor discrete-map
blob `ca2676c84b3c93766c59aa3ef81740565226dad9`. The R2 blocked archive
is SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
These identities are historical evidence, not inputs to the active Rust build.

## First bounded implementation task: `REI-JOINT-PARENT-AFFINE-01`

**Goal.** Demonstrate, with exactly representable synthetic affine maps, a
replayable joint-parent difference certificate and an independent checker.
This is a mathematical test fixture, not a replacement local-error judge.

**Owned path.** Add only
`rust/rei_microphysics/tests/joint_parent_affine.rs`. The task changes no
library API, physical input, frozen judge, tolerance, archived source, or BASS
dependency. Work in the repository root; no new worktree is needed.

**Inputs and mathematical contract.** Use a test-local checked dyadic type
`n/2^e` with signed `i128` numerator and bounded nonnegative exponent. Reject
any arithmetic overflow or exponent outside the declared fixture domain. This
keeps the first certificate exact without pretending binary64 rounding has been
enclosed. Let `P=[lo,hi]`, `lo<=hi`, have one shared parent-coordinate ID, a
full map `F(x)=a*x+b`, and a half map `H(x)=c*x+d`. Both paths must use the
same `x` in `P`. In exact arithmetic the difference is

```text
D(x) = F(x) - H(H(x))
     = (a-c*c)*x + b-(c+1)*d.
```

The certificate records the shared ID, the dyadic coefficients, `P`, and an
enclosing dyadic range for `D(P)`. The checker recomputes the affine range from
the recorded inputs with checked exact arithmetic, independently of the
certificate generator, and rejects a reversed interval, arithmetic overflow,
mismatched parent ID, or a claimed range that fails to enclose the recomputed
range. It must never infer a shared parent merely because separately computed
endpoint boxes overlap. No test writes a candidate state. A failure therefore
has no commit path. Conversion to a rounded binary64 production certificate is
outside this first task.

**Frozen synthetic oracle cases.** Use dyadic inputs so the expected results
are exact in binary64:

1. `P=[0,1]`, `H(x)=x/2+1/4`, `F(x)=x/4+3/8`: `D(P)=[0,0]`. Separate full and
   two-half output boxes are both `[3/8,5/8]` and have nonzero cross-box
   extreme separation `1/4`; the joint difference is zero.
2. `P=[0,1]`, `H(x)=x/2`, `F(x)=x`: `D(P)=[0,3/4]`. A synthetic strict gate below
   `3/4` rejects without a candidate state.
3. Mismatched full/half parent IDs, reversed `P`, checked-arithmetic overflow,
   and an under-enclosing or altered claimed range all fail closed.

**Acceptance.** The focused tests pass; case 1 certifies zero while explicitly
recording the nonzero independent-box separation; case 2 rejects; every invalid
case returns an error; the seven existing APIs and tests remain unchanged.
Run from this root:

```bash
cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --test joint_parent_affine --locked
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --workspace --locked
cargo clippy --manifest-path rust/rei_microphysics/Cargo.toml --workspace --all-targets --locked -- -D warnings
python scripts/verify_repo.py
```

The focused test command becomes executable when the test file is created.
Passing this task establishes only the affine shared-parent calculation and
checker behavior. It cannot certify a nonlinear 46,080-node map or alter the
historical `[160,161]` decision.

## Next Rust kernel that is independently implementable

After the joint-parent fixture, a separate task may add a fixed-input
`hydrogen_constant_rate_step` in `src/hydrogen_step.rs`, export it from `lib.rs`,
and test it in `tests/hydrogen_step.rs`. For `x=x_HII`, time `dt` in seconds,
nonnegative constant caller-supplied ionisation rates `I_photo`, `I_coll`,
`I_secondary` per **neutral** H atom in `s^-1`, and recombination rate `R` per
ion in `s^-1`, set `I=I_photo+I_coll+I_secondary`, `k=I+R`, and for `k>0`

```text
x_eq = I/k
x_next = x_eq + (x-x_eq)*exp(-k*dt).
```

Return separate primary, collisional, secondary, and recombination event
counts per H nucleus. Their signed sum must equal `x_next-x` to rounding.
At `dt=0` or `k=0`, preserve the input and return zero events. Require finite
inputs, `0<=x<=1`, `dt>=0`, nonnegative rates, and a representable finite `k`
and `k*dt`; reject invalid data without clipping or silently inferring a rate.
Use `expm1` or an equivalent stable small-depth formula for integrated event
counts. Pure-photo, pure-recombination, secondary-only at `x=1`, equilibrium,
mixed-rate, zero-duration, and invalid-input tests are the independent synthetic
oracle. This is a local H map only, with no H/He/photon/energy history claim.

## Transition to a physical first interval

Before either synthetic slice can change the scientific judge, specify a
common parent-coordinate representation for the actual four-site nonlinear
discrete map and derive a validated enclosure for
`F_h(P(z))-F_{h/2}(F_{h/2}(P(z)))`, including coefficient response and a proved
remainder. An independent checker must verify the certificate without calling
the production evaluator. The successor contract must deliberately version
the input/runtime locks, rejected-receipt endpoint payloads, worker envelope,
and policy validator. The strict `<2e-4` local-error and `<2e-3` public-width
limits stay fixed; all three lanes, structural H/He/photon/energy ledgers,
positivity, four source sites, and Hummer–Seaton restart semantics remain gates.

Physical rates additionally require explicit source and owner admission:
cross sections and primary photon events, collisional/recombination and
secondary-electron rates, electron-density/temperature closure, case selection,
and photon storage/escape/threshold accounting. Only after a complete first
interval passes may the hydrogen-frame adapter, recombination splice,
Thomson/visibility calculation, or Bianchi/CAMB propagation be assessed.

The theory reference is Dossier IV §§4–6, 8, 10 (target-limited chemistry,
photon/material inventories, and one electron state) and Dossier V §§10, 14,
15.1–15.6 (inventory, finite positive maps, common references, and validated
defects). Those results have explicit finite-map, domain, and remainder
hypotheses; none alone validates the present nonlinear solver.
