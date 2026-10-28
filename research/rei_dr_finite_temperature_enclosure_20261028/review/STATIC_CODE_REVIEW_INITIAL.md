# Independent static implementation review — DR enclosure

Native reviewer: **`/root/current_repo_census`**. Unit: `rei_dr_finite_temperature_enclosure_20261028`.
Initial source-only judgment at **2026-10-28 11:08:28 UTC**: **TWO_BOUNDED_TARGETED_REPAIRS_REQUIRED**.
Workflow status remains **C9 STATIC_ONLY_NOT_RUNTIME_ACCEPTED**; **C6, C7 and C8 NOT_RUN**.

This single static addendum preserves the separate initial R6 judgment in `INDEPENDENT_THEORY_REVIEW.md` unchanged. The reviewer did not author the inspected implementation, tests, plot or supervisor. The review uses shared source/census context and is not blind. No scientific module was imported or executed, no compilation, test, CAS, benchmark or plot was run, and no runtime success is inferred from this source inspection.

## Complete source reads and identities

`STATIC_READ_LEDGER_INITIAL.json` preserves complete pre-repair reads, line counts, byte sizes, SHA256 and Git blobs. The original theory/source reads remain in `THEORY_READ_LEDGER.json`.

| File | Complete initial read | Initial SHA256 |
|---|---|---|
| `code/dr_enclosure.py` | 1–229 | `7cd06394c18cc478aa2af259cb0323aa62365083a457e04c13963f117442d840` |
| `tests/test_dr_enclosure.py` | 1–123 | `a3adad589a8acf40a0d8bdd6b50175cfe053057c63ee9cf72f3a72e77cb5eb3b` |
| `code/run_once.py` | 1–81 | `71cf227bdd965f2087b655e4b81de1df765f5c8abf11eb5170091f4e5f3de16e` |
| `code/plot_saved.py` | 1–73 | `ba410df5a2099682d9c455f0d2b263fda10673aa6069893e30d04ee548f39b2a` |
| `code/execute_bounded.py` | 1–111 | `474c239dabddf1990a4487ab35b1cf130f9c9174f77d2de7cb37c72f3a7cdd0b` |
| `code/PREPARATION.md` | 1–25 | `dee71f84ce25f6a68819e385687edcbc05e141b0fa1133e7101e116a5a3274ad` |
| `code/PREFLIGHT_FINDING.md` | 1–12 | `c7e5664fc51c5b0e842d2d430745f34c419eae4bec654acbf49b20e90cbf3a9d` |
| `PREPARED_IDENTITIES.json` | 1–50 | `c3e6247d2a66457f21ca461472541d98c303942386996830758d1852a5f4425b` |

The official Python Decimal documentation was read on 2026-10-28 for conversion, correctly rounded exp/ln, neighbouring representable values, exponent limits and traps: https://docs.python.org/3/library/decimal.html . Relevant sections are `Decimal.from_float`, `Decimal.exp`, `Decimal.ln`, `Decimal.next_minus`, `Decimal.next_plus`, `Context.Etiny`, `Subnormal` and `Underflow`. This is a trusted arithmetic-library dependency, not a new numerical execution or an independently verified libmpdec implementation.

## Equation-to-code inspection

### Encoding, arithmetic and D1

`number` accepts explicit int/Decimal and exact float images while refusing bool, complex, NaN and infinity. `load_source` checks the pinned coefficient bytes and exact three-row set. `parameter_images` records float hex, integer ratio and exact decimal image. The runtime model draws valid keys from the retained recombination key set and treats a missing DR row as structural absence, with unknown keys rejected.

Basic interval addition and corner-product extrema use explicit downward/upward contexts. Negation and magnitude use quiet exact sign operations. Division reverses reciprocal endpoints correctly for either sign of a nonzero denominator interval. `transcend` uses a nearest-rounded monotone endpoint evaluation and expands its neighbours. On the selected positive temperature and exponential ranges this encloses the mathematical values. The large exponent range includes the smallest required exp(-117000); the enabled subnormal/underflow traps prevent silently accepting a lost positive support value.

`kernel` evaluates exp(-E/T)/(T sqrt(T)) using interval operations. `term_range` evaluates both endpoints, uses exact Fraction peak membership, and adds an outward enclosure of the exact2E/3 peak when needed. The lower endpoint is the minimum of the two endpoint lower bounds and the upper is the maximum candidate upper. This follows D1.

### Signed positivity, loss products and D3–D4

`positivity` constructs exact Fraction coefficient or coefficient-energy weights and checks the actual D2 ordering and strict margin. `weights` keeps s, k, c and E as separate exact-image inputs surrounded by interval operations. No clipped amplitude or pre-rounded c*E constant is introduced.

`range` sums signed interval terms, then tightens only its lower endpoint with the positive rewritten source-specific expression. The replacement correctly uses (c0+c2)g0+c1g1 for alpha, or (c0E0+c2E2)g0+c1E1g1 for loss, and the unchanged signed total upper. All-positive rows use their ordinary lower endpoint. The strict-support check is explicit.

`first_log_derivative` implements the D3 multiplier E/T−3/2. `second_bound` uses the outward x interval, its endpoints and x=2 when included, interval evaluation of q2, absolute weight bounds and each kernel upper. Correlation is discarded conservatively. `taylor` validates both endpoints inside I, encloses the log ratio, base value and derivative, and uses an upper B2 times the squared maximum absolute h divided by2. This is correct for its ordinary nonzero steps. The valid zero-step edge has finding F-ZERO below.

## Concrete findings and bounded repairs

### F-ZERO — exact zero log step reaches trapped subnormal arithmetic

**Target:** initial `code/dr_enclosure.py` lines219–229, especially223 and226.

**Static counterexample:** `m.taylor('2:1', 100, 101, 100, 100)` is within the admitted contract. The point and center intervals are exactly[100,100]. Their reciprocal-product ratio is exactly1 because1/100 is a terminating decimal. Its correctly rounded log is exactly0. `transcend('ln')` then expands0 to the nearest nonzero representable values. At precision60 and Emin−999999, Etiny=−1000058, so the h interval has subnormal endpoints ±10^-1000058. The subsequent positive curvature-bound multiplication at line226 produces a subnormal/underflow result and encounters the explicitly enabled traps.

**Impact:** this valid API input raises instead of returning the finite zero-step Taylor enclosure. The theoretical D4 bound remains correct, with exact radius0. The planned36 nonzero-step controls do not exercise this edge. This is a source-derived counterexample, not a claimed observed exception.

**Minimum requested author repair:** after the existing input/domain validation, handle exact endpoint equality with h=[0,0], radius0 and enclosure=f0, retaining the base derivative in the return contract. Add a small zero-step control to the same future single selected suite and preserve changed identities. Do not disable support traps or widen the scientific domain.

### F-FAMILY — nested session detaches the numerical worker from the outer aggregate watcher

**Target:** initial `code/run_once.py` lines44–46 and64, versus `code/execute_bounded.py` lines26–43 and79–84.

**Static trace:** the outer supervisor makes the inner runner a session/process-group leader and scans only that session. The runner then forks its numerical leaf worker and calls a second `os.setsid()` in that child. The leaf therefore has a different session and process group. While it is alive, the outer session scan omits its own CPU; the outer `killpg` also does not reach it. The inner .38 CPU-s watchdog and per-process hard limit still exist, and normal final waited-child accounting can still include its cost, but the prepared outer aggregate monitoring/termination claim is not implemented for that live leaf.

**Impact:** the outer whole-family fractional target and abort path cannot be relied on as written. This is execution-control correctness tied to the actual budgeted job, not an adversarial security requirement. No existing run or measured cost is affected because the new worker has not run.

**Minimum requested author repair:** keep the single leaf worker in the supervising session and use a direct `os.kill(worker_pid, SIGKILL)` in the inner watchdog. The frozen leaf has no descendants, so this preserves the inner targeted stop and restores the outer session group's coverage. Retain the existing wait4/raw-result accounting and no-retry rule. Review only this delta; no live watchdog probe is requested now.

Both findings were returned to the controller and implementation author. The independent reviewer makes no source repair. The initial hashes and finding trace remain preserved here even after an authorized targeted correction.

## Prepared test oracle and diagnostic coverage

The test scalar oracle is separately written at90-digit precision and does not call the interval kernel/range. It directly loads the same represented coefficients and computes number/loss values; a separate scalar derivative supports the residual. Its finite samples are diagnostics, while the range proof is D1–D5 plus the arithmetic inspection.

The original one selected test method prepares30 row/interval/quantity cases,36 source/quantity/signed-step Taylor records, four signed-versus-clipped comparisons, six present-row underflow records, the He+ interior kernel peak, two structural-absence quantities, four50/70-digit comparisons and nine explicit rejection cases. The Taylor target records preserve both requested rational h and the actual log ratio of the90-digit target. Raw base, derivative, h, radius, residual and enclosure values are serialized on successful completion. A method count is not a scientific verdict.

The runtime positivity record is computed by implementation Fraction arithmetic and checks its positive sign; the independent written exact-image proof is the stronger separate reference for that sign claim. Actual serialized margins and numerical values will still require a future raw-output read. No expected number is fabricated in this source-only review.

## F-PLOT1 correction and prepared outer accounting

The already applied root finding F-PLOT1 is statically closed: Decimal `.5E` formatting retains scientific exponents, the left signed/clipped pairs have explicit independent normalizations, and the right panel labels the six individual signed h values with0/1 ratio cues. The plotting script reads saved JSON only; it imports no rate implementation or tests. A single Inkscape conversion is prepared, with raw renderer streams and SVG/PNG identities. No actual image exists yet, so no visual or C8 admission is made.

The runner preserves source identities, raw stdout/stderr, exit status, wait4 worker CPU and separate supervisor-prefix CPU. The outer wrapper verifies prepared hashes, refuses a pre-existing attempt, applies one-thread environment limits, bounds wall/address-space, preserves aggregate sampling and final waited-command receipts, and has no retry. The stated final accounting correctly avoids adding nested inner costs twice; unknown startup/tail and aborted un-reaped descendant costs remain explicit. F-FAMILY is the single required correction to its current session coverage.

The wrapper explicitly distinguishes fractional targets from strict whole-host guarantees. Runtime feasibility, final actual CPU, source identity match and successful rendering remain unmeasured. The initial PREPARATION commands and resource baseline are historical preparation text; the actual planned command is the outer wrapper and the late `BUDGET_HOLD_ADDENDUM.json` controls present authority.

## Admission boundary

R6 **PASS_SCOPED_INDEPENDENT_THEORY** remains fixed. C9 is **STATIC_ONLY_NOT_RUNTIME_ACCEPTED**, initially with the two targeted source findings above pending author correction. C6–C8 remain **NOT_RUN**. No old tests, native callback, IVP, scientific function, CAS or renderer was executed by this reviewer.

The late PR246 evidence places the current conservative planning charge above its approved20 ceiling. Source preparation and this review continue; numerical and presentation invocations remain held. After targeted source repairs are inspected, the next transition is a concrete prepared package and controller permission request for the pending runtime only. This report issues no budget grant, no original-DAG gate change and no physical completion claim.

## Targeted author correction return

Pending at this initial save. Only changes addressing F-ZERO/F-FAMILY will be inspected; unchanged proof and source reads are reused.

