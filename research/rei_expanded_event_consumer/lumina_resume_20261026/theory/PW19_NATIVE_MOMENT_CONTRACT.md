# PW19 native-source consumption and Lumina template defect

Version 1.0, 2026-10-26. Scientific authority: next_source_theory; requested Astra role, observed runtime model label unavailable. Root owns execution authorization, cumulative resources and final admission. This contract grants no execution by itself.

## Selected input and result

Consume the existing C23B PW19-release source at the exact tabulated redshift 2.479. Compute the HeII primary ionization rate, electron kinetic-energy supply and matching photon absorption from the actual spectral table. Pass the same incident number exposure through the frozen late Lumina HeII moment operator, and report its numerical template defect relative to native Verner absorption. Implement a conservative local source residual/JVP from the actual native coefficients, without a new evolution.

This is a selected external model radiation source. The original external-source gate does not require empirical measurement. The input is an instantaneous isotropic bath-rest-frame spectrum at z=2.479, with rates per proper second; neither redshift interpolation nor a temporal history extension is selected. Lumina's published HeIII history ends at z=2.992408. The calculation compares local spectral operators and is not a comparison with a Lumina simulated cell or history at z=2.479.

Immutable source files are under `../intake/provider/`:

- `data/z_02.479000.csv`: 27966 bytes, SHA256 `f93db0bb33dc6b7011cc0490f96253a489e5c7cd20cba99005b1461a3e56a5d1`.
- `data/verner_photo.dat`: 17760 bytes, SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.
- `CONTRACT.json`, `spectral_photo_source.py`: inherited C23B source/provider contract and implementation fetched at bass_cr `8d0a5c375589fbddadc2bb90c8117311c80bad09`; the contract is under `research/cr_c23b_source_frame_20261023/source_providers/`, while implementation and data are under `research/cr_c23e_d43_source_binding_20261024/implementation/reuse/c23b/`. `../intake/SOURCE_PROVENANCE.json` retains their exact upstream paths.
- Existing Lumina `radiation_moments.json` and `FROZEN_CONTRACT.md` remain the source of the late coefficient sigma_L=7.34e-19 cm2, excess_L=13.5 eV, threshold=54.42 eV, band [54.42,2000] eV.

PW19 source attribution is Taira2025 PW19 v1.0.0, DOI 10.5281/zenodo.15367103; the inherited contract records release commit `863c3b7fa73a8510fbf57ee7b75ad1e8c34086de` and original archive hash. The atomic provider is the pinned Verner et al. 1996 official table. Provider uncertainty, physical-model uncertainty and interpolation error relative to an unprovided continuum remain three separate null fields (unknown), not zero. Quadrature evidence records the actual GL8/16 differences, and floating-arithmetic evidence records actual roundoff/conservation residuals; neither is a global physical error bound. Existing verified C23B source representation and atomic fit are reused; no historical suite is replayed.

## Derived measure, moments and energy conservation

The table gives S(E)=4*pi*nu*J_nu in erg cm^-2 s^-1 per dln E. With epsilon=1.602176634e-12 erg/eV, its incident photon exposure measure is

    dPhi = S(E)/(epsilon E^2) dE = S(E)/(epsilon E) dln E.

This is the isotropic absorption exposure 4*pi*J/E, not net vector flux. The true-c map, if requested, is n_gamma(E)dE=dPhi/c with c=2.99792458e10 cm/s; no reduced speed appears. Given positive source measure and native sigma(E), define on a stated band B:

    Phi_B = integral_B dPhi                      [cm^-2 s^-1]
    Psi_B = integral_B E dPhi                    [eV cm^-2 s^-1]
    Gamma_B = integral_B sigma(E) dPhi           [s^-1 per target]
    K_B = integral_B (E-chi) sigma(E) dPhi       [eV s^-1 per target]
    A_B = integral_B E sigma(E) dPhi             [eV s^-1 per target]
    A_B = chi Gamma_B + K_B.

All band boundaries are explicit and split the quadrature. No integral heating table is inverted into a spectrum. Native moment coefficients sigma_eff=Gamma_B/Phi_B and excess_eff=K_B/Gamma_B are derived diagnostics for this exact source; they do not replace the frozen Lumina coefficients.

For B=[54.42,2000], the existing late Lumina operator returns Gamma_L=Phi_B*sigma_L and K_L=Gamma_L*13.5. Report signed relative template defects

    delta_Gamma=(Gamma_L-Gamma_B)/Gamma_B,
    delta_K=(K_L-K_B)/K_B,
    delta_abs=(chi*Gamma_L+K_L-A_B)/A_B.

These defects are a physical mismatch of two within-band spectral weightings, not numerical integration errors. They have no acceptance threshold. Report the inherited quadrature error separately. The exact identities behind the defects are Delta_Gamma=integral_B(sigma_L-sigma(E))dPhi and Delta_K=integral_B(sigma_L*13.5-(E-chi)sigma(E))dPhi. The signs have no a priori guarantee. Matching photon number and energy alone does not imply matching these absorption moments.

For each positive log-log source segment [a,b], S(E)=S(a)(E/a)^p. With L=ln(b/a) and F(q,L)=expm1(qL)/q, continued as F(0,L)=L,

    Phi_ab=S(a)/(epsilon*a)*F(p-1,L),
    Psi_ab=S(a)/epsilon*F(p,L).

This analytic evaluation, already implemented in the provider, gives an independent number/energy normalization check for the quadrature measure. The p=0 and p=1 limits require the continuous F expression, not division by zero. A new remote Wolfram symbolic calculation independently returned zero residuals for both segment integrals, the limits Phi(p=1)=S(a)*ln(b/a)/(epsilon*a) and Psi(p=0)=S(a)*ln(b/a)/epsilon, zero He/charge and energy-partner residuals, and the stated density JVP. `PW19_WOLFRAM_CHECK.json` retains returned output and intermediate warnings; remote CPU telemetry is UNKNOWN, not zero.

## Full support and finite partition

Keep the native atomic domain [54.42,50000] eV. Partition at 204.42 and 2000 eV:

1. [54.42,204.42]: primary-electron kinetic support [0,150] eV.
2. (204.42,2000]: higher-energy electrons inside the late Lumina band.
3. (2000,50000]: native supported absorption outside that band.

For each partition return Phi, Psi, Gamma, K and A, and retain their sums. Endpoint assignment is half-open except the final right endpoint; isolated boundary values have zero weight in the continuous representation. The full band primary spectrum has support to 1945.58 eV, and the full atomic spectrum to 49945.58 eV. A request to inject either complete source into a 150 eV kinetic grid must raise the existing domain error. The separately returned first submeasure is usable only with its explicit excluded positive tail; it is never renormalized to represent the complete source.

Return known radiation number/energy exposure over the source-table portions below54.42 and above50000 as separate ledgers using analytic photon_flux_moments. Below threshold the HeII primary rate is physically zero. Above50000 the atomic rate is unknown, represented by null/status, never zero-filled. Return total finite-table radiation exposure and verify number/energy partition. No extrapolation beyond the source table.

## Native local residual and tangent

For externally prescribed radiation and any supplied proper HeII density n>=0 cm^-3, let J=n*Gamma, P=n*K*epsilon and B=n*chi*Gamma*epsilon. In species order (HI,HII,HeI,HeII,HeIII,e), return

    dN/dt = (0,0,0,-J,+J,+J)                    [cm^-3 s^-1]
    dU_ion/dt = +B,
    dU_primary/dt = +P,
    dU_external_radiation/dt = -(B+P)            [erg cm^-3 s^-1].

Ion and primary-electron energy are distinct reservoirs. Primary kinetic energy is not yet heat. The external-radiation term is the accounted source reservoir, not an evolved native radiation state. For a density tangent v_n, the JVP replaces n by v_n in these linear expressions. A signed tangent is valid even though physical density must be nonnegative. Per-target native coefficients are the source-consumed physical result; any test density is a labelled arithmetic fixture rather than an inferred cosmological gas density.

He nuclei, electric charge and total listed energy are exact left-null invariants. Electron number grows at J. The source creates no neutron/tritium nuclear channel and identifies no helium isotope. No recombination or collisional term is introduced, so detailed balance for a completed photoionization-recombination system remains outside this one-way external-source residual. Event ownership is one HeII photoionization owner; no native Lyalpha, same-parcel recombination source or duplicate UVB heating is introduced.

The consumer-facing inter-repository boundary returns SI alongside these native cgs values: Phi_SI=1e4*Phi [m^-2 s^-1], sigma_SI=1e-4*sigma_cm2 [m2], K_SI=1.602176634e-19*K and A_SI=1.602176634e-19*A [J s^-1 per target], n_SI=1e6*n_cm3 [m^-3], number residual_SI=1e6*number residual_cgs [m^-3 s^-1], and power_SI=0.1*power_cgs [W m^-3]. Gamma is unchanged. State labels, event owner, frame, exact source z, instantaneous proper-time convention, threshold and excluded support accompany the SI coefficients. Check Phi_SI*sigma_eff_SI=Gamma, n_SI*K_SI=0.1*(n_cm3*K*epsilon), and the same conversion for the radiation/binding partners at the inherited 2e-14 scaled roundoff tolerance. This is a unit-equivalent handoff, not a new physical criterion.

Symmetry/gauge axis: normal bath-rest tetrad with isotropic incident scalar exposure; passive tetrad rotations preserve scalar rates. A change of physical observer needs a transformed spectrum and is not gauge. No geometry or shear is evolved. Invariant axis: He nuclei, charge and external+binding+primary energy. Observable axis: actual source-qualified Gamma, K, effective moments and their Lumina template defects; no electron history, tau or CMB observable is inferred without a gas trajectory and geometry.

## Coding contract and bounded verification

Lower-tier implementation only. Allowed new code under this unit's `implementation/`; use the already verified unchanged layout `intake/provider/spectral_photo_source.py`, `intake/provider/CONTRACT.json`, `intake/provider/data/z_02.479000.csv` and `intake/provider/data/verner_photo.dat`. The source module SHA256 is `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`; `intake/SOURCE_PROVENANCE.json` records exact origin paths and readback. Reuse that record. Do not monkeypatch the source constructor or alter input data.

Use native PW19Spectrum(2.479), Verner96.from_table('HeII') and provider sigma/evaluate. Add a bounded band moment adapter using Gauss-Legendre8 and16 in ln E on each original interpolation segment split by the four thresholds. Fixed orders only. Evaluate one z, one ion, one source; no source scan, IVP, old307200-atom measure, fit, grid extension, recalibration or statistical uncertainty invention. Do not call the provider's full historical suite or full three-channel production.

Required checks, with inherited C23B tolerances:

- All moment entries finite and nonnegative; positive expected denominators stay positive.
- GL8 vs16 relative differences for Gamma,K,A each <=2e-11; report all actual residuals.
- Quadrature Phi/Psi versus analytic source integrals <=2e-11 relative on each partition; no max(1,physical_tiny_quantity) floors.
- Band and full-domain count/energy additivity and A=chi*Gamma+K <=2e-14 relative to the positive corresponding total.
- Native residual conserves He nuclei and charge exactly at algebraic level, with numerical residual <=2e-14 relative to J; energy partner residual <=2e-14 relative to absorbed power.
- Density JVP at labelled n=1 cm^-3, v=0.3 cm^-3: compare central finite difference h=1e-4 to analytic tangent <=2e-11 scaled by each positive rate/power. At n=0 rates vanish exactly and derivative remains finite.
- Source z=20 is rejected; negative density rejected; above50000 atomic evaluation rejected; full late-band150eV injection rejected; zero/under-threshold HeII source distinguished from unknown atomic tail.
- Confirm frozen Lumina late active species HeII only; no HI/HeI external rates are silently zero-filled as complete physics.

On any scientific failure preserve raw output, stop and return diagnosis to Astra; no automatic higher order, tolerance change or replay. Root freezes command, one scientific-child resource cap, cumulative accounting and GO after inspecting preparation. An independent Astra review examines actual raw results and diff before scoped admission.

## Admission and transition

R1-R5: exact source and new constructive source-consumed rate/energy/JVP map are frozen above. R6 requires independent review. R7 requires the newly authorized bounded execution. R8-R10 consume that evidence and publish a scoped decision with next executable action.

The external gate is evaluated literally: actual source E/z/angle/proper-time-rate support, units, uncertainties and explicit branch; no forbidden z extrapolation and no integrated-heating substitution. This exact snapshot can supply that prerequisite, subject to original node scope review. Full REC spectral admission additionally requires its existing species dependency, actual native consumer binding, energy partner, applicable detailed balance, band interfaces and exclusive Lyalpha ownership. A detached residual is not claimed as live REC-FIELD integration. Canonical count remains29/88 until root reviews the complete original gate. No new strong no-go result is proposed.

The exact original task was re-read at `pilot/recovered_coupled_20261026/research/orchestration_expansion_20261025/task_assignments/rec_bianchi.json`, `/source_assignment/tasks/3`, originating from `authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json`, `/tasks/3`. It explicitly requests a source-qualified result within its stated domain, unresolved provider/model uncertainty, a consumer-facing event/state contract, and unchanged historical evidence with an additive status observation. Its only REC-EXP-SPECTRAL dependency has predicate `downstream_REC_consumer_qualification_only_not_source_distribution_construction`. Therefore the minimal candidate external closure is this verified z2.479 isotropic snapshot with its finite energy support, SI event/state output, conservative primary/binding/radiation partners, separated unknown uncertainties and reviewed raw checks. No temporal interpolation, complete UVB family, thermalization, live chemistry trajectory or full REC consumer qualification is added to that closure scope.

PASS transitions to wiring the source-qualified native residual/JVP into the selected REC-FIELD callback, or a newly frozen electron-history step under its original scenario/geometry gate. It does not trigger a large run or budget reset.
