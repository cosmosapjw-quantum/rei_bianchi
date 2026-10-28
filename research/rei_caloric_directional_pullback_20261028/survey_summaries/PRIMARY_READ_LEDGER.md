# Primary-content and retrieval ledger

Intake date: 2026-10-28, Asia/Seoul. This is a new literature/physics intake. Closed Phase 1, Phase 2 and F1 closure reports were not reopened or modified. No scientific module or numerical calculation was executed.

## What is preserved

SEARCH_ROUND1_RAW.json and SEARCH_ROUND2_RAW.json preserve the actual queries and tool responses. QUERY_CANDIDATE_LEDGER.json records 40 SciSpace candidate records, 32 requested/returned Exa URL records and the distinction from 10 selected papers with primary passages inspected. Multiple URLs or versions of a paper do not increase the paper count.

The originals/ directory holds provider-returned primary-source text and complete fetch envelopes, with request URLs and extraction caps. These are **primary-content extraction snapshots**, not byte-identical downloaded publisher PDF files. Their local hashes identify the preserved extracts; they do not certify publisher PDF bytes or a Git commit. File names ending EXTRACTED.txt contain the text used for local passage reads. The EXA.json counterparts preserve tool results including errors.

The three initial search angles were particle-count/first-law thermodynamics, recombination interfaces, and modern feedback/conservative updates. S4/E4 were targeted coverage-gap followups. No broad new mathematical literature census was undertaken for the controller's later moving-knot selection; the directional formula in the synthesis is a direct conditional derivation.

## Primary paper identities and scientific reading

Line numbers below refer to the saved extraction, except the Bianchi paper, whose original PDF tool line/page references are retained. Metadata/heading locator searches were also used; they are not counted as complete scientific reading of surrounding sections.

| ID | Original identity | Discovery IDs | Primary passages actually inspected | Use and limits |
|---|---|---|---|---|
| P01 | Hui & Gnedin, Equation of State of the Photoionized Intergalactic Medium; arXiv:astro-ph/9612232; DOI 10.1093/mnras/292.1.27 | S4 SciSpace 0wnc61pdps9w and 4kabn51d89; E1 | P01_HUI_GNEDIN_TEX_EXTRACTED.txt 45–90, especially Eq. (2) and normalization explanation 65–79. Original journal page 29. Also retrieved journal PDF extraction/header. | Particle-number term and proper-volume heat definition. Eq. (2) OCR is degraded; the synthesis's legible equation is independently derived, not claimed to be a character-perfect transcription. No full-paper scientific read. |
| P02 | Ali-Haïmoud & Hirata, HyRec; arXiv:1011.3758; DOI 10.1103/PhysRevD.83.043513 | S2 SciSpace 45gwrpvqjn and 2jgcy1ojxu; E2 | P02_HYREC_EXTRACTED.txt 35–123, especially 41–59 and Eq. (12) at 113–119; 926–950 with 930–950 reread without truncation. | \(x_e\), \(n_H\), matter/radiation temperature, standard Compton law, tight-coupling switch. Extraction cap 120000 characters cuts the later reference material; no full radiative-transfer or appendix review. |
| P03 | Lee & Ali-Haïmoud, HyRec-2; arXiv:2007.14114; DOI 10.1103/PhysRevD.102.083517 | S2 SciSpace mli4agns2dy1 and 47zg2d28t2; E2 | Abstract in versioned arXiv extracts; P03_HYREC2_NSF_EXTRACTED.txt 136–191, Section III C, including Eqs. (12)–(15), plus paper header/abstract. | Helium mass/number correspondence, cosmological calibration and injection dependence. Versioned arXiv fetches returned abstract only; original author manuscript was then read from NSF PAR. Accuracy claims are used only in their stated parameter domain. |
| P04 | Seager, Sasselov & Scott, A New Calculation of the Recombination Epoch; DOI 10.1086/312250 | E2 | P04_RECFAST_EXTRACTED.txt 60–94, chiefly Section 3 at 66–88. | The paper explicitly calls its temperature equation a truncated adiabatic/Compton equation and defines H-normalized fractions. Some displayed equations are absent from the HTML extraction; no unsupported equation transcription is supplied. |
| P05 | Liu, Ridgway & Slatyer, DarkHistory; arXiv:1904.09296; DOI 10.1103/PhysRevD.101.023530 | S3 SciSpace q13atlavh4zq and 1usaeoge0g | P05_DARKHISTORY_EXTRACTED.txt 48–95, Section II; abstract/intro passages appeared in locator output. | Channel separation, deposition dependence on ionization, source feedback. The Eq. (5) extraction is incomplete; exact coefficients are cross-grounded in readable HyRec code and the explicit 2026 formulas. Later cascade appendices were not read; the 120000-character extraction is not the full paper. |
| P06 | Ng & Chu, Constraining the Locally Rotationally Symmetric Bianchi Type I Model with Self-Consistent Recombination History and Observables; arXiv:2503.14969v2, revised 4 Aug 2025; DOI 10.1103/3njx-sy22 | S3 SciSpace y08oq1t2dr8i and 4f12nwhywzv6 | Generic-fetch PDF source lines 0–337 and the continued output through 542; scientific use is Section II, lines 118–157 and 215–359, Eqs. (4)–(7), (17)–(23). Metadata page 8–30. | Isotropic-pressure/radiation approximation and hydrogen-only recombination scope. Original-source excerpts are in P06_BIANCHI2025_PRIMARY_READ.txt and RECENT_PRIMARY_METADATA_AND_BIANCHI_CONTINUED.txt. Later statistical constraints and observational claims are not independently assessed. |
| P07 | Scott & Moss, Matter temperature after cosmological recombination; published body title Matter temperature during cosmological recombination; arXiv:0902.3438; DOI 10.1111/j.1365-2966.2009.14939.x | S4 SciSpace 5o5tqucv9npg and 1n5fiybf9s; E4 | P07_SCOTT_MOSS_EXTRACTED.txt 1–97, complete extracted short paper, especially 33–75, Eqs. (1)–(7). | Compton time and tight-coupling transition; mathematical OCR is imperfect, so primary readable HyRec Eq. (12) supplies the explicit common equation. No numerical results reproduced. |
| P08 | Smith et al., Grackle: a Chemistry and Cooling Library for Astrophysics; arXiv:1610.09591; DOI 10.1093/mnras/stw3291 | E4 | P08_GRACKLE_EXTRACTED.txt 140–240, Sections 3.2–4.1.2, Eqs. (5)–(15), plus candidate abstract. | Internal-energy/chemistry updates, subcycling, composition-dependent inverse temperature. No solver execution or whole-library review. |
| P09 | Khan, Ray, Kulkarni & Dasgupta, Stronger Constraints on Primordial Black Holes as Dark Matter Derived from the Thermal Evolution of the Intergalactic Medium over the Last Twelve Billion Years; arXiv:2503.15595v2, 17 Dec 2025; DOI 10.1103/8h9x-hfpk | E3 | P09_PBH2025_EXTRACTED.txt 285–338, 412–438, 480–503, 1198–1236; version marker at 76. Current metadata page 8–30. | Eqs. (8)–(9), changes to DarkHistory, Appendix A heat terms. Only model/interface implications used; PBH bounds or astrophysical calibration are not adopted. |
| P10 | Yin, Cheng & Visinelli, Primordial Black Hole Abundance from Reionization; arXiv:2602.06794v2, 19 Oct 2026; DOI 10.1016/j.dark.2026.102487 | E3 | P10_PBH2026_EXTRACTED.txt 78–143 first; then explicit version P10_PBH2026_V2_EXTRACTED.txt 83–169, Eqs. (9)–(20), plus header/abstract; locator hits at 193 and conclusions. Current metadata page 8–32. | **Explicit v2 supersedes unversioned body for synthesis.** Supports redshift signs, channel-specific tabulated deposition and stated scope, not a general nonlinear-feedback guarantee. No constraints reproduced. |

All paper URLs are in the synthesis and raw fetch envelopes. Primary authors and original publication/version evidence override index metadata.

## Official code/documentation inspected

| Snapshot | Actual read | Relevant evidence and limit |
|---|---|---|
| C01_HYREC2_REPO_EXTRACTED.txt | 1–69, complete | Official README, output columns redshift / electron fraction / matter temperature in K, listed source files, July 2020 code version label. Repository statistics were not used as scientific evidence. |
| C02_RECFAST_SOURCE_EXTRACTED.txt | 1–234, complete | Official CAMB documentation comments: normalization, stored a*Tmat and April 2026 change note. The page is not the entire Fortran implementation. |
| C03_HYREC_HISTORY_EXTRACTED.txt | 280–355, especially 301–351; function locator hits elsewhere | rec_Tmss, rec_dTmdlna, Tm_implicit units and mathematical RHS. No whole-file algorithm review. |
| C04_HYREC_ENERGY_INJECTION_EXTRACTED.txt | 1–247, complete, across successive reads | Injection/deposition distinction, explicit approximate recipes and chi_heat/chi_ion/chi_exc definitions. This does not certify all physical recipes or establish a new BASS implementation dependency. |
| C05_CAMB_RECFAST_RAW_EXTRACTED.txt | 1210–1255 and 1380–1426; specific temperature-variable locator hits | Total electron fraction construction, a*Tmat storage and branch-specific temperature equations. No current release/commit identity was established. |

These source URLs track public master branches. The snapshots are inspection evidence on the retrieval date, not interchangeable with the project's frozen production source. No compilation, import, test or scientific execution occurred.

## Retrieval and metadata limitations

1. SciSpace returned several arXiv records with 2022 index dates for much older papers. Dates in the synthesis use the original publication/preprint/version evidence.
2. Exa's versioned HyRec-2 and Bianchi arXiv URLs initially returned only abstracts. HyRec-2 full primary content was obtained from the NSF author-manuscript repository. For Bianchi, an APS accepted-manuscript URL returned CRAWL_NOT_FOUND; the Exa searching guide permits another fetch tool when full-content retrieval fails, so the original arXiv PDF was read with the generic web fetch tool. No general fallback search was performed.
3. The first unversioned arXiv:2602.06794 extract and its current abstract were not identical in methodology. An explicit v2 fetch succeeded and showed channel-specific efficiencies rather than the older factorized formula. The generic versioned PDF attempt returned DisabledError; the successful public Exa HTML read is separately preserved.
4. The explicit v2 Exa envelope incorrectly printed “Author: B. P. Abbott et al.” while the paper body and arXiv metadata identify Yin, Cheng and Visinelli. The envelope field is not adopted.
5. The HyRec HTML rendering contains a 2026 rendering date despite the paper's 2011 identity. No new 2026 HyRec publication is inferred.
6. PDF/OCR extraction defects are preserved. Formula claims use readable equations/code plus declared independent derivation, not inferred missing glyphs.
7. No model/backend identity, authorship independence, source quality or numerical acceptance is inferred from a tool's result count, source rank or evaluative label.

## Skill application and scope decisions

Applied Exa Search plus searching.md, patterns-papers.md, patterns-code.md, source-quality.md and synthesis.md; reused/read physmath-research-loop 1.0.0 SKILL, RESEARCH_POLICY, THEORY_LOOP and EVIDENCE_AND_HANDOFF.

The current request explicitly requires distinguishing candidate counts from primary reading. Therefore the Exa skill's suggested numResults-based “sources reviewed” wording was not used as a scientific-read count. Source quality for theoretical physics was assessed through original authorship, explicit equations/assumptions and official implementation, rather than excluding theoretical work for lacking a commercial implementation.

This agent retains the observable task name /root/finite_thermal_blind_reviewer but acted here as literature/physics intake with full prior knowledge. This work is not described as a blind review. No final R/C stage decision or new stage count is issued.

## Unread material and remaining dependencies

Full radiative-transfer derivations, cascade appendix details, observational likelihood analyses, nonselected candidate bodies, repository-wide code and source history were not needed for this intake and were not read. Their correctness is not certified.

For the selected moving-knot inverse construction, the parent owns the exact current repository contract and admissible knot/domain directions. The conditional formula is supplied in the synthesis. The optional physical chemical pullback requires its declared F_T; no numerical value or physical zero derivative is invented. Physical REI state/native25 activation/error radii remain unprovided. None of these limits requires repeating the accepted caloric/driver decomposition.

