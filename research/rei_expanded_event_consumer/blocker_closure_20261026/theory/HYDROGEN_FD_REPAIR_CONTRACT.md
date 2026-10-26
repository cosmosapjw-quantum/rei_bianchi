# One targeted repair: resolved hydrogen finite-difference displacement

Version1.0,2026-10-26. Scientific authority next_source_theory; root supplies resource authorization and RUN_GO. No numerical execution by the theory agent.

## Observed failure and scope

Original run01 is preserved byte-for-byte. CHECKS.json SHA2568b2a87870e7b7c8d37fcd75422bb056671e0ba17c377df1178de877d9d5905e9 reports82/84PASS. The only failures are:

- full_native_hydrogen_electron_feedback_JVP:4.712660174501273e-8 against2e-8.
- native_hydrogen_electron_feedback_electron_tangent:5.667163219414058e-8 against2e-8.

Raw CALLBACK.json SHA256df5d289dac63d01200cbbffb30fb8c52e6760fc06748c3588c7f26c5d1e12e7e supplies the exact matched snapshot. Native callback/source/input identities are unchanged across run01. Source, isotope/state normalization, energy partners, helium/density/amplitude tangents and domain guards passed. This is a **numerical verification conditioning failure** in a finite-difference probe, not evidence of a changed physical model, invalid source, resource exhaustion or incorrect native analytic derivative. Retain that classification as a diagnosis to be confirmed by the single affected repair.

## Derivation and chosen correction

At fixedT,nb,lambda the native F(Y)=L*Y+nb*(q.Y)*R*Y is polynomial of degree2 inY; n_e=nb*q.Y is linear. Thus for every nonzero realh whose trials are defined, exact arithmetic gives

    [F(Y+h*v)-F(Y-h*v)]/(2*h)=J(Y)*v,
    [ne(Y+h*v)-ne(Y-h*v)]/(2*h)=nb*q.v.

There is exactlyzero centered truncation error. The selected hydrogen direction is unchanged: v1=-1e-5,v2=+1e-5, otherszero, so q.v=1e-5 andG*v=0. The two failing probes usedh_old=1e-4, giving changesh*v=1e-9 againstq.Y approximately0.876. The elementary relative subtraction scale is epsilon_machine*abs(q.Y)/(h*abs(q.v)), approximately2e-7 at the oldh; the observed~5e-8 discrepancies are consistent with roundoff at this scale. This estimate is a conditioning diagnostic, not a rigorous bound on the complete BLAS/operator evaluation.

Freeze **h_new=1e-2** for these two checks only. The actual abundance displacement becomes1e-7,100times larger. The elementary subtraction scale falls100times toapproximately2e-9, below the unchanged2e-8 threshold with a useful margin; exact polynomial truncation remainszero. The actualY_HI=1.8453372310189325e-5 andY_HII=0.7529482333969896 keep both trials positive with this displacement. All other entries are unchanged. The step choice is determined once from the observed conditioning and domain, not selected by trial until passing.

For the RHS difference continue using the returned native rr_rhs+dr_rhs+decay_rhs, sinceG*v=0 exactly. Compare against the **full native analytic J*v**. This is the same directional derivative and avoids an unrelated unchangedphoto subtraction. Do not alter the actual native rates/evaluate or analyticJVP. Neither the2e-8 tolerance nor its positive reference scale changes.

## Implementation and finite stopping rule

Lower-tier executor may add a dedicated repair checker and receipt runner underimplementation/. Do not rewrite run01 files or the original frozen contract/checker. Consume the saved run01snapshot directly, verify its identity, and instantiate the same PW19HeIINetwork with the same admitted source packet and native code. Reusing the saved snapshot avoids unnecessary donor interpolation or source-quadrature recomputation.

Run exactly the two affected numerical checks, at h_new only. Report originalcheckname,oldh/newh,originalresidual,newresidual,unchangedlimit2e-8, positive trial-domain margins and elementaryroundoff scales. Preserve actual native finite-difference vectors and references so the reviewer can inspect the cancellation resolution. The domain and inputidentity observations are setup metadata, not a replay of the82 successful tests.

No84check rerun, no historical suite, no new sourcequadrature, noIVP, no physicalparameter or coefficient change, no additional finite-difference scan. If either check still fails, retain its raw result and returnHOLD to independent authority; no secondautomaticstep/repair.

The combined result is82 run01PASS checks reused plus2 targetedrepair outcomes. Report it as combined evidence across two executions; never rewrite the original run01 as84/84PASS. Fresh independent reviewer examines only the changed probe and actual affected outcomes. Physics admission follows only if the original gate and combined evidence support it.

## Resources

Known cumulative before this repair11.368119996CPU_s. Root may reserve up to0.8CPU_s total including startup/wrapper/receipt for this one repair, within temporarycap13CPU_s (originalbaseline10,+30%,no reset/ratchet). Suggested childsoft0.7CPU_s, hard1CPU_s, wall5s,512MiB,oneworker,BLASthreads1; root freezes the actual enforceable limits beforeGO. If the implementation requires a larger launch envelope, root may reserve within remaining13−11.368119996 without scientific scope expansion. All costs, including any failed launch, remain cumulative. Temporarycap returns tobaseline10 after the authorized run; no future allowance is inferred.
