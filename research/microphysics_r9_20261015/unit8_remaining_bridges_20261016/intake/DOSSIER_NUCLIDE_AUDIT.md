# Dossier-driven nuclear and atomic state audit

The attached *Reionization: Microphysics, Transport and Observation* is actively used here to fix the state mapping, excluded ancestry, baryon constraint and covariance interpretation. It does not supply a replacement BBN network or measured nuclear covariance. D's frozen source-native small-network calculation is compatible with these distinctions and may execute within its existing limits. No additional BBN solve, source edit or change of priors is required by this audit.

Source: `upload/Reionization_Standalone_Dossier(3).pdf`, 73 PDF pages, 967541 bytes, SHA256 `179b114f60c1f8923f9faffb7218a90f1189667c335922525cb6247a174e85a3`. Page citations below give PDF page first and the printed page in parentheses. Text was read from the local extraction `dossier_u8_extract.txt`. The dossier is an owner-supplied theory source; its numerical examples retain their stated conditional assumptions.

## Exact seventeen-state census

Equation (1.15), PDF 8 (3), has **17 atomic/nuclear entries spanning seven isotope reservoirs**, not 17 isotopes:

| Isotope | Exact retained charge entries | Baryon weight per entry | PRIMAT reservoir |
|---|---|---:|---|
| neutron | n | 1 | n |
| hydrogen-1 | H0, H+ | 1 | p |
| deuterium | D0, D+ | 2 | H2 |
| tritium | T0, T+ | 3 | H3 |
| helium-3 | He3_0, He3_1+, He3_2+ | 3 | He3 |
| helium-4 | He4_0, He4_1+, He4_2+ | 4 | He4 |
| lithium-7 | Li7_0, Li7_1+, Li7_2+, Li7_3+ | 7 | Li7 |

The ordered vector is `[n,H0,H+,D0,D+,T0,T+,He3_0,He3_1+,He3_2+,He4_0,He4_1+,He4_2+,Li7_0,Li7_1+,Li7_2+,Li7_3+]`. Nuclear abundances are numbers per baryon. The mapping is `y_Aq=Y_A sum_alpha P_Aqalpha`, with each isotope's conditional probabilities normalized over charge/internal states, Eq. (1.14). PRIMAT's nuclear outputs do not determine those probabilities. A scalar electron fraction likewise cannot determine them (PDF 35 / printed 30).

Be7 is an **auxiliary isotope outside these seventeen entries**. Retaining its reservoir and later charge-resolved electron capture is mandatory whenever that ancestry is material; it cannot be silently assigned to Li7 at the BBN endpoint. Electrons/positrons, photons, molecules, negative ions, extra nuclei and nonthermal populations are separate sectors (PDF 8–9 / printed 3–4). The dossier does not provide a complete molecular/negative-ion list or their rates, so naming their sector is not a claim that their physics is implemented.

## Actual donor and source-native census

The immutable large-network donor is `inputs/laneA/donor_R5_DONOR_BBN.json`, with 59 distinct `result.Y_final` entries. All 59 are accounted for below; none is discarded or renormalized.

| Partition | Exact isotope entries | Count |
|---|---|---:|
| Seven retained reservoirs | n, p, H2, H3, He3, He4, Li7 | 7 |
| Explicit Be auxiliary | Be7 | 1 |
| Other omitted ancestry | He6; Li6, Li8, Li9; Be9, Be10, Be11, Be12; B8, B10, B11, B12, B13, B14, B15; C9, C10, C11, C12, C13, C14, C15, C16; N12, N13, N14, N15, N16, N17; O13, O14, O15, O16, O17, O18, O19, O20; F17, F18, F19, F20; Ne18, Ne19, Ne20, Ne21, Ne22, Ne23; Na20, Na21, Na22, Na23 | 51 |

Direct arithmetic on those actual donor numbers gives:

| Quantity | Value |
|---|---:|
| Full baryon sum | 1.0000000000016263 |
| Seven-reservoir baryon sum | 0.9999999973520842 |
| Excluded baryon abundance, 52 isotopes | 2.649541940299385e-9 |
| Be7 baryon abundance | 2.6494959656705533e-9 |
| Other 51 excluded isotopes' baryon abundance | 4.5974628831871203e-14 |

These are deterministic donor diagnostics, not uncertainty estimates. The finite arithmetic residual is recorded rather than normalized away. The omitted-ancestry optical bound in Eqs. (1.22)–(1.23), PDF 10 (5), additionally requires positive linear evolution, conserved baryon weights, a prescribed non-tilted background and no pair creation/external tagged source. It controls direct tagged electrons/column, not indirect thermal feedback or catalysis; no optical number is assigned without the required background integral.

The pinned provider's `primat-c/src/network_data.c:483` gives the small-network order `[n,p,H2,H3,He3,He4,Li7,Be7]`; `primat/data/nuclear/networks/small.txt` supplies its 12 thermonuclear reactions. The native CLI appends **every tracked nuclide** to its MC quantities (`primat-c/src/cli.c`, quantity assembly around lines 1521–1544). Thus D retains eight native nuclides, seven core reservoirs and Be7, with their joint samples/covariance. The 51 other donor isotopes are **absent from this model**, not measured zero and not covariance-constrained by D. D's small network also differs from the donor's large bare-Be overlay. Shared commit and cosmology do not make their covariance interchangeable.

## Relevant equations and source boundaries across the dossier

| Dossier source | Content used | Consequence for this work |
|---|---|---|
| Scope, PDF 5 (iv) | Conditional calculations are separate from empirical uncertainty and calibrated source histories. | No numerical covariance is fabricated for unspecified physics. |
| Ch. 1, PDF 7 (2), Eqs. (1.3)–(1.8) | One event supplies species and energy-momentum changes; baryon and charge contractions; normal/proper-density distinction. | Conserve baryon-weighted nuclear number, not the unweighted number of nuclei. BBN common-rest-frame mapping is not a general tilted transport result. |
| Ch. 1, PDF 7–8 (2–3), Eqs. (1.9)–(1.13) | Translating electrons enter heat capacity; changing particle counts and nonthermal injection affect temperature. | Nuclear fractions alone do not close electron/thermal evolution. |
| Ch. 1, PDF 8–9 (3–4), Eqs. (1.14)–(1.21) | Charge lift, exact17, baryon stoichiometry, mass convention, finite time origin and Be electron capture. | Preserve H3/He3 and Be7/Li7 separately, actual endpoint time, free-electron rest energy once, and the charge-dependent decay hazard. |
| Ch. 1, PDF 10 (5), Eqs. (1.22)–(1.24) and surrounding text | Excluded ancestry, selector covariance, full baryon null variance and shared-parameter tangent. | Compute `B_R`; no core renormalization; linear projection `L C L^T`; report baryon residual/variance. |
| Ch. 1, PDF 10–20 (5–15), sections 1.4–1.14 | Radiation transport, opacity, material clock and finite observer bins. | A composition covariance is an initial-data input, not a completed optical-depth/source-history uncertainty. |
| Ch. 2, PDF 22–26 (17–21), Eqs. (2.2)–(2.29) | Finite-mass hydrogenic E1 physics and separately stated infinite-mass ground-state continuum model; kinetic/internal/radiative energy moments. | Applicable to declared one-electron sectors, including H/D/T, He+ and Li2+ with their masses; cannot replace neutral He or neutral/singly-ionized Li multielectron rates. |
| Ch. 2, PDF 26–29 (21–24), Eqs. (2.30)–(2.45) | Cascade injection, finite line delays and their full parameter derivatives. | Terminal charge selection alone does not specify excited populations or photon production times. |
| Ch. 2, PDF 29–31 (24–26), Eqs. (2.46)–(2.54) | Sudden one-electron daughter overlap and beta-phase-space weighting; tritium example. | H3 ancestry remains explicit; quench probabilities are not automatically physical decay branching fractions or thermal heating. |
| Ch. 2, PDF 31–34 (26–29), Eqs. (2.55)–(2.72) | Radiation-weighted rates; stoichiometric conservation and chemical/kinetic energy; restricted detailed balance. | No species/rate closure from one mean electron energy; H-only example does not replace full17 chemistry. |
| Ch. 2, PDF 34–35 (29–30), Eqs. (2.73)–(2.75) | Conditional HYREC reference and empirical covariance distinction. | Its stated cosmology differs from D; neither its table nor scalar xe specifies our17-state matching surface. |
| Ch. 3, PDF 36–46 (31–41), especially section 3.9 | Restricted H–H ionization model and transfer into gas/electron/energy equations. | A hydrogen collision kernel is not a rate provider for all isotopes and charge states. |
| Ch. 4, PDF 47–49 (42–44), Eqs. (4.1)–(4.11) | n+p↔d+gamma; threshold regularization, reciprocity and distinct stationary/thermal ensembles. | Separate native np-EFT amplitude work from PRIMAT empirical reaction-prior propagation; no inferred EFT parameter/truncation covariance. |
| Ch. 5, PDF 50–62 (45–57), especially Eqs. (5.4), (5.62)–(5.66) | Nonthermal-to-thermal transfer conserves total electrons; H/He proper-density closure and common electron current. | Electron inventory is outside17; H/He illustrative closure neither deletes trace nuclei nor derives their charge histories. |
| Ch. 6, PDF 63–67 (58–62) | Finite-aperture polarized detector and radiation response. | Adds no nuclides or rate census; downstream covariance needs its own detector/source derivatives. |
| Ch. 7, PDF 68–69 (63–64), Eqs. (7.1)–(7.11) | Complete event variations, proper/normal fractions and constraint residual forcing. | A numerical baryon residual must be measured, not eliminated by renormalizing samples. |
| Ch. 7, PDF 70–71 (65–66), Eqs. (7.14)–(7.24) | Eliminated-species memory, shared-parameter covariance, joint daughter law and proper decay time. | Omitted nuclei may have retarded daughter effects; do not assign independent copies of shared uncertainty or mistake marginal spectra for joint laws. |

## Minimal executable consequence for D

`spec/DOSSIER_NETWORK_CONTRACT.json` adds postprocessing only. Preserve all native8 sample columns and their covariance; compute the seven-reservoir selection, Be7 and `B_R=7Y_Be7`; report full baryon sums and their sample variance. A fixed bare-charge lift supplies an explicitly conditional17 bookkeeping vector with zeros in other charge slots. It is **not** a computed late-time charge state. For that lift and an appended excluded-baryon coordinate, use the same linear map on every existing sample and its full covariance, keeping cross-covariances. Fixed zero slots have zero covariance and undefined correlations; never add jitter or treat these expected zeros as an MC failure.

For a general physically supplied charge law, replace the bare lift by its actual conditional map and propagate any uncertain charge probabilities jointly. No 17-state matching/history, additional large-network prior run, complete reionization history, or original-donor covariance is admitted by the conditional bookkeeping output. The existing build30s/numerical30s, nominal+tight+pilot8+at-most-one chosen ensemble limits remain unchanged. PASS leads immediately to bounded native execution and independent review.
