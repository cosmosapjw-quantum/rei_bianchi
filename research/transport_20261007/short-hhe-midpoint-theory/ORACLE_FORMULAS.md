# Independent scalar oracles for the midpoint test contract

These formulas supplement T2–T7 of TEST_FIRST_CONTRACT.md. They are mathematical controls, not alternate provider physics or replacements for the actual original37-field experiment. No numerical history is produced here.

## O1. Smooth coupled absorption, exact photon/count solution

Take q=0, constant k>0, x'=k(1-x)f, f'=-k(1-x)f. Let u0=1-x0 and d=u0-f0. Since x+f=x0+f0, f'=-k(d+f)f. For d!=0,

  f(t)=d f0 exp(-k d t)/[u0-f0 exp(-k d t)],
  x(t)=x0+f0-f(t).

For d=0,

  f(t)=f0/(1+k f0 t),
  x(t)=x0+f0-f(t).

For positive admitted data these formulas provide an independent smooth endpoint oracle; they are not the candidate's frozen-opacity formula. With absorption switched off at tau=alpha*h, the exact endpoint is simply this solution evaluated at min(h,tau), followed by constant x,f. This exposes the event-chord defect rather than assuming local order3.

If a nonzero constant source is wanted, its second-order Taylor oracle is sufficient for T3:

  v=k(1-x0)f0,
  g=q-v,
  c=-k v f0+k(1-x0)g,
  x(h)=x0+v h+c h^2/2+O(h^3),
  f(h)=f0+g h-c h^2/2+O(h^3).

A quadratic-coefficient test should compare against these coefficients or use an independently derived higher-order Taylor series so the reference remainder is smaller than the measured candidate local error. Comparing only with a second-order truncated oracle cannot isolate the candidate's own cubic coefficient.

## O2. Local event coefficient and photo-only root limitation

For O1 stopped at tau=alpha*h, v=k(1-x0)f0. The single-global-chord segment-centered method satisfies

  x_candidate-x_exact = [k f0 v alpha^2(1-alpha)/2] h^2+O(h^3).

The coefficient is strictly positive for k,f0,v>0 and0<alpha<1. Setting alpha=1/3 preserves a noncentral event. Across fixed-endpoint refinements the event's position within its step can change; this affects adjacent-grid coefficients and must not be hidden by fitting arbitrary ratios.

Without the cutoff, write D=x1-x0. The midpoint residual is

  L(D)=D-f0[1-exp(-kh(u0-D/2))].

Its derivative is1+(kh f0/2)exp(-kh(u0-D/2))>0. For f0>u0, no physical root D<=u0 exists if

  kh>-(2/u0)ln(1-u0/f0).

For u0=0.8,f0=1.6 this threshold is2ln2/0.8, below3. This provides a genuine photo-coupled admission-negative control.

## O3. Exact proper-time source versus frozen-per-s source

Take constant H, zero opacity, and one event-free source interval centered at sm. Let E(s)=Em exp(-(s-sm)), C=1/Emin-1/Emax and K=Q_t/(C H). Then q_exact(s)=qmid exp(s-sm), where qmid=K/Em. Over a segment of length h,

  Q_N_exact=2 qmid sinh(h/2),
  Q_N_kernel=qmid h,
  Q_E_exact=epsilon K h,
  Q_E_kernel=2 epsilon K sinh(h/2).

Thus Q_N_exact-Q_N_kernel=qmid h^3/24+O(h^5), and Q_E_kernel-Q_E_exact=epsilon K h^3/24+O(h^5). These discrepancies are expected consistency errors. The kernel must continue using its own internally shared Q_N and Q_E; replacing them with these oracle values alone is a deliberately failing ledger-mismatch mutant.

For source on/off event segments, apply the same formulas using that segment's midpoint and length. This tests segment-centered explicit source coefficients independently of nonlinear gas. In nonconstant H use an independent positive quadrature or exact special-case H, not the candidate's midpoint formula as its own reference.

## O4. Expansion and EOS interpolation

For zero electrons/photo forcing, dw/ds=-2w:

  w_exact=w0 exp(-2h),
  w_midpoint=w0(1-h)/(1+h),
  work_midpoint=h(w0+w_midpoint)=w0-w_midpoint,
  w_midpoint-w_exact=-(2/3)w0 h^3+O(h^4).

For fixed fHe, put D(theta)=1+fHe+xHII(theta)+fHe[xHeII(theta)+2xHeIII(theta)], positive and affine, and w(theta)=w0+theta Delta w. Then

  T(theta)=2w(theta)/(3kB D(theta)),
  T'(theta)=2[Delta w D0-w0 Delta D]/[3kB D(theta)^2].

The sign is constant. The accepted reconstructed stage temperature cannot overshoot its endpoint range in exact arithmetic. This does not bound an unrelated exact solution between outputs or excuse missing binary64/provider checks.

## O5. Diagnostic jump is not a continuous kink

For J(s)=J0 when0<=s<alpha*h and0 thereafter, exact owner=J0 alpha h. A global midpoint owner is J0 h if alpha>1/2, and0 if alpha<1/2 (the equality case follows the specified branch mask). The error is generically O(h), not O(h^2) or O(h^3).

The actual HeI ce_cap indicator switches at13179/69.07755278982137 K. Passing a tiny absolute diagnostic allowance and proving second-order integration of a discontinuous diagnostic are separate claims.
