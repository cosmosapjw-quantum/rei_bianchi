# RUN18: exact continuous depth reconstruction and its response budget

## New result and owners

This is a new bounded continuation of **P4-S4C-SPECTRAL-EDGE-SUPPORT**.
It uses the frozen RUN17 first-birth control B and its exact polynomial
domain certificate. It does not replay any native IVP or historical M2 run.

The source state archive has SHA-256
`ddc62155d70a9a9b2f7ae3ab2caf827cbb8bab6bebc1aeae6ce229b4b4ebddf4`.
Its 23 saved degree-seven DOP853 pieces cover the first smooth birth panel
\(z\in[0.004989333151072248,0.02371416180174271]\), where
\(z=(X-0.7)/0.0004\). The 257 feedback coordinates comprise five invariant
gas coordinates and 252 cohort optical depths. Eight passive ledger
coordinates are outside this audit; their exclusion does not alter the
gas/depth field. All original 48 spectral cells, fixed births/GL8, native
atomic owners and prescribed BASS121 SIGNED_MINUS geometry remain the owners.

The exact Python reference found:

| Exact statement about stored real polynomials | Result |
|---|---:|
| Normalized right-end clocks exactly equal to one | 23/23 |
| Gas internal coordinate jumps | 0/110 |
| Gas terminal endpoint mismatches | 0/5 |
| Nonzero depth coordinate jumps | 431/5,544 |
| Time interfaces carrying those jumps | 3, after pieces 1, 2, 3 |
| Largest individual absolute depth jump | \(2^{-55}\) |
| Sum of interface depth infinity norms | \(13/288230376151711744\) |
| Maximum cumulative signed depth offset, \(\Gamma\) | \(9/288230376151711744\) |
| Exact rational response factor, \(\beta\) | \(9/288230376151711735\) |
| Decimal display of \(\beta\) | \(3.122502256758253\times10^{-17}\) |
| Repaired interfaces exactly continuous | all 22 |
| Repaired depth pieces nonnegative | all 23 |

The 431 mismatches are coordinate values at three time interfaces, not 431
physical events or calculations. They arise when stored binary64
coefficients are treated as exact real numbers. A floating endpoint
evaluation may round to the stored accepted endpoint even when the ideal
real polynomial trace differs. This work specifies and verifies a new
reconstruction; it does not diagnose a discontinuous physical solution.

The actual new reference completed in 1.7876 seconds internally, with zero
native RHS calls and zero IVP solves. Full rational offsets, derivatives,
clock checks and positivity margins are retained in
execution01/EXACT_C0_DEPTH_REFERENCE.json. The original arrays are immutable.

## 1. A state jump is an atom of the residual

Let a piecewise smooth reconstruction \(\widehat y\) have traces
\(\widehat y(t_j^-)\) and \(\widehat y(t_j^+)\), with

\[
J_j=\widehat y(t_j^+)-\widehat y(t_j^-).
\]

For the convention \(r=\widehat y'-F(t,\widehat y)\), the distributional
residual is the measure

\[
d\mathcal R =
[\widehat y'_{\rm pw}-F(t,\widehat y)]\,dt
+\sum_j J_j\,\delta_{t_j}.
\tag{1}
\]

If the true ODE state is continuous and \(e=y-\widehat y\), then

\[
e'=F(t,y)-F(t,\widehat y)-r_{\rm pw}
\quad\hbox{on each open piece},\qquad
e(t_j^+)=e(t_j^-)-J_j.
\tag{2}
\]

A jump in the one-sided derivative alone is not an atom of this first-order
state residual. Such derivative jumps affect pointwise residual traces and
higher regularity; they do not appear as an extra state jump in (1).

For two reconstructed paths with \(\delta=P-R\), the integrated signed
balance contains \(J_P-J_R\):

\[
\delta(T^-)-\delta(a^+)
=\int_a^T[F(P)-F(R)+r_P-r_R]dt
+\sum_{a<t_j<T}(J_{P,j}-J_{R,j}).
\tag{3}
\]

Thus a continuous P path contributes \(-J_R\). This sign agrees with the
RUN17 orientation; an unsigned jump radius is used only when passing to a
norm comparison.

Suppose a uniform admitted tube gives the existing two-block comparison

\[
D^+w\le M(t)w+\rho(t),\qquad
M(t)=\begin{pmatrix}a(t)&b(t)\\c(t)&0\end{pmatrix},
\quad b,c\ge0,
\]

for gas and depth error radii. Across a representation jump,
\(w^+\le w^-+\gamma_j\), with block norms
\(\gamma_j=(\|J_{q,j}\|,\|J_{\tau,j}\|)\).
The nonnegative fundamental matrix gives

\[
w(t)\le\Phi_M(t,a)w(a)
+\int_a^t\Phi_M(t,s)\rho(s)ds
+\sum_{a<t_j\le t}\Phi_M(t,t_j)\gamma_j.
\tag{4}
\]

This follows by ordinary comparison on each open piece and induction across
the jumps. It requires no strict contraction premise. For a physical event
map \(\mathcal J\), replace the representation jump by
\(\widehat y^+-\mathcal J(\widehat y^-)\) and propagate the preceding
radius with a bound for the event map. The present panel has no internal
physical event; only the three representation interfaces enter this unit.

Equation (4) remains conditional on continuous residual and tube bounds.
Current sampled RUN17 coefficients are not substituted as certified bounds.

## 2. Exact cumulative repair

Let the saved depth polynomial on piece \(i\) be \(\tau_i(t)\). Define

\[
c_0=0,\qquad c_{i+1}=c_i+J_i,\qquad
\widetilde\tau_i(t)=\tau_i(t)-c_i.
\tag{5}
\]

At a shared boundary,

\[
\widetilde\tau_{i+1}(t_{i+1}^+)
-\widetilde\tau_i(t_{i+1}^-)
=J_i-(c_{i+1}-c_i)=0.
\]

The reconstructed depth is therefore exactly continuous, and its derivative
on every open piece is unchanged. A finite collection of such continuous
piecewise polynomials is absolutely continuous. The gas is unchanged because
all its value jumps and cumulative offsets are exactly zero. The new full
gas/depth reconstruction is thus globally continuous on this panel, with
piecewise analytic derivatives sufficient for the residual integral.

The reference computes every number in (5) with exact Fraction arithmetic.
The Rust fixture preserves the original finite binary64 bits as hexadecimal
integers. The Python polynomial evaluation uses the independent explicit
basis

\[
p_i(x)=y_{i,0}+\sum_{k=0}^6
F_{i,k}x^{1+\lfloor k/2\rfloor}(1-x)^{\lceil k/2\rceil}.
\tag{6}
\]

The physical derivative includes the saved \(1/h_i\) factor. Each endpoint
clock is evaluated as the exact rational
\((t_{i+1}-t_i)/h_i\), not a rounded substitution of one. Here all 23
ratios are exactly one. Then higher basis terms vanish at the right endpoint;
nevertheless the fixture retains all seven rows so the Rust recurrence can
check both values and one-sided derivatives independently.

The reference also compares each final polynomial trace with its stored
accepted endpoint. All terminal mismatches are zero. The cumulative repair
offset at the final time is generally nonzero: a zero *local terminal*
mismatch does not undo earlier signed jumps.

## 3. Reusing the exact domain certificate

For each original depth component, its Bernstein coefficients on piece
\(i\) already supplied a certified lower bound. A constant shift subtracts
\(c_{i,k}\) from every Bernstein coefficient of that component. If the
previous certificate retained a common lower bound \(L_i\) for all 252
depths, then

\[
\widetilde\tau_{i,k}(t)
\ge L_i-\|c_i\|_\infty.
\tag{7}
\]

The actual rational calculations verify that (7) is nonnegative on every
piece. This reuses the prior certificate rather than repeating its whole
polynomial calculation. The gas lift, exact nuclear totals, positive gas
populations and EOS domain remain certified because the gas polynomial is
identical to RUN17.

This proves nonnegative depth and continuity for the newly defined ideal
real reconstruction. It makes no claim about the exact IVP solution or every
rounded runtime evaluation. No absorber-specific decomposition of total
cohort depth was invented: the saved states contain total optical depths.
The per-cohort offsets apply to every absorber channel that uses that
cohort's survivor.

## 4. A rational bound on the repair's physical response

For the same prescribed geometry, source weight and gas path, the cohort
survivor is \(p_k=B_k e^{-\tau_k}\), and (5) gives

\[
\widetilde p_k=p_k e^{c_{i,k}}.
\]

Let \(\Gamma=\max_{i,k}|c_{i,k}|<1\). The nonnegative exponential series
or the monotonicity of
\(-\log(1-\Gamma)-\Gamma\) yields

\[
|e^{c_{i,k}}-1|
\le e^\Gamma-1
\le\frac{\Gamma}{1-\Gamma}
\equiv\beta.
\tag{8}
\]

The final inequality is exact in rational arithmetic once \(\Gamma\) is
known. No floating exponential is used to certify \(\beta\).

For any fixed nonnegative coefficients \(w_k(t)\),

\[
Q(t)=\sum_k w_k(t)p_k(t)\ge0
\quad\Longrightarrow\quad
|\widetilde Q(t)-Q(t)|\le\beta Q(t).
\tag{9}
\]

The statement remains valid at \(Q=0\) as an absolute inequality. Its
relative form applies when \(Q>0\). It applies independently to each
nonnegative absorption channel and each nonnegative heat channel, because
their opacity, gas factor and excess-energy coefficient stay fixed.
Integrating in time preserves the bound for their positive accumulated
rates. It also applies to a fixed survivor subset, including an energy-bin
indicator determined by the unchanged geometry. Threshold membership is
not altered by the depth repair.

For the actual offsets,

\[
\Gamma=\frac{9}{288230376151711744},
\qquad
\beta=\frac{9}{288230376151711735}.
\]

The common gas source \(G(z,q)\), which contains the native chemical and
thermal processes, is unchanged. The photo vector \(\Phi\) changes, so
the repaired gas defect is

\[
\widetilde r_q
=r_q+\Phi(q,\tau)-\Phi(q,\widetilde\tau),
\qquad
\widetilde r_\tau=r_\tau
\quad\hbox{on each open piece}.
\tag{10}
\]

If \(\Phi_q=\sum_a v_a R_a\) with nonnegative channel rates \(R_a\),
then

\[
|\widetilde\Phi_q-\Phi_q|
\le\beta\sum_a |v_a|R_a
\tag{11}
\]

componentwise. A signed net coordinate, particularly the net HeII channel,
need not admit a relative \(\beta\) bound because positive and negative
terms can cancel. Equation (11), not a relative bound on a cancelled net
rate, is the appropriate gas residual allowance.

The repair changes a prescribed reconstructed path; it does not solve the
coupled system again. Equations (8)–(11) therefore quantify the reconstruction
change itself. They do not certify that opacity feedback of the true IVP
is this small. That latter statement still requires residual transport and
continuous bounds for the coupled field.

## 5. Actual VigilODE contract and useful reuse

The independently inspected source is VigilODE commit
`ac1cd2a4738c2441c92e5fdae5f70aba35e53544`, file
`crates/rodas5p-integrators/src/dense_output_v2.rs`.

Its public `ContinuousResidualProvider` requires two owner obligations:

1. `enclose_rhs` must enclose every exact RHS on a time/state box.
2. `one_sided_log_norm_upper` must bound the **Euclidean** logarithmic norm
   of every state Jacobian throughout the supplied tube.

The field must be continuously differentiable in state on the tube, the
mass matrix must be identity, and the caller must bind the provider to the
same dynamics as the saved segment. The trait records these premises; it
does not establish them automatically.

`Rodas5pQuarticSegment::verify_continuous_residual_tube` combines outward
curve/derivative/RHS boxes with a scalar logarithmic-norm comparison. Its
documentation explicitly limits it to a single represented segment and
does not provide adjacent-segment or whole-driver certification.

The useful reuse for REI is the interval arithmetic, explicit provider
contract, work accounting and conditional local comparison design. The
RUN17 polynomial is degree seven and was generated by DOP853, so it cannot
be relabeled as the private RODAS5P quartic segment. The repaired path needs
its own representation adapter. It also needs an interval implementation of
the original native gas and photo/depth field before the API's RHS and tube
premises hold.

RUN17's sampled gas \(\mu_\infty\) and two-block infinity-norm comparison
are not interchangeable with this provider's full-state
\(\mu_2\). In a fixed Euclidean scaling, write

\[
J=\begin{pmatrix}A&B\\C&0\end{pmatrix}.
\]

If a uniform tube bound gives
\(a_2\ge\lambda_{\max}((A+A^T)/2)\) and
\(d\ge\|B+C^T\|_2/2\), then the Rayleigh quotient proves

\[
\mu_2(J)
\le\lambda_{\max}
\begin{pmatrix}a_2&d\\d&0\end{pmatrix}
=\frac{a_2+\sqrt{a_2^2+4d^2}}{2}.
\tag{12}
\]

This is a possible bridge to the actual scalar provider. The required
uniform bounds in (12) have not been computed. A documented fixed scaling
can be chosen before taking those norms; a silently changing norm or a
sampled infinity-norm value cannot replace them.

## 6. Literature and verification boundaries

SciSpace and Exa identified Makridakis and Nochetto,
*A posteriori error analysis for higher order dissipative methods for
evolution problems*, Numerische Mathematik 104 (2006), 489–514,
DOI 10.1007/s00211-006-0013-6. The author preprint actually read is dated
August 10, 2004:
http://users.math.uoc.gr/~makr/MN_dissSub04.pdf .

In that preprint, section 2.1, Lemmas 2.1–2.2 and equation (2.7), printed
pages 4–5, restore continuity using a polynomial times the negative node
jump; equation (2.9) relates the correction norm to that jump. These results
motivate explicitly correcting a discontinuous time reconstruction.
They concern dG/Radau structures and do not transfer an order estimate to
DOP853. The cumulative constant depth repair, its positive-response budget,
and the REI interface contract above are derived here.

Wolfram actually checked the derivative/nonnegativity argument behind (8),
the exponential ratio, and the cancellation of the corrected interface
jump. Its receipt distinguishes those symbolic checks from the exact
Python/Rust arithmetic on the saved data.

The next genuinely incomplete work remains within the same original DAG
node: outward continuous residual enclosures and Jacobian tube bounds for
the unchanged coupled native field, followed by propagation of prefix,
event and source-forcing uncertainty. RUN18 removes the representation-jump
ambiguity for this particular repaired reconstruction; it does not close
the spectral, angular, birth-time or full coupled continuum obligations.

