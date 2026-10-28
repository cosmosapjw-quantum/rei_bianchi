# 승인된 세 case의 과학 범위와 완료 판정

2026-10-28. Requested authority: Astra; observed runtime identity: unobserved. 이 문서는 이번 실행의 판정 기준이며 실제 PASS를 미리 선언하지 않는다. 실행 전 고정한 `rei_source_history_20261028/theory/FROZEN_CONTRACT.md`와 준비된3case를 재사용한다.

## 승인과 목적

사용자가 “제안한 작업은 실행 승인할게”라고 명시했으므로 현재 cloud에서 OFF_base, ON_base, ON_refined의 유한 실행은 승인되었다. `OWNER_IVP_OVERRIDE.json` 및 이번 `BUDGET_AUTHORIZATION.json`이 그 범위를 고정한다. main595.225063의 기존 debit과 original600을 유지하며, 이번 예약100 및 temporary700만 적용하고 종료 후600으로 복귀한다. 그밖의 NO_MORE_IVPs는 유지된다. 동일 승인에 대한 재확인은 필요하지 않다.

이번 사용자 산출물은 처방된 동일 배경에서 실제로 시간 진화시킨 n;H I/II;D I/II;T I/II;He3 I/II/III;He4 I/II/III;Li7 I/II/III/IV의17개 population과 수치 refinement 비교다. source는 명시된 현상론적 외부장이고, photon/temperature/electron bath와 hidden Li6는 저장 이력에서 처방된다. 관측 보정 및 새로운 Einstein feedback는 이 목표의 선행 조건이 아니다. 성공하면 유한 현상론적 pilot을 완료한 것으로 전달한다.

## 같은 F0–F6 ID의 두 범위

원래 `rei_fast_selected_20261028/ROUTE_KO.md`의 ID와 분모7은 보존한다. 승인된 현상론적 범위는 그 작업 흐름의 구체적인 제한판이며, calibrated physical source 범위의 완료를 소급 주장하지 않는다.

| ID | 승인된 현상론적 의무 | 완료 근거 |
|---|---|---|
| F0 | source·17상태·예약·예산 확정 | 기존 완료를 재사용, 이번 명시승인/예외 결속 |
| F1 | 같은 raw·source·단위 확보 | 기존201epoch 입력과 matched H/clock 재사용 |
| F2 | 17상태 추출·매핑 | 기존 완료와 LiIV/hiddenLi6 매핑 재사용 |
| F3 | 기준 population 그림 | 기존 완료된 baseline 그림 재사용 |
| F4 | 선택 source/rate·적용구간·초기조건 확정 | PR245 현상론적 operator와 PR246 실제 source history/QSS contract |
| F5 | 유한 처방배경 계산과 수치 검증 | 세 case 실제 완료, 고정 positivity/balance/refinement 검사 통과 |
| F6 | 확장17상태 최종 그림과 독립 검토 | 실제 렌더와 비작성자 scoped scientific review 통과 |

판정 규칙: F0–F4=5/7의 현상론적 범위 근거는 이미 있다. F5 수치PASS이면6/7, F6 렌더·독립검토PASS이면 **현상론적 fast7/7 COMPLETE_SCOPED**다. 이를 끝까지4/7로만 보고하면 사용자가 승인한 실제 진전을 누락한다. 별도 표시할 역사적 calibrated-physical fast 상태는4/7이며, 원래 전체작업33/88·중앙28/88은 해당 중앙 권한의 추가 admission 없이 유지된다. 두7분모를 합치거나88개 분모에 더하지 않는다. 기존 F0–F6 이외의 새 ID를 만들어 완료수를 늘리지 않는다.

## 고정 수치 gate의 읽는 법

모든 case가 실제 종료하고 동일 준비 time grid의 유한 raw arrays를 저장해야 한다. positivity는 저장된 stock의 scaled minimum≥−1e-9로 판정하며 값을 clipping해서 통과시키지 않는다. base/refined의 각 isotope 최대 scaled difference≤1e-5를 그대로 적용한다. 이는 준비한 출력 시점과 초기 transient samples에서의 refinement agreement이며 전 구간 rigorous global error bound나 continuum convergence order를 뜻하지 않는다. solver rtol 자체를 최종 오차로 인용하지 않는다.

augmented open-baryon/free-electron ledger 잔차는 기존1e-8 기준을 유지한다. 구현이 보존한 초기 heavy-particle stock으로만 분모를 잡는 검사는 frozen max(initial stock,absolute throughput) 기준보다 엄격한 충분조건이다. 이 선택은 허용하며 absolute throughput을 실제 측정했다고 주장하지 않는다. Bn+3BT와 hidden Li6의6배 입자수는 baryon stock에 포함한다. hiddenLi6 charge 이력은 electron bookkeeping에 포함한다.

implicit Newton/finite-difference 시도의 signed 값은 accepted physical output이 아니다. RHS는 원래 반응식을 매끄러운 다항식으로 연장할 수 있으며, solver trial마다 physical positivity를 강제하여 미분을 깨뜨리지 않는다. 실제 stock admissibility는 출력에서 따로 검사한다. fast kinetic transport는 ksU,keU,(lambda/gamma)U를 직접 사용한다. U/B나 과거QSS의 P/S를 동적 energy transport에 대입하지 않는다. OFF에서는 thermal 및 fast escape가 모두0이다. 이는 물리 closure 변경이 아니라 원래 OFF 의미와 implicit method의 정의역을 일치시킨 최소 보수다.

## 결과 해석

ON−OFF는 같은 prescribed bath에서 선택 외부 source와 escape를 켠 결과다. n/T가0에서 유한 값으로 성장하고 stable isotope/charge partition이 변하면 그것은 실제 유한모형의 예측이다. 그 크기를 측정된 천체 source의 예측이나 오차막대로 부르지 않는다. OFF와 저장 donor가 정확히 일치하지 않아도 그 자체는 실패가 아니다. donor는 photon/T/e를 자체 결합해 진화시켰지만 OFF는 저장된 bath를 재생하며 source interpolation도 고정되어 있다.

표시 단위 perHref는 evolving baryon fraction과 다르다. B=A·y+Bn+3BT+6ΣLi6라고 둘 때 f_i=A_i y_i/B이다. 두 결과의 차이에 대해 정확한 항등식은

    Δf_i = A_i (B Δy_i − y_i ΔB) / [B(B+ΔB)].

따라서 작은 총 baryon 유입/탈출과 ion partition 변화는 구별해 읽는다. frozen per-isotope scaled tolerance가 자동으로 모든 극미량 charge fraction의 상대오차를 보증하지 않는다. 이 식은 새 tolerance나 실행 gate를 추가하지 않고 최종 그림의 단위를 해석하기 위한 것이다. Wolfram Language evaluator가 이 항등식의 residual0을 실제 반환했다.

## 실패 분류와 정지

| 관측 | 판정과 최소 다음 행동 |
|---|---|
| CPU/wall/memory 제한 종료 | RESOURCE_LIMIT; 실제 prefix와 debit 보존, 뒤 case 자동실행·재시도 없음 |
| import/input schema/identity 불일치 | EXECUTION_OR_INPUT_ERROR; 해당 입력/경로만 교정 제안, 물리 no-go 아님 |
| solver status failure | NUMERICAL_SOLVER_HOLD; 반환 메시지·last time·raw status로 분류 |
| positivity/balance 초과 | NUMERICAL_ADMISSIBILITY_HOLD; 실패량과 종·시점 보고, clipping/tolerance 완화 없음 |
| refinement>1e-5 | REFINEMENT_HOLD; 유한 곡선은 보존하되 F5 완료승격 없음 |
| 모든 수치검사PASS·render/review 대기 | F5_COMPLETE_SCOPED_F6_PENDING; 완료 실행 반복 없음 |
| 모두PASS | F4–F6_PHENOM_COMPLETE_SCOPED; 최종17상태 그림 먼저 전달 |

한 fresh independent review가 최종 admission을 내린다. 이미 검증된 formula/source를 재검증하기 위한 추가 reviewer tree나 calibration gate를 만들지 않는다. 실질 결함에는 한 coherent targeted repair와 관련된 검사만 허용되며, 새 IVP attempt는 기존 no-retry/고정3case 권한의 적용 여부를 controller가 별도로 판단한다.

## 이번 실제 도구 근거

Exa로 공식 SciPy Radau/solve_ivp 문서를 조회하고 공식 페이지를 열었다. 문서의 local estimator control 및 dense-output 설명에 따라 solver completion, sampled refinement, 과학모형 admission을 구분했다: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.Radau.html . 검색 당시 문서판은1.18.0이며 실제 실행 패키지 버전의 대체 근거로 쓰지 않는다.

SciSpace의 production–destruction positivity/conservation 검색에서 Kopecz–Meister의 MPRK 연구를 찾아 저자 원문 초록 https://arxiv.org/abs/1703.05052 를 열었다. 이 문헌은 positivity·conservation·order가 구분되는 수치 설계 속성임을 확인하는 비교 근거다. 현재 Radau 코드가 Patankar method의 무조건 positivity theorem을 만족한다고 전용하지 않았고 solver 교체를 제안하지 않는다. 원문 초록 이상의 정리 검증을 주장하지 않는다.

Wolfram actual evaluator input: `Clear[a,y,b,dy,db]; FullSimplify[a (y+dy)/(b+db)-a y/b-a (b dy-y db)/(b (b+db)),Assumptions->b>0&&b+db>0]`; returned `0`, timeConstraint10. 기존 QSS CAS를 체크박스용으로 재실행하지 않았다. 이론 담당자의 local IVP/수치campaign 실행0, remote tool/저작 비용은 UNKNOWN_NOT_ZERO다.

## 실제 반환을 읽은 뒤의 범위 판정

세 case의 COMPLETED/exit0 receipt와 `PILOT_VALIDATION.json`을 읽었다. 저장361시점에201matched epoch 및 initial-transient samples가 포함되었고, 모든 case의 검사와 refinement가 PASS였다. 최대 isotope normalized difference는He3의9.4756292130907e-8로 고정1e-5보다 작다. 최대 baryon residual1.3040679647247089e-12와 최대 charge residual6.536073223449568e-13은 OFF case에서 발생했고, 고정된 보수적 absolute threshold1.0820350005000101e-8보다 작다. 저장 stock minimum scaled 값은 모두0이고, zero-B/nonzero-U 불일치0이다. 따라서 **F5_COMPLETE_SCOPED**로 판정할 실제 근거가 있다. 이 작성자의 재독은 독립 review가 아니며 F6 최종승격은 해당 reviewer의 실제 반환에 따른다.

ON_refined의 z≈2 endpoint 원CSV에는 n=7.324624081649258e-23/Href, TI=1.40155845939593e-20/Href, TII=4.501833369307673e-19/Href, Li7IV=1.4071149243049183e-14/Href가 있다. 이는 이전의 점별QSS 계산과 달리 zero-IC에서 실제 진화한 finite source model의 결과다. 총 baryons/Href는 시작1.32808000350006에서1.2057192755038328로 바뀌며 open ledger가 이를 추적한다. common escape가 켜진 열린계이므로 이 변화를 closed baryon nonconservation으로 오해하지 않는다. 관측 보정의 부재는 이번 명시적 현상론적 결과의 완료를 막지 않는다.
