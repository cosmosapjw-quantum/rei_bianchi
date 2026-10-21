# Attached dossier reconciliation · 2026-10-22 series

The three PDFs supplied directly for this upgrade are the controlling editorial sources. This public record contains bibliographic titles, hashes and paraphrased scientific relationships only. Full extracted text stays outside the repository. PDF byte hashes identify the actual attachments; extraction hashes depend on the `pdftotext -layout` method and therefore should not be compared byte-for-byte with an earlier provider's extracted-text hashes.

| Attached source | PDF pages | PDF SHA-256 | `pdftotext -layout` SHA-256 | Editorial role |
| --- | ---: | --- | --- | --- |
| *Reionization: Microphysics, Transport and Observation* (14 Oct 2026) | 73 | `179b114f60c1f8923f9faffb7218a90f1189667c335922525cb6247a174e85a3` | `8fdd6d427a952e41c176ecbd332ee092805b5fbbf1d98263c78f86cb598b81d8` | Complete seven-chapter baseline. |
| *Reionization and Nonthermal Matter: Abundances, spectra, thermal evolution and observations* (14 Oct 2026) | 33 | `2efa8872985f152153a31ec2766c67b2b87dca9b83bd8c6d12d7a7024e1cb75a` | `d3a6eb0a9fe423efa92ccd5ce389c645153e775eec27675ef511e7558258a86d` | Later two-chapter series treatment, corresponding to baseline chapters 1 and 5. |
| *Nuclear Capture and Photodisintegration: Thresholds, reciprocity and thermal ensembles* (14 Oct 2026) | 7 | `0016c29fdf056327b558e8e3b10ca8182931fd77616442869aaeb533fb2738ea` | `4ce236db3947d77fd7db9b26963757f7bc9a3477a06473cac9de079172882144` | Specialized derivation of neutral capture and inverse thermal ensembles, corresponding to baseline chapter 4. |

The attached first and second files have the same title, PDF length and seven/two-chapter structure as the previously located backup versions. Their normalized text token sequences agree at roughly 91% under two different extraction methods, with different spacing and ordering of some displayed equations. This establishes a close content match, but no source byte comparison to the earlier cloud objects was available; do not label their binary hashes identical to a backup revision. The specialized nuclear volume is new to this intake and gives a direct primary derivation for the original chapter-4 formulas.

## Substantive nuclear correction map

| Topic | What the attached nuclear dossier actually supports | Required status in the upgraded work |
| --- | --- | --- |
| Scope and units | Its sole worked reaction is `n+p ⇌ D+γ`. Cross sections are m², capture coefficients m³/s, inverse rates s⁻¹. Relative/rest/thermal energies must be unit-consistent. | Cite it for this reaction and methodology only. The 18-family implementation needs separate provider and coefficient records. |
| Threshold regularization | A neutral `1/v` capture cross section can have finite `K(E)=σ(E)v_rel`; averaging over a Maxwell distribution can use a smooth `y² exp(−y²) K(kBT y²)` endpoint. Expansion coefficients give `K₀+(3/2)K₁kBT+(15/8)K₂(kBT)²+…`. | Preserve this structure when discussing low-energy neutral capture; it does not establish constant-S charged fusion behavior. Bound a truncated integration tail only after bounding the integrand outside the selected interval. |
| Photon reciprocity | For unpolarized n, p and D, the photodisintegration/capture cross-section ratio includes `2 p_np²/(3 p_γ²)`, where the incoming photon polarization average matters. | Do not exchange its `2/3` factor for the thermal equilibrium degeneracy `4/3`. Other channels require their own spin and identical-particle accounting. |
| Recoil and stationary target | Exact two-body kinematics shifts the example stationary D target's photon threshold above its binding Q by approximately 1.31923 keV for the stated equal-mass convention. The inverse integral uses an isotropic Planck field, not the pilot's 5–60 eV external UV. | Distinguish the positive but exponentially suppressed Planck tail from exact zero support in the model's compact UV spectrum. A new hard-photon transport source would require its own calculation. |
| Thermal target | A Maxwell–Jüttner/Møller-flux average and matching Wien photon ensemble yield a thermal detailed-balance factor with `4/3`; its leading nonrelativistic limit is `(4/3)[μ kBT/(2πℏ²)]^(3/2) exp[−Q/(kBT)]`. | Compare forward and inverse rates under the **same ensemble**. Do not place a recoil-shifted stationary threshold into a recoil-free equilibrium formula. Recoil shifts small versus nuclear rest energy may be large versus `kBT` at low T. |
| Numerical example | Its equal-mass effective-theory example uses `M=938.92 MeV`, `Q=2.224575 MeV`, and `K(0)=7.3524012×10⁻²⁶ m³/s`. Chen–Savage (1999) and Gondolo–Gelmini (1991) are the two cited methodological references. | Identify those values as a selected amplitude and mass convention. The newer evaluated 2200 m/s neutron-capture anchor is a distinct numerical provider; their spread is not a measured uncertainty interval. |
| Missing physics | It contains no calibrated low-temperature coefficients for DD, DT, He3+D, T+α, Li6 closure, p+T radiative capture, or 3He neutron transfer, and no energetic-daughter slowing or ion/heat deposition model. | Keep the current `100–10000 K` charged-rate extrapolations and instant thermalization explicitly conditional. It cannot validate observed T production or a fully coupled reionization history. |

The standalone volume's nonthermal chapter separately distinguishes active electrons from thermal electrons, their changing heat capacity, the thermalization front and optical sensitivity. The present trajectory solver prescribes gas temperature and does not evolve those degrees of freedom. The two-chapter curated volume is relevant to that distinction, but it does not replace the standalone chapters on atomic processes, hydrogen ionization, nuclear capture, finite observations and error control.

## Review actions for the new dossier

1. Keep the seven-chapter narrative and identify the attached three-volume relationship in the opening source note.
2. In chapter 4, cite the specialized nuclear dossier for `n+p ⇌ D+γ` reciprocity and ensemble distinctions only; cite the frozen coefficient registry separately for the implemented 18-family conditional network.
3. Keep `K(0)=7.3524012×10⁻²⁶ m³/s` distinct from the evaluated thermal-capture anchor `0.3326 b × 2200 m/s ≈ 7.3172×10⁻²⁶ m³/s`.
4. Do not use the stationary-target photon threshold to alter a thermal equilibrium inverse rate; do not conflate Planck-photon tails with the compact UV source.
5. Keep separate the local event-energy ledger, actual nonthermal stopping, daughter charge distribution and a solved thermal history. Their absence bounds the plots' physical interpretation.

No original PDF, extracted text, attachment path, cloud identifier or source page reproduction is published in this record.
