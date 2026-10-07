# Continuous-spectrum adaptive research runner, v1

`igm_adaptive` is an additive, opt-in driver for the existing continuous proper-emissivity model. The `igm_continuous` example and fixed-step API retain their existing behavior. Neither driver implements a restart format or adaptive spectral remeshing.

## Verified manufactured-fixture run

The profile below completed and passed the unchanged numerical criteria on 2026-10-07 for the original manufactured z=12 to 11.5 H/He fixture. It uses 32 threshold-band panels per segment (512 fixed nodes), local relative tolerance 1e-6, and absolute-scale multiplier 1000. Validation covered 21 regular, 81 dense, and 61 frozen off-phase outputs against independently tightened 512-node and 1024-node Radau histories. The worst final comparison ratio was 0.9811165190 (off-phase Gamma_HeII). This is a scoped empirical result, not a rigorous continuum or all-step LTE bound.

From the repository root:

```sh
cargo build --manifest-path rust/rei_microphysics/Cargo.toml --example igm_adaptive --release --offline
rust/rei_microphysics/target/release/examples/igm_adaptive \
  --config configs/igm_manufactured_v1.cfg \
  --output /tmp/igm-adaptive-new-run \
  --spectral-panels 32 \
  --spectral-grid threshold-bands \
  --max-dln-a 0.0002 \
  --output-panels 80 \
  --rtol 0.000001 \
  --atol-scale 1000 \
  --microstep-policy guarded-research
```

If `CARGO_TARGET_DIR` is set, use its `release/examples/igm_adaptive` instead. The output directory must not already exist. The example has no new package dependencies; provenance hashing uses the existing `sha256sum` helper and fails visibly if that program is unavailable.

The example accepts the same config, output, spectral-grid, spectral-panels, max-dln-a, and output-panels options as `igm_continuous`, plus:

- `--output-times FILE`: explicit observation epochs, one `ln_a` number per nonempty line, optionally preceded by the literal CSV header `ln_a`. Values must be finite and strictly increasing, with the first and last values exactly equal to the parsed config endpoints. This option is mutually exclusive with `--output-panels`; it supports frozen nonuniform/off-phase schedules. Exact input bytes are preserved.
- `--rtol R`: finite, positive relative tolerance for every controlled family.
- `--atol-scale S`: finite, positive multiplier applied to **all six** absolute tolerance defaults. The resulting absolute tolerances must also pass the library's validation.
- `--microstep-policy strict|guarded-research`: `strict` is the default. Guarded research behavior requires an explicit opt-in.

Unknown options, duplicates, malformed values, invalid controls, and invalid configurations are rejected before creating the run directory. Twenty output panels mean 21 rows, including the initial and final states. With an explicit schedule, the number of output rows equals the number of supplied epochs; effective `output_panels` is that count minus one.

The manifest records the effective values, rather than requiring readers to infer them from defaults. Current unscaled defaults are:

| Family | Absolute tolerance |
| --- | ---: |
| Ion fractions and electrons per H | `1e-10` |
| Temperature, K | `1e-8` |
| Energy, erg per H | `1e-24` |
| Photon/reaction counts per H | `1e-12` |
| Photoionization rate, per second | `1e-26` |
| Heat rate, erg per absorber per second | `1e-36` |

For the verified profile, multiply the table values by 1000: fraction/electron 1e-7, temperature 1e-5 K, energy 1e-21 erg/H, count 1e-9/H, Gamma 1e-23/s, and heat 1e-33 erg per absorber per second.

The unscaled defaults are not a validated full-history profile. With `--atol-scale 1`, the original fixture drove near-zero Gamma control into tiny steps and stopped in the first-half transaction with `IGM_STEP_ENERGY_LEDGER`, at attempted delta ln(a)=1.3953282973488967e-12. No physical budget was relaxed to bypass that arithmetic/admission floor. Likewise, default `strict` mode intentionally rejects an unsplittable hard-boundary interval; the successful profile explicitly uses `guarded-research` and records 16 unestimated microsteps.

The default relative tolerance is `1e-6`. These are local controller settings. They do not replace the frozen independent-comparison tolerances in `tools/igm_compare.py`.

## Ordinary accepted steps

The controller compares one unchanged physical transaction with two sequential physical half-transactions starting from the same accepted state. It estimates first-order error from their difference and commits the actual two-half endpoint when admitted. It does not Richardson-extrapolate physical fields or ledgers. Every rejected candidate remains private.

The error norm includes the endpoint material state, radiation number and energy, cancellation-free photon spectral L1 defects, per-absorber photoionization and heat rates, and local transaction ledger increments. Local increments are obtained from the physical transaction rather than subtracting large accumulated ledgers. Floating-point half-width asymmetry is recorded by `last_error_factor`; the factor is `0.5 * (h1/h2 + h2/h1)`, which equals one for equal halves.

Accepted macro-steps, physical substeps, rejected LTE attempts, rejected physical attempts, and evaluated trial transactions are separate counters. A coarse candidate does not add its physical ledger or residual history to the accepted state. The manifest includes safety, growth/shrink limits, maximum attempts, maximum trial evaluations, and the microstep motion limit.

## Adjacent-f64 hard-boundary exception

An adjacent representable interval has no interior midpoint, so it cannot receive the ordinary doubling estimate.

- **Strict:** fail explicitly with `ADAPTIVE_UNSPLITTABLE_EVENT` and preserve the last accepted primary state.
- **Guarded research:** a positive-width interval terminating at a hard boundary may be accepted only by the separate noncancelling motion guard. Records label the boundary as a physical event, the final endpoint, or a requested observation endpoint. A retry-created unsplittable interior interval is rejected.

These admitted microsteps are **unestimated**. They are not zero-error steps or LTE-certified steps. The guard compares motion envelopes and equation defects to the same named local scales. Endpoint rate bounds use the post-event support/export convention recorded by `post_event_rate_guard`; exact support changes are distinguished from continuous rate motion.

Every recorded microstep includes decimal and hexadecimal-f64 endpoints, proper time, boundary kind, exact event identities, maximum guard ratio, worst component, per-field bounds and ratios, fraction-equation defects, and energy-equation defect. A failed guard's record is retained in failure diagnostics. Primary and observation records are separate; observation records also identify the sample target.

In JSON, `last_error` and `last_error_factor` are `null` when no current ordinary estimate is available. `last_was_guarded` and `last_error_measured` disambiguate the admission mode. CSV retains numeric previous/default diagnostic values for compatibility with readers that convert every column to a float; **those values are not current estimates when `primary_last_error_measured=0`**. The initial row likewise has no measured step estimate.

## Output times do not drive the primary trajectory

The primary controller always advances toward the configured final endpoint, capped internally by physical events and its own proposal. Requested output times never become its step limits.

For an output inside a primary accepted interval:

1. Keep that interval's accepted left state unchanged.
2. Independently integrate a private observation branch from that same left state to the output time.
3. Write its physical values, account for observation-only work, and discard the branch.

Multiple probes in one primary interval are never chained. An exact primary endpoint is reused without another solve. Sampling does not change the primary controller proposal, ledgers, counters, microstep records, or accepted state. A sampling failure is a failed run with `failure_scope="observation"`; it is never concealed by interpolation or by falling back to the primary endpoint.

For identical representable common output times, this makes all physical and primary-diagnostic CSV columns deterministic across requested grids. The regression compares 21 and 81 rows, full common rows byte-for-byte by their CSV strings, final primary CSV and spectral files byte-for-byte, and primary status objects exactly. Observation work intentionally differs. This is a numerical-programming invariance test, not a continuum-accuracy result.

## Output files and identity

- `history.csv`: requested physical samples, retaining the legacy physical column names consumed by `igm_compare`. Legacy counter/residual columns and appended `primary_*` diagnostics describe the primary accepted right endpoint covering each sample. `primary_ln_a` identifies that endpoint. The initial and final rows use their exact primary states.
- `primary_state.csv`: one row for the last accepted primary state, even when a later primary attempt or an observation fails.
- `nodes.csv`: fixed comoving-energy nodes and quadrature weights.
- `nodes_final.csv`: the last accepted primary readout and authoritative log count at every node, even on failure. Zero readouts do not erase finite log tails.
- `config.cfg`: exact original config bytes. Command-line overrides are recorded separately.
- `output_times.txt`: exact bytes supplied by `--output-times`, or the generated round-trip decimal regular schedule. `output_times_sha256` identifies these exact bytes.
- `effective_config_identity.txt`: versioned identity containing the original-config SHA256, effective max-step f64 bits, effective output panel count, schedule kind, and output-times SHA256.
- `manifest.json`: solver, model, provider, closure, fixed-grid identity, all effective tolerances and controls, microstep policy, exception scope, and sampling convention.
- `status.json`: `complete`, `primary`, independent `observation` totals/records, `failure_scope`, attempted failure diagnostics, and error text.

`config_sha256` hashes the unmodified original bytes. `effective_config_sha256` hashes the exact identity file. `source_sha256` retains the continuous driver's definition: analytic source parameters by f64 bits plus the exact serialized eta nodes and weights. Output panels are excluded from the source identity. The effective config identity includes output panels and the schedule identity, so it changes even though the primary trajectory does not. The manifest labels `output_schedule` as `regular` or `explicit` and records `output_time_count`.

On failure, `primary` refers only to the last accepted main state. `failed_attempt` carries the failed primary or observation branch's diagnostic snapshot; it does not overwrite accepted primary counters. The diagnostic fields `last_attempt_error`, `last_attempt_component`, `last_attempt_width`, `last_failure_code`, and `last_trial_phase` retain attempt-level evidence separately from the last accepted estimate. Observation totals count only work additional to that branch's inherited left state. An unsuccessful estimate's nonfinite diagnostic is represented by JSON `null`, never by invalid JSON tokens. The process exits nonzero on runtime or sampling failure.

These output files are research evidence, not resumable checkpoints. Successful completion does not by itself establish physical or numerical accuracy.

## Regression tests

```sh
cargo build --manifest-path rust/rei_microphysics/Cargo.toml --example igm_adaptive --offline
IGM_ADAPTIVE_EXE="$PWD/rust/rei_microphysics/target/debug/examples/igm_adaptive" \
  python -m unittest discover -s tools/tests -p test_igm_adaptive_cli.py -v
```

Use the corresponding `CARGO_TARGET_DIR` executable when overridden. Without `IGM_ADAPTIVE_EXE`, these integration tests explicitly skip so that the original Python-only test workflow remains usable.

Coverage includes regular and explicit-nonuniform output-grid independence, strict explicit-epoch validation, default strict policy, explicit guarded opt-in, full physical-event microstep evidence, original/effective config hashes, invalid options and tolerances, real work-limit failure, and visible observation failures from unrepresentable requested output times. The neutral event fixture exercises the policy distinction without claiming validation of a driven H/He history.

## Completed validation and cost

At fixed 512 nodes, the completed absolute-tolerance ladder 10000→3000→1000 reduced the worst same-grid CMB allowance ratio 2.1510446763→1.5423571314→0.9141222621. The two looser profiles failed the original field criteria despite conserved photon/energy budgets; their failure evidence is retained. The 10000 exploratory result uses the honestly recorded earlier producer, whose healthy-input update arithmetic is unchanged. The final 1000 and 3000 results are bound to the final validated executable.

The three final 1000 output schedules have bit-identical primary state, final photon counts/log-counts, primary diagnostics, and 21 shared rows. Per run, the main path has 52,176 accepted macro-steps (104,336 accepted physical transactions), 157,889 attempted physical transactions, and 16 guarded microsteps. Observation work adds 57, 237, or 177 trials for regular 21, dense 81, or off-phase 61 outputs. The old accepted fixed-step baseline used 100,583 transactions. This work establishes error-control behavior and scoped accuracy; it does not claim a speedup. Wall times were measured under shared concurrent load and are not a controlled benchmark.

Recorded failures for invalid gas/ledger/diagnostic data, contradictory normal count/log pairs, work/min-step exhaustion, nonfinite norms, and failed observation probes remain explicit. The legacy fixed driver's checked output files are byte-identical before/after the additive transaction diagnostics.

## Claim boundary

A local error estimate and conservation admission are not global error bounds. Independent temporal and spectral refinement, dense/off-phase checks, and the unchanged frozen field/ledger comparator remain necessary. This additive driver does not establish observed EoR validity, Bianchi coupling, continuum spectral convergence, restart support, or a certified global tolerance. Passing a synthetic controller or CLI test must not be reported as passing those broader claims.
