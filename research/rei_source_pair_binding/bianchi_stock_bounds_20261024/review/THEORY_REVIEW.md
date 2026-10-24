# Independent theory review: prescribed Bianchi I stock bounds

## Verdict

**PASS_SCOPED_THEORY.** Under the explicitly prescribed diagonal Bianchi I
geometry, positive-mass geodesic transport and finite nonnegative momentum
measure assumptions, the characteristics, sharp kinetic-energy bounds,
conservative pressure-trace bounds, continuity/shear-work equation, cohort
superposition and rational enclosure construction are mathematically
consistent. The exact references in the proposed finite fixture agree with
direct algebraic substitution. No actual mathematical defect was found.

Reviewer: `/root/pressure_review`, a separate native read-only reviewer who
did not author the theory or implement the candidate. Same inherited model
family; no cross-family independence claim. The review uses hand derivation
and inspection of the supplied formulas. No numerical evaluation, candidate
import, compile, test, scientific child, CAS or rendering occurred.

The current reviewed inputs are `next_stock/THEORY_KO.md` and
`next_stock/IMPLEMENTATION_CONTRACT.json`; their exact byte identities and
inspection scope are recorded in `THEORY_REVIEW.json`. The theory was reread
after root corrected two bibliographic titles; the formulas were unchanged.
This review is independent of the completed pressure fixture's execution
review. It supplies no new scientific execution permission.

## 1. Geometry, characteristics and density normalization

The metric and momentum conventions at theory lines 14–24 are sufficient for
this calculation: positive C1 directional scale factors on a finite interval,
comoving proper time, physical orthonormal momentum components, homogeneous
finite nonnegative measure, positive mass, and no collision or external force.
The geometry is an input, with no Einstein backreaction solved here.

Spatial translation symmetry conserves covariant spatial momentum. Since the
orthonormal component is `p_i=q_i/a_i`, the displayed map is

\[
p_i(t)=r_i p_i(s),\qquad
r_i=\frac{a_i(s)}{a_i(t)},\qquad
D=\prod_i r_i=\frac{V_s}{V_t}.
\]

Conservation of particle number in a comoving volume therefore gives

\[
\nu_t=D(T_R)_*\nu_s,\qquad N_t=DN.
\]

The pushforward relocates momentum atoms; its mass is still N. Multiplication
by D then converts number per initial physical volume to number per final
physical volume, exactly once. This is consistent with the specified units:
N and N_t are number densities, while U, the pressure tensor and its trace/3
have energy-density units. M, k and L use one common energy unit. These facts
support theory lines 28–34 without an isotropy assumption.

## 2. Single-particle kinetic map and curvature

For the prescribed positive diagonal map R,

\[
r_-^2|p|^2\le |Rp|^2\le r_+^2|p|^2.
\]

Combining this with `c^2|p|^2=k(k+2M)` gives the displayed monotone kinetic
map and support bound:

\[
F_r(k)=\sqrt{M^2+r^2 k(k+2M)}-M,\qquad
F_{r_-}(k)\le k_t\le F_{r_+}(k),\qquad
L_t^*=F_{r_+}(L).
\]

Writing `S^2=r^2(k+M)^2+M^2(1-r^2)` makes the differentiation direct:

\[
F_r'(k)=\frac{r^2(k+M)}S,\qquad
F_r''(k)=\frac{r^2M^2(1-r^2)}{S^3}.
\]

These match theory lines 52–55. F is convex for expansion ratio `0<r<1`,
concave for contraction ratio `r>1`, and exactly k at r=1. Its monotonicity
in r is nondecreasing, with equality at k=0. Mixed expanding and contracting
axes require no change to these inequalities.

## 3. Sharp moment bounds and the allowed angular class

For N,L positive, the probability measure `nu_s/N` has mean kinetic energy
`mu=U/N` in `[0,L]`. When `r<=1`, Jensen gives the lower bound
`N F_r(mu)` and the chord through k=0,L gives the upper bound
`(U/L)F_r(L)`. Concavity reverses the roles when `r>=1`. At r=1 the two
expressions both reduce to U. Multiplication by D and choosing r_- for the
lower map and r_+ for the upper map produces the stated bounds

\[
D\ell_{r_-}\le U_t\le D u_{r_+}.
\]

Both inequalities are sharp over the specified set of all positive momentum
measures with the supplied N, U and support bound L. The Jensen measure puts
all mass at k=mu; the chord measure places weights `N-U/L` and `U/L` at k=0
and k=L. Align the nonzero momenta with an extremal-ratio axis to saturate
the directional inequality. Splitting each nonzero atom equally between
the two signs of that axis preserves energy and also makes mean momentum
zero. Each endpoint uses its own admissible measure. A repeated extremal
ratio leaves at least one such axis available.

This sharpness claim does not carry over to an imposed initially isotropic
angular distribution. The theory expressly retains validity of the bounds
but declines sharpness for that restricted class (lines 76–82). It also
allows atoms; a smooth-only class would generally realize the atomic
witnesses as limiting approximations. These are appropriate claim limits.

The zero cases are valid: positivity and `U<=NL` force U=0 when N=0 or L=0.
If U=0, every positive-mass particle has zero kinetic energy almost
everywhere, so its momentum remains zero under R. Handling these cases
before evaluating U/N or U/L is mathematically required and is explicit in
the contract.

## 4. Pressure trace without a pressure-isotropy claim

The massive stress formula gives, for every angular distribution,

\[
\frac13\operatorname{Tr}P
=\frac13\int \frac{c^2|p|^2}{E}\,d\nu
=\frac13\int \frac{k(k+2M)}{k+M}\,d\nu.
\]

Thus the previously derived concave-kernel moment inequality applies to
trace/3 without requiring `P_ij=Pi delta_ij`. The derivative
`g''=-2M^2/(k+M)^3` is negative. The pressure interval at known N_t,U_t,L_t
is therefore valid even when the stress has anisotropic components.

The substitutions producing the conservative outer interval have the
correct direction. For

\[
C(L)=\frac{L+2M}{3(L+M)},\qquad
G(U)=\frac{U(U+2MN_t)}{3(U+MN_t)},
\]

one has

\[
C'(L)=-\frac{M}{3(L+M)^2}<0,\qquad
G'(U)=\frac13\left(1+\frac{(MN_t)^2}{(U+MN_t)^2}\right)>0
\]

when N_t>0. Therefore a lower energy bound and an upper support bound
produce a valid pressure lower bound, while an upper energy bound produces
a valid pressure upper bound. The N_t=0 branch is separately zero. Composing
these inequalities need not preserve attainability, so the theory's explicit
conservative, non-sharp pressure claim is appropriate (lines 97–104).

## 5. Continuity and anisotropic work

Differentiating conserved `a_i p_i` yields `dot(p_i)=-H_i p_i` and hence

\[
\dot k=-\sum_i H_i\frac{c^2p_i^2}{E}.
\]

Since `dot(D)=-theta D`, differentiating the transported number and kinetic
energy moments gives

\[
\dot N+\theta N=0,\qquad
\dot U+\theta U+\sum_i H_iP_{ii}=0.
\]

Finite support, positive C1 scale factors and a finite interval make the
moment differentiation consistent with the stated finite-measure setting.
With `H_i=theta/3+sigma_i` and `P_ij=Pi delta_ij+pi_ij`, the trace-free sums
remove the cross terms and leave

\[
\dot U+\theta(U+\Pi)+\sum_i\sigma_i\pi_{ii}=0.
\]

The diagonal background contracts only with the diagonal stress entries;
the equation does not assume other stress entries vanish. The explicit shear
work is why a scalar pressure interval alone does not supply a complete
anisotropic work model. The theory presents this as a conservation identity,
without a strong no-go or universal impossibility assertion. Rest energy MN
obeys its own number-continuity part and is correctly distinguished from
kinetic U and from a new source in an ionization energy ledger.

## 6. Positive source cohorts

The linear geodesic propagator acts on the initial measure and on each
positive injection measure separately. The stated Duhamel-type expression

\[
\nu_t=D(t,t_0)(T_{t,t_0})_*\nu_0
+\int_{t_0}^t D(t,s)(T_{t,s})_*I_s\,ds
\]

has the appropriate dilution and proper-time source units. Positivity lets
cohort inequalities be integrated. As stated in the theory, this connection
is conditional on supplied integrable source data; obtaining finite energy
and finite integrated energy bounds means the relevant transported moments
or their outer bounds must also be integrable. No actual source history or
quadrature is supplied by this statement.

The text explicitly withholds the physical target density, initial stock,
time-dependent source and prescribed scale factors that are absent from the
single-redshift HI rate card. Stopping, collisions and thermal deposition are
also outside this propagator. No hidden empirical closure is introduced.

## 7. Rational square-root enclosure and stable kinetic map

Let `Q=p/q>=0`, q>0 and `s=2^b`. Set
`A=p*s*s/q` and `n=isqrt(floor(A))`. Since n is an integer,

\[
n^2\le A<(n+1)^2.
\]

Dividing by s squared gives the claimed enclosure for sqrt(Q). Equality
`n*n*q=p*s*s` identifies a square exactly representable on that dyadic grid
and allows collapse of the endpoints. Other rational squares remain enclosed
even when their roots are not grid points. The width bound `2^-b` is an
absolute energy-grid resolution in the supplied unit; it is not a physical
uncertainty or an invariant bit-exact energy-unit transformation rule.

For `x=r^2 k(k+2M)>=0`, rationalizing the kinetic subtraction gives

\[
F_r(k)=\frac{x}{\sqrt{M^2+x}+M}.
\]

If the square root is enclosed by `[E_-,E_+]`, positivity of M makes both
denominators positive. The quotient decreases as the square root increases,
so the resulting ordered interval is exactly

\[
\left[\frac{x}{E_++M},\frac{x}{E_-+M}\right].
\]

For x>0 the lower endpoint is strictly positive in exact rational arithmetic.
The x=0 and r=1 shortcuts produce exact 0 and k, respectively. They are
mathematically justified and avoid introducing grid width into exact special
cases. Input float conversion preserves the supplied binary value; it does
not recover precision already lost before the input was supplied.

Taking the outer endpoint of each sharp-energy endpoint enclosure gives an
outer interval for U_t. The additional cap `N_t*L_upper` is another valid
upper bound, so its minimum with the energy upper enclosure remains valid.
The monotonicity arguments in section 4 justify the contract's subsequent
pressure substitutions. The separately returned lower/upper sharp-endpoint
enclosures and support enclosure preserve the computational information
needed to distinguish radical enclosure width from the moment-information
gap. These intervals are not probabilistic uncertainty estimates.

## 8. Proposed exact controls

The fixed radical references below follow from direct substitution into the
displayed expressions with `N=U=L=2, M=1`; they were inspected algebraically,
not executed. The tiny-energy case has its own specified k.

| Proposed control | Checked reference and purpose |
|---|---|
| Identity `(1,1,1)` | D=1, N_t=2, energy exactly 2, support exactly 2, pressure interval `[8/9,1]` |
| Isotropic expansion `(1/2,1/2,1/2)` | D=1/8, sharp energy endpoints `(sqrt(7)-2)/8` and `(sqrt(3)-1)/8` |
| Isotropic contraction `(2,2,2)` | D=8, sharp energy endpoints `8*(sqrt(33)-1)` and `16*(sqrt(13)-1)` |
| Mixed axes `(1/2,1,2)` | D=1, sharp energy endpoints `sqrt(7)-2` and `2*sqrt(13)-2`; support `sqrt(33)-1` |
| Tiny k=`2^-200`, M=1, r=1/2, b=64 | Positive rationalized lower bound; enclosure independently checkable by squaring `F_endpoint+M` against Q |
| Zero and invalid domains | Zero branches and exact refusal requirements are explicitly specified; runtime behavior remains untested |
| Common weight factor `7/3` | N,U and their propagated endpoint enclosures scale exactly; `U/N`, support and sqrt grids stay unchanged; pressure endpoints scale by the same factor |

An independent future radical check can transform each endpoint to a
nonnegative square-root comparison and compare exact squares. This checks
the enclosure without calling the production `isqrt` helper. The contract
appropriately calls for such a reference. A future code review must examine
its actual implementation; this theory review does not certify code that
has not been inspected.

## Scope, sources and next transition

The primary references and bibliographic title corrections are supplied by
root's recorded literature intake. This reviewer did not repeat the web
search or independently reopen those primary PDFs. The mathematical checks
above derive from the explicitly supplied assumptions and equations. No
massless pressure formula was transferred into the M>0 calculation, and
neither a literature novelty claim nor a CAS proof is asserted.

This PASS permits continuing the already authorized static preparation and
separate equation-to-code review. It admits no stock numerical result,
physical source history, stopping law, selected EOS, Einstein evolution,
L4 completion or new child execution. The current pressure allowance is
separate and already consumed. No theory repair is requested; stop this
bounded theory review and inspect the actual static implementation when
assigned.
