# BASS_HE R10B: Q23 기하학적 중복 노드와 보간 rank 손실

## 결론과 범위

R10A의 SURROGATE_REBUILD_UNRESOLVED와 탐색적 적분값 격리는 그대로 보존한다. 이번 노드는 기존 파일만으로 Q23 실패의 원인을 재현하고, 새 fitting view의 제한된 수정 효과를 검사했다. 새로운 spectral/Delta solve, transport/단면적 적분, author FORTRAN 실행은 0회다. PR15 production source와 기존 R10A 증거를 수정하지 않았다.

확인한 PR17 기준은 5954d5d31d1c4536b41e13b4868aa5fa97cd2924이다. 입력 archive는 640,484 bytes, SHA256 2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75이며 이번 작업을 위해 Drive에서 회수한 원본의 SHA256과 ZIP CRC를 확인했다. 입력은 archives/receipt의 선언만 믿은 것이 아니라 실제로 읽었다.

## 1. 원인: 하나의 기하학적 midpoint, 두 개의 binary64 좌표

Q23 support Rb=9.212477692166999에서 최초 GK7 중앙점은 sqrt(Rb^2/2), 추가 split 경계는 Rb/sqrt(2)로 생성됐다. 둘 다 수학적으로 u/Rb^2=1/2이다. 그러나 저장 rho는 다음처럼 다르다.

- 기존 parent GK7 중앙점: 0x1.a0e8bdf74847dp+2
- 추가 split midpoint: 0x1.a0e8bdf74847cp+2
- rho 차이: 8.881784197001252e-16, 1 ULP
- u=rho^2 차이: 1.4210854715202004e-14, 2 ULP

R10A 생성기는 정확히 같은 float만 set으로 제거했다. 이전 연구 handoff의 exact-float dedup 지시도 이 경우를 놓쳤다. 이는 원본 바이트와 cache key의 exact identity를 보존해야 한다는 규칙을, 기하학적으로 동일한 interpolation node를 두 번 쓰지 않아야 한다는 규칙과 혼동한 데서 생겼다. 기존 record와 cache key를 반올림해서 합치자는 결론은 아니다.

원래 24개 Q23 anchor 중 실제 기하학적 node는 23개다. 거의 중복인 두 행이 실패 query의 4점 local cubic stencil에 동시에 들어갔다. constructor는 rho가 엄격히 증가하는지만 확인하므로 1 ULP 간격은 통과했다. 이후 scaled Vandermonde가 수치적으로 rank 3이 되면서 polyfit의 singular-value truncation이 작동했다.

## 2. 동일 입력의 실제 재현과 대조

전체 repository를 실행했다고 주장하지 않는다. 현재 GitHub blob과 일치하는 eq54.py(688448971dc38e72247a167a54242361100a6771), geometry.py(9e2bc7959c49436ceb78a3ac19bda6cc108ad458)에서 AST로 DeltaSurrogate, validate_delta_surrogate, GK node 생성 함수만 선택하여 실행했다. BASS_HE 패키지 import와 과학 solver 호출은 없다.

기존 query rho=6.571108725834446, rho/Rb=0.7132835427565373에 대해:

| 항목 | 원래 24개 anchor | 수정 후보 view의 23개 anchor |
|---|---:|---:|
| local cubic 수치 rank | 3 | 4 |
| scaled-coordinate Vandermonde condition number | 5.917069719313704e15 | 139.679889423492 |
| 보간 Delta | 0.5030279345417287 | 0.5023163321097681 |
| 기존 32-panel reference 대비 상대오차 | 1.4166389817345478e-3 | 3.0509875020116615e-9 |
| 기존 64-panel reference 대비 상대오차 | 1.4166045154428908e-3 | 3.746852183319305e-8 |

기존 32/64 reference는 각각 0.502316333642329와 0.5023163509308193이다. 새 view는 추가 split midpoint record만 fit에서 제외하고 원래 parent record를 유지했다. 선택 기준은 생성 역할이며 두 record 중 기준값에 더 잘 맞는 것을 선택하는 규칙이 아니다. 실제 분석은 실패를 본 뒤 시행했으므로 사전등록되거나 blind한 검증으로 부르지 않는다.

원본 데이터는 변경하지 않았고 제외한 record도 receipt에 보존했다. 나머지 네 branch, 모든 retained ordinate, cubic 차수, polyfit/evaluation 함수, 허용오차는 그대로다. 다른 dataset의 비슷한 좌표를 자동 병합하는 일반-purpose deduplicator가 아니다.

## 3. 왜 고정밀도 또는 barycentric 치환만으로 해결되지 않는가

실패 stencil의 binary64 u와 Delta를 정확한 유리수로 변환한 뒤 Lagrange polynomial을 정확히 계산하면 Delta=0.548061958796019이다. 실패 query의 pointwise Lebesgue function 값은 약 9.88729432964348e12다. 따라서 같은 거의 중복된 입력을 더 정확히 보간하면 수치적으로 더 믿을 만한 Delta가 자동으로 나오는 것이 아니다. 가까운 두 독립 solver ordinate의 차이를 매우 큰 divided difference로 해석하는 데이터 conditioning 문제가 남는다.

수정 view의 exact-rational 보간값은 0.5023163321097679, pointwise Lebesgue function은 1.0733910042223922이며 float 평가와 일치한다. Exact rational은 주어진 binary64 데이터의 interpolation을 검증할 뿐 그 데이터가 정확한 spectral 해임을 인증하지 않는다.

Wolfram의 별도 대수 검산은 midpoint 식의 동등성, 노드 {a,a+h,b,c}의 Vandermonde determinant가 h에 선형으로 소멸한다는 것, 두 점 divided difference의 ordinate noise가 (e1-e0)/h로 증폭됨을 확인했다.

## 4. 검사 결과와 남은 불확실성

행동 실패를 먼저 관측한 TDD는 RED 3 failed(exit 1), 수정 후보 후 GREEN 12 passed(exit 0)다. 순수 archived interpolation forensics에 해당하며 repository full suite가 아니다.

- 기존 fixed holdout 30개는 모두 원래 2e-4 기준 이내다.
- 저장된 nontraining reference 50개를 재사용한 검사는 위반 0이다. 이는 새 독립 검증점이 아니다.
- 최대 상대오차는 S23에서 1.9715317060022399e-4로 gate에 가깝다. Q23 원인이 해결됐다고 모든 branch의 global accuracy를 주장할 수 없다.
- 기존 105개 GK15 좌표를 재생성하여 360개 active branch/query pair의 conditioning만 확인했다. rank-deficient pair는 1개에서 0개로 줄었다. stencil이 바뀐 query는 두 개다.
- 새 view의 contiguous cubic stencil 44개는 모두 full rank이며 최대 condition number는 139.68이다.

conditioning 검사와 reference accuracy 검사는 다른 것이다. 대부분의 GK15 pair에는 아직 직접 계산된 reference가 없으며, fixed holdout PASS 또는 embedded quadrature estimator는 그 오차를 보증하지 않는다. 새 view는 RESEARCH_VIEW_PREPARED 상태이고 R10A 적분 admission은 여전히 unresolved다. 격리된 3.333/1.880 비율을 새 승인 수치로 재사용하지 않는다.

## 5. 수렴한 다음 계약

추가 midpoint refinement, spline/PCHIP/barycentric로의 교체, rcond 또는 tolerance 완화가 아니라 기하학적 node identity의 제한된 수리가 가장 작은 변경이다. 원본 records/cache keys는 계속 exact byte/float identity로 보존하고, fit view에만 생성 provenance를 사용한다.

준비한 package와 test를 별도 Codex context에서 검사하면 이 제한된 수리를 검토할 수 있다. 새로운 Delta 계산은 별도 수치 계약 승인 대상이다. 제안하는 후속 계약은 기존 GK15의 정확히 105 좌표/360 active pairs만 직접 검증하는 소비 지점 검사다. 같은 source/input/environment에서 이미 존재하는 reference만 재사용하고, 없는 점만 계산하며, 새 interval/query/refinement를 추가하지 않는다. 첫 2e-4 위반에서 중단하며 64-panel 진단 최대 한 번만 허용한다. 정확한 queue는 PROPOSED_QUERY_CONTRACT.json에 고정했다. 이번 R10B에서는 이 queue를 실행하지 않았다.

고정된 적분 query만 검사해도 연속 domain의 global bound는 아니다. 향후 adaptive integration이 새로운 query를 요청하면 그 점도 별도로 admission되어야 한다. 먼저 모든 consumed node와 quadrature estimator를 구분한 새 반환을 받아야 I2 정량 비교를 재개할 수 있다.

## 6. 문헌과 근거 제한

NumPy 2.3 polyfit 공식 문서는 작은 singular value의 배제, numerical rank 반환, RankWarning의 의미 및 rcond 감소의 roundoff 위험을 설명한다. 이것은 이번 rank 3 재현의 해석을 지지한다. Higham(2004)의 author abstract는 barycentric formula의 안정성에서 작은 Lebesgue constant의 중요성을 설명한다. 해당 논문이 이번 BASS_HE 오류나 특정 node 제외 규칙을 검증한 것은 아니다. SciSpace는 관련 논문 탐색에 사용했고 확정적 진술은 실제 원전 abstract/공식 문서와 직접 계산을 구분했다.

## 상태

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
R10A=SURROGATE_REBUILD_UNRESOLVED_PRESERVED.
R10B=ARCHIVED_NODE_ROOT_CAUSE_REPRODUCED_AND_REPAIR_CANDIDATE_TESTED.
독립 검토, 신규 소비 지점 reference, 단면적 정량 closure는 아직 수행하지 않았다.
