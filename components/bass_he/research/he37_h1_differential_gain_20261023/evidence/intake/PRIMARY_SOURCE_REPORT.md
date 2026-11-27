# H1 reaction gain source admission — HE37

## Decision

Adopt the **native semiclassical ground-state H1 ionization model** explicitly specified by Hai P. Le and Jean-Luc Cambier, *Modeling of Inelastic Collisions in a Multifluid Plasma: Ionization and Recombination*, *Physics of Plasmas* 23, 063505 (2016), DOI [10.1063/1.4953050](https://doi.org/10.1063/1.4953050), author manuscript [arXiv:1605.06545](https://arxiv.org/pdf/1605.06545). The complete chosen kernel consists of their Eq. (85) differential energy distribution and §III.E isotropic angular distribution. This is an explicit, source-qualified physical **approximation**, not calibrated H1 angular data. It supports an executable gain-plus-loss reference model, while the calibrated differential provider remains an open dependency.

Do not multiply the CCC total table by this partition law and describe the result as the native Le–Cambier model. Such a combination would be a separately named hybrid approximation. No hybrid is selected here. The paper also treats reverse three-body recombination; that does not supply radiative recombination and is not included by selecting its forward CI model.

## Source and retrieval evidence

Retrieved and read relevant manuscript sections: Eq. (7), printed p.5; differential normalization Eqs. (11)–(12), printed p.7; electron-induced heavy-mass and isotropic reduction §III.E, printed pp.14–16; scalar number source Eq. (49), printed p.15; electron net energy Eq. (53c), printed p.16; semiclassical differential model Eq. (85), printed p.25; source bibliography item26, printed p.39. PDF page images independently confirmed the angular assumption on printed p.15 and Eq. (85) on printed p.25. This is a targeted equation audit, not a claim to have independently checked every equation in the paper.

- Original PDF: 449706 bytes; SHA256 `5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68`.
- Scratch PDF/text: `/tmp/he37_sources/raw/le_cambier_2016.pdf` and `le_cambier_2016.txt`.
- Underlying Eq. (85) citation26: Zel'dovich and Raizer, *Physics of Shock Waves and High-Temperature Hydrodynamic Phenomena*, Dover 2002. The book was not independently audited in this unit.
- Early agent note mistakenly called §III.E “III.F”; visual inspection corrected this metadata before model implementation. No scientific input used the mistaken section label.
- Default sandbox network denied read-only HEAD requests. The approved escalation then retrieved the same public author URLs. Failed and successful HEAD records are preserved in `raw/`; no permission boundary was bypassed.
- Source PDF and page images are scratch-only and must not be redistributed in the public project. Publish the bibliography, selected source facts, hashes and original derivation/code.

## Native kernel and units

The paper uses Boltzmann constant absorbed into temperature in its displayed formulas. Implementation restores `theta = k_B T` as energy, while keeping SI mass, area and time. Use a consistently chosen energy unit in both incident energy E and transferred energy Upsilon.

For a hydrogen initial principal quantum number n, the paper's Eq. (85) is

\[
\frac{d\sigma_n}{d\Upsilon}=\frac{4\pi a_0^2 I_H^2}{E\Upsilon^2},\qquad
I_n\le\Upsilon\le E,\qquad
\sigma_n(E)=\frac{4\pi a_0^2 I_H^2(E-I_n)}{I_n E^2}.
\]

The selected process is **ground state only**, n=1, I_n=I_H=I. The source assigns I_H=13.6 eV and a_0=0.529 Å. Literal source-native implementation should use those values and state their limited precision. A modern Bohr radius or 13.6058-eV threshold is a deliberate parameter update requiring a separately recorded identity; it must not be silently mixed with the source-native values. The CCC threshold and Le–Cambier threshold are different model inputs.

For ground state,

\[
\sigma(E)=4\pi a_0^2\frac{I(E-I)}{E^2},\quad
p(\Upsilon\mid E)=\frac{IE}{(E-I)\Upsilon^2},\quad E>I.
\]

The area unit is a_0 squared, **including** the displayed 4 pi factor. The differential cross section has area/energy units; p has inverse-energy units. At E<I the channel is forbidden, sigma=0. At E=I the event cross section is zero and the normalized conditional density has no finite continuous density; code should represent the zero-event boundary explicitly rather than divide by E-I. The one-sided sharing law collapses to Upsilon=I. The source does not assign a validated error envelope or a temperature domain to this approximation; a chosen sandbox T grid is a computational domain, not a physical calibration statement.

## Energy, angle and counting contract

Eq. (7) gives transferred energy Upsilon and total available relative energy E. In the stationary infinite-heavy-target limit, outgoing electron energies are

\[
E_1=E-\Upsilon,\qquad E_2=\Upsilon-I,\qquad E_1+E_2=E-I.
\]

Each is nonnegative on the source support. §III.E takes the angular density

\[
G(\Omega_1,\Omega_2)=\frac{1}{16\pi^2},\qquad
\int G\,d\Omega_1d\Omega_2=1.
\]

Thus each of two labelled outgoing directions is independently uniform in the paper's reduced model. Electron1 is the scattered incident electron and electron2 is the ionized electron in the derivation. The energy partition in those labels is asymmetric. For unlabelled physical observables, sum both outgoing contributions; do not double the event cross section. An inclusive single-electron spectrum integrates to2 per event, whereas the event law integrates to1. If needed its symmetric energy marginal follows by adding p(E2+I|E) and the reflected labelled marginal. At this order, the summed energy and isotropic second tensor do not depend on how energy is shared beyond E1+E2=E-I.

The normalized CDF and inverse are new algebraic consequences of the cited differential law:

\[
F(\Upsilon\mid E)=\frac{E(\Upsilon-I)}{(E-I)\Upsilon},\qquad
\Upsilon(u)=\frac{IE}{E-u(E-I)},\quad 0\le u\le1.
\]

They provide a positive finite-interval quadrature/sampling transformation with endpoints I and E. No Monte Carlo simulation is required to verify normalization or summed energy.

## Physical boundary

The source reduction requires m_e/M much less than1 and m_e/M much less than T_e/T_t; it approximates the relevant reduced masses by m_e. Its full paper permits drifting Maxwellians, but the HE37 selected scope is common bulk, fixed target/heavy limit, common reference T and an infinitesimal incoming electron STF perturbation. Product momentum can be transferred to the heavy reservoir with negligible leading-order recoil energy. Finite-mass recoil and finite target thermal velocity are not supplied by replacing the mass in the heavy kernel. Photon processes, nuclear reactions, anions, molecules, arbitrary isotopes, high-amplitude non-Maxwellian closure and cosmological evolution are outside this selection.

In the selected isotropic kernel the outgoing STF gain vanishes, while the scalar gain does not. Adding gain to incoming loss changes electron number by +1 per event and kinetic heat by -I per event; it must not use -E as net heat. An energy-weighted l=2 angular moment remains needed to replace isotropy by a calibrated differential H1 model. The current adoption is explicitly conditional on the isotropic semiclassical approximation and makes no new strong no-go or originality claim.

## CCC author archive audit

Author landing page: https://atom.curtin.edu.au/CCC-WWW/index.html . Current H1 link: https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/e-H_XSEC_LS.zip . Retrieved ZIP 7010887bytes, SHA256 `57730e72656639e92c47c1b8457db0edac5a69ae93db6c357471a93759af1fc9`; server Last-Modified 2026-10-12T13:11:04Z. Catalog has3162members. Both READMEs explicitly define integrated cross sections; TICS denotes total ionization. Catalog and representative headers support that this downloaded package supplies integrated transition/total tables, not a differential angular provider. This statement is about the inspected archive, not all CCC calculations or all possible unpublished data.

The contained `TICS.1S` is5754bytes and has SHA256 `7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae`, byte-identical to HE36. No scientific recalculation follows from redownloading identical data. No permissive redistribution license was discovered in the README; attribution is retained, and the complete ZIP remains scratch evidence rather than a new public code dependency.

## Search scope

One Exa query returned6results; one SciSpace natural-question search returned10papers. Primary strong-search follow-up and source reads were limited to finding usable differential data or a complete published approximation. The DDCS/TDCS literature includes restricted energies/geometries; no complete machine-readable H1 angular provider was admitted from those results. NIST's advertised H/He/H2 singly differential cross sections alone do not establish the outgoing l=2 moment. Search output counts are retrieval counts, not full-paper reading counts. Raw tool responses are saved under `raw/`.

## Deliverable split

This report plus compact provenance JSON can be copied into the new Git-backed unit. The downloaded PDF, full author ZIP, page screenshots and unabridged search/source extraction remain private scratch/intake evidence. New code must carry the selected constants, physical approximation and outgoing counting contract. Independent derivation and affected checks are separate from this source-admission result.
