# Sandbox source adapter: frozen theory-to-code contract

Date: 2026-10-22. Workflow: physmath-research-loop built-in 1.0.0, as explicitly
supplied by the user in this turn. Objective: continue C2 through numerical
design, executable conditional local kinetics, numerical validation and an
independent scoped decision, using the current CPU sandbox. This is the
R1–R10 / C3–C10 work unit; C1/C2 evidence is reused.

## Authority, inputs and preservation

The user now requests sandbox-executable optimization, physical simplification
and the following coding loop. This authorizes the finite local calculations
below. Historical 50-trial and cosmological campaign ledgers are not reset or
debited by relabelling these diagnostics as old campaigns. No historical IVP is
replayed. No cosmological trajectory, new physical daughter probability, or
unprovided thermal/radiation closure is introduced.

Verified remote starting branch: research/rei-coupled-isotope-contract-20261022;
PR221 HEAD 42e44494bd0956756d8c610e75da5b1cafe20d3c, base
6a12f3865d9ea427c1391c41caed8bb7cb7ec00d, open draft. The restored local
rei_isotope directory has no .git. Preserve it and all existing files. Do not
clone, make a worktree, or alter historical source/evidence. New owned root:
research/rei_coupled_isotope_sandbox_20261022/.

Inputs are the adjacent C2 vendor/donor_atomic tree, fixtures/nuclear_sample.npz,
vendor/nuclear/EVALUATED_DECAY_INPUTS.json, BINDINGS.json and SOURCE_IDENTITY.json.
Atomic donor commit: 8be7533cc97b3302bf42608699d6e8313ed6af8a. C2 scientific
commit: c1714f82ea7de15fee230a1a995365970ee6dc02. Reuse their scoped findings;
do not invoke check_bindings.py. Copy the small required vendor inputs into this
unit for standalone execution, preserving bytes and relative paths. The full
historical nuclear arrays are not needed by this new program.

Root/Astra owns this contract, theory, tolerances, failure interpretation and
admission. Existing lower-tier worker owns implementation and execution.
Existing independent reviewer reviews the new work without implementing it.
Actual executor identity must be recorded without guessing a runtime model.

## 1. Physical domain and API

SI units, proper time in seconds, Y_i=n_i/n_B and original ordered 21 slots.
A.Y=1 for normalized examples. Temperature and external spectrum are prescribed
and fixed within one PreparedAtomic object; reconstruct it if either changes.
n_B is supplied explicitly and nonnegative. Default all nuclei and electrons
are thermal. A separately supplied scalar f=Y_e,fast is supported at the local
source boundary, with 0<=f<=q.Y; no stopping law is invented.

Use AtomicNetwork.rates(T,uv) and leave D unused. Do not use the old evaluate()
as a coupled source. The beta event layer alone owns the evaluated decay input.
The existing finite 5..200 eV spectrum and donor isotope electronic-equality
assumption are retained. No isotope abundances or charge fractions are removed.

Implement one useful PreparedAtomic API (the alternative of rebuilding all
rates at each RHS call is the reference/performance comparator). It supplies
RHS, analytic abundance Jacobian, fast-electron column, batching, exact shared
block solve, and a positive atomic-only stepping method. A second small module
supplies resolved events, coefficient status/interpolation, scaling, and EOS.
Keep public names and CLI simple; no framework, network calls, GPU or compiled
extension is required. NumPy/SciPy are available. Runtime must work offline.

## 2. Exact atomic simplification

Let P=G0, R=Gne=Grr+Gdr, e=n_B(q.Y-f), B=P+eR, u=n_B RY.

    F=B Y
    J_YY=B+u q^T
    J_Yf=-u

P and R have identical isotope blocks for H1/D/T (2x2), He3/He4 (3x3),
Li6/Li7 (4x4); n is a zero block. This is an exact computational sharing under
the donor's electronic-equality model. It preserves all 21 absolute abundances.
Do not extend this claim to isotope-changing event matrices.

For h>=0, M=I-hB, z=M^-1 rhs, w=M^-1 u:

    (I-hJ)^-1 rhs = z + h w (q.z)/(1-h q.w).

Solve three shared tridiagonal blocks, each with the relevant isotope columns
and u as multiple right-hand sides; neutron entry is unchanged. A hand-coded
small Thomas solve is allowed, with positive pivots in the physical domain.
Check finite values, normalized residual and the correction denominator. If a
numerically unsafe pivot/denominator occurs, use a recorded dense fallback;
no silent inaccurate solution. The physical-domain denominator theorem may be
used only after the accompanying derivation/review establishes it. Initial
guard: denominator must exceed 1e-12 in magnitude relative to its terms.
No claim that fewer operations automatically improves Python wall time.

Atomic-only integrator, fixed T,uv,n_B, f=0:

    Yhalf = exp[(h/2) B(Y)] Y
    Ynew  = exp[h B(Yhalf)] Y.

Reuse each common small-block exponential across its isotopes. This exponential
midpoint is second order for the smooth autonomous finite system. Each stage
is a nonnegative column-stochastic map in exact arithmetic; A.Y and each
isotope total are conserved. Do not clip or renormalize output to pass tests.
Reject material negative states. This is not a coupled nuclear/thermal stepper.
Dense solve/expm and a high-accuracy Radau solution provide independent numeric
references. Shared-block and rank-one operations are reusable implementation
components even if the dense solve is faster at dimension 21.

## 3. Resolved event source and zero onset

Events explicitly specify id, reactant/product integer slots and multiplicities,
coefficient or log coefficient, unary s^-1 versus binary m^3/s units, physical
or manufactured provenance/applicability, and signed energy allocation. Every
event satisfies A.nu=0. A resolved channel has one specified branch; if multiple
branches of a parent are accepted, probabilities and their normalization must
be explicit. Do not invent branching weights or apply bare k to isotope totals.

    R_j = k_j n_B^(m_j-1) product_i Y_i^a_ij / product_i(a_ij!)
    S = sum_j nu_j R_j
    J_S = sum_j outer(nu_j, grad R_j).

Limit m to 1 or 2 for this unit. Compute log flux before exponentiation so a
tiny k is not discarded before multiplication by a large density/population.
At zero reactants, compute polynomial partial derivatives by reducing the
corresponding exponent; never use R*a/Y at Y=0. A zero rate caused by a zero
reactant, a structural support zero, an absent channel, and representational
underflow have separate returned statuses. Absent inputs raise/return unresolved
instead of entering the physical sum as zero. Overflow raises a named error.
Negative physical abundances are rejected; the smooth atomic polynomial may
be evaluated separately for finite-difference/complex reference tests.

Energy uses the C1 neutral-atom reference. Each event requires Q0,W and named
signed terms dI,dEth,dEfast,dEexc,dEgamma_ret,Egamma_esc,Enu, all in J/event:

    Q0+W=dI+dEth+dEfast+dEexc+dEgamma_ret+Egamma_esc+Enu.

Validate per-event ledger with 128 epsilon normalized tolerance; preserve each
reservoir separately and sum its event rate. A supplied dI must agree with the
chosen explicit binding reference when that reference is present. A wholly
manufactured ledger is labelled as such. No physical mass-data admission here.
Construct at least one supplied continuum-beta endpoint using the evaluated
lambda, and binary identical-reactant and source-onset manufactured examples.
Return q.S, 1.S and (1+q).S; beta electrons are not added a second time.

## 4. Tiny stocks, coefficient interpolation, EOS and outer mapping

Store absolute binary64 abundances, including exact zero. Allow an explicit
positive diagonal scale s and z=Y/s. Choose diagnostic s_i from the known test
inventory/source scale, including 1e-104..1e-120 traces. Scaling is a numerical
coordinate choice, not an abundance floor or a claim about an unknown future
source. Require componentwise accuracy for trace tests. Demonstrate a positive
trace born from zero against an analytic source-loss solution; do not count
global norm agreement as trace resolution. Keep log rates/statuses for values
that underflow binary64. No all-log population representation at Y=0.

The saved three-knot nuclear fixture is default KNOT_ONLY. No automatic
extrapolation or off-grid physical accuracy claim. Implement optional explicit
log-linear interpolation for a provided positive coefficient table. For
x=ln T and f=ln k, a supplied |f''|<=M gives
|f-L|<=M*(dx)^2/8 and relative k error <=expm1(M*dx^2/8).
Require an explicit curvature bound and tolerance for admitted off-grid use;
refuse where bound exceeds tolerance. Structural-zero interpolation applies
only to a whole interval explicitly declared zero. Absent/zero/positive status
crossings cannot be silently interpolated. Manufactured power-law and quadratic
log-rate cases test the bound. Three stored points alone do not establish M.

All nuclei thermal with supplied fast electrons:

    C=(1+q).Y-f; Cdot=(1+q).F-fdot
    Tdot=-2HT + [2 Q_per_baryon/(3 k_B)-T Cdot]/C.

Q_per_baryon is an explicitly supplied total translational source in J/baryon/s.
Do not silently set missing DR heat, nuclear partitions or stopping to zero.
Test the constant-energy particle-number term, two-to-one capture and the
fast-electron source column. Full thermal feedback Jacobian is not claimed.
Provide one outer transform F_z,x=F/(sH), J_z,x=diag(1/s)J diag(s)/H, H>0.
There is one H division and no H inside the local source.

## 5. Finite checks and frozen acceptance

One coherent diagnostic run, saving raw numbers and failure cases. Additional
runs require a concrete diagnosed implementation/numerical failure; preserve
the first failure and do not relax these scientific tolerances. Prior C1/C2
scientific runs remain at zero new invocations.

* Verify exact immutable vendor copies against the C2 manifest.
* Atomic grid: T=100,1000,10000 K; uv=0,0.3,1; n_B=1,1e6 m^-3;
  positive manufactured, donor initial and trace-bearing states. Compare with
  direct dense P/R construction, beta-free. Normalized RHS/J algebra residual
  <=512 epsilon; complex-step Jacobian <=1e-10 relative to nonzero J norm.
* Linear solves: selected grid states, h*max(-diag B)=1e-3,1,100 (h=0
  when B=0), random deterministic rhs seed 20261022. Backward residual
  ||Ax-b||inf/(||A||inf||x||inf+||b||inf) <=1e-12; forward difference to
  dense <=1e-10 where cond_inf(A)<=1e8. Record conditioning and denominator.
* Event flux/J tests: unary beta, unequal binary, identical binary symmetry
  1/2, exactly zero reactants, n/T injection, underflow with preserved log,
  invalid/missing ledgers and absent statuses. Event algebra <=512 epsilon;
  log-exponent arithmetic relative <=2e-12; exact integer baryon balance.
* Trace analytic source-loss tests: onset at zero, scales 1e-104 and1e-120,
  analytic expm1 reference, component-relative error <=1e-8. Three tolerances
  or step sizes demonstrate actual resolution; no arbitrary positive floor.
* Atomic midpoint convergence: one normalized positive case T=1000 K, uv=1,
  n_B=1e6; final t chosen as 1/max(-diag B(Y0)); N=16,32,64,128 steps.
  Radau oracle rtol=1e-11, component atol=1e-13*isotope totals, analytic J.
  Relative isotope-weighted final error decreases with refinement, last two
  observed orders in [1.7,2.3], isotope conservation <=1e-12, no population
  below -1e-14 times its isotope total. Report actual error; finite accuracy
  is not a universal high-stiffness error bound.
* EOS and outer mapping: <=512 epsilon normalized identities. Negative
  controls omitting nuclear particle change, electron rank-one term, beta
  separation or symmetry factor must be detected where applicable.
* Timing: warmup and seven repeat batches at the same inputs, BLAS threads1.
  Compare rates-rebuilt dense RHS with prepared dense RHS with identical
  outputs; separately compare dense versus structured linear solves and
  scalar versus vectorized batch RHS. Record medians/ranges and setup cost.
  No speed threshold as correctness gate. Select the measured faster valid
  default for this dimension; keep honest conditions on each speedup.
* Save plots for convergence, trace onset/error and timing, then inspect them.

## 6. Resource and stopping contract

Single CPU process, BLAS threads1, max diagnostic CPU120s, wall180s, address
space1GiB; report observed peakRSS. Input working arrays are at most batch256
by21, benchmark iterations at most2000 per method per repeat. Atomic local
midpoint integrations and the explicitly listed trace/oracle calculations are
authorized; no new cosmological IVP or historical pilot. Limit native setup to
installed dependencies. If bounds are reached, preserve partial evidence and
return the concrete cause. Do not silently expand the campaign.

Deliver source, complete required small inputs, one offline run command,
raw results, timing data, figures, physical/numerical interpretation and resume
state. One independent reviewer examines derivation, changed source and raw
evidence, without replaying old campaigns. A scoped PASS advances the local
adapter while full coupled physical closure remains the next input dependency.

## Policy alignment

The 2026-10-11 skill overlay's historical separate-thread restriction and old
cloud-isolated-checkout anchor predate the actual current AGENTS tiered routing
and no-new-worktree rule. Apply current AGENTS and the developer's delegation
instruction: existing compatible agents, same restored directory, disjoint
paths. The user explicitly requests continuation through theory and coding;
the prior C2 instruction selecting C3 alone is a historical resume point, not
a cap on this newly authorized complete finite work unit. Scientific domains,
old tolerances, campaign budgets and missing physical inputs remain unchanged.
