# RUN17 independent implementation and mathematical scope review

## Outcome

**No material physical, algebraic, or implementation defect was found in the
reviewed bounded unit.** The controls, residual decomposition, and exact
polynomial domain certificates support the stated local conclusions. The
conditional comparison remains a sampled-coefficient numerical diagnostic;
it is not a certified error radius for the true coupled initial-value problem.

This was one complementary review by the spectral-theory agent. It read the
frozen native and residual sources, their tests, source bindings, actual result
JSONs, and the exact Bernstein certificate. The reviewer made **zero native
RHS calls, zero IVP solves, and zero test reruns**, and did not edit those
implementations. Producer execution is identified separately below.
The reviewed byte identities are in THEORY_DELIVERY_MANIFEST.json.

## 1. Physical and event ownership

The new controls use the original finite M2 packet on the first smooth
birth-to-birth panel,

\[
z\in[0.004989333151072248,\;0.02371416180174271],
\qquad z=(X-0.7)/0.0004.
\]

The outgoing first-birth and incoming second-birth branches contain 252 exact
reflection-quotient cohorts, corresponding to 504 physical rows from all 48
spectral cells. The first threshold root lies later. Future birth cohorts are
not activated on this panel. The gas is initialized from the recorded RUN16
prefix-C state; local absorption and heat ledgers are newly initialized to
zero, with no claim to reconstruct earlier transport ledgers.

The affine gas lift, native proper-density factor, geometry-dependent
\(dt/dz\), four absorber channels, and photoheating were checked against
the original owners. H binding energy, H fitting edge, and D gate retain their
distinct roles. The D approximation remains threshold-gated H equality.
The source measure, prescribed BASS121 SIGNED_MINUS geometry, 160 births,
and GL8 rule are inherited. No new unit convention sets \(c\), \(k_B\),
or \(\hbar\) to one.

The 265-state control consists of five invariant gas coordinates, 252 depths,
and eight local ledger coordinates. Its adaptive error norm is therefore a
new reduced-state control norm; it is not identified with the historical
40,357-state error norm. The stored endpoint replays agree exactly in floating
arithmetic with the original full section RHS after packing.

## 2. Dense derivatives and the signed defect balance

The differentiated seven-term DOP853 recurrence includes both product-rule
terms and the saved step-clock factor. It computes the derivative directly
from coefficients, preserving small derivatives that would be lost by
subtracting two nearly equal state values.

The new P path is a PCHIP of five invariant coordinates lifted by the same
affine map as the native path. Its depths are integrals of its own opacity,
with the fixed active cohort set. The outer quadrature is split on the
necessary reconstruction and geometry pieces. The R path is the saved dense
output of control B. Native and photo forcing are evaluated separately at
both paths; the optical and gas defects of R are retained.

For the orientation \(\delta=P-R\),

\[
r_P=P'-F(P),\qquad r_R=R'-F(R),\qquad
\delta'=F(P)-F(R)+r_P-r_R.
\]

The implementation uses this sign convention, including
\(\Delta Y_{\rm HI}=-h_*\Delta q_H\). Its temperature derivative
uses the derivative of the native EOS, including the particle-count term.

Actual producer results give the following local hydrogen-coordinate
decomposition at GL10 quadrature:

| Contribution to \(\Delta q_H\) | Recorded value |
|---|---:|
| Initial P minus R | \(+1.4141500097458737\times10^{-6}\) |
| Integral of native forcing difference | \(-1.231282605522407\times10^{-9}\) |
| Integral of photo forcing difference | \(-1.0565857009456857\times10^{-12}\) |
| Integral of P defect | \(+2.007717655822495\times10^{-6}\) |
| Minus integral of R defect | \(+1.9927256078590084\times10^{-18}\) |
| Endpoint P minus R | \(+3.420635326378818\times10^{-6}\) |

The maximum closure discrepancy over all five coordinates is
\(2.307910671383792\times10^{-17}\). The endpoint HI relative difference
is \(-3.800718802625755\times10^{-6}\), and the temperature difference is
\(+0.12465231681380828\) K. These observations identify the initial path
difference and the integrated P defect as the dominant terms for this
hydrogen-coordinate contrast. The P hydrogen defect changes sign within
this panel, so a signed integral carries information that a single unsigned
maximum discards.

The first-birth population's finite-source survivor contrast is
\((S_P-S_R)/S_R=3.095494720825061\times10^{-6}\). This is the survivor of
the first birth at the incoming second-birth endpoint. It is not a
full-history sub-H observable, a new spectral refinement result, or a
continuum estimate.

The GL6/GL10 forcing-integral contrast and GL12/GL20 optical-integral contrast
are finite numerical checks. The close endpoint balance and ledger closure
do not by themselves bound the quadrature remainder or the spectral error.

## 3. Exact Bernstein domain result: proof and scope

For an ascending-power polynomial
\(p(u)=\sum_{k=0}^{n}a_k u^k\) on \([0,1]\), its degree-\(n\)
Bernstein coefficients are

\[
b_j=\sum_{k=0}^{j}
       a_k\frac{\binom{j}{k}}{\binom{n}{k}},
\qquad
p(u)=\sum_{j=0}^{n}b_j\binom{n}{j}u^j(1-u)^{n-j}.
\]

The Bernstein basis is nonnegative and sums to one. Thus
\(p(u)\ge\min_j b_j\) throughout the interval. This implication is
sufficient, not necessary: a negative coefficient bound alone does not prove
that the polynomial is negative.

The implementation performs this conversion with exact rational arithmetic
on the stored binary64 coefficients. Its independent DOP853 basis is

\[
F_k\,x^{1+\lfloor k/2\rfloor}(1-x)^{\lceil k/2\rceil},
\quad k=0,\ldots,6.
\]

The exact accepted interval maps to the saved clock using
\(x=((t_{\rm right}-t_{\rm left})/h)u\), with the subtraction and ratio
performed on exact rational representations of the stored numbers. It
does not silently assume that a rounded saved \(h\) equals an exact real
endpoint difference.

The gas certificate uses exactly
\(Y=Y_0+L(q-q_0)\). Nuclear totals are compared with exact sums of stored
\(Y_0\), rather than a separately rounded normalization scalar. Positivity
of the particle count reduces the temperature constraints to polynomial
signs for

\[
\frac{2e_{\rm V}}{3k_B}U-T_{\min}N_p,
\qquad
T_{\max}N_p-\frac{2e_{\rm V}}{3k_B}U.
\]

The recorded exact result certifies all **24 gas polynomial pieces** (one
P cubic and 23 R degree-seven pieces), their H/D/He totals, positive active
gas populations, positive thermal energy and particle count, and
\(2.7<T<200000\) K under the stored constants. All **5,796 R depth
polynomials** are nonnegative on their respective closed pieces.
The independently defined ideal P depths are nonnegative because they
integrate nonnegative opacity along a positive gas path; they are not
certified as quadrature polynomials by this computation.

These are exact statements about ideal real polynomials specified by saved
coefficients. They do not establish an error tube around the true IVP,
bound every rounded evaluation, or certify depth monotonicity. The
certificates apply piece by piece. A later rigorous residual error estimate
must establish the required inter-piece continuity of its chosen exact
reconstruction, or include representation jumps in its defect measure.
The present finite endpoint closure is not promoted to that stronger claim.

## 4. Comparison propagator and execution bindings

The three-by-three augmented exponential correctly integrates a constant
Metzler two-block comparison with constant forcing, including singular and
zero matrices. A negative gas logarithmic norm is retained. No inverse of
the comparison matrix and no strict-contraction premise are introduced.

For the current numerical candidate, the gas/depth block scales are sampled
at three points, and the gas defect scalar is the maximum over the 230 GL10
quadrature points. It is not a supremum and excludes separately sampled
endpoints. The separately stored left-endpoint gas defect is slightly larger
than that GL10 scalar. The explicit source-binding clarification preserves
this distinction. A rigorous optical defect estimate would also include
the unbounded remainder of the P path's optical quadrature.

The original comparison module's docstring omitted floating exponential
rounding in its hypothetical certified-input interpretation. The publication
version now states that even certified tube coefficients require an
enclosure of the returned floating map. The exact executed source is
preserved at residual/history/comparison_propagator_executed.py, and
DOCUMENTATION_REPAIR_AND_SOURCE_BINDING.json records identical executable
AST after removal of docstrings. No numerical result was re-executed or
rewritten to conceal this documentation correction.

The archived native result field named step_halving_comparison is explicitly
qualified by NATIVE_UNIT_RECEIPT.json: control B has a fivefold reduction of
the configured maximum step, giving 15 versus 23 accepted steps. It is not a
uniform factor-two refinement and establishes no asymptotic order.

## 5. Actual execution and remaining scientific work

Producer evidence records two new bounded native panel solves, 578 native
calls, and zero historical M2 reruns. The residual analysis adds 800 native
point evaluations and zero IVP solves. The Bernstein unit makes zero native
calls. The producer reports five dense-derivative/sign tests, four comparison
tests, and three Bernstein tests passed. The reviewer read those test sources
and the available execution receipts; the reviewer did not rerun them.

This unit supplies a constructive local explanation of the P/R difference
and a continuous polynomial admissibility result. Within the existing
P4-S4C-SPECTRAL-EDGE-SUPPORT node, the next incomplete task is to turn the
post-birth residual and comparison candidates into a conditional continuous
estimate: bound the residual between evaluation points or its positively
weighted integral, bound the relevant Jacobian blocks on an admitted gas/depth
tube, and propagate the prefix uncertainty and event/representation defects.
The exact polynomial domain result is useful input to this work; it does not
supply those missing bounds by itself.

For a claim about the continuous source rather than this finite packet, the
full gas and photo forcing quadrature discrepancy must also enter the
residual budget. A terminal sub-H tail estimate alone cannot replace that
forcing discrepancy. Angular, birth-time, whole-domain, full EoR, Einstein,
and the remaining original atomic/nuclear DAG obligations remain unchanged.

