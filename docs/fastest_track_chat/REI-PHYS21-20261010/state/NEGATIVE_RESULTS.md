# PHYS21 negative results and corrections

## Rejected generalizations

1. A positive free-photon mean-energy quadratic coefficient does not determine absorption or heating signs. Smooth inverse-cube cases yield both signs at different optical depths; exact counterexamples are in the tensor contribution.
2. Zero local mean-opacity curvature for E^-3 does not mean zero survival-weighted response. Mean optical depth is preserved, while survival variance remains; cumulative absorption and instantaneous event rate have different sign statements.
3. A positive thermal energy/H coefficient does not alone determine temperature. The total-particle-count derivative in report Eq. (35) must be retained.
4. Inactive direct He photo forcing does not imply zero coupled He response through nonphoto thermal/electron feedback.
5. Fixed initial neutral-fraction cohort coefficients do not provide evolving-gas or full continuous-source coefficients.
6. PHYS19 published derivative upper bounds and terminal error intervals do not uniquely specify the new time-dependent response. A limited archive-title search did not resolve a ZIP; this does not establish absence or a project-wide blocker.
7. Continuum first-order cancellation is inherited only under PHYS20's conditions; finite-grid generic shear, non-smooth thresholds and Einstein-backreacted mean expansion remain outside the new claim.

## Actual execution and correction provenance

The owner HI check passed 39/39 (exit 0); tensor diagnostics passed 44/44 (exit 0); final local gas derivative diagnostic passed 60/60 (exit 0). No numerical FAIL occurred in these reported executions.

The initial local gas v1 also passed 60/60, exit 0. A subsequent source comparison found that its manual Python transcription combined the two DR Kelvin constants in a different operation order from the source. The code was changed to multiply each constant before addition. The v1 script, result, logs and receipt were retained. The corrected run used the same complex step 1e-24 and relative tolerance 2e-12 and passed 60/60. This is a diagnostic implementation/transcription correction, not an initial failure, physics failure, native runtime failure or tolerance relaxation. Shared transcription can conceal a source mismatch even when its own derivative check passes.

## Preserved project gates

physical=HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED. No source/default/runtime-returns changes, native history, gas IVP or closed PHYS19/PHYS20 proof replay.
