# First-cell resolved-owner sensitivity: a data-bound partial result

Task: REI_OWNER_FIRST_CELL_STATE_PARTIAL_BOUND
Date: 2026-09-07
Status: ANALYTIC_G2A_STATE_PARTIAL_BOUND_DERIVED; FULL_OWNER_TUBE_UNKNOWN

## 1. Intake and scope

Parent is PR #77 at commit `1244fa97b8e854ae0ced40f306cb41f28232800d`,
tree `581e304bd0aaefe784d88d5ac4f1f9494780eeed`.
Its fixed handoff, TUBE_INPUT_STATUS, source bindings, original O01--O10 stderr
and EXECUTION.json were read. That existing run used scientific source
`12d64833419651a532451ad4c9a180aa65a0a70b`, tree
`93f34e2c869e888a0f78bd67b53d905c74e83710`: 10/10, one invocation, exit 0,
no timeout/failure/error/skip. It was not rerun. The empty PR discussion and
latest PR listing contained no later first-cell result when this work began.

This note derives a narrower bound using actual saved forcing literals. It
neither manufactures a trajectory tube nor promotes the historical endpoint
box into one. The exact-real current law and its JVP from #77 are reused.
The new step is the source-specific group split and a uniform G2a state-only
bound which does NOT require an additional neutral-population lower margin.

The theorem concerns the exact-real PCHIP input contract and exact-real owner
law, with saved decimal literals interpreted as real numbers. It is not a
certificate for a particular SciPy binary, CSV-to-binary64 parsing, polynomial
coefficient construction, residual corrections, or MPFR/Rust implementation.
Calculator outputs below are numerical cross-checks, not interval arithmetic.

Freeze the source tables, cross sections, structural mask, elemental totals,
and the comparison time t. Different states are compared at the SAME t. The
bound is uniform as this fixed comparison time ranges through the first cell.
No arbitrary forcing-table, time, external-current, or total-abundance tangent
is set to zero in a claimed full derivative: those tangents are simply outside
this declared state partial. There is no new atomic-rate fit or physical run.

## 2. Source-to-input correspondence

All files below were read at the parent commit. Full paths and server-reported
Git blobs, literal rows, and calculator expressions are in RESULT_AND_INPUTS.json.

- ADAPT/analysis/tensorized_inputs.py: current from absorption_* columns;
  opacity from kappa_*; time from time_s; redshift from z_mid. External e is
  raw_component_kappa_cMpc_inv for EFFECTIVE_HI_SUBGRID, sorted by interval/node.
  It is NOT conditioned_kappa_cMpc_inv. Owner support is distinct from atomic
  cross-section support.
- ADAPT/analysis/array_forcing.py: separate non-extrapolating PCHIP models for
  current, opacity, external response, redshift and Gamma. point evaluates at
  t; step averages the first three by integration and evaluates z/Gamma at the
  midpoint. These operations are not substituted for one another.
- VALID/analysis/reduced_interval_rhs.py, _explicit_photo_fields: already uses
  the resolved species-marginal cancellation with elemental denominators
  H, He, H. It supplies the CROSS event_box source. This older primal reduction
  is reused, not claimed as a new discovery.
- CROSS/analysis/interval_discrete_map.py: run_lane takes one full step and two
  half steps at partition 2048. The saved population and log-temperature are
  the second-half endpoint. The same corrected population enters that half's
  final thermal source, but the saved public box is not the other three sites.

The first two interval-0 forcing knots have times

    0 and 6134904103445.532 seconds.

The interval duration is 638562959250984.8 seconds. Thus the historical
microstep ends at duration/2048 = approximately 311798319946.7699 s, only
0.05082366646475457 of the first-cell duration. Its second half begins at
approximately 155899159973.38495 s. These are read/derived times, not a new run.
All full-step and half-step source times lie inside this first forcing cell.

PCHIP preserves the range between adjacent nodal values without overshoot.
Therefore the first-cell endpoint hull bounds the exact-real interpolant
throughout that cell. This is use of a shape-preserving interpolation theorem,
NOT a sampled-maximum estimate. A positive-time average over a subinterval is
in the same hull; that observation does not commute normalization and averaging.
Flat adjacent values give a constant interpolant on their cell.

Source literature for this limited interpolation claim:
SciPy PchipInterpolator documentation, Notes and its Fritsch--Butland reference,
https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html
Fritsch and Butland, SIAM J. Sci. Stat. Comput. 5 (1984), 300--304,
DOI 10.1137/0905021. The documentation was read, not the full 1984 article.
No exact local SciPy runtime identity or implementation parity is inferred.

## 3. Actual first-cell group split

Groups are (G1,G2a,G2b,G3). The source mask has subgrid=(1,1,0,0),
HI=(0,0,1,1), HeI=(0,1,1,1), HeII=(0,0,0,1).

| Group | Resolved owners | Actual saved forcing fact | State-partial consequence |
| --- | --- | --- | --- |
| G1 | none | subgrid only | resolved current and its state partial are zero |
| G2a | HeI | e>=0.0165719948704725 cMpc^-1 | uniform bound below |
| G2b | HI,HeI | e=0 and J>0 | neutral-response denominator still needs a lower bound |
| G3 | HI,HeI,HeII | adjacent J values both zero | current and state partial vanish on the admissible positive-support domain |

G3 is a current-null result for THIS saved first cell, not a permanently
inactive species/group mask. It says nothing about an imposed delta J_G3,
other cells, collisional HeII ionization, or OTS HeII transitions.
G1's subgrid node distribution remains outside the resolved material source.

All four opacity endpoint hulls have strictly positive lower values. In the
exact-real contract kappa>0 is therefore established on this first cell, rather
than assumed from an isolated point. This does not supply R>0 for every group.
In particular G2b's external authoritative kappa is not its raw owner sum R.

The actual forcing field z_mid equals 5.95 at both cell ends and hence is
constant on the first cell. The owner-table z_snapshot values near 6 are NOT
substituted for this field, and no physical redshift history is redefined.

## 4. G2a theorem and source-literal numerical bound

Let H_He>0 be the fixed GLOBAL helium count. Define dimensionless extensive
shares u_i=N_HeI,i/H_He, not local helium fractions. N already includes node
quadrature weighting. There is no second node weight or proper-volume factor.
Let

    p(t)=NH0_CM3*YHE*MPC_CM*sigma_HeI,G2a*(1+z(t))^2,
    s=sum_i u_i, R=e+p*s, theta=p*s/R, v_i=p*u_i/R.

p and e have opacity units cMpc^-1; J is the photon count rate of the normalized
one-cMpc^3 box. In this group only HeI is resolved. The source law becomes

    j_i=J*p*u_i/(e+p*s),
    D_u j=(J*p/R)*(I-v*1^T).                              (1)

Assume J>=0, p>=0, e>0 and u_i>=0. The actual strictly positive physical state
domain is a subset; boundary use here is only the continuous rational extension.
The l1 absolute sum of column k in I-v*1^T is

    1+theta-2*v_k <= 1+theta.

Writing x=p*s/e>=0 yields

    ||D_u j||_1 <= (J*p/e)*(1+2*x)/(1+x)^2 <= J*p/e,       (2)

because (1+x)^2-(1+2*x)=x^2>=0. Restricting to fixed-nuclei admissible directions
cannot increase this ambient operator bound. The nonnegative fixed-totals
state domain is convex. Integrating the derivative along a straight segment
between two admissible states proves

    ||j(u,t)-j(u_tilde,t)||_1 <= L_G2a*||u-u_tilde||_1,
    L_G2a = sup_t J(t)*p(t)/e(t).                        (3)

This is a RESOLVED-OUTPUT bound, not the augmented norm including the subgrid
output. For that augmented vector the extra row has column absolute sum
2*(1-v_k), and the corresponding coarse bound has a factor two. Do not apply
(2) to the augmented vector. The source's resolved photo term enters F[3,2]
(HeI -> HeII), so (3) bounds that photo numerator contribution only.

The actual input literals give

    sigma_HeI,G2a = 5.371732151822615e-18 cm^2,
    z = 5.95,
    e_min = 0.0165719948704725 cMpc^-1,
    J_max = 7.727811587461376e49 box photons/s,
    p = approximately 11.891029169582541 cMpc^-1.

The first-cell endpoint-hull estimate J_max*p/e_min is approximately
5.544995259880935e52 box photons/s per unit dimensionless l1 share. This is a
calculator estimate of the analytic upper-bound expression, not a rigorous
rounded decimal endpoint and not an observed sensitivity maximum.

For the quoted conservative theorem constant use the exact looser inequalities

    e > 0.0165, J < 7.8e49, p < 12.

The source-literal q=p/(1+z)^2 is

    q=12308916898279117347435815258329933 /
      50000000000000000000000000000000000 < 247/1000.

Since (1+z)^2=19321/400, p<4772287/400000<12. Consequently

    L_G2a < (7.8e49*12)/0.0165
           = (1872000/33)*10^48
           < 5.7e52 box photons/s.                     (4)

The final comparison is an exact rational inequality; the calculator merely
cross-checked it. For a norm on unnormalized counts, divide this constant by
the fixed H_He. We do not insert metadata's nominal total as a newly certified
exact sum. This bound is uniform over the state's admissible domain because
the actual positive external e controls R. No unknown thermal/path enclosure
is required for this particular partial theorem. It still does NOT close the
full state/forcing derivative or the full nonlinear step.

Limiting checks: J=0 or p=0 gives zero response; at small s the bound remains
finite; for a single resolved node the derivative is J*p*e/(e+p*u)^2. At large
s the exact derivative bound decays. The normalization contribution is retained
at every step of the proof; frozen-R differentiation is not used.

## 5. What remains in G2b, and why it is not just missing paperwork

For G2b, e=0. Set u_HI,i=N_HI,i/H_H and u_HeI,i=N_HeI,i/H_He. With positive
source constants

    q_HI=NH0_CM3*MPC_CM*sigma_HI,G2b,
    q_HeI=NH0_CM3*YHE*MPC_CM*sigma_HeI,G2b,
    D=sum_i(q_HI*u_HI,i+q_HeI*u_HeI,i),

the common (1+z)^2 cancels and j_si=J*q_s*u_si/D. This cancels only the direct
common redshift prefactor at fixed J and state/totals; it is not a full time or
physical-parameter derivative. The still-needed state datum is a quantitative
D>=d_min>0 on the selected source-input set. A usable conditional bound is

    ||D_u j_G2b||_1 <= 2*J_max*max(q_HI,q_HeI)/d_min.      (5)

A global all-state bound like (4) cannot be obtained by assuming only positive
neutral populations. For a fixed J>0 choose positive neutral shares epsilon/2
for each element and vary them as u_HI=epsilon/2+s,
u_HeI=epsilon/2-s, compensating the charged populations to preserve nuclei.
At s=0 the derivative of the total HI photon share is

    4*J*q_HI*q_HeI/[epsilon*(q_HI+q_HeI)^2].              (6)

The input l1 derivative is 2 and the output l1 derivative is twice (6), so the
gain diverges as epsilon tends to zero. The construction embeds in all nodes
using fixed positive within-element node weights. It is a boundary counterexample
for the declared law, not a physical trajectory or a claim that REI is unstable.

The saved endpoint can support a strictly narrower future calculation, conditional
on its stated enclosure interpretation. With fixed node totals h_i, he_i,

    u_HI,i=(h_i/H_H)*(1-x_HII,i),
    u_HeI,i=(he_i/H_He)*(1-x_HeII,i-x_HeIII,i).

Independent charged-fraction boxes may lose their anticorrelation and fail to
give a positive neutral lower bound. Positivity must not be manufactured with a
floor. Source population-box constraints may be reused only if actually saved
and identified; do not regenerate them by rerunning the full solver.
This endpoint belongs to the second-half thermal_t1_final population input.
It does not represent the other sites or a continuous exact-flow tube.

## 6. A concrete rounding qualification discovered in source review

VALID/analysis/pchip_bounds.py, blob b12d298c1c42059a8c0596a0ae591d4701f5c9a9,
performs its Horner/Bernstein arithmetic in binary64 and only then expands the
final min/max with nextafter. Its generic 'Certified' claim is not justified
by that final expansion alone. Under ordinary IEEE binary64 round-to-nearest,
ties-to-even, separate scalar operations, the point branch has this counterexample:

    coefficients = [0.0,1.0,9007199254740992.0,-9007199254740992.0]
    lower = upper = 1.0
    exact polynomial value = 1
    rounded Horner: fl(1+2^53)=2^53, then 2^53-2^53=0.

The returned [-2^-1074,+2^-1074] does not contain 1; a second nextafter expansion
also does not. This is a STATIC, explicitly modelled arithmetic derivation.
The helper was not run, and no existing forcing dataset was shown to fail.
No inherited source was patched. This witness blocks treating the generic helper
as an already-proved rounding oracle; it does not refute the exact-real PCHIP
shape theorem or prove that the saved endpoint is numerically wrong.

Equations (2)--(4) do not invoke this helper. A future native numerical claim
needs either a verified arithmetic route or explicit rounding-error bounds.
No machine-certification claim is made here.

## 7. Review, evidence classification, and next step

PHYS-MATH review, same assistant: resolved versus augmented norms, fixed-global
totals, proper-time units, group support, raw versus conditioned e, constant
z_mid versus z_snapshot, convex-domain integration, G3 current-null restriction,
and the G2b boundary example were checked explicitly above.
PHYS-MATH-CODE review, same assistant: actual CSV consumers and masks, point
versus averaged forcing, source-site mapping, retained global normalization,
prior output-box semantics, and the unsafe generic rounding inference were
inspected. Neither pass is external independent certification.

New execution: calculator arithmetic only. New project/CAS tests: NOT_RUN;
Python plots: NOT_GENERATED. The current container command and independent
Python probe each failed before process start with ClientError. No Actions or
Wolfram retry was used to conceal that boundary. Old successful tests were not
replayed. No new executable implementation is claimed by these research files.

SciSpace was used for validated-ODE literature discovery. Abstract-level
methodology distinguishes whole-interval a priori enclosures from endpoint
information; a primary author record was read for Nedialkov--Jackson--Pryce,
Reliable Computing 7 (2001) 449--465, DOI 10.1023/A:1014798618404:
https://experts.mcmaster.ca/scholarly-works/1710287
This supports the scope distinction, not the present REI source or constants.
No literature novelty claim is made for the normalization estimates.

Next selected work: calculate D_min for G2b from the EXISTING primary saved
endpoint and fixed node totals, with exact/directed rounding and explicit
endpoint-only/source-site semantics. If the public representation cannot
supply a positive bound, return that specific result and preserve the arrays;
no synthetic box, new trajectory, producer replay, or global source tube claim.
The direct local prompt is in LOCAL_CODEX_HANDOFF_KO.md.

No production files, O01--O10 code/evidence, physical laws, tolerances, locks,
workflows, BASS/REC/HTT repositories, native/GCC/XZ results, acquisition budgets,
Section-0/ref/lease/worker, first interval/provider, ready/merge or force-push
are changed. The REI Jira item may receive an append-only result pointer, not
an admission or dependency transition.
