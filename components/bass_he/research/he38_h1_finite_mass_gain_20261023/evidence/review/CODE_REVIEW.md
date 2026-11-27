# HE38 independent implementation review

**Verdict: PASS_SCOPED, with one low-severity documentation clarification recommended.** No blocking implementation defect was found in the reviewed finite-mass component. The public wrapper preserves the new direct STF and total heat, and the independent two-probe execution passed. Review target: `/tmp/he38_implementation`, before any root integration edits.

Reviewer `/root/he38_independent_review` did not author the theory, source qualification or implementation. Workflow **1.0.0**, approval **0.2**.

## Equation–code correspondence

| Target | Inspected correspondence and result |
|---|---|
| `model.py`, constants and model identity | CODATA proton mass, inherited electron mass/constants, additive neutral mass, both reduced masses and the original Jacobi angular scope are explicit. The public model identity differs from the byte-preserved heavy-target arithmetic donor. |
| `FiniteMassModel.evaluate`, line117 | Inherited moments are multiplied by $1/\sqrt\zeta$; κ1, κ2, Λ, the first Jacobi moment, species heat, direct combined heavy heat, and the 3×2 STF map match the reviewed equations. The finite temperature contract prevents radial underflow in the admitted interval. |
| `finite_mass_source`, line202 | Column0 uses $n_H\pi_e$, column1 uses $n_e\pi_H$. Direct total $Q$ and $J$ are computed separately from species sums. Signed pressure sources are retained; no covariance clipping or stress allocation is introduced. |
| `event_kinematics`, line269 | Original-coordinate velocity reconstruction matches exact event conservation. Directions are checked as unit vectors, rather than normalized implicitly. Artificial ion masses carry a separate control-only label. |
| `bridge.py::_state`, line35 | Pure-H21 slots1/2, nonnegative normalized inventory and no implicit renormalization are enforced. Other populated species remain outside this adapter’s contract. |
| `h1_ci_source`, line81 | With $n_e=n_BY_p$, the abundance source is ν $n_B\alpha Y_HY_p$. The two physical derivatives are $n_B\alpha Y_p$ and $n_B\alpha Y_H$. The frozen-electron donor derivative is separately returned. The normalized-manifold tangent restriction is documented. |
| Energy and census | The net event tensor half-trace agrees with dEth. Species total heat, wrapper Q and dEth are the same owner. All-retained thermal scope is explicit before constructing the temperature source. Source zero at an absent reactant is separated from an activated boundary derivative. |

Input paths reject mixed Python booleans, nonfinite values, complex/object data, invalid shape, non-STF inputs and nonzero stress for an absent species. The new wrapper checks the additional mixed-boolean cases before using the inherited arithmetic helpers. The product helpers distinguish mathematical zero from nonzero binary64 underflow. Returned arrays use bytes-backed storage, and nested donor records are frozen by the inherited adapter.

## Identity and existing affected evidence

All six declared donor source files were compared directly against the current destination bytes and the recorded SHA256 values; **6/6 match**. The eleven source identities captured by the author’s completed affected-control `START.json` still match the reviewed files. Its **107 PASS controls** are reused as that execution’s evidence; the review did not replay them.

## New reviewer probes

Exact command and source hashes are in `PROBE_START.json`; code is `probe_interface.py`. This was one process with two targeted cases, **0.848680205 CPU seconds**, **0.873032597 wall seconds**, peak RSS **46,704KiB**, exit **0**. No old suite, IVP, benchmark or figure render was executed.

1. **Tiny diagonal STF through the full pure-H adapter.** At $T=2\times10^4\,K$, $n_B=10^6\,m^{-3}$, $Y_H=0.6,Y_p=0.4$, πe has diagonal ±1.1045192×10⁻⁵³Pa. Wrapper `.J` preserves diagonal ∓1.59477584646×10⁻⁶³Pa/s, with $2.22\times10^{-16}$ normalized discrepancy from the direct coefficient. The nested inherited adapter’s `.J` is zero because it reconstructs STF from the full pressure tensor.
2. **Fully ionized boundary.** With $Y_H=0,Y_p=1$ and a valid electron STF, the event rate, total STF and temperature source are zero. The derivative toward a populated neutral state remains active, $9.39520383130\times10^{-12}\,s^{-1}$, as required by the physical abundance polynomial.

## Finding F1: make nested STF field ownership explicit

**Severity: low; documentation only.** Target: `bridge.py` line59 (`event_tensor_source`) and line72 (the public `.J` property), plus `README_KO.md`.

The public wrapper `.J` is correct. The returned `event_tensor_source.J` is the byte-preserved HE36 trace-projected value and may lose an arbitrarily small diagonal STF beside the much larger isotropic source. The concrete input and outputs above are saved in `PROBE_RESULT.json`. The README already directs tiny-STF users to direct J, but it does not explicitly name the nested field that has lower relative accuracy.

**Minimum clarification:** state that `event_tensor_source` preserves the legacy donor/attachment audit and that STF consumers should use wrapper `.J` or `species.total_J_Pa_s`; the nested `.J` is a trace-projected diagnostic. No donor change, new scientific calculation, or old-suite replay is required. This finding is not a failure of the implemented direct-source contract.

## Acceptance boundary

This review admits the new instantaneous kernel and pure-H adapter under their declared finite-mass model. It does not approve a full-gas evolution, empirical angular calibration, a coupled IVP, or final archive/publication consistency. Root owns the independent raw contraction, new diagnostic/figure and delivery checks; their status must be recorded from their own evidence.

