# ANGTHERM02 — scientific decision

Date: 2026-10-23 UTC. Authority: Astra controller.
Procedure: physmath-research-loop intrinsic 1.0.0 / approved v0.2, retained for this frozen unit.

## Admission

**PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE.**

Admit splitGL16_thin as the selected late trace-lithium response on the explicitly prescribed primary thermal/electron bath, retained grid044 geometry and source fits, and the common saved M16 seed at eta*=0.10702505819804223. All 13 preflight checks, ten selected small cases, ten numerical admission gates, fresh independent raw-array review and three direct figure inspections passed.

This closes the selected numerical/theoretical leaf. It does not close the full coupled continuum-angular 2e-7 objective. The exact-bath error, earlier continuum seed and higher-energy angular tail outside retained M16 rays have not been bounded by this unit.

## Frozen criteria and observations

Native fractions are normalized per total Li nuclei. Maxima of pairwise differences are over the declared 593-point common late report grid unless specified; original M16 comparisons use 190 exactly matching report times. Invariants also use accepted states.

| Quantity | Observation | Frozen requirement / interpretation |
|---|---:|---|
| GL16 rate coefficient versus independent scalar quad | 5.417909337147719e-16 normalized difference | <=1e-10 |
| Split GL16 versus GL32 fractions | 3.362649048099797e-11 | <=2e-8 |
| Split GL8 versus GL16 fractions | 1.0371814518350675e-11 | Report separately; no fitted order |
| Fixed M16 thin versus attenuated | 2.833488998987832e-11 | <=expm1(2e-8)+2e-9 |
| Attenuated M16 reconstruction versus saved M16 | 2.5929480784725456e-11 | <=2e-7 |
| Primary versus secondary bath | 2.3851890296189282e-8 | <=2e-7 sensitivity gate |
| Fraction-sum residual | 2.4424906541753444e-15 | <=2e-10 |
| Charge-event residual | 2.886579864025407e-15 | <=2e-10 |
| Event-energy residual | 1.2434497875801753e-14 eV/Li | <=2e-9 eV/Li |
| Minimum raw Li fraction | 7.136066675025076e-16 | >=-2e-12 |
| Largest B_last plus numerical margin | 6.132548021438158e-9 | <delta=2e-8 |
| Standard/tight B_last difference | 7.385391109312327e-18 | <1e-11 |
| Late seed and initial optical profile | Both envelope inequalities pass | Required |

The selected endpoint fractions at eta=ln(7) are
(0.32552356726438253, 0.674475620781234, 8.119543832501908e-7, 7.136076709037422e-16).

Fixed M4/M8/M16 comparisons against split GL32 give
1.98067616514889e-4, 1.012636510152598e-4, and 3.06125673253943e-5.
The M16 maximum is near eta=0.71975; its endpoint discrepancy is only
3.581540108932302e-8. Endpoint agreement would hide the transient threshold error.

## Constructive result and its assumptions

The fixed covariant angular measure is dmu0. Restrict positive Gauss–Legendre weights to the actual ionizing interval with its physical width. Moving integration nodes evaluate the thin integral; they do not inherit invented optical histories.

For the same imposed bath, late seed and upper charge states, if 0<=tau<=delta,
the thin and attenuated neutral fractions obey

    0 <= f_I,attenuated - f_I,thin <= expm1(delta).

The Li II difference is opposite and the higher-state differences vanish analytically. The inequality follows from the scalar difference equation with a nonnegative forcing and its dissipative integrating factor; it has no amplification by the large total photoionization rate.

The independent full-time F/B comparison closes the optical-depth assumption numerically for the declared family of initial profiles bounded by Bstar. The adopted cross-section maximum 1.66e-18 cm^2 is above the source-fit maximum 1.65892479072499e-18 cm^2. Two tolerance runs give B_last≈6.03254802e-9. Thus the frozen conditional component implication is expm1(2e-8)=2.00000002e-8. Numerical margin and tolerance agreement are not interval-arithmetic certification.

The retained higher-bin count bounds additional future absorptions only for the finite saved M16 tail. The data are retained in logarithmic form to avoid turning numerical underflow into an exact-zero claim. No bound on unobserved continuum directions is inferred.

The last-threshold asymptotics are

    active width ~ (eta_L-eta)^(1/2),
    Lambda0 ~ A*(eta_L-eta)^(1/2),
    LambdaE-chi*Lambda0 ~ (2/3)*chi*beta*A*(eta_L-eta)^(3/2).

They explain the differing sensitivity of ionization and photoelectron excess heat, and support the explicit last-crossing time split. They do not bound the entire temperature history.

## Equation-to-code and physical ledger scope

All four fractions are retained directly, with no floor, clipping or renormalization. The five event ledgers verify charge and energy transferred to/from the prescribed bath. The bath is not updated. This result is not substituted into the original radiation/gas/Einstein ledgers and described as a new conserved full-system solution.

The primary bath is the saved-node log-Hermite model with original-RHS slopes; the secondary is log-PCHIP on the same samples. Their difference is a sensitivity control, not an enclosure of an unknown exact bath. GL8/16/32 differences at approximately 1e-11 do not establish an asymptotic order or a rigorous continuum-error bound.

## Cost, recovery and stopping decision

Ten small IVPs were completed once: eight late response cases and two two-state opacity envelopes. No original full gas/photon trajectory was rerun. Case6 has nine states, 1055 accepted nodes, and 2.095741451 CPU seconds. Fixed M16 thin has nine states, 2415 accepted nodes and 4.472551900 CPU seconds. These are finite observations on this conditional model, not a universal or equal-accuracy full-model speedup claim.

Charged solver/check/analysis use is 105.71851917 CPU / 135.995204254 wall seconds, inside 120/180. Known measured use is 45.71851917 CPU / 45.995204254 wall seconds, plus a conservative 60/90 debit for the original pre-reset failure whose actual usage is unknown. Of the known measured use, 1.948593 CPU / 1.986869219 wall seconds survives only in tool history because its raw logs were lost. Packaging is separate.

Two workspace losses occurred before the ten selected IVPs. The prior exact archive was restored, prepared texts recovered, and the reconstructed executable freshly reviewed. Serialization, equivalent row-container comparison, clean log-directory setup, nested CPU limits, donor module shadowing and one plot-range issue were diagnosed and repaired without changing physical parameters, tolerances or admission criteria.

No further IVPs, solver sweeps or optional checks are requested for ANGTHERM02. R9/R10 and C9/C10 close with this decision, report, DAG and handoff; external delivery is tracked separately by actual receipts.

## Next dependency

Prioritize a new bounded thermochemical-feedback/retained-bath error study using this support-resolved coefficient. The observed bath sensitivity 2.385e-8 now exceeds the split-quadrature discrimination 3.363e-11. Start by defining how corrected Li charge and heat events couple to gas/electron equations and which earlier seed is retained. Derive the smallest closed response or justified sensitivity model before proposing runs. Earlier angular-continuum seed and extinct higher-bin continuum-tail control remain explicit dependencies of any full-history accuracy claim.

Keep source-spectrum/emission/escape, nonzero beta/stopping channels and Einstein feedback as distinct later dependencies. New CR/REC donor results are candidates for those units, not already admitted physics here.

## Evidence

- THEORY_CONTRACT.md; THRESHOLD_ASYMPTOTIC.md
- INDEPENDENT_REVIEW.md
- results/preflight.json; ten case NPZ/JSON pairs
- results/comparisons.json; results/execution_summary.json; results/cost_receipts.json
- figures/01_rates_support_li.png; figures/02_signed_fraction_errors.png; figures/03_bootstrap_ledgers.png
- sources/SOURCE_ASSESSMENT.md; sources/WOLFRAM_CHECK.md
- delivery/CHECKPOINT_RECEIPTS.json; DAG.json; HANDOFF.md

Prepared commit: 1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c.
Implemented-observed commit: 906f217f412500fd8d4129818e70a4064439c945.
Final publication and provider acknowledgements are external delivery facts recorded by the final delivery sidecar; they are not a condition hidden inside the numerical PASS.

