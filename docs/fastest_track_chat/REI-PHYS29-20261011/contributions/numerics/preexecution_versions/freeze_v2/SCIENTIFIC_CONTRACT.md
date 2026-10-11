# PHYS29 numerical scientific contract

Status: **PREEXECUTION / NOT_RUN** at authoring. This file fixes the proposed scientific computation; it does not claim that it ran. The later `EXECUTION.json` and first raw output supply actual execution evidence.

## Objective and protected meaning

Evaluate the one-sided second-order threshold coefficient

\[
W_j(\delta)=w_j+c_j\delta+d_j\delta^2+o(\delta^2),\qquad d_j=\tfrac12W_j''(0),
\]

at the two **stored PHYS26 numerical root points**, using fixed actual photon variance \(W\), and separate the physical variance correction, within-band average, geometric motion and implicit-root terms. The exact-zero theorem is separate analytic evidence; the numerical general formulas at a point with residual \(A\ne0\) describe continuation of that same response level. No numerical point is relabeled as an exact zero or refined.

The user requested the next research loop. Root `PHYSICS_CONTRACT.json`, actual PHYS29 handoff, source manifest, full PHYS22 serialized J and PHYS26–28 raw records define the scope. Physical HOLD; original [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED. Production source/default/runtime changes0. The result concerns the initial HeIII \(\epsilon^2t^4\) coefficient in s⁻⁴, with no history/emitter admission.

## Definitions and conventions

\(a=13.61,b=24.58,m=18\) eV, \(L=m-a=4.39,H=b-m=6.58\) eV. \(\delta\ge0\) is a uniform **half-width** in eV, not a full width. Write \(\alpha=a+\delta,\beta=b-\delta,\ell=L-\delta,h=H-\delta,V=W-\delta^2/3\). Actual admissibility is \(\delta^2/3\le W\le\ell h+\delta^2/3\); only a local one-sided neighborhood of each interior simple root is claimed.

\[
f_\delta(c)=\frac12\int_{-1}^{1}k(c+\delta z)\,dz,\quad
A_{\delta,+}=\frac{Vf_\delta(\alpha)+\ell^2f_\delta(m+V/\ell)}{\ell^2+V},\quad
A_{\delta,-}=\frac{h^2f_\delta(m-V/h)+Vf_\delta(\beta)}{h^2+V}.
\]

Use metric (−,+,+,+), gas-comoving proper seconds, photon energies eV, thermal variable w eV/H. \([\epsilon^2]\) is half the second epsilon derivative. The t⁴ coefficient has no extra factorial. \(D=E\partial_E\) holds the initial gas state fixed. Source f64 literals are interpreted as exact real numbers through `Decimal.from_float(float(literal))`; subsequent arithmetic is Decimal80, without native-arithmetic equivalence.

The actual source fit is the HI Verner expression on \([a,b]\), entirely above the HI fit threshold13.60 and below the HeI threshold24.59. Binding energy \(\chi=\mathrm{f64}(13.598434599702)\) is distinct from the opacity threshold. Parameters \(E_0=\mathrm{f64}(.4298),y_a=\mathrm{f64}(32.88),P=\mathrm{f64}(2.963),\sigma_0=\mathrm{f64}(5.475\times10^4)\), area conversion \(\mathrm{f64}(10^{-18})\). Full J strings are read from `results.baseline_local.J_nonphoto[2][0]` and `[2][3]`; no rounded narrative coefficient becomes input.

## Kernel derivation and separate expressions

Let \(\phi(E)=\sigma(E)[J_x+J_w(E-\chi)]\) and \(K=qN_0\kappa/180\), with \(q=2\,\mathrm{shear}^2\), \(\kappa=c n_H(1-x_{HII})\). Each kernel includes K once:

\[
k=K(D^2+3D)\phi,\quad k'=\frac K E(D^3+3D^2)\phi,\quad
k''=\frac K{E^2}(D^4+2D^3-3D^2)\phi.
\]

The last expression follows by differentiating \(E^{-1}(D^3+3D^2)\phi\): \(\partial_E(E^{-1}g)=E^{-2}(D-1)g\). No finite difference is used.

The primary kernel uses a degree4 log-energy Taylor algebra, \(c_n=D^n\phi/n!\), explicitly adapted after reading the complete PHYS28 program. The second kernel uses scalar \(\ell_j=D^j\log\sigma\), \(S_2=\ell_1^2+\ell_2\), \(S_3=\ell_1^3+3\ell_1\ell_2+\ell_3\), \(S_4=\ell_1^4+6\ell_1^2\ell_2+3\ell_2^2+4\ell_1\ell_3+\ell_4\). With \(x=E/E_0,z=\sqrt{x/y_a}\),

\[
\ell_4=-\frac{2x(x^2+4x+1)}{(x-1)^4}
-\frac{Pz(1-4z+z^2)}{16(1+z)^4}.
\]

For \(g=J_x+J_w(E-\chi),t=J_wE\), scalar k″ is

\[
\frac{K\sigma}{E^2}\{(S_4+2S_3-3S_2)g+(4S_3+12S_2+4\ell_1)t\}.
\]

This pair shares fit, source-real constants, J and Decimal `ln/exp`; it is algebraic implementation comparison, not independent physical data.

## Explicit chain rule and decomposition

Use endpoint-first ordering for both branches. \((s,R,e)=(+1,L,a)\) for upper, \((-1,H,b)\) for lower. At \(\delta=0\), set \(D_R=R^2+W,p=W/D_R,q=R^2/D_R,x=m+sW/R\). The endpoint derivative is s and its acceleration is0. At fixed V,

\[
p_\delta=2RW/D_R^2,\quad p_{\delta\delta}^{geom}=8R^2W/D_R^3-2W/D_R^2,\quad
x_\delta=sW/R^2,\quad x_{\delta\delta}^{geom}=2sW/R^3.
\]

The center variance correction contributes \(p_{\delta\delta}^{V}=-2R^2/(3D_R^2)\) and \(x_{\delta\delta}^{V}=-2s/(3R)\). It is inserted once. With \(C=F_W\), its combined contribution is \(F_{\delta\delta}^{V}=-(2/3)C\).

The program computes \(F_{\delta\delta}\) as nine displayed terms: uniform averaging \((pk''(e)+qk''(x))/3\), V″ correction, endpoint curvature, center curvature, endpoint acceleration0, center acceleration at fixed V, probability acceleration at fixed V, twice probability×endpoint motion, and twice probability×center motion. It separately computes \(F_{\delta W}\) and \(F_{WW}\) by explicit product rules. The root coefficients are

\[
c=-F_\delta/C,\qquad d=-\frac{F_{\delta\delta}+2F_{\delta W}c+F_{WW}c^2}{2C}.
\]

Each fixed-W term is multiplied by \(-1/(2C)\); the final two entries are \(-F_{\delta W}c/C\) and \(-F_{WW}c^2/(2C)\). Thus \(d_V=+1/3\) exactly, while \(d_{avg}=-(pk''(e)+qk''(x))/(6C)\). **No sign or nonzero assumption on total d is fixed.**

## Independent envelope and root algebra

The secondary envelope program operates on ordinary bivariate Taylor coefficients in \(\delta,\eta=W-w\), total degree≤2. It constructs the exact rational weights, endpoint and center series directly, then uses \(k(c_0)+k'(c_0)\Delta c+\frac12k''(c_0)(\Delta c)^2+\frac16\delta^2k''(c_0)\). Its own root coefficients are solved by cancellation of the δ and δ² ordinary coefficients. It does not call the explicit chain-rule derivative or root postprocessor. The two paths share the prescribed family/Taylor expansion and primitive input, which is disclosed.

The residual-preserving numerator identities are checked using the independently formed numerator series. With \(F=N/Q_R\), \(Q_R=(R-\delta)^2+W-\delta^2/3\), actual \(A=F(0,w)\) is retained: \(N_W=D_RC+A\), \(N_{\delta\delta}=D_RF_{\delta\delta}-4RF_\delta+4A/3\). The numerator formula for d subtracts \(4A/3\) and divides by \(2(N_W-A)\), rather than assuming A=0.

## Validation fixed before execution

| Requirement | Reference / check | Prospective criterion |
|---|---|---|
| Exact inputs and protected source | Contract/protocol and all frozen byte identities | All equal before physical kernels |
| k,k′,k″ normalization and algebra | Four nodes, LogJet vs scalar derivatives | Scaled difference≤10⁻⁶⁰ |
| Historical first derivative consistency | Existing PHYS28 serialized k,k′,B,C,c and residual | Same fixed scaled tolerance; no old code replay |
| Second-order envelope implementation | Explicit chain vs independent bivariate coefficients | Scaled difference≤10⁻⁶⁰ for A,B,C,Fdd,FdW,FWW,c,d |
| Physical moments | Six bivariate coefficients for mass, mean and actual variance | Mass1, mean m, variance W+η, scaled error≤10⁻⁶⁰ |
| Variance correction and terms | Independent C relation, d decomposition and root coefficient cancellation | Same fixed scaled tolerance |
| Exact known limit | Fraction toy k=(E−m)²−w; exact A=W−w in both branches | Exact equality: B=Fdd=FdW=FWW=c=d=0, C=1; d_avg=−1/3,d_V=+1/3 |
| Stored-root distinction | Full response retained; no root simplification/correction | |Response|/10⁻⁶⁴≤10⁻⁶⁵; this is not an interval bound |
| Existing δ=.05 comparison | PHYS27 roots and full PHYS28 linear/residual strings | Report quadratic residual; only bookkeeping identities tested |
| Reproducibility | Different contributor, distinct path, same frozen new program once | Actual bytes/result/count comparison; independent physics credit0 |

Kernel scale is10⁻⁶⁴ s⁻⁴; a derivative of total energy dimension−j uses10⁻⁶⁴/18ʲ for j1–4. Sigma scale10⁻¹⁸ cm². Dimensionless/moment/c/d comparisons use max(1,|actual|,|expected|). Constants use max(|actual|,|expected|). No tolerance is chosen from new results, and none may be relaxed afterward. Dimensional interpretation: Fδ s⁻⁴/eV, FW and Fδδ s⁻⁴/eV², FδW s⁻⁴/eV³, FWW s⁻⁴/eV⁴, c eV, d dimensionless.

## Execution, failure and claim ceiling

First new scientific main max1; exactly four stored-root nodes times two kernel paths planned,8 joint calls with8 outputs each of k,k′,k″,24 components total. The code enforces this smaller budget within the contract maximum24 joint calls. Two exact quadratic toy branches use rational arithmetic and no physical kernel calls. One different-path replay of this new program is separately debited. Roots0, old PHYS19–28 main/suite/root0, quadrature0, finite differences0, width sweep0, derivative-sign campaign0, native0, gas IVP0, dense LP0. First process timeout60s.

Before first science, freeze code, protocol, filled contract, input paths, bytes/hashes, tolerances and counts. AST/compile-only static checks execute no candidate. Preserve draft corrections and actual first failure/partial result/stdout/stderr/exit/UTC. No hidden rerun, silent fallback or clipping. The distinct final reviewer is neither this generator nor the verification designer.

No interval enclosure of roots/coefficient/J uncertainty, original gas/atomic uncertainty, Taylor remainder bound, certified width window, convergence rate or general positive-width family nesting follows. A single previously stored δ=.05 root comparison may improve or worsen and remains descriptive. New c is checked against PHYS28 c; diagnostics retain the exact serialized PHYS28 linear shift and use the new d. About12 significant digits may be printed in narrative; long Decimal strings are reproducibility evidence.
