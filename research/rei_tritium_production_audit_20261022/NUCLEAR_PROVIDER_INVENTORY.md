# Nuclear coefficient inventory and retained model gaps

These providers complete the numeric conditional eighteen-family contract. `source-supported anchor` does not mean a cross section experimentally validated throughout the 100–10000 K Gamow window. Coefficients, chemical assumptions, energetic-particle closure and probability statements have separate status.

## Admitted forward anchors

| Family | Adopted numeric anchor | Source and actual scope |
|---|---:|---|
| DDp / DDn | 50.8 / 51.0 keV barn | Viviani et al. 2023, DOI 10.1088/1742-6596/2586/1/012076; theoretical zero-energy constants; preceding `SOURCES.md` |
| D(p,gamma)He3 | 0.21 eV barn | NACRE-II §3.1 |
| D(D,gamma)He4 | 5.8 meV barn | NACRE-II §3.2 |
| D(alpha,gamma)Li6 | 2.2 meV barn | NACRE-II §3.5 |
| T(D,n)He4 | 11 MeV barn | NACRE-II §3.6 |
| T(alpha,gamma)Li7 | 98 eV barn | NACRE-II §3.7 |
| He3(D,p)He4 | 5.9 MeV barn | NACRE-II §3.8 |
| Li6(p,alpha)He3 | 3.1 MeV barn | NACRE-II §3.12 |
| Li7(p,alpha)He4 | 52 keV barn | NACRE-II §3.14 |
| T(p,gamma)He4 | 0.95 eV barn | Dubovichenko et al., DOI 10.1142/S0218301319300042; E1 cluster-model low-energy estimate |
| He3(n,gamma)He4 | 54.02 microbarn at thermal reference | JENDL-5 He3, MT102; controller-retrieved evaluated table |
| He3(n,p)T | 5328 barn at thermal reference | JENDL-5 He3, MT103; controller-retrieved evaluated table |
| p(n,gamma)D | 0.3326 barn at 2200 m/s | NIST NCNR H1 absorption; capture assignment |
| D(n,gamma)T | 0.000519 barn at 2200 m/s | NIST NCNR D absorption; capture assignment |
| Li6(n,alpha)T | 940 barn at 2200 m/s | NIST NCNR Li6 absorption, assigned to dominant branch as an explicit approximation |
| T / n beta decay | Evaluated half-life / mean lifetime | `EVALUATED_DECAY_INPUTS.json`; never confuse half-life with mean lifetime |

NACRE-II: Y. Xu et al., Nuclear Physics A 918 (2013) 61–169, DOI https://doi.org/10.1016/j.nuclphysa.2013.09.007, author manuscript https://arxiv.org/abs/1310.7099, full HTML https://ar5iv.labs.arxiv.org/html/1310.7099. This primary evaluation uses potential/DWBA models to continue charged cross sections downward. Its rate tables begin around 1e6 K; they are not used here. Its §3 introduction says nominal S(0) commonly denotes values near 0.5–1 keV. Continuing these constants to eV-scale Gamow energies is therefore an explicit new approximation, not inherited validation. The full HTML was retrieved locally with urllib (3,590,388 bytes); Exa independently retrieved the abstract and relevant source sections. The displayed numeric constants were read directly from the relevant sections. Their quoted high/low ranges are not adopted as a 99% distribution.

pT: https://arxiv.org/pdf/1811.04779, pp.14–15, short quotation: “S(0) = 0.95(5) eV b.” This is the authors' estimate from their near-flat 1–3 keV E1 model. The paper distinguishes uncertain experimental extrapolations and states that its M1 contribution is zero in that model. Our provider is thus an E1 model kernel, not an empirically complete multipole evaluation. The unresolved minor multipole/low-energy uncertainty remains explicit.

JENDL-5 channel table: https://wwwndc.jaea.go.jp/jendl/j5/elm/Table/z002/T3.html. The controller successfully read MT102 and MT103 at 0.0253 eV; this agent's retry returned HTTP503. The values above follow the controller's actual retrieval, not a successful local fetch claim. For the 1/v approximation the standard 2200 m/s reference is used. A controller-retrieved primary experimental cross-check for the tiny radiative branch is https://inspirehep.net/literature/276545, with thermal capture 54±6 microbarn. The older channel-specific ENDF/B-V evaluation, https://www.nndc.bnl.gov/endfdocs/ENDF-301.pdf, gives He3(n,p)T 5327 barn and adopts 1/v up to 1.7 keV; that is a cross-check, not the nominal number.

NIST neutron table: https://ncnr.nist.gov/resources/n-lengths/list.html. Its last column is total absorption at 2200 m/s. It supplies the adopted H1/D values and rounded Li6 absorption. Li6 branch allocation is an explicitly retained approximation; the missing radiative Li6(n,gamma)Li7 branch is listed outside this finite network rather than silently counted twice. This use does not turn the thermal table into a fast-neutron transport evaluation.

## Masses and inverse coefficients

NIST lithium isotope masses https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Li were retrieved through Exa: Li6 6.0151228874 u and Li7 7.0160034366 u. NIST spin cross-check https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable1.htm gives J=1 and J=3/2. Subtract three electron masses for the declared nuclear-mass approximation. Other species use the actual SciPy physical-constant mass table serialized by the executable. Ground-state degeneracies and the same mass table define thermal two-body inverse rates; the actual non-Planck external photon spectrum defines photon inverse rates separately.

## Existing provider packages and donor assessment

| Provider or donor | What was actually inspected | Reuse decision |
|---|---|---|
| Pinned REI RUN19 | Full target JSON and `RUN19_full_network.rs` fetched at PR219 head; source named full_network contains atomic physics | Reuse stoichiometry and source ownership conventions, not nonexistent nuclear coefficients |
| Pinned R5 BBN donor | `R5_DONOR_BBN.json`: C-backend abundance output, T_end=0.001 MeV and bare-Be7 overlay | Reuse as historical abundance context only; it is not low-T rate validation |
| PRIMAT | Official https://www2.iap.fr/users/pitrou/primat.htm and developer https://github.com/CyrilPitrou/primat; current README lists 1e-3≤T9≤10 master rate grid | Useful network data/solver and future source lookup; current grid excludes this task's temperatures, so no rate-table extrapolation admitted |
| JINA REACLIB | Official https://reaclib.jinaweb.org/ and search/help records; versioned rate families and detailed-balance reverse flag | Useful reaction/source catalog; no generic package-level low-T guarantee. No numeric REACLIB fit used here |
| AlterBBN | Authors' manual https://arxiv.org/pdf/1806.11095 and official https://alterbbn.hepforge.org/ | Public C BBN code; bbnrate.c and REACLIB importer documented. No actual 100–10000 K cross-section validation established in this intake |
| PArthENoPE tables | Current PRIMAT README identifies a `small_parthenope` table option | Candidate BBN table source, not a retrieved low-T provider; no package installed or invoked |
| HE/HH/BASS/REC | Pinned tree/provider inspection in the separate `PROVIDER_CODE_INTAKE.md` | Existing transport/atomic scaffolds do not supply a complete validated low-T nuclear kernel |

## Missing providers and remaining physical scope

Every admitted family has a numeric provider or an exact external-photon support-zero reason. Missing low-energy screening/neutral/molecular physics, energetic product stopping, nuclear-photon reprocessing, detailed electronic daughters, pT multipole completeness, Li6 partial-branch correction, and reactions beyond the explicit eighteen-family list are recorded limitations. None is replaced by an empirical claim of zero. The numeric model may run now; those missing providers limit its interpretation and define future upgrades.
