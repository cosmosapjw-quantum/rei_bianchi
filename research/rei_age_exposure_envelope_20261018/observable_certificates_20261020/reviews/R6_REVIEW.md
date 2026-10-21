# R6 independent theoretical review

Reviewer: /root/fresh_upstream_v8. Scope: THEORY_KO.md in OBSERVABLE_CERTIFICATES_20261020_V8. This review is independent of the author's derivation and the implementation executor. No solver run, benchmark repeat, or implementation admission is claimed.

## Finding and readiness

The mathematical formulas and assumptions are ready for the contracted implementation. There are zero mathematical blockers. One small dimensional wording correction was identified and is now closed: Section5 calls the cited dimensionless exponential difference identical to -k0, whereas k0 also includes the photon weight w. The author now explicitly substitutes x=Lambda(a+delta), y=Lambda*a and multiplies by w_i to obtain -k0. The targeted readback confirms the correction. This changes no implemented formula. Status: PASS_SCOPED, zero open findings.

## Endpoint identities checked independently

Write y=a+delta and x=a. Then n(y)-n(x)=wu(v-1)=-wuh. Expanding yv-x gives delta*v-a*h; expanding y^2*v-x^2 gives delta*(2a+delta)*v-a^2*h. Subtracting c times the number identity from the first-moment identity gives wu[delta*v-(a-c)h]. The A/B sign convention is consistent: A older gives these signed values, B older gives their negatives. At equal ages the exact difference is zero.

At Lambda=0, u=v=1 and h=0, so the passive number difference is zero and passive first/second moments retain w*delta and w*delta*(2a+delta). The centered passive first moment is independent of c. This confirms the important distinction between survivor-number agreement and age-moment agreement.

Energy E multiplies survivor difference. With positive total hazard, species cumulative-event difference is minus p_s times survivor difference. Nonnegative species hazards imply p_s>=0 and sum_s p_s=1. Thus species absolute envelopes sum to the number labelled envelope in exact arithmetic, including zero passive contribution. Outward endpoint equality is unnecessary.

The stated units match all formulas: k0 has photons/H, k1 and kc have photon*s/H, k2 has photon*s^2/H, U has eV/H, and p_s is dimensionless. Center c must have seconds, as implemented by selecting it from a mean-age interval.

## Fallback Lipschitz estimates

For x=Lambda*a>=0, |1-x|exp(-x)<=1. On [0,1] it decreases from1; on [1,infinity) its maximum is exp(-2) at x=2. Hence f1(a)=a exp(-Lambda*a) is globally1-Lipschitz on nonnegative ages.

For f2(a)=a^2 exp(-Lambda*a), |f2'(a)|=a|2-x|exp(-x). On [0,2] the second factor is at most2; on [2,infinity) its maximum is exp(-3), at x=3. On an age interval bounded by Amax this proves |f2'|<=2Amax. Multiplying individual age displacements by their nonnegative unchanged weights and summing yields the two stated fallbacks. No positive lower hazard is needed.

## Normalized mean and signed-total correction

Independently expanding the quotient difference gives
mu_A-mu_B=(N_B*DeltaM1-M1_B*DeltaN)/(N_A*N_B)
          =(DeltaM1-mu_B*DeltaN)/N_A.
Adding and subtracting c*DeltaN yields the stated centered identity. The triangle inequality then proves the bound with B(c) and any E0>=|DeltaN|. E0 need not bound each labelled difference or their absolute sum. Therefore using the outward stable SIGNED total number difference is valid and can retain cancellations.

For an interval I_B containing mu_B and a represented finite center c, r_B=max(|I_B.lo-c|,|I_B.hi-c|) contains |mu_B-c|. Its outward arithmetic must be retained. The numerator bound is divided by a certified strictly positive N_A lower endpoint. Reversing A/B yields a second valid bound. The fallback follows from |DeltaM1|<=C, mu_B<=Amax and |DeltaN|<=L0. Taking the minimum of these independently valid bounds is valid.

Every subset must use its own mass and age moments. All-node mass cannot substitute for a sensitive-subset denominator. Empty or unresolved-positive masses correctly produce no finite normalized certificate. No universal optimum over centers is claimed.

## Exact representation and interval premises

Binary64 inputs are interpreted as exact dyadic values. Ages and total species hazard are exact differences/sums in that model. Signed moment and centered intervals must not be evaluated with a nonnegative-only clamp. Subnormal passive and sensitive terms remain governed by the reused certified exponential arithmetic. These are implementation premises to be checked by C6–C9, not additional mathematical assumptions invented by this review.

## Literature and scope

The actual Catalano–Lijoi–Prünster author paper contains the scalar exponential identity and Jensen argument in Theorem9/§6.7. The finite labelled deterministic adaptation is valid without importing that paper's Bayesian random-measure model. Its weighted optical-depth term cannot be replaced by age-marginal W1 in the presence of hazard/age correlation. The related normalized-density paper is correctly identified as background rather than a directly imported REI theorem.

The new work remains a fixed exported coefficient model with same source labels, energy and hazards. No nonlinear Grackle bound, new native age/time convergence, production admission or new strong no-go follows from these formulas. The source-age/native admission statuses are preserved.

## Verification budget

One theory pass, one requested wording correction, then targeted closure. No new numerical execution, no full historical rerun and no adjacent proof obligations were added.

