# Same-author blind-referee-style hostile review, one bounded pass

Date 2026-10-31. Independence: same-author adverse re-reading only, not distinct-author R6/C9.

1. **Photon-number provenance.** Original 193-epoch total Q includes tiny last Q_192 with no arrival. Truncating k=192 would underreport the unabsorbed count. Reconstruct last Q from exact original total source and all 192 earlier source weights, enforce sum_j N + sum_k R = 2sum_k Q. Emission final is retained.
2. **Original photon transport source is conditional.** Ferrett bounded LiII singlet envelope is not a positive astrophysical LiII measurement and this is not a second cosmological evolution. Does not prove any nonzero physical LiII background under a new source.
3. **Per-bin vs integrated error.** Off-diagonal 0.5922% total event mass; 103 late intervals have >50% memory fraction but only 0.36849% total event weight. Reporting 103 without its total support could exaggerate significance; both provided.
4. **Kernel state dependence.** Frozen matrix K is a derivative of first flight with respect to externally supplied pair emission Q at fixed opacity, not a local chemical Jacobian or a full derivative with respect to evolving Y/H/K. No F/J native claim.
5. **Li I Auger.** One electron per primary photoionization is native BASS coarse graining and does not establish physical charge yield for LiI 1s Auger or fluorescence. Avoid isotope-resolved F injection.
6. **First absorption vs final escape.** Residual by z=2 includes survivor photons and latest emission, not rays escaping to infinity. No physical photon energy closure with binding, redshift, helium secondary cascade from scalar count alone.
7. **Clock and attribution.** Original BASS elapsed_s and frozen PR302 proper_interval_s agree relative <=1e-12, but absorption occurs within the interval. Only delay brackets are valid. Mean of brackets is not inferred event time.
8. **FS2010 off-manifold.** All 192 BASS chemistry rows violate exact single-x_i HeII/HeIII assumption. Only 87 xi-range projected bins have model-only heat bounds. Invalid bins left NaN; no false physical heating gate.
9. **Numerics and provenance.** Original source identities by full SHA. Original PR305 heat bounds reconstructed independently from 18528 source links, rather than simply copying the PR305 192 columns; 30 tests incl negative controls. One initial broadcasting implementation error requested an artificial 51 GiB temporary array, fixed to (18528,1,5) coefficient broadcast without altering science inputs. Runtime/resource issue, not physics failure; rerun tests PASS.
10. **Double count and weak Jacobian.** The formal source port is never added to pre-existing BASS or REI photo RHS; inherited neutron weak J[H1II,n]=1/878.4 s^-1 explicitly verified. A future replacement requires identifying same photon owner and isotope stoichiometry.

Verdict: SOURCE_SCOPED_NUMERICALLY_CHECKED, NOT_FULL_REI17, NOT_PRODUCTION, NOT_DISTINCT_AUTHOR_REFEREE. Canonical DAG unchanged 33/88, 28/88, 4/7.
