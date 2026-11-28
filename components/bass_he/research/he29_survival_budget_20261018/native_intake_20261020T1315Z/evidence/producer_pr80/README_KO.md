# HE29 NCP native reference return

이 반환은 PR #79의 고정 HE29 source/controller를 사용해 NCP에서 미시작한 네 finite reference pair만 순차 실행한 자료입니다. baseline science `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`, analysis `09929b0a06a833f0c2497e72f074ec8694a264df`, controller `ed5adca43f474553a9bce7f5de45d464be5905cb`를 pin했습니다.

네 pair 모두 exit 0으로 끝나며 controller classification과 read-only budget reducer가 4/4를 admit했습니다. 총 native 호출은 1,161,446회, controller wall은 5,672.09초입니다. 매 case 제한 3,600초, 실행 동시성 1, numerical/BLAS thread 1을 지켰습니다. physics, precision, tolerances는 변경하지 않았고, unchanged tests는 기존 pinned validation 증거로 재사용했습니다.

`execution/`에는 build, build receipt, preflight, pilot/study input snapshot, 네 native trace와 IDENTITY/TABLE/method/RESULT, controller PLAN/BEFORE/AFTER/SUMMARY/classification, process stdout/stderr/commands가 있습니다. `analysis_budget/REFERENCE_BUDGET.json`은 저장된 결과에 대한 read-only 분석입니다. `provenance/`는 실행 overlay, input source archive와 manifests, AGENTS/handoff/DELIVERY, host topology 및 명령을 보존합니다. Python venv는 포함하지 않고 exact package freeze와 `requirements.txt`를 포함합니다.

NCP는 64 CPU를 OS에서 허용하고 가용 RAM은 121 GiB였습니다. bootstrap log에서 `nproc=1`로 출력된 것은 미리 설정한 `OMP_NUM_THREADS=1` 때문이며, 별도 `lscpu`/cpuset 확인에서 64 CPU를 확인했습니다. 이 campaign은 계약상 단일 thread/동시성 1을 유지했습니다.

이 결과는 네 고정 finite HE29 model/table cohort만을 admission합니다. continuum 또는 continuous spectrum 수렴, global temperature bound, full EoR, upstream Grackle 전체 동등성, Bianchi/CMB 예측은 HOLD입니다. Optional packed canary는 이번 요청의 미시작 reference 범위 밖이라 실행하지 않았습니다.
