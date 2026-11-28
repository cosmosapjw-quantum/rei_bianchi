# HE36 non-author theory and scope review

## Decision and actual reviewer role

**PASS_SCOPED — three scope clarifications requested during review are closed in the reviewed file bytes.** No remaining blocking algebra or scientific-scope issue was found in the incoming-loss derivation. The result is a conditional local kinetic component. It does not complete physical reaction gain, nuclear daughter charge/energy distributions, stopping, nonlinear anisotropy closure, or a coupled gas/metric integration.

Reviewer: `/root/atomic_donor_survey`. I did **not** author `theory/THEORY_KO.md`, `CONTRACT.json`, or `theory/independent_DERIVATION.md`. I previously authored the donor survey, finite-source moment implementation and CCC diagnostic/plot component. Therefore this is a non-author review of the named derivations and their scope, **not** an independent review of my own implementation, numerical tests, benchmark or figure. A separate code/numerical reviewer remains necessary for those deliverables.

The review consisted of reading the complete three primary files, checking the algebra by independent reasoning, reading the saved exact-arithmetic receipt without executing it, and comparing the particle-source assumptions with the reused REI donor's theory and implementation. No numeric suite, symbolic program, IVP, benchmark or renderer was run for this review.

Workflow1.0.0 / approval0.2 is retained. No novelty or literature-wide no-go claim is admitted.

## Scope findings and closure

| ID | Initial finding | Required clarification | Readback result |
|---|---|---|---|
| TH-SCOPE-01 | Root §3's “fixed bath” wording could be read as a finite-mass thermal bath, although its Q=−nn_tβ is the stationary-target result. | Identify a stationary/heavy fixed target and direct finite-mass Maxwellian targets to §4. | **CLOSED**: §3 now says the target thermal velocity is neglected, μ→m_s, and §4 owns CM energy and mass fractions. |
| TH-SCOPE-02 | Root §5 stated weighted-norm dissipation without explicitly freezing the density-dependent weight. | Restrict the result to frozen densities/coefficients; mention the time derivative of W in an evolving reaction system. | **CLOSED**: root wording now matches the explicit restriction in the independent derivation. |
| TH-SCOPE-03 | Root §8 did not state all assumptions behind R_e=q·ν r and thermal R_part=(1+q)·ν r. | State the charge-neutral 21-state heavy-species/free-electron census, no positrons/negative ions, all-retained-thermal assumption, and the extra number-source subtraction for a separate fast pool. | **CLOSED**: both root theory and CONTRACT now state these restrictions; dEfast alone is explicitly insufficient to determine the missing number source. |

These were textual/scientific-scope clarifications. They do not change A, B, C, the moment ladder, or any numerical result. The root reported applying them in R9 commit `ac9a8109362a5639247bd13460d65cacfcae939d`, followed by R10 `d88da131917a6fd8a453cf7c72d498591c052800`. The new Git object was absent from this local shallow checkout; its automatic remote lookup was unavailable. This review therefore binds to the directly read SHA256 file identities below, rather than asserting an independent readback of those remote commits.

## Mathematical checks

### 1. Maxwellian moment ladder and SI meaning

The normalized relative-energy measure is correct for independent Maxwellians at common temperature and zero relative bulk drift. With a temperature-independent K and fixed integration domain,

\[
D M_j=M_{j+1}/\theta-3M_j/2,\quad D=T\partial_T,
\]

implies β=θ(D+3/2)α and γ=θ²(D+5/2)(D+3/2)α. Expanding D²=T²∂²_T+T∂_T gives the stated ordinary-derivative coefficient **5Tα′**, not 4Tα′. Dimensions of α, β and γ are respectively m³/s, J·m³/s and J²·m³/s.

The root and independent derivations correctly require legal exchange of derivative and integral. They do not silently apply the ladder to a temperature-dependent screened kernel, to an empirical fit without derivative-error control, or to a hybrid whose number rate and energy factor are drawn from different microscopic assumptions. Necessary positive-moment constraints are not presented as a complete across-temperature microscopic reconstruction theorem.

### 2. Stationary target and finite-mass parent-energy trace

The first variation has the correct normalization: contracting the fourth Gaussian angular moment with traceless π returns the intended pressure perturbation and leaves scalar number/energy unchanged at first order. The stationary-target loss is J=−n_t[4γ/(15θ²)]π, while Q=−nn_tβ. Density units turn κ₂ [m³/s] into an instantaneous loss frequency [s⁻¹].

For finite masses, V and g are independent only for the stated common-temperature Maxwellian reference. Using c_a=V+bg and c_b=V−ag gives

\[
Q_a=-n_an_b(3a\theta\alpha/2+b\beta),\qquad
Q_b=-n_an_b(3b\theta\alpha/2+a\beta).
\]

Their sum includes both parents' removed CM kinetic energy: −n_an_b(3θα/2+β). This is a parent-removal trace. Treating it as net recombination or nuclear heat would remove CM energy that can remain in the product. The documents correctly require supplied product/recoil/radiation contributions before net Q or J is formed. In the heavy-mass limit, the projectile projection approaches the stationary-target result, while the target's own common-T energy is not the same reference as a cold stationary target.

### 3. Fourth-moment coupling, determinant and sign

The V⁴, V²g² and g⁴ contractions reproduce

\[
A=a^2\alpha+2ab\kappa_1+b^2\kappa_2,\quad
B=b^2\alpha+2ab\kappa_1+a^2\kappa_2,\quad
C=ab(\alpha-2\kappa_1+\kappa_2).
\]

The mixed Vg terms explain both the factor 2ab in the diagonal terms and its negative sign in C. Density factors in the block are consistent with each species' Grad normalization. W=diag(1/n_a,1/n_b) symmetrizes the negative loss operator, and the supplied factorization of AB−C² is consistent with direct expansion and limiting cases. Positive masses/densities and a nonzero nonnegative kernel supported at positive energy make the frozen-state quadratic form strictly dissipative; degenerate limits require the stated care.

For a time-varying density the norm derivative also contains πᵀ(dot W)π. The revised root text now explicitly retains this obligation. Neither the determinant nor a negative C proves componentwise monotonic decay, finite-step positivity, a nonlinear entropy theorem, or the validity of an evolving finite-amplitude Grad trajectory.

The constant-cross-section example is internally consistent: s=1/2 yields C=−abα/15; equal masses give A=B=79α/60 and C=−α/60. The two loss eigenvalues are 13nα/10 and 4nα/3. Clipping negative C would alter the derived projection.

### 4. Counterexample and infinitesimal interpretation

At T=T₀, the positive fixed kernels K₁=K₀ and K₂=(2K₀/5)(E/θ₀−5/2)² give the same α and β but different γ. Maxwell Gamma moments reproduce 15/4 and 27/4 for γ/(θ₀²K₀), hence κ₂/K₀=1 and 9/5. The finite equal-mass block/eigenvalue comparison follows. θ₀ is a fixed parameter of the kernel, not the varying integration temperature.

This is a counterexample to reconstructing the STF sink from scalar number/first-energy data **at one temperature**. The text correctly excludes a claim of impossibility when an exact temperature-dependent α transform or a full microscopic kernel is available. It does not claim these manufactured kernels are calibrated atomic cross sections or promote the construction to a new strong no-go theorem.

A nonzero STF quadratic Grad polynomial has a negative direction at sufficiently large velocity. Both derivations correctly interpret it as a first variation; the independent note also identifies the tangent of a positive anisotropic Gaussian family. Small |π|/p alone does not bound a finite-amplitude threshold-tail error. No closure trajectory is certified by this calculation.

## Source mapping and event obligations

### CCC finite source

The actual-data source uses electron laboratory energy and σ in a₀². The conversion in Eq. (7) has the correct eV-to-joule power and heavy-target velocity prefactor. Fixed support permits the temperature ladder without endpoint-motion terms. The finite 13.6058–968.61 eV integral is explicitly a partial moment; unmeasured tail and interpolation errors have no physical bound in this unit.

The theory correctly distinguishes the table's incident-energy coordinate from E_rel=μg²/2. A bare substitution μ≠m_e would silently change the cross-section function. The declared possible speed-preserving map E_tab=m_e g²/2, E_rel=μg²/2 and θ_tab=(m_e/μ)k_BT identifies the needed coordinate conversion, but is not treated as a finite-mass source qualification. Actual CCC diagnostics retain μ=m_e. This review does not revalidate my own integrator or its saved numerical comparisons.

### Atomic/nuclear particle counts and energy ownership

The reused donor explicitly uses Y per conserved baryon and a charge-neutral inventory of heavy species plus free electrons, with no positrons or negative ions. Under its all-retained-thermal fixture, q·ν, 1·ν and (1+q)·ν are the free-electron, heavy-particle and thermal-particle changes per event. Multiplication by baryon density converts its per-baryon event source to a volumetric source. Nuclear capture need not preserve heavy-particle count, so R_part=R_e is not a general nuclear identity.

The revised theory now states the separate-fast-population number correction. The donor's `thermal_rhs` explicitly contains C=(1+q)·Y−fast_e and dot C=(1+q)·F−fast_edot; an energy-only fast reservoir does not determine these number terms. A future positron, negative-ion, molecule, nonthermal ion or additional reservoir model must revise the census and event closure explicitly.

The event energy ledger keeps nuclear/ionic reference energy, thermal energy, fast products, excitation, retained/escaping photons and neutrinos distinct. A supplied net kinetic second-moment increment in J/event has half-trace equal to dEth; multiplication by the event rate yields a pressure source in Pa/s. This is a consistency check on supplied information, not a physical model of product tensors. Unknown products remain unknown. Incoming β is not the net ground-state CI common-pool heat loss when outgoing electrons remain in the same thermal pool.

The general-frame central source has the correct birth/death term:

\[
C_s=R_{2,s}-u_sF_s^T-F_su_s^T+m_sR_{n,s}u_su_s^T.
\]

Here F_s is the mass-weighted momentum source and R₂,s is the mass-weighted raw second-moment source. The last term follows from differentiating ρ_s u_su_sᵀ and is absent only under its stated special conditions. This frame identity does not extend the common-bulk pair coefficients to an arbitrary relative-drift distribution.

The temperature equation includes both shear work and thermal particle-number changes once. The isotope-reduction condition requires the full source, heat and tensor projection to commute; equal electronic rates alone do not establish this when isotope energies or nuclear changes differ.

## Remaining boundaries

The global DAG correctly leaves B2 partial and B3–B5 pending. Required future inputs include source-qualified outgoing/secondary moments, matched isotope sources, nuclear daughter charge and spectra, recoil/stopping, any separate fast-particle number evolution, closure validity, and gas/metric feedback. This review supplies no physical error bar, new species coverage, numerical trajectory, or literature novelty claim.

## Reviewed byte identities

| File | SHA256 |
|---|---|
| theory/THEORY_KO.md | `65dcdef05882b04d6329372d2804566cd799f929853e7de8163826250acdb68a` |
| CONTRACT.json | `2c089b41b2bd200b5d3ea5dd852271f4c2124c8d17bb0d36a40ff72c8812e2de` |
| theory/independent_DERIVATION.md | `2414bc3be894970c81db5b7064efe9d72a06214433afa9134932a13e9165aaaf` |

The machine-readable companion lists all supporting files, role disclosure, closed findings and execution counts. `reviewed_initial/` is the **first saved local snapshot**, taken after the root had already applied the three requested clarifications; it is not a snapshot of the pre-clarification wording. The initial wording was read directly before the requests and is recorded in the findings above.
