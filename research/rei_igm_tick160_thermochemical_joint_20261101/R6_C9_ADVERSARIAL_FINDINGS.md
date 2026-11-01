# Same-context adversarial referee | 2026-11-01

*Not a distinct-author blind review. The source CI's generated original state and the present scripts share project context, although the independently implemented arithmetic does not import the main scientific code.*

### Adversarial falsification and decisions
1. **Source correlation/lane inflation:** Three source lanes have exact same 46,080 numeric state arrays (verified owner SHA `cc031a...` and every numeric field), therefore **46,080 physical states**, not 138,240 independent samples. PASS scoped.
2. **Original physics versus new atomic energy:** NIST atomic ionization potentials are an explicit new reference to annotate original state, **not a claim of exact 26-event source energy constants**. Cannot claim identity to full augmented energy or a new reionization simulation. CONSTRAIN CLAIM.
3. **Fixed u_mat is not an ODE conservation:** It is an isochoric algebraic counterfactual. Full EoR gains/loses radiation, heat, and expansion work. It cannot replace the original dynamical Jacobian. CONSTRAIN CLAIM.
4. **Helium basis**: A naive partial derivative with x_HeIII varying at fixed x_HeII corresponds to simultaneous HeI -> HeIII, not elementary HeII -> HeIII. Corrected by evaluating the physical path d x_HeII=-d alpha, d x_HeIII=+d alpha. Both explicit finite-difference and analytical results recorded. DEFECT FIXED.
5. **Independent U/xe boxes**: 252 rebuilt parent widths exceed the **numeric scale** 2e-4; original error gate is for full/two-half local error, not for parent width. They MUST NOT be reported as 252 failed source nodes or as a bound that the next step passes. PASS claim boundary.
6. **Pseudo-independent review**: An alternate pandas/NumPy source reader independently recomputes full 46,080 rows and checks 200 common-state finite differences; same author context, not distinct-author. PASS scoped; external review NOT_RUN.
7. **Parent locked failure**: One tick recorded local error=2.1245050576368385e-4 >2e-4, all three lanes blocked. No state source edit, tolerance relaxation, fake acceptance, extra IVP, or canonical progress. PASS scope.
8. **One invalid initial hash transcription**: First pipeline invocation rejected a 63-character mistyped expected state-body SHA before any computation. Corrected using exact 64-char source JSON and reran all actual tests. Historical failure preserved in this note; no data or acceptance tolerance changed. ERROR_KIND=implementation/source-transcription, closed.
9. **Independent Jacobian certificate still missing**: Full source event/screen/table Jacobian + correlation remainder at tick [160,161] NOT_IMPLEMENTED. It would be mathematically incorrect to promote the thermodynamic algebraic derivative to that certificate. HOLD central M1.

### Next shortest real science action
Obtain original 26-event nonlinear owner `F_h` with unmodified parent tick160 source and exact interval dual numbers/affine sensitivity. Construct the common-parent difference map `D_h(y,theta)`, not two independently enclosed images. Bound source/parent Jacobian and remainder across 3 lanes, then retry exactly [160,161] with the **same original local-error 2e-4**, unchanged min step and positivity/conservation gates. Stop on actual original failure, do not iterate wrapper PRs.
