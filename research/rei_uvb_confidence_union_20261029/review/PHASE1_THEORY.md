# Independent source-only theory freeze

Status: PHASE1_FROZEN; analytic derivation complete; numerical execution NOT_RUN.
Reviewer task: `/root/uvb_theory_review`. Requested routing: Astra-tier independent
theory/review. Observed runtime model identity: unavailable; no identity inferred.

This record was derived before access to owner results, owner reports, code, or
other reviews. Scientific intake was only `intake/BLIND_SOURCE.json`, SHA256
`6e72099e6d3981ac731d5bed5ed70f6dabaa1514b7283613f3c258c4ec57e224`.
Its declared original source SHA256 is
`13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`;
that original object was not independently opened. AGENTS.md and the
physmath-research-loop skill/policies were read. Git metadata was inspected only
to preserve the checkout. Observed HEAD:
`d6657071ea0e36a1b2643cb3df990e4b1faa855a` on
`research/rei-uvb-confidence-union-20261029`.

## 1. Objects, signs, and required conditions

There are n=7 observations d, a fixed saved template m, an EOS response v, and a
correlated covariance C in dex squared. Put x_i=z_i-3.6, X=[1,x], and define
a=(b,kappa)^T through the affine correction X a. This defines the slope sign:
positive kappa means the corrected log residual increases with redshift.
The response to be fitted is exactly the source convention

    r(eta)=d-m+theta*v+j, eta=(theta,j),
    theta in [-1,1], j_i in [l_i,u_i].                         (1)

The deterministic domain H is the Cartesian product of these intervals; no
probability law or independence law is attached to theta or j. The EOS theta is
one shared scalar, whereas the seven Jeans coordinates vary independently in
the stated outer box. An outer box may be conservative relative to a physically
correlated admissible subset. Here all results refer to this declared box.

Require C real, finite, symmetric positive definite, and rank(X)=2. Distinct
source redshifts establish rank(X)=2 algebraically. Positive definiteness of the
particular C is a numerical prerequisite still to be checked, rather than an
observed result of this phase. Set W=C^{-1}, H_X=X^T W X, V=H_X^{-1},
A=V X^T W. b is in dex and kappa is in dex per unit redshift; x is dimensionless.
All inverses denote mathematical operators; implementation should use stable
linear solves/whitening, not materialize C^{-1} merely to fit two coefficients.

## 2. GLS and exact deterministic coefficient set

For Q(a;eta)=(r-Xa)^T W(r-Xa), differentiation gives H_X*a=X^T W*r.
Thus the unique fit and the completed square are

    a_hat(eta)=A*r(eta)=a0+g*theta+A*j,
    a0=A*(d-m), g=A*v,
    Q(a;eta)=Q_min(eta)+(a-a_hat)^T V^{-1}(a-a_hat).           (2)

Let j_c=(l+u)/2, j_h=(u-l)/2. For the given EOS interval,

    c=a0+A*j_c,
    G=[g, A*diag(j_h)],
    Z={a_hat(eta):eta in H}=c+G*[-1,1]^8.                    (3)

No assumption about G having eight independent columns is needed. For any dual
direction s in R^2, maximization over independent interval coordinates gives

    h_Z(s)=max_{a in Z} s^T*a=s^T*c+sum_k |(G^T*s)_k|.       (4)

An equivalent endpoint rule in original coordinates uses t_theta=s^T*g and
t_i=s^T*A[:,i]. Choose theta=+1 if t_theta>0 and -1 if t_theta<0;
choose j_i=u_i if t_i>0 and l_i if t_i<0. For a zero coefficient either endpoint
is valid; the midpoint is a deterministic tie rule. Lower witnesses use -s.
The witness must be evaluated through (1)-(2) to verify attainment; do not
report the componentwise envelope as one coefficient pair generally attained
at a common nuisance value. Each requested direction can use a different eta.

For coordinate e_k, the exact deterministic projection is

    [L_k,U_k]=[-h_Z(-e_k),h_Z(e_k)]
             =[c_k-sum_j |G_kj|,c_k+sum_j |G_kj|].           (5)

This is a geometric image of deterministic input bounds. It has no confidence
level. A direction scan approximates a boundary picture; it must not replace
(4)-(5) with sampled extrema when claiming exact support or projections.

## 3. Nested intercept versus intercept-and-slope improvement

Use the same response r(eta), nuisance eta, and covariance for both models.
For intercept-only fitting define

    M=W-W*1*(1^T*W*1)^{-1}*1^T*W,
    T=x^T*M*x>0,
    kappa_hat=(x^T*M*r)/T,
    V_kappa,kappa=1/T.                                     (6)

Eliminating the intercept reduces Q to a scalar quadratic in kappa. Therefore

    DeltaQ(eta)=Q_min,intercept(eta)-Q_min,affine(eta)
              =(x^T*M*r)^2/T
              =kappa_hat(eta)^2/V_kappa,kappa >= 0.          (7)

The positive sign is fixed by the order of subtraction. These identities are
pointwise at one eta; subtracting two separately optimized nuisance-profiled
Q minima is a different statistic and need not satisfy (7).

If [L,U] is the deterministic kappa projection, continuity and convexity give
every kappa in that interval. Hence the exact DeltaQ range is

    min = 0 if L<=0<=U, else min(L^2,U^2)/V_kappa,kappa,
    max = max(L^2,U^2)/V_kappa,kappa.                        (8)

When the minimum is zero inside the interval, a nuisance witness is a convex
combination of lower and upper kappa witnesses with weight chosen to make
kappa zero. A squared affine function need not attain its minimum at a box
vertex. Formula (7) alone is not a calibrated global significance calculation
for nuisance optimization or template selection.

## 4. Conditional Gaussian bridge

The following sampling assumptions are additional conditions, not facts
established merely by listing C in the intake:

    d=m+X*a_star-theta_star*v-j_star+epsilon,
    epsilon ~ N(0,C), eta_star in H.                        (9)

C is known and fixed; X, template m, response v, and H are fixed for repeated
sampling, or legitimately conditioned on independently of epsilon. The same
additive model is correct at the true nuisance, with no unmodeled template or
functional-form discrepancy. For each fixed true eta_star, (2) gives

    a_hat(eta_star)-a_star=A*epsilon,
    Cov[a_hat(eta_star) | eta_star]=A*C*A^T=V.               (10)

The equality follows directly by substituting A and cancelling W*C*W=W.
The covariance does not vary with eta because the nuisance shifts are
deterministic and C and X stay fixed. This does not assign the nuisance a
Gaussian prior and does not add box widths to C in quadrature.

For q>=0 define E_q={delta:delta^T V^{-1}delta<=q} and

    U_q(d)=union_{eta in H} {a:(a-a_hat(eta))^T V^{-1}
                                      (a-a_hat(eta))<=q}
          =Z(d)+E_q.                                      (11)

Both sets are compact convex, so their Minkowski sum is compact convex. Apply
Cauchy-Schwarz after writing delta=V^{1/2}u to obtain

    h_Uq(s)=h_Z(s)+sqrt(q*s^T*V*s).                        (12)

For s!=0, an attaining ellipsoid displacement is

    delta_s=sqrt(q)*V*s/sqrt(s^T*V*s).                     (13)

Combine (13) with the nuisance witness for h_Z(s). For q=0 use delta_s=0;
for s=0 use delta=0 and any nuisance. A confidence endpoint has both a nuisance
component and a statistical displacement; it generally is not a fitted center.
The full exact coordinate projection is

    [L_k-sqrt(q*V_kk), U_k+sqrt(q*V_kk)].                   (14)

For two-sided 95% coverage of one pre-specified scalar coordinate, choose

    q_single=chi_square_1^{-1}(0.95)
            =[Phi^{-1}(0.975)]^2.                         (15)

Using this q in (11) is convenient for support calculations, but the resulting
two-dimensional ellipsoids are not 95% joint ellipsoids. Their projection on
any one pre-specified scalar direction has the requested conditional 95%
coverage before nuisance union. Separate 95% coordinate statements do not
automatically have 95% simultaneous coverage.

For 95% coverage of the full two-coefficient vector, choose

    q_joint2=chi_square_2^{-1}(0.95)=-2*log(0.05).           (16)

With (9), the true-eta ellipsoid covers a_star with probability exactly 0.95;
it is a subset of the union in (11), so

    for every fixed eta_star in H and a_star in R^2,
    P_{a_star,eta_star}(a_star in U_q_joint2(d)) >= 0.95.    (17)

Similarly the coordinate projection with q_single covers the corresponding
true coordinate with probability at least 0.95. This is pointwise frequentist
coverage uniformly valid over the fixed allowed nuisance domain. No prior on
eta, multiple-testing penalty over eta, or random independent copies of the
ellipsoid are required: inclusion of the one true-eta set proves (17).
Coverage can be conservative. The proof does not claim exact 95% union coverage.

If C is estimated, Gaussianity approximate, H misses the true nuisance, m is
estimated/selected from these data, X or bounds are data-dependent, or the
additive affine mean is misspecified, (17) needs a justified replacement
sampling argument. A pure affine-model residual may be called a projection
parameter under a specified misspecification analysis, but the coverage theorem
above must not silently be transferred to a different physical estimand.

## 5. Statistical sign and scientific scope

Even L_kappa>0 does not imply a statistically resolved positive slope.
Under the conditional Gaussian assumptions a sufficient exclusion criterion
for the two-sided 95% scalar interval is

    L_kappa-sqrt(q_single*V_kappa,kappa)>0.                (18)

For sign exclusion using the 95% joint2 union, replace q_single by q_joint2.
To see the logical gap without numerical calculation, take a deterministic
slope set consisting of one point mu>0 and variance sigma^2 with
sigma>mu/Phi^{-1}(0.975). The deterministic lower bound is positive and its
two-sided Gaussian confidence interval includes zero. This counterexample is
an elementary inference distinction, not a novel strong no-go theorem.

No actual kappa interval, covariance positivity value, or statistical sign for
this source was computed in phase 1. A numerical conditional sign finding
would concern the fitted correction relative to the frozen template and the
specified seven observations, not a new IVP, physical closure, or broad
cosmological preference. This phase adds no physical scope.

## 6. Equation-to-code acceptance and remaining work

1. Verify finite 7-row dimensions, l<=u, symmetry and positive Cholesky factors
   of C; verify rank two after whitening X. Fail clearly if these prerequisites
   fail. Do not silently add jitter, discard correlations, or use a pseudoinverse.
2. Solve the whitened GLS with QR or another stable factorization and retain A,
   V, a0, g, c, G with named coordinate order (b,kappa).
3. Verify A*X=I, A*C*A^T=V, the GLS normal equations, and the quadratic
   completion. Use scale-aware residuals; a baseline relative tolerance of
   1e-10 and absolute tolerance of 1e-12 is prescribed for these small matrices
   unless observed conditioning makes it inadequate. In that case report the
   failure to the reviewer rather than changing the criterion silently.
4. Verify endpoint witnesses by direct response formation and GLS evaluation;
   compare (4) against endpoint-rule evaluation for both coordinate axes and
   their negatives and at least one oblique direction. Verify q=0 gives Z,
   the all-zero direction gives zero support, and fixed nuisance gives one
   ellipse. Floating sign ties can use an explicit zero-coefficient rule;
   do not discard a nonzero contribution just because it is small.
5. Verify (7) by direct nested residual sums of squares at the same eta and
   verify (8), including an interval straddling zero through an analytic
   synthetic check if the observed interval does not straddle zero.
6. Verify (12)-(14) and the confidence endpoint witnesses, including
   delta_s^T*V^{-1}*delta_s=q for s!=0 and q>0. Support witness errors use the
   same scale-aware tolerance. q must be explicitly labeled single-coordinate
   or joint2 and computed from (15) or (16), never from residual degrees of
   freedom n-p or an unrequested residual variance estimate.
7. Preserve the deterministic interval and the widened confidence intervals
   separately. Record conditional assumptions, q, V, lower/upper bounds and
   sign criterion, rather than converting a deterministic bound into a p-value.

This freeze completes the source-only derivation and mathematical contract.
Independent source review is complete in this scope. Numerical/implementation
checks and comparisons with owner output are pending phase-2 authorization.
No Python, C++, CAS, numerical run, new IVP, commit, push, merge, or production
gate change was performed. Quantiles above are analytic definitions.
