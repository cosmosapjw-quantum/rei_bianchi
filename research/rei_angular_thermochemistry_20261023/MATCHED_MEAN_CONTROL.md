# R7 addendum: one matched mean-redshift control

The nine prescribed trajectories completed within the original cumulative
CPU300s/wall420s allowance. The initial comparison grid044 versus grid022
changes both the saved expansion history H and its shear. It therefore
cannot isolate the effect of replacing C22A's mean-redshift UV approximation
by the directional characteristic. This is a concrete interpretation risk.

The controller authorizes one final distinct trajectory, case10
`grid044_M4_mean_tight`: use the same saved grid044 H and n_Href, the same
M=4, C22A initial populations, T=300K and finite UV counts as the existing
`grid044_M4_tight`, but use the already implemented Background(sign=0).
Thus b=b'=0 only in the new trace geometry. Use exactly the same tight
rtol2e-11 and corresponding atols as the existing tight case. No event RHS,
source coefficient, initial density, solver or physical accuracy tolerance
is changed. This is a prescribed counterfactual mean-redshift calculation,
not a claim that the stored anisotropic background becomes an Einstein
FLRW solution.

Compare T, electron fraction, U_gamma, signed Q, W_mean, W_shear and tau_T
at the same201 reporting times. Record endpoints and maximum differences.
This separates a physical model contrast from a numerical-reference error.
No pass condition requires the two physically different traces to agree.
Each retains the original conservation and validity gates.

Ten distinct completed trajectories plus the first interrupted/resumed
attempt remain within the original maximum11 new-IVP attempts. The extra
process invocation is operational only; total new scientific CPU300s,
wall420s and1.5GiB address-space caps remain unchanged. No further optional
parameter sweep or matched timing experiment is authorized by this addendum.
All previous results are reused. The independent reviewer checks the new
configuration/result and the final figure-only layout correction.

Angular refinement reports log2 ratios of successive observed differences.
Those ratios are not asserted to be asymptotic convergence orders. In
particular T, n_e and tau_T differences at the solver-noise level establish
no resolved angular order in this run.
