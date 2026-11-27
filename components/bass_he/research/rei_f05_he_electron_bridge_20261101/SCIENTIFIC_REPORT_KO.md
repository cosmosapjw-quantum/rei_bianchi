# BASS_HE → REI-F05: original source H/He electron increment (2026-11-01)

## Owner and physical contract
Scientific contributor: cosmosapjw-quantum/BASS_HE. Original source owner/central receiver: cosmosapjw-quantum/rei_bianchi. Immutable parent BASS_HE PR143 HEAD 99b03e5c7ade74bfb87d8149167c011b4467e680. Input source: central REI Draft PR348 HEAD fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120, original 26-event MPRK22(1)+SDIRK2 first accepted tick160/131072. No source, solver, original state, clock, tolerance or production mutation.

The actual CI 41292070383 artifact has 3 technical lanes of the SAME 46080 physical nodes. All three original CSV.gz inputs have identical SHA256 f20ae64ff11765c6d3d09b2a728ad648630353bd8fefaa1595b1867051932b85. Each original RESULT.json binds matching named lane, original state array cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01, accepted tick160, 14 original ledger tests, canonical delta0.

## Exact species reconstruction
Original atomic-number budget per H nucleus with original primordial nuclei ratio eta=N_He/N_H=79/1000:
  n_e/N_H = x_HII + eta*(x_HeII+2*x_HeIII).
For any SAME native step realization, delta(n_e/N_H)=delta x_HII + eta*(delta x_HeII+2*delta x_HeIII).
Helium conservation also implies delta(x_HeII+2x_HeIII)=-delta x_HeI+delta x_HeIII.
Wolfram symbolic conservation check residual: exactly 0 (same author CAS check).
This identity is evaluated on each ORIGINAL full, twohalf and joint-input-cancelled-defect interval from the REAL REI PR348 30-column source CSV. Derivation is exact at original discrete-map semantics; arithmetic takes exact Fraction images of source IEEE754 binary64 endpoints and one outward ULP for serialized result. Interval validity inherits the native original REI/Krawczyk enclosures; this is not fresh formal MPFI verification.

## Physical results, new actual 46,080-row output
- H full ionized-fraction increment CERTAIN NEGATIVE in 42,534/46,080 original source cells.
- He electron increment contribution CERTAIN POSITIVE in 11,862 cells, with 11,610 having certain H-negative and certain He-positive simultaneously.
- Total electron number increment per H CERTAIN NEGATIVE in 43,392 cells.
- All 46,080 derived electron local-error defect intervals include zero, which is NOT evidence that the local error itself vanishes.
- Global across-cell ranges (extrema may occur at different cells):
  H full [-3.6207084320705834e-5, +1.9745473976857225e-6];
  He full [-3.715579423072624e-6, +4.2821108480887677e-7];
  total e full [-3.992266374377846e-5, +2.402758482494599e-6].
  He defect [-1.8324652169089471e-7, +1.8322734279615155e-7];
  total e defect [-3.6104001854973116e-6, +3.5918440728191527e-6].
- New compressed 46,080-row, 15-column numerical artifact results/REI_F05_H_HE_ELECTRON_46080.csv.gz, SHA256 dc340b3be3f939b984bc87434644cda8b799f99264000f9a73a8dbb3906361d2 (check latest RESULT.json).
- Generated result is a new species-resolved scientific electron-source response on the ORIGINAL first F05 source clock; not merely a source-cone atlas or a new cosmological IVP.

## Adversarial scope: what it does NOT establish
Cell count and sign certainty are derived from original *interval enclosures*, not probabilistic samples or independent 3-lane astrophysical data. Original He/H=0.079 is a source convention. Electron count per H is NOT proper electron density: requires original nuclei proper volume/history for n_e^proper. It cannot be plugged into independent F08 S0 Thomson line-of-sight histories without matching source clock, state, expansion/shear, spatial ray mapping and density. It cannot alone establish updated tau_CMB, ionization history or observational constraint. Original PR348 proposed correlation-preserving local-error certificate remains only candidate pending original REI owner's adoption; 160/131072 frozen, no newly accepted tick. Native source spectral J_nu, species opacities/heat owner remain RUX03_UNBOUND, P19 effective UVB remains RUX04_NOT_ADMITTED, no generalized UVB no-go.

## Claim & deployment
MATHEMATICS=DERIVED; CAS_CONSERVATION=SYMBOLICALLY_CHECKED; SOURCE_AUTHENTIC_NUMERICAL_OUTPUT=CHECKED_ON_ORIGINAL_46080_CELLS; IMPLEMENTATION=TESTED_LOCALLY; DISTINCT_AUTHOR_REFEREE=NOT_RUN; NATIVE_SUBAGENT=NOT_RUN. Validity conditional on original PR348 inherited interval algorithm and actual source identity. A source-informed data contribution, but no canonical DAG admission. REI Central 28/88; Working 33/88; Fast 4/7; BASS_HE Physical 14/18, canonical delta0; PRODUCTION=HOLD. Do not merge, force push, reset budget, start new IVP or convert F05 into F08 without actual same-clock owner.
