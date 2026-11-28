# HE36 finite-source moment implementation: independent review

Reviewed source: `/tmp/he36_moment_implementation/maxwellian_moments.py`, SHA256 `644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`.

This review read source, frozen contract, baseline verification script and receipts, the preserved conditional-mean failure, exact repair diff and affected fixture receipt. It did not dispatch the previous suite or repeat CCC coefficient calculations.

## Findings

1. **SI normalization and source coordinate — pass.** Changing E from J to numerical eV in the Maxwell convolution gives `sqrt(8 eV_J/(pi mu)) theta_eV^(-3/2) ∫E^(j+1)σ(E)e^(−E/theta_eV)dE eV_J^j`. This agrees with the code. Actual CCC incident-electron data is bound to m_e and a distinct heavy-fixed-target mapping. The generic finite-mass path requires its own manufactured-relative-energy label.

2. **Positive quadrature — pass within declared numerical scope.** Interpolation is a positive endpoint combination, and Legendre quadrature has positive weights. All four moments share one fixed set of nodes and exponentials. Therefore it approximates one declared nonnegative finite-support measure, rather than separately fitting its moments. No tail or missing lower interval is added. Fixed finite bin boundaries also make the derivative recurrence valid without boundary terms. No universal quadrature error claim for arbitrary user tables follows; the existing GL16/32 and independent integral witness specifically qualifies its selected table and temperatures.

3. **Temperature derivatives — pass.** The recurrence `dM_j/dlnT=M_(j+1)/(kBT)−3M_j/2` is correct for the fixed source model. The output uses separate sign/log-absolute derivative reconstruction and can retain a derivative even when the lower moment underflows. This does not certify second derivatives of an arbitrary empirical rate fit or explicitly T-dependent collision kernels.

4. **Extreme-input handling — scoped pass.** Nonfinite or negative source data, unrepresentable prepared weights, invalid domains/mapping and overflowing output logs are explicitly rejected. Tiny positive results retain logarithms and underflow/subnormal indicators; all-zero supplied tables have a separate marker and undefined mean/slopes. The original `EV_J*sums1/sums0` conditional-mean defect was preserved, corrected to `EV_J*(sums1/sums0)`, and its affected independent80decimal fixture passed. No claim is made that arbitrary binary64-scale inputs return an accurate value instead of explicit rejection.

5. **Caller obligation — preserve underflow provenance.** A downstream adapter must not reinterpret underflowed positive moment values `(0,0,0)` as an exact zero kernel. It must carry the log/flag provenance or refuse that conversion. The declared CCC2000–200000K witness does not enter this case. This is a prospective API-boundary obligation, not a discovered failure of the current evaluated source rows.

6. **Physical interpretation — scope condition.** Incident energy β and γ are incoming event moments. For CI, the net common-gas kinetic loss depends on ionic defect plus outgoing-particle/escaped-radiation ownership. β is not itself the net chemical cooling. A finite source integral is also not a full physical rate; `require_full_physical_rate=True` correctly refuses that promotion.

## Validation evidence reused

The baseline eight groups use an independently written SI incomplete-gamma integral at80decimal precision, derivatives of that independent expression, and an SI-energy per-bin QUADPACK witness. The tested model and source are held fixed during these numerical comparisons. The9temperature GL16/32 comparison and3temperature adaptive integral comparison therefore test numerical convolution, not empirical cross-section uncertainty. The final receipt correctly links the baseline source to the conditional-mean-only repair and retains its original failed fixture. No existing test result was claimed as a new execution by this reviewer.

## Decision

No blocking defect was found in the finite-source moment module at the pinned hash within its declared partial-source numerical scope. Complete HE36 review still requires the independent finite-mass raw-Cartesian source controls, review of reactive_moments.py and the root event/source assembly contract.
