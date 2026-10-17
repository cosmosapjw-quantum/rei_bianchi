# 후속 완료: 고정 기하 cohort 출생시간 연결

2026-10-17 UTC. Wolfram 및 사용자 컴퓨터 실행 없이, 기존 클라우드 Rust와 SymPy/mpmath를 사용했다.

## 실제 변경
`PositiveAgeBridge::advance_fixed_geometry_phi`를 opt-in으로 추가했다. 기존 `advance` 경로는 보존한다. 원본 MD14/BB50k 광원으로 생성되는 현재 구간의 새 cohort에는 Phi 노출을 적용하고, 이미 존재하던 cohort에는 전체 구간의 exp(-tau) 생존을 적용한다. 기존 공유 H/He/D photo 사건과 chemistry-only 후속 단계에 연결했다. 새 cohort는 timestamp 비교가 아니라 append 이전 인덱스로 식별한다.

적용 조건은 원본 background의 H=0, shear=0, 시작/중간/끝 geometry 동일이다. 이를 만족하지 않는 시간 의존 기하는 새 메서드가 거부한다. 이 정적 geometry에서 광원 z가 고정되어 MD14 rate와 스펙트럼도 상수다. 기체 opacity는 매 구간 시작 상태에 동결되므로 coupled 적분은 여전히 1차다.

부가 안전 검사: history/full-state 시각 일치, 숨은 photon bin 없음, 이전 cohort의 geometry·시각 유효성, 전진 가능한 유한 시각, 65,536 cohort 한도, 유한 누적 원장, counter checked-add. 정적 검토에서 geometry_work의 NaN 유입과 counter overflow 가능성을 발견해 수정하고 회귀 테스트를 추가했다. signed geometry_work는 음수 유한값을 허용한다.

## 의미론 제한
새 cohort의 birth_time midpoint는 방출 구간의 대표 라벨이다. 정확한 birth-age 분포/모멘트를 저장한 것으로 해석하지 않는다. 고정 기하에서는 이후 흡수가 현재 생존 개수에만 의존하므로 이 표현을 쓸 수 있다. 원래 public AgeHistory를 반환하므로 다른 legacy 메서드를 통한 혼합 사용까지 타입 수준으로 금지하지는 않는다. 이 함수 외의 mixed-mode continuation은 계약 밖이다. 입력 이전에 수행한 계산의 Phi 정확성도 인증하지 않는다.

## 실행 증거
- 1단계: 기존68+신규21=89개 전체 테스트가 통과한 고정 snapshot을 보존.
- 2단계 최종 코드: 신규 cohort9개 + 관련 기존12개 회귀 검사, 총21개 통과. 89개 전체를 최종 변경 후 다시 돌렸다는 주장은 하지 않는다.
- SymPy1.14.0에서 상수 광원 ODE 대입 잔차 및 두 구간 합성 잔차가 모두0. Phi/Psi 급수 확인.
- 앞선 Rust scalar kernel1,890행/450자리 mpmath 비교 결과 재사용. 이 결과를 전체 chemistry 오차 상계로 승격하지 않는다.
- 원본 owner_src12개 파일 변경 없음. 새 장구간 캠페인 없음. Clippy 미설치로 미실행.

누적 제한 명령20회, command wall 합19.669065s, child CPU 합19.814236s. 기존13회에서 이어 누적했고 예산을 초기화하지 않았다. 새 작업의 bounded cap은 wall300s/CPU600s이므로 이 명령 집계의 잔여는 각각280.330935s/580.185764s. 전체 프로젝트 및 계측하지 않은 시간·비용은 UNKNOWN이다.

## DAG
- P4 scalar frozen-opacity clock: PASS_SCOPED
- 기존 H/He/D fixed-volume photo transaction 연결: PASS_SCOPED
- static-geometry source cohort opt-in 연결: PASS_SCOPED
- evolving-gas second order: HOLD
- variable Bianchi source-on cohort: HOLD
- source-age/angle/energy 전역 수렴 및 full EoR/native history: HOLD

다음 과제는 시간 의존 opacity·geometry와 emission clock의 공동 quadrature 계약이다. 그 전에 midpoint 대표 라벨을 실제 age 분포로 재해석하면 안 된다. 해당 계산이나 게시 승인을 이번 완료와 혼동하지 않는다.
