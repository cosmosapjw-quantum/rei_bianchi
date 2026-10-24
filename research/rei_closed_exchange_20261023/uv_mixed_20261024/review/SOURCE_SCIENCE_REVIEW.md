# REI-L0 SRC-01 repair: independent source and science review

## Decision

**Recommendation: PASS_SCOPED — accept candidate `c8dc1d8e8ad1ee72693bae20b86367b0e1aa1e52e9ff307575d21ca0b9279f77` as the REI-L0 standalone reference source-exchange algebra within the scope stated below. SRC-01 is CLOSED.**

The exact two-call-site repair removes the mixed rational/float UV cancellation defect. The actual authorized run reproduces the defect in all four before checks and gives exact agreement with all five expected components in all four after checks. Source inspection explains the result and preserves the original threshold, source, JVP, units, and ownership obligations. No additional source/scientific blocker remains within this reviewed repair scope.

The **current prospective resource gate is PASS**: one scientific child used 0.046246999999999996 CPU seconds and 0.04686999799741898 wall seconds, below the separately authorized 1.0-second CPU and 5.0-second wall limits. The **historical resource gate remains FAIL / LIMIT_EXCEEDED_RECORDED**: 10.110448 CPU seconds against the earlier 10-second cap. The new authorization does not reset or retrospectively repair that earlier overrun.

This is the independent reviewer's scoped admission recommendation. Formal recording and publication remain root/owner actions. It is not a claim of cosmological-history completion, physical thermal-source validation, production performance, or universal validation of every helper in the module.

## Identity, authorization, and reviewed artifacts

Reviewer: **`/root/source_review`**. This is the follow-up closure by the separately invoked native reviewer who originally identified SRC-01. The original review began in a fresh context; this closure uses that retained context. I did not implement the candidate or execute the scientific fixture. The review branch uses the same inherited model as its parent; no different backend identity is asserted.

The implementation/execution worker is `/root/uv_coding`. Its requested model and reasoning effort were `gpt-6.1-sol` / `high`; the independently observed backend and effort remain `unknown`, as honestly recorded in `M/preflight.json:18–25` and `M/raw/resource_receipt.json:13–20`.

The current frozen contract records the user's explicit additional approval, the exact two-call change, one mixed-input fixture group, and one allowed child evaluating before and after (`C/CONTRACT.json:2–8,17–75`). It prohibits the old 22/66/83 and donor-campaign replays, new IVPs, NCP, rendering, and a CAS worker (`C/CONTRACT.json:76–87`). The contract requires root's Stage A release before execution (`C/CONTRACT.json:94`); the backup acknowledgment is root's separately managed record, outside this source review. This reviewer performed only source/evidence reads, read-only byte comparison/hashing, and review-file writing.

Citation roots in this document are:

- `C/`: `/workspace/scratch/03a65a604d4c/rei_l0_uv_repair_20261024/`
- `M/`: `C/work/research/rei_closed_exchange_20261023/uv_mixed_20261024/`
- `P/`: `/workspace/scratch/03a65a604d4c/rei_l0_fresh_review/source/research/rei_closed_exchange_20261023/review_20261024/`
- `R/`: `/workspace/scratch/03a65a604d4c/rei_l0_fresh_review/`

The retained full source review and static inherited-test impact map are `R/source_review.md`, especially sections 2–6. Its overall PARTIAL verdict applied to the frozen pre-UV-repair candidate; this report closes its sole in-scope open source finding for the new hash.

### Byte identity and exact change boundary

I independently compared the actual before and after files with a read-only diff and checked the five file hashes below. Exactly two source lines differ, at lines 123 and 143. The hashes match the preflight record and the actual run receipt (`M/preflight.json:26–31`; `M/raw/resource_receipt.json:21–26`).

| Artifact | SHA256 |
|---|---|
| `closed_exchange_before.py` | `f551026241d2838852f1eea5a8f3df3c966006e68f70044a97ae8ce594677067` |
| `closed_exchange.py` | `c8dc1d8e8ad1ee72693bae20b86367b0e1aa1e52e9ff307575d21ca0b9279f77` |
| `focused_fixture.py` | `b9ba33b211a28fb562d1c441688b21e73bfd1a01511ef00c828eac40a04167de` |
| `run_bounded_fixture.py` | `807d0b4305adab5c20d2f83de25e2f49d90d184a0e369b17982b2b4d9dbf39f9` |
| `source_diff.patch` | `9ee244631f9c701d01e6f0343eccf7c70fcedb4dd119864bfca14e84e26f2d21` |

## 1. Source correctness and closure of SRC-01

The admitted input types remain `int | float | Fraction`. For the exact witness

\[
\epsilon=2^{-54},\qquad \chi=1,\qquad
m=(1,1+\epsilon,0,0,1.0),
\]

the required UV exchange is `J-Pabs=-epsilon`. The pre-repair `_add` converted the exact rational `1+epsilon` to float before subtracting, producing a false zero. This was information discarded by the implementation, not an unrepresentable final result or information already absent from the input.

The reviewed diff is precisely (`M/source_diff.patch:3–18`):

```diff
- _add(j,-p)
+ _poly_sum((j,-p))

- _add(dj,-dp)
+ _poly_sum((dj,-dp))
```

The existing `_poly_sum` converts each admitted operand to its exact rational value, sums constants and products exactly, retains an exact result for an all-exact row, and performs only one final float conversion for a float-containing row (`M/closed_exchange.py:50–70`). Consequently, it forms `1-(1+epsilon)` exactly before converting the result. Since `-2^-54` is exactly representable in binary64, the final value is exact. The JVP row follows the same reasoning.

No global change to `_add` was made. The three product-bearing rows of each source/JVP vector previously reviewed, the exact threshold comparison, the input guards, the finite/external branch, and all adjacent helpers are byte-preserved. The proposed fix did not expand into unrelated cleanup.

### Source and JVP equations

Using `K` for the unnormalised captured kinetic power `P_K`, the source remains

\[
q=(P-\chi A-K,\;\chi A-\chi R,\;J-P,\;\chi R+K,\;-J).
\]

In external mode only the last row becomes zero. The source sum is zero in finite mode and `J` in external mode before component rounding. All nontrivial sums/products in these source rows now use exact represented-input arithmetic followed by at most one final float conversion per row; negating `J` is exact for admitted finite operands (`M/closed_exchange.py:112–125`). This claim concerns these source rows, not all arithmetic helpers in the file.

The JVP remains

\[
\begin{aligned}
Dq_0&=dP-\chi dA-A\,d\chi-dK,\\
Dq_1&=\chi dA-\chi dR+A\,d\chi-R\,d\chi,\\
Dq_2&=dJ-dP,\\
Dq_3&=\chi dR+R\,d\chi+dK,\\
Dq_4&=-dJ
\end{aligned}
\]

with the last row zero in external mode (`M/closed_exchange.py:128–144`). This is the analytic derivative of the real source polynomial on represented operands; it is not a derivative of floating quantization or of the admission predicate. Callers still supply the full moment derivative, including `K_mean*dR+R*dK_mean` when differentiating `P_K`.

The unchanged threshold check compares `Fraction(P)` to `Fraction(chi)*Fraction(A)` exactly (`M/closed_exchange.py:90–109`). The unchanged helper preserves cancellation before float overflow can occur, rejects a final overflow, and allows ordinary final rounding to a subnormal or zero. The UV repair adopts that same behavior; it adds no tolerance, clipping, floor, renormalization, or rate division.

Units remain proper seconds and eV/Href. The five physical owners and the conditional immediate-heat closure are unchanged. Binding energy is not duplicated, the dynamic escaping-radiation sector remains physical, a bolometric tally remains excluded from energy ownership, and finite/external source ownership is preserved. Those conclusions are supported by the prior full source review and the exact two-line current diff, not by an assertion of newly calibrated physical rates.

## 2. Adequacy and actual outcome of the focused fixture

The driver uses one manufactured input group. It evaluates two operations (`energy_source`, `source_jvp`) in two modes (`finite`, `external`) for each of two immutable source versions. This is **four checks per version, eight evaluated outputs in one child**, not eight new physical cases.

The expected vectors are defined explicitly from the witness, independently of either module's arithmetic helper (`M/focused_fixture.py:33–49`):

\[
q_{\rm finite}=Dq_{\rm finite}=(\epsilon,1,-\epsilon,0,-1),
\]

\[
q_{\rm external}=Dq_{\rm external}=(\epsilon,1,-\epsilon,0,0).
\]

The source is finite and admissible because `P=1+epsilon >= chi*A=1`, `R=P_K=0`, and `J=1.0`. The JVP base is the zero moment vector, with direction equal to the displayed moment tuple and `dchi=0`. This directly exercises the original source and zero-rate derivative failures.

The fixture verifies source hashes before importing either version (`M/focused_fixture.py:10–11,22–30`). It compares every component and the output length. Before, it requires exactly the UV/index-2 mismatch with value `0.0`; after, it requires all five equalities. The success condition requires all eight expected patterns (`M/focused_fixture.py:50–82`). Thus a different baseline failure, a changed non-UV component, or a missing row cannot silently satisfy the intended red/green result.

I independently read all nine lines of the actual JSONL output and the empty stderr:

| Version | Operation | Mode | Actual UV | Full-vector result | Raw line |
|---|---|---|---|---|---|
| Before | Source | Finite | `0.0` | Only index 2 differs | `M/raw/stdout.jsonl:1` |
| Before | JVP | Finite | `0.0` | Only index 2 differs | line 2 |
| Before | Source | External | `0.0` | Only index 2 differs | line 3 |
| Before | JVP | External | `0.0` | Only index 2 differs | line 4 |
| After | Source | Finite | `-0x1.0000000000000p-54` | All five components equal | line 5 |
| After | JVP | Finite | `-0x1.0000000000000p-54` | All five components equal | line 6 |
| After | Source | External | `-0x1.0000000000000p-54` | All five components equal | line 7 |
| After | JVP | External | `-0x1.0000000000000p-54` | All five components equal | line 8 |

The summary explicitly records one group, four old red checks, four repaired green checks, and a satisfied contract pattern (`M/raw/stdout.jsonl:9`). The hexadecimal after value proves that the retained UV component is exactly `-2^-54`; the printed decimal is `-5.551115123125783e-17`. The source and fixture hashes in the raw rows match the reviewed versions.

This evidence is sufficient for the identified two-site defect and the finite/external branches it affects. I do not request a full old-suite replay or an adjacent-helper audit to close this finding.

## 3. Resource accounting

The parent runner verifies preflight hashes, creates an exclusive attempt marker, and launches one direct Python child with bytecode writing disabled (`M/run_bounded_fixture.py:24–48`). The child receives `RLIMIT_CPU` soft and hard limits of one second. The wall timeout deducts launch elapsed time; timeout/error paths kill and reap the child and retain output (`M/run_bounded_fixture.py:20–21,37–62`). The receipt records both child user and system CPU from `RUSAGE_CHILDREN` deltas, wall elapsed time, exit state, exact file/stream identities, and the absence of automatic retry (`M/run_bounded_fixture.py:63–89`).

Limits alone would not prove compliance because accounting and termination can have scheduling granularity. I compared the **actual recorded values** with the prospective limits:

| Quantity | Actual receipt | Authorized limit | Decision |
|---|---:|---:|---|
| Scientific child attempts | 1 | 1 | PASS |
| Child user CPU | 0.031063999999999994 s | Included in total | Recorded |
| Child system CPU | 0.015183 s | Included in total | Recorded |
| Child total CPU | 0.046246999999999996 s | 1.0 s | PASS |
| Wall elapsed | 0.04686999799741898 s | 5.0 s | PASS |
| Return code | 0 | Successful contract evaluation | PASS |
| Timed out / launch error | false / null | Neither | PASS |

Sources: `M/raw/resource_receipt.json:2–12,28–41`; `M/raw/attempt.json:1–6`. The attempt is timestamped `2026-10-24T04:29:34.176324+00:00`. No automatic rerun occurred. This child covers both before and after scientific evaluations; the reviewer launched none.

Parent preparation, IO, communication, review, and any historical remote CAS costs are separately unmeasured, not zero. The whole historical L0 cost remains `UNKNOWN_NOT_ZERO`, and the original cumulative cap remains `NOT_FROZEN` (`C/CONTRACT.json:63–74`; `M/raw/resource_receipt.json:28–30`). The historical exploration's 0.110448-second overrun is retained. **Current prospective PASS and historical FAIL are distinct records.**

## 4. Inherited obligations and evidence reuse

The earlier fresh review examined the original contract, source equations, baseline/candidate diff, acceptance fixtures, all 22 test definitions, and the saved study before issuing its scoped assessment. Its static map remains applicable because the only new changes are the two reviewed UV call sites (`R/source_review.md`, sections 2–6).

| Evidence | Retained role | Current treatment |
|---|---|---|
| Historical 22-group baseline results | Original exact fixtures, domain guards, ownership, stress, units, escape, geometry | Preserved at their original hash and run status; statically mapped, not replayed or relabeled as a current run. |
| Thirteen groups reaching changed source/guard/JVP: F01–F09 and G01–G04 | Source dependencies and derivative obligations | Exact formulas and actual parent input admission remain valid by inspection. The present UV substitution preserves exact values and adopts the already-reviewed one-final-rounding helper. |
| Nine helper-only groups: F10–F18 | Unchanged particle, stress, clock/SI, escape, and event-owner behavior | Their relevant helper implementations remain byte-identical, so old evidence retains its original scope. |
| Saved 66-group trace study | 49 dyadic traces, 16 Decimal source/JVP comparisons, one input-information witness | Retained finite evidence for the previous threshold/product repair; not reexecuted or represented as 66 current-candidate passes. |
| Current mixed UV group | Direct SRC-01 source/JVP closure in both modes | Actually executed once for before+after; four expected before failures and four exact after matches. |

The original exact input cases have explicit nonnegative threshold margins. The float G02 cases are far above threshold; the G03 rational points obey `z*(20-z)>0`. The current UV change does not alter admission at all. All-exact UV results may have concrete type `Fraction` instead of `int`, which remains inside the declared `Number` interface and satisfies the original value-equality fixtures. The prior static impact map identifies no hidden near-threshold parent input or unsupported source dependency requiring replay (`R/source_review.md`, section 5; `P/baseline/test_exchange.py:35–72,155–216`).

The retained study reported 66 passing groups, 46 nonzero rounded dyadic references, three final-rounding-to-zero rows, and the stated finite trace/Decimal errors (`P/evidence/STUDY.json:2–16`). The present change leaves its repaired product rows and threshold guard untouched. Its UV row now computes the same equation by exact pre-conversion summation. This is a narrow evidence carry-forward argument; it does not convert separate historical runs into one larger current pass count.

## 5. Precise admission scope and remaining boundaries

I recommend that root record **REI-L0 source/reference admission as PASS_SCOPED for the reviewed candidate hash**, with SRC-01 CLOSED and the new prospective execution gate PASS. The accepted scope comprises:

1. The declared five-sector source exchange, its finite/external distinction, and exact represented-input threshold admission.
2. Exact integer/rational source evaluation and exact represented products/sums with at most one final float conversion per nontrivial source/JVP row.
3. The full analytic JVP, including variable-threshold terms, with caller responsibility for correct moment derivatives.
4. Preserved proper-time units, energy owners, and conditional immediate-heat algebra, supported by the prior fresh source review and static inherited-fixture map.
5. The saved finite evidence at its original scope and the actual new mixed-input before/after witness at the current hash.

This acceptance does not make the following claims: accurate physical rate/source providers, a completed nonthermal stopping calculation, validated primordial/cosmological evolution, step-size positivity, production throughput, exhaustive floating boundary tests, or universal exact arithmetic in adjacent helpers. These are boundaries of the reference task, not newly discovered defects or additional prerequisites for closing this repair.

The historical operational overrun must remain visible. It does not nullify the new explicit prospective authorization or the actual within-limit repair run. There is no remaining in-scope source finding that warrants withholding this scoped recommendation. Publication should retain the reviewed hash and follow the separately authorized root/owner process; this reviewer made no Git or cloud mutation.
