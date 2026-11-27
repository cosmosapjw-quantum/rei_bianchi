# FOLLOWUP runtime snapshot

진단 시점: 2026-10-01T13:53:12.163238+00:00. 과학 source·inputs·CONTRACT는 읽기만 했고 새 benchmark·물리 계산은 0회다.

현재 3 workers가 150개 작업을 실행하고 있다. RUN_IDENTITY 파일 생성 후 약 460.2초에 41개가 immutable TASK_EXECUTION/RESULT/DATA identity 검사를 통과했다. 이 시간은 launcher setup을 제외한 근사값이며 최종 LAUNCH 기록이 authoritative하다.

관측된 각 q의 wall time을 R 중간점에 대해 개별 선형 적합하면, 전체 overlap 작업시간 합을 3으로 나눈 값이 약 **2834초**다. 관측된 wall/R의 최솟값과 최댓값을 전체 grid에 적용한 시나리오는 **2650–3109초**다. 두 계산 모두 parity 네 작업, scheduling tail 및 launcher overhead를 제외한다. 따라서 **고정 1800초 cap 안에 전체가 끝날 가능성은 낮다**.

이 수치는 보장 bound나 통계적 confidence interval이 아니다. 아직 작은 R 쪽 task만 관측했고 이후 geometry·cache pressure·Python parity cost는 달라질 수 있다. 다른 rank 배치로 바꾸면 이 시간 적합을 그대로 쓸 수 없다. speedup이나 NCP64 scaling 주장은 없다.

| q | 측정 개수 | 측정 R 중간점 범위 | wall 범위 (s) | 적합 slope (s/R) |
|---|---:|---:|---:|---:|
| 16 | 14 | 17–29 | 16.91–28.54 | 0.890 |
| 24 | 13 | 17–29 | 24.66–39.63 | 1.357 |
| 32 | 12 | 17–27 | 34.39–55.53 | 2.102 |

현재 남은 109개(진행 중 포함)를 cap 내에 끝내려면 평균 task wall이 약 36.9초 이하여야 한다. 기존 MAIN의 preflight 통과 실행시간은 298.973초다. FOLLOWUP이 1800초를 모두 쓰면 전체 3600초에서 약 1501.0초가 남는다. 이는 이후 cleanup 및 실제 launch 기록으로 다시 계산해야 한다.

고정 cap은 유지한다. 중단된 계산은 runtime interruption으로 분류하며, 계산이 끝나지 않은 것을 수치 정확도 실패로 기록하지 않는다. 최소 복구 산출물과 순서는 다음과 같다.

1. Allow the existing bounded launcher to enforce its 1800-second cap; do not extend the live cap, alter source, or relabel timeout as numerical failure.

2. After launcher termination and owned-process cleanup, preserve FOLLOWUP_MPI_LAUNCH.json, FOLLOWUP_MPI_LOG.txt, MANIFEST_INPUT.json, RUN_IDENTITY.json, every task folder and existing source snapshot. Preserve cleanup and memory-events evidence.

3. Create a derived create-only RECOVERY_TASK_LEDGER.json with all 150 manifest tasks in order: completed validated, final non-PASS, started/interrupted, result-present-without-final-execution, or never started. Each row binds input, RESULT/DATA and TASK_EXECUTION hashes when present.

4. Accept completed tasks only after independent input/result/data/source/backend identity checks. If RESULT is present without final TASK_EXECUTION, explicitly validate and mark salvaged with its own evidence; do not fabricate an original successful execution record.

5. If a collector-compatible derived partial BATCH_SUMMARY is produced, label provenance as derived after interruption, copy unchanged verified execution entries, and mark unresolved entries explicitly. Do not forge a full PASS or overwrite any original record.

6. Construct a new create-only recovery manifest only for never-started and explicitly selected interrupted attempts. Use distinct task IDs and an external retry_of mapping to original IDs; keep original scientific parameters and state hashes unchanged. Never rerun a validated completed task.

7. Before recovery, subtract actual prior MAIN and FOLLOWUP active wall from the fixed 3600-second total; cap the new batch by the remaining total and each task by 300 seconds. Count interrupted/retried attempts in the execution and task-budget ledgers. Recovery is not quadrature fallback and must not silently consume forbidden additional parity calls.

8. Fresh resource preflight must pass again. Preserve exact source identity; if any recovery/collector source change is needed, first freeze a source snapshot corresponding to the interrupted RUN_IDENTITY, then record a new identity explicitly. If budget or count admissibility is unresolved, stop execution-blocked with retained evidence.

완료·진행·미시작 상태 목록과 관측 task별 시간·points·입력 identity, 적합 계수는 같은 이름의 JSON에 보존했다. 이는 live snapshot이며 그 이후 완료 여부를 대신하지 않는다.
