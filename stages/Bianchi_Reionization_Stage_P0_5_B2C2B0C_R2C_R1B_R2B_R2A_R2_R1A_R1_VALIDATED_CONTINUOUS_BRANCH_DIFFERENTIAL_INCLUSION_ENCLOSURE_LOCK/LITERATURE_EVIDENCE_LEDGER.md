# Literature evidence ledger

## Verified ODE integration and Taylor models

M. Neher, K. R. Jackson, and N. S. Nedialkov, “On Taylor Model Based Integration of ODEs,” *SIAM Journal on Numerical Analysis* 45 (2007), 236–262, DOI `10.1137/050638448`.

Load-bearing use: interval dependency and wrapping can make validated bounds overly pessimistic or break an integration; Taylor models combine symbolic dependence with interval remainders to reduce those effects.

## Stable affine set-valued integration

B. Houska, M. E. Villanueva, and B. Chachuat, “Stable Set-Valued Integration of Nonlinear Dynamic Systems using Affine Set-Parameterizations,” *SIAM Journal on Numerical Analysis* 53 (2015), 2307–2328, DOI `10.1137/140976807`.

Load-bearing use: axis-aligned/Taylor-model enclosures may diverge from wrapping, while predictor-validation propagation of affine set-parameterizations can provide guaranteed enclosures with stability properties; Taylor models with ellipsoidal remainders are a named admissible realization.

## Set-valued sensitivity integration

N. D. Peric, M. E. Villanueva, and B. Chachuat, “Sensitivity Analysis of Uncertain Dynamic Systems Using Set-Valued Integration,” *SIAM Journal on Scientific Computing* 39 (2017), A3014–A3039, DOI `10.1137/16M1102719`.

Load-bearing use: polynomial-model inclusions can propagate parameter-dependent trajectories and sensitivities while treating parameterization error as time-varying uncertainty.

## Claim boundary

These references motivate and specify the next validated-numerics architecture.  They do not prove that the present `rei_bianchi` enclosure will be narrow; that remains the next stage’s calculation.
