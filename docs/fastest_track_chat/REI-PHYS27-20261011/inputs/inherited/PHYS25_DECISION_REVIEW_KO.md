# PHYS25 독립 최종 판정

## 1. 판정과 범위

**판정: PROMOTE_SCOPED. 물리적 채택: HOLD.**

고정 평균 18 eV, 지원구간 [13.61, 24.58] eV, 광자 수 기준 Borel 확률측도와 델타 선 허용, 직렬화 수치 Jacobian을 정확한 실수 입력으로 해석하는 계약 아래에서, PHYS25의 최소 분산 정리와 수치 평가를 연구 보고 및 후속 연구의 닫힌 입력으로 채택한다. 이 범위의 치명적 결함, blocking finding, 필수 과학 수정은 모두 **0건**이다.

최적해의 정확한 정의는
\[
(v_*-18)k(13.61)+4.39\,k(v_*)=0,\qquad 18<v_*<24.58
\]
의 유일근과
\[
P_*=\frac{v_*-18}{v_*-13.61}\delta_{13.61}
+\frac{4.39}{v_*-13.61}\delta_{v_*},
\qquad V_*=4.39(v_*-18)
\]
이다. 이 측도는 비음수 응답 문제의 **유일한 전역 최소해**이며 응답은 정확히 0이다. 원 수치 기록은
\[
v_*\simeq21.72208306483\ {\rm eV},\quad
V_*\simeq16.33994465459\ {\rm eV}^2,\quad
\sqrt{V_*}\simeq4.04226974045\ {\rm eV}
\]
를 준다. 정확한 근으로 정의한 측도와 표시된 유한 소수를 구별하는 보고서의 서술은 타당하다. [직접 유도](../contributions/variational/VARIANCE_MINIMUM_DERIVATION_KO.md), [수치 원 결과](../contributions/numerics/VARIANCE_CANDIDATE.json), [통합 보고서](../report/PHYS25_REPORT_KO.md).

이 판정은 유한 시간 HeIII 거동, 원자·기체·Jacobian 불확실성, 실제 방출원 실현성이나 물리적 채택을 승인하지 않는다. 최종 ZIP 복원·외부 게시·전달의 실제 완료는 owner의 별도 closeout과 receipt가 기록한다.

## 2. 실제 검토자와 동결 후보

검토자는 **/root/phys25_decision**, GPT-6 Astra다. Owner /root와 도함수·변분·수치 기여자 세 명과 구별되는 새 최종 판정 역할이며, 후보 생성이나 검증 설계에 참여하지 않았다. 전체 대화 이력과 결과 요약을 받은 **NONBLIND** 검토다. 역할과 판단 권한의 분리는 성립하지만, 결과에 대한 맹검·다른 물리 입력·다른 모델 계열에 의한 검증이라고 주장하지 않는다.

harness의 PROJECT_INSTRUCTIONS.md와 Phase 8 Independent Decision Gate를 실제 읽었다. 이 검토자가 실행한 과학 프로그램·근 탐색·도함수 인증·과거 suite·native·gas IVP는 **모두 0회**다. 새 감사자를 추가하지 않았고 동결된 후보 파일을 변경하지 않았다.

| 동결 대상 | SHA256 |
|---|---|
| 후보 freeze, payload 70개 | e37ab9d11dc513c40c07bfe5b9426a2e7b1acdb1629ec01b852f351fc86b40cd |
| PHYS25 보고서 | 1d117fb9a1d44fb10ba2ed18d9656e25f2fc1fe9efe5fe28ac5bf281a5f1fd5f |
| 물리 계약 | 7fce1d8729a22b89b00d8116d237af3ddcddc0951901eaa46ba821d9ed07b1c3 |
| 수치 J 입력 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |

2026-10-10 22:26:31 UTC와 22:30:29 UTC의 읽기 전용 identity 검사에서 70개 payload의 크기·SHA가 모두 일치했다. 해시는 후보의 정체성을 고정하는 근거이며, 아래의 수학적 검토를 대신하지 않는다. 전체 파일별 identity와 실제 read scope는 [DECISION_REVIEW.json](DECISION_REVIEW.json)에 기록했다.

## 3. 핵심 주장별 판정

| 주장 | 판정 | 주요 이유 |
|---|---|---|
| I0–I1: 고정 입력·닫힌 PHYS24 조건 | CONSUME_SCOPED | 같은 J·에너지 구간·정규화를 사용하며 기존 \(k''>0\), \(k(18)<0<B(18)\)를 닫힌 입력으로 소비한다. |
| C1: 최소해 존재·응답 활성화 | PROMOTE_SCOPED | 콤팩트한 측도 허용집합과 연속 모멘트로 달성을 얻는다. 양수 응답 law를 단색과 혼합하면 분산을 낮추며 영 응답에 도달한다. |
| C2: 일반 세 점 가능성과 반례 | PROMOTE_SCOPED | 세 등식 보존 가중치 제거가 타당하다. 정확한 세 점 반례는 단순 볼록성만으로 두 선 최적성을 결론낼 수 없음을 보인다. |
| C3: 실제 \(k'''<0\) | PROMOTE_SCOPED | 원 HI 적합식, 새 미분 분자, 양의 인자, 전체 구간 포함, 18개의 정확히 음수인 Bernstein 계수가 연결된다. |
| C4: 유일근과 두 선 측도 | PROMOTE_SCOPED | 엄격 볼록성으로 경로 응답의 도함수가 양수이고 양 끝의 응답 부호가 반대다. 질량·평균·분산 공식이 맞다. |
| C5–C6: 연속 dual·전역 최소성과 유일성 | PROMOTE_SCOPED | Taylor 적분 나머지의 엄격 감소가 전체 구간 잔차의 비음수성과 정확한 두 영점을 준다. 임의 Borel 측도에 적분한 부등식과 등호 조건으로 결론낸다. |
| N1·C7: 근·확률·분산·RMS·접촉 수치 | PROMOTE_SCOPED | 원식 jet, 별도 차분 경로, 사전 허용오차와 127개 첫 검사가 수치 평가를 지지한다. 수치 bracket을 엄밀 구간으로 재분류하지 않는다. |
| C8: 문턱과 엄격 양수 문제 | PROMOTE_SCOPED | 문턱 아래는 모든 law가 음수, 문턱 위에서는 양수 law의 존재를 주장한다. \(A>0\)의 infimum은 \(V_*\)이나 minimum은 없다. |
| C9: 같은 평균·분산의 반대 부호 | PROMOTE_SCOPED | 문턱에서 반대쪽 끝점 경로가 다른 law라는 사실, dual 등호의 유일성, 연속성이 국소 공존을 준다. |
| D0: 그림 | ACCEPT_DISPLAY_ONLY | 실제 PNG의 선 위치·확률·단위·접촉점·조건부 범위가 일치한다. 연속 부호의 증거는 그림이 제공하지 않는다. |
| PHYSICAL | HOLD | 기존 물리 admission 제한을 바꾸는 새 근거가 없다. |
| PHYS26 후속 질문 | ACCEPT_SINGLE_NEXT_QUESTION | 전체 고정 분산 응답 구간은 다음에 증명할 문제로 분리되어 있다. 이번 판정이 그 결과를 미리 승인하지 않는다. |

### 전역 증거를 받아들이는 이유

가장 중요한 연결은 \(k'''<0\)에서 모든 측도에 대한 부등식으로 넘어가는 부분이다. 정확한 근 \(v_*\)에서
\[
\lambda_2=\frac{(v_*-a)^2}
{k(a)-k(v_*)+(v_*-a)k'(v_*)}>0
\]
이며, 유도문의 \(H_v(E)\)는 \(E<v\), \(E=v\), \(E>v\)를 함께 다루는 Taylor 적분 나머지다. \(H_v\)의 엄격 감소 때문에
\[
h(E)=(E-v_*)^2[1-\lambda_2H_{v_*}(E)]\ge0
\]
이고 영점은 정확히 \(a,v_*\)다. 따라서
\[
V(P)-V_*-\lambda_2A(P)=\int h\,dP\ge0
\]
를 임의의 Borel 확률측도에 적용할 수 있다. \(A\ge0\) 제약에 대한 multiplier 부호가 맞고, 등호는 두 영점 지지와 유일한 가중치를 강제한다. 두 내부 선, 세 점 이상 또는 연속 스펙트럼을 누락한 최적화가 아니다. [변분 유도 §§4–5](../contributions/variational/VARIANCE_MINIMUM_DERIVATION_KO.md).

일반 세 점 반례도 직접 검토했다. \(k_{\rm ex}(x)=x^2/2+x^4/2-1/4-2x\)의 잔차 \(x^2(1-x^2)/2\)는 전체 [-1,1]에서 비음수이며 영점 세 개와 모멘트가 확률 (1/8, 3/4, 1/8)을 고정한다. 따라서 새 세 번째 도함수 조건은 실제로 필요한 논리적 진전을 제공한다.

## 4. 원 코드와 첫 실행에 대한 판단

새 도함수·수치 프로그램을 각각 전체 읽었다. 도함수 검토에서는 원 HI 적합식의 로그 미분, 이동 상수 \(\eta=\chi-J_x/J_w\), \(R\)에서 \(T\)로 가는 미분과 원식의 다섯 로그 연산자 경로, \(1/128\) 인자 및 \(E^{-3}G^{-5}\) 분모를 확인했다. 원 인증의 18개 Bernstein 분수는 모두 음수였고, 구간 포함과 나머지 인자의 양수성 및 기저 역변환 검사가 함께 보존되어 있었다. 이는 **고정 J에 조건부인 정확 산술 구현 근거**다. [도함수 코드](../contributions/derivative/exact_third_derivative_certificate.py), [원 인증](../contributions/derivative/THIRD_DERIVATIVE_CERTIFICATE.json).

수치 검토에서는 5차 로그 Taylor jet와 보통 에너지 미분으로의 변환을 확인했다. \(k'''\)의 연산자는 \(E^{-3}(D^5-7D^3+6D^2)\)이며 필요한 인자와 항이 포함되어 있다. 별도 13점 직접 차분은 정확 유리수 stencil과 65개 모멘트 항등식을 사용한다. Richardson 인자 256에 대한 설명도 5차 로그 미분의 선도 \(h^8\) 항에 제한되어 있다. 두 경로가 같은 물리식·상수·J를 공유한다는 한계를 유지한다. [수치 코드](../contributions/numerics/variance_candidate.py), [동결 프로토콜](../contributions/numerics/PROTOCOL.json).

| 첫 실행 근거 | 확인한 결과 |
|---|---|
| 도함수 | 17/17 PASS, exit 0, 한 구간, 분할 0 |
| 수치 | 127/127 PASS, exit 0, 근 탐색 3개·총 720회 |
| 차분 | 7개 에너지에서 최대 상대 차이 약 \(4.310407\times10^{-49}\), 사전 허용오차 \(10^{-38}\) |
| 입력·소스 | 같은 계약 SHA와 serialized J; 원 HI 적합식 소스 block 확인 |
| 최초 실패·과학 코드 수정·허용오차 변경 | 기록상 모두 0 |

검사 개수는 독립 물리 정리의 개수가 아니다. 표본 slack이나 차분 일치만으로 연속구간 최적성을 승인하지 않았다.

수치 중점의 응답은 \(-2.27486876684\times10^{-137}\ {\rm s}^{-4}\)다. 이 중점을 정확히 feasible이라고 주장하면 오류가 되지만, 후보 보고서는 이를 명시적으로 구별한다. 저장된 양의 위 bracket 끝점에 대한 별도 산술 기록도 **numerically feasible**이라고만 분류한다. 끝점의 원 분자 단위는 eV·s\(^{-4}\)이고 \(v-a\)로 나누면 응답 단위 s\(^{-4}\)가 된다. 추가 커널·근 평가 없이 원 결과를 보존한 처리도 타당하다. [끝점 산술 기록](../contributions/numerics/NUMERICAL_FEASIBLE_ENDPOINT.json).

정규화는 \(k=(qN_0/45)g\), \(g\) 내부의 \(1/4\), 수치 코드의 \(qN_0\kappa/180\)이 일치한다. 확률은 광자 수 기준이며 총 에너지를 \(18N_0\)로 보존한다. \(V\)와 \(\lambda_0\)는 eV², RMS와 \(\lambda_1\)은 eV, \(\lambda_2\)는 eV²s⁴다. Metric (-+++), proper seconds, \(w\) in eV/H, \([\epsilon^2]\) 관례와 추가 시간 factorial 없음도 유지한다.

## 5. 독립성·문헌·재현 범위

세 기여자의 protocol·freeze·실행·provenance를 읽었다. 도함수 기여는 기대 부호나 새 다른 기여 결과 없이 첫 실행을 했고, 수치 기여는 다른 새 결과를 받기 전에 설계와 첫 실행을 마쳤다는 기록을 갖는다. 변분 기여는 핵심 정리를 결과 통지 전에 전달한 설계 독립성과, 나중에 완성 문서에 실제 조건을 연결한 시점을 구별한다. 이 기록은 독립 원자 데이터나 독립 Jacobian을 의미하지 않는다. [실제 독립성 기록](../evidence/INDEPENDENCE_ACTUAL.json).

일반 모멘트 극점 문헌으로 Pinelis 원문 초록·정의·Theorem 1과 Proposition 9·Corollaries 10–11의 관련 부분을 직접 열람했다. 콤팩트 실구간에서 세 모멘트 등식에 대한 세 점 이하 극점 구조와의 연결은 적절하다. 실제 HeIII의 특별한 두 점 최소해는 이 문헌에서 인용한 결과로 취급하지 않았다. 문헌 전체·저널판·우선권 검색을 읽거나 수행했다고 주장하지 않는다. [Pinelis 원문, PDF pp.7–8](https://arxiv.org/pdf/1204.0249).

Owner의 portability receipt도 읽었다. 새 main 각각 한 번, 총 두 번이 exit 0이었으며 원 과학 JSON과 생성된 결과의 canonical 내용 및 원 바이트 identity가 일치한다는 기록이 있다. 이 검토자는 replay를 실행하지 않았으며 이를 새 독립 물리 증거로 합산하지 않는다. 최종 ZIP 복원과 Git 게시 readback은 판정 이후 별도 완료 기록의 책임이다. [REPLAY_RECEIPT.json](../portability/REPLAY_RECEIPT.json).

## 6. 유지할 주장 한계와 종료 결정

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 수치 J·원자 적합식·초기 기체의 불확실성, finite-time·finite-\(\epsilon\) remainder, native 산술 동등성, 실제 방출원 admission, 세계 최초성은 승격하지 않는다. 첫 초기 계수가 0이라는 사실로 유한 시간 HeIII 편차의 소멸을 추론하지 않는다.

분산 문턱 위에 양수 law가 존재한다는 결론을 모든 law의 양수성으로 바꾸지 않는다. 같은 평균·분산의 양·음 응답 공존은 현재 증명된 문턱 직후의 존재 구간까지 승인한다. 전체 분산 envelope와 비교근 23.42021899 eV²의 두 번째 전역 부호 경계 지위는 PHYS26에서 새로 증명해야 한다. [다음 단일 질문](../next/PHYS26_NEXT_HANDOFF_KO.md).

**현재 동결 후보는 이 연구 단계에서 충분하다.** 추가 과학 실행·허용오차 변경·재귀적 리뷰를 요청하지 않는다. Owner는 이 판정을 반영하여 최종 상태, 재현 묶음, 승인된 동일 브랜치 문서 게시와 전달을 완료할 수 있다.

