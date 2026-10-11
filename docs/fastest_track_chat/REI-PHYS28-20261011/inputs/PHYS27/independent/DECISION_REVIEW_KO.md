# PHYS27 독립 최종 판정

**결정: PROMOTE_SCOPED · Physical HOLD 유지**  
검토자: `/root/phys27_decision` · GPT-6 Astra · distinct final decision reviewer  
검토 방식: **NONBLIND**, full-history 노출. 후보 생성·과학 수치 설계·첫 실행·portability 실행에는 참여하지 않았다.

## 1. 무엇을 승격하는가

평균 18 eV, 광자 지원구간 [13.61,24.58] eV, 균일 대역 반폭 δ=0.05 eV 하나, 동결 source-real 상수와 직렬화 수치 J라는 계약 안에서 다음 결과를 **연구 보고와 다음 루프의 닫힌 입력으로** 승격한다.

- 실제 광자 분산과 중심 분산의 정확한 관계 및 전체 허용 분산 범위.
- 모든 허용 분산에서의 sharp 응답 구간, 두 극값 중심 측도와 실제 밀도의 유일성, 양 끝 퇴화, 엄격 단조성.
- 같은 실제 광자 분산에서 PHYS26 응답 구간의 엄격한 안쪽에 들어간다는 정리.
- 명시적인 수치 지원 끝값 부호에 조건부인 두 정확근의 존재, 전체 strict/nonstrict 부호 지도와 문턱의 안쪽 이동 방향.
- 두 문턱의 제한된 소수 근사와 W=19.74의 구체적 유한 대역 예, 사전 고정 수치 프로그램의 실제 실행 및 별도 경로 byte 재현성.
- δ→0의 경계 응답 수렴과 극값 측도의 약한 수렴, 명시한 부호 전제 아래의 근 수렴.

이 판정은 정확 정리, 수치 관측, 구현 재현성을 서로 대체하지 않는다. **물리 방출원 admission, 유한 시간 history, J·원자 데이터·기체 상태의 불확실성, native 동등성, 전체 연속 스펙트럼, 세계 최초성은 승격하지 않는다.**

## 2. 고정 후보와 실제 읽은 범위

검토 대상은 `evidence/CANDIDATE_FROZEN.json`이다. 실제 파일은 **15804 bytes**, SHA256 **2e5ecca4aa8bdfd594fff868dc6462d9231ba98f4b3fb494e24ad3addfcb0e87**이며, 열거한 **87/87 payload**의 크기와 SHA256이 일치했다. 물리 계약은 **8458 bytes**, SHA256 **46fe6fb98a78ca549f27ed78968850c14bdc12cdd3250892f28e239574005443**으로 일치했다. 첫 수치 전 동결 목록의 13개 파일도 현재 원본과 일치한다. 이 identity 검사는 내용의 물리적 타당성을 대신하지 않는다.

현재 이론 유도와 15개 theory claim, 물리 계약, 보고서, claim DAG, 수치 코드 전체, PROTOCOL/PREEXECUTION/EXECUTION, 수치 해설을 실제로 읽었다. 원 JSON은 모든 bytes를 읽고 파싱했으며, 상수·끝값·근·9개 분산·혼합·405개 check와 두 80행 이분법 history를 대상으로 정적 산술 대조를 했다. 보고서 요약의 수치·근 diagnostics·대표 스펙트럼·혼합·실행 정보가 원 관측을 그대로 옮겼는지 확인했다. PNG도 실제로 열어 축·단위·대역 확률·두 문턱의 표시를 확인했다.

Portability 프로토콜·동결·wrapper 코드 전체·실행 receipt·started 기록과 역할 provenance를 읽었다. ZIP 안의 기존 15개 stage payload를 bytes로 읽어 identity를 확인하고, 첫 결과와 실제 replay 결과를 다시 비교했다. **새 경로 복구나 replay를 이 검토자가 또 실행하지는 않았다.**

과거 연구는 지정한 닫힌 전제로만 소비했다. PHYS26 원 유도의 1–110행에서 물리 정의·정규화·곡률 전제를 읽었고, 기존 결정 JSON의 decision/promoted scope/limits/protected 및 필요한 극값·단조성 claim 결정을 읽었다. PHYS26 원 결과의 W=8 상한 음수, W=26 하한 양수 레코드를 읽었다. PHYS24/25 도함수 원 인증 전체를 새로 감사하거나 과거 프로그램을 실행하지 않았다. Rust는 HI fit 전체, 초기 광자 수·기체 상태, binding energy, shear·cgs 상수의 필요한 구간만 읽었으며 전체 저장소를 의미적으로 읽었다고 하지 않는다. J의 두 전체 직렬화 값은 원 PHYS22 데이터와 실제 대조했다.

GPT-6 Astra 하네스 v4.0.0의 core, phases 06/08, EVIDENCE_AND_CITATION, STOP_RULES와 state를 실제로 읽었다. 하네스의 `NOT_RUN` state는 템플릿이며 과학 실행 증거가 아니다. 각 원 파일의 hash와 구체적인 read scope, 판정별 근거는 [DECISION_REVIEW.json](DECISION_REVIEW.json)에 있다.

## 3. 수학·물리 연결에 대한 판정

**모멘트와 정규화 — PASS.** 실제 광자 밀도는 중심 법칙 Q와 Uniform[−δ,δ]의 convolution이다. 광자 수 기준의 질량 1, 평균 m, 그리고

\[
W=V+\delta^2/3
\]

를 직접 적분으로 얻는다. 중심 구간을 [a+δ,b−δ]로 제한하므로 모든 대역은 잘림 없이 원 지원구간 안에 든다. 비음수 모멘트 항등식과 명시적 두 중심 법칙이

\[
W\in[1/1200,850231/30000]\ {\rm eV}^2
\]

의 필요충분성을 제공한다. N0가 커널에 이미 포함되어 있으며, `/180`은 기존 `/45`와 `/4`의 결합으로 한 번만 적용된다. Metric (−,+,+,+), proper seconds, w in eV/H, ε² 계수의 1/2와 시간 추가 factorial 없음이 유지된다. HI opacity cutoff와 binding energy를 혼동하지 않았다.

**전역 경계와 유일성 — PASS.** k″>0, k‴<0를 동일 매끄러운 구간의 양의 평균으로 옮기는 절차가 정당하다. 평균화된 f의 적분 Taylor 잔차 R에 대해 ∂cR<0가 전 구간에서 성립하므로 두 이차 접촉식의 majorant/minorant 방향이 맞는다. 고정 질량·평균·분산은 모든 이차식의 기대값을 고정한다. 잔차의 영 집합으로 equality support를 강제하고 질량·평균으로 가중치까지 고정했으므로 중심 측도가 각각 유일하다. 같은 극값 밀도의 다른 표현도 극값 중심 측도를 요구하므로 실제 밀도의 a.e. 유일성에 일반적인 convolution 역문제 정리를 추가할 필요가 없다.

V=0과 V=ℓh는 별도로 처리했고, 내부에서만 상·하단 간격이 엄격하다. 모든 내부 응답은 두 극값 밀도의 볼록 혼합으로 달성된다. 내부 응답의 모든 표현이 유일하거나 네 대역이 최소 개수라는 결론은 없다. dV/dW=1을 유지한 두 경계의 미분은 각각 Rv(α), Ru(β)>0이며, 이 단조성에는 f″의 부호를 사용한다.

**엄격 포함 — PASS.** 모든 유한 폭 광자 측도는 같은 실제 W의 PHYS26 허용집합에 속하면서 절대연속이다. 해당 W는 원 분산 영역의 내부이며 원 극값은 유일한 원자 측도이므로 개별 유한 대역 응답은 원 경계에 닿을 수 없다. 새 경계는 실제로 달성되므로 이 엄격성을 attained maximum/minimum에 적용할 수 있다. 이 달성 단계가 명시되어 있어 infimum/supremum에 관한 논리적 공백이 없다.

\[
A_{0,-}(W)<A_{\delta,-}(W)\le A_{\delta,+}(W)<A_{0,+}(W).
\]

바깥 부등식은 새 허용 W의 양 끝에서도 엄격하다. 이 결과를 서로 다른 임의의 양의 폭 두 개의 포함관계로 확장하지 않는다.

**영점·양화·이동 방향 — 조건부 PASS.** 두 영점의 존재에는 f(m)<0<Bδ(m)가 필요하다. 이론은 곡률만으로 끝값 부호를 선언하지 않았으며, 기존 W8 상한 음수·W26 하한 양수라는 수치 지원을 명시했다. 새 끝값 계산도 같은 부호를 수치 확인했다. 따라서 정확한 유일근 정의와 부호 지도는 그 부호 전제에 조건부다. 새 두 정확근에서 엄격 포함을 적용하고 원 경계의 단조성을 사용하면

\[
V_{*,0}<W_{*,\delta}<W_{0,\delta}<W_{0,0}
\]

가 따른다. 옛 근들이 새 허용 분산 안에 있다는 불필요한 가정을 쓰지 않았다. 존재/모든, 엄격 양수/비음수, 최소/infimum, 영 밀도의 문턱 유일성 및 혼합 구간의 비유일성을 정확히 구별했다.

**δ→0 극한 — 조건부 PASS.** 평균화 차이의 O(δ²) 해석적 한계와 노드·가중치의 연속성으로 경계가 수렴한다. 실제 광자 측도는 연속 시험함수의 연속성 계수로 원자 극한에 약하게 수렴한다. δ>0에서 불가능한 W=0과 원 최대 분산은 움직이는 허용 끝점을 따라 접근한다. 원자 극한에 대한 밀도 함수의 점별·L1 수렴을 주장하지 않았다. 근 수렴에는 원 strict endpoint sign을 유지하는 충분히 작은 폭이라는 조건이 남는다.

## 4. 수치 증거와 구현 증거

관측된 새 물리 분산 문턱은

\[
W_{*,\delta}\simeq16.6294590240,
\qquad W_{0,\delta}\simeq23.3008661823\quad({\rm eV}^2).
\]

원 값 대비 이동은 +0.289514369390, −0.119352810041 eV²이며 공존 구간 감소는 약 0.408867179431 eV², 5.77473640%다. 보고서의 변환·차이·비율이 원 JSON과 일치한다. 이 숫자는 exact-root 정의를 대체하지 않는다.

주 경로의 degree-three log Taylor jet과 별도 scalar 로그 도함수 식을 코드 전체에서 확인했다. 두 식의 k, k′ 구성 및 균일 평균의 Gauss 1/2, Simpson 1/(3n), Richardson6/8 계수가 맞는다. GL 노드 풀이와 그 exactness 검사는 응답 근 풀이와 별도로 기록되었다. 사전 고정 7개 중심은 두 root 중심과 그 anchor를 포함한다. 원 Gauss16/24 차이는 최대 4.50×10⁻⁷⁸, 별도 scalar Simpson–Richardson8 차이는 최대 1.05046×10⁻²⁸의 정규화 값이며 사전 허용오차를 통과했다. 공유 HI fit·J·Decimal 연산의 상관된 오류는 이 비교로 배제되지 않는다.

실제 첫 main의 **405개 저장 check**는 모두 PASS다. 검토자는 저장 actual/expected/residual/scale/tolerance의 산술 및 비허용오차형 predicate를 모두 대조하여 405/405 판정 일치를 얻었다. 두 근의 **160개 저장 history 행**에서 midpoint·분기·부호 유지·마지막 중심 bracket·실제 W 변환도 일치했다. 이는 저장 데이터와 구현의 정적 대조이며 F나 k를 독립적으로 다시 평가한 405개 새 과학 실험이 아니다. [정적 검토 원자료](STATIC_REVIEW_CHECKS.json), [검토 스크립트](review_existing_evidence.py).

각 근의 마지막 물리 W bracket 폭은 약 2.34425×10⁻²³ eV²다. midpoint 응답의 +1.41664×10⁻⁹⁰와 +8.24347×10⁻⁸⁹ s⁻⁴를 보존했다. 별도 quadrature 차이를 이용한 선형화 이동량은 국소 조건수 진단이다. **어느 값도 정확 적분 근의 directed interval enclosure나 물리 오차 한계가 아니다.** 새 문턱의 제시 자릿수는 프로토콜의 최대 12 유효숫자 범위를 지킨다.

W=19.74의 두 실제 두 대역 밀도는 같은 질량·평균·광자 분산에서 서로 반대 부호를 낸다. 정확 경계값으로 정한 θ 혼합이 정확한 영 응답을 보장하고, 수치 네 대역 결과의 `0E-144`와 affine 잔차 `2E-145`는 유한 산술 기록으로만 다룬다.

| 실제 실행 구분 | 관측 범위 |
|---|---|
| 첫 PHYS27 과학 main | 1회, exit 0, 405/405 PASS |
| 첫 응답 근 / 커널 | 2개×80회 / 3923회 |
| 첫 quadrature 노드 | 20개, Newton 총 118회 |
| 별도 새 프로그램 replay | 1회, exit 0, 결과 305521 bytes 동일 |
| 실제 PHYS27 main 합계 | 2회; 그중 1회는 재현 |
| 표시용 scalar 값 | 5508개, 독립 검증 credit 0 |
| 이 최종 검토자의 새 science·kernel·root·replay | 모두 0회 |
| 과거 main/suite·새 곡률 campaign·native·gas IVP | 모두 0회 |

첫 raw/replay의 공통 SHA256은 **3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314**다. 실제 byte와 parsed JSON 모두 일치했고, stage의 15개 payload도 일치했다. 재현의 독립 물리 credit은 0이다.

## 5. 발견 사항과 남은 완료 단계

**현재 후보의 과학 승격을 막는 fatal issue는 발견하지 않았다.** 최초 과학 실패·수치 실패·과학 코드 사후 수정·허용오차 변경은 기록상 0이며, 화면 출력 절단·잘못된 read 경로·문서 생성 구문 오류 등은 별도 도구 사건으로 보존되어 있다. 이 검토에서도 긴 도구 출력이 일부 잘려 필요한 근거를 작은 범위로 다시 읽었다. 절단된 원문 전체를 읽었다고 세지 않았다.

한 가지 비차단 문서 해석 한계를 남긴다. 보고서 §9의 근거 표에 있는 ‘최종 묶음의 identity 검증’은 이 gate 시점에는 **최종 closeout 항목**이다. 지금 검증된 것은 후보 87개와 기존 portability stage·실제 replay다. gate 이후 만드는 최종 연구 ZIP의 복구 검증, 같은 branch의 추가 문서 게시·선택 원격 readback, 최종 전달은 **아직 pending**이며 이 판정이 완료를 인증하지 않는다. 동결 후보 파일을 이 검토자가 수정하지 않았고, 후속 detached publication receipt의 실제 증거로만 이 항목이 닫힌다. 보고서의 상단·JSON authority는 최종 판정과 publication receipt를 구별하므로 이 주석으로 범위를 명확히 할 수 있다.

하네스 및 현재 owner state의 과거 `IN_PROGRESS` 문구도 판정 시점의 완결 증거로 사용하지 않았다. candidate freeze가 state를 명시적으로 제외했으므로 owner가 gate 결과와 실제 게시 결과를 반영해 closeout을 작성할 수 있다.

## 6. Phase 8 결정과 종료

Evidence, 수학·물리 의미, 검증가능성, 제한된 수치 견고성, 계산 가능성, 가정의 공개, 원래 연구 동기의 보존을 각각 검토했다. 유한 폭족이라는 새 제약과 PHYS26 원자족의 차이가 분명하고, 그 차이를 같은 실제 W에서 증명했다. novelty/priority는 별도 조사하지 않아 미승격이며 종합 점수로 대체하지 않았다.

검토자는 후보 생성자나 과학 검증 설계자와 분리되어 있으므로 Phase 8의 distinct decision 조건을 충족한다. Full-history 노출 때문에 blind prediction credit은 0이다. 필수 과학 근거와 한 번의 집중 최종 검토가 충분하므로 **추가 커널 계산·근 탐색·전면 재감사·recursive reviewer를 종료**한다. owner는 이미 승인된 최종 묶음 검증과 게시·전달을 이어 갈 수 있다.

다음 질문 **PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY**는 인수문에 적힌 **제안 / NOT_RUN**으로만 소비한다. 일차 이동계수나 δ=.05 선형 예측은 이번 루프의 결과가 아니다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED.** 생산 source/default/runtime 변경은 0이며 이 판정은 보호 상태를 바꾸지 않는다.
