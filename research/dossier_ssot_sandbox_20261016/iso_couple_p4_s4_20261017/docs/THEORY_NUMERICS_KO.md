# ISO-COUPLE P4/S4 | Bianchi-I photon photo-edge roots and exact-zero source-age retirement

2026-10-17 KST. Claim gate: **PASS_SCOPED_ROOTS_WITH_SOURCE_NATIVE_PHOTON_AND_GAS_TESTS**. Parent P4/S3 Draft PR #185 head `d239fc2e5e9402801f3cca2523425a9ddf2a1504`; original production Rust PR #150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` read-only. This is an off-shell prescribed background reference, not a cosmological Einstein/Thomson/full EoR result.

## Definitions, derivation and scope

Metric signature (-,+,+,+), proper time t in seconds, diagonal axisymmetric Bianchi-I:
\(a_\perp=a e^{-b},a_\parallel=a e^{2b}\), \(H=\dot a/a, s=\dot b\), \(H_\perp=H-s, H_\parallel=H+2s\). For one photon with birth energy \(E_b>0\) in eV, initial longitudinal direction cosine \(\mu_b\), and fixed Killing spatial momenta:

\[
 F(u):=\frac{E(t_b+u)^2}{E_b^2}=(1-\mu_b^2)e^{-2(H-s)u}+\mu_b^2 e^{-2(H+2s)u}, \quad u=t-t_b.
\]

With \(r_\perp=H-s\), \(r_\parallel=H+2s\):
\[
 F'(u)=-2[(1-\mu_b^2)r_\perp e^{-2r_\perp u}+\mu_b^2 r_\parallel e^{-2r_\parallel u}].
\]
When both weighted rates have the same sign, E(t) is monotonic. Opposite nonzero signs permit at most one stationary point
\[
 u_* =\frac{\ln[-\mu_b^2 r_\parallel/((1-\mu_b^2)r_\perp)]}{2(r_\parallel-r_\perp)}.
\]
Split a finite interval at \(t_b+u_*\) only if interior; each resulting piece is monotonic. Therefore the equation \(E(t)=E_\mathrm{thr}\) has at most **two isolated roots** per threshold inside a finite interval. A bisection on every strict sign-changing monotone bracket resolves roots to floating-point time resolution; endpoint/tangency contacts do not create spurious zero-length intervals. No claim of this result beyond constant axisymmetric directional Hubble rates.

The photo-**fit** thresholds from the **actual frozen Verner 1996 provider** are HI 13.60 eV, HeI 24.59 eV, HeII 54.42 eV. The D H-equality photo cross section has an additional explicit user-owned gate \(\chi_D=13.598434599702+0.0037=13.602134599702\) eV **for this manufactured isotope defect**. Do not equate these photo fit thresholds with the H/He binding-energy levels in `HHeModel::controlled_fixture()` and `DAtomicProvider`.

For each old/new age cohort, preserve exact original birth time and Killing ray, split opacity quadrature cells at these photo edges, compute \(\kappa_j(t)=c\,n_j(t)\sigma_j(E(t))\), then on each microcell use the positive exponential competitor partition
\[
N_{b}=N_a\exp[-\kappa_\Sigma(t_m)\Delta t],\quad
\Delta N_j=N_a[-\operatorname{expm1}(-\kappa_\Sigma\Delta t)]\frac{\kappa_j(t_m)}{\kappa_\Sigma(t_m)}.
\]
The native photo channel deposits \(\chi_j\Delta N_j\) into binding and \((E_m-\chi_j)\Delta N_j\) into heat, at the event sample energy, and P2 collisional/CX/FF/CMB gas owners are called separately with photo OFF. Number is conserved to the represented f64 accuracy; total-energy ledger includes prescribed geometric work. This is a **midpoint frozen-composition operator split**, not continuous gas feedback during every photon trajectory, full physical redshift history, or second-order entire solver.

## Actual bounded experiment and outcome

- Original P4/S3 restored `91/91` payload SHA-256, frozen native PR #150 module `12/12` SHA-256, Rust 1.94.1 offline. New `threshold_roots.rs` + `retarded_transport_threshold.rs`, seven new tests, 84 inherited tests. Changed source-only rustfmt and strict clippy PASS.
- Source-native FLRW/signed-prescribed BI parity when no thresholds crossed, real MD14+Verner+D source split and bounded H/He/D thermal event with genuine edge crossings; all photon/gas state commits transactional. Signed one-contracting-axis countercase has two HeI roots in one path, both found. No new Einstein backreaction.
- Manufactured independent Verner HI+D opacity, \(E_b=13.605\) eV, \(H=1.2\times10^{-16}\) s\(^{-1}\), duration \(5\times10^{12}\) s and proper neutral densities each 0.03 m\(^{-3}\). Original unsplit midpoint \(N=4\) optical-depth relative error **22.1807%**; threshold-root \(N=4\) **4.1254\(\times10^{-9}\)** against 131072-slab root reference. Independently reimplementing the same Verner HI formula in SciPy, explicitly split at analytic H/D crossing times, gives \(\tau=0.0274867212668695\), and Rust N128 root result differs by **6.73\(\times10^{-12}\)** relatively. This is numerical equivalence *within one provider model*, not independent atomic-data support.
- Cached geometry is reused for equal physical emission proper times, and original opacity coefficients are memoized by the *exact* f64 energy bit pattern within a frozen gas-stage (at most 8192 entries). This changes no energy or species ownership. Matched 3-run alternating-order N4/8/16 benchmarks show median original/P4S4 speed ratios **0.962/0.977/1.019**. Thus ordinary low-opacity general speedup is NOT established.
- Opt-in exact-zero age retirement: remove **only** cohorts whose remaining represented f64 number is literally 0 after full accepted step. This is lossless only relative to the represented f64 state: physical nonzero tails already underflowed; it is not a mathematically exact continuum compression. In 12-step high-opacity source-native benchmark cohort count 9216 → 2544 at step 12 (72.396% fewer), with identical surviving photon number, cumulative absorption and gas temperature. Last-step time in that single run was 0.01472 vs 0.01105 seconds, ~1.33×. No relative mass cutoff/phase-space coarse graining. Long-lived nonzero source ages still scale approximately O(N_time²) in the naïve overall implementation.

## Claim gate and remaining obligations

`P4/S4 = PASS_SCOPED_THRESHOLD_ROOTS_AND_EXACT_ZERO_COMPACTION` for these prescribed backgrounds; P4 full `PARTIAL`. `SA-01`, `SA-02`, `FLRW-CONV`, `BI-SIGNED`, `FULL_EOR` all **HOLD**. This neither certifies external 0.5%-level spectral/native gates nor a full BASS self-consistent Einstein history. Time, age, angle, spectral and chemistry-feedback error axes remain separate. No extrapolation beyond source z 4..20 or energy 13.6..100 eV; test characteristic energy may redshift below the *birth support* and is handled by the original cross-section threshold guard, not new photon births outside source support.

Next P4/S5: physically meaningful nonzero-cohort compression with an **a priori observable-error budget and independent future-time bound**, or a more efficient owner-faithful transport update; incorporate frozen BASS on-shell history and matched-source 4-axis convergence before any native science admission. Avoid an unbounded N64 repeated timeout while the age O(N²) issue is open.

## Primary references

- Verner, Ferland, Korista, Yakovlev, *Atomic Data for Astrophysics II*, ApJ 465 (1996), 487. DOI: https://doi.org/10.1086/177435. Original fitted parameter archive: https://www.pa.uky.edu/~verner/photo.html.
- Mellema, Iliev, Alvarez, Shapiro, *C²-Ray: a new method for photon-conserving transport of ionizing radiation*, New Astronomy 11 (2006). DOI https://doi.org/10.1016/j.newast.2005.09.004.
- J. Mackey, *Accuracy and efficiency of raytracing photoionisation algorithms*, A&A 539 (2012) A147, https://www.aanda.org/articles/aa/full_html/2012/03/aa17984-11/aa17984-11.html. Supports keeping temporal and multifrequency errors distinct, not a direct verification of our code.
