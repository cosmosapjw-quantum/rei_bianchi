# Dossier source intake (publication-safe)

The October 2026 upgrade uses two authored dossier versions as an editorial scaffold. The complete seven-chapter *Reionization: Microphysics, Transport and Observation* (14 October 2026) is the coverage baseline; the later curated *Reionization and Nonthermal Matter: Abundances, spectra, thermal evolution and observations* (14 October 2026) revises its opening and nonthermal chapters. The *Mathematical Verification Dossier IV: Cosmic Reionization, Ionising Radiative Transfer, and Thomson Rescattering* (revised 12 September 2026) is a supplementary formula audit. Extracted text hashes identify the two source versions without distributing their contents. The three PDFs directly attached for this upgrade, including the specialized nuclear volume, are reconciled in `ATTACHED_DOSSIER_RECONCILIATION.md` and are the controlling source set.

| Source version | SHA-256 of extracted text | Chapters used |
| --- | --- | --- |
| Seven-chapter standalone dossier, 2026-10-14 | `350c439e1e74f0427f9d714532e5de61bf1d3757e5f39425afaec5d533612174` | 1–7, comprehensive structure |
| Curated reionization volume, 2026-10-14 | `08ce4d50ca117f1936d76bb227f04715317c6097f90f67a11a7d44c02686357c` | Revised chapters 1 and 5 |

| Baseline chapter | Editorial coverage in the upgrade |
| --- | --- |
| 1. Covariant radiation and matter | Continuity equations, state census, quotient normalization, relativistic stress and closure. Correct the earlier 17-state discussion to the 21-state atomic pilot census, then distinguish the newer conditional nuclear extension. |
| 2. Atomic microphysics | Bound states, photoionization, recombination, line transfer, heating and energy accounting. |
| 3. Hydrogen ionization fronts | Spectral moments, impact ionization and transport approximations. |
| 4. Nuclear creation and destruction | Capture and thermally stimulated inverse reactions, with explicit low-temperature rate validity and an admitted network catalog. |
| 5. Nonthermal matter | Energetic secondaries, electron thermalization and deposition limits; incorporate the later curated revision. |
| 6. Finite-aperture observations | Polarization, angle dependence, path integrals and instrumental sampling. |
| 7. Approximation and errors | Conservation residuals, limiting cases and observability claims. |

The original chapter 1 normalization uses a nucleus-per-baryon census, `Y_A = n_A/n_B`, and baryon closure `sum_A A Y_A = 1`. This is distinct from a mass fraction or a charge-state conditional fraction. The previous pilot's tritium history was fixed to zero structurally; any new tritium curves must be labeled as conditional on the admitted low-energy nuclear coefficients and daughter-deposition treatment.

The original nuclear chapter provides capture and photodisintegration structure, but it is not a complete coefficient catalog for all reactions. The thermal reverse term is tied to the Planck photon bath and must not be silently identified with the ionizing 5–60 eV UV field. Earlier network sketches contain forward/inverse duplicate labels and omit some lithium-6 closure routes. The upgraded numerical section should rely on its own explicitly enumerated reactions, receipts, and verification results.

No original PDF, full extracted text, private storage identifiers, or unpublished source paths are included here.
