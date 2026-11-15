# AXBI saved-history stress/energy diagnostic: independent review

**Verdict: accepted within the four-case frozen-background diagnostic scope.**
No unresolved factor, sign, angular-measure, unit-conversion, or target-normalization defect was found in the final implementation. The full-source result is `axbi_science/results/FULL_SUMMARY.json`; the earlier `SUMMARY.json` is explicitly a reduced-input background-only result. This is a quantitative approximation diagnostic for the AX03/AX08 obligation, not AX10 optional-observable completion or full parent-node admission.

The reviewer is a separately spawned agent with no inherited parent conversation. The derivation below and numerical implementation in `axbi_independent_checks.py` were developed by this reviewer. Shared source data and NumPy's Legendre-node implementation prevent a claim of total software independence. The adaptive 50-digit mpmath angular reference and the direct proper-time long-double trapezoidal sum are distinct from the production local-angle/SciPy Simpson calculation. Only the native `SHEAR_MINUS` history was numerically reprocessed independently; the other three full-history outputs were read and code-reviewed, not independently rerun.

## Independent derivation

With signature `(-,+,+,+)`, let the directional scale factors be
`a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, and `s=db/dt`. Then
`H_perp=H-s`, `H_parallel=H+2s`, with proper time in seconds.
The spatial Ricci difference is

\[
R^z{}_z-R^x{}_x
=\frac{\dot H_\parallel-\dot H_\perp+3H(H_\parallel-H_\perp)}{c^2}
=\frac{3(\dot s+3Hs)}{c^2}.
\]

The Einstein trace term cancels in this difference. Since the pressure components have energy-density units,

\[
\dot s+3Hs=\frac{8\pi G}{3c^2}(P_\parallel-P_\perp).
\]

Thus the production factor `8πG/(3c²)` and sign are correct. For `delta_s(t_i)=0`, holding the saved background fixed gives

\[
\delta s(t)=a^{-3}(t)\int_{t_i}^{t}a^3(t')\frac{8\pi G}{3c^2}\Delta P(t')\,dt'.
\]

The coupling times pressure has units `s^-2`; the integral before multiplication by `a^-3` has units `s^-1`. Converting `dt=d ln a/H` gives precisely the production integrand. This prescribed-forcing calculation omits the `3s delta_H` and changed-distribution terms of a coupled linearized Einstein–matter calculation; its numerical value is not a coupled-trajectory error estimate.

For conserved initial momentum direction `v`, define

\[
R^2=e^{2b}(1-v^2)+e^{-4b}v^2,\qquad
\mu=e^{-2b}v/R.
\]

The initial isotropy condition is imposed at `a_i=1/21, b_i=0`. The local-angle factor is
`D=e^{-2b}(1-mu²)+e^{4b}mu²=R^-2`, and differentiating the direction map gives `dmu/dv=R^-3`. Consequently,

\[
M=\tfrac12\int_{-1}^{1}D^{-2}d\mu
=\tfrac12\int_{-1}^{1}R\,dv,\qquad
F=\tfrac12\int_{-1}^{1}P_2(\mu)D^{-2}d\mu
=\tfrac12\int_{-1}^{1}R P_2(\mu)\,dv.
\]

Uniform measure belongs to the corresponding integration direction; no additional conserved-momentum weight belongs in the local-angle formula. The pressure combination is `DeltaP=u_ref F`, since `mu²-(1-mu²)/2=P2(mu)`. There is no factor 5 in this moment convention.

The identity `dR/db=-2R P2(mu)` implies `M'=-2F`. With `sigma=diag(-s,-s,2s)` and `pi=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3)`, the work term is `sigma:pi=2s DeltaP`. Therefore `dot u+4Hu+2s DeltaP=0`, consistent with both measures and the pressure sign. Near isotropy, `F=-(8/5)b+O(b²)` and `M=1+(8/5)b²+O(b³)`, so positive accumulated `b` produces negative stress.

The production subtraction `F=<P2(D^-2-1)>` is an exact continuum identity because `<P2>=0`. It enforces zero background stress at isotropy without removing any physical quadrupole. The nonzero `ZERO` ionizing-source residue (`max |delta_s/H|=3.78e-23`) remains in the full result instead of being silently subtracted.

## Original source convention and energy comparator

The source `axbi_driver.rs::moments` computes `u=stock_per_H*E_eV`, then `moments[2]+=u*(3mu²-1)/2` using the evolved local direction. The history writer exports this value under `J2_photon_u_eV_per_H`. Angular weights are already in the photon stocks. The conversion
`DeltaP_ion=nH_cm^-3 * 1e6 * J2_eV/H * 1.602176634e-19`
therefore has units `J/m³` and is correct. `J0` equals the separately emitted photon-energy inventory exactly in the independently inspected native history.

The local `geometry_solver/private/source_identity.txt` was inspected directly. Its first source component has SHA-256 `a614725c153ee21d88554573c15801087d8fb412954fa51d67b781f671475dbf`, matching the original driver component recorded in `POST_PLUS_RECEIPT.json`. The background component hash is `65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254`. The entire concatenated local source identity has a different hash from the original history manifest; only component identity is asserted here.

For the isotropic ideal gas in this conditional model,
`u_th=(3/2)k_B T(n_H+n_He+n_e)` and `n_He/n_H=Y_He/[4(1-Y_He)]`. Thermal energy contributes to the energy diagnostic, not an invented gas anisotropic stress.

One substantive review correction was applied: the source-defined energy comparator uses

\[
\frac{u_{\rm ion}+u_{\rm th}+|u_{\rm ref}(M-1)|}
 {3H_{\rm FLRW}^2c^2/(8\pi G)},
\]

whereas `3H²c²/(8πG)` includes the shear contribution. The final consumer matches the former exactly and retains the latter only as a separately named ratio. Including the nonnegative background-energy correction is a stricter version of the scenario's ionizing-plus-thermal comparison. The original `1e-4` threshold is unchanged. The source already contained instantaneous radiation/ionizing feedback and an integration helper; the new result is the reconstructed full saved-history consumption and extrema, not a new stress theorem or first implementation of that physics.

## Executed checks and result

Current-turn execution established `PYTHON_PASS`: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3. No C++ availability claim is made. The reviewer ran the final 10-test unit suite once: all 10 succeeded, including native fixed-decimal round-trip parsing. The author preserved the preceding parser failure and repair in `FAILURE_REPAIR.json`; neither source data nor acceptance tolerance was changed.

Five adaptive mpmath angular checks covering `-0.01 <= b <= 0.01` agree with production GL16 to at most `2.23e-16` in `M` and `2.61e-17` in `F`. This range contains the represented histories. The independent native `SHEAR_MINUS` read verified its exact hash `0c1d2479eebef9b1ec2d4ff56417ee3395ecd122c17326d4a8d827e2ead76d11`, 312,238 rows, increasing scale factor/proper time, the inventory identity, and the locked Hubble constraint.

| Quantity, `q=-0.01` | Final production | Independent proper-time check |
| --- | ---: | ---: |
| max absolute total `delta_s/H` | 1.0210497766163151e-5 | 1.0210497766173791e-5 |
| max absolute background `delta_s/H` | 1.0210497755358002e-5 | 1.0210497755368654e-5 |
| max absolute ionizing `delta_s/H` | 1.2590645208915413e-13 | 1.2590645217516943e-13 |
| max source-defined extra-energy ratio | 9.728861295902034e-8 | 9.728861295902034e-8 |

The total-shear difference is `1.0641e-17`; both methods locate the stored-node maximum at `zbar=4.874646834963898`. These comparisons are numerical evidence, not interval enclosures. The full-production source reports the other nonzero-case total maxima as `5.080535497518622e-6` (`q=+0.005`) and `5.097074341612322e-6` (`q=-0.005`). All four represented cases lie below the declared shear and energy thresholds.

The reduced 501/1001/2001-grid checks assess only the reconstructed diagnostic quadrature. Native proper-time versus log-scale-factor integration checks the change of variable, while this review's trapezoid versus production Simpson additionally checks quadrature choice. Neither certifies the saved source's energy/angular/time convergence. Stored-node maxima are not certified continuous suprema. The full-history result supersedes the reduced-grid maxima for the represented cases.

## Claim boundary and disposition

- **Derived and numerically checked:** stress factor/sign, moment measure, isotropic subtraction, source `J2` mapping, SI conversions, frozen forcing, and threshold comparison for the four represented histories.
- **Implementation-verified within the stated test scope:** source-pinned full consumer logic, 10 unit tests, and the independent native `SHEAR_MINUS` check.
- **Unresolved:** the missing complete `q=+0.01` history, original evolution convergence (AX11), robustness work (AX12), and any coupled abundance/temperature response or error bound.
- **Conditional assumption:** the entire effective `Omega_r` inventory is massless, collisionless, and initially isotropic at `zbar=20`. This is not a rigorous universal envelope over massive-neutrino histories, collisions, or other initial anisotropies.
- **Decision:** these results support retaining the declared background for the existing exploratory comparison under its diagnostic criterion. They do not establish physical accuracy of a small paired abundance difference. The maximum correction relative to the prescribed shear is about `0.8714%`, which must not be confused with the smaller correction relative to H.

No canonical DAG counter change or parent-node completion is authorized by this review. Source histories remain preserved conditional-model outputs rather than converged cosmological evolution. Reviewed-file hashes and machine-readable disposition are in `AXBI_REVIEW.json`; executable independent evidence is in `AXBI_INDEPENDENT_NUMERICS.json` and `axbi_independent_checks.py`.
