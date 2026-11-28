# ARSENY Version 1 static data-flow

Primary bytes: arseny.f, SHA256 96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78; public Mendeley dataset [10.17632/n43srxwdnm.1](https://data.mendeley.com/datasets/n43srxwdnm/1). Line numbers refer to the 2,816-line original CRLF FORTRAN file preserved outside the clean-room repository. The archive and each file match provider SHA256; see `AUTHOR_SOURCE_MANIFEST.json`. No author code was compiled or run.

| Stage | Exact author file lines | Static observation |
| --- | --- | --- |
| Call order | 144–154 | Main calls BRANCHES, then STCKLBRG, then CR_SECTION. |
| Contour data | 1181, 1382–1385, 1416, 1437 | SURFACE supplies complex two-surface difference `DE` at contour points in `surfaces.dat`; ITYPE=11 skips this call. |
| Eq.(56) quantity | 1193–1199, 1255–1306 | STCKLBR2 reads contour samples, accumulates nonnegative imaginary contributions into `DMESI` for each impact sample, and computes spline second derivatives. STCKLBRG receives `DMES` and stores it without an extra factor of two in the real component of `RC`. |
| Persistent record | 1211, 1243–1247 | STCKLBRG writes header and each complex `RC` plus support radius `RB` to `stuckelberg.dat`. The final slot holds state indices and branch radius (1188–1192). |
| Restore | 1591–1593, 1633–1645 | CR_SECTION reads every stored pair; accepted records are copied into `RCI/RBI`. No Delta multiplier is applied here. |
| Energy and handoff | 1692–1706 | CR_SECTION sets collision speed from energy at 1703 and passes `RCI/RBI`, `CMES/SPRO` into SECTION. |
| Inbound probability | 1888–1911 | SECTION copies `RCI` to `CMES`, gates by support, computes `DEXP(-CNUM2*DREAL(CMES(1))/V)` at 1904, then updates two matrix rows with that probability at 1905–1910. `CNUM2=2` at 1868. |
| Outbound probability | 1967–1985 | Reverse-order pass uses the same factor-two expression at 1978 and the same row-update pattern. Upper-shell `CQ=0` at 1976 suppresses the reverse source term. |
| Final observables | 1987–2005, 2214 onward | SECTION passes the assembled `P` to C_S_AT and accumulates shell cross-section components. No production execution was performed in this audit. |

**Classification:** `AUTHOR_USES_FACTOR2_DIRECT` on the stored, STCKLBR2-derived Delta for non-ITYPE11 branches. No renormalization appears between `DMES` and the exponent. The same exponent is present on both traversals and no separate Q/S exponent branch is visible in SECTION. This supports author-code agreement with the factor-two Eq.(55) expression and a source/code mismatch with the printed Eq.(52) factor-one matrix probability. It does not prove the discretized `DMESI` is mathematically identical to every interpretation of Eq.(56).

**Additional static limitation:** STCKLBR2 creates samples at multiple impact parameters; 1285 makes sample 1 correspond to zero impact parameter. SECTION iterates `RO` at 1888–1889 but exponentiates `CMES(1)` at both 1904 and 1978. No spline interpolation call occurs in SECTION or elsewhere in the 2,816-line file. Thus the stored impact-parameter-dependent Delta values and second derivatives are not selected for the matrix probability in this distributed source. Support gating still depends on `RO` (1903, 1977). This is a static code observation, not a measured cross-section error.

**Eq.(43) separation:** the source has no explicit `DeltaE_min` or `(DeltaE_min)^2` over slope formula. ITYPE=11 is assigned near a small gap (456–459); STCKLBRG instead stores zero for that type (1181,1193–1208). No source statement ties this zero path exactly to printed Eq.(43), so the linear-versus-squared Eq.(43) implementation question is `NOT_IMPLEMENTED_IN_DISTRIBUTED_SOURCE`, not a selection of either printed formula.
