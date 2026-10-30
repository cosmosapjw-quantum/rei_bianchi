# F4 OCR-free source-cone physics report · 2026-10-30

**Bounded objective:** replace PR284's OCR-partial 21-point 2E1 distribution by proven positive cone and conditional-monotone-cone spectra to establish source-number-independent frozen BASS193 optical absorption bounds; no IVP, no false full RT.

Original immutable PR284 complete source ZIP SHA256 `fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9`; parent HEAD `661f34c5216aa52402be6f9db5c16ab2e55ecfb3`. Original Draco scanned glyphs remain unresolved.

Actual new physical data: **193 epoch envelopes**, **4,825 native channel envelopes**, **7,720 generator responses**, two PNG; source native 21 species, 193 archived BASS epochs. All outputs are *new data calculated on the original source states*, not inferred from abstracts.

## Frozen physics sample

At z=20, P2 positive **[0,1]**, monotone **[0.567724678225374,1]**, old OCR-witness 0.7212181903340495. At z=2, P2 positive **[0,0.00228246]**, monotone **[0.000893456128546894,0.0015216821922610583]**, old OCR-witness 0.001115920147001298.

## Source-integrated across ALL original saved epochs, ONE fixed spectral shape

| Linear quantity and dimension | Positive 21-knot cone | Nondecreasing 21-knot cone | Parent witness |
| --- | --- | --- | --- |
| Two initial photoabsorption events per baryon | [0, 3.0150735281263275e-11] | [1.711724978952485e-11, 3.0150735281263275e-11] | 2.1745145060967717e-11 |
| Initial electrons per baryon | [3.014964386404465e-11, 6.030173483550272e-11] | [4.7267925430011114e-11, 6.030173483550272e-11] | 5.189586318243342e-11 |

## Blind-style same-author adversarial review

Referee question: Is a model source-agnostic if the basis uses 1969 table ordinates? **Answer:** Basis construction uses only grid 21 knots, original BASS21 gas and physical 2E1 total energy; original A_TAB only to reconstruct parent witness. Distinguish SHAPE_MODEL identity from numeric ORDINATE identity.

Referee objection: Unqualified monotonicity is physically necessary? **Counterexample:** a single positive nonmonotone hat on y=.025 yields z20 P2=0 while monotone-family lower bound=.5677. Therefore no unconditional claim of monotonicity from the proof.

Referee objection: Can the epochwise minimum be integrated to get a sharp global source bound? **No:** it allows epoch-dependent spectrum; generator response is integrated over all 193 epochs before extrema.

Referee objection: Does sharp bound apply to covariance/TV? **No:** probability channel and electron count are linear in p, but covariance and TV after marginals are nonlinear. No bound claim for those in this new theorem.

Referee objection: Is the 1969 original Table II digit source visually verified? **No**, direct bitstream unavailable; use CHIANTI derived table as potential independent source, but it is not yet downloaded or checked and cannot certify original pixels.

Referee objection: Is the physical absorbed electron number a self-consistent chemical evolution or gas heat? **No:** static fictitious Hubble-length gas and all-singlet hypothetical source; actual redshift integrated ionization, heating and CMB τ HOLD.

Referee objection: Is this a formal interval numerical certification? **No:** finite quadrature 8 vs16 checked; sharpness exact for mathematical 21-knot cone, numerical extrema have un-certified ~1e-15 quadrature residual. Formal MPFR interval proof NOT_RUN.

Source `DIFFERENT_AUTHOR_BLIND_REFEREE=NOT_RUN`; this review is a single same-author adversarial pass plus Wolfram CAS independent algebra mechanism, not a distinct researcher. Scientific DIL publication cannot promote absent gates.

**Acceptance:** new source-scoped auxiliary 1/1, original Working 33/88; Central 28/88; Physical Fast 4/7; Δ0; F4 PARTIAL; L4_ready=false; NO_MORE_IVPS true, NO_MERGE, NO_FORCE_PUSH, AUTO_NEXT_NODE false, NO_BUDGET_RESET true. The next physical source owner is original table image and genuine Li+ residual singlet/triplet yields or full REI17/BASS21 common F/J+thermal+radiation clock.
