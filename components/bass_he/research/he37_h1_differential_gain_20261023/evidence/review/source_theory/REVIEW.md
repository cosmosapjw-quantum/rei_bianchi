# HE37 independent source, theory, and provider review

Date: 2026-10-23. Review role: independent, read-only with respect to all author files. Contract: workflow1.0.0 / approval0.2; project `AGENTS.md` read. The net-source bridge, later diagnostics, figures, and publication are outside this review. The parent confirmed that the bridge had not yet been implemented when this review was requested.

## Verdict

**The source equations, number/energy/STF derivation, and scalar-moment provider are confirmed within their declared stationary heavy-target, ground-H, isotropic-outgoing, infinitesimal-electron-Grad scope. No blocking scientific or numerical defect was established in those objects.** Two low-severity corrections are recorded below. The saved tests support the exact reviewed bytes; they do not establish calibrated H1 angular accuracy, finite-mass kinetics, a total-gas closure, or a uniform numerical error theorem.

The reviewed model is Le–Cambier Eq. (85) with the explicit isotropic angular approximation of §III.E and a documented Bohr-radius precision refinement. It is not a CCC-normalized hybrid. The PDF checksum agrees with the source report and code. I checked the local primary text at Eq. (7), Eqs. (11)–(12), §III.E/Eqs. (49), (53c), and Eq. (85), including the source constants and the meaning of the relative energies. I did not audit the cited Zel'dovich–Raizer book or all equations of the paper.

## Findings requiring small corrections

### R1 — low: Boolean input promise exceeds the guard

**Object:** `lc_ionization.py`, `_real`, lines 53–61; corresponding broad Boolean-rejection wording in `README.md`.

**Evidence:** `np.asarray(values)` executes before the dtype check. A mixed sequence such as `[True, 0.5]` becomes a floating array, so the Boolean identity is gone before the guard examines `dtype.kind`. Thus `transfer_u(20.0, [True, 0.5])` is accepted by static NumPy coercion reasoning. Pure Boolean scalars/arrays are rejected as intended.

**Impact:** The element-level input contract is stronger than the implementation. No effect on the saved scientific calculations has been established; their inputs are ordinary real numbers. This does not invalidate the existing source/moment evidence.

**Minimal correction:** Either state that Boolean-typed inputs are rejected, or inspect mixed input elements before coercion if strict rejection of every Boolean element is intended. If the implementation is changed, add only the affected mixed-input guard check and bind its evidence to the new bytes; do not replay the scientific suites merely for this wording/guard issue.

**Claim verdict:** The claim that every Boolean input element is rejected is **rejected**. The pure-Boolean-array rejection claim is **confirmed**.

### R2 — low: Inexact paper title in the derivation

**Object:** `DERIVATION.md`, lines 152–154.

**Evidence:** The local primary manuscript title is *Modeling of Inelastic Collisions in a Multifluid Plasma: Ionization and Recombination*. The derivation instead supplies a different title beginning “Modeling of ionization/recombination processes.” The DOI, authors, journal identifier, and arXiv identifier point to the inspected primary source; `REPORT.md` already gives the exact title.

**Impact:** Bibliographic precision only. The cited equations and numerical model are not changed by this metadata error.

**Minimal correction:** Copy the exact title already used in `REPORT.md`. Refresh document/manifest hashes after the edit. No scientific re-execution is warranted.

**Claim verdict:** The exactness of that title as written is **rejected**; the identity of the intended primary source is **confirmed**.

## Physics and algebra assessment

### Source, normalization, units, and energy convention

Eq. (85), printed p.25, gives

\[
\frac{d\sigma_n}{d\Upsilon}=\frac{4\pi a_0^2 I_H^2}{E\Upsilon^2},\qquad
\sigma_n(E)=\frac{4\pi a_0^2 I_H^2(E-I_n)}{I_n E^2}.
\]

The factor `4π` is present. For the selected ground state, integrating over `I≤Υ≤E` gives `σ=4πa₀²I(E−I)/E²`. The implementation's cross section is an area in m²; its SDCS is m²/eV. Its SI Maxwellian moments consistently use `I_J=I_EV*EV_J` and joule energy weights. No eV/J conversion or cross-section multiplicity factor is missing. [Primary text, Eq.85; provider lines 26–37, 69–85, 120–139, 203–223.]

The source uses `I_H=13.6 eV` and rounded `a₀=0.529 Å`. The provider preserves the threshold and uses `5.29177210544e−11 m`, explicitly documented as the HE36 constant precision update. Both constants are bound into the model identity. This confirms reproduction of the functional model with a recorded parameter refinement; it does not mean a literal numerical reproduction of every rounded source constant. The CCC table's first-row threshold `13.6058 eV` is separate and is not silently substituted. [Primary text p.25; `SOURCE_ADMISSION.json`; provider lines 24–50; implementation README; local `CCC_TICS.1S.txt` header.]

The source's `E` is a relative COM energy with reduced mass `μ`, not automatically an electron laboratory energy. Section III.E takes `μ≈μ_t≈m_e` for small electron/heavy mass ratio; the additional temperature condition is in the text adjacent to Table I. In the chosen stationary infinite-heavy-target limit, replacing those relative energies by the electron laboratory kinetic energies is consistent. The implementation names this energy mapping explicitly. It cannot be converted to a finite-mass or isotope-specific model by merely substituting a reduced mass. [Primary text Eqs.6–7, Table I, §III.E; `DERIVATION.md` lines 10–17; provider `ENERGY_MAPPING`.]

The author CCC README files describe integrated transition/total cross sections, and the inspected `TICS.1S` header describes a total ionization table in `a₀²`. They support the report's limited statement that the inspected archive is not the admitted angular provider. This is not a literature-wide claim that no differential CCC result exists.

### One event, two outgoing electrons, one ionization defect

For `E>I`, the conditional transfer density integrates to one event. The two labels have energies `ε₁=E−Υ` and `ε₂=Υ−I`; their sum is exactly `E−I` on the model support. Consequently the inclusive outgoing electron measure integrates to two, the net electron-number increment is one, and the event cross section is not doubled. Symmetrizing the labels leaves the additive number and second moments unchanged. [Primary text Eqs.7, 11–12, 49; `DERIVATION.md` sections 2, 3, 5; saved provider `energy_partition` group.]

Writing `R=n_e n_H α`, the reviewed equations correctly give

\[
Q_{\rm loss}=-n_e n_H\beta,\qquad
Q_{\rm gain}=n_e n_H(\beta-I\alpha),\qquad
Q_{\rm net}=-IR.
\]

This agrees with the common-rest heavy-limit reduction of source Eq. (53c). A subsequent energy ledger must assign `+IR` to the same ionization-potential owner, with the identical threshold, so that kinetic plus potential energy is conserved. The current provider does not implement that ledger. Its actual ownership wiring is therefore **inconclusive/out of scope**, not certified by the correct scalar formula. [Primary text Eq.53c; `DERIVATION.md` lines 90–125.]

For an all-retained common-T pool, `R_part=R` and differentiating `U_th=(3/2)n_part k_B T` produces the stated temperature equation, including its `−T R_part/n_part` term. This number-change term belongs to the conversion from energy to temperature and must not be added a second time to the energy defect. The formula remains conditional on the declared thermal census and common-T closure.

### STF factors and species ownership

The Grad first variation has the correct normalization:

\[
\delta f/f_M=\frac{E}{n_e\theta^2}\,\pi_e:(nn),\qquad
\langle (nn-\mathbf1/3)(\pi_e:nn)\rangle_\Omega=\frac{2}{15}\pi_e.
\]

The single-electron pressure contribution is `2ε rr`. Thus an inclusive energy-weighted angular moment `D=∫ε P₂(n·r)dμ` gives

\[
B_{\rm gain}=\frac{2(E-I)}3\mathbf1+2D(nn-\mathbf1/3),\qquad
J_{\rm net}=-\frac{4n_H}{15\theta^2}\langle EK(E-D)\rangle\pi_e.
\]

These independently reproduce the factors in the derivation. Section III.E explicitly assumes `G=1/(16π²)` for the two relative outgoing solid angles. In the selected heavy stationary frame this gives isotropic one-electron marginals, `D=0`, zero STF gain, and `J_net=−n_H κ₂ π_e`, with `κ₂=4γ/(15θ²)`. Zero STF gain does not imply zero number or scalar-energy gain. [Primary §III.E; `DERIVATION.md` sections 2–5; provider `kappa2_m3_s`; saved direct Cartesian angular controls.]

The perturbation and resulting source act on **electron** STF `π_e`. Neither the derivation nor the provider supplies a relation between `π_e` and a total gas STF. Such a relation would require a separate species closure or an explicitly restricted perturbation subspace. The formulas are infinitesimal derivatives around a Maxwellian and do not establish a positive finite-amplitude Grad distribution.

The constructive angular bounds are correct: positivity and `−1/2≤P₂≤1` give `−(E−I)/2≤D≤E−I`, and hence

\[
\frac{4n_H I\beta}{15\theta^2}\le\nu_{\rm net}
\le\frac{2n_H(3\gamma-I\beta)}{15\theta^2}.
\]

They constrain admissible recoil-free angular models at the same event kernel. They are not a calibrated uncertainty interval for actual H1 data. The finite-recoil inequalities in section 7 also follow from the triangle/Cauchy inequalities, but remain bounds on an energy scale with a specified event weighting; they do not authorize adding recoil energy to products already assigned the entire `E−I`.

### Analytic moments and conditioning

With `C=sqrt(8/(πm_e))(4πa₀² I) θ^(−3/2)`, direct substitution gives `K dM=C(E−I)exp(−E/θ)dE/E`. Integrating the successive powers of `E` confirms all four formulas for `α,β,γ,δ`. The implementation's `α=C θ expn(2,x)` is equivalent to `C[θexp(−x)−I E₁(x)]` and avoids the cancellation in the latter expression. [Derivation section 6; provider lines 203–223.]

The Jensen bounds on the positive `F(x)` integral and the conditional-energy/`κ₂/α` consequences in Eq. (15) are correct. The declared numerical interval gives approximately `0.789≤x≤78.911`; the saved moments are positive finite normal binary64 values. The provider rejects lower/outside temperatures and rejects zero, nonfinite, or subnormal evaluated moments rather than treating numerical underflow as physical support zero.

At `E=I`, the cross section is zero, the ordinary conditional density is undefined, and the quantile returns its degenerate limit. That distinction is implemented consistently. A specific suspected upper-endpoint overflow at extreme finite energies was investigated by four new narrow quantile calls; it did not occur in those calls, including binary64 maximum. The suspicion is **rejected for the tested cases**. This check does not assert physical validity at those energies.

## Saved evidence and exact-byte applicability

All five provider-manifest entries and all three theory-summary payload entries match current byte counts and SHA256. The provider START/RESULT receipt uses the current provider and verifier hashes, and its execution identity recomputes as `9f4874b0ec077126b707cd536a019d57d0c85585cc02452b369b2b627ff8369d`.

| Object | SHA256 |
|---|---|
| Primary PDF | `5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68` |
| DERIVATION.md | `6930fb76b645144e8baef87cb927554a3dbc75495590f843c607c5715f8eba21` |
| check_gain_derivation.py | `dbdb0fbc8f9950509fa737c226dae931e64ad3e88f6b4dfaa16a62877d8a08ec` |
| CHECKS.json | `6f51e6337171ace7e18b58a708d9bf5c186a90b274be2dba0995ec2c73648033` |
| lc_ionization.py | `9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16` |
| verify_provider.py | `aeec5c1fe813cfc9df5e796ba17085a484714e52c16862e5077733496b234997` |
| Provider RESULT.json | `b5e171015434afc04334ec547bb31032cf7e7fbed59a497b93f8b8a391587faf` |

The saved direct original-integrand 80-digit radial comparison has maximum relative discrepancy `2.1974065901747693e−14` at three selected temperatures. The independent theory controls include four angular cases, three radial cases, and four sharing cases. The original angular residual function uses a denominator floor of one; `CHECK_SUMMARY.json` explicitly converts the saved residuals to true relative values, whose maximum is `1.4561819709916926e−15`. The maximum recorded theory radial discrepancy is `5.1916864393071865e−15`. These are local numerical comparisons and must not be presented as physical calibration or a uniform all-input guarantee.

Full path/size/hash bindings and individual claim verdicts are in `REVIEW.json`; the subsidiary receipt audit is in `numerical_audit/AUDIT.json`. The only new numerical review work consisted of four targeted `transfer_u` calls preserved in `numerical_audit/check_transfer_endpoint.py` and `TRANSFER_ENDPOINT_OBSERVATIONS.json`. No unchanged suite, IVP, benchmark, or render was executed. No author file was modified and no source PDF or other payload was published.

## Handoff boundaries

The next bridge review must assess actual code for the potential-energy owner, event/thermal number census, normalization and units, electron-vs-gas STF arguments, density dependence in Jacobians, and preservation of all exact input identities. This review does not preapprove that code. Calibrated angular data, finite-mass target motion/recoil, isotope-specific kinetics, thermalization, and coupled gas/metric evolution remain separate dependencies exactly as stated in the author contract.
