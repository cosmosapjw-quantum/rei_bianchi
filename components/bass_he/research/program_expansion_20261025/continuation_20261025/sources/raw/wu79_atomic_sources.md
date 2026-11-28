# PHYS79 atomic CI/CX source and thermal-contract contribution

Date: 2026-10-22. Scope: R2/R3/R5 contribution to WU088_HH after PHYS78. No existing trajectory was rerun. Exa search/fetch and SciSpace search were actually invoked; primary author tables, primary papers, and source code were read. Numeric values below are fresh Python scalar evaluations, not ODE science runs. User-selected physmath protocol 1.0.0 was applied (RESEARCH_POLICY and THEORY_LOOP read).

## Decision for a constructive bounded next unit

A conservative reaction kernel and isolated parcel controls can be implemented now for a **specified subset and specified temperature domain**. The sources inspected do not close the full original 255–25371 K isotope CI/CX+thermal problem. Neutral H/He/Li Voronov CI has lower fit temperature 11604.52 K. KF96 He–H nonradiative CX has a coefficient-domain overlap, but its channel-level energy assignment remains quarantined until full primary branch text is verified. D–H CX has a separate 2.7–200000 K fit domain and explicit ground-state channel scope. This supports finite local controls; it does not supply a valid all-channel z20→2 trajectory at the cold initial condition.

Do not promote empirical rate extrapolations or a numerical floor to a scientific rate-domain certificate. Do not obtain radiative-CX heating by depositing the full chemical defect in gas: the emitted photon energy moment is required.

## 1. Electron collisional ionization: exact primary table

Source S1: G. S. Voronov (1997), Atomic Data and Nuclear Data Tables 65, 1–35, DOI 10.1006/adnd.1997.0732. Author-hosted dataset/readme/subroutine:

- https://www.pa.uky.edu/~verner/col.html
- https://www.pa.uky.edu/~verner/dima/col/cfit.dat
- https://www.pa.uky.edu/~verner/dima/col/cfit.txt
- https://www.pa.uky.edu/~verner/dima/col/cfit.f

Let theta_e = k_B T / (1 eV), U = dE/theta_e. The fit is

    k_CI(T) = A (1 + P sqrt(U)) U^K exp(-U) / (X + U)  [cm^3 s^-1].

Here dE is the **tabulated fit parameter in eV**. It should remain pinned to the fit; do not silently replace its rounded value by a precise ionization potential. The chemical-energy ledger may use independently pinned physical thresholds, with the difference documented.

| Target | Z | bound electrons N | dE eV | P | A cm3/s | X | K | Tmin eV | Tmax keV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H I | 1 | 1 | 13.6 | 0 | 2.91e-8 | 0.2320 | 0.39 | 1 | 20 |
| He I | 2 | 2 | 24.6 | 0 | 1.75e-8 | 0.1800 | 0.35 | 1 | 20 |
| He II | 2 | 1 | 54.4 | 1 | 2.05e-9 | 0.2650 | 0.25 | 3 | 20 |
| Li I | 3 | 3 | 5.4 | 0 | 1.39e-7 | 0.4380 | 0.41 | 1 | 20 |
| Li II | 3 | 2 | 75.6 | 1 | 2.01e-9 | 0.2090 | 0.23 | 4 | 20 |
| Li III | 3 | 1 | 122.4 | 1 | 9.60e-10 | 0.5820 | 0.17 | 5 | 20 |

The readme explicitly labels Tmin **eV** and Tmax **keV**. At PHYS78 Tmax=25370.7 K, theta_e=2.18627776994 eV. Therefore H I, He I, Li I fall within their table domains; He II, Li II, Li III do not. Every row is outside its table domain at 255 K. The author Fortran routine computes theta_e=T*8.617385e-5 and returns zero for U>80, but that is an implementation choice rather than an exact physical vanishing theorem. New code should record the modern/pinned k_B convention and retain domain checks separately from underflow handling.

Fresh scalar values at 25370.7 K using k_B=8.617333262145e-5 eV/K:

| Target | evaluated k cm3/s | source-domain status |
|---|---:|---|
| H I | 1.8288234853725495e-11 | within fit domain |
| He I | 4.636221688562934e-14 | within fit domain |
| Li I | 5.857922237074024e-9 | within fit domain |
| He II | 1.7029833909961953e-20 | extrapolation diagnostic only |
| Li II | 8.623768473504677e-25 | extrapolation diagnostic only |
| Li III | 1.3841086207912853e-34 | extrapolation diagnostic only |

Tiny extrapolated high-stage values are not validated upper bounds. A physical negligibility bound would require a source-qualified cross-section envelope and integration against the Maxwellian tail, then propagation over actual density/time exposure. No such bound was established here.

### Low-temperature H/He alternative investigated

S2: Janev et al. (1987), *Elementary Processes in Hydrogen–Helium Plasmas*. The author/project-hosted guide https://www.eirene.de/Documentation/janev_buch.pdf states 0.1 eV–20 keV, density below approximately 5e14 cm^-3; it explains logarithmic-polynomial rate fits and reproduces H ionization reaction 2.1.5. Even 0.1 eV corresponds to 1160.45 K, above the 255 K initial condition.

S3: Grackle official source and license, inspected on main (a revision must be pinned before importing source):

- https://raw.githubusercontent.com/grackle-project/grackle/main/src/clib/rate_functions.c
- https://raw.githubusercontent.com/grackle-project/grackle/main/LICENSE
- https://grackle.readthedocs.io/en/latest/Reference.html

Grackle k1/k3/k5 implement Janev/Abel logarithmic polynomial H/He CI. k3 and k5 return `tiny` when T_e<=0.8 eV; k1 takes max(tiny, polynomial result) in that regime. This is useful code provenance and a regression target but does not establish a physical rate-domain certificate down to 255 K. Source copying is allowed under the Enzo Public License, including University of Illinois/NCSA terms; retain copyright, license, and disclaimers. The new compact Voronov formula can instead be independently implemented from the cited table; no third-party source code needs copying.

## 2. Nonradiative H–He charge transfer

S4: Kingdon & Ferland (1996), ApJS 106, 205–211, DOI 10.1086/192335, Eq.7 and Table1. Primary article https://articles.adsabs.harvard.edu/pdf/1996ApJS..106..205K . The He+ row is based on Zygelman et al. (1989), PRA 40, 2340, DOI 10.1103/PhysRevA.40.2340.

For He+ + H -> He + H+:

    k_HeH_NR(T) = 7.47e-15 (T/1e4)^2.06
                  [1 + 9.93 exp(-3.89 T/1e4)] cm^3/s,
    6000 <= T <= 100000 K.

The table parameters are a=7.47e-6 (in units 1e-9 cm3/s), b=2.06, c=9.93, d=-3.89. They were independently confirmed in author-owned Cloudy c17.03 code https://data.nublado.org/doxygen/c17.03/atmdat__char__tran_8cpp_source.html lines90–93, which explicitly adds this term separately from radiative charge transfer. At 10000 K the value is 8.986576477590704e-15 cm3/s; at 25370.7 K it is 5.087079674378878e-14 cm3/s.

A tentative GP98 PDF text extraction produced an inconsistent SI-looking prefactor, so **the direct KF96/Cloudy coefficients above supersede that OCR**, and the tentative extracted GP98 coefficient must not be imported.

Ground-state finite-channel energy release is Q=I_HeI-I_HI about10.99eV. For a ground-state-channel model, deposit +Q per forward reaction and -Q per reverse. A general total CX rate into excited products needs its state-specific energy distribution or prompt-radiation channel. KF96 explicitly warns that total CX into excited products can require state resolution. The detailed original Zygelman1989 A-to-X transition model should be retained as the channel assumption, not inferred solely from ion names. Its publisher abstract confirms both direct and radiative channels and a radiative spectrum; full primary channel text was not obtained here.

### Reverse detailed balance: derived, not a new empirical fit

For A + B+ -> A+ + B, set Q=I_B-I_A (positive for exothermic forward). At a single Maxwellian T and ground-state partition factors g,

    k_f/k_r = (g_A+ g_B)/(g_A g_B+)
              [m_A+ m_B/(m_A m_B+)]^(3/2) exp(Q/k_B T).

Derivation: divide the two ideal-gas Saha ratios n_A+ n_e/n_A and n_B+ n_e/n_B; the electron factors cancel. For He+ + H -> He + H+, k_r/k_f = 4 [m_He+ m_H/(m_He m_H+)]^(3/2) exp(-Q/k_BT). The factor4 comes from electronic ground-state degeneracies; nuclear spin factors cancel species by species. Neglecting electronic mass corrections is an explicit approximation. The derived reverse is a finite-channel model choice and must not be presented as an independently measured rate. Preserve the original forward fit domain for both directions.

## 3. D–H ground-state charge transfer: particularly useful conservative control

S5: Savin (2002), ApJ566,599–603, DOI10.1086/324218. Eq.6 and Table2:

- https://iopscience.iop.org/article/10.1086/324218/pdf
- http://user.astro.columbia.edu/~savin/papers/54551.web.pdf

With T in K and rates in cm3/s:

    D(1s)+H+ -> D+ +H(1s):
    k_f = 2.00e-10 T^0.402 exp(-37.1/T) - 3.31e-17 T^1.48

    D+ +H(1s) -> D(1s)+H+:
    k_r = 2.06e-10 T^0.396 exp(-33.0/T) + 2.03e-9 T^-0.332

Calculated rates are given for1–200000K; **fit validity is2.7–200000K**, with errors below6% forward/4% reverse. The reaction is endothermic forward by I_D-I_H approximately k_B*43K, because deuterium has slightly larger ionization energy. Primary discussion says capture is ground-state dominated in the relevant low-T regime, and higher-level capture becomes important at much higher collision energy.

Important: the independent fits do not enforce exact detailed balance. Scalar checks give k_f/k_r=0.8240059422 at255K,1.0098937563 at10000K,1.0158168124 at25370.7K. Slightly superunit ratios in the last cases are consistent with fit error but should not be called exact thermal equilibrium. Choose either (a) source-pair rates with a reported detailed-balance fit residual or (b) one source fit plus a thermodynamically derived reverse and explicitly label the new closure. Do not silently change the source pair to force an exact test.

PHYS78 used element-based isotope-blind ionization energies. Activating fractionating D–H CX requires consistent isotope binding-energy changes in the relevant ledger/thresholds; leaving I_D=I_H makes CX chemical-energy release zero while the rates resolve the isotope defect. Tritium and helium/lithium isotope-specific CX are not established merely by copying H/D rates.

The parent-selected isolated control uses the original reverse fit and a **new derived forward** `k_f(T)=k_r(T)*exp(-43/T)`. Its exactness applies to the declared rounded 43 K chemical defect, equal neutral/ion masses A*m_p per isotope, electronic degeneracy ratio 1, cancelled nuclear spin, and omitted hyperfine structure. Keep the two raw Savin fits as a separate comparison profile. This derived forward must never be attributed to Savin as the paper's original forward formula.

## 4. Lithium: distinguish direct and radiative channels and fit/data domains

S6: Galli & Palla (1998), A&A335,403, https://arxiv.org/pdf/astro-ph/9803315 Table4 Li7/Li8; primary rate references Kimura,Dutta&Shimakura1994 ApJ430,435 (DOI10.1086/174418), erratum1995 ApJ454,545 (DOI10.1086/176506), and Stancil&Zygelman1996 ApJ472,102 (DOI10.1086/178044).

GP98 gives:

    Li(2s)+H+ -> Li+(1s2)+H(1s), nonradiative:
    k_Li_NR = 2.5e-40 T^7.9 exp(-T/1210) cm3/s.

    Li(2s)+H+ -> Li+(1s2)+H(1s)+photon, radiative:
    k_Li_RCT = 1.7e-13 T^-0.051 exp(-T/282000) cm3/s.

The nonradiative formula must not be extrapolated to25371K with a validity claim. Original Kimura table shown in the extracted primary paper extends100–10000K; the erratum retrieval returned unrelated journal material rather than usable erratum text, so **corrected low-T coefficients and exact fit-domain provenance remain OPEN**. KF96 Table3 Li0 fit combines Kimura and Stancil/Zygelman rates over100–10000K; its total coefficient mixes radiative and direct channels and cannot be assigned one purely thermal Q.

S7: Stancil&Zygelman1996 primary full article https://articles.adsabs.harvard.edu/pdf/1996ApJ...472..102S . Original table gives RCT data10–40000K. Its analytic Eq14 fit is stated accurate within5% for20–10000K only. Thus the data range and analytic-fit range are different. Rates near20000,30000,40000K are1.03,1.04,1.05 times1e-13 cm3/s. A table interpolation would require its own approximation statement. No mean radiated-energy coefficient was read or integrated here.

For nonradiative ground-state Li0+H+ transfer, Q=I_H-I_Li about8.207eV and electronic degeneracy ratio1. The reverse ground-state rate is the forward times the reduced translational mass factor and exp(-Q/k_BT). For RCT the reverse includes a photon and depends on the photon field; it is not the binary reverse charge-exchange reaction.

The primary Li RCT article reports a spectrum peaking near158nm, unlike the asymptotic energy-defect wavelength150.8nm. That fact directly rules out interpreting the defect as the exact photon energy. Use an energy-weighted rate coefficient

    L_gamma(T) = integral E_gamma d(rate)/dE_gamma dE_gamma

and gas thermal term Q*R-L_gamma*n_Li*n_H+. Number rate alone does not determine this moment. The same issue occurs for radiative He–H transfer; spectrum near113nm is reported by Zygelman1989.

Li high-stage CI fits exist in S1 but are out of domain at this pilot Tmax. Li high-stage CX often populates excited ionic levels; state energies and cascade photons are needed. Li hard-UV PI branching/inner-shell/spectral-energy contract stays OPEN. Li6/Li7 copying of elemental rates is a declared isotope approximation, not an isotope-resolved source calculation.

## 5. Thermal and implementation contract

Assume a common nonrelativistic Maxwellian temperature for electrons and heavy particles, isotropic reacting gas, no tilt. Metric signature(-,+,+,+); keep k_B and SI conversion explicit. Convert every cm3/s coefficient to m3/s with1e-6. A two-body event density is R=n_a*n_b*k [m^-3 s^-1].

Let u_th=(3/2)k_B T n_part and u_chem=sum_i n_i E_i where E_i is cumulative ionization energy relative to the neutral ground state. For ground-state CI A^q+e -> A^(q+1)+2e:

    du_chem/dt = +I_q R
    du_th/dt = -I_q R
    dn_e/dt = +R.

If T is the evolved variable, the collision contribution is

    dT/dt = -(2/(3 k_B n_part)) I_q R - (T/n_part) R,

where the second term is the change in number of thermal particles. It must not be added again if u_th is already the evolved variable and T is reconstructed from u_th and n_part. In an expanding cell use the existing dilution/work terms consistently; this local exchange identity is independent of that background accounting.

For nonradiative binary CX, total heavy-particle and electron counts remain constant. Chemical and thermal terms are opposite +/-Q R. For radiative CX use du_th=Q R-Q_gamma and du_radiation=Q_gamma. Excitation cooling, recombination cooling, free-free emission, Compton exchange, molecules, spectral transport, and nonthermal-electron deposition remain separate contracts; adding CI/CX alone does not complete them.

Recommended code acceptance for this bounded unit:

1. Positive finite input validation and reaction-local temperature guards; reject unsupported positive-population channels rather than silently zeroing them.
2. Nuclear-count and charge conservation from the stoichiometric matrix, with electron derivative derived from ionic charges.
3. Energy-exchange identity using the same binding-energy vector as the state ledger.
4. Exact detailed-balance test only for a derived-balance profile; separately quantify source-fit-pair residuals.
5. One within-domain hot parcel control (e.g.20000K with strict admitted subset), one D-CX finite control if isotope energies are consistently updated; no existing PHYS78 run replay.
6. Trace every result to source/profile/domain and count a refusal outside the domain as a domain-control result, not an ODE failure.

## 6. Evidence status and minimal next source work

The companion `SOURCE_EVIDENCE_EXTRACTED.json` retains numeric source excerpts, normalized coefficients, source URLs, and admission decisions. Acquisition was through web extraction tools. **Original remote PDF/ASCII file bytes were not retained or hash-verified.** Hashes of these local deliverables identify the assembled report/extraction only. The Savin PDF OCR merges a subscript 2 with the 2.7 K fit bound; the parsed fit domain is recorded along with this extraction limitation.

Literature-supported: coefficient tables and explicit domains above. Derived: stoichiometric energy accounting and ground-state detailed-balance relation. Numerically checked: scalar values shown. Implementation-verified: no production module implemented by this subagent; parent owns integration/tests. OPEN: full cold-to-hot CI coverage, Li corrected nonrad fit domain, radiative CX energy moments, high-stage/state-resolved CX, complete thermal cooling, recombination-to-z20 initial charge reconstruction. NG1–NG7 not invoked as a no-go admission; no impossibility theorem is asserted.

The next source step is to fetch unambiguous original nonradiative He/Li channel text and Kimura erratum, then either integrate sourced cross sections over Maxwellians to extend the cold domain or document a justified error budget for the omitted reactions. This follows the tested local kernel without treating missing rates as an exact physical zero.
