# BR05 final figure captions

These captions accompany the final 182 mm and 90 mm versions. Each pair uses the same data with a separately constructed layout. The accompanying `FIGURE_PROVENANCE.json` pins the plotting script and input CSVs.

## BR05_TIME_BIRTH_RECTANGLE

**Finite time–birth refinement comparison.** Six final native H/He/D states at \(T=8\times10^{12}\,\mathrm{s}\) are compared for \(N_t\in\{16,32\}\) and fitted birth refinement \(r\in\{2,4,8\}\). The control is the same one-way BASS `SIGNED_MINUS` background, source grid 121 and opacity GL4; BR05 adds the \((16,8)\) history and reuses the other five recorded histories. Panels (a)–(c) show reference-comoving surviving photon number, survivor-weighted mean age and the energy-weighted quadrupole \(q_2\), respectively. Lines connect the discrete sampled refinements; the horizontal refinement axis is logarithmic in base 2. The offsets written on the vertical axes are numerical baselines used to display small changes, not exact solutions or zero-error references. Panel (d) shows the ratio of two finite mixed differences,

\[
D_{tr}^{r\to2r}(f)
=f(32,2r)-f(16,2r)-f(32,r)+f(16,r),
\qquad
\frac{|D_{tr}^{4\to8}(f)|}{|D_{tr}^{2\to4}(f)|},
\]

for photon number, mean age, second age moment and \(q_2\). The differences are evaluated in Decimal96 from the recorded final values. The bars quantify the reduction of this finite-grid interaction. They are not convergence orders, Richardson error estimates, or certificates for the unknown nonlinear solution. The near-horizontal photon-number curves do not establish joint time, age, spectral or angular convergence.

**Data:** `evidence/independent/pair/NATIVE_FINALS.csv` and `NATIVE_INTERACTION_COMPARISON.csv`.

## BR05_NATIVE_BIRTH_MONITOR

**Read-only birth monitoring in the completed \(N_t=16,r=8\) native history.** Panels (a) and (b) compare the actual fitted rule's target-age atoms with a constant-source, constant-opacity reference at each of 48 emitted photon energies. The reference opacity is the original corrector selector evaluated at emitted energy and its actual rate gas; it is not a later path-integrated opacity. The displayed curves and filled bands are minima and maxima over all 16 successful local fixed-step transactions, comprising 768 step/rule records. They are deterministic ranges, not statistical confidence intervals; the narrow ranges often appear as a single line. \(W_1\) is the distance between normalized survivor-age distributions in seconds, while the CDF supremum distance is dimensionless. Both compare the stated frozen reference only.

In panel (c), let \(N_0\) denote the exact constant-source frozen-reference newborn number, \(N_{sf}\) the actual birth weights attenuated with the frozen selector and represented clocks, and \(N_{nat}\) the newborn number retained by the actual local solver transaction. The blue and orange curves are

\[
10^6\frac{N_{sf}-N_0}{N_0},
\qquad
10^6\frac{N_{nat}-N_{sf}}{N_0},
\]

respectively. Their sum is the combined native shift relative to \(N_0\); they are separately normalized additive increments, not two competing estimates of one total error. Here “accepted” means a successful local fixed macrostep, not an instrumented outer four-corner adaptive acceptance decision.

Panel (d) is the actual final retained photon-number distribution over age, displayed in 32 logarithmically spaced bins. All 314,624 recorded final cohorts enter the display calculation, including 21,652 zero-weight records; bin heights are retained probability per bin and sum to unity within floating point summation tolerance. The histogram is a display reduction and does not merge or remove any solver cohort. Neither the frozen-reference distances nor the native histogram certify absolute variable-opacity, gas-coupled error or full longspan convergence.

**Data:** `evidence/independent/monitor/RULE_REFERENCE_COMPARISON.csv`, `NEWBORN_MEASURE_COMPARISON.csv`, `evidence/native/monitor_n16_r8/MONITOR_FINAL_COHORTS.csv`; the exact displayed reductions are `figures/MONITOR_ENVELOPE_DATA.csv` and `RETAINED_AGE_HISTOGRAM_DATA.csv`.
