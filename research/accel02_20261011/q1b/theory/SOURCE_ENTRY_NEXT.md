# Q1B next algorithm: conservative finite-step source entry

Status: **a concrete implementation proposal, not a production implementation or scientific admission**. This note follows the corrected local reconstruction and its explicit `FLOAT_Q_COORDINATE_UNRESOLVED` behavior. The generic physical-q callback guard remains unchanged. All protected physics, providers and full-history criteria remain unchanged. No old run, new ODE, native call or additional literature search is performed by this note.

The immediate target is narrower than a complete time integrator: enter a previously empty cell without a photon floor, artificial seed, ordinary Jacobian at the origin or unresolved subcell arithmetic. The same positive absorption map could later become a complete first-order baseline, but runtime competitiveness has not been measured. Existing local ABI success does not supply a new history, N/U Jacobian or domain-preserving nonlinear solver.

## 1. Decision

Implement one **event-aligned, conservative positive entry step**:

1. Locate a true source-band birth event for a dormant fixed-q cell.
2. Integrate its real source number, q moment and injected energy over a finite trial step, jointly with photon redshift.
3. At the trial endpoint reconstruct the positive incident distribution from those moments on the actual reachable support.
4. Apply a positive implicit absorption map, coupled to the unchanged native gas RHS through the same species-resolved number/energy integrals.
5. Accept only a realizable, residual-converged step whose error estimate and arithmetic-resolution checks pass; record all source, absorption and work counters from their actual operators.

There is no evaluation of a mean q or reconstruction Jacobian at zero. The endpoint state is produced by an integration of the physical source, not by selecting a small N. An unsuccessful trial is rejected without changing stored state. An unresolved source-entry step is a numerical blocker, not permission to lower a physical tolerance.

This is explicitly a first-order split time-discretization candidate. It is not claimed equivalent at finite step size to the prospective fully implicit continuous-moment ODE. It has that ODE's first-order local limit under smoothness and an interior moment state. This consistency claim must be checked separately at the singular birth boundary; the source-entry exact fixtures below are part of that check.

## 2. Why source entry and coordinate evaluation are different problems

The repaired reconstruction solves for the dimensionless power-law shape using a cell-relative mean. That fixes one cancellation. It does not recover information lost when an arbitrary kernel is given rounded binary64 physical q. For example, `(q-a)/(b-a)` amplifies a q ulp by the inverse cell width. A 64/128 order agreement can therefore be a false certificate, which is why the present generic API fails closed for unresolved widths.

An explicit coordinate kernel could instead receive

\[
x=\ln(q/a),\quad L=\ln(b/a),\quad
\xi={\operatorname{expm1}(x)\over\operatorname{expm1}(L)},
\quad q=a+(b-a)\xi.
\]

The test kernel ξ can then be evaluated without recovering it from rounded q. For native H/He cross sections, above and away from thresholds, smoothness allows a **provider-specific value condition estimate**, for example a verified bound on \(|d\ln\sigma/d\ln E|\). It is not an arbitrary-kernel bound. A narrow physical-energy interval does not by itself cause a large relative σ error, even though it can destroy a covariance derivative obtained by subtraction.

However, a coordinate callback alone does not restore the subcell mean if that mean was already lost in the stored binary64 pair N,U. Nor does it create a Fréchet derivative at the empty origin. Its complete version would need: accurately retained moment offsets, robust threshold-side comparisons, the same native formula evaluated with certified arguments/traces, and a derivative contract. It is therefore a separate binding task rather than an excuse to remove the current guard.

The first birth of a new high-q cell occurs at Emax=50 keV, far above the H/He thresholds. That fact makes a bounded smooth-native startup plausible; it is not a numerical bound until the pinned native formulas are evaluated and their interval conditioning is checked. Ordinary threshold crossings later in a populated cell remain distinct events.

## 3. Source plus redshift substep: exact moment targets

Use a trial interval [t0,t1], h=t1−t0>0. R, λ and V come from the same pinned background map. For each cell, integrate

\[
\Delta N_s=\int_{t_0}^{t_1}S_0(t)\,dt,\quad
\Delta Q_s=\int_{t_0}^{t_1}S_1(t)\,dt,\quad
\Delta E_s=\epsilon_{\rm eV}\int_{t_0}^{t_1}R(t)S_1(t)\,dt.
\]

S0/S1 are the exact declared cell-source moments already specified by Q1B. Split the time integral at genuine source/provider/geometry events; use positive time quadrature and evaluate all three moments on the same nodes. The time integral is new work, not a replay of the saved Q0 references. The declared interpolation's cell integration and this new time integration have separate error budgets.

Form

\[
N_*=N_0+\Delta N_s,\quad Q_*=Q_0+\Delta Q_s,\quad U_*=R_1Q_*.
\]

The radiation work during this substep is the physical expansion integral. An equivalent useful formula is

\[
W_A=\epsilon_{\rm eV}\left[(R_0-R_1)Q_0+
\int_{t_0}^{t_1}(R(t)-R_1)S_1(t)\,dt\right].
\]

It follows directly by integrating \(\lambda RQ\) while Q receives S1. It is not an a posteriori residual assigned to close a ledger. Evaluate its integrand with the same positive time rule and stable background differences; then separately check
\(U_*\epsilon_{\rm eV}-U_0\epsilon_{\rm eV}+W_A-\Delta E_s=0\).

No absorption is applied in this substep. Its delay to the following implicit substep is part of the explicit first-order splitting error. Retain photons below 10 eV. Restrict the photon support by the monotone reachable cap, not by the current lower source boundary.

At a smooth birth, the integrated moments satisfy
\(N_*=A_0\lambda_0h^2/2+O(h^3)\) and
\(Q_*/N_*=a+(b_1-a)/3+O(h^2)\).
Use the **integrated** moments directly. The 1/3 formula is a fixture and a limiting diagnostic, not an imposed mean or an approximate seed. If source power is exactly zero over the step, the state remains exactly empty.

## 4. Positive implicit absorption with four gas unknowns

For N*>0 and an admitted endpoint support [a,b1], reconstruct the incident power law \(F_*\) with moments N*,Q*. For a trial endpoint gas state y=(xHII,xHeII,xHeIII,w), let

\[
\kappa(q;y)=c\sum_\alpha n_\alpha(y,t_1)
\sigma_\alpha(R_1q),\qquad
F_+(q;y)={F_*(q)\over1+h\kappa(q;y)}.
\]

Every admissible gas state has κ≥0, hence F+≥0 with unchanged support. Integrate F+ to obtain N+,Q+ and U+=R1Q+. The common absorption integrals are

\[
K_{0\alpha}=c\int\sigma_\alpha(R_1q)F_+\,d\ln q,
\quad K_{E\alpha}=c\int R_1q\sigma_\alpha(R_1q)F_+\,d\ln q.
\]

Each species receives exactly h nα K0 photo-events per reference volume and
\(h\epsilon_{\rm eV}n_\alpha(K_{E\alpha}-\chi_\alpha K_{0\alpha})\)
heat. Gas photo-inputs are the same Γ=ΣK0/V1 and heat/V1 used in the integrated native ABI. Solve only the four endpoint gas equations

\[
y-y_0-h\,f_{\rm gas}(t_1,y;K_0(y),K_E(y))=0
\]

with the unchanged native gas microphysics. Expansion, non-photo cooling, recombination, escape and CMB terms enter through that native owner. The solver must use a demonstrated gas-domain-respecting line search/active-set strategy and a residual acceptance check; merely calling a generic Newton routine is insufficient. Failure to find an admissible residual-converged state rejects the trial. There is no projection or clipping of gas fractions.

Crucially, the photon state is a positive integral functional of the gas trial, not an independently guessed N/U Newton stage. The derivative with respect to a gas unknown yj is

\[
\partial_{y_j}F_+=-{hF_*\partial_{y_j}\kappa\over(1+h\kappa)^2},
\]

plus the native gas derivatives. It does not invoke the undefined photon reconstruction derivative at N=0. At fixed trial source/background, F* is held fixed during this gas solve. The empty F*=0 case gives zero photo-input and zero photo-input derivatives exactly.

After the absorption map, retain only the resulting N+,U+ moments and reconstruct their power law at the next step. This re-compression is the declared numerical closure. It is not claimed that energy-dependent attenuation preserves a power law. Fixed-support grey attenuation is the appropriate exact closure-preserving fixture.

### Moment-exact positive quadrature is a necessary part of this proposal

A positive quadrature for F* alone is not enough: if its first moment differs from Q*, summing its absorbed and surviving photons would close around the quadrature approximation instead of the stored energy. The step must first produce positive weights Pi with

\[
\sum_iP_i=N_*,\qquad \sum_i q_iP_i=Q_*.
\]

One implementable bounded option is a positive exponential reweighting of a sufficiently resolved provisional quadrature in ξ:
\(P_i=N_*w_i e^{\eta\xi_i}/\sum_jw_j e^{\eta\xi_j}\), choosing η to match the stored cell-relative first moment. This requires the target mean to lie strictly inside the node convex hull. If it does not, reject or select an explicitly declared richer quadrature; never shift the target mean. Record the reweighting and independently compare the resulting native moments at the predetermined order pair. This is a new moment-fitting implementation, not something already proven by the current covariance tests.

Using these same Pi and native opacities, set
\(P_i^+=P_i/(1+h\kappa_i)\) and
\(A_{\alpha i}=h n_\alpha c\sigma_{\alpha i}P_i^+\).
Then pointwise \(P_i=P_i^++\sum_\alpha A_{\alpha i}\). The same q_i gives number, photon energy, species gain and heat pairing. Compute the ratios without an overflow or catastrophic subtraction; reject unresolved arithmetic. Moment-fitting residuals and all accumulated ledger residuals remain explicit checks, not hidden fixes.

The ABI must expose or separately identify thermal work and radiation work. The photon redshift work was already integrated in substep A; it must not be counted again by integrating the combined work output of `CELL_RHS_V1` over substep B. A versioned split-output adapter may reuse the same owners, but it must pass new pairing tests before use. Escape and CMB counters in substep B use the same converged endpoint native state.

## 5. Trial-step selection and narrow support

Event alignment does not mean marching through infinitely small supports. The first reconstruction is requested at t1, after a finite amount of real source has been integrated. There is no reconstruction request at intervening source-integration quadrature nodes. Choose h by physical temporal error and stiffness, and also require the endpoint to be arithmetically resolvable for every requested calculation.

For the **first implementation**, keep the current generic coordinate admission indicator and require it to pass for h, h/2 and h/4 entry trials. Thus the step-doubling test cannot hide an unresolved subtrial. Do not pick h only from the geometric width, and do not report success from an asymptotic prediction of the answer.

If the largest step allowed by the temporal/stiffness criterion is smaller than the minimum resolvable step, report `ENTRY_PRECISION_TIME_BUDGET_CONFLICT`. The next justified action is a native-specific coordinate/precision adapter, not a photon floor, delayed activation or a larger step that fails error control.

Such an adapter would retain a compensated/high-precision offset
\(D=Q-aN\) or an equivalent two-component representation of N/U during the local step, evaluate coordinate moments without subtracting rounded physical energies, and return a consistent N/U result with a rounding budget. D must be derived from and reconciled with the authoritative moment state; a new silently independent state variable is inadmissible. A checkpoint must include any authoritative low components. The physical state is still N/U; the precision representation is additional explicit metadata and arithmetic, not an extra physical degree of freedom.

For the native kernel, retain each threshold side explicitly and split there. Smooth-value conditioning can support a native-specific allowance beyond the arbitrary-q guard only after an independent bound/check; it does not authorize a covariance Jacobian from unresolved differences. If an endpoint coincides with a threshold, use the explicit interior trace contract. A scalar `nextafter` call alone does not establish that trace. Source entry at 50 keV and a later atomic-threshold crossing must not be conflated.

## 6. Bounded local tests and error budget

No long history should begin before these new, focused tests close:

| Test | Required meaning |
|---|---|
| Source-only expanding birth | Recover exact integrated N/Q and the 1/3 limiting mean; no instantaneous-source midpoint seed; zero source remains zero |
| Fixed/full support grey absorption | Verify the backward-Euler attenuation factor and paired counters, including stiff hκ≫1; distinguish it from exact exponential attenuation |
| Smooth-entry grey source+absorption | Use the analytic source-birth integral with exponential survival as a reference; show the proposed entry scheme's first-order error and step rejection behavior |
| Constant/affine coordinate kernels | Verify moment fitting, positive weights and common number/energy identities independently of the power-law oracle |
| Actual native 50-keV entry | Check HI/HeI/HeII paired rates, smooth-value conditioning, gas-domain handling and the predetermined integration-order comparison |
| Threshold trace cases | Verify lower/upper side and reject unverified equality-branch substitutions |
| h, h/2, h/4 entry trials | Compare the same final time; establish expected convergence without allowing an unresolved subtrial |
| Counter and restart test | Save after entry, restore N/U, gas, counters, support/precision identity and history, then compare to an uninterrupted new manufactured case |

Use separate budgets for source-time quadrature, opacity quadrature/moment fitting, nonlinear residual, precision loss and time splitting. They must be set prospectively in the implementation contract using the same absolute/scaled units as the affected quantities. Do not spend the entire global 10⁻⁹ ledger allowance on one local quadrature or normalization change. A count-based allocation over an unknown number of future steps is not a demonstrated global bound; record actual accumulated residuals as well.

The existing local source target and native/reconstruction local comparisons remain additional engineering gates. None replaces the full redshift 15.9→4 validation, nine-field 2×10⁻⁶ temporal test, 24-field 10⁻³ spectral test on separate 65/129 epoch sets, 10⁻⁹ ledgers, 10⁻¹¹ geometry or strict domains. A first-order entry rule must prove that its contribution is controlled within the eventual temporal comparison; conservation alone cannot certify it.

For an independent grey-birth reference, take a constant comoving source density A on \(a\le q\le ae^{\lambda t}\), constant λ>0, constant grey absorption κ>0 and an initially empty cell. Its exact moments are
\[
N(t)=A\lambda{\kappa t-1+e^{-\kappa t}\over\kappa^2},
\quad Q(t)=Aa\left[{e^{\lambda t}-e^{-\kappa t}\over\kappa+\lambda}
-{1-e^{-\kappa t}\over\kappa}\right].
\]
The proposed grey step reduces to
\(N_{j+1}=(N_j+\Delta N_{s,j})/(1+h\kappa)\) and
\(Q_{j+1}=(Q_j+\Delta Q_{s,j})/(1+h\kappa)\).
`SOURCE_ENTRY_ALGORITHM_DECISION.json` records a standard-library Decimal evaluation of this new scalar recurrence against those exact expressions at a common final time. This is an analytic manufactured check of the proposed time map, not a coupled physical ODE, native binding or production-code test.

## 7. Concrete implementation boundary

The next bounded code unit is `SOURCE_ENTRY_POSITIVE_STEP_V1`: provider-bound temporal source moments; physical radiation-work integral; endpoint incident reconstruction; moment-exact positive quadrature; implicit absorption functional; four-variable native gas residual; explicit trial rejection; and a structured result containing all moments, counters, numerical errors and source/native/background identities. It should run only the focused tests above initially.

The interior-history backend, native endpoint traces, precision-conflict adapter, complete new Jacobian strategy and full scientific admission remain separate obligations. This proposal resolves the algorithm choice for a local implementation attempt; it does not assert those obligations are closed. If the bounded entry attempt fails, preserve its first failure and diagnose that new failure rather than replaying completed RUN002, EVENT003, Q0 or Q1A histories.
