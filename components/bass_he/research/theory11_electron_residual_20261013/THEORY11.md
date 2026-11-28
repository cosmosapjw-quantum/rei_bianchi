# THEORY11: signed electron-event residual correction for optical depth

Unit: `HERE_RUX03_ELECTRON_RESIDUAL_OPACITY_CORRECTION_11`.
Date: 2026-10-13. Status: **derived / symbolically checked; independent scientific review pending**.
This document gives the complete compact argument. The evidence index links the full Korean proof, exact returned values, predecessor inputs, replay sources and execution record.

## 1. Same physical model and preserved authority

Parent THEORY10 commit: `5330be9ffdbc8dd093928a6585f6e426a20d8429`; parent06 real-function bounds: `3932669f7904f7f68f2f07dced4cf1da9d472480`; receiver PR114: `a5c958c414dea41216b445c05f58df837f05cacb`.

Keep signature (-,+,+,+), fixed Eulerian tetrad and D=gamma*n_H=10^-3 cm^-3, f=2/25, common gas velocity, the original warm primitive domain and mass-energy parameter family. The full retained source is FT03 CI3/RR3/DR2/photo with Case-A kinetic and binding escape. External birth, geometry evolution and CR/RCT/HH are zero in this selected source problem. Lab photon directions/energies are (23,+/-ex),(35,+/-ey),(70,+/-ez) eV; epsilon_eV*E=hbar*omega. The thermal EOS and explicit c,k_B follow the parents.

There are two exact BE steps h1,h2<=H=5e8 s, total T<=2H. Gas X belongs to the same affine conservative cube Q=[-1,1]^7; composition coordinates have scale 10^-3. Initial ||X0||_infinity<=.01, initial v_q in [.99,1.01], and p_q=p0_q*v_q with p0_q=.01 unchanged throughout. The source ODE is Y'=F(Y)=(g(X,v),-Lambda(X)*v), Y=(X,v). Use the linear reconstruction Yhat of both gas and lab photon inventories between the same endpoints. Do not reapply photon elimination at interior reconstruction points.

The parents prove the discrete roots, continuous-flow containment, and Q-wide bounds. Source and observable model uncertainty remains distinct from discretization/evaluation error. Thomson opacity is the same passive cold-electron diagnostic.

## 2. Project events before taking absolute values

Let zeta=(x_HII,f*x_HeII,f*x_HeIII), e=zeta1+zeta2+2*zeta3. Ionization columns are nu0=(1,0,0), nu1=(0,1,0), nu2=(0,-1,1). Therefore (1,1,2).nu_i=1 and

    g_e = de/dt = sum_i(photo_i+CI_i-RR_i)-DR1-DR2.

The reverse HeIII edge (0,1,-1) removes one electron, not three. Retain temperature, closure, velocity and opacity derivatives in every rate.

The parent's first two chemical rows are nonnegative absolute event majorants. The HeII row counts the HeI and HeII edges once each. Thus, from the same source-pinned rational values,

    |g_e| <= b_e = U*10^-3*(b1+b2),
    ||g_e,X||_1 <= a_X = U*10^-3*(ell01+ell02),
    ||g_e,v||_1 <= a_v = sum_iq p0_q*lambda_bar_iq,  U=1.01.

The exact inputs are in the retained parent06 JSON. Their returned values are:

- b_e = 1.916608195898998008e-12 s^-1;
- a_X = 5.9541028002204625188896e-14 s^-1;
- a_v = 1.6140488971997208e-12 s^-1.

## 3. Exact signed time-moment identity

Define r_e(t)=d(ehat)/dt-g_e(Yhat(t)). For the same initial condition, z=e(Y)-ehat obeys z'=g_e(Y)-g_e(Yhat)-r_e, z(0)=0. Fubini gives exactly

    integral_0^T z dt = -R_e+G_e,
    R_e = integral_0^T (T-s)*r_e(s) ds,
    G_e = integral_0^T (T-s)*(g_e(Y(s))-g_e(Yhat(s))) ds.

R_e is signed and has units seconds. The weight is time remaining to the global horizon. Resetting the weight independently per step loses r0*h1*h2 for a constant test residual r0.

## 4. Bound the remaining coupling without a Hessian

Reuse B=1607/10^12, L=281/6250000000000, Lambda_bar=4727/10^14 and L_Lambda=3/5000000000000, all s^-1. The absolute derivative and dissipative error comparison matrices are

    A=[[U*L,B],[U*L_Lambda,Lambda_bar]],
    C=[[U*L,B],[U*L_Lambda,0]],
    m=(U*B,U*Lambda_bar), a=A*m, Rstar=(I-2H*C)^-1>=0.

Parent09 supplies E(t)=(||X-Xhat||,||v-vhat||), with E(t)<=Rstar*integral_0^t |r(s)|_block ds and |r(tprev+s)|_block<=(h-s)*a. It has already proved physical containment by a first-exit argument.

Integrating once and twice yields

    I1=integral E dt <= Rstar*a*7H^3/6,
    I2=integral (T-t)*E(t) dt <= Rstar*a*5H^4/6.

For a general partition the second scalar factor is

    sum_j [(T-tprev)^2*h_j^2/4-(T-tprev)*h_j^3/6+h_j^4/24].

It comes from integral_0^h (T-tprev-s)^2*(h-s)/2 ds. For two steps the expression increases with each nonnegative step size; at h1=h2=H it equals 5H^4/6. Thus |G_e|<=a_X*I2_X+a_v*I2_v. Numerically the enclosing vectors are

    I1=(2.38003889396995148e7,486978.138676624573) s,
    I2=(8.50013890703554099e15,1.73920763813080205e14) s^2.

## 5. Correct a common integrated current

Set beta_star=(0,0,41/841), kappa=c*sigma_T*D and H_e(Y)=e(Y)*(beta(Y)-beta_star). The parent Q-wide bounds give

    e in [.556,.564], L_e=.004, L_beta=3e-6,
    |beta-beta_star|<=3e-6,
    Lip(H_e)<=3e-6*L_e+.564*L_beta=1.704e-6=:L_H.

For a fixed unit lab ray ell,

    chi(Y)-chi(Yhat)=kappa*(1-beta_star.ell)*z
                    -kappa*(H_e(Y)-H_e(Yhat)).ell.

Let Q10 be the unchanged positive endpoint-current quadrature with certified radius E_Q from THEORY10. Define

    Q_c(ell)=Q10(ell)-kappa*(1-beta_star.ell)*R_e.

Then

    tau-Q_c = (tauhat-Q10)+kappa*(1-beta_star.ell)*G_e
              -kappa*integral(H_e(Y)-H_e(Yhat)).ell dt.

Hence the all-ray remainder is

    |tau-Q_c| <= E_Q+E_rem,
    E_rem=kappa*((1+|beta_star|)*(a_X*I2_X+a_v*I2_v)+L_H*I1_X).

Using the same specified CODATA-2022 central sigma_T model as the parents gives E_rem=1.72659121219172618e-14, E_Q=6.84621626429555762e-15, and E_rem+E_Q=2.41121283862128195e-14. All dimensional bounds scale with sigma_T/sigma_0.

With n.n=-1 and u_star=gamma_star*(n+beta_star), the integrated number current is

    J_c=J10-c*D*R_e*(n+beta_star)=J10-c*D*R_e*u_star/gamma_star.

Contraction with -sigma_T*(n+ell) gives the correction above. All rays share one scalar R_e; the monopole/dipole form is preserved. The antipodal correction is -2*kappa*R_e. This passive estimator does not alter gas/photon source states or event conservation.

For positive horizon, Q10>=kappa*.556*.95*T. With a_e below, |R_e|/T<=a_e*H^2, so the correction is strictly smaller than this margin; the corrected integrated current remains future timelike. Zero horizon gives zero current.

## 6. Immediate improvement even without evaluating R_e

On each reconstruction segment, r_e is Lipschitz with

    a_e=a_X*m_X+a_v*m_v=1.73698308603875371244e-22 s^-2.

At the right endpoint of an exact BE segment r_e=0. Thus |R_e|<=a_e*7H^3/6=25331.0033380651583 s. It follows that the SAME uncorrected Q10 has

    |tau-Q10|<=E_Q+E_rem+kappa*(1+|beta_star|)*|R_e|
             =5.53931547026933391e-13 <5.540e-13.

This strengthens its prior 2.00124113187348410e-12 sufficient budget without a new source evaluation.

## 7. A constructive signed integral and its certificate

Use n equal midpoint panels in each original segment, d_j=h_j/n, retaining global T-t:

    R_e^(n)=sum_jk d_j*(T-t_jk)*r_e(t_jk).

For a panel midpoint m and length d,

    integral_panel(T-t)*|t-m|dt=(T-m)*d^2/4.

Since |r_e'|<=a_e almost everywhere within an original step, summing gives

    |R_e-R_e^(n)|<=a_e*(H/n)*T^2/8<=a_e*H^3/(2n).

The complete bound is E_n=E_Q+E_rem+kappa*(1+|beta_star|)*a_e*H^3/(2n).

| n per stage | Read-only event evaluations for two stages | E_n |
|---:|---:|---:|
| 1 | 2 | 2.51177593518e-13 |
| 4 | 8 | 8.08784946692e-14 |
| 8 | 16 | 5.24953115277e-14 |
| 16 | 32 | 3.83037199570e-14 |
| 32 | 64 | 3.12079241716e-14 |
| 64 | 128 | 2.76600262789e-14 |

For n=16 the outward ceiling is 3.831e-14 and the parent's budget/new budget ratio is 52.2466521299469. These compare proved budgets, not observed errors or runtime speedups. The 32 actual full-source samples and the corrected physical tau value have NOT been executed in this theory unit.

For exact BE steps the positivity margin above also survives the midpoint error: its per-time bound is a_e*H^2/(4n). Read-only samples do not require a new nonlinear stage or an adjoint ODE.

## 8. Inexact inputs and discriminating tests

For actual endpoints use r_e=d(ehat)/dt-g_e(Yhat) with the true source and its evaluation enclosure. Update I1 and I2 from the actual full residual under parent09, and use the actual segment slopes in a_ej. If initial electron values differ, add T*z(0) to the exact identity. A scalar residual sample error eta_r contributes at most kappa*(1+|beta_star|)*eta_r*T^2/2. Keep primal residual, Q10 quadrature, signed-residual quadrature and arithmetic errors separate without double counting.

Manufacture: v'=-lambda*v, e'=lambda*v, v0=1 and constant beta. With z=lambda*h, two equal steps have v1=(1+z)^-1, v2=(1+z)^-2 and R_e/h=-z^2*(5v1/6+v2/3). In units kappa*h, the true-minus-Q10 error is 7z^2/6-7z^3/3+O(z^4), whereas true-minus-Qc is -5z^3/6+7z^4/5+O(z^5). This checks the sign and horizon weight. The general fixed-horizon result here is a quantitative first-derivative bound; global second-order BE convergence is not asserted.

Mandatory implementation tests: one-electron HeIII RR counting; global rather than reset horizon weights; signed correction; actual current photons at interior points; full primitive feedback; all-ray current identity and positivity; residual evaluation errors; exact expected check registry/count.

## 9. Actual execution, provenance and remaining work

Cloud Wolfram evaluator calls: three. First certificate returned 17/18 True; E17 used unsimplified symbolic equality. A second call confirmed the same integral residual with FullSimplify as zero and passed eight additional scalar tests. Intermediate limit warnings and unevaluated example display strings are preserved. Actual xAct passed eight groups with ten zero tensor residuals. Distinct resolved named targets: 18+8+8=34.

The xAct result's unqualified kernel metadata resolved to the package version rather than System`$Version. It is not used as kernel metadata. The scalar runs returned Wolfram Language 15.0.1; actual xTensor was 1.3.0 with official archive SHA256 7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be and xTensor.m SHA256 04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36.

Stored online results are selective normalized transcriptions, not raw transport bytes. Portable replay scripts are reconstructed readable equations, not claimed original submitted byte strings; those replay files were not separately executed. No independent reviewer, native chemistry/stage solve, ODE trajectory or actual midpoint source samples were run.

Pierce & Giles (2000), SIAM Review 42(2),247-264, DOI10.1137/S0036144598349423, section2 p250, provides the signed adjoint-residual correction framework; author-hosted text and page image were inspected: https://people.maths.ox.ac.uk/gilesm/files/sirev00.pdf . The current derivation uses the explicit approximate adjoint kappa*(1-beta_star.ell)*(T-t)*grad_Y(e), with omitted coupling bounded directly above. Its cited paper's superconvergence assumptions are not imported. Residual background: Kehlet & Logg, https://arxiv.org/abs/1504.06765 . Actual package: https://xact.es/download.html .

Next execution: bind actual shared-provider endpoints and 32 read-only electron-event samples to this residual-aware observable certificate. Native PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04, MOVING_GAS_STAGE_05, CERTIFICATE_ADAPTER_06, reviews08-11, original RUX02+global RUX03 -> RUX04 -> RUX05 and separate all-Bianchi/D2.3 obligations remain unchanged.
