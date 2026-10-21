# SIGMA_PI_COMPONENT_PILOT_20261021 — matter/radiation addendum v1

2026-10-21 (Asia/Seoul). Latest explicit user steering: "\pi_ab는 matter와 radiation을 별도로 고려하고 싶어."
This addendum extends the first source-free LRS pilot with independent initial matter/radiation stress controls and component plots. It does not alter or rerun the completed original91+3 cases or their frozen contract/review/raw bytes.
Owned new implementation path: sigma_pi_pilot_20261021/components/. Original package files and their execution identity remain unchanged. Root Astra owns theory/contract, lower-tier authors/executes, independent Astra admits this exact contract before new IVPs and reviews the new diff/raw once afterwards.

## Physics and component conventions

All original metric, source cosmology/clock, physical kernel pin, solver, mass allocation and interpretation limits remain.
Matter means massive canonical Vlasov plus cold dust; dust anisotropic stress is zero. Radiation means gamma+nu. Lambda contributes no anisotropic stress.
pi_ab^m=diag(-p_m,-p_m,2p_m), pi_ab^r=diag(-p_r,-p_r,2p_r), p_r=p_gamma+p_nu.
Signed dimensionless P_m=sqrt6 kappa_t p_m/H², P_r=sqrt6 kappa_t p_r/H², P_total=P_m+P_r.
Component norms Pi_m=|P_m|,Pi_r=|P_r|,Pi_total=|P_total|; kappa_t=8piG/c² for SI energy stress.
Cross tensor pi_m:pi_r=6p_m p_r. Normalized cross is P_m P_r and Pi_total²=Pi_m²+Pi_r²+2P_m P_r.
Triangle/reverse triangle follow. Total stress cancellation does not imply isotropic species.
Separate source-free species continuity is dotrho_A+3H(rho_A+pbar_A)+6s p_A=0. No new numerical energy-residual PASS is introduced.

Keep common radiation W_r=1+kP2 and independent matter W_m=1+AP2.
At b_i=0, ai=1/21, H_i²=Href²/(1-Sigma_F,i²/6), initial energy normalization makes H_i independent of A,k.
Define
Q_M = [integral q^4 f_FD(q)/sqrt(M²+q²) dq] / [integral q² f_FD(q)sqrt(M²+q²) dq], M=30.
Use the exact finite positive quadrature of the unchanged source at each resolution to calibrate the physical component target.
p_m,i = rhoCrit0 fm Omega_m ai^-3 A Q_M/15.
p_r,i = rhoCrit0 Omega_r ai^-4 k/15.
K_m=(sqrt6/5)(H0²/H_i²)(fm Omega_m/ai³) Q_M.
K_r=(sqrt6/5)(H0²/H_i²)(Omega_r/ai⁴).
A=P_m,i/K_m and k=P_r,i/K_r. fm=.1, other matter remains cold dust.
At nominal24x12Gauss3, Q_M=.014042977679696454, K_m(Sigma0)=.000683609293237126 and K_m(.1)=.000682469944415064, from independently reviewed static quadrature. Source A domain[-1,2], radiation |k|<=.5 are retained.
Worst proposed |A|=.4395797975500973; W_m>=.5604202024499028. Worst |k|=.33548963507834245.
Refinement keeps the physical P_m,i,P_r,i fixed, recalibrating A for the refined quadrature. Do not silently switch to fixed-A refinement.

## Frozen finite-grid case set and reuse

Sigma_F,i = [0,.0003,.001,.003,.01,.03,.1].
Signed P_m,i = [-.0003,-.0001,0,.0001,.0003].
Signed P_r,i = [-.001,-.0003,0,.0003,.001].
Seven25point component planes =175 nominal points. These are signed aligned-LRS coordinates; save norms and signs separately.
35 points with P_m,i=0 have identical physical input and resolution to existing nominal trajectories. Reuse their exact original raw bytes and original execution receipts, with explicit original case ID+input/raw hashes. No new solver call for them. New addendum configuration metadata must not relabel historical executed code.
Only140 new nominal cases are allowed.
Only3 new refined corners: (Sigma,P_m,P_r)=(.1,+.0003,+.001),(.1,-.0003,-.001),(0,+.0003,-.0003). Refined L12,48x24,Gauss3; nominal L8,24x12,Gauss3.
Max newIVPs143, original94 already completed, overall scientificIVPs237. No retries or old trajectory repeats. No benchmark.

## Implementation and outputs

Keep original adapter.py,pilot.py,resources.py,vendor/ and original results byte-identical. New modules may import their stable functions or use a mechanically adapted controller under components/.
Caches include amplitude and complete grid/mass parameters; identical radiation/Einstein RHS and DOP853 call are preserved. Independent process workers, BLAS1, resource sharing policy remain.
Identity covers all new/actually imported code, exact vendor and dependency semantic versions. Reused35 references bind original code/source/input/raw identities explicitly.
New plan/run/check/plot accepts same resource/resume semantics; cumulative original debit persists. Never clone/worktree, change owner checkout, rootRust/.github, protected lanes or other processes.
Failure/partial outputs and attempts persist. No automatic retry, no alternate-directory budget reset.

Save per-epoch signed P_m,P_r,P_total and norms, SI stress coefficients and cross contraction, initial/endpoint CSV for all175. Radiation is signed gamma+nu before absolute value.
Also generate component-separated diagnostics for all91 original saved points without solver calls, labelled initial P_m=0 slice.
Required plots: independent (P_m,i,P_r,i) finite planes at fixed Sigma; distinct final matter/radiation values; selected opposite-stress cancellation trajectory from the actual saved arrays. Show actual computed samples and signs; no interpolated samples or fitted response surface. PNG/PDF and machine-readable CSV.
The exact equality P_total=0 at initial opposing stresses is not a preserved physical constraint and is not an isotropy control.

## Targeted validation and stopping rule

Contract PASS required before scientific runs.
Reuse prior kernel tests and CLOSED_PASS operational review. Add only tests for this changed risk: independent calibration including signs, forbidden amplitude, combined zero stress versus actual isotropy, reused35 identity, shared original debit, component aggregation/cross relation.
Total targeted mechanical time across original and addendum <=30s (prior .205s).
Allcase gates unchanged: finite,121epochs,endpoint,positiveH,nonnegativecanonical,number5e-11,positiveenergy,64-nodebrightness>=-1e-10. Add separate initialP_m andP_r mismatch<=5e-12 and sameSigma<=5e-12. Trueisotropy applies onlySigma=P_m=P_r=0 and reuses original control.
Do not apply old aggregate-total initialPi calibration to radiation alone or label cancellation isotropic.
Three refined endpoint gates: abs differences Sigma_F,P_m,P_r,b<=2e-6 and Hrelative<=2e-6. Record actual differences. No global continuum/error/convergence claim.
Independent reviewer reads new raw once, verifies original35 reuse and component formulas and plot labels; one bounded repair batch only for concrete findings if needed.

## Shared resource allowance, no budget reset

Same overall sandbox envelope across ORIGINAL+ADDENDUM: <=4workers (actualCPU/quota wins), percase30s, aggregate chargedchild<=240s, aggregate controller<=180s.
Prior scientific debit: child8.778983763986616s and controller2.720931695002946s. New controller must reserve these before dispatch; maximum remaining231.22101623601338s child,177.27906830499705s controller before new work.
Record olddebit,newcharge,total in receipts. Failed/incomplete attempts debit and stop preserved. No newrun on original35.
SameNCPprofile up to63single-threadworkers with actualaffinity/memory/idle/budgetminimum, reserve16GiB on128GB,0.5GiB/worker,case60s,overallchild1800s/controller1200s if needed. Completed sandbox outputs reused. No exclusivehostlock; unrelatedjobs untouched.
FreshDCmonthlycap is still explicit no-retry for that tool. User's separate report of full NCP root disk is a reason for actual df preflight in Codex, not permission to delete other work. This pilot needs only small files; no disk reconfiguration.

## Admission and delivery

Original91+3scientificPASS remains valid. Component175point result is PRELIMINARY_PENDING_REVIEW until independent diff/raw admits it.
Nativeage/timeHOLD, nonlinearGrackleresponseNOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.
Separatecomponentstressknobs remain within fixed axisymmetric species family, not general non-LRS tensor orientations, baryonic viscosity, nativeHHe/UV or observational inference.
Post-review expected-headFF at actualremoteparent only, PR199draft,no merge/no force-push. Final dual-provider bundle includes both original and component sources, allraw, plots, contracts/reviews and exact reuse map. No user manual file handling.

