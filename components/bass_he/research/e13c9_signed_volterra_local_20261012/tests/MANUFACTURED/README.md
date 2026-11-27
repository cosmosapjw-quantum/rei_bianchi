# E13C9 independent manufactured controls

## Actual result

`EXEC01/RECEIPT.json` records `PASS_MANUFACTURED_CLOSED_FORM_CONTROLS`:

- Nine manufactured cases at M8 and M32: 18 executions.
- All 3,686 recorded checks passed; no failure or retry occurred.
- Wall time 1.379927 s; process CPU time 1.378837 s.
- 720 calls to an artificial constant-coefficient protocol, covering 360 cells.
- Captured physical coefficient evaluations, inherited baseline reruns, ODE solves, full-population inferences, and NCP launches: all zero.
- Tested candidate SHA-256: `5f20e1b5b0f4936f7bd443d19c7181fd2c7de9de762fe2fa3e9be98f8963cfc5`. The candidate file hash matched before and after execution.
- Detailed result SHA-256: `ace368adca94b7fb8df530e3c85d27bf9aa0c59a6f761068beb3056a7d02b5ed`.

The candidate was imported after the original `Context` source-lock validation. The controls did not modify the candidate or restored scientific sources. The root's representation-grouping repair had already been applied to this tested candidate; the exercised prefix, field, and remainder routines were unchanged by that repair.

## Independent oracle

Let all manufactured frozen coefficients be constant, with total frozen opacity L, individual defects d_i, total defect d = sum(d_i), source defect b = Delta q, and initial correction c. All supplied constants are exact rational numbers. The prescribed energy is E(u) = E0 exp(-u). The actual total opacity L+d and actual source qf+b remain nonnegative.

For L > 0 define

\[
\alpha=\frac{b-dq_f/L}{L},\qquad
\beta=c-\alpha,\qquad
\gamma=-d(f_0-q_f/L).
\]

The exact first-Volterra prefix is

\[
\delta_1(u)=\alpha+(\beta+\gamma u)e^{-Lu}.
\]

For L = 0 it is the polynomial

\[
\delta_1(u)=c+(b-df_0)u-\frac{dq_f}{2}u^2.
\]

The oracle evaluates these closed forms using a separately authored, 140-digit directed Decimal interval evaluator. Candidate computation uses its inherited 60-digit interval arithmetic. The oracle does not call candidate `fields`, `prefix_and_correction`, numerical quadrature, or an ODE integrator to construct a target value.

The closed forms give at most one stationary point for a prefix on each segment. Its location is calculated with exact `Fraction` arithmetic. The oracle encloses each cell's **entire prefix range** by evaluating its endpoints and any interior stationary point. It then checks that this range fits in the candidate whole-cell enclosure. These are whole-range checks, rather than a finite sampling test. Left and right prefix endpoints are checked separately.

For the signed correction define

\[
I_0=\int_0^h\delta_1(u)\,du,\quad
I_E=\int_0^h E(u)\delta_1(u)\,du,\quad
C=\int_0^h e^{-L(h-u)}\delta_1(u)\,du.
\]

All three have elementary exponential-polynomial antiderivatives, implemented directly. Their integrated response kernels are

\[
Q_0=\frac{I_0-C}{L},\quad
Q_E=\frac{I_E-E(h)C}{L+1},
\]

with the exact polynomial integral used for Q0 when L = 0. The signed target vector follows independently:

\[
P_2=-dC,\quad Z_2=-dQ_E,\quad
A_{2,i}=d_i I_0-\lambda_{f,i}dQ_0,\quad
B_{2,i}=d_i I_E-\lambda_{f,i}dQ_E,\quad
H_{2,i}=B_{2,i}-\chi_iA_{2,i}.
\]

QN and QE have zero second correction. The oracle constructs P energy, total A/B/H, and all individual species quantities. All 17 signed target intervals were contained by the candidate at both resolutions for every case.

## Cases

| Case | Principal property tested |
|---|---|
| Exact zero | All prefix endpoints and signed corrections remain exactly zero. |
| Frozen match with nonzero c and eta | Attenuated incoming correction, with uncertainty separated from the prefix. |
| Constant forcing, L = 0 | A signed polynomial prefix crossing zero, including exact dyadic endpoint cancellation. |
| Constant forcing, L > 0 | Exponential response with a negative initial prefix. |
| Positive total opacity defect | A strictly negative signed photon correction. |
| Negative total opacity defect | A strictly positive signed photon correction while actual opacity stays nonnegative. |
| Zero total defect, nonzero opposite species defects | Photon correction is exactly zero but individual A corrections are nonzero and have opposite signs. |
| L = 0 with nonzero opacity defect | A quadratic prefix and the zero-rate response limits. |
| D = 1 | Finite remainder evaluation without assuming D < 1. |

## Analytic remainder controls

The true manufactured solution is evaluated from the independent closed form

\[
P(u;e)=(f_0+c+e)e^{-(L+d)u}+(q_f+b)J(L+d,u),
\qquad e\in\{-\eta,0,+\eta\}.
\]

Its photon and moment differences relative to the frozen reference, first variation, and signed second correction are calculated analytically. Every resulting endpoint and moment remainder lies within the candidate's analytic bound in the tested cases.

The bound inputs are independently derived constant-data integral upper bounds, including D = |d|h and Br >= integral(|b|+|d|Pf). The check also converts all candidate bound values to exact `Fraction` values and verifies that the returned bound is outward of

\[
|G_i|\eta+T_i\eta+T_iDS.
\]

For the fixture's `effective_*` entries, the interval encloses a valid triangle upper-bound expression. The candidate consumes its upper endpoint; the lower endpoint is not asserted to bound the integral of the absolute effective kernel from below.

It verifies S >= |c|+eta+Br and explicitly checks D against the whole-segment integral, so replacing D with the endpoint Hh would not pass this control.

## Evidence and scope

`CONTROL_RESULTS.json` retains the inputs, candidate and independent oracle signed intervals, whole-cell ranges and their exact extrema locations, independent bound inputs, candidate remainder decomposition, true remainder intervals, and individual check outcomes. `START.json` and `RECEIPT.json` bind the source bytes, contract, control code, actual timings, resource counters, and claim ceiling. The runner writes a fresh output directory and preserves a `FIRST_FAILURE.json` plus partial results if an execution fails.

The oracle and candidate share Python's Decimal exponential primitive; the mathematical target and interval expression evaluation are separately implemented. This is manufactured computational validation, not a new physical coefficient model, proof-assistant verification, full-population numerical admission, or the final independent decision on E13C9. The new candidate's captured-path outputs still require their own scoped review.
