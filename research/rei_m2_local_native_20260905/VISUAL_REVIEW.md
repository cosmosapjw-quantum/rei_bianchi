# Direct visual readback of REI M2 and M2A

Performed by the same Host Codex on 2026-09-05. The existing PNGs were opened
directly; the original SVGs were rendered in local headless Chromium and
visually inspected at widths 340 and 680 CSS pixels, representing 90 and
180 mm at 96 dpi. This is a screen-based reduced-size inspection, not a
physical printed-paper proof. No scientific source or figure was regenerated.

## Exact artifact binding

| PR | Artifact | Source commit | ZIP SHA-256 |
|---|---|---|---|
| REI #64 | [9952685032](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/33914615807/artifacts/9952685032) | `3f2f876b219d5c435cfd5d0dc70236a1edc1fd96` | `cc4c19e0564034bdb836833b5d3e53be2ea240f41c2085fedb0799f1b1472f3b` |
| REI #65 | [9959145017](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/33932820559/artifacts/9959145017) | `7d2fe29d46e3aab4a649c3679ae028e82ef0796c` | `607c8dc15a88b318aef29fc7fd45eb9de24ce03f12a5480d61d920bb30959157` |

Both ZIP hashes, EXECUTED_HEAD/TREE files and every SHA256SUMS entry were
checked. Plot-producing source from each nested source ZIP matches the exact
Git commit bytes. These are historical REI oracle artifacts, not artifacts
from the new BASS native execution. Detailed image/data identities are in
VISUAL_ARTIFACT_READBACK.json. The inspected Chromium comparison is preserved
as visual/svg-review-chromium.png.

## Figure and exact-data review

M2: the four legend entries map to the source's locked, old geometric sign,
3A mutation and matter-sign residual columns. All eight locked CSV residuals
are exact zero. Their markers are displayed at `1e-30` only; that number is
explicitly identified in the title and is not a measured residual. The 3A
mutation is invisible in the four class-A controls and visible in all four
class-B cases. The old-sign curve has its explicit A3 cancellation locus;
7/8 cases detect it. The matter-sign curve is nonzero in all eight cases.
The separator correctly distinguishes A1-A4 from B1-B4. Overlapping zero
markers at the display floor require the CSV/legend to disambiguate them.

M2A: the plotted incompatible norm agrees with the nine CSV samples, from
89 at delta=0.1 to 8999999999 at delta=1e-9; the compatible norm remains 1.
The log axis increases left-to-right, so growth toward the singular limit is
read right-to-left. Both legend entries, distinct markers/line styles, axis
labels and the explicit algebraic-not-evolution title are visible. Delta=0
is excluded, and the companion caption states the separate Qq=0 treatment.
No zero display floor is used in this norm plot. CSV residual/error columns,
including exact compatible-solution zeros, are not plotted as tiny norms.

## Readability disposition

| Figure | 180 mm screen proxy | 90 mm screen proxy |
|---|---|---|
| M2 momentum-sign | Axes, title and outside legend readable; no clipping in Chromium or original PNG. | Full layout survives, but legend/tick/axis text is too small for a confident publication-readability PASS. |
| M2A condition sweep | Both curves, legend and mathematical labels readable; no clipping. | Text is too small for a confident publication-readability PASS. |

The M2 SVG's native width is 203.2 mm, so ordinary 10-point labels scale to
about 8.86 points at 180 mm and 4.43 points at 90 mm. M2A is 180.34 mm wide;
its explicit 9-point legend scales to about 8.98 and 4.49 points respectively.
No new journal-specific threshold is imposed; the reduced-size judgment is
recorded rather than relabelled a universal visual PASS.

Status: direct PNG/SVG inspection completed, with a 90 mm readability limit.
Physical-print review was not performed. Historical artifact captions and
receipts are not rewritten. A future 90 mm publication layout can address
font/legend sizing separately; it does not block preserving native results.

## Renderer limitation preserved

The first ImageMagick internal-SVG previews returned exit 0 but omitted plot
curves and misrendered some text. Those previews were rejected as visual
evidence and retained outside the checkout for diagnosis. Chromium rendered
the same original SVGs correctly, matching the original PNGs. This is a local
renderer limitation, not a finding that the original SVG figures lack curves.
