# RUN17 first-birth gas-path figure

The publication figures are the PNG/SVG files in `final/`. The `180mm` pair
is arranged in two columns; the `90mm` pair stacks the same two panels for
single-column publication. They show the same 17 saved evaluations. Earlier
images at this directory's top level are retained as the initial rendering
record; use `final/` in the report.

## Caption

**First-birth finite-packet gas-path differences, P minus R.** P is the
invariant five-coordinate PCHIP reconstruction of the original RUN13 saved
gas knots, with the original H/D/He totals imposed by the affine lift. R is
the saved RUN17 native coupled control B dense polynomial. Panel (a) plots
`1e6 * (HI_P/HI_R - 1)`, so the ppm denominator is R at each displayed
sample. Panel (b) plots `T_P - T_R` in kelvin. The horizontal coordinate is
`u=(z-z_left)/(z_right-z_left)`, where code-z is
`(X-0.7)/(0.7004-0.7)`, an integration coordinate, and
`[z_left,z_right]=[0.004989333151072248,0.02371416180174271]`.
The endpoints are outgoing at the first birth and incoming at the second
birth. Markers are the 17 actual stored evaluations; straight segments are
visual guides. The original finite M2 packet and all 48 spectral cells are
retained. These are signed differences between two defined local gas paths,
not a rigorous error bound or a full-history sub-H survivor result.

## Numerical endpoint contribution table

These GL10 signed-balance values are read from the existing residual JSON;
no additional quadrature is performed to construct the figure. In this
table every contribution uses the same **endpoint** R HI denominator
`0.899996948987685` per initial H. This differs slightly from the denominator
used for the first plotted point. The conversion is
`delta_HI = -H_total * delta_q_HII`.

| Contribution to endpoint HI difference | ppm of endpoint R HI |
|---|---:|
| Initial difference | -1.571283115277787 |
| Integrated native gas forcing difference | +0.0013680964217793754 |
| Integrated photo forcing difference | +0.000001173988091997569 |
| Integrated P residual | -2.230804957817659 |
| Integrated minus-R residual | -0.000000000002214147070276652 |

The direct endpoint difference plotted in panel (a) is
`-3.800718802625755 ppm`; panel (b)'s endpoint is
`+0.12465231681380828 K`. Tiny terms are supplied numerically rather than
shown as visually indistinguishable near-zero bars. Floating-point balance
closure is preserved in `final/PLOTTED_VALUES_AND_PROVENANCE.json`; it is
not promoted to a quadrature or spectral error bound.

## Rendering and provenance

`render_first_birth_figures.py` reads only the frozen residual and native
control JSON files. It verifies the control-B/result link, the invariant
normalization input hash, the common interval and the actual 17-sample
count. It writes the plotted values, original packet identity, all input
SHA-256 hashes, exact command arguments, plotting environment and output
hashes. The exact final command is recorded in that JSON and in the final
standard-output log.

```bash
python -B render_first_birth_figures.py \
  --residual-result /absolute/residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json \
  --control-a /absolute/native/control_A_execution01/FIRST_BIRTH_CONTROL.json \
  --control-b /absolute/native/control_B_execution01/FIRST_BIRTH_CONTROL.json \
  --output-dir /absolute/new_figure_output
```

No native call, IVP, quadrature, or scientific test was run by this figure
unit. Matplotlib PNGs use 300 dpi; SVG text remains editable vector text.
`render_cache/` directories contain only Matplotlib runtime cache and are
excluded from the delivery manifest.

## Scoped figure check

The user-provided figure presets 07 and 08 were read for semantic alignment,
print-size legibility, clipping, panel spacing and bounded repair. One
visual inspection examined both initial layouts. The 180 mm image had no
observed collision. The 90 mm image had a concrete overlap between the
lower x-axis title and the first footer line. Its bottom plot margin was
increased from 0.14 to 0.20 of figure height, leaving scientific values and
units unchanged. Actual rendered text bounding boxes now pass the targeted
x-title/footer nonoverlap gate for both layouts. No second visual inspection
or broader review cycle is claimed. The final 180 mm PNG/SVG are byte-identical
to the already inspected initial pair; the 90 mm pair contains only that
spacing change. Initial source bytes and rendering outputs remain preserved.

The 180 mm version should be used at its intended two-column width; shrinking
it to 90 mm would halve the type size. The dedicated 90 mm stacked figure
keeps its core labels at 8.5–9 points. The smallest retained footer text is
8 points. The caption supplies the exact coordinate and normalization
definitions without crowding the figure.
