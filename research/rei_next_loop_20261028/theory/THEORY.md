# Supplied caloric branch and uncertainty transport

Result: a strictly increasing piecewise-affine caloric branch admits an exact rational inverse, and a supplied uniform EOS discrepancy widens the energy interval before inversion. This constructs the implementation link absent from prior finite_thermal R5 section 7. It uses the saved source only as represented-law calibration. The actual REI recipient EOS and physical radii remain inputs to a later physical binding.

## R1–R4: scope, source, and choice

The fixed finite source law already provided E/(cv D), residual/JVP/normalization/segment identities, and a C1 monotone inverse theorem. Repeating them would add no scientific result. This unit supplies an explicit finite branch representation, a closed-form exact algorithm and uncertainty transfer that was not implemented in that source. The source reviewed at b77c7b8d45c48a7e4722e733309430d5ba668b0d explicitly says general-EOS inversion remains theoretical; see finite_thermal R5 section 7 and POST_DISCLOSURE_R6_C9.md claim ceiling. The existing source-law result and its F1 corrected encoding relation are reused unchanged.

Metric convention (-,+,+,+), c,hbar,kB explicit when relevant. This scalar thermodynamic construction introduces no metric dynamics. All comparisons use common reference-volume energies in J and temperature in K. The thermal store excludes independently owned atomic, radiation and fast-electron stores. An energy-origin shift is permitted only when applied to BOTH EOS and target energy with consistent store bookkeeping.

Choose a caller-supplied piecewise-affine branch rather than an arbitrary numerical root finder: its inverse and slope bound are finite exact constructions. This is a one-dimensional caloric slice at a fixed non-temperature state, not a full pressure/density EOS. The change has a concrete consumer: replace the hard-wired ideal inverse by a supplied branch in the additive endpoint adapter.

## R5: constructive proof

Let I=[T0,Tn], 0<T0<...<Tn, and F0(Ti)=Fi with F0 continuous affine between knots and F0 strictly increasing. Write si=(Fi+1-Fi)/(Ti+1-Ti)>0 and m0=min_i si. For U in [F0,F_n], select i such that Fi<=U<=Fi+1. Then

    Inv(U)=Ti+(U-Fi)/si.                                      (1)

It lies in its segment and substitution gives F0(Inv(U))=U. At a shared endpoint both segment formulas give the same Ti. Strict monotonicity yields uniqueness. All operations preserve rationality for rational input knots and U.

For x<y, split [x,y] at knots. On each subinterval F0 gains si times its width, so summing gives

    F0(y)-F0(x) >= m0(y-x).                                  (2)

This proves an inverse Lipschitz constant 1/m0 without assuming differentiability at knots.

Let actual F_* be continuous and strictly increasing on I. Assume a SUPPLIED uniform bound |F_*(T)-F0(T)|<=eta, eta>=0, on all I. Let actual U_* lie in [Elo,Ehi]. If

    F0(T0)<=Elo-eta <= Ehi+eta<=F0(Tn),                       (3)

then F_*(T0)<=Elo<=U_* and F_*(Tn)>=Ehi>=U_*. Continuity and strict monotonicity give one actual root T_*. At that root F0(T_*) lies [U_*-eta,U_*+eta] and hence

    T_* in [Inv(Elo-eta), Inv(Ehi+eta)].                      (4)

The enclosure is sharp over the stated unconstrained family: take U_*=Elo,F_*=F0+eta for the lower endpoint and U_*=Ehi,F_*=F0-eta for the upper endpoint. These shifted branches satisfy all assumptions and (3). Physical admissibility and correlations may shrink this family; sharpness here concerns only the declared mathematical information set.

For any Tbar in I, energy center Ebar and bound |U_*-Ebar|<=eE, the triangle inequality gives

    |F0(T_*)-F0(Tbar)|
       <= eta + eE + |Ebar-F0(Tbar)|.

Combining with (2) proves the a posteriori bound

    |T_*-Tbar| <= [eta+eE+|F0(Tbar)-Ebar|]/m0.                (5)

The numerator includes numerical/root residual, energy uncertainty and EOS discrepancy separately. Their units are energy per reference volume; m0 has energy per reference volume per K. A tiny represented conservation defect supplies none of the physical uncertainty terms. Missing eta or eE remains unknown.

If a composition parameter z lies in a convex allowed region and a separately established bound |partial_zj F(T,z)|<=Lj holds for every T in I and every z on the line from z0 to z, with |zj-z0j|<=rj, the line-integral fundamental theorem gives

    |F(T,z)-F(T,z0)| <= sum_j Lj rj.

Thus a supplied interpolation/model discrepancy eta0 at z0 yields eta=eta0+sum Lj rj. This is a conditional construction; no Lj or rj is manufactured from missing REI state. This optional formula is a theory result, not required numerical functionality in the first adapter.

Under F0'=aF0+b,U'=aU+b,eta'=a eta,eE'=a eE with a>0, slopes and residual numerators scale by a while inverse temperatures do not change. This proves common energy-unit/reference-scale covariance and energy-zero invariance. The parameter b is constant for the fixed composition slice. A composition-dependent binding shift needs its own energy terms; it cannot be silently gauged away.

## R6–R7: independent checks and discrimination

Algebra checks: substitutions prove (1); segmented sums prove (2); order comparison proves (4); triangle inequality proves (5). A nonlinear discriminating example F_*(T)=T^2, T in [1,3], F0(T)=4T-3 has F0-F_*=(T-1)(3-T) in [0,1], derivative F_*'=2T>=2. For E=4, (4) gives [3/2,2], containing the exact root 2 and reaching its upper end. This separates the method from merely repeating the ideal quotient.

Remote Wolfram polynomial checks returned two exact zeros and one nonnegativity True for a quadratic difference/Taylor remainder and radius sign. It emitted Symbol::undefined2 for T0/T1 and General::messages. Retain those warnings; this is limited algebra support, not a proof of the order theorem or a new physical computation. Remote cost UNKNOWN_NOT_ZERO. New local scientific tests and source adapter execution NOT_RUN. Independent non-author review of this new derivation remains pending.

Existing SciSpace and Exa searches on 2026-10-28 located Gary A. Dilts, Consistent thermodynamic derivative estimates for tabular equations of state, Phys Rev E 73,066704 (2006), original https://arxiv.org/abs/physics/0510195, DOI https://doi.org/10.1103/PhysRevE.73.066704. The primary abstract distinguishes thermodynamic consistency from interpolant stability. It contextualizes the decision to expose a caloric slice instead of claiming a full thermodynamically consistent EOS. D.E. Maiden's Thermodynamic Interpolation (1998), https://www.osti.gov/servlets/purl/7449, likewise distinguishes monotonic interpolation from consistency. Neither source is invoked as proof of (1)–(5), which are derived here. No literature novelty claim is made; contribution is the exact REI implementation/uncertainty bridge.

## R8–R10: scope and handoff

Conditional algebra is DERIVED. New implementation/runtime acceptance remains pending. The scientific gain is a computable supplied-EOS branch and explicit propagation of model/composition uncertainty; actual physical error numbers remain INPUT_PENDING. This is constructive and does not propose a no-go theorem: NG1–NG7 admission not invoked. Singular/absent brackets are domain failures for this algorithm, not impossibility of the physical problem.

Frozen implementation, source fields, exact controls and stop/resume requirements are in EOS_BRANCH_CONTRACT.md. This new unit leaves original working33/88, central28/88, 88 IDs/17 edges unchanged; L4_ready=false and global_physical_completion=null. R6 independent review and R7 runtime discrimination remain pending. Final R8 scientific adoption and R10 completion cannot precede them. No new CPU allowance, publication or physical closure is created by this theory note.
