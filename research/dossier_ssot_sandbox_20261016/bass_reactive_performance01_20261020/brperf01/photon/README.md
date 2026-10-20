# BRPERF01 photon work reuse and ordered parallel evaluation

This add-only Rust crate is a performance side lane over the preserved BR06
frozen reference operator. It uses the actual MD14/BB50k source labels and the
original H/He/D photoionization and BASS Killing-ray owners. The default `Mode`
calls the original BR06 `native_path`. `Mode::Cached` and `ParallelPool` opt in to
the new implementation. No original source file is edited.

## What changed and why it remains the same physical computation

The BR06 path solver evaluates an immutable frozen gas state at many energies
along each actual birth ray. Its original `ApMidpointBridge::opacity_channels`
calls `gas.eos()` on every sample, then repeatedly reads the same isotope number
densities, thresholds, and atomic-provider identities. `PreparedOpacity` holds
an immutable borrow of the fixture, validates EOS once, and retains the same
four scalar densities and thresholds. Every energy-dependent cross section is
still evaluated by the original owner at the actual photon energy. In
particular, this is not an interpolation table for opacity.

For species i the copied adapter evaluates exactly the original order

`((n_i * sigma_i(E)) * c) * (recorded_mid_volume / volume(t))`.

HI, HeI, HeII and DI remain separate positive channels. The D owner, its
manufactured 0.0037 eV binding defect, original H edge convention, and error
mapping are unchanged. An immutable borrow prevents gas/source/configuration
mutation during reuse; the only interior mutation in the fixture is its
already-existing exact-time geometry cache.

The original `Cohort::ray_at` first reconstructs and normalizes the same birth
ray before every pullback. `PreparedNativePath` hoists precisely that first
construction. It calls the original `CharacteristicRay::pullback` at every
geometry sample, including all its normalizations, domain checks and
underflow-safe fallback. No Killing momentum is recomputed from a new birth
time. No age, direction, source label, population or birth geometry is averaged.

`Rules` computes the two original positive Gauss rules once per control pair.
The scalar integrator is an auditable derived copy of the preserved BR06
integrator: `scripts/derive_kernel.py` makes count-asserted textual changes and
records the source hash. The only integration changes are borrowed quadrature
rules and a reusable 128-element rate scratch array, replacing a newly allocated
`Vec<(rate, weight)>` for every opacity integral. All summation orders,
Newton/bisection decisions, thin/subnormal branches, event updates, stopping
criteria and independent geometry-work ledger arithmetic remain unchanged.
The virtual sample counter is still incremented at every original sample; no
work-limit budget is silently relaxed.

## Parallel ownership and numerical order

The original `GeometryChoice` uses `Rc<RefCell<...>>`, so sharing a fixture
across threads would violate its type-level ownership. `ParallelPool` instead
creates persistent standard-library workers. Each worker loads its own original
fixture and exact-time cache. The workers receive immutable cohort data in an
`Arc`, compute independent path results, and return them with the original
unique-path index. A round-robin partition distributes varying opacity costs.
No `unsafe` code, fake `Send` implementation, parallel floating-point sum or
new thread-pool dependency is used.

`PreparedBatch` uses the same exact reflection key as the original BR06 `run`.
All template/node birth records remain present. It returns reflected final
directions separately for each original label and accumulates the unchanged
ledger in the original template-major, node-minor order. The lowest failing
original cohort index determines the returned numerical refusal. Every worker
reply is consumed before returning a numerical refusal, and a regression test
checks that the pool works again after an intentional sample-budget failure.
Worker/channel failures use the original `ENVIRONMENT_IO_FAILURE` class.
Worker death or a broken channel requires constructing a new pool; recovery is
only verified for ordinary numerical refusals returned by live workers.

The public prepared contexts are bound explicitly. A path's prepared opacity
must belong to that exact fixture. `PreparedBatch` holds an immutable fixture
borrow; serial evaluation and reduction check that fixture pointer. Parallel
workers compare a frozen semantic receipt containing the original geometry
identity, complete source/configuration identity, all thirteen isotope-density
bits, thermal energy, clock endpoints, reference geometry/volume, source
amplitude and binding thresholds. A different frozen state or observation
time is rejected before any worker job. This prevents valid birth geometry
alone from silently admitting a different frozen opacity problem.
The result consumer still accepts raw `PathResult` slices: callers must supply
this batch's outputs in its unique-cohort order, and `result_for_birth` requires
a valid birth index. Same-length foreign result slices are not intrinsically
tagged. The supplied driver constructs and checks this association throughout;
this crate does not claim an opaque, tamper-proof result container API.

## Work and memory model

Let U be the number of exact reflection-unique paths, Q the opacity degree,
E the event degree and I the total number of opacity integrals, including
inverse iterations. The baseline constructs 2U Gauss objects and allocates I
temporary buffers with 16Q payload bytes. The cached serial path constructs
two Gauss objects and uses a 1,024-byte stack scratch array per active path.
This removes I heap allocations and 16QI bytes of cumulative allocation churn;
it does not claim that these bytes were simultaneously live. Every original
sample still computes the same opacity and ray. EOS calls fall from the number
of virtual path samples to one per cached serial run, or one per worker job.

For the actual384-label SIGNED_MINUS r1/Q2/E4 example, U=1,824, the labelled
birth count is 3,648 and I=37,194. The change removes 1,190,208 bytes of opacity
allocation churn, 111,872 repeated EOS calls and 3,646 Gauss constructions.
These are executed work counts, not a wall-time speed estimate. Raw timing
files and derived results separately show whether wall time improved.

The prepared input and ordered output do require O(B+U) storage: an original
`Cohort` is 112 bytes and `PathResult` is 248 bytes on the tested target. The
baseline comparison uses this same prepared representation, so the wall-time
comparison is a computation-stage comparison. The original streaming CSV
driver has a different memory profile. Each parallel worker also duplicates
the immutable fixture and its bounded 8,192-entry geometry cache. Subprocess
peak RSS, setup time and input preparation time are recorded independently.
Reduced temporary allocations therefore do not imply a lower whole-program
peak memory footprint.

## Verification and measured scope

`tests/exact_reuse.rs` checks all 41 semantic words of every compared
`PathResult`, including all f64 bits, directions, species channels, heat,
chemical energy, geometry work, residuals, counters and underflow flags.
Its cases cover zero source/opacity, thin through thick absorption, subnormal
hazards, invalid rates/cuts/source/population/geometry, explicit sample budget
refusal and post-refusal pool reuse. It probes all 384 original labels at five
times for both signed BASS geometries and native paths across energy/age bands.
An original BR06 `run` at the declared eight-template prefix reproduces every
field of the new ordered ledger exactly. Source preparation still calls the
original emitter.

The final guarded benchmark additionally writes full little-endian path-bit
and 33-word ledger-bit files for baseline, cached serial and parallel modes.
The earlier exploratory revision stored complete path bits and compared
finite ledger fields using their Rust Debug representation. Its logs remain
identified as the pre-guard revision. `scripts/analyze.py` compares the
entire files, independently reconstructs label order, birth age, Killing
components and linear photon/energy moments using Python `math.fsum`, and
records SHA-256 digests. It checks positive channel events and the number
ledger. This bitwise proof transfers the established baseline answers to the
new implementation on the tested cases; it is not a new discretization-error
or nonlinear gas-evolution proof.

The measured cases use the recorded first BR05 macrostep, t=0 to 5e11 s,
frozen reference-comoving gas, time-varying density through V(t), and actual
SIGNED_MINUS/PLUS BASS geometry. No new chemistry trajectory, CX half-flow,
four-corner controller step, nuclear species, Einstein feedback or longspan
convergence result is produced by this side lane. The production photon
emission/absorption/thermal/chemical/work owners are unchanged.

## Timing protocol and VigilODE reuse

We inspected `rodas5p-fair-ab/src/paired_timing.rs` at the preserved VigilODE
pin `a21d573980f66fe02891bd216153443b5352f921`. Its license is MIT, copyright
2026 cosmosapjw-quantum; exact file hashes and the license are retained under
`evidence/DEPENDENCY_IDENTITY.json` and `evidence/VIGILODE_LICENSE`.
We reused the measurement principles—warmups, interleaved A/B/B/A order,
session identities, A/A noise control, work/accuracy matching and explicit
inconclusive reporting. No VigilODE timing code or newer solver code was
copied. The newest upstream HEAD reported by the parent research audit is
recorded separately; it does not replace the validated scientific pin.

The benchmark performs two warmups of every mode, then predeclared alternating
baseline/cached and baseline/parallel pairs. It clears each original geometry
cache before every timed run. Ordered reduction is timed; fixture loading,
source preparation, thread startup, validation fingerprints and CSV output are
separately recorded or outside the compute interval. `black_box` retains the
computed output. Three paired A/A controls describe within-session variability.

These bounded one-process-per-case runs do not satisfy VigilODE's six-session,
30-pair, bootstrap/Monte-Carlo confirmatory gate. All wall-time observations
are exploratory, and a serial result near unity must remain unadmitted as a
speedup. The code still removes the measured allocations even when donor
geometry evaluation dominates wall time. No fast-math or reassociation is
enabled. Scalar opacity is nonlinear in energy; direct SIMD approximations and
energy/birth bin merging were therefore not introduced. The contiguous scratch
and independent cohort jobs expose batch work without altering the adaptive
inverse solver's scalar reduction order.

## Reproduction

Use the sandbox Rust environment supplied by the root stage. No source owner
or original crate needs a patch. From this directory:

```bash
source ../runtime/env.sh
export CARGO_TARGET_DIR="$PWD/target"
cargo test --offline --all-targets
cargo clippy --offline --all-targets -- -D warnings
cargo build --offline --release --bin photon_bench
python3 scripts/run_bench.py BENCH_MINUS_R1 evidence/bench_minus_r1 SIGNED_MINUS 0 1 2 2 4 7 2
python3 scripts/run_bench.py BENCH_PLUS_R1 evidence/bench_plus_r1 SIGNED_PLUS 0 1 2 2 4 7 2
python3 scripts/run_bench.py BENCH_MINUS_R2 evidence/bench_minus_r2 SIGNED_MINUS 0 2 4 4 8 3 2
python3 scripts/run_bench.py BENCH_FINAL_MINUS_R1 evidence/bench_final_minus_r1 SIGNED_MINUS 0 1 2 2 4 7 2
python3 scripts/run_bench.py BENCH_FINAL_PLUS_R1 evidence/bench_final_plus_r1 SIGNED_PLUS 0 1 2 2 4 7 2
python3 scripts/analyze.py
```

The command argument `0` selects all 384 original source templates. A positive
prefix limit is explicitly a smoke input, never a full-source result. The
dependency sources and locked registry are restored by the root archive's
recovery contract. Build products under `target/` are reproducible and excluded
from source/backup manifests.
