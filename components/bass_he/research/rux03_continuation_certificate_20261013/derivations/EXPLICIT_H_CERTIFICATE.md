# Explicit full-rate continuation certificate

Unit: HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06. Author's quantified result, read together with the independent adoption decision in ../review/DECISION.json. This result holds for the real analytic functions specified by the source decimals; native floating-point implementation has a separate contract.

## 1. Certified statement

Fix any neutral-reference energy parameter
\(\mu\in[10^9,1.5\times10^9]\) eV/H and the old state, affine coordinate and six photon nodes in [SCIENTIFIC_CONTRACT.md](../dossier/SCIENTIFIC_CONTRACT.md). The positive-cube proof is [PRIMITIVE_DIFFERENTIAL_BOUNDS.md](PRIMITIVE_DIFFERENTIAL_BOUNDS.md). It is established before rate differentiation and holds uniformly in this parameter family.

Let \(F(X,h)=X-hG_h(X)\) be the seven finite equations S1–S11 of [FULL_SOURCE_CONTINUATION_CERTIFICATE.md](FULL_SOURCE_CONTINUATION_CERTIFICATE.md), on \(\|X\|_\infty\le1\). All three CI, three RR, both DR and supported primary absorption terms remain active. At fixed old state there is exactly one solution in this cube for each

\[
\boxed{0\le h\le H=500000000\ {\rm s}.}
\tag{C1}
\]

It belongs to one \(C^1\) branch with \(X(0)=0\), stays strictly within the physical cube and the retained warm provider/cutoff cells, and satisfies all seven original finite equations through the exact affine row transformation. H is about 15.844043907 Julian years (a Julian year is 31557600 seconds). This is the parameter of one backward-Euler source problem with the old physical state fixed. It does not assert that a production trajectory was integrated for that duration or that a requested time-discretization error has been met.

## 2. Complete reproducible input family

| Input | Exact value or definition |
|---|---|
| Fixed Eulerian H density | \(D=10^{-3}\ {\rm cm^{-3}}\) |
| Helium/H ratio | \(f=2/25\) |
| Composition per H | \(\zeta_*=(1/2,1/50,1/50)\) |
| Temperature | \(T_*=50000\ {\rm K}\) |
| Common gas velocity | \(\beta_*=(0,0,41/841)\), \(\gamma_*=841/840\) |
| Reference energy | \(\mu=m_{\rm ref}c^2/\epsilon_{\rm eV}\in[10^9,1.5\,10^9]\) eV/H |
| Particle count | \(d_*=1+f+\zeta_{*,1}+\zeta_{*,2}+2\zeta_{*,3}=41/25\) |
| Thermal coordinate at anchor | \(w_*=3k_Bd_*T_*/(2\epsilon_{\rm eV})=2830330450/267029439\) eV/H |
| Binding energy | \(B=\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3\) |
| Binding values, eV | \((13.598434599702,24.587389011,54.41776)\) |
| Scales of \((\zeta,t,m)\) | \((10^{-3},10^{-3},10^{-3},1/4,a_*10^{-6},a_*10^{-6},a_*10^{-6})\) |
| Momentum center | \(m_*=(a_*+5w_*/3)\gamma_*\beta_*\), \(a_*=\mu+B_*\) |
| Photon nodes | \((23\ {
m eV},\pm e_x),(35\ {
m eV},\pm e_y),(70\ {
m eV},\pm e_z)\) |
| Every old photon inventory | \(N_q^-/D=1/100\) |
| External photon source | \(S_q=0\) |

The constants used in the rate arithmetic are \(c=29979245800\) cm/s, \(k_B=1.380649\times10^{-16}\) erg/K and \(\epsilon_{\rm eV}=1.602176634\times10^{-12}\) erg/eV. The lab energies obey \(\epsilon_{\rm eV}E_q=\hbar\omega_q\). The metric convention is \((-+++)\). These are a declared mathematical construction, not a reassignment of a production campaign's initial data.

## 3. Primitive and rate inputs

The entire cube is in \(10<w<11\) eV/H and \(45000<T<55000\) K before derivative estimates are applied. Its derivative bounds per \(\|dX\|_\infty\le1\) are

\[
L_T=1400\ {
m K},\quad L_w=0.26\ {
m eV/H},\quad
L_\beta=3\times10^{-6},\quad L_\gamma=2\times10^{-7},\quad
L_\delta=4\times10^{-6}.
\tag{C2}
\]

These give the stronger cube temperature enclosure \(48600<T<51400\) K. The specified rays remain in fixed cutoff branches; the smallest gap to a fit cutoff is \(8203267/5250000=1.562527047619\ldots\) eV, and every transformed energy is below 74 eV.

The source-bound actual coefficients and first derivative caps are in [RATE_ENVELOPES.md](RATE_ENVELOPES.md), [SOURCE_FUNCTIONS.md](../source_map/SOURCE_FUNCTIONS.md) and [RATE_ENVELOPE_RESULT.json](../evidence/RATE_ENVELOPE_RESULT.json). The rate result consumed by the actual combined calculation has SHA256 `ef9fcb4d6d18d388bc45ae71844b1f8d3c284e529185898d195cdf28add69546`.

Kinetic coefficients are divided by \(\epsilon_{\rm eV}\) before entering eV/H rates. For each atomic process, the common bound applies to \(D\gamma^{-2}e_H y k(T)\), including the candidate density, electron fraction, target fraction and temperature derivatives. The photon bound includes both relative incidence and Doppler-shifted cross-section differentiation, followed by exact differentiation of the eliminated denominator. It does not differentiate a frozen old opacity.

## 4. Actual seven-row majorants

The analytic construction S12–S25 produces

\[
|G_{h,i}|\le b_i,\qquad
\|D_XG_{h,i}\|_1\le\ell_i^{(0)}+H\ell_i^{(1)}
\quad (0\le h\le H).
\tag{C3}
\]

The following numbers are rounded displays of the exact rational quantities received from Wolfram. Use the rational strings in [FULL_SOURCE_CERTIFICATE_RESULT.json](../evidence/FULL_SOURCE_CERTIFICATE_RESULT.json) for a certificate consumer; the short decimal displays are not new outward bounds.

| Scaled row | \(b_i\), s\(^{-1}\) | \(\ell_i(H)\), s\(^{-1}\) | \(H b_i\) |
|---|---:|---:|---:|
| \(X_1\), HII/H | \(1.606087775479313\times10^{-9}\) | \(4.495653810921768\times10^{-11}\) | 0.8030438877396564 |
| \(X_2\), HeII/H | \(2.915441016484080\times10^{-10}\) | \(1.419517632415940\times10^{-11}\) | 0.1457720508242040 |
| \(X_3\), HeIII/H | \(2.642859310912800\times10^{-11}\) | \(1.263134042779403\times10^{-12}\) | 0.0132142965545640 |
| \(X_4\), anchor energy | \(1.124935025151191\times10^{-10}\) | \(3.448066852423435\times10^{-12}\) | 0.05624675125755954 |
| Each of \(X_5,X_6,X_7\), momentum | \(5.012731451955840\times10^{-14}\) | \(6.993805625578905\times10^{-16}\) | 0.00002506365725977920 |

The momentum rows deliberately use the uniform lower scale \(s_m\ge1000\) eV/H and the full sum of positive photon energy magnitudes. Exact direction-by-direction cancellation is unnecessary for this sufficient certificate. The comparatively tight thermal row uses the exact anchor/binding cancellation, rather than bounding the large rest/bulk energy independently.

The HII row sets both maxima:

\[
B=\max_i b_i
=\frac{2007609719349141}{1250000000000000000000000}\ {\rm s^{-1}},
\tag{C4}
\]
\[
HB=\frac{2007609719349141}{2500000000000000}
=0.8030438877396564<1,
\tag{C5}
\]
\[
q=H\max_i\ell_i(H)
=\frac{702445907956526291951811059835445533}
{31250000000000000000000000000000000000}
=0.02247826905460884\ldots<1.
\tag{C6}
\]

The exact acceptance comparisons included \(HB\le9/10\) and \(q\le1/4\), in addition to the strict inequalities. The self-map margin is \(1-HB=0.1969561122603436\). The contraction margin is \(1-q=0.9775217309453911\ldots\). H was selected as the minimum of explicit positive rational sufficient candidates, and the selected value was exactly 500000000 seconds. No numerical search for a nonlinear stage root preceded this inclusion proof.

## 5. Constructive consequences

### Existence, uniqueness and finite balances

For each fixed \(h\in[0,H]\), the map \(\mathcal T_h(X)=hG_h(X)\) sends the whole cube into its strict interior by C5 and contracts by C6. Banach's theorem gives its unique fixed point. S1/B8 identify that fixed point with a solution of exactly the original chemistry, total lab energy and three momentum equations using the same eliminated photon events.

The statement is scoped to the certified cube. It does not assert uniqueness of every physical solution outside that domain or optimality of H.

### Stage parameter and state displacement

\[
|X_i(h)|\le h b_i,\qquad
\|(I-hD_XG_h)^{-1}\|_\infty\le\frac1{1-q}
=1.0229951604583454\ldots .
\tag{C7}
\]

The implicit/parameter contraction theorem then gives one \(C^1\) branch from the old state. Because \(S_q=0\), the actual parameter derivative of \(hR^\gamma\) is bounded by the same positive event majorant. Hence

\[
\left\|\frac{dX}{dh}\right\|_\infty
\le\frac{B}{1-q}
=1.6430200215866467\times10^{-9}\ {\rm s^{-1}}.
\tag{C8}
\]

Using C2 and C5, the branch has
\(|T-50000|\le1124.261442835519\ldots\) K,
\(|\beta-\beta_*|_2\le2.4091316632189692\times10^{-6}\),
and \(|\gamma-\gamma_*|\le1.6060877754793128\times10^{-7}\).
The physical cube proof supplies the primary domain margin. These are additional branch-local enclosures from its smaller displacement.

### An explicit corrector error bound

Start the mathematical Picard sequence with \(X_0=0\),
\(X_{k+1}=hG_h(X_k)\). Its error obeys

\[
\|X(h)-X_k\|_\infty
\le\frac{q^k}{1-q}HB.
\tag{C9}
\]

For **eight updates**, the exact arithmetic gives
\[
\frac{q^8}{1-q}HB
=5.354461272651965\times10^{-14}\ldots<10^{-12}.
\tag{C10}
\]

This is an a priori theorem for exact evaluation, not an executed eight-step trajectory. A native finite-precision corrector has additional primitive, provider, arithmetic and residual enclosure errors. Its implementation contract must account for those errors rather than relabel C10 as measured native convergence.

An approximate candidate \(\widetilde X\) lying in the cube also has the useful a posteriori bound

\[
\|X(h)-\widetilde X\|_\infty
\le\frac{\|F(\widetilde X,h)\|_\infty}{1-q}.
\tag{C11}
\]

Indeed, add and subtract \(\mathcal T_h(\widetilde X)\), use the contraction inequality and move the \(q\) distance term to the left. If each computed update has an absolute scaled error bounded by \(\eta\) and stays in the certified cube, the recurrence gives
\(\|e_k\|\le q^k\|e_0\|+\eta(1-q^k)/(1-q)\).
These expressions specify what the later native residual/rounding budget must control.

### Photon positivity

The actual bounds on \(H\Lambda_q\), ordered by the six nodes, are
\[
(0.0236333439764163,\ 0.0236333439764163,
 0.0131610837712977,\ 0.0131610837712977,
 0.00355679468227902,\ 0.00355679468227902).
\tag{C12}
\]
Every node therefore satisfies
\(p_q^-/(1+H\overline\Lambda_q)\le p_q^+(h)\le p_q^-=1/100\).
The exact six positive floors are in the result record. Every absorbed photon enters the same composition/energy/momentum event count; a separate photon limiter is not introduced.

## 6. Subsequent continuation

S32–S34 establish the reusable preconditioned tube criterion with a fixed invertible A, a predictor \(\bar X(h)\), positive component radii r, and **full-tube** bounds
\(Y\ge|AF(\bar X(h),h)|\), \(Z\ge|I-A D_XF(X,h)|\).
The component inequalities \(Y+Zr<r\) and
\(\max_i(Zr)_i/r_i<1\) certify the branch in every parameter section.
A valid common-root enclosure or whole endpoint-box inclusion identifies neighboring branches. Merely intersecting two geometric boxes supplies no such identification.

The current actual numerical certificate is C1, one closed physical cube and the full interval [0,H]. A later predictor-centered box chain beyond H has been derived as a construction method but has not been instantiated numerically in this loop. The finite maximal-endpoint alternative in §6 of the main proof has the appropriate nonextendibility qualification.

The standard weighted contraction and validated branch-following principles are attributed to [Day–Lessard–Mischaikow (2007), Theorem 2.1](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf), [van den Berg–Lessard–Mischaikow (2010), Lemmas 5/7 and Proposition 8](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf), and the interval inclusion setting of [Rump (1995), §3](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf). The new contribution is the explicit physical cube, actual source envelopes and numerical sufficient interval for the retained moving H/He system.

## 7. Actual computation and capture limits

One short Wolfram evaluation executed [FULL_SOURCE_CERTIFICATE_CHECK.wl](FULL_SOURCE_CERTIFICATE_CHECK.wl), with exact input saved before execution. It returned **12/12 named groups PASS**, four new scalar identity residuals equal to zero, H=500000000 seconds and the C3–C12 quantities above. Kernel: Wolfram Language 15.0.1 for Linux x86 (64-bit); reported kernel evaluation time 0.00676 seconds. The outer tool call took longer; no total wall-time inference is made from kernel time.

The tool shortened the middle of its long JSON response at roughly 10000 returned characters. The unmodified response is preserved. All seven b, ell0, ell1 and ellH vectors, exact H/HB/q, 12 acceptance outcomes and the numerical summary were received. Four redundant exact scalar fields in the omitted region are recorded as null; their formulas are C5–C8. The surviving displacement-vector key suffix was associated with the full key explicitly present in the executed program. The capture provenance describes that representation repair. No received value was invented, and the successful science was not rerun for a longer serialization.

Related execution files: [call input](../evidence/FULL_SOURCE_CERTIFICATE_CALL_INPUT.json), [executed code copy](../evidence/FULL_SOURCE_CERTIFICATE_EXECUTED.wl), [raw response](../evidence/FULL_SOURCE_CERTIFICATE_RAW.json), [received-field result](../evidence/FULL_SOURCE_CERTIFICATE_RESULT.json). The proofs, rather than the number of check groups, justify whole-domain claims.
