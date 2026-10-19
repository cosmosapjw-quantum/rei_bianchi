# RUN17: invariant first-birth reconstruction and local residual transfer

## New contribution and actual scope

This unit advances **P4-S4C-SPECTRAL-EDGE-SUPPORT**, specifically the
gas-path and opacity-feedback error after the first photon birth. It reuses
RUN16's fixed-support survivor derivative and conditional logarithmic-norm
comparison; it does not replay those proofs or the old M2 trajectories.

The new constructions are an affine invariant gas reconstruction with
checkable physical-domain margins, an event-aware gas/depth residual,
a signed endpoint decomposition for two defined paths, and a nonsingular
constant-forcing transfer map that exposes the first orders at which optical
memory affects local error. It also states precisely what upgrades a sampled
residual diagnostic to a continuous estimate.

Actual source checkout read: commit
**45ee7192b9d405214ec2650185aeaaa635e0fa13** in
/tmp/rei_run17_repo. Individual reused file identities are in
SOURCE_AND_RETRIEVAL_RECEIPT.json.

The selected interval is

\[
z_a=0.004989333151072248,\qquad
z_b=0.02371416180174271,\qquad h=z_b-z_a.
\]

Here \(z=(X-0.7)/0.0004\). The original event partition identifies these
as the first and second photon births, with **252 active reflection-quotient
cohorts** between them. All original 48 spectral cells enter their gas
forcing. The first threshold event is later, at
\(z=0.04632015265112987\). Use the outgoing first-birth branch and the
incoming second-birth branch; the new second-birth cohorts are absent from
this panel's right-limit calculation.

The source remains the original finite M2 packet: 160 birth samples, GL8,
unchanged atomic owners and prescribed BASS121 SIGNED_MINUS geometry.
The metric is \((- ,+,+,+)\); \(c\) and \(k_B\) remain explicit below.
No \(\hbar=1\) convention is introduced. This kinetic opacity formulation
does not require an additional explicit \(\hbar\) factor.

## 1. An invariant gas path with explicit physical margins

Use the initial invariant totals
\(h_*,d_*,e_*\) for H, D, and He and the initial scaled thermal energy \(U_0\).
They are inherited constants, not re-fitted separately at each checkpoint.
For the five coordinates \(q=(q_H,q_D,q_1,q_2,q_U)\), define

\[
\begin{aligned}
Y_{\mathrm{HI}}&=h_*(1-q_H),&
Y_{\mathrm{HII}}&=h_*q_H,\\
Y_{\mathrm{DI}}&=d_*(1-q_D),&
Y_{\mathrm{DII}}&=d_*q_D,\\
Y_{\mathrm{HeI}}&=e_*(1-q_1-q_2),&
Y_{\mathrm{HeII}}&=e_*q_1,&
Y_{\mathrm{HeIII}}&=e_*q_2,\\
U&=U_0q_U.
\end{aligned}
\tag{1}
\]

The unused original isotope spectators stay zero. This is an affine map
\(Y=Y_c+Lq\); therefore every polynomial reconstruction of \(q\) preserves
all three nuclear totals algebraically, and \(Y'=Lq'\).
This repairs the specific RUN16 issue that fourteen independently shaped
PCHIPs need not preserve the helium total between knots.

A linear interpolation between admissible \(q\) endpoints stays in the
convex domain

\[
0\le q_H,q_D\le1,\qquad q_1,q_2\ge0,\qquad q_1+q_2\le1,\qquad q_U>0.
\tag{2}
\]

A PCHIP or DOP853 dense polynomial can preserve (1) through the same lift,
but its physical margins require checks. Separate scalar shape preservation
does not control \(q_1+q_2\). On every polynomial piece evaluate the extrema
of the polynomials in (2), using endpoints and all interior critical points.

For the native EOS let
\(N_p(q)=\sum_s(1+Z_s)Y_s(q)\), which is affine in \(q\). Then

\[
T(q)=\frac{2U_0e_{\rm V}q_U}{3k_BN_p(q)},\qquad
e_{\rm V}=1.602176634\times10^{-19}\ {\rm J}.
\tag{3}
\]

After checking \(N_p>0\), the native Savin domain
\(T_{\min}=2.7\ {\rm K}\), \(T_{\max}=200000\ {\rm K}\) can be checked
without optimizing a rational function: the two polynomial inequalities are

\[
2U_0e_{\rm V}q_U-3k_BT_{\min}N_p\ge0,\qquad
3k_BT_{\max}N_p-2U_0e_{\rm V}q_U\ge0.
\tag{4}
\]

For cubic pieces only quadratic critical-point equations are needed.
Floating polynomial roots and padded extrema are numerical domain checks
unless the root isolation and rounding treatment provide a verified
enclosure. Record their method and margins.

Recovering the lower populations through (1) can change the raw saved gas
by its floating invariant drift. Keep
\(d_k=Y_c+Lq_k-Y_k^{\rm saved}\) as a measured reconstruction discrepancy;
the reconstructed path has new provenance, not byte identity with the
original fourteen-component interpolant. Do not clip populations after
differentiation: clipping changes the path and its residual.

## 2. Continuous paths, event sides, and full forcing

On the fixed event branch let

\[
K_{ia}(z)=\frac{c\,\Delta X}{H(z)}
           \sigma_a(E_i(z))\frac{n_{H,0}}{V(z)},\qquad
V=(a/a_0)^3,\quad \Delta X=0.0004,
\tag{5}
\]

where the absorber order is HI, HeI, HeII, DI. The proper density is
\(n_s=n_{H,0}Y_s/V\), and \(dt/dz=\Delta X/H\).
Each \(K_{ia}Y_{\ell(a)}\) is a dimensionless optical-depth rate per \(z\).
For positive original source weights \(B_i\),

\[
p_i=B_i e^{-\tau_i},\qquad
q'=G(z,q)+\Phi_Q(z,q,\tau),\qquad
\tau'_i=\sum_aK_{ia}Y_{\ell(a)}(q),
\tag{6}
\]

\[
\Phi_Q=\sum_{i,a}v_{ia}(z)K_{ia}
              Y_{\ell(a)}(q)B_i e^{-\tau_i}.
\tag{7}
\]

The \(v_{ia}\) implement the original species stoichiometry and heating
\((E_i-\chi_a)/U_0\). Binding energy enters the heat; the fitting edge
selects the cross-section branch. In particular, keep H binding
13.598434599702 eV distinct from H fit 13.6 eV. D remains the
threshold-gated H-shape approximation with gate 13.602134599702 eV.
The full four-channel forcing in (7) must be evaluated even though the
separate retained sub-H survivor core is H-only and D-inactive.

For a chosen differentiable gas reconstruction \(\hat q\), two useful
depth reconstructions are:

- The native-control dense depth polynomial \(\hat\tau_D\), whose
  derivative is obtained analytically from its saved polynomial coefficients.
- The path-consistent optical integral
  \[
  \hat\tau_{I,i}(z)=\int_{z_a}^{z}
          \sum_a K_{ia}(s)Y_{\ell(a)}(\hat q(s))\,ds.
  \tag{8}
  \]
  All cohorts on this first-birth panel have initial depth zero.

The exact mathematical integral in (8) has zero depth residual. A numerical
approximation to it has a separate optical quadrature uncertainty. If
\(\|\hat\tau_{\rm num}-\hat\tau_I\|_\infty\le\eta_\tau(z)\), a bound
on \(\|\Phi_\tau\|_\infty\) over the intervening depths transfers it to
at most \(b(z)\eta_\tau(z)\) in the gas forcing. A comparison between two
quadrature orders measures finite quadrature sensitivity; it does not alone
establish \(\eta_\tau\).

For either reconstruction define

\[
r_q=\hat q'-G(z,\hat q)-\Phi_Q(z,\hat q,\hat\tau),\qquad
r_\tau=\hat\tau'-K(z)Y_\ell(\hat q).
\tag{9}
\]

The native gas owner includes expansion and the inherited masks/rates.
The photo owner includes the complete spectral absorption and heating;
a small terminal survivor tail does not control this earlier forcing.

For multiple panels, split at every actual birth, threshold event, geometry
piece, gas reconstruction knot and dense-output step boundary. At a shared
birth, the gas and previously active depths are continuous; newly active
depths start at zero, while the photon population has the known source jump
\(p_i(z_{b,i}^{+})=B_i\). Inactive slots make this an activation change
rather than an unexplained gas/depth reset. A reconstruction discontinuity,
different source weight, or uncertain event location contributes its own
initial/jump/source term. No differentiability through a forcing jump is
assumed.

Local absorption/heat ledgers can start at zero at \(z_a\). They measure
only this panel and do not convert the prefix gas state into a complete
historical transport checkpoint.

## 3. Signed endpoint balance for two defined paths

Let \(P=(q_P,\tau_P)\) be the invariant PCHIP plus same-path depths, and
\(R=(q_R,\tau_R)\) be the new native-control dense reconstruction.
Use the explicit orientation

\[
\delta=P-R,\qquad r_P=P'-F(P),\qquad r_R=R'-F(R).
\]

Then the following identity is exact for these defined paths:

\[
\delta'=F(P)-F(R)+(r_P-r_R).
\tag{10}
\]

For the gas block it yields the directly calculable decomposition

\[
\begin{aligned}
\delta_q(z_b)=\delta_q(z_a)
&+\int_{z_a}^{z_b}\big[G(z,q_P)-G(z,q_R)\big]\,dz\\
&+\int_{z_a}^{z_b}\big[\Phi_Q(P)-\Phi_Q(R)\big]\,dz\\
&+\int_{z_a}^{z_b}(r_{P,q}-r_{R,q})\,dz .
\end{aligned}
\tag{11}
\]

Retain the dense-output residual \(r_R\): calling \(R\) a numerically
integrated reference does not make it an exact ODE solution. The HI sign is

\[
Y_{{\rm HI},P}-Y_{{\rm HI},R}=-h_*\,\delta_{q_H}.
\tag{12}
\]

The verified RUN16 prefix-C result provides the numerical initial reference
\(Y_{\rm HI}(z_a)=0.9000000534472483\),
\(T(z_a)=9999.925747777985\ {\rm K}\).
Its recorded fourteen-component PCHIP-minus-prefix HI relative difference
is \(-1.5712776951781748\times10^{-6}\). Recompute the initial discrepancy
for the newly defined invariant PCHIP, because (1) can change it by the
recorded invariant drift. All newborn depth differences are zero.
The prefix's step-size contrast is numerical evidence; any comparison
against the exact IVP still carries its unestablished initial error.

Equation (11) gives a useful physical diagnostic: compare the inherited
initial discrepancy, direct native-reaction drift, photo-forcing drift,
and integrated reconstruction defect. Closure of the decomposition is an
algebraic/numerical consistency check for two defined paths, not an IVP
error certificate. Integrating both sides of a pointwise identity with the
same nodes can produce tiny closure error without making its terms accurate.

For a signed local linear estimate, freeze or reconstruct a stated block
Jacobian \(J_*\), propagate the actual initial vector difference and the
signed residual difference, and record the ignored term
\(F(P)-F(R)-J_*\delta\). Its smallness must be measured or bounded.
A 2-by-2 norm comparison instead gives magnitudes and deliberately removes
cancellation; it should not be presented as a signed explanation.

## 4. Constant-forcing comparison without a singular inverse

Reuse RUN16's conditional comparison for
\(u=\|e_q\|_\infty\), \(v=\|e_\tau\|_\infty\), with genuine tube bounds
\(a\ge\mu_\infty(G_q+\Phi_q|_\tau)\),
\(b\ge\|\Phi_\tau\|_\infty\), \(c\ge\|KY_{\ell,q}\|_\infty\).
For piecewise constant residual upper bounds \(\rho=(\rho_q,\rho_\tau)^T\),
set

\[
M=\begin{pmatrix}a&b\\c&0\end{pmatrix},\qquad
\mathcal A=
\begin{pmatrix}a&b&\rho_q\\c&0&\rho_\tau\\0&0&0\end{pmatrix}.
\]

The exact comparison propagation across one interval is

\[
w(h)=\left[
e^{h\mathcal A}\begin{pmatrix}u_0\\v_0\\1\end{pmatrix}
\right]_{1:2}
=e^{hM}w_0+\int_0^h e^{(h-s)M}\rho\,ds.
\tag{13}
\]

It holds when \(M\) is singular, including \(b=0\) or \(c=0\).
The proof follows by differentiating the augmented linear system; equivalently,
\((\mathcal A^j)_{1:2,3}=M^{j-1}\rho\) for every \(j\ge1\).
The entire series is \(h\varphi_1(hM)\rho\), not an instruction to invert \(M\).
The off-diagonal entries are nonnegative, so its comparison propagator is
positive even when the direct gas coefficient \(a\) is negative.
No strict contraction less than one is needed on a finite interval.

The first new diagnostic consequence is visible in its series. For
\(w_0=0,\rho_\tau=0\),

\[
u(h)=\rho_qh+\frac{a\rho_q}{2}h^2+
             \frac{(a^2+bc)\rho_q}{6}h^3+O(h^4),\qquad
v(h)=\frac{c\rho_q}{2}h^2+\frac{ac\rho_q}{6}h^3+O(h^4).
\tag{14}
\]

Optical feedback from a continuously injected gas defect first contributes
\(bc\rho_qh^3/6\). In this actual first-birth comparison, however,
\(u_0\ne0,v_0=0\), and the propagated initial error includes

\[
u_{\rm initial}(h)=u_0+au_0h+
                       \frac{(a^2+bc)u_0}{2}h^2+O(h^3).
\tag{15}
\]

Thus initial gas uncertainty reaches gas again through optical memory already
at order \(h^2\). A nonzero depth residual gives the additional
\(b\rho_\tau h^2/2\) gas term. These are expansions of the specified local
comparison system, not inferred asymptotic orders of the spectral method.

For reference, with \(d=\sqrt{a^2+4bc}\),

\[
e^{hM}=e^{ah/2}\left[
\cosh(dh/2)I+\frac{2\sinh(dh/2)}{d}(M-aI/2)\right].
\tag{16}
\]

The \(d=0\) value is obtained by continuity. The augmented implementation
avoids both this special-case division and subtractive cancellation in
\(M^{-1}(e^{hM}-I)\).

Actual Wolfram evaluation checked the power identities for orders 1--6,
the displayed exponential's differential equation and initial value,
the zero-matrix forcing limit, and the coefficients in (14)--(15).
The complete query/output, including its emitted undefined-global-symbol
precheck warning, is retained in WOLFRAM_LOCAL_COMPARISON_RECEIPT.json.
The explicit symbolic outputs evaluated successfully; the warning is not
silently removed.

## 5. From sampled residual to a continuous estimate

A finite set of residual values supplies a sampled maximum. A constructive
upgrade needs a variation or integration-error bound. On a smooth panel,
the exact derivatives of (9) are

\[
\begin{aligned}
r_q'&=\hat q''-G_z-G_q\hat q'
       -\Phi_z-\Phi_q\hat q'-\Phi_\tau\hat\tau',\\
r_\tau'&=\hat\tau''-K'Y_\ell(\hat q)
                     -KY_{\ell,q}\hat q'.
\end{aligned}
\tag{17}
\]

Polynomial first and second derivatives are available analytically. To use
(17) as a continuous bound also requires bounds on the native-rate and
radiative derivatives over the relevant physical tube and event branch.

If \(\|r'\|_\infty\le L_r\) and the sample set has fill distance
\(\delta_Z=\max_z\min_{s\in Z}|z-s|\), then

\[
\sup_z\|r(z)\|_\infty
\le \max_{s\in Z}\|r(s)\|_\infty+L_r\delta_Z.
\tag{18}
\]

This follows directly from the fundamental theorem of calculus. A derivative
inferred only from the same finite samples is not yet such an \(L_r\).

A uniform residual supremum is sufficient but not necessary. The positive
comparison also admits a validated weighted integral

\[
w(z_b)\le\Psi(z_b,z_a)w(z_a)
 +\int_{z_a}^{z_b}\Psi(z_b,s)
       \begin{pmatrix}\|r_q(s)\|_\infty\\\|r_\tau(s)\|_\infty\end{pmatrix}ds.
\tag{19}
\]

An enclosure of this weighted integral can be sharper and easier than
enclosing every point by one maximum. Quadrature-order contrasts and
additional samples are useful numerical diagnostics; rigorous quadrature
remainders or equivalent validated integration are the additional ingredient
for an enclosure.

Do not omit event strips in applying (17)--(19). A branch discrepancy over
a time strip of width \(\epsilon_z\) contributes at most the integral of
the forcing mismatch there (or a verified mismatch supremum times
\(\epsilon_z\)). Interpolate and differentiate only within the frozen branch.

The positive polynomial-domain margins of Section 1 establish a property
of the reconstruction. They do not establish that the exact solution lies
in the chosen tube. Closing that condition uses a self-consistent error
bound and continuation/bootstrap argument.

## 6. Source continuum and the next calculable extension

For the exact same finite M2 source, its source-discretization mismatch
relative to that finite system is zero. For a continuous first-cell target
\(\mu\), at the same gas reconstruction and its same-path optical integrals,

\[
r_q^\mu=r_q^Q+\Phi_Q[\hat q]-\Phi_\mu[\hat q].
\tag{20}
\]

All first-cell absorption channels and heat enter this extra term, including
photons that contribute almost nothing to a terminal sub-H survivor.
The other 47 cells, finite births, GL8, geometry and native providers remain
fixed for the current comparison. Their separate continuum/feedback
obligations remain in the original DAG.

The current short panel can therefore produce useful new numerical results
without asserting a global tube: physical invariant reconstruction margins;
analytic dense-output residual samples; finite quadrature sensitivity for
path-consistent depths; the signed balance (11); and a clearly labeled
constant-coefficient transfer diagnostic (13). A verified \(L_r\), weighted
defect enclosure, or tube bound is a concrete next increment once the
measured sizes identify which term matters.

## Primary evidence reused and added

- RUN16 theory and feedback artifacts are reused through their actual file
  hashes and commit45ee. The short prefix-C initial state is read from the
  original published JSON with SHA-256
  69cd9e459991fa7f0bf1ed6fed12bedbadffc1b5451ad0b8a380235e8f8813eb.
- Al-Mohy and Higham, *SIAM Journal on Scientific Computing* 33(2),
  488--511 (2011), DOI10.1137/100788860: Section2, Theorem2.1,
  equations(2.6)--(2.10), provides the general augmented-exponential identity.
  Primary full text actually read:
  https://eprints.maths.manchester.ac.uk/1591/1/alhi11.pdf .
- SciSpace located Akrivis, Makridakis and Nochetto,
  DOI10.1007/s00211-009-0254-2; Exa returned the primary abstract and author
  PDF location. The two attempted full-text web endpoints failed. Its
  abstract supports the relevance of continuous reconstruction, but no
  theorem or optimal-order claim from that unread full text is imported
  into DOP853 here.
- RUN16's already-read Ranocha--Giesselmann residual/one-sided stability
  evidence is reused; this unit contributes the concrete post-birth
  reconstruction, signed decomposition and local forcing map.

This theory unit performs no native integration and no old M2 rerun.
Root and the runtime agent own the new numerical control and its execution
receipts. One scoped implementation review will be added when those files
and results are frozen.

