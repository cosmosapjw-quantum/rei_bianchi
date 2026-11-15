# Original five-case baseline: actual incremental result

The previously missing q_ref=+0.01 native continuation reached a=0.2, zbar=4, accepted=312237, exit0. Geometry composition retains 312238 complete time-ordered rows, verifies both segment boundaries, excludes the 47 unsupported orphan rows, and pins the composed SHA-256 to `e1b0c293302ec5ab9a56d525631098227205556e9902db6bf277e8d307460560`. This result consumes those actual rows. The four previously reviewed cases are reused without another reduction or trajectory.

The incremental consumer completed in 15.609194189 seconds. It generated a complete normalized native +0.01 abundance table (62,611,024 compressed bytes, SHA-256 `fb9c0821b4180bed9f65d807ddb0e8b39a6e6a35567e8f0235f611512b3c75f6`) and a separate 5005-row five-case inspection sample. Charge and baryon-Y residuals are at most 2.22e−16; comoving-density residual is 3.33e−16. The large normalized table has a public source/column/hash manifest and is retained separately from the small git package.

Actual data generation is complete. Independent fifth-case review and owner admission are recorded separately. AX11 resolution and AX12 robustness remain open; they are downstream scientific obligations, not a reason to deny that a complete baseline history exists.

## Prescribed-background approximation result

For +0.01 the maximum forced fixed-background |δs/H| is **1.014434481527696e−5**, at zbar=4.8864814663. The native ionizing contribution is at most 1.2586430036e−13; the effective initially isotropic collisionless radiation term dominates. The original extra-energy comparator, using H_FLRW² in its denominator, peaks at **9.682725793760002e−8**. Both are below the unchanged 1e−4 diagnostic targets. The maximum |δs/s| is 0.008654483727, so a small |δs/H| is not the same statement as an arbitrarily small fractional correction to shear.

All five represented cases now have these diagnostics. Their largest |δs/H| and extra-energy ratio remain the −0.01 values, 1.0210497766163151e−5 and 9.728861295902034e−8. The CMB-only +0.01 shear diagnostic is 6.0025552434e−6. This is the conditional massless, collisionless, initially isotropic radiation model; it is not a universal background-radiation bound.

These values solve a forced equation with the saved geometry held fixed. They omit −3s₀δH and the radiation/matter response to perturbed geometry. They are not a closed linear backreaction solution and do not bound coupled abundance or temperature errors. The detailed distinction is in `INTERPRETATION_AND_CONTRACT.md`.

## Abundance response and sign comparison

The following are signed values at the largest absolute sampled +0.01-minus-ZERO response. Both coordinate modes use the exact original PR374 1001-point sample grids and pinned interpolation conventions.

| Quantity | Fixed a / zbar | Fixed elapsed proper time |
|---|---:|---:|
| x_HII | −2.467175664e−6 | +1.710271699e−5 |
| x_HeII | −2.300940398e−6 | +1.484863986e−5 |
| x_HeIII | −2.562300807e−8 | +4.090945989e−7 |
| n_e/n_H | −2.644677207e−6 | +1.827262310e−5 |
| T_gas [K] | −0.02657833578 | +0.1538474448 |

This coordinate-dependent sign is an estimate from the saved conditional model. It does not by itself establish a resolved physical effect. Original fraction floors are 1e−7 (with the charge-propagated electron floor) and the temperature floor is 0.01 K; exceeding a floor is necessary but does not replace the paired AX11 refinement target. In particular the fixed-a HeIII response is below the original fraction floor.

With O(q)=[X(+q)−X(−q)]/2 and E(q)=[X(+q)+X(−q)]/2−X(0), the fixed-a x_HII odd maximum is 5.52335955e−15, while its even maximum is 2.467175664e−6. The maximum E(.01)−4E(.005) residual is 1.03502318e−10. This supports an approximately quadratic baseline sample trend but does not prove continuum order or exact sign symmetry. The temperature odd maximum is 1.33263711e−8 K, also far below its scientific floor. All odd-sign claims remain unresolved.

The original source genuinely transports angle-resolved photons and applies energy-dependent photoabsorption; exact scalar sign parity is not imposed by a mean-H-only radiation operator. A separate frozen angular-kernel counterexample and actual native half-sign moment differences are preserved. No exact-parity theorem is inferred from the small chemical differences.

Native first-upward x_HII crossings for the new case occur at zbar approximately 10.248037, 6.816983 and 5.804533 for levels 0.1, 0.5 and 0.9. Brackets, proper-time values, PCHIP sensitivity and comparisons with ZERO/−0.01 are in `results_five/fifth_milestones.csv`; these are interpolation diagnostics, not evolution-error estimates.

## Cohort residence check

The actual native columns also permit

\[
\lambda_{\rm abs}=\frac{(1-x_{\rm HII})\Gamma_{\rm HI}
+f_{\rm He}(x_{\rm HeI}\Gamma_{\rm HeI}+x_{\rm HeII}\Gamma_{\rm HeII})}{N_\gamma/{\rm H}},
\qquad \chi=|s|/\lambda_{\rm abs}.
\]

At the nearest native row to the fixed-a HII response peak, λ_abs=2.24377189e−13 s⁻¹ and χ=1.74321245e−7. At the HeII and temperature response peaks χ is respectively 3.98474287e−8 and 1.18317566e−8. Under a quasi-stationary, absorption-dominated residence approximation these values support short anisotropy memory at those epochs. They do not measure a cubic abundance coefficient. The largest late-time χ is 0.00257515455; source evolution, redshift losses and energy-dependent residence distributions prevent a universal conclusion. Numerical suppression remains an AX11 question.

The next scientific gate is a paired convergence experiment on actual baseline responses, with source/IC and atomic-model robustness kept separate. Repeating baseline plots or recomputing the four frozen diagnostics will not resolve that gate.
