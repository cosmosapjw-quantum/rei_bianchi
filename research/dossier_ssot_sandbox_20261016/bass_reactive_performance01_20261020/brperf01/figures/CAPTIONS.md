# BRPERF01 figure captions and scope

These figures use retained BRPERF01 measurements. `SOURCE_INDEX.json` identifies
the 24 CSV/JSON inputs by byte count and SHA-256; `PLOT_DATA.json` contains every
plotted value and every constituent timing ratio. `render.py` regenerates the
figures without running the physical model, Rust tests, or benchmarks. English
labels keep the standalone vector figures portable; the captions below define
their scientific and statistical scope.

## Figure 1 — Measured performance by workload

Wall-time ratios of the original implementation to each candidate are shown
within three separate workloads. A ratio above one means the candidate took
less wall time in that comparison. Markers show medians, and horizontal spans
show the observed minimum and maximum of the statistical units named in each
panel. The spans are not confidence intervals. Panel axes have different limits;
their visual lengths should not be compared across panels.

**(a)** One query evaluates the same 15 original temperature-only coefficients.
Each of six ABBA blocks contains two direct and two candidate windows of 100,000
queries. Each block contributes the ratio of its mean direct time to its mean
candidate time. The scalar 8,193-node median is 4.9166 with range 4.0635–5.2893.
The legacy 65,537-node median is 1.5131, and the optional SIMD implementation is
4.4201 with a wider 2.4396–6.8472 range. All candidates use the same temperature
inputs, but the table approximations have different errors, quantified in
Figure 2. This is not a comparison at a common matched coefficient-error bound.

**(b)** The native gas RHS benchmark uses 64 identical fixture states and 32,768
evaluations per window. Each of five sequential, separate processes contributes
the median of six ABBA/BAAB pair ratios; the displayed marker is the median of
these five process medians, and the span is their range. Direct coefficient
reuse retains bitwise direct parity and gives 1.4115 [1.3972, 1.4969]. The legacy,
compact scalar and compact SIMD table medians are respectively 2.1761, 2.9182
and 2.8847. This instantaneous collision/CMB RHS benchmark sets `use_cx=false`;
it does not time adaptive CX half-flows. Fifteen A/A control ratios had median
1.0467 and range 0.8338–1.1534, so the small scalar/SIMD difference is not an
established incremental SIMD gain. Only the final benchmark binary
`957eb548de494c4f99eb6166846a338426d895f476e33297c2551599f5b81d81`
is used here.

**(c)** Each signed BASS frozen-ray fixture retains 384 source labels, 3,648
birth records and 1,824 paths after the already admitted exact reflection
symmetry reduction. Both baseline and candidates use identical quadrature and
path controls: birth refinement 1, two path slabs, opacity degree 2 and event
energy degree 4. A persistent two-worker pool gives medians 1.8047 [1.7089,
1.9163] for negative shear and 1.7751 [1.5249, 1.9610] for positive shear. Each
case uses seven paired ratios in one process; these are exploratory paired
observations, not an independent-process confirmatory result. Complete path and
ordered ledger byte parity is retained. Cached serial medians, 1.0185 and
0.9858, do not establish a wall-time gain.

The three panels represent separate measured workloads. Their ratios cannot be
multiplied into an end-to-end radiation–gas acceleration. The frozen-ray result
does not time evolving gas, and the native RHS result does not time photons or
background dynamics. No extra SIMD speedup is admitted by this figure.

## Figure 2 — Coefficient accuracy and table storage

**(a)** Maximum sampled relative error, `abs(k_table / k_direct − 1)`, across 15
original coefficient channels is plotted against the number of temperature
nodes on the 1–10⁶ K domain. When the direct coefficient is zero, an exactly
zero table coefficient contributes zero error; a nonzero value would contribute
infinite error. The compact coefficient-space PCHIP points use 1,025, 2,049,
4,097 and 8,193 nodes. Each resolution has its own probe set consisting of
20,001 offset log-uniform temperatures plus three interior probes in every
cell: 23,073, 26,145, 32,289 and 44,577 temperatures respectively. These probe
sets differ and do not supply a continuous-domain error supremum.

The corresponding compact maxima are 7.70451×10⁻³, 8.97608×10⁻⁴,
1.06664×10⁻⁴ and 1.30017×10⁻⁵. Thus only the tested 8,193-node compact choice
passes the displayed 10⁻⁴ sampled target. The 65,537-node legacy log-linear
diamond uses its maximum over the union of the four recorded probe sets,
3.83448×10⁻⁷. On the 8,193-node probe set alone the legacy maximum is
3.83110×10⁻⁷. The legacy table is more accurate over these coefficient probes.
The line connecting compact points is a visual guide; no continuous error law
or global bound is inferred from it.

**(b)** Reported table storage is shown using MiB = 2²⁰ bytes. Compact 8,193 uses
4,259,840 bytes (4.0625 MiB), compared with legacy 9,109,624 bytes (8.6876 MiB),
a 53.2380% reduction under the same storage accounting API. These numbers are
table storage, not whole-process peak RSS, allocator capacity or runtime
working memory. This figure quantifies a tradeoff: the selected compact table
uses less storage while accepting more sampled coefficient error than legacy.
It does not claim that all accuracy and performance measures improve together.

## Figure 3 — Hot native H/He/D control

This bounded gas control has fixed volume, no initial photons, photon source
OFF, and photo reactions OFF. Original H/He/D CI, RR, CE, DR, free-free and CMB
thermochemistry, with the existing adaptive CX half-flows, evolve from 60,000 K
for 2×10¹¹ s. Initial densities in m⁻³ are HI=1,000, HII=900, DI=25, DII=5,
HeI=300, HeII=100 and HeIII=60; all six remaining spectator populations are
zero. The regression CMB bath is 20 K and the existing manufactured D defect
is 0.0037 eV. These are control inputs, not a physical full-EoR initialization.

**(a)** Direct-coefficient temperature histories at Nt=48, 96 and 192 nearly
coincide on the displayed 10³ K scale. This visual overlap is not a numerical
accuracy estimate. **(b)** Direct final-temperature shifts relative to the
finite Nt=192 endpoint make the grid dependence visible. The direct endpoints
are 42,302.3693886748, 42,301.7882130068 and 42,301.6443469075 K. Consecutive
differences are 0.5811756681 and 0.1438660993 K, giving the formal three-grid
diagnostic p = log₂|Δ48,96 / Δ96,192| = 2.01425. Nt=192 is a finite reference,
not the exact solution; this diagnostic does not prove universal second order.

**(c)** Compact scalar 8,193-node minus original direct temperature is computed
at each identical output time and identical Nt, and displayed in µK. The
largest absolute difference anywhere along these three histories is
2.24831×10⁻⁶ K. This trajectory maximum is distinct from the largest final
relative temperature difference, 2.22948×10⁻¹¹. The µK structure is a difference
between numerical representations on these fixed grids; it is not a measured
physical fluctuation or an absolute error against a continuum oracle.

**(d)** The compact histories' total, thermal and chemical ledger residuals
are independently reconstructed from retained states and cumulative budgets.
With U thermal energy, B positive chemical binding energy, R escaped radiation
and C the CMB reservoir, E=U+B+R+C. The three quantities are the history maxima
of |E−E₀|/|E₀|, |U−U₀−Qthermal|/|U₀| and |B−B₀−Qchemical|/|B₀|. Binding is
reconstructed from the original H/He/D species densities and binding energies;
the denominators differ as explicitly shown in the legend. Their maxima across
these three HOT compact histories are respectively 1.26338×10⁻¹⁵,
1.89644×10⁻¹⁵ and 6.54723×10⁻¹⁶. The chemical maximum here is a HOT-subset
quantity, not the maximum across every retained case and backend. Small ledger
residuals test bookkeeping consistency and do not imply small time-integration
or coefficient-interpolation error.

The figure does not test dynamic geometry work, photon number conservation,
source-on radiation–gas feedback or full EoR. The retained BASS photon controls
are a separate evidence set. `LONGSPAN_SOLUTION` remains not admitted.
