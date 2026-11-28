# C9 independent implementation review

## Decision

**PASS_SCOPED_DIRECT_CBA.** The implementation, actual finite-fixture results, and actual plotted figure support the reviewed analytic fixed-centre labelled direct Coulomb–Born model. There are no open blocking findings within this unit. Proceed to its scoped documentation and delivery; the physical-provider and full-event admissions remain unchanged.

Reviewer: `/root/cba_independent_review`; requested `gpt-6-astra`, observed runtime model `NOT_OBSERVABLE`. The requested implementer was `gpt-6.1-sol`; a requested label is not observed runtime evidence. This reviewer authored no implementation and ran no scientific code, replay, or Wolfram evaluation. Read-only source inspection, saved-JSON inspection, selected identity comparison, and actual PNG viewing were performed. Only this C9 review and its JSON report were written.

The independent R6 source/algebra review and R7 diagnostic review are reused because their source, model, convention and equations are unchanged. This C9 review applies the builtin physmath-research-loop 1.0.0 coding loop and the HE/central policy snapshots already read.

## Equation-to-code correspondence

All five code files were read: `code/cba.py`, `code/test_cba.py`, `code/run_analysis.py`, `code/plot_results.py`, and `code/run_bounded.py`.

`nordsieck_i` implements Eq. (1) with a real logarithm of positive A and the principal complex logarithm of Bc. Its input preparation checks the strictly negative imaginary part required by the chosen branch. `overlap_k` implements Eq. (2) at independent eta; it never differentiates an eta tied to lambda. The eta-zero tests recover the separate inverse-radius and no-inverse-radius Fourier transforms. The nuclear test uses Eq. (3), and the matched implementation returns an exact complex zero at Delta zero.

`matched_overlap` accepts Delta itself and forms the Eq. (5) polynomial directly. Its numerator is `Delta^2-(1+i*eta)*Delta.p`, with eta=lambda/p, and its denominator and prefactor agree with the independently reviewed expression. It does not recover a small Delta by adding nearly opposite q and p vectors. It still forms q for A, where that operation does not subtract the two leading overlap contributions. The explicit matched branch is correctly used by the hydrogen form factor and TDCS API.

`normalized_form_factor` supplies the Eq. (7) bound and continuum factors. Its default matched branch uses the exact nuclear orthogonality; the explicit-eta branch retains both terms. In particular the plane-wave control retains the nonzero nuclear subtraction. `coulomb_normalizer` explicitly selects SciPy complex loggamma, and `sommerfeld_strength` uses expm1 and the exact eta-zero limit. There is no implicit alternate numerical backend.

`direct_tdcs` fixes hydrogen lambda=1 and binding=0.5, forms the stated fixed-centre energies and transfer, rejects nonpositive open-channel energies, and uses Eq. (9)'s coefficient. Its returned `T_delta` matches the independently reviewed Fourier convention. Spin factor one and the labelled direct count are explicit. Direction normalization preserves a supplied direction and does not clip an energy or momentum transfer. The returned a0-squared/Hartree quantity is divided by the frozen nominal 27.2 factor only for the illustrative per-eV output.

The implementation is an evaluated finite-domain numerical kernel. The existing claim boundary does not promise representability, underflow-free evaluation or a relative-error bound for every finite floating-point input. No such enlarged guarantee is inferred from its input validators.

## Verification independence and frozen inputs

The preparation fixture file, actual analysis rows, and acceptance values were inspected. The nine generic fixtures and four quadrature fixtures match their stored preparation lists; the latter also match the root contract exactly. The tiny-transfer powers, two directions, p=0.7, lambda=1, seven normalization eta values, and 73-point geometry match the frozen design. The acceptance objects in contract, fixtures and results are equal. A selected read-only byte check confirmed that the current theory, contract, fixture file and all five code files match the input identities recorded for the completed plot child. The figure input and PNG/SVG bytes match their receipt.

The multiprecision lane imports the existing pinned mpmath wheel through an explicit PYTHONPATH, while the primary kernel uses binary64 and SciPy. Reference input conversion preserves the exact binary64 fixture inputs; a different decimal interpretation is not used to create artificial discrepancies. The 50-versus-80-digit formula comparison measures precision stability of the formula. The independent 80-digit derivative holds eta fixed. Neither is presented as an independent physical calibration.

The four Eq. (6) checks actually integrate `hyp1f1` with the original-integral polynomial, using exactly the segments 0–1, 1–4, 4–12 and 12–infinity at 50 digits. They do not differentiate the closed I expression. Saved complex segment contributions and total values are retained. This checks the integral reduction against Eq. (2) by a distinct numerical route. The matched tiny-transfer reference is the stable formula at 80 digits; its interpretation is supported by the independent R6 polynomial derivation, exact-zero test, moderate generic comparison and quadrature evidence.

The 14 tests contain both contract checks and analytic controls. Some checks, such as the two TDCS representations, intentionally test normalization consistency rather than external physical accuracy. The illustrative rows' PASS fields likewise check the scalar/delta-T coefficient; they do not certify experimental agreement at 73 angles.

## Actual finite numerical evidence

The actual test report records **14 tests, zero failures, zero errors**. `results/ANALYSIS.json` records all rows passing in every category:

| Category | Rows | Maximum observed residual | Frozen tolerance |
|---|---:|---:|---:|
| Binary64 I/K against mp80 | 9 | 1.0629567988304066e-15 | 2e-12 scaled |
| mp50 versus mp80 formula | 9 | 9.183265145706724e-51 | 1e-40 scaled |
| Fixed-eta derivative against K | 9 | 2.838573667686538e-81 | 1e-40 scaled |
| Eq. (6) quadrature against Eq. (2) | 4 | 3.506764608003949e-51 | 1e-32 scaled |
| Stable matched overlap against mp80 | 16 | 4.0063870834280886e-16 | 2e-11 true relative |
| Complex normalization/strength controls | 7 | 1.5116805406513489e-15 | 3e-12 scaled |
| Illustration delta-T coefficient consistency | 73 | 7.159247292900658e-16 | 2e-12 scaled |

Here scaled means `abs(value-reference)/max(1,abs(reference))`, with complex modulus; it is not a pure relative bound for small values. The stable tiny-transfer comparison uses pure relative error for the nonzero references, while exact matched Delta zero has its own exact-zero tests. The many printed digits of mp50 values are serialization precision, not an assertion that their numerical accuracy exceeds the precision used.

The stored cancellation diagnostic is scientifically useful and correctly separated from the stable acceptance gate. At transverse t=1e-14, generic Eq. (2) has relative error 1.742881133761018e12, while stable Eq. (5) has relative error 1.928809976914049e-16. The generic result has reached a cancellation floor while the true overlap is of order t squared. At parallel t=1e-14, the corresponding generic error is 0.016729855113103972. These are conditioning fixtures; no physical zero-transfer ionization event is asserted.

## Actual figure review

I opened and visually inspected `results/figures/CBA_NORDSIECK.png`, 207055 bytes, SHA256 `dc5777d2b4c9aabb958ce8f5e193eeaf43116c08cecce150aecec6a621811469`. Both panels are legible; titles, axes and legends are readable and not clipped. The left panel displays the saved direct CBA and plane-wave angular curves in the stated per-eV units and geometry. The right panel distinguishes parallel/transverse and stable/generic results and marks the frozen stable tolerance. It visibly shows the stable curves below tolerance and the generic loss of accuracy. The direct-model and physical-provider-pending scope is explicit.

`plot_results.py` reads saved analysis only and imports no kernel. Its receipt binds the plotted input and both PNG/SVG outputs; no new scientific sampling is performed. The receipt's historical `PENDING_ACTUAL_ASTRA_INSPECTION` field describes its generation-time state. This independent review supplies the completed actual inspection without rewriting that historical receipt.

## Execution accounting and preserved failures

The actual resource ledger and child records show the three planned children completed once each with return code zero and PASS: tests, analysis, plot. Their recorded parent-plus-child CPU total is **4.987974 seconds** and wall total **5.122489414992742 seconds**, within the distinct 20-CPU/60-wall allocation and their individual caps. Memory limits and single-thread environment settings are explicit in the runner. The one diagnosed-repair reserve remains unused. These measured windows do not include every host, model, provider or prelaunch cost; those unknown costs are retained as `UNKNOWN_NOT_ZERO` rather than silently counted as zero.

The first plot invocation failed at exclusive creation of `RUN.lock`, before a scientific child or START record existed. Its traceback, zero-byte lock observation/preserved copy, process observation, unknown prelaunch parent CPU, and root's exact cleanup authorization are present. The observed completed analysis session and absent active owned runner supported removal of that specific stale lock. Its origin remains `NOT_ESTABLISHED`. The subsequent plot was the first actual planned plotting child; no test/analysis replay, code change, ledger reset or reserve consumption is recorded. This is a preserved execution-coordination failure, not a numerical failure of the model. The recovery is closed for this unit; it does not assert a general explanation for the lock's origin.

The initial symbolic false failures and the one actual diagnostic remain preserved and independently closed in the R7 review. No third symbolic call is required by C9.

## Admission and stopping rule

This review admits the analytic direct model implementation and its finite numerical controls as **PASS_SCOPED_DIRECT_CBA**. It does not admit exchange/count completion, finite-mass amplitude coupling, a full-event distribution, a calibrated full-support physical provider, or new claims about the earlier 20/54.4/413.6 eV data. Overall HE-ANG remains `SOURCE_INPUT_PENDING`, `physical_provider_admitted=false`. Previously scoped or OPEN obligations, including C9-NB-01 and other-owner work, retain their existing scope.

There are no new blocking findings, no tolerance changes and no further executions requested. The next action is the existing scoped result writeup and publication/backup delivery sequence.
