# BASS_HE HE18 C6: 네 번째 warm P01 source 셀 구현·성능 연구

**2026-10-15 KST.** BASS_HE parent commit `9a4a554bfffd5aea81dbf0ea018f092f55e3efa9`. Selected C5 implementation, C6 affected tests, C8 measurement. This project worktree is separate from rei_bianchi's owner processes. No local Codex session was invoked.

## 1. 물리·수치 계약

계량 (-,+,+,+), photon `p^a=(E/c)(u^a+e^a)`, `E=ℏω`. LRS shear `σ_ab=s(3z_a z_b-h_ab)`, `h_ab=g_ab+u_a u_b`, `σ_ab e^a e^b=s(3μ²-1)`. Optical energy ratio from the original epoch:

```
E(t)/E0 = sqrt(exp(2b)(1-mu0^2)+exp(-4b)mu0^2) / a(t)
b(t)=int_0^t s(t')dt', a(t)=V(t)^(1/3)
d(ln E)/dt = -H(t)-s(t)*(3mu(t)^2-1)
mu(t)^2=exp(-4b)mu0^2/(exp(2b)(1-mu0^2)+exp(-4b)mu0^2).
```

This is the preserved original non-tilted LRS Bianchi-I source, NOT a switched cold AXBI chemistry recipe. The actual HM12 forcing, fitted Verner cutoffs, Case-A RR/DR gas and photon positivity come from the pinned parent. CGS units used in source; final certified column in m^-2 and optical depth dimensionless. Proper t fourth cell [1.875e10,2.5e10] s.

## 2. Code changes and measured benefits

- `stage_fourth.py`: source and previous 3-cell payload sha validation; freeze third→fourth saved Hermite endpoints by only two actual old-source RHS calls, no source IVP; global shear start remains epoch0.
- `optimize_sparse.py`: cache reused 4-gas factors and skip only verified exact-zero opacity Jets. There is **no** float64 cutoff-based omission. All 2904 photon source/residual terms remain.
- `run_parallel.py`: 2 independent mid/whole processes with OMP/BLAS thread caps=1, no nested overthreading, stable per-task output, fail-on-existing evidence.
- `vectorized_preview.py`: actual NumPy vectorized 2904 photon-energy screening (non-certified, diagnostic only). It agrees with whole-cell interval containment and predicts the same 784 transparent nodes.
- `propagate_fourth.py`, `verify_fourth.py`: full 2904 outgoing exact rational error vector, four gas errors, positive comparison inverse, dyadic endpoint and global gas cube verification.

Matched workstation: Ubuntu 24.04, local Ryzen9 5900X, Python3.12, NumPy/mpmath.iv, original C6 input frozen once. Performance measurement, seconds:

| Component | Unmodified | Sparse | Ratio original/sparse |
|---|---:|---:|---:|
| Midpoint interval evaluation | 15.00 | 13.59 | 1.10375 |
| Whole-cell interval evaluation | 14.87 | 13.46 | 1.10475 |
| Comparison assembly | 9.48 | 10.07 | 0.9414 (slower) |

Two independent sparse evaluations launched through public `run_parallel.py` finished in **13.2025 seconds of wall time** and returned exit0 for both domains. Their scientific JSON outputs were **byte-semantic identical to the earlier optimized run after removing elapsed-time metadata**. This is a measured concurrent run, not an estimate of production throughput.

Matched-accuracy check: 23,312 coefficient interval comparisons had zero disjoint pairs; the 2904 node energy, cross-section and source records were identical; both cases retain nonnegative source and gain<1. Thus performance numbers are NOT obtained by relaxing source bounds. Comparison/enclosures do not constitute a formal independent proof of the mpmath.iv backend.

## 3. Actual fourth-cell science

- Fourth cell source-scoped optical depth: `[see machine-readable outward interval in results/PUBLIC_SUMMARY.json]`.
- First four cell cumulative tau: `[3.19996574611042619899371894559593372103484809e-8,3.19996574611042717933993836134532558990845243e-8]`.
- Four-cell first-scattering probability: `[3.19996569491152286370922698385007279813327223e-8,3.19996569491152384405541502885677996150448831e-8]`.
- Fourth column radius <33235.467 m^-2, positive comparison gain 0.00230508703765<1, global tube use <1; 2904/2904 outgoing errors and 784 transparent photon source nodes.
- Formal selected claim: **SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES**. Independent interval primitive verification, native binary64 roundoff, 16-cell/global EoR, source atomic-model uncertainty, observer foreground, independent scientific reviewer are NOT_RUN.

Actual tests: original and optimized 2904-node whole/mid sweeps, optimized assembly, exact-rational photon propagation, 11 scientific verification checks; five public synthetic Python unit tests; 8 actual Wolfram/xTensor checks (9 zero tensor residuals). No native Codex, no native production rei_bianchi mutation. No native subagent capability exposed: NOT_RUN (serial research orchestration, scientific subprocess parallelism only).

## 4. Cross-repo and literature use

REI PR117 continues independent AXBI abundance-history goal. WU088_HH PR74 provides a separate exact rational-log screened-cusp efficiency study, not transferable as an HH atomic rate. bass_cr source has a different temperature, electron model and donor bounds; no cross-regime rate transplantation. We did reuse the shared mathematical strategy of certified fast paths, byte identity, physically selective bound preservation and measured concurrency.

Original numerical-method backdrop: Neher, Jackson & Nedialkov (2007), *On Taylor Model Based Integration of ODEs*, SIAM J Numer Anal, DOI 10.1137/050638448. Actual interval arithmetic and exact source are from the pinned user project, not claimed independently guaranteed by that paper.

## 5. Next

Remaining 12 cells require new saved source reference and incoming full 4+2904 component radii; original-time shear and source knot thresholds for each. Cell5 proper time [2.5e10,3.125e10] s. Apply source-scoped validation and targeted interval primitive audit before global/admitted use. In rei_bianchi, the BBN-style ionization history remains the main nonblocking goal; do not place these optional optical validations on its critical path.

See README_KO.md for reproducible commands and next-action JSON for required pins and unfinished obligations.
