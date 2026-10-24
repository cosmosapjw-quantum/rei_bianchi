# Formal independent review: moment-feasible stress and work bounds

## Decision and exact scope

**PASS_SCOPED_THEORY.** The formal stress-set theorem, signed work bounds,
fixed-energy derivative interval, full Frobenius bound and conservative
uncertain-energy composition are correct under the stated assumptions.
Mathematical findings: zero. One worker-identified input-binding documentation
finding, **WORK-INPUT-01**, is **closed at the formal-contract level** after
the targeted repair described below. Unresolved findings: zero.

This review binds the final files:

| Input | SHA-256 |
|---|---|
| `THEORY_KO.md` | `d2febfb893e3e06adc7d3e276d49f6fd8f560a3f845199061c984a0bef4546e2` |
| `IMPLEMENTATION_CONTRACT.json` | `03548169c1f874eee9816b6af69c947bf41cd20c9a026c84debe853ea5ca057d` |
| `BINDING_REPAIR.json` | `3c7acf04217f155a13836014bd563d273b2dd5d55f8a6e42c0d4f1ff8a6e8c70` |

The initial formal theory and contract were read completely. The preserved
pre-repair copies match those initially reviewed hashes. A complete diff
against the final files contains only the stated stored-input selector,
provenance and transported-witness changes; the core theorem and previously
checked literal cases are unchanged. The final versions were reviewed through
that complete diff and the final hash comparison.

Reviewer: `/root/pressure_review`, independent of the root author and coding
worker. Same inherited model family; no cross-family independence assertion.
The preceding `review/WORK_BOUNDS_PRELIM_REVIEW.md/.json` is reused for the
already checked PSD/spectral argument, signed endpoints, beam attainment,
zero/negative/mixed-sign cases and Frobenius inequality. The earlier stock
proof was not reaudited. This formal review inspects the new assertions and
contract; it does not admit an implementation or a numerical run.

## 1. Full stress feasibility set: sufficiency verified

The necessity of

\[
\mathcal P=\{P=P^T:\;P\succeq0,\ S_{\rm lo}\le\operatorname{tr}P
\le S_{\rm hi}\}
\]

follows from the positive semidefinite particle integrand and the trace
moment bounds. The new sufficiency proof in section 3 is also valid.

For any P in this set with positive trace S, choose a radial kinetic-energy
measure rho with the prescribed N,U,L and `integral g(k) rho(dk)=S`.
Such a measure is the convex mixture of the two radial trace extremizers;
when the trace interval collapses, either extremizer already has the required
trace and no division by its width is needed. Decompose

\[
P/S=\sum_j w_j e_j e_j^T,\qquad w_j\ge0,\quad\sum_jw_j=1.
\]

At every radial energy use the angular probability measure assigning
`w_j/2` to each of the directions `+e_j` and `-e_j`. At k=0 these all
represent the same rest momentum, which changes no mass or energy count.
This product construction preserves N,U and support and gives

\[
\int g(k)\,\rho(dk)\sum_jw_je_je_j^T=S(P/S)=P.
\]

The momentum mean vanishes pairwise. If S=0, positive semidefiniteness implies
P=0; the positive trace-lower coefficient implies U=0, so `N delta_0`
realizes the case. This includes the zero measure. Thus the stated set is
exact for the selected unrestricted angular class with atoms allowed.

The text correctly excludes the stronger interpretation that every such
tensor belongs to a fixed transport history or to a self-consistent diagonal
Einstein solution. The diagonal-rate extrema themselves remain realizable
by axis beams with diagonal stress. No extra dynamical hypothesis was used
to enlarge that claim.

## 2. Work, derivative and anisotropy claims

The formal sections 4–6 preserve the already checked formulas. In particular,
the fixed-U derivative interval is obtained from the single work contraction
`W_H=Tr(HP)`. It avoids treating pressure and shear extrema as independently
attainable and is sharp for the same instantaneous admissible measure set.
The work, shear and norm extrema are explicitly not asserted to occur
simultaneously.

The norm is the complete Frobenius norm, with
`norm_squared_upper=(2/3)*S_hi^2`; it contains no LRS or one-half convention
factor. The instruction to add actual signed STF tensors before forming
combined quantities preserves cancellation and does not replace a tensor
with a sum of scalar upper bounds.

For uncertain energy, section 7 first establishes the valid outer trace band

\[
S\in[\phi(u_{\rm lo},\bar L),\psi(u_{\rm hi},N_t)].
\]

The signed spectral formula then encloses work. Since `-theta*U` is affine,
sorting its endpoint values gives `[A_lo,A_hi]` for either sign of theta.
Subtracting the work interval yields

\[
\dot U\in[A_{\rm lo}-W_{\rm hi},\;A_{\rm hi}-W_{\rm lo}].
\]

This interval is valid even though work and U are correlated. Its rectangular
composition can be wider than the actual joint range, and the formal text
correctly withholds sharpness. The input constraints
`0<=u_lo<=u_hi<=N_t*Lbar`, positive M and explicit zero branches suffice for
the displayed formulas. These statements concern the source-free,
collisionless, force-free homogeneous cohort on prescribed geometry.

## 3. Exact fixture literals and API scope

All formal rate-case literals agree with direct symbolic substitution at
`N=U=L=2,M=1`, where `S=[8/3,3]` and the norm-squared upper bound is 6.
No fixture was executed during these checks.

| Rates H | Work interval | Shear-work interval | Energy-derivative interval |
|---|---|---|---|
| `(-2,1,4)` | `[-6,12]` | `[-9,9]` | `[-18,0]` |
| `(1,2,3)` | `[8/3,9]` | `[-3,3]` | `[-21,-44/3]` |
| `(-3,-2,-1)` | `[-9,-8/3]` | `[-3,3]` | `[44/3,21]` |
| `(2,2,2)` | `[16/3,6]` | `[0,0]` | `[-18,-52/3]` |
| `(-2,-2,-2)` | `[-6,-16/3]` | `[0,0]` | `[52/3,18]` |
| `(0,0,0)` | `[0,0]` | `[0,0]` | `[0,0]` |

For the explicitly uncertain example `N=2,U in [1,2],L=2,M=1,H=(-2,1,4)`,
the trace `[4/3,3]`, work `[-6,12]` and derivative `[-18,3]` are also correct.
Common measure-weight scaling changes linear moment/work outputs linearly
and the squared norm quadratically. Rate reversal reverses and negates the
work/derivative endpoints; axis permutation preserves the scalar bounds.
The U=NL collapse, zero cases and tiny positive exact-U case are appropriate
finite controls. Their actual code and runtime reach remain separate checks.

The abstract theorem allows a general symmetric B, while both implementation
APIs accept only three signed diagonal rates. This is an explicit and sound
restriction: eigenvalue bounds are exact min/max of those rates, so no
floating spectral estimate is being treated as an exact endpoint. The two
claim labels distinguish sharp exact-moment output from conservative
energy-enclosure output. The contract requires exact represented Fraction
arithmetic, including the positive tiny-U case; it does not recover input
precision lost before conversion.

## 4. WORK-INPUT-01: corrected and statically verified

The original formal contract proposed consuming numerical identity values
from stock stdout. The coding worker correctly reported that the frozen
stock fixture emits `identity_checked: true`, but no numerical identity
payload. This was a concrete stored-input binding defect in the next-work
description, not a stock-theory, source-code or execution defect.

The repaired contract instead selects `mixed_energy_interval`. This selector
and its encoding were checked directly against the frozen stock fixture:

- The copied fixture SHA-256 is
  `47ecf7dc0ec59790e4eb339d59c527e71c07aab4ecb7b2fc0c4e265e77b35f43`,
  and its bytes equal the prior prepared original.
- `serial` at lines 28–30 encodes each Fraction as decimal numerator and
  denominator strings.
- The mixed call at lines 48–52 fixes `N=U=L=2,M=1` and ratios `(1/2,1,2)`.
- The actual emission at lines 93–101 includes `mixed_energy_interval` and
  its endpoint enclosures; identity is only a completion flag there.

The revised provenance distinction is correct. N_t=2 follows from frozen
N=2 and D=1. The new support majorant Lbar=5 follows from
`sqrt(33)-1<5`, using `33<36`. Neither quantity is mislabeled as read from
stdout. The contract binds both the eventual complete saved stdout and the
original fixture identity, and prohibits stock replay/import for consumption.

The added transported witness is also consistent. A symmetric initial
axis-2 beam at k=1 with N=2 has r_2=1 and D=1, hence final U=2 and
`P=diag(0,3,0)`. At `H=(-2,1,4)`, theta=3 and shear rates are `(-3,0,3)`.
The witness therefore has trace 3, work 3, shear work 0, derivative -9 and
full anisotropy norm squared 6. These are suitable containment references
for the composed outer intervals and do not assert that their endpoints
are jointly attained.

**Finding status: CLOSED_IN_FORMAL_CONTRACT.** The preserved initial theory
hash `f94f5d0c407a309112845ba4cbb96e96b31e60724788f5dedcdde3fac98419bf`
and contract hash
`2aa0e33104eab95fd0f3272c0c5b94a1f876ccbffc82001903db72b350236921`
match the initial full reads. The final diff is limited to the necessary
binding/provenance/witness repair. No science or stock replay was used for
that repair. Actual raw-file availability, its frozen hash, the consumer
implementation and successful future consumption are not implied by this
static closure; those await their separately supplied evidence.

## 5. Primary conventions and retained CAS record

The saved primary-text excerpts in `research/PRIMARY_DETAIL_RAW.json` were
read for the relevant kinetic stress and sign conventions. Heinzle–Uggla's
massive stress and conserved covariant-momentum expression are consistent
with the physical-frame kernel `c^2 pp^T/E`, with `E=k+M`. Rendall's
`dot(g_ij)=-2k_ij` gives `k^i_j=-H_i delta^i_j` for `g_ii=a_i^2`, and its
mean curvature is therefore minus theta. The formal mapping has the correct
sign. These were local cached excerpts, not a new PDF retrieval or a claim
to have reviewed either complete paper. Their global Einstein–Vlasov
asymptotics are not admitted by the present prescribed-background theorem.

All three retained Wolfram raw records were inspected. The context record
contains an internal error. The initial evaluation retains `D::ivar` and
an unevaluated derivative with respect to 2; that does not establish g''.
The corrected record gives the stated g'', phi_U, phi_L and psi_U, consistent
with the direct derivation. Reading this output is not a new CAS invocation
and does not promote CAS to an independent model review or to proof of the
full feasible-stress theorem. No new strong no-go or novelty claim appears.

## Recommendation and stop

Continue the already authorized finite implementation preparation under the
final contract, then review the actual source, bound input and raw outcome
when supplied. The work-bound theorem supplies meaningful tensor-work
information while retaining the limits on history, EOS, thermalization,
Einstein feedback and L4. No mathematical repair or additional review
campaign is requested.

This review's candidate imports, compilation, tests, scientific executions,
CAS calls, rendering, implementation edits, Git writes and cloud writes
are all zero. Root retains scientific admission and execution-release
authority. The stock execution raw review remains a separate task.
