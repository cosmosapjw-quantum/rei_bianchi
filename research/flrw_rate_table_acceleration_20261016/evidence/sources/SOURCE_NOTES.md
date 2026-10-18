# Active primary coefficient intake: lithium

The user's scope correction before R6 selects lithium and its ions/isotopes as the only added nuclei. Earlier carbon source notes/registry are preserved without modification in `../../historical_unselected/carbon_sources_R5/`; carbon coefficient files and R1–R5 checkpoint packages remain historical unselected evidence. They are not active provider inputs.

The actual active electronic data are ground-state elemental-Li electron-impact ionization (CI), radiative recombination (RR), and dielectronic recombination (DR) fit coefficients. Charges q=0,...,3 form a complete adjacent charge chain for these declared processes. The upstream fit tables do **not** identify isotope mass number. `../../data/lithium_coefficients.json` therefore records `isotope_specific=false`, not isotope-native 6Li/7Li authority. Any isotope-native population integration must preserve isotope identity separately and explicitly declare whatever shared-electronic-rate approximation is authorized.

Exact source snapshot identities/hashes and primary references appear in `SOURCE_REGISTRY.json`. The actual selected source lines are `badnell_lithium_rr_rows.txt`, `badnell_lithium_dr_rows.txt`, and `voronov_lithium_ci_rows.txt` in `../../data/`. JSON source-line numbers are one-based original-file lines. No full upstream source code or papers were copied into the repository.

## CI convention and selected rows

Voronov (1997), DOI 10.1006/adnd.1997.0732, uses U=I/(k_B T):

C_q(T)=A (1+P sqrt(U)) U^K exp(-U)/(X+U).

I is eV; A and C_q are cm^3 s^-1; P,X,K are dimensionless. The original evaluator `https://www.pa.uky.edu/~verner/dima/col/cfit.f` uses k_B=8.617385e-5 eV/K. Preserve that historical literal for source fidelity; it is not a current-CODATA assertion. The evaluator truncates U>80 to zero, but every admitted Li CI domain lies below that cutoff. This does not license cold extrapolation. Original N is initial bound-electron count, q=Z-N, and CI maps q -> q+1.

| Initial q | I/eV | P | A/(cm^3 s^-1) | X | K | Tmin/eV | Tmax/keV |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5.4 | 0 | 1.39e-7 | 0.4380 | 0.41 | 1 | 20 |
| 1 | 75.6 | 1 | 2.01e-9 | 0.2090 | 0.23 | 4 | 20 |
| 2 | 122.4 | 1 | 9.60e-10 | 0.5820 | 0.17 | 5 | 20 |

## RR convention

Badnell's official Kelvin table version 20230511 uses

b(T)=B+C exp(-T2/T),

alpha_RR(T)=A/[sqrt(T/T0) (1+sqrt(T/T0))^(1-b(T)) (1+sqrt(T/T1))^(1+b(T))].

A and alpha_RR are cm^3 s^-1; all temperatures are Kelvin; B,C are dimensionless. Differentiate the temperature dependence of b(T) when C is nonzero. Badnell N is initial electron count; RR maps q=3-N -> q-1. M=1 selects the initial ground level. W is source metadata, not a rate multiplier. Absent optional C,T2 columns mean C=0 and are recorded as zeros in JSON.

| Initial q | N | A/(cm^3 s^-1) | B | T0/K | T1/K | C | T2/K |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 8.700e-12 | 0.3640 | 1.470e2 | 7.153e6 | 0.1508 | 7.154e5 |
| 2 | 1 | 9.349e-11 | 0.6916 | 3.470e1 | 7.329e6 | 0.0351 | 6.293e5 |
| 3 | 0 | 2.867e-10 | 0.7493 | 2.108e1 | 6.268e6 | 0 | 0 |

## DR convention

Badnell's official Kelvin table version 20230512 uses

alpha_DR(T)=T^(-3/2) sum_i c_i exp(-E_i/T).

E_i is Kelvin; c_i is cm^3 s^-1 K^(3/2); alpha_DR is cm^3 s^-1. Source c rows and E rows occupy separate table sections and must pair on (Z,N,M,W).

For Li+ (q=1,N=2): c=[2.941e-5,6.068e-5,-7.753e-7], E=[6.345e5,7.024e5,8.271e5] K.

For Li2+ (q=2,N=1): c=[1.451e-4,5.789e-3,1.889e-5], E=[8.529e5,1.056e6,1.170e7] K.

Retain the negative fitted c3 for Li+. Individual fit terms are not physical channels; positivity applies to their sum. Bare Li3+ has no core electron to excite and its DR is a structural zero. The applicable DR literature is the H-like initial-target sequence (Badnell, A&A 447, 389, 2006) and the He-like initial-target sequence (Bautista & Badnell, A&A 466, 755, 2007, DOI 10.1051/0004-6361:20077056). The lithium-*isoelectronic* DR paper concerns initial three-electron ions and must not be mistaken for this elemental-lithium chain.

## Per-channel temperature domains

CI source Tmin values for q=0,1,2 are 1,4,5 eV, respectively; Tmax=20 keV for all three. Convert each bound with the source k_B literal above.

The Badnell official pages specify standard ADAS tabulation extent [10q^2,10^7 q^2] K for initial target charge q. This is the conservative supported range adopted here, not a separately proven universal fit-accuracy envelope. RR q=1: [10,1e7] K; q=2: [40,4e7] K; q=3: [90,9e7] K. DR q=1 and 2 use the same respective intervals; bare-ion DR is structural zero for T>0. The full CI+RR+DR chain shares [5/(8.617385e-5),1e7] K. Cold RR queries retain their own domains and do not authorize cold CI. The common interval is below the source's approximately 1e8 K relativistic-distribution warning.

## Isotope evidence and precise limitation

Bushaw et al., *Ionization Energy of 6,7Li Determined by Triple-Resonance Laser Spectroscopy*, Phys. Rev. A 75, 052503 (2007), DOI 10.1103/PhysRevA.75.052503, report Li7 ionization energy 43487.15940(18) cm^-1 and an isotope shift labelled IS(EI)7,6 of 18067.54(21) MHz. The inspected abstracts do not explicitly define the subtraction order, so only the magnitude is admitted and the sign remains unresolved. The author institution's primary record is https://www.pnnl.gov/publications/ionization-energy-li-6li-7-determined-triple-resonance-laser-spectroscopy. The publisher abstract was also inspected at https://journals.aps.org/pra/abstract/10.1103/PhysRevA.75.052503. These measured isotope inputs, reported uncertainties, sign limitation, and symbolic SI conversion recipes are preserved in `../../data/lithium_isotope_thresholds.json`; no Li6 absolute threshold is inferred and no Voronov fit parameter is changed.

This establishes a real isotope difference. Its energy form is h times 18067.54 MHz, which can enter a specifically derived threshold-sensitivity diagnostic. It does not establish isotope-resolved CI, RR, or DR rate fits and does not bound isotope effects on DR resonance positions/strengths. A neutral threshold shift cannot be promoted into a rigorous error bound for every Li ionic channel. No empirical bound on the complete shared-electronic-rate approximation was admitted by this intake. A shared fit applied to separately conserved 6Li/7Li populations must remain an explicitly named model approximation with its own claim ceiling. It must never be described as native isotope-specific coefficients.

SciSpace and Exa searches found isotope-resolved spectroscopy and laser photoionization studies, but no complete isotope-resolved thermal CI/RR/DR table suitable for direct ingestion. Laser isotope selectivity is not a T-only thermal rate provider. An ion-atom isotope charge-exchange result encountered in discovery was not used as evidence for electron CI/RR/DR isotope equality.

## Other boundaries and reuse

These are low-density initial-ground-level Maxwellian-electron coefficients, excluding metastable mixtures, finite-density DR suppression, three-body recombination, charge exchange, molecular channels, and non-Maxwellian electrons. Photoionization requires Gamma_q=4 pi integral[J_nu sigma_q(nu)/(h nu)] dnu and is not T-only absent a frozen radiation field. Recombination number coefficients are insufficient for emitted-energy moments or full cooling. No Li photo/cooling model is inferred from these fits.

No explicit SPDX or blanket redistribution license was identified on the inspected author tables/pages. Badnell headers carry copyright attribution. The authors offer numerical fit tables for plasma modelling. This unit retains only a small factual coefficient subset with attribution and independently authored schema/provenance. It asserts no permissive software license or blanket redistribution permission for upstream code/databases.

All source work was parsing, discovery and documentary assessment; no rate evaluation, numerical simulation or benchmark was executed by the source-intake agent. Prior-PR isotope authority is being assessed separately by the frontier owner.

## Final selected isotope policy

The root contract authorizes mandatory explicit opt-in `ElementalElectronicEquality` for A=6 or A=7, preserving separate nuclear identities and charge populations q=0,...,3. Native isotope-resolved coefficient requests return `MissingSource`. This does not change `isotope_specific=false` for upstream coefficients or supply an empirical full-error bound. Li8/Li9 remain excluded pending nuclear-decay closure. The preceding PR authority is recorded in `../intake/LI_PRIOR_PR.json`.
