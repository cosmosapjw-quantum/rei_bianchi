# HE34 independent reduction derivation

## Scope and exact coordinate reduction

This is a constructive reduction of the already derived HE33 homogeneous,
nonrelativistic, source-free mechanical pressure model, with prescribed
pressure-anisotropy relaxation. It does not determine a physical mixture
transport frequency or chemical/thermal source moments.

For H>0 use N=ln(a/a0), S=s/H and chi=nu_pi/H. Here chi is a prescribed positive
constant and S(N) is the **defined piecewise-linear interpolant** of a saved
background. The interpolation is the control input, not an error estimate for
the original cosmological trajectory. Let r=q/p and
u=ln[(p/p0) exp(5N)]. Then, exactly,

    r' = F(N,r) = 4 S r^2 - (chi+2 S) r - 2 S,
    u' = -4 S r.

The prime means d/dN. Expansion is removed analytically; H and density do not
need another ODE. The cone I=[-1/2,1] is invariant because F(-1/2)=chi/2 and
F(1)=-chi. For finite N and finite u, p=p0 exp(-5N+u)>0. Existing HE32
composition histories cannot be turned into self-consistent temperature
histories by this source-free mechanical step: that requires the separate
R_part, Q and J contract.

## Stable root and its physical pressure contribution

Define

    D = sqrt(chi^2+4 chi S+36 S^2)
      = hypot(chi+2 S, sqrt(32) S),
    b = -4 S/(chi+2 S+D).

For chi>0, b is the stable root in the interior of I. The rational expression
is regular at S=0 and avoids subtracting almost equal roots. Direct substitution
gives F(b)=0 and F_r(b)=-D. Implicit differentiation gives

    b' = (4 b^2-2 b-2) S'/D.

The root's expansion-factored pressure source is

    -4 S b = (D-chi-2 S)/2 = 16 S^2/(D+chi+2 S) >= 0.

The last expression is suitable for computation. For |S|/chi small,

    b = -2 S/chi + O(S^2/chi^2),
    u' = 8 S^2/chi + O(S^3/chi^2).

Thus the stress opposes the shear and transfers shear work into kinetic
pressure. Actual pressure still carries the exact exp(-5N) factor.

For comparison, the bare hydrodynamic approximation bH=-2S/chi has residual

    bH'-F(bH) = -2S'/chi -4S^2/chi -16S^3/chi^2.

The exact algebraic root removes the finite-S/chi terms without an additional
ODE. The retained initial layer also matches r0, whereas the bare root alone
has an initial mismatch |r0-b(0)|. The full ratio ODE remains the reference
outside the accepted error-certificate regime.

## Closed nonlinear initial layer on each source interval

Let tau=N-N_j in [0,h], S(tau)=Sa+(Sb-Sa) tau/h. Given a continuous approximate
left state rhat_j, set

    ba=b(Sa), D0=D(Sa), delta0=rhat_j-ba,
    c=4 Sa delta0/D0,
    delta(tau)=delta0 exp(-D0 tau)/(1-c[1-exp(-D0 tau)]),
    rhat(tau)=b(S(tau))+delta(tau).

The denominator is evaluated as 1+c*expm1(-D0*tau). Require
dmin=min(1,1-c)>0. This layer solves delta'=-D0 delta+4 Sa delta^2 exactly.
Consequently the candidate preserves the left state and is exact for constant
S and chi, including an arbitrary admissible initial anisotropy. For varying S,
the residual is the explicit expression

    rho = rhat'-F(N,rhat)
        = b' + (D-D0) delta + 4 (Sa-S) delta^2.

At a knot, restart with rhat_{j+1}=rhat(h). This gives a continuous piecewise
differentiable candidate. Derivative jumps at source knots cause no impulses.

The initial layer is retained even when chi*h is large. The method evaluates
an algebraic root, an exponential and a small scalar pressure quadrature; it
does not resolve each collision time with an ODE step.

## Explicit residual bound from interval data

Define

    Sm=max(|Sa|,|Sb|), Ls=|Sb-Sa|/h,
    kappa=chi-6 Sm, Dmin=chi-2 Sm,
    B=2 Sm/Dmin, A=|delta0|/min(1,1-c).

Require kappa>0. Then D>=Dmin>0 and |b|<=B. The sufficient cone check
B+A<=1/2 implies rhat in [-1/2,1/2], hence in I. More refined range checks can
be used, but sampled cone checks alone do not replace this sufficient bound.
If this check fails, the certificate is unavailable; the full positive
mechanical propagator remains applicable.

Because |4 b^2-2 b-2|<=9/4 on I and also
|4 b^2-2 b-2|<=2+2B+4B^2,

    Rb = min(9/4, 2+2B+4B^2) Ls/Dmin,
    LD = (2 chi+36 Sm) Ls/Dmin

bound |b'| and |D'| respectively. Also |delta(tau)|<=A exp(-D0 tau),
|D-D0|<=LD*tau and |S-Sa|<=Ls*tau. For

    m(a,h) = h exp(-a h), if a h<=1,
             1/(a e),    if a h>=1,

the complete interval residual bound is

    |rho| <= R = Rb + LD A m(D0,h) + 4 Ls A^2 m(2D0,h).

These are deterministic bounds for the specified linear source interval; no
sampling or empirically fitted safety factor enters their derivation.

## Contraction and propagated error certificate

For exact r and candidate rhat in I, the secant slope is

    [F(r)-F(rhat)]/(r-rhat)
      =4 S(r+rhat)-chi-2 S <= -(chi-6|S|) <= -kappa.

With e=r-rhat, e'=a(N)e-rho where a<=-kappa. The scalar comparison inequality
therefore proves, given |e(0)|<=E_j,

    |e(tau)| <= E(tau)
      =exp(-kappa*tau) E_j + (R/kappa)[1-exp(-kappa*tau)].

This is also valid when e crosses zero by the upper Dini derivative of |e|.
Set E_{j+1}=E(h). The envelope is monotone between E_j and R/kappa, so the
maximum on the interval is max(E_j,E_{j+1}). For matching initial data E_0=0.

Set m0=(1-exp(-kappa*h))/kappa. Then

    integral_0^h E(tau) dtau
      = E_j*m0 + (R/kappa)(h-m0).

The logpressure error obeys

    |u-uhat| <= L,
    L_{j+1}=L_j+4 Sm [E_j*m0+(R/kappa)(h-m0)], L_0=0.

Thus |ln(p/phat)|<=L and |p/phat-1|<=expm1(L). These bounds are dimensionless.
The declared independent acceptance criteria may be max E<=1e-6 and final
L<=1e-6; monotonicity of L certifies every intermediate point as well.

If tensor-component errors are needed, at any point

    |X-Xhat|/phat <= (1-rhat)(exp(L)-1)+exp(L)*E,
    |Y-Yhat|/phat <= (1+2 rhat)(exp(L)-1)+2 exp(L)*E,

where X=p(1-r), Y=p(1+2r). The inequalities follow by adding and subtracting
p(1-rhat), p(1+2rhat), respectively. q bounds follow similarly.

## Computation and numerical-error boundary

1. Store the exact saved coefficient knots and their declared interpolation.
2. For each interval, build b, delta and the analytic residual bound.
3. Propagate E and L. Reject the reduced certificate if kappa, denominator,
   sufficient cone check, finiteness, or requested bounds fail. Do not relax
   tolerances after seeing the result.
4. Compute uhat by integrating -4 S rhat, then reconstruct p,q,X,Y.
5. Compare against a separately implemented high-accuracy full mechanical ODE
   or converged exact frozen propagator on identical source data.

For the pressure integral, separate the slowly varying rational root term
16S^2/(D+chi+2S) from the initial layer. In the latter use x=D0*tau:

    integral -4 S delta dtau
      = integral [-4 S(x/D0) delta0 exp(-x)
                   /(D0 [1-c(1-exp(-x))])] dx.

The integration domain is [0,D0*h]. If it is truncated at x=C, its absolute
tail is <=4 Sm A exp(-C)/D0. Thus no quadrature nodes have to chase a narrowing
layer on the original N interval. C can be chosen from the desired tail budget.

Compute m0 with -expm1(-kappa*h)/kappa. For small z=kappa*h, h-m0 benefits from
the series h[z/2-z^2/6+z^3/24-...], or another cancellation-free implementation.
The formal derivation supplies a continuum approximation bound. Ordinary
binary64 evaluation, library quadrature error estimates, and a finite reference
comparison are separate numerical evidence. They do not by themselves create
an outward-rounded machine proof. Such a stronger claim would require interval
arithmetic or an explicit roundoff budget for all operations.

## Degenerate regimes and limits

- S=0 is regular: b=0, D=chi; the layer is exact exp(-chi*tau).
- Constant S is exact (rho=0) and pressure has a closed additional layer term
  ln[1-c(1-exp(-D0*h))]. This is a discriminating exact-reference check.
- chi<=6 Sm invalidates this contractive bound, not the original ODE.
- Nonmonotone expansion H<=0 requires another independent-variable contract.
- Nonzero Q,j or varying chi change the formulas and must carry a new residual
  derivation; they are not silently included in the current certificate.
- The interpolation-controlled statement does not certify errors in HE32's
  saved background or fit a baryon collision frequency.

If a separate bound |S_true-S_interpolant|<=epsilon_S becomes available, the
same proof can include a residual allowance (9/4)*epsilon_S, since
|dF/dS|<=9/4 on I. The pressure-error integral additionally receives
4*epsilon_S per unit N. No such background interpolation bound is assumed
by the present control.

## Independent symbolic and finite checks performed

The Wolfram evaluator returned F(b)=0, F_r(b)=-D, the shifted polynomial
identity zero, and boundary flows chi/2,-chi. Its front-end emitted an
undefined-symbol warning; the returned symbolic expressions were evaluated
successfully and match the explicit derivation above. Exact tool transcript
is in WOLFRAM_CHECK.json.

check_reduction.py compares the proposed candidate and analytic envelopes
against a separately coded SciPy Radau integration of (r,u), with analytic
Jacobian, rtol=1e-11, atol=1e-13. Eight new synthetic controls use positive or
sign-changing piecewise-linear S and chi=10,100,1000,10000. There is no HE32
background IVP or HE33 test replay. CONTROL_RESULTS.json records numerical
errors, analytic envelopes and target outcomes; reference sampling corroborates
the proof rather than replacing it.
