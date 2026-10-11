C12 retains the C11 physical map and adds a declared interval extension, output observation, and durable transactions. The background is the existing expanding FLRW r=0 member, with proper elapsed time in seconds and a_rel(0)=1. No anisotropic or CR/RCT admission follows from this binding.

For a positive cell photon measure dν(q), measured per initial physical cm³, q and E=R(t)q are in eV. The authoritative moments are N=∫dν and U=∫E dν. At a gas endpoint the existing positive implicit absorption map uses dν_h=dν_inc/[1+h c∑_a n_a σ_a(E)], with proper absorber densities n_a. This statement describes the existing map, not a new closure. The implementation uses overflow-safe algebra and its unchanged quadrature/own-component tests.

The endpoint kernels are K0_a=c∫σ_a(E)dν_h and KE_a=c∫Eσ_a(E)dν_h. Their units are s⁻¹ and eV s⁻¹ under the reference-volume convention. With V=a_rel³ and ε_eV=1.602176634e-12 erg/eV, the reported rates are

\[
\Gamma_a=V^{-1}\sum_{\mathrm{cells}}K0_a,\qquad
\mathcal H_a=\epsilon_{\mathrm{eV}}V^{-1}\sum_{\mathrm{cells}}(KE_a-\chi_a K0_a),\qquad
\dot u_{\mathrm{heat},a}=n_a\mathcal H_a.
\]

Here H_a is per absorber, in erg s⁻¹; its proper volumetric counterpart is in erg cm⁻³ s⁻¹. Chemical χ and the pinned cross-section thresholds retain their existing distinct values. The diagnostic binding captures the actual converged native RHS inputs and returned Γ. It must not infer those kernels from a fresh power-law fit to the resulting N/U moments: matching two moments does not identify ∫σ(E)dν for a nonlinear σ. This is why merely renaming the existing nine outputs would not produce the required 24 fields.

Radiation energy is ε_eV∑U in reference units and ε_eV∑U/V in proper units. Instantaneous source rates are ∑S_N and ε_eV∑S_U from StableCellSource.source(t), with corresponding proper values divided by V. Cumulative source counters remain time integrals from the original epoch. No division of a recent finite source increment by its step substitutes for an instantaneous rate. Initial output has no preceding attenuated-step kernel; its h=0 positive-measure evaluation is an output binding with SIGMA calls and zero gas RHS, not a repeat of IC scientific acceptance.

Every one of the saved 129 output times is a mandatory accepted macro endpoint; the 65 subset is the exact even-index subset. There is no new time interpolation. Source-band/cell-edge and emissivity-redshift knots are hard integration boundaries. Internal emissivity-energy knots remain source-quadrature subdivisions, and opacity thresholds remain cell-quadrature cuts. This separation preserves the discontinuity locations without forcing every internal integration node to become a gas time step.

The old PILOT02 gen3 identity binds a shorter interval. A valid extension therefore loads and verifies that identity first, preserves its physical arrays, seven-state prefix, R/support, counter origins/extrema, initial scales, and adaptive cursor, and publishes a new child identity for the declared full end/event/output schedules and runtime allocation. Equality of the inherited prefix is a byte-level property. Future numerical equality to an unexecuted hypothetical run is not claimed. Updated schedules may change future step boundaries while leaving the physical equations and acceptance criteria unchanged.

Durable acceptance requires the positive fine path and all original domain/ledger checks before publication. A completed atomic checkpoint is authoritative even if a later output/journal operation encounters an I/O exception; reconciliation must use its pinned transaction receipt and must not replay the accepted dynamics. An incomplete in-flight trial is not an accepted state. Its evidence must be retained and its resumption policy explicit. Rejected temporal trials preserve their new cursor and consumed attempt count without advancing the physical prefix.

The controller's fixed-unit local defect target 2e-7 remains a heuristic. It does not prove the full-history 9-field temporal gate 2e-6. Final temporal/spectral comparisons still normalize each field by its own fine maximum on each selected 65/129 set separately; zero reference requires exactly zero difference. The existing 24-field spectral gate 1e-3, original-energy/initial-nH ledger gates 1e-9, and geometry gate 1e-11 remain unchanged. A successful binding or continuation chunk is implementation/numerical evidence in its measured scope only.

Source trace: c10/positive_absorption.py (_attenuate, _kernels, absorb); c11/integration/native_step_v3.py; rust/rei_microphysics native RHS and q1a/compare.py field definitions; c11/integration/production_design/PLAN.md. Implementation evidence and independent decisions are recorded separately in c12 component/review directories. This derivation introduces no external physical model or literature-dependent parameter.
