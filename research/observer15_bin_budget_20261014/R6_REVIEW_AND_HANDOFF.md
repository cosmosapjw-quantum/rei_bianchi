# OBSERVER15 R6: partial-cell repair and observable-projected event review

2026-10-14 KST. Selected stage R6, following actual R5 HANDOFF. Parent PR115 head4716c469535422ba6c293a26e3478cedd3923e6b. Decision: **ACCEPT_SCOPED_AFTER_REFERENCE_REPAIR**. Same-author new mathematical review plus exact arithmetic and actual CAS; external independent scientific review and native subagents NOT_RUN.

## Full executable payload

- `REI_OBSERVER15_R6_20261014_SOURCE.zip`,118296bytes,53members/52manifest payloads.
- SHA256 `a9f58bd894fffa84e623b7b05e70364d87595ccfe99ec5b279a1915c2eae518a`.
- [Full Korean derivation, original/repaired code, tests, inputs and raw evidence](https://drive.google.com/file/d/150oKyUVG7X1CmkeuWvFaq895SSLpxqDW/view?usp=drivesdk).
- Drive ID150oKyUVG7X1CmkeuWvFaq895SSLpxqDW, existing parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Actual create-only upload and ID/name/size/parent readback matched. Local CRC and all52payload hashes verified. Remote full restore and new Dropbox backup not performed.

This Git file is the substantive review and restore entrypoint. The runnable reference patch, full proof, exact source CSV and CAS outputs are in the immutable archive, not all expanded into this repository.

## 1. An actual R5 reference defect, now repaired

R5 `curvature_stencil` evaluates the partial-cell integral of `(u-l)(r-u)/2` using a subtraction of nearly equal normalized cubic terms. On the original cell[0,1], overlap[a,1], a=`0x1.ffffffffffffdp-1`, its upper coefficient was1.8488927466117464e-32.

For y=u(1-u)/2, endpoint interpolant0 and sup|y''|=1, the exact error is

`40532396646334455 / 1461501637330902918203684832716283019655932542976`

approximately2.773339119917619e-32. The original claimed upper coefficient is only two thirds of the exact required value. This is a real reference implementation defect, not a manufactured upstream failure. Its absolute scale is tiny; it does not overturn the separately computed R5 baseline certificate.

With p=a-l>=0, d=b-a>=0, q=r-b>=0, direct integration gives the positive identity

`C_ab = p*q*d/2 + (p+q)*d^2/4 + d^3/12`.

For nonnegative rate,decay, the weighted coefficient is bounded by `rate*exp(-decay*a)*C_ab`. The repair uses exact Fraction gaps, upward Decimal exponent/polynomial arithmetic, exp.next_plus, and an outward binary64 conversion. It retains the original cell endpoints for arbitrary overlap. Returning coefficients does not license an inward later multiplication/sum by a consumer.

The original regression actually failed with exit1; the identical command passed with exit0 after the repair. Original code, first error, green output and patch are preserved. Only the preexisting `curvature_stencil` function and Fraction import change in the task-local module; no native source changed.

## 2. Project the event onto the actual observable

For y'=f±, guard g=0, reset y+=R(y-,s), isolated transversal crossing nu=g_s+g_y f- !=0, the usual synchronized saltation is

`S=R_y+(f+ -R_y f- -R_s)g_y/nu`.

Attach I'=kappa(y,s), I+=I-. Direct augmentation yields

`S_aug = [[S,0],[(kappa+ -kappa-)*g_y/nu,1]]`.

Thus a preserved total electron current on the same ray gives zero instantaneous optical tangent row even if the state saltation has norm>1. Later source dynamics can still change a future optical integral. Use total free electrons, not the thermal-only census.

Signature(-+++), x0=ct, dx=c*k*ds, q=c grad(theta), u.q=1, D=-u.k, A=q.k>0. Optical weight is `c sigmaT N D/(V A)`. For varying tilt in a normal-slice homogeneous clock, theta=integral dt/Gamma(t), not t/Gamma(t). Actual xAct used beta(ct) and verified Gamma^2(1-beta*mu), total-current relabeling, separate spatial-current and divergence identities.

The new actual CR54 compact proof at e484feb7762f969dbe29b3116b886455baa14395 supplies the preserved-current versus amplified-state example. Its two-edge source-specific time/temperature/radius values are not imported into SHEAR12. HE42 R7's preserved D/A source contract remains active.

## 3. Continuous events still affect second order and interpolation

For a continuous family q-(s(eps),eps)=q+(s(eps),eps), write

`I(eps)=integral_0^s q- dt + integral_s^h q+ dt`.

With [q]=q+ -q-, direct twice-differentiated Leibniz and `[q_eps]+[q_t]s'=0` give

`I'' = integral q_eps_eps± dt + [q_t]*(s')^2`.

The coefficient of eps^2 therefore has `+[q_t]*s1^2/2`. The first NEW R6 expected-sign expression was wrong; actual Wolfram returned s1^2(-vminus+vplus). Correcting the expected coefficient and checking the same example plus Leibniz identity resolves it. This is a new R6 draft error, not an inherited R5 formula defect. Concrete q0=1,v-=0,v+=2,s=.5+eps,h1 gives exactly5/4-eps+eps^2.

For continuous piecewise-C2 source y with finitely many slope jumps, define

`G(u,s)=(min(u,s)-l)*(r-max(u,s))/(r-l)>=0`.

Since -G_uu=delta and endpoint G=0,

`y-Ly = -integral G*y''reg ds -sum [y']_j G(u,s_j)`.

Consequently, with K>=0 and |y''reg|<=M2,

`|integral_a^b K(y-Ly)| <= M2*C_K + sum |[y']_j| Q_ab(s_j)`,

where `C_K=integral K(u)(u-l)(r-u)/2 du` and `Q_ab=integral K(u)G(u,s)du`. For a whole constant-weight cell, Q=K0(s-l)(r-s)/2. y=|u-.5| saturates this extra term: error1/4 although regular curvature0. Split at the event or use a valid jump-location/magnitude bound. R5 explicitly required C2; its threshold-free baseline therefore needs no new event term. Do not double-count a term already in an event-aware cumulative response.

## 4. Same observer measure and shared source normalization

Read the actual frozen FA02 two-parameter derivation1-130 at BASS143 head2feae8c3a038bb08185835d7352b7df46e8fe81c. The physical observer cap is pulled to fixed labels, with its actual Jacobian/observable-weight cancellation. Retaining a fixed old normal-sky integral instead would change the measurement.

For a normalized pulled-back weight m=1+eps*m1+eps^2*m2,

`C=<mP>/<m>`,

`C1=<P1>+Cov(P0,m1)`,

`C2=<P2>+Cov(P1,m1)+Cov(P0,m2)-<m1>Cov(P0,m1)`.

R5's fixed-observer STF mean remains valid in its stated domain. Even with isotropic P0, a changing measure can contribute Cov(P1,m1). If the exact pullback already contains the measure, do not add it again.

Read actual HH60 PHYS27 R5_RESULT at c56cae5662a4c44b4f387699b5602355e63cb7dc. Its signed cumulative forcing uses a whole-tube source gap and retains electron birth time. For constant extra source q, deltaN(t)=qt and a bin[a,b] has wq(b^2-a^2)/2, not endpoint census times duration. No HH rate, P01 temperature or foreign sigma convention is substituted into SHEAR12.

Finally, for fixed Cn,CB>0 and shared r>=0,

`P(r)=exp(-tail-r*Cn)*(1-exp(-r*CB))`,

`P'(r)=exp(-tail-r*Cn)*((Cn+CB)*exp(-r*CB)-Cn)`.

The maximum is at `r*=log(1+CB/Cn)/CB`. On a shared-r interval compare both endpoints and the interior stationary point; the existing T/B outer box remains valid. For the displayed saved coefficients r*=90.07254836404260..., and synthetic tail.25 gives Pmax.05270239889512813.... This is a mathematical control, not a physical sigma-ratio choice.

## 5. Preserved science, actual checks, exact next action

Retain R5 source-free smooth baseline M2=.0425142592, interpolation/r upper1.771427466709e-9, and CSV SHA25669bceac64e356d202c4cc4cb8c3db35d9e37c632df7d37bc6219f7c53a696927. That rational certificate did not use the defective float helper. Source-node ODE error remains null; the existing exact declared-interpolant arithmetic is not nodal dynamics certification.

Actual new evidence:
- 41 named new arithmetic checks PASS, including one60-case binary-endpoint group and24exponential-overlap checks. Focused regression1 overlaps these; counts are not added as disjoint.
- Cloud Wolfram15.0.1:13main zero groups, one newly corrected main sign group, plus2supplementary zero relations. Original JSON failure, diagnostic InputForm result and sign repair are preserved; the final formatted replay script was not run as one fresh whole command.
- Actual remote Wolfram15.0.0/xTensor1.3.0/xCoba0.8.6:9new tensor/covariant-derivative zeros, exit0. Submitted WL SHA2560815824979382d5c86922748fea6bb11ed1b1e20826f3aacd2d3f6218a597820. Raw outputs were recovered and their hashes matched.
- One checker string-to-Fraction schema error was repaired without changing math. Shell stale-cwd and cloud pre-analysis warnings remain recorded.
- An inherited extreme-domain linear_weights(g~1e155) overflow diagnostic is deferred; it is outside selected fixture kh~.0006 and outside the repaired function. No whole-module all-domain certification is claimed.

No source ODE, inherited scientific suite, atomic campaign, native receiver, HPC, main merge or force push. CR/RCT/HH OFF and prior global DAG/owner/receipt status preserved. External independent review NOT_RUN.

**Next selected stage: R7_SAME_SOURCE_SAVED_NODE_RESIDUAL_BINDING.** Read REPORT_KO.md3-6, DECISION, SOURCE_MAP and HANDOFF inside the archive. Retrieve existing same-source nodal/signed residual evidence first; if absent, recover only the source state/definition needed to construct it. Keep r symbolic; the synthetic input reaches its actual fixture observer u=.5, so its missing tail is0. Physical EoR calibration is a separate task, not a new prerequisite for this synthetic certificate. Preserve completed R5/R6 and the corrected partial-cell bound.
