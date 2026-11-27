# HE-ANG R2/R4 source intake: CCC equal-sharing conventions
Retrieved 2026-10-24 UTC. Investigator task only: literature intake, source extraction and candidate decision. No scientific simulation, fixture replay, numerical physics or provider solve was executed.

## Actionable result
The selected new unit is the source-specific CCC equal-energy-sharing convention adapter, using Bray arXiv:physics/9906008v3 equations (2), (21), (24)–(27), independently constrained by Stelbovics arXiv:physics/9905020v1. The raw-pair coherent assembly has an exact positive defect identity. Bray v3 equation (26) prints a negative defect sign; page 10 was rendered and visually inspected, confirming the printed sign rather than merely a text-extraction error. This finding is limited to that pinned preprint version, not an assertion about all journal versions.

No full-support physical H(1s) two-electron payload was acquired. Figure 28 is a real finite joint coplanar cut at 20 eV, but no point digitization was adopted. The physical HE-ANG-SOURCE-PAYLOAD gate therefore retains its actual differential-payload, finite-mass and support obligations.

## Pinned primary source bytes
- Igor Bray, “Electron-impact ionization of atomic hydrogen from near threshold to high energies”, arXiv:physics/9906008v3 (margin date 9 June 1999), https://arxiv.org/pdf/physics/9906008v3
  - local bray_physics_9906008v3.pdf, 1178386 bytes
  - SHA256 5f52f7624aab3beb7a6062d301787645d35b0a5f543c1f8b83d9de8fe8f09700
  - extracted text bray_physics_9906008v3.txt; visual source bray_p10.png.
  - Search-service references turn3view0/turn9view0; screenshot turn8view0 is Fig28.
  - SciSpace metadata disagreed between DOI 10.1071/PH000355 and published article 10.1071/PH99093. Use pinned arXiv identity for this finding; do not silently merge versions.
- Andris T. Stelbovics, “Calculation of ionization within the close-coupling formalism”, arXiv:physics/9905020v1, https://arxiv.org/pdf/physics/9905020
  - local stelbovics_physics_9905020.pdf, 114171 bytes
  - SHA256 1ae2401f79af8e7722c4bb72bdbac854641d913e3dc32830bd258dc32597f755
  - extracted text stelbovics_physics_9905020.txt; visual source stelbovics_p4.png.
  - PDF margin says v1 7 May 1999; title-page compilation date is August 13, 2018. Preserve both, do not treat compilation date as original publication date.
  - primary abstract https://arxiv.org/abs/physics/9905020 search ref turn16academia12.
  - Model is Temkin–Poet, spherical averaging over both electrons, total orbital angular momentum zero; independent normalization support does not supply full 3D angular dynamics.

## Exact convention map (source vs local derivation)
| Item | Source statement/location | Adopted scope |
|---|---|---|
| Target | Bray abstract and section2: electron impact H ground state | H(1s) source identification |
| Raw amplitudes | Eq2/24 uses f_S^(N)(k,q) plus (-1)^S f_S^(N)(q,k) | Same source, same spin, exchanged outgoing momentum arguments |
| Coherent TDCS | Eq2: d³σ_S/(dΩ1 dΩ2 dE2)=|f_S^(N)(k,q)+(-1)^S f_S^(N)(q,k)|² | Equal magnitudes |k|=|q|, not arbitrary energy partition |
| Spin average | Eq21: 1/4 singlet +3/4 triplet | Weights applied once; figure components may already include weights |
| Source spin/exchange | Eq22 and concluding text: raw CCC spin amplitude already contains direct/exchange treatment | Pair assembly is exchange of outgoing assignments, not re-addition of direct/exchange amplitudes |
| Finite-N defect | Eq25 δ=a−s b, where a=f_S^(N)(k,q), b=f_S^(N)(q,k), s=(-1)^S | δ need not vanish; smallness is physical/numerical condition to verify separately |
| Printed Eq26 | 2(|a|²+|b|²)=|a+s b|²−|δ|² | Literal printed source contains minus; preserve in source record |
| Corrected identity | Local elementary derivation: |a+s b|²+|a−s b|²=2(|a|²+|b|²) | C+D=2I, D≥0; no numerical estimate or new physical approximation |
| Half step | Bray§2.4 and Stelbovics concluding text/TableI | Raw equal-sharing singlet amplitude can require factor2 in amplitude/factor4 cross section; already-coherent amplitude must not be multiplied again |
| Incoherent shortcut | Bray§2.4 compares coherent result with 2(|a|²+|b|²) | Exact coherent result is 2I−D; replacing by2I needs a defect allowance |
| Partial-wave source | Eq27 includes Coulomb overlap phase exp(iσ_l(q)) and T_JS | Real probabilities cannot reconstruct these phases |
| Unequal sharing | Bray§2.5; Stelbovics Eq18 vs19 | Different long-range logarithmic phases impede general coherent combination; equality of magnitudes is the admitted source scope |
| Count/domain | Stelbovics flux Eq14 integrates secondary energy0..E/2 | Distinguish event-domain convention from inclusive two-electron count; do not import a second factor2 |
| Frame/recoil | Bray Eq5 uses ε_n+k_n²/2 and no explicit nuclear kinetic term | Fixed-center source energy relation; no finite-proton-mass law or lab/COM Jacobian supplied |

Exact algebra derivation: expanding C=|a|²+|b|²+2s Re(a b*) and D=|a|²+|b|²−2s Re(a b*) gives C+D=2I. This is a source-equation correction and pre-admission diagnostic. Symmetry alone does not establish physical convergence (Bray p10 says this explicitly).

## Independent actual numerical source table
Stelbovics TableI (p4), visually checked against extracted text, reports singlet energy DCS in units π a0² per Ryd at equal energy sharing εa=εb=E/2. E is total THREE-BODY energy, not incident electron energy. The listed CCC values already include factor4.
| E/Ryd | N | Npos | Published 4CCC | BRM independent reference |
|---:|---:|---:|---:|---:|
|2|20|8|0.0172|0.0140|
|2|30|13|0.0145|0.0140|
|2|40|18|0.0137|0.0140|
|2|50|24|0.0135|0.0140|
|3|42|19|0.0072|0.0068|
|3|44|20|0.0081|0.0068|
|3|46|22|0.0069|0.0068|
|3|48|23|0.0069|0.0068|

These are exact printed source decimals. They support normalization/provenance control in the TP model. They are not production H angular values, not fitted normalization factors, and not fresh scientific calculations. No convergence bound is inferred from the table.

## Candidate inventory and remaining obligations
1. **Bray v3 Fig28, primary joint cut.** E0=20eV, EA=EB=3.2eV, coplanar, CCC(18,5), TDCS units10^-18 cm² sr^-2 eV^-1. Multiple fixed relative-angle geometries and symmetric/fixed-angle cuts, including spin-weighted components. Paper§3.7 and caption explicitly state experimental relative points normalized to theory. Graph is accessible; exact raw values, complete energy/angular grid and producer-phase payload were not retrieved. No figure digitization adopted.
2. **Official CCC database**, https://atom.curtin.edu.au/CCC-WWW/ (turn2view0). Page links e-H_XSEC_LS.zip and dates current H dataset August2026, ni≤9. Link fetch through web failed; local default curl failed proxy connection. Archive contents were NOT inspected, so no archive-internal claim made. Official LXCat provider description https://nl.lxcat.net/contributors/ lines217–225 (turn7view2) explicitly identifies its CCC H database as angle-integrated and angle-differential results as on-request. No author contact initiated.
3. **Bray et al PRA90 022710 (2014)**, DOI10.1103/PhysRevA.90.022710, primary APS abstract turn5search2; institutional repository https://curate.curtin.edu.au/articles/journal_contribution/Ionization_amplitudes_in_electron-hydrogen_collisions/31464412 (search turn5search5). Abstract supports amplitude interpolation when pseudostates sufficiently dense; full text/payload not obtained, so this is a follow-up source, not adopted formula/data.
4. **Baertschy et al PRA63 022712 (2001), ECS**, DOI10.1103/PhysRevA.63.022712, primary APS abstract turn0search2/turn6search0, manuscript https://escholarship.org/uc/item/5q97s1wt. Abstract establishes calculated TDCS at17.6,20,25,30eV. PDF route encountered429 then bot challenge; no full numerical data accepted.
5. Hex prior official SQL scan and missing ionf / subthreshold H1 tmat are reused from existing intake. No scan, build or solve repeated.

## Existing evidence reuse
Read actual BASS_HE/research/he_ang_source_hex_20261024/NEXT_SOURCE_CONTRACT.json and he_ang_ddcs20_window_20261024/HANDOFF_RESEARCH_KO.md after parent staged them locally.
- Childers2004 TableIV window remains COMPLETE_SCOPED: E0=20eV; detected-electron E3–6eV, theta15–120degrees;40 retained values,32 principal inputs. Its already-computed window moments are untouched.
- HE-X1 science eb03981d15ad291375dd6d574a9c28809f85fc02; HE-ANG-CONTRACT896e5427100ad48d017deff2697b6f992ba029cd; Hex science15053fe4445a32e0544d644e864fe27780d08743; HE38 unchanged.
- Old budgets, errors, failed invocations and UNKNOWN_NOT_ZERO obligations remain with their original ledgers. No fresh scientific numerical allocation or budget transfer is claimed.
- Physical parent remains SOURCE_INPUT_PENDING. Actual source records plus finite-mass prescription/support error/count-frame map are still needed. This is input status, not a no-go.

## Intake execution/failure provenance
- SciSpace explicitly used twice; raw responses saved in scispace_search_raw.json and scispace_second_raw.json. Semantic results are discovery only; formulas/table adopted only from primary PDFs.
- Web searches primary CCC/LXCat/APS/arXiv/institutional routes; selected raw results in web_initial_raw.json and web_source_follow_raw.json.
- Initial default curl CCC site failed exit7 at configured browser-proxy:8889. No repeat of same default attempted.
- Exa fetch returned402 credit limit. No data content acquired through Exa.
- Read-only escalated curl public arXiv downloads succeeded exit0 for two primary PDFs.
- pdftotext and pdftoppm performed document extraction/rendering only; Stelbovics rendering emitted font-cache warnings but exited0 and table image was visually readable.
- SHA256 and byte lengths are artifact integrity checks, not scientific runtime calculations.
- No external messages, remote mutation, simulation, IVP, physics fixture or source-code execution.

