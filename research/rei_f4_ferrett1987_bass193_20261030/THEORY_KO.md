# REI F4: Ferrett 1987 Li I 1s measured residual-state branching on original archived BASS193

**Source/model status:** literature-supported Ferrett et al. (1987) measured partial photoelectron cross sections; **derived** fractional state projection; **numerically checked** original BASS21 saved history projection; **unresolved** common physical source ownership, especially primary Li I full K-shell cross sections and singlet vs `1s2p ^3P` decomposition. No new IVP; mean archived BASS gas and radiation flux unchanged.

## Definitions and measurement limitations

Ferrett et al. (1987), *Phys. Rev. A* **36**, 3172-3183, DOI `10.1103/PhysRevA.36.3172`, original author report LBL-22068: `https://escholarship.org/uc/item/8k72s0qj` (complete Table IV, p.31-32 of report). Define at measured photon energy `E`:

- `sigma_2(E)`: total Li+ `1s nl` residual `n=2` intensity (Mb).
- `sigma_3(E)`: total Li+ residual `n=3` intensity (Mb).
- `sigma_T(E)`: resolved Li+ `1s2s ^3S` (Mb).
- `sigma_U(E)`: **unresolved** Li+ `1s2s ^1S` plus `1s2p ^3P` (Mb).

For **only the recorded n=2 and n=3 core channels**, set `D(E)=sigma_2(E)+sigma_3(E)`. The empirical competing partitions are

\[f_T=\frac{\sigma_T}{D},\quad 0\le f_S\le \frac{\sigma_U}{D},\quad f_{n3}=\frac{\sigma_3}{D},\quad f_{\rm other}=\frac{\sigma_2-\sigma_T-\sigma_U}{D}.\]

One has `f_T + f_U + f_n3 + f_other = 1` by identity, but the true singlet lies only between 0 and `f_U`. The `f_other` residual is **not** a physical standalone product state, and the `f_U` bound must not be promoted as a measured spin-specific yield. At 87eV: `sigma_2=1.45Mb`, `sigma_3=.30Mb`, `sigma_T=.89Mb`, `sigma_U=.51Mb`, and `f=(89,51,30,5)/175`; Wolfram independent exact sum is one. One megabarn = `10^-22 m^2`. The original reference reports ~20% **absolute calibration** uncertainty from total photoabsorption; statistical errors in parentheses do not include it. Ratio errors need their *covariance*, not quadrature of independent absolute errors.

Only 80–99eV has fully tabulated `sigma_3` and this code explicitly refuses extrapolation. For high end 93–99eV the authors averaged `3S/(1S + 1,3P)` and assumed a continuation of another resonance ratio, hence those records are separately marked. 80–92.5eV has directly reported `R31` but some associated deconvolution still invokes a described `Rp` relation. The 75/77.5eV rows lack sigma_3 and are excluded even though they have sigma_T. Higher satellites `n>=4`, direct valence ionization and multiple-ionization may exist, so `D` is not a proven total K absorption denominator.

## Link to frozen original BASS21 source events

Reuse exactly original BASS owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c` trajectory `x=ln(a/a_ini)`, original `H(x)`, Li6I/Li7I partial photon event rows `r_{k,i,b}` (per baryon proper s). Source is original PR287 full package (SHA in README); reject any source hash mismatch. For each of the 4 original 71 photon bins with E within [80,99] eV, interpolate **published measured partial cross sections only within observed knot support**; do not extrapolate to any other BASS photon bin. The conditional cross-owner diagnostic is

\[r_T^{\mathrm{projection}}(x_k,E_b)=r^{\rm BASS}_{K}(x_k,E_b)\,f_T^{\rm Ferrett}(E_b),\]
\[0\le r_S^{\mathrm{projection}}(x_k,E_b)\le r^{\rm BASS}_{K}(x_k,E_b)\,f_U^{\rm Ferrett}(E_b).\]

**Important**: Multiplication across two distinct cross-section source owners is a **model transfer assumption**, not a derived identity of the real BASS atom. The experiment did not constrain its behavior outside [80,99]eV, and this study never applies it there. The `1s2s ^3S` state emits a 59.0207eV M1 photon on complete isolated radiative decay, whereas `1s2s ^1S` emits a pair totaling 60.9226eV on vacuum 2E1 decay. This study does **not** assume radiative escape or instantaneous gas heating.

Use original 193 equally spaced log-scale epochs with Simpson postprocessing only:

\[N_{\alpha}^{\rm projection}=\int\frac{dx}{H(x)}\sum_{i\in\{Li6,Li7\}}\sum_{b\in[80,99] \mathrm{eV}}r_{i,b}(x)f_{\alpha}(E_b).\]

No cosmological evolution or radiative transport is integrated. Units are events per original BASS baryon. Every coefficient is nonnegative. Original summed Li K rate is positive; the integrated restricted window must not exceed the total source-integrated K events. Potential observational `sigma_U` is not a realized singlet count; use it only as an upper envelope.

## Scientific claim/adversarial boundary

1. **Source-original:** Original BASS 193 epochs, 8492 Li 1s isotope-bin event records, exactly 4 measured in-window photon bins per isotope.
2. **Literature-supported, source-transcribed:** Ferrett Table IV numerical rows; this system did not directly verify the image pixels of the PDF, so per-digit scan glyph verification remains open.
3. **Derived/numerically checked:** 1544 actual BASS source-driven conditional projection rows and epoch-integrated competing channel envelopes, *within* the native measured 80–99eV window.
4. **Not shown:** Same-source-equivalent Li spin yields, isotope-dependence of laboratory Li source (original experiment did not separately measure Li6 and Li7), actual 2E1 photon propagation or deposition, full REI17/BASS21 common electron/clock/chemical owner.
5. **No new IVPs; no canonical DAG physical acceptance:** Working `33/88`, Central `28/88`, F4 fast `4/7`, physical delta `0`.

## References/data request (only for publication-grade refinement)

- T. A. Ferrett, D. W. Lindle, P. A. Heimann, W. D. Brewer, U. Becker, H. G. Kerkhoff, D. A. Shirley, *Lithium 1s main-line and satellite photoemission: Resonant and nonresonant behavior*, Phys. Rev. A **36** (1987) 3172-3183, DOI `10.1103/PhysRevA.36.3172`. Author LBL-22068 full PDF: `https://escholarship.org/content/qt8k72s0qj/qt8k72s0qj.pdf`, Table IV report p.31-32 and Table II report p.29-30. If inaccessible, download from `https://escholarship.org/uc/item/8k72s0qj` and supply just those printed PDF pages for direct pixel verification.
- G. W. F. Drake, G. A. Victor, A. Dalgarno, *Two-Photon Decay of the Singlet and Triplet Metastable States of Helium-like Ions*, Phys. Rev. **180** (1969) 25-32, DOI `10.1103/PhysRev.180.25`, original Li II 2E1 Table II p.29. Printed column OCR remains partly unverified; this new experimental branching calculation itself does not depend on the OCR shape.
- For full physical spin state ownership: high resolution Li I K-shell cross sections of `1s2s ^1S` separately from `1s2p ^3P`, measured across all original BASS 71 photon bins or calculation with source-qualified state-resolved partial rates. The 1987 paper does **not** provide that separation for the listed high energies.
