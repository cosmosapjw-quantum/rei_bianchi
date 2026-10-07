# Independent review: bounded z12 to z10 Radau pilot

## Verdict

**Execution contract: confirmed for this completed pilot, with the resource-enforcement qualification below. Assessment implementation and reported results: confirmed. Full-history 64/128 pairwise field acceptance: failed.** Both references individually pass admission and conservation budgets. No additional run or active-run stop is needed to establish these findings; both authorized solves have terminated. No native-grid selection, long-interval temporal certificate, realistic EoR claim or z6 release follows.

Reviewed assessor SHA-256: `ba7985324b55404e57c6b3817849cc67dfc09b9c1e6c354b4bb1262fe9e16ca8`.

Reviewed assessment SHA-256: `2fefbd240e41898685d284b94ed18ca1aabd3ea0ac9caddd0c81b7c55980f2d1`.

## Independent evidence

`independent_audit.py` reproduces this audit without importing the assessor or solver and without any ODE run. It independently recomputes all 37 fields' absolute, relative and allowance maxima, worst rows and signed differences. Every reported metric matches exactly, including all four derived subsets, both cross-endpoint prefix diagnostics and `FIELD_SUMMARY.csv`. All results and input hashes are in `AUDIT_RESULTS.json`.

Both histories have exactly the declared 273 epochs; all 28 immutable input hashes and every receipt artifact hash/size match. Config snapshots differ from baseline only in z_end. Producing-source snapshots, manifests, Radau method, threshold-band grids, order 2, rtol 2e-12 and atol 2e-15 match. Independent grid reconstruction reproduces all 1024/2048 eta nodes and weights exactly. Output values are finite, species remain in the simplex, radiation stocks are nonnegative and temperatures remain within 1–1e6 K. Receipts show sequential execution without overlap.

The original unchanged output N/E budget ratios are:

| Reference | Number | Energy |
|---|---:|---:|
| 64 panels | 0.0359942468941 | 0.0114857536391 |
| 128 panels | 0.0849973378798 | 0.0271646823136 |

Recorded accepted-state maxima also pass: 64 panels 0.0362459588135 / 0.0115537344323; 128 panels 0.0855214133540 / 0.0273141015980. These recorded maxima were verified against status and receipts, with enforcement at frozen solver lines 219–260. Accepted-state arrays are not retained, so those maxima were not independently recomputed; output-row maxima were.

The six non-ODE assessor tests were independently rerun with exit 0. Their code and log hashes match `ASSESSMENT_SELF_TESTS.json`.

## Full-history failure and outflow interpretation

Eight original field allowances fail: out_E 1362.112368×, out_N 335.165259×, Gamma_heii 2.276892×, Gamma_hei 1.862148×, Gamma_hi 1.838891×, Eactive 1.783113×, x_heii 1.229153× and Nactive 1.202496×. The remaining 29 pass.

- out_E's allowance maximum is row 185, z=11.0857883949: coarse 1.91930330360e-17 versus fine 2.35886718730e-18 erg/H, difference 1.68341658487e-17 against allowance 1.23588671873e-20.
- out_N's allowance maximum is row 188, z=11.0585628721: coarse 1.58707446218e-5 versus fine 2.89130456229e-5 photons/H, difference −1.30423010012e-5 against allowance 3.89130456229e-8.
- Maximum absolute out_N and out_E differences instead occur at row 271, z=10.0092665302: −9.56214108385e-4 photons/H and −2.08355250611e-14 erg/H. These must not be confused with the allowance-worst rows.
- At row 271, the out_N difference nearly cancels the Nactive difference of +9.56126039667e-4. Smaller absorption/source differences account for the remaining balance; the number-residual difference is only 5.43698419619e-12. Thus budget closure does not imply convergence of separate ledger channels.
- In both histories, out_E/(13.6 eV × out_N) equals 1 to roundoff for out_N above 1e-12. The two outflow failures track the same below-threshold exit process; they are not independent evidence of unrelated physics defects. Frozen solver lines 247–252 implement these transfers.

The huge raw relative-error maximum near tiny reference outflow is not the acceptance criterion. The stated failures use the original absolute-plus-relative allowances, including their floors. Near-perfect endpoint agreement does not remove substantial intermediate-history failures. The justified conclusion is that this 64/128 pair does not establish adequate full-history resolution; it does not identify 128 panels as converged truth or isolate temporal from spectral error without a tighter same-grid pair.

## Prefix, resource and scope qualifications

The short-reference inputs match the prior independent review hashes and admission criteria. Both use matching solver tolerances. The 64-panel cross-endpoint prefix diagnostic fails with maximum Gamma_heii ratio 2.081532802; the 128-panel diagnostic passes at 0.894730579. These compare endpoint-dependent bases and associated trajectory discretization. They are neither isolated basis-only errors nor native temporal errors. Derived subsets are observations of these same runs, not independent schedule-invariance experiments (`assess_pilot.py:115–140`).

Actual resource receipts pass: 64 panels used 104.0914 s wall, 103.5009 s CPU and 459,082 output bytes; 128 panels used 285.2116 s wall, 284.5511 s CPU and 599,589 bytes. Overall elapsed time was 389.3375 s. Max RSS was 103,844 / 199,804 KiB, with the controller's cumulative-child maximum semantics.

CPU 850 s, address-space 2 GiB and per-file 128 MiB are hard pre-exec rlimits (`run_pilot.py:108–112`). Wall 900 s, overall 1800 s and aggregate output 128 MiB are polled every 0.5 s, not strict hard ceilings (`137–148`). Post-exit assessment rejects observed overruns (`assess_pilot.py:71–101,110–112`); actual receipts are comfortably inside all measured limits. Live applied rlimits could not be independently read across exec PID namespaces. RSS is not a measurement of peak address space. These limitations are retained rather than represented as stronger runtime proof.

Solver and original failed evidence were untouched.

## Appendix: independent lower-boundary event diagnosis

**Confirmed, with the inference limits below.** `independent_outflow_audit.py` independently reconstructs crossing times with scalar logarithms and counts events by binary searches between every adjacent pair of output epochs. It recomputes ledger increments, stock bounds, allowance ratios and the heuristic estimates without importing `diagnose_outflow.py` or running an ODE. Every recorded event-interval field, selected epoch detail and cost-scenario number matches exactly. Results and source/input hashes are in `OUTFLOW_AUDIT.json`.

- 64 panels: 128 H I cutoff crossings, distributed over 104 output intervals; 80 intervals contain exactly one crossing.
- 128 panels: 256 crossings over 146 intervals; 81 contain exactly one crossing.
- Every interval without an H I crossing has exactly zero recorded out_N and out_E increment. Every event-containing interval has nonnegative increments. This confirms the direct event-transfer mechanism, including crossings with zero surviving stock.

For 128 panels, interval ending at zero-based row 187 (z=11.0805075973) contains exactly one H I crossing, at ln(a)=−2.491749631004249. Its cumulative-ledger difference therefore isolates a transferred stock of **1.917476835337226e-6 photons/H**, to stored floating-point precision. The energy increment is **4.178105751266454e-17 erg/H** against the interval-end original allowance **5.413992469996033e-20 erg/H**, a ratio of **771.723598513**. This is a single-event amplitude relative to that run's current allowance; it is not the same quantity as the two-grid error reported at row 185.

The largest isolated 128-panel stock occurs in the final interval, ending at row 272: **9.621762980734083e-4 photons/H**. It is not established as the largest stock among all nodes. Nonnegative group totals and group means imply only these global individual-stock bounds:

| Grid | Lower bound, photons/H | Upper bound, photons/H |
|---|---:|---:|
| 64 panels | 1.918401994418645e-3 | 3.524613104983539e-3 |
| 128 panels | 9.621762980734083e-4 | 3.441300544890932e-3 |

For each interval with m nonnegative transfers and sum S, at least one transfer is at least S/m and every transfer is at most S. Taking maxima across intervals gives these bounds. Final snapshots do not retain each exited stock, so the exact global maximum remains unknown.

The arithmetic **ceil(128 × 771.723598513) = 98,781 panels** is correct, giving 1,580,496 nodes at 16 nodes per panel. The analogous 64-panel estimate is 58,750 panels. These assume local stock amplitude scales inversely with panel count while local continuum density and allowance stay fixed. They are **event-amplitude heuristics, not necessary resolution bounds, predictions of the next grid, or proofs about the prescribed 273 output phases**. Event positions, stocks and allowances all change with refinement. The half-jump estimates and the 79.0245× predicted ratio at the 20,000-node cap have the same limitations. Likewise, 781.48 s for a possible 256-panel run extrapolates one observed wall-time doubling and is not a forecast.

The recorded sources directly support a discontinuous stock-transfer ledger at the lower boundary. They do not isolate how much of the two-grid discrepancy originates in source-edge quadrature or coupled chemistry before that transfer. These findings support examining a conservation-consistent continuous boundary-flux or event-local partial-panel mathematical design while holding further uniform-refinement and native solves. They do not validate any replacement algorithm; no implementation or new solve was performed in this appendix.

The named original audit scripts and full execution receipts are retained in the research archive. This compact public checkpoint includes their scientific conclusions and exact historical source hashes; the local `../verify_checkpoint.py` rechecks every original comparison metric from the included histories.
