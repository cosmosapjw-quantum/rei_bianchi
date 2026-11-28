# Covariant radiation energy projection and a paired-beam construction

BASS_HE THEORY04 — geometric and constructive contribution  
2026-10-12 UTC · physmath-research-loop built-in 1.0.0  
Author role: independent derivation producer. Final adoption belongs to the separate reviewer.

## 1. Result and relation to the retained source

For a unit timelike gas frame \(u^a\), the radiation tensor specified in Section 2 obeys the exact projection identity

\[
\boxed{-c u_b\nabla_aT_\gamma^{ab}
 =\dot\rho+\frac43\Theta\rho+D_aq^a
 +\frac{2a_aq^a}{c^2}+\sigma_{ab}\pi^{ab}.}
\tag{G1}
\]

In a homogeneous geodesic Bianchi-I gas frame, a nonnegative antipodal beam distribution can have zero flux and zero absorbed spatial momentum while retaining a nonzero anisotropic stress and nonzero shear work. Its moments give

\[
\sigma:\pi=\sum_q E_qn_q\,\sigma_{ab}e_q^ae_q^b
 =2s(P_\parallel-P_\perp)
\tag{G2}
\]

for the selected axisymmetric shear convention \(\sigma_{\hat\imath\hat\jmath}=\mathrm{diag}(-s,-s,2s)\). Directional geodesic transport and parity-even absorption preserve this construction.

The finite endpoint-energy reaction stage has the exact history-energy budget

\[
\boxed{\mathcal E_\gamma^+-\mathcal E_\gamma^-
 +\mathcal W_\gamma+\sum_{a,q}E_q^+A_{aq}
 =h\sum_qE_q^+S_q^*,\qquad
 \mathcal W_\gamma=-\sum_q(E_q^+-E_q^-)N_q^-.}
\tag{G3}
\]

Here \(N_q=Vn_q\), \(S_q=V\mathfrak s_q\), and \(A_{aq}\) are reference-volume photon counts, source rates, and integrated absorption counts. Equation (G3) uses the incoming population because the reaction/source increment is valued at endpoint energy.

**Reused foundation.** The selected source already implements \(\dot\rho=-4H\rho-2s\Delta P+Q_\gamma\), the moment \(\Delta P\), directional photon redshift, and the reference work \(V(H\rho+2s\Delta P+2Hu_g)\). These are [S1–S3] below. PRIMARY_THEORY_03 already derived the reference/source normalization and the scalar product rule in (G3) [P3, Sections 3 and 8]. The contribution here is their explicit covariant projection and a constructive angular realization, including paired momentum cancellation, a two/six-beam family, and its directional finite-step energy map.

## 2. Conventions, units, and assumptions

Use signature \((-+++)\), \(u_au^a=-1\), physical four-velocity \(cu^a\), and

\[
h_{ab}=g_{ab}+u_au_b,\qquad
\dot f=c u^a\nabla_af,\qquad
\Theta=c\nabla_au^a,\qquad
a^a=c^2u^b\nabla_bu^a.
\tag{G4}
\]

The projected derivative is \(D_a=h_a{}^b\nabla_b\), with projection also on every free spatial tensor index. The physical shear and vorticity have units \({\rm s}^{-1}\), and

\[
\nabla_au_b
 =-\frac{u_aa_b}{c^2}
 +\frac1c\left(\frac{\Theta}{3}h_{ab}+\sigma_{ab}+\omega_{ab}\right).
\tag{G5}
\]

Both \(\sigma\) and \(\omega\) are spatial; \(\sigma\) is symmetric and trace-free, and \(\omega\) is antisymmetric. The acceleration is spatial.

The radiation decomposition is

\[
T_\gamma^{ab}
 =\rho u^au^b+\frac{u^aq^b+q^au^b}{c}
 +\frac{\rho}{3}h^{ab}+\pi^{ab},
\tag{G6}
\]
\[
u_aq^a=0,\qquad u_a\pi^{ab}=0,\qquad
\pi^{ab}=\pi^{ba},\qquad h_{ab}\pi^{ab}=0.
\]

Here \(\rho\) is energy density, not mass density. The coefficient \(\rho/3\) is the mean pressure of the massless population and does not require isotropic angular occupation. The flux \(q^a\) is energy per area per time; \(\pi^{ab}\) is anisotropic pressure. Every term in (G1) has units of power per proper volume.

Photon energies \(E_q=\hbar\omega_q\) in this note are physical energies in erg. The native cross-section/source argument is \(e_q\) in eV:

\[
E_q=\epsilon_{\rm eV}e_q,\qquad
\epsilon_{\rm eV}=1.602176634\times10^{-12}\ {\rm erg/eV}.
\tag{G7}
\]

Thus \(\sigma_a(e_q)\) and \(j_{\log}(e_q,z)\) retain their native eV arguments, while \(E_qn_q\), \(E_qA_{aq}\), and all work terms use erg. The source converts \(n\) in \({\rm cm}^{-3}\) to \(10^6n\) in \({\rm m}^{-3}\), and \(\rho\) in \({\rm erg\,cm}^{-3}\) to \(0.1\rho\) in \({\rm J\,m}^{-3}\) [S2, 388–436].

The derivation uses the following assumptions:

1. The metric, unit frame, and moment fields are differentiable as required by (G1). The beam realization uses a finite sum with \(E_q>0\), \(n_q\ge0\), and spatial unit directions \(e_q^ae_{qa}=1\).
2. The constructive specialization is test radiation on a prescribed diagonal Bianchi-I geometry, in one common geodesic gas frame. The homogeneous gas lower-state densities are finite and nonnegative. No Einstein-background solve is required by this kinematic construction.
3. Absorption acts diagonally on the characteristic nodes once the candidate gas state and stage geometry are specified. The channels are HI, HeI, and HeII. Their existing scalar cross sections remain the native provider functions. The selected primary-only Case A setting retains prescribed external photon sources; the parent's gas/escape ledger owns recombination escape.
4. Antipodal pairs have matched energies, counts, and sources, with equal opacity within each pair. Opacities and counts may differ between pairs.
5. The finite stage uses the retained reference-volume variable and endpoint-energy backward-Euler reaction/source placement. Its exact ledger describes that discrete map. The continuous identities describe differentiable transport with local sources.

The parent's contribution owns the covariant gas/binding/escape exchange and closure. The angular construction here supplies the radiation projection and the conditions under which its absorbed spatial momentum vanishes.

## 3. Derivation of the covariant energy equation

### 3.1 Contract the stress tensor before differentiating

From (G6),

\[
u_bT_\gamma^{ab}=-\rho u^a-\frac{q^a}{c}.
\tag{G8}
\]

Apply the product rule to its divergence:

\[
\begin{aligned}
-c u_b\nabla_aT_\gamma^{ab}
 &=-c\nabla_a(u_bT_\gamma^{ab})
   +cT_\gamma^{ab}\nabla_au_b\\
 &=\dot\rho+\Theta\rho+\nabla_aq^a
   +cT_\gamma^{ab}\nabla_au_b.
\end{aligned}
\tag{G9}
\]

This step fixes the sign convention: if \(\nabla_aT_\gamma^{ab}=G_\gamma^b\), the local photon energy source is

\[
Q_\gamma=-c u_bG_\gamma^b.
\tag{G10}
\]

A positive \(Q_\gamma\) adds photon energy in the gas frame.

### 3.2 Evaluate the kinematic contraction

The four contributions to the last term in (G9) are

\[
\begin{array}{c|c}
\text{part of }T_\gamma^{ab} & cT_\gamma^{ab}\nabla_au_b\\ \hline
\rho u^au^b &0\\
(u^aq^b+q^au^b)/c & a_bq^b/c^2\\
(\rho/3)h^{ab} & \rho\Theta/3\\
\pi^{ab} & \sigma_{ab}\pi^{ab}.
\end{array}
\tag{G11}
\]

For the first and the \(q^au^b\) contributions, \(u^b\nabla_au_b=0\) follows from unit normalization. The other flux contribution is

\[
u^aq^b\nabla_au_b=\frac{a_bq^b}{c^2}.
\]

In the pressure contribution, \(ch^{ab}\nabla_au_b=\Theta\). In the anisotropic term, spatiality removes the acceleration factor, trace freedom removes \(\Theta h_{ab}/3\), and symmetry removes \(\omega_{ab}\).

### 3.3 Convert the flux divergence to its spatial divergence

The definition of \(D\) and differentiation of \(u_aq^a=0\) give

\[
\begin{aligned}
D_aq^a
 &=h_a{}^b\nabla_bq^a
 =\nabla_aq^a+u_au^b\nabla_bq^a\\
 &=\nabla_aq^a-q^au^b\nabla_bu_a
 =\nabla_aq^a-\frac{a_aq^a}{c^2}.
\end{aligned}
\tag{G12}
\]

Consequently,

\[
\nabla_aq^a=D_aq^a+\frac{a_aq^a}{c^2}.
\]

Substituting this relation and (G11) into (G9) proves (G1). One acceleration-flux term comes from differentiating the frame in \(T_\gamma\); the other comes from converting the four-divergence of the spatial flux to \(D_aq^a\).

With (G10), the local evolution equation is therefore

\[
\dot\rho
 =-\frac43\Theta\rho-D_aq^a-\frac{2a_aq^a}{c^2}
 -\sigma_{ab}\pi^{ab}+Q_\gamma.
\tag{G13}
\]

This projection follows from the tensor decomposition, unit normalization, and spatial kinematics.

## 4. Bianchi-I specialization and the photon moment map

### 4.1 Geometry and node stress tensor

Consider

\[
ds^2=-c^2dt^2+\sum_{i=1}^3a_i(t)^2(dx^i)^2,\qquad
u=\frac1c\partial_t.
\tag{G14}
\]

The spatial orthonormal frame is \(e_{\hat\imath}=a_i^{-1}\partial_i\). Let

\[
H_i=\frac{\dot a_i}{a_i},\qquad
H=\frac{H_1+H_2+H_3}{3},\qquad
\Theta=3H,\qquad
\sigma_{\hat\imath\hat\jmath}=(H_i-H)\delta_{ij}.
\tag{G15}
\]

The normal congruence is geodesic and irrotational. For homogeneous \(q^a=0\), (G13) becomes

\[
\boxed{\dot\rho=-4H\rho-\sigma:\pi+Q_\gamma.}
\tag{G16}
\]

For a node direction \(e_q^a\), define the dimensionless null vector \(k_q^a=u^a+e_q^a\). Its physical photon momentum is \(p_q^a=(E_q/c)k_q^a\). The nonnegative beam stress tensor is

\[
T_\gamma^{ab}=\sum_q E_qn_q\,k_q^ak_q^b.
\tag{G17}
\]

Expanding (G17) and comparing with (G6) yields

\[
\boxed{
\rho=\sum_qE_qn_q,\quad
q^a=c\sum_qE_qn_qe_q^a,\quad
P^{ab}=\sum_qE_qn_qe_q^ae_q^b,\quad
\pi^{ab}=P^{ab}-\frac{\rho}{3}h^{ab}.}
\tag{G18}
\]

The spatial trace of \(P\) is \(\rho\), because every \(e_q\) is a unit vector. Contraction with the trace-free shear gives the first equality in (G2).

### 4.2 Axisymmetric reduction and the existing pressure variable

Set \(H_1=H_2=H-s\) and \(H_3=H+2s\). Then

\[
\sigma=\mathrm{diag}(-s,-s,2s),\qquad
\sigma:\pi=-sP_{11}-sP_{22}+2sP_{33}.
\]

Define

\[
P_\parallel=P_{33},\qquad
P_\perp=\frac{P_{11}+P_{22}}2,\qquad
\Delta P=P_\parallel-P_\perp.
\tag{G19}
\]

For axisymmetric moments, \(P_{11}=P_{22}=P_\perp\). The contraction also has the form \(2s\Delta P\) for a general node distribution in this diagonal shear, with \(P_\perp\) interpreted as the transverse average.

Writing \(\mu_q=e_q^{\hat3}\),

\[
\boxed{\Delta P
 =\frac12\sum_q(3\mu_q^2-1)E_qn_q,\qquad
 \sigma:\pi=2s\Delta P.}
\tag{G20}
\]

Since \(0\le\mu_q^2\le1\) and \(E_qn_q\ge0\),

\[
-\frac{\rho}{2}\le\Delta P\le\rho.
\tag{G21}
\]

This is the pressure-domain guard already present in [S1, 208–209]. The moment accumulation in [S2, 401–403] is exactly (G18)/(G20), and [S1, 254–256] evaluates (G16) as

\[
\dot\rho=-4H\rho-2s\Delta P+Q_\gamma.
\]

### 4.3 Directional energy and direction evolution

Spatial translation invariance implies conservation of the covariant spatial momenta

\[
K_i=\frac{a_iEe^{\hat\imath}}{c}
\tag{G22}
\]

along a photon geodesic. Equivalently, the geodesic equation for \(p_i\) has right-hand side \(\tfrac12(\partial_i g_{ab})p^ap^b=0\). The null constraint gives

\[
E=c\left(\sum_i\frac{K_i^2}{a_i^2}\right)^{1/2}.
\]

Its logarithmic derivative and the direction derivative are

\[
\boxed{\frac{\dot E_q}{E_q}
 =-\sum_iH_i(e_q^{\hat\imath})^2
 =-\left[H+\sigma_{ab}e_q^ae_q^b\right]\equiv-\nu_q,}
\tag{G23}
\]
\[
\boxed{\dot e_q^{\hat\imath}
 =-(H_i-\nu_q)e_q^{\hat\imath}.}
\tag{G24}
\]

The direction remains unit length: its norm derivative is
\(-2\sum_iH_ie_i^2+2\nu_q\sum_i e_i^2=0\).
Equations (G23)–(G24) preserve \(E_{k,+}=E_{k,-}\) and \(e_{k,-}=-e_{k,+}\) for an antipodal pair.

For arbitrary two prescribed endpoints, define

\[
r_i=\frac{a_i^-}{a_i^+}>0,\qquad
R_q=\left[\sum_i r_i^2(e_q^{\hat\imath,-})^2\right]^{1/2}.
\]

Then the exact characteristic map is

\[
\boxed{E_q^+=E_q^-R_q,\qquad
e_q^{\hat\imath,+}=\frac{r_ie_q^{\hat\imath,-}}{R_q}.}
\tag{G25}
\]

The energy ratio is even under direction reversal, and the endpoint direction is odd. This supplies the directional energy arrays needed by (G3) without a new radiation evolution run.

### 4.4 Continuous reference-volume work

Choose a fixed reference volume and let

\[
V(t)=\frac{a_1(t)a_2(t)a_3(t)}
 {a_1(t_{\rm ref})a_2(t_{\rm ref})a_3(t_{\rm ref})},
\qquad \dot V=\Theta V.
\tag{G26}
\]

For proper node source \(\mathfrak s_q\) and total opacity \(\lambda_q\),

\[
\dot n_q=-\Theta n_q+\mathfrak s_q-\lambda_qn_q,\qquad
\dot N_q=S_q-\lambda_qN_q.
\tag{G27}
\]

Differentiating \(\rho=\sum E_qn_q\) using (G23) and (G27) reproduces (G16), with

\[
Q_\gamma=\sum_qE_q(\mathfrak s_q-\lambda_qn_q).
\]

For reference photon energy \(\mathcal E_\gamma=V\rho=\sum_qE_qN_q\),

\[
\boxed{\dot{\mathcal E}_\gamma
 =\sum_qE_qS_q-\sum_qE_q\lambda_qN_q
 -V(H\rho+\sigma:\pi).}
\tag{G28}
\]

The factor \(4H\) in the proper-density equation becomes \(H\) in the reference-energy work: differentiating \(V\rho\) supplies \(3H V\rho\). With (G20), the photon term is \(V(H\rho+2s\Delta P)\). Adding the retained ideal-gas thermal work gives the source's existing \(V(H\rho+2s\Delta P+2Hu_g)\) [S2, 480–483].

## 5. Constructive antipodal absorption model

### 5.1 Pair variables and zero odd moments

Index the pairs by \(k\) and their two directions by \(\zeta=\pm1\). Let

\[
e_{k,\zeta}=\zeta e_k,\qquad
E_{k,\zeta}=E_k,\qquad
N_{k,\zeta}=\frac{N_k}{2},\qquad N_k\ge0.
\tag{G29}
\]

Here \(N_k\) is the total reference count of a pair. Equations (G18) become

\[
\rho=\frac1V\sum_kE_kN_k,\qquad q^a=0,\qquad
P^{ab}=\frac1V\sum_kE_kN_ke_k^ae_k^b.
\tag{G30}
\]

The odd first moment cancels pairwise. The even second moment adds pairwise.

For \(a\in\{\mathrm{HI},\mathrm{HeI},\mathrm{HeII}\}\), set

\[
\lambda_{ak}(t)
 =c\,\ell_a(t)\,
 \sigma_a\!\left(\frac{E_k(t)}{\epsilon_{\rm eV}}\right)\ge0,
\qquad \lambda_k=\sum_a\lambda_{ak}.
\tag{G31}
\]

The \(\ell_a\) are the common-frame proper lower-state densities. These are the actual native scalar opacity factors [S2, 388–399]. Opposite members of a pair have the same energy, hence the same opacity for every species. Different directions can have different energies under (G23), so (G31) supplies direction-dependent opacities through the existing energy-dependent cross sections. Each direction uses the same existing energy-dependent atomic fit.

The absorbed proper power and spatial momentum per proper volume per time are

\[
Q_{\rm abs}
 =\frac1V\sum_{a,k,\zeta}E_k\lambda_{ak}N_{k,\zeta}
 =\frac1V\sum_{a,k}E_k\lambda_{ak}N_k,
\tag{G32}
\]
\[
f_{\rm abs}^{\,a}
 =\frac1{cV}\sum_{a',k,\zeta}
 E_k\lambda_{a'k}N_{k,\zeta}e_{k,\zeta}^{a}=0.
\tag{G33}
\]

Cancellation holds for each absorber separately. Whenever an occupied pair has a positive absorption coefficient, \(Q_{\rm abs}>0\) while the absorbed spatial momentum remains zero. Equations (G30) and (G2) leave the anisotropic stress and shear work available independently of this cancellation.

### 5.2 Continuous preservation and the native source parity

Give each pair a matched source \(S_{k,\zeta}=S_k/2\). Subtracting the two reference equations in (G27) yields

\[
\frac{d}{dt}(N_{k,+}-N_{k,-})
 =-\lambda_k(t)(N_{k,+}-N_{k,-}).
\tag{G34}
\]

Thus paired initial counts remain paired. This statement continues to hold when \(\lambda_k\) depends on a common evolving nonlinear gas state: the two members receive the same coefficient at every time.

For the retained axisymmetric characteristic, with \(\dot a/a=H\) and \(\dot b=s\),

\[
\mathcal R(q,\mu_0,t)
 =\frac{\sqrt{(1-\mu_0^2)e^{2b}+\mu_0^2e^{-4b}}}{a},
\quad e_q=q_{\rm eV}\mathcal R,\quad
\mu_q=\frac{\mu_0e^{-2b}}{a\mathcal R}.
\tag{G35}
\]

The ratio \(\mathcal R\) and energy are even in \(\mu_0\); \(\mu_q\) is odd. The actual reference source is

\[
S_q=j_{\log}(e_q,z)\,\frac{w_q}{\mathcal R_q^3}.
\tag{G36}
\]

For matched quadrature weights this source is even as well [S3, 107–110 and 156–166]. Equation (G36) already contains the angular/source Jacobian; \(N_q\) and \(S_q\) need no extra angular weight in (G27).

The source survey's static input record identifies 1,452 exactly matched opposite-\(\mu_0\) pairs among 2,904 selected nodes, with identical energy labels, weights, and initial count bits [IP]. Within the axisymmetric interpretation, the azimuth average cancels transverse odd moments and the matched \(\mu_0\) pairs cancel the axial odd moment. The full three-dimensional antipodal construction (G29) makes that angular assumption explicit. The source record establishes the selected input pairing; the proof (G34) establishes preservation under the stated continuous paired equations.

### 5.3 Pair preservation by the endpoint reaction stage

At a candidate endpoint, with prescribed \(h\ge0\), \(V_*>0\), \(E_k^*>0\), \(S_k^*\ge0\), and finite nonnegative \(\lambda_{ak}\),

\[
N_k^+=\frac{N_k^-+hS_k^*}{1+h\lambda_k},\qquad
A_{ak}=h\lambda_{ak}N_k^+.
\tag{G37}
\]

Each denominator is at least one. Applying this update to the two half-count beams gives \(N_{k,\zeta}^+=N_k^+/2\) and \(A_{ak,\zeta}=A_{ak}/2\). Endpoint absorbed momentum cancels with the endpoint directions from (G25):

\[
\sum_{a,k,\zeta}\frac{E_k^+}{c}
 A_{ak,\zeta}e_{k,\zeta}^{a,+}=0.
\tag{G38}
\]

This is a simultaneous nonlinear-stage statement: the endpoint gas state may set \(\ell_a\) and hence \(\lambda_{ak}\), and both pair members consume that same state.

## 6. Two beams and an anisotropic six-beam family

### 6.1 Two axial beams

Take one pair along the symmetry axis, with \(E n_+=E n_-=\rho/2\). Its moments are

\[
q=0,\qquad
P=\mathrm{diag}(0,0,\rho),\qquad
\pi=\rho\,\mathrm{diag}(-1/3,-1/3,2/3),
\tag{G39}
\]
\[
\Delta P=\rho,\qquad \sigma:\pi=2s\rho.
\]

This realizes a nonzero shear contraction for any \(s\rho\ne0\), with the absorbed momentum cancellation of (G33).

### 6.2 Six principal-axis beams

Use the directions \(\pm e_{\hat1},\pm e_{\hat2},\pm e_{\hat3}\). Let the total pair energy fractions be

\[
w_1=w_2=\frac{1-\eta}{2},\qquad w_3=\eta,\qquad 0\le\eta\le1.
\tag{G40}
\]

Each individual beam has half its pair's energy density. For \(0<\eta<1\), all six beams have positive occupation. The exact moments are

\[
q=0,\qquad
P=\rho\,\mathrm{diag}\!\left(\frac{1-\eta}{2},
 \frac{1-\eta}{2},\eta\right),
\tag{G41}
\]
\[
\pi=\rho\,\mathrm{diag}\!\left(\frac{1-3\eta}{6},
 \frac{1-3\eta}{6},\frac{3\eta-1}{3}\right),
\qquad
\Delta P=\frac{\rho}{2}(3\eta-1),
\qquad
\sigma:\pi=s\rho(3\eta-1).
\tag{G42}
\]

| Family member | Pair energy fractions \((w_1,w_2,w_3)\) | \(\Delta P/\rho\) | \((\sigma:\pi)/(s\rho)\) |
|---|---|---:|---:|
| Two axial beams, \(\eta=1\) | \((0,0,1)\) | \(1\) | \(2\) |
| Anisotropic six beams, \(\eta=2/3\) | \((1/6,1/6,2/3)\) | \(1/2\) | \(1\) |
| Isotropic second moment, \(\eta=1/3\) | \((1/3,1/3,1/3)\) | \(0\) | \(0\) |
| Transverse boundary, \(\eta=0\) | \((1/2,1/2,0)\) | \(-1/2\) | \(-1\) |

The \(\eta=1/3\) row has an isotropic second moment at that instant. Its six discrete directions remain explicit; an isotropic second moment does not specify all higher angular moments.

### 6.3 Exact zero-mean-expansion directional-shear example

Choose the prescribed test metric with

\[
H=0,\qquad s>0\ \text{constant},\qquad
a_\perp(t)=a_\perp^-e^{-s(t-t_-)},\quad
a_\parallel(t)=a_\parallel^-e^{2s(t-t_-)}.
\tag{G43}
\]

The volume ratio is constant. Set \(r=e^{s(t-t_-)}\). Principal-axis photon energies evolve as

\[
E_\perp(t)=E_\perp^-r,\qquad
E_\parallel(t)=E_\parallel^-r^{-2}.
\tag{G44}
\]

Thus transverse photons gain energy while axial photons lose energy. For source-free transparent beams whose initial pair energy fractions are (G40),

\[
\frac{\rho(t)}{\rho^-}=(1-\eta)r+\eta r^{-2},\qquad
\frac{\Delta P(t)}{\rho^-}
 =\eta r^{-2}-\frac{1-\eta}{2}r.
\tag{G45}
\]

Direct differentiation gives

\[
\dot\rho=-2s\Delta P,
\tag{G46}
\]

the \(H=0\), \(Q_\gamma=0\) specialization of the retained source law.

For the exact endpoint choice \(sh=\log2\), one has
\(a_\perp^+/a_\perp^-=1/2\), \(a_\parallel^+/a_\parallel^-=4\),
\(V_+/V_-=1\), \(R_\perp=2\), and \(R_\parallel=1/4\). The history-energy/work ratios are

| Initial family | \(\mathcal E_\gamma^+/\mathcal E_\gamma^-\) | \(\mathcal W_\gamma/\mathcal E_\gamma^-\) |
|---|---:|---:|
| Two axial beams, \(\eta=1\) | \(1/4\) | \(3/4\) |
| Anisotropic six beams, \(\eta=2/3\) | \(5/6\) | \(1/6\) |
| Initially isotropic second moment, \(\eta=1/3\) | \(17/12\) | \(-5/12\) |

All three retain \(q=0\). The final row begins with zero instantaneous shear contraction, then develops anisotropic pressure through directional redshift. The negative integrated work there records net energy supplied to the photons by the prescribed anisotropic geometry.

The same geometry supports positive, parity-even absorption. At one endpoint let the native total opacities in the perpendicular and parallel pairs be \(\Lambda_\perp\ge0\) and \(\Lambda_\parallel\ge0\). In the source-free backward-Euler stage, the surviving and absorbed energy fractions are

\[
F=\frac{(1-\eta)r}{1+h\Lambda_\perp}
 +\frac{\eta r^{-2}}{1+h\Lambda_\parallel},
\tag{G47}
\]
\[
B=\frac{(1-\eta)r\,h\Lambda_\perp}{1+h\Lambda_\perp}
 +\frac{\eta r^{-2}\,h\Lambda_\parallel}{1+h\Lambda_\parallel}.
\tag{G48}
\]

The geometry work fraction is

\[
W=1-(1-\eta)r-\eta r^{-2},
\tag{G49}
\]

and \(F+B+W=1\) follows by adding each rational pair. If any occupied pair has positive opacity, \(B>0\); the absorbed momentum is still zero by (G38). Each \(\Lambda\) is the sum of its HI/HeI/HeII coefficients from (G31), so differing directional photon energies can be used without altering the channel law. The rational table above isolates the transparent geometric limit; it is not an evaluation of the native atomic coefficients.

## 7. Exact finite-step work and recovery of the scalar formula

### 7.1 Endpoint energies, reference counts, and proper rates

For a general node \(q\), the source-aware endpoint solve and channel allocation are the retained PRIMARY_THEORY_03 formulas

\[
N_q^+=\frac{N_q^-+hS_q^*}{1+h\lambda_q(x^+)},\qquad
A_{aq}=h\lambda_{aq}(x^+)N_q^+,\qquad
N_q^+-N_q^-=hS_q^*-\sum_aA_{aq}.
\tag{G50}
\]

The opacity uses proper absorber densities, while \(N_q\), \(S_q\), and \(A_{aq}\) use the same reference volume. In proper-density variables the identical map is

\[
n_q^+
 =\frac{(V_-/V_*)n_q^-+h\mathfrak s_q^*}{1+h\lambda_q(x^+)}.
\tag{G51}
\]

An absorption rate is \(P_{aq}=\lambda_{aq}N_q^+/V_*\) per proper volume per time; for \(h>0\), \(A_{aq}=hV_*P_{aq}\). These relations preserve the source/geometry scaling in [P3]. Geometry and node energies are prescribed during the candidate gas solve.

### 7.2 The discrete product rule selects incoming counts

The scalar product identity, applied separately to each direction, is

\[
E_q^+N_q^+-E_q^-N_q^-
 =E_q^+(N_q^+-N_q^-)+(E_q^+-E_q^-)N_q^-.
\tag{G52}
\]

Multiply (G50) by \(E_q^+\), sum, and use (G52). This proves (G3), with the characteristic expression

\[
\boxed{\mathcal W_\gamma
 =\sum_qE_q^-N_q^-\left[
  1-\sqrt{\sum_i
     \left(\frac{a_i^-}{a_i^+}\right)^2
     (e_q^{\hat\imath,-})^2}\right].}
\tag{G53}
\]

For paired beams it becomes
\(\mathcal W_\gamma=\sum_kE_k^-N_k^-(1-R_k)\);
the two half-count members are counted once through \(N_k^-\).

Equation (G52) is equivalent to transporting the incoming photon energies to the endpoint and then applying the endpoint reaction/source increment. Source photons in that increment are assigned \(E_q^+\) once. This specifies why newly injected photons do not receive an additional incoming-history work term in this stage placement.

For transparent source-free characteristic nodes, \(N_q\) is constant, and (G53) also equals the exact continuous geometric work integral
\(\int_{t_-}^{t_+}\sum_q\nu_qE_qN_q\,dt\).
With reactions/sources during a step, (G53) remains the exact work of the chosen endpoint discrete map.

### 7.3 Axisymmetric characteristic and the previous scalar work

The axisymmetric metric factors are \(a_\perp=ae^{-b}\) and \(a_\parallel=ae^{2b}\), up to fixed reference normalizations. Substitution in (G25) recovers the native characteristic (G35). Differentiation gives

\[
\nu_q=H+s(3\mu_q^2-1).
\tag{G54}
\]

Therefore the small-step limit of (G53) is

\[
\frac{\mathcal W_\gamma}{h}
 \longrightarrow\sum_q\nu_qE_qN_q
 =V(H\rho+2s\Delta P).
\tag{G55}
\]

The expression before the limit is precisely the previous scalar work
\(-\sum_q\Delta E_qN_q^-\) [P3, Section 8]. The covariant form (G2) identifies the angular contraction that this scalar accumulator represents.

If a discrete counter instead uses the continuous endpoint quadrature

\[
\mathcal W_{\gamma,\rm end}
 =h\sum_q\nu_q^*E_q^+N_q^+,
\]

its exact correction is

\[
\boxed{\delta\mathcal W_\gamma
 =-\sum_q(E_q^+-E_q^-)N_q^-
  -h\sum_q\nu_q^*E_q^+N_q^+.}
\tag{G56}
\]

Then \(\mathcal W_{\gamma,\rm end}+\delta\mathcal W_\gamma=\mathcal W_\gamma\).
For smooth geometry and solution branches the correction is \(O(h^2)\). The exact formula holds at every admitted step and remains well-defined in transparent, source-free, and zero-step limits. It retains the geometry/source placement already derived in PRIMARY_THEORY_03.

## 8. Constructive handoff

The geometric interface consists of the following linked quantities:

| Input or output | Meaning and ownership |
|---|---|
| \(a_i^\pm\), or the retained \(a,b\) characteristic | Prescribed endpoint geometry; supplies \(V_\pm\), \(E_q^\pm\), and \(e_q^\pm\) through (G25) |
| \(N_q^-\), \(S_q^*\), \(\ell_a^*\) | Incoming reference counts, one endpoint reference source, and proper candidate absorber densities |
| \(\lambda_{aq}\), \(N_q^+\), \(A_{aq}\) | Existing channel opacity and source-aware endpoint algebra, (G31)/(G50) |
| \(\rho,q,\pi,\Delta P\) | Constructed moments, (G18)/(G20); the retained scalar source consumes \(\rho,\Delta P\) |
| \(f_{\rm abs}\) | Photon absorption momentum moment; zero under the explicitly paired construction |
| \(\mathcal W_\gamma\) | Incoming-count history-energy work, (G53), matched to endpoint-energy event accounting |

Two parity properties are required at the interface: a matched opposite-direction characteristic and a common state/source/opacity for each pair. Count equality alone does not set the opacity or source. Given those properties, both the continuous and discrete preservation proofs apply.

The existing conditional state exposes node energy, \(\mu\), reference number, and reference source, then accumulates scalar even moments [S2–S3]. An evolved gas-momentum variable and an escape angular distribution are separate interface outputs to construct. The parent's explicit four-force/escape closure can use (G33)/(G38) for the paired common-frame case.

The earlier primary-provider coding obligation remains the retained next implementation dependency [CS]. The formulas here supply its geometry and angular interpretation; no native source or integrator was edited in this derivation task.

## 9. Evidence and scope of the result

The analytic arguments establish (G1)–(G56) under Section 2. The exact Wolfram Language evaluator executed the preserved script and returned **16 of 16 identity groups equal to True**, with no tool error. The groups cover:

- The local-rest-frame contraction with general spatial STF stress/shear, antisymmetric vorticity, and explicit acceleration/flux factors.
- Direction normalization, antipodal parity, Bianchi-I directional redshift, and the actual axisymmetric characteristic derivative.
- The six-beam flux/stress and shear contraction.
- Paired backward-Euler number allocation and absorbed momentum cancellation.
- The history-energy product rule, endpoint-work correction, and the generalized product identity.
- The \(H=0\) family and the three exact rational energy/work examples.

Execution evidence is preserved in:

- [Executed Wolfram input](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/geometry_exact.wl).
- [Raw evaluator response](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/GEOMETRY_WOLFRAM_RAW_RESULT.json).
- [Normalized result and verification scope](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/evidence/GEOMETRY_EXACT_RESULT.json).

The algebraic script checks the displayed reductions; the coordinate-free differential proof is Section 3. The parent owns the separate xAct verification and final independent review. This contribution used no ODE integration, atomic-fit evaluation, native executable, historical campaign, or production source mutation.

## 10. Exact retained sources

The current source survey selects receiver commit
\(\texttt{a5c958c414dea41216b445c05f58df837f05cacb}\).
The following local byte hashes match the retained source; the current survey [CS] supplies their repository identities.

| ID | Source and used locations | SHA-256 |
|---|---|---|
| S1 | [axisym_coupling.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs): pressure bounds 208–209; proper geometry/source derivative 232–256 | \(\texttt{6bb3feb6a290894bd8bdd45f9745f28329265cee8ce89589a11960b523e6b008}\) |
| S2 | [axisym_conditional.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs): proper opacity and moments 388–405; scalar source 418–456; actual consumer 458–466; reference work 480–483 | \(\texttt{9aacd51f539ff6274cd43b6e6a97483758135de76ae3445fe362abd6a230a983}\) |
| S3 | [source_bound_interval.py](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py): characteristics 107–110; reference total energy 149–154; node/source stage 156–166 | \(\texttt{050e9a3acf714606573c3dea73cfd3637952481d4ed0a3a85d98efd01872f411}\) |
| P3 | [PRIMARY_THEORY_03 photon derivation](https://github.com/cosmosapjw-quantum/BASS_HE/blob/be96b0011772b47af4bd3c8e420f73153a745508/research/rux03_primary_theory_20261012/derivations/PHOTON_ELIMINATION.md): source normalization Section 3; continuous/discrete geometry Section 8 | \(\texttt{629a0a497b56adcf141cb7e7416277b29ad285743b9d72b448a33cfa8af01c2c}\) |

[CS] [Current source survey](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/source_map/CURRENT_SOURCE.json).  
[IP] [Static selected-input parity inspection](sandbox:/workspace/scratch/a868870ed554/he_covariant_04_work/source_map/STATIC_INPUT_PARITY.json), input SHA-256 \(\texttt{3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be}\).

Source reuse, explicit constructive assumptions, analytic proof, actual symbolic execution, and final adoption are tracked separately.
