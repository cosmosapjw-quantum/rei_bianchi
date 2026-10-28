# R6 post-evidence static disposition and C9 limits

Unit: `rei_rr_mao_finite_temperature_enclosure_20261028`  
Actual reviewer task: `/root/rr_mao_native_reviewer`  
Review date: 2026-10-28 UTC.  
Review mode: source, diff, prepared-test, wrapper, and actual CAS-error inspection; no scientific execution by this reviewer.

## Verdict

The R5 mathematical conclusion in the sealed phase-one report is unchanged. The RR/Mao algebra, actual-row monotonicity, positive mathematical source functions, and uniform two-sided log-temperature Taylor theorem remain supported for the declared represented-real scope.

The implementation finding F-CODE-1 is **CLOSED_STATIC** in core source SHA256 `028b854a68e5d3e2ac64f3e3ff4a5b531416fc00610dbe7901563808f26541e7`. A targeted regression-fixture overconstraint, discovered during the later test-source contrast, is **CLOSED_STATIC**. Its corrected fixture was first reviewed at test SHA256 `0554fc8b3869761f8a127cd98854bd3df70813781f6c14967929d114167cf6fc`; a final serialization-only addition gives the frozen test SHA256 `08bc50acd6a6baca563e3bf7a259ff39f7c86d4c2c13a50f18a58421fc6f48f5`. The record-envelope question is also **CLOSED_STATIC** for that complete saved-record format. None of these closures is an executed regression result.

The full numerical validation and C9 remain **PENDING / NOT_RUN**. No new numerical outputs or rendered figures were produced or inspected by this reviewer. The parent states that scientific execution remains held under current resource authority. The actual CAS call returned an internal tool error and no scientific result. A completed source review cannot replace any of these missing empirical/runtime obligations.

The unchanged old DR Taylor implementation has the same near-equal-input limitation. That shared impact is documented separately in `R6_DR_DEPENDENCY_SCOPE_ADDENDUM.md`; the new RR-local helper does not repair the pinned old DR method.

## 1. Preserved ordering and evidence boundaries

The source-equation review was sealed before reading implementation or test contents. The static implementation finding was separately written and hashed before reading test/wrapper/CAS artifact contents. The preserved identities are:

| Artifact | SHA256 |
|---|---|
| `R6_PHASE1_SOURCE_ONLY.md` | `9349123bcf8302c19f228425070e1a8a3be1cad342a82ee8de4ee9da82216cb8` |
| Final `R6_PHASE1_READ_LEDGER.md` | `46b4149f0b8d7856b3aadbe3e92c5d1c8979a365c955e545c8a87f8fdc0fb5b2` |
| Prior root-observed ledger snapshot | `472c30a107046288e2f14f48881fd6bc5575d67fb90727bf8f1407012fbf77d6` |
| `R6_PHASE2A_STATIC_CODE.md` | `9b025bb1c82cde44fb783fe64ec5580fa6115407d7d52d5d5ebb9f19145c79a0` |
| `R6_DR_DEPENDENCY_SCOPE_ADDENDUM.md` | `f5bd05f38092e6c01fd04a77b72844bcbbc1f6fd8fd7713deaed32926191ff24` |

The phase-one report, final ledger, and phase-two-A report hashes were rechecked after the later evidence reads and remained unchanged. Shared filesystem access is not security-enforced blinding. Original-source historical evaluations, author-proposed controls, and later parent metadata are disclosed in the respective ledgers rather than erased.

## 2. F-CODE-1 repair disposition

The reviewed repair adds a local `natural_log` helper. For an input endpoint exactly equal to 1, the corresponding output bound is exactly 0 by the identity `ln(1)=0`. Other endpoints retain the correctly rounded logarithm followed by one outward adjacent value. The helper rejects a nonpositive lower argument.

All new RR/Mao logarithm call sites use this helper: the alpha exponent, lambda, Mao numerical-eV temperature, and log-temperature step h. The pinned inherited arithmetic file is unchanged. No rate, Mao, loss, derivative, or Taylor formula was modified.

For the preserved witness—key `1:1`, precision 60, anchor 100, target `100+10^-100`, domain `[100,101]`, alpha—the ratio lower endpoint still rounds to exactly 1. The helper now returns a lower log bound of exact zero. Multiplication by the derivative therefore uses an exact zero endpoint rather than the artificial minimum subnormal. This removes the specific analytically established trap path while preserving inclusion.

This is a mathematically justified local endpoint identity, not an equality tolerance or a fitted numerical allowance. It does not assert that arbitrary nonzero h is zero. The other log endpoint still supplies arithmetic uncertainty, so the small nonzero step remains enclosed.

Disposition: **CLOSED_STATIC for the identified path and repaired source version**. Actual execution of the witness and the prepared regressions remains **NOT_RUN**. The original finding and original source identity remain in the phase-two-A record.

## 3. F-TEST-1: negative regression sign overconstraint

The first disclosed regression draft used a negative step from anchor 101 to `101-10^-100`, with a requirement that the returned h upper endpoint be nonpositive. That requirement does not follow from generic interval division: `1/101` is nonterminating, its rounded-up reciprocal is strictly above the exact reciprocal, and the reciprocal rounding error is vastly larger than the target displacement. The ratio upper bound is therefore greater than 1. A valid log enclosure may cross zero even though the exact h is negative.

This was identified by static inspection before any test execution. It is a test expectation problem, not a failure of the repaired enclosing function. The parent separately reported noticing the same issue; that report was not needed for this derivation.

The final reviewed fixture uses anchor 125, target `125-10^-100` written as `"124." + "9"*100`, and domain `[124,125]`. Its reciprocal is exactly `0.008`, so the ratio upper endpoint rounds to exactly 1 and the repaired log upper endpoint is exactly zero. It now exercises the intended exact-endpoint case on the negative side. The positive 100 K witness is retained. Both alpha and loss paths are prepared, with a separate 180-digit log diagnostic.

Disposition: **CLOSED_STATIC for the fixture logic at the reviewed final test hash**. The later addition of `domain_K`, f0, d0, and B2 serializes existing return values and does not change the fixture or assertions. No assertion has been run. The intermediate unexecuted fixture is not retroactively called a failed runtime result.

## 4. Prepared-test contrast

The prepared source covers all six selected keys, narrow low-temperature and high-temperature intervals, an interval around 15000 K, and the full common domain. It proposes scalar sample comparisons against the interval boxes for rates, factors, losses, and their displayed logarithmic derivatives. It also proposes point derivative records, the Li correction at T2, explicit separation of the selected hybrid from the alternate closure, positive/negative finite steps, exact zero steps, a second precision setting, and invalid-source/input/quantity refusals.

The scalar oracle uses separately written 90-digit scalar arithmetic, but it shares Decimal/libmpdec with the interval code. Its derivative expressions closely follow the same analytic formulas. Consequently it supplies a numerical implementation contrast when executed, not different-library validation or an independent algebraic proof. That limitation is disclosed in the test source and worker output. The source proof and independent manual algebra review carry the derivative-identity argument.

The log-base perturbation test changes the main Mao exponent's log argument while retaining its already-computed U and V. It is a discriminating perturbation, not a complete alternative implementation of the entire formula using base-10 logarithms. The actual native natural-log convention was established directly from the source rather than inferred from that one proposed inequality.

The manufactured analytic controls in R5 remain mathematical statements. This prepared test source does not turn them into executed controls. Likewise, stored fields such as `contained=True` are populated only after the programmed assertions are reached in a future run; their presence in source is not a recorded containment result.

No check count, planned loop cardinality, or proposed assertion determines acceptance. The evidence needed next is the actual bounded-run status and raw values at the frozen source identities.

## 5. Record envelopes, runners, and saved-data plotting

`run_once.py` is prepared to wrap the test records with top-level source identities, represented-real scope, runtime arithmetic versions, and explicit physical-scope nulls. Its numeric interval serialization retains Decimal endpoint strings. This resolves the phase-two-A provenance question for the complete saved worker envelope. A detached bare `Interval`, `Decimal`, or isolated record is not by itself a source-identified result; preserve the containing envelope and pinned manifest with it.

The core Taylor method returns h, f0, d0, B2, radius, and enclosure. The ordinary saved Taylor rows retain those numerical fields. The first repaired tiny-step record dictionary omitted its domain, f0, d0, and B2 even though the method had returned them. I reported that record-completeness limitation. The final test source at SHA256 `08bc50acd6a6baca563e3bf7a259ff39f7c86d4c2c13a50f18a58421fc6f48f5` adds `domain_K`, f0, d0, and B2 from the same existing variables without changing scientific calculations or assertions. I read this final narrow change and its refreshed manifest/diff. The tiny-step record-completeness issue is therefore **CLOSED_STATIC**, subject to inspecting the actual serialized output when a run is authorized.

The outer runner checks frozen file hashes, refuses replay of an existing attempt, and records process identity and resource accounting fields. The sources explicitly distinguish watched job-family targets from a strict whole-host CPU guarantee and keep unmeasured overhead visible. I did not execute or experimentally validate the supervisors, process-identity logic, or accounting. Their presence does not authorize a run or establish a runtime cost.

The plot script reads saved numeric records and constructs a rate/loss table and a saved residual-to-radius display; it does not import or reevaluate the scientific rate function. It requires a successful saved result. It prepares alpha and loss units and the 15000 K anchor label. A future figure review should make the right panel's uniform bound domain `[14000,16000]` K explicit in its caption or associated record and distinguish requested step labels from the actual stored h enclosure. No SVG/PNG has been rendered or visually inspected by this reviewer.

## 6. Actual CAS return

The disclosed `CAS_ACTUAL_RETURN.json` records a request beginning at 12:33:30 UTC and an error return at 12:33:34 UTC. The tool reports internal error `-32603` and `isError=true`. It contains no algebraic residual output and no observed kernel CPU value.

Therefore the correct scientific disposition is **TOOL_ERROR / NO_SCIENTIFIC_RESULT**. It is neither an identity pass nor an identity failure, and it is not an observed symbolic timeout result. The reservation and requested time constraints are planning/request data; the error does not establish that kernel CPU use was zero. No retry or substitute CAS calculation was performed by this reviewer.

The exact R5 derivation and manual review remain self-contained. No new numerical RR/Mao result can be inferred from the symbolic tool error.

## 7. Scope of the old DR correction

Mechanical hashing confirms that the original old DR implementation and the new unit's inherited dependency share SHA256 `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`. Its unchanged `DRModel.taylor` still uses the original unconditional log expansion. The same witness applies to the present `2:1` DR channel with exact Decimal inputs. The structurally absent `1:1` DR channel is not the witness.

Withdraw an unrestricted return guarantee for arbitrary near-equal unequal Decimal temperatures from that unchanged implementation. This does not by itself contradict the DR mathematical theorem or any particular historical selected result. Those historical outputs and admission records were not read or regraded by this reviewer. The RR-local repair must not be reported as a global repair of the inherited DR class.

## 8. What remains unexecuted for C6/C9 and the deliverable

The static work supports “authored, source-reviewed, and locally repaired.” It does not support “numerically validated” or a completed overall C9 judgment. The outstanding evidence is concrete:

1. Under valid current resource authority, execute the frozen selected worker once and preserve its actual process receipt, stdout, stderr, arithmetic versions, and complete source identities.
2. Inspect the actual finite-box and point records, both signs of finite Taylor steps, exact zero steps, the corrected tiny-step cases, source/input refusals, and precision records. Resolve actual failures without treating proposed counts as proof.
3. Check that the actual saved record envelope retains the domains and numeric terms needed to assess each claimed bound. The prepared tiny-step serialization now contains the required context, but its future runtime output still needs inspection.
4. Render only from accepted saved data when separately authorized, retain the saved-input identity, and inspect the actual exported figure for units, domains, labels, and legibility.

These items are listed as pending obligations, not execution instructions or a resource grant. There is no need to rerun a full old DR suite, native callback, or IVP to interpret the already-established static issue. Physical fitting uncertainty, actual recipient temperature/state/radius certification, and global physical completion remain outside this review.

## 9. Exact phase-two-B read and identity ledger

All local scientific files were read as text; none was imported or executed. The first batched return was truncated by a few output tokens inside the outer-runner excerpt. `execute_bounded.py` was subsequently re-read completely, so no full-read claim depends on that truncated text.

| File/resource | Semantic read | Final or observed identity |
|---|---|---|
| `tests/test_rr_mao.py` | Entire 1–121 line disclosed draft, then entire 1–121 line intermediate version; fixture correction at lines 88–109 and its complete diff; final serialization-only change at lines 90–109 and diff lines 70–91 | Intermediate verified `1bb2688a3e012d5b0457697604f184b11d4f9ebbe826c93040de4a779d792a4d`; corrected fixture `0554fc8b3869761f8a127cd98854bd3df70813781f6c14967929d114167cf6fc`; final verified `08bc50acd6a6baca563e3bf7a259ff39f7c86d4c2c13a50f18a58421fc6f48f5`. |
| `code/run_once.py` | Entire lines 1–124 | `a2993a05a01aef10f7478467b22d10140366f9798eea71f266779de107b0e76b` |
| `code/execute_bounded.py` | Entire lines 1–167 after complete re-read | `57ad89f0bc26e41d9faee0ee258a81d404fa8fd8d0279fbb5b3e90f69cc22e29` |
| `code/plot_saved.py` | Entire lines 1–57 | `29e0e3239102e2eaa000276cc0daf63fbd722161c3136261ee1d26f7b3a2e6f8` |
| `SOURCE_IDENTITIES.json` | Entire lines 1–71; followed from the already-authorized runner/manifest reference | `44802020bd64f47a132d5fe545c1ab7510ad0be597c65a6f39eda22894d03cea` |
| `PREPARED_IDENTITIES.json` | Entire lines 1–84 of disclosed and corrected-fixture versions; final changed core/test entries at lines 53–64 | Intermediate observed `ccc535bbb49b0ef2da2814dfd5aba31199a4537ad10a261b7d3d9e6f4d91bbbb`; corrected-fixture `ef285b8cec6ac5caca14045665ffb8d977ade59c5bc7a9bf937e3bdfac18d6fd`; final verified `4f055b8d33b767ae34fc90c3fc87519c371192ad188dd214d979e0b08adef750`. |
| `review/AUTHOR_TINY_LOG_REPAIR.diff` | Entire lines 1–90, intermediate and corrected-fixture versions; final serialization hunk lines 70–91 | Intermediate `1932ddb7b61de948eed237da600c2e6cf9a27aaa5c34e58b59b6d0fdff2599de`; corrected-fixture `98e159f9243311c3636b85be9e190baa94cabaef3aaa86aea403c8eff71d8065`; final `6f28861fddac9542f89481b7eb281e49b0963e7269b67ac69fe31a53269ebd09`. |
| Repaired `code/rr_mao_enclosure.py` | Complete changed diff; direct text at lines 35–59 and 165–171; all log call sites selected with `rg` | `028b854a68e5d3e2ac64f3e3ff4a5b531416fc00610dbe7901563808f26541e7`. Original whole-file read remains recorded in phase two A. |
| `execution/CAS_ACTUAL_RETURN.json` | Entire lines 1–17, including exact request and error | `b90a7d28f10c8f7873721030d00de22332bdcf73d4fa3e5aa570014457fb2351` |
| `execution/CAS_RESERVATION.json` | Entire lines 1–18, including planned constraints and reservation metadata | `d94049ebae60b8ad7ec04014c24d12e62d2d94b1b4ba74498cf60e061886f145` |
| Original `rei_approved_continuation_20261028/unit/code/dr_enclosure_cached.py` | Hash only; no additional semantic read | Same `be32fe...` identity as the fully read inherited dependency. |

All relative paths in this table are under `/workspace/scratch/cc0531120bc9/rei_post_dr_continuation_20261028/unit/`, except the explicitly named original old DR path. The initial test text arrived during the author's unexecuted editing window; its contemporaneous manifest named a `be114418...` version, but I did not obtain an independent byte hash of that first text read. I do not retroactively attribute it to the later verified test bytes. Subsequent full intermediate read and final changed-block/diff read provide the stated verified review identities.

Author finding prose, sibling review/status/handoff/census documents, old DR numerical outputs, new scientific output files beyond the explicit CAS error, and intermediate draft directories were not inspected. Parent messages naming their availability or reporting another reviewer's agreement do not count as source evidence.

The parent reported that the old DR scope correction was published at commit `b461ab44ac45360af5c6b789808725c8fba79f10` while retaining historical selected stage records. That status message was exposed; the commit and historical records were not fetched or independently reviewed. The last narrow code/record read above was completed with an observed clock time of `2026-10-28 12:49:27 UTC`. No new optional review or scientific execution followed that final requested serialization check.

No scientific execution, source import, CAS call, test run, plot, or external write occurred in this reviewer task. Local mechanical operations were reading, hashing, known-text snapshot recovery, and report writing. Standard-library documentation was read on the web in phase two A. Total model/tool/host/network overhead remains unknown and is not asserted to be zero.
