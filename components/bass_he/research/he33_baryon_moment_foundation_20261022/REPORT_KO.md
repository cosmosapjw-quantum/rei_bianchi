# HE33 결과: 바리온 pressure-moment foundation

## 완료 범위

HE32의 완료된394case·그림6쌍·30단계는 재사용했다. 새 HE33은 별도 DAG의
이론 R1–R10과 코딩 C1–C10으로 기체 압력텐서의 mechanical foundation을
완료했다. 과학 구현·검산 및 C10의 게시/백업/handoff는
최종 delivery ACK에 연결된다. 현재 단원의 완료는 mechanical model의20/20이다.

새 cosmological IVP0, HE32 IVP 재실행0, render0, benchmark0, NCP0이다.
finite mechanical operator controls 및 독립 CAS 계산은 실제 새로 수행했다.

## 얻은 물리식

- pressure drift: dot P+5HP+sigma P+P sigma=−nu_pi(P−pI)+S.
- LRS: dot p=−5Hp−4sq+2Q/3,
  dot q=−(5H+nu_pi+2s)q−2ps+j.
- 열수지: dot e+3H(e+p)+sigma:pi=Q, e=3p/2.
- fixedT에 필요한 kinetic power:
  Q_iso=3Hp+6sq+(3/2)k_B T R_part.
- cone: P_perp,P_parallel>=0 ⇔ −p/2<=q<=p.

정의/유도/극한/단위/적용 조건은 THEORY_KO.md에 있다. 기존 nonbaryonic
matter stress와 새 baryon q_b의 소유권을 유지했다.

## 실행한 검산

현재 셸은 기본 cwd와 명시적 /tmp 호출 모두 SERVICE_ERROR를 반환했다.
Python/C++ 설치 실패로 해석하지 않았다. 실제 실행은 도구가 제공하는 V8에서
보존할 ECMAScript 원문을 평가하고, 별도 Wolfram 계산과 비교했다.
Node CommonJS/CLI 경로의 smoke는 NOT_RUN이며 core 검산 결과와 분리한다.

최종 source/test hash:

- core SHA256 d93e7a88f99a19e1199004bee4730eb0cd1aa250c4da069a72b49aeb07122588
- checks SHA256 fc2d69633f2e9a4573f12c63154fc0e0bc5dab57d0434b4715398b7455f66326

| 검사 | 실제 결과 |
|---|---:|
| 전체 검사 group | 17/17 PASS |
| 일반40자리 CAS oracle 최대 절대차 | 2.220446049250313e-16 |
| 강한충돌40자리 CAS oracle 최대 절대차 | 4.440892098500626e-16 |
| cone/경계/stiff 조합 | 135개, 최소 압력0 |
| semigroup 조합 | 108개, 최대 scaled차1.1102230246251565e-15 |
| 에너지 RHS residual | 2.220446049250313e-16 |
| ratio RHS residual | 1.1102230246251565e-16 |
| analytic variable-drift 수렴차수 | 2.000352,2.000088,2.000022 |
| noncommuting coefficients 독립CAS 수렴차수 | 1.999084,1.999771,1.999943 |
| 작은 projector60자리 oracle 상대차 | 4.803485728801572e-15 |
| invalid input | 10개 명시적 거절 |

실제 입력, 모든 결과 및 exact code hash는 evidence/VALIDATION.json에 있다.
표는 작은 mechanical model과 명시한 숫자 범위의 검사 결과다.

## 독립 검토에서 발견하고 수정한 오류

첫 후보는 보통 크기의12개 검사를 통과했지만, 독립검토는
작은 spectral projector의 상쇄와 fast-mode intermediate underflow를
실제 입력으로 재현했다. 이 과거 PASS와 targeted FAIL을 함께 보존했다.

F1: P=(0,1),H=0,s=100,nu=1e-8,dt=1에서 잘못된 parallel pressure는
1.915169583946289e-174였다. 60자리 MatrixExp의 값은
4.4604776197277046e64다. 작은 projector를 rationalize하고 log로 유지했다.

F2: P=(1e-100,1e100),H=0,s=130,nu=0,dt=1에서 이전 parallel 출력은0,
실제 directional redshift 해는1.4684846469095248e-126이었다.
최종 압력까지 양의 spectral contribution을 log-sum으로 계산하도록 고쳤다.
clip/renormalization은 없다. 수정된 step/invariants에 의존하는17group을 실행했다.

## 수치 선택의 의미

H=.2,s=.14,nu_pi=1e8,dt=.1,P0=(1,1)에서 exact frozen operator의
q/p는 −2.800000134279129e-9이고 독립 CAS는
−2.799999992159999978e-9다. 반면 drift-half/충돌/drift-half의
q/p는 −0.01390065209951809다. 양성성만으로 stiff 정확도가 따라오지 않아
full frozen exponential을 채택했다.

Midpoint freezing의2차 수렴은 smooth manufactured histories 두 개에서
검사했다. 시간의존 stiff 초기층 전체의 uniform-order나 실제 실행속도 개선을
주장하지 않는다. 이산화/roundoff/물리 closure의 오차를 분리한다.

## 아직 필요한 실제 물리

nu_pi는 prescribed model parameter다. 전자/이온/중성의 실제 모멘트
relaxation과 종간 에너지 교환, photo/RR/CI/DR/CX의 thermal/source moments,
원자 binding/radiation energy, metric feedback은 NEXT_DAG.json의 의존성이다.
이 단원의 manufactured pressure 결과를 HE32 baryon-stress 예측으로 사용하지 않는다.

PHYS79의 source-domain 자료는 재사용한다. 20000K≈1.723eV에서
HeII/LiII/LiIII CI source minima의 공백을 확인했으므로 full6 CI를
묵시적으로 켜지 않는다. 추가 종·분자·fully reactive nuclear network는 별도 범위다.
