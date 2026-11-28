# Fresh R2/R4 joint-source intake — 2026-10-24

## Decisive new input
An actual numerical joint TDCS source was acquired: S. Jones and D. H. Madison, Physical Review A62,042701 (2000), “Ionization of hydrogen atoms by fast electrons”, DOI10.1103/PhysRevA.62.042701. TableIV plus the explicit angle statement on article page8 identifies two complete coplanar kinematic points:
E0=54.4eV, slower-electron energy5eV, slower angle210degrees clockwise from incoming forward beam, faster-electron angles4 or10degrees counterclockwise. The table supplies three separate numerical TDCS columns in atomic units.

| fast angle CCW | slow angle CW | CDW-EIS | CCC99 | experiment |
|---:|---:|---:|---:|---:|
|4|210|1.83|2.58|1.52|
|10|210|0.99|1.51|1.24|

These six values are original printed decimals, transcribed from a primary paper, not digitized from curves. Both the angle statement and table were visually verified in local rendered pages. The paper's abstract/front matter identify ground-state hydrogen, and Eq2 explicitly uses ψ1s. Other TableIV entries retain their peak-height status because their slow-electron angle is not specified by the table.

The previously completed CCC equal-sharing unit and TP normalization table are reused unchanged. This source concerns unequal sharing and supplies actual 3D-physics joint differential observables; no equal-sharing factor2/factor4 or raw-amplitude adapter is applied to reported TDCS.

## Source identity and acquisition
- Public institutional PDF: https://scholarsmine.mst.edu/cgi/viewcontent.cgi?article=2586&context=phys_facwork
- Publisher DOI: https://doi.org/10.1103/PhysRevA.62.042701
- Bytes218450, SHA2564e7b8d86cd9d29200f9de736b09215b045ceb592ef86b82a26c82a68e20864d3.
- Local jones2000.pdf, jones2000.txt; jones_page-09.png is articlep8, jones_page-10.png is articlep9/TableIV (institutional cover adds1page).
- Published8September2000; institutional cover dated1October2000. Preserve these as distinct dates.
- Copyright©2000AmericanPhysicalSociety. Institutional cover permits free public access while retaining US copyright; it does not declare an open data license. Numerical values and scholarly provenance are extracted; do not describe the PDF as CC-BY.
- Search discovered the official institutional source (search ref turn19search16). Search-service direct PDF open later gave403; read-only escalated curl succeeded. Access status is tool-path-specific.

## Exact source conventions and remaining producer fields
1. **Representation:** Published TDCS values, units “atomic units”. Physical dimensions are area/energy/solid-angle². An eventual SI conversion must document chosen a0/Eh constants rather than treating eV as atomic energy.
2. **Initial target:** H1s (Eq2).
3. **Energy:** incident54.4eV; slow5eV. Faster energy is not a printed table column; derive from the specified infinite-nucleus source shell if needed, marking it derived.
4. **Angles/frame:** coplanar scattering plane; Fig10 caption defines slow angle clockwise from forward beam, fast angle counterclockwise. Any canonical(theta,phi) mapping is a local derived convention and must preserve those signs. Source does not provide a lab/COM finite-mass transformation.
5. **Nuclear mass:** §II articlep2 explicitly assumes infinitely massive nucleus. Nuclear recoil moments from a physical finite-mass event law are therefore not supplied.
6. **CDW-EIS provenance:** Authors' own primary perturbative calculation. §III articlep4 explicitly neglects electron exchange at its chosen kinematics and labels faster electron “scattered”, slower “ejected”. This approximation must remain attached to these values. Reported estimate “less than2% numerical uncertainty at peak values” is a peak statement; the two210degree anchors need not be at theoretical peaks, so do not attach that2% as a certified pointwise bound.
7. **CCC99 provenance:** Values supplied by Igor Bray; reference[9] says “I.Bray(unpublished)” and acknowledgment thanks him for results prior to publication. Jones2000 is the publication that makes these numbers available. No identity equivalence to the earlier pinned Bray arXiv preprint or current2026CCC archive is established. Spin-resolved amplitudes and raw Coulomb phases are unavailable in this table.
8. **Experiment provenance:** Republished data from Ehrhardt and Röder, in Coincidence Studies of Electron and Photon Impact Ionization (Plenum,1997),pp1–10, ref[11]. Primary original source not retrieved here. Jones discusses relative54.4eV data ref[29] Schlemmer etal JPhysB22,2179(1989), brought to absolute scale via ref[11].
9. **Spin/count:** These are already reported cross sections, not raw spin amplitudes. No additional spin weights or inclusive-count2 factors are authorized by this table. Separate raw singlet/triplet fields unavailable. For future event admission, resolve producer event-domain/count explicitly.
10. **Uncertainty:** Articlep4 reports experimental internormalization±10%;54.4eV absolute scale±35%. No covariance matrix, per-point statistical error, or explicit probability model is supplied. Their practical disagreement analysis later questions the nominal relative estimate for recoil comparisons. Preserve quoted values as source metadata; deterministic boxes/statistical confidence intervals require explicit separately justified interpretation.
11. **Support:** Two located coplanar points at one incident energy and one slow energy; zero-measure subset for full continuous5D joint law. No off-plane/energy interpolation, total/event integral or omitted-domain bound follows from these points.
12. **Meaning of recoil:** “Recoil peak” names an ejected-electron angular lobe. It is not a measured proton-recoil distribution.

## New executable science contribution
A bounded source-specific sparse joint-anchor unit can admit these two geometries, preserve the three physical columns, and derive normalized angular contrast or ratio between fast4degrees and10degrees at common slow210degrees. A common experimental absolute scale would cancel from such a ratio under an explicitly common-scale model, while relative-angle uncertainty remains. That cancellation is a conditional mathematical construction, not an inferred covariance model. It creates a genuine new joint observable/control using source numbers; it cannot close full HE-ANG admission.

Suitable code/data obligations for root freeze: exact literal source rows; signed-angle→vector mapping with declared beam axis; source-specific infinite-mass shell metadata; units; separate producer columns; exclusion of source-unknown-angle extrema from coordinate interpolation; and tests against transcription/sign/unit mistakes. No science execution or tolerance/budget decision made in this intake.

## Official CCC archive — previous access gap resolved
- Index https://atom.curtin.edu.au/CCC-WWW/ downloaded as ccc_index.html.
- Exact linked archive https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/e-H_XSEC_LS.zip downloaded.
- Bytes7010887; SHA25657730e72656639e92c47c1b8457db0edac5a69ae93db6c357471a93759af1fc9.
- ZIP directory3162files,26428148uncompressedbytes. Exact member inventory ccc_archive_members.txt.
- Root README explicitly calls these integrated cross sections in a0² for ni≤9,nf≤10; TICS=sum positive-energy pseudostate channels; TCS=sum all open channels.
- Read both README entries plus selected1S.1S,TICS.1S,TCS.1Sheaders. Fields E(eV),sig,asym and producer calculation-path labels. TICS.1S threshold line13.6058000eV retained as a source literal, not substituted into Jones2000.
- Current index says August2026; ZIP member mtimes2026-10-12. This is version/provenance evidence, not proof of same calculation provenance.
- No explicit license text was observed in the inspected README.
- Archive is not admitted as joint TDCS input. This conclusion follows from its explicit integrated-data specification, not mere missing filename search.
- Additional known directory endpoint https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/ was read into ccc_h_directory.html. Response ends midtag among4d...files; preserve as incomplete/truncated directory observation. Do not claim a complete negative directory survey.
- No provider-wide solve, source-code scan or old Hex task repeated.

## Other new search and local attachment coverage
SciSpace was explicitly queried anew for publicly downloadable numerical hydrogen TDCS/amplitudes; raw response scispace_raw.json. It returned relevant literature and also proton-impact/H2/metastable entries, which were excluded from H1s-electron joint admission. Targeted primary-source web search located Jones2000 and official CCC links.
ECS eScholarship landing https://escholarship.org/uc/item/5q97s1wt returned a JavaScript bot challenge; no payload acquired. MDPI primary candidate https://www.mdpi.com/2218-2004/8/2/26 returned429; its data availability remains uninspected in this intake.
Local project_sources/19-papers.zip and18-literatures.zip were inspected by central-directory names only. The first lists8cosmology-related papers; the second7cosmology/kinetic-theory books. No broad extraction performed, and no atomic-H TDCS file was identifiable by these names. File contents of those PDFs were not searched, so this is a filename-level coverage statement.

## Execution and policy scope
All commands were read-only downloads, archive listings/selective text reads, PDF text/render extraction, and integrity hashes. No physics solver, quadrature, source sweep, fixture replay, IVP, code implementation, or numerical uncertainty calculation executed. Fontcache warnings occurred during rendering; rendering exited0 and relevant images were visually readable. Prior budgets/failures/UNKNOWN_NOT_ZERO stay with their original ledgers; no allocation transferred or reset. No author contacted, no external message sent, no repository mutation/publication.
Full HE-ANG gate remains SOURCE_INPUT_PENDING; this is a finite real new payload/control input, not a full event provider or impossibility conclusion.

