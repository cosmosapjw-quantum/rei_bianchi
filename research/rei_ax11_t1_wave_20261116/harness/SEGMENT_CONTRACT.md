# AX11 T1 finite production segment

This entry point uses the verified candidate crate at
`ax11_work/source_v2/instrumented/rust/rei_microphysics`; the driver read for this
implementation is 65,377 bytes, SHA256
`e7c6ffcbc9a400eef550c050221824900382d32d215295dcf218ae0443d02deb`.
The original adaptive/output/checkpoint methods and recursive byte guards remain
unchanged. Native compilation and execution are the owning launcher's next step,
not evidence supplied by this authored wrapper.

```text
ax11_production_segment CONFIG CHECKPOINT|IC NEW_OUT ZERO|PLUS ACCEPTED_DELTA [SEGMENT_FRESH_WALL_SECONDS]
```

Install as `examples/ax11_production_segment.rs` in the isolated candidate crate.
Build with the same verified settings, including `--cfg ax11_profile` if terminal
timing snapshots are wanted. Set **`AX11_CACHE=1` and `AX11_LAZY=1`** before each
process: both candidate options otherwise default to OFF. The outer launcher
verifies input, binary, full source corpus, config and checkpoint hashes before
each execution, and owns aggregate two-case CPU, disk and segment accounting.

`NEW_OUT` must not exist and its parent must exist. The only supported physical
configuration is the original ZERO/PLUS scenario with T1 local target
`2.5e-6`, initial proposed step `1e-4`, original temperature/escape/grid/background
settings, original zbar4 endpoint and 60 accepted-step spectrum cadence. This
wrapper does not mutate physical fields. It sets only resource fields to the
approved cumulative case limits: 1,800,000 accepted, 5,400,000 trials,
43,200,000 RHS, 9,000 wall seconds and 2,048 MiB per segment. Checkpoint counters,
wall, photons, gas, ledgers and adaptive state are never reset. An accepted
increment must be between 1 and 250,000. The optional fresh segment wall cap is
positive and at most 9,000 seconds; cumulative case caps still take precedence.

| Exit | Meaning | Launcher interpretation |
|---|---|---|
| 0 | `SCIENTIFIC_ENDPOINT_ZBAR4` | Native case endpoint reached; scientific admission remains separate. |
| 10 | `SEGMENT_ACCEPTED_BOUNDARY` or `SEGMENT_WALL_BOUNDARY` | Controlled boundary; a verified endpoint checkpoint can initialize the next authorized segment. |
| 11 | `CASE_*_CAP` | Cumulative case budget exhausted; no automatic continuation beyond the approved budget. |
| 2 | Real/setup/finalization failure | Preserve all outputs and costs; no process retry. |

The original adaptive handling of rejected tentative steps remains inside one
process. It is distinct from a process retry. Paid trial/RHS/comparison costs
survive rejection, cap exhaustion and output-batch rollback. An output guard
failure remains a failure; the wrapper does not enlarge its allocation or
silently roll into another segment. A checkpoint save failure is recorded
separately from the original outcome. As in the original runner, wall checks are
cooperative at comparison boundaries. The outer hard cap must account for setup,
finalization and any interrupted unfinished work; original-style cumulative
evolution wall and separately measured process wall are both reported.

All original five scientific tables and the rejection table retain their exact
headers. A new segment writes one initial checkpoint-state row and its complete
initial spectrum, then every accepted-state scientific row, the original
60-accepted/30-wall-second spectra/checkpoints, and the terminal spectrum.
Every cadence checkpoint is retained. `checkpoint.start.txt`, `checkpoint.txt`
and `checkpoint.end.txt` preserve full scientific/adaptive state. Across segments,
the first row is a shared boundary, not another physical step; consumers must
handle that duplicate explicitly. Source identities are saved at start and end;
the original and effective resource configs are both preserved.

There is no full-state trace, trace preallocation, component CSV or additional
every-step diagnostic I/O. The original rollback clone is retained. Only a scalar
maximum of newly accepted local defects is accumulated; it is not a refinement
bound. `progress.json` is atomically replaced at start, existing checkpoint
cadence and terminal completion. It contains a, proper time, cumulative counts,
wall, adaptive fields and outcome. Each receipt is limited to 8 KiB and all
receipts/timing metadata fit the launcher reserve. The unchanged recursive
scientific guard also counts existing auxiliary files, which is conservative.
`segment_summary.json` and `RETURN.txt` provide complete start/end/delta costs,
last metric, Newton residual, native outcome and finalization status. A missing
terminal receipt after external interruption never means zero unknown cost.

## Forecast limitation retained from the actual source

The original `output_batch` calls `directory_bytes` recursively on every accepted
step, and checkpoint saves use the same guard. With 60-step checkpoints, a
250,000-step segment accumulates about 4,167 retained checkpoint files and roughly
`N^2/120 = 5.21e8` checkpoint-file visits from the every-step guard alone. This is
a design count, not a measured elapsed-time claim. The verified 1,024-step prefix
cost therefore cannot be linearly extrapolated to 250,000 steps. The owner must
use actual finite segment timing before forecasting the full T1 wave. This
wrapper deliberately preserves guard semantics and all checkpoint evidence.

The planned finite preflight is PLUS128 followed by PLUS128 from its exact
checkpoint, and ZERO256, compared against already saved T1 prefixes. Its costs
belong to the outer cumulative budget. Compare common physical states and
cadence-qualified spectra; a chained segment adds its explicit boundary spectrum.
No preflight or production execution is performed by this authoring task. DAG
counts remain original **10/17**, expansion **28/88** until the owner consumes
new native physical/error evidence.
