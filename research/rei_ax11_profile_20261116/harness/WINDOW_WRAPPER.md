# Bounded native AX11 window wrapper

`ax11_profile_window.rs` calls the original public `Driver` APIs. It is a finite
initial prefix or checkpoint continuation, not a full cosmological-history
runner and not evidence that AX11 refinement is complete.

## Invocation

Install the file as `examples/ax11_profile_window.rs` inside each isolated source
variant crate. The deployment runner first verifies all source-manifest hashes,
the exact original config hash and, for restart windows, the exact checkpoint
hash. It must not infer identity from a file name or a branch label.

```sh
cargo build --release --example ax11_profile_window
RUSTFLAGS='--cfg ax11_profile' cargo build --release --example ax11_profile_window
```

The first form applies to the untouched original driver; the second applies to
the instrumented driver. Build them in separate variant directories/target
directories to avoid confusing executables. These commands are suggested
invocations, not a claim that compilation or native execution was performed in
the cloud environment.

```text
ax11_profile_window CONFIG CHECKPOINT|IC NEW_OUT ACCEPTED_DELTA ATTEMPT_DELTA_CAP RHS_DELTA_CAP FRESH_WALL_SECONDS [STOP_A|NONE] [CASE_ID]
```

All three count arguments and the wall argument must be finite positive values.
`NEW_OUT` must not exist; its parent must exist. The default case label is `ZERO`
for q=0, `PLUS` for q=+0.01, `MINUS` for q=-0.01, and `AX11` otherwise. Pass an
explicit case label when a canonical label differs. Current approved bounded
profiling uses `NONE` for `STOP_A`.

The wrapper parses only checkpoint resource counters/wall before construction,
sets effective cumulative caps to old accepted+requested+1, old attempts+cap,
old RHS+cap and old wall+fresh wall cap, constructs the original driver, and then
uses its `read_checkpoint`. It verifies that the recovered counters/wall equal
the preparsed values. No scientific config field, including `end_zbar`, is changed.

Attempt and RHS caps are native strict caps inside the original driver. Wall
checks are cooperative at comparison boundaries; the deployment runner remains
responsible for the externally enforced hard process cap, 64 MiB output cap and
512 MiB memory cap. A single adaptive comparison cannot be interrupted by this
wrapper without changing the original algorithm. The native original resource
checks are also retained at checkpoint cadence.

Exit 0 means a finite window completed, not that the full represented interval or
AX11 completed. Exit 2 means a cap, failure, unsupported endpoint or setup error.
The wrapper emits one compact final stdout status and a compact stderr error.

## Scientific output and error preservation

`history.csv`, `abundances.csv`, `spectra.csv`, `ledgers.csv` and `feedback.csv`
have exactly the original headers and are written by `Driver::output_batch`.
Every window includes its initial state, even for a checkpoint restart; thus
these are new scoped tables and should not be appended directly to an existing
full trajectory without removing its already represented initial row.

Spectra use original initial / configured accepted interval (normally 60) /
30 wall second / terminal cadence. `checkpoint.start.txt`, `checkpoint.txt`,
cadence checkpoints under `checkpoints/`, and `checkpoint.end.txt` preserve
cumulative counters, prior wall and original full scientific state. Original
rejection handling and output-batch rollback preserve paid trial/comparison/RHS
cost. No retries beyond the original adaptation are introduced. Original source
identity, original config and the effective resource config are copied into the
new window directory. The existing feedback table is preserved; the private
driver function that makes a secondary feedback summary is not called.

Two speed variants can trigger different 30 wall second spectrum snapshots.
Require exact equality of accepted-state traces and the four every-state tables.
Compare spectrum rows at common `(case_id,time_s)` snapshots and separately
record any unmatched wall-cadence snapshots; never call the entire spectra files
byte-identical unless the cadence sets also match. The separate deterministic
driver output tests can supply stronger matched-cadence byte/reserve evidence.

`raw/error_components.csv` exists only for `cfg(ax11_profile)`. Each native
comparison records its starting a, proposed endpoint and step, actual accepted /
rejected / error outcome, cumulative before/after costs, wrapper-measured adaptive
nanoseconds and the six source-defined normalized defects. When the driver did
not complete the error comparison, all six values are `NA` and
`components_available=false`; stale `last_error` is not emitted as a fresh defect.

`raw/driver_timing.csv` and `raw/background_timing.csv` are snapshots of the
instrumented hooks. Scopes are inclusive and can be nested. Their times must not
be added as if they were disjoint. Window wall includes trace/diagnostic I/O;
adaptive nanoseconds exclude that I/O. Setup and final persistence are separately
distinguished from the original-style evolution wall in `window_summary.json`.
The wrapper adds full-state trace output and therefore its wall time is not a
measurement of the unwrapped historical launcher.

## Bit-exact accepted-state trace

`raw/state_trace.bin` is little endian. It includes the initial state, followed
by every accepted state whose scientific output batch succeeded. Floats are
stored as their exact IEEE binary64 `to_bits()` values; no decimal formatting or
numeric tolerance is involved. Wall time is deliberately excluded. The terminal
checkpoint separately retains costs incurred by rejected or failed trials after
the last accepted record.

The 56-byte header consists of eight-byte magic `AX11TRC1`, followed by six u64s:

1. Photon-vector length.
2. Scalar count, always 32.
3. Counter count, always 6.
4. Record size in bytes, `8 * (38 + photon_length)`.
5. Number of records actually written.
6. Initially reserved maximum records, `accepted_increment + 1`.

Each record contains 32 f64-bit u64 words in this order:

```text
a, x_HII, x_HeII, x_HeIII, w_erg_per_H,
next_dln_a, max_newton_residual, last_error,
source_n, source_u, absorbed_n, escaped_u,
boundary_n, boundary_u, thermal_work, photon_work, cmb_input,
dr_events, ce_cap_ev, excluded_dr_ev,
rr_events[0:3], ci_events[0:3], photo_events[0:3], ci_floor_events[0:3]
```

Then six ordinary u64 counters:

```text
accepted, attempts, comparisons, rejects, consecutive_rejects, rhs_evaluations
```

Then the complete photon vector, in the original driver order, as f64-bit u64s.
The file reserves its maximum size before scientific output begins, so the
original output guard counts all future trace bytes in advance and retains its
terminal-spectrum/checkpoint reserve. Successful finalization truncates the file
to actual written records. After interruption, read only the record count in the
header; reserved zero-filled space is not physical data. A failed/partial record
must not be counted by the consumer.

`window_summary.json` reports prior/end/delta cumulative costs, a/proper-time
endpoints, evolution/setup/process wall, caps and outcome. Its
`delta_counts.consecutive_rejects` is explicitly the end value, not a difference;
all other delta counters are differences. If final persistence fails, the
separate `finalization_error` field preserves that distinction.

## Optional fixed-a interface

The original public `adaptive_step` has only the scientific config endpoint.
For optional future `STOP_A`, the wrapper adjusts a crossing proposed step only
when an allowed binary64 step reproduces the requested a exactly under the
original `a * exp(h)` expression. It preserves `end_zbar`, accepts no approximate
endpoint, and reports `AX11_FIXED_A_UNREPRESENTABLE` if the representation cannot
be achieved within its finite search, or if the needed step is below the
original minimum. This is an explicit interface limitation, not a new physical
gate. It does not affect current `STOP_A=NONE` profiling. A robust general fixed-a
refinement runner would need a separately admitted exact endpoint API.

## Minimal consumer checks

1. Build original and instrumented executables from their separately verified
   source trees; preserve build errors and the exact compiler/version evidence.
2. Use identical config/checkpoint/finite caps, canonical case label and `NONE`.
   Do not rerun any completed full baseline.
3. Check exit status, complete summary/checkpoint output, and trace shape before
   asserting equality. Compare trace headers/actual records and the four
   every-state tables exactly, then use the cadence-aware spectrum comparison.
4. Inspect every unavailable component marker and rejected/failed comparison.
   Keep prior cumulative costs separate from newly paid costs; record any
   externally killed process as interrupted with unknown unfinished cost.
5. Treat equality and measured cost as scoped implementation evidence. They do
   not supply dt/dE/dmu refinement error bounds or complete AX11.
