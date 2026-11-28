# THEORY06 후속 구현 계약

**단위:** `HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06`  
**작성 상태:** `author_complete` — 이 문서는 증명 저자의 구현 인계 기록이다. 최종 채택 여부와 범위는 `../review/DECISION.json`에 둔다.  
**현재 실행 범위:** 정해진 유리수·해석식에 대한 Wolfram/xAct 이론 검산. 이 문서를 작성하면서 추가 과학 계산을 수행하지 않았으며, 이번 THEORY06의 native 구현·빌드·화학 RHS·ODE·Picard 반복 실행은 모두 **0회**다.

이 계약의 구현 목표는 전체 CI/RR/두 DR/일차 광흡수 사건을 사용하는 7변수 moving-gas backward-Euler(BE) 단계에 **물리 영역 포함 증명, 전 영역 미분 상계, 매개변수 연속 추적 인증**을 붙이는 것이다. 다음 세 구현 owner의 pending 상태를 유지한다.

| 선행 owner | 먼저 갖출 출력 | THEORY06이 소비할 경계 |
|---|---|---|
| `PRIMARY_PROVIDER_03` | 실제 FT03/Verner 값과 같은 광자 종말점에서 만든 일차 사건·에너지 장부 | 원시 사건, 포획 운동에너지, binding/escape 소유권과 미분 |
| `COVARIANT_MOMENTS_04` | 방향을 보존한 광자 에너지·운동량·압력 모멘트 | 같은 흡수 사건의 전체 광자 에너지와 \(E/c\) 운동량 |
| `MOVING_GAS_STAGE_05` | 고정 Eulerian 체적의 보존형 7개 잔차, 물리 primitive 회복 | \(D\) 고정, lab 에너지·운동량, 등방적인 gas-frame escape의 Lorentz 변환 |
| 이 문서의 continuation adapter | 정확한 affine 좌표, 값/JVP/구간 상계, 국소 및 tube 인증 | 위 세 owner의 실제 production 경로를 소비하고 인증 범위를 출력 |

새 adapter의 ID는 `HERE_RUX03_CONTINUATION_CERTIFICATE_ADAPTER_06`이다. 기존 owner 구현을 완료한 것으로 간주하지 않는다. 같은 사건을 공유하는 경계에 추가하며, 원래 DAG의 미완료 노드를 유지한다. 근거는 [과학 계약](SCIENTIFIC_CONTRACT.md), [전체 source 증명 S1–S34](../derivations/FULL_SOURCE_CONTINUATION_CERTIFICATE.md), [명시적 \(H\) 인증 해설 C1–C12](../derivations/EXPLICIT_H_CERTIFICATE.md)이다.

## 1. 입력, 단위와 정규화

고정 local Eulerian tetrad, 고정 lab 체적, 계량 부호 \((-+++)\)의 homogeneous source substep을 사용한다. 한 인증에서 \(D=\gamma n_H\), \(f=n_{\rm He}/n_H\), 중성 기준질량, anchor, lab 광자 방향·에너지, 이전 단계 광자 수를 고정한다. \(h\)는 이 동일한 이전 상태에서 출발하는 BE 단계의 **lab 시간 매개변수**다.

| 기호 | 정의 및 단위 | 실제 호출 경계 |
|---|---|---|
| \(D\), \(n_H\) | 각각 lab 및 gas-frame H 핵수 밀도, \(\mathrm{cm^{-3}}\); \(n_H=D/\gamma\) | 후보 속도가 변하면 proper \(n_H\)도 갱신 |
| \(\zeta\) | \((n_{\rm HII},n_{\rm HeII},n_{\rm HeIII})/n_H\) | 세 성분 모두 H당 수; He 성분을 He당 fraction과 혼동하지 않음 |
| \(\epsilon\) | \(1.602176634\,10^{-12}\ \mathrm{erg/eV}\) | 에너지 단위 변환을 한 번만 적용 |
| \(\chi\) | \((13.598434599702,24.587389011,54.41776)\ \mathrm{eV}\) | binding ledger 값 |
| \(B(\zeta)\) | \(\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3\), eV/H | \(dB=(\chi_0,\chi_1,\chi_1+\chi_2)\cdot d\zeta\) |
| \(\mu,a,w\) | \(\mu=m_{\rm ref}c^2/\epsilon\), \(a=\mu+B\), thermal \(w\), 모두 eV/H | EOS는 \(\rho=n_H\epsilon(a+w)\), \(p=(2/3)n_H\epsilon w\) |
| \(E,\mathbf M\) | lab gas 에너지 밀도, \(c\)를 곱한 lab 운동량 밀도; 모두 \(\mathrm{erg\,cm^{-3}}\) | 물리 운동량 밀도는 \(\mathbf M/c\) |
| \(e,\mathbf m\) | \(E/(D\epsilon)\), \(\mathbf M/(D\epsilon)\), eV/H | 잔차 scaling의 보존형 에너지·운동량 |
| \(E_q,\mathbf e_q,N_q\) | lab 광자 에너지 eV, 단위 방향, lab 광자 수 밀도 \(\mathrm{cm^{-3}}\) | \(N_q\)에 이미 포함된 node 적분 weight를 다시 곱하지 않음 |
| \(S_q,p_q,s_q\) | lab 광자 공급 \(\mathrm{cm^{-3}s^{-1}}\), \(N_q/D\), \(S_q/D\) | 이 인증의 실제 공급은 \(S_q=0\) |
| \(R_c\) | proper 사건률 \(R'_c\)를 \(D\)로 나눈 값, H당 \(\mathrm{s^{-1}}\) | 추가적인 lab-time \(1/\gamma\)를 곱하지 않음 |

사건률의 조성 인자는
\[
y=(1-\zeta_1,\ f-\zeta_2-\zeta_3,\ \zeta_2),\qquad
v=(\zeta_1,\zeta_2,\zeta_3),\qquad
e_H=\zeta_1+\zeta_2+2\zeta_3,\qquad d=1+f+e_H.
\]
따라서 \(n_e=n_H e_H\), \(w=(3k_B/2\epsilon)dT\)다. 기존 `HHeState.fractions` 형식을 호출할 때는 \((\zeta_1,\zeta_2/f,\zeta_3/f)\)로 변환하고, 해당 호출의 proper gas 밀도를 \(D/\gamma\), \(fD/\gamma\)로 설정한다. 기존 고정 gas 밀도 또는 기존 fraction derivative를 moving-gas 잔차에 그대로 넣지 않는다. 실제 raw 사건과 포획 운동에너지를 읽고 위 정규화로 source를 조립한다.

인증 fixture는 다음과 같다. 이는 수학 인증을 위해 선언한 입력이며 이전 production interval dataset을 교체하지 않는다.

- \(D=10^{-3}\ \mathrm{cm^{-3}}\), \(f=2/25\), \(\zeta_*=(1/2,1/50,1/50)\), \(T_*=50000\ \mathrm K\).
- \(\boldsymbol\beta_*=(0,0,41/841)\), \(\gamma_*=841/840\), \(\mu\in[10^9,1.5\,10^9]\ \mathrm{eV/H}\). 한 단계 안에서는 \(\mu\)를 고정하며 상계는 이 전체 구간에 균일하다.
- 여섯 실제 방향 node: \(23\ \mathrm{eV}\)의 \(\pm\mathbf e_x\), \(35\ \mathrm{eV}\)의 \(\pm\mathbf e_y\), \(70\ \mathrm{eV}\)의 \(\pm\mathbf e_z\). 각 \(p_q^-=1/100\), \(s_q=0\).
- \(w_*=2830330450/267029439\ \mathrm{eV/H}\). \(\Gamma=5/3\), \(\kappa=2/3\)로 두면 \(\mathbf m_*=(a_*+\Gamma w_*)\gamma_*\boldsymbol\beta_*\)다.

일반 3차원 속도 변화가 포함된 cube이므로 각 node의 실제 방향을 유지해야 한다. 기존 광자 방향의 극각 cosine node에 대한 방위각 평균 ring은 속도가 축 방향일 때 정확히 축약되며, 횡방향 속도까지 받는 API에는 방향별 ray 또는 명시적인 방위각 적분이 필요하다. 기존 reference-volume/per-H 데이터에서 입력을 옮길 때는 `PRIMARY_PROVIDER_03` 계약에 따른 변환을 한 번 수행한 뒤 이 고정 lab-volume 정규화로 진입한다.

## 2. 정확한 affine 좌표와 큰 기준 에너지의 정밀도

다음 변환은 anchor를 고정했을 때 정확하고 가역적인 affine 변환이다.
\[
t=\gamma_*(e-\boldsymbol\beta_*\cdot\mathbf m)-a,\qquad
z=(\zeta,t,\mathbf m),\qquad
e=\frac{t+a}{\gamma_*}+\boldsymbol\beta_*\cdot\mathbf m.
\]
\(t_*=w_*\)이지만 일반 후보에서는 \(t=w\)가 아니다. 특히 anchor에서 \(D\)를 고정한 미분도
\[
dt=dw+\frac{2}{3}\frac{w}{\gamma}\,d\gamma
\]
를 포함한다. 가변 속도에서 이 압력·밀도 기여를 삭제하면 부모의 7개 보존형 방정식과 달라진다.

Scaling은
\[
H_s=\operatorname{diag}(10^{-3},10^{-3},10^{-3},1/4,s_m,s_m,s_m),\qquad
s_m=a_*10^{-6},\qquad X=H_s^{-1}(z-z_*),\quad\|X\|_\infty\le1.
\]
실행 시 실제 \(s_m\)를 사용한다. 검산 코드에서 momentum 상계에 사용한 분모 \(1000\)은 \(\mu\) 전체 구간에서 성립하는 **\(s_m\ge1000\ \mathrm{eV/H}\)의 보수적 하한**이다. 이를 실제 chart의 \(s_m\)를 바꾸는 값으로 해석하지 않는다.

원래 보존형 잔차를 같은 상수 affine 행 변환과 \(H_s^{-1}\)로 변환하면
\[
F(X,h)=X-hG_h(X),\qquad G_h=H_s^{-1}S(z_*+H_sX,h)
\]
가 된다. 새 thermal 진단을 여덟 번째 solve equation으로 추가하지 않는다. chart를 고정한 동안 변환에는 시간 적분 보정항이 생기지 않는다.

**재좌표화할 때의 이전 상태.** 위 fixture에서는 chart center가 이전 상태이므로 \(X_{\rm old}=0\)이다. 같은 물리적 이전 상태를 유지하면서 다른 고정 anchor 또는 center로 옮기면 그 이전 상태도 새 affine chart로 변환하여
\[
F_{\rm new}(X_{\rm new},h)
=X_{\rm new}-X_{{\rm old,new}}-hG_{{\rm new},h}(X_{\rm new})
\]
를 사용한다. 일반적으로 \(X_{{\rm old,new}}\ne0\)이며 이를 0으로 지우면 source 초기값 문제 자체가 바뀐다. 한 certificate 안에서는 chart와 scale을 고정한다. \(h\)-dependent chart를 채택할 경우에는 \(\partial_h\)에 좌표변환과 변환된 이전 상태·scale의 미분까지 포함하여 별도로 유도해야 하며, 이 문서의 고정-chart 매개변수 미분을 그대로 사용하지 않는다. 이 표현 의무는 8절의 같은 이전 상태를 가진 tube 연결에 적용되며, 실제 다음 timestep에서 입력 상태를 갱신하는 작업과 구별한다.

**표현 계약.** \(e\)에는 \(10^9\ \mathrm{eV/H}\) 수준의 rest baseline이 있다. 반복 상태와 직렬화에는 가능한 한 \(t,\zeta,\Delta\mathbf m\) 또는 baseline과 increment를 분리한 표현을 보존한다. 다음 increment 식을 직접 쓴다.
\[
\Delta e=\frac{\Delta t+\Delta B}{\gamma_*}+\boldsymbol\beta_*\cdot\Delta\mathbf m,\qquad
\Delta t=\gamma_*(\Delta e-\boldsymbol\beta_*\cdot\Delta\mathbf m)-\Delta B.
\]
큰 \(e\)를 매번 재구성한 뒤 \(a\)와 뺄셈하여 \(t\)를 얻는 경로를 기본 solve 경로로 삼지 않는다. 이미 단일 부동소수점 \(E\)로 반올림된 입력의 열적 정보를 후속 보상 합만으로 되찾을 수는 없다. 필요한 입력 정확도는 split 입력, 더 높은 정밀도 또는 입력 구간과 오차 전파로 확보하고 기록한다. FMA·보상 합·정밀 primitive 회복의 사용 자체가 오차 보증은 아니며, 실제 error enclosure를 최종 예산에 포함한다.

## 3. Provider 호출 전에 물리 포함을 확보한다

[Primitive 회복 및 미분 증명](../derivations/PRIMITIVE_DIFFERENTIAL_BOUNDS.md)이 닫힌 unit cube 전체를 물리 영역에 포함시킨다. 구현은 이 증명의 가정과 입력 범위를 먼저 확인한 뒤 rate/JVP 상계를 소비한다.

큰 rest-energy 차이를 안정적으로 평가하려면
\[
\mathbf u_*=\gamma_*\boldsymbol\beta_*,\quad
\mathbf v=\mathbf m-a\mathbf u_*
=\Delta\mathbf m+(\Gamma w_*-\Delta B)\mathbf u_*,\quad
H_c=\sqrt{a^2+|\mathbf m|^2}
\]
와
\[
R=H_c-\frac a{\gamma_*}-\boldsymbol\beta_*\cdot\mathbf m
=\frac{|\mathbf v|^2-(\boldsymbol\beta_*\cdot\mathbf v)^2}
 {H_c+a\gamma_*+\boldsymbol\beta_*\cdot\mathbf v},\qquad
0\le R\le\frac{|\mathbf v|^2}{2a}
\]
를 사용한다. 정확한 cold-cone gap은
\[
e-H_c=\frac t{\gamma_*}-R>0
\]
이다. 이 우변의 검증된 양의 하한을 사용하면 큰 두 수의 직접 뺄셈을 피할 수 있다.

고정 \(a,\mathbf m\)의 scalar primitive 회복은
\[
C=a+\Gamma w,\quad \mathbf u=\mathbf m/C,\quad
\gamma=\sqrt{1+|\mathbf u|^2},\quad\boldsymbol\beta=\mathbf u/\gamma,\quad
\Gamma_{\rm rel,*}=\gamma_*\gamma-\mathbf u_*\cdot\mathbf u
\]
를 이용해
\[
t=w+C(\Gamma_{\rm rel,*}-1)+\kappa w(1-\gamma_*/\gamma)
\]
의 \(w\)를 구하는 것으로 구현할 수 있다. cube에서 양의 bracket \(10<w<11\ \mathrm{eV/H}\)가 증명되며 이 scalar 식은 엄격히 증가한다. 작은 상대 속도에서는
\(\Gamma_{\rm rel,*}-1=(|\mathbf u-\mathbf u_*|^2-(\gamma-\gamma_*)^2)/2\)와
\(\gamma-\gamma_*=(\mathbf u-\mathbf u_*)\cdot(\mathbf u+\mathbf u_*)/(\gamma+\gamma_*)\)
를 사용해 상대 Lorentz factor의 작은 초과분을 보존할 수 있다. 실제 사용 표현의 반올림 오차도 primitive enclosure에 포함한다.

| 전체 cube에서 소비 가능한 guard | 증명된 범위 또는 상계 |
|---|---|
| 조성 | \(\zeta_1\in[.499,.501]\), \(\zeta_{2,3}\in[.019,.021]\), HeI/H \(\in[.038,.042]\) |
| 온도와 속도 | \(45000\le T\le55000\ \mathrm K\), \(\lVert\boldsymbol\beta\rVert_2\le49/1000\), \(\gamma\le501/500\) |
| 공급자 외부 domain | 실제 FT03 \(30000\le T\le110000\ \mathrm K\); Verner \(0\le E'_q\le50000\ \mathrm{eV}\) |
| 단위 \(\|dX\|_\infty\)당 \(T,\beta,\gamma\) | \(L_T=1400\ \mathrm K\), \(L_\beta=3\,10^{-6}\), \(L_\gamma=2\,10^{-7}\) |
| \(n_H,\delta_q\) | \(L_{n_H}<1.33\,10^{-10}\ \mathrm{cm^{-3}}\), \(L_\delta\le4\,10^{-6}\), \(\delta_q=\gamma(1-\beta\cdot e_q)\) |
| 여섯 transformed photon energy | 모두 \(74\ \mathrm{eV}\) 미만; 각 관련 cutoff에서 거리가 \(1.5\ \mathrm{eV}\)보다 큼 |

이 fixture의 \(23\) eV node는 HI만, \(35\) eV node는 HI/HeI, \(70\) eV node는 세 흡수체 모두 활성인 고정 smooth cell에 남는다. Verner cutoff \(13.60/24.59/54.42\ \mathrm{eV}\)를 binding \(\chi\)로 치환하지 않는다. 구간이 cutoff를 가로지르는 새 입력에는 이 smooth-cell certificate를 그대로 쓰지 않고 cell을 분할하거나 그 입력에 맞는 새 정칙성·상계를 구성한다.

### 3.1 같은 primitive inverse의 JVP

후보값을 회복한 뒤 조성 의존성을 포함한 아래 미분을 사용한다. \(\theta=\Gamma w/C\)로 두고
\[
\ell=\frac{1-\kappa\theta|\beta|^2}{\gamma},\quad
s_a=\frac{1-\tfrac25\theta|\beta|^2}{\gamma},\quad
k_m=1+\frac{\tfrac25\theta}{\gamma^2}
\]
이면
\[
dw=\frac{dt/\gamma_*+(1/\gamma_*-s_a)\,dB
       +(\boldsymbol\beta_*-k_m\boldsymbol\beta)\cdot d\mathbf m}{\ell},\quad
\ell^{-1}<501/500.
\]
그 뒤
\[
dC=dB+\Gamma dw,\quad d\mathbf u=(d\mathbf m-\mathbf u\,dC)/C,\quad
 d\gamma=\boldsymbol\beta\cdot d\mathbf u,\quad
 d\boldsymbol\beta=(I-\boldsymbol\beta\boldsymbol\beta^T)d\mathbf u/\gamma,
\]
\[
dn_H=-D\,d\gamma/\gamma^2,\qquad
dT=\frac{2\epsilon}{3k_B}\left(\frac{dw}{d}-\frac{w\,dd}{d^2}\right),\quad
dd=d\zeta_1+d\zeta_2+2d\zeta_3,\quad
d\delta_q=(\boldsymbol\beta-\mathbf e_q)\cdot d\mathbf u
\]
를 전파한다. \(dB\), \(dd\), \(dn_H\) 중 하나를 누락한 JVP는 같은 7변수 잔차의 미분이 아니다. 이 식의 계수와 remainder를 전체 입력 box에서 감싸야 하며, 한 점의 정확한 Jacobian만으로 전체 box의 역행렬·Lipschitz 상계를 대신하지 않는다.

## 4. 실제 사건 provider와 공통 에너지 장부

선정된 source는 `rei_bianchi` PR114 head `a5c958c414dea41216b445c05f58df837f05cacb`의 다음 함수다. [정확한 source와 위치](../source_map/SOURCE_FUNCTIONS.md), [현재 identity](../source_map/CURRENT_SOURCE.json), [전체 온도·에너지 구간의 상계](../derivations/RATE_ENVELOPES.md)를 함께 소비한다.

| 경계 | 소비할 실제 값 | 단위와 소유권 |
|---|---|---|
| `ft03_rates::ft03_coefficients` | CI 3개, RR 3개, DR 2개 | 각 계수 \(\mathrm{cm^3\,s^{-1}}\) |
| 같은 FT03 반환값 | `rr_kinetic_erg_cm3_s[3]`, `dr_energy_erg[2]` | RR 포획 운동에너지 계수, 각 DR 사건의 포획 에너지 |
| `ft03_controlled::ft03_rhs`의 사건 분해 | 3 CI, 3 RR, **HeII→HeI인 두 DR**, PI, escape | 사건 target와 binding/kinetic 귀속의 기존 정의 |
| `AtomicProvider::cross_section` | 실제 Verner 값과 해당 smooth cell의 도함수 | 입력 \(E'_q=\delta_qE_q\)는 eV; 출력 \(\mathrm{cm^2}\) |

`AtomicProvider::raw_coefficient`의 Grackle reference 계수를 FT03 대신 사용하지 않는다. 신규 point/JVP/interval 인터페이스가 동일한 source 정의를 공유해야 한다. 구간 callback은 source literal, 거듭제곱·지수·제곱근, 미분의 해석적 범위를 outward enclosure로 감싼다. native의 `powf`/`exp` 결과와 derivative 구현의 반올림까지 포함하는 증거를 별도로 마련한다.

Collisional 사건은
\[
R_c=D\gamma^{-2}e_Hy_c k_c(T)=R'_c/D
\]
다. CI에는 \(y\), RR에는 \(v\), 두 DR에는 모두 \(v_1=\zeta_2\)를 사용한다. 여기서 \(v_1\)의 첨자 1은 0부터 센 HeII target다. 두 DR를 하나로 합치려면 각각의 계수와 포획에너지가 동일하게 반영되는 명시적 합을 사용한다.

\(K\)를 RR 및 두 DR의 proper 포획 운동에너지 합을 \(D\epsilon\)으로 나눈 값, 그리고
\[
B_{\rm esc}=\sum_i\chi_iR_{{\rm RR},i}+\chi_1(R_{{\rm DR},1}+R_{{\rm DR},2})
\]
로 둔다. 둘 다 \(\mathrm{eV\,H^{-1}\,s^{-1}}\)이다. gas-frame 총 escape는 \(D\epsilon(K+B_{\rm esc})\); lab energy source에는 \(\gamma\), \(c\)를 곱한 momentum source에는 \(\gamma\beta\)를 반영한다. 이를 새로운 photon spectrum이나 photon number로 분해할 필요는 없다.

입사 사건 incidence는
\(\nu_0=(1,0,0),\nu_1=(0,1,0),\nu_2=(0,-1,1)\)이고
\[
S_\zeta=\sum_i
\nu_i\left(\sum_qR_{\gamma,iq}+R_{{\rm CI},i}-R_{{\rm RR},i}\right)
-\nu_1(R_{{\rm DR},1}+R_{{\rm DR},2}).
\]
같은 사건으로 조립하는 나머지 네 source는 정확히
\[
S_t=\sum_{iq}(E_{q,*}-\chi_i)R_{\gamma,iq}
-\sum_i\chi_iR_{{\rm CI},i}
-\Gamma_{\rm rel,*}K-(\Gamma_{\rm rel,*}-1)B_{\rm esc},
\]
\[
S_{\mathbf m}=\sum_{iq}E_q\mathbf e_qR_{\gamma,iq}
-\gamma\boldsymbol\beta(K+B_{\rm esc}),\qquad
E_{q,*}=\gamma_*(1-\boldsymbol\beta_*\cdot\mathbf e_q)E_q.
\]
이 \(S_t\)는 lab energy/momentum 및 조성 잔차의 정확한 affine 행 조합이다. RR/DR의 binding cancellation을 이 식으로 보존하고, 별도 thermal 계산에서 같은 binding을 재차 빼지 않는다. 부모 THEORY05의 유한 단계 에너지·운동량·binding 장부와 thermal correction은 해의 진단식으로 유지한다.

## 5. 동일 종말점 광자 소거와 두 종류의 미분

각 candidate의 primitive에서
\[
b_q=1-\boldsymbol\beta\cdot\mathbf e_q,\qquad
\lambda_{iq}=cD\,y_i b_q\sigma_i(E'_q),\qquad
\Lambda_q=\sum_i\lambda_{iq}
\]
를 구한다. candidate-independent 비음수 공급을 일반화한 식은
\[
P_q=p_q^-+hs_q,\qquad
p_q^+=\frac{P_q}{1+h\Lambda_q},\qquad
R_{\gamma,iq}=\frac{\lambda_{iq}P_q}{1+h\Lambda_q}
\]
다. 이번 수치 인증은 \(s_q=0\)만 소비한다. 소거식·비음수 구조는 기존 이론에서 재사용하며, 새 부분은 이 전체 source와 같은 endpoint derivative의 정량 상계다.

**소유권과 반환값.** 하나의 endpoint evaluation이 \(p^+\), 모든 \(\lambda_i,\Lambda\), 모든 \(R_{\gamma,iq}\), 그리고 그 미분을 반환하게 한다. 흡수 수 \(hD R_{\gamma,iq}\)를 species, 전체 광자 에너지, 운동량과 잔차에 그대로 공유한다. provider의 기존 pre-stage birth를 이미 \(p^-\)에 더했다면 새 \(hs\) numerator에서 다시 넣지 않는다. 공급을 넣는 owner는 한 번만 선택해 receipt에 기록한다.

\(h\) 고정 candidate JVP는
\[
D_Xp_q^+=-\frac{hP_qD_X\Lambda_q}{(1+h\Lambda_q)^2},\qquad
D_XR_{\gamma,iq}=P_q\left[\frac{D_X\lambda_{iq}}{1+h\Lambda_q}
-\frac{h\lambda_{iq}D_X\Lambda_q}{(1+h\Lambda_q)^2}\right].
\]
반드시
\[
D_X\lambda_{iq}=cD\left[
(D_Xy_i)b_q\sigma_i-y_i(\mathbf e_q\cdot D_X\boldsymbol\beta)\sigma_i
+y_ib_q\sigma_i'(E'_q)E_qD_X\delta_q\right]
\]
를 포함한다. opacity, \(n_H\), \(T\), Doppler energy를 이전값에 동결하면 다른 residual/Jacobian을 계산하게 된다. inactive cell은 \(\sigma_i=\sigma'_i=0\)로 처리한다.

\(X\) 고정 매개변수 미분은 별도 반환한다.
\[
\partial_h p_q^+=\frac{s_q-p_q^-\Lambda_q}{(1+h\Lambda_q)^2},\qquad
\partial_h(hR_{\gamma,iq})=\frac{\lambda_{iq}[p_q^-+2hs_q+h^2\Lambda_qs_q]}
{(1+h\Lambda_q)^2}.
\]
즉 \(\partial_h(hG_h)\)는 단순히 \(G_h\)가 아니다. \(s=0\)에서도 소거 denominator의 미분이 남는다. 위 식은 \(p^-\), \(s\), geometry가 이 미분에서 고정이라는 계약을 전제로 한다. 상태나 \(h\)에 추가로 의존하는 공급을 허용할 때는 그 미분과 상계를 별도로 추가한다.

분모는 \(1+h\Lambda\ge1\)이고 위 표현은 \(\Lambda=0\)에서도 정의된다. 총 opacity로 나누어 species allocation을 계산한 뒤 0/0을 보정하는 경로가 필요 없다. \(\sum_i hR_{\gamma,iq}=p_q^-+hs_q-p_q^+\)라는 유한 수 장부를 같은 반환값으로 검사한다.

## 6. 실제 유리수 certificate를 소비하는 방법

[실행 입력](../derivations/FULL_SOURCE_CERTIFICATE_CHECK.wl)과 [실제 결과](../evidence/FULL_SOURCE_CERTIFICATE_RESULT.json)는 S1–S34의 전체 source에 대해 12개 named check가 모두 PASS임을 기록한다. 검산이 소비한 rate-envelope SHA256은 `ef9fcb4d6d18d388bc45ae71844b1f8d3c284e529185898d195cdf28add69546`이다.

Scaled source의 전 cube 상계는
\[
|G_{h,i}|\le b_i,\qquad
\sum_j|\partial_jG_{h,i}|\le\ell_i(h)\le\ell_{i,0}+H\ell_{i,1},\quad0\le h\le H.
\]
\(B_{\max}=\max_i b_i\), \(L(H)=\max_i\ell_i(H)\), \(q=HL(H)\)로 두면 실제 결과는 다음과 같다. 소수는 가독성을 위한 표시값이며 accept/reject에는 결과 파일의 유리수 또는 그것의 outward enclosure를 사용한다.

| 항목 | 실제 exact certificate의 값 또는 표시값 |
|---|---|
| \(H\) | \(500000000\ \mathrm s\) |
| \(B_{\max}\) | \(2007609719349141/1250000000000000000000000\ \mathrm{s^{-1}}\) |
| \(HB_{\max}\) | \(2007609719349141/2500000000000000=0.8030438877396564\) |
| \(q\) | \(702445907956526291951811059835445533/31250000000000000000000000000000000000\), 표시 \(0.02247826905460884\) |
| self-map margin | \(1-HB_{\max}\), 표시 \(0.1969561122603436\) |
| contraction margin | \(1-q\), 표시 약 \(0.9775217309453911\) |
| \(\|(D_XF)^{-1}\|_\infty\) 상계 | \(1/(1-q)\), 표시 약 \(1.0229951604583454\) |
| \(\|dX/dh\|_\infty\) 상계 | \(B_{\max}/(1-q)\), 표시 약 \(1.6430200215866466\,10^{-9}\ \mathrm{s^{-1}}\) |
| 정확한 Picard 8회 갱신의 오차 상계 | \(q^8HB_{\max}/(1-q)\), 표시 \(5.354461272651965\,10^{-14}\) |

\(HB_{\max}<1\), \(q<1\)은 \(0\le h\le H\) 각각에서 cube의 내부 self-map, 수축, cube 안의 유일한 물리 해, 그리고 같은 이전 상태에서 출발하는 \(C^1\) branch를 보장한다. cube 바깥의 모든 해에 대한 전역 유일성으로 확대하지 않는다.

해의 component enclosure는 \(|X_i(h)|\le hb_i\)다. \(h=H\)에서 실제 표시값은
\[
(0.8030438877396564,\ 0.145772050824204,\ 0.013214296554564,
0.05624675125755955,\ 2.5063657259779202\,10^{-5},
2.5063657259779202\,10^{-5},\ 2.5063657259779202\,10^{-5})
\]
이다. 성분 enclosure 또는 보수적인 \(\|X\|_\infty\le HB_{\max}\)를 primitive Lipschitz 상계와 결합해 guard 여유를 출력한다. \(h\) 변화에 따른 guard 이동은 \(L_gB_{\max}|\Delta h|/(1-q)\)로 감쌀 수 있다. 이러한 이동 상계는 앞선 전체 cube의 물리 포함 증명을 소비한다.

**결과 capture 범위.** actual raw 응답은 출력 길이 제한으로 중간 일부가 생략되었다. 12개 판정과 위 핵심 유리수, 7개 row 상계, 오차 상계는 수신되었고 normalizer가 누락을 기록했다. `self_map_margin`, `contraction_margin`, `inverse_Jacobian_infinity_bound`, `branch_parameter_derivative_per_second_bound`의 exact 필드는 JSON에서 `null`이다. 위 표의 해당 식은 수신된 exact \(HB_{\max},q,B_{\max}\)에 적용하는 해석적 공식이며, 이 네 exact 필드를 원응답에서 수신했다고 기록하지 않는다. 재현 구현은 유리수 분자·분모를 정수로 읽어 식을 평가하거나 outward enclosure를 만들고, 출력 재구성과 원응답 수신을 구별한다.

현재 인증은 명시된 한 cube와 \([0,H]\)를 실제로 감싼다. BE source 단계의 존재·유일성과 solve 오차를 인증하며 시간 이산화 오차나 연속 ODE 궤적의 정확도를 수치로 인증한 결과는 아니다.

## 7. Native solve와 부동소수점 오차 예산

정확한 Picard 시작값은 \(X_0=0\), 갱신은 \(X_{k+1}=hG_h(X_k)\)다. **8회 갱신은 아직 실행되지 않았다.** 위 \(5.35446\,10^{-14}\)는 모든 \(h\le H\)에 대한 정확 연산의 이론 상계다.

Native 구현은 계산된 잔차 \(\widetilde F\)와 그 엄밀한 error enclosure \(\eta_F\)를 함께 출력한다. 후보가 인증 cube 안에 있을 때
\[
\|X_*-\widetilde X\|_\infty
\le\frac{\|\widetilde F(\widetilde X,h)\|_\infty+\eta_F}{1-q}
\]
를 종료 기준으로 사용할 수 있다. residual norm만 작은 것을 최종 오차 인증으로 기록하지 않는다. \(\eta_F\)에는 primitive 회복, rate/opacity, 사건 합산, affine 변환과 scaling, 분모 계산의 실제 오차를 포함한다.

매 갱신의 실제 계산 오차가 \(\eta\) 이하이고 모든 갱신이 cube에 머물면
\[
\|e_k\|_\infty\le q^k\|e_0\|_\infty+\eta\frac{1-q^k}{1-q}.
\]
정확 Picard 궤적과 비교할 때는 이 계산 오차 항을 위 이론적 truncation 상계에 더한다. 예를 들어 최종 scaled 목표 \(\tau=10^{-12}\)를 선택한다면, 8회 고정 갱신을 채택하는 조건은
\[
\frac{q^8HB_{\max}}{1-q}
+q^8\eta_0+\eta\frac{1-q^8}{1-q}
+\eta_{\mathrm{input/chart}}\le\tau
\]
와 각 갱신의 cube 포함이다. 마지막 항은 실제로 증명한 입력·chart 변환의 영향만 넣는다. \(\mu\), 초기 광자 수, 조성 등 문제 입력을 반올림해 다른 source 문제로 바꾼 영향은 단순한 solve roundoff와 구별하여 입력 구간 또는 parameter sensitivity로 감싼다.

이 예산은 solver를 반드시 Picard로 제한하지 않는다. Newton 또는 다른 predictor/corrector를 쓰더라도 최종 잔차 enclosure와 유효한 uniqueness box를 제시하면 같은 사후 오차식을 소비할 수 있다. 작은 \(q\)라는 exact 결과와 실제 부동소수점 error budget의 PASS를 서로 다른 receipt 항목으로 저장한다.

## 8. \([0,H]\) 다음의 full-box continuation tube

추가 \(h\) 구간에는 S32–S34의 구성식을 사용한다. \(I_h\) 전체의 predictor \(\bar X(h)\), 양의 vector \(r\), 한 certificate 동안 고정인 가역 행렬 \(A\)를 입력하고
\[
\mathcal T=\{(X,h):h\in I_h,\ |X-\bar X(h)|\le r\}
\]
전체를 물리적인 smooth domain 안에 넣는다. 표본점의 guard만 확인하는 것으로 이 단계를 대신하지 않는다. 여기서 \(Y_{\rm rad}\)는 radii의 비음수 residual 상계이며 원래의 보존 변수 \(Y_{\rm cons}=(\zeta,E,\mathbf M)\)와 구별한다.
\[
Y_{\rm rad}\ge |AF(\bar X(h),h)|\quad\text{모든 }h\in I_h,\qquad
Z\ge |I-A D_XF(X,h)|\quad\text{모든 }(X,h)\in\mathcal T.
\]
한 점에서 구한 \(J_0\)를 preconditioner 구성에 사용할 수 있다. 그러나
\[
|D_XF-J_0|\le\Delta J\quad\text{on }\mathcal T,\qquad
Z=|I-AJ_0|+|A|\Delta J
\]
의 \(\Delta J\)는 전 tube enclosure여야 한다. \(D_XF=I-hD_XG_h\)에는 photon denominator의 \(h\) 의존성까지 넣는다.

다음 componentwise 조건을 검증한다.
\[
Y_{\rm rad}+Zr<r,\qquad
q_r=\max_i\frac{(Zr)_i}{r_i}<1.
\]
이는 \(X\mapsto X-AF(X,h)\)가 각 section을 내부로 보내고 \(\|v\|_r=\max_i|v_i|/r_i\)에서 수축함을 보장한다. 여기에 parameter 구간의 균일한 \(C^1\) regularity를 기록하여 section마다 유일한 해와 branch regularity를 연결한다. 현재 THEORY06에서는 이 후속 tube 알고리즘을 유도했으며, \(H\) 바깥의 tube chain을 native로 실행한 결과는 없다.

**Branch 연결 조건.** 두 geometric box가 겹친다는 사실만으로 동일한 해라고 결정하지 않는다. 공통 \(h\)에서 한 certificate의 **전체 endpoint root enclosure**를 다른 uniqueness box 안에 넣거나, 양쪽 안에 포함되는 공통 certified root enclosure를 제시한다. 이 root identity와 local uniqueness를 확보한 뒤 연결된 공통 parameter 구간의 branch를 이어 붙인다. chart를 바꾸면 interval affine map과 반올림 enclosure를 포함하여 nesting을 증명한다.

한 branch에서 이전 상태는 고정이다. 실제 시간 적분의 다음 단계로 넘어가 \(p^-,z_*\) 등을 갱신할 때는 새로운 local certificate 또는 이미 증명된 초기 상태 family의 균일 certificate를 사용한다. 인증 실패 시에는 \(I_h\)를 줄이거나, 상계를 좁히거나, chart를 옮기는 구체적인 다음 조작을 기록한다. box 인증 실패만으로 실제 물리 branch가 종료되었다고 판정하지 않는다.

## 9. 구현 입력·출력과 provenance

아래는 의미 계약이며 기존 production 함수 이름을 일괄 변경하라는 요청이 아니다.

| 동작 | 입력 | 필수 출력 |
|---|---|---|
| 물리 회복 | 고정 model/anchor와 exact 또는 enclosed \(X\) | \(w,T,\gamma,\beta,n_H,n_e,E'_q\), 조성·cold gap·domain enclosure |
| Point event 평가 | 같은 후보·같은 \(h\), 고정 old photons | PI/CI/RR/두 DR, kinetic/binding/escape, \(p^+\), 공통 7개 source와 장부 |
| JVP 및 parameter 미분 | 같은 endpoint와 방향 \(dX\) | primitive·rate·opacity·photon denominator·source의 JVP, \(\partial_h(hG_h)\) |
| Box/tube 평가 | 닫힌 \(X\) box와 \(h\) interval | outward primitive/rate/Jacobian enclosure, \(b,\ell\) 또는 \(Y_{\rm rad},Z,r\), cutoff cell |
| 인증/종료 | 실제 계산 후보, valid enclosure, error budget | physical inclusion, self-map/contraction margin, residual error와 해 오차 상계, root nesting evidence |

각 실행은 다음을 묶어 재현할 수 있어야 한다.

1. 실제 repository/head/tree, 공급자 source SHA, schema와 상수, compiler·target·binary SHA, 수학 함수 library 및 rounding/enclosure 방법.
2. \(D,f,\mu,\zeta_*,T_*,\beta_*,\gamma_*,H_s\), 실제 baseline/increment 입력 표현, 모든 node의 방향·에너지·이미 적용된 weight·수·공급 owner, 원문 input byte SHA.
3. 소비한 proof/실제 evaluator 입력·raw/result/최종 manifest의 identity. 특히 exact literal, rational bound, native floating value를 별도 필드로 기록.
4. 실제 호출 경로와 횟수, endpoint event 및 derivative 출력, 구간 결과, 종료오차 예산, 채택한 branch enclosure와 유효 \(h\) 범위.
5. 계산한 것과 해석적으로 보장된 것의 구별. “8 updates”가 이론 budget인지 실제 native 반복 횟수인지 명시하고 raw 반복값이 있을 때만 실제 실행으로 기재.

## 10. 완료를 판별하는 최소 대조 검사

다음은 후속 coding unit의 완료 조건이다. 이 문서에서 수행한 native test 목록이 아니다. owner가 실제 경로를 구현한 뒤 남은 위험을 직접 구별하는 검사로 묶는다.

| 판별할 구현 위험 | 필요한 증거 |
|---|---|
| affine 변환에서 열적 정보 손실 | 큰 baseline과 작은 increment를 분리한 fixture의 roundtrip enclosure; 원래 7개 보존 잔차와 변환 잔차의 행 동등성 및 실제 roundoff budget |
| primitive·조성 chain 누락 | 일반 3차원 \(dX\)의 분석 JVP를 독립 고정밀/구간 기준과 대조; \(dB,dd,dn_H,D_XE'\) 각 경로가 반영된 결과 |
| photon opacity 또는 denominator 동결 | 같은 후보의 exact finite photon identity, JVP, \(\partial_h(hR)\)를 함께 대조; \(h=0\), \(\Lambda=0\), 활성 여러 absorber가 있는 node 포함 |
| 사건/에너지 중복 또는 DR 누락 | 각 gross CI/RR/두 DR/PI 및 kinetic/binding/escape의 독립 배열 대조와 하나의 의도적 사건 perturbation이 공통 species/energy/momentum ledger에 한 번 반영됨을 확인 |
| moving frame 또는 방향 정보 손실 | nonzero bulk와 작은 횡방향 후보에서 Doppler/전체 photon momentum 확인; axial adapter와 명시적인 방향 node 계산의 유효한 대칭 한계 대조 |
| point 검사로 full-box 범위를 대체 | 동일 source 정의의 analytic/interval 전체 box 상계, 정확 유리수 certificate의 PASS, 실제 floating enclosure가 더한 여유를 각각 기록 |
| 작은 잔차를 해 오차로 오인 | \(\eta_F\)가 포함된 사후 bound 또는 증명된 update-error recurrence와 cube 포함 |
| continuation의 다른 root 연결 | full parameter tube의 \(Y_{\rm rad},Z,r\), strict inequalities와 공통 \(h\)의 certified root nesting |

물리 ledger의 nuclear H/He, charge closure, 공유 흡수 수, full energy·momentum, escape 부호는 gross 사건 규모에 맞춰 검사하고 차감 후 거의 0인 net source만 분모로 삼지 않는다. isotope/추가 species, source abundance 변경, 새로운 recombination closure를 이 구현의 입력 범위에 암묵적으로 더하지 않는다.

완료된 native 계약은 **실제 provider 경로의 결과**, **whole-domain 이론 상계**, **부동소수점 오차 enclosure**가 동일 source/input identity에 연결된 상태다. 그 시점에 독립 검토와 실제 실행 receipt를 붙여 coding owner의 상태를 바꾼다. 지금은 원래 세 coding owner와 continuation adapter 구현이 pending이며, THEORY06의 명시적 정량 인증과 후속 구성식이 인계되었다.

## 근거 경로

- [과학 계약](SCIENTIFIC_CONTRACT.md), [Primitive differential bounds](../derivations/PRIMITIVE_DIFFERENTIAL_BOUNDS.md), [실제 primitive check 결과](../evidence/PRIMITIVE_DIFFERENTIAL_RESULT.json).
- [실제 FT03/Verner 전 구간 상계](../derivations/RATE_ENVELOPES.md), [실제 rate-envelope 결과](../evidence/RATE_ENVELOPE_RESULT.json), [source 함수](../source_map/SOURCE_FUNCTIONS.md), [source identity](../source_map/CURRENT_SOURCE.json).
- [전체 source/continuation S1–S34](../derivations/FULL_SOURCE_CONTINUATION_CERTIFICATE.md), [명시적 \(H\) C1–C12](../derivations/EXPLICIT_H_CERTIFICATE.md), [실제 계산 입력](../derivations/FULL_SOURCE_CERTIFICATE_CHECK.wl), [실제 결과](../evidence/FULL_SOURCE_CERTIFICATE_RESULT.json), [원응답](../evidence/FULL_SOURCE_CERTIFICATE_RAW.json).
- [수학 문헌과 적용 범위](../review/LITERATURE_MAP.md), [부모 THEORY05의 불변 source tree](https://github.com/cosmosapjw-quantum/BASS_HE/tree/94a34d09ad5810a675b556561e5593b279d30448), [선정된 실제 rate source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs).
