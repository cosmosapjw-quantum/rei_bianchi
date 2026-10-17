# Primary coefficient intake: elemental carbon

The admitted provider ingredients are the actual ground-state elemental-carbon electron-impact ionization (CI), radiative recombination (RR), and dielectronic recombination (DR) fit coefficients. Carbon charges q=0,...,6 form a complete adjacent charge chain for these three declared processes. This is not a complete atomic cooling/radiation model, and it is not an isotope-native 12C or 13C dataset.

The exact source identities, hashes of downloaded original tables, bibliographic references, and source-version dates are in `SOURCE_REGISTRY.json`. Small exact selected rows and a normalized factual schema are in `../../data/`. Original full tables were downloaded only as scratch intake inputs. Their hashes identify the upstream snapshots; selected row files are exact source lines. JSON source-line numbers are one-based original-file lines. Missing optional RR C,T2 columns mean C=0; JSON records these zeros explicitly.

## Equations and conventions

For CI, use Voronov (1997), DOI 10.1006/adnd.1997.0732, with U=I/(k_B T):

C_q(T) = A (1 + P sqrt(U)) U^K exp(-U)/(X+U).

I is the tabulated ionization energy in eV, A and C_q have units cm^3 s^-1, and P,X,K are dimensionless. The official `cfit.f` evaluator uses k_B=8.617385e-5 eV/K. Preserve that literal for a source-faithful evaluator; do not label it current CODATA. Its implementation truncates U>80 to zero. This truncation is irrelevant inside each admitted CI fit domain and is not a reason to extrapolate to cold temperatures. The original table N is the *initial* number of bound electrons: q=Z-N, with q -> q+1.

For RR, use Badnell's official Kelvin table, version 20230511:

b(T)=B+C exp(-T2/T),

alpha_RR(T)=A / [sqrt(T/T0) (1+sqrt(T/T0))^(1-b(T)) (1+sqrt(T/T1))^(1+b(T))].

A and alpha_RR have units cm^3 s^-1; T,T0,T1,T2 are Kelvin; B,C are dimensionless. Do not accidentally treat b(T) as a constant in a temperature derivative when C is nonzero. Badnell N is also initial bound-electron count, q=Z-N, so RR maps q -> q-1. M=1 selects the initial ground level; W is preserved source metadata, not a multiplicative rate factor.

For DR, use Badnell's official Kelvin table, version 20230512:

alpha_DR(T)=T^(-3/2) sum_i c_i exp(-E_i/T).

E_i is Kelvin and c_i has units cm^3 s^-1 K^(3/2); the rate is cm^3 s^-1. The source places all c rows before all E rows; pair on (Z,N,M,W), not line proximity. Preserve negative fit coefficients: carbon initial N=2 has c3=-7.843e-4. Individual fit terms are not separate positive reaction channels. Rate positivity applies to their total. Bare C6+ has no core electron to excite, hence DR is a structural zero, not a missing tabulated channel filled by an approximation.

## Temperature domains

CI initial q=0,1,2,3,4,5 has source Tmin = 1,1,2,3,20,20 eV, respectively. Every carbon CI row has Tmax=20 keV. Domain checks must use each row independently.

Both Badnell documentation pages describe their standard ADAS tabulation temperatures as [10 q^2, 10^7 q^2] K, where q is the initial target charge. Adopt this conservatively as the supported interval for each RR/DR channel; it is not an independently verified universal fit-accuracy bound. In particular RR q=1 starts at 10 K, q=2 at 40 K, and q=6 at 360 K. A complete carbon CI+RR+DR-chain calculation shares only [20/(8.617385e-5), 10^7] K. Do not impose that hot lower bound on an independent cold RR query, or silently allow a complete CI chain below it. The source warns of relativistic distribution effects above approximately 10^8 K; the common chosen interval is below that warning regime.

These are low-density ground-level Maxwellian-electron coefficients. Metastable mixtures, three-body effects, DR density suppression, charge exchange, and non-Maxwellian distributions require additional models or data.

## Radiation, cooling, and isotope boundary

A photoionization rate is a radiation integral, Gamma_q=4 pi integral[J_nu sigma_q(nu)/(h nu)] dnu, and cannot be promoted to a T-only coefficient without a separately frozen J_nu and radiative-transfer convention. CI energy loss I*C_q can be derived as the electron energy removed into ionization potential under an explicitly stated energy bookkeeping convention; it is not the total carbon cooling coefficient. Number recombination coefficients alone do not specify emitted-energy moments, line cooling, or a complete thermal closure.

The source tables identify Z, electron count and initial level, not isotope mass number. Any use with 12C/13C population labels would require a declared isotope-independent approximation or new isotope-native data and is outside this provider's authority. An abundance-weighted atomic mass is also not supplied here.

## Reuse and discovery assessment

SciSpace was used for literature discovery and Exa for primary-source discovery and inspection. SciSpace returned a misleading 2022 metadata year for the Verner-Ferland 1995 arXiv/1996 journal work; primary author pages controlled the bibliographic decision. Verner-Ferland RR alone covers only three carbon recombination transitions and therefore was not selected as a full-carbon provider. Badnell fills the actual full chain; no hydrogenic replacement was invented.

No explicit SPDX or blanket redistribution license was found on the inspected author pages. Badnell tables have copyright attribution. The authors publicly offer the fit tables for plasma modelling. This intake preserves a small factual selected coefficient subset, attribution, source identity and independently authored schema/notes; it does not copy upstream code or full papers, or assert that the whole upstream database is public domain. Licensing of upstream software/database redistribution remains unspecified.

## Additional source coverage, not yet admitted implementation

Mechanical inspection of the same exact downloaded tables found full ground-state CI/RR/DR charge coverage for Li, N, O, Ne, Mg, Si, and S in addition to C. Their CI common lower limits are respectively 5,30,40,70,100,200,200 eV, with a shared upper CI bound of 20 keV. Their common supported RR/DR upper bound remains 10^7 K because q=1 is present. Per-channel domains and source-series bibliographic mapping still apply. These are ready coefficient candidates, not implemented or isotope-native claims. Fe lacks RR and DR initial N=16,17,19,20,21,22,23,24,25 in these tables, so this source combination does not supply a complete Fe chain. No gap is to be filled silently.

Only source parsing and coverage inspection were performed during intake. No scientific rate evaluation, simulation or benchmark was run by the source-intake agent.
