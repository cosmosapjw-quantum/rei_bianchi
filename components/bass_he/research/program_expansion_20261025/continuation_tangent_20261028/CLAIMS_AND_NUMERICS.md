# R3 claim alignment / C3 exact numerical design

## Mathematical object
Fix nominal theta=(46,61,73,87) degrees at E_gamma=258MeV, and the literal sensitivity windows in CONTRACT.md. Let z_i=cos(theta_i)^2. The true family T consists of real b=(b0,b1,b2) satisfying q_b(z)>=0 for every z in[0,1] and L_i<=q_b(z_i)<=U_i for every row. The inherited coefficient box |b_j|<=160 and denominator floor d.b>=49/4800000 are proved consequences, not new model priors. T is closed and bounded; the positive floor makes each aperture ratio continuous. Once a feasible witness is checked, the minimum is attained on this compact nonempty family.

The physical aperture moment k is the integral of (1,mu²,mu⁴) over the inherited same-event coincidence set. Its saved interval [k-,k+] is reused exactly. P_g(b)=k.b/(d.b), d=(2,2/3,2/5). Coefficients and D have nb/sr units; P, k, d, roots and dual multipliers are dimensionless. Overall DCS normalization cancels here; absolute event rate requires separately owned physical input.

## Claims and evidence classes
T1 DERIVED: h=m61-(L61outer/U73outer)m73 has h.b>=0 for every b in T; positivity of the used bounds is checked.
T2 DERIVED: for r in[0,1], exact k_mid-alpha*d=lambda*h+mu*(1,r,r²), lambda,mu>=0, implies midpoint ratio>=alpha on all T.
T3 REUSED+DERIVED: old outer polytope vertices enclose T; their maximum |b_j|/D bounds normalized coefficient magnitudes on T.
T4 DERIVED: |P-k_mid.b/D|<=Delta_k=sum M_j*(k+_j-k-_j)/2. This statement includes signed b.
T5 DERIVED construction, pending actual verification: an inner-row root bracket supplies a rational square q=a(z-r_in)² satisfying all four sensitivity windows.
T6 CONDITIONAL certificate theorem: given checked T1–T5, min_T P lies in [alpha-Delta_k,U_witness]. Exact code validates the width and prior-bracket inclusion.
T7 UNRESOLVED physical inputs: actual angular/polarization law, event normalization/medium response, flux history, named birth/deposition/thermalization/global species binding retain their owners and null fields.

The chosen active pair is an inference from saved prior extremal witnesses, not a proof of optimality. The dual identity is the global lower-bound proof. This avoids assuming an exhaustive search of all possible positivity-boundary mechanisms. The feasible witness supplies an upper bound without claiming its midpoint decimal is the exact optimum.

## Exact algorithm and error design
Read immutable bytes and check hashes. Select only258/free_N16. Construct inner/outer row bounds from the stored rational epsilon. Derive two ascending quadratic F polynomials. Check opposite endpoint signs and a strictly positive affine derivative over[4/5,9/10]. Eighty rational bisections give width<=1/(10*2^80), or an exact rational root gives width0.
Use outer root midpoint solely as a candidate evaluation functional; exact3×3 elimination yields alpha,lambda,mu. Check all residual components equal0 and both multipliers nonnegative. These checks certify the lower bound independently of root-rounding error.
Use inner root upper endpoint; positive F there makes a nonempty amplitude interval. Select its midpoint and verify the exact square coefficients and all contracted row inequalities. Fixed four windows, B and Dfloor remain unchanged. No outcome-based angle/window/model/tolerance adjustment is allowed.
Compute normalized coefficient envelopes from the saved outer vertices and check their stored inequalities. Denominator-weighted Jensen, proved in THEORY.md, supports the reduction. Exact moment uncertainty enters Delta_k, so it is not hidden by root bisection.
Emit exact rational endpoints. For human-readable decimal endpoints use a fixed decimal integer grid with floor(lower*10^16)/10^16 and ceil(upper*10^16)/10^16. Binary64 numbers are display/plot values only. The certificate reader parses decimal strings as rationals to verify enclosure direction.

## Domain and failure classification
Missing immutable input/hash: input-dependency failure. Wrong root signs or negative dual multiplier: this fixed candidate failed and requires a mathematical diagnosis; no physical exclusion follows. Singular3×3 solve: algorithm/candidate failure. Witness row violation: implementation or candidate error. Excess bracket width: computational target not met, preserving exact available bracket. Timeout: environment/resource result. None is automatically a global no-go.

An optional exact SOS/2×2PSD formulation is a literature-supported alternate representation of the full positivity cone. This implementation uses the directly proved evaluation-functional subset of its dual and does not require an SDP numerical solver or strong-duality theorem.

R3 complete: definitions, assumptions, reused and derived claims, pending actual conditions and physical obligations are separated.
C3 complete: continuous object, exact rational operations, certified row/moment errors, numerical stopping criterion and independent validation interfaces are fixed.
