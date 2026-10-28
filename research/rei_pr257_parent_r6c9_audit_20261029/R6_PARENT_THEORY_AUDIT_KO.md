# R6 · PR257 parent theory audit (2026-10-29)

Status: **PARENT_DERIVED_AND_NUMERICALLY_CHECKED; distinct-author independent R6 NOT_RUN; no original science node promoted**. Baseline PR257 `dc1660c3950ca61d0dedfe5d6c5a069df212f8da`, source SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b` reproduced exactly in fresh Python source projection. Original DAG **33/88 working, 28/88 central last, delta0**; PR257 still **18/20**.

## Mathematical theorem

For published seven-bin BB13 covariant-statistical GLS `A=(X^T C^{-1}X)^{-1}X^T C^{-1}`, `X=[1,z-3.6]`, `r=d-m`, `theta=(gamma_TDR-1.4)/0.2 in [-1,1]`, independently allowed deterministic Jeans coordinates `j_i in [l_i,u_i]`, the joint parameter image is `Z={A(r+theta v+j)}`. With `c=(l+u)/2`, `h=(u-l)/2` the support is `H_Z(s)=s·A(r+c)+|s·Av|+sum_i h_i|s·A_i|`. This is an exact deterministic **outer box image**, not a probability law, physically jointly attainable thermal history or posterior.

**New constructive control:** the eight nonzero planar generators `g0=Av,gi=h_i A_i` have eight distinct unoriented angles; the 2D zonotope therefore has exactly **16** vertices. Orient each generator into polar angular range [0,pi), sort by angle, start at `A(r+c)-sum(g)`, traverse `+2g` in sorted order, then `-2g` in the same sorted order. Proof: supporting-face maximizing signs change exactly at normals perpendicular to these eight distinct generators. For N generators, boundary construction costs O(N log N) sorting plus O(N) output and avoids 2^N enumeration. Parallel generators require merging and fewer vertices.

Fresh independent-algorithm QR-whitened full-C numerical check: beta [-0.13087466565371770,0.05120681213727568] dex; kappa [0.053617504767915526,0.09922533966611840] dex/redshift, consistent with original exact-rational PR257. Eight-generator compact polygon vs 256 mapped corners maximum vertex discrepancy **1.962615573354719e-17**, 721-direction support discrepancy **5.551115123125783e-17**. C SPD and `AX=I` (maximum residual **4.44e-16**). Common all-bin additive offset alters beta but not kappa; affine `a+b(z-3.6)` responds exactly by `(a,b)`.

**P1 joint representation:** `max_Z(beta+kappa)=0.12823628160591508`, strictly below sum of independent component maxima `0.1504321518033941`. Do not replace the joint zonotope with its axis-aligned enclosing rectangle in any downstream joint profiling.

**P2 signed-source ambiguity:** the unlabeled symmetric interval image is invariant under `v->-v`. The hull alone cannot check EOS sign. The signed gamma=1.6 / theta=+1 response must match BB13 Table 1. **P1 physical scope:** other systematics, statistical sampling law, thermal-history correlation, source-template physics and Bianchi global tilt not covered. EOS/Jeans corrections are not globally fitted physical rates.

Runtime: local actual separate Python code, QR and 256 corners **exit 0**, source-byte identity matched, `/usr/bin/time` user2.07/sys0.28 CPU seconds (not deducted from historical closed grants), peak117512KiB; Wolfram symbolic GLS row algebra yields True,True. This parent is not a separate native author, whose tool was **not exposed**. No ODE/IVP or original owner modifications.

Local immutable checked archive: `REI_PR257_R6_PARENT_REVIEW_20261029.zip`, 24469 bytes, SHA256 `b8a4ba4de3bfac7b1e36af0d54fdb390dc3a316cfc10a0ad548442db4755b8a6`; original payload SHA/CRC PASS; new cloud ZIP upload NOT_RUN. Older PR257 archive dual-provider metadata read back at 126789 bytes.
