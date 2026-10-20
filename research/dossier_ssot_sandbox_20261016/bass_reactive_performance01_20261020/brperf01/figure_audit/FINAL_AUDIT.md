# Figure hostile audit and residual error pass

**Final verdict: PASS for the scoped figures and captions at 180 mm and 90 mm.**
Existing evidence supports all displayed values. No final text crosses the
canvas, the inspected 90 mm previews remain readable, and the captions prevent
kernel speed, sampled rate error, finite-grid differences and ledger residuals
from being promoted into broader physical claims.

This is a file-only figure review under the supplied `Figure Hostile Audit` and
`Figure Residual Error Pass` instructions. No web lookup, Rust run, new physical
simulation, new benchmark, or scientific test suite occurred in this figure
unit. `render.py` re-derives display statistics from retained CSVs and compares
them with retained summaries. It does not create new timing or trajectory data.
The figure agent also authored the photon receiver; this audit does not claim
new independent authorship of that receiver. Its independent calculation scope
is the retained-data display statistics and source-scope review, supplemented
by the already retained separate photon reviewer evidence.

## Intent and caption consistency

Figure 1 compares alternatives within three explicitly separate workloads. The
visible original/candidate ratios are paired statistics with observed ranges.
Figure 2 exposes the compact table's error–storage tradeoff and the legacy
table's smaller sampled error. Figure 3 separates direct time-grid diagnostics,
same-grid table differences and ledger consistency in a fixed-volume HOT gas
control. `../figures/CAPTIONS.md` is the standalone final caption set. Panel
labels, units, curve identities and normalizations were checked against it.

## Ranked audit ledger and repair disposition

| Priority | Issue or risk | Disposition |
|---|---|---|
| P0 | Different measured workloads could imply one overall solver acceleration | Three panels; explicit no-combined-speedup text; caption disallows multiplying ratios |
| P0 | Native timing has superseded or stale-launch directories | Only `native_rhs_abba_final` used; exact final binary SHA asserted |
| P0 | Rate candidates have different approximation errors | Asterisk in Figure 1; finite-probe error and legacy advantage in Figure 2; caption says no matched-error-bound comparison |
| P0 | Nt=192 could be treated as an exact reference | Figure 3 endpoint axis names Nt=192; caption explicitly calls it finite, with only a formal three-grid diagnostic |
| P0 | Ledger residual could masquerade as trajectory accuracy | Separate panel and denominator legend; footer and caption separate the checks |
| P1 | First Figure 3 right panel titles crossed the canvas | Shortened to “Endpoint shift” and “Compact ledger”; final outside-text count 0 |
| P1 | Headers, legends or footers nearly touched | Increased margins and separated header/legend/panel positions; inspected full and half width |
| P1 | Sampled-target annotation crossed compact error line | Moved into blank right-side space; no values changed |
| P1 | Figure 3 subtitle could imply direct panels used compact rates | Reduced subtitle to “Fixed volume · photon source off”; direct and compact panels name their own paths |
| P1 | Observed ranges could be read as confidence intervals | Explicit on-figure footer and full statistical-unit definitions in caption |
| P1 | SSE2/no-AVX “environment” wording misstates host evidence | Separate issue record distinguishes advertised host capabilities from compile-time configuration; frozen report unmodified |
| P2 | Long scientific explanations would crowd panels | Denominators, sample sets, workload identities and inference limits moved to standalone captions |
| P3 | Ledger legend markers did not share plotted hollow fill | Legend marker faces made white to match plotted ledger markers |
| P3 | Half-width preview had 150 dpi metadata despite a 90 mm print intention | Export now renders half the pixels and stores 300 dpi metadata; measured width ≈89.916 mm |

The first pass was **REVISE** for bounded P1/P2 issues. The initial clipping
record remains in `LAYOUT_INITIAL.json`; `FIRST_PASS_FINDINGS.md` records the
repairs before edits. No P0 data or panel-meaning error requiring a redesign
was found. Source files were not modified during these repairs.

## Bounded hostile verification: seven questions

| Question | Answer from retained evidence and the rendered figure |
|---|---|
| Are all timing spans the same statistic? | No. Figure 1(a) has six block ratios, (b) five process medians of six pair ratios, and (c) seven single-process pair ratios. Titles and caption distinguish them; none is a confidence interval. |
| Could the candidate speedups be multiplied? | No. Kernel, instantaneous RHS and frozen photon path costs overlap or omit different work. The subtitle and caption state that no combined end-to-end result was measured. |
| Does the smaller compact table improve rate accuracy over legacy? | No. Compact 8,193 has sampled maximum 1.30016634×10⁻⁵; legacy's union-of-probes maximum is 3.83448339×10⁻⁷. The lower legacy error is printed next to its distinct diamond. |
| Does the last HOT grid difference estimate an absolute physical error? | No. It compares finite discrete direct histories. Formal p=2.01425 is restricted to these three endpoints; Nt=192 is not an exact oracle. |
| Are the µK differences an all-time error bound? | No. They are compact-minus-direct differences at stored times on identical Nt, in the single HOT control. The caption distinguishes their 2.24831×10⁻⁶ K trajectory maximum from final relative differences. |
| Do 10⁻¹⁵ ledger residuals establish a converged radiation–gas solution? | No. The HOT source is off and volume fixed. The ledger panel reconstructs separate bookkeeping residuals; source-on BASS radiation, geometry work and longspan admission are outside its scope. |
| Does compiled_avx=false mean the host lacks AVX? | No. Archived host flags advertise AVX/AVX512. The separate issue record limits the flag statement to this build, and no extra SIMD gain is claimed. |

The provisional verdict “repair layout, retain scientific structure” survives
these checks. Keeping separate workload panels and independent HOT diagnostic
panels is safer than splitting each into unrelated figures, because the visible
scope distinctions remain adjacent. A common legend and shorter annotations
were adopted; deeper derivations remain in captions rather than inside plots.

## Residual scan and print-size risks

The three final full-width PNGs and all three 90 mm previews were visually
inspected. `LAYOUT_CHECKS.json` reports zero text boxes outside the canvas for
each final figure. The PDFs have exactly 180 mm page width; PNG pixel rounding
gives ≈179.917 mm at 300 dpi. Half-width previews are ≈89.916 mm at 300 dpi.

Standard text is at least 14 pt at 180 mm, becoming 7 pt at 90 mm. Math
subscripts/superscripts scale below the surrounding 7 pt text in the usual way;
the most vulnerable elements are Figure 3's denominator subscripts and the
Figure 1 range caps. They remained distinguishable in the raster preview, but
no physical printer proof or further reduction below 90 mm is claimed. Data
line widths are normally 1.6–1.8 pt at 180 mm, or 0.8–0.9 pt at 90 mm. The
weaker grid lines are auxiliary; data interpretation does not depend on them.

Color is not the sole key: performance alternatives have explicit row labels,
compact/legacy points have different marker shapes, HOT curves have distinct
line styles, and ledger quantities have different markers and line styles.
The main HOT temperature curves still overlap at their broad plotting scale by
design. Panels (b) and (c), not that overlap, carry the difference information.

## Final residual CoVe: four questions

| Question | Final answer |
|---|---|
| What becomes hardest to read first at 90 mm? | Math subscripts and error-bar caps. Full-size fonts, short titles and vector PDFs preserve them at the audited size; further shrinkage needs a new review. |
| Is any clipping or text collision left? | No final canvas-bound violation was detected, and visual inspection found no remaining label/title/legend collision. Tight but separated annotations in Figure 2 remain readable. |
| What is the most likely semantic misreading? | Treating ranges as confidence intervals or small HOT ledger residuals as accuracy. On-figure text and explicit caption definitions address both; publication must retain the captions. |
| Would deleting another annotation make the figure safer? | Removing detailed methods from the panels was useful. The remaining “legacy lower sampled error,” sampled target, finite-grid formal p and no-combined/no-extra-SIMD notes carry necessary scope, so further deletion would weaken interpretation. |

## Final micro-repair plan and deletions

All identified bounded micro-repairs are complete. Long right-hand titles were
shortened; header/legend/footer spacing increased; one target annotation moved;
one ambiguous subtitle qualifier was removed; ledger marker fill and preview
DPI metadata were made consistent. No new plot type, extrapolation, fit or
physical conclusion was introduced. No remaining annotation deletion is
recommended while keeping each standalone figure's scope legible.

**PASS reason:** the final panels are readable at both audited widths, every
display value is pinned to retained evidence, and inference limits remain
explicit. The SIMD report wording issue is recorded for the root publication
text, without altering the frozen implementation/report archive.
