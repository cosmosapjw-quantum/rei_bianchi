# Quantitative primitive inverse and physical-cube bounds

Unit: HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06. Claim contribution: C1. Author derivation under physmath-research-loop 1.0.0; the independent adoption decision is recorded separately.

## 1. Result, assumptions and reused authority

The affine coordinates below map a closed seven-dimensional unit cube into the strict physical domain of the accepted moving-gas constitutive inverse. Uniformly for the declared neutral-reference parameter \(10^9\le\mu\le1.5\,10^9\) eV/H, the cube has \(45000<T<55000\) K, positive H/He species and a positive primitive-cone gap. It admits explicit inverse-Jacobian bounds, including

\[
\boxed{L_w=0.26\ {\rm eV/H},\quad L_T=1400\ {\rm K},\quad
L_\beta=3\,10^{-6},\quad L_\gamma=2\,10^{-7},\quad
L_\delta=4\,10^{-6}.}
\tag{B1}
\]

These are derivative/operator bounds per unit input \(\|dX\|_\infty\); the velocity output uses the Euclidean norm. They also bound finite differences between any two points of the cube. The six photon nodes in the scientific contract stay in their fixed atomic-cutoff cells with a minimum cutoff distance greater than \(1.5\) eV. Root's rate and source majorants can therefore consume one fixed smooth physical domain.

We reuse the accepted THEORY05 [global inverse and scalar gap bounds](https://github.com/cosmosapjw-quantum/BASS_HE/blob/94a34d09ad5810a675b556561e5593b279d30448/research/rux03_moving_gas_source_20261013/derivations/PRIMITIVE_RECOVERY_AND_EXAMPLES.md), [seven-variable source equations](https://github.com/cosmosapjw-quantum/BASS_HE/blob/94a34d09ad5810a675b556561e5593b279d30448/research/rux03_moving_gas_source_20261013/derivations/MOVING_SOURCE_AND_THERMAL_BALANCE.md), [coding contract](https://github.com/cosmosapjw-quantum/BASS_HE/blob/94a34d09ad5810a675b556561e5593b279d30448/research/rux03_moving_gas_source_20261013/dossier/CODING_CONTRACT.md) and [next DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/94a34d09ad5810a675b556561e5593b279d30448/research/rux03_moving_gas_source_20261013/dossier/NEXT_DAG.json). Their fixed-composition global cone theorem, known gamma-law attribution, physical reference-mass convention and retained FT03 model are unchanged. The new work is the affine scale, constructive whole-cube inclusion and quantitative composition/velocity derivative chain.

The local setting and exact input family are [SCIENTIFIC_CONTRACT.md](../dossier/SCIENTIFIC_CONTRACT.md): fixed Eulerian tetrad and lab volume, signature \((-+++)\), fixed \(D=10^{-3}\ {\rm cm}^{-3}\), \(f=2/25\), one common gas velocity, and unchanged full retained atomic channels. Python is used only for text and metadata. The actual scientific computation for this contribution is one Wolfram batch described in §9.

## 2. Units, endpoint variables and the affine chart

Let \(\epsilon=\epsilon_{\rm eV}\), \(\Gamma=5/3\), \(\kappa=2/3\). Normalize the parent's conserved lab energy and momentum by the fixed positive \(D\epsilon\):

\[
 e=\frac{E}{D\epsilon},\qquad \mathbf m=\frac{\mathbf M}{D\epsilon},\qquad
 a=\mu+B(\zeta),\qquad \mu=\frac{m_{\rm ref}c^2}{\epsilon}.
\tag{B2}
\]

Thus \(e,m_i,a,w\) have units eV per H. The physical \(\mathbf M\) remains \(c\) times the gas momentum density. The neutral reference includes the bound electrons. The composition is the parent's per-H vector \(\zeta=(x,fa_{\rm HeII},fb_{\rm HeIII})\), not three independently normalized ion fractions. Write

\[
\begin{split}
\mathbf b&=(\chi_0,\chi_1,\chi_1+\chi_2),\quad
B=\mathbf b\cdot\zeta,\\
\boldsymbol\nu&=(1,1,2),\quad e_{\rm el}=\boldsymbol\nu\cdot\zeta,
\quad d=1+f+e_{\rm el},\\
\mathsf C&=a+\Gamma w,\quad
\mathsf W=\sqrt{\mathsf C^2+|\mathbf m|^2},\quad
\mathbf u=\frac{\mathbf m}{\mathsf C},\\
\gamma&=\sqrt{1+|\mathbf u|^2},\quad
\boldsymbol\beta=\frac{\mathbf u}{\gamma},\quad
n_H=\frac D\gamma,\quad T=\frac{2\epsilon w}{3k_Bd}.
\end{split}
\tag{B3}
\]

Here \(\mathbf u\) is the spatial four-velocity in the fixed tetrad; \(c\) still denotes the physical speed of light. \(\mathsf C\) and \(\mathsf W\) equal the parent's \(C\) and \(W\) divided by \(D\epsilon\). The inherited binding values are \(\chi_0=13.598434599702\), \(\chi_1=24.587389011\), \(\chi_2=54.41776\) eV. They remain distinct from the fit cutoffs \(13.60,24.59,54.42\) eV.

Choose the exact anchor

\[
\begin{gathered}
\zeta_*=(1/2,1/50,1/50),\quad T_*=50000\ {\rm K},\quad d_*=41/25,\\
\boldsymbol\beta_*=(0,0,41/841),\quad \gamma_*=841/840,\quad
\mathbf u_*=(0,0,41/840),\\
w_*={3k_Bd_*T_*\over2\epsilon},\quad
a_*=\mu+B_*,\quad \mathbf m_*=(a_*+\Gamma w_*)\mathbf u_*.
\end{gathered}
\tag{B4}
\]

The useful energy coordinate is

\[
\boxed{t=\gamma_*(e-\boldsymbol\beta_*\cdot\mathbf m)-a(\zeta),\qquad
e=\boldsymbol\beta_*\cdot\mathbf m+\frac{a(\zeta)+t}{\gamma_*}.}
\tag{B5}
\]

The map is affine and invertible for a fixed anchor, because \(a(\zeta)\) is affine. Its energy coefficient is \(\gamma_*>0\). No time foliation, physical event or finite source equation is changed. At an endpoint with \(\boldsymbol\beta=\boldsymbol\beta_*\), (B5) gives \(t=w\) exactly. For general endpoint velocity,

\[
\begin{split}
\gamma_{{\rm rel},*}&=\gamma_*\gamma(1-\boldsymbol\beta_*\cdot\boldsymbol\beta),\\
t&=w+(a+\Gamma w)(\gamma_{{\rm rel},*}-1)
       +\kappa w(1-\gamma_*/\gamma).
\end{split}
\tag{B6}
\]

At the anchor this implies \(dt=dw+\kappa w\,d\gamma/\gamma\). The pressure-work term persists in a velocity variation. The new inverse differential below retains it; root's xAct variation check covers the stress-projection form separately.

Define dimensionless coordinates by

\[
\zeta_i=\zeta_{*,i}+10^{-3}X_i,\quad
t=w_*+\tfrac14X_4,\quad
m_j=m_{*,j}+s_mX_{4+j},\quad s_m=a_*10^{-6},
\qquad \|X\|_\infty\le1.
\tag{B7}
\]

For every fixed \(\mu\) this is an affine image of a convex compact cube in the original seven conserved/composition coordinates. \(\mu\) is constant in a source solve; the bounds below hold uniformly over its stated family.

### 2.1 Exact equivalence of the seven finite residuals

Let \(\widehat F_e=F_E/(D\epsilon)\), \(\widehat F_m=F_M/(D\epsilon)\), with the parent's already per-H composition residual \(F_\zeta\). The scaled residual is exactly

\[
\begin{split}
F_{X_i}&=10^3F_{\zeta_i},\qquad i=1,2,3,\\
F_{X_4}&=4\,[\gamma_*(\widehat F_e-\boldsymbol\beta_*\cdot\widehat F_m)
                    -\mathbf b\cdot F_\zeta],\\
F_{X_M}&=\widehat F_m/s_m.
\end{split}
\tag{B8}
\]

Its constant matrix is invertible. The forward Jacobian determinant from \(X\) to \((\zeta,e,\mathbf m)\) is \((10^{-3})^3(1/4)s_m^3/\gamma_*>0\). Thus (B8) is a row transformation of exactly the parent's seven equations. In particular

\[
F_X=X-X_- -h\mathcal S_{X,h}(X),\quad
\mathcal S_t=\gamma_*(\mathcal S_e-\boldsymbol\beta_*\cdot\mathcal S_m)
                  -\mathbf b\cdot\mathcal S_\zeta
\tag{B9}
\]

holds for finite \(h\), with the same endpoint event bundle and eliminated photons. No nonlinear-coordinate backward-Euler correction is needed. The three momentum rows remain present.

### 2.2 Representing the small energy gap

The coordinate \(e-a\) contains a bulk term of order \(a(\gamma_*-1)\) at this anchor. Independently varying \(m\) in that coordinate leaves a first-order thermal sensitivity proportional to \(\beta_*\,dm\). Equation (B5) removes the leading cold kinetic tangent term with a constant transformation. The remaining thermal sensitivity is quantified in §5.

Store \(t_*\) from the exact thermal input and store the small affine increments. Reconstruct total energy, if needed, with a declared precision or compensated representation. The cancellation-free cone formula below permits primitive recovery without first rounding \(e\) and its large cold baseline to nearby machine numbers. It preserves information represented by the input; a later precision choice must still resolve the requested thermal and residual margins.

## 3. Exact cold-norm remainder and a finite physical inclusion proof

For fixed \(a>0\), put

\[
H(a,\mathbf m)=\sqrt{a^2+|\mathbf m|^2},\qquad
\mathbf m_0=a\mathbf u_*,\qquad \mathbf v=\mathbf m-\mathbf m_0.
\tag{B10}
\]

At \(\mathbf m_0\), \(H=a\gamma_*\) and \(\nabla_m H=\boldsymbol\beta_*\). Define the tangent-plane remainder

\[
R=H-\frac a{\gamma_*}-\boldsymbol\beta_*\cdot\mathbf m.
\tag{B11}
\]

**Lemma 1.** For every finite \(\mathbf m\) and fixed \(a>0\),

\[
\boxed{0\le R\le\frac{|\mathbf v|^2}{2a},\qquad
R=\frac{|\mathbf v|^2-(\boldsymbol\beta_*\cdot\mathbf v)^2}
 {H+a\gamma_*+\boldsymbol\beta_*\cdot\mathbf v}.}
\tag{B12}
\]

**Proof.** The Hessian is
\(D_m^2H=I/H-\mathbf m\mathbf m^T/H^3\). Its transverse eigenvalues are \(1/H\); its radial eigenvalue is \(a^2/H^3\). They are positive and at most \(1/a\). The supporting-plane inequality and the integral second-order Taylor remainder prove the two bounds. For the rational formula, set \(s=\boldsymbol\beta_*\cdot\mathbf v\). Then \(H^2=(a\gamma_*+s)^2+|\mathbf v|^2-s^2\). The numerator is nonnegative and positive for \(\mathbf v\ne0\), because \(|\boldsymbol\beta_*|<1\). Hence the denominator is positive, including \(\mathbf v=0\), and rationalization proves the identity. This proof is uniform over all directions.

Equations (B5) and (B11) give the exact conservative cone gap

\[
\boxed{\Delta=e-H=\frac t{\gamma_*}-R.}
\tag{B13}
\]

The numerator in (B12) is a small quadratic form; the denominator contains the large baseline only as positive additions on this cube. This directly supplies a thermal-scale \(\Delta\) to the parent's positive-term scalar recovery formula.

### 3.1 Uniform bounds before using the inverse derivative

The exact constants are

\[
B_*=8.871068060291,\quad
B_{\rm rad}=10^{-3}\sum_i b_i=0.117190972621702<\frac{59}{500},\quad
w_*={2830330450\over267029439}=10.599319912438568\ldots .
\tag{B14}
\]

For every \(X\) in (B7),

\[
\begin{gathered}
\zeta_1\in[0.499,0.501],\quad \zeta_2,\zeta_3\in[0.019,0.021],\\
1-\zeta_1>0,\quad f-\zeta_2-\zeta_3\in[0.038,0.042],\quad
d\in[409/250,411/250],\\
a\ge10^9,\qquad
|\mathbf m-\mathbf m_*|\le\sqrt3s_m<2700.
\end{gathered}
\tag{B15}
\]

The last inequality follows from \(\sqrt3<7/4\), \(a_*\le1.5\,10^9+B_*\) and \(B_*<9\). All energies in this proof are eV/H. Because \(\mathbf m_*=(a_*+\Gamma w_*)\mathbf u_*\),

\[
\begin{split}
|\mathbf v|&\le|\mathbf m-\mathbf m_*|
+|\mathbf u_*|\,[\Gamma w_*+|a_*-a|]\\
&<2700+{41\over840}\left({55\over3}+{59\over500}\right)<2701.
\end{split}
\tag{B16}
\]

Consequently \(R<2701^2/(2\,10^9)=0.0036477005<1/250\). Also

\[
\frac{|\mathbf m|}{a}\le |\mathbf u_*|+\frac{|\mathbf v|}{a}
<{41\over840}+\frac{2700+(41/840)(55/3+59/500)}{10^9}
<\frac{49}{1000}.
\tag{B17}
\]

The cold Lorentz factor therefore obeys
\(\gamma_{\rm cold}=H/a<\sqrt{1+(49/1000)^2}<501/500\).
Equation (B13) now gives

\[
\frac{w_*-1/4}{\gamma_*}-\frac1{250}<\Delta
\le\frac{w_*+1/4}{\gamma_*}.
\tag{B18}
\]

The lower bound is greater than 10. Thus the parent's global positive-cone theorem supplies a unique positive primitive at every cube point. Its monotone scalar bracket gives \(\Delta\le w\le\gamma_{\rm cold}\Delta\). We obtain

\[
10.333013943458260\ldots<w<10.858092251963488\ldots,
\qquad 10<w<11.
\tag{B19}
\]

The printed decimals display exact rational bounds in the machine record. The proof uses their rational expressions in (B18) and \(\gamma_{\rm cold}<501/500\).

Combining (B15) and (B19) with the temperature law yields

\[
45000<\frac{2\epsilon\,10}{3k_B(411/250)}<T
<\frac{2\epsilon\,11}{3k_B(409/250)}<55000.
\tag{B20}
\]

This proves whole-cube physical inclusion before any inverse-derivative estimate is used. It supplies the closed inner rate enclosure \([45000,55000]\) K while remaining strictly inside the parent's \([30000,110000]\) K provider domain. Since \(\mathsf C>a\), equations (B17)–(B19) also yield

\[
|\mathbf u|<49/1000,\quad |\boldsymbol\beta|<49/1000,\quad
1\le\gamma<501/500,\quad D/(501/500)<n_H\le D.
\tag{B21}
\]

## 4. Exact inverse differential for arbitrary velocity and composition

In the normalized units, the reused scalar energy map is

\[
e=\mathscr E(\mathsf C;a,|\mathbf m|^2)
 ={3\mathsf C^2+2a\mathsf C+5|\mathbf m|^2\over5\mathsf W}.
\tag{B22}
\]

Define the positive thermal enthalpy fraction and three differential coefficients

\[
q={\mathsf C-a\over\mathsf C}={\Gamma w\over\mathsf C},\qquad
\ell={1-\kappa q|\beta|^2\over\gamma},\quad
s={1-(2/5)q|\beta|^2\over\gamma},\quad
k=1+{2q\over5\gamma^2}.
\tag{B23}
\]

Direct differentiation gives \(\Gamma\mathscr E_C=\ell\), \(\mathscr E_C+\mathscr E_a=s\), and \(\nabla_m\mathscr E=k\boldsymbol\beta\). Thus the inverse differential and its affine form are exactly

\[
\boxed{\ell\,dw=de-s\,da-k\boldsymbol\beta\cdot d\mathbf m
 ={dt\over\gamma_*}+
    (1/\gamma_*-s)\,da+
    (\boldsymbol\beta_*-k\boldsymbol\beta)\cdot d\mathbf m.}
\tag{B24}
\]

At every endpoint \(da=\mathbf b\cdot d\zeta\), \(dd=\boldsymbol\nu\cdot d\zeta\). For example, in the original normalized conserved variables,
\(w_e=1/\ell\), \(w_{m_i}=-k\beta_i/\ell\), and \(w_{\zeta_i}=-s b_i/\ell\) at fixed \(e,\mathbf m\). The transformed coefficients are those on the right side of (B24). Composition is evaluated at the candidate state, so its binding and particle-count derivatives both enter.

The remaining chain is constructive:

\[
\begin{split}
d\mathsf C&=da+\Gamma\,dw,\qquad
d\mathbf u={d\mathbf m-\mathbf u\,d\mathsf C\over\mathsf C},\\
d\gamma&=\boldsymbol\beta\cdot d\mathbf u,\qquad
d\boldsymbol\beta={I-\boldsymbol\beta\boldsymbol\beta^T\over\gamma}
                      d\mathbf u,\\
dn_H&=-{D\over\gamma^2}\boldsymbol\beta\cdot d\mathbf u,\\
dT&={2\epsilon\over3k_B}\left({dw\over d}-{w\,dd\over d^2}\right),\\
d\delta_q&=(\boldsymbol\beta-\mathbf e_q)\cdot d\mathbf u,\qquad
dE'_q=E_q\,d\delta_q.
\end{split}
\tag{B25}
\]

The last line uses a fixed lab energy and physical unit direction, \(\delta_q=\gamma-\mathbf u\cdot\mathbf e_q\). All formulas are smooth at zero momentum as well as at the nonzero anchor; none divides by \(|\mathbf m|\).

The parent's scalar derivative lower bound gives

\[
\ell\ge\frac1{\gamma_{\rm cold}}>\frac{500}{501},\qquad
\ell^{-1}<\frac{501}{500}.
\tag{B26}
\]

This is an explicit inverse coefficient bound on the whole cube.

## 5. Quantitative operator bounds

For a scalar \(g\), let \(L_g\) mean \(|dg|\le L_g\|dX\|_\infty\). For a vector, use its Euclidean output norm. Equations (B7) and (B15) imply

\[
L_a<59/500,\quad L_d=1/250,\quad L_t=1/4,\quad L_m<2700.
\tag{B27}
\]

First control the small coefficient differences in (B24). Since \(w,w_*\in(10,11)\),

\[
\begin{split}
|\mathbf u-\mathbf u_*|
&\le { |\mathbf m-\mathbf m_*|
 +|\mathbf u_*|\{|a-a_*|+\Gamma|w-w_*|\}\over\mathsf C}\\
&<\frac{2700+(41/840)(59/500+5/3)}{10^9}<3\,10^{-6},\\
0<q&<\frac{(5/3)11}{10^9}<2\,10^{-8}.
\end{split}
\tag{B28}
\]

The maps \(\mathbf u\mapsto\boldsymbol\beta\) and \(\mathbf u\mapsto1/\gamma\) have operator norms at most 1 and \(49/1000\), respectively, on the segment between this endpoint and its anchor. The segment stays within the Euclidean \(|u|<49/1000\) ball. Hence

\[
\begin{split}
|1/\gamma_*-s|
&\le (49/1000)(3\,10^{-6})+(2/5)(2\,10^{-8})(49/1000)^2
 <1.5\,10^{-7},\\
|\boldsymbol\beta_*-k\boldsymbol\beta|
&\le3\,10^{-6}+(2/5)(2\,10^{-8})(49/1000)
 <3.001\,10^{-6}.
\end{split}
\tag{B29}
\]

These cancellations follow from the affine anchor energy and the actual inverse, with all velocity and composition terms retained. They turn the rest-scaled momentum radius into a manageable thermal derivative.

Equations (B24), (B26), (B27) and (B29) give

\[
\begin{split}
L_w&<\frac{501}{500}\left[
\frac{1}{4\gamma_*}+(1.5\,10^{-7})\frac{59}{500}
 +(3.001\,10^{-6})2700\right]\\
&={1086240071784357\over4205000000000000}
=0.258321063444555\ldots<0.26,\\
L_C&<59/500+(5/3)(0.26)<0.56.
\end{split}
\tag{B30}
\]

Using \(|u|<1/20\), \(\mathsf C\ge10^9\) in (B25),

\[
\begin{split}
L_u&<\frac{2700+(1/20)(0.56)}{10^9}
=2.700028\,10^{-6}<2.71\,10^{-6},\\
L_\beta&\le L_u<3\,10^{-6},\\
L_\gamma&<(49/1000)(2.71\,10^{-6})<1.33\,10^{-7}<2\,10^{-7},\\
L_{n_H}&<1.33\,10^{-10}\ {\rm cm}^{-3},\\
L_\delta&<(1+49/1000)(2.71\,10^{-6})<3\,10^{-6}<4\,10^{-6}.
\end{split}
\tag{B31}
\]

The more conservative values in (B1) are the fixed root-facing bounds. The sharper intermediate inequalities remain recorded. The thermal law gives

\[
\begin{split}
L_T&<{2\epsilon\over3k_B}\left[
\frac{0.26}{409/250}+
\frac{11(1/250)}{(409/250)^2}\right]\\
&={313332343722600\over230956345369}
=1356.673458016438\ldots<1400\ {\rm K}.
\end{split}
\tag{B32}
\]

Since the cube is convex, integrating these derivatives on a line segment proves the finite Lipschitz estimates. In particular every point has \(|T-T_*|<1400\) K, \(|\beta-\beta_*|<3\,10^{-6}\), \(|\gamma-\gamma_*|<2\,10^{-7}\) and \(|n_H-D/\gamma_*|<1.33\,10^{-10}\ {\rm cm}^{-3}\). The strengthened temperature guard is \(48600<T<51400\) K, leaving a positive margin inside the inner rate box.

### 5.1 A seven-by-seven normalized inverse-Jacobian norm

To state one dimensionless operator bound, define the output primitive chart

\[
\widehat\Phi(X)=\left(
10^3(\zeta-\zeta_*),\ 4(w-w_*),\quad
\frac{\boldsymbol\beta-\boldsymbol\beta_*}{3\,10^{-6}}\right).
\tag{B33}
\]

Equations (B30)–(B31) imply

\[
\boxed{\|D_X\widehat\Phi\|_{\infty\to\infty}\le\frac{26}{25}.}
\tag{B34}
\]

This is a coordinate-specific norm of the constitutive inverse Jacobian, with all scales displayed. It is also a Lipschitz constant for that normalized primitive map. Parent's global inverse supplies its one-to-one constitutive meaning; (B34) supplies the quantitative norm for this cube.

### 5.2 Density and composition bounds for the atomic chain

Let \(y=(1-\zeta_1,\zeta_1,f-\zeta_2-\zeta_3,\zeta_2,\zeta_3)\), so \(n_j=n_Hy_j\). The exact row radii for \(y\) are \((10^{-3},10^{-3},2\,10^{-3},10^{-3},10^{-3})\). Their proper-density derivative bounds are

\[
L_{n_j}\le D L_{y_j}+y_{j,\max}L_{n_H},\qquad
L_{n_{\rm He}}=fL_{n_H},\qquad
L_{n_e}\le D/250+(141/250)L_{n_H}.
\tag{B35}
\]

Here \(e_{\rm el}\in[139/250,141/250]\), \(n_e=n_He_{\rm el}\). These product-rule bounds include both the endpoint proper-density change and the electron closure. They are the direct inputs to the full CI/RR/DR rate chain.

## 6. Directional photon and cutoff guards

For any fixed unit direction and lab photon energy \(E_q\ge0\), (B25)–(B31) yield

\[
|E'_q(X)-E'_{q,*}|\le4\,10^{-6}E_q\|X\|_\infty,
\qquad E'_{q,*}=E_q(\gamma_*-\mathbf u_*\cdot\mathbf e_q).
\tag{B36}
\]

Thus a specified node stays in a given provider cell if its anchor energy has more than \(4\,10^{-6}E_q\) distance from each relevant cutoff and domain endpoint. Arbitrary velocity variations inside the cube are covered; no axial restriction is used in this derivative argument. The directions here are actual rays, not a transverse approximation to an azimuthal ring.

For the scientific contract's six rays, the following are exact rational enclosures, displayed as decimals only for readability. \(\pm\mathbf e_x\) and \(\pm\mathbf e_y\) share anchor values but remain separate nodes.

| Lab node | Gas-frame energy enclosure, eV | Active HI / HeI / HeII edges |
|---|---|---|
| \(23,\pm\mathbf e_x\) | [23.02728895238095…, 23.02747295238095…] | yes / no / no |
| \(35,\pm\mathbf e_y\) | [35.04152666666666…, 35.04180666666666…] | yes / yes / no |
| \(70,+\mathbf e_z\) | [66.66638666666666…, 66.66694666666666…] | yes / yes / yes |
| \(70,-\mathbf e_z\) | [73.49972, 73.50028] | yes / yes / yes |

The minimum distance to the three fit cutoffs is exactly
\(8203267/5250000=1.562527047619\ldots>3/2\) eV. All six intervals lie within \((0,74)\) eV, hence within the parent's \((0,50000)\) eV domain. The original binding coefficients in (B3) are used for chemical energy; the separate fit cutoffs determine the fixed active cells. The nonnegative photon inventories and source ownership are inputs to root's source proof and do not enter the constitutive inverse bound.

## 7. Reusable construction for another anchor or radius

The proof gives a direct sufficient construction, rather than a sampled test. For an arbitrary physical anchor, choose component radii \(r_{\zeta_i},r_t,r_{m_i}\), let
\(B_r=\sum_i|b_i|r_{\zeta_i}\), \(d_r=\sum_i\nu_i r_{\zeta_i}\), \(a_{\min}=a_*-B_r>0\), and \(R_m=(\sum_i r_{m_i}^2)^{1/2}\). Then the following explicit envelopes replace (B16)–(B19):

\[
\begin{split}
V_r&=R_m+|u_*|(\Gamma w_*+B_r),\quad
R_{\max}=V_r^2/(2a_{\min}),\\
U_0&=|u_*|+V_r/a_{\min},\quad G_0=\sqrt{1+U_0^2},\\
\Delta_{\min}&=(w_*-r_t)/\gamma_*-R_{\max},\quad
\Delta_{\max}=(w_*+r_t)/\gamma_*.
\end{split}
\tag{B37}
\]

Together with the strict simplex tests, \(\Delta_{\min}>0\) and

\[
\frac{2\epsilon\Delta_{\min}}{3k_B(d_*+d_r)}>T_{\min},\qquad
\frac{2\epsilon G_0\Delta_{\max}}{3k_B(d_*-d_r)}<T_{\max}
\tag{B38}
\]

are a finite whole-box inclusion certificate. Once this is established, (B23)–(B25) give bounds for the new chart by the same explicit arithmetic. Derivatives and source rates must be evaluated on that candidate-dependent domain.

For anchors extremely close to a warm boundary, a sharper sufficient test uses the parent's exact warm-face map

\[
t_T(\zeta,\mathbf m)=\gamma_*\left[
\mathscr E\!\left(a+\Gamma\frac{3k_BdT}{2\epsilon};a,|m|^2\right)
-\boldsymbol\beta_*\cdot\mathbf m\right]-a.
\tag{B39}
\]

It is strictly increasing in \(T\), with \(\partial_Tt_T=\gamma_*\ell(3k_Bd/2\epsilon)>0\). Bounding the lower and upper faces so that \(\sup t_{T_{\min}}<t_*-r_t\) and \(t_*+r_t<\inf t_{T_{\max}}\) proves exact warm inclusion. The face differential is
\(dt_T=\gamma_*[(s-1/\gamma_*)da+\ell\,dw_T+(k\beta-\beta_*)\cdot dm]\), with \(dw_T=(3k_BT/2\epsilon)dd\). It uses known forward states at the specified face temperature and therefore supplies explicit enclosures without presupposing an inverse-domain proof. This sharper test is available when the coarse sufficient bounds (B38) have unnecessary slack. Root's continuation theorem specifies how an accepted new box overlaps the retained branch.

## 8. Source and coding interface

The receiving source proof consumes the unit \(X\)-cube, the exact affine residual transformation (B8), the proper normalization (B2), and the root-facing constants (B1). Full source differentiation follows composition → primitive → Doppler/atomic provider → eliminated photon → owned event rows. Equations (B24)–(B25) expose every primitive part of this chain.

For an implementation, the inputs are the immutable physical constants and source identity, fixed \(D,f,\mu\), anchor, cube scales, selected photon energies/directions and precision budget. The primitive routine returns \(w,T,\beta,\gamma,n_H\), positive cone/warm/simplex/Doppler guard margins, and either its explicit Jacobian or the product (B24)–(B25). It can compute \(\Delta\) using (B12)–(B13), then reuse the parent's safeguarded positive scalar inverse. The conservative residual and its transformed residual must refer to the same candidate and events.

All root-facing numbers here are mathematical bounds for this declared certificate input family. Production coding remains in the retained PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04 and MOVING_GAS_STAGE_05 nodes. Their exact source/input/native acceptance evidence is a separate obligation; this contribution has no native, chemical RHS or ODE execution.

## 9. Actual exact computation and evidence status

The author executed [PRIMITIVE_DIFFERENTIAL_CHECK.wl](PRIMITIVE_DIFFERENTIAL_CHECK.wl) once through the Wolfram Language evaluator. Wolfram 15.0.1, Linux-x86-64, returned **17/17 PASS**, with kernel elapsed time **0.068243 s**. The batch contains **7 new algebra/differential identity groups and 10 exact envelope-arithmetic groups**. The latter check the rational inequalities used in the whole-domain proof above; they are not a scan or a pointwise inverse solver. No parent suite was rerun. The separate Wolfram context lookup provided no mathematical premise used here.

Preserved evidence:

- [Actual call input](../evidence/PRIMITIVE_DIFFERENTIAL_CALL_INPUT.json) and [executed code](../evidence/PRIMITIVE_DIFFERENTIAL_EXECUTED.wl).
- [Unmodified raw tool response](../evidence/PRIMITIVE_DIFFERENTIAL_RAW_RESULT.json).
- [Normalized kernel result](../evidence/PRIMITIVE_DIFFERENTIAL_RESULT.json), retaining every check name, exact fractions, display values and six-node intervals.
- [Machine handoff](PRIMITIVE_DIFFERENTIAL_BOUNDS.json), binding the reusable constants, assumptions and source identities.

The argument's basis is **derived**, supported by the actual scoped exact checks. This is the author contribution to C1; the project decision uses the designated independent review. No new no-go claim is proposed. The new guards and derivatives are the precise changed dependency; the accepted parent's inverse existence proof and physical ownership remain reused.
