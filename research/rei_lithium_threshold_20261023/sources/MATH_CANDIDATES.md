# ANGTHERM02 independent mathematical candidate assessment

Role: independent Astra theory intake, no new IVP and no implementation edits.
Source: ANGTHERM01 `THEORY.md`, `code/angular_model.py`, `code/run_cases.py`,
`results/species_analysis.json`, and saved `grid044_M16_tight.npz`.

## Recommendation

Use a clearly identified **late-time trace-Li subproblem on a frozen thermal
and electron history**, and integrate the known moving angular support directly.
This isolates the unresolved threshold quadrature error at very low cost. It
does not replace the completed coupled ANGTHERM01 calculation or claim a newly
conserved full photon/gas evolution. It is preferable to silently moving photon
quadrature nodes and treating their new locations as old photon histories.

The full coupled angular-continuum problem remains a later task. A fixed-node
refinement is a useful control but does not, by itself, remove the discontinuous
support that produced the slow Li convergence.

## 1. Evidence from saved arrays (zero IVPs)

At the final sample of the M16 tight calculation, the 10 eV cohort's 16 optical
depths range from `3.19744698e-9` to `5.617874831337621e-9`. The cumulative depths
are monotone in the model. In contrast, final depths for the other five energy
bins are at least `301729.8, 336479.0, 215263.3, 90173.9, 36493.6` respectively.

At `eta_star = 0.10702505819804223`, the summed count of the 150 eV cohort is
approximately `1.3108876e-317` per Href and all other cohorts above 10 eV have
underflowed in the saved count representation. Their saved log counts must be
used to evaluate a rigorous numerical tail estimate; raw zero is not a proof
of mathematical extinction. The common history then has T about 8115.99 K and
v about 0.217531/Href. At eta zero, Li is entirely LiII.

The largest native Li M8/M16 difference occurs at eta `0.7102572044051894`.
The active angular interval there is approximately `0 <= mu0 <= 0.25804648`.
Thus the error concerns a moving finite-width support edge, not only an
unresolved singular limit at the final ray's crossing.

These observations motivate the approximation. They do not alone certify an
angular continuum solution.

## 2. Fixed-q measure and the moving support

Let a 10 eV cohort have initial density `G0 = 0.05` per Href per unit mu0 on
`0 <= mu0 <= 1`, after using the existing reflection/azimuth quotient. Define

    A = exp(2b), B = exp(-4b),
    E(eta,mu0) = E0 exp(-eta) sqrt(A + (B-A) mu0^2).

For b>0, energy decreases with mu0. Above the LiI threshold chi=5.392 eV,

    mu_c^2 = [(chi/E0)^2 exp(2eta)-A]/(B-A).

If E(eta,0)<chi the active interval is empty; if E(eta,1)>=chi it is the
whole interval; otherwise it is `[0,mu_c]`. Testing these physical endpoint
energies before taking the square root is more robust than clipping a generic
mu_c^2 formula. The equality convention at a single boundary does not change
the continuum integral. b=0 is a separate all-or-none common threshold. For
b<0 the partially active interval is `[mu_c,1]`.

Define k(eta,mu0)=(c nHref/H) sigma_LiI(E), with sigma in cm^2. The optically
thin rate per LiI target per eta is

    Lambda0(eta) = G0 integral_active k(eta,mu0) dmu0.

Use Gauss-Legendre nodes on this **integration interval**, including its width
in the weights. The measure is dmu0; there is no extra physical-angle Jacobian.
This evaluation does not define moving photon packets. Its nodes are sampling
points for the rate integral, not material cells carrying earlier optical depths.

For b>0 partial support, a [0,1] Gauss rule gives

    Lambda0 ~= G0 mu_c sum_j w_j k(eta,mu_c x_j).

The integrand is smooth within this interval. Independent GL orders and a
separately implemented adaptive integral can test quadrature error on the
actual background. Their differences are observed estimates, not a theorem
of asymptotic order.

## 3. The scalar late-Li equation

Freeze a declared interpolation of the accepted ANGTHERM01 T(eta), v(eta),
and the already frozen H,n,b history. Let

    r_q(eta) = (nHref/H) v alpha_q(T), q=1,2,3.

After bounding the residual high-energy photon tail, Li obeys

    f3' = -r3 f3,
    f2' = r3 f3-r2 f2,
    f1' = Lambda f0-r1 f1+r2 f2,
    f0' = r1 f1-Lambda f0.

Here f0,f1,f2,f3 denote LiI through LiIV. Since the upper two charge states
have no 10 eV photoionization, their evolution is independent of Lambda.
Let cLi=1-f2-f3. Then

    f0' = r1 cLi-(r1+Lambda) f0,
    f1 = cLi-f0.

For numerical fraction outputs retain a directly evolved f1 if cancellation
is relevant. The scalar formula is a proof and integration simplification;
it does not authorize a numerically unstable output subtraction. The Markov
generator has nonnegative off-diagonal entries and zero column sums, so the
continuum system preserves positivity and sum f=1.

The exact scalar propagator is

    f0(t) = exp[-integral_s^t (r1+Lambda)] f0(s)
          + integral_s^t exp[-integral_u^t (r1+Lambda)] r1(u)cLi(u) du.

Thus there is no need to evolve every photon ray merely to obtain the
threshold-sensitive trace fraction in this conditional subproblem.

## 4. A conditional attenuation bound that does not use a small-number guess

Keep the exact late-time continuum photon equation as the mathematical
reference:

    g(eta,mu0) = G0 exp[-tau(eta,mu0)],
    tau' = YLi k(eta,mu0) f0(eta), YLi=5.0001e-10,
    Lambda = G0 integral k exp(-tau) dmu0.

Suppose a bound `0 <= tau <= delta` holds. Then

    exp(-delta) Lambda0 <= Lambda <= Lambda0.

Let f_thin and f_exact share the same initial Li fractions and thermal/electron
bath. The upper states and cLi coincide. Scalar comparison gives
`0 <= f_exact,0-f_thin,0`. Writing d=f_exact,0-f_thin,0,

    d' = -(r1+Lambda)d + (Lambda0-Lambda) f_thin,0.

Because `Lambda0-Lambda <= (exp(delta)-1) Lambda` and `0<=f_thin,0<=1`,

    0 <= d(t) <= exp(delta)-1.

The LiII difference has the opposite sign and equal magnitude; LiIII/IV are
unchanged. The L1 fraction error is at most `2[exp(delta)-1]`. This bound is
uniform in the size/stiffness of Lambda, and is more useful than an unstable
generic Lipschitz/Gronwall bound. It is conditional on the declared bath and
initial radiation profile.

### Closing the assumption by a bootstrap envelope

Choose delta before the experiment (the controller proposes 2e-8), and solve the comparison
equation with `Lambda_delta=exp(-delta)Lambda0` and the same cLi and initial
state. Let its neutral fraction be f_delta. Until any first crossing of
tau=delta, scalar comparison gives `f_exact,0 <= f_delta`.

For a nonnegative initial optical profile with a known upper bound tau_star,

    tau(eta,mu0) <= tau_star
       + YLi sigma_max integral_eta_star^min(eta,eta_last)
                         (c nHref/H) f_delta(s) ds.

If the right side is strictly below delta over the interval, a first crossing
is impossible. This closes the attenuation bound. A numerical evaluation of
this envelope needs an explicit integration/quadrature error allowance; do
not label a floating-point number a formal rigorous certificate without it.

The original M16 optical depths suggest a generous numerical margin, but the
new scalar comparison and envelope must actually be evaluated before admission.

### Preferred controller refinement: close the prehistory from eta zero

The controller's proposed global envelope improves the initial-data treatment.
Keep the same declared frozen T,v bath on the whole interval from eta=0, and
define the upper scalar function F_delta by

    F_delta' = r1(1-F_delta)-exp(-delta)Lambda0 F_delta,
    F_delta(0)=0.

For the complete Li chain, any extra higher-energy LiI photoionization is a
nonnegative sink and fII<=1-fI. While tau10<=delta,

    fI' <= r1(1-fI)-exp(-delta)Lambda0 fI.

Scalar comparison therefore gives fI<=F_delta independently of the higher
charge fractions and the unmodeled-in-this-bound higher-energy optical histories.
The global bootstrap quantity is

    B(eta) = YLi sigma_max integral_0^min(eta,eta_last)
                            (c nHref/H) F_delta(s) ds.

If B(eta_last)<delta after numerical integration uncertainty is included,
the continuum prehistory and late interval have tau10<delta on this frozen
bath. This avoids assuming that M16's nodal optical depths certify an unknown
continuum profile. The endpoint eta_last is the transverse threshold crossing;
on grid044 it is approximately 0.72799989168701.

If the late problem is seeded with the saved M16 Li fractions rather than the
unknown continuum state at eta_star, explicitly check
`fI_saved(eta_star)<=F_delta(eta_star)`. If not, an upward reset of **the bound**
at eta_star gives a valid piecewise comparison problem; this is not a clipping
of the physical Li solution. The reset and added envelope area must be reported.

A saved-array trapezoid of the same sigma_max envelope using the *actual M16*
neutral fraction, not the new comparison solution, gives approximately
`6.0394957643e-9`. This is a design diagnostic only. It suggests a useful margin
for the proposed delta=2e-8, but the upper comparison function must be evaluated.

### Explicit proof with a changing cLi<1

The upper LiIII/IV equations coincide for the attenuated and unattenuated
10 eV problems, hence cLi(t) is identical even when it changes in time.
Their neutral equations share the exact source r1 cLi. Subtraction cancels
that source, leaving the difference equation above. The only inequality
used for f_thin is `0<=f_thin<=cLi<=1`; cLi=1 is not required. Finally,

    integral_s^t Lambda(u) exp[-integral_u^t (Lambda+r1)] du
       <= integral_s^t (Lambda+r1)(u)
                         exp[-integral_u^t (Lambda+r1)] du
       = 1-exp[-integral_s^t (Lambda+r1)] <= 1.

Thus the bound expm1(delta) is uniform for the actual changing upper-charge
populations. It does require identical Li initial fractions at the late seed.

### A source-specific sigma maximum

The frozen LiI PH2 row is Efit=3.107 eV, s0=62.45 Mb, ya=15.01, p=4.895,
and yw=y0=y1=0. On 5.392<=E<=10 eV, set x=E/Efit and u=sqrt(x/ya). Then

    sigma = s0 (x-1)^2 x^(p/2-5.5) (1+u)^(-p).

The stationary equation is

    -7 ya u^3 + (p-7) ya u^2 + 11 u + (11-p) = 0.

The coefficient signs have exactly one change, so there is exactly one
positive stationary root. It lies at E=6.708263233652767 eV, with
sigma=1.6589247907249876 Mb (numerical evaluation of this algebraic root).
The endpoint values are lower. A conservative rounded bound is
`sigma_max=1.66e-18 cm^2`. This is a bound for the adopted source fit on the
specified energy interval, not an empirical atomic-accuracy bound.

## 5. Initial-data and frozen-bath obligations

To define a genuine continuum late-time problem, specify the angular optical
profile at eta_star. A nonnegative shape-preserving interpolation of the M16
optical depths is one explicit numerical initial model; its maximum is then
bounded by the maximum nodal value. It is not a recovered exact continuum
history before eta_star. Alternatively define an exactly isotropic unattenuated
profile at eta_star and classify that initial modification separately.

The complete control chain should separate:

1. Frozen-bath M16 ray rate with saved optical histories versus saved M16 Li
   fractions (tests interpolation and late problem reconstruction).
2. Same finite M16 rule with attenuation removed (tests the trace approximation).
3. Threshold-partitioned GL orders, with identical bath and initial fractions
   (tests moving-support quadrature).
4. A common-threshold b=0 control and opposite-sign support algebra.
5. The attenuation bootstrap envelope and the omitted high-energy tail.

Interpolating only the 201 common output times may miss the sharp initial
thermal transient. Starting at eta_star and using the accepted late history
avoids that transient. Accepted-node cubic Hermite interpolation can use the
original RHS for derivatives; PCHIP is another explicit model. Their numerical
difference or comparison against the saved finite-M16 trajectory is a bath
reconstruction diagnostic, not a continuum error proof.

If bath coefficient perturbations are bounded, Markov L1 contractivity gives
an additional useful error relation:

    ||delta f(t)||_1 <= ||delta f(start)||_1
       + 2 integral [|delta Lambda| f0_ref
                    + sum_q |delta r_q| f_q_ref] d eta.

No exponential condition-number amplification is needed in this l1 bound.

## 6. Conservation and scope

The moving support rate integral preserves the fixed-q angular measure and
positive rates. It is not by itself a full photon transport solve. Do not
combine the corrected Li fractions with the old photon/gas ledgers and then
claim exact energy/count conservation of a new coupled trajectory.

For the exact continuum reference, define absorption density
`A=YLi f0 k g`, and moments over the fixed interval [0,1]. Then

    N_gamma' = -integral A dmu0,
    U_gamma' = -U_gamma-2b' Q-integral E A dmu0.

These identities retain the old photon loss, energy and signed shear work.
No boundary term belongs to a whole fixed-interval moment. If an active
subinterval is differentiated, its moving-boundary flux must be included
and canceled against the inactive subinterval. Sampling at new quadrature
nodes never licenses assigning tau=0 or copying an unrelated old optical depth.

The proposed late trace experiment admits a corrected conditional Li response
and quantified error components. It does not certify the fully coupled
angular-continuum thermochemistry or Einstein feedback.

## 7. Alternative exact finite model

A static composite Gauss rule or positive variable transformation
`mu0=x^p`, with weights `p x^(p-1) dx`, preserves the material-ray interpretation
and all ANGTHERM01 event identities exactly within the new finite quadrature.
Its initial weights must be positive and sum to one, with frozen fixed nodes.
It avoids remapping but still samples a step-like moving support and therefore
requires observed convergence tests. It is a useful finite comparator if the
controller chooses to keep the entire new unit fully coupled; no general
speedup or continuum certificate follows merely from endpoint clustering.

## Decision ceiling

All formulas above are derived for the given LRS Bianchi-I characteristic map,
the frozen photo/RR electronic model, and a prescribed bath. They do not assert
a general Bianchi theorem, empirical astrophysical prediction, or strong no-go.
No new IVPs or solver experiments were executed in preparing this assessment.
