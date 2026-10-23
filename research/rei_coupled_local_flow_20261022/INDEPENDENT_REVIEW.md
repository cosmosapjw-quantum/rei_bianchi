# Independent review: coupled local flows

Reviewer role: separate Astra-tier agent, not the author of the execution
contract, THEORY.md or implementation. Date: 2026-10-22 UTC. The reviewer
read root AGENTS.md, the complete frozen contract, SOURCE_INTAKE.md and
THEORY.md, and independently re-derived the identities below. No historical
diagnostic or new scientific integration was run by the reviewer.

**Final recommendation: PASS_SCOPED_LOCAL_THERMAL_AND_BETA_FLOWS.**
The exact retained-model reductions, finite numerical results and standalone
replay repair are supported. The timing evidence supports the conservative
implementation choices below; it does not establish a universal speedup.
No current-unit finding remains open. The controller owns final admission.

## 1. Independently checked physics and algebra

The saved H coefficient row, donor threshold and evaluated neutron-lifetime
file match the numerical constants in the contract. The selected H moment is
bound to the same VF coefficient; the work does not mix the donor Li rate
with a different Li thermal provider. The adopted two subspaces distinguish a
closed retained-process Case-A energy calculation from a prescribed-T beta
population calculation.

For a fixed-target Maxwellian coefficient,
alpha(T) is proportional to T^(-3/2) times the integral of
sigma(E)*E*exp[-E/(k_B*T)]. Differentiating this expression gives the rate
weighted electron kinetic moment

    Lambda = k_B*T*(3*alpha/2 + T*dalpha/dT)
           = k_B*T*alpha*(3/2+D).

This is a conditional inference from the fitted rate and stated kernel
assumptions. It does not establish independent empirical heat accuracy.

For U=(3/2)k_B(1+x)T, substitution of xdot=-kappa*x^2 gives

    Udot = -(kappa*x^2)*k_B*T*(3/2+D),
    Tdot = -(2/3)*kappa*x^2*T*D/(1+x).

Adding Idot=-chi_H*kappa*x^2 and the escaped-photon source cancels exactly.
The omitted-particle-number control has negative Tdot, while the retained
EOS term yields positive Tdot because -3/2<D<-1/2. The physical interpretation
in THEORY.md is consistent with these signs and the fixed-target closure.

Eliminating the common rate from xdot and wdot gives
dln(1+x)/dw=3/(2D), hence the exponential first integral. Its orbit T(x) is
independent of n_B and of the rate amplitude A; these quantities rescale
physical time. For the specified H fit the partial fractions have residues
1 at r=0 and B1 at r=-ell1, with total residue 1/3 at infinity. These fix the
quadratic numerator and verify the logarithmic primitive. The stable root
product and log1p/expm1 form in the contract implement the same expression.
The bracket a/3<=w_target<=a follows by integrating -3<3/(2D)<-1.

Differentiating the full [x,w] vector field confirms every entry of the
2x2 Jacobian in THEORY.md. The reduced derivative follows by adding the
chain-rule contribution g_x*(3/2)*(1+x)/D. The independently evolved
escaped-energy state is needed for a non-tautological energy test; the
contract explicitly requires it for the Radau reference.

For beta+RR, each exact stage preserves its nonnegative simplex and linear
baryon invariant. In v=lambda*t, a composed Strang step of size d has

    n_new = n - d*n + d^2*n/2 + O(d^3),
    p_new = p + d*(n-rho*p^2)
              + d^2*(-n/2-rho*n*p+rho^2*p^3) + O(d^3).

The second-order coefficient is exactly (J_f*f)/2. Thus the smooth finite
problem has global order two; neither exact stages nor positivity imply a
uniform stiff-limit error bound. The noncommuting-field term in THEORY.md
has the stated sign under its explicit bracket convention.

Independently applying p=u_v/(rho*u) gives
u_vv=rho*n0*exp(-v)*u. With z=2*sqrt(rho*n0)*exp(-v/2), this is
z^2*u_zz+z*u_z-z^2*u=0. A convenient normalization is

    c=z0*K1(z0)-2*rho*p0*K0(z0),
    d=z0*I1(z0)+2*rho*p0*I0(z0),
    u=c*I0(z)+d*K0(z),
    p=-(z/(2*rho))*(c*I1(z)-d*K1(z))/u.

The initial conditions follow from I0*K1+I1*K0=1/z. A common scaling of c,d
cancels from p; the executed implementation uses the normalization above.
Positive u and nonnegative u_v persist because
u_vv has a nonnegative coefficient while u>0. The finite contract avoids
extreme-argument overflow; n0=0 and rho=0 use their elementary limits.

The modified Bessel equation, Wronskian and derivatives were checked directly
against the primary NIST DLMF pages (accessed 2026-10-22):

* [10.25.1: modified Bessel equation](https://dlmf.nist.gov/10.25#E1).
* [10.28.2: I_nu K_(nu+1)+I_(nu+1) K_nu=1/z](https://dlmf.nist.gov/10.28#E2).
* [10.29.3: I0'=I1, K0'=-K1](https://dlmf.nist.gov/10.29#E3).

For the bare-to-neutral energy convention, substituting
m_atom=m_nucleus+Z*m_e-I_bare/c^2 gives Q0=Q_bare+dI. Neutron continuum beta
has dI=chi_H. DD->He3III+n has dI=24.59+54.42-2*13.6=51.81 eV under the
donor's isotope-electronic-equality convention. This reference conversion
does not supply beta electron/neutrino/recoil energy fractions.

## 2. Preliminary findings and finite review boundary

No theory/source blocker was found in the declared two cases. The current
claim is a constructive model reduction plus finite-domain numerical evidence;
no strong no-go, physical-provider accuracy upgrade or mathematical novelty
claim is proposed.

A nonblocking implementation observation was sent before execution: fixed
primitive roots/residues and alpha(T_i) should be prepared once for fair
solver timing, rather than charging repeated preparation to scalar RHS calls.
The worker remains the implementation owner. Numerical criteria, source
values and physics conventions were not changed by this suggestion.

This review does not reopen unchanged historical tests or require an absent
beta thermal partition for the population-only case.

## 3. Executed implementation and numerical evidence

The reviewer read the entire executed scientific module and driver, all 103
check records, execution metadata, raw numerical summary and three actual PNG
figures. The worker completed one coherent diagnostic with 103/103 checks,
no scientific failures and exit 0. The recorded 40.260782102 s wall and
38.323068887 s CPU intervals begin after Python imports. Process peak RSS
was 113576 KiB. Threads were set to one and the observed process limits were
120 s CPU and 1 GiB address space; the shell supplied the 180 s timeout.

The reviewer separately opened the saved NPZ without importing any project
solver, confirmed all 82 arrays were finite, and recomputed the main energy
residuals, trajectory errors, convergence orders and trace-relative error from
those saved arrays. This was evidence analysis, not another integration run.

| Frozen requirement | Observed evidence and assessment |
|---|---|
| Actual immutable inputs | Three source/copy SHA256 pairs agree; selected H row, threshold and lifetime agree with the inspected source files. |
| Rate slope, slope derivative and thermal Jacobian | Maximum complex-step relative discrepancy 5.281e-16, below 1e-7. |
| Exact primitive versus direct quadrature | Maximum absolute difference 1.111e-16 across the specified 17 points for each Ti; largest target-root abundance error 5.357e-15. |
| Thermal trajectories | Reduced x scaled error <=3.125e-10 and T relative error <=2.578e-11 against Radau; full/reduced maximum discrepancy 4.376e-10, below 5e-8. |
| Thermal physical conditions | x stays nonnegative, T stays in the public interval and rises; U decreases and the conditional kinetic moment stays positive. |
| Independent escaped-energy evolution | Largest recomputed absolute normalized energy residual 2.143e-15, below 2e-10. The reference E_gamma was evolved from its RHS, not reconstructed from the invariant. |
| EOS and omission control | Maximum source identity residual 8.162e-16; omitting the particle-count term gives the opposite temperature sign at all three initial temperatures. |
| Bessel/Radau reference agreement | Maximum absolute abundance discrepancy 4.219e-14 on the stated finite cases, below 2e-10. |
| Strang convergence | Last two observed orders lie between 1.99938 and 2.00019; errors decrease at all three rho. |
| Positivity and baryons | No negative numerical abundance; largest listed Strang baryon discrepancy 1.333e-15, below 2e-12. |
| Elementary limits | Maximum discrepancy 3.331e-16 for n0=0 and rho=0 cases. |
| Source onset and trace | Positive p is born from zero. For n0=1e-104, final p=6.321205588285657e-105 and maximum component-relative error 1.288e-14, below 1e-10. |
| Original 21-state coordinates | Inactive slots are exactly zero, independent scatter RHS matches the 3-state embedding, and A.Y and q.Y agree with the intended baryon/electron values. |
| Energy-reference conversion | The declared Q0 ledger closes and the Qbare-as-Q0 control exposes the missing chi_H. DD ionization increment is 51.81 eV. This is correctly labelled a convention check. |

At target x=0.225 the independently recomputed temperatures are
119.838858083, 1210.497547970 and 6126.300286880 K for initial temperatures
100, 1000 and 5000 K. N=256 Strang maximum errors are respectively
3.118896763e-8, 7.372063382e-8 and 1.560862076e-6 for rho=0.1,1,10.
The adaptive beta comparison has errors 8.85e-11 to 1.66e-10; timing claims
must retain this unequal achieved-accuracy information.

The scientific code contains no abundance clipping, floor or renormalization.
Stable expm1/log1p expressions and separate trace components implement the
claimed finite-domain constructions. Fixed primitive constants and the
initial-temperature normalization are prepared/cached before the run.

## 4. Narrow delivery repair and timing finding

The initial replay driver required the adjacent historical unit to check
copied inputs, while its helper wrote into the delivered results directory.
This was a concrete standalone-replay defect, without impact on the completed
numerical calculation. Controller authorization is recorded in
TARGETED_FOLLOWUP.md.

The reviewer compared current source with `results/first_run_source.zip`.
`code/local_flows.py` remains byte-identical with SHA256
`e32069af2f1e6178a62878bd77031f68b23379100ea74aaf83f2b67923df0c19`.
The driver diff only replaces sibling-file reads with the manifest populated
from the observed source/copy equality. The helper copies the unit's own
code and inputs to a fresh /tmp directory before execution. The prepare-only
log records PASS in `/tmp/rei-coupled-local-flow.egO277`, verifies all three
input copies and imports the required runtime without invoking a diagnostic.
This closes the delivery finding without a scientific rerun.

The three original figures were visually inspected: they faithfully display
the retained trajectories, independent energy residual, convergence, source
and trace onset, and timing ranges with measured errors. Dense minor labels
on the convergence x-axis do not alter the explicitly reported N values.

The baseline sequential timing shows substantial within-method variation:
thermal100 reduced ranges from 15.3 to 741.6 ms per solve, and thermal1000
full ranges from 26.3 to 108.7 ms. These results alone do not support a robust
algorithm speedup. The controller authorized exactly one paired timing-only
clarification using unchanged scientific code, saved grids and references,
alternated method order, and both CPU and wall clocks. No physics, tolerance,
Radau reference or convergence campaign was changed or replayed for that
purpose.

## 5. Paired timing assessment and final scoped decision

The reviewer read `code/run_paired_timing.py`, its raw batch data and output
checks, the implementation metadata and handoff, and visually inspected
`figures/paired_timing.png`. The script actually uses the saved grids and
reference arrays, alternates A/B and B/A order, warms each method once, and
runs seven batches of three solves per method. Assessment is outside the
timed region. The scientific module hash remains the first-run value.

The one timing-only invocation exited 0 with body wall 4.362194691 s,
body CPU 4.358364734 s and process peak RSS 97632 KiB, under its separate
CPU30s/wall45s/AS1GiB limits. All 96 warmup/batch-final checks passed. The
paired beta checker includes a 2e-15 roundoff margin on the saved Strang
ceiling; independent inspection of the saved numbers confirmed all 96
checks also pass the original, unexpanded thresholds. No admission relies
on that margin and no additional run is needed.

| Case | Method A / wall median ms | Method B / wall median ms | Assessment |
|---|---|---|---|
| Thermal100 K | full 10.443 | reduced 20.984 | Full median lower; ranges overlap. |
| Thermal1000 K | full 12.505 | reduced 17.747 | Full median lower; ranges overlap. |
| Thermal5000 K | full 9.602 | reduced 13.168 | Full median lower; ranges overlap. |
| Beta rho=0.1 | Strang 5.598 | DOP853 5.772 | Similar time range; adaptive error is smaller. |
| Beta rho=1 | Strang 4.722 | DOP853 4.111 | Similar time range; adaptive error is smaller. |
| Beta rho=10 | Strang 5.181 | DOP853 7.935 | Time/accuracy tradeoff; ranges overlap. |

The process CPU medians give the same ordering in these pairs, while the
individual samples still vary. The full thermal formulation uses 212 RHS
calls compared with 221 for the scalar coordinate at the chosen tolerances.
The beta DOP853 errors are substantially below N=256 Strang errors, so these
figures are measured costs at stated achieved errors, not equal-error speed
ratios. The reason for timing variation has not been established.

The controller's proposed defaults are consistent with this evidence:

* Use the direct two-state DOP853 thermal path as the follow-on execution
  baseline; retain the exact scalar orbit for dimension reduction, density
  scaling, reference construction and thermodynamic checks.
* Use adaptive DOP853 for the finite beta/RR precision calculation; retain
  exact Strang subflows as nonnegative, conservative finite-step components
  with the demonstrated second-order convergence.

No additional performance sweep is required to admit the physical/mathematical
results, and the agreed stopping rule ends optional timing here.

This recommendation admits the specified pure-H Case-A thermal calculation,
its same-fit conditional moment and exact scalar reduction, plus the specified
isothermal neutron-beta/H-RR population calculation, exact positive stages,
finite convergence and trace resolution. It also accepts the corrected
self-contained replay preparation, with the original executed source and
results preserved. Publication/backup success is a later controller action,
not inferred from this review.

The beta thermal energy fractions, competing omitted channels, expansion and
directional radiation coupling remain separate next-unit physical inputs.
No claim about those inputs or a full cosmological trajectory is needed for
this completed scope. No strong no-go or novelty claim was submitted.
