# HE36 finite-source CCC moment diagnostic

## Outcome and retained scope

One new bounded diagnostic evaluated 129 unique temperatures from 2000 to 200000 K, with the midpoint set exactly to 20000 K. It uses the frozen finite-source Maxwellian module and all 87 donor CCC rows, with positive piecewise-linear cross-section interpolation and GL16 on each of 86 source intervals. There were no new IVPs, no donor-suite replays and no new adaptive-quadrature or GL32 checks. The existing unchanged α–δ numerical-path witness remains the source of those quadrature checks.

This folder is a portable component for the parent HE36 unit, whose workflow remains workflow1.0.0 / approval0.2. It has not been published remotely by this agent. Root owns unit integration, stage backups, publication and the overall DAG.

The interval is 13.6058–968.61 eV in incident electron energy. The heavy fixed-target mapping uses μ=mₑ. Cross sections are supplied in a₀² and converted to m² without a π or multiplicity factor. The unknown high-energy contribution is not assigned zero and has no physical error bound. The table interpolation has no physical source-error certificate. The numerical temperature interval is not an extension of the donor's active chemical model admission range.

## Outputs and definitions

`outputs/ccc_moments.csv` and `.json` contain all 129 rows, with α, β, γ, δ, κ₁, κ₂, both normalized κ ratios, the reaction-weighted mean incident energy, the energy-selection ratio β/(θα), C_moment and the feasibility margin. All values are finite and all four moments are positive; no output underflow or subnormal occurred.

With θ=k_B T and moments α=⟨K⟩, β=⟨EK⟩, γ=⟨E²K⟩ of the finite-source kernel K=gσ(E), the derived diagnostic quantities are

\[
\kappa_1=\frac{2\beta}{3\theta},\qquad
\kappa_2=\frac{4\gamma}{15\theta^2},\qquad
C_{\rm moment}=1-\frac{2\kappa_1}{\alpha}+\frac{\kappa_2}{\alpha},
\]

\[
\mathcal F=\frac{\kappa_2}{\alpha}
 -\frac35\left(\frac{\kappa_1}{\alpha}\right)^2
 =\frac{4\operatorname{Var}_{\rm reaction}(E)}{15\theta^2}\geq0.
\]

κ₂ here denotes incoming-electron loss only. It does not supply the outgoing-secondary contribution, the net CI pressure relaxation frequency, finite-mass recoil, or a reactive STF closure. The incident mean energy β/α is not a common-pool net CI cooling loss. No closure is activated by these outputs.

| T [K] | α_partial [m³/s] | κ₂/α | Mean incident energy [eV] | Feasibility margin |
|---:|---:|---:|---:|---:|
| 2000 | 7.210750815982397e-50 | 1762.795137946184 | 14.010240989222781 | 0.5992872897929828 |
| 20000 | 2.7441444073979985e-18 | 27.317869001614586 | 17.268706522059013 | 0.5457602366645169 |
| 200000 | 1.056633326699312e-14 | 2.2946106262079176 | 45.362991834142 | 0.4471876400622907 |

The minimum sampled feasibility margin is 0.4471876400622907. C_moment reaches −0.2148271123722738 at 200000 K. That signed algebraic combination is retained without clipping; it is not itself a positive rate or a completed pressure-relaxation prediction.

## Same-kernel performance measurement

One five-pair timing experiment compared one vector-temperature `.evaluate` against a scalar-temperature loop calling the identical prepared `.evaluate`. Both paths use the same GL16 nodes, weights, cross section and four moment orders; δ supports the temperature derivative of γ. The complete evaluation payload is compared, including moments, logarithms, derivatives, slopes, means and flags. Scalar list construction is timed; concatenation for the parity check is excluded. Preparation, comparison, I/O and plotting are outside the timed sections.

One warmup per path preceded five alternating-order measured pairs. The maximum relative output difference was **2.8482781212955235e-14**, below the frozen **3e-13** gate; all flags matched exactly.

| Pair | Execution order | Vector [ms] | Scalar loop [ms] |
|---:|---|---:|---:|
| 1 | vector → scalar | 4.680058 | 50.921037 |
| 2 | scalar → vector | 12.333806 | 21.312333 |
| 3 | vector → scalar | 3.714566 | 19.355767 |
| 4 | scalar → vector | 4.228976 | 25.487915 |
| 5 | vector → scalar | 3.751415 | 22.770529 |

The median paired speedup is **6.0269708317096145×**, with individual pairs **1.72796077707076–10.880428618619684×**. The ratio of median times is **5.384407241847672×**: vector median 4.228976 ms, scalar median 22.770529 ms. The broad spread is retained. This is a same-kernel batching result on one shared host, not an ODE comparison or an improvement in physical accuracy.

Runtime: Python 3.12.14, NumPy 2.3.5, OpenBLAS 0.3.30 with one BLAS thread, Intel Xeon Platinum 8573C, nine CPUs visible/affine, cgroup quota eight CPUs, 8 GiB memory limit. `outputs/BENCHMARK.json` records the full actual environment, all raw nanosecond timings and dispersion. The whole diagnostic body, including the experiment and outputs, took 0.348766743 s; the observed outer process time was 0.702625994 s.

Evaluation counts are exact: one prepared kernel; six vector calls and 774 scalar calls, for **780 total evaluate calls / 1548 temperature evaluations**. The latter counts both paths, warmups and measured trials. They are not independent physical simulations.

## Plot and visual review

`plots/ccc_finite_moments.png` and `.svg` show α_partial, κ₂/α and the reaction-weighted mean energy. The finite support, heavy target assumption, incoming-loss interpretation and unknown tail/source error appear directly in the figure. No physical error bars are shown.

The actual final PNG was inspected with `view_image`; all panels, labels, units and captions are legible. The first render had a small threshold-annotation intersection with the mean-energy curve. It is preserved in `plots/attempts/render_001` with its original script and receipt. Only the annotation position was changed. The final render took 1.915329865 s internally and 3.279887178 s as an outer process. There was no numerical or timing rerun for this display change.

There were **two render invocations**, producing one final scientific PNG/SVG pair and one preserved prior attempt, plus **two cache-hit checks**. The final cache check returned `REUSED_COMPLETE_RENDER`, verified both output hashes and performed zero renders, moment evaluations or IVPs. This truthful count supersedes the initial contract's planned single render. `plots/RENDER_RECEIPT.json`, `plots/VISUAL_INSPECTION.json` and `receipts/PROCESS_TRANSPORT.json` keep these facts separate.

## Frozen identities

- Module SHA256: `644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`
- CCC source SHA256: `7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae`
- Diagnostic identity: `cfa2e14c6c53111593e744709df5ebff7a73ec676dd5e2a7bc8d3462b2c7e8b8`
- Final render identity: `b11262ce43a52a841ec5c8d5353cb477617b184b8b5954ee5c9c1877d1e5d3a6`
- Final PNG SHA256: `d5bcd1ba86c5ee6d15bddd7399805a70757deb2595f7c7f0cbed60db2d15782e`
- Final SVG SHA256: `b903f81062d879a9f8c0e858264ab2f32f5cf41d14e970ebcbe35fabe6062e4a`

## Reuse commands

The module and raw table are vendored unchanged with hashes, so copying the whole folder keeps relative imports and payload paths portable. Commands on complete outputs verify and reuse them; they do not repeat the diagnostic or render.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_diagnostic.py
MPLCONFIGDIR=/tmp/he36-mpl-cache OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python render_diagnostic.py
```

Changed identities intentionally refuse to replace a completed output. Preserve the old attempt and choose a new output folder or an explicit parent-controlled revision before any changed-dependency run. Existing independent module tests and old IVPs remain evidence to reuse, not work to repeat.

## Parent integration checklist

- Copy this component unchanged into the HE36 unit and verify `MANIFEST.json`.
- Reuse the independent moment checks from `/tmp/he36_moment_implementation`; the diagnostic parity is an implementation comparison, not an independent physical/quadrature validation.
- Link the parent derivation of κ₁/κ₂ and finite-mass/outgoing terms. No net reactive pressure term is furnished here.
- Aggregate the counts as one diagnostic, one benchmark experiment, five timing pairs, two render attempts, two render-cache hits, zero new IVPs.
- Publish the final figure and complete source/evidence through the parent unit's existing workflow, preserving the first render and all receipts.
