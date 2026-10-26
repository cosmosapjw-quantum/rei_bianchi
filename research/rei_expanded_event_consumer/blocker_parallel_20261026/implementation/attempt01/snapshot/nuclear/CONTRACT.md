# Frozen nuclear beta transfer coding contract — 2026-10-26

Author: nuclear_blocker26 (theory). Independent admission: pending review26. Source authority: AGENTS_CURRENT.md; unchanged WU PR150 HEAD 87933da5654bb2e4d93f7de4341df5e0fa0f8716 confirmed by authority26. No change to central DAG or source rate admission.

## Owned scope and execution controls

Implement under pilot/blocker_parallel_20261026/implementation only, after root authorization. Standard-library scalar functions, no IVP, no NumPy/SciPy, no network, no empirical defaults, no canonical solver edits. Preserve old files. Root owns cumulative timing: planning 9.689830337/10 CPU s; main 595.225063/600 CPU s; NO_MORE_IVPs. This contract grants no new allowance. Write source and tests first; do not import/execute until root GO. STOP on ambiguous state convention or substantive failed acceptance; return to theory/root.

## Exact declared-input operator

Use proper seconds h >= 0; isotope numbers per fixed Href (or comoving counts), never number densities without an expansion term. All scalar inputs P0, source s, beta rate lambda, competing destruction kappa must be explicitly supplied, finite, nonnegative; missing kappa is an error, while explicitly supplied kappa=0 is an admissible declared scenario. Rates are inverse proper seconds, source counts per second. Freeze source and rates over this one map. T denotes tritium, never temperature.

Define k=lambda+kappa, x=k*h, E=exp(-x), A=h*phi1(-x), C=h*h*phi2(-x), with phi1(-x)=(1-exp(-x))/x and phi2(-x)=(x-1+exp(-x))/x^2. At x=0, phi1=1 and phi2=1/2. Reject nonfinite derived k, x, A, C or outputs rather than silently clipping.

P1=E*P0+A*s; I=A*P0+C*s; B=lambda*I; R=kappa*I.

Return P1, integrated_parent I, beta_events B, competing_removals R. I has count*time units. B and R are event counts. B/R are event counters, not species assignment for unspecified competing reactions. Exact conservation: P1+B+R=P0+s*h. beta daughter, emitted continuum-electron, and antineutrino counters each increase by B in the declared continuum branch. No heat, electron spectrum, ionization or cosmic source normalization is produced.

Stable evaluation: h=0 exact return; for 0 <= x <= 0.1 evaluate phi1=sum_{j=0}^{10}(-x)^j/(j+1)! and phi2=sum_{j=0}^{10}(-x)^j/(j+2)! (finite fixed series, no adaptive search). Remainders at x=0.1 are < 0.1^11/12! and <0.1^11/13!, respectively. For x>0.1 use m=-expm1(-x), phi1=m/x, phi2=(x-m)/(x*x); avoid x*x overflow using phi2=(1-m/x)/x. Return E=exp(-x). This yields positive phi1,phi2 for the permitted scalar domain. Do not clamp negative input/results to hide an error.

## Jacobian scope

Return exact derivatives of outputs (P1,I,B,R) with respect to inputs (P0,s), with h,lambda,kappa held fixed:

[[E,A],[A,C],[lambda*A,lambda*C],[kappa*A,kappa*C]].

No rate/clock Jacobian is required. Document this explicitly. A coupled network RHS uses J=sum_r nu_r grad(v_r)^T; for beta r, grad(v_r)=lambda_r e_parent. For full map with unchanged product components, each product's own-state derivative is 1 and its parent derivative is lambda*A. Source and rate dependence on network state require extra chain-rule terms and are outside this frozen map.

## Stoichiometry and physical conventions

Optional constant data only: state=(n,p,T,He3,e_minus,antinue), nuclear isotope counts and continuum beta branch. n column=(-1,+1,0,0,+1,+1); T column=(0,0,-1,+1,+1,+1). Baryon row=(1,1,3,3,0,0); bare nuclear charge row=(0,1,1,2,-1,0); electron lepton row=(0,0,0,0,1,-1). Each row times either column is exactly zero. This bare continuum count basis must not claim that a neutral-laboratory tritium half-life or a bound-state beta branch supplies its physical rate. Neutral T with retained spectator electron produces He3+ plus emitted electron; bare T continuum produces He3++ plus electron; bound-state beta emits no free electron and has a different ionic daughter. These are separate branches.

Do not change electron density twice: emitted-electron count is event bookkeeping; the eventual owner must choose explicit electron evolution or charge-neutrality reconstruction. No thermal electron increment is implied by a freshly emitted fast electron.

## Required finite tests (root-controlled execution)

1. Zero duration: h=0 with P0=2,s=3,lambda=4,kappa=5 gives unchanged parent and zero integral/events.
2. Zero rates: h=2,P0=3,s=5,lambda=kappa=0 gives P1=13,I=16,B=R=0; Jacobian [[1,2],[2,2],[0,0],[0,0]].
3. Pure decay: h=1,P0=2,s=0,lambda=1,kappa=0 gives P1=2/e,B=2*(1-1/e),R=0.
4. Finite source and competing removal: h=2,P0=3,s=5,lambda=0.2,kappa=0.3. Check conservation and B/R=lambda/kappa. Split h into 0.75+1.25 and check map composition with same source/rates; sum both integrals/events.
5. Small and stiff x: h=1,P0=1,s=2; (lambda,kappa)=(1e-12,0),(0.03,0.07),(1,0),(1000,0). Check nonnegative outputs and conservation; x=1000 exp underflow is valid.
6. Analytic state/source Jacobian via linearity differences (unit increments), not noisy tiny finite differences. Check all entries against output differences.
7. Exact integer baryon/charge/lepton null rows; zero/tiny initial parents with s=0 remain zero; source-driven zero parent becomes positive for s>0 and h>0.
8. Reject missing rates, negative inputs, NaN and infinities. Explicit lambda=kappa=0 must work.

Acceptance: exact equality for prescribed integer invariants and zero branches. Otherwise absolute residual <= 5e-13*max(1, sum of absolute compared terms), including composition/Jacobian. This is floating implementation validation of a closed form; it does not replace project's physical tolerances. No empirical-rate or cosmic-observable tests. Tests may be written but remain NOT_RUN until a root-budgeted command is authorized. Fresh reviewer receives source plus raw results before any admission.

## Data qualification ceiling

Measured-input anchors are evidence only, not module defaults: UCNtau 2021 tau_n=877.75 s (mean lifetime, stat 0.28 s, syst +0.22/-0.16 s; doi:10.1103/PhysRevLett.127.162501); NIST Lucas/Unterweger 2000 tritiated-water evaluated t_half=4500±8 days (doi:10.6028/jres.105.043). lambda_n=1/tau_n; lambda_T=ln(2)/t_half. Standard day=86400 s. T charge-state and bound/continuum branch qualification is required for physical use. No numerical Q or deposited fraction is introduced.

### Branch clarification (theory source completion, no API change)

The continuum qualification applies also to neutron beta: bound-state n→H+antinue yields a neutral hydrogen atom with a bound electron. A total experimental neutron disappearance rate is not identically the continuum event rate without an explicit branch approximation or qualified branching fraction. If separately modeling a continuum rate lambda_c and bound rate lambda_b, use k=lambda_c+lambda_b+other_loss, B_c=lambda_c*I and B_b=lambda_b*I, with distinct daughter columns; the present scalar API represents B_c=lambda*I and places the explicitly supplied other loss channels in kappa until their products are separately mapped. Faber et al., PRC80,035503(2009), https://arxiv.org/abs/0906.0959, supports the distinction. Do not insert the historical theoretical branching number as a new empirical default. Isotope-H count and free proton/electron counts are different observables.
