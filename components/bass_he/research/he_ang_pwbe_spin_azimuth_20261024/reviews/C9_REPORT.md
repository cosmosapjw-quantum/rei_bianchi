# HE-ANG-PWBE-SPIN-AZIMUTH independent C9 review

**Verdict: PASS_SCOPED_SCIENCE_PRESENTATION_OPEN.** The reviewed kernel and six-case numerical evidence support scoped model admission. The planned figure is not complete: its render failed, three label strings were subsequently corrected statically, and no replacement render or visual verification occurred. The whole unit must not be marked 20/20 or fully complete while that presentation obligation remains open.

Reviewer: separate `/root/independent_review`, Astra requested; backend runtime identity is not independently observable. One read-only C9 pass, no recursive reviewers. No scientific calculation, test, renderer, import/compile check, CAS invocation, budget reallocation, old-suite replay, or implementation edit was performed by this reviewer. R6 is reused unchanged. Root owns execution/repair authorization and the disposition of the remaining presentation work.

## 1. Reviewed identities and actual evidence

Read the final core, tests, analysis and plotting code; source manifest; frozen theory/contract identities; actual initial failure log; targeted repair authorization/diff/log/report; all four actual FINISH records; full six-fixture results and convergence levels; resource and reused-cost records; and the actual plot traceback plus static-correction diff. No figure was available for visual acceptance.

| Reviewed item | SHA256 |
|---|---|
| THEORY_KO.md, unchanged from R6 | ba074c0750478230700c5b3df35c89814db41b786ae071e701ec25793a57ac9e |
| FROZEN_CONTRACT.json, unchanged | 215b62de28cb840c55846e8936f777b4d32dba22d9e35d44da8503250d2267f0 |
| code/pwbe.py | 9485f9a97689d14b819de2bdb3005643e7b1b12b2b321df7695129fa699c4c37 |
| code/run_azimuth_analysis.py | ec6d0ca523c89ca11198293a751e129b57559941e2dfb9e8d0bf090342e1dfb6 |
| Initial test code | 4493e4265e2e792a63b8e8382dfa41f3ab2759823d478b08ea87a7323d5ae229 |
| Repaired test code | e1e271e96b6479ba6a305c1986b5c9ef3676d8c1deb7853aab942da2f73dd73c |
| Repaired bounded runner | 57b0c3810b1b25bfec61dfd6d17bb07d936a8d0730a80219f72d594401670809 |
| Actual AZIMUTH_ANALYSIS.json | fe6c23f3475ba9c50dd4c295ce0687f61db666babc04198a4a4faf7e35ae21e5 |
| Plot code used in failed render | 0e360fe0e14123bacf6b365d7e95b5fd5c1810a551f4c37dd258a6a90ffea119 |
| Statically corrected plot, not rerendered | bac815be2cacb9ed69a067a491b297e848c0f9ee5647f5402226ec9396395d68 |

All four FINISH records retain the same core and analysis-code hashes. Only the recorded test assertions/targeted routing changed for the test repair. The later plot changes affect three text labels, not source values, formulas, axes, or saved analysis data.

## 2. Scientific implementation assessment

The core retains both nuclear subtraction terms and performs the exact outgoing-argument swap. Positive momentum-gap expressions avoid subtracting large squared norms; pointwise q² is a Cartesian norm; the inverse-square differences are rationalized. The source transition coefficient √2/π³ and output coefficient 32/π² match the R6 normalization derivation. The spin helper computes raw singlet/triplet moduli and applies 1/4 and 3/4 once. Its independent four-spin matrix test uses an explicitly constructed swap permutation and Frobenius trace, rather than reusing the production weighted-channel formula as the oracle.

The azimuth implementation evaluates the closed moments through dimensionless ratios and the stable positive endpoints a−b and a+b. The positive variance formula and positive M_0 sum implement Eq. (10); no absolute-value replacement or epsilon clipping is used to conceal negative densities. The polynomial M_0 expression remains a cancellation-prone cross-check, not the production mean. M_1 is evaluated as a signed sum, and cancellation ratio/mean scale are reported. Invalid energies, ordering, angles, nonfinite values and observed overflow are rejected. This is finite binary64 reference code, not an all-dynamic-range accuracy guarantee.

The relative-azimuth PDF uses K/(2π Kbar). Its normalization/measure is consistent with dE_B dΩ_A dΩ_B and the one-azimuth average. The pointwise kernel adds neither an event factor 1/2 nor an equal-sharing factor 2 or 4. Ordered mode admits the equal-sharing boundary as a diagnostic; full-labeled exchange tests explicitly request the diagnostic mode. No global angle/energy integral is calculated or reported as event sigma.

The exact rational node fixture establishes t=h at the mathematical zero. Its binary64 geometry is allowed to retain a tiny represented residual, without clipping it to zero. The test checks consistency of the actual returned conditional status, and separately injects a computed-undefined status to exercise the PDF's null branch. This is appropriate branch/control evidence; it must not be described as an observed exact floating-point realization of the irrational algebraic node. A computed zero M_0 or underflowed zero Kbar yields an explicitly undefined numeric conditional law. All six accepted high-energy cases have positive represented means.

Source qualifications are preserved: FIAS-R-39 June 1978 Eqs. (19)–(20), not an asserted identical 1979 journal equation; printed Eq. (21)'s −2fg is not adopted as unpolarized; independent spin trace supplies the chosen law; Born–Ochkur is a distinct exchange approximation; Buică v1 is a nonessential cross-check and its later unread erratum remains an access/version qualification. No source table is fitted or used, no empirical physical-error envelope is claimed, and physical-provider admission remains false.

## 3. Initial failure and targeted repair assessment

The first child actually ran 14 methods: 12 passed and two failed. The original failure report and raw stderr remain intact. It would be incorrect to report a clean initial 14/14 pass.

**C6-ASSERT-01, first assertion:** exact dictionary equality expected triplet 13.0 and mixture 14.0, while binary64 abs-square arithmetic produced 12.999999999999998 and 13.999999999999998. The minimal change compares these outputs with the existing frozen relative 2e−13 / absolute 2e−15 helper. The independent spin-matrix trace remains. This corrects an assertion inconsistent with the already frozen floating-point criterion; it is not a changed physical target.

**C6-ASSERT-01, second assertion:** for G1, positive M_0=1.564313391312208e−13 and the polynomial expression=1.564313391312724e−13 differ by 5.159781408869594e−26. The initial explicit absolute=0 override excluded the frozen absolute allowance, and failed its stricter 2e−13 relative comparison. The repair removes only that override. This cross-formula comparison consequently does not independently certify relative accuracy at tiny M_0. Crucially, the subsequent independent raw-source quadrature for this very G1 case separately achieves relative Kbar error 7.15623529622744e−15 at N=2048 under the unchanged 1e−10 acceptance target. Thus the scientific finite-case accuracy is not inferred merely from the absolute-tolerance assertion.

The targeted repair child ran only methods 01 and 06 and actually passed both. The remaining 12 methods reuse their unchanged initial evidence. Core, theory, source, and analysis tolerances were unchanged. This closes the two assertion defects with provenance: **12 initial passing methods plus two targeted passing methods**, not a full-suite replay.

## 4. Independent quadrature and observed finite results

The diagnostic oracle constructs fresh Cartesian vectors in NumPy, evaluates literal source transition amplitudes using direct nuclear subtraction, applies the independently derived spin weights, and then takes periodic sample means. It does not call production pointwise K, rationalized amplitude subtraction, positive-gap helpers, closed moments, or the variance formula for its raw density. The closed result is used only as the comparison and PDF-normalization reference. This is meaningful algorithmic independence, coupled with the exact source/hand tests.

The normalization check raw_K/(2π closed_Kbar) is mathematically linked to the mean-density comparison; it is not a third wholly independent oracle. The actual API denominator is checked separately in method 14. Likewise the saved pointwise heatmap is a diagnostic field, not a new independently certified continuum-wide solution.

All six frozen cases passed their N=2048 final criteria:

| Case | Closed Kbar | Closed E[cos φ] | Final relative Kbar error |
|---|---:|---:|---:|
| G1 | 3.4992701523574837e−12 | 0 | 7.15623529622744e−15 |
| G2 | 2.4271929760419153e−5 | −0.9970629282251592 | 5.4440310711161585e−15 |
| G3 | 5.77548044734344e−12 | 0.2622029354496094 | 5.594641514666567e−16 |
| G4 | 6.172267592876118e−5 | −0.9978972840121045 | 4.391425663952355e−16 |
| G5 | 5.642122920098023e−10 | −0.9694320682299375 | 1.0995603396105956e−15 |
| G6 | 4.050308029839717e−10 | 0 | 6.382081054537734e−16 |

The observed maximum final absolute conditional-cosine error is 3.3306690738754696e−16, and maximum normalization error is 6.772360450213455e−15. These are finite-case observed discrepancies, not global accuracy certificates or calibrated physical errors.

The raw convergence levels are informative and retained. G4 has relative mean error about 0.01836 at N=64, 6.27974e−13 at N=256, and 4.39143e−16 at N=1024/2048. G2 also has a visible N=64 error before reaching its roundoff plateau. G5's N=64 mean error is about 1.1339e−10, slightly above the final threshold, and later levels pass. The contract requires the last level, so these coarse discrepancies are not hidden failures or a reason to change tolerance. At a roundoff plateau, small nonmonotonic residuals do not imply a failed convergence test.

## 5. Open presentation finding C8-PLOT-01

- **Object:** `code/plot_results.py` and required PNG/SVG/visual evidence.
- **Observed evidence:** the fourth child exited 1 while saving the first PNG. The actual traceback reports `Expected \\overline{body}` for `\\overline K`. The same source also contained unbraced `\\frac14` and `\\frac34` labels. No completed figure or plot receipt was produced.
- **Effect:** the numerical analysis remains available and verified, but the requested rendered presentation and visual acceptance are incomplete. A syntactically edited plotting source is not a rendered deliverable.
- **Minimal correction already made:** root authorized exactly three static label edits: `\\overline{K}`, `\\frac{1}{4}`, and `\\frac{3}{4}`. Reviewed the actual preserved-original/current diff and static-correction record. No data, axes, model, tests, or analysis changed. Status is **STATIC_CORRECTED_NOT_RERENDERED**, not CLOSED.
- **Exact remaining obligation:** under a separately authorized execution disposition, render the corrected plot from the already saved AZIMUTH_ANALYSIS.json, preserve that actual result, then visually inspect the resulting PNG/SVG. No scientific kernel, test suite, or analysis rerun is necessary. This reviewer authorizes no such extra invocation: the sole repair reserve has already been consumed, and no fifth child is authorized by the current contract/root decision.

There is no visual PASS. C8 presentation remains PARTIAL/OPEN, and full-unit completion remains false. The plotting code's intended panel semantics are consistent on static inspection, but actual text layout, legends, heatmap rendering, and output existence remain unverified.

## 6. Accounting and admission decision

| Actual child | Status | CPU s | Wall s |
|---|---|---:|---:|
| Initial 14-method tests | FAIL: two assertions | 0.093884 | 0.11865653000040766 |
| Targeted two-method repair | PASS | 0.089662 | 0.12036444200020924 |
| Six-case azimuth analysis | PASS | 0.172483 | 0.2182225649994507 |
| Plot | FAIL: Mathtext parse | 1.610416 | 1.6219177279999712 |

All four started children, including both failures, are charged: measured CPU 1.966445 s and wall 2.079161265000039 s. The single repair reserve is used; none remains. Measured totals are below 8/30, but remaining measured time does not create a fifth authorized invocation. Host orchestration and remote total CPU remain UNKNOWN_NOT_ZERO, so an end-to-end CPU cap is not established. Prior TDCS54/CCC/DDCS/Hex/HE38 costs, failures, and unknowns remain in the pinned reuse chain without reset or allowance transfer. The inherited-reference document contains preparation-era NOT_RUN/NOT_FROZEN fields; those describe its preparation snapshot, while the current execution ledger is authoritative for this unit's actual runs.

**Scoped admission recommendation:** accept the unchanged R6 derivation, implemented model kernel, repaired contract controls, and actual six-case numerical verification as DERIVED / IMPLEMENTATION_VERIFIED_SCOPED / NUMERICALLY_CHECKED_SCOPED. Preserve C8-PLOT-01 as an explicit unfulfilled presentation obligation. No current source/kernel numerical defect was identified in the reviewed finite scope. Do not infer full physical-provider admission, empirical accuracy, an end-to-end cost guarantee, visual acceptance, or 20/20 completion from this scientific pass. Parent HE-ANG remains SOURCE_INPUT_PENDING.
