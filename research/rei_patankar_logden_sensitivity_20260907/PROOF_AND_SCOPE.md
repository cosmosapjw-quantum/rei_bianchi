# Patankar denominator sensitivity after the conservative solve

Task layers: derive, research-reference verification, review. This is a conditional result for the actual algebraic population-stage form mapped in REI PR #74, not a new production solver, a real rate bound, or an exact-flow defect certificate.

## 0. Input authority and before-state

Parent: REI PR #74 at `032b59372e55bdbb86860e8075206bd0026f7be1`, tree `7220d791d614d34e63097e3115c8036fcfcb8e94`. Its tested mapping source was `9605f8f89e35c2a25d60e8dc0098c6d859d38e66`, tree `2663929364f577cb6f1dd4e09520bb3f56d5a336`.

The mapping and existing ten-method log were read, not rerun. The preserved `mprk22.py` uses F[dest,source], divides each column by its strictly positive denominator, and solves with RHS y0. Predictor and gamma denominators are y0; corrector denominator is yp and its flux is (F0+F1)/2. No source/tolerance/SSOT or previous test is modified here. Gamma remains 1-1/sqrt(2); the proof applies to any fixed nonnegative substep, while the exact composed fixture tests the actual rational MPRK22(1) predictor/corrector weights, not an invented rational replacement for gamma.

PR #74's entrywise generator bound contains a valid term proportional to |F_ij| |delta d_j|/m_j^2. That is not a demonstrated code defect. This work asks whether first multiplying the denominator tangent by the conservative resolvent exposes cancellation that the entrywise norm bound loses.

## 1. Domain, notation and units

Let K(F) have off-diagonal entries F_ij>=0 and diagonal K_jj=-sum_(i!=j)F_ij. Let D=diag(d), d_j>0, A=K(F)D^-1, P=(I-hA)^-1 and v=P b with b>=0 and fixed h>=0. For an REI population stage, b and d are extensive population counts in the declared node normalization, F is counts/s, A is s^-1 and h is proper-time seconds. No c=1 conversion is made; hA is dimensionless.

Assume fixed w_i>0 with w^T K=0, and use ||x||_(1,w)=sum_i w_i |x_i|. For the actual H/He graph this holds with weights constant on each connected elemental block, even when different blocks/nodes carry different fixed scales. Do not use particle-count or energy weights as conserved nuclei weights. This proof needs no detailed balance, irreducibility, or positive flux on every edge. Nonnegative b is enough for the theorem; the preserved implementation has the narrower strictly positive-state admission.

The frozen result from PR #73 gives P>=0, w^T P=w^T and ||P||_(1,w)=1. In particular 0<=P_jj<=1. Set M=w^T b=w^T v. Fixed flux below means every F_ij is held fixed, not merely that some externally supplied photoionization input is fixed.

Write r_j=delta d_j/d_j. This is a dimensionless differential, equivalently delta log(d_j/dref_j) for any fixed positive reference with matching units. Finite logarithms below always have a dimensionless ratio e_j/d_j.

## 2. Exact denominator-only cancellation

At fixed F,b,h, delta A=-A diag(r). Differentiating (I-hA)v=b gives

    delta v = h P delta A v = -h P A diag(v) r.

Since P(I-hA)=I, h P A=P-I. Therefore

    [T1] delta_d v = (I-P) diag(v) r.

This identity is exact for the frozen algebraic solve and includes the correct sign. It remains valid at h=0, where both sides vanish. It does not replace v by the denominator d or change the stage RHS.

For column j of I-P, weighted conservation yields

    sum_i w_i |delta_ij-P_ij| = 2 w_j (1-P_jj).

Consequently

    [T2] ||delta_d v||_(1,w)
      <= 2 sum_j w_j v_j (1-P_jj) |r_j|
      <= 2 M ||r||_infinity.

This is a bound in relative/log-denominator coordinates. It removes the explicit squared-small-denominator penalty for this contribution after the solve. It does NOT claim that the full absolute derivative is uniformly bounded at d=0, nor that binary floating-point evaluation of I-P near h=0 is cancellation-free. The first, componentwise upper bound is often substantially sharper than 2M. No claim of optimality of the universal constant 2 is made.

For small hA, I-P=-hA+O(h^2), so the exact contribution tends to zero with h. A numerical implementation would need a stable evaluation choice; this work supplies an exact reference and proof, not a production floating-point algorithm.

## 3. Finite denominator changes without Taylor remainder

For the same F,b,h and two positive denominator vectors d,e, let P_d,P_e be their resolvents and v_e=P_e b. Since A_e=A_d D_d D_e^-1, the resolvent difference identity gives

    [T3] P_d b-P_e b
      = (I-P_d) diag(v_e) (d/e-1),

with elementwise ratios. Thus an entirely algebraic finite bound is

    ||P_d b-P_e b||_(1,w)
      <= 2 sum_j w_j (v_e)_j (1-(P_d)_jj) |d_j/e_j-1|
      <= 2M ||d/e-1||_infinity.

Swapping d and e gives a second valid bound. Also both outputs are nonnegative with the same weighted mass, so their distance is <=2M.

A scale-symmetric bound follows along the positive path d(theta)=d*exp(theta log(e/d)), 0<=theta<=1. Its mass is M at every point, and T2 applies with r=log(e/d). Integration gives

    [T4] ||P_e b-P_d b||_(1,w)
      <= 2M min(1, ||log(e/d)||_infinity).

This global finite statement is ONLY for the denominator-only comparison. A small absolute perturbation near zero can have a large log-ratio, so this result does not erase the boundary problem. The path never sets a denominator to zero. The general theorem is analytically proved; rational fixtures corroborate finite cases, not all real inputs by enumeration. The checker uses rigorous rational upper enclosures of logarithms only in small finite cases.

## 4. Full differential: do not lose flux and RHS changes

Allow differentiable variations of F,d,b while h remains fixed. The exact total differential is

    [T5] delta v = P delta b
                 + h P K(delta F) D^-1 v
                 + (I-P) diag(v) (delta d/d).

The second term remains even after the denominator cancellation. Source state/temperature/radiation dependence, global owner normalizations and branch laws all enter delta F. Replacing the full derivative by T1 would therefore be wrong.

For the actual graph, an edge transfers within an equal-weight block. The flux contribution can be bounded by

    ||h P K(delta F) D^-1 v||_(1,w)
      <= h sum_(i!=j) |delta F_ij| (v_j/d_j) ||P(e_i-e_j)||_(1,w)
      <= 2h sum_j w_j (v_j/d_j) sum_(i!=j)|delta F_ij|.

This still needs actual flux derivative/tube bounds and may be loose or singular. We have not evaluated them. For general weighted graphs without equal endpoint weights, retain the first edge norm instead of silently replacing it by 2w_j. For variable h an additional P A v delta h term is necessary; the task holds h fixed.

## 5. Apply the identity to the mapped REI stages

Write A0=A(F0,y0), Pp=(I-hA0)^-1, Pg=(I-gamma*h*A0)^-1 and Pc=(I-h A((F0+F1)/2,yp))^-1. Then

    delta yp = Pp delta y0
             + h Pp K(delta F0) diag(y0)^-1 yp
             + (I-Pp) diag(yp) (delta y0/y0),

    delta yg = Pg delta y0
             + gamma*h Pg K(delta F0) diag(y0)^-1 yg
             + (I-Pg) diag(yg) (delta y0/y0),

    delta yc = Pc delta y0
             + h Pc K((delta F0+delta F1)/2) diag(yp)^-1 yc
             + (I-Pc) diag(yc) (delta yp/yp).

These are computationally useful reorganizations of PR #74's derivative, not different integrator stages. The RHS is y0 throughout, the corrector denominator is yp, and delta yp is not zero. delta F1 retains the predictor thermal/state/source dependence. The exact fixture checks this composed predictor/corrector tangent against forward dual-number differentiation of a separate two-state closed-form solve with a declared synthetic flux law.

No thermal row is added to K. The thermal system is open and its full inverse bound remains UNKNOWN; the fixed-Q slope does not include dynamic heating derivatives. No smooth derivative is asserted through CELL_LOWER_STRICT jumps, active-set boundaries or a failed positive denominator condition. Four independent source sites remain independent.

## 6. Two complementary small-denominator examples

All following examples use dimensionless normalized populations and one declared time unit; they are algebra fixtures, not physical atomic rates.

Example A: h=1, F10=1, F01=0, b=(1,1), d=(epsilon,1), epsilon>0. Then

    v1=epsilon/(1+epsilon),
    ||partial v / partial log d1||_1=2epsilon/(1+epsilon)^2.

The old coarse resolvent-plus-generator bound for r=(1,0) is 4/epsilon, while the exact output derivative tends to zero. Thus a small denominator alone does not prove a large output sensitivity.

Example B: h=1, F10=F01=1, b=(1/2,1/2), d=(epsilon,epsilon). At these base points v=b, but varying d1 alone gives

    ||partial v / partial log d1||_1=1/(epsilon+2),
    ||partial v / partial d1||_1=1/[epsilon(epsilon+2)].

The relative derivative stays bounded while the absolute derivative diverges. This refutes the overinterpretation that the new bound proves a uniformly benign population boundary. Both examples are checked for exact rational epsilon down to 10^-18. No clipping, denominator floor, threshold change or production relaxation is introduced.

## 7. Literature and review

SciSpace returned MPRK stability and weight-denominator papers. The primary abstract of Torlo, Öffner and Ranocha, `Issues with Positivity-Preserving Patankar-type Schemes`, arXiv:2108.07347 (Applied Numerical Mathematics 182, 117-147; DOI 10.1016/j.apnum.2022.07.014), identifies oscillations and order reduction near vanishing initial components. This motivates retaining boundary/accuracy qualifications; it does not supply T1-T5 or validate this repository. No novelty claim is made for the resolvent algebra or norm argument. Only abstract-level methodological content is attributed to that paper here.

Sequential PHYS-MATH review: positive-domain, fixed-flux versus total derivative, fixed timestep, conserved positive weights, units, signed flux tangent, exact finite identities, limits and the absolute-derivative counterexample are explicit. Claims for physical rate bounds, thermal coupled bounds and exact-flow defect rho remain UNKNOWN.

Sequential PHYS-MATH-CODE review: reuse the earlier exact matrix helper; pin and read the preserved mprk22 source without importing it. New checks use exact Fraction arithmetic, an independent two-state formula/dual arithmetic and mutation controls. No old ten-test suite, native calibration, package acquisition or production call is rerun. The same assistant's two reviews are not independent reviewers. Execution status must be read from actual new logs, not this proof.

## 8. Scope after completion

The deliverable is a denominator sensitivity identity and bounded exact research oracle applicable to the mapped population solve under stated hypotheses. It does not implement the absent source-bound four-site Rust replay ABI, provide real rate/Jacobian constants, establish binary64/MPFR rounding error, bound the ODE-flow defect, or admit the first interval/provider.

Next material obligation: evaluate the remaining flux-response contribution for one explicitly event-free positive physical tube, using actual source dependencies and keeping the already derived denominator term separate. Source reading possible in the main conversation stays there. Only missing local saved input or actual high-precision/interval execution is delegated directly to local Codex. Do not repeat this generic oracle or make another WORK_THREAD.
