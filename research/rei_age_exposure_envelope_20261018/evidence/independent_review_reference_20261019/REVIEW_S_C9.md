# Independent C9 review of S reference diagnostics

**PASS within the reviewed scope. No actionable findings or repair request.** The reviewer did not implement the 12 S source files. Their current hashes match IMPLEMENTATION.json; unchanged generator, norm module, and donor solver hashes also match.

## Executed verification

One targeted stdlib suite passed **14/14 tests, exit 0**. It covers passive reference diagnostics and retry rollback (2), age32 receipt binding/default preservation (2), exact compact B1 build reuse (1), and existing error control (9). The test command, environment, timestamps and duration are in TEST_RUN.json; full output is in TEST_LOG.txt. No native campaign was run.

## Scientific and computational checks

- **passive error estimator:** ObservedDOP853 calls super()._estimate_error_norm once and returns the same actual object unchanged. Diagnostic dots and norms do not write K, scale, or the solver state. Full on/off fixture RHS byte logs, accepted coordinates, endpoint, old observations, ledger and provider errors match exactly.
- **RK stages, dense output and RHS:** Generated base is the actual B1 78386db7... solver; diagnostics-disabled source hash is unchanged. AST of rhs, send, binary IO and norm functions is identical. _step_impl, _dense_output_impl, _estimate_error, step and dense_output resolve to the same installed SciPy function objects.
- **interval retry accounting:** Each solve invocation records event/retry and retained/discarded state. A failed interval may contain local error-accepted estimates, but final_trajectory_accepted_estimates is zero. Fixture has one discarded attempt containing such estimates, and retained estimate totals equal solver step totals.
- **true source jump snapshots:** Existing physical pre-birth P output is retained before assigning the new birth coordinates; a separate P query occurs after the one original birth assignment. Neither the established observations schedule nor the original RHS calls are changed. Native P accepts immutable Setup and coordinate slices and constructs physical output locally. Nonbirth/gas/ledger bit comparisons are descriptive fields.
- **exact stored-term jump diagnosis:** Coverage enumerates expected source_inventory births, requires exactly one AVAILABLE record with matching active counts, inventory and birth clock, and marks missing/duplicates/invalid/unexpected records incomplete. Fraction.from_float computes delta N + delta photo events - injected N from exact stored binary64 values, including minimum subnormal fixture. No automatic accuracy certificate is issued.
- **age32 axis and defaults:** age32 changes only name and birth_panels relative to age64. Shared q0, n_mu8, source_subdivisions8, transport16, common_birth_levels8/16/32/64, time_factor1 remain. DEFAULT_CASES remains age64,time8,time16,time32,spectral128; the new diagnostic age32 case requires explicit selection.
- **finite-neighbor receipt binding:** Before computing metrics, validates COMPLETE status, stored output hashes, q0 reference axis settings, original native SHA, exact computational base solver SHA, same binary/interpreter/numpy/scipy/thread/rpc identity, and equality of non-age config fields. Diagnostic-copy identity is produced only by the exact-base transform. Comparison scope is explicitly finite age32-to-age64 only, with no continuum or production admission.
- **compact B1 executable reconstruction:** reuse_compact requires exit0 build, all prepared source output hashes, exact original PREPARED_IDENTITY bytes bound by BUILD_RECEIPT, and exact compact binary SHA. It copies the bound binary/build receipt only after those checks. A mismatched reconstruction cannot be reused; fallback recompilation carries a comparison record and is subject to later same-binary binding.

## Decision and remaining scope

The reviewed S changes are ready for the already-authorized tiny native age2 diagnostics-on/off control. No repair requested by this C9 pass.

- This review executed deterministic fixture tests and read native source; it did not execute the native age2 control or any NCP/full native/age64 campaign.
- Identical RK/RHS logic and fixture trajectory do not by themselves establish native age32-to-age64 accuracy. The matched-source finite-neighbor comparison remains a future execution result.
- The diagnostic old RMS value is descriptive and does not establish RMS dilution as the causal mechanism of prior failures.
- Exact jump residuals are exact arithmetic on stored binary64 terms, without a simulation roundoff or continuum accuracy certificate.

**PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.
