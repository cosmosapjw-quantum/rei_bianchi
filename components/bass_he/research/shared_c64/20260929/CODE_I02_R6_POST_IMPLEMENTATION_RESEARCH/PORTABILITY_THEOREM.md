# R6 portability theorem and certificate-record contract

For a 2x2 nonnegative distance matrix D, the pair-membership algorithm uses

E(D) = min(max(d00,d11), max(d01,d10)).

If ||D-D'||_inf <= eta, then

|E(D)-E(D')| <= eta.

Reason: max is 1-Lipschitz in the sup norm, and so is min. Therefore both permutation bottlenecks change by at most eta, and their minimum changes by at most eta.

If each distance entry has a rigorous interval enclosure d_ij in [lower_ij, upper_ij], monotonicity gives

E(lower) <= E(D) <= E(upper).

A future rigorous checker can classify:

- CERTIFIED_PASS if E(upper) < tolerance;
- CERTIFIED_REJECT if E(lower) > tolerance;
- UNRESOLVED if the enclosure straddles the policy threshold.

The difficult part is rigorous enclosure of the spectral roots entering the four distances, not the min/max layer.

Current R5 requires exact IEEE-754 hex equality of stored and fresh matching error. This is fail-closed but stronger than semantic membership. Literature on numerical reproducibility shows that cross-platform bitwise equality is not automatic for floating-point linear algebra. R6 therefore leaves a contract decision to independent rereview:

1. environment-bound record: exact hex equality is retained and environment identity becomes part of record validity; or
2. portable semantic record: fresh semantic revalidation owns admission and stored matching error is diagnostic metadata.

The representative hostile-review endpoint had error 3.156324676166531e-11 against tolerance 5e-6, a ratio of about 1.584e5. This is empirical margin only, not a rigorous cross-platform enclosure.
