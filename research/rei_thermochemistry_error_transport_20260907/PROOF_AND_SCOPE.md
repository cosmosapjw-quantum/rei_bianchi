# Conservative population substeps: what contracts, and what does not

Task layers: research/derive, exact-reference computation, review. This is a new conditional research result and verification oracle, NOT a replacement chemistry solver, production regression of the existing MPRK code, or first-interval admission.

## Source basis and status before this work

Base REI commit: `54a879231c68734fdda6990d67d8458d2918943e`, tree `29c406032a99d335ac52f866460e9b47ea42463b`.

`docs/science/current_00_READ_FIRST.md` describes a historical four-site FLRW microstep, keeping `population_t0`, `population_t1_predictor`, `thermal_tgamma`, and `thermal_t1_final` independent. It identifies stoichiometry/MPRK column sums and structural ledgers as conservation evidence. That file's historical authorization wording is NOT current production authorization; AGENTS.md withholds the first canonical interval. No old numerical certificate was rerun here.

The newly published XZ repair is a separate completed dependency result: the base's `XZ_INDEX_REPAIR_WORK_UNIT.json` records two valid streams (first uncompressed size 4225206, trailing empty stream 32 compressed bytes), 16 XZ methods, 18 donor, 15 member, 7 compatibility and 5 join methods, and one changed-source real GCC member result. Executed source is `744f684367375e546a30ce4d672d39cda50a0e18`; the base commit publishes the result. This is local execution evidence read remotely, not a fresh local run in this conversation. GCC authentication does not close all providers, installed paths, ELF/Rust closure or physics.

The scientific question addressed here is narrower and useful independently of host recovery: does positivity plus elemental conservation suffice to prevent uncertainty amplification when population rates depend on state and thermal/radiation inputs? The answer is no. A frozen-generator bound and an explicit nonlinear counterexample are derived below.

## 1. Definitions, units and assumptions

Use proper time t in seconds; Delta t >= 0. A is a finite real transition generator acting on a COLUMN vector u:

    du/dt = A u,     A_ij >= 0 (i != j),     w^T A = 0,

with fixed positive weights w_i and W=diag(w). Define ||u||_(1,w)=sum_i w_i |u_i| and ||B||_(1,w)=||W B W^-1||_1. A has units s^-1; Delta t*A is dimensionless. No natural-unit convention is introduced. If an existing geometric code uses c^-1 d/dt, its rate conversion must be mapped separately, not silently dropped.

For the H charge states (HI,HII) with frozen ionization/recombination rates a,b >= 0:

    A_H = [[-a, b], [a, -b]].

For helium charge states (HeI,HeII,HeIII) with frozen adjacent-transition rates a1,b1,a2,b2 >= 0:

    A_He = [[-a1, b1, 0], [a1, -(b1+a2), b2], [0, a2, -b2]].

These are an explicit mathematical subsystem, not an assertion that this is the complete REI production operator. For normalized elemental fractions each block sums to one. Fixed per-element weights may normalize their combined weighted mass M to one. Free electrons, photon groups, temperature and energy are not additional closed Markov populations in this argument. Rates may depend on them, but that dependence is frozen only for the first theorem.

No detailed balance, irreducibility or strictly positive rates is required. The domain excludes negative rates and time steps. Extra reactions are allowed only if the same sign and conserved-positive-weight hypotheses remain true. External sources/sinks, expansion dilution in proper densities, variable weights, charge exchange between blocks, event switches, and higher-order stage assembly require an explicit additional derivation.

## 2. Frozen resolvent theorem

Let P_A=(I-Delta t*A)^-1. Then for every Delta t >= 0:

    P_A >= 0,     w^T P_A = w^T,     ||P_A||_(1,w) = 1.

Consequently ||P_A u-P_A v||_(1,w) <= ||u-v||_(1,w).

Proof: transform Abar=W A W^-1. It is Metzler and has zero column sums. Put lambda=max_j(-Abar_jj). If lambda=0, all off-diagonal entries vanish by column conservation, so A=0 and P_A=I. Otherwise S=I+Abar/lambda is nonnegative and column stochastic. With r=Delta t*lambda/(1+Delta t*lambda) < 1,

    (I-Delta t*Abar)^-1 = [1/(1+Delta t*lambda)] sum_(k>=0) r^k S^k.

The series converges in induced 1-norm. Every summand is nonnegative, and each column sum equals the scalar geometric sum, which is one. Similarity back by W proves the claims. This is nonexpansion, not strict contraction: conserved modes prevent a strict full-space norm less than one.

For hydrogen specifically, d=1+Delta t*(a+b)>0 and

    P_H = (1/d) [[1+Delta t*b, Delta t*b],
                 [Delta t*a, 1+Delta t*a]].

The analytic formula and an independent rational Gaussian elimination agree in the executable check. As Delta t->0, P_H->I. With a+b>0, Delta t->infinity sends each column to (b,a)/(a+b); zero-rate/absorbing limits remain regular. This is a property of backward Euler/frozen resolvents, not a theorem about every MPRK method or a recommendation to replace REI's existing integrator by first-order Euler.

## 3. Different frozen coefficients and state feedback

For two generators A and B sharing w and the same Delta t, the resolvent identity is

    P_A - P_B = Delta t * P_A (A-B) P_B.

It follows exactly that

    P_A u - P_B v = P_A(u-v) + Delta t*P_A(A-B)P_B v,

and hence

    ||P_A u-P_B v||_(1,w)
       <= ||u-v||_(1,w) + Delta t*||A-B||_(1,w)*||v||_(1,w).

For v>=0 of conserved weighted mass M, its last norm is M. This explicitly exposes the rate-feedback term that a same-generator comparison hides.

Suppose A=A(u,xi) and a separately established bound on the relevant invariant domain gives

    ||A(u,xi)-A(v,zeta)||_(1,w)
       <= L_u ||u-v||_(1,w) + L_xi ||xi-zeta||_xi.

Then the corresponding lagged-rate map has the conditional bound

    E_(n+1) <= (1+Delta t_n*M*L_(u,n))*E_n
               + Delta t_n*M*L_(xi,n)*delta_(xi,n) + rho_n.

rho_n must bound the actual additive local-map defect, including applicable rate-freezing, time-discretization and solve/rounding errors. It is not automatically supplied by a full-step/two-half-step difference; that difference needs its existing validated remainder argument. L constants must be bounded over the whole admitted state/input enclosure, not sampled at a convenient endpoint.

Set alpha_n=1+Delta t_n*M*L_(u,n) and eta_n=Delta t_n*M*L_(xi,n)*delta_(xi,n)+rho_n. Iteration yields

    E_N <= [product_(n=0..N-1) alpha_n]*E_0
            + sum_(j=0..N-1) eta_j*product_(k=j+1..N-1) alpha_k.

The empty product is one. The simple sum of local defects is justified only when valid step gains are <=1. The proof here gives neither actual REI values of L nor a validated full-interval tolerance.

## 4. Exact counterexample to unconditional nonlinear nonexpansion

Let s be the HII fraction, u(s)=(1-s,s), and take a(s)=s^2/tau0, b=0, Delta t=tau0 with tau0>0. The source model is a deliberately simplified counterexample, not a physical recombination/photoionization rate fit. Every frozen matrix satisfies the theorem, and the nonlinear update preserves the unit simplex:

    g(s) = (s+s^2)/(1+s^2),    0<=s<=1.

Yet g(1/4)=5/17, g(1/2)=3/5, so

    ||u(g(1/2))-u(g(1/4))||_1 / ||u(1/2)-u(1/4)||_1
       = 104/85 > 1.

Thus positivity and conservation do not imply global nonlinear nonexpansion. No real REI solver instability is claimed. A simple Lipschitz bound on this unit-simplex example is L_u<=2/tau0, giving alpha<=3, which safely exceeds 104/85 but is not sharp. Distinguish this pairwise statement from asymptotic stability of a particular equilibrium; they are different properties.

## 5. What the exact checker does and does not establish

`verify_bounds.py` uses standard-library Fraction arithmetic for small, declared matrices. Ten named checks cover closed-form H, H+He blocks, weighted conservation, the resolvent difference identity, two-input bound, exact feedback counterexample, composed error budget, equilibrium/zero-rate limits, wrong-sign/transpose mutations, and invalid-domain rejection. Negative hypotheses are checked directly; this is NOT a missing-implementation RED->GREEN narrative and no production method was altered.

Finite rational checks corroborate the analytic statements and catch signs/orientation. They are not an arbitrary-dimension theorem prover, performance benchmark, MPFR validation, production chemistry test, actual microstep replay or first interval. The proof above carries the general claim under its explicit hypotheses.

## 6. Literature and repository attribution

SciSpace located these primary papers; their arXiv abstracts were read for methodological scope (no equation-level full-text replication is claimed):

- Kopecz and Meister, On Order Conditions for modified Patankar-Runge-Kutta schemes, arXiv:1702.04589. Positivity/conservation and accuracy order are separate method properties.
- Izgin, Kopecz and Meister, A Stability Analysis of Modified Patankar-Runge-Kutta methods for a nonlinear Production-Destruction System, arXiv:2210.11845v2. Nonlinear iteration/fixed-point stability needs its own analysis, including for nonlinear MPRK maps.

Our resolvent proof, feedback counterexample and conditional error bound above are derived here. We do not attribute them as new theorems proved in either paper, or claim novelty over numerical-analysis literature.

The repository-derived motivation is the historical four-site state/source separation and elemental ledgers. The correspondence between any actual production MPRK population stage and this frozen-resolvent form has NOT been proved in this work. It must be mapped from current source, including predictor denominators and stage weights, before this bound is used for an REI interval claim. Do not collapse four independent source evaluations into one shared source to obtain a smaller bound.

## 7. Review and next material task

Sequential PHYS-MATH review: proof uses fixed positive weights, nonnegative off-diagonal rates, same timestep and no open sources. Dimensionless fraction norms do not mix temperature/energy units. Frozen positivity is separated from feedback stability and local defects from global error. The exact counterexample refutes an overbroad inference, not the current solver.

Sequential PHYS-MATH-CODE review: checker is an independent rational reference, no production import and no JAX/Rust replacement. Tests must execute, discover exactly ten IDs and preserve original failures; output is not pre-labelled PASS. No new native or scientific-admission gate is added. Execution status is recorded only after actual CI/local output is read.

Next: map the existing REI population-stage matrices and four source sites to these hypotheses in a read-only, isolated scientific source inspection; derive the real stage sensitivity/defect composition or produce a concrete violating term. Actual MPFR/JVP execution may need local Codex. No first interval, external provider, BASS geometry or historical-host recovery is authorized by this note.
