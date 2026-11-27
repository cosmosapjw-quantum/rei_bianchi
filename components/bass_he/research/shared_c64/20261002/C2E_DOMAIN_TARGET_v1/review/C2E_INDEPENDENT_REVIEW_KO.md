# C2e 독립 검토

판정은 **PASS_IN_DEFINED_C2E_SCOPE**다. 충돌 영역의 source authority 회수, 조건부 궤적–거리 사상, 구별된 spectral target, 후속 구현의 실행 경계가 서로 일치한다. 이는 C2 전체의 수치 closure, 실제 충돌 궤적의 채택, 전 구간 gap 인증 또는 production 승격을 뜻하지 않는다. 검토 파일의 정확한 byte identity는 동반 JSON에 고정한다.

## 근거와 실제 검토

검토자는 저자 코드와 별도로 원 사용자 계약, C1b handoff, A2 유도, C2d handoff와 의존성 권고를 읽었다. 회수된 legacy 코드·모형 계약·DR9A trajectory gate·benchmark matrix도 읽어 source 요약과 대조했다. 16개 입력의 local bytes/SHA-256, 그중 12개 Git 입력의 blob-content SHA-1이 입력 manifest와 일치했다. 이 검사는 새 remote fetch 또는 restore 검증을 주장하지 않는다.

새 유도문 두 개, spectral claims, C2e 계약, C2f 비실행 사전등록, semantic validator와 15개 manufactured counterexample tests의 코드 및 실제 PASS 로그를 검토했다. 이미 통과한 15개는 재실행하지 않았다. 검토자가 따로 작성한 `C2E_INDEPENDENT_REVIEW_CHECKS.py`는 저자 구현을 import하지 않고 `Fraction`과 양자수 열거로 22개 유리수·정수·운동학 관계를 확인했다. 새 molecular eigensolve·과학 적분·시간 전파는 수행하지 않았다. 정수 검산이 함수해석적 증명을 대신하지 않는다.

## 받아들인 결론

1. 원 요청은 0.5 및 5 keV/u를 연구 anchor로 지정하지만 공통 lab/CM frame, isotope/mass, production trajectory, 유한 b/time/R 구간이나 새 허용오차를 지정하지 않는다. Legacy A의 Coulomb lane, B/C의 straight lane, DR9A proxy 또는 REAL/EXTENDED support는 그 빈칸의 권위가 아니다. Benchmark의 native 좌표와 기존 admission 제한이 보존됐다.
2. 정지 표적에 대한 비상대론적 질량·에너지 변환, 직선 궤적의 거리 및 각속도 부호, 반발 Coulomb turning point가 보존법칙·차원·극한과 일치한다. 전하중심 O와 핵 질량중심은 분리되어 있다. Bare nuclear repulsion과 neutral entrance의 전자 screening을 동일시하지 않는다. 전자 공통 scalar를 더할 때 continuum threshold도 함께 이동한다.
3. 기존 g+bright rank-2는 지정 sector의 관측량 계산 공간이다. 제외한 dark partner가 같은 에너지를 가지므로 전체 H의 energy-Riesz projector가 아니며, retained/discarded reducing blocks의 spectral distance는 0이다. 단순한 에너지 값 집합 차로 dark multiplicity를 지워서는 안 된다는 설명이 명시됐다.
4. 큰 R의 H1s+He n=2는 full rank 5, sector ranks 3+1+1이다. 기존 g+bright는 incoming H1s를 포함하지 않는다. Ground를 합한 rank 6, 원래 D1의 최소 rank 3, 조건부 planar-even 축소는 다른 대상이다. 큰 R에서의 정성적 isolation을 특정 유한 R의 정량 gap으로 바꾸지 않는다.
5. UA norm-resolvent 유도는 Coulomb potential을 compact-support L^(3/2) 부분과 bounded uniformly continuous 부분으로 나누어 form norm의 translation continuity를 사용한다. 공통 coercivity와 resolvent factorization으로 필요한 연산자 수렴을 얻는다. Convex decomposition에 의한 H_R >= -9 E_A/2 하한도 맞다.
6. Ground를 제외한 full-space rank-5 Riesz projector가 R→0까지 continuum을 포함한 외부 spectrum과 일률적으로 분리될 수 없다는 no-go는 성립한다. Uniform lower bound와 continuum gap이 선택 에너지를 고정 음의 compact interval에 가두므로 threshold escape가 불가능하다. Norm-resolvent limit에서는 UA의 완전한 shell만 선택할 수 있으나 excited shell ranks 4,9,16,…의 합으로 5를 만들 수 없다. Rank 6도 complete-shell sum이 될 수 없다. 반면 ground+n=2의 rank 5는 가능하므로 ground exclusion은 첫 명제의 본질적 조건이다.
7. 이 no-go는 모든 finite-R rank-5 continuation의 실패를 주장하지 않는다. 양의 R_min을 갖는 compact interval, 비균일하게 작아지는 gap, symmetry-resolved target, P+Q formulation은 배제하지 않는다. 동일 projector를 연속적으로 추적하고 exterior gap이 열린다는 조건이 있을 때만 큰 R의 ordering을 유지할 수 있다는 한계도 명시됐다.
8. Static m-sector 보호를 rotating/ETF generator 전체의 독립 block으로 바꾸지 않는다. Planar reflection 축소는 실제 generator의 대칭 및 초기 상태가 그 조건을 만족할 때만 허용된다. L² projector 오차·Ritz gap·일반적 unweighted H² bound가 각각 L_y 관측량이나 연속 연산자 gap의 certificate가 아니라는 경계가 정확하다.

## 코드와 다음 단계의 판정

Validator는 frozen C2e의 지정된 의미 불변량만 검사한다. 전체 schema 검증기, 수학 증명기 또는 physical launch admission으로 쓰면 안 된다. 현재 계약과 validator의 hash는 실제 validation record에 일치하고, 어떤 validation 결과도 자체적으로 물리 실행을 켜지 않는다. 15개 테스트는 주요 source/target/claim 승격 오류의 manufactured 반례를 거부한다.

C2f의 단일 다음 단계는 대칭을 완성한 여러 상태의 target 선택 및 projector transport 구현과 manufactured 검증으로 적절하다. F1의 최종 궤적 비교를 모든 C2 구현의 선행조건으로 삼지 않으므로 원래 C2→D1→…→F1 DAG에 순환 대기를 만들지 않는다. 실제 새 전자구조 pilot은 exact R 목록·target·basis/box·guard states·새 threshold·wall/RSS/eigenstate budget을 별도로 등록한 뒤 수행할 수 있다. 그런 trajectory-independent pilot을 production collision coverage로 부르면 안 된다. 이번 C2e 계약은 새 physical launch나 D1을 열지 않는다.

## 정정한 사항과 남은 한계

검토 중 발견한 원문 행 수는 마지막 newline 부재를 반영하여 newline count 1527과 실제 splitlines 1528을 구분하고 최종 문서에서 1528로 통일했다. 원문 bytes는 바뀌지 않았다. 초기 수학 초안의 ordering 문장에는 continuous-projector 조건을 추가했고, 한국어 본문으로 정리했다. 이들은 최종 파일에 반영되어 미해결 blocker로 남지 않는다.

현재 review blocker는 없다. 하지만 production domain 선택, incoming-state solver, finite-R full-space gap enclosure, continuum 및 weighted-observable error bound, 시간/impact tail, channel truncation, NCP64 실측은 해결되지 않았다. `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `Eq55_next_node_authorized=false`, `production_default_change=NOT_AUTHORIZED`를 그대로 유지해야 한다.
