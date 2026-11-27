# FT03 / Verner coefficient and first-derivative envelopes

**Unit:** HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06  
**Status:** author derivation and actual exact checks complete; independent adoption belongs to the unit's final review.  
**Source:** receiver PR114, commit [a5c958c414dea41216b445c05f58df837f05cacb](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/a5c958c414dea41216b445c05f58df837f05cacb).  
**Parent:** accepted THEORY05, BASS_HE [94a34d09ad5810a675b556561e5593b279d30448](https://github.com/cosmosapjw-quantum/BASS_HE/commit/94a34d09ad5810a675b556561e5593b279d30448).

## 1. Result and domain

On the physical enclosure below, every retained FT03 CI/RR/two-DR coefficient, captured kinetic coefficient, escape-energy coefficient and active Verner cross section has an explicit nonnegative upper bound and an explicit upper bound on its first derivative. The tables in §§4–6 are rational constants. The derivation bounds the whole enclosure; no temperature, velocity or photon sampling is used.

The source-defined mathematical functions are the real analytic fits obtained from the pinned decimal literals. These are the coefficients needed by the mathematical continuation problem. Source-level floating-point implementation and a native moving-stage solver remain in the coding lane.

Use

\[
T_-=45000\ {\rm K},\quad T_+=55000\ {\rm K},\quad
D=10^{-3}\ {\rm cm}^{-3},\quad f=2/25,
\]
\[
\zeta=(x,z_1,z_2)=(x,fa,fb),\qquad
|\zeta-\zeta_*|_\infty\le10^{-3},\quad
\zeta_*=(1/2,1/50,1/50).
\tag{R1}
\]

The synchronized primitive enclosure supplies

\[
\beta_*=(41/841)e_z,\quad\gamma_*=841/840,\quad
|\beta-\beta_*|_2\le10^{-4},\quad |\beta|_2\le B_v=49/1000.
\tag{R2}
\]

Its proof that the selected affine conservative cube lies inside R1–R2 is the separate primitive-author dependency. Here the rate bounds are proved under R1–R2. The neutral-reference rest energy parameter does not enter the atomic coefficient functions directly; it enters that primitive map.

There are six lab photon nodes:
\((23\,{\rm eV},\pm e_x)\), \((35\,{\rm eV},\pm e_y)\),
\((70\,{\rm eV},\pm e_z)\), each with \(N_q^-/D=1/100\), and \(S_q=0\).
The same coefficient bounds apply to each node in a pair. They retain the full warm FT03 CI/RR/two-DR/primary-absorption model.

Exact source functions, literals and line locations are in
[SOURCE_FUNCTIONS.md](../source_map/SOURCE_FUNCTIONS.md);
current heads and local/source hashes are in
[CURRENT_SOURCE.json](../source_map/CURRENT_SOURCE.json).

## 2. Which functions enter the source

The public selected source-bound provider is FT03. Its coefficient function is
`ft03_rates::ft03_coefficients`; the actual event products and kinetic/escape ownership are in
`ft03_controlled::ft03_rhs`. `AtomicProvider::cross_section` supplies Verner absorption.
The separate `AtomicProvider::raw_coefficient` Grackle bodies are reference functions and do not replace these FT03 coefficients.

Index \(i=0,1,2\) denotes the HI/HII, HeI/HeII and HeII/HeIII edges. Define lower and upper target fractions per H nucleus and the electron fraction by

\[
y=(1-x,\ f-z_1-z_2,\ z_1),\qquad
z=(x,z_1,z_2),\qquad e=x+z_1+2z_2.
\tag{R3}
\]

The proper densities are \(n_H=D/\gamma\), \(n_e=(D/\gamma)e\).
Write \(C_i\) for the source's `beta_ci_cm3_s`,
\(\alpha_i\) for `alpha_rr_cm3_s`,
\(d_j\) for the two `alpha_dr_cm3_s`,
\(\kappa_i\) for `rr_kinetic_erg_cm3_s`,
and \(E_{d,j}\) for `dr_energy_erg`.
Then the source's positive event products are

\[
R'_{\mathrm{CI},i}=D^2(1-|\beta|^2)e\,y_i C_i(T),\quad
R'_{\mathrm{RR},i}=D^2(1-|\beta|^2)e\,z_i\alpha_i(T),
\]
\[
R'_{\mathrm{DR},j}=D^2(1-|\beta|^2)e\,z_1d_j(T).
\tag{R4}
\]

Both DR terms are HeII \(\to\) HeI and therefore multiply \(z_1\).
Captured kinetic powers are the same target/electron product times
\(\kappa_i\) for RR and \(E_{d,j}d_j\) for DR.

The immutable source constants include

\[
k_B=1.380649\,10^{-16}\ {\rm erg\,K^{-1}},\quad
\epsilon=1.602176634\,10^{-12}\ {\rm erg/eV},\quad
c=29979245800\ {\rm cm/s},
\]
\[
\chi=(13.598434599702,\ 24.587389011,\ 54.41776)\ {\rm eV}.
\tag{R5}
\]

The escape coefficients are

\[
\Psi_{\mathrm{RR},i}=\epsilon\chi_i\alpha_i+\kappa_i,\qquad
\Psi_{\mathrm{DR},j}=(\epsilon\chi_1+E_{d,j})d_j.
\tag{R6}
\]

Consequently the retained proper escape power is exactly

\[
Q'_{\rm esc}=D^2(1-|\beta|^2)e
 \left[\sum_{i=0}^2 z_i\Psi_{\mathrm{RR},i}
       +z_1\sum_{j=1}^2\Psi_{\mathrm{DR},j}\right].
\tag{R7}
\]

The finite moving stage uses \(h\gamma Q'_{\rm esc}\) for lab escape energy
and \(h\gamma Q'_{\rm esc}\beta\) for scaled lab escape momentum, following
THEORY05's owned isotropic gas-frame escape moment. R7 specifies an energy moment; it does not require a new emitted photon spectrum.

## 3. Exact FT03 formulas and endpoint reduction

Set \(\ell_i=L_i/T\), with

\[
L=(315614,\ 570670,\ 1263030)\ {\rm K}.
\]

For \(i=0,2\),

\[
u_i=(\ell_i/0.522)^{0.470},\qquad
\alpha_i=A_i\,{\ell_i^{1.503}\over(1+u_i)^{1.923}},
\quad A_0=1.269\,10^{-13},\quad A_2=2A_0.
\tag{R8}
\]

For \(i=1\),

\[
\alpha_1=3\,10^{-14}\ell_1^{0.654}.
\tag{R9}
\]

The source's dimensionless logarithmic slopes and their logarithmic derivatives are

\[
g_i={d\log\alpha_i\over d\log T}
=-1.503+1.923(0.470){u_i\over1+u_i},
\]
\[
\dot g_i:={dg_i\over d\log T}
=-1.923(0.470)^2{u_i\over(1+u_i)^2},\qquad (i=0,2),
\tag{R10}
\]
with \(g_1=-0.654,\ \dot g_1=0\).
Thus `log_slope_derivative` is \(T\,dg/dT\), not \(dg/dT\).
Every \(\alpha_i\) decreases, so
\(\alpha_i(T)\le\alpha_i(T_-)\).

The collisional coefficient is

\[
C_i=A^{\rm CI}_i T^{-3/2}e^{-\ell_i/2}
 {\ell_i^{p_i}\over(1+v_i)^{d_i}},
\qquad v_i=(\ell_i/c_i)^{r_i},
\tag{R11}
\]

with the source literals

| Edge | \(A^{\rm CI}\) | \(p\) | \(c\) | \(r\) | \(d\) |
|---|---:|---:|---:|---:|---:|
| HI/HII | 21.11 | −1.089 | 0.354 | 0.874 | 1.101 |
| HeI/HeII | 32.38 | −1.146 | 0.416 | 0.987 | 1.056 |
| HeII/HeIII | 19.95 | −1.089 | 0.553 | 0.735 | 1.275 |

Direct logarithmic differentiation gives

\[
s_i^{\rm CI}:={d\log C_i\over d\log T}
=-\frac32-p_i+\frac{L_i}{2T}
+d_i r_i{v_i\over1+v_i}.
\tag{R12}
\]

On R1 its explicit lower bound
\(-3/2-p_i+L_i/(2T_+)\) is positive. Therefore
\(C_i(T)\le C_i(T_+)\), and

\[
|C_i'(T)|\le{\overline C_i\over T_-}
\left[-\frac32-p_i+\frac{L_i}{2T_-}+d_i r_i\right].
\tag{R13}
\]

For the DR terms, retain the source's exact decimal products

\[
b_1=40.49664394833662(11605)\ {\rm K},\qquad
b_2=8.099328789667(11605)\ {\rm K},
\]
\[
a_d=1.54\,10^{-9}(11605)^{3/2},\quad
d_1=a_dT^{-3/2}e^{-b_1/T},\quad
d_2=0.3a_dT^{-3/2}e^{-(b_1+b_2)/T},
\]
\[
E_{d,1}=k_Bb_1,\qquad E_{d,2}=k_B(b_1+b_2).
\tag{R14}
\]

For \(b=b_1\) or \(b_1+b_2\),
\(d\log d_j/d\log T=-3/2+b/T>0\) on R1.
Hence \(d_j(T)\le d_j(T_+)\), and

\[
|d_j'(T)|\le{\overline d_j\over T_-}
\left(-\frac32+\frac{b}{T_-}\right).
\tag{R15}
\]

These endpoint reductions retain all the original smooth thermal functions.
The provider's outer guard is \(30000\le T\le110000\) K; R1 is a strict interior interval.

## 4. Rational coefficient and thermal-derivative bounds

All entries below are upper bounds on the whole interval R1. Coefficients have units
\({\rm cm^3\,s^{-1}}\), and derivative bounds have units
\({\rm cm^3\,s^{-1}\,K^{-1}}\).

| Process | \(\bar k\) | \(\overline{|dk/dT|}\) |
|---|---:|---:|
| RR HII → HI | \(2\,10^{-13}\) | \(7\,10^{-18}\) |
| RR HeII → HeI | \(2\,10^{-13}\) | \(3\,10^{-18}\) |
| RR HeIII → HeII | \(10^{-12}\) | \(4\,10^{-17}\) |
| CI HI → HII | \(10^{-9}\) | \(10^{-13}\) |
| CI HeI → HeII | \(4\,10^{-11}\) | \(7\,10^{-15}\) |
| CI HeII → HeIII | \(2\,10^{-14}\) | \(7\,10^{-18}\) |
| DR resonance 1 | \(4\,10^{-14}\) | \(8\,10^{-18}\) |
| DR resonance 2 | \(2\,10^{-15}\) | \(5\,10^{-19}\) |

The RR derivative bounds use

\[
|\alpha_i'|\le {\bar\alpha_i\over T_-}
\begin{cases}1.503,&i=0,2,\\0.654,&i=1.\end{cases}
\tag{R16}
\]

For reference, the actual certified endpoint upper enclosures display as

| Endpoint quantity | Edge/resonance 1 | Edge/resonance 2 | Edge 3 |
|---|---:|---:|---:|
| RR at 45000 K | \(1.378238\,10^{-13}\) | \(1.579779\,10^{-13}\) | \(7.900751\,10^{-13}\) |
| CI at 55000 K | \(8.654016\,10^{-10}\) | \(3.217573\,10^{-11}\) | \(1.476884\,10^{-14}\) |
| DR at 55000 K | \(2.903946\,10^{-14}\) | \(1.577316\,10^{-15}\) | — |

This short display is rounded upward for readability. The authority for the rational caps is the exact enclosing arithmetic and exact cap comparisons in
[RATE_ENVELOPE_RESULT.json](../evidence/RATE_ENVELOPE_RESULT.json), not the printed decimal digits.

### Captured kinetic coefficients

The actual source uses

\[
\kappa_i=k_BT\alpha_i(3/2+g_i),\qquad
\kappa_i'=k_B\alpha_i[(1+g_i)(3/2+g_i)+\dot g_i].
\tag{R17}
\]

For hydrogenic edges, \(u_i(T_+)>3\) gives
\(3/2+g_i>0.6748575\), while the exact global upper bound is \(0.90081<1\).
The HeI-edge factor is \(0.846\).
Also
\[
|1+g_i|\le0.503,\quad
|\dot g_i|\le0.106197675,\qquad i=0,2.
\]
Thus \(|(1+g_i)(3/2+g_i)+\dot g_i|\le0.559305105\).
For \(i=1\) the factor is \(0.346(0.846)=0.292716\).
Multiplication by the rational RR caps proves the derivative bounds below.
For DR, the kinetic coefficient is \(E_{d,j}d_j\) and \(E_{d,j}\) is constant.

| Captured kinetic coefficient | Upper bound, erg cm³/s | Absolute \(T\)-derivative upper, erg cm³/(s K) |
|---|---:|---:|
| RR HII | \(2\,10^{-24}\) | \(2\,10^{-29}\) |
| RR HeII | \(2\,10^{-24}\) | \(10^{-29}\) |
| RR HeIII | \(10^{-23}\) | \(10^{-28}\) |
| DR 1 | \(3\,10^{-24}\) | \(6\,10^{-28}\) |
| DR 2 | \(2\,10^{-25}\) | \(4\,10^{-29}\) |

### Escape coefficients

Use R6 and the source binding constants R5. Positivity and the triangle inequality give
\[
\bar\Psi_{\rm RR}\ge\epsilon\chi\,\bar\alpha+\bar\kappa,\quad
\overline{|\Psi'_{\rm RR}|}\ge
\epsilon\chi\,\overline{|\alpha'|}+\overline{|\kappa'|},
\]
with the analogous constant-energy multiplication for DR.
The following rational table was checked using those exact inequalities.

| Escape coefficient | Upper bound, erg cm³/s | Absolute \(T\)-derivative upper, erg cm³/(s K) |
|---|---:|---:|
| RR HII | \(7\,10^{-24}\) | \(2\,10^{-28}\) |
| RR HeII | \(10^{-23}\) | \(1.5\,10^{-28}\) |
| RR HeIII | \(10^{-22}\) | \(4\,10^{-27}\) |
| DR 1 | \(5\,10^{-24}\) | \(10^{-27}\) |
| DR 2 | \(3\,10^{-25}\) | \(6\,10^{-29}\) |

## 5. Post-Doppler support and exact Verner function

For a lab unit direction \(e_q\), set
\[
a_q=1-\beta\cdot e_q,\quad
\delta_q=\gamma a_q,\quad E'_q=\delta_qE_q.
\]
R2 implies
\[
\sqrt{\frac{1-B_v}{1+B_v}}\le\delta_q\le
\sqrt{\frac{1+B_v}{1-B_v}}.
\]
The convenient rational enclosure
\[
\boxed{\frac{19}{20}\le\delta_q\le\frac{20}{19}}
\tag{R18}
\]
follows by squaring positive endpoints. Therefore:

| Lab energy | Enclosed \(E'\), eV | Active absorbers |
|---|---|---|
| 23 eV | \([437/20,\ 460/19]\) | HI |
| 35 eV | \([133/4,\ 700/19]\) | HI, HeI |
| 70 eV | \([133/2,\ 1400/19]\) | HI, HeI, HeII |

The exact source fit cutoffs are \(13.60,\ 24.59,\ 54.42\) eV.
Every enclosed interval lies strictly on one side of every relevant cutoff,
and its maximum is below the outer 50000 eV guard.
Inactive cross sections and their derivatives are identically zero on an open neighborhood of the enclosure.
Active energies exceed the corresponding binding energy R5 as well as the fit cutoff.
The fit cutoff and binding threshold keep their distinct roles.

On an active branch the source is
\[
x=E'/E_0-y_0,\quad y=(x^2+y_1^2)^{1/2},\quad
F=(x-1)^2+y_w^2,\quad q=p/2-11/2,
\]
\[
\boxed{\sigma(E')=10^{-18}\sigma_0\,F\,y^q
       [1+\sqrt{y/y_a}]^{-p}}\quad{\rm cm^2}.
\tag{R19}
\]

| Species | \(E_0\), eV | \(\sigma_0\) | \(y_a\) | \(p\) | \(y_w\) | \(y_0\) | \(y_1\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| HI | 0.4298 | 54750 | 32.88 | 2.963 | 0 | 0 | 0 |
| HeI | 13.61 | 949.2 | 1.469 | 3.188 | 2.039 | 0.4434 | 2.136 |
| HeII | 1.720 | 13690 | 32.88 | 2.963 | 0 | 0 | 0 |

For every active interval, \(1<x_-\le x_+\), \(y_->0\), \(F_->0\), and \(q<0\).
All factors are therefore smooth and positive there. Logarithmic differentiation gives
\[
\frac{\sigma'}{\sigma}
=\frac1{E_0}\left[
\frac{2(x-1)}F
+q\frac{x}{y^2}
-\frac p2\frac{x}{y^2}\frac{\sqrt{y/y_a}}{1+\sqrt{y/y_a}}
\right].
\tag{R20}
\]

The prime here means \(d/dE'\), so its unit is eV\(^{-1}\).
Since \(|q|+p/2=11/2\) and the last square-root ratio is at most one,
\[
\left|\frac{\sigma'}{\sigma}\right|
\le H_\sigma:=
\frac1{E_0}\left[
\frac{2(x_+-1)}{F_-}+\frac{11}{2}\frac{x_+}{y_-^2}
\right].
\tag{R21}
\]

An explicit upper value bound is
\[
\bar\sigma_{\rm factor}
=10^{-18}\sigma_0 F_+\,y_-^q
 [1+\sqrt{y_-/y_a}]^{-p}.
\tag{R22}
\]
Rational enclosures of the positive powers in R22 yield a rational upper bound.
Using the lower rational enclosure of \(y_-\) in R21 only enlarges that bound.
Then \(|\sigma'|\le\bar\sigma_{\rm factor}H_\sigma\).
No monotonicity assumption about the complete Verner fit is needed.

## 6. Rational Verner and Doppler-derivative bounds

Rows below follow HI, HeI, HeII; columns follow lab energy 23, 35, 70 eV.
The interval support from §5 makes the zeros exact.

\[
\boxed{
\bar\sigma=
\begin{pmatrix}
3\,10^{-18}&10^{-18}&2\,10^{-19}\\
0&8\,10^{-18}&2\,10^{-18}\\
0&0&2\,10^{-18}
\end{pmatrix}{\rm cm^2}
}
\tag{R23}
\]
\[
\boxed{
\overline{|\sigma'|}=
\begin{pmatrix}
10^{-18}&3\,10^{-19}&3\,10^{-20}\\
0&10^{-18}&3\,10^{-19}\\
0&0&3\,10^{-19}
\end{pmatrix}{\rm cm^2/eV}.
}
\tag{R24}
\]

The actual certified factor upper bounds before choosing those rational caps display as

| Species/energy | \(\bar\sigma_{\rm factor}\), cm² | \(\bar\sigma_{\rm factor}H_\sigma\), cm²/eV |
|---|---:|---:|
| HI / 23 | \(2.129289\,10^{-18}\) | \(8.146003\,10^{-19}\) |
| HI / 35 | \(6.439934\,10^{-19}\) | \(1.615724\,10^{-19}\) |
| HI / 70 | \(8.288059\,10^{-20}\) | \(1.037700\,10^{-20}\) |
| HeI / 35 | \(4.982954\,10^{-18}\) | \(7.118488\,10^{-19}\) |
| HeI / 70 | \(1.347142\,10^{-18}\) | \(1.604530\,10^{-19}\) |
| HeII / 70 | \(1.137404\,10^{-18}\) | \(1.432441\,10^{-19}\) |

These abbreviated displays are upward-rounded. R23–R24 are the simple exact rational caps consumed by the continuation construction.

For velocity derivatives, the exact identities
\[
\nabla_\beta\delta_q=\gamma^3 a_q\beta-\gamma e_q,\qquad
\nabla_\beta a_q=-e_q
\tag{R25}
\]
give the rational bounds
\[
\gamma\le\bar\gamma=501/500,\quad
a_q\le1+B_v,\quad
|\nabla_\beta\delta_q|_2
\le\bar\gamma+\bar\gamma^3(1+B_v)B_v<11/10.
\tag{R26}
\]
The inequalities \(\bar\gamma^2(1-B_v^2)>1\) and the final rational inequality were included in the exact check.

## 7. From atomic envelopes to full event/Jacobian bounds

This section is the reusable connection for the parent matrix majorant.
All differentials first treat \((\zeta,T,\beta)\) as independent primitive coordinates;
the certified conservative-to-primitive derivative is then composed by the chain rule.

From R1 and R3,
\[
\bar e=141/250=0.564,\quad
\bar y=(0.501,\ 0.042,\ 0.021),\quad
\bar z=(0.501,\ 0.021,\ 0.021).
\tag{R27}
\]
The coefficient-vector norms are
\(\|\nabla_\zeta e\|_1=4\),
\(\|\nabla_\zeta y_i\|_1=(1,2,1)\),
and \(\|\nabla_\zeta z_i\|_1=1\).
The cube has strictly positive upper-ion, lower-target and electron fractions.

For any rate or energy coefficient \(k(T)\) in §§4, with target fraction \(q(\zeta)\),
put
\[
P_k=D^2(1-|\beta|^2)e\,q\,k(T).
\]
If \(0\le q\le\bar q\), \(\|\nabla_\zeta q\|_1=s_q\), then
\[
|P_k|\le D^2\bar e\,\bar q\,\bar k,
\tag{R28}
\]
\[
\boxed{
|dP_k|\le D^2\left[
\bar e\bar q\,\overline{|k'|}\,|dT|
+(4\bar q+\bar e s_q)\bar k\,|d\zeta|_\infty
+2B_v\bar e\bar q\,\bar k\,|d\beta|_2
\right].
}
\tag{R29}
\]
The velocity term uses the exact identity \(\gamma^{-2}=1-|\beta|^2\).
R29 covers every CI/RR/DR event and every RR/DR kinetic or escape power.
For DR use \(\bar q=0.021,s_q=1\). Sum the R6/R7 positive contributions to obtain the total escape bound.

The moving absorption coefficient is
\[
\lambda_{iq}=cD\,y_i\,a_q\,\sigma_i(\delta_qE_q).
\tag{R30}
\]
It has no explicit temperature dependence at fixed \((\zeta,\beta)\).
For each active species/node pair, R23–R26 give
\[
\bar\lambda_{iq}=cD\bar y_i(1+B_v)\bar\sigma_{iq},
\tag{R31}
\]
\[
|d\lambda_{iq}|
\le cD(1+B_v)\bar\sigma_{iq}s_{y_i}|d\zeta|_\infty
+cD\bar y_i
 \left[\bar\sigma_{iq}+(1+B_v)E_q
       \overline{|\sigma'_{iq}|}\frac{11}{10}\right]|d\beta|_2.
\tag{R32}
\]
Inactive entries and their derivatives remain zero. These bounds include the Doppler-energy derivative and the relative-incidence factor from the same endpoint.

For the selected \(S_q=0\), photon elimination supplies
\[
N_q^+=\frac{N_q^-}{1+h\Lambda_q},\qquad
F_{iq}:=\lambda_{iq}N_q^+
=\frac{N_q^-\lambda_{iq}}{1+h\Lambda_q},\quad
\Lambda_q=\sum_i\lambda_{iq}.
\tag{R33}
\]
Here \(N_q^-=D/100\) is fixed for every node. For all \(h\ge0\) and physical candidates,
\[
0\le F_{iq}\le N_q^-\bar\lambda_{iq},
\tag{R34}
\]
\[
dF_{iq}=N_q^-\left[
\frac{d\lambda_{iq}}{1+h\Lambda_q}
-\frac{h\lambda_{iq}\,d\Lambda_q}{(1+h\Lambda_q)^2}\right].
\]
Since \(0\le h\lambda_{iq}/(1+h\Lambda_q)\le1\),
\[
|dF_{iq}|\le N_q^-\bigl(|d\lambda_{iq}|+|d\Lambda_q|\bigr),
\qquad
\sum_i|dF_{iq}|\le2N_q^-\sum_i|d\lambda_{iq}|.
\tag{R35}
\]
This derivative majorant is uniform in \(h\ge0\). The formula itself also covers a zero \(\lambda_i\); when every opacity is zero the rational denominator is still one.
For physical event increments \(A=hF\), multiply R34–R35 by \(h\).

The composition source divides net proper event counts by \(D\), as in THEORY05.
Lab absorption energy/momentum multiply these same events by
\(\epsilon E_q\) and \(\epsilon E_qe_q\).
The escape term uses \(\gamma Q'_{\rm esc}\) and \(\gamma Q'_{\rm esc}\beta\).
Consequently R28–R35 and the independently certified primitive derivative supply finite, explicit componentwise majorants for the parent's seven-variable source/Jacobian.
Their units remain visible: event rates per proper volume and time, lab photon number density, erg energies, and H-normalized composition.

## 8. Exact interval certificate and actual execution

The endpoint and positive-factor enclosures use rational arithmetic:

1. For positive rational \(x\) and rational exponent \(p/q\), choose positive rational \(l,u\) on a \(10^{-16}\) grid using an 80-digit proposal. Accept the bracket only after the exact comparisons
   \(l^q\le x^p\le u^q\) succeed. Monotonicity of the positive \(q\)-th power proves \(x^{p/q}\in[l,u]\). This applies to negative \(p\) as well.
2. Propagate positive products, quotients and powers with the appropriate endpoint order.
3. For \(x\ge0\), \(n=64\), let \(S_n=\sum_{k=0}^{n}x^k/k!\) and \(t_{n+1}=x^{n+1}/(n+1)!\).
   When \(x<n+2\),
   \[
   S_n\le e^x\le S_n+\frac{t_{n+1}}{1-x/(n+2)}.
   \]
   Each subsequent term ratio is at most \(x/(n+2)\). Inversion gives an exact rational enclosure of \(e^{-x}\).
4. Compare every resulting rational upper endpoint and derivative majorant with its chosen rational cap using exact arithmetic.

The current request performed **one** scientific evaluator call. Its exported result has **20/20 named expression-check groups PASS**. It includes six differential identities, whole-interval monotonicity/positivity and all caps/domain/prefactor comparisons. The interval helpers returned 76 accepted rational-power brackets and five accepted exponential enclosures; these are internal witnesses, not additional independent theorem or scenario counts. No previous unit's successful group was rerun.

Artifacts:

- [Exact executed WL](RATE_ENVELOPE_CHECK.wl)
- [Exact evaluator call input](../evidence/RATE_ENVELOPE_CALL_INPUT.json)
- [Unmodified raw tool response](../evidence/RATE_ENVELOPE_WOLFRAM_RAW_RESULT.json)
- [Decoded scientific JSON](../evidence/RATE_ENVELOPE_RESULT.json)
- [Execution and metadata record](../evidence/RATE_ENVELOPE_EXECUTION_RECORD.json)

The final logging append generated `AssociateTo::argrx`: it passed three rules as separate arguments to `AssociateTo`, whose second argument should have been their rule list. The scientific Association and all 20 results were already complete and were exported unchanged. Elapsed kernel time, version and system ID were not appended, so those fields are recorded as unavailable rather than inferred from another run. The actual call's `timeConstraint: 60` is an input limit, not a measured runtime. The original input and warning are preserved; the metadata record gives the exact two-argument correction for any future replay. The successful mathematics was not rerun to repair logging.

## 9. Handoff

Use the simple rational coefficient/derivative tables in §4 and R23–R24, together with the kinetic/escape tables, in the parent's full-rate source majorant. Compose R29/R32 with the primitive author's certified bounds on \(dT,d\beta,d\zeta\) in the selected scaled affine cube. The next construction is the explicit self-map and contraction/continuation bound in that cube, including its thermal, simplex, velocity and active-support margins.

The original PRIMARY_PROVIDER_03 and COVARIANT_MOMENTS_04 coding obligations, the MOVING_GAS_STAGE_05 consumer obligation, and the owner DAG remain unchanged. This contribution supplies the full retained rate constants and first-derivative bounds needed by the new mathematical certificate.
