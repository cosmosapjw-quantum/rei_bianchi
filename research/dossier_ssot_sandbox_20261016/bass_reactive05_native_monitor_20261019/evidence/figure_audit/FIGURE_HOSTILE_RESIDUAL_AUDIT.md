# BR05 final figure hostile and residual audit

**Final verdict: PASS for both figure families at both requested widths, with the accompanying scientific captions.** No P0 or P1 issue remains in the inspected final images. This verdict follows the completed C9 code/math gate (`PASS_SCOPED`, 2026-10-19 10:09:47 UTC), the final repaired rendering, direct visual inspection of all four PNGs, and the independent 44/44 visualization checks. It does not add a physical convergence or absolute-error claim.

This review applies project sources `07-Figure-Residual-Error-Pass.txt` and `08-Figure-Hostile-Audit.txt`. The source/data/figure hashes and exact print dimensions are recorded in `FIGURE_NUMERIC_LAYOUT_AUDIT.json`. No project source, final image or original input was changed by this reviewer. The reader should retain `FIGURE_CAPTIONS.md` with the figures; those captions state definitions that cannot be inferred safely from a curve alone.

## 1. Reconstructed scientific intent

The time–birth figure tests whether increasing birth refinement changes the finite interaction between two time grids. It shows observable-dependent sensitivity and a smaller mixed difference on the next refinement rectangle; it does not determine an asymptotic order. The monitor figure shows how a physically retained native birth population relates to a well-defined frozen diagnostic, keeping target-age shape, actual source/clock effects, transport increments and the final native age distribution distinct.

| Figure and panel | Intended information | Correct comparison and units |
|---|---|---|
| Time–birth (a) | Photon-number dependence on birth refinement at two time grids | Six native final numbers, reference-comoving \(\mathrm{m}^{-3}\), explicitly scaled and shifted |
| Time–birth (b) | Remaining mean-age sensitivity | Survivor-weighted age in seconds, explicitly scaled and shifted |
| Time–birth (c) | Direction-sensitive energy observable | Dimensionless energy-weighted \(q_2\), explicitly scaled and shifted |
| Time–birth (d) | Finite mixed-difference reduction | Ratio of two absolute finite mixed differences; dimensionless |
| Monitor (a) | Frozen survivor-age resolution | Unit-mass \(W_1\), seconds, all 16 step/rule values within each energy envelope |
| Monitor (b) | Frozen CDF discrepancy | Unit-mass CDF supremum, dimensionless; same 768 rule records |
| Monitor (c) | Additive source/clock and native transport increments | Both normalized by the same constant-source newborn reference, ppm |
| Monitor (d) | Actual final retained age population | Photon-number-weighted probability per logarithmic bin; no native cohort merging |

## 2. Caption reconstruction and semantic comparison

The captions in `FIGURE_CAPTIONS.md` reconstruct the plotted quantities directly from the CSV columns and plotting script. They specify the numerical offsets, the finite mixed-difference formula, the frozen selector's role, the deterministic meaning of the envelopes, the two additive ppm definitions and the local acceptance scope. These statements agree with the final provenance and C9 scope.

At the initial audit inventory, a final report/README caption was not yet available for comparison. The supplied captions therefore form the audited accompaniment; a later publication caption should preserve these definitions. The image titles already distinguish “Frozen-reference” from “Actual final cohort”, so the figure itself does not silently equate their measures.

Neither figure plots a total-energy residual or a photon-work discrepancy. The native number increments in panel (c) must not be described as a thermal or total-energy closure test. No such claim is present in the audited captions.

## 3. Scientific semantic audit

The exact six-point grid was checked, including the new \((N_t,r)=(16,8)\) point. Four mixed-difference ratios were recalculated independently in Decimal96 from the final tables. The displayed values round to 0.096, 0.078, 0.086 and 0.083 for number, mean age, second age moment and \(q_2\). These values support a reduction on the tested rectangle, with no inferred universal order.

All 768 frozen rule rows enter the 48 energy envelopes, with exactly 16 records per energy. The minima and maxima reproduce the displayed CSV values exactly in binary64. The narrow band in much of the CDF plot is real within this diagnostic; increasing its visual thickness would misrepresent the data.

For all 16 newborn batches, the two relative increments reproduce their definitions and add to the combined shift. The maximum dimensionless arithmetic discrepancy is \(2.710505431213761\times10^{-20}\). In particular, the orange curve is an increment from the source/clock-frozen measure to the actual native measure, not the total shift from the constant-source baseline.

The histogram covers every recorded final age. The independently reconstructed 32 values match the supplied display CSV exactly; their sum is 0.9999999999999788. All 314,624 cohort records have positive age and nonnegative retained count; 21,652 have zero retained count and remain present in the native data. The histogram therefore suppresses no positive-age cohort by its range selection. Display binning is not a modification to solver cohorts or an age-error certificate.

## 4. Print-size and residual error audit

All four final PNGs were opened directly at their original pixel resolution. The 182 mm figures use a 2 by 2 layout; the 90 mm figures use independently created 4 by 1 layouts rather than a scaled-down copy. The PNGs carry 220 dpi output and the matching one-page PDFs have the requested media boxes. Every inspected visible title, axis label, major/minor tick, legend and bar annotation is at least 7.5 pt. Math glyphs, minus signs, exponents, subscripts and Greek symbols render correctly.

| Figure | Final dimensions | Minimum text size | Minimum adjacent visible tick-label gap |
|---|---:|---:|---:|
| Time–birth, wide | 182 × 142 mm | 7.5 pt | 15.82 pt |
| Monitor, wide | 182 × 142 mm | 7.5 pt | 10.80 pt |
| Time–birth, narrow | 90 × 234 mm | 7.5 pt | 10.90 pt |
| Monitor, narrow | 90 × 234 mm | 7.5 pt | 12.48 pt |

The independent artist check includes both major and minor tick labels, including their actual displayed ranges; it is stricter than checking canvas boundaries alone. No pair of adjacent visible tick labels overlaps, and all audited text lies within the canvas. The 90 mm panels retain readable titles and legend symbols. When placed into a document, their stated physical widths must be preserved; further shrinking would require a new print-size check.

## 5. Layout, reading order and text reduction

The wide layouts read left to right and then down; the narrow layouts read top to bottom with the same panel lettering. Blue circles and orange squares consistently distinguish the two time grids, and shape differences preserve the comparison if color is less visible. The monitor has one frozen-reference envelope family, two explicitly named number increments, and one native histogram; no additional legend hierarchy is needed.

The current short monitor title “Newborn number increments” is preferable to restoring its previous longer text. The detailed measure definitions belong in the caption, not another in-panel annotation. A second legend or connector would occupy data space without resolving any remaining scientific ambiguity. Keep the current layout and the concise axis text; retain the caption definitions.

## 6. Ranked audit ledger and minimal repairs

| ID | Priority | Finding and evidence | Minimal correction / final state |
|---|---|---|---|
| R0 | P0 | Frozen reference, actual native measure, numerical offsets and finite mixed term could be conflated if captions were omitted | Explicit image titles, provenance and supplied captions distinguish them. No incorrect claim found; closed |
| R1 | P1 | Earlier 90 mm monitor (c) title extended outside the canvas; the parent's actual failed render log records the text | Title shortened to “Newborn number increments”; direct viewing and boundary check pass; closed |
| R2 | P1 | The earlier energy-axis scientific tick labels around \(3\times10^1\) and \(4\times10^1\) were visually crowded at both widths | Parent changed only the labels to explicit 15, 25, 50, 100 eV majors and hid minor labels. Log axis and data unchanged; final spacing check passes; closed |
| R3 | Tooling | The first parent boundary guard counted off-range tick labels that were not rendered; its failure log is preserved | Parent filters the actual visible range. This was a guard false positive, not a physical failure; closed |
| R4 | Tooling | The independent audit's first JSON write rejected a NumPy scalar boolean after the computations completed | Only the audit serializer was corrected; the corrected run passed all 44 checks. Recorded separately in `INITIAL_AUDIT_SERIALIZATION_FAILURE.json`; closed |
| R5 | P2, declared scope | The deterministic step envelopes are often thinner than the line; the mixed ratio and offsets need definitions outside the image | Preserve the supplied caption. Do not artificially broaden bands or label ratios as orders; no layout repair required |
| R6 | P3 | Separate narrow/wide layouts must keep identical panel names, units, colors and data selection | Direct viewing and data reconstruction agree; no inconsistency found |

The two genuine visual repairs were made by the parent before this final verdict. The reviewer made no source or image mutation. Parent render receipts retain both unsuccessful preliminary attempts, the successful title repair, and the successful final tick repair.

## 7. Independent verification questions

1. **Are the plotted baselines exact physical references?** No. The shifted axes state arbitrary numerical offsets, and the caption explicitly forbids an exact-solution interpretation.
2. **Does the small change in surviving number imply age convergence?** No. The same figure shows visible age and quadrupole sensitivity; the captions make no joint convergence claim.
3. **Can the bar heights be converted into a universal convergence order?** No. They are two finite interaction magnitudes on one rectangle, derived directly from six states; no asymptotic model has been established.
4. **Do monitor panels (a)/(b) measure the error of the nonlinear H/He/D history?** No. They compare a specified frozen selector and constant-source kernel with target-age atoms. The native measure is displayed separately.
5. **Are the bands statistical confidence intervals?** No. Their exact minima and maxima are taken over 16 deterministic step records per energy; the caption states this.
6. **Are the two ppm curves normalized consistently?** Yes. Both use the same exact constant-source reference; their sum reproduces the combined shift, as independently checked for every batch.
7. **Does “accepted” silently mean outer adaptive acceptance?** No. The caption and C9 gate restrict it to successful local fixed-step transactions. No four-corner controller is instrumented here.
8. **Does the age histogram discard cohorts or alter the dynamics?** No. Every final record contributes to the display calculation; zero-weight records remain in the native source data, and the histogram changes no solver cohort.

These answers support the keep-layout option with precise captions. Redesigning panels or adding a second legend does not improve any of the verified scientific distinctions.

## 8. Final gate and reproducibility

The final rendering completed at 10:05:24 UTC and was a preliminary graphical artifact until the C9 gate completed at 10:09:47 UTC. This final hostile/residual verdict was issued only after reading that gate, which records no P0/P1 and explicitly limits the physical claims. The separate personnel and scope limitations in C9 remain intact; this figure review does not upgrade them.

The visual audit is tied to the four final image hashes in `FIGURE_NUMERIC_LAYOUT_AUDIT.json`. Its 44 checks cover provenance, finite-grid arithmetic, envelope/histogram selection, ppm decomposition, print size, visible-text boundaries, major/minor tick separation, font sizes and pre/post immutability of the originals. No native solve or Rust test was executed for this review.

To reproduce only the numeric/layout part, keep the plotting script and its recorded input tables together and run:

```sh
python3 verify_final_figures.py --unit /path/to/bass_reactive05_native_monitor_20261019 --out-dir /path/to/separate/figure_audit
```

The output directory must be outside the original unit. The script imports the original plotting code unchanged and redirects its output root and save callback to a separate audit directory; it reconstructs artist objects without overwriting or rerendering the final PNG/PDF files. Direct visual inspection remains a separate gate.

## 9. Verdict and reason

**Residual pass: PASS. Hostile audit: PASS.** The final figures have no remaining P0/P1 issue, the two repaired text issues are verified closed, and all quantities match their inputs and captions. The accepted result is a legible visualization of the finite crossed comparison and the stated frozen/native monitoring diagnostics. Full longspan convergence, universal second order, variable-opacity absolute error and two-way Einstein feedback remain outside the plotted evidence.
