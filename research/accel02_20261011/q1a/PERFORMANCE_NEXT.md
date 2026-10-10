# Exact block solve as a bounded follow-up to Q1A

**Decision: mathematically applicable to the current assembled Jacobian; implementation and speed benefit unverified.** This note authorizes no change to the three running Q1A jobs, their grids, physics, tolerances, event boundaries, or wall budgets. No RHS, native, ODE, profiling, benchmark or historical-reference calculation was executed for this note. Local source and progress files were read only.

The concrete candidate is to replace the generic sparse factorization of each BDF Newton matrix by exact diagonal-photon elimination and a four-dimensional gas Schur complement. Keep the six ledger counters inside the BDF state, Newton vector, error norm and dense output. This is a linear-solver change, not a new gas approximation or a spectral correction. It cannot repair Q1A quadrature error.

## What the inspected code establishes

`integration/run_native_history.py::Coupled.jac` assembles a Jacobian for the scaled state and normalized proper time,

\[
v=S^{-1}y,\qquad u=t/t_{\rm end},\qquad
J=t_{\rm end}S^{-1}\frac{\partial f}{\partial y}S.
\]

Here the positive diagonal scaling matrix \(S\) is fixed during a run. Gas variables are \((x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w)\). Photon variables are \(U_i=E_iN_i\), with \(E_i\) in eV and \(N_i\) per reference volume. The six counters, in order, are escape energy, expansion work, source energy, absorbed photon number, source photon number, and signed CMB-to-gas energy. Counter units are already converted to dimensionless numerical coordinates by \(S\); do not mix physical and scaled blocks.

For one open event segment, `run_gauss_history.py` retains the four gas variables, the \(m\) active photon coordinates, and all six counters. Dormant photon coordinates remain their exact algebraic zero and are absent from the reduced Newton system. The ordering is therefore gas / active photons / counters, even though \(m\) changes across segments.

The supplied **assembled** Jacobian has the block structure

\[
J=\begin{pmatrix}
A & B & 0\\
C & D & 0\\
F & G & 0
\end{pmatrix},\qquad
A\in\mathbb R^{4\times4},\quad
D=\operatorname{diag}(d_i),\quad
d_i=-t_{\rm end}(\kappa_i+\lambda_i).
\]

The scalar \(\lambda_i=H+s(3\mu_i^2-1)\) is the characteristic energy-loss rate and \(\kappa_i=c_{\rm light}\sum_a n_a\sigma_{ia}\ge0\) is the absorption rate. The diagonal is unaffected by the fixed diagonal state scaling. Each photon couples to the gas but not directly to a different photon. The prescribed source is independent of the evolved photon/gas state; the source spectrum and opacity coefficients depend explicitly on time through the pinned background and current-energy evaluation. All counter columns vanish because counters are integrals and do not feed back into any RHS component.

This structure is exact for the inspected matrix construction. It does **not** claim that its four finite-difference gas columns are exact analytic derivatives of the physical RHS: the proposed solver must consume those existing columns without changing their differencing or threshold conventions. Native source code independently confirms that counters are not RHS inputs.

The last block rows must be preserved in full. The work counter has gas thermal-expansion and photon contributions; absorbed number depends on gas opacity and photon populations; cooling/escape and signed CMB exchange depend on gas state. Source-energy/source-number derivatives with respect to state vanish for the current prescribed source, but a generic wrapper should retain the actual supplied blocks rather than hardcode those individual rows to zero.

## Exact elimination of the supplied Newton matrix

The installed SciPy BDF forms \(M=I-\eta J\), where \(\eta=h_u/\alpha_k\); \(h_u\) is a normalized-time step and \(\alpha_k\) is its BDF/NDF coefficient. The notation \(\eta\) avoids confusion with the speed of light. Both \(J\) and \(M\) are dimensionless in the coordinates above. Define

\[
P=I_m-\eta D,
\qquad K=I_4-\eta A-\eta^2BP^{-1}C.
\]

For an arbitrary Newton right-hand side \(b=(b_g,b_p,b_c)\), the solution is

\[
\begin{aligned}
K\,\delta g &= b_g+\eta BP^{-1}b_p,\\
\delta p &=P^{-1}(b_p+\eta C\delta g),\\
\delta c &=b_c+\eta F\delta g+\eta G\delta p.
\end{aligned}
\]

Substituting the second line into the gas row gives the first; substituting both into the counter row gives the third. These solve exactly the same block equations as sparse LU in exact arithmetic. The six counter identities need no factorization, but their solution increments must not be omitted. The zero-photon case reduces to a four-dimensional gas solve followed by the six counter updates.

For the current forward FLRW runs, \(\eta>0\), \(H>0\), \(s=0\), and valid abundances give

\[
P_{ii}=1+\eta t_{\rm end}(\kappa_i+H)\ge1.
\]

Thus photon elimination introduces no small diagonal denominator in this scope. The gas Schur matrix \(K\), however, is generally nonsymmetric and can be ill-conditioned; use a pivoted dense LU, never Cholesky or an explicitly formed inverse. In a future background with nonpositive \(\lambda_i\), the positivity argument must be reconsidered. A future redistribution/scattering/re-emission closure may make \(D\) nondiagonal or counters feed back; reject such matrices rather than silently dropping their couplings.

Construction of \(BP^{-1}C\) costs \(O(16m)\), and diagonal application, gas/photon recovery and six-counter recovery all cost \(O(m)\), with a constant-size gas factorization. Storage is linear in \(m\). This gives a predictable exact block implementation, **not** proof of an asymptotic advantage over the present sparse solver: a good sparse ordering can already exploit the same arrowhead structure. Eliminating a dense gas block first would create photon fill, but no inspection or timing here establishes that the current SuperLU ordering does so.

## SciPy integration boundary and safeguards

Installed SciPy **1.17.0**, `scipy/integrate/_ivp/bdf.py`, uses `splu(M)` for sparse Jacobians and `LU.solve(b)` through instance attributes `lu` and `solve_lu`. `_step_impl` invokes `self.lu(self.I - eta * J)` and reuses that factor object according to its existing Jacobian/Newton/step logic. The source even retains an existing factor on one error-rejection path. A wrapper must factor the **actual matrix passed to `lu`** and preserve that exact reuse policy. It must not reconstruct a different matrix from the currently visible step size or assume that every Newton solve has a newly formed Jacobian.

A minimal future prototype should therefore extract blocks directly from the supplied sparse \(M\), rather than initially changing the Jacobian builder. With blocks \(M_{gg},M_{gp},M_{pg},P,M_{cg},M_{cp}\), use

\[
K=M_{gg}-M_{gp}P^{-1}M_{pg},\qquad
K\delta g=b_g-M_{gp}P^{-1}b_p,
\]
\[
\delta p=P^{-1}(b_p-M_{pg}\delta g),\qquad
\delta c=b_c-M_{cg}\delta g-M_{cp}\delta p.
\]

This form naturally preserves the original signs and stale-factor semantics. Check the numerical off-diagonal photon block and all counter columns, including the counter identity block, before accepting the structure; sparse stored zeros are not nonzero couplings. Check dimensions against the current segment's active-node count, finiteness, diagonal invertibility and pivot success. A structural or conditioning failure must be explicit and preserved; any fallback to ordinary sparse LU must be recorded. No unrecorded epsilon diagonal, damping, dropped entries, clipping or altered Newton tolerance is allowed.

The `lu`/`solve_lu` hooks are inspected implementation details, not a stable advertised solver API. Pin the SciPy version and source SHA, use an isolated adapter or subclass, and do not monkeypatch process-global SciPy behavior. Preserve `nlu` accounting, factor reuse, all BDF norms, order/step decisions, dense interpolation, active-set restarts and accepted-state gates. The initial adapter can keep the existing CSC matrix allocation; a later allocation optimization would be a separate change after equivalence has been established.

## Required evidence before a solver change is adopted

1. **Independent linear-system equivalence.** Capture the exact scaled \(M\), active-node map and one or more Newton right-hand sides at a bounded selection of new-run states. Preserve early neutral gas, rapid ionization, late ionized gas, representative pre/post-support-entry segments, and the legal no-active-node structural case. On the *same saved matrices*, compare block solve to `splu(M).solve(b)`. Add deterministic generic RHS vectors so counter and gas couplings are actually exercised. This is linear algebra, not a replay of RUN002/EVENT003/Q0.
2. **Residual and conditioning checks.** Record \(\|M\delta-b\|_\infty/(\|M\|_\infty\|\delta\|_\infty+\|b\|_\infty)\), a row-scaled/componentwise residual with exact-zero denominator semantics, \(\operatorname{cond}(K)\), minimum \(|P_{ii}|\), and the gas/photon/counter difference from sparse LU. Well-conditioned binary64 cases should have near-roundoff residuals; prospectively fix their numerical tolerance with the independent reviewer. A conditioning-amplified forward difference is not automatically an implementation error, and a small aggregate residual alone does not validate all six counters. Preserve singular, nonfinite, non-arrowhead and wrong-dimension rejection cases.
3. **Same-discretization bounded equivalence.** Only after the linear solves pass, run a newly identified fixed-grid candidate through the unchanged whole \(z=15.9\to4\) interval and compare against the matching ordinary-LU result. Different roundoff can change BDF step counts, so require the existing scientific/time gates rather than identical trajectories. Keep energy/number \(10^{-9}\), temporal nine-field \(2\times10^{-6}\), geometry \(10^{-11}\), positivity/domain gates, and existing spectral \(10^{-3}\) criteria unchanged. Linear-solver agreement cannot override an unresolved spectral failure.
4. **Measured cost attribution.** Record segment totals for Jacobian builds, factorizations, linear solves, Newton iterations, accepted/rejected steps, native RHS calls and time spent in each category on future controlled runs. Include native text serialization/IPC and sparse matrix construction. Compare on the same grid, environment, concurrency setting and solver controls; separate startup/event-restart costs from matrix-solve costs. These counters/timings are currently missing, so a speedup claim is premature.

Stop after this bounded equivalence experiment if the structured solve does not improve measured wall time or memory sufficiently. Native stage evaluations, repeated cross sections, text IPC and frequent BDF restarts remain plausible costs; the block solve removes none of those. The existing four finite-difference gas columns also require multiple native RHS evaluations per Jacobian and remain unchanged by this proposal.

## Read-only progress snapshot and provenance

Observed **2026-10-10 23:21:54 UTC / 2026-10-11 08:21:54 KST**. These are in-progress snapshots under concurrent execution, not controlled performance measurements or final results.

| New run | Finished segments | Normalized time | Mean redshift | Reported RHS calls | Elapsed seconds |
|---|---:|---:|---:|---:|---:|
| GAUSS1_FINE | 200 / 388 | 0.3084948979501068 | 7.928884897687336 | 292937 | 1309.0426898860023 |
| GAUSS2_FINE | 87 / 750 | 0.06472963548862215 | 12.929433468967055 | 150115 | 1291.9647717909975 |
| GAUSS1_TIGHT | 176 / 388 | 0.2471960117942578 | 8.741423446171511 | 288590 | 1300.1865786840062 |

The enriched grid has more nodes and more event restarts; the snapshots do not separate these effects from concurrency, nonlinear iteration count or factorization cost. Linear extrapolation in normalized cosmic time is especially unreliable because event density and ionization stiffness are nonuniform. No completion-time or measured speedup is inferred here.

Inspected source identities:

- `integration/run_native_history.py`: `06275b5dd45e9e2b67264a8265c60d83966539093797748aa99e0a5ea5985602`.
- `q1a/run_gauss_history.py`: `9cbae11904e569dac47498dc5a4795f3aef8d55e5f32addf4c79a3608b815f61`.
- `n1/native/src/main.rs`: `239a08b0fdbe171f21112c128602be3ad9bbaae596ada1b6791fda482e8aeb76`.
- Installed SciPy 1.17.0 `bdf.py`: `a5b75a2ae8aca2e66cc35ed268af51d8a9685878209d5cf77a44c8ccef3b76e6`.
- Snapshot `GAUSS1_FINE/PROGRESS.json`: `29d53aaa67f5614d04ce3ad68d968b1e5709781ccfe639ad470e62b7d4a4b784`.
- Snapshot `GAUSS2_FINE/PROGRESS.json`: `2e902ce35ee71bf01fe3ffea67404486db96db4f3490f7bd4ff5782347924f3c`.
- Snapshot `GAUSS1_TIGHT/PROGRESS.json`: `844ade9a1ed51898640860f1c70efc3db308d48eb4fe141cf31bb26c186ead7e`.

Progress files naturally continue to change. The values above are the recorded read-only snapshot, not identities asserted for later versions. Final classification: **derived** block equivalence; **source-inspected** current Jacobian/BDF compatibility; **unresolved** numerical conditioning, implementation equivalence and performance benefit. No candidate solver has been implemented or executed.
