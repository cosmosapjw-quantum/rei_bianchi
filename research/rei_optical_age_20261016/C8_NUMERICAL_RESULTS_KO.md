# C7–C8: optical-depth versus time-born HeI threshold numerical experiment

**Source authority**: original native PR171 HEAD `c07ba9b839aa003a7b9afb3c6be9adce24761eeb`, parent code Grackle owner `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. Independent sandbox only, with **manufactured** per-normalized-u source and positive rates. Do not transfer these numeric errors to actual MD14/Grackle.

### Measured q0, τ=308.56, x_HeI_cut=.992

Independent QUAD survivor `9.318191209927805e-7 photon/H`; SciPy Radau `9.318191209927693e-7`. Eight-node fractional errors:

| Method | abs(N-N_QUAD)/N_QUAD |
|---|---:|
| Uniform-time midpoint impulse | 0.9999998103916472 |
| Positive event-aligned φ1 slabs | 0.0031865560806303666 |
| Optical-Laguerre without HeI event split | 0.07885298735169083 |
| **Optical-depth GL+shifted-Laguerre with event split** | **1.2498888209482091e-15** |

**This extreme result uses a deliberately simple piecewise-affine manufactured hazard.** The high-τ `794.875` control yields n8 event-split optical relative error `2.1161e-14`. Neither establishes native adaptive spectral, H/He chemistry or Bianchi forecast accuracy. Since scalar κ is prescribed the q=0,±0.1 survivor counts are identical *by construction*; signed shear changes photon energy and geometric work, independently validated.

Source-independent Radau H/He number ledger at q0 `6.5052e-19 photon/H`, full photon/thermal/binding/shear-work energy ledger `9.9747e-18 eV/H`. Surviving photon mean source age, normalized u, `0.00463867006782456`, independently reproduced by optical-clock positive quadrature to < `2e-11` absolute. HeII channel remains exactly zero.

### Original PR171 actual numerical comparisons, **not from toy**

Original fetched `evidence/matrix/MATRIX_COMPARISON.json` Git blob SHA1 `f1408f759615e66d38021e688a63a3ad4812242c`:
- age16→32: survivor N relative difference `0.9013495137`, integrated HeI events `1.956139715976142e-5`, sensitivity quotient `46077.97`.
- transport32→64: HeI instantaneous Gamma relative difference `0.0008124834365`, cumulative HeI event relative difference `0.0074973509683`, quotient `9.227697`. **Endpoint-Gamma agreement does not prove HeI integrated event accuracy.**
- Both are adjacent-grid differences (not continuum errors or rigorous bounds). Actual PR171 age32→64/native-time and transport64→128 remain HOLD.

### Execution/preservation

21/21 new runnable `unittest`, SciPy QUAD/Radau consistency, original source moment sensitivity, two manuscript figures and numeric `evidence/optical_age_study.json` were actually run on Python 3.13 sandbox, no remote Rust. First faulty test assumptions retained in first-test log. Wolfram verified exact Bianchi energy derivative and piecewise hazard derivatives `{0,0,0}`. Cross-reference prior established photon conservation C²-Ray [Mellema et al.](https://arxiv.org/abs/astro-ph/0508416), helium [Friedrich et al.](https://arxiv.org/abs/1201.0602).

- [C8 standalone full scientific ZIP, Drive](https://drive.google.com/file/d/1f1mXsRWj17xSj7RWxNY3-DbLaN74wXcM/view), **166,824 bytes**, SHA256 `9b9796eb22e7b1aa1feb9b3de0290211eac0b6ed016b72f30de597d5d232a579` and 20 payloads.
- Google Drive and ChatGPT Library both uploaded/independently full downloaded: **2/2 exact SHA, ZIP CRC and per-payload manifest PASS**. A more complete C10 full package also exists and is independently replayed.
- Full code/test/result/figure bytes are in Drive capsule, not substituted by this Markdown summary. Nothing copied into native production Rust.

**DAG C7 SCIENCE_QUAD_RADAU=SCOPED_PASS; C8 POSITIVE_HAZARD_TEST=SCOPED_PASS; C10 backup+publication next. Production scientific admission NOT_ISSUED.**
