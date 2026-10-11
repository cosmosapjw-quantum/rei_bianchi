# Newly requested exact failed-boundary diagnosis

Evidence: `evidence/PILOT01_FAILED_MEAN/RESULT.json`, source arrays and64/128 mathematical probability measures; `ENDPOINT_PRODUCT.json`. Source implementation bytes are unchanged from first C11 runs. `diagnose_failed_mean.py` recomputes only the new exact boundary's source integrals, not the failed native coupled map or previous tests. Native calls0.

At elapsed977363400.0610615s, the unchanged generic indicator is1.6553590127107777e-7 and rejects against1e-7. The stored born cell is [50000,50000.00421957968]eV. An80digit source integral gives mean50000.001406526568470457...eV; the binary64 reconstructed mean is50000.00140652657eV. Its difference2.9020667e-12eV is2.0633e-9 of the tiny born-cell mean offset but only5.8e-17 of the physical mean. The difference due to reconstruction division rounding alone, relative to the exact rational stored U/(R N), is1.3090994e-12eV.

The positive power-law family has a monotone likelihood ratio in q. Hence two same-support family members are stochastically ordered, and their one-dimensional Wasserstein distance equals the absolute difference of their means. For a positive smooth kernel with |d ln K/d ln q|<=L, its relative expectation perturbation is bounded by

    L exp(L ln(b/a)) |delta mean|/a.

Using endpoint lane's declared conservative Lsigma8.8 and Lheat24303.5 gives bounds2.3041e-16 (K0),2.5659e-16 (KE),6.3763e-13 (heat) for division rounding alone. These are conditional mathematical bounds on a same-support smooth-kernel comparison; they exclude support changes, discontinuity crossings, native implementation roundoff, nonlinear evolution and fullhistory acceptance. The actual native physical-kernel derivation/tests remain the endpoint lane's responsibility.

The unchanged `_measure` q/P arithmetic was inspected with a constant manufactured sigma callback. This constructs the same reconstruction/probability nodes without native opacity calls and is explicitly not physical opacity admission or a bypass path. Its64/128 measures preserve the authoritative energy to4.31e-17 in80digit summation and fit the reconstructed mean offset to1.26e-16. All nodes are strict interior.

There is no numerical evidence that authoritative D is required solely for this50keV cell's1e-7 smooth native-kernel target. D remains diagnostic. The generic indicator is conservative for arbitrary kernels and has not been removed or relaxed here; any provider-specific alternative needs its own explicit trace and bound.

A separate exact-product caution is preserved: binary64 R*b equals50000, while the exact product of those stored binary64 operands exceeds50000 by2.3540e-12eV. This is a domain/rounding convention issue, not permission to extend the physical provider. Nodes themselves are interior. Any rigorous interval argument must include its explicit float-coordinate contract and that tiny support-product uncertainty.
