# TANGENT13: constructive full-positive quartic minimum certificates

Root derivation, R5, 2026-10-28. Conventions and all frozen physical inputs are in CONTRACT.md. We derive a computational certificate for the two258MeV aperture minima under the full nonnegative even-quartic model. Every actual certificate condition is checked by the new single campaign. General positivity and fractional-program connections are cited in sources/TANGENT13_PRIMARY_SUPPORT_KO.md; the proof below uses elementary weak duality and exact polynomial algebra.

## 1. Fixed family, signed coefficients and normalized aperture
Let z=mu², mu=cos(theta_cm), q_b(z)=b0+b1*z+b2*z² and f_b(mu)=q_b(mu²). The full true family T is defined by q_b>=0 on[0,1] and the four literal EXFOR sensitivity windows at the four exact nominal cosines. All b are real and may have either sign. Coefficients are measured in nb/sr. Uniform azimuth is a declared inherited model assumption.
With d=(2,2/3,2/5), D(b)=d.b is the integral of f over mu. The normalized same-event aperture is P_g(b)=k_g.b/D(b), where the inherited moment k_g integrates(1,mu²,mu⁴) over the same-event detector union. The measured absolute event/inclusive convention cancels from this ratio only insofar as it is an overall common DCS factor. It is still required for any absolute event-rate interpretation.

The inherited proofs imply |b_j|<=B=160 and D>=Dmin=49/4800000 for every b in T. These consequences make T compact and keep the ratio continuous. An actual feasible witness establishes nonemptiness; compactness then guarantees its minimum exists. We do not assume the old finite inner cone exhausts T.

## 2. Transfer of exact nominal-angle uncertainty
The saved rational row m_i=(1,mid(z_i),mid(z_i²)) has an error bound epsilon_i satisfying
 |q_b(z_i)-m_i.b|<=epsilon_i
on the inherited containing box. Thus true feasibility implies m_i.b>=L_i-epsilon_i and <=U_i+epsilon_i. Conversely m_i.b between L_i+epsilon_i and U_i-epsilon_i implies the true nominal-angle window. Define the expanded bounds L_i^o,U_i^o and contracted bounds L_i^i,U_i^i accordingly.
No new trigonometry is computed. The exact row identity is inherited from the pinned source bytes and the previous completed reference.

## 3. A useful nonnegative linear functional from the data
Use the61degree lower bound and73degree upper bound. Require L_61^o>=0 and U_73^o>0, as holds for the fixed windows. Set rho=L_61^o/U_73^o and
 h=m_61-rho*m_73.
For any true feasible b,
 h.b=m_61.b-rho*m_73.b>=L_61^o-rho*U_73^o=0.
The sign of rho is essential to this inequality. The other two rows are retained in the family and checked for the feasible witness, although they are not required by this lower-bound certificate.

## 4. Evaluation functional and a global lower-bound certificate
For each r in[0,1], v(r)=(1,r,r²) belongs to the dual of the full nonnegative-quadratic cone because v(r).b=q_b(r)>=0 for every b in T.
Suppose exact numbers alpha,lambda,mu satisfy
 k_mid-alpha*d=lambda*h+mu*v(r),  lambda>=0, mu>=0.
Taking the dot product with arbitrary b in T yields
 k_mid.b-alpha*D=lambda*h.b+mu*q_b(r)>=0.
Since D>0, k_mid.b/D>=alpha for ALL b in T. There is no inference from a grid of tested b, no assumed optimizer convergence and no assumption that an enumerated list of curved-boundary candidates is complete.
The three coefficients(alpha,lambda,mu) are obtained by solving the3×3linear system whose columns are(d,h,v(r)). Exact residual0 and multiplier signs are necessary certificate conditions. If the system is singular or a multiplier is negative, this candidate certificate fails without excluding the physical family.
An approximate rational r is sufficient: the evaluation inequality is true at every r in[0,1]. Therefore root-rounding uncertainty does not need a separate subtraction from alpha after the exact dual identity has been checked.

## 5. Locating a complementary square boundary
A nonzero convex quadratic touching zero at an interior point has the form q(z)=a(z-r)², a>0. Its coefficient vector is b=a(r²,-2r,1). For a midpoint row define
 w_i(r)=r²-2*m_i[1]*r+m_i[2].
Then m_i.b=a*w_i(r), including the fact that the independently enclosed m_i[2] need not equal m_i[1]².
Equality at the selected lower/upper rows requires a*w_61=L_61, a*w_73=U_73, so r satisfies
 F(r)=U_73*w_61(r)-L_61*w_73(r)=0,
with ascending coefficients
 (U_73*m_61[2]-L_61*m_73[2], -2U_73*m_61[1]+2L_61*m_73[1], U_73-L_61).
Both the expanded and contracted systems use this exact quadratic. On the fixed interval[4/5,9/10], check opposite endpoint signs and positivity of F' at both endpoints. Since F' is affine, it is positive throughout. The intermediate-value theorem and strict monotonicity give one root in this interval. Eighty exact bisections enclose it with width<=1/(10*2^80); exact midpoint roots terminate with zero width. This is local root isolation, not a claim about other roots outside the interval.
The outer root midpoint supplies r for the dual. Its usefulness is judged by the independently checked dual signs and final bracket, not assumed from the root equation alone.

## 6. A rational feasible witness, including its scale
Take r_in as the upper endpoint of the contracted root bracket. Then F_inner(r_in)>=0. If w_61,w_73>0,
 a_low=L_61^i/w_61(r_in),  a_high=U_73^i/w_73(r_in)
satisfy a_low<=a_high, because cross multiplication is exactly F_inner>=0. Choose their midpoint a.
Require a>0, r_in in[0,1], the coefficient box and Dfloor, and verify all four contracted data rows. Then q=a(z-r_in)² is nonnegative for EVERY z, and the contracted rows imply all true nominal-angle windows. Its existence proves T nonempty. The polynomial can touch zero inside the domain; no strict-positivity margin is required.
For this fixed witness compute the sign-aware moment bounds
 n_low=sum_j b_j*(k-_j if b_j>=0 else k+_j),
 n_high=sum_j b_j*(k+_j if b_j>=0 else k-_j).
Dividing by its exact D>0 encloses its actual aperture probability. Hence min_T P<=n_high/D=:U_witness.

## 7. Uniform correction for uncertain moments
The physical moment vector lies componentwise in the saved interval[k-,k+]. A midpoint objective certificate alone does not certify the physical moment objective.
The already certified258MeV outerN16 polytope P contains T and has the complete saved vertex set V. Every vertex has positive D. For b=sum_v t_v*v, t_v>=0,sum t=1,
 b_j/D(b)=sum_v omega_v*v_j/D(v),
 omega_v=t_v*D(v)/D(b)>=0, sum omega=1.
Consequently |b_j|/D(b)<=max_v |v_j|/D(v)=M_j. The old completeness proof and exact identity are reused; the new reader checks saved constraints/denominators and the finite maxima without re-enumerating vertices.
With k_mid=(k-+k+)/2,
 |(k-k_mid).b|/D <=sum_j |b_j|/D*(k+_j-k-_j)/2 <= Delta_k,
 Delta_k=sum_j M_j*(k+_j-k-_j)/2.
This bound is valid for either sign of every coefficient. Combining with section4 gives P_g(b)>=alpha-Delta_k on all T.

## 8. Minimum bracket theorem and error accounting
Under the checked conditions in sections2–7,
 max(0,alpha-Delta_k) <= min_{b in T} P_g(b) <= min(1,U_witness).
Clipping uses the genuine nonnegative normalized probability interpretation and does not claim physical feasibility for a surrogate outer vertex. Feasibility is separately supplied by the square witness.
Both endpoints and their difference are exact fractions. We require width<=10^-10 and containment in the predecessor exact minimum bracket. The two geometries get separate(alpha,lambda,mu,Delta_k) but may share rows, root brackets, coefficient envelope and the feasible square witness.
The final width contains the expanded/contracted-row gap, finite rational candidate difference and saved moment enclosure. Root interval width is reported separately. Delta_k is reported explicitly. We do not identify the final numerical bracket with experimental error or a joint statistical confidence interval.

## 9. Independent controls and constructive example
CONSTRUCTION_AND_EXECUTION.md contains an exact manufactured case with r=17/20, q=(z-r)², active rows1/4 and1/10, positive multipliers1/2 and1/3, and exact optimum1/4. It tests the relationship between square feasibility and dual optimality without importing EXFOR values.
The code verifier reads saved certificates and checks polynomial/root inequalities, dual algebra, all four witness rows, normalized coefficient bounds, signed moment envelopes, interval width and decimal rounding. It does not solve for the candidate or rerun geometry. Wolfram separately checks the generic polynomial formulas and manufactured exact arithmetic. A nonauthor reviewer reads the proof, source, actual output and figure.

## 10. Interpretation and admission boundary
This construction improves two minima for one fixed full-positive quartic/data family. It does not add an angular law measurement, a photon history, an event/inclusive normalization, a medium/response kernel or a nonthermal/binding source. The three physical obligations stay open and the central completed count stays28/88 with HEdelta0. New local scientific acceptance adds one scoped reference, giving13/17 after independent admission.
No strong no-go is proposed. The result is a constructive feasible witness plus quantified minimum bounds. NG1–NG7 are screened at R8 to keep exclusion/novelty claims aligned with actual proofs and literature. Earlier finite-family exclusions, initial failures and inherited partial workflows remain unchanged.
