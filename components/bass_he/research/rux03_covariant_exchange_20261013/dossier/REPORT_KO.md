# BASS_HE — 공변 사건 전달과 비등방 복사 work

**연구 단위:** `HERE_RUX03_COVARIANT_EXCHANGE_04`  
**일자:** 2026-10-13 KST  
**경로:** `physmath-research-loop` THEORY R1–R10

## 1. 이번 루프에서 닫은 연결

직전 `PRIMARY_THEORY_03`의 H/He 사건·결합에너지·열에너지 수지를, 공통 기체
정지계에서 정의한 **에너지·운동량 전달 4-벡터**로 확장했다. 이 4-벡터의 시간
투영은 기존 열방정식을 재현하고, 공간 투영은 고정된 homogeneous/geodesic
기체 프레임이 만족해야 할 흡수 운동량 조건을 준다. 같은 투영 구조에서 기존
광자 전단 work를 복사 응력의 수축항으로 연결했다.

핵심 결과는 다음 세 식이다. 아래에서 `u.u=-1`, `h=g+u u`,
`mathcal E_q=epsilon_eV E_q=hbar omega_q`이고, `R_iq`는 proper volume·proper
time당 흡수 사건률이다.

\[
\boxed{G_g^a=\sum_{iq}{\mathcal E_q\over c}\mathcal R_{iq}
(u^a+e_q^a)-{\mathcal Q_{\rm esc}\over c}u^a.}
\tag{1}
\]

\[
\boxed{\dot w=Q_{\rm th}^{(H)}-{2\over3}\Theta w,\qquad
{\rho_g+p_g\over c^2}a^a+D^ap_g=f_{\rm abs}^a.}
\tag{2}
\]

\[
\boxed{\dot\rho_\gamma+{4\over3}\Theta\rho_\gamma+D_aq^a
+{2a_aq^a\over c^2}+\sigma_{ab}\pi^{ab}
=\mathcal Q_\gamma.}
\tag{3}
\]

식 (1)–(2)의 escape 공간항은 **기체 정지계에서 등방적인 방출**을 가정했다.
방출 비등방성을 주면 식 (2)의 우변에 `-ell_esc^a`가 추가된다.

이 구성이 실제로 가능한 경우도 만들었다. 같은 에너지·광자 수를 갖는 반대
방향 쌍은 각 흡수종의 운동량 전달을 상쇄한다. 쌍 사이의 에너지 배분을 다르게
하면 비등방 압력과 전단 work가 남는다. 양의 광자 수를 가진 여섯 빔 예에서는
평균 팽창이 0인 시험 계량에서도 광자 에너지가 초기값의 **5/6**으로 변한다.
따라서 `순흡수 운동량=0`인 프레임과 `비등방 에너지 work != 0`인 복사를 함께
구성할 수 있다.

Wolfram에서 공식 xAct를 실제 적재하여 **24개 텐서 항등식**을 계산했다.
기체 에너지·운동량 및 복사 에너지의 미분형 투영까지 모든 잔차가 0으로
환원됐다. 별도 **21개 정확 대수 검산**도 통과했다. 최종 독립 검토의 판정과
검토한 입력 identity는 `review/DECISION.json`에 모았다.

## 2. 현재 가정과 근거

현재 채택 base는 [BASS_HE PR31](https://github.com/cosmosapjw-quantum/BASS_HE/pull/31)의
`be96b0011772b47af4bd3c8e420f73153a745508`, 실제 receiver는
[rei_bianchi PR114](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/114)의
`a5c958c414dea41216b445c05f58df837f05cacb`이다. 두 head는 직전 기록과 같았다.
최근 PR과 관련 branch를 조회한 범위에서 primary-provider 후속 구현은
관측되지 않았다.

| 항목 | 이번에 사용하는 가정·근거 | 상태 |
|---|---|---|
| 기체 | 공통 four-velocity, 한 온도, 전하중성, 비상대론적 H/He ideal gas, 보존되는 핵수 | 기존 physical contract 재사용 |
| 정의역 | `n_H>0`, 고정 `f=n_He/n_H>0`, 물리적인 H/He fraction simplex | 기존 사건식의 정의역 유지 |
| 원자 과정 | warm FT03, 30,000–110,000 K, CI/RR/DR·primary absorption, RR/DR 포획 운동에너지 냉각, CR/RCT/HH off | 기존 계수·포획 운동에너지 모멘트 재사용 |
| 사건 에너지 | 결합에너지 다항식과 `Q_th + dot B + Q_esc = sum E P` | 직전 이론 증명과 47개 symbolic group 재사용 |
| 공변 구조 | `(-+++)`, `u.u=-1`, `U=c u`, 명시적인 `c,hbar,k_B` | 이번 정의와 직접 유도 |
| escape | 기존 scalar `Q_esc`에 기체 정지계 등방 방출 모멘트를 부여 | 이번에 명시한 추가 angular closure |
| 선택된 배경 | prescribed LRS Bianchi I, normal/geodesic gas, homogeneous pressure | 현재 적용 대상 |
| 비등방 복사 | photon-node moment로 `rho,q,P,pi` 구성; 평균압력 `rho/3`과 비등방 `pi` 동시 유지 | 이번 구성과 현재 stress moment 대응 |

국소 투영식은 충분히 매끄러운 계량·기체 프레임·복사 모멘트에 대해 유도했다.
유한한 photon-node 합을 사용하므로 합과 미분의 교환에 별도 수렴 가정이
필요하지 않다. 기체의 비상대론적 상태방정식과 원자 계수의 적용 범위는 위
표의 범위로 유지된다.

원전 대조에서는 [Farris et al. (2008), 식 (19), (20), (30)](https://arxiv.org/pdf/0802.3210)의
일반 흡수·방출 four-force, [Barrow–Maartens, 식 (11), (12)](https://arxiv.org/pdf/astro-ph/9808268)의
정확한 1+3 투영식, [Rosdahl–Teyssier (2015), 식 (27), (28)](https://arxiv.org/pdf/1411.6440v2)의
H/He 광흡수 운동량, [Rosdahl et al. (2013), Appendix A](https://arxiv.org/pdf/1304.7126)의
등방 재결합 방출과 photoheating을 확인했다. 일반 four-force와 shear 항은
확립된 구조다. 이번 결과의 역할은 이를 BASS_HE의 사건률·결합에너지·광자
정규화 및 실제 코드의 work에 맞추고, 필요한 각도 조건을 구성하는 것이다.

## 3. 광흡수와 Case A 방출을 같은 4-벡터 수지에 넣기

광자의 물리적 에너지를 `mathcal E_q=epsilon_eV E_q=hbar omega_q`로 두면
운동량은

\[
p_q^a={\mathcal E_q\over c}(u^a+e_q^a),\qquad
u\cdot e_q=0,\quad e_q\cdot e_q=1
\]

이다. 따라서 `p_q.p_q=0`이고 기체가 측정한 에너지는 `-c u.p_q=mathcal E_q`다.
흡수 사건마다 이 운동량을 더하면

\[
\mathcal A^a=\sum_{iq}\mathcal R_{iq}p_q^a,
\quad
\mathcal Q_{\rm abs}=-c u_a\mathcal A^a
=\sum_{iq}\mathcal E_q\mathcal R_{iq},
\]

\[
f_{\rm abs}^a=h^a{}_b\mathcal A^b
={1\over c}\sum_{iq}\mathcal E_q\mathcal R_{iq}e_q^a.
\tag{4}
\]

한 사건의 `E_q-chi_i`는 열로, `chi_i`는 결합에너지 변화로 들어간다.
흡수 운동량은 이 분할 전의 **전체 광자 에너지 `mathcal E_q/c`**를 사용한다.
열에너지만으로 운동량을 계산하면 같은 사건에서 전달된 일부 운동량을
누락한다.

Case A의 총 방출 power를 `mathcal Q_esc`라 하고 기체 정지계에서 등방적으로
방출하면

\[
\mathcal L^a=(\mathcal Q_{\rm esc}/c)u^a
\tag{5}
\]

를 얻는다. 양의 모멘트 실현도 명시적으로 가능하다. 임의의 `E_*>0`에서
세 직교축의 여섯 방향에 각각

\[
\mathcal R_j^{\rm em}={\mathcal Q_{\rm esc}\over6\epsilon_{\rm eV}E_*}
\]

만큼 방출하면 공간 운동량 합이 0이고, 에너지 합은 `mathcal Q_esc`이며,
두 번째 각도 모멘트도 등방적이다. 구면에 균일하게 분배하면 완전한 각도 등방
실현을 얻는다. 이는 필요한 방출 모멘트의 구성이고, `E_*`를 실제 재결합
스펙트럼으로 선택한 것은 아니다. 기존 scalar escape counter는 방출
스펙트럼이나 방출 후 전파된 stress tensor를 결정하지 않는다.

외부 primary 주입을 `S^a`라 할 때 세 부문의 전달은

\[
G_g^a=\mathcal A^a-\mathcal L^a,\quad
G_{\gamma,p}^a=-\mathcal A^a+\mathcal S^a,\quad
G_{\rm esc}^a=\mathcal L^a
\]

이며 합은 정확히 `S^a`다. RR/DR의 결합에너지와 포획 운동에너지는 기존
`Q_esc`의 소유권을 유지한다. 여기서 냉각은 이 포획 운동에너지 손실을 뜻하며
별도 line/free-free 채널을 추가하지 않았다. 현재 코드에서 escape는
reference-volume 누적 에너지 counter로 남고, 위 식은 그에 대응하는
국소 공변 전달 계약을 준다.

## 4. 기존 열방정식이 재현되는 과정

직전 변수와 동일하게

\[
e=x+f(a+2b),\quad d=1+f+e,\qquad
w={3k_B\over2\epsilon_{\rm eV}}dT,
\]

\[
B=\chi_0x+f\chi_1a+f(\chi_1+\chi_2)b
\]

를 쓴다. 중성 원자 조성의 기준질량 `m_ref=m_HI+f m_HeI`를 고정하면

\[
\rho_g=n_Hm_{\rm ref}c^2+n_H\epsilon_{\rm eV}(w+B),
\quad p_g={2\over3}n_H\epsilon_{\rm eV}w,
\]

\[
T_g^{ab}=\rho_g u^au^b+p_g h^{ab}.
\tag{6}
\]

기준 중성 원자 질량에는 전자의 질량도 포함한다. 여기에 자유전자 질량을
다시 더하면 이중 계산이 된다. 이온화에 따른 조성 에너지 증가는 양의 `B`로
계상된다.

식 (6)의 시간 투영은

\[
\dot\rho_g+\Theta(\rho_g+p_g)=\mathcal Q_g.
\]

핵수 보존 `dot n_H=-Theta n_H`를 대입하면 기준질량·열에너지·결합에너지의
공통 희석항이 소거되어

\[
n_H\epsilon_{\rm eV}(\dot w+\dot B)+\Theta p_g
=\mathcal Q_{\rm abs}-\mathcal Q_{\rm esc}
\tag{7}
\]

가 된다. 여기서 직전 사건 항등식

\[
Q_{\rm th}^{(H)}+\dot B+Q_{\rm esc}^{(H)}
=\sum_{iq}E_q\mathcal P_{iq},
\qquad \mathcal R_{iq}=n_H\mathcal P_{iq}
\]

을 사용하면 식 (2)의 열방정식이 바로 나온다. `Theta=3H`인 현재 배경에서는
`dot w=-2H w+Q_th^(H)`이고, proper thermal density
`u_th=n_H epsilon_eV w`는

\[
\dot u_{\rm th}=-5H u_{\rm th}+\mathcal Q_{\rm th}
\tag{8}
\]

를 만족한다. 이는 [현재 AXI derivative](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs#L233-L256)의
기체 식과 같다.

공간 투영도 같은 stress에서 따라온다.

\[
{\rho_g+p_g\over c^2}a^a+D^ap_g=f_{\rm abs}^a-\ell_{\rm esc}^a.
\tag{9}
\]

따라서 normal/geodesic gas, homogeneous pressure, comoving-isotropic escape를
함께 쓰는 현재 적용에서는 `f_abs=0`이 호환 조건이다. 일반 node 입력에서 이
힘이 남으면 식 (9)의 가속도 또는 별도로 지정한 지지력이 필요하다. 현재
에너지 잔차만으로 그 공간 방정식까지 계산된 것은 아니다.

## 5. 복사 투영과 기존 전단 work의 대응

물리적 energy flux를 `q^a`로 두고

\[
T_\gamma^{ab}=\rho_\gamma u^au^b
+{u^aq^b+q^au^b\over c}
+{\rho_\gamma\over3}h^{ab}+\pi^{ab}
\tag{10}
\]

로 분해한다. `q`와 `pi`는 공간적이고 `pi`는 대칭·무흔적이다.
`rho_gamma/3`은 질량 없는 입자 분포의 평균압력이다. 비등방 압력을 없애는
가정은 `pi=0`이며, 여기서는 그 가정을 두지 않았다.

먼저 `u_b T_gamma^{ab}=-rho_gamma u^a-q^a/c`를 수축한 뒤 미분하면

\[
-c u_b\nabla_aT_\gamma^{ab}
=\dot\rho_\gamma+\Theta\rho_\gamma+\nabla_aq^a
+cT_\gamma^{ab}\nabla_a u_b.
\]

속도 미분의 분해를 사용한 마지막 항은

\[
cT_\gamma^{ab}\nabla_a u_b
={\Theta\rho_\gamma\over3}
+{a_aq^a\over c^2}+\sigma_{ab}\pi^{ab}.
\]

또한 `u.q=0`을 미분하면

\[
\nabla_aq^a=D_aq^a+{a_aq^a\over c^2}
\]

를 얻는다. **가속도·플럭스 항 두 개는 서로 다른 두 전이에서 하나씩 나온다.**
이를 합하면 식 (3)이 된다. 원전의 `c=1` 표현과도 부호와 계수가 일치한다.

현재 LRS convention은

\[
H_\perp=H-s,\quad H_\parallel=H+2s,\qquad
\sigma=\operatorname{diag}(-s,-s,2s)
\]

다. 광자 모멘트

\[
\rho_\gamma=\sum_q\mathcal E_q n_q,\qquad
P^{ab}=\sum_q\mathcal E_q n_q e_q^ae_q^b,
\quad \pi^{ab}=P^{ab}-{\rho_\gamma\over3}h^{ab}
\]

를 대입하면

\[
\boxed{\sigma:\pi=2s(P_\parallel-P_\perp)=2s\Delta P.}
\tag{11}
\]

이에 따라 현재 식 `dot rho_gamma=-4H rho_gamma-2s DeltaP+Q_gamma`가
회복된다. `2s DeltaP` 자체는 이미 구현되어 있고, 이번에는 그 공변 의미와
동시에 필요한 first-moment 조건을 연결했다.

## 6. 운동량은 상쇄되고 전단 work는 남는 구성

### 6.1 쌍의 대칭이 유지되는 조건

각 쌍에서 `e_-=-e_+`, `E_-=E_+`, `N_-=N_+`, `S_-=S_+`를 둔다. 흡수종
`i`의 opacity가 방향 반사에 대해 같으면 `R_i-=R_i+`다. 그러면 각 종의
공간 운동량이 쌍마다 따로 소거된다. 다른 쌍 사이의 에너지·흡수율·광자 수는
서로 달라도 된다.

Bianchi I에서 endpoint 에너지비는

\[
R_q={E_q^+\over E_q^-}
=\sqrt{\sum_i\left({a_i^-\over a_i^+}\right)^2
(e_q^{\hat i,-})^2}.
\tag{12}
\]

방향 반사에 대해 `R_q`는 짝함수이고 최종 방향은 홀함수다. 공통 gas endpoint
state에서 두 node의 BE 식은 같은 양의 분모를 가지므로 pair equality가
그대로 유지된다. 이 주장은 비선형 gas root가 이미 존재한다고 가정하는
대신, **각 공통 물리적 후보 state에서 node map의 대칭이 유지됨**을 먼저
보인다. 따라서 그 state를 만족하는 해에서도 같은 대칭이 성립한다.

현재 실제 초기 자료의 정적 비교에서도 726 energy × 4 angular node,
총 2,904개 node에 대해 **1,452개의 opposite-mu pair**가 에너지 좌표·가중치·
초기 광자 수까지 bitwise 동일했다. production characteristic은 `mu_0^2`를
통해 에너지비를 계산하고 source도 같은 pair에서 even이다. 축대칭 ring의
azimuth 평균과 `mu -> -mu`를 함께 사용하면 모든 first moment가 상쇄된다.
이 결과는 선택된 초기 배열과 source의 구조에 관한 것으로, 과거 ODE
history의 parity를 재검사한 결과는 아니다.

반면 [현재 일반 stage API](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L84-L107)는
서로 다른 `+mu,-mu` count를 허용한다. 후속 구현은 선택된 입력의 대칭과
일반 API의 공간 잔차 검사를 구별해야 한다.

### 6.2 양의 여섯 빔 예

세 축의 반대 방향 쌍에 배분하는 초기 에너지 비중을

\[
\left({1-\eta\over2},{1-\eta\over2},\eta\right),
\qquad 0\le\eta\le1
\]

로 두자. 각 쌍은 반씩 나누어 가진다. 그러면

\[
q^a=0,\quad f_{\rm abs}^a=0,\qquad
P=\rho_\gamma\operatorname{diag}
\left({1-\eta\over2},{1-\eta\over2},\eta\right),
\]

\[
\sigma:\pi=s\rho_\gamma(3\eta-1).
\tag{13}
\]

`0<eta<1`이면 여섯 빔이 모두 양의 에너지를 가지며, `eta != 1/3`이면
초기 전단 work가 남는다. 흡수율은 같은 pair 안에서만 같으면 된다.

정확한 수를 보기 위해 prescribed test metric에서 `H=0`, 상수 `s>0`,
`s h=log 2`를 택한다. 이때

\[
{a_\perp^+\over a_\perp^-}={1\over2},\quad
{a_\parallel^+\over a_\parallel^-}=4,
\]

이므로 transverse 광자 에너지는 2배, axial 에너지는 1/4배가 된다.
흡수·주입을 끈 기하 단계의 총 에너지비는

\[
F=2(1-\eta)+{\eta\over4},\qquad
{\mathcal W_\gamma\over\mathcal E_\gamma^-}=1-F.
\tag{14}
\]

| 초기 배분 | 최종/초기 광자 에너지 | Work/초기 에너지 |
|---|---:|---:|
| 축방향 두 빔, `eta=1` | `1/4` | `3/4` |
| 비등방 여섯 빔, `eta=2/3` | `5/6` | `1/6` |
| 초기 second moment가 등방적인 여섯 빔, `eta=1/3` | `17/12` | `-5/12` |

마지막 행은 초기 각도 second moment가 등방적이어도 비등방 redshift가 이후의
분포를 바꾼다는 예다. 음의 work는 지정된 기하가 광자 에너지를 증가시키는
경우다. 이 `H=0` 수치 예는 운동학적 시험 계량에 대한 정확한 계산이며,
현재 dust+Lambda background의 해로 채택한 것은 아니다. 반대 방향 쌍의
구성 자체는 실제 선택 배경의 `H != 0`에서도 식 (12)로 유지된다.

흡수도 포함할 수 있다. 양의 endpoint 흡수율 `Lambda_perp,Lambda_parallel`을
주면 살아남은 에너지비는 각 방향의 기하 에너지비에
`1/(1+h Lambda)`를 곱한 값이다. 흡수된 비율에는 `h Lambda/(1+h Lambda)`가
곱해진다. 따라서 **생존 에너지비 + 흡수 에너지비 + work 비 = 1**이 정확히
성립하며, 쌍의 흡수 운동량 상쇄도 유지된다.

## 7. 유한 단계 work와 flux-only 조건의 판별

Endpoint-energy 사건 배치에서는 이전에 증명한 product rule을 방향별 에너지에
적용하여

\[
\boxed{\mathcal W_\gamma
=-\sum_q(\mathcal E_q^+-\mathcal E_q^-)N_q^-
=\sum_q\mathcal E_q^-N_q^-(1-R_q)}
\tag{15}
\]

를 얻는다. 광자 history budget은

\[
\mathcal E_\gamma^+-\mathcal E_\gamma^-+\mathcal W_\gamma
+\sum_{iq}\mathcal E_q^+ A_{iq}
=h\sum_q\mathcal E_q^+S_q^*
\tag{16}
\]

이다. 사건·주입 증가량을 최종 에너지에서 평가하므로 기하 work에는 들어온
광자 수 `N^-`가 붙는다. 이것이 연속 극한의
`V(H rho_gamma+2s DeltaP)`와 연결된다. 후속 endpoint-energy BE 구현은 이
discrete product rule에 맞추어야 한다. 현재 source의 `work_ref`는 순간
도함수이며, 현재 ProductionInterval은 그 누적 counter를 ODE로 적분한다.
식 (15)는 해당 BE map의 정확한 이산 수지이고, 일반 반응 과정의 연속 work
적분과 동일시하지 않는다. 이전 work identity와 sourceborn 주입 소유권은
그대로 재사용한다.

또 하나의 판별은 **에너지 플럭스만 0으로 검사해도 충분한가**이다. 서로
반대 방향의 두 빔에 같은 에너지 밀도 `U_0/2`를 주되, 서로 다른 광자
에너지에서 `kappa_+ != kappa_-`가 되게 하면

\[
q_z=c(U_0/2-U_0/2)=0,\qquad
f_{{\rm abs},z}={U_0\over2}(\kappa_+-\kappa_-)\ne0.
\tag{17}
\]

모든 count와 opacity를 양수로 둘 수 있다. 예를 들어 `kappa_+=2kappa`,
`kappa_-=kappa>0`이면 힘은 `kappa U_0/2`다. 이 비율은 FT03의 특정 두
에너지에서 측정한 수치가 아니라, 약한 flux-only 조건을 판별하는 양의
모델 구성이다. 실제 `sum_i n_i sigma_i(E)`가 다른 두 에너지도 같은
일반식을 준다.

따라서 후속 검사는 `q=0`만 사용하지 않고 식 (4)의 **흡수율로 가중한
운동량 합**을 직접 계산해야 한다. 정확히 에너지까지 맞춘 pair 조건은 이를
만족시키는 충분조건이다.

## 8. 관측 프레임을 바꾸었을 때

다른 관측자를

\[
n^a=\gamma(u^a+\beta v^a),\quad u\cdot v=0,\quad v^2=1,
\quad \gamma=(1-\beta^2)^{-1/2}
\]

로 쓰면 같은 국소 four-force에 대해

\[
\boxed{\mathcal Q_g(n)=\gamma[\mathcal Q_g(u)-c\beta v_af_g^a]}
\tag{18}
\]

가 정확히 성립한다. 기체 정지계의 등방 방출도 이 관측자에게는

\[
\mathcal Q_L(n)=\gamma\mathcal Q_{\rm esc},\qquad
h(n)^a{}_b\mathcal L^b={\mathcal Q_{\rm esc}\over c}(u^a-\gamma n^a)
\]

로 보인다. 관측 프레임을 바꾸는 계산과 원자 계수의 평가 프레임을 구별해야
한다. 현재 계수는 기체 rest-frame 에너지·온도·밀도의 함수다. 식 (18)은
그렇게 만든 전달 벡터의 정확한 투영이며, 원자 계수의 상대론적 보정을 새로
유도한 것은 아니다.

## 9. 실제 검산과 근거 상태

| 근거 | 이번 실제 결과 | 지지하는 범위 |
|---|---|---|
| xAct/xTensor | 24개 tensor group 모두 True, 잔차 24개 모두 0 | projector, null photon, 흡수·방출 four-force, observer projection, 기체·복사 미분 투영 |
| 같은 Wolfram 실행의 scalar algebra | 5개 모두 True | 기준질량 희석 소거, 열방정식 환원, flux/force 판별, 관측자 정규화 |
| 독립 기하 Wolfram 실행 | 16개 모두 True | `c` 계수, redshift·parity, 여섯 빔 stress, paired BE, finite work와 유리수 예 |
| 초기 광자 자료 정적 비교 | 1,452개 pair 일치 | 선택된 초기 입력의 반사 대칭 |
| 이전 이론 | 47개 group 재사용 | 원자 사건·provider·binding 및 finite-work 선행 결과 |

새 검산은 **45개**다. 이전 47개, 중복 smoke 6개, metadata 교정 전의 동일한
29개 실행은 여기에 더하지 않았다. 이번 native build/test, chemical RHS 및
ODE/history 실행은 0이다.

최종 실제 런타임은 Wolfram Language **15.0.1**, 공식 xAct bundle **1.3.0**,
xTensor **1.3.0**, xPerm **1.2.4**다. 최초에는 패키지가 없어 공식 배포본을
임시 설치했다. 이어진 이름공간과 기본 backend/rule 구성 문제는 실패
입력·출력을 보존하고 교정했다. 성공한 계산은 xAct의 순수 Wolfram xPerm
backend를 사용했다. 마지막 재현 입력은 패키지 archive의 SHA256을 검증한
뒤 실제 tensor declaration과 canonicalization을 수행한다.

계산 기록은 `evidence/EXECUTION_RECORD.md`, 입력·원응답·정규화 결과는
`evidence/XACT_COVARIANT_*`와 `evidence/GEOMETRY_*`에 있다. 문헌의 일반식,
이번 유도, 실제 source 기능, 미래 구현 의무는 `dossier/CLAIMS.json`과
`source_map/SOURCE_MAP.md`에서 구별한다. 신규 strong no-go는 채택하지 않는다.

## 10. 다음 구현과 열린 이론

현재 원래의 코딩 후속 단위 **`HERE_RUX03_PRIMARY_PROVIDER_03`은 그대로
남아 있다.** shared coefficient/event provider를 실제 ordinary/conservative
point, endpoint, interval/root 및 paired caller에 연결하는 작업이다.

이번 이론이 추가하는 구현 계약은 같은 raw absorption event에서
`Q_abs`, `f_abs`, `q`, `P_parallel`, `P_perp`, `sigma:pi`를 함께 반환하고,
고정 프레임 호환 잔차를 노출하는 것이다. 축대칭 node는 azimuth 평균 ring이므로
`q_z=c sum calE n mu`, `f_abs,z=sum calE R mu/c`를 사용한다. weights는
count에 이미 포함되어 있다. 이 계약과 단위 경계·정확한 참조 사례는
`dossier/CODING_CONTRACT_KO.md`에 모았다.

다음 이론 의무는 **힘이 남는 common-gas-frame의 유한 단계**다. 입력은 이번
`G_g^a`와 방향별 광자 에너지, 이전 thermal/binding 변수이며, 풀어야 할
문제는 Doppler-shifted opacity와 bulk kinetic energy를 포함한 유한 단계에서
총 four-momentum과 기체 정규화가 동시에 맞는 stage map을 구성하는 것이다.
현재 scalar BE에 운동량 증가량만 더하는 방식의 적합성은 아직 확보하지
않았다. 이번 루프는 그 작업이 사용할 연속 source와 정확한 zero-force
부분공간을 확정했다.

기존 `RUX02 + RUX03 -> RUX04 -> RUX05` owner DAG와 완료 상태는 유지하며,
별도 all-Bianchi abundance-source D2.3 작업의 범위도 확장하지 않았다.
재개 입력과 완료 기준은 `dossier/NEXT_DAG.json`, R1–R10 대응은
`dossier/LOOP_RECORD.md`에서 확인할 수 있다.
