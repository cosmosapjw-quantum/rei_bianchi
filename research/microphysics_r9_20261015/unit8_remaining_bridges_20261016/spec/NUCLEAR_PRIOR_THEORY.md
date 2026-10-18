# Unit 8 lane D: actual source-native nuclear-prior covariance

Authority requested Astra; observed model UNKNOWN. This is a bounded propagated-prior calculation, not a joint observational fit and not a replacement of the immutable R5 donor. The same public PRIMAT source commit is reused, but the frozen small reaction network differs from the donor's large bare-Be overlay. No pre-existing runner or provider source edits are authorized.

## Source and physical model

Use official CyrilPitrou/primat commit4bf97d5082eee54b9df50d88f43182bb651fea80, staged at /workspace/scratch/37bc4acea758/u8_primat_provider. The root intake manifest must verify exact Git blob identities of all used primat-c source and primat/data files before execution. Build the standalone native executable with its own Makefile; do not install Python packages or rewrite the BBN solver. The supplied plasma/weak caches and NEVO files are actual model inputs, not permission to recompute expensive missing tables in this task.

Freeze network=small, Omegabh2=.02205, Omegach2=.12495, h=.7, DeltaNeff=0, tau_n=878.4s, std_tau_n=.5s, T_end_MeV=.001, decay_era=false, numerical_precision=1e-7, strict_params=true. All other parameters are pinned source defaults, including the standard neutrino/background and weak-rate corrections. Use a task-owned cache overlay and no user_nuclear_dir. This network has12 active thermonuclear reactions, with weak n↔p handled separately; retain the complete exact small.txt and associated uncertainty tables in the portable provider package. The frozen rate-rescale cap is30, as in the upstream default. This is part of the prior model, not an invisible numerical safeguard.

Source-native MC draws one independent p_r~N(0,1) for each active thermonuclear reaction in its network order and then one normal neutron-lifetime deviate, tau=878.4+.5*z_tau s. A single p_r is used at every temperature for that reaction: rate uncertainties are coherent across temperature, not independent temperature-bin noise. For tabulated multiplicative uncertainty factor f_r(T),

    rate_r(T;p)=rate_median_r(T)*clip(exp[p_r*ln f_r(T)],1/30,30).

All additive delta_r=0. Reverse rates are rebuilt from varied forward rates through the source's detailed-balance convention, so they are not independent nuisance parameters. The weak normalization scales inversely with sampled tau. Source mc.c uses its own xoshiro256**/SplitMix64 normal generator with seed+sample_index; it does not reproduce NumPy sample values. No prior for Omega_b, cosmological parameters, missing nuclear channels, or EFT truncation is added. In particular this is not a fitted covariance of the native np EFT kernel.

## Observables and connection to existing work

Retain all native CLI samples, then focus analysis on [YPBBN,DoH,He3oH,Li7oH,Be7,Li7]. The last two are abundances per baryon at the BBN endpoint. Native Li7oH=(YLi7+YBe7)/Yp and He3oH=(YHe3+YH3)/Yp already represent combined observable reservoirs; they do not mean those decays were dynamically followed. Also derive Ymass7=Be7+Li7 row by row and its covariance. This algebraic quantity may support a later uncertainty propagation into an explicitly compatible atomic history, but do not attach the small-network covariance to the old large-network donor without a separate network-difference calculation.

For N actual successful samples X_s and mean Xbar,

    C_hat = sum_s (X_s-Xbar)(X_s-Xbar)^T/(N-1),
    R_ij = C_hat_ij/sqrt(C_hat_ii C_hat_jj).

Report units as products of the two observables' units. Recompute from exported samples independently in NumPy and compare to the native covariance/correlation outputs. Source header comments about a population std are stale; the implementation mc.c divides the variance by N−1, consistent with its covariance routine. This contract uses that actual ddof=1 implementation.

Scaled fractional covariance Cfrac_ij=C_ij/(central_i central_j) improves readability and conditioning. Positive semidefiniteness is checked on the correlation matrix of nonzero-variance selected observables. Exact derived identities must be checked row by row, and for the augmented covariance using the linear map Ymass7=YBe7+YLi7; no random covariance matrix is invented.

## Bounded native execution

Build using make -j2 with an independent30s build ceiling; no source repair is permitted if it fails. First obtain one nominal --json solve, timeout5s, and one otherwise-identical numerical_precision=1e-8 solve, timeout5s. Capture actual wall times. Require selected central observables to agree within1e-4 relative; after the ensemble also compare their difference to the ensemble standard deviation and require <=.05 sigma for the six selected observables. This is a resolution check, not proof of full network accuracy. A failed cold-cache/profile solve returns its exact missing file or runtime evidence; do not silently disable corrections to accelerate it.

Next run a native8-sample pilot with --mc-seed20261016 --mc-jobs1 and write samples/covariance/correlation. The CLI performs some repeated central/background setup; use observed pilot wall time t8 rather than a guessed per-sample time. After the pilot choose the largest N in [64,32,16] satisfying 1.5*t8*(N+2)/10 <= remaining numerical budget−2s. If none fits, use the completed8-sample pilot as the result. Run that chosen native command once with a timeout bounded by the remaining budget; do not begin an unbounded ensemble. Total numerical wall budget30s includes profile, tighter solve, pilot and final ensemble. If a larger run times out, preserve its logs and report the valid completed pilot with N=8 and BUDGET_LIMITED; do not call the aborted run successful.

Production and pilot share seed and sample order. Compare the first8 selected-observable rows numerically, relative<=1e-9, as a repeatability check (not a cross-backend identity claim). No repeat or larger ensemble is required after the allowed sequence. The task's useful output is an actual finite-sample covariance under a declared prior, even if only8 samples fit; it must be labeled exploratory and must not be called converged precision uncertainty.

## Sampling uncertainty and acceptance

Report sample means, nominal central values, sample standard deviations, correlations and covariance. Report first-half versus second-half means/stds as sampling diagnostics without forcing agreement. For orientation only, sqrt(2/(N−1)) is the Gaussian approximation to relative sampling error of a variance; it is not an exact uncertainty for these nonlinear outputs. Optionally compute512 deterministic bootstrap resamples of the existing rows, seed20261017, for percentile intervals on standard deviations and correlations, explicitly labeling them finite-sample bootstrap diagnostics. This requires no new BBN solves and may be omitted if the30s budget is exhausted.

All samples must be finite and selected observables positive. Require covariance symmetry in standardized units<=1e-12; correlation diagonal error<=1e-10; min correlation eigenvalue>=−1e-10. Native vs independently recomputed covariance residual is scaled by sqrt(Cii Cjj) and must be<=5e-7, allowing the native exported sample values'10-digit rounding. Selected native correlation agreement<=5e-7. Central precision and repeatability gates are above. Mass-seven row identity absolute<=1e-25+1e-12*|Ymass7| and linear covariance-transform error<=1e-12 in standardized units. A zero selected variance or nonpositive central abundance is a substantive unexpected result: retain it and return to authority; do not divide by zero, drop it silently or add jitter.

PASS→independent review and release of the source-native, small-network, prior-conditioned finite-sample covariance with its sampling limitations. Owner-likelihood precision inference, native-EFT calibration/truncation covariance, original-donor covariance and complete T5 closure remain separate claims with precisely different inputs.
