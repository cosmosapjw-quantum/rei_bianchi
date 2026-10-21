# V9 implementation handoff

Implementation follows the frozen V9 controller contract. Scientific admission is reserved to the controller and independent reviewer. The final analysis artifact is `results/attempt004/ANALYSIS.json`; the three earlier nonempty attempts are preserved.

## Entry points

`analysis.py` accepts explicit `--data32`, `--data64`, `--out`, and optional `--lambda-per-s`. It resolves repository-owned modules and the saved v8 study relative to its own file, and runs from arbitrary working directories. Output must be absent or empty. The implementation does not execute the native solver or saved v8 study.

`run_bounded.py` accepts the same data/output paths plus `--receipts`. It saves commands, cwd, stdout, stderr, exit code and monotonic wall time. Existing receipt records count against the 120-second aggregate scientific budget. `--postprocess-only` runs only the new postprocessor. Actual invocation cwd was `/tmp`.

```bash
python /absolute/repo/research/rei_age_exposure_envelope_20261018/native_age32_analysis_20261020/run_bounded.py \
  --data32 /absolute/new32/data \
  --data64 /absolute/original64/data \
  --out /absolute/empty/new_attempt \
  --receipts /absolute/receipt_directory
```

## Implemented work

- Exact `Fraction` arithmetic from individual binary64 N, photo ledgers and source terms, with Decimal80 display. Explicit birth records give every signed continuous increment and jump, sums, L1, maximum absolute increment and cumulative history. Initial zero photons/photo counters are accepted only with an executed/base solver source whose SHA matches the parent run receipt and whose explicit zero-state initialization is verified. Missing explicit age64 events remain `INCOMPLETE`; the existing observation-derived photon diagnosis remains available.
- Every actual32 pre-event N/clock/active value and accepted-state photo counter is crosschecked exactly. Missing crosscheck artifacts get a separate `MISSING_CROSSCHECK` record. Missing/duplicate/wrong events are typed `INCOMPLETE`/`INVALID` without a fabricated telescope.
- `src/photon_ledger_diagnosis.py` now prefers explicit source-event records when present, preserving legacy observation matching when absent. Only this focused integration module and its focused test file changed outside the V9 directory.
- Existing `endpoint_metrics` computes native32/native64 finite differences with the original target `.005`. All-native N/U survivor age moments use exact accumulation and centered variance, newest 1/2/4 cohort mass fractions and weighted age quantiles. Endpoint cohort sums are checked against the existing `2e-14` numerical scale with an 8-ulp floor, and the exact discrepancy/tolerance is retained. Empty measures return `UNDEFINED`.
- Saved v8 fixed-export all/sensitive/passive cases and pair intervals are copied as separate evidence. Empirical native-all versus fixed-sensitive discrepancies retain denominators and an explicit missing response bridge. Endpoint frozen passive labels are not presented as persistent native trajectories.
- Exact paired photon identity uses Delta = native32 minus native64 and retains `DeltaN = DeltaS - sum(DeltaPhoto) + DeltaR`, signed per-species counters, individual endpoint budgets, exact fractions and native64-N normalization.
- Independent constant-scalar midpoint diagnostic implements stable ratio/defects, scalar continuum root bracket, paired exposure limit, coarse/refined continuum defects at the paired boundary and optional unit-bearing conditional step recommendations. Stable positive source-step absorption is an implementation primitive and never changes native birth schedules.
- JSON, CSV and PNG files are produced from the new stored-output postprocessing. No original raw data are changed.

## Observed execution

`receipts/RECEIPTS.json` records nine bounded subprocesses. Aggregate actual scientific wall time is **10.235522128990851 seconds**, below the 120-second cap. There were zero new native trajectories, RHS calls, v8 study runs or v8 Decimal campaigns.

The final focused run passed **12 tests** (including actual32 all-event crosschecks and actual historical64 missing-source preservation). The unchanged focused integration suite retains its earlier **12-test PASS** receipt (11 existing methods plus1 new method). The scalar tests independently compare Decimal100 exponential values and a seven-term finite geometric sum at x = 0, 1e-8, 0.1, 1, 10, 100 and 1000, and test source-step zero/stiff limits, nonnegative absorption, bracket correctness, moment scale/zero mass, malformed event rejection and nonempty output preservation. The final postprocess-only execution includes the corrected tail crosscheck and Decimal-sign continuum brackets while retaining explicit continuum defects at the paired boundary.

Actual32 history has 33 `VERIFIED` crosschecks (32 birth pre-states plus the final tail endpoint) and an exactly zero telescope residual. Continuous signed sum and L1 are both `1.6596175588774036614e-14`; jump signed sum is `1.2770322873736214737e-20` and jump L1 is `3.2955571922167330291e-20`. These are stored-history arithmetic facts, without a native truncation-error interpretation.

Native N and U finite relative differences are respectively `0.8248861211419689` and `0.7916059535400799`. The unchanged `.005` selected endpoint target is false. The exact paired identity residual is zero. Its signed native64-N-normalized components are DeltaN `-0.824886121141968939`, DeltaS `-0.000133681986259922505`, minus summed DeltaPhoto `-0.824742659650618901`, and DeltaR `-0.00000977950509011547758`.

Every native output retains `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`, native age/time `HOLD`, and nonlinear response bound `NOT_ESTABLISHED`. Controller review decides any additional interpretation.

## C9 authorized repair receipt

The three initial C9 findings were repaired without changing native/v8 inputs, native birth schedules, existing fixed gates, or THEORY. Tail event B now crosschecks interval x/active/N and accepted-state photo counters against the endpoint, bringing actual32 to 33 verified crosschecks. Targeted fixtures reject endpoint N and photo-counter mismatches and distinguish missing tail files. Scaled logarithmic exponential branches preserve representable weighted survivors at large exposure; independent Decimal100 expectations cover `source_step(1e300,0,1,1000)` and subnormal `midpoint_ratio(1491)`. Scalar continuum bounds now classify actual binary64 candidate endpoints with Decimal100 signs and record both signs and the exact-binary64 epsilon target; independent Decimal100 tests verify the bracket. The final focused repair run passed 12 tests. The existing 12 integration tests were unchanged and retain their prior passing receipt. One final postprocess created attempt004; attempts001–003 remain preserved. Independent C9 disposition is PASS_SCOPED with three findings closed and zero open; see reviews/c9/C9_RECEIPT.json.
