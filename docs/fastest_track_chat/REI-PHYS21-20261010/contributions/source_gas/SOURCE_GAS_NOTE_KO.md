# PHYS21 source binding와 FT03 scalar gas response

기여자: `/root/phys21_source_gas`. 후보 유도·source 해석 기여이며 최종 독립 판정이 아니다. 이 문서는 새 native history나 gas IVP를 실행하지 않는다. PHYS20의 닫힌 과학 검산도 재실행하지 않았다.

## 1. 실제 읽은 source와 identity

2026-10-10의 PHYS21 입력 head는 `faec51259ed26f660cf14568bcaa3d288e54bf9a`, root tree는 `d4c734ac2047e68966ccecc81da79eb68420f8a1`다. GitHub Git tree를 직접 읽어 `rust/rei_microphysics/src` tree가 PHYS20과 같은 `cb69b4736dd046e4675557577eb8e0ead037d1f3`임을 확인했다. PHYS20에 포함된 Rust source/example/test 8개 blob은 모두 현재 tree와 동일하다. 이는 source identity 검증이며 과학 검산 재실행이나 Rust execution이 아니다.

PHYS20 snapshot에 없던 `ft03_controlled.rs`와 `hhe_events.rs`를 이번에 pinned head에서 직접 읽었고, 저장한 bytes의 Git blob을 실제 remote tree와 대조했다.

| 파일 | 이번 유도에서 읽은 내용 |
|---|---|
| `coupled_primary.rs` | `PrimaryState`/stage 단위, 온도 변환, `raw`의 zero-photon FT03 호출, packet absorption/heat, endpoint gas RHS |
| `ft03_controlled.rs` | `ft03_rhs` 전체의 CI/RR/two-DR event, thermal/escape 및 species stoichiometry |
| `ft03_rates.rs` | 온도의존 CI/RR/DR fit, RR kinetic energy coefficient와 logarithmic slopes |
| `hhe_events.rs` | thermal constants, thresholds, electron-density/temperature 정의 |
| `paired_runtime.rs` | per-H/fixed-q 배열, initial source, birth weights, geometry 및 source의 stage 소유권 |
| `examples/paired_history.rs` | `Gamma`의 per-absorber 정의와 출력 온도 변환 |

새로 읽은 source identity:

- `ft03_controlled.rs`: Git blob `370fd2fa60521f2dc121ee81c7d24013a3b0d1e5`, SHA256 `61e11471482bb49d99e5d0eb79504d3f67538fbe6361653a0462d1abb0b672db`, 14,726 bytes.
- `hhe_events.rs`: Git blob `57a63eee1e9d8c4aa2b5ed663dbea15619359f71`, SHA256 `c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290`, 9,447 bytes.

전체 identity는 `SOURCE_BINDING.json`, 실제 Git 응답은 `REMOTE_SOURCE_READ.json`, source bytes는 `source_read/`에 있다. 아래 식은 이 source의 연속 시간 RHS에 결속한 직접 유도다. finite backward-Euler, energy-node hat remapping, binary64 evaluation 전체를 미분·인증했다는 뜻은 아니다.

## 2. State, 단위, source 소유권

Proper time \(t\), metric signature \((-+++)\), 고정된 prescribed mean expansion \(H(t)\)를 사용한다. \(\epsilon\)은 무차원 shear amplitude이며 \(H,n_H,f_{\rm He}\), 초기 scalar state와 scalar source amplitude는 \(\epsilon\)에 독립적이다. 현재 constant-H 입력에서는

\[
n_H(t)=10^{-4}\exp(-3Ht)\ {\rm cm}^{-3},\qquad f=f_{\rm He}=0.083.
\]

기체 상태는 코드와 같이

\[
y=(x,a,b,w)
=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w_{\rm eV/H})
\]

로 둔다. \(a,b\)는 He nucleus당 fraction이며 hydrogen-normalized fraction이 아니다. 총 전자수/H와 총 입자수/H는

\[
X_e=x+f(a+2b),\qquad \Pi=1+f+X_e,\qquad n_e=n_HX_e.
\]

\(e_{\rm V}=1.602176634\times10^{-12}\ {\rm erg/eV}\)와 \(k_B=1.380649\times10^{-16}\ {\rm erg/K}\)를 유지하면

\[
T=\mathcal A\,\frac{w}{\Pi},
\qquad
\mathcal A=\frac{2e_{\rm V}}{3k_B}.
\tag{SG1}
\]

원래 FT03 class의 `initial_state()`에는 [20,35,70] eV photon fixture가 있지만, paired history는 이것을 사용하지 않는다. 실제 paired initial은 \(x=0.9,a=0.3,b=0.6,T=50000\) K, \(N_{\rm init}=0.05\) photon/H, \(E_b=13.7\) eV다. source는 \(S=5\times10^{-15}\) photon/H/s다. `coupled_primary::raw`는 `photon_cm3=[0,0,0]`로 FT03 nonphoto RHS를 호출한 뒤, primary packet photo events와 heating을 한 번 추가한다. 따라서 source/transport는 `paired_runtime`, local reaction·thermal evolution은 `coupled_primary`가 소유한다. RR/DR emission은 이 Case-A closure의 escaped-energy ledger에 들어가며 여기서 primary photon source로 재주입하지 않는다.

연속 constant-S 모델의 birth measure는

\[
d\mu(\tau,E_b)
=0.05\,\delta_0(d\tau)\delta_{13.7}(dE_b)
+S\,d\tau\,\delta_{13.7}(dE_b),
\qquad 0\le\tau\le t.
\tag{SG2}
\]

이는 photon/H 단위다. 각 cohort는 birth의 물리적 입체각에서 등방이다. 그 각도 \(\Omega_b\)를 적분변수로 쓰면 \(d\Omega_b/(4\pi)\)만 사용한다. fixed-\(q\) 표현에는 \(J_b\)가 필요하며 두 표현을 동시에 곱하지 않는다. per-H photon count의 연속 방정식에 별도의 \(-3HN\)을 추가하지 않는다. proper density가 필요할 때 \(n_H N\)으로 변환한다.

## 3. 실제 FT03 nonphoto 및 primary RHS

각 species의 lower/upper population/H를

\[
\ell=(1-x,\ f(1-a-b),\ fa),\qquad
u=(x,\ fa,\ fb)
\tag{SG3}
\]

로 둔다. 아래 \(\beta_j,\alpha_j,d_k\)는 각각 source의 CI, RR, two-DR coefficient [cm\(^3\)/s]다.

\[
C_j=\ell_j n_e\beta_j(T),\qquad
R_j=u_j n_e\alpha_j(T),\qquad
D_k=u_1 n_e d_k(T),\quad k=1,2.
\tag{SG4}
\]

이들은 모두 events/H/s다. \(D_k\)는 HeII \(\to\) HeI를 담당한다. photo event/H/s를 \(A_j\), primary heating을 \(Q\) [eV/H/s]라 두면

\[
\begin{aligned}
\nu_0&=C_0-R_0+A_0,\\
\nu_1&=C_1-R_1-\sum_kD_k+A_1,\\
\nu_2&=C_2-R_2+A_2,\\
\dot x&=\nu_0,\\
\dot a&=(\nu_1-\nu_2)/f,\\
\dot b&=\nu_2/f.
\end{aligned}
\tag{SG5}
\]

RR kinetic cooling coefficient를

\[
\kappa_j(T)
=\frac{k_BT}{e_{\rm V}}\alpha_j(T)
\left(\frac32+g_j(T)\right),
\qquad
g_j=\frac{d\ln\alpha_j}{d\ln T},
\tag{SG6}
\]

로 두고 DR kinetic energy를 \(e_k^{\rm DR}=\mathrm{dr\_energy\_erg}_k/e_{\rm V}\)라 하면

\[
\mathcal C(y,t)
=\sum_j\chi_j C_j
+\sum_j u_j n_e\kappa_j(T)
+\sum_k e_k^{\rm DR}D_k
\tag{SG7}
\]

가 source의 nonphoto cooling/H/s다. 이에 따라

\[
\boxed{\dot w=-2Hw-\mathcal C+Q.}
\tag{SG8}
\]

thermal thresholds는 \(\chi=(13.598434599702,24.587389011,54.41776)\) eV다. HI opacity cutoff 13.60 eV와 thermal threshold \(\chi_0\)를 하나로 바꾸지 않는다. 이 source에 없는 extra thermal terms나 secondary-electron partition을 암묵적으로 더하지 않았다. prescribed isotropic gas의 work는 \(-2Hw\)이며 별도 shear-viscous heating 항을 도입하지 않는다.

## 4. Radiation functional과 gas feedback

FLRW baseline \(y_0(t)\)에 대해

\[
E_0(s;\tau,E_b)=E_b\,a(\tau)/a(s),\qquad
\lambda_0(s;\tau,E_b)=cn_H(s)\sum_j\ell_j(y_0(s))\sigma_j(E_0(s)),
\]

\[
P_0(t,\tau,E_b)=
\exp\!\left[-\int_\tau^t\lambda_0(s;\tau,E_b)\,ds\right].
\tag{SG9}
\]

일반 scalar radiation output은

\[
\mathcal R_\phi(t;y,\epsilon)
=\int_{\tau\le t}d\mu
 \left\langle P(t,\tau;\Omega_b)\,
 L_\phi(t,E(t),y(t))\right\rangle_{\Omega_b}.
\tag{SG10}
\]

endpoint functions의 정확한 mapping은 다음과 같다.

| 출력 | \(L_\phi\) | 단위 |
|---|---|---|
| 남은 photon count/H \(N\) | \(1\) | 적분 후 photon/H |
| photon energy/H \(U_\gamma\) | \(E\) | 적분 후 eV/H |
| per-absorber \(\Gamma_j\) | \(cn_H\sigma_j(E)\) | 적분 후 s\(^{-1}\) |
| photo event/H/s \(A_j\) | \(\lambda_j=cn_H\ell_j\sigma_j(E)\) | 적분 후 H\(^{-1}\)s\(^{-1}\) |
| primary heat/H/s \(Q\) | \(cn_H\sum_j\ell_j\sigma_j(E)(E-\chi_j)\) | 적분 후 eV/H/s |

특히 \(A_j=\ell_j\Gamma_j\)다. \(Q=\sum_j\ell_j\mathcal H_j\)로 쓸 때 \(\mathcal H_j=cn_H\int d\mu\langle P\sigma_j(E)(E-\chi_j)\rangle\)는 per-absorber heating rate다. source의 \(\Gamma\) 출력에는 \(\ell_j\)가 들어가지 않는다.

이제 continuum first variation가 0인 PHYS20 조건 아래

\[
y_\epsilon=y_0+\epsilon^2\eta+o(\epsilon^2),
\qquad \eta=[\epsilon^2]y=\tfrac12\partial_\epsilon^2y|_0
\tag{SG11}
\]

를 사용한다. 아래는 coefficient convention이며 second derivative convention에는 전체를 2배 해야 한다. frozen *baseline trajectory*에서의 순수 geometry forcing은

\[
r_\phi(t)=[\epsilon^2]\mathcal R_\phi(t;y_0,\epsilon)
\tag{SG12}
\]

다. 이는 neutral fraction을 상수로 고정한다는 뜻이 아니다. \(y_0(t)\)를 시간에 따라 유지하면서 \(\epsilon\)-변화만 고정한 것이다. 전체 2차 계수는

\[
\boxed{
\mathcal R_{\phi,2}
=r_\phi+D_y\mathcal R_\phi[y_0](\eta).
}
\tag{SG13}
\]

energy는 gas state와 독립인 prescribed geometry로 결정된다. 따라서 Fréchet derivative는

\[
\boxed{
D_y\mathcal R_\phi[\eta](t)
=
\int_{\tau\le t}d\mu\,P_0
\left[
 L_{\phi,y,0}(t)\eta(t)
 -
 L_{\phi,0}(t)\int_\tau^t
 \lambda_{y,0}(s)\eta(s)\,ds
\right].
}
\tag{SG14}
\]

첫 항은 endpoint absorber abundance 변화, 두 번째는 모든 이전 시각의 opacity 변화다. \(\Gamma,N,U_\gamma\)의 \(L_y\)는 0이고 gas response는 survival memory에서 온다. \(A_j,Q\)에는 local abundance 항과 memory가 모두 있다. \(A_j\)용 식을 사용한 뒤 \(\ell_j\)의 변분을 한 번 더 더하면 double count가 된다. \(\Gamma_j\)용 식을 사용한다면 반대로

\[
A_{j,2}=\ell_{j,0}\Gamma_{j,2}+\ell_{j,2}\Gamma_{j,0}
\tag{SG15}
\]

를 적용해야 한다.

Source의 cross section은 local \(T\)에 직접 의존하지 않으므로

\[
\lambda_y
=cn_H
\left(
-\sigma_0,\ f(\sigma_2-\sigma_1),\ -f\sigma_1,\ 0
\right).
\tag{SG16}
\]

따라서 \(\lambda_w=0\)이나 thermal feedback 전체가 0인 것은 아니다. 온도는 이후 CI/RR/DR를 통해 fraction과 opacity에 다시 영향을 준다.

현재 13.7 eV soft-photon support와 expanding axes의 cutoff-free neighborhood에서는 \(\sigma_{\rm HeI}=\sigma_{\rm HeII}=0\). 따라서 direct \(r_{A_1},r_{A_2}\)와 \(\Gamma_{\rm HeI},\Gamma_{\rm HeII}\)는 0이다. He gas response는 \(n_e,T\)를 통해 연결되므로 \(\eta_a,\eta_b=0\)이라고 결론 내릴 수 없다.

## 5. 명시적인 local gas Jacobian

\[
\eta_\ell=(-\eta_x,-f(\eta_a+\eta_b),f\eta_a),
\qquad
\eta_u=(\eta_x,f\eta_a,f\eta_b),
\qquad
\eta_{n_e}=n_H[\eta_x+f(\eta_a+2\eta_b)].
\tag{SG17}
\]

가장 중요한 thermal mapping은

\[
\boxed{
\eta_T=
\frac{\mathcal A}{\Pi_0}\eta_w
-\frac{T_0}{\Pi_0}
 [\eta_x+f(\eta_a+2\eta_b)]
=
T_0\!\left(\frac{\eta_w}{w_0}-\frac{\eta_\Pi}{\Pi_0}\right).
}
\tag{SG18}
\]

\(\eta_w=0\)이어도 입자수가 증가하면 \(\eta_T<0\)다. \(w\)를 온도로 표시할 때 \(T_0\eta_w/w_0\)만 사용하면 잘못된 thermal response가 된다. \(y_1=0\)이므로 이 차수에 \(D^2T[y_1,y_1]\)는 없다.

event variations는

\[
\begin{aligned}
\eta_{C_j}
&=n_e\beta_j\eta_{\ell_j}
+\ell_j\beta_j\eta_{n_e}
+\ell_jn_e\beta_j'(T)\eta_T,\\
\eta_{R_j}
&=n_e\alpha_j\eta_{u_j}
+u_j\alpha_j\eta_{n_e}
+u_jn_e\alpha_j'(T)\eta_T,\\
\eta_{D_k}
&=n_ed_k\eta_{u_1}
+u_1d_k\eta_{n_e}
+u_1n_ed_k'(T)\eta_T.
\end{aligned}
\tag{SG19}
\]

모든 우변 coefficient는 baseline에서 평가한다. cooling은

\[
\eta_{\mathcal C}
=\sum_j\chi_j\eta_{C_j}
+\sum_j\left[
 n_e\kappa_j\eta_{u_j}
 +u_j\kappa_j\eta_{n_e}
 +u_jn_e\kappa_j'\eta_T
\right]
+\sum_ke_k^{\rm DR}\eta_{D_k}.
\tag{SG20}
\]

\(\eta_{C}-\eta_R-\eta_D\)를 SG5의 동일 stoichiometry에 넣고, thermal row를 \(-2H\eta_w-\eta_{\mathcal C}\)로 두면 \(J_{\rm np}(t)\eta\)가 완전히 정해진다. gas Hessian은 필요하지 않다. scalar \(y_1=0\)이므로 \(D_y^2F[y_1,y_1]=0\)이고 선두 quadratic response는 baseline의 **선형** gas operator로 전달된다.

소스에 있는 fit만으로 필요한 derivative를 직접 평가할 수 있다. \(g_j'=dg_j/d\ln T\)는 `log_slope_derivative` 필드다.

\[
\alpha_j'=\frac{\alpha_jg_j}{T},
\qquad
\kappa_j'=\frac{k_B}{e_{\rm V}}\alpha_j
\left[(1+g_j)(\tfrac32+g_j)+g_j'\right].
\tag{SG21}
\]

CI의 \(\lambda_j=\Lambda_j/T,\ v_j=(\lambda_j/C_j^{\rm fit})^{r_j}\)라 쓰면

\[
\frac{d\ln\beta_j}{d\ln T}
=-\frac32+\frac{\lambda_j}{2}-p_j
 +d_j^{\rm fit}r_j\frac{v_j}{1+v_j}.
\tag{SG22}
\]

DR fit \(d_k=A_kT^{-3/2}e^{-B_k/T}\)에는 \(d_k'=d_k(-3/2+B_k/T)/T\)를 쓴다. CI event \(C_j\)와 fit constant \(C_j^{\rm fit}\)는 다른 양이다.

## 6. 닫힌 causal equation의 computational form

\[
\mathbf R=(A_0,A_1,A_2,Q)^T,\qquad
B_{\rm inj}=
\begin{pmatrix}
1&0&0&0\\
0&1/f&-1/f&0\\
0&0&1/f&0\\
0&0&0&1
\end{pmatrix}.
\tag{SG23}
\]

그러면

\[
\boxed{
\dot\eta
=J_{\rm np}(t)\eta
 +B_{\rm inj}D_y\mathbf R[\eta]
 +B_{\rm inj}\mathbf r(t),
\qquad \eta(0)=0.
}
\tag{SG24}
\]

birth integral과 past-time integral을 바꾸면

\[
\boxed{
\dot\eta(t)=A(t)\eta(t)
+\int_0^tK(t,s)\eta(s)\,ds
+f_2(t),
}
\tag{SG25}
\]

\[
\begin{aligned}
A(t)&=J_{\rm np}(t)+B_{\rm inj}
 \int_{\tau\le t}d\mu\,P_0(t,\tau)\,\mathbf L_{y,0}(t;\tau),\\
K(t,s)&=-B_{\rm inj}\!
 \int_{\tau\le s}d\mu\,
 P_0(t,\tau)\,
 \mathbf L_0(t;\tau)\otimes\lambda_{y,0}(s;\tau),\\
f_2(t)&=B_{\rm inj}\mathbf r(t).
\end{aligned}
\tag{SG26}
\]

연속 source와 초기 cohort atom은 둘 다 \(d\mu\)에 포함한다. source가 \(\epsilon\)-independent이므로 \([\epsilon^2]S=0\)이며 별도 source-amplitude forcing은 없다. 유한 구간의 continuous/bounded coefficients와 인과적 regularity 아래 SG25는 standard linear Volterra initial-value problem으로 유일한 해를 갖는다. 이것은 response를 정의하는 닫힌 방정식이며, 수치해 \(\eta(t)\)를 이번 source 기여자가 계산했다는 뜻은 아니다.

유일성과 boundedness만으로 \(f_2\)의 부호가 온도·ion fraction의 부호로 그대로 전달되지는 않는다. \(J_{\rm np}\), memory kernel, thermal particle-count mapping에 서로 다른 부호가 있기 때문이다.

## 7. 추적 가능한 observable와 conservation checks

\[
\Gamma_{j,2}=r_{\Gamma_j}+D_y\Gamma_j[\eta],
\qquad
Q_2=r_Q+D_yQ[\eta],
\qquad
N_2=r_N+D_yN[\eta],
\qquad
U_{\gamma,2}=r_U+D_yU_\gamma[\eta].
\tag{SG27}
\]

고정 proper-time 구간에서 scalar Thomson integral을 **정의한다면**

\[
\tau_e(t)=c\sigma_T\int_0^tn_e(s)\,ds,\qquad
\tau_{e,2}=c\sigma_T\int_0^t n_H(s)
 [\eta_x+f(\eta_a+2\eta_b)]\,ds.
\tag{SG28}
\]

SG28은 photon absorption optical depth \(\Theta\)와 다른 양이다. observer lightcone, redshift-fixed endpoint, full sky directional Thomson observable를 계산했다는 뜻도 아니다.

per-H photon number는 \(\dot N=S-\sum_j A_j\)이므로 source가 고정이면

\[
\dot N_2=-\sum_j A_{j,2},\qquad N_2(0)=0.
\tag{SG29}
\]

ionization potential/H

\[
I=\chi_0x+f[\chi_1a+(\chi_1+\chi_2)b]
\]

와 escaped energy/H \(U_{\rm esc}\)를 포함한 source의 연속 ledger는

\[
\frac{d}{dt}(w+I+U_{\rm esc}+U_\gamma)
=S E_b-2Hw-\dot W_{\rm redshift},
\qquad
\dot W_{\rm redshift}=\int H_\parallel E\,dN.
\tag{SG30}
\]

따라서 2차 coefficient에도
\(\partial_t(w_2+I_2+U_{{\rm esc},2}+U_{\gamma,2})
=-2Hw_2-\dot W_{{\rm redshift},2}\)가 성립해야 한다.
SG29–30은 유도에 의한 count/energy 일관성 조건이며 native ledger 실행 PASS를 뜻하지 않는다.

## 8. 기존 PHYS19 evidence가 주는 것과 이번에 실제 없는 것

이번에 읽은 PHYS19 자료는 Git의 README, contract, results summary, source binding, verification 및 BRIDGE13 continuous-chain contract다. PHYS19 immutable ZIP의 SHA256 `66b93eebf614cc83949abfeb167a94b94d1a2cae3024c9e1ecdf9fcd7e116737`와 remote backup IDs는 기존 metadata에서 읽었지만, 본 기여자가 그 ZIP 전체를 복원해 검토한 것은 아니다.

확인한 published evidence는 다음을 준다.

- 동일 FT03 nonphoto equations, continuous constant-S source의 정확한 의미와 source identity.
- \(t\in[0,1.25\times10^9]\) s에서 cutoff와 time/birth derivatives에 대한 이전 conditional certificate의 범위.
- finite-birth solution, native scheme, true constant-S gas 사이의 구별.
- \(\sup\) 및 terminal source-error bounds, continuum-minus-native terminal intervals.

이 자료의 finite list of derivative bounds와 terminal difference intervals만으로 \(y_0(s)\), cohort survival \(P_0(t,\tau)\), pathwise Hessian moments 또는 SG26의 시간 의존 coefficient가 **유일하게 복원되지 않는다**. error bound를 baseline trajectory 값으로 사용하는 것은 불가능하다. 본 workspace의 PHYS20 snapshot에도 true constant-S baseline의 callable dense output이나 전체 trajectory enclosure가 없다. Library에서 정확한 PHYS19 archive 이름과 짧은 PHYS19 제목으로 각 한 번 검색했으나 resolve되지 않았다. 이는 archive의 부재를 증명하지 않으며, root 지시에 따라 다른 저장소/원자물리 lane으로 범위를 넓히지 않았다.

따라서 **구조적 functional SG24–26은 derived로 완료**할 수 있다. 실제 evolving-gas leading coefficient와 그 부호의 숫자를 얻으려면 기존 immutable archive에서 다음 값을 source-bound하게 읽을 수 있어야 하거나 별도 허용된 실행이 필요하다.

1. 같은 continuous constant-S 모델의 \(y_0(s)\) 값 또는 적분 가능한 enclosure, 그 validity interval.
2. cohort별 \(E_0(s;\tau,E_b),P_0(t,\tau,E_b)\)와 source measure.
3. time/birth integration 오차 및 정밀도, baseline trajectory error가 새 quadratic functional에 미치는 범위.
4. 사용되는 interval 전체의 cutoff margin과 bounded \(C^2\) response; native discretization의 branchwise smoothness는 별도 문제.

이는 whole-project blocker가 아니다. 이번 root 후보의 직접 2차 유도, light radiation kernels, gas-response operator와 다음 handoff를 진행하는 데는 이 숫자가 필요하지 않다. PHYS19 숫자를 Bianchi error certificate나 \(\eta_T,\eta_x,\eta_\tau\)의 계산값으로 승격하지 않는다.

## 9. 근거 상태와 유지 조건

- source identity 및 source-defined units/ownership: **source-inspected / byte-identity-verified**. 이에 결속한 수식은 **derived; source supports**. Native 구현 실행을 검증했다는 상태로 분류하지 않는다.
- SG1–30와 explicit Jacobian/Volterra mapping: **derived**, declared smooth continuum conditions.
- 새 local derivative diagnostic: 세 개의 명시적 local fixture에서 nonphoto Jacobian 48개와 temperature/particle-count gradient 12개를 analytic JVP와 complex-step으로 대조했다. **60/60 통과**, 최대 상대차 `1.1287609103309596e-15`, 실제 exit 0. `LOCAL_GAS_DERIVATIVE_CHECK.json` 및 execution receipt 참조. 이는 manual Python transcription의 local derivative 검산이며 native Rust, radiation memory 해, gas trajectory를 실행·인증하지 않는다.
- 첫 diagnostic은 실패가 아니라 실제 **60/60 PASS, exit 0**이었다. 이후 source의 DR Kelvin 상수 계산 순서와 Python transcription의 미세한 차이(합산 후 곱셈 대 각각 곱한 뒤 합산)를 발견해 source 순서로 수정했다. 분류는 **diagnostic implementation/transcription correction**이며 물리 오류나 runtime failure로 분류하지 않는다. 최초 passing result, execution receipt와 원 source를 `_v1`로 보존했다. 동일 step `1e-24`, 동일 tolerance `2e-12`를 유지해 수정본도 **60/60 PASS, exit 0**으로 실행했다. 최종 표시 최대 상대차도 동일하다. 기존 PHYS20 proof 재실행은 없다.
- 실제 coupled \(x,T,\Gamma,\tau\) quadratic coefficient/sign: **unresolved**.
- physical admission: **HOLD**.
- `[160,161] FAIL`, `tick160`, auxiliary escape FAIL 보존.
- HH/RCT/CR OFF, precision atomic PARKED. source/default/runtime_returns mutation 없음.

