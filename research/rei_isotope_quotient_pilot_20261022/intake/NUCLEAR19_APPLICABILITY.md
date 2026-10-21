# Applicability of the supplied19-channel target

The source-pinned transcription is `research/rei_hheli_pilot_20261021/intake_remote/RUN19_target_network.json`, SHA256 `96466ae646905c7f47509ea30898f677d12b922571e23d166426bf223fbf889a`. It distinguishes19 total listed reactions:3 atomic and16 nuclear/decay/capture. It supplies stoichiometry and missing-source obligations, not measured coefficients.

The current executable quotient model inherits an external UV spectrum supported exactly at5–60eV and T=100–10000K. Source photons have no support at MeV nuclear thresholds. This settles the forward photodisintegration source term only. The electron/ion dynamics does not thereby implement the reverse nuclear capture reactions. Zero nominal n/T is a frozen initial condition, not a decay-rate model or a proof that all nuclear pathways vanish.

| ID | Listed reaction | Status in inherited executable atomic lane | Concrete next dependency |
|---|---|---|---|
|1|HI+photon ↔ HII+electron|Photo/RR active; H and D elemental coefficients equal|Isotope-specific coefficients for isotope spectroscopy|
|2|HeI+photon ↔ HeII+electron|Photo/RR active; He3/4 elemental coefficients equal|Isotope-specific coefficients|
|3|HeII+photon ↔ HeIII+electron|Photo/RR active up to60eV|Isotope-specific coefficients|
|4|He4+photon ↔ He3+n|Forward source outside UV support; reverse capture unimplemented|He3(n,gamma)He4 cross section and ionic daughters|
|5|He4+photon ↔ T+p|Forward source outside UV support; reverse capture unimplemented|T(p,gamma)He4 low-energy data and ionic daughters|
|6|He4+photon ↔ D+D|Forward source outside UV support; reverse capture unimplemented|D(D,gamma)He4 low-energy data and symmetry factor|
|7|He3+photon ↔ D+p|Forward source outside UV support; reverse separately listed13|D(p,gamma)He3 low-temperature validity|
|8|D+photon ↔ p+n|Forward source outside UV support; reverse separately listed12|n(p,gamma)D thermal cross section|
|9|T → He3+electron+antineutrino|Absent T inventory in atomic lane; decay operator absent|Evaluated lifetime; daughter ionic mapping; beta/neutrino energy partition|
|10|n → p+electron+antineutrino|Absent n inventory in atomic lane; decay operator absent|Evaluated neutron lifetime and beta/neutrino energy partition|
|11|Li7+photon ↔ He4+T|Forward source outside UV support; reverse separately listed19|T(alpha,gamma)Li7 low-temperature validity|
|12|p(n,gamma)D|Unimplemented capture; initial neutron reactant absent|Thermal neutron capture source and energy/charge treatment|
|13|D(p,gamma)He3|Unimplemented; populated reactants exist|Low-energy cross section or justified low-T rate integral|
|14|D(D,p)T|Unimplemented; can create T even with initial T=0|Low-energy cross section, identical-reactant1/2 factor|
|15|D(D,n)He3|Unimplemented; can create n even with initial n=0|Low-energy cross section, identical-reactant1/2 factor|
|16|T(D,n)He4|Unimplemented; initial T absent but14 can create it|Low-energy source; consistent coupled inventory|
|17|He3(D,p)He4|Unimplemented; populated reactants exist|Low-energy cross section or justified low-T rate integral|
|18|He3(n,p)T|Unimplemented; initial n absent but15 can create it|Thermal neutron reaction source and ionic mapping|
|19|T(alpha,gamma)Li7|Unimplemented; initial T absent but14 can create it|Low-energy capture source; no duplicate with reverse11|

Li6 and fully stripped LiIV are requested census additions beyond the drawing. The atomic lane includes both. LiIII/LiIV conditional populations are nominally zero because initial higher charges and their photo-source terms vanish under the60eV cutoff, while their RR operator is tested with positive high-charge populations. The supplied graph does not provide Li6 nuclear creation/destruction channels. A full nuclear network requires an explicit Li6 channel selection and should consider closure under produced species, rather than silently assuming the drawn set is closed.

## Constructive rate and decay extension

For a two-body channel i+j→products, use event density `R=n_i*n_j*<sigma v>/(1+delta_ij)` with cm^-3 and cm^3/s consistently, or explicitly converted SI. Update each isotope by stoichiometric multiplicity and enforce A-weighted conservation. Charge states need product branching or a declared shell-preservation approximation; nuclear charge alone does not assign ionic charge. Reverse rates may be derived by detailed balance only with its distributional and thermodynamic assumptions stated; an arbitrary nonthermal UV source does not supply those assumptions.

For decay of a known populated parent, solve `dY_parent/dx=-(lambda/H)Y_parent` and add daughter yield with the same event count. Neutron daughter is HII plus one free beta electron in the bare-nucleon mapping. In the simplest shell-preserving tritium mapping, T charge q becomes He3 charge q+1 plus a beta electron, conserving net charge; shell excitation/shake-off then requires explicit corrections. Positive n/T would introduce decay times far shorter than cosmological H^-1 and invalidate the current fixed-isotope quotient. A source-pinned decay-only extension can use an analytic fast stage or an asymptotic elimination with a quantified transient error, rather than force unresolved cosmological steps through the decay transient.

Use evaluated primary data to establish rate applicability. The literature search found Pizzone et al.2016, DOI10.1051/epjconf/201611709010, whose stated numerical rate range is0.01<T9<10, i.e.10^7–10^10K. That stated range does not cover100–10000K. Its fitted coefficients must not be blindly extrapolated into this pilot. This is a concrete input gap, not a no-go for low-temperature rate calculations; the constructive route is a source-backed low-energy cross section and Maxwellian integral or a validated low-temperature evaluation.

## Sources actually retrieved

- Verner & Ferland1996, DOI10.1086/192284, authors' table page https://www.pa.uky.edu/~verner/rec.html. Directly supports atomic RR convention and broad temperature fit.
- R.J.Howerton1981, https://doi.org/10.61092/iaea.n03v-85t3, primary IAEA threshold/Q-value evaluation. Defines mass-difference thresholds; used for threshold methodology rather than a fitted reaction rate.
- Van der Leun & Alderliesten1982, https://ui.adsabs.harvard.edu/abs/1982NuPhA.380..261V, primary deuteron-binding measurement approximately2.2246MeV. This is over37000 times the60eV upper support; numerical precision here is unnecessary for the support argument.
- Pizzone et al.2016, https://doi.org/10.1051/epjconf/201611709010, SciSpace-retrieved primary conference paper with explicit BBN rate-temperature range. No new low-temperature coefficients were admitted.
- Yeh, Olive & Fields2023, https://doi.org/10.3390/universe9040183, retrieved paper establishing how neutron lifetime enters weak-decay/BBN calculations. Its cosmological inferred lifetime was not adopted as an experimental decay input.

Outcome: exact atomic quotient implementation can proceed immediately. Nuclear target coverage remains explicit per channel, and no omitted nuclear rate has been silently certified zero. No full19 claim or no-go is issued by this matrix.
