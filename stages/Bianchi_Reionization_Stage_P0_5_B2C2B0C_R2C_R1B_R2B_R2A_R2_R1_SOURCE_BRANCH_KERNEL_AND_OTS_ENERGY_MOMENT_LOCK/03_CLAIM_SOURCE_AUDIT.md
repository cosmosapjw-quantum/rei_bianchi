# 03 Claim/source audit

1. Hummer & Seaton identify the nodal two-photon branch.  Their Ly-alpha equation carries `(1-X)` and their two-photon equation carries `X`; Table V tabulates `2(1-X)`.  Hence `v=X=1-[2(1-X)]/2` at the five tabulated temperatures.
2. Neither Hummer & Seaton nor Kramer & Haiman specifies the exact numerical interpolation algorithm.  A piecewise-linear adapter in tabulated `log10(T)` is retained only as a declared adapter; the nodal values are the source-identical objects.
3. Friedrich et al. define `f` as the absorbed He II Ly-alpha fraction and `1-f` as escape.  Their prose/table supplies only the range `0.1--1`, not a function of neutral fraction.  The table's “escape fraction” label conflicts with the surrounding equations and is not used to reverse the meaning.
4. `ell=1.425` and `m=0.737` are zeroth photon-count moments.  They do not identify a first spectral-energy moment.
5. The He II Ly-alpha packet is monoenergetic in the adopted H/He model and therefore has an identifiable first moment.
