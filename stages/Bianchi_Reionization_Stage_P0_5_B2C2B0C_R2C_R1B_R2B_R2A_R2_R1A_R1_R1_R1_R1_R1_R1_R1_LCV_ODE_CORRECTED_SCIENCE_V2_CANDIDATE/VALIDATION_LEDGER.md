# VALIDATION LEDGER

## Claim boundary

Every captured command is classified `TEST_ONLY_NOT_SCIENCE`. A zero exit code
validates only the named fixture/primitive in the observed local environment.
No command in this ledger ran a production history, BDF reference, parity
campaign, package build, endpoint generation, or publication analysis.

Authoritative per-run material is under `audit_runs/<name>/`:

- `manifest.json`: canonical full argv, resolved executable stat/hash, cwd,
  fresh environment, explicit import-root identity, Git HEAD/tree/status, UTC
  timestamps, monotonic duration, return code/signal, limits and raw hashes;
- `manifest.json.sha256`: sidecar over the exact manifest bytes;
- `stdout.bin` and `stderr.bin`: exact captured byte streams.

`AUDIT_RUN_INDEX.json` is a non-circular summary. All ten streams were complete
until child termination; none hit the output caps or timeout.

## Pre-capture baseline

Before N existed, the ambient-shell neighboring suite ran 49 tests and passed:

```text
CWD: /tmp/rei-ode-integrated-audit.ZcRbz6/worktree
ARGV: python3 -B -m unittest discover -s <A-stage>/tests -p 'test_*.py'
EXIT: 0
WALL: 8.63526495 s
DECISIVE STDERR: Ran 49 tests in 8.545s / OK
```

Runtime then observed CPython 3.12.3, NumPy 2.4.2, SciPy 1.17.0 and pandas
3.0.0. This ambient run predates the capture runner and therefore has no
per-stream manifest. It is retained as local baseline evidence, not parity.

## Captured run matrix

| Run | Exact purpose | Exit | Duration ns | Decisive result | Manifest SHA-256 |
|---|---|---:|---:|---|---|
| `001_predecessor_red` | predecessor combined witness | 1 | 151454890 | NumPy unavailable because initial fresh environment disabled user site; no vector executed | `eda5f81019264afeea422795f5548859729699c00d8509700244e735353b8376` |
| `002_successor_focused` | all N tests by discovery | 1 | 715681436 | 37 displayed tests passed; shadow setUpClass failed on one overlong C-stage path constant | `567b414bee67fdd48c3dfb5d95fb27880309e347833211f52f3873b9d2d2b2a3` |
| `003_neighbor_49` | predecessor neighboring 49 tests in fresh capture env | 1 | 8677387798 | 46 passed; three launcher tests assumed ambient `PATH` and raised `KeyError` | `a78d677d02db21fb22591dc36b15f96e9dd643118a6f2487a4aec559c9b3e2a5` |
| `004_audit_capture_tests` | post-repair capture policy | 0 | 617249747 | `Ran 5 tests in 0.560s`, `OK` | `9566e07ee9f3f8de09f5f1eb656a5c39650ee734a6ad6d0f4cac7df7e4fef1c5` |
| `005_numerical_physics_tests` | exact arithmetic, exact point certificates, physics | 0 | 101266094 | `Ran 22 tests in 0.021s`, `OK` | `b2bc3c1a891bf5181a7a73b88275d27c312b8ab3cf05139b9f270a481b12b756` |
| `006_admission_fsm_tests` | closed evidence admission and total FSM | 0 | 68421501 | `Ran 11 tests in 0.005s`, `OK` | `05cf314e53bec19b8af758cc82cd26410a8472177e84ce7aba6ba861103e3625` |
| `007_successor_vector_a` | deterministic integrated successor vector | 0 | 55965249 | exact/vector JSON, stdout SHA `e353ab...13b1b` | `332d996d024e520817299a48a2b778faa2b2dcb3569536f466e26420aa6ade08` |
| `008_successor_vector_b` | exact repeat of integrated vector | 0 | 55563184 | byte-identical stdout SHA `e353ab...13b1b` | `0ecf92f1af63fb50f35eb0c32eba8bfe259d9760c8a186420b537435eb0df969` |
| `009_predecessor_manifest` | all frozen predecessor ordinary files | 0 | 67637380 | 1012/1012 hashes, zero failures | `62c2672498327de8cdf8f28b54da2c9416e58af2bccb6adadcb72da534faf8f2` |
| `010_runtime_identity` | import/runtime identity | 0 | 250416322 | CPython 3.12.3; NumPy 2.4.2; SciPy 1.17.0; pandas 3.0.0 | `1841c1ee6c63e28934b839df26c07fa9d95d29f95a01b3ab8f06d2516626589c` |

The full commands and UTC timestamps are intentionally not abbreviated in the
manifests. The Git tree in every run is
`2f541ee051f0844bdeed88fd2dcba2a0c54ab035`, HEAD is
`111b6ace750e36e218df7fc9626c6bad2ec19971`, and status hashes change as
additive untracked N evidence accumulates.

## Exact successor vector result

Both repeat runs emitted exactly 2,824 stdout bytes with SHA-256
`e353ab05f9158e319f69d3251a890ee29ca587fbcf194654a74f1c7ccac13b1b`.
The decisive values are:

- signed binary64 sequence `[1e20, 1, -1e20]`: exact sum `1/1`, outward
  binary64 `[0x1.0000000000000p+0, 0x1.0000000000000p+0]`;
- simple point system: exact determinant `1`, exact solution `(4,7)`, exact
  residual zero, independent replay PASS;
- M-matrix system: exact determinant `10011`, exact solution
  `(30001/10011, 32/10011)`, outward binary64 coordinate enclosures and
  independent replay PASS;
- per-H fixture: abundances `(1/2,0,79/1000)`, opacities
  `(7,0,553/200)`; no second helium factor;
- direct owner shares for raw `(3,5,2)`: `(3/10,1/2,1/5)`; nonzero current
  with zero opacity gives `NONZERO_CURRENT_WITH_ZERO_OPACITY`;
- complete ten-gate evidence is `ADMITTED`; deleting `CORRECTED_LINEAGE` is
  `BLOCKED`; the worker success claim has no authority;
- malformed action on terminal `BLOCKED_EVENT` is byte-identical,
  `TERMINAL_NO_WRITE`, and `write_required=false`.

## Preserved failures and non-rerun rule

Runs 001--003 are not removed, renamed, or superseded. The sole repair-closeout
added an explicit resolved import root, corrected the probe's C-stage path, and
set a fixed public `PATH=/usr/bin`; the changed capture code then passed its
dedicated five-test module. The exact failing discovery and neighboring
commands were not rerun because the frozen global same-failure retry had
already been consumed by the earlier source-exact Krawczyk probe correction.

There was also one outer invocation typo before run 004: the shell cwd was the
N test directory while the capture-runner path was relative to repository root,
so Python reported “can't open file” before a capture directory or child was
created. The command was corrected to an absolute runner path. It is an
operator/instrumentation dead end, not evidence about any module.

## Environment and reproducibility ceiling

The imported scientific packages reside in
`/home/cosmosapjw/.local/lib/python3.12/site-packages`. The explicit root is
path/direct-listing identified in each applicable manifest, but is not a
recursive content seal. Dependency versions do not match the older declared
runtime pins. Therefore these runs are reproducible local diagnostics, not a
pinned-runtime replay or scientific reference execution.
