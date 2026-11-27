# EXFOR11 mathematical result and implementation contract
Convention: signature(-,+,+,+), A=m_alpha c^2, M=m_d c^2, e=E_gamma in MeV; c,hbar,k_B retained. This construction concerns fixed-energy data-constrained angular reference families.

## 1. Measured quantities and declared family
The source provides four nominal CM polar angles46°,61°,73°,87° at each e=213,258,330MeV. Let y_i,s_i be literal DATA-CM and ERR-S in nb/sr. This study declares L_i=max(0,y_i-s_i), U_i=y_i+s_i. The statistical correlations, systematic errors, liquid-target projection and full azimuth/polarization law are not supplied by those numbers. Accordingly [L_i,U_i] are a deterministic sensitivity-window choice, not confidence coverage.

For even n in{4,8}, x=(mu+1)/2 and m=n/2 define
B_j^n(x)=binom(n,j)x^j(1-x)^(n-j),
psi_j(mu)=B_j^n(x)+B_(n-j)^n(x) for j<m, and psi_m=B_m^n(x).
Let f_a(mu)=sum_j a_j psi_j(mu), a_j>=0.
Then f_a is even and nonnegative on[-1,1]. In the endpoint-zero subfamily a_0=0, because f_a(±1)=a_0. This cone is a sufficient certificate family; general positive polynomials can have Bernstein coefficients outside it.

The normalization coefficients follow from beta integration:
integral_-1^1 B_j^n((mu+1)/2)dmu=2/(n+1).
Thus d_j=4/(n+1) for j<m and d_m=2/(n+1), and D(a)=d^T a.
A direct computational primitive is obtained by expanding (1+mu)^j(1-mu)^(n-j)/2^n and integrating every exact rational monomial. No angular quadrature is needed.

## 2. Nominal-angle evaluation with an enclosure
Set mu_i=cos(theta_i*pi/180). The inherited fixed rational trigonometric certificate is called at turns theta_i/720, since4pi*(theta_i/720)=theta_i*pi/180.
For any rational enclosure mu_i∈[m_i^-,m_i^+], x and1-x are nonnegative interval quantities. Multiplication of their nonnegative powers and multiplication by exact binomial coefficients encloses each Bernstein basis term. Adding the pair and rounding outward to grid2^-60 yields rational l_ij<=psi_j(mu_i)<=u_ij.
For the four interior angles and either declared family every l_ij is strictly positive; the implementation checks this rather than assuming a floating result is exact.

This construction propagates numerical representation of the nominal angle. It does not assign an experimental angle-error distribution.

## 3. The exact polytope sandwich
Write
P_true={a>=0: L_i<=sum_j psi_j(mu_i)a_j<=U_i for all i}.
Define the outer polytope
P_o={a>=0: l_i^T a<=U_i, u_i^T a>=L_i},
and the inner polytope
P_i={a>=0: u_i^T a<=U_i, l_i^T a>=L_i}.

For a>=0, summing componentwise bounds gives l_i^T a<=f_a(mu_i)<=u_i^T a.
If a∈P_i, both exact data inequalities follow, so a∈P_true.
If a∈P_true, its upper and lower inequalities imply the necessary outer inequalities, so a∈P_o.
Therefore P_i subset P_true subset P_o.

These are two uses of interval bounds with different logical directions. Treating every point in the outer set as an actual fit would reverse the first implication. Inner points supply constructive nominal fits; outer points supply conservative bounds.

### Compactness and positive normalization
Select any observed row with l_ij>0 and finite U_i. For every a∈P_o,
0<=a_j<=U_i/l_ij.
Both polytopes are closed and bounded. At least one L_i>0 gives u_i^T a>=L_i, excluding a=0. Since each d_j>0, D(a)>0 on every nonempty feasible polytope.

A uniform explicit denominator lower bound is available from
u_i^T a <= max_j(u_ij/d_j) D(a):
D(a)>=L_i/max_j(u_ij/d_j)>0 for any row L_i>0.
The code separately checks every saved vertex denominator exactly. Boundedness/nonzero claims are not inferred merely from finite optimization output.

## 4. Exhaustive finite vertex construction
For A a<=b in r variables, enumerate every r-element subset of inequality rows, including all nonnegativity rows. For an invertible subset solve exactly over the rationals, retain the solution only if all inequalities hold, and deduplicate identical vectors.
Every vertex of a polyhedron in R^r has r linearly independent active inequalities. Conversely a feasible point with r independent active equalities is a vertex. Thus this procedure returns exactly all vertices, including vertices of lower-dimensional bounded feasible sets. A nonempty bounded polyhedron is the convex hull of its vertices; therefore no retained vertex means the specified bounded polytope is empty.

All3energy cases share a coefficient matrix for each degree/endpoint/inner-outer choice. Its exact inverse can be reused with different right sides without sharing physical source amplitudes between energies.
Counts of attempted bases, singular bases, feasible bases and unique vertices are distinct and are all saved.

## 5. Same-event detector acceptance
In fixed rest-energy variables define s=A^2+2Ae, H=s-4M^2>0, G=A+e, R=H/s.
The inherited lab direction map is
F(mu)=(e+G sqrt(R)mu)/sqrt[(e+G sqrt(R)mu)^2+H(1-mu^2)].
The two daughters of one event have directions(F(mu),t) and(F(-mu),t+1/2 mod1), t=phi/(2pi).
The coincidence event is C=(A_plus∩B_minus)∪(A_minus∩B_plus). It is not the product of independent single-particle probabilities.

Each azimuth strip has certified polar sets C^- subset C subset C^+. For each nonnegative psi_j integrate its exact primitive over C^- and C^+, multiply by exact strip length and sum. This gives
0<=c_j^-<=c_j<=c_j^+<=d_j.
The fixed new geometry tolerance is delta2^-48. The actual coefficient widths are reported; no predecessor blanket relative error guarantee is transferred to these ratios.

We evaluate FULL(A=B=whole sphere), HEMISPHERES(A forward,B backward), and CAPS(A labcos>=1/2,B labcos<=-1/2), all with full-turn azimuth. Thus c=d exactly for FULL.
Physical angular masses and selected geometry are held fixed throughout each energy's family optimization.

## 6. Linear-fractional extremum theorem
For a nonempty polytope P and c fixed, R_c(a)=c^T a/(d^T a), with d^T a>0.
Write a=sum_v lambda_v v, lambda_v>=0,sum lambda_v=1.
Then
R_c(a)=sum_v [lambda_v d^T v/(d^T a)] R_c(v).
The coefficients in brackets are nonnegative and sum to1. Therefore the global min and max occur at vertices. No differentiability, floating optimizer or local-optimum test is required.

Every true fit lies in P_o, hence its actual acceptance p_C satisfies
min_(v∈V_o) (c^-·v)/(d·v) <= p_C <= max_(v∈V_o) (c^+·v)/(d·v).
Both endpoints are exact rational numbers and have coefficient witnesses for the corresponding outer problems.

For inner witnesses w∈P_i, the actual p_C(w) lies in[(c^-·w)/(d·w),(c^+·w)/(d·w)]. These intervals show constructive nominal fits and their geometry enclosures. Their endpoints are not asserted to be the exact attainable range of P_true. If P_i is empty but P_o is nonempty, feasibility of P_true remains unresolved by this sandwich; if P_o is empty, that particular declared family/window combination is incompatible.

## 7. Model choices and nesting
Endpoint-zero is a subfamily of the endpoint-free model at a fixed n. For degree elevation4→8,
b_k^(8)=sum_i b_i^(4) binom(4,i)binom(4,k-i)/binom(8,k),
where only valid indices are included.
Weights are nonnegative, preserve the represented polynomial and preserve symmetric coefficients. Endpoint-zero is preserved. Thus the exact n4 family is contained in n8 for the same nominal data windows. This explains why allowing degree8 can widen physically conditional acceptance possibilities; it is model flexibility, not a statistical confidence claim.
The small independent row-rounding boxes can make numerical sandwich endpoints differ from ideal nesting by their explicit enclosure uncertainty; saved exact results are interpreted with that distinction.

## 8. Normalization and physical meaning
At fixed e suppose dm_e=K(e) f_a(mu)dmu dt with one common K(e)>0. K may contain2pi, unit conversion, a calibration factor, or an event-vs-inclusive factor.
p_C=integral_C dm_e/integral dm_e=c^T a/(d^T a); K cancels separately at each fixed energy.
Angle-dependent response does not cancel this way. In energy-integrated observables, a varying factor inside the energy integral generally changes the weighting and cannot be canceled globally.
The analysis therefore makes progress on shape-dependent response while keeping absolute event rates and heating input-gated.

The Rice total-cross-section convention supplies an explicit primary example of identical-particle normalization. Its discussion of Arends endpoint fits motivates the two extrapolation assumptions. M0475003 totals at201/225/253/285/320/359MeV are not same-energy constraints on213/258/330MeV shapes and are not interpolated into the model.

## 9. Admission boundary and executable obligations
The result to be admitted is an exact bounded finite-family sensitivity reference: original rows→nominal-angle enclosure→inner/outer polytopes→same-event functional→verified ratio bounds.
NG1–NG7 are checked for applicability: no new strong global no-go or literature-wide novelty is proposed. Any empty family only has the quantified finite-model meaning proved in§3–4.
The three inherited physical inputs remain open: actual normalization/liquidtargetprojection; actual full law and photon encounter history; named birth/deposition/thermalization/global species binding.
Binding remains single-owned by population_rest_energy_witness; thermal ports and globalphysicalcompletion remain null, L4false, productionNOT_APPROVED.

