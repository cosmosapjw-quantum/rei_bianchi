# BASS_HE — 움직이는 공통 기체의 유한 source 단계

**연구 단위:** `HERE_RUX03_MOVING_GAS_SOURCE_05`  
**경로:** physmath-research-loop, THEORY R1–R10  
**날짜:** 2026-10-13 KST  
**출발점:** THEORY04의 공변 four-force와 사건 수지를 움직이는 기체의 유한 단계로 연결

## 1. 이번 루프에서 얻은 결과

**기체 속도가 변하는 동안에도 광자 흡수, H/He 조성, 기체의 총에너지와
운동량, Case A 탈출 복사를 한 endpoint에서 갱신하는 유한 단계를 구성했다.**
광자 변수는 양의 backward Euler 식으로 소거하고, 조성 3개와 기체
에너지·운동량 4개를 합친 7변수 문제를 풀도록 정리했다. 이 과정에서
기존 열방정식에 필요한 **유한 속도 보정항**을 직접 유도했다.

기체 원시 변수 회복은 단조인 스칼라 방정식 하나로 환원된다. 주어진 조성에서

\[
E>\sqrt{(Dr)^2+|\mathbf M|^2}
\]

이면 양의 열에너지를 갖는 기체 상태가 정확히 하나 존재한다. 이 역함수를
사용하면, 모든 보존식과 채택된 atomic rate가 결합된 단계도 매끄러운
물리적 내부 영역에서 충분히 작은 시간 간격에 대해 유일한 국소 해를 갖는다.
수축사상 반복과 그 충분조건도 제시했다.

실제 검산은 xAct 25개, 원시 변수·흡수 예제의 Wolfram 18개, 유한 단계의
Wolfram 12개 named assertion으로 수행했다. 마지막 묶음은 원래 11개
성공과 양의 부등식 하나에 대한 별도 증명 검산을 합친 결과다. 서로 겹치는
Jacobian 검산은 중복 집계에서 제외한다. 수학적 증명은 두 유도 문서에,
입력·원출력·실패와 교정은 증거 폴더에 보존했다. 독립 채택 범위는
[DECISION.md](../review/DECISION.md)에 기록한다.

## 2. 현재 가정과 근거

이 결과의 대상은 고정된 local Eulerian tetrad와 고정된 lab volume에서의
균일한 source substep이다. 이 단계 동안 photon lab energy와 방향은 고정한다.
기하학적 redshift, 체적 변화와 공간 수송은 기존 하위 단계에 배치한다.
H와 He, 전자는 하나의 기체 속도를 공유한다.

| 항목 | 채택한 정의·범위 | 근거 |
|---|---|---|
| 계량과 속도 | signature \((-+++)\), \(u^a=\gamma(n^a+\beta^a)\), \(U^a=cu^a\) | THEORY04의 convention |
| 보존되는 H 밀도 | \(D=\gamma n_H\), lab volume당 H 핵 수 | H 핵 current의 연속방정식 |
| 조성 | \(\zeta=(x,fa,fb)\), H/He simplex | 기존 atomic state와 정확한 변수 사상 |
| 결합에너지 | \(B=\chi_0x+f\chi_1a+f(\chi_1+\chi_2)b\) | 기존 사건·escape 수지 |
| 기체 EOS | \(r=m_{\rm ref}c^2+\epsilon B\), \(\rho=n_H(r+\epsilon w)\), \(p=\tfrac23n_H\epsilon w\) | neutral-reference gamma-law EOS |
| 온도 | \(T=2\epsilon w/[3k_B(1+f+e)]\), \(e=x+fa+2fb\) | 전자 수를 포함한 기존 열변수 |
| atomic closure | CI, RR, 두 DR, primary absorption; 기존 FT03 범위 | 현재 source identity 확인 |
| provider 정의역 | \(30000\le T\le110000\) K, \(0\le E'_q\le50000\) eV | 실제 provider guard |
| 탈출 복사 | 기체계 등방성, RR/DR binding + captured kinetic power | THEORY04에서 채택된 four-current |

여기서 \(\epsilon=\epsilon_{\rm eV}\), 광자 물리적 에너지는
\(\epsilon E_q=\hbar\omega_q\)다. \(\mathbf M\)은 물리적 운동량 밀도의
\(c\)배여서 \(E\)와 같은 에너지 밀도 단위를 가진다.
중성 원자 기준 질량에는 속박 전자가 이미 들어 있으므로 전자 rest mass를
다시 더하지 않는다.

현재 BASS_HE 기준은 PR32의
[`ca85cfc7353da190613f7fb37a6e0ffed9b51913`](https://github.com/cosmosapjw-quantum/BASS_HE/commit/ca85cfc7353da190613f7fb37a6e0ffed9b51913),
receiver 기준은 PR114의
[`a5c958c414dea41216b445c05f58df837f05cacb`](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/a5c958c414dea41216b445c05f58df837f05cacb)다.
현재 상태와 바이트 identity, 재사용한 전제는
[SOURCE_MAP.md](../source_map/SOURCE_MAP.md)와
[VALID_REUSE_IDENTITY.json](../source_map/VALID_REUSE_IDENTITY.json)에 있다.
기존 성공 근거는 같은 가정 아래 재사용했다.

## 3. 문헌과 이번 구성의 관계

공변 복사 전달의 Doppler opacity 변환과 보존형 implicit source 갱신은
확립된 구조다. Younsi–Wu–Fuerst의 \(\nu\alpha_\nu\) 불변량을 이번
\(\delta=E'/E\) 표기에 옮기면
\(\alpha_{\rm lab}=\delta\alpha'\)가 된다.
Sądowski 등의 식 (54)–(56)은 같은 endpoint four-force를 matter와
radiation에 반대 부호로 적용해 총합을 보존한다.
Wu–Tang의 Lemma 2.1은 \(1<\Gamma\le2\) gamma-law EOS의 양의 원시 변수
회복 영역과 유일성을 증명한다.

이번 결과는 이 구조를 현재의 **H/He 사건률, H당 에너지, 변하는 proper
밀도, 탈출 복사, photon inventory와 구현 상태**에 정확히 연결한 것이다.
특히 유한 \(\mathcal K_\gamma\) 식과 원시 변수의 양수항 잔차,
warm absorption 구성, local source branch를 한 계약으로 연결했다.
전체 결합 단계의 큰 시간 간격에서의 유일성은 이 문헌만으로 결론낼 수 없다.

Exa에서는 세 질의로 15개 결과 슬롯을 요청했고 SciSpace에서는 한 질의로
10개 항목을 받았다. 독립 검토자는 네 고유 논문의 필요한 식과 주변 문맥을
읽었다. 검색 슬롯 수와 원문을 읽은 논문 수는 별도로 기록했다.
원문 위치와 조건 대응은 [LITERATURE_MAP.md](../review/LITERATURE_MAP.md)에 있다.

## 4. Doppler 변환과 사건률 정규화

방향 \(\mathbf e_q\)의 lab photon node에 대해

\[
\delta_q=\gamma(1-\boldsymbol\beta\cdot\mathbf e_q),\qquad
E'_q=\delta_qE_q,\qquad N'_q=\delta_qN_q.
\]

이 관계는 광자 사차원 운동량과 number current를 \(u\)에 투영하면 직접
나온다. \(N_q\)에는 node의 에너지·각도 가중치가 포함되어 있다.
흡수체의 proper 밀도 \(n'_i=D y_i/\gamma\)를 쓰면

\[
R'_{iq}=c n'_i\sigma_i(E'_q)N'_q=\lambda_{iq}N_q,
\]
\[
\boxed{\lambda_{iq}=cD y_i(1-\boldsymbol\beta\cdot\mathbf e_q)
\sigma_i(\delta_qE_q).}
\]

따라서 에너지 인자뿐 아니라 상대 운동에 따른 입사율도 함께 바뀐다.
\(R'\)는 proper volume·proper time당 사건 수이며, 작은 four-volume의
사건 수는 Lorentz 불변이다. lab 시간 간격 \(h\)의 사건 증분은
\(hR'\), H당 조성 증분은 \(hR'/D\)다. 기존 proper H당 rate로 표현하면
동일한 식이 \(h/\gamma\)의 계수를 가진다.

## 5. 유한 단계와 정확한 총합 보존

모든 rate를 같은 endpoint에서 평가한다. \(S_q\)를 lab volume·lab
time당 외부 광자 주입률로 두면

\[
\boxed{N_q^+=\frac{N_q^-+hS_q}{1+h\sum_i\lambda_{iq}(X_+)}},\qquad
A_{iq}=h\lambda_{iq}(X_+)N_q^+.
\]

물리적 후보에서 \(N_q^-,S_q,h\ge0\)이면 분모는 양수이고
\(N_q^+\ge0\)다. 광자 소실 수는 주어진 광자와 새 주입의 합을 넘지 않는다.
조성과 기체는 같은 \(A\)를 사용한다.

\[
D(\zeta_+-\zeta_-)=\sum_c\nu_c A_c,
\]
\[
\Delta E=\sum_{iq}\epsilon E_q A_{iq}-h\gamma_+Q'_{\rm esc},
\]
\[
\Delta\mathbf M=\sum_{iq}\epsilon E_q A_{iq}\mathbf e_q
-h\gamma_+Q'_{\rm esc}\boldsymbol\beta_+.
\]

CI에 의한 binding 증가는 새 조성의 \(r\)에 들어가고, RR/DR 복사는
채택된 escape current로 빠져나간다. 그 결과 각 에너지와 운동량 성분마다

\[
\Delta(E+E_\gamma+E_{\rm esc})=E_{\rm injected},\qquad
\Delta(\mathbf M+\mathbf M_\gamma+\mathbf M_{\rm esc})
=\mathbf M_{\rm injected}
\]

가 유한 단계에서 정확히 성립한다. 증명은 같은 사건 증분의 항별 소거다.
실제 구현의 허용 잔차는 각 기여의 절댓값 합과 해결된 nonlinear residual로
정규화하도록 구현 계약에 옮겼다.

## 6. 원시 변수 회복: 단조 방정식과 안정한 잔차

조성을 고정한 한 후보에서 \(a_r=Dr\), \(m=|\mathbf M|\),
\(C=D(r+\tfrac53\epsilon w)\)를 정의한다. EOS를 소거하면

\[
\boxed{E=\mathscr E(C)=
\frac{3C^2+2a_rC+5m^2}{5\sqrt{C^2+m^2}},\qquad C\ge a_r.}
\]
\[
\mathscr E'(C)=
\frac{3C^3+Cm^2+2a_rm^2}{5(C^2+m^2)^{3/2}}>0.
\]

왼쪽 경계의 값은 \(\sqrt{a_r^2+m^2}\), 무한대 극한은 무한대다.
따라서 허용 조건과 전역 유일성이 직접 따라온다. 해를 구한 뒤에는

\[
W=\sqrt{C^2+m^2},\quad
\gamma=W/C,\quad \boldsymbol\beta=\mathbf M/W,\quad n_H=DC/W,
\quad w=\frac{3(C-a_r)}{5D\epsilon}.
\]

작은 thermal energy를 큰 rest energy에서 반복해서 빼지 않도록
\(z=C-a_r\), \(E_0=\sqrt{a_r^2+m^2}\)를 쓰면

\[
\mathscr E(a_r+z)-E_0=
\frac{z(6a_r+z)}{5(W+E_0)}
+\frac{2z^2(a_r+z)(2a_r+z)}{5W(W+E_0)^2}.
\]

각 항이 음수가 아니며, \(\Delta=E-E_0>0\)인 해에는 명시적 bracket

\[
\frac53\Delta\le z_*\le\frac{5E_0}{3a_r}\Delta
\]

가 있다. Bisection 또는 safeguarded Newton으로 원시 변수를 구성할 수 있다.
입력 \(E-E_0\) 자체의 부호를 반올림으로 잃었다면 별도의 보상·구간
평가가 필요하다는 것도 계약에 명시했다.

양의 온도 조건과 현재 warm provider의 범위는 구별된다. 조성에서
\(\theta_{\min,\max}=\tfrac32 k_BdT_{\min,\max}\),
\(C_{\min,\max}=a_r+\tfrac53D\theta_{\min,\max}\)를 만들면

\[
\mathscr E(C_{\min})\le E\le\mathscr E(C_{\max})
\]

가 정확히 현재 warm 범위에 대응한다.

## 7. 핵심 연결: 유한 열 보정

\(\gamma_{\rm rel}=-u_+\cdot u_-\)라 두고, 기체의 Eulerian energy
current 차이를 endpoint gas velocity에 투영하면

\[
D\epsilon(\Delta w+\Delta B)
=\sum_{iq}\epsilon E'_{q,+}A_{iq}-hQ'_{\rm esc}
+\mathcal K_\gamma,
\]
\[
\boxed{\mathcal K_\gamma=D\left[
\left(r_-+\frac53\epsilon w_-\right)(\gamma_{\rm rel}-1)
-\frac23\epsilon w_-\left(\frac{\gamma_+}{\gamma_-}-1\right)
\right].}
\]

기존 binding–thermal–escape 항등식을 같은 endpoint에 적용하면

\[
\boxed{\Delta w=\frac h{\gamma_+}Q_{\rm th}^{(H)}
+\frac{\mathcal K_\gamma}{D\epsilon}.}
\]

이 식이 기존 thermal provider와 움직이는 보존형 gas stage를 연결한다.
매끄러운 작은 단계에서 \(\gamma_{\rm rel}-1=O(h^2)\)이므로

\[
\frac{\mathcal K_\gamma}{D\epsilon}
=-\frac23w_-\Delta\log\gamma+O(h^2).
\]

고정 lab volume에서도 \(n_H=D/\gamma\)가 변한다. source substep에서는
\(\Theta=\partial_t\gamma\), 기체의 proper-clock 미분은
\(\dot w=\gamma\partial_tw\)다. 따라서 연속 극한은

\[
\dot w=Q_{\rm th}^{(H)}-\frac23\Theta w
\]

로, THEORY04의 열방정식과 일치한다. Eulerian 공간에 균일한 압력이라도
기체계의 공간 투영 gradient는 속도와 시간 변화 때문에 생길 수 있다.
이 관계까지 실제 xAct로 확인했다.

## 8. 전체 단계의 국소 해를 실제로 구성하는 조건

미지수를 \(Y=(\zeta,E,\mathbf M)\)로 두고 원시 변수와 광자를 소거하면

\[
Y_+=Y_-+h\mathcal S_h(Y_+)
\]

다. 엄격한 H/He simplex, warm 구간, photon energy 구간 안에서 rate의
piecewise 경계를 피한 매끄러운 이웃을 잡는다. \(h=0\)에서 잔차의
\(Y\)-Jacobian이 항등행렬이므로 implicit function theorem에 따라
충분히 작은 \(h\)에 대해 유일한 물리적 국소 해가 존재한다.

더 구체적으로, 물리적 영역 안의 닫힌 공 \(\mathcal B_r(Y_-)\)에서
정규화한 변수의 norm으로

\[
M_0=\sup\|\mathcal S_h\|,\quad
L_0=\sup\|D_Y\mathcal S_h\|,
\qquad hM_0\le r,\quad hL_0<1
\]

이면 Picard 반복이 그 공 안에서 수축한다. 반복의 오차도
\((hL_0)^k\|Y_1-Y_0\|/(1-hL_0)\)로 제한된다.
이것이 전체 atomic stage에 대한 조건부 구성이다. 특정 입력 상자의
\(M_0,L_0\) 수치를 인증하고 큰 시간 간격으로 이어가는 문제를 다음
이론 의무로 좁혔다.

## 9. 양의 흡수 예제와 부모 단계의 회복

온도 \(T_0=50000\) K, 내부 조성의 정지 기체에 23 eV HI 광자를 흡수시키는
명시적 family를 구성했다. H당 흡수 수 \(\xi>0\)에 대해

\[
x_+=x_0+\xi,\quad r_+=r_0+\epsilon\chi_H\xi,\quad
E_+=D(r_0+\theta_0+23\epsilon\xi).
\]

단일 beam에서는 \(\mathbf M_+=23D\epsilon\xi\mathbf e_z\)이며, rapidity
매개변수로 \(\xi,w_+,\beta_+\)를 모두 유리식으로 구했다. 실제 endpoint
opacity로 양의 초기·최종 photon inventory를 역구성해 finite backward
Euler 식을 정확히 만족시켰다. 작은 양의 매개변수에서 조성, warm 온도와
Doppler energy 구간이 유지됨을 증명했다.

동일한 반대 두 beam이 각각 \(D\xi/2\)를 흡수하면 운동량이 상쇄되고

\[
T_+=\frac{d_0T_0+T_{\rm exc}\xi}{d_0+\xi},\qquad
T_{\rm exc}=\frac{2\epsilon(23-\chi_H)}{3k_B}
=72733.757372464264931\ldots\ {\rm K}.
\]

따라서 \(0<\xi<1-x_0\)의 모든 pair reference는 두 온도 사이에 있다.
이 예제는 다른 channel increment를 0으로 지정한 HI absorption 검증용
구성이다. 채택된 전체 FT03 모델의 CI/RR/DR는 앞 절의 국소 정리에 들어간다.

전체 모델에서도 초기 정지 기체와 동일한 반대 photon pair·source는 반사
대칭을 갖는다. 유일한 국소 해에서 속도가 0으로 유지되고
\(\mathcal K_\gamma=0\)이 되어, geometry를 고정한 부모 scalar stage가
그대로 회복된다.

## 10. 실제 검산, 교정과 구현 상태

| 항목 | 확보 상태 | 증거 |
|---|---|---|
| M01 Doppler·사건 정규화 | 유도 + 실제 tensor/scalar 검산 | 유도 S7–S9, xAct 결과 |
| M02 finite photon/species/gas/escape | 유도 + exact finite balance | 유도 S10–S15, scalar 결과 |
| M03 원시 변수 회복 | 전역 단조 증명 + exact 역대입·bracket 검산 | primitive P7–P26 |
| M04 유한 열 보정 | 직접 투영·EOS 소거·연속극한 + 실제 검산 | 유도 S22–S30 |
| M05 전체 stage | 매끄러운 내부의 국소 존재·유일성 및 수축조건 증명 | 유도 S16–S21 |
| M06 양의 예제 | 명시적 one-beam·pair 구성 + exact 검산 | primitive P33–P55 |
| M07 구현 연결 | 함수·상태·단위·정의역·참조값 계약 작성 | CODING_CONTRACT |
| native/ODE 구현 | 해당 CODING 의무에 남김 | 다음 DAG |

실제 xAct 첫 두 시도는 dummy index가 helper의 free index와 충돌해
중단됐다. 동치인 current 전개로 고치고, stress에서 current를 다시
확인하는 식을 추가한 최종 실행에서 25개가 모두 통과했다. 원래 입력과
실패 출력도 보존했다.

Wolfram의 최종 Jacobian 부등식 하나는 첫 방법에서 판정되지 않았고,
같은 식의 비음수 계수와 엄격양의 단항식을 확인하는 별도 exact 계산으로
닫았다. 물리적 가정을 바꾸지 않았으며, 나머지 성공 항목은 재실행하지
않았다. 세부 분류와 runtime은 [EXECUTION_RECORD.md](../evidence/EXECUTION_RECORD.md)에 있다.

## 11. 코딩 연결과 다음 연구점

현재 receiver의 `ConditionalStage`에는 기체 속도, lab 총에너지·운동량과
원시 변수 회복기가 없다. 따라서 새 단계는 photon 단위 변환, conservative
gas state, primitive adapter, 공통 사건 ledger를 명시적으로 추가해야 한다.
기존 azimuth ring은 기체 속도가 축 방향일 때 그대로 쓸 수 있다.
횡방향 속도에는 azimuth를 나눈 양의 quadrature 또는 실제 각도 적분이
필요하다. Doppler energy에서 rate와 provider guard를 평가한다.

기존 `HERE_RUX03_PRIMARY_PROVIDER_03` 및
`HERE_RUX03_COVARIANT_MOMENTS_04`의 CODING 의무는 유지한다.
이번 구성의 구현 노드는 `HERE_RUX03_MOVING_GAS_STAGE_05`다.
원래 소유 DAG `RUX02 + RUX03 → RUX04 → RUX05`를 유지하며, 별도
all-Bianchi·상대 species tilt D2.3 문제와도 섞지 않는다.

**다음 THEORY의 첫 작업은 full atomic rate의 구체적 warm/energy 상자에서
\(M_0,L_0\) 또는 잔차 Jacobian을 정량적으로 제한하는 것이다.**
그 제한을 이용해 실제 step bound와 continuation criterion을 만들고,
해가 물리적 정의역 경계에 닿는지 또는 Jacobian 가역성을 잃는지 구별한다.
이미 닫힌 four-force, binding ownership과 원시 변수 단조 증명을 다시
확인하는 단계로 돌아갈 필요는 없다.

## 12. 읽기 순서와 전체 자료

1. 본 보고서: 결과와 물리적 연결.
2. [MOVING_SOURCE_AND_THERMAL_BALANCE.md](../derivations/MOVING_SOURCE_AND_THERMAL_BALANCE.md): 전체 stage, 국소 정리와 유한 열 보정의 증명.
3. [PRIMITIVE_RECOVERY_AND_EXAMPLES.md](../derivations/PRIMITIVE_RECOVERY_AND_EXAMPLES.md): inverse·stable gap·warm range·흡수 family의 완전한 식.
4. [CODING_CONTRACT.md](CODING_CONTRACT.md): 입력·출력·잔차·solver·검증 계약.
5. [DECISION.md](../review/DECISION.md), [EXECUTION_RECORD.md](../evidence/EXECUTION_RECORD.md): 독립 판정과 실제 실행 근거.
6. [HANDOFF_KO.md](HANDOFF_KO.md), [NEXT_DAG.json](NEXT_DAG.json): 다음 소유자와 정확한 재개점.

이 자료의 science manifest는 파일별 바이트 수와 SHA256을 고정한다.
게시·백업의 실제 식별자와 확인 범위는 별도의 전달 기록에 둔다.

### 일차 문헌

- Younsi, Wu, Fuerst (2012), [arXiv:1207.4234](https://arxiv.org/abs/1207.4234), eqs. (9)–(17).
- Sądowski et al. (2013), [arXiv:1212.5050](https://arxiv.org/abs/1212.5050), §3.3–3.4, eqs. (54)–(56).
- Wu, Tang (2015), [arXiv:1504.07707](https://arxiv.org/abs/1504.07707), Lemma 2.1.
- Cai, Qiu, Wu (2023/2024), [arXiv:2305.14805](https://arxiv.org/abs/2305.14805), pressure-root branch와 Newton convergence의 구별.
