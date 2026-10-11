# NCP Codex 실행 인계 — 공개 템플릿

아래 지시와 별도 private handoff를 함께 사용한다. private handoff가 원래 seed와 이미 완료된 serial baseline의 외부 SHA pin을 제공한다. 저장 위치·인증정보·raw 결과를 이 공개 파일에 적지 않는다.

```text
rei_bianchi의 NCP 단일 노드 full-history 계산을 이어서 실행한다.

1. private handoff에 지정한 공개 commit을 별도 checkout으로 고정한다.
   research/accel02_20261011/q1b/hpc/README_KO.md를 읽는다.
   기존 작업/실행이 있으면 그 journal과 종료 receipt부터 확인한다.
   이미 진행한 trial이나 완료된 과학 캠페인을 다시 시작하지 않는다.

2. 실제 할당 노드의 affinity, cgroup-v2, 사용 가능한 RAM, Python/NumPy,
   원래 두 native binary의 SHA/실행 가능 여부를 확인한다.
   목표 장비는 64 CPU/128 GiB이나 실제 가용값을 우선한다.
   프로세스별 BLAS/OpenMP thread=1. 새 서버를 자동 생성하지 않는다.

3. private seed ZIP의 SHA를 외부 handoff 값과 대조한 뒤
   restore_private_seed.py --archive ... --sha256 ... --repo ... 로 복구한다.
   출력 경로는 private persistent volume의 var 아래로 둔다.
   기존 파일이 다르면 덮어쓰거나 historical JSON/hash를 고치지 않는다.
   원래 parent와 과거 실패 evidence, initial counter origin을 보존한다.

4. 새 HPC 제조/실패/복구 테스트를 실행한다. 원래 광역 과학 suite는 반복하지 않는다.
   private handoff가 제공하는 완료된 serial baseline과 RESULT/LAUNCH SHA를
   재사용해 benchmark_workers.py를 실행한다. serial baseline은 재실행하지 않는다.
   후보는 8,16,32,48 workers이며 현재 자원에 맞는 후보만 각1map, 최대4maps다.
   새 candidate map만 별도 diagnostic 예산에 기록하고 production cursor는 유지한다.
   첫 실행 실패/불일치가 발생하면 campaign을 멈추고 원본을 보존한다.
   통과한 설정들의 단일 표본 elapsed를 비교해 worker 수를 고른다.
   startup 포함 시간과 순수 map 시간/phase 비용을 구분한다.

5. 새 source가 바뀌지 않은 최종 checkout에서 prepare_hpc_run.py로 새 child를 만든다.
   신규 시도 할당10000, 원래 target/output schedule/수치기준을 유지한다.
   prepare의 누적 counter와 이전 외부 failure debit이 원래 parent와 연결되는지 본다.
   memory/cpuset admission 실패를 피하려고 임의로 허용치를 바꾸지 않는다.

6. run_ncp.sh로 chunk당 최대32 신규 시도/1800초를 실행한다.
   첫 bounded 작업의 총 wall budget은 준비·계산·백업을 포함해12시간이다.
   정상 chunk boundary이면 같은 bundle에서 새 작업만 이어간다.
   첫 실패, 미해결 journal, zero progress, signal stop, 자원 상한,
   할당량 소진 또는 원래 full target 도달 시 멈춘다.
   runtime source/input/config를 실행 중 수정하지 않는다.

7. 각 accepted pair는 즉시 checkpoint로 저장한다. chunk 종료 후 정지된 파일만
   archive하고 별도 프로세스로 새 archive identity를 확인한다.
   기존 private backup 목적지에 업로드하고 ACK/size/object identity를 기록한다.
   계산·패키징·업로드가 같은 경로에서 겹치지 않게 한다.
   upload 확인을 remote restore 검증이라고 부르지 않는다.
   private 원시 결과/복구 경로/locator/receipt는 공개 Git에 올리지 않는다.

8. 반환 보고: 공개 code commit과 binary/source/control/runtime identity,
   마지막 manifest/cursor/출력 epoch, 신규attempt/accepted/rejected/failed,
   별도 diagnostic/native/map 계수, 원래 ledger/geometry 기준,
   worker별 phase시간/최대RSS/종료사유/백업 receipt와 다음 최소행동.
   C2 full target 도달과 Time9/spectral24 수렴 통과를 구분한다.
   65/129 비교·각field own-fine normalization·zero 조건과 모든기존기준을 유지한다.
   Bianchi/BASS/CR/RCT의 별도 판정을 이번 계산으로 승격하지 않는다.
```

node별 profile 예시(두 baseline SHA는 검증된 private handoff에서 가져온다):

```bash
"$REI_PYTHON" "$HPC/benchmark_workers.py" \
  --parent-repo "$REI_REPO" --parent-root "$REI_PARENT" \
  --baseline "$REI_BASELINE" \
  --baseline-result-sha256 "$REI_BASELINE_RESULT_SHA" \
  --baseline-launch-sha256 "$REI_BASELINE_LAUNCH_SHA" \
  --workers 8 16 32 48 --output "$REI_REPO/var/ncp_worker_profile"
```

기존 profile이 있으면 해당 결과와 identity를 먼저 읽는다. 같은 후보를 자동 반복하지 않는다. 정상 완료된 결과의 `recommendation` 스키마와 `--help`를 확인해 `prepare_hpc_run.py --cell-workers`에 전달한다. 측정상 가장 빠른 설정은 이 표본에서의 선택이며 장기 scaling 보장이 아니다.

NCP 접속권한이나 private seed 접근이 없으면 코드 변경·환경 점검 등 독립 작업까지만 수행하고, 부족한 실제 접근권한을 정확히 보고한다. checkpoint를 새로 제조하거나 공개 링크로 바꾸어 대체하지 않는다.
