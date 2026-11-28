# THEORY R1–R10 실행 대응

단위: HERE_RUX03_MOVING_GAS_SOURCE_05.
운영 규약: physmath-research-loop 1.0.0 / 승인 design v0.2.
날짜: 2026-10-13 KST.

**기록 상태: author_complete.**
**Independent decision reference: review/DECISION.json.**
실제 최종 판정은 DECISION 한 곳에서 확정한다. 아래 단계는 작성 시점의
작업 snapshot이며, R6·R8의 최종 상태는 독립 판정을 참조한다. 실제 최종
종료·게시 완료는 별도 closeout과 delivery receipt에서 기록한다.

## R1–R10

| 단계 | 현재 상태 | 실제 수행·근거 및 남은 의무 |
|---|---|---|
| R1 연구 위치·계약 | complete | 직전 THEORY04 handoff의 moving-gas 의무를 재개했다. 고정 Eulerian tetrad·체적, \(D=\gamma n_H\), full retained warm Case A, common endpoint와 7변수 residual을 SCIENTIFIC_CONTRACT.md에 고정했다. Native/ODE campaign을 이 THEORY 단위에 추가하지 않았다. |
| R2 근거·재사용 | complete | 현재 BASS PR32·receiver PR114의 동일 head 및 관련 state/normalization을 확인했다. Source·reuse identity를 source_map에 보존하고, THEORY04의 45개와 PRIMARY_THEORY03의 47개 check group을 재실행 없이 연결했다. 독립 reviewer가 네 고유 일차 논문의 지정 절을 읽어 invariant opacity, conservative implicit source, known primitive theorem과의 대응을 LITERATURE_MAP.md에 정리했다. |
| R3 주장·전제 정렬 | complete | M01–M07의 정의역·closure·역할을 SCIENTIFIC_CONTRACT와 CLAIMS.json에 연결했다. Proper 사건률과 lab 적분 count, gas thermal/binding과 full lab energy, 고정 조성 primitive inverse와 coupled local stage, cold 수학적 경계와 warm provider 범위를 구별했다. |
| R4 가설·표현 탐색 | complete | Full lab conservative 변수와 endpoint rest-frame thermal 표현을 같은 사건으로 연결하는 표현을 선택했다. Photon node를 정확히 소거하고, primitive 회복에는 pressure 식과 positive thermal-enthalpy excess 식을 대응시켰다. One-beam·opposite-pair reference로 recoil과 pressure correction을 판별할 구성을 얻었다. |
| R5 구성적 유도 | complete | MOVING_SOURCE_AND_THERMAL_BALANCE.md에서 Doppler/current, invariant event normalization, finite total energy·momentum, \(\mathcal K_\gamma\), smooth limit, IFT와 contraction 충분조건을 유도했다. PRIMITIVE_RECOVERY_AND_EXAMPLES.md에서 known cone theorem을 재유도하고 단조성·stable gap·정확한 도함수·warm subdomain·양의 HI23 eV family를 증명했다. 수치 \(M_0,L_0\) bound는 다음 정량 continuation 의무로 특정했다. |
| R6 독립 검증 | decision_ref | 별도 reviewer가 원전·적용 가정을 확인하고 known gamma-law theorem의 신규성 문구 교정을 요청했다. Primitive §9의 해당 문구만 교정했다. 후보 전체와 실제 raw/result를 대상으로 하는 독립 최종 상태는 review/DECISION.json을 참조한다. |
| R7 판별 검증 | complete | 실제 Wolfram/xAct final 25/25, primitive 18/18, root finite/clock/Jacobian final aggregate 12/12를 확보했다. 초기 xAct dummy-index 구현 오류 두 건과 CAS conditional inequality 하나를 원본으로 보존했다. Jacobian의 미결정 항목만 coefficient certificate로 보완했으며 닫힌 11개 root 항목은 다시 실행하지 않았다. |
| R8 결과 판정 | decision_ref | 각 claim의 derived·actual-check 상태와 의무를 CLAIMS.json에 기록했다. 최종 사용 결정은 독립 review/DECISION.json 한 곳에 둔다. 이번 단위에는 새 strong no-go 후보가 없다. |
| R9 정식 결과·코딩 연결 | complete | 두 proof와 actual evidence, CLAIMS·HANDOFF·LOOP, CODING_CONTRACT.md, NEXT_DAG.json 및 REPORT_KO.md를 작성했다. 기존 PRIMARY_PROVIDER_03 및 COVARIANT_MOMENTS_04의 coding pending을 보존한다. 최종 artifact identity는 freeze manifest에 연결한다. |
| R10 종료·재개 | in_progress | HANDOFF에 full rates warm/energy box의 \(M_0,L_0\) 정량 certificate와 구체적인 첫 구성·완료 근거를 남겼다. Source·과학 증거는 확보되어 있고 최종 review, Git 게시 및 create-only backup의 실제 receipt는 후속 delivery 작업에서 기록한다. 이 초안은 게시 성공을 선기록하지 않는다. |

## 실제 계산의 집계 단위

수학적 결과는 M01–M07의 **7개 claim family**다. 한 family에 정의·lemma·
보존 identity·local theorem·reference가 함께 들어갈 수 있으므로 이 수를
독립 정리의 개수로 바꾸지 않는다.

| 실제 suite | 최종 PASS/대상 | 실행 근거 |
|---|---:|---|
| xAct tensor | 25/25 | evidence/XACT_MOVING_SOURCE_EXECUTED_v3.wl, XACT_MOVING_SOURCE_RAW_v3.json, XACT_MOVING_SOURCE_RESULT.json |
| Primitive | 18/18 | derivations/PRIMITIVE_EXACT_CHECK.wl, evidence/PRIMITIVE_WOLFRAM_RAW_RESULT.json, PRIMITIVE_EXACT_RESULT.json |
| Root finite·clock·Jacobian | 12/12 | evidence/MOVING_SOURCE_WOLFRAM_EXECUTED.wl, MOVING_SOURCE_WOLFRAM_RAW_RESULT.json, MOVING_SOURCE_EXACT_RESULT_v1.json 및 targeted positivity input/raw/result |

세 suite의 raw 관측 수 합계는 **55 named groups**다. Primitive
positive-factor와 root의 Jacobian이라는 선언된 중복 목표 1개를 합치면
**54개 검사 목표**다. 이 수치들은 독립 정리의 개수가 아니다.
다른 scalar/tensor 표현의 물리적 교차 검증도 유지한다. 기존 45개·47개,
실패 입력 두 건, 미결정 1개와 그 보완을 추가 성공 개수로 중복 집계하지
않는다.

Primitive suite는 17개 exact algebra/derivative group과 1개
decimal-as-rational warm-fixture inequality group이다. Positivity·
bijectivity·IFT·continuation의 정량 조건은 proof에 있고, CAS group의 성공
수로 그 논증을 대체하지 않는다.

최종 actual runtime은 Wolfram Language 15.0.1이다. xAct final은
xTensor 1.3.0을 로드했고 xPermExternalBackend=false로 기록되었다.
Native build, chemical RHS, ODE/history, parameter scan의 새 실행 수는 0이다.

## 관측한 실패와 최소 교정

### EX01 — 초기 xAct dummy-index 구현 오류

- 관측: package load 뒤 최종 반환이 Hold[Throw[Null]]이었다.
- 분류: implementation index-hygiene error. 고정 내부 dummy b를 쓰는
  Cp[i_]:=-Tp[i,b]normal[-b]를 Cp[b]로 호출하여 free/dummy index가 충돌했다.
  원인 진단은 evidence/EXECUTION_RECORD.md에 있다.
- 보존: evidence/XACT_MOVING_SOURCE_EXECUTED_v1.wl,
  XACT_MOVING_SOURCE_RAW_v1.json.
- 교정·결과: helper를 동치인 전개 current로 바꾸고
  -Tp[a,b]normal[-b]-Cp[a]라는 stress-current 검산을 추가했다.
  실제 final v3의 25개 tensor group이 통과했다. 최초 실패를 성공으로
  소급하거나 과학 반례로 해석하지 않았다.

### EX02 — 진단용 호출에서 확인한 동일 dummy-index 충돌

- 관측: debug phase와 일부 named check를 출력한 뒤 Hold[Throw[Null]]로
  끝났다. 전체 tensor 결과가 완결된 호출은 아니었다.
- 분류: implementation index-hygiene error. 진단 출력은
  M03_conservative_momentum에서 동일 dummy-index 충돌을 특정했다.
- 보존: evidence/XACT_MOVING_SOURCE_DEBUG_v2.wl,
  XACT_MOVING_SOURCE_RAW_v2.json.
- 교정·결과: EX01과 같은 동치 current 및 독립 stress-current 검산을
  포함한 final v3의 input/raw/normalized 결과로 완료를 확인했다.

### EX03 — Jacobian positivity의 CAS 미결정

- 관측: root scalar 최초 결과는 11 PASS와 primitive_jacobian_positive의
  false 표시였다. 실제 evaluatedAssertions에는 FullSimplify가 끝내
  판정하지 않은 조건부 부등식이 남아 있다. TrueQ의 false가 음의 determinant
  또는 반례의 발견을 뜻하지 않았다.
- 분류: symbolic-method unresolved assertion.
- 보존: evidence/MOVING_SOURCE_EXACT_RESULT_v1.json 및
  MOVING_SOURCE_WOLFRAM_RAW_RESULT.json.
- 최소 교정: derivations/MOVING_JACOBIAN_POSITIVITY_REFINEMENT.wl에서
  비음수 다항계수와 \(a_r^3g^5\)의 양의 계수 1을 실제 확인했다.
  정의역은 \(a_r>0,g\ge1,p\ge0,\alpha-2\ge0\)다.
- 결과: MOVING_JACOBIAN_POSITIVITY_RAW_RESULT.json와
  MOVING_JACOBIAN_POSITIVITY_RESULT.json의 certificate가 그 항목을
  닫는다. Final MOVING_SOURCE_EXACT_RESULT.json은 원래 11개 PASS와
  이 보완을 합친 12/12이다. 닫힌 11개를 재실행하지 않았다.

## 독립 검토의 서술 교정

Reviewer는 primitive §9의 “new mathematical results” 표현이 global cone
theorem 자체를 새 정리처럼 읽히게 한다고 지적했다. 해당 한 문구를
**Wu and Tang (2015), Lemma 2.1의 known gamma-law admissibility를 현재
\(Dr\)와 조성·단위에 맞춰 재유도했다**는 문장으로 바꿨다. 다른 증명식,
assumption, 검사 input 또는 raw 결과는 바꾸지 않았다.

신규성 문구를 교정한 당시 snapshot은 27,101 B,
SHA256 78572d6417ca22f67efd0563aa248877c865b29e474ccf0de8df6db633e3dbe5였다.
이후 root가 부모 문서 링크 3개를 immutable PR32-head URL로 바꾸었으며
증명식은 유지했다. 따라서 위 hash는 현재 freeze identity로 사용하지
않는다. 초기 author execution context도 각 시점의 관측 snapshot으로
보존하고, 현재 문서 identity는 최종 artifact manifest를 참조한다.

문헌 근거는 review/LITERATURE_MAP.md, SEARCH_EVIDENCE.json,
SOURCE_EVIDENCE.json에 있다. Exa 결과 슬롯 수, SciSpace 검색 항목 수,
실제 읽은 고유 논문 네 편의 지정 절을 각각 기록하며 전체 전문 읽기나
새 수학 정리 수로 바꾸지 않는다.

## Strong no-go·정책·재개

새 strong no-go 후보나 채택은 없다. 이 단위는 finite map, physical
primitive inverse, local branch와 양의 reference를 구성한다. 전체 source
stage의 정량 continuation은 열린 \(M_0,L_0\)/Jacobian bound 의무로
연결한다. 그 미완료 부분을 impossibility claim으로 바꾸지 않는다.

사용자 고정 물리 대상·정확도·provider closure를 바꾸는 policy override는
없었다. Dummy-index helper의 동치 교정, CAS positivity 표현의 교체,
known-theorem credit 교정은 원래 가정과 대상식을 보존했다. 별도의 로컬
파일 준비에서 발생한 JavaScript syntax/API 교정 두 건은 과학 evaluator를
호출하지 않았으며 EXECUTION_RECORD.md의 별도 기록을 따른다. 원래 owner DAG와
PRIMARY_PROVIDER_03·COVARIANT_MOMENTS_04 coding pending도 유지했다.

재개는 HANDOFF_KO.md §6과 NEXT_DAG.json의 정량 continuation 작업에서
시작한다. Final adoption은 독립 DECISION을, 실제 publication·종료 완료는
delivery receipt와 별도 closeout을 참조한다.
