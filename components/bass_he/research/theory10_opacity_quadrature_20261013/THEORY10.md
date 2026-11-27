# THEORY10: positive affine-abundance optical-depth quadrature

Unit: `HERE_RUX03_AFFINE_ABUNDANCE_OPACITY_QUADRATURE_10`. Date: 2026-10-13. Workflow: actual `physmath-research-loop` 1.1.0, release `pluginrel_6acdfbbb29408191b5751b2a99dfc1dd`.

Status: **derived and symbolically checked; independent review pending**. This is a documentation/theory change. Production chemistry, ODE and stage implementations are unchanged. THEORY08/09 complete original archives and their verified recovery identities are linked in `../theory08_09_recovery_20261013/RECOVERY_INDEX.md`.

## Result

On the same two exact BE source stages of length at most 5e8 s each, replace endpoint optical-depth quadrature by a positive weighted endpoint-current rule. Electron abundance is exactly affine on the conservative-state reconstruction. The full primitive velocity is generally nonlinear, and its deviation is bounded by the inherited first-derivative certificate.

The new quadrature error budget is **6.84621626429555762458e-15**, compared with the prior endpoint budget 3.40019921930598713366e-11. The unchanged temporal reconstruction budget is 1.99439491560918853831e-12, giving a total bound **2.00124113187348409593e-12**. These are proved sufficient error-budget ratios: approximately 4966.54 for quadrature and 17.987 for the total. They are not measured error or runtime ratios.

## Assumptions

Use signature (-,+,+,+), fixed Eulerian tetrad, conserved D=gamma*n_H=1e-3 cm^-3, common gas velocity, f=2/25, and the retained FT03 CI3/RR3/DR2/photo plus Case-A kinetic/binding escape source. Geometry, external photon injection and CR/RCT/HH are zero in this chosen source problem. The six lab rays and previous gas/photon input family are unchanged. This unit concerns the same passive cold-Thomson observable.

The physical cube Q=[-1,1]^7 contains each conservative reconstruction segment. For electron abundance e=zeta1+zeta2+2*zeta3, use e_min=139/250, e_max=141/250, L_e=1/250, L_beta=3e-6 in the infinity-to-Euclidean norm, and ||Delta X||<=h*m_X with m_X=162307/1e14 s^-1. The predecessor source pins are BASS_HE PR35 commit 670496dbbee5c19f3eb6c5759018cf284e4a3bae and rei_bianchi PR114 commit a5c958c414dea41216b445c05f58df837f05cacb.

## Constructive rule

Let X(theta)=(1-theta)X0+theta*X1, theta in [0,1]. Composition is affine, hence e(theta)=e0+(e1-e0)theta exactly. Write beta(theta)=beta(X(theta)), kappa=c*sigma_T*D, and a fixed unit lab direction ell. Then the exact reconstruction optical depth is

`tau_hat = kappa*h*Integral[e(theta)*(1-beta(theta).ell), {theta,0,1}]`.

Set w0=(2e0+e1)/6 and w1=(e0+2e1)/6. Exact integration of affine abundance times endpoint-linear velocity gives

`Q_L = kappa*h*((e0+e1)/2 - (w0*beta0+w1*beta1).ell)`.

Equivalently,

`Q_L = h*(chi0+chi1)/2 + kappa*h*(e1-e0)*(beta1-beta0).ell/6`.

Both weights are positive and sum to (e0+e1)/2. The weighted mean velocity is a convex combination of subluminal endpoint velocities. Therefore the integrated surrogate electron current is future timelike for h>0, and Q_L is positive for every unit ray. Its monopole is exact on the reconstruction, and

`Q_L(ell)+Q_L(-ell)=kappa*h*(e0+e1)`.

The rule uses existing endpoint primitives only. No additional source or interior primitive evaluation is required once the endpoint data exist.

## Proof of the nonlinear-velocity error certificate

For b(theta)=beta(theta).ell, define db=b1-b0, S=e0+e1, de=e1-e0, K=L_beta*||X1-X0||. The chain rule gives Lipschitz constant K. For K>0, r=db/K lies in [-1,1]. Pointwise extremal envelopes are

`b_plus=min(b0+K*theta,b1+K*(1-theta))`,
`b_minus=max(b0-K*theta,b1-K*(1-theta))`.

Their intersections are (1+r)/2 and (1-r)/2. Since e is positive, their weighted integrals bound the actual weighted integral. Integrating the four polynomial pieces yields center and radius

`Ic=S*(b0+b1)/4 + de*db*(3-r^2)/24`,
`RI=S*K*(1-r^2)/8`.

The endpoint-linear weighted moment is `IL=S*(b0+b1)/4+de*db/12`. Consequently

`|tau_hat-Q_L| <= kappa*h*K*(1-r^2)*(S/8+abs(de)*abs(r)/24)`.

With a=S/8>0, b=abs(de)/24 and t=abs(r), the identity

`a+b^2/(4a)-(1-t^2)*(a+b*t)=a*(t-b/(2a))^2+b*t^3 >=0`

proves the uniform all-direction radius

`E_Q,j <= kappa*h*K*(S/8+de^2/(288*S))`.

For K=0 use the exact constant-velocity branch. If |db|=K, the scalar path is forced to be affine and the cone radius is zero. Equal endpoint projections admit tent functions attaining the scalar-class radius S*K/8. The physical source-generated velocity class is smaller; no sharpness for that smaller class is asserted.

The direction-specific center Ic contains a cubic directional term. Use it as an interval center for a requested ray. The principal current rule Q_L retains its monopole-plus-dipole form.

## Uniform evaluation and optional panels

For two steps h_j<=H=5e8 s, the preceding inequality gives

`E_Q <= A0+A1`,
`A0=kappa*L_beta*e_max*m_X*H^2/2`,
`A1=kappa*L_beta*L_e^2*m_X^3*H^4/(288*e_min)`.

Actual exact arithmetic gives A0=6.84621466669347756826e-15 and A1=1.59760208005631322355e-21. Numerical conversion uses the inherited CODATA-2022 central model value sigma_T=6.6524587051e-25 cm^2 and exact c=29979245800 cm/s; all dimensional bounds scale with the chosen sigma_T. Constant uncertainty is separate from numerical error.

The triangle inequality combines E_Q with the inherited THEORY09 temporal bound. At the full 1e9 s horizon the resulting relative total bound is below 0.0190%, using the inherited positive optical-depth lower bound.

If each existing segment is split into n equal quadrature panels and primitives are recovered at the n-1 new interior conservative states, then

`E_Q(n)<=A0/n+A1/n^3`.

For n=1,2,4,8 the quadrature bounds are approximately 6.84622e-15, 3.42311e-15, 1.71155e-15, 8.55777e-16. At n=1 the quadrature budget is already less than E_time/250. Prefer that setting until an actual requested tolerance needs additional panels. Subdivision does not change the source steps or their temporal order.

## Evaluation and verification contract

Return the integrated monopole/dipole current, each requested ray value, a rigorous radius, and actual input/roundoff enclosures. For endpoint errors epsilon_e and epsilon_beta within a common positive/subluminal hull, rule perturbation is bounded by

`kappa*h*((1+beta_max)*epsilon_e+e_max*epsilon_beta)`

plus arithmetic error. Keep that contribution distinct from source residual error already included in the inherited temporal certificate. Exact or interval consistency must establish |db|<=K; do not clip an inconsistent input to pass the guard.

Discriminating cases: zero step; constant beta; affine e and beta with the signed trapezoid correction; positive weights and antipodal sum; scalar tent and smooth quadratic curved paths; saturated endpoint slope; interval/roundoff enclosure; fixed reconstruction under panel refinement.

## Actual execution and epistemic status

Online Wolfram 15.0.1 completed four cone checks. Subsequent scientific calls failed with 502/network errors, so the same short requested work used the connected research PC's existing Wolfram Engine in an isolated /tmp directory. No package installation or production repository mutation was performed on that PC.

A first local certificate had an AssociateTo arity error and registered only 8 of 18 checks despite all_pass=true and shell exit 0. That incomplete execution was not admitted. Its input/output/log are preserved. The corrected wrapper requires the expected check count as well as all_pass. The final certificate returned 18/18 True and exit 0. The separate actual xAct run returned 8/8 groups and all 9 tensor residuals zero, exit 0. Final named groups total 30; earlier overlapping/incomplete checks are excluded.

Local kernel: Wolfram 15.0.0, xTensor 1.3.0, xPerm 1.2.4, pure-Wolfram canonicalization. Actual loaded xTensor.m SHA256: 04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Raw remote source/results/stdout were recovered in a manifest-verified archive (SHA256 70b9cb0fb78e5005b00bdbe0c87bfa48e0da8bde04b7c924c04fac4e5cb77829).

The complete archive includes the full derivation, exact scripts, failures, raw remote outputs, coding contract and state record. Independent review, native source/stage execution and observed optical-depth values are pending. Parent scientific statuses are unchanged.

## Literature and next action

SciSpace and Exa identified S. S. Dragomir, A weighted Ostrowski type inequality for functions with values in Hilbert spaces and applications, JKMS 40(2),207-224 (2003), DOI 10.4134/JKMS.2003.40.2.207. Metadata and abstract were inspected, not a full-text theorem. No uninspected theorem is imported; all required inequalities are proved above. No novelty-priority claim for scalar Lipschitz cones is made.

Primary records: https://vuir.vu.edu.au/2420/ ; official xAct https://xact.es/download.html ; constant model https://physics.nist.gov/cuu/Constants/Table/allascii.txt .

Next: connect actual shared-provider endpoint primitives and true residuals to this rule. Further theory should target the now-dominant observable temporal error or time-step allocation. Existing PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04, MOVING_GAS_STAGE_05, CERTIFICATE_ADAPTER_06, original RUX02/global RUX03 -> RUX04 -> RUX05 and separate all-Bianchi/D2.3 obligations remain unchanged.
