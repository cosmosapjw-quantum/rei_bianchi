# Independent review of the actual pressure execution

## Advisory decision

**PASS_SCOPED — the single authorized finite positive-measure pressure fixture
completed successfully within its stated resource allowance.** No actual
implementation, input-binding, fixture-reach, or resource-compliance defect
was found in the inspected evidence. One non-scientific historical accounting
label defect, identified by root, was corrected by the worker and independently
verified here. Unresolved findings: zero. Root's scientific admission remains
a separate decision.

Reviewer: `/root/pressure_review`, separate from `/root/pressure_coding` and
not an implementer or executor of this module. This is a native read-only
review with the same inherited model family. Cross-family independence is not
claimed. The review consumed the actual files and raw receipt; it did not
rerun, import, compile, or numerically reevaluate the implementation.

## Inputs actually reviewed

The complete read set, sizes, and SHA-256 values are recorded in the companion
`PRESSURE_EXECUTION_REVIEW.json`. Full text/JSON was read for the 12 prepared
files in the current copied pressure directory, all four actual raw files,
the current authorization overlay and root GO, both preflight records,
`execution/EXECUTION_RESULT.json`, the saved current AGENTS policy and identity
record, and the Stage A backup receipt. The retained pre-repair execution
result, metadata repair record and final budget closeout were also inspected.
The 12 prepared originals and four
original raw files were read mechanically for byte comparison.

The current copied pressure directory is
`work/research/rei_source_pair_binding/hi_pressure_next_20261024/` under this
review root. The actual command ran the frozen original directory under
`/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/`; the new directory
contains byte-identical source and raw copies. This review does not claim a
second execution at the copied location.

| Frozen file | Observed SHA-256 | Comparison |
|---|---|---|
| `pressure_interval.py` | `8ab04ea247a43328432fd0b57899c501e298f356736b60a73e5e1ec345228e77` | Original, copied file, frozen record, GO and raw binding agree |
| `focused_check.py` | `0bdd8c8017a6e52953a713fa7b74603f5cbc14b42794cbad676be7be4c4ba7d4` | Original, copied file, frozen record, GO and raw binding agree |
| `run_focused_once.py` | `3eff72d14c6ee996e1cfb4b617ddc0fc3cfb914d9cca8e29c28a0906bbea24fe` | Original, copied file, frozen record, GO and raw binding agree |

All 12 prepared files match their preflight hashes and original bytes,
including theory, contract, proposal, binding, README and the previous analytic
and static reviews. All four copied raw files equal the actual original raw
files. The attempt, resource receipt and stdout embedded in
`EXECUTION_RESULT.json` equal the corresponding actual raw JSON records.
Stdout/stderr hashes agree with the resource receipt. Hash comparisons bind
the reviewed inputs and recovered evidence; the fixture assertions establish
the arithmetic result.

## Theory, implementation and actual fixture reach

The unchanged analytic and static reviews remain applicable. The source
implements the stated conditional moment problem for a finite nonnegative
measure on `0 <= k <= L`, with `M > 0`, `N,U,L >= 0`, and exact represented
feasibility `U <= N*L`. Its pressure kernel is

\[
g(k)=\frac{k(k+2M)}{k+M},\qquad
\Pi=\frac13\int g(k)\,d\nu(k).
\]

The lower and upper formulas, width, nonrelativistic comparison and error
bound correspond to the frozen theory and contract. Zero branches avoid a
zero upper denominator. Atom accumulation uses caller-supplied nonnegative
weights and energies with the same support; it performs no HI source loading,
provider qualification, donor integration, transport or unit conversion.

The fixture contains one group, with all checks before its final JSON print.
The raw stdout contains that final print, and the receipt records exit 0 with
empty stderr and no launch error or timeout. Together with the fixed inspected
fixture this supports successful completion of the following contracted
checks:

| Contracted check | Fixed assertions reached by the observed run |
|---|---|
| Moment interval | For `N=U=L=2, M=1`, lower `8/9`, upper `1`, width `1/9`, NR pressure `4/3`, NR error upper bound `4/9` |
| Attaining atom measures | `(1,0),(1,2)` gives `8/9`; `(2,1)` gives `1` |
| Half mixture | `(1/2,0),(1/2,2),(1,1)` gives `17/18`, lies inside the interval, and satisfies the NR error bound |
| Separate algebraic reference | Atom results equal a separately written sum using `k+M-M^2/(k+M)` |
| Zero cases | Four zero-moment cases, empty atoms, and positive weight at zero support return their specified zero pressure values |
| Invalid moments | `N=1,U=3,L=2,M=1` is refused with `DomainError` |
| Common scaling | Multiplication of atom weights by `7/3` scales `N,U,Pi` and every interval output linearly |

These fractions are the fixed assertions read from the fixture, supported by
the successful run; stdout itself contains completion flags rather than a
table of measured fractions. The atom reference shares the Fraction arithmetic
backend and is an algebraically separate check, not an empirical physical
oracle. Guards for every other unsupported type, malformed pair, nonfinite,
negative, or out-of-support input were not all exercised by this finite group;
the previous static review's coverage limit is retained.

## Actual execution and allowance

`ROOT_GO.json` releases exactly one prepared child under the current user
authorization. Its UTC timestamp precedes the raw attempt timestamp
`2026-10-24T08:50:56.402947+00:00`. The wrapper invokes the frozen fixture once,
sets CPU soft and hard limits to 1 second, records launch-inclusive elapsed
wall time, and has no retry loop. The intake records that the attempt and raw
files were absent before release; this review reads that historical intake
record rather than claiming to have observed the prelaunch filesystem itself.

| Quantity | Actual record | Authorized limit/status |
|---|---:|---|
| Scientific child attempts | 1 | Maximum 1 |
| Child user CPU | 0.034017 s | Component of child total |
| Child system CPU | 0.010748 s | Component of child total |
| Child total CPU | **0.044765 s** | Soft/hard 1 s |
| Launch-inclusive elapsed wall | **0.04515560300023935 s** | 5 s |
| Child / wrapper exit | 0 / 0 | Successful completion |
| Timeout / launch error | false / null | None |
| Automatic retries | 0 | 0 |

The actually observed child CPU and wall time satisfy the allowance. This is
an observation of this successful invocation, not a general certification of
timeout behavior under every future failure condition. The raw record reports
Python 3.12.14 and the frozen `-B` invocation. The review performs no runtime
probe or further scientific invocation.

The execution record advances the known partial child CPU from 10.193342 s to
10.238107 s by adding this child's 0.044765 s. The historical 10-second-capped
sequence consumed 10.110448 s, exceeding that cap by 0.110448 s. This excess
is not a separate child's CPU debit, and its `FAIL_PRESERVED` status remains.
Whole-L0 cost remains
unknown, not zero; the original cumulative cap remains not frozen. Parent
I/O, review, model and remote costs remain separately unmeasured. No old
allowance is transferred or reset.

### Resolved accounting-label finding

The initial `EXECUTION_RESULT.json` mislabeled 0.110448 s as
`historical_failed_child_cpu_s`. Root identified this non-scientific metadata
defect, and `/root/pressure_coding` performed the authorized metadata-only
repair: replace that key with `historical_10s_overrun_s` and add
`historical_overrun_status: FAIL_PRESERVED`. The number itself and the known
partial CPU sum did not change. The corrected `BUDGET_CLOSEOUT.json` explicitly
distinguishes the prior sequence debit, its overrun, and later child debits.

The pre-repair result was retained as
`execution/EXECUTION_RESULT_PRE_METADATA_REPAIR.json`; its SHA-256
`a494106e3d31696ec37573492da7523adb0d04ac019007301d03f13f611ee0bc`
equals the initially reviewed result. The final current result SHA-256 is
`0e3fa125f359143e6021bc99302f7faf12bf2c6d42d983480a2ee9b617f20ea3`.
A complete JSON comparison found exactly the stated key removal, key addition
and status addition, all under `historical_accounting`. Raw, science inputs,
results and proposal remained unchanged. This review's draft description
inherited the same mislabeled meaning and has been corrected in the final
review. Finding status: **RESOLVED; scientific result unchanged; reruns 0**.

## Historical metadata and current executor

The frozen proposal, source binding, README, docstrings and previous reviews
describe the preparation epoch. Their `NOT_AUTHORIZED`, `NOT_RUN` and
`UNEXECUTED` wording has not been rewritten into a current outcome. Likewise,
the runner copies the proposal's `/root/uv_coding` executor field into the raw
receipt. That field identifies historical preparation metadata; it is not
independent evidence of the worker that invoked the wrapper today.

The current authorization overlay, root GO and execution result consistently
identify the actual invoking worker as `/root/pressure_coding`. They record
requested model `gpt-6.1-sol`, requested effort `high`, and observed backend
model/effort `unknown`. The current overlay supplies authorization separately
from the frozen proposal. This explicit distinction resolves the historical
metadata without changing the scientific input or overstating runtime model
identity. No amendment of the frozen raw file is required.

## Scoped recommendation and limits

Root may admit **the successful finite exact-arithmetic pressure fixture for
the pinned module and stated positive-measure domain**. That decision may
reuse the unchanged analytic and static PASS records and add this observed
single-child result.

This review does not admit a physical HI pressure value, calibrated EOS,
physical uncertainty band, qualified raw-atom provider, accumulated stock,
redshift/stopping history, self-consistent recombination/reionization,
Einstein coupling, L4, or whole-model completion. The injection-rate versus
stock unit distinction remains a caller obligation. The actual fixture uses
the stipulated dimensionless example and does not consume HI moments or a
donor spectrum. New redshift-stock theory and static preparation are separate
work and are not validated or authorized for execution by this review.

The current root-supplied source and policy snapshots were read as saved
evidence. No independent network resurvey or external backup byte redownload
was performed. The Stage A receipt records completed dual uploads and matching
metadata sizes; no stronger remote-content claim is made here.

**Stopping rule satisfied:** actual evidence has been reviewed and the one
metadata-only repair has been verified. No further repair is requested.
Proceed to root's scoped admission and authorized
delivery; do not rerun the fixture or add adjacent validation gates.

## Review actions

Only text/JSON reading, byte/hash comparison, and writing these two review
files occurred. Candidate/fixture/runner imports: 0. Compiles: 0. Scientific
executions and reruns: 0. New numerical evaluation or CAS: 0. Rendering: 0.
Implementation edits, Git mutations and cloud mutations: 0.
