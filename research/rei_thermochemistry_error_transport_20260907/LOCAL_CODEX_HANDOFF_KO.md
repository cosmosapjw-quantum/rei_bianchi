# REI 다음 scientific task — 실제 population-stage와 오차 경계의 연결

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION
WORK_THREAD_REQUIRED=false

이 문서는 새 독립 solver 작성이나 first interval 실행 지시가 아니다. 같은 디렉터리의 PROOF_AND_SCOPE.md를 읽고, 이미 존재하는 REI population/thermal source의 실제 단계가 그 가정을 충족하는지 연결하라. 먼저 이 프롬프트가 게시된 exact commit과 최신 동일 작업의 진행 여부를 읽어 중복하지 마라. Git-first 반환 규칙은 REI PR #72의 지시를 적용하되 기존 작업선을 그 문서 branch로 되감지 마라.

## 여기에서 이미 수행한 것

고정 바탕은 REI `54a879231c68734fdda6990d67d8458d2918943e`, tree `29c406032a99d335ac52f866460e9b47ea42463b`다. XZ 수정과 실제 GCC chain은 XZ_INDEX_REPAIR_WORK_UNIT.json의 기존 local 결과다. 다시 다운로드하거나 같은 consumer/calibration을 반복하지 마라.

새 연구는 고정 generator A의 weighted l1 비증폭 정리, 서로 다른 A/B의 resolvent 식, rate feedback을 포함한 오차 점화식, 양수·보존인데도 104/85로 차이를 확대하는 합성 반례다. 정확 유리수 checker의 실제 CI 결과를 읽고, 그 결과가 production source 검증이 아님을 유지하라.

## 실제 로컬 접근이 필요한 다음 범위

기존 REI checkout/보존 source에서 population 단계와 네 독립 source site (`population_t0`, `population_t1_predictor`, `thermal_tgamma`, `thermal_t1_final`)를 찾아 source path/commit/blob와 함께 읽는다. 현재 Python/Rust wrapper의 실제 구현을 찾아라; 문서에서 경로를 추측하거나 BASS 소스를 검색하지 마라. 원래 시간 단위, state 단위, species ordering, stage weights, Patankar denominator, rates의 state/T/radiation dependence를 적는다.

각 단계가 (I-dt*A)u_next=b 형태이면 실제 A와 b를 유도하고, nonnegative off-diagonal, element별 conserved left vector, fixed positive weights, RHS positivity를 검증한다. b=u인지, 여러 source/site의 결합인지, open source가 있는지를 생략하지 마라. 고차 MPRK 전체를 backward Euler 한 단계로 대체하지 마라. 성립하지 않는 가정은 concrete term/counterexample으로 반환하고 같은 정리를 적용하지 않는다.

가정이 성립하는 부분에만 A의 state/input variation bound를 적용하고, stage composition과 thermal coupling의 block sensitivity를 도출하라. 원자핵 보존을 total energy나 photon closure의 증명으로 쓰지 마라. local estimator 자체를 rigorous defect rho라고 부르려면 기존 remainder certificate와의 연결을 보여라. 실제 derivative bound가 없으면 UNKNOWN으로 남기고 수치를 임의로 채우지 않는다.

필요한 작은 research-only exact CAS/유리수/JVP 비교는 기존 local 패키지로 수행해도 된다. 기존 production importer/guard/worker를 호출하지 않는 독립 algebra fixture로 제한한다. native 생산 실행이나 환경 복원은 금지한다. 기존 실제 단계에 결함이 확인되면 research oracle/직접 관련된 테스트는 같은 범위 안에서 근거 기반으로 여러 번 수정 가능하나, protected production code/물리식/허용오차/SSOT 변경은 별도 판단으로 남긴다.

## 결과와 게시

한 bounded 결과는 실제 stage-to-theorem mapping 또는 적용 불가를 입증하는 counterexample이다. 넓은 새 계획만 반환하지 마라. `CHATGPT_HANDOFF_KO.md`, 작은 machine-readable 결과, 필요한 원본 로그를 REI의 새 research/evidence child에 commit/non-force push하고 exact tested-source와 publication commit을 구분하라. 여기에는 HANDOFF 고정 링크와 실제 결과만 붙여 넣으면 된다. 새 public provider census 또는 rootfs 작업과 합치지 않는다.

금지: BASS/REC/HTT 접근·변경, 과거 XZ/native 실행 반복, 새 Snapshot GET, 패키지 설치/downgrade, production lock 수정, Section-0/ref/lease/worker, 전체 first interval, provider, ready/merge/force-push. 보존된 one-shot 예산은 reset하지 않는다. 동일 writer 하나를 유지하고, main conversation에 직접 반환한다.
