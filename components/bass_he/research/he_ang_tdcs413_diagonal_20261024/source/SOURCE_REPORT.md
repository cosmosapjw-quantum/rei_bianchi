# Next HE-ANG source intake after PR97 — 2026-10-24
Role: Astra source/theory intake R2/R4, not independent reviewer. Frozen PWBE theory reused. No scientific kernel evaluation, fit, quadrature, symbolic solve, simulation, or extra agent executed.

## Decisive candidate
Use a bounded experimental shape benchmark of the already frozen spin-corrected PWBE model against the FIAS-R-39 Table1 E0=413.6eV, EA=EB=200eV, coplanar equal-polar-angle diagonal. Sixteen source settings exist; thirteen currently have clear transcriptions. Three settings are explicitly unresolved and excluded, independently of any model prediction. This is actual joint coincidence TDCS information, not a DDCS marginal; it is a finite geometry cut, not a full physical joint provider.

Parent's proposed next science unit is exact equal-sharing coplanar PWBE one-dimensional angular shape plus common-positive-scale weighted L-infinity discrepancy. Printed pointwise1sigma may serve as a declared numerical weighting scale; this does not make the resulting number a confidence statement, p-value, or deterministic error certificate. Source covariance is unavailable. No physical HEANG admission follows.

## Primary source identity and reuse
Weigold E., Noble C.J., Hood S.T., Fuss I., Electron impact ionization of atomic hydrogen: experimental and theoretical (e,2e) differential cross sections.
FIAS-R--39, June1978, versionv1, INIS RN10438831.
Official record https://inis.iaea.org/records/5gbvq-nbn24
PDF https://inis.iaea.org/records/5gbvq-nbn24/files/10438831.pdf?download=1
Reused local ../next_heang_source_20261024/weigold1979.pdf (filename shorthand; actual document1978report),917299bytes.
SHA256 verified unchanged: aaa750d5d5f0652ba7e6090878f938174fc26268265c256022c4d9437c3a96a8.
No repeated download. No explicit PDF redistribution license established; private renderings stay outside public PR deliverables.
Related journal DOI10.1088/0022-3700/12/2/019, J.Phys.B12,291–314(1979); do not assert byte/page/equation identity with report.

## New correction discovery, actual accessible content
Fresh Exa search located the actual journal corrigendum:
https://iopscience.iop.org/article/10.1088/0022-3700/12/8/519
https://iopscience.iop.org/article/10.1088/0022-3700/12/8/519/pdf
DOI10.1088/0022-3700/12/8/519; J.Phys.B12,1450(1979).
Exa full-content fetch of this primary publisher PDF returned the correction body: final page314 was not printed; the correction supplies missing references. In this retrieved corrigendum there is no Table1 numerical correction or Eq21 correction. This finite claim does not prove no other corrections exist. No original PDF bytes acquired/hash asserted for this corrigendum.
Ordinary web open could not fetch corrigendumPDF. Exa is the actual primary-text retrieval here, not just a discovery claim.

## Selected geometry and observational contract
Reportp6/PDF9: polar angles thetaA,thetaB are measured relative to incident momentum k0. Coplanar experiments have phiA−phiB=0 orpi. For unequal energies only, A=faster and B=slower; at equal energy A/B retain detector labels. Electrons indistinguishable.
Table1 caption/reportp30/PDF33: phiA−phiB=pi except one explicitly marked20degree series, unrelated to selected413.6diagonal.
Selected row: thetaA=thetaB; E0=413.6eV; bracketed EA=200eV. Reportp19/PDF22 independently specifies EA=EB=200eV and phiA−phiB=pi for413.6data.
Source Eq1 gives separation epsilon=E0−EA−EB and says ion recoil energy ignored; Eq2 q=k0−kA−kB. These source decimal energies are rounded observations, not exact infinite-mass atomic constants.

Parent must fix the model energy-shell convention before execution: preserve printed413.6/200/200 in source metadata; separately declare either source-rounded13.6eV binding or an exact hydrogen binding with a nearby on-shell incident energy. Do not silently overwrite experimental energies. A model adjustment justified as within printed rounding is not a source measured value.

Measure/count: source theory reports differential density in dEA dOmegaA dOmegaB; observations are two-detector coincidences of electrons from the same ionizing event, background-subtracted. They are not event counts per angular bin or a one-electron yield. Do not multiply by2 to repair a density/count convention. No spin-resolved apparatus is described in inspected experiment paragraphs; a numerical initial spin-density matrix is not supplied by the table. Frozen unpolarized PWBE theory remains its explicit model assumption.

## Relative normalization and uncertainty
Table caption: each independent series maximum is displayed as100. Parenthesized figures are one-standard-deviation errors of individual points.
Reportpp18–19/PDF21–22: no absolute crosssections obtained. At413.6/250/113.6eV different-angle series share one unknown arbitrary normalization; separate interseries normalization percentage sigmaN excludes point parenthesis errors. At100eV each series is independently normalized, outside this selection.
Selected diagonal sigmaN column prints0. This denotes the reference-relative series normalization, not exact absolute calibration or zero common-scale uncertainty.
Reportp10–11 describes statistical errors after accidental-coincidence subtraction and repeated scans. For the equal-angle scan the preset scaler uses a voltage-to-frequency converter measuring electron current or mean atomic-beam intensity; reported long-term stability is a fewpercent.
The full covariance of normalized points, correlation from common normalization, count likelihood, and calibration systematics are not supplied. Independent Gaussian errors are not established. A pointwise1sigma is not a deterministic bound. The measured0(1) at60degrees must remain0(1), not be dropped, clipped upward, or treated as exact zero probability.
Fig3 uses normalization to DWIA1 at(thetaA,thetaB)=(40,45)degrees for plotting, and rescales other theory peaks. This is not an independent experimental absolute scale and is not adopted.

## Instrument resolution, limits of point comparison
Reportp7/PDF10: analyzer angular positions set better than0.2degree; incoming beam maximum angular divergence1degree. These are different quantities and neither is a numerical detector-acceptance kernel.
Reportp9/PDF12: separation-energy spectrum resolution approximately1.0eV FWHM; hydrogen peak13.6eV, molecular peak15.9eV. This is not an assertion that each selected detector energy has independent1eV Gaussian error.
Detector field of view is aperture-defined, but no numerical angular response convolution kernel is supplied in inspected paragraphs. Benchmarking nominal point values is a scoped approximation; a discrepancy cannot be assigned entirely to model dynamics while detector response and calibration covariance remain unknown.

## Bounded transcription
Candidate JSON stores decimal strings, all16settings with unresolved fieldsnull and explicit exclusions. CSV contains only13clear settings.
Clear(theta,value,point1sigma):
32,10,3;34,11,3;36,17,3;38,28,4;40,50,4;42,76,5;43,82,6;44,100,6;50,30,3;52,15,2;54,4,1;56,2,1;60,0,1.
38degree visual28(4) corrects OCR20(4).
Unresolved source scan:
45degree value89 clear, error3or5.
46degree value84or86, error3or5.
48degree value54or58, error4clear.
Do not guess these cells, fill from model, or treat OCR as authority. Root independent visual read pending; journal representation attempts did not recover a cleaner table.
Private source images: table1_5000.png fulltable, table1_diagonal_crop.png, table1_midvalues.png, geometry_p6.png, normalization_p18.png, normalization_p19.png, apparatus_p7.png, resolution_p9.png, scaler_p11.png.

## Fresh search evidence and access gaps
SciSpace semantic question: What primary numerical tables, normalization conventions, uncertainty definitions, or published corrections exist for Weigold,Noble,Hood,Fuss hydrogen ionization at413.6eV with200eV outgoing electrons in FIAS-R39 and JPhysB12,291?
One fresh SciSpace call, scispace_raw.json. It returned originalDOI and a journal mirror URL, but no clear numeric table or erratum.
One Exa search, exa_search_raw.json; primary corrections discovery as above. Two Exa fetch batches, exa_fetch_raw.json and journal_access_raw.json.
Publisher originalPDF Exa fetch returned abstract/bibliographic references, not article table; do not count as original fulltext access.
SciSpace-listed https://members.iinet.net.au/~stuarts/positrons/assignment3refs/jbv12i2p291.pdf shell request returnedHTTP503; originalhttpURL viaExa returnedCRAWL_HTTP502. No cleaner bytes obtained.
Exa officialIAEArecord fetch timed out; ordinary web fetch succeeded (primary_web_raw.json).
No other source claimed absent and no exhaustive literature/no-correction theorem claimed.
Fees/remoteCPU unknown, explicitly UNKNOWN_NOT_ZERO. Existing Wolfram and four-child costs/failures unchanged. Wolfram work belongs to root after scopefreeze, not this source task.

## Prior scientific qualifications preserved
PR97 PWBE spin/azimuth theory is reused; no replay. FIAS Eq21 printed−2DX is not admitted as unpolarized. Buică BO exchange is distinct from exact-swapPWBE. Buică later erratum access/version limitation persists. Prior DDCS/Hex/CCC/TDCS54 are unchanged, not promoted to fulljointlaw.

## Bounded ANU follow-up before execution
Root supplied https://dspace-test.anu.edu.au/handle/1885/733728310 . Ordinary web open failed; one read-only shell download succeeded and saved private/anu_record.html. The page explicitly identifies itself as a test environment and the record collection as DevOps Pure Testing. It confirms1979/authors/DOI10.1088/0022-3700/12/2/019, but shows no downloadablePDF link. The server-rendered public page includes its loaded ORIGINAL bundle05e3a1d3-b475-4434-9ea1-8fb1263cd2e8 and bitstream pagination with totalElements0,totalPages0. Thus this particular accessible test record supplies no cleaner primaryPDF. This is a record-local finding, not an absence claim about all ANU repositories. No further scan or access-control probing performed. Preserve thirteen clear rows and the three transcription exclusions; no input was silently changed.

