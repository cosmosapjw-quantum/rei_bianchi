# From rate-table error to frozen-bath charge errors

## Contract and source

This additive theory connects the RUN19 coefficient-level interpolation bounds to an observable error budget for a finite atomic charge network with a prescribed bath. It does not replace the separate nonlinear temperature/electron-density/radiation tube problem. RUN19's current four-node interpolator is a value cubic in log temperature, not a log-Hermite interpolator. Its original smooth-branch and rounded-node obligations remain in the pinned source report.

The general residual/adjoint framework is literature-supported by K. Kormann and S. MacNamara, *Error Control for Exponential Integration of the Master Equation*, arXiv:1610.03232 (https://arxiv.org/abs/1610.03232), especially the residual integral bound. The edge pairing, source ledger, observable factors and computational contract below are derived here for the project. No novelty or impossibility theorem is claimed.

## 1. Finite charge network and time

Use a column vector p of nonnegative populations per conserved nucleus. In proper seconds,

    dp/dt = K(t) p + b(t),       K_ij >= 0 (i != j),  sum_i K_ij = 0.

For charge transitions j->i, K contains a_ij(t)(e_i-e_j)e_j^T, where a has units s^-1. A tabulated collisional coefficient k(T) in cm^3 s^-1 becomes a=n_e k only after matching density units. Photo rates and Be electron-capture hazards retain their own physical providers. If x=ln a_cos and H>0, use K_x=K/H and b_x=b/H; the error integral includes dt=dx/H exactly once. A monotone alternate clock uses its actual positive dt/dx. A clock reversal must be handled by reordering the physical integration interval, not a negative Markov generator.

Conserved-parent extension can place Be7 and its Li7 daughters in one block, with one nucleus on either side. Then source transfer is internal and the total mass is conserved. An external injection b is allowed, but its amount and errors must be retained; source disagreement is not zero-sum automatically.

Assume K is bounded and piecewise continuous on a finite interval. The fundamental solution U(t,s) is nonnegative and column stochastic: positivity follows from positive diagonal-shift Euler products and their limit, and 1^T U=1^T follows from differentiating 1^T U. Thus its induced l1 norm is one.

## 2. Residual identity and bound

Let p_hat be any continuous piecewise C1 approximation, and define

    r = d p_hat/dt - K p_hat - b.

For e=p-p_hat, variation of constants gives

    e(t) = U(t,t0)e(t0) - integral U(t,s)r(s) ds,
    ||e(t)||_1 <= ||e(t0)||_1 + integral ||r(s)||_1 ds.

For solver residual r_hat relative to K_hat,b_hat, r=r_hat+(K_hat-K)p_hat+(b_hat-b). Their contributions can be integrated separately with the triangle inequality. Jumps add their l1 defect exactly at the event; dense-output continuity must not be assumed across injection or event resets.

A finite sampled residual quadrature is a numerical diagnostic. A continuous certificate requires an interval enclosure or a proved quadrature remainder for each smooth panel and explicit event contributions. Endpoint interpolation accuracy alone does not establish this integral.

## 3. Edge defects and useful cancellation

Represent each unordered physical pair i,j once, with rates k_f for i->j and k_b for j->i. Let delta k=k_hat-k. Then

    d_ij = delta k_f p_hat_i - delta k_b p_hat_j,
    (K_hat-K)p_hat = sum_pairs d_ij (e_j-e_i),
    ||(K_hat-K)p_hat||_1 <= 2 sum_pairs |d_ij|.

The first expression computes the exact statewise defect vector in O(E+N), and can exploit cancellation between adjacent pairs. If only absolute coefficient bounds eta_f,eta_b are available, replace |d| by eta_f |p_hat_i|+eta_b |p_hat_j|. For positive populations and relative rate bounds epsilon, eta=epsilon*k. A negative reconstructed population must not be silently clipped; the absolute formula remains available and positivity loss is reported.

If both directions have the same relative perturbation delta k_f=epsilon k_f and delta k_b=epsilon k_b, then d=epsilon(k_f p_hat_i-k_b p_hat_j). Near balance this depends on net flux, which can be much smaller than the sum of gross forward/backward fluxes. This improvement requires an actual shared multiplicative error identity. Equal error bounds, a common temperature, or detailed balance in the exact model alone do not establish correlated interpolation errors. The implementation therefore accepts a declared common perturbation only as a separate explicit calculation, not as a default optimization of independent bounds.

## 4. Observables, conservation and nonlinear extension

For an observable w^T p, |w^T e|<=||w||_infinity ||e||_1. If 1^T e=0 exactly, subtract c1 with c=(max w+min w)/2 to obtain

    |w^T e| <= (max w-min w)/2 * ||e||_1.

If mass error m=1^T e is present and |m|<=M, the valid mixed bound is

    |w^T e| <= (max w-min w)/2 * E + |c| M,

where E bounds ||e||_1. Thus a single charge fraction has E/2 under matched total abundance, and Li mean charge q=0,1,2,3 has 3E/2. Ionization-energy and electron ledgers need their physical weights/units; this bound does not convert kinetic energy into deposited heat.

When K depends on the evolving state, the Markov contraction applies to the term K(t,p)(p-p_hat), while [K(t,p)-K(t,p_hat)]p_hat remains. A proved weighted bound <=L(t)||p-p_hat|| adds a Gronwall factor. Temperature, electron-density, opacity and source feedback must enter that L/tube. Frozen-bath certification therefore transfers only to the matching prescribed-bath block until those dependencies are enclosed.

## 5. Implementation and acceptance

Implement a small pure Python reference kernel with explicit N and pairs (i,j), population, actual forward/backward rate differences or nonnegative absolute bounds. Reject nonfinite inputs, self edges, out-of-range and duplicate unordered pairs; aggregate physically distinct subchannels before passing a pair. Preserve orientation, signed defects and source mass. Outputs: exact assembled defect, its l1 norm, pairwise triangle bound, independent-rate majorant, and observable mixed bound. No evolved-state modification and no provider/fit substitution.

Panel integration API must take widths in the stated clock and nonnegative *supremum bounds* plus optional independently bounded event defects. A separate sampled trapezoid diagnostic must have a different name/status so it cannot be presented as continuous certification. Return explicitly unresolved if only samples are supplied to a certificate request.

Focused checks: independent dense-generator assembly for arbitrary 2/4/17-state cases; orientation invariance; conservation; correlated-pair near-equilibrium cancellation versus gross bounds; analytic two-state evolution and analytic integrated perturbation upper bound; mass-mismatched observable counterexample; one jump; zero/invalid inputs. Tests are manufactured mathematical controls, not a fresh physical Li or RUN19 trajectory. Use a new bounded local execution allocation, preserve all previous failed BDF evidence and deadlines. Root must obtain independent review before adoption/publication.
