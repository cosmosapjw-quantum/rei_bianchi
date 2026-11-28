# BASS_HE THEORY06 — full-rate moving gas의 정량적 해 가지와 continuation

연구 단위: **HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06**  
경로: physmath-research-loop 1.0.0, THEORY R1–R10  
작성일: 2026-10-13 KST  
부모: THEORY05, BASS_HE PR33의 고정 head `94a34d09ad5810a675b556561e5593b279d30448`  
실제 provider: rei_bianchi PR114의 고정 head `a5c958c414dea41216b445c05f58df837f05cacb`  
채택 판정: 별도 [독립 DECISION](../review/DECISION.json); 최종 종료 identity는 CLOSEOUT 및 전달 영수증을 따른다.

## 1. 이번에 얻은 결과

직전 THEORY05가 열어 둔 과제는 실제 full-rate source에 대한 정량적 도함수 상계와 양의 step 구간이었다. 이번에는 명시한 7차원 물리 cube에서 CI 세 과정, RR 세 과정, 두 DR 공명 및 광흡수를 함께 유지하고, 아래 구간 전체의 backward-Euler 해를 인증했다.

\[
\boxed{0\le h\le 5\times10^8\ {\rm s}.}
\]

고정된 이전 상태에 대해 이 범위의 각 h마다 cube 안에 정확히 하나의 해가 있고, 해들은 이전 상태에서 시작하는 하나의 \(C^1\) 가지를 이룬다. 정확한 유리수 계산으로 얻은 self-map 상계와 수축 상수는

\[
HB=0.8030438877396564<1,\qquad
q=HL(H)=0.02247826905460884\ldots<1
\]

이다. H는 약 15.844 Julian years다. 이 수치는 **한 source stage의 시간 간격 h를 바꾸는 매개변수 가지**에 대한 존재·유일성·물리 영역 보증이다. 여러 time step으로 이루어진 궤적이나 그 시간 이산화 오차는 이후 구현·적분 계약에서 다룬다.

이번 구성의 세 핵심은 다음과 같다.

1. 기준 기체 속도에 투영한 에너지에서 조성의 결합에너지를 빼는 **가역 affine 좌표**를 도입했다. 큰 rest/bulk 에너지 때문에 생기는 열적 역변환의 민감도를 줄이면서 부모의 7개 유한 보존식을 정확히 유지한다.
2. 이 좌표의 cube 전체가 물리 영역에 들어감을 먼저 증명한 뒤, primitive·온도·밀도·Doppler·실제 반응률의 도함수를 결합했다. 구간 상계는 표본 최대값에 의존하지 않는다.
3. 실제 H를 갖는 인증에 더해, 다음 corrector의 잔차 오차상계, parameter tube의 포함 조건, 인접 인증을 같은 root로 잇는 조건, 최대 가지의 연장 대안을 유도했다.

상세 유도는 [primitive 증명](../derivations/PRIMITIVE_DIFFERENTIAL_BOUNDS.md), [실제 rate 경계](../derivations/RATE_ENVELOPES.md), [full source 및 continuation 증명](../derivations/FULL_SOURCE_CONTINUATION_CERTIFICATE.md), [명시적 H 인증](../derivations/EXPLICIT_H_CERTIFICATE.md)에 나뉘어 있다. 아래에서는 결론을 평가할 수 있도록 필요한 식과 경계를 함께 설명한다.

## 2. 현재 가정과 근거

| 항목 | 이번 루프에서의 지위와 근거 |
|---|---|
| 공통 기체 속도, 고정 Eulerian tetrad·체적 | 부모 THEORY05의 물리적 stage 정의를 유지한다. \(D=\gamma n_H\)가 고정이다. |
| 7변수 보존식 | \((\zeta,E,\mathbf M)\)의 화학 3식, 에너지 1식, 운동량 3식을 그대로 사용한다. \(\mathbf M\)은 물리적 운동량 밀도에 c를 곱한 양이다. |
| Primitive inverse | 부모의 양의 conservative cone에서의 gamma-law 전역 역변환 정리를 재사용한다. 이번 새 부분은 조성을 함께 움직이는 affine cube의 포함 증명과 정량 Jacobian 경계다. |
| 원자 물리 | source에 고정된 full FT03 CI/RR/two-DR/primary absorption을 사용한다. 다른 reference coefficient body로 바꾸지 않았다. |
| 광자 | 23, 35, 70 eV의 여섯 방향성 node, 고정 lab energy와 direction, 동일 endpoint의 opacity·event·energy·momentum을 사용한다. |
| 방출 손실 | RR/DR의 source-defined captured kinetic 및 binding escape를 모두 포함한다. 부모의 gas-frame isotropic escape moment를 유지한다. |
| 새로운 수치 영역 | 아래 초기 상태와 cube를 명시한 수학적 예로 구성했다. 기존 production campaign의 초기 조건을 바꾸는 지시가 아니다. |
| 검증 범위 | Wolfram exact algebra·구간 산술 및 실제 xAct tensor 검산. Native build, chemical RHS, ODE 적분 실행은 모두 0이다. |

Source의 현재 head와 최근 PR 범위를 읽어 선택한 두 head가 유지됨을 확인했다. 네 관련 source 파일의 정확한 SHA256, 함수와 literal, line 위치는 [CURRENT_SOURCE.json](../source_map/CURRENT_SOURCE.json)과 [SOURCE_FUNCTIONS.md](../source_map/SOURCE_FUNCTIONS.md)에 있다. THEORY05에서 이미 닫힌 검산은 재실행하지 않았다. 부모가 채택한 global primitive theorem과 일반 contraction·continuation 정리 자체를 이번 새 정리로 주장하지 않는다.

공간시간 부호는 \((-+++ )\)다. \(c,\hbar,k_B,\epsilon_{\rm eV}\)를 명시하며, photon energy는 \(\epsilon_{\rm eV}E_q=\hbar\omega_q\)다. 계산 단위는 cm, s, erg이고, per-H energy를 적을 때에는 eV/H로 정규화한다.

## 3. 실제로 구성한 물리 cube

\[
D=10^{-3}\ {\rm cm^{-3}},\quad f=2/25,\quad
\zeta_*=(1/2,1/50,1/50),\quad T_*=50000\ {\rm K}.
\]

여기서 \(\zeta=(x_{\rm HII}, f x_{\rm HeII},f x_{\rm HeIII})\)다. 세 성분은 모두 H nucleus당 abundance이며, helium fraction 두 개를 다시 f로 곱하지 않는다. Electron fraction과 입자 수는

\[
e_H=\zeta_1+\zeta_2+2\zeta_3,\qquad d=1+f+e_H
\]

이다. Anchor 속도는

\[
\beta_*=(0,0,41/841),\qquad \gamma_*=841/840
\]

로 정했다. Lorentz normalization이 정확한 유리수이므로 뒤의 경계 산술에 근삿값을 넣을 필요가 없다. Neutral reference parameter는

\[
\mu=\frac{m_{\rm ref}c^2}{\epsilon_{\rm eV}}
\in[10^9,1.5\times10^9]\ {\rm eV/H}
\]

이며, 하나의 stage에서는 고정되고 아래 경계는 이 전 구간에서 유효하다.

Binding energy는

\[
B=\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3,
\quad a=\mu+B
\]

이다. 정확한 값은 \(\chi=(13.598434599702,24.587389011,54.41776)\) eV다. Cross-section fit cutoff \((13.60,24.59,54.42)\) eV와 서로 다른 역할을 유지한다.

Lab normalized energy·momentum을

\[
e=\frac{E}{D\epsilon_{\rm eV}},\qquad
\mathbf m=\frac{\mathbf M}{D\epsilon_{\rm eV}}
\]

로 놓고, 새 energy coordinate를

\[
\boxed{t=\gamma_*(e-\beta_*\cdot\mathbf m)-a}
\]

로 정의한다. \(e=(a+t)/\gamma_*+\beta_*\cdot\mathbf m\)이므로 이 변환은 고정된 가역 affine 변환이다. Anchor에서 \(t_*=w_*=3k_Bd_*T_*/(2\epsilon_{\rm eV})\)이며 약 10.59932 eV/H다.

\(z=(\zeta,t,\mathbf m)\)와 diagonal scale

\[
s=(10^{-3},10^{-3},10^{-3},1/4,
 a_*10^{-6},a_*10^{-6},a_*10^{-6})
\]

로 \(X_i=(z_i-z_{*,i})/s_i\)를 정의한다. 인증 영역은 \(\|X\|_\infty\le1\)이다. Momentum center는 \(\mathbf m_*=(a_*+5w_*/3)\gamma_*\beta_*\)다.

여섯 photon node는 \((23\,{\rm eV},\pm e_x),(35\,{\rm eV},\pm e_y),(70\,{\rm eV},\pm e_z)\)이며, 각 node에 \(N_q^-/D=1/100\), 외부 source는 \(S_q=0\)이다. HI는 모든 node를 흡수하고, HeI는 35/70 eV node를, HeII는 70 eV node를 흡수하는 고정 cutoff cell을 구성한다.

## 4. 왜 affine energy가 필요한가

에너지의 큰 rest/bulk 부분을 각각 독립적으로 경계하면, momentum의 작은 상대 변화도 열적 energy 좌표에서는 과도한 경계를 만들 수 있다. 새 t는 cold kinetic energy의 anchor tangent를 상수 계수로 제거한다. 따라서 finite backward-Euler map 자체를 바꾸는 비선형 좌표 보정이 필요하지 않다.

원래 잔차를 \(F_\zeta,F_E,F_M\)라 할 때 변환된 energy 잔차는 정확히

\[
F_t=\gamma_*\left(\frac{F_E}{D\epsilon_{\rm eV}}
-\beta_*\cdot\frac{F_M}{D\epsilon_{\rm eV}}\right)
-\nabla_\zeta B\cdot F_\zeta.
\]

이는 원래 일곱 식의 상수 행 변환이다. Momentum 세 식과 사건의 lab-time 정의를 유지한다. 또 anchor velocity에서의 미분은

\[
dt=dw+\frac23 w\frac{d\gamma}{\gamma}
\]

다. 압력에 해당하는 velocity 항을 버리지 않았으며, 이 항은 실제 xAct stress-current projection에서도 확인했다.

## 5. 물리 영역 포함을 먼저 증명했다

\(\mathcal H=\sqrt{a^2+|\mathbf m|^2}\), \(\mathbf v=\mathbf m-a\gamma_*\beta_*\)라 놓는다. Cold norm의 tangent-plane remainder는

\[
R=\mathcal H-\frac a{\gamma_*}-\beta_*\cdot\mathbf m
\]

이고, convexity와 Hessian 경계로

\[
0\le R\le\frac{|\mathbf v|^2}{2a}
\]

를 얻는다. 실제 상쇄를 피해 평가할 수 있는 식도 구성했다.

\[
R=\frac{|\mathbf v|^2-(\beta_*\cdot\mathbf v)^2}
 {\mathcal H+a\gamma_*+\beta_*\cdot\mathbf v},\qquad
\Delta=e-\mathcal H=\frac t{\gamma_*}-R.
\]

분자는 작은 quadratic form이고, 현재 cube에서 분모는 큰 양의 합이다. 여기서 먼저 \(a\ge10^9\), \(|\mathbf v|<2701\) eV/H, \(R<1/250\) eV/H 및 \(\Delta>10\) eV/H를 얻는다. 부모의 monotone inverse를 적용하면 cube 전체에 유일한 양의 primitive가 존재하고,

\[
10<w<11\ {\rm eV/H},\qquad 45000<T<55000\ {\rm K}
\]

가 따른다. 이 순서는 중요하다. 아직 물리적임을 모르는 cube에서 rate의 미분 경계를 가정하는 순환을 피했다.

그 위에서 정확한 inverse differential을 유도했다. \(\Gamma=5/3,\kappa=2/3\), \(C=a+\Gamma w\), \(q_e=\Gamma w/C\)에 대해

\[
\ell=\frac{1-\kappa q_e|\beta|^2}{\gamma},\quad
s_a=\frac{1-(2/5)q_e|\beta|^2}{\gamma},\quad
k_m=1+\frac{2q_e}{5\gamma^2}
\]

이면

\[
\ell\,dw=\frac{dt}{\gamma_*}
 +(1/\gamma_*-s_a)da+(\beta_*-k_m\beta)\cdot d\mathbf m.
\]

Binding 변화와 속도 변화가 모두 남아 있다. 이 식과 \(dC=da+(5/3)dw\), \(n_H=D/\gamma\), 온도식, Doppler식을 결합해 다음 전구간 경계를 얻었다.

| Primitive 출력 | \(\|dX\|_\infty\le1\)당 유효 상계 |
|---|---:|
| \(|dw|\) | 0.26 eV/H |
| \(|dT|\) | 1400 K |
| \(\|d\beta\|_2\) | \(3\times10^{-6}\) |
| \(|d\gamma|\) | \(2\times10^{-7}\) |
| \(|dn_H|\) | \(1.33\times10^{-10}\ {\rm cm^{-3}}\) |
| \(|d\delta_q|\) | \(4\times10^{-6}\) |

Cube의 convexity에 따라 이 도함수 경계는 유한 변화에도 적용된다. 따라서 더 좁은 \(48600<T<51400\) K를 얻으며, 최저 cutoff 여유는 약 1.562527 eV이고 모든 gas-frame photon energy는 74 eV보다 작다. 출력 scaling을 명시한 7×7 normalized primitive inverse Jacobian의 infinity norm도 \(26/25\) 이하로 경계했다. 정확한 정의와 분수는 primitive 증명의 B33–B34 및 JSON에 있다.

## 6. 실제 rate 함수를 경계했다

현재 source의 함수와 decimal literal을 직접 사용했다. 예를 들어 CI는 \(\lambda_i=L_i/T\)에 대해

\[
k_i^{\rm CI}=A_iT^{-3/2}e^{-\lambda_i/2}
\frac{\lambda_i^{p_i}}{[1+(\lambda_i/c_i)^{r_i}]^{d_i}}
\]

이며, logarithmic derivative는

\[
\frac{d\log k_i^{\rm CI}}{d\log T}
=-\frac32-p_i+\frac{L_i}{2T}
+d_i r_i\frac{(\lambda_i/c_i)^{r_i}}{1+(\lambda_i/c_i)^{r_i}}
\]

다. 이 구간에서의 부호를 확인해 endpoint 감소·증가를 판정했다. RR와 두 DR도 source의 실제 함수와 kinetic-energy moment를 사용했다. 다음은 \([45000,55000]\) K 전체의 간단한 유리수 상계다.

| 과정 | \(\bar k\), cm³/s | \(\overline{|k'|}\), cm³/(s K) |
|---|---:|---:|
| CI HI → HII | \(10^{-9}\) | \(10^{-13}\) |
| CI HeI → HeII | \(4\times10^{-11}\) | \(7\times10^{-15}\) |
| CI HeII → HeIII | \(2\times10^{-14}\) | \(7\times10^{-18}\) |
| RR HII → HI | \(2\times10^{-13}\) | \(7\times10^{-18}\) |
| RR HeII → HeI | \(2\times10^{-13}\) | \(3\times10^{-18}\) |
| RR HeIII → HeII | \(10^{-12}\) | \(4\times10^{-17}\) |
| DR 첫 공명 | \(4\times10^{-14}\) | \(8\times10^{-18}\) |
| DR 둘째 공명 | \(2\times10^{-15}\) | \(5\times10^{-19}\) |

RR captured kinetic coefficient는 source가 정의하는 \(k_BT\alpha(3/2+g)\), \(g=d\log\alpha/d\log T\)다. 그 도함수에 \(dg/d\log T\)까지 포함했다. DR의 공명 energy도 source literal을 그대로 유지했다. 전체 kinetic·escape 계수와 도함수 표는 RATE_ENVELOPES에 있다.

Verner cross section은 active branch의 양의 factor를 구간별로 경계하고, 그 logarithmic derivative를 경계했다. \(\delta\in[19/20,20/19]\)라는 충분한 유리수 Doppler enclosure를 사용한다. HI·HeI·HeII 행과 23·35·70 eV 열에 대한 상계는

\[
\bar\sigma=\begin{pmatrix}
3\times10^{-18}&10^{-18}&2\times10^{-19}\\
0&8\times10^{-18}&2\times10^{-18}\\
0&0&2\times10^{-18}
\end{pmatrix}\ {\rm cm^2}
\]

다. 미분 상계와 threshold branch의 정확한 0도 함께 보존한다. 80자리 수치는 enclosure 후보를 제안하는 데만 사용했고, 실제 채택은 유리수 power의 정수 거듭제곱 비교와 exponential Taylor-tail 경계의 exact inequality로 결정했다. 실제 내부 witness는 rational-power bracket 76개와 exponential enclosure 5개다. 이 수를 독립 정리의 개수로 세지 않는다.

## 7. Photon 소거와 full source의 정확한 미분

\(b_q=1-\beta\cdot e_q\), \(\delta_q=\gamma b_q\), \(y=(1-\zeta_1,f-\zeta_2-\zeta_3,\zeta_2)\)라 하면

\[
\lambda_{iq}=cD y_i b_q\sigma_i(\delta_qE_q),\qquad
\Lambda_q=\sum_i\lambda_{iq}
\]

다. \(p_q^-=N_q^-/D\), \(s_q=S_q/D\), \(P_q(h)=p_q^-+hs_q\)에 대해

\[
p_q^+=\frac{P_q(h)}{1+h\Lambda_q},\qquad
R^\gamma_{iq}=\frac{\lambda_{iq}P_q(h)}{1+h\Lambda_q}
\]

로 정확히 소거한다. Candidate-state derivative는

\[
D_XR^\gamma_{iq}=P_q(h)\left[
\frac{D_X\lambda_{iq}}{1+h\Lambda_q}
-\frac{h\lambda_{iq}D_X\Lambda_q}{(1+h\Lambda_q)^2}
\right]
\]

이며, stage-parameter derivative는

\[
\partial_h(hR^\gamma_{iq})=
\lambda_{iq}\frac{p_q^-+2hs_q+h^2\Lambda_qs_q}{(1+h\Lambda_q)^2}.
\]

현재 \(s_q=0\)에서는 후자의 분자가 \(\lambda_{iq}p_q^-\)다. 이 분모의 derivative를 빼먹으면 coupled Jacobian과 continuation bound가 달라진다.

원자 과정의 per-H event rate는 \(R=D\gamma^{-2}e_Hyk(T)\)다. 그 도함수의 충분한 상계는

\[
L_R=D\left[(L_e\bar y+\bar eL_y+2\bar e\bar yL_\gamma)\bar k
+\bar e\bar y\overline{|k'|}L_T\right]
\]

이다. Proper density 두 개에 기인한 \(\gamma^{-2}\), electron closure, target abundance, 온도를 모두 포함한다.

Energy row에서는 새 affine 좌표가 정확한 상쇄를 만든다. \(K\)를 captured kinetic power per H, \(B_{\rm esc}\)를 RR/DR binding escape per H, \(\Gamma_*=-u_*\cdot u\), \(E_{q,*}=\gamma_*(1-\beta_*\cdot e_q)E_q\)라 하면

\[
\boxed{
S_t=\sum_{iq}(E_{q,*}-\chi_i)R^\gamma_{iq}
-\sum_i\chi_iR_i^{\rm CI}
-\Gamma_*K-(\Gamma_*-1)B_{\rm esc}.}
\]

RR/DR의 binding 변화와 escape의 단위 부분이 정확히 상쇄되어 마지막 항에 \(\Gamma_*-1\)만 남는다. 이 값은 단순 근사로 0으로 놓은 것이 아니다. 함께 쓰는 momentum row는

\[
\mathbf S_m=\sum_{iq}E_qe_qR^\gamma_{iq}
-\gamma\beta(K+B_{\rm esc})
\]

다. 모든 source row는 동일 endpoint의 사건을 공유한다.

## 8. 실제 H와 해의 오차·민감도

Scaled equation을 \(F(X,h)=X-hG_h(X)\)로 쓰고

\[
|G_{h,i}|\le b_i,\qquad \|D_XG_{h,i}\|_1\le\ell_i^{(0)}+H\ell_i^{(1)}
\]

를 구성했다. 아래 숫자는 실제 반환된 exact rational의 짧은 표시다. 기계 소비용 상계는 결과 JSON의 분수를 사용한다.

| Scaled row | \(b_i\), s⁻¹ | \(\ell_i(H)\), s⁻¹ | \(H b_i\) |
|---|---:|---:|---:|
| HII/H | \(1.6060877755\times10^{-9}\) | \(4.4956538109\times10^{-11}\) | 0.8030438877 |
| HeII/H | \(2.9154410165\times10^{-10}\) | \(1.4195176324\times10^{-11}\) | 0.1457720508 |
| HeIII/H | \(2.6428593109\times10^{-11}\) | \(1.2631340428\times10^{-12}\) | 0.01321429655 |
| Anchor energy | \(1.1249350252\times10^{-10}\) | \(3.4480668524\times10^{-12}\) | 0.05624675126 |
| 각 momentum 성분 | \(5.0127314520\times10^{-14}\) | \(6.9938056256\times10^{-16}\) | 0.00002506365726 |

\(B=\max b_i\), \(L(H)=\max\ell_i(H)\)에 대해 \(HB<1\)은 전체 cube의 strict self-map을, \(q=HL(H)<1\)은 uniform contraction을 보장한다. HII 행이 두 최대값을 정하며, 실제 선택은 \(H=500000000\) s다. 충분조건을 exact rational로 확인했으므로 경계에 가까운 float 비교에 결과를 맡기지 않았다.

해와 Jacobian에는

\[
|X_i(h)|\le hb_i,\qquad
\|(I-hD_XG_h)^{-1}\|_\infty\le\frac1{1-q}
=1.0229951604583454\ldots
\]

가 성립한다. 또한

\[
\left\|\frac{dX}{dh}\right\|_\infty
\le\frac{B}{1-q}
=1.6430200215866467\times10^{-9}\ {\rm s^{-1}}.
\]

이 branch에서는 \(|T-50000|\le1124.261442835519\ldots\) K라는 추가 enclosure를 얻는다. Photon inventory도 항상 양수이며, 각 node에 \(p_q^-/(1+H\bar\Lambda_q)\le p_q^+\le p_q^-\)가 성립한다.

정확한 arithmetic의 Picard map \(X_{k+1}=hG_h(X_k)\), \(X_0=0\)에는

\[
\|X(h)-X_k\|_\infty\le\frac{q^k}{1-q}HB
\]

가 성립한다. **8회 update의 이론 오차상계**는 약 \(5.3544613\times10^{-14}\)이며 \(10^{-12}\)보다 작다. 실제 iteration을 실행한 횟수가 아니다. Native corrector가 이 결과를 소비하려면 primitive/provider/rounding의 오차를 포함해야 한다.

한편 cube 안의 근사값 \(\widetilde X\)에 대해

\[
\|X-\widetilde X\|_\infty\le
\frac{\|F(\widetilde X,h)\|_\infty}{1-q}
\]

이므로, 실제 잔차를 엄밀히 경계할 수 있는 구현은 그 값을 직접 error certificate로 연결할 수 있다. H는 충분한 존재 구간이며 최대 허용 step이나 integration accuracy optimum을 뜻하지 않는다.

## 9. 다음 구간으로 이어 가는 구성

다음 단계의 predictor \(\bar X(h)\), 양의 성분 반경 r, 고정 가역 approximate inverse A를 택한다. Parameter 구간 전체의 tube에서

\[
Y\ge|AF(\bar X(h),h)|,\qquad
Z\ge|I-A D_XF(X,h)|
\]

를 성분별로 경계하면

\[
\boxed{Y+Zr<r,\qquad
\max_i\frac{(Zr)_i}{r_i}<1}
\]

이 전체 tube 안의 \(C^1\) 해 가지를 인증한다. Jacobian 경계는 중심 한 점이나 유한 sample이 아닌 tube 전체에서 유효해야 한다. 인접 tube를 잇는 데에는 한 endpoint enclosure가 상대 uniqueness box에 포함되거나, 양쪽에 들어가는 공통 root enclosure가 있어야 한다.

유한한 **비연장 최대 끝점**도 명확히 정리했다. 가지가 smooth physical domain의 compact 부분에 머물고 inverse Jacobian이 균일 유계이면, \(X'=-F_X^{-1}F_h\)가 유계여서 끝점 극한이 존재하고 IFT로 더 연장된다. 따라서 비연장 끝점은 그 compact domain에서의 이탈 또는 inverse Jacobian 유계성 상실과 함께 온다. 특정 상계 부등식의 실패는 그 자체로 물리적 해 가지의 종료를 뜻하지 않는다.

이번 실제 인증은 하나의 cube에서 [0,H] 전체를 덮는다. H를 넘어서는 다중 predictor tube chain과 fold를 통과하는 pseudo-arclength 수치 인증은 다음 이론 구성으로 남겼다.

## 10. 실제 Wolfram·xAct 검증과 독립 검토

| 실행 묶음 | 이번 최종 결과 | 실제 확인한 내용 |
|---|---:|---|
| Primitive exact batch | 17/17 groups PASS | 새 항등식 7개와 전체 cube 경계 산술 10개 |
| FT03/Verner batch | 20/20 groups PASS | 실제 함수 도함수, 전구간 monotonicity/positivity, 계수·energy·Doppler 상계 |
| Full-source certificate | 12/12 groups PASS | photon/parameter derivative와 affine source 4개 잔차 0, 실제 H·self-map·contraction·guard·오차경계 |
| 실제 xAct batch, 최종 v2 | 8/8 groups PASS, tensor residual 17개 모두 0 | projector·rest-ray direction·고정 Eulerian current·stress variation·anchor energy와 escape projection |

총 **57 named check groups**다. xAct 안의 residual 17개를 17개 group으로 바꾸어 더하지 않는다. 서로 다른 scalar/tensor 표현의 교차 검산이 있으므로 이 수를 57개의 독립 정리로 해석하지 않는다. 실제 evaluator call은 5회로, 최초 xAct 입력의 실패 1회를 포함한다. Native build/test, chemical RHS, ODE/history 실행은 모두 0이다.

xAct는 실제 Wolfram kernel에서 공식 archive의 SHA256 guard를 거친 뒤 xTensor 1.3.0을 로드했다. 최종 출력에는 Wolfram Language 15.0.1, xTensor loaded/version 및 xPerm external backend disabled가 들어 있다. Formal variation vector에 정규화의 1·2차 미분 조건을 부여하고 tensor contraction/canonicalization을 실제 수행했다. ParamD가 모든 식을 자동 유도했다고 주장하지 않는다.

관측한 문제도 결과에서 분리해 보존했다.

- 첫 xAct 시도는 free/dummy index 충돌이 있는 helper 표현 때문에 완결된 결과를 반환하지 못했다. 같은 Doppler 미분을 명시적인 projection scalar로 표현한 v2가 최종 8개 group을 통과했다. 실패 입력·원응답을 유지한다.
- Rate batch의 마지막 metadata append에는 `AssociateTo` 인자 오류가 관측됐다. 성공한 20개 과학 결과는 완전하게 반환됐으며 kernel 시간·버전 누락은 null로 기록했다. xAct wrapper에도 같은 입력 형식 문제가 있지만 그 원응답에는 해당 warning이 없었다. xAct의 수신되지 않은 추가 hash·runtime metadata를 추정하지 않았다.
- Combined batch의 긴 JSON은 도구가 중간을 생략했다. Exact H/HB/q, 7행 b/ell0/ell1/ellH, 12개 판정 및 summary는 수신됐다. 생략된 네 개의 중복 scalar exact field를 null로 남기고, raw 및 정규화 절차를 함께 보존했다.

성공한 과학 계산을 기록 형식만 고치기 위해 재실행하지 않았다. Primitive와 full-source의 수신된 kernel 시간은 각각 0.068243 s와 0.00676 s다. 나머지 runtime을 여기서 역으로 추정하거나 tool wall time과 섞지 않는다.

독립 reviewer는 저자 계산을 실행하거나 수정하지 않은 채 가정·유도·actual input/raw/result를 읽는다. 중간 검토에서 최대 끝점의 양화와 몇 개의 literal 수식 표기 교정을 요청했고 해당 문구만 수정했다. 최종 판정과 읽은 파일 identity는 [DECISION](../review/DECISION.json) 및 manifest에 고정한다.

## 11. 원전과 이번 기여의 관계

SciSpace와 Exa를 실제 사용해 필요한 표준 구성의 원전을 읽었다. Exa는 4개 query, 요청 result slot 20개와 서로 다른 URL 19개를 반환했고, SciSpace는 1개 query에서 10개 paper entry를 반환했다. 실제 정리 본문을 읽은 원전은 다음 3편의 지정 절이다. 검색 항목 수와 원전 읽기 수를 구분했다.

| 원전 | 이번 적용 |
|---|---|
| [Day–Lessard–Mischaikow (2007), Theorem 2.1](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf) | 성분 scaling을 가진 residual·contraction 인증 |
| [van den Berg–Lessard–Mischaikow (2010), Lemmas 5/7, Proposition 8](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf) | parameter tube의 uniform certificate와 인접 root의 nesting 연결 |
| [Rump (1995), §3](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf) | approximate inverse 및 interval inclusion의 전제·결론 범위 |

일반 fixed-point/continuation 도구는 이 원전에 귀속한다. 이번 새 결과는 현재 moving H/He conservative map에 대한 affine 물리 cube, actual FT03/Verner derivative 연결, 모든 retained channel의 구체적 상계 및 H를 구성한 것이다. 원래 gamma-law cone 정리와 opacity/covariant exchange 문헌은 부모의 승인된 근거를 재사용한다. 문헌 전체를 읽었다거나 제한된 검색으로 전역 신규성·부재를 증명했다고 주장하지 않는다. 상세 scope와 query provenance는 [LITERATURE_MAP](../review/LITERATURE_MAP.md), SEARCH_EVIDENCE, SOURCE_EVIDENCE에 있다.

## 12. 코딩 연결과 다음 연구 의무

기존 owner DAG인 **RUX02 + global RUX03 → RUX04 → RUX05**를 보존한다. `all-Bianchi / abundance-source / reference-current / class-B / relative-species-tilt D2.3`는 별도 의무다. 이번 local moving-source certificate로 전체 cosmological branch를 완료 처리하지 않는다.

기존 coding pending은 다음 세 노드에 남는다.

- `HERE_RUX03_PRIMARY_PROVIDER_03`: 실제 공통 provider/event consumer 연결.
- `HERE_RUX03_COVARIANT_MOMENTS_04`: same-event energy·momentum moment 연결.
- `HERE_RUX03_MOVING_GAS_STAGE_05`: primitive inverse·eliminated photon·7변수 stage의 실제 구현과 검증.

이번 결과는 여기에 `HERE_RUX03_CONTINUATION_CERTIFICATE_ADAPTER_06`을 연결한다. Exact chart와 scale, source identity, primitive/rate enclosure, H와 q, residual/rounding budget, tube/nesting record를 같은 입력 계약으로 전달해야 한다. 구체적인 입력/출력·실패 처리·완료 증거는 [CODING_CONTRACT.md](CODING_CONTRACT.md)에 있다.

다음 이론 노드는 **`HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07`**로 정했다. 먼저 고정 old-state의 현재 h-branch에서 full Jacobian preconditioner와 predictor tube를 구성하고, 공통 root enclosure로 두 구간을 실제 연결해야 한다. 그 뒤 old-state 자체를 작은 물리 family로 확장해 reanchoring과 오차의 균일 의존성을 증명한다. 첫 단계는 하나의 명시적 full-rate tube pair와 exact/outward inequalities를 제시하는 것이다. 일반 정리만 반복해서 이 노드를 완료 처리하지 않는다.

이 루프에는 새 strong no-go 후보나 채택이 없다. 아직 구성하지 않은 tube chain이나 아직 실행하지 않은 native stage를 불가능성 결론으로 바꾸지 않았다. 현재까지 실제로 닫힌 것은 명시한 cube에서의 [0,H] 해 가지, 그 정량 경계와 다음 구성의 수학적·구현 계약이다.
