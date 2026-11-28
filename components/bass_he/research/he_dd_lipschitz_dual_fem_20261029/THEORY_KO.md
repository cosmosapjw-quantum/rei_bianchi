# HE-DD Lipschitz Angular Moment: certified inner/outer extrema brackets

2026-10-29 | Scope: 4He(gamma,d)d, E_gamma=330 MeV, **source-conditional mathematical model only**.
Parent: cosmosapjw-quantum/BASS_HE Draft PR #109, frozen `11b3cfdb987137323d8ebd220e74063b0ed6db22`.

## Original data / regime

Reuse frozen PR109 EXFOR M0475002 transcript, IAEA-NDS/exfor_master@`939a14d7bba1ddce51975cb5e8711ce96b3b0871`, `exforall/M04/M0475.x4`, previously pinned SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`. At E_gamma=330 MeV, four theta_CM [degree], [DA-ERR-S,DA+ERR-S] [nb/sr] pairs: (46,[.11,.17]),(61,[.11,.21]),(73,[.02,.12]),(87,[.14,.24]). ERR-S is **statistical coordinate sensitivity only**, not a simultaneous confidence region. Fresh original full-source SHA in the local container is not claimed; parent Git blob is the source identity. Actual Arends(1976) and Silverman(1984) detector efficiencies, angular acceptance, beam polarization and identical-D counting convention remain unresolved.

Assume f:[0,90 degree]->[0,infty), L-Lipschitz in **degrees**, source boxes, reflection symmetry f(theta)=f(180-theta) and azimuthal average. L>=1/700 nb/(sr degree), externally assumed, not measured. Let k=pi/180 per degree, v(theta)=cos^2(k theta), w(theta)=sin(k theta) and

  D(f)=integral_0^90 f(theta) w(theta) dtheta,
  N(f)=integral_0^90 v(theta) f(theta) w(theta) dtheta,
  b(f)=N(f)/D(f).

The common radian Jacobian k, full-sphere reflection factor and any **angle-independent** positive event/particle factor cancel in b. Angle-dependent efficiency does NOT cancel. D(f)>0 because the source point lower cone has positive measure.

## Theorem T1: continuum / finite element interpolation

For any grid theta_j=j h with h=1/subdiv degree and every experimental angle included as a grid knot, define the nodal linear interpolant I_h f. Each piecewise-linear I_h f is nonnegative, L-Lipschitz, source-feasible, and its nodal values satisfy the finite LP inequalities y>=0, |y_(j+1)-y_j|<=Lh, ell_i<=y_(theta_i/h)<=u_i. Conversely any such nodal vector determines a physically *conditional* feasible Lipschitz piecewise-linear f_h. This is an exact finite-dimensional feasible subset, not a heuristic interpolation of DA observations.

For theta in [theta_j,theta_(j+1)] the Lipschitz endpoint inequalities yield

  |f(theta)-(I_h f)(theta)| <= 2 L (theta-theta_j)(theta_(j+1)-theta)/h <= Lh/2.

Let F_t(f)=N(f)-tD(f), t in [0,1]. Since |(v-t)w|<=1,

  |F_t(f)-F_t(I_h f)| <= 90 Lh/2.   [units nb/sr degree]

This is a true continuum error estimate; it is O(h) without additional smoothness of f.

## Theorem T2: scalar coefficient quadrature and rational trigonometric enclosure

Identity verified with Wolfram:

  g_t(theta)=(v(theta)-t)w(theta)=(1/4-t) sin(k theta)+(1/4)sin(3 k theta).

Thus |g_t''(theta)|<=3k^2, k<22/(7*180). On each cell use the linear Taylor expansion at theta_mid:

  Q_h(y;t)=sum_cells { h g_t(mid)(y_j+y_(j+1))/2 + h^2 g_t'(mid)(y_(j+1)-y_j)/12 }.

For a nonnegative PL y<=B, the exact continuum-to-quadrature error obeys

  |F_t(f_h)-Q_h(y;t)|<=90 B (3k^2) h^2/8.

B=min_i [u_i+L max(theta_i,90-theta_i)] is a rational global bound from the original point constraints.

The implementation derives rational upper/lower bounds on pi via Machin's 16 atan(1/5)-4 atan(1/239) alternating series. The rational pi0=3.1415926535897932384626433832795 is within 1e-27 of pi, as explicitly checked with exact Fraction. Sine 31st-degree and cosine 30th-degree Taylor polynomials on |z|<24/5 have errors bounded by (24/5)^33/33! and (24/5)^32/32!. Directed Decimal interval arithmetic encloses polynomial evaluation. The code verifies coefficient intervals and uses a conservative 10^-8 bound for **the t-combined** g_t and g_t' coefficients, beyond the residual Taylor/pi error; no mpmath digits are silently promoted to an interval certificate. The integral error allowance for these coefficients is at most

  epsilon_trig = 90 B e + 90 L h^2 e/12, e=10^-8.

Together, all continuum f obey |F_t(f)-Q_h(y;t)| <= epsilon=epsilon_interp+epsilon_quad+epsilon_trig where y is the exact vector f(theta_j).

## Theorem T3: LP dual residual produces mathematical outer bounds

At fixed t, let c(t) be the *exact rational* coefficients of Q_h. Maximize c^T y under rational A y<=b, 0<=y_j<=B. Numerical HiGHS is used only to suggest candidate nonnegative dual (lambda,nu), not as a proof. Convert each dual output to a literal Fraction and compute, in exact arithmetic,

  U_t = b^T lambda + B sum_j nu_j
      + B sum_j max(0,c_j-(A^T lambda)_j-nu_j),
  lambda>=0,nu>=0.

Then c^T y <= U_t for **every** nodal feasible y, independently of numerical LP solver claims or its stopping tolerance. Therefore the continuum satisfies F_t(f)<=U_t+epsilon. With g=-F_t and a separate dual U^-_t, F_t(f)>=-U^-_t-epsilon. Bounds on normalized b use an exact rational denominator floor:

 D(f) >= Dmin = integral f_-(theta)*(theta/90)dtheta > 0,

because f>=f_- and sin(k theta)>=theta/90 on [0,90]. The latter integral is evaluated exactly from the piecewise-affine lower cone.

For E_+=max(0,U_t+epsilon), E_-=max(0,U^-_t+epsilon),

  b(f) <= min(1,t+E_+/Dmin),
  b(f) >= max(0,t-E_-/Dmin).

The truncation to positive E is essential to avoid reversing the denominator argument when E<0.

## Theorem T4: exact feasible inner witnesses

The numerical LP primal solution is **not automatically feasible**. Convert its values to rationals, apply the 1D McShane upper hull m_j=max_k(y_k-L|theta_j-theta_k|), and then clamp to the rational source cones f_-<=m<=f_+. Max/min of L-Lipschitz functions preserve Lipschitz continuity. The resulting grid y* is therefore **exact-rational feasible**. Its PL interpolation is a constructive witness. The N and D integrals of this witness are enclosed using the certified quadrature/trig budgets *without the continuum interpolation term*, giving a computably valid inner interval on its b.

Consequently for the true extrema b_min and b_max, the resulting four numbers obey

 outer_min <= b_min <= feasible_min_witness_upper,
 feasible_max_witness_lower <= b_max <= outer_max.

These brackets are finite-grid error certified, but do NOT assert exact algebraic sharpness or any experimental distribution identification.

## Evaluated conditional outcomes (h=1/50=0.02 degree, 4501 nodes)

| L [nb/(sr degree)] | lower <= min b <= inner upper | inner lower <= max b <= outer upper |
|---|---|---|
| 1/700 | [0.2800766324, 0.2803338733] | [0.3794460960,0.3797024351] |
| 1/200 | [0.1854121068, 0.1866070873] | [0.4679082819,0.4691036321] |
| 1/100 | [0.1301587544, 0.1335489820] | [0.5634911669,0.5668850720] |

Numbers are *display* roundings only, not the interval objects themselves. Full Fraction numerators/denominators are in `evidence/EXTREMA_CERT_*.json`, code regenerates the complete post-dual certification. In particular, L=1/700 previous PR109 approximate outer `[0.279238681235,0.386397436244]` is strengthened on both sides by the new **conditional mathematical** outer. At L=1/200 and 1/100 the new upper is stronger, but the older numerically approximated lower is not itself a new certified bound, so do not take a numerical maximum and relabel it rigorous.

## Physics bridge and nonadmission

For a pair of produced D at E_gamma=330 MeV with inherited mass convention, K±=K0±Delta cos(theta), K0=153.0767609 MeV, Delta²=3798.60144551708985 MeV²; its single-D marginal variance satisfies Var(K_D)=Delta² b under the declared f. This is a *generation* variance. Actual D_fast stopping, redistribution, escape, heat capacity, photon history, target proper distribution and event convention are missing. No measured b, no measured R_event, no thermalized heat or physical L4 follows. `kappa=null`, `R_event=null`, `heat_rate=null`, `physical_activation=false`, `L4=false`, `production=HOLD`. Previous IVPs and science suite are not rerun.

## Literature context and novelty boundary

Arends et al. Phys. Lett. B 62 (1976) 411–412, DOI 10.1016/0370-2693(76)90671-7; Silverman et al. Phys. Rev. C 29 (1984) 35, DOI 10.1103/PhysRevC.29.35. Neuenhofen & Kerrigan arXiv:1810.04059 discusses convergence of direct transcription in optimal control; verified linear-program bounding literature includes *A review of computation of mathematically rigorous bounds on optima of linear programs* (2017, DOI 10.1007/s10898-016-0489-2). These are methodological context, **not evidence this exact BASS_HE enclosure is novel or source-qualified**. The above finite-dimensional dual and continuum lemma are directly derived here and independently checked only at CAS / alternative numerical algorithm level. Distinct nonauthor R6/C9 remains NOT_RUN.
