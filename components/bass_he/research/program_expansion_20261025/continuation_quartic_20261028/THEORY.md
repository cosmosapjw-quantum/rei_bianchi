# QUARTIC12 — rigorous full-family quartic aperture reference
Root-authored R3/R5 derivation; workflow1.0.0; 2026-10-28.
All statements are conditional on the fixed nominal-angle sensitivity windows, even quartic angular model, declared uniform azimuth and inherited physical kinematic/geometry map. They are not an experimental confidence region or a measured event rate.

## 1. Claim and units
Let mu=cos(theta_cm), z=mu^2 in[0,1], and
  f(mu)=q(z)=b0+b1*z+b2*z^2.
The coefficients are signed and have the same DCS units nb/sr as the data. B=160 is in those coefficient units. Define
  d=(2,2/3,2/5), D(b)=d.b.
The normalized even angular measure is f(mu)dmu/D, with the declared uniform azimuth measure. An overall DCS scale cancels in the acceptance ratio. This cancellation does not identify event/inclusive normalization or supply a photon flux.
There are two separately stated model choices: q>=0 on[0,1] (endpoint-free), and the same condition with q(1)=0 (endpoint-zero).
Mass rest energies, three photon energies, metric(-,+,+,+), c/hbar/kB conventions, detector geometry and same-event union are inherited unchanged.

Claims:
Q1: a finite proven box contains every true feasible coefficient vector.
Q2: contracted/expanded rational data rows certify inner/outer data inclusion.
Q3: fixed N1/4/16 cell/grid positivity gives nested containing polyhedra.
Q4: endpoint-zero positivity is an exact two-inequality cone.
Q5: exact active-set enumeration plus signed moment envelopes bounds the full family's aperture extrema.
Q6: actual inner vertices provide certified witnesses and hence brackets on extrema.
Q7: any exclusion is limited to the specified family, windows and endpoint choice.

## 2. A containing coefficient box; no outcome-tuned truncation
Choose the nominal theta values46,61,87deg. The existing certified cosine routine encloses their z values in[0,1]. The new controls verify every pair of these intervals is separated by at least g=1/5.
For a true feasible q, the three ordinates y_i=q(z_i) satisfy0<=y_i<=1 in the fixed literal windows. Lagrange interpolation is exact:
  q(z)=sum_i y_i (z-z_j)(z-z_k)/[(z_i-z_j)(z_i-z_k)].
The denominator magnitude is at least g^2=1/25. Numerator coefficient magnitudes in ascending powers are at most(1,2,1), since z_j,z_k lie[0,1]. Summing three ordinates bounded by1 gives
  |b0|<=75, |b1|<=150, |b2|<=75.
Thus |b_j|<=160 is a proven containing box. It is not a regularizer and does not reject any member of the true family. All four original data angles, including73deg, remain in the fit constraints.

## 3. Signed data rows and outward interval arithmetic
At each nominal angle, use the inherited exact-rational trigonometric enclosure to obtain intervals Z_i for mu_i^2 and T_i for mu_i^4. Interval powers are nonnegative and outward rounded on the fixed2^-60 grid.
Let m_i=(1,mid Z_i,mid T_i) and
  eps_i=B*(width Z_i+width T_i)/2.
For every signed b in the containing box,
  |q(z_i)-m_i.b|
  <= |b1| width Z_i/2 + |b2| width T_i/2
  <= eps_i.
Hence true data L_i<=q(z_i)<=U_i imply
  L_i-eps_i<=m_i.b<=U_i+eps_i.
Conversely, the contracted inequalities
  L_i+eps_i<=m_i.b<=U_i-eps_i
imply the true nominal-angle data bounds. No coefficient sign assumption enters this proof. All endpoints are rational certificates; binary64 numbers are display-only.
The ERR-S windows are fixed coordinate sensitivity windows. No covariance, independent-error or joint-confidence claim is introduced.

## 4. A strictly positive denominator on the true family
All87deg lower bounds satisfy L_i>=L*=7/50. Since
  f'(mu)=2b1*mu+4b2*mu^3,
the box gives |f'|<=6B on[-1,1].
Set delta=L*/(12B). The certified87deg mu interval plus/minus delta lies inside[-1,1], a control checked in this campaign.
For every true f and |mu-mu87|<=delta,
  f(mu)>=L* -6B*delta=L*/2.
Therefore
  D=integral_-1^1 f(mu)dmu >=(2delta)*(L*/2)
   = L*^2/(12B)=49/4800000=:Dmin.
Dmin has DCS units. Adding d.b>=Dmin to both approximating polyhedra preserves the outer inclusion and improves conditioning of the fractional objective. The independent certificate reader checks it at every saved vertex.

## 5. Endpoint-free positivity sandwich
Fix N in{1,4,16} before any result. Every cell is[l,r]=[k/N,(k+1)/N].
The outer constraints are q(k/N)>=0 at all grid nodes.
The inner constraints require the three quadratic Bernstein controls on every cell to be nonnegative:
  beta0=q(l),
  beta1=b0+b1*(l+r)/2+b2*l*r,
  beta2=q(r).
For t=(z-l)/(r-l),
  q(z)=beta0*(1-t)^2+2*beta1*t*(1-t)+beta2*t^2.
The nonnegative basis sums to1, proving the inner positivity certificate.
Combine inner positivity with contracted data, box and Dfloor to define Pinner_N. Combine outer nodal positivity with expanded data, box and Dfloor to define Pouter_N. Then
  Pinner_N subset Ptrue subset Pouter_N.
On nested grids, Pinner_1 subset Pinner_4 subset Pinner_16 and Pouter_16 subset Pouter_4 subset Pouter_1. Subdivision controls are convex combinations of parent controls; additional outer nodes add constraints.

A quantitative outer residual follows from the exact chord identity:
  q(z)=chord(z)+b2*(z-l)*(z-r).
The nonnegative endpoints imply chord>=0; hence
  q(z)>=-max(b2,0)/(4N^2).
This bounds pointwise positivity violation of an outer surrogate. It does not by itself bound the aperture-extremum error, and it is not a physical uncertainty estimate.
A strictly positive polynomial has positive cell controls at sufficiently fine resolution. A zero-touching boundary polynomial may never enter a finite inner cone. The full contracted-data inner set also requires the data margins; refinement alone cannot remove fixed row-contraction exclusion at a data boundary.
We therefore publish observed finite-N extremum brackets, not a universal finite-N completeness or convergence-tolerance assertion.

## 6. Endpoint-zero family is exactly linear
For q(1)=0, set b2=-b0-b1. Then
  q(z)=(1-z)[b0+(b0+b1)z].
The affine bracket is nonnegative on[0,1] exactly when
  b0>=0, 2b0+b1>=0.
Necessity at z=1 uses the limit from below. Sufficiency follows from affine interpolation of its endpoints. These are exact positivity conditions, not an N-dependent sufficient approximation.
Transform every data row, all three signed coefficient box bounds and Dfloor into the two parameters(b0,b1).
One endpoint-zero inner/outer pair is computed per energy; their sole gap is the tiny data-row contraction/expansion. The complete fixed case set is12 unique cases:3energies times3free resolutions plus3endpoint-exact cases.

## 7. Exact polytope certificates
In r=3 free parameters or r=2 endpoint parameters, enumerate every set of r active constraints. Solve a nonsingular candidate exactly with rational inverse; check every inequality, then deduplicate vertices. Singular systems are counted and skipped.
A bounded nonempty polytope has at least one vertex, and each vertex admits r linearly independent active constraint normals, including lower-dimensional cases. Thus exhausted enumeration contains all vertices; a zero-vertex bounded polytope is empty.
The containing box ensures compactness. Identical coefficient matrices share inverses across the three energy RHS; inner/outer identical endpoint coefficient matrices also share them.
Publish matrices, RHS, all vertices, attempted/singular/feasible bases, unique vertices, actual inverse calls and RHS candidate counts. The saved reader verifies certificates without repeating optimization.
Outer emptiness excludes this full quartic family under the fixed assumptions. Inner emptiness alone leaves feasibility undecided. Outer nonemptiness alone also does not certify true feasibility.

## 8. Same-event detector response and signed moments
Use the inherited same-event event set
  C=(A_plus intersect B_minus) union (A_minus intersect B_plus).
It is a union on one event, not a product of unrelated detector probabilities. The inherited exact kinematics and azimuth strips use the fixed2^-48 preimage tolerance; there are nine new geometry calls(3energies x3geometries).
For basis(1,mu^2,mu^4), integrate using
  integral_l^h mu^(2j)dmu=(h^(2j+1)-l^(2j+1))/(2j+1).
The nonnegative basis gives certified moment intervals k_j^-<=k_j<=k_j^+ with0<=k_j^-<=k_j^+<=d_j.
Signed coefficients require a sign-aware interval sum:
  nlow(b)=sum_j b_j*(k_j^- if b_j>=0 else k_j^+),
  nhigh(b)=sum_j b_j*(k_j^+ if b_j>=0 else k_j^-).
Then nlow<=integral_C f<=nhigh. Reusing a positive-coefficient dot-product bound without sign reversal would be invalid.

## 9. Vertex optimization of signed envelope ratios
Each term of nlow is the minimum of two linear forms; nlow is concave. Each term of nhigh is a maximum; nhigh is convex.
Write any polytope member b=sum_v lambda_v v, lambda>=0, sum lambda=1. D(b)>0 and D(v)>0. Concavity implies
  nlow(b)/D(b)
  >=sum_v [lambda_v D(v)/D(b)] nlow(v)/D(v).
The bracketed denominator-weighted coefficients are nonnegative and sum to1. Thus the minimum of nlow/D occurs at a vertex. Convexity proves the maximum of nhigh/D likewise.
For every true member, the outer raw range is
  [min_Vout nlow/D, max_Vout nhigh/D].
Intersect with[0,1], because the actual numerator is the measure of an event under a nonnegative normalized distribution.
An empty intersection is represented by physical_range=null and status EMPTY_PHYSICAL_INTERSECTION, with the raw range preserved. A simultaneous inner witness would be a validation contradiction. This excludes only this specified conditional case, not global physical possibility.
For each nonempty inner vertex set, actual feasible probabilities obey their individual interval bounds. Therefore true extrema satisfy
  true_min in[outer_lower_clipped, min_Vin nhigh/D],
  true_max in[max_Vin nlow/D, outer_upper_clipped].
The inner endpoints are attained-witness bounds. The formula does not assert that an inner envelope range equals an attained probability range or exactly optimizes the curved true family.
FULL has ratio1 identically for every genuine feasible distribution. A displayed FULL=1 with only an outer surrogate is conditional and does not assert existence. Feasibility comes from an inner witness or a separate certificate.

## 10. Explicit positivity and predecessor comparison
Independently test any inner q by q(0),q(1), and q(-b1/(2b2)) if b2>0 and its stationary point lies inside(0,1). The smallest of those exact rational values is its global minimum.
For x=(mu+1)/2, the same polynomial has EXFOR11 folded degree4 Bernstein coordinates
  a0=b0+b1+b2,
  a1=b0-b2,
  a2=b0+b2-b1/3.
That is f=a0*(B0^4+B4^4)+a1*(B1^4+B3^4)+a2*B2^4.
A negative a_j is compatible with f>=0 and proves exclusion by the old sufficient coefficient cone, not by positivity itself. A simple analytic control is q(z)=(z-1/2)^2+1/100, whose a1 is negative.
Actual330MeV witnesses must be found by this fixed campaign; they are not presumed. Compare with the saved EXFOR11 result by its pinned hash only. Preserve every predecessor EMPTY/PASS/failure-history statement.

## 11. Strong no-go screen and limits
NG1 statement: only an exact fixed-family infeasibility may be claimed.
NG2 mechanism: identify the exhausted outer polytope or exact contradiction.
NG3 assumptions: explicit degree, endpoint, data, azimuth and geometry scope.
NG4 alternatives: signed coefficients, refinement, exact endpoint cone and stronger curved-cone approaches considered.
NG5 counterexample search: inner witnesses and a known positive polynomial outside the old cone are mandatory.
NG6 robustness: fixed N levels and row/moment enclosures separate algebraic exclusion from finite-resolution uncertainty.
NG7 conclusion: no universal angular-law, reaction, heating, production or cosmological no-go.
The complete physical response still needs normalized event/inclusive data and liquid-He projection; actual full angular/polarization law and photon history; named birth/deposition/thermalization and global species binding.
global_physical_completion=null;L4=false;production=NOT_APPROVED;activation=false.

