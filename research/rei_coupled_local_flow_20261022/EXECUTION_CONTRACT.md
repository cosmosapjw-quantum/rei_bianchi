# Coupled local flows: frozen theory-to-code contract

Unit: `rei_coupled_local_flow_20261022`. Controller date: 2026-10-22,
Asia/Seoul. Apply physmath-research-loop built-in 1.0.0 and current root
AGENTS.md. This is the next physical/numerical unit after the completed
conditional atomic sandbox. Reuse its evidence; do not rerun it.

## Authority, identity, ownership

The user requests sandbox-executable theoretical physics, physical
simplification and the following coding loop. This authorizes the finite
local calculations below. Existing publication and backup authority persists.
Starting PR221 head, freshly read this turn:
`2f9ebff30c7505e425179862819f212ddbd07542`; branch
`research/rei-coupled-isotope-contract-20261022`, open draft, unmerged.
The restored project has no .git. Preserve all existing paths and use this
new owned directory. No clone, worktree, historical campaign or cosmological
integration is needed.

Astra controller owns this contract and acceptance; the source/theory agent
owns THEORY.md. A lower-tier coding worker owns code, small input copies,
bounded execution and mechanical packaging. A separate Astra reviewer owns
the independent decision. Record requested executor identity without claiming
an unobserved runtime model. Stop for controller interpretation on a failed
scientific criterion; preserve the original result.

## 1. Immutable source binding and offline inputs

Copy, preserving bytes, from the completed sibling unit:

* `vendor/donor_atomic/data/atomic_coefficients.json`;
* `vendor/nuclear/EVALUATED_DECAY_INPUTS.json`;
* `fixtures/nuclear_saved_metadata.json` (energy-reference check only).

No donor executable or old diagnostic is required. The frozen H row is
`rr/1:1`: A=7.982e-11 cm^3/s, b=0.748, T0=3.148 K,
T1=703600 K, C=0, T2=0. Convert A by 1e-6 to SI. Retain chi_H=13.6 eV
from the same donor and exact SI k_B=1.380649e-23 J/K,
eV=1.602176634e-19 J. Public domain here: 100 <= T <= 10000 K.
Neutron mean lifetime is the supplied 878.4 s, lambda=1/tau_n.
Atomic donor pin: `8be7533cc97b3302bf42608699d6e8313ed6af8a`.
Completed sandbox scientific pin: `569f784e78676123513b7390001d317eb62d6372`.
PR219 provider input pin: `6a12f3865d9ea427c1391c41caed8bb7cb7ec00d`.

Use a small, self-contained Python/NumPy/SciPy implementation and an offline
CLI. No runtime network, extra dependency installation, generic reaction
framework or nuclear table interpolation. Input copies need one byte identity
check; numerical outputs are compared semantically.

## 2. Case A: dark pure-H Case-A recombination with evolving T

Uniform fixed n_B, expansion H=0, no imposed photons, ground-state H plus
HII/electrons, one thermal T, fixed-target Maxwellian RR approximation,
complete radiative cascade and escaped bolometric photons. The retained
process is radiative recombination. All other isotope slots are zero. This
subspace needs no DR, nuclear energy partition or fast-particle stopping.

Use the VF rate alpha(T) and its same-fit conditional kinetic moment:

    r=sqrt(T), s0=sqrt(T0), s1=sqrt(T1)
    alpha=A_SI/[(r/s0)(1+r/s0)^(1-b)(1+r/s1)^(1+b)]
    D=-1/2-(1-b)r/[2(r+s0)]-(1+b)r/[2(r+s1)]
    D_w=-(1-b)r*s0/[4(r+s0)^2]-(1+b)r*s1/[4(r+s1)^2]
    lambda_RR=k_B*T*alpha*(3/2+D).

The kinetic moment is conditional on this fit/model; numerical agreement
does not independently evaluate an experimental heat coefficient.
Let x=Y_HII, Y_HI=1-x, w=ln(T/Ti), kappa=n_B*alpha:

    xdot=-kappa*x^2
    wdot=-(2/3)*kappa*x^2*D/(1+x)
    U=(3/2)*k_B*(1+x)*T; I=chi_H*x
    Egammadot=n_B*x^2*(chi_H*alpha+lambda_RR).

U+I+Egamma is constant. D<0 implies rising T although U decreases.
Implement the analytic 2x2 Jacobian derived from these expressions.

Eliminate x through the exact thermodynamic first integral:

    L(T)=(3/2)*integral_Ti^T dln(theta)/D(theta)
    x=x_i+(1+x_i)*expm1(L).

For this H row, Q=3r^2+c*r+s0*s1,
c=(2+b)*s0+(2-b)*s1, Q=3(r+ell1)(r+ell2),

    ell2=(c+sqrt(c^2-12*s0*s1))/6
    ell1=s0*s1/(3*ell2)
    B1=(s0-ell1)*(s1-ell1)/[-3*ell1*(ell2-ell1)]
    B2=-2/3-B1
    L=-6*[w/2+B1*log1p(dr/(ri+ell1))
                +B2*log1p(dr/(ri+ell2))]
    dr=ri*expm1(w/2), ri=sqrt(Ti).

Integrate only w using reconstructed x. Domain: x_i/4 <= x <= x_i,
x_i=0.9, Ti in {100,1000,5000} K, n_B=1e12 m^-3. Use dimensionless
time s=n_B*alpha(Ti)*t. Obtain the common final s from the target x=x_i/4:
brentq the monotone first integral on
ln[(1+x_i)/(1+x_i/4)]/3 <= w <= ln[(1+x_i)/(1+x_i/4)], then quadrature
ds/dw=1/g_s(w). This preparation is outside timed solver calls and reported.
Use 129 uniformly spaced s output samples for both formulations.

Independent references: (i) direct quadrature of 1/D for the primitive;
(ii) full coupled [x,w,Egamma/Escale] Radau at rtol=2e-12, atol=1e-14,
with Escale=U_i+I_i and Egamma independently evolved. Do not define reference
Egamma by the invariant. Production comparison: full [x,w] and reduced [w],
both DOP853 at rtol=1e-9, atol=1e-12, same output grid. Reconstruct Egamma
algebraically for both production paths so timing does not charge an extra
energy variable to only one method.

## 3. Case B: neutron decay plus H recombination at prescribed T

This is a population calculation with prescribed T=1000 K, common thermal
electrons assumed after decay, UV=0 and expansion H=0. A thermostat/energy
partition is not derived. The beta kinetic/neutrino partition remains an
input obligation for a future thermally coupled beta case. Apply the supplied
total neutron lifetime to the selected continuum channel, retaining its
inherited branch approximation. Never silently add beta to atomic donor D.

    ndot=-lambda*n
    pdot=lambda*n-kappa*p^2
    hdot=kappa*p^2, n+p+h=1.

n,p,h map to original 21-state indices 0,2,1 respectively. All other slots
are exactly zero. Electron abundance is p; it is not incremented separately.
Use dimensionless v=lambda*t, rho=kappa/lambda. Construct densities
n_B=rho*lambda/alpha(1000 K) for rho in {0.1,1,10}; report actual SI values.
Initial (n,p,h)=(0.1,0.2,0.7), v in [0,4]. This is a declared local model
family with physical coefficients, not a measured astrophysical history.

Exact decay step d: n'=n*exp(-d), delta=n*(-expm1(-d)), p'=p+delta.
Exact RR step d: p'=p/(1+rho*p*d), delta=p*(rho*p*d)/(1+rho*p*d),
h'=h+delta. Apply D(d/2) R(d) D(d/2). No clipping or renormalization.
The stages preserve nonnegativity and baryon count in exact arithmetic;
Taylor expansion through d^2 proves order two for the coupled smooth field.

Implement the independent Bessel solution on the finite positive cases as
a reference, using u''=kappa*lambda*n_i*exp(-lambda*t)*u and p=u'/(kappa*u),
z=2*sqrt(rho*n_i)*exp(-v/2), u=c*I0(z)+d*K0(z). Fix the ratio from p_i;
the initial z in these cases is <=2, so large-argument scaling is unnecessary.
The n_i=0 or rho=0 limits use their elementary analytic solutions. Bessel
reference is not the production algorithm and no untested global domain is
claimed. Independent Radau reference: rtol=2e-12, component atol=1e-14.

Convergence: N=32,64,128,256 steps to v=4, all three rho. Observe last
two orders; finite errors are retained. Include source-onset n_i=0.1,p_i=0
at rho=1, and trace onset n_i=1e-104,p_i=0 at rho=1 and v=1. For the trace,
use its analytic decay source n_i*(-expm1(-v)); the omitted quadratic loss
has relative bound rho*n_i*v <1e-103, far below binary64 tolerance. Measure
component-relative p error rather than a norm dominated by h~1. Preserve the
tiny amount separately when its subtraction from h rounds to one.

## 4. Frozen checks, performance and meaningful negative controls

One coherent diagnostic invocation; preserve raw arrays, errors, counters,
versions, command, resource use and original failures. A concrete new failure
can authorize one targeted repair/run without replaying unrelated evidence.

* Input copy SHA256 equality. Record source paths and selected values.
* VF D and D_w, full thermal Jacobian: complex-step or independent high-order
  finite differences on interior states; normalized error <=1e-7.
* Primitive: direct quadrature on 17 w points for each Ti, including 1e-12
  near-origin w, absolute L difference <=2e-11. Root endpoint x error <=2e-11.
* Thermal trajectory: production x relative to x_i/4 and T relative to
  reference T each <=5e-8; full/reduced agreement at same tolerance. Reference
  energy residual |U+I+Egamma-Escale|/Escale <=2e-10. No negative retained
  species, T inside supported range, monotonically rising T and decreasing U.
* Finite-temperature kinetic moment positive; EOS source identity normalized
  <=1024 epsilon. A control omitting -T*Cdot/C must reverse the temperature
  sign for these inputs; record/detect it, do not accept that control.
* Beta/RR Bessel vs Radau absolute population difference <=2e-10 on 129
  samples; n analytic, baryon discrepancy <=2e-12. Strang errors decrease;
  last two observed orders in [1.8,2.2]. No population below -1e-15.
* Exact subflow n_i=0 and rho=0 limiting trajectories <=2e-12 absolute error.
  Onset tests: p>0 and trace p relative error <=1e-10. No artificial floor.
* 21-state embedding: all other slots exactly zero, A.Y remains consistent
  with the 3-species model and q.Y=p; compare RHS at representative states.
* Energy-reference convention check only: saved Q_bare plus dI=chi_H equals
  neutral-reference Q0 for neutron beta; DD->He3III+n dI=51.81 eV under the
  donor thresholds. Detect direct Q_bare-as-Q0 mismatch. No beta partition
  or coupled thermal beta result is admitted from this identity.
* Timing: warmup + seven batches, at most ten solves/batch. For thermal,
  same DOP853 tolerances and output grid; for beta/RR compare N=256 Strang
  against a DOP853 solve on the same 257-point grid with tolerances tightened
  enough to meet <=Strang reference error (rtol=1e-9, atol=1e-12). Show both
  measured errors: adaptive solver may substantially exceed the requested
  accuracy. No claim of equal-work/equal-error performance from tolerance
  labels alone. Retain median/range, RHS counts, setup costs and clock scope.
  Select a default based on actual accuracy and timing; no speedup gate.
* Plot thermal trajectories + energy residuals, beta convergence + trace
  onset, and timing with errors or clearly stated accuracy. Inspect actual
  figures once. Do not widen a sweep to manufacture a timing winner.

## 5. Bounds, stopping and handoff

Single CPU process, BLAS threads1; diagnostic CPU<=120s, wall<=180s,
address space<=1 GiB. Arrays at most a few thousand samples. Installed
NumPy/SciPy/Matplotlib suffice. Record peak RSS and timing interval explicitly.
No historical IVP/diagnostic invocations, network calls or optional campaign.
If blocked, preserve partial results and state the concrete remaining cause.

Deliver runnable source + three small input copies + raw numerical results +
figures + exact commands + theory/report/resume. Independent review receives
the new source, derivation and raw outputs, not merely the author's verdict.
One bounded review with targeted repair of actual findings advances to a
scoped admission. No strong no-go or mathematical novelty claim is proposed;
these are constructive reductions and finite-domain numerical results.

R1–R10 and C1–C10 completion links belong in the final report/checkpoint;
they must point to actual source, derivation, execution and decision evidence.
Once reviewed, preserve this additive unit on existing PR221 and authorized
backups. Complete this coupled-local work unit and state the next physical
input dependency without expanding into an unprovided cosmological closure.
