# HE36 final event bridge and diagnostic review

## Decision and reviewer role

**PASS_SCOPED_BRIDGE_AND_DIAGNOSTIC. No blocking findings remain in the reviewed components.** The policy remains **workflow1.0.0 / approval0.2**. This is a review of the supplied-input event bridge, the finite-source record adapter, the local source-lift guard, and the saved CCC diagnostic and benchmark. It does not admit a physical reaction network or a closed reactive pressure model.

Reviewer: `/root/he_latest_synthesis`. The bridge, diagnostic, benchmark and plot were authored by other agents. This reviewer read their actual source and saved receipts and inspected the actual final PNG. The reviewer independently derived the earlier incoming-loss formulas relative to the parent's provisional equations and authored the earlier Cartesian oracle. Accordingly, this report is an independent review of the other agents' implementations and artifacts; it is **not** a fresh non-author review of this reviewer's own `DERIVATION.md`.

The previous `INDEPENDENT_REVIEW.json`, `CARTESIAN_LOSS_RESULT.json`, `KERNEL_REVIEW.md`, and `MOMENT_SOURCE_REVIEW.md` remain unchanged. Their completed controls were reused. This follow-up made no new model evaluations, IVPs, numerical test runs, benchmarks or renders. It read and hashed saved files and recomputed summary ratios from already saved timing numbers. `FINAL_DIAGNOSTIC_READBACK.json` and `FINAL_BRIDGE_READBACK.json` record these readbacks; `FINAL_BRIDGE_PLOT_REVIEW.json` pins this review's source and receipt hashes.

The final bridge README had two literal carriage returns in its tensor-definition line. The author corrected that line to plain `C_event [J/event]` and regenerated only the manifest. The previous README/manifest are preserved at `/tmp/he36_event_bridge_docfix/before/`. Executable sources and their successful test receipt did not change. The final README contains no carriage returns and all 13 final package payloads match its regenerated manifest.

## Event tensor and scalar ledger

The exact REI donor is preserved byte for byte at SHA256 `d0998261323609901f0cf9636d71282e7848bac6c00c1e5f7240ed7fc540e88a`, from `cosmosapjw-quantum/rei_bianchi` pin `9620e1fcc4bdda76e0311206f614234926600381`. Its execution contract gives the nine energy-ledger terms in **J/event**. With absolute abundances per baryon, its event row rate has units events/(baryon s). The bridge uses the actual donor row rather than replacing its stoichiometry or rate algebra.

The caller must supply the complete signed **net thermal central second moment per event**, including removed parents and all retained thermal products, in a declared common bulk frame. If that tensor is \(C_{\rm event}\), the bridge computes

\[
S=n_B r C_{\rm event},\qquad
Q=\tfrac12\operatorname{tr}S=n_Br\,dE_{\rm th},\qquad
J=S-\tfrac23 QI.
\]

Here `S` and `J` have units Pa/s, and `Q` has units W/m³. The input tensor has units J/event, not pressure per event. The code checks `tr(C_event)/2 == dEth` within its explicit floating point gate both before and after multiplication by the volumetric rate. `Q` and the donor's `dEth` reservoir are two views of **one energy owner** and must not be added. An incoming-loss tensor alone is not a net reaction tensor. The adapter does not infer recoil, daughter spectra, secondary electrons, photon transport or stopping.

The complete tensor, its provenance, frame and unit labels are mandatory, including at zero event rate. Missing product moments therefore remain unresolved when the instantaneous rate is zero. The code accepts an explicitly supplied isotropic tensor or zero-heat pure shear but does not silently insert either. A signed source tensor need not be positive semidefinite; it is not a covariance matrix.

The donor remains responsible for its scalar conservation and energy checks. Its event objects are caller-owned mutable objects, and the adapter's documented contract requires that they not be mutated after validated construction. The adapter returns an immutable snapshot of the row and immutable source arrays. This is a conditional scientific adapter, not a defense against a caller forging or mutating its input records.

### Thermal inventory finding: resolved

The charge census alone gives an electron count, not an arbitrary thermal-particle count. The final code therefore requires both explicit declarations:

- all retained nuclei and free electrons are thermal;
- the 21-state census is charge neutral and contains no positrons or negative ions.

Under these assumptions,

\[
R_{\rm part}=n_Br\,(1+q)\cdot\nu
=R_{\rm nucleus}+R_{\rm electron}.
\]

Thus nuclei and electrons both contribute. Nonzero `dEfast` is rejected as unresolved: fast-particle energy does not determine fast-particle number. Zero `dEfast` alone would not establish the inventory condition; the all-retained-thermal declaration is separately required. A future fast component needs its own number source and an explicit thermal-count correction. Positron or anion channels require a different census.

The saved three manufactured event checks include charge change with unchanged nucleus count, two nuclei becoming one, and a neutron-to-proton beta census. Their coefficients and all energy partitions are explicitly manufactured. They do not validate measured nuclear rates or daughter-energy distributions.

### Status and representability

Positive donor-rate underflow and nonzero reservoir underflow are rejected. Declared support zero, zero density and zero reactant retain their donor statuses. The implementation uses stable products and an overflow-safe half trace. The residual trace in a nearly isotropic STF projection is measured against the original source tensor, avoiding an artificial singular normalization by a vanishing STF remainder. No trace repair or physical-zero substitution is hidden in this path.

## Finite moments and source lift

The finite-source module is unchanged at SHA256 `644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`; the finite-mass pair module is unchanged at SHA256 `49104bb9244af92f707f83b489f217a0573566b2d9f3e5154366b7d35eaaab89`.

The finite adapter retains the original prepared/evaluation types, identity, selected temperature, source ID, numerical domain, finite energy interval and energy mapping. Positive alpha/beta/gamma underflow cannot become an all-zero physical channel. A genuinely zero tabulated integral remains a declared **finite-source** zero with no full-rate-zero claim. The value/log identity gate can conservatively reject a representable subnormal after exponential rounding; universal subnormal admission is not claimed. This is explicit rejection, not silent loss of support.

The actual CCC incident-electron table uses the heavy fixed-target convention with mass `m_e`. Its record can be used for radial diagnostics. It cannot enter `for_pair` or `binary_loss` as a finite-mass relative-energy kernel, even for a numerical mass combination whose reduced mass equals `m_e`. The finite-pair route requires the separately declared manufactured relative-energy mapping and matching reduced mass and temperature. Exposed raw values remain audit data; copying those values into an unrelated primitive would discard the adapter's source qualification and is not an admitted workflow.

The source-lift guard evaluates the supplied full and reduced sources once each at the proper states. It checks

\[
d=R_{\rm full}(Lz)-L R_{\rm reduced}(z),\qquad
|d_i|\leq a_i+r\max(|R_{{\rm full},i}|,|(LR_{\rm reduced})_i|).
\]

The fixed linear lift, absolute gates, relative gate and source units are explicit. The full lifted state must be strictly positive before either callback runs; no abundance floor is inserted. A failing check raises `SourceLiftDefect` carrying the complete residual report. The saved selective-source fixture conserves the sum of its first two source entries but fails the componentwise lift gate, as intended. This is a one-state compatibility diagnostic, not a global reduction theorem or an integration error bound. Moving or nonlinear lifts require additional derivatives and are outside its scope.

## Saved diagnostic and actual plot

All **22 diagnostic payload hashes and byte counts** match the saved component manifest. The CSV has **129 rows and 129 distinct temperatures**. The source has 87 CCC rows spanning **13.6058–968.61 eV**. Its cross sections are in a₀² and are converted without an extra π or multiplicity factor. The positive piecewise linear interpolant is integrated with GL16 on 86 intervals. The numerical temperature domain is 2000–200000 K and does not expand a physical chemical-provider admission range.

The inspected final PNG has SHA256 `d5bcd1ba86c5ee6d15bddd7399805a70757deb2595f7c7f0cbed60db2d15782e`. Its corresponding SVG has SHA256 `b903f81062d879a9f8c0e858264ab2f32f5cf41d14e970ebcbe35fabe6062e4a`. The actual image contains three legible panels: finite alpha, the incoming-loss ratio kappa2/alpha, and the reaction-weighted mean incident energy. The exact 20000 K marker, axis units, finite-source support and limiting assumptions are visible. No remaining label clipping, text/curve overlap or implied physical error bars were observed.

The unknown high-energy contribution is not assigned zero. There is no physical tail-error bound and no source interpolation-error certificate. Kappa2 is an **incoming-electron loss coefficient**, not a net CI pressure-relaxation frequency. The mean incident energy beta/alpha is not a complete CI cooling ledger. In particular, the large low-temperature kappa2/alpha value reflects selection of rare high-energy particles; it is not an independently calibrated gas closure. Application of a finite anisotropy would additionally require control in the reaction-weighted tail, beyond the instantaneous first variation reviewed here.

At 20000 K the saved partial alpha is `2.7441444073979985e-18 m^3/s`, kappa2/alpha is `27.317869001614586`, and the weighted mean incident energy is `17.268706522059013 eV`. All four saved moments are positive and finite, with no underflow/subnormal outputs in this diagnostic. The minimum sampled feasibility margin is `0.4471876400622907`. The signed `C_moment` reaches `-0.2148271123722738` at 200000 K and is retained without clipping; it is not itself a positive rate.

The original render's threshold annotation was moved in a display-only revision. Both attempts and their scripts/receipts are preserved. The truthful count is **two render invocations**, one final scientific PNG/SVG pair and two cache hits. This supersedes the initial contract's planned single render. The separate visual-inspection receipt completes the renderer receipt's intentionally pending visual-inspection field. This review did not rerender the figure.

## Benchmark scope and execution accounting

The saved benchmark compares one 129-temperature vector call with a loop of 129 scalar calls to the **same prepared GL16 kernel**. Both return and compare the full moment-evaluation payload. Scalar list assembly is timed; final concatenation for comparison, preparation, I/O, comparisons and rendering are excluded. One warmup per path precedes five alternating-order paired timings.

The raw saved timings reproduce a median paired ratio of **6.0269708317096145×** with range **1.72796077707076–10.880428618619684×**. The separate ratio of median times is **5.384407241847672×**; median vector and scalar times are 4.228976 ms and 22.770529 ms. These are different statistics and are correctly distinguished. Maximum full-payload relative difference is `2.8482781212955235e-14`, below the `3e-13` gate, and flags match exactly.

These measurements describe temperature batching on one shared host and process. The receipt retains all five pairs, their dispersion, Python/NumPy/OpenBLAS versions, CPU identity and thread/quota information. There is no confidence interval, cross-machine speed claim, IVP speedup or physical-accuracy gain.

The saved diagnostic counts reconcile: one prepared kernel, six vector calls and 774 scalar calls, **780 evaluate calls / 1548 temperature evaluations** including warmups and both timed paths. These are not 1548 independent physical simulations. The diagnostic body took 0.348766743 s; its outer process took 0.702625994 s. Render and import times are separate.

| Evidence reused in this follow-up | Saved result | New execution by this review |
|---|---|---:|
| Earlier independent Cartesian incoming-loss oracle | Six controls; max relative error 7.46229818803753e-14 at gate 2e-11 | 0 |
| Bridge author's new adapter checks | Seven groups pass; manufactured events, mapping/status guards and source-lift controls | 0 |
| Finite CCC diagnostic | One 129-temperature diagnostic | 0 |
| Same-kernel timing experiment | Five measured pairs, one warmup per path | 0 |
| Plot production | Two attempts, one final pair, two cache hits | 0 |
| Old HE32/donor IVPs or completed tests | Reused evidence only | 0 |

## Remaining scientific boundary

This review closes the previously unreviewed **component** event/source adapter and saved diagnostic/plot boundary. It leaves the physical product/birth moments, isotope-specific differential data, stopping, radiation/thermal evolution, calibrated gas closure, full reactive 19-channel network and metric feedback unresolved. The earlier HE32 gas condition `pi_b=0` and the separate nonbaryonic matter-stress interpretation remain unchanged. Parent integration, stage backups, publication and overall DAG accounting are owned by `/root`; this reviewer made no remote mutation or external publication.
