# HARMONIC10 S04 — R4/C4 후보 비교, 독립 검증 및 실행 계획

## 1. 후보를 실제 입력과 완료 가능성으로 비교

| 후보 | 구성적 이득 | 필요한 미확보 입력/비용 | 이번 결정 |
|---|---|---|---|
| 양성 second-harmonic Fourier–Bernstein 측도 | 유한 방위각 response의 orientation과 polar–azimuth coupling을 exact/outward 경계로 연결 | 선언한 계수만으로 유한 테스트 가능; 실제 계수 추정은 별도 | HARMONIC10으로 선택 |
| 임의 bivariate positive density/모든 harmonic | 보다 넓은 각분포를 표현 | 일반 positivity certificate, complexity/오차 계약 추가 필요 | 이번 단위 밖 |
| 실제 parameter uncertainty propagation | 저장값에서 물리 입력 불확실성으로 확대 | 실제 correlated mass/beam/target input와 response binding 필요 | 물리 owner 입력 대기 |
| 실제 사건률·열화·전역 species closure | 최종 physical consumer를 닫는 방향 | 원 정규화, encounter history, named deposition/thermalization 미확보 | 열린3개 입력 유지 |

선택된 후보는 단순한 workflow 문서 작업이 아니라 새 양성 측도·signed primitive·geometry/산술 합성 경계와 코드 구현이다.
제외 후보를 불가능하다고 선언하지 않으며 strong no-go를 주장하지 않는다.
계약 밖 양성 다항식의 구체적 예는 coefficient certificate의 충분조건 한계를 보여준다.

## 2. 독립 oracle와 새 검증의 사전 고정

준비된25개 unique test method는 다음 서로 다른 주장을 확인한다.

1. Cone 경계·σ 및 signed/even 입력.
2. Invalid coefficient domain, 양성이지만 cone 밖인 예의 명시적 거절.
3. 독립 decimalπ와 rational enclosure, cardinal/noncardinal/half-period 산술.
4. Signed μ² primitive,17개 orientation 표본의 독립 Decimal closed form.
5. Full/half identical detector의 coincidence·assignment·overlap 구분.
6. 비분리 full-polar 및 forward/backward closed form과 naive marginal 오차.
7. Uniform으로 줄어들 때 동일 explicitδ의 inherited 결과와 exact 일치.
8. Zero/empty, law/type/delta/geometry cap, wrap/union/half-turn.
9. Exact coefficient rotation, partner exchange·count·energy identity.
10. Manual/default width 각각의 실제 반환 경계, unresolved conditional null.
11. Fold/stopped/increasing topology.
12. Degree8·N8에서 실제 nonzero boundary bisection 및 해당 bracket52상한.
13. NIST 저장 mass·213/258/330MeV의 manufactured-law 새3rows.
14. Strip provenance와 signed 성분별 clipping 부재.

목록 숫자는 assertion 수나 독립 theorem 수가 아니다. 실제 unique method 수와 실행 평가 수는
runner가 따로 보존한다. 이전 suite의 PASS를 이번 새 suite의 PASS로 합산하지 않는다.
모든 saved plot 값은 이 최초 validation process가 직접 저장한다.

독립 이론 사전 검토는 PASS_SCOPED_THEORY_PREEXECUTION, blocking0이다.
Prepared implementation 정적 검토도 같은 recorded pass에서 진행했으며 실제 실행 증거는 아직 없다.
Root가 계약·오라클·과학 채택을 소유하고 lower-tier는 구현·runner·기계적 조립을 담당한다.
독립 reviewer는 구현을 수정하거나 science를 재실행하지 않는다.

## 3. 새 단위의 유한 예산

| 작업 | 새 CPU cap | 새 wall cap | 횟수/조건 |
|---|---:|---:|---|
| 최초 신규 validation | cumulative20s | cumulative60s | 전체 suite1회 |
| 진단된 targeted repair | 위와 동일 누적 cap 안 | 위와 동일 누적 cap 안 | reserve1회; 새 실패 원인·최소수정 승인 후에만 |
| Wolfram evaluator | 원격 실제CPU 미제공 시 null | TimeConstrained15s | evaluator1회, context lookup과 별도 |
| 저장값 plot | 10s | 30s | 최초1회, render reserve0 |

로컬 작업은 AS512MiB/process, thread1로 제한한다. Whole-process CPU는 inner runner의
Python 시작부터 종료까지와 기다린 자식 process를 포함한다. 외부 controller metadata CPU는 별도다.
모든 descendants에 대한 엄격한 aggregate 선점 cap을 구현했다고 주장하지 않는다.
Metadata 조립·commit·archive·upload는 science validation CPU에 합산하지 않으며 별도 행위다.

실행 source는 S05의 **실제 local commit + exact tree**로 고정하고
그와 same-tree인 remote 게시 commit을 별도 기록한다. HEAD와 tracked source의 일치,
해당 code hash 및 새 run directory를 검사한 뒤 최초 실행한다.
S05 내부 파일에 미래 자기 commit SHA를 써 넣지 않는다. 실제 source pin receipt를
source 게시 직후 외부에서 만들고 S06 evidence에 결속한다.

Wall/CPU 실패·traceback·raw stdout/stderr를 보존한다. 실패 후 전체 suite를 무단 반복하거나
조건을 느슨하게 바꾸지 않는다. 이전 AZIMUTH09/APERTURE07/PHOTON05/KINEMATIC08/HE101의
결과·reserve·예산을 초기화하거나 이전하지 않는다.

## 4. Wolfram과 plot의 사전 역할

한 Wolfram 프로그램은 Bernstein 정규화/반사, Machin 식과 π enclosure,
signed primitives, rotation, 비분리 oracle, coefficient 예 및 폭 상한을 검산한다.
각 literal residual·Boolean 결과·unevaluated expression을 원 응답 그대로 분리한다.
원격 CPU가 제공되지 않으면 null이며 요청 latency를 원격 CPU로 바꾸지 않는다.

Plot은 저장 JSON만 읽어 orientation, coupled/naive, native energy rows,
actual polar/arithmetic error의4panel을 한 번 PNG/SVG로 만든다.
Scientific imports/calls0, 실제 font-cache state와 renderer/source hash를 기록한다.
Parent와 reviewer는 이 원본을 읽으며 재렌더링하지 않는다.

## 5. 단계·채택·정지

S01–S10 각각의 work product를 source 게시 후 Drive·Dropbox에 백업하고 actual ACK를 보존한다.
S09에서 실제 suite·CAS·plot·같은 pass 검토가 충족된 경우 새 reference 하나를 채택하여
local9/14에서10/14로 바꾼다. 중앙 physical DAG는28/88, HE delta0을 유지한다.

S10 후 fresh central HEAD/AGENTS를 읽고 허용된 HE observation delta만 검토하여
실제 expected SHA와 force=false로 게시한다. 기존 REC/CR/B3h 및 다른 owner 상태를 보존한다.
외부 최종4문서는 POSTPUBLICATION_EXTERNAL_DELIVERY이며 Git 내부 pending snapshot과 구분한다.

그다음 새 노드·재실행·추가 예산을 자동으로 시작하지 않는다.
현재 work product R4/C4 완료, **local9/14 · central28/88**.
