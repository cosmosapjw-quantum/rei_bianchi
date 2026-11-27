# BASS_HE: Fermi-LAT 2015 A/B/C × EXFOR M0475 measured-photon source calculation

Scope 2026-10-30 KST. Parent BASS_HE Draft PR116 frozen HEAD `93173f3c73f53e114616f524be73000688ab432b`. The PR114 low-energy E2 (3/4 scoped, 75 EXFOR rows) is a distinct sibling, not merged. BASS CE1-S PR262 is a model-energy sky map and does not authenticate a physical 200–400 MeV photon population through cosmic history. REI 5–200 eV UV backgrounds cannot be substituted for 200–400 MeV photons. Current Central 28/88, HE physical 14/18, old observed gamma 2/4 all remain unchanged.

## Source and units

Ackermann et al., ApJ 799:86 (2015), DOI 10.1088/0004-637X/799/1/86, Table 3, original CDS VizieR catalog J/ApJ/799/86. The *third-party GitHub mirror*, commit `774174d9faaa5df40b67af5fa42b4191f09d38c6` and blob `794cb6fcbef243be950613475c4254d6ab3877a4`, has 78 records, 26 each for correlated Galactic foreground models A/B/C. Full file was copied to this repository and local source artifact with identical Git blob. The original CDS server byte stream itself was inaccessible, hence original-CDS byte identity is NOT claimed. Numeric Table 3 fields and units were crosschecked to CDS ReadMe. Relevant 200.0–282.8 and 282.8–400.0 MeV bands retain integrated photon number intensities in photons cm^-2 s^-1 sr^-1, with directional BASIC errors (statistical PLUS instrument systematic), foreground systematics separately, and resolved-source reported flux.

Original nuclear experiment: EXFOR M0475003 from pinned IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871, six source reported SIG points at 201,225,253,285,320,359 MeV, cross sections 2.41,1.29,0.92,1.04,0.61,0.55 nb, statistical ERR-S only. No original measured 330 MeV total. Parent PR104 rest energy M_alpha*c^2=3727.3794118 MeV, m_d*c^2=1875.61294500 MeV, Q=(2m_d-M_alpha)c²=23.84647820 MeV. Signature (-,+,+,+); c=2.99792458e10 cm/s.

## Conditional physical formulation

Let J_b^X be the **published energy-bin integrated intensity** for X=IGRB or total EGB, b=1,2. Let g_b^F(E)>0 be a *specified* intra-bin spectrum, either flat or model-specific IGRB spectral fit g=(E/100 MeV)^(-gamma_F) exp(-E/Ecut_F), (gamma_A,B,C)=(2.32,2.28,2.26), Ecut=(279,206,233) GeV. The IGRB PLE shape applied to EGB is an additional surrogate assumption, NOT a measured EGB spectrum. Define normalized w_b(E)=g_b(E)/integral_{Emin_b}^{Emax_b}g_b(E)dE [MeV^-1]. Note each model F has its own correlated measured fluxes and uncertainties.

For source-reported SIG(E), interpolate linearly **only** between measured knots E_j=201,225,253,285,320,359 MeV:

sigma_rep^lin(E)=sum_{j=1}^6 sigma_j B_j(E), where all B_j>=0, sum B_j=1, support restricted [201,359]. No extrapolation across photon-bin edges 200,400 and no unmeasured 330SIG promotion.

For local *hypothetically isotropized* photon field coinciding with 4He proper frame, define

G_X,F,g^reported=4*pi*1e-33 cm²/nb * sum_b J_b^X * integral_{bin_b intersection [201,359]} dE w_b(E) sigma_rep^lin(E) [s^-1 He^-1].

B_X,F,g^reported is same expression with (E-Q) [MeV] in integrand. Number density (only if local isotropic coframe) n_gamma^X=(4*pi/c)sum_b J_b^X [cm^-3] over the FULL two observed bins, not only nuclear overlap. For EGB, resolved sources are NOT actually isotropic; the isotropic replacement is a diagnostic sky average, not a source-owned local radiation field. EGB is not IGRB + another standalone EGB component; NEVER sum them.

## Positive cross-section response and source uncertainty

At fixed measured flux J and spectrum g, G=sum_j A_j sigma_j, A_j=4*pi*1e-33 sum_b J_b integral_{overlap}w_b(E)B_j(E)dE [s^-1 He^-1 nb^-1], each A_j>=0. Therefore absolute sensitivity to nuclear pointwise ERR-S is delta_j=A_j*e_j. If their unknown covariance matrix is otherwise arbitrary but positive semidefinite with the stated diagonal, standard deviation lies within [max(0,2max_j delta_j-sum delta), sum delta]; conditional diagonal covariance gives sqrt(sum delta_j²). This interval describes covariance ambiguity **only for the interpolated source-reporting diagnostic**, not interpolation curvature/true exclusive sigma. Likewise Fermi BASIC up/down each propagate through nonnegative bin factors; report independence conditional and feasible unknown-correlation bounds separately. Galactic foreground model ± and A/B/C scenario spread are correlated systematic diagnostics, NOT independent statistical samples; neither their values nor nuclear ERR-S should be silently quadrature combined across all categories.

The mirrored source's published `fEGB` need not equal `fIGRB + fsrc` in the sampled high-energy bins to printed accuracy, particularly model B residuals 3.3% and 4.8% of EGB. `fsrc` is reported above |b|>20°, with separate analysis assumptions, and the three printed columns must NOT be forced into an exact arithmetic identity by changing source values. Preserve explicit discrepancy provenance; this is not a newly proved physical inconsistency.

## Scientific status

**Established original measurements:** Fermi 78 source-mirror records, with six relevant measured band/model rows, EXFOR six original reported SIG points. **Derived:** 12 modeled local source-weighted reported-sigma times flux diagnostics (3 FG models × 2 components × 2 spectral assumptions) and decomposed uncertainty coefficients, exact positive basis. **Numerically checked:** Python 20 targeted tests, exact rational flat-spectrum integrals, independent Wolfram flat-sector A/B/C rates and energy shell background from parent. **Unresolved:** original CDS raw byte restoration, Fermi actual z,t,x,Ω photon phase-space in He coframe, nuclear detector event/inclusive normalization, unmeasured spline curvature between source SIG points, two-source uncertainties/covariance, and nonthermal D_fast stopping, deposition, escape, secondary particles and C_V. `kappa=null;R_event=null;heat_rate=null;physical_activation=false;L4=false;production=HOLD`.

This science slice produces a NEW **auxiliary source-model A/B/C 3/4 scoped** once verified: D1 complete 78-row mirror identity/ReadMe map, D2 physical energy-bin and uncertainty data crosswalk, D3 physical-source-weighted conditional model/implementation; D4 original CDS byte-readback plus independent experiment interpretation unfulfilled. Original central/HE/old gamma auxiliary counters are unchanged, physical delta 0. No general no-go theorem or production activation is asserted.
