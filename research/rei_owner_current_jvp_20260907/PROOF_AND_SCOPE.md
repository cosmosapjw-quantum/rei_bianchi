# Source-bound resolved photon-owner sensitivity

STATUS: DERIVED_EXACT_REAL_LAW__REFERENCE_CODE_UNEXECUTED
Task: REI_OWNER_CURRENT_JVP_SOURCE_SLICE. Date: 2026-09-07.
This advances the owner-normalization portion of the unfinished numerator term.
It does NOT complete the event-free physical tube requested by PR #76.

## Authority and inspected sources

Continuation parent: PR #76, commit 9651959529b1048d9346f695e52ace2558d9bed6,
tree 1440a7610e01cd4ed8abadf80319f7dcad8f863e. PR #75 remains a separate,
unmodified sibling. #73--#76 generic denominator results are reused, not rerun.
The original private conversation URL redirected to login; the shared URL
returned Cache miss twice. Recovery is from GitHub handoffs and source, not a
claim that the linked transcript was read.

All source reads below use that parent commit:

- `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis/array_owner_kernel.py`, blob b9ccab2af7f302b9188bdde7bfbc846acc5c91f7. Read lines 1--145 and 260--485: _condition, _allocate, _global_raw_values, evaluate_values.
- Same directory, `physical_trial.py`, blob 7b9591282a453e193e7a802bdfa629342d9de7c3, lines 55--115: photo_fields.
- `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT/analysis/event_uncertainty_operator.py`, blob 765f2cb2957c0466a5cf0bde15a55e5a2ed5e0f3, lines 65--180: event flux and actual photo insertion.
- `src/rei_bianchi/source_bound_mprk_sdirk_operator.py`, blob fba94e59d20d640237290911abd774ede3fe5360, full file: intentionally unavailable four-site Rust replay.

These are connector source reads with server-reported blob identities, not a
local checkout/hash validation or a production invocation. The old code was
not modified, imported, or executed.

## Domain and conventions

One fixed photon group g; s=(HI,HeI,HeII); nodes i. N_si are extensive species
counts, already carrying node quadrature weights. H=sum_i(N_HI+N_HII) and
He=sum_i(N_HeI+N_HeII+N_HeIII) are positive elemental totals. No second node
weight or volume factor is inserted into the explicit-owner measure.
Keep the source's fixed cross sections and support mask. We work on an
interior patch with positive node counts, positive group opacity kappa,
nonnegative total absorbed photon current J and external subgrid raw response e,
and positive total raw response R. Inactive coefficients stay exactly zero.
A zero e or J is held fixed for this two-sided tangent; other boundary/one-sided
questions require their own domain analysis.

The operator below is the EXACT-REAL algebra underlying the source. The actual
binary64 _condition and _allocate add residual corrections at argmax entries.
They vanish identically in real arithmetic, not necessarily in floating point.
No derivative, numerical stability, or rounding-error bound for those machine
operations has been established. The code here is not a production replacement.

## Actual coefficient map (preserve the unusual HeII convention)

Let a=1/(1+z), nH_phys=NH0_CM3*(1+z)^3, nHe_phys=YHE*nH_phys.
For the fixed group, define

    p_HI   = a*nH_phys *sigma_HI  *MPC_CM
    p_HeI  = a*nHe_phys*sigma_HeI *MPC_CM
    p_HeII = a*nHe_phys*sigma_HeII*MPC_CM
    c = (p_HI/H, p_HeI/He, p_HeII/H).

The last denominator is H, NOT He. This follows literally from
x_heii_per_h in _global_raw_values; no correction or physical reinterpretation
of the locked convention is made here. Unsupported group/species pairs have c=0.
Each p scales as (1+z)^2 at fixed cross section, so

    delta p_s = 2*p_s*delta z/(1+z),
    delta c_s = (delta p_s-c_s*delta elemental_total_s)/elemental_total_s.

On fixed-total chemistry directions delta H=delta He=0. Do not impose that on
arbitrary input/parameter perturbations. The candidate coefficient helper takes
actual prefactors/directions explicitly, rather than inventing physical values.

## Eliminate the species marginal, retain the global normalization

Write S_s=sum_i N_si. The real source law gives raw explicit response r_s=c_s*S_s,
raw subgrid response r_0=e, and R=e+sum_s c_s*S_s. _condition and evaluate_values
then give owner opacity kappa*r_s/R and owner current J*r_s/R. For an active
species, _allocate uses N_si*sigma_s/(S_s*sigma_s)=N_si/S_s. Therefore

    j_si = J*(c_s*S_s/R)*(N_si/S_s) = J*c_s*N_si/R.                 (1)

This cancellation is of the species marginal S_s, not the total R. For inactive
support j_si is structurally zero and no division by its zero measure is used.
The subgrid GROUP current is j_0=J*e/R; its per-node measure is out of scope.
The direct kappa factor cancels only at fixed J,e,c,N and on kappa>0. Any physical
forcing relation J(kappa), e(kappa), etc. still contributes through the chain rule.
No behavior at kappa=0 is inferred from (1).

Define a_si=c_s*N_si, delta a_si=c_s*delta N_si+N_si*delta c_s and

    delta R = delta e + sum_si delta a_si.
    delta j_si = (a_si/R)*delta J
                 + (J/R)*[delta a_si-(a_si/R)*delta R].             (2)

The last term is a genuine global cross-node response. Freezing R incorrectly
removes the response at unperturbed nodes. At fixed c,J,e, perturb HI at node k
(while compensating HII to keep H fixed); at i!=k,

    partial j_HI,i/partial N_HI,k = -J*c_HI^2*N_HI,i/R^2.

The augmented current (subgrid group total plus all resolved nodes) obeys
sum j=J and sum delta j=delta J exactly. These are analytic consequences, not
claims that the newly authored script has executed.

## Conditional bound and physical-input boundary

For a_aug=(e,{a_si}), p=a_aug/R, p>=0 and 1^T p=1,

    delta j_aug=p*delta J+(J/R)*(I-p*1^T)*delta a_aug.

Column j of I-p*1^T has absolute sum 2*(1-p_j), hence its induced l1 norm is <=2.
Consequently

    ||delta j_aug||_1 <= |delta J|+(2J/R)*(|delta e|+sum_si|delta a_si|). (3)

For a specified event-free positive tube with R>=r>0 and J<=Jmax, replace J/R
by Jmax/r and use independently justified direction bounds. Along a path,
integrate (3); this is a conditional finite variation estimate. No actual r,
Jmax, prefactor envelope or state/forcing tube has been evaluated here. A point
sample or the synthetic rational test fixture is NOT a physical interval bound.

Units: c and delta c are raw opacity per extensive count, R/e are raw opacity,
J/j are photon counts per physical second, and (2)--(3) have count/time units
for a dimensionless direction parameter. This photon-current l1 norm is not
silently substituted for the weighted population norm used by #74--#76.

## Join to the already derived population tangent (not a new denominator proof)

photo_fields sums j_si over groups without a per-atom division. The event source
adds the resulting photo terms only to F10 (HI), F32 (HeI), F43 (HeII), using
F[dest,source]. All their reverse photo entries are zero. Resolved photoheat is
EV_ERG*sum_si,g excess_eV[s,g]*j_si,g; for variable excess moments retain both
excess*delta j and j*delta excess. This identifies a source term, not thermal closure.

For the existing P=(I-h*K(F)*diag(d)^-1)^-1 and x=P*b, insert delta F_photo into

    delta x = P*delta b + h*P*K(delta F)*diag(d)^-1*x
              + (I-P)*diag(x)*(delta d/d).

K has each diagonal equal to minus its outgoing column sum. For fixed positive
weights equal along each elemental transfer, and x>=0,d>0,

    ||h*P*K(delta F_photo)*diag(d)^-1*x||_(1,w)
       <= 2h*sum_photo_edges w_source*|delta F_dest,source|*x_source/d_source.

This uses the already established frozen P contraction and a columnwise triangle
bound. Collisional ionization/recombination/OTS flux derivatives are NOT included
in delta F_photo; their opacity floors, min/max branches and T dependence remain.
Keep the actual corrector half weights, RHS y0, denominator yp, and all four
independent sites. No local-defect rho or full coupled inverse bound follows.

## Review and execution status

Sequential same-assistant PHYS-MATH review: signs, extensive-count normalization,
HeII/H, independent forcing derivatives, strict domain, exact-real versus rounded
program, and photon/population norms were checked as written derivations.
Sequential PHYS-MATH-CODE review: the proposed reduced JVP includes delta R and
delta c; tests differentiate a separate two-stage dual reference and include a
frozen-R negative control. This is static review, not independent certification.

Ten O01--O10 test methods were authored. NONE was run. No observed RED, GREEN,
compile success, per-test PASS, numerical plot, or production result is claimed.
Container command and independent Python probe each failed BEFORE process start
with caas.internal.errors.ClientError. Wolfram Context and the actual algebra
Evaluator both failed at MCP SSE routing (404), before kernel evaluation. No
unchanged retry loops or GitHub Actions execution were used as substitutes.
Publication uses [skip ci]; skipped/pending checks are not successes.

Next: execute this small candidate where a runtime actually works, then bind
its owner component to one EXISTING saved event-free state/forcing tube. Preserve
an exact missing-input boundary if such a tube is unavailable. Do not regenerate
canonical intervals or reopen XZ/GCC/native/environment work to obtain it.
