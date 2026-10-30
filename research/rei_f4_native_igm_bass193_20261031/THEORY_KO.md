# Source-verified theory/algorithm: REI native H/He on BASS193

**Conventions:** GR signature `(-,+,+,+)`; mean Bianchi-I expansion H>0, `x=ln(a/a_ini)`, physical proper time `dt=dx/H`. Original 193 BASS background is externally fixed. Atomic energies eV, cgs thermal densities cm^-3 and energy erg; Boltzmann constant retained. Imported BASS number fractions are per baryon; native REI H/He number fractions are per H and He nucleus. Grackle Case-A coefficient owner remains from pinned Rust code, not independently remeasured atomic data.

## Constructive input map

For saved source epoch s, define `n_H=(n_b/10^6)(Y_HI+Y_HII)` and `n_He=(n_b/10^6)(Y_HeI+Y_HeII+Y_HeIII)`, with n_b expressed in m^-3. Fractions are `x_HII=Y_HII/(Y_HI+Y_HII)`, `x_HeII=Y_HeII/(sum He)`, `x_HeIII=Y_HeIII/(sum He)`.

Absorbers `N=(n_H(1-x_HII), n_He(1-x_HeII-x_HeIII), n_He x_HeII)`. Pass original native BASS per-absorber photo rates **once**: `Gamma_i = Gamma_i^BASS` (not Gamma_REI + Gamma_BASS). Let original primary kinetic power per H-reference nucleus for each absorber be `Q_i / n_H`. Then `H_i=Q_i/N_i` is the per-absorber kinetic power passed as REI `IgmPhotoInput.heat_erg_per_absorber_s`. When N_i=0 and Q_i=0, the photon source power at this state vanishes; setting H_i=0 is a **state-scoped** choice, **not** a globally identified per-absorber transport law.

Native Rust point RHS returns `F_{ion}=(dx_HII/dt,dx_HeII/dt,dx_HeIII/dt)`, species chemical number derivatives, photo/CI/RR/DR events, thermal/cooling/escape/CMB ledgers and gas temperature point derivative. Its particle density `n_part=n_H+n_He+n_e^HHe`, with `n_e^HHe=n_H x_HII+n_He(x_HeII+2x_HeIII)`, omits other original BASS ionic charges. `n_e^BASS-n_e^HHe` is explicitly recorded; this difference is not silently zeroed in full BASS21 coupling.

REI binding-energy owner uses `chi_REI=(13.598434599702,24.587389011,54.41776) eV` rather than original BASS rounded `chi_BASS=(13.6,24.59,54.42) eV`. At each epoch:

\[ \dot E_{\gamma}^{\rm REI} = \sum_i N_i \left[ \Gamma_i\chi_i^{\rm REI}(1.602176634\times10^{-12}\,\mathrm{erg/eV})+\mathcal H_i\right]. \]

The **owner binding defect** `sum_i N_i Gamma_i (chi_REI-chi_BASS)` is tracked, not injected as an invented additional physical heat term. `Q_th+Q_bind+Q_escape=Q_gamma+Q_CMB` is a point energy identity; temperature point derivative follows from `u=(3/2)(n_H+n_He+n_e)k_B T`, expansion work `2 H u`, and chemical electron loading `-T dot(n_e)_chem/n_part`. No external ionizing photon is counted twice.

## Specific new result and use limit

The new 193×32 source-response packet retains original photon-owner numbers and expected *source-translated* RHS; the Rust test calls the **existing native implementation**, not a second translation. Native agreement, when CI passes, establishes the matched-H/He point-evaluator correspondence on 193 frozen states **at the pinned source version only**. It neither proves a self-consistent REI17/BASS21 global trajectory nor the Li I 1s state-resolved branching/secondary electron transport. In particular, ionization-fraction complement calculations at near-complete ionization introduce floating-point cancellation; test tolerances use bounded relative discrepancies, not invented exact equality.

Existing source-integrated REI H/He photon input `2.570815638374822e-10 erg/Href` and thermal point-source exposure `5.191549580748317e-11 erg/Href` are reused from PR #295. These are **integrals of RHS along the original saved BASS states**, not evolved energy or temperature changes. No new observational tau, CMB anisotropy or source-integrated gas temperature prediction is admitted.
