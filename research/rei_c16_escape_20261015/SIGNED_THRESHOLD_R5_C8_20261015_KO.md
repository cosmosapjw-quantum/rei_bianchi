# C16B → PR150: signed threshold, positive spectral reconstruction and reversible source-free split

2026-10-15 KST. 독립 bounded research lane. 원본 `rei_bianchi` PR149 science `4f55234dee39e538de929b119c865dfcdbb5c673`; PR149 v3 handoff commit `0190d06385c574078ea98f76d043766ce9ec1f03`. PR150 current observed HEAD `c578683d995d375dbfc824cb080cb6b576d19348`; PR152 independent toy threshold oracle `9cd36354e46b8a75e3cb70d87e78f9e3c3c2f0a7`. Existing production/parallel HPC source untouched.

## 1. Convention repair and exact interface

**Erratum:** prior `V3_HANDOFF_AND_THRESHOLD_KO.md` listed metric `a²[e^(+2b) dx_perp²+e^(-4b) dz²]` incompatible with its own photon characteristic `R²=(1-mu0²)e^(+2d)+mu0²e^(-4d)`. Correct convention (aligned to the original C13 and independent PR152):

```
ds²=-c²dt²+a²[e^(-2b)(dx²+dy²)+e^(4b)dz²],  s=db/dt
sigma^i_j=diag(-s,-s,2s),  Sigma=sqrt(3)*abs(s)/H
```

For `x=ln a`, signed `v=s/H`, `d=b-b_e`, emitted `q=a_e epsilon_e` and initial direction `mu_e`:
`R²=(1-mu_e²)e^(2d)+mu_e²e^(-4d)`, `epsilon=q R/a`, `mu²=mu_e² e^(-4d)/R²`.
The fixed physical threshold chi_j is at `q_th=a chi_j/R` and
`d ln q_th / dx=1-v(1-3mu²)`.
Endpoint transverse/polar velocities: `1-v`, `1+2v`.
Necessary and sufficient strict forward-cut motion for every ray: `-1/2<v<1`; outside this interval some ray may reverse, and signed v cannot be recovered from Sigma alone.

## 2. Positive parent two-moment representation

For a source-free emission cohort, take `q ∈ [lo,hi]` with positive photon number `N`, reference energy `Uq` and `m=(Uq/N-lo)/(hi-lo)∈[0,1]`. Use the *declared reconstruction closure*, not an inferred true spectral shape:
`p_t(y)=exp(t y)/Z(t)`, `Z(t)=(exp(t)-1)/t`, `y=(q-lo)/(hi-lo)`; `m(t)=1/(1-exp(-t))-1/t`. Invert m monotonically for signed t; exact endpoint means are delta atoms. Numerical evaluation uses expm1/symmetric formulas and moment series near zero.

For cut `r=(q_th-lo)/(hi-lo)` interior, the active number fraction is `F=(exp(t)-exp(t r))/(exp(t)-1)`. Its positive first moment uses the conditional tail mean `r+(1-r)m(t(1-r))`; passive uses `r*m(t r)`. The implemented algorithm computes **smaller child N and Uq directly from positive quadrature formula**, then larger child as parent minus smaller. This avoids tiny-child cancellation. The first Rust sweep exposed 7 negative passive energies in 4,000,000 inputs from the earlier majority-first branch, as small as ~`-2.84e-14` eV/H. Actual local reproducer logs retained. The single targeted numerical correction gives 0 failures on exactly the same 4 million deterministic indices, without loosening tolerances.

At any `q_th(x)`, `N_a+N_p=N`, `U_{q,a}+U_{q,p}=Uq`, `N_a,N_p,U_a,U_p≥0`. The continuous interface flux is
`dN_a/dx=-N p_t(r) dr/dx`, `dU_a/dx=q_th dN_a/dx`.
Since the immutable parent is retained, an arbitrary source-free forward/reverse threshold trajectory ends at the same partition as applying the final cut once. This is **not** a no-memory closure under changing opacity: chemical absorption modifies the underlying q-distribution and requires a new source-aware transaction.

Physical energy is `(R/a)Uq`; its change includes cosmological redshift and signed shear work. Pool transfer alone is not a photon sink nor a nonradiative heating source. H/He photo absorption, gas thermal source, recombination emission, Thomson and stellar Qmu are untouched.

## 3. Real execution and failure history

- Wolfram independent exact symbolic checks: face fraction derivative; first-energy closed form; `m(t)+m(-t)-1` all **0**.
- Python local research: **18/18 tests PASS** including high-precision mpmath 65d characteristic derivative, independent 55d quadrature, both shear signs, reversed flux, regression against first floating-point failures, delta endpoints and invalid domains. First initial finite-difference test failed 1/17 on O(h^2) numerical truncation, then reformulated with high-precision independent differentiation; original failure documented and not reclassified as a physics bug.
- Existing untouched PR149 C16B source suite **11/11 PASS**.
- Rust local deterministic independent sweep `4000000/4000000`, 12 threads: **0 failures**, `max |ΔN|/N=2.215e-16`, `max |ΔUq|/Uq=2.210e-16`, zero source-free same-cut round-trip discrepancy, tested `t∈[-30,30]`, `qlo>0`, finite positive widths and both outside/interior cutoff.
- **NCP status distinct:** actual 64 logical CPU, 125 GiB, Rust 1.99.0 verified with exact SSH key; prior pre-repair 24-thread 4-million-case sweep yielded 7 failures (retained). Corrected source bytes were uploaded to `/root/REI_C16B_SIGNED_THRESHOLD_20261015_001/signed_threshold_sweep.rs` with local SHA identified in source ledger. A **post-repair NCP recompile/run was blocked by host execution tool safety checks**, so NCP repaired PASS **NOT_RUN**, not promoted from local test.
- The simulated HeII ray experiment is **manufactured**, `a=.2, q∈[10,12] eV, N=1, Uq=11 eV/H`, and includes `d=±0.05`. At `d=+.05` transverse active fraction `0.823409471867115`, polar `0`; at `d=-.05` transverse `0.2789826935216766`, polar `1`. Demonstrates angularly asymmetric cutoff crossing, **not** a physical Case-A spectrum or an inferred ionization history.
- Profiling is per-5,000 threshold cuts of the reconstructed bin, not a native solver speedup. Measured values live in `results/signed_threshold_20261015/physical_probe.json`.

## 4. Reuse and strict claim boundary

Source comparison: PR150 already has exact 2-moment positive exponential closure and a one-way **FLRW-only** inactive HI reservoir, with cold coupled Newton chemistry. PR152 has an independent **conditional E^-3 fixed-neutral** positive H/He ray oracle including the observed HeII angular quadrature problem. `bass_cr` PR72 has source-bound Verner H/He absorption and thermal RHS, and PR71 has adaptive positive child-moment bounds; `BASS_HE` PR65 has source one-birth cutoff preimage; `rec_bianchi` PR95 has an H-only HyRec short-trajectory donor gate; `bass` PR162 optimizes massive stress; `WU088_HH` PR90 is still not a physical H-H collision rate for REI. All kept independent, not silently adopted.

Scientific status: **derived + symbolic-verified + local-code-verified conditional source-free closure**. This is an exact operator *within a selected positive exponential closure*, not a proof that two moments uniquely determine the actual photon spectrum. No production PR150 native integration, full z20→4 history, chemistry-active reversible cutoff, or cosmological isotope activation is claimed. Existing C12 negative HH gate stays HOLD.

## 5. Reproduce and next specific node

```bash
cd research/rei_c16_escape_20261015
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 test_signed_threshold_partition.py
rustc -O signed_threshold_sweep.rs -o /tmp/rei_signed_threshold
/tmp/rei_signed_threshold 4000000 12
```

On the separately authorized NCP (key kept outside published artifacts): `rustc -O /root/REI_C16B_SIGNED_THRESHOLD_20261015_001/signed_threshold_sweep.rs -o .../signed_threshold_sweep`, then run corrected binary with user-chosen logical worker count and verify JSON `failures=0`. Original shared PR150 NCP stages and existing R9 worker must remain untouched.

The next implementation gate for *production* is to read PR150 current source at its new exact HEAD, preserve its fixed-reference moments, integrate a source-aware bidirectional cutoff in an isolated opt-in path, and verify three species/number/heat/shear-work ledgers and threshold-sensitive angular/time refinements. Only then consider full NCP physical history and actual Tgas(t) source ownership. No code in PR150 has been mutated this turn.

Literature: Mellema et al., `C2-Ray`, New Astronomy 11 (2006) 374, DOI 10.1016/j.newast.2005.09.004; Pawlik & Schaye, MNRAS 412 (2011) 1943, DOI 10.1111/j.1365-2966.2010.18032.x; Verner et al., ApJ 465 (1996) 487, DOI 10.1086/177435. These support method comparison and physical opacity distinctions, not claimed novelty of the derived closure.

Native subagent dispatch: NOT_RUN; no host delegation tool exposed. Scientific checks include actual Wolfram CAS and independent Python/Rust numerical implementations.
