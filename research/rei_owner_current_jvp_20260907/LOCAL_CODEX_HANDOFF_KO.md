# REI owner-current JVP — main conversation direct handoff

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION
WORK_THREAD_REQUIRED=false
TASK=REI_OWNER_CURRENT_JVP_SOURCE_SLICE

## 수령 상태

이 디렉터리는 PR #76의 owner-normalization 후속 연구다. production 구현이 아니다.
부모 commit 9651959529b1048d9346f695e52ace2558d9bed6,
부모 tree 1440a7610e01cd4ed8abadf80319f7dcad8f863e.
현재 파일을 담는 새 commit은 게시 readback 링크에서 확인하라. 부모를 후보
테스트 commit이라고 기록하지 말라. 먼저 동일 작업의 더 새 결과가 있는지
해당 branch/PR만 확인하고, 존재하면 그 결과를 재사용하라.

주 대화에서 실제 source 대응식, 전역 owner 합의 미분, source의 HeII/H 규약,
photo event 세 간선으로의 연결, 조건부 norm bound를 유도했다. 소스와 O01--O10
테스트는 작성했으나 실행은 0회다. container/Python은 process 시작 전 ClientError,
Wolfram은 kernel 평가 전 MCP 404였다. 예상 PASS를 실행 결과로 승격하지 말라.

## 지금 수행할 최소 작업

1. 이 새 research directory만 변경 가능한 격리 작업공간에서 현재 후보를 읽어라.
   PROOF_AND_SCOPE.md, WORK_UNIT.json, 두 Python 파일을 먼저 읽고 exact source
   commit/tree/blob을 기록하라. 현재 사용자 작업트리의 수정은 덮어쓰지 말라.

2. 설치된 Python으로 새로운 연구용 테스트만 실행하라.

   python3 -B research/rei_owner_current_jvp_20260907/test_owner_current_reference.py

   실제 stdout/stderr, process exit, timeout 여부, 각 O01--O10 결과를 보존하라.
   Syntax/import error는 수학 RED가 아니다. 테스트는 합성 Fraction fixture이며
   production/NumPy/JAX 모듈을 import하지 않는다. 이 실행은 Rust-first numerical
   gate를 대체하지 않는다. #73--#76 기존 성공 suite는 다시 돌리지 말라.
   범위 안의 오류는 증거를 보존하면서 edit-test-diagnose-edit로 자율 수리하라.
   테스트 삭제, skip, assertion 완화, 물리 의미 변경으로 통과시키지 말라.

3. 실제 입력이 이미 보존돼 있다면 그중 ONE event-free positive state/forcing tube만
   읽어 owner 항의 경계를 계산하라. 필요한 것은 단순 point state가 아니라 경계를
   정당화하는 enclosure다. 최소 입력: source에 결합된 N의 범위와 고정 elemental
   totals, z 범위, 고정 sigma/support, J와 external raw response e의 범위/방향,
   kappa>0와 R>=r>0의 근거, 연결할 source site identity 및 시간 구간.
   후보 coefficient_jvp에 넣는 prefactor는 source의 NH0/YHE/MPC_CM/sigma에서
   읽어 구성하고 HeII의 denominator H를 유지하라. node weight는 다시 곱하지 말라.
   redshift, totals, J, e의 실제 종속성을 frozen independent input과 구별하라.

4. 보존된 tube를 찾지 못하면 파일/field별 UNKNOWN으로 반환하라. point sample,
   #75의 illustrative box 또는 이 Fraction fixture를 실제 tube라고 만들지 말라.
   새 canonical interval/production worker를 실행하여 입력을 만들지 말라.
   비어 있는 입력 때문에 이 디렉터리의 실행 가능한 연구 테스트까지 미루지는 말라.

5. 실수식과 binary64 source의 argmax residual corrections는 구별하라. 이 수리적
   항등식으로 machine rounding 또는 interval enclosure가 증명됐다고 하지 말라.
   source rounding/argmax 검증은 실제 parity 대상으로 따로 필요하다. 새 rounding
   certificate나 native ABI 전체를 만들지 말라. unresolved subgrid NODE allocation,
   OTS/atomic rate derivatives, thermal coupled bound, exact-flow rho는 계속 별도다.

6. PHYS-MATH, PHYS-MATH-CODE 순차 검토 후 후보/실행 source와 증거 commit을 구별하여
   REI-only non-force branch에 결과를 게시하고 일반 Git 파일 링크로 직접 반환하라.
   기존 PR은 Draft로 유지한다. proof 전체가 끝났다는 승인이나 independent reviewer
   인증을 만들어내지 말라. 실제 실행 실패도 원본과 함께 게시할 수 있다.

## 보존해야 할 경계

새 GitHub Actions workflow/dispatch/re-run은 만들지 말라. Git 게시 commit에는
[skip ci]를 넣고 skipped/pending status를 PASS로 쓰지 말라. GitHub 과거 기록
읽기는 필요 범위에서만 한다. 자동 local dispatch는 이 파일의 게시와 별개다.

BASS/REC/HTT 접근, BG02/native/XZ/GCC 재실행, Snapshot GET, 설치/rootfs/census,
production import/lock/Section-0/attempt ref/lease/controller/worker 변경,
46,080-node x three pilot, first interval/provider, ready/merge/force-push 금지.
기존 one-shot budget는 그대로 보존한다. 다른 site를 같은 시각이라는 이유로
합치지 말라. population RHS y0, predictor/gamma denominator y0,
corrector denominator yp와 (F0+F1)/2는 불변이다.

최대 이번 claim: source-bound exact-real resolved-owner JVP의 실제 소규모
reference validation 및, 실제 입력이 있을 때만 그 owner 항의 조건부 경계.
전체 flux bound, full nonlinear thermochemistry validation 또는 production PASS가 아니다.
