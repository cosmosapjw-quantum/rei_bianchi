# HE-ANG analytic source intake — 2026-10-24
Role: source/theory R2/R4, not independent review. No scientific solver, sweep, quadrature, fitting, or simulation executed. Previous PR96 TDCS54, CCC exchange and TP proofs are reused without replay.

## Decision
Two newly read primary documents supply a constructive next unit: an absolute, analytic field-free plane-wave first-Born/Born–Ochkur (PWBA/BO) joint detector TDCS, and an independent exact-swapped plane-wave Born exchange (PWBE) amplitude with richer relative experimental angular cuts. This advances beyond the two TDCS54 points. Neither is a numerically converged full physical event provider. Parent selected HE-ANG-PWBE-SPIN-AZIMUTH: use Weigold Eqs19–20 amplitudes, independently derive the unpolarized spin trace with the swap operator, and derive conditional relative-azimuth measure. Buică Eq46 supplies a separately versioned spin-weight cross-check. Do NOT adopt Weigold Eq21 as unpolarized, and do NOT silently replace Buică BO exchange with exact-swapped PWBE exchange. Admission is source-specific nonrelativistic fixed-center plane-wave model only; full physical-provider gate remains pending.

## A. Buică arXiv:2306.08573v1
Title: Dressing effects in laser-assisted (e,2e) process in fast electron-hydrogen atom collisions in an asymmetric coplanar scattering geometry.
Author: Gabriela Buică.
Version: arXiv stamp 14 June 2023, manuscript dated 16 June 2023.
Primary PDF: https://arxiv.org/pdf/2306.08573
Local PDF: buica2023.pdf; 1,201,864 bytes.
SHA256: 33c4a4c91244313dddd90d99fed986344d479cb0c1a91135a42f77d2f8345755.
Equation numbering below is this arXiv v1, not an asserted journal-version identity. Publisher APS landing page independently confirms the same title/author, Phys.Rev.A106022804, DOI10.1103/PhysRevA.106.022804, publication10August2022, received14February2022, accepted26July2022. Do not confuse with PRA109052808 (2024), a different paper. APS links a later Erratum PRA108059901, DOI10.1103/PhysRevA.108.059901, published3November2023, received25October2023. Erratum body was not delivered by landing-page text; webPDF fetch failed and one read-only shellPDF attempt returnedHTTP403. This is an unresolved access/version gap: do not claim the June2023 arxiv version incorporates the November2023 correction or that its content leaves Eq46 unchanged. The independent spin trace for selected PWBE does not rely on that assumption.
Primary publisherURLs:
https://journals.aps.org/pra/abstract/10.1103/PhysRevA.106.022804
https://journals.aps.org/pra/abstract/10.1103/PhysRevA.108.059901

### Source formulas, atomic units
Set incoming momentum ki, scattered kf, ejected ke; q=ki−kf−ke; Δ=ki−kf; Δe=ki−ke. Source Eq15 explicitly neglects proton kinetic energy q²/(2mp) against electron energies. Field-free shell Ef+Ee=Ei−|E1|. Source uses E1=−13.6eV; exact hydrogen model convention may instead declare −1/2Hartree without treating displayed rounded13.6 as exact.

Eq19:
f = −2^(5/2)/(π Δ²) [(1+q²)^−2−(1+ke²)^−2].
Eq29:
g_BO = −2^(5/2)/(π Δe²(1+q²)²).
Eq18/Eq28:
T_direct^(0)=−JN(Rq) f exp(iNφq)/(2π)²,
T_exchange^(0)=−JN(Rq) g_BO exp(iNφq)/(2π)².
The text after Eq29 calls its exchange expression consistent with Born–Ochkur. It is NOT f with outgoing momenta simply swapped. The direct nuclear subtraction is retained; the BO exchange expression lacks the corresponding swapped subtraction.

Eq46 p18:
d³σ_N/(dΩf dΩe dEf)=(2π)^4(kf ke/ki)[(1/4)|Td+Tex|²+(3/4)|Td−Tex|²].
Source states incoming projectile AND H beams unpolarized, average initial spins, sum unresolved final spins. Labels f/e are scattered/ejected detector coordinates. No extra event factor1/2 is stated in Eq46. Do not import an all-labelled-domain event count without a separate derivation.

### Derived field-free model, explicit derivation scope
At zero laser intensity and N=0, J0(0)=1 and atomic-dressing terms vanish. Therefore
K_BO=(kf ke/ki)[(1/4)|f+g_BO|²+(3/4)|f−g_BO|²]
is the TDCS density relative to dEf dΩf dΩe.
With real amplitudes its bracket is f²+g_BO²−f g_BO.
Dimensional restoration is a0²/Eh per sr²; this follows from the measure, not a numerical conversion performed here.
The source does not impose a strict fast/slow ordering in Eq46. Restricting to Ef>Ee is a proposed admission convention justified by asymmetric fast/slow use, not a quoted source domain. Likewise, extending vector formulas to arbitrary azimuth is an algebraic consequence of their dot products, while displayed plots are coplanar.
A product of polar-angle differentials alone is not its measure: dΩ=sinθ dθ dφ.

### Validity and missing physics
SectionIIA pp5–6 assumes BOTH Ef≫1au and Ee≫1au and neglects residual-ion Coulomb distortion of fast outgoing waves. SectionIIB p9 focuses on Ei,Ef≥1keV. Source numerical examples include Ei2keV/Ee200eV but laser-driven figures are not field-free validation data.
This is first Born in the static potential, plane-wave final states in the field-free limit, neglects three-body final Coulomb correlation, and ignores proton recoil energy. q is a derived ion momentum, not a finite-mass joint recoil-law calculation.
The source's statement about good plane-wave agreement above200eV cannot be promoted into a uniform error bound. No supplied model uncertainty certificate, converged full-joint grid, or absolute event normalization integral is present.

## B. Weigold, Noble, Hood, Fuss, FIAS-R-39 (June1978)
Primary official IAEA record:
https://inis.iaea.org/records/5gbvq-nbn24
Primary PDF:
https://inis.iaea.org/records/5gbvq-nbn24/files/10438831.pdf?download=1
Official metadata: June1978, versionv1, report FIAS-R--39, INIS RN10438831; open report. No explicit reuse license found on record; do not redistribute PDF.
Local weigold1979.pdf (filename historical discovery shorthand; ACTUAL document is1978report),917,299bytes.
SHA256: aaa750d5d5f0652ba7e6090878f938174fc26268265c256022c4d9437c3a96a8.
Official record MD5:60096885b74c08561bd9cfdc85ae2a65.
Related1979journal DOI10.1088/0022-3700/12/2/019; journal fulltext not acquired, identity of all equations not asserted.

### Exact inspected formulas
Reportp18, PDFpage21 visually read:
Eq19 f_T(kA,kB)=8√2/[(2π)^3|k0−kA|²]·[(1+q²)^−2−(1+kB²)^−2].
Eq20 g_T(kA,kB)=f_T(kB,kA).
This f_T equals −f_Buica/(2π)² under A=f,B=e.
Reportp6/PDF9 specifies A=faster, B=slower when energies differ, acknowledges identical electrons, defines angles relative incoming momentum, q=k0−kA−kB, and explicitly neglects ion recoil energy.
Reportp11 uses initial-spin averaging/final-spin sum for DWIA and symmetric normalization.

IMPORTANT unresolved source discrepancy:
Reportp18 Eq21 visually appears (2π)^4 kA kB/k0 [f²+g²−2fg], while unpolarized 1/4,3/4 spin decomposition yields f²+g²−fg for real f,g. Do not silently replace its printed coefficient, and do not claim the manuscript Eq21 itself provides the unpolarized PWBE law. Exact-swap amplitudes plus standard spin algebra is a separately declared source-derived model construction. Scan image weigold_p21.png preserves the evidence.

### Actual richer numeric joint payload, finite relative support
Table1 reportp30/PDF33 contains measured H(e,2e) angular correlations at E0=413.6,250,113.6,100eV. For413.6eV, EA=EB=200eV: sixteen diagonal θA=θB values32–60degrees, plus fixedθA30,40,50degree scans in θB. Other energies provide additional unequal-energy fixedangle cuts. Coplanar φA−φB=π except marked20degree series.
Tablecaption gives pointwise1σ uncertainties in parentheses and separate inter-series normalization errors σ_N(%). Source pp18–19 says no absolute crosssections obtained: one unknown normalization per energy for413.6/250/113.6; at100eV each angular series independently normalized to100. Negative background-subtracted points occur; do not clip or interpret as probabilities. No finite-width angular cells are provided.
These are actual joint angular observations, not DDCS. They remain measure-zero cuts and do not define a full joint event law.
No complete transcription was admitted: OCR disagreed with visual table (e.g.38degree diagonal value), so any chosen fixture must be visually transcribed and independently checked. weigold_p33.png preserves source layout.
The source conclusions report plane-wave PWIA/PWBE inadequate over tested100–413.6eV. This is useful adverse model-evidence, not a full-domain no-go theorem.

## Three executable next science candidates
1. Selected by parent: Eq19/20 Weigold exact-swapped amplitudes, unpolarized spin algebra declared as derivation, separately named PWBE. Derive exchange-symmetric density and relative-azimuth integral/conditional law, and formulate ordered-domain count. Preserve printed Eq21 discrepancy as an open source consistency item; do not combine this g with Buică's source-defined BO label. Parent freezes domain and budgets before calculations.
2. Alternative: literal Buică field-free PWBA/BO high-energy unequal-sharing detector kernel. Fix a compact energy/polar-angle domain with both outgoing energies≫1au. Derive angular support and conditional azimuth normalization from explicit vector dependence; expose singlet/triplet contributions once. No empirical rescaling; no parent physical-provider promotion. Its later erratum content remains inaccessible and must be retained as a version qualification.
3. Richer benchmark branch: choose one complete WeigoldTable1 highenergy geometry family and transcribe relative joint values/errors plus normalization nuisance. Test only shape invariants/ratios or a declared likelihood with correlated normalization; cannot set absolute event scale or extrapolate out-of-plane. This is secondary to1 because source itself warns against plane-wave accuracy there.

## Access/discovery and cost ledger
One new SciSpace semantic question used (raw scispace_raw.json); retrieval is discovery, not primary evidence. SciSpace fees/remoteCPU UNKNOWN_NOT_ZERO. Prior Wolfram/4child costs and failures retained by parent, not reset here.
Question: What explicit analytic first Born direct and exchange amplitudes give a fully differential ionization cross section for electron impact on ground state hydrogen for arbitrary outgoing momenta, and what assumptions about nuclear mass, continuum Coulomb distortion, normalization and spin averaging are required?
Primary actual PDF reads: Buică and Weigold above. SciSpace also located Rudge/Seaton1965 DOI10.1098/RSPA.1965.0020 and Sahlaoui2014 DOI10.1139/CJP-2013-0342; these are abstract-only candidates, not admitted fulltext equations.
arXiv abs web failed DisabledError; PDF web/shell succeeded. IAEA PDF web open failed but read-only shell download succeeded; official landing page succeeded. Journal DOI web open failed. These failures are access gaps, not absence proofs.
Previously inspected official CCC e-H_XSEC_LS.zip remains integrated-only (3162files, README E,sig,asym); not rescanned. Hex ionf absence and H1tmat below threshold, Childers DDCS window, CCC exchange adapter and TDCS54 retain their prior exact scope.
Attachments were available but not newly extracted in this bounded pass because two useful actual primary sources were acquired. No claim that all attachment pages or all public datasets were exhausted.
All downloaded public PDFs and rendered pages are local intake aids only; omit from public PR/package. Publish source URLs, hashes, concise derived formulas and original code/tests only.

