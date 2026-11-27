# BASS_HE PR129 original nuclear-source + neutral stopping bridge (2026-10-30)

## Authority and original source identities
Parent immutable PR128 HEAD `e218b1fdccbc8c3e156d9f70805fe8a9048604f8`.
1998/2000 Rice campaign retained once. New Asbury-Loeffler 1965 **one independent campaign**,
two original *absolute differential* cross-section observations at source mean photon energies.
Asbury & Loeffler, Phys Rev 137, B1214–B1220 (1965), DOI 10.1103/PhysRev.137.B1214,
Table II paper p.B1218 / provided PDF page 5. Their full/event cross sections are
**reported author-model integrals**, not independently measured.
Original PDF SHA256 `954042ad95c1aab77a84b9a402ccf9dc213403723a93820d4aeebcddaa51d75c`.

Williamson, Boujot, Picard, CEA-R3042 (1966), "Tables of range and stopping power
of chemical elements for charged particles of energy 0.05 to 500 MeV", report
pp.76 and 78, provided PDF pages 90 and 92, 12 source tabulation entries.
Original PDF SHA256 `e5ff9c4e9b3d635103935c0fefb3a6e11988ec9ebe90150da686666d06568652`.
These are **author-calculated empirical elemental stopping** entries, not independently
measured astrophysical plasma stopping. The PDF's erratum page 388 explicitly
replaces **report pp.223–296**, NOT pp.76/78. The report defines range as actual
track-length mass thickness; projected range needs scattering corrections.
The report itself cautions on accuracy and media applicability.

Drake, Victor, Dalgarno Phys Rev 180, 25 (1969) (`213a9a620dbb9b5cc63ccdab246e6564018cc3262629d13303879ac133b59b95`)
is source-relevant to atomic Li II/He-like two-photon decay lanes but
**not** a 150–250 MeV gamma field, and must not be used as one here.

## Two new measured cross sections
- E_gamma_mean=220.5 MeV, theta_CM=52.4 deg:
  DA=(6.3 ± 2.2) nb/sr; paper sigma_tot=(22.3 ± 7.9) nb
  under sin^2(theta)cos^2(theta) angular ansatz.
- E_gamma_mean=265.3 MeV, theta_CM=53.2 deg:
  DA=(1.5 ± 1.1) nb/sr; model-dependent paper sigma_tot=(5.4 ± 3.8) nb.
Two DA points are one campaign and are distinct from Rice's campaign.
The second mean photon energy is beyond Rice 250 MeV upper bin.

## Derivation and units (metric -,+,+,+)
Let M_alpha c²=3727.3794118 MeV, m_d c²=1875.61294500 MeV,
Q=(2m_d-M_alpha)c²=23.84647820 MeV.
For target alpha at rest and a gamma of source-reported mean E,
s_E=(M_alpha c²)²+2(M_alpha c²)E.
K_±=(E-Q)/2±(E/2)sqrt(1-4(m_dc²)²/s_E)cos(theta_CM).
This is **exact at specified (E,theta)** but experimental E is source average, not
actual individual event energy. The derived four K records in the results must
therefore be labeled `nominal`, not `source_measured`.
K_++K_-=E-Q exactly, and the two daughters are not two experiments.
At E=220.5 MeV: 118.985783272801 and 77.667738527199 MeV.
At E=265.3 MeV: 147.482229691252 and 93.971292108748 MeV.

Use *source-specific* linear interpolation only between adjacent CEA entries at
50,60,75,100,125,150 MeV. Units: `R` g/cm², `S_mass` MeV cm²/g.
`S_mass=-dK/d(ρl)` is NOT a time-dependent plasma stopping rate.
No continuation outside 50-150 MeV and no neutral-to-ionized transport.
The event energy available for fast-D kinetic energy is E-Q and is not all heat.

## Angular model self-check
For author assumption dσ_ord/dΩ = C sin²θ cos²θ and identical final-state d:
σ_event=(1/2)∫dΩ dσ_ord/dΩ
=(4π/15) C. Consequently σ_event/DA(θ)=(4π/15)/(sin²θ cos²θ).
Direct use on printed source DA gives 22.585 nb at 220.5 (printed 22.3 nb)
and 5.462 nb at 265.3 (printed 5.4 nb). Discrepancy is compatible with
printed rounding and differences in author acceptance integration; this check
is **not** an independent total cross-section measurement.
Under normalized event-angle measure w(mu)=15/4 mu²(1-mu²),
<mu²>=3/7, compared with Rice M1 (<mu²>=1/5). DO NOT pool these models.

## Scope of model comparison
Asbury mean E=220.5 overlaps Rice 190–250 broad energy bin but Rice's
reported source-bin and angle-bin weights, acceptance/covariance are unknown.
The measured DA at 52.4° is not pointwise comparable to Rice's
45.4°/63.6° *bin averages* without a response model. The different
published normalizations are a research lead, NOT a statistical rejection,
and the two event-total model fits are not independent measured total SIG.

## Adversarial scientific audit (same author, one finite pass)
- Finding 1 (BLOCK if misclassified): CEA 1966 range is neutral elemental
  track-length mass thickness, not ionized primordial plasma deposition.
  Repair: type and unit labels in all JSON/CSV; leave heat_rate=null.
- Finding 2 (BLOCK if misclassified): Asbury total SIG is model-inferred under
  sin²θ cos²θ, not independently measured; do not double experimental count.
  Repair: separate DA source rows from reported model totals, 1 campaign.
- Finding 3 (CONCERN): printed mean beam energy/CM angle vs actual
  bremsstrahlung spectral response. Repair: all four daughter records `nominal`.
- Finding 4 (CONCERN): Rice M1 assumes sin²theta at every E; Asbury assumes
  sin²theta cos²theta at its two mean energies; no forced joint fit.
- Finding 5 (CONCERN): CEA author acknowledges empirical stopping uncertainty.
  No unsupported independent 5% statistical confidence bar assigned.
- Finding 6 (BLOCK for L4): unknown source-owned target-epoch He-rest
  n_gamma(E,Omega,x,t), n_alpha/U_alpha, ionized-plasma fast-D transport,
  nuclear secondaries/escape and heat capacity. Hold event/heat/kappa.

## Acceptance and decision
Measured DA 2/2 source-owned; CEA 12/12 modeled published rows; 4 nominal
daughter K with interpolated neutral media.
New source-scoped auxiliary `2/2` on *this bounded project unit*.
Canonical central 28/88 and HE physical 14/18 UNCHANGED; canonical delta 0.
L4 false, production HOLD, no merge/force-push.
R06 distinct-author and C09 distinct-author NOT_RUN; native subagent NOT_RUN.
