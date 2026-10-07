Publication note: hash declarations in this historical report identify archived original bytes. Relocated publication hashes are recorded in ../PROVENANCE.json. Some historical guard/run artifacts are summarized rather than copied; use ../README.md for the supported replay boundary.

# Bounded continuous-boundary prototype: PARTIAL

This is an additive pure-radiation research prototype. It is not an accepted radiation solver, a coupled cosmological history, a production change, or recovery of the existing 37-field certificate. No coupled reference is released by this result.

## Useful results

- Rust 1.94.1 implements continuous swept initial-density intervals, positive initial moment abscissae, the frozen-rate/source characteristic kernel, source/HI/HeI/HeII event partitions, exact-time source-only E^-2 controls, and ordinary/front-vanishing exponential reconstructions.
- Source-front density has the factor (1-y) throughout its interior. Its trace tends to zero genuinely; it is not an endpoint reassignment. Explicit occupied support prevents future-source leakage.
- Initial quadrature weights are the analytically computed interval photon mass; the abscissa is its energy-moment mean. The same positive weight multiplies every owner. No weight renormalization, owner repair, clipping, source normalization change, or posthoc conservation correction is used.
- The unit-amplitude (K=1) source-only analytic expanding-band fixture uses exact-in-time injection on each characteristic segment, with the identical injected contribution feeding all ledgers. Off-phase epochs, emission-interval partitioning, injection-and-exit within one interval, front entry, and a separately labeled direct-below-band control pass.
- The final Rust suite has 10 passing groups and one failing accuracy gate. The independent 80-digit oracle has 1,026 passing component/root checks, but 11 failing approximation/admission gates. The aggregate result is PARTIAL, not PASS.
- Maximum source-only original number/energy budget ratios are approximately 2.754e-6 and 6.341e-6. The original formulas are unchanged. Nonzero-initial controls are separately audited against their initial inventory and are not production comparator certificates.
- N/M closure round trips are within 4.183e-16 relative for the tested cases. A separate source-shape E^-3 observable reconstruction bias decreases from 8.200e-5 at 4 panels to 1.061e-7 at 64 panels.

## Two unresolved numerical gates

### 1. Initial-opacity quadrature accuracy

The moment-consistent rule conserves the initial inventory but is only a low-order approximation for spectrally varying absorption. At 64 subdivisions the error is 1.91049e-5 relative to the independent high-precision integral, above the unchanged 1e-6 target. The 512-subdivision diagnostic reference gives 1.88093e-5 for the same 64-subdivision comparison; it is not treated as an exact oracle.

Errors for 4/8/16/32/64 subdivisions against the 512 reference are 3.41679e-3, 1.26597e-3, 3.17384e-4, 7.51476e-5, and 1.88093e-5. The later refinement is approximately second order. Extrapolation, not a new test, suggests 128/256/512 would give roughly 4.8e-6/1.2e-6/3.0e-7, so 512 is a plausible next candidate under the same target. The frozen candidate sequence ended at 64; no new 128/256/512 acceptance sequence was run. The existing 512 calculation was a diagnostic reference only.

### 2. Narrow-support normalized mean conditioning

All ten approximately 1e-7-width closure cases fail the 5e-13 absolute scaled-mean target when authoritative binary64 N/M/L/R inputs are interpreted exactly by the oracle. Worst error is 1.61282e-9. Wider tested cases pass this gate. Forward N/M round trips passing does not erase this failure.

The root solve matches its internally rounded normalized target. The separate input-to-target calculation subtracts nearly equal quantities and amplifies binary64 moment/transcendental rounding by about 1/width. The correct oracle is the exact binary64 input moment pair, not the original generating beta. A next bounded design should consider centered/scaled stored moments or compensated/higher-precision arithmetic, with the same acceptance target. This prototype does not solve that conditioning problem or claim tiny-cell readiness.

## Positivity, tails, and explicit rejection

Authoritative exact-empty state is distinct from retained logarithmic inventory. A source-free local kernel can retain logarithmic number/energy when its readout underflows. The multi-segment boundary explicitly rejects number or energy underflow instead of advancing a false empty state. Positive source underflow also rejects. These guards have retained failing-before/passing-after regressions. No integrated log-tail evolution, certified aggregate tail bounds, or universal extreme-state completion is claimed. In particular, arbitrary near-empty initial-panel moment formation can still underflow to a computed zero, and weighted aggregation does not generally propagate log metadata. Those paths are unresolved admission defects outside the tested normal-inventory fixtures; they must not be used as a safe near-empty API.

Endpoint means, unresolved interior quadrature abscissae, below-minimum-width reconstructions, out-of-bracket extreme means, invalid source/rates, and unsplit species support reject. The nominal 1e-7-width fixture whose actual representable width falls just below the frozen minimum remains an expected rejection; adjacent representable admitted geometry is tested separately. Ordinary atom controls remain explicitly singular and retain their physical exit jump.

## Verification and retained failures

- The frozen CONTRACT.json and all eleven source/design input hashes are rechecked by the final manifest; production/baseline evidence is unchanged.
- The first test executable ran against explicit unimplemented stubs and failed all T1–T7 groups. Source and logs are retained in failures/.
- The first narrow-width failure was a fixture-representation issue; the threshold was not changed.
- A T3b expected-initial-energy fixture omitted its initial factor 0.7; the fixture was corrected and the failure retained.
- Independent review identified and corrected the wrong quadrature assertion (1e-3 was the reconstruction target, not the quadrature target), a source-free multi-segment tail loss, positive-source underflow, and energy-only tail loss. The 1e-6 quadrature target remains failing.
- A strengthened oracle run had an indentation/NameError in its new reference section. Its logs are retained; the corrected oracle was rerun.
- Final Rust compilation uses -D warnings. Formatting and the full standalone prototype suite are checked. No production suite or coupled-history run was authorized or attempted.
- HIGH_PRECISION_ORACLE.json distinguishes component agreement, root agreement, exact-input mean gates, and quadrature approximation gates. Its quadrature error estimates are numerical estimates, not rigorous interval bounds.

## Resource scope and caveats

RESOURCE_RECEIPT.json contains every numerical and compilation attempt, including failures. Numerical runs were sequential and single-threaded. Compilation is a separate measured step. Observed CPU, wall time, address-space/RSS and output sizes remain below the frozen 120 CPU-second / 180 wall-second / 512 MiB / 32 MiB ceilings.

The final oracle clears its quadrature caches per integral and conservatively counts retained/current/previous nodes: its measured high-water bound is 2,157, below 4,096. Rust's largest nested evaluation vectors hold 128 samples; geometry breakpoint arrays are separate from evaluation samples.

The first, uninstrumented oracle is retained separately as ORACLE_INITIAL_UNINSTRUMENTED.json. Its live sample count was not measured, so retrospective compliance with the 4,096-sample cap is unverified. This qualification is not erased by the later instrumented rerun. The supervisor enforces per-process limits and now locks launches, but aggregate directory output is observed after runs rather than hard-enforced during writes. This is evidence of measured usage, not a universal resource-safety proof.

## Next scope, not automatically authorized

Keep the two blockers separate: improve or refine the positive absorption quadrature under the same 1e-6 target; redesign narrow-support moment arithmetic under the same 5e-13 target. Then independently review again before any projected multi-step or coupled history. No gas/Radau/BDF histories, p256/z6, production changes, dependency installation, uploads, or provider/source-constant changes occurred.
